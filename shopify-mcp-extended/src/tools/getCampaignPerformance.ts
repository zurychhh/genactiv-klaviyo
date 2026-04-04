import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders.js";

const GetCampaignPerformanceInputSchema = z.object({
  dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
  dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
  limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
  utmSource: z.string().optional().describe("Filter by UTM source (e.g., facebook, instagram, google)"),
  utmMedium: z.string().optional().describe("Filter by UTM medium (e.g., cpc, email, social)"),
  financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid)")
});

type GetCampaignPerformanceInput = z.infer<typeof GetCampaignPerformanceInputSchema>;

interface CampaignMetrics {
  campaign: string;
  utmSource: string;
  utmMedium: string;
  orderCount: number;
  totalRevenue: number;
  averageOrderValue: number;
  firstOrderDate: string;
  lastOrderDate: string;
  contents: Array<string>;
  terms: Array<string>;
}

let shopifyClient: GraphQLClient;

const ORDERS_QUERY = gql`
  query GetOrdersForCampaigns($first: Int!, $query: String, $after: String) {
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
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          displayFinancialStatus
          customerJourneySummary {
            firstVisit {
              source
              sourceType
              utmParameters {
                source
                medium
                campaign
                content
                term
              }
              referrerUrl
            }
            lastVisit {
              source
              sourceType
              utmParameters {
                source
                medium
                campaign
                content
                term
              }
              referrerUrl
            }
          }
        }
      }
    }
  }
`;

const getCampaignPerformance = {
  name: "get-campaign-performance",
  description: "Get detailed performance metrics for marketing campaigns based on UTM parameters. Uses pagination to fetch ALL orders (not limited to 250). Default: only paid orders.",
  schema: GetCampaignPerformanceInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: GetCampaignPerformanceInput) => {
    try {
      const { dateFrom, dateTo, limit, utmSource, utmMedium, financialStatus } = input;

      const queryFilter = buildOrderQueryFilter({ dateFrom, dateTo, financialStatus });

      const { edges, totalFetched, hasMore } = await fetchAllOrders(
        shopifyClient,
        ORDERS_QUERY,
        { query: queryFilter },
        limit
      );

      // Aggregate by campaign
      const campaignMap = new Map<string, CampaignMetrics>();
      let totalOrders = 0;
      let totalRevenue = 0;
      let ordersWithCampaign = 0;

      for (const edge of edges) {
        const order = edge.node;
        const revenue = parseFloat(order.totalPriceSet.shopMoney.amount);
        const createdAt = order.createdAt;

        totalOrders++;
        totalRevenue += revenue;

        // Check first visit UTM
        const journey = order.customerJourneySummary;
        const utm = journey?.firstVisit?.utmParameters;

        if (utm?.campaign) {
          // Apply filters
          if (utmSource && utm.source?.toLowerCase() !== utmSource.toLowerCase()) {
            continue;
          }
          if (utmMedium && utm.medium?.toLowerCase() !== utmMedium.toLowerCase()) {
            continue;
          }

          ordersWithCampaign++;

          const campaignKey = `${utm.campaign}|${utm.source || "unknown"}|${utm.medium || "unknown"}`;
          const existingMetrics = campaignMap.get(campaignKey);
          const metrics: CampaignMetrics = existingMetrics || {
            campaign: utm.campaign,
            utmSource: utm.source || "unknown",
            utmMedium: utm.medium || "unknown",
            orderCount: 0,
            totalRevenue: 0,
            averageOrderValue: 0,
            firstOrderDate: createdAt,
            lastOrderDate: createdAt,
            contents: [] as string[],
            terms: [] as string[]
          };

          metrics.orderCount++;
          metrics.totalRevenue += revenue;

          // Track date range
          if (createdAt < metrics.firstOrderDate) {
            metrics.firstOrderDate = createdAt;
          }
          if (createdAt > metrics.lastOrderDate) {
            metrics.lastOrderDate = createdAt;
          }

          // Track content and term variations
          const utmContent = utm.content as string | undefined;
          const utmTerm = utm.term as string | undefined;
          if (utmContent && !metrics.contents.includes(utmContent)) {
            metrics.contents.push(utmContent);
          }
          if (utmTerm && !metrics.terms.includes(utmTerm)) {
            metrics.terms.push(utmTerm);
          }

          campaignMap.set(campaignKey, metrics);
        }
      }

      // Calculate AOV and finalize
      const campaigns = Array.from(campaignMap.values())
        .map(m => ({
          ...m,
          totalRevenue: Math.round(m.totalRevenue * 100) / 100,
          averageOrderValue: m.orderCount > 0
            ? Math.round(m.totalRevenue / m.orderCount * 100) / 100
            : 0
        }))
        .sort((a, b) => b.totalRevenue - a.totalRevenue);

      // Group by source for summary
      const bySource: Record<string, { orderCount: number; revenue: number; campaigns: number }> = {};
      for (const campaign of campaigns) {
        if (!bySource[campaign.utmSource]) {
          bySource[campaign.utmSource] = { orderCount: 0, revenue: 0, campaigns: 0 };
        }
        bySource[campaign.utmSource].orderCount += campaign.orderCount;
        bySource[campaign.utmSource].revenue += campaign.totalRevenue;
        bySource[campaign.utmSource].campaigns++;
      }

      return {
        period: { from: dateFrom, to: dateTo },
        filters: { utmSource: utmSource || null, utmMedium: utmMedium || null },
        dataQuality: {
          ordersAnalyzed: totalFetched,
          hasMoreOrders: hasMore,
          financialStatusFilter: financialStatus,
          campaignAttributionRate: totalOrders > 0
            ? Math.round(ordersWithCampaign / totalOrders * 100)
            : 0,
          note: hasMore
            ? `Przeanalizowano ${totalFetched} zamówień (limit). Mogą istnieć dodatkowe zamówienia.`
            : `Przeanalizowano WSZYSTKIE ${totalFetched} zamówień w tym okresie.`
        },
        summary: {
          totalOrders,
          totalRevenue: Math.round(totalRevenue * 100) / 100,
          ordersWithCampaign,
          campaignAttributionRate: totalOrders > 0
            ? Math.round(ordersWithCampaign / totalOrders * 100)
            : 0,
          uniqueCampaigns: campaigns.length
        },
        bySource: Object.entries(bySource).map(([source, data]) => ({
          source,
          ...data,
          revenue: Math.round(data.revenue * 100) / 100
        })).sort((a, b) => b.revenue - a.revenue),
        campaigns
      };
    } catch (error) {
      console.error("Error analyzing campaign performance:", error);
      throw new Error(
        `Failed to analyze campaign performance: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }
};

export { getCampaignPerformance };
