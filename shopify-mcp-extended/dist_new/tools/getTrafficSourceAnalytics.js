import { gql } from "graphql-request";
import { z } from "zod";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders.js";
const GetTrafficSourceAnalyticsInputSchema = z.object({
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
    financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid — excludes cancelled/refunded)")
});
let shopifyClient;
const ORDERS_QUERY = gql `
  query GetOrdersForAnalytics($first: Int!, $query: String, $after: String) {
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
          sourceName
          sourceIdentifier
          channelInformation {
            channelId
            channelDefinition {
              channelName
              handle
            }
          }
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
const getTrafficSourceAnalytics = {
    name: "get-traffic-source-analytics",
    description: "Analyze orders by traffic source with revenue and AOV metrics. Uses pagination to fetch ALL orders (not limited to 250). Default: only paid orders.",
    schema: GetTrafficSourceAnalyticsInputSchema,
    initialize(client) {
        shopifyClient = client;
    },
    execute: async (input) => {
        try {
            const { dateFrom, dateTo, limit, financialStatus } = input;
            const queryFilter = buildOrderQueryFilter({ dateFrom, dateTo, financialStatus });
            const { edges, totalFetched, hasMore } = await fetchAllOrders(shopifyClient, ORDERS_QUERY, { query: queryFilter }, limit);
            // Aggregate by traffic source
            const sourceMap = new Map();
            const channelMap = new Map();
            const utmSourceMap = new Map();
            let totalOrders = 0;
            let totalRevenue = 0;
            let ordersWithJourney = 0;
            let ordersWithoutJourney = 0;
            for (const edge of edges) {
                const order = edge.node;
                const revenue = parseFloat(order.totalPriceSet.shopMoney.amount);
                totalOrders++;
                totalRevenue += revenue;
                // Track channel
                const channelName = order.channelInformation?.channelDefinition?.channelName || order.sourceName || "Unknown";
                const channelData = channelMap.get(channelName) || { orderCount: 0, revenue: 0 };
                channelData.orderCount++;
                channelData.revenue += revenue;
                channelMap.set(channelName, channelData);
                // Track customer journey (first visit attribution)
                const journey = order.customerJourneySummary;
                if (journey?.firstVisit) {
                    ordersWithJourney++;
                    const firstVisit = journey.firstVisit;
                    const source = firstVisit.source || "Direct";
                    const sourceType = firstVisit.sourceType || "unknown";
                    const key = `${source}|${sourceType}`;
                    const existingMetrics = sourceMap.get(key);
                    const metrics = existingMetrics || {
                        source,
                        sourceType,
                        orderCount: 0,
                        totalRevenue: 0,
                        averageOrderValue: 0,
                        campaigns: {}
                    };
                    metrics.orderCount++;
                    metrics.totalRevenue += revenue;
                    // Track campaigns
                    if (firstVisit.utmParameters?.campaign) {
                        const campaign = firstVisit.utmParameters.campaign;
                        if (!metrics.campaigns[campaign]) {
                            metrics.campaigns[campaign] = { orderCount: 0, revenue: 0 };
                        }
                        metrics.campaigns[campaign].orderCount++;
                        metrics.campaigns[campaign].revenue += revenue;
                    }
                    sourceMap.set(key, metrics);
                    // Track UTM sources separately
                    if (firstVisit.utmParameters?.source) {
                        const utmSource = firstVisit.utmParameters.source;
                        const utmData = utmSourceMap.get(utmSource) || { orderCount: 0, revenue: 0, campaigns: new Set() };
                        utmData.orderCount++;
                        utmData.revenue += revenue;
                        if (firstVisit.utmParameters.campaign) {
                            utmData.campaigns.add(firstVisit.utmParameters.campaign);
                        }
                        utmSourceMap.set(utmSource, utmData);
                    }
                }
                else {
                    ordersWithoutJourney++;
                }
            }
            // Calculate AOV for each source
            for (const metrics of sourceMap.values()) {
                metrics.averageOrderValue = metrics.orderCount > 0
                    ? Math.round(metrics.totalRevenue / metrics.orderCount * 100) / 100
                    : 0;
                metrics.totalRevenue = Math.round(metrics.totalRevenue * 100) / 100;
            }
            // Sort by revenue
            const bySource = Array.from(sourceMap.values())
                .sort((a, b) => b.totalRevenue - a.totalRevenue);
            const byChannel = Array.from(channelMap.entries())
                .map(([channel, data]) => ({
                channel,
                orderCount: data.orderCount,
                revenue: Math.round(data.revenue * 100) / 100,
                averageOrderValue: Math.round(data.revenue / data.orderCount * 100) / 100
            }))
                .sort((a, b) => b.revenue - a.revenue);
            const byUtmSource = Array.from(utmSourceMap.entries())
                .map(([source, data]) => ({
                utmSource: source,
                orderCount: data.orderCount,
                revenue: Math.round(data.revenue * 100) / 100,
                averageOrderValue: Math.round(data.revenue / data.orderCount * 100) / 100,
                campaigns: Array.from(data.campaigns)
            }))
                .sort((a, b) => b.revenue - a.revenue);
            return {
                period: { from: dateFrom, to: dateTo },
                dataQuality: {
                    ordersAnalyzed: totalFetched,
                    hasMoreOrders: hasMore,
                    financialStatusFilter: financialStatus,
                    journeyTrackingRate: totalOrders > 0 ? Math.round(ordersWithJourney / totalOrders * 100) : 0,
                    note: hasMore
                        ? `Przeanalizowano ${totalFetched} zamówień (limit). Mogą istnieć dodatkowe zamówienia w tym okresie.`
                        : `Przeanalizowano WSZYSTKIE ${totalFetched} zamówień w tym okresie.`
                },
                summary: {
                    totalOrders,
                    totalRevenue: Math.round(totalRevenue * 100) / 100,
                    averageOrderValue: totalOrders > 0 ? Math.round(totalRevenue / totalOrders * 100) / 100 : 0,
                    ordersWithJourney,
                    ordersWithoutJourney,
                    journeyTrackingRate: totalOrders > 0 ? Math.round(ordersWithJourney / totalOrders * 100) : 0
                },
                bySource,
                byChannel,
                byUtmSource
            };
        }
        catch (error) {
            console.error("Error analyzing traffic sources:", error);
            throw new Error(`Failed to analyze traffic sources: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
};
export { getTrafficSourceAnalytics };
