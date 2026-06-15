import { gql } from "graphql-request";
import { z } from "zod";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders.js";
const GetRevenueReconciliationInputSchema = z.object({
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    maxOrders: z.number().default(5000).describe("Max orders to fetch for reconciliation (default 5000)")
});
let shopifyClient;
// Lightweight query — only fields needed for reconciliation
const ORDERS_QUERY = gql `
  query GetOrdersForReconciliation($first: Int!, $query: String, $after: String) {
    orders(first: $first, query: $query, sortKey: CREATED_AT, reverse: true, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          id
          name
          createdAt
          displayFinancialStatus
          cancelledAt
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          subtotalPriceSet {
            shopMoney {
              amount
            }
          }
          totalDiscountsSet {
            shopMoney {
              amount
            }
          }
          totalShippingPriceSet {
            shopMoney {
              amount
            }
          }
          totalTaxSet {
            shopMoney {
              amount
            }
          }
          refunds(first: 10) {
            id
            totalRefundedSet {
              shopMoney {
                amount
              }
            }
          }
        }
      }
    }
  }
`;
const getRevenueReconciliation = {
    name: "get-revenue-reconciliation",
    description: "Cross-validate revenue data: fetches ALL orders in date range and breaks down revenue by financial status, refunds, discounts, shipping, and tax. Use this to verify why MCP numbers might differ from Shopify Admin panel.",
    schema: GetRevenueReconciliationInputSchema,
    initialize(client) {
        shopifyClient = client;
    },
    execute: async (input) => {
        try {
            const { dateFrom, dateTo, maxOrders } = input;
            // Fetch ALL orders (no financial_status filter — we want everything for reconciliation)
            const queryFilter = buildOrderQueryFilter({ dateFrom, dateTo, financialStatus: "any" });
            const { edges, totalFetched, hasMore } = await fetchAllOrders(shopifyClient, ORDERS_QUERY, { query: queryFilter }, maxOrders);
            // Aggregate by financial status
            const byStatus = {};
            let grandTotal = 0;
            let grandSubtotal = 0;
            let grandDiscounts = 0;
            let grandShipping = 0;
            let grandTax = 0;
            let grandRefunded = 0;
            let cancelledCount = 0;
            let totalOrders = 0;
            for (const edge of edges) {
                const order = edge.node;
                const status = order.displayFinancialStatus || "UNKNOWN";
                const totalPrice = parseFloat(order.totalPriceSet.shopMoney.amount);
                const subtotal = parseFloat(order.subtotalPriceSet?.shopMoney?.amount || "0");
                const discounts = parseFloat(order.totalDiscountsSet?.shopMoney?.amount || "0");
                const shipping = parseFloat(order.totalShippingPriceSet?.shopMoney?.amount || "0");
                const tax = parseFloat(order.totalTaxSet?.shopMoney?.amount || "0");
                // Sum refunds
                let refunded = 0;
                if (order.refunds && order.refunds.length > 0) {
                    for (const refund of order.refunds) {
                        refunded += parseFloat(refund.totalRefundedSet?.shopMoney?.amount || "0");
                    }
                }
                totalOrders++;
                grandTotal += totalPrice;
                grandSubtotal += subtotal;
                grandDiscounts += discounts;
                grandShipping += shipping;
                grandTax += tax;
                grandRefunded += refunded;
                if (order.cancelledAt)
                    cancelledCount++;
                if (!byStatus[status]) {
                    byStatus[status] = { count: 0, totalPrice: 0, subtotal: 0, discounts: 0, shipping: 0, tax: 0, refunded: 0 };
                }
                byStatus[status].count++;
                byStatus[status].totalPrice += totalPrice;
                byStatus[status].subtotal += subtotal;
                byStatus[status].discounts += discounts;
                byStatus[status].shipping += shipping;
                byStatus[status].tax += tax;
                byStatus[status].refunded += refunded;
            }
            // Calculate "net revenue" variants that different panels might show
            const paidOnly = byStatus["PAID"] || { count: 0, totalPrice: 0, subtotal: 0, discounts: 0, shipping: 0, tax: 0, refunded: 0 };
            const partiallyPaid = byStatus["PARTIALLY_PAID"] || { count: 0, totalPrice: 0, subtotal: 0, discounts: 0, shipping: 0, tax: 0, refunded: 0 };
            const partiallyRefunded = byStatus["PARTIALLY_REFUNDED"] || { count: 0, totalPrice: 0, subtotal: 0, discounts: 0, shipping: 0, tax: 0, refunded: 0 };
            const refundedStatus = byStatus["REFUNDED"] || { count: 0, totalPrice: 0, subtotal: 0, discounts: 0, shipping: 0, tax: 0, refunded: 0 };
            const r = (n) => Math.round(n * 100) / 100;
            // Format status breakdown
            const statusBreakdown = Object.entries(byStatus)
                .map(([status, data]) => ({
                status,
                orders: data.count,
                totalPrice: r(data.totalPrice),
                subtotal: r(data.subtotal),
                discounts: r(data.discounts),
                shipping: r(data.shipping),
                tax: r(data.tax),
                refunded: r(data.refunded),
                netRevenue: r(data.totalPrice - data.refunded)
            }))
                .sort((a, b) => b.totalPrice - a.totalPrice);
            return {
                period: { from: dateFrom, to: dateTo },
                dataCompleteness: {
                    totalOrdersFetched: totalFetched,
                    hasMoreOrders: hasMore,
                    note: hasMore
                        ? `⚠️ Pobrano ${totalFetched} zamówień (limit). W tym okresie mogą być dodatkowe zamówienia.`
                        : `✅ Pobrano WSZYSTKIE ${totalFetched} zamówień w tym okresie.`
                },
                // === GŁÓWNA SEKCJA: różne sposoby liczenia revenue ===
                revenueVariants: {
                    allOrders_totalPrice: {
                        value: r(grandTotal),
                        label: "Suma totalPrice WSZYSTKICH zamówień",
                        description: "Wszystkie zamówienia (paid + pending + cancelled + refunded). Shopify Admin → Orders → All."
                    },
                    paidOnly_totalPrice: {
                        value: r(paidOnly.totalPrice + partiallyPaid.totalPrice),
                        label: "Suma totalPrice tylko PAID + PARTIALLY_PAID",
                        description: "Tylko opłacone zamówienia. To jest najbliższe 'Revenue' w Shopify Admin → Analytics."
                    },
                    paidOnly_minusRefunds: {
                        value: r(paidOnly.totalPrice + partiallyPaid.totalPrice + partiallyRefunded.totalPrice - grandRefunded),
                        label: "PAID + PARTIALLY_PAID + PARTIALLY_REFUNDED − zwroty",
                        description: "Net revenue po odjęciu zwrotów. Najbliższe 'Net sales' w Shopify."
                    },
                    subtotalOnly: {
                        value: r(grandSubtotal),
                        label: "Suma subtotal (bez shipping, bez tax)",
                        description: "Tylko wartość produktów, bez dostawy i podatku."
                    }
                },
                // === Rozbicie na składowe ===
                breakdown: {
                    totalOrders,
                    cancelledOrders: cancelledCount,
                    grossRevenue: r(grandTotal),
                    subtotal: r(grandSubtotal),
                    totalDiscounts: r(grandDiscounts),
                    totalShipping: r(grandShipping),
                    totalTax: r(grandTax),
                    totalRefunded: r(grandRefunded),
                    netRevenue: r(grandTotal - grandRefunded)
                },
                // === Po statusie finansowym ===
                byFinancialStatus: statusBreakdown,
                // === Wyjaśnienie rozbieżności ===
                reconciliationNotes: [
                    grandRefunded > 0
                        ? `Zwroty: ${r(grandRefunded)} PLN — to najczęstsza przyczyna różnicy między 'gross' a 'net' revenue.`
                        : null,
                    cancelledCount > 0
                        ? `Anulowane zamówienia: ${cancelledCount} (${r(byStatus["CANCELLED"]?.totalPrice || 0)} PLN) — Shopify Admin może je wykluczać z totali.`
                        : null,
                    grandDiscounts > 0
                        ? `Rabaty: ${r(grandDiscounts)} PLN — Shopify Admin odejmuje je od subtotal, ale totalPrice już je uwzględnia.`
                        : null,
                    grandShipping > 0
                        ? `Dostawa: ${r(grandShipping)} PLN — niektóre raporty wliczają shipping do revenue, inne nie.`
                        : null,
                    grandTax > 0
                        ? `Podatek: ${r(grandTax)} PLN — Shopify Admin może pokazywać revenue z lub bez VAT.`
                        : null,
                    "💡 Porównując z Shopify Admin → Analytics → 'Total sales', użyj wariantu 'paidOnly_totalPrice'. Dla 'Net sales' użyj 'paidOnly_minusRefunds'."
                ].filter(Boolean)
            };
        }
        catch (error) {
            console.error("Error in revenue reconciliation:", error);
            throw new Error(`Failed to reconcile revenue: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
};
export { getRevenueReconciliation };
