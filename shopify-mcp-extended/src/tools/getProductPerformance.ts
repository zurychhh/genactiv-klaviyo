import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders.js";

const GetProductPerformanceInputSchema = z.object({
  dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
  dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
  limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
  utmSource: z.string().optional().describe("Filter by UTM source to see product performance from specific source"),
  financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid)")
});

type GetProductPerformanceInput = z.infer<typeof GetProductPerformanceInputSchema>;

interface ProductMetrics {
  productId: string;
  title: string;
  sku: string | null;
  variantTitle: string | null;
  unitsSold: number;
  revenue: number;
  orderCount: number;
  averagePrice: number;
  sources: Record<string, { units: number; revenue: number }>;
}

let shopifyClient: GraphQLClient;

const ORDERS_QUERY = gql`
  query GetOrdersForProducts($first: Int!, $query: String, $after: String) {
    orders(first: $first, query: $query, sortKey: CREATED_AT, reverse: true, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          id
          createdAt
          displayFinancialStatus
          customerJourneySummary {
            firstVisit {
              source
              sourceType
              utmParameters {
                source
                medium
                campaign
              }
            }
          }
          lineItems(first: 50) {
            edges {
              node {
                id
                title
                quantity
                originalTotalSet {
                  shopMoney {
                    amount
                  }
                }
                variant {
                  id
                  title
                  sku
                  product {
                    id
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`;

const getProductPerformance = {
  name: "get-product-performance",
  description: "Analyze product performance with breakdown by traffic source. Uses pagination to fetch ALL orders (not limited to 250). Default: only paid orders.",
  schema: GetProductPerformanceInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: GetProductPerformanceInput) => {
    try {
      const { dateFrom, dateTo, limit, utmSource, financialStatus } = input;

      const queryFilter = buildOrderQueryFilter({ dateFrom, dateTo, financialStatus });

      const { edges, totalFetched, hasMore } = await fetchAllOrders(
        shopifyClient,
        ORDERS_QUERY,
        { query: queryFilter },
        limit
      );

      // Aggregate by product
      const productMap = new Map<string, ProductMetrics>();
      let totalOrders = 0;
      let totalRevenue = 0;
      let totalUnits = 0;

      for (const edge of edges) {
        const order = edge.node;
        const journey = order.customerJourneySummary;
        const orderSource: string = journey?.firstVisit?.utmParameters?.source ||
                           journey?.firstVisit?.source ||
                           "direct";

        // Apply UTM source filter
        if (utmSource) {
          const orderUtmSource = journey?.firstVisit?.utmParameters?.source;
          if (!orderUtmSource || orderUtmSource.toLowerCase() !== utmSource.toLowerCase()) {
            continue;
          }
        }

        totalOrders++;

        for (const lineItemEdge of order.lineItems.edges) {
          const item = lineItemEdge.node;
          const productId = item.variant?.product?.id || item.id;
          const revenue = parseFloat(item.originalTotalSet.shopMoney.amount);
          const quantity = item.quantity;

          totalRevenue += revenue;
          totalUnits += quantity;

          const key = productId;
          const existingMetrics = productMap.get(key);
          const metrics: ProductMetrics = existingMetrics || {
            productId,
            title: item.title,
            sku: item.variant?.sku || null,
            variantTitle: item.variant?.title || null,
            unitsSold: 0,
            revenue: 0,
            orderCount: 0,
            averagePrice: 0,
            sources: {} as Record<string, { units: number; revenue: number }>
          };

          metrics.unitsSold += quantity;
          metrics.revenue += revenue;
          metrics.orderCount++;

          // Track by source
          if (!metrics.sources[orderSource]) {
            metrics.sources[orderSource] = { units: 0, revenue: 0 };
          }
          metrics.sources[orderSource].units += quantity;
          metrics.sources[orderSource].revenue += revenue;

          productMap.set(key, metrics);
        }
      }

      // Finalize metrics
      const products = Array.from(productMap.values())
        .map(p => ({
          ...p,
          revenue: Math.round(p.revenue * 100) / 100,
          averagePrice: p.unitsSold > 0
            ? Math.round(p.revenue / p.unitsSold * 100) / 100
            : 0,
          sources: Object.entries(p.sources)
            .map(([source, data]) => ({
              source,
              units: data.units,
              revenue: Math.round(data.revenue * 100) / 100
            }))
            .sort((a, b) => b.revenue - a.revenue)
        }))
        .sort((a, b) => b.revenue - a.revenue);

      // Top sources by product count
      const sourceProductMap: Record<string, Set<string>> = {};
      for (const product of products) {
        for (const source of product.sources) {
          if (!sourceProductMap[source.source]) {
            sourceProductMap[source.source] = new Set();
          }
          sourceProductMap[source.source].add(product.productId);
        }
      }

      const topProductsBySource: Record<string, { title: string; units: number; revenue: number }[]> = {};
      const allSources = new Set<string>();
      for (const product of products) {
        for (const source of product.sources) {
          allSources.add(source.source);
          if (!topProductsBySource[source.source]) {
            topProductsBySource[source.source] = [];
          }
          topProductsBySource[source.source].push({
            title: product.title,
            units: source.units,
            revenue: source.revenue
          });
        }
      }

      // Sort and limit top products per source
      for (const source of Object.keys(topProductsBySource)) {
        topProductsBySource[source] = topProductsBySource[source]
          .sort((a, b) => b.revenue - a.revenue)
          .slice(0, 5);
      }

      return {
        period: { from: dateFrom, to: dateTo },
        filters: { utmSource: utmSource || null },
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
          totalUnits,
          uniqueProducts: products.length,
          averageOrderValue: totalOrders > 0
            ? Math.round(totalRevenue / totalOrders * 100) / 100
            : 0,
          averageUnitsPerOrder: totalOrders > 0
            ? Math.round(totalUnits / totalOrders * 10) / 10
            : 0
        },
        topProducts: products.slice(0, 20),
        topProductsBySource
      };
    } catch (error) {
      console.error("Error analyzing product performance:", error);
      throw new Error(
        `Failed to analyze product performance: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }
};

export { getProductPerformance };
