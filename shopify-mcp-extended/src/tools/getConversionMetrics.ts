import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders.js";

const GetConversionMetricsInputSchema = z.object({
  dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
  dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
  limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
  groupBy: z.enum(["day", "week", "month"]).default("day").describe("Time grouping for trends"),
  financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("any").describe("Filter by financial status (default: any — shows all statuses for conversion analysis)")
});

type GetConversionMetricsInput = z.infer<typeof GetConversionMetricsInputSchema>;

let shopifyClient: GraphQLClient;

const ORDERS_QUERY = gql`
  query GetOrdersForConversion($first: Int!, $query: String, $after: String) {
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
          displayFulfillmentStatus
          cancelledAt
          cancelReason
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
          paymentGatewayNames
          transactions(first: 5) {
            id
            status
            kind
            gateway
            formattedGateway
            amountSet {
              shopMoney {
                amount
              }
            }
          }
          customer {
            id
            numberOfOrders
          }
          lineItems(first: 20) {
            edges {
              node {
                quantity
              }
            }
          }
        }
      }
    }
  }
`;

const getConversionMetrics = {
  name: "get-conversion-metrics",
  description: "Get conversion metrics including payment methods, financial status, and fulfillment trends. Uses pagination to fetch ALL orders (not limited to 250). Default: all financial statuses (for full conversion funnel view).",
  schema: GetConversionMetricsInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: GetConversionMetricsInput) => {
    try {
      const { dateFrom, dateTo, limit, groupBy, financialStatus } = input;

      const queryFilter = buildOrderQueryFilter({ dateFrom, dateTo, financialStatus });

      const { edges, totalFetched, hasMore } = await fetchAllOrders(
        shopifyClient,
        ORDERS_QUERY,
        { query: queryFilter },
        limit
      );

      // Initialize metrics
      let totalOrders = 0;
      let totalRevenue = 0;
      let totalDiscounts = 0;
      let totalShipping = 0;
      let totalItems = 0;
      let cancelledOrders = 0;
      let newCustomerOrders = 0;
      let returningCustomerOrders = 0;

      const byFinancialStatus: Record<string, { count: number; revenue: number }> = {};
      const byFulfillmentStatus: Record<string, { count: number; revenue: number }> = {};
      const byPaymentGateway: Record<string, { count: number; revenue: number }> = {};
      const byCancelReason: Record<string, number> = {};
      const byTimeGroup: Record<string, { orders: number; revenue: number; items: number }> = {};

      for (const edge of edges) {
        const order = edge.node;
        const revenue = parseFloat(order.totalPriceSet.shopMoney.amount);
        const discounts = parseFloat(order.totalDiscountsSet?.shopMoney?.amount || "0");
        const shipping = parseFloat(order.totalShippingPriceSet?.shopMoney?.amount || "0");
        const createdAt = new Date(order.createdAt);

        totalOrders++;
        totalRevenue += revenue;
        totalDiscounts += discounts;
        totalShipping += shipping;

        // Count items
        const itemCount = order.lineItems.edges.reduce(
          (sum: number, item: any) => sum + item.node.quantity,
          0
        );
        totalItems += itemCount;

        // Track new vs returning customers
        const customerOrderCount = parseInt(order.customer?.numberOfOrders || "0", 10);
        if (customerOrderCount <= 1) {
          newCustomerOrders++;
        } else {
          returningCustomerOrders++;
        }

        // Track cancelled
        if (order.cancelledAt) {
          cancelledOrders++;
          const reason = order.cancelReason || "unknown";
          byCancelReason[reason] = (byCancelReason[reason] || 0) + 1;
        }

        // Track by financial status
        const finStatus = order.displayFinancialStatus || "UNKNOWN";
        if (!byFinancialStatus[finStatus]) {
          byFinancialStatus[finStatus] = { count: 0, revenue: 0 };
        }
        byFinancialStatus[finStatus].count++;
        byFinancialStatus[finStatus].revenue += revenue;

        // Track by fulfillment status
        const fulfillmentStatus = order.displayFulfillmentStatus || "UNKNOWN";
        if (!byFulfillmentStatus[fulfillmentStatus]) {
          byFulfillmentStatus[fulfillmentStatus] = { count: 0, revenue: 0 };
        }
        byFulfillmentStatus[fulfillmentStatus].count++;
        byFulfillmentStatus[fulfillmentStatus].revenue += revenue;

        // Track by payment gateway
        const gateways = order.paymentGatewayNames || ["unknown"];
        for (const gateway of gateways) {
          if (!byPaymentGateway[gateway]) {
            byPaymentGateway[gateway] = { count: 0, revenue: 0 };
          }
          byPaymentGateway[gateway].count++;
          byPaymentGateway[gateway].revenue += revenue;
        }

        // Track by time group
        let timeKey: string;
        if (groupBy === "day") {
          timeKey = createdAt.toISOString().split("T")[0];
        } else if (groupBy === "week") {
          const weekStart = new Date(createdAt);
          weekStart.setDate(createdAt.getDate() - createdAt.getDay());
          timeKey = weekStart.toISOString().split("T")[0];
        } else {
          timeKey = `${createdAt.getFullYear()}-${String(createdAt.getMonth() + 1).padStart(2, "0")}`;
        }

        if (!byTimeGroup[timeKey]) {
          byTimeGroup[timeKey] = { orders: 0, revenue: 0, items: 0 };
        }
        byTimeGroup[timeKey].orders++;
        byTimeGroup[timeKey].revenue += revenue;
        byTimeGroup[timeKey].items += itemCount;
      }

      // Format output
      const formatStatusData = (data: Record<string, { count: number; revenue: number }>) =>
        Object.entries(data)
          .map(([status, { count, revenue }]) => ({
            status,
            count,
            revenue: Math.round(revenue * 100) / 100,
            percentage: totalOrders > 0 ? Math.round(count / totalOrders * 100) : 0
          }))
          .sort((a, b) => b.count - a.count);

      const trends = Object.entries(byTimeGroup)
        .map(([period, data]) => ({
          period,
          orders: data.orders,
          revenue: Math.round(data.revenue * 100) / 100,
          items: data.items,
          averageOrderValue: data.orders > 0
            ? Math.round(data.revenue / data.orders * 100) / 100
            : 0,
          averageItemsPerOrder: data.orders > 0
            ? Math.round(data.items / data.orders * 10) / 10
            : 0
        }))
        .sort((a, b) => a.period.localeCompare(b.period));

      return {
        period: { from: dateFrom, to: dateTo, groupBy },
        dataQuality: {
          ordersAnalyzed: totalFetched,
          hasMoreOrders: hasMore,
          financialStatusFilter: financialStatus,
          note: hasMore
            ? `Przeanalizowano ${totalFetched} zamówień (limit). Mogą istnieć dodatkowe zamówienia.`
            : `Przeanalizowano WSZYSTKIE ${totalFetched} zamówień w tym okresie.`
        },
        summary: {
          totalOrders,
          totalRevenue: Math.round(totalRevenue * 100) / 100,
          totalDiscounts: Math.round(totalDiscounts * 100) / 100,
          totalShipping: Math.round(totalShipping * 100) / 100,
          totalItems,
          averageOrderValue: totalOrders > 0
            ? Math.round(totalRevenue / totalOrders * 100) / 100
            : 0,
          averageItemsPerOrder: totalOrders > 0
            ? Math.round(totalItems / totalOrders * 10) / 10
            : 0,
          discountRate: totalRevenue > 0
            ? Math.round(totalDiscounts / (totalRevenue + totalDiscounts) * 100)
            : 0
        },
        customerMetrics: {
          newCustomerOrders,
          returningCustomerOrders,
          newCustomerRate: totalOrders > 0
            ? Math.round(newCustomerOrders / totalOrders * 100)
            : 0,
          returningCustomerRate: totalOrders > 0
            ? Math.round(returningCustomerOrders / totalOrders * 100)
            : 0
        },
        cancellationMetrics: {
          cancelledOrders,
          cancellationRate: totalOrders > 0
            ? Math.round(cancelledOrders / totalOrders * 100 * 10) / 10
            : 0,
          byCancelReason: Object.entries(byCancelReason)
            .map(([reason, count]) => ({ reason, count }))
            .sort((a, b) => b.count - a.count)
        },
        byFinancialStatus: formatStatusData(byFinancialStatus),
        byFulfillmentStatus: formatStatusData(byFulfillmentStatus),
        byPaymentGateway: Object.entries(byPaymentGateway)
          .map(([gateway, { count, revenue }]) => ({
            gateway,
            count,
            revenue: Math.round(revenue * 100) / 100,
            percentage: totalOrders > 0 ? Math.round(count / totalOrders * 100) : 0
          }))
          .sort((a, b) => b.count - a.count),
        trends
      };
    } catch (error) {
      console.error("Error getting conversion metrics:", error);
      throw new Error(
        `Failed to get conversion metrics: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }
};

export { getConversionMetrics };
