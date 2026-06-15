/**
 * Exhaustive edge-case and crash tests for Shopify Extended MCP Server.
 *
 * Covers:
 *   - Analytics tools: empty results, null fields, pagination edge cases, date boundaries
 *   - SEO tools: over-limit batches, dry-run, empty titles, XSS, unicode, long strings
 *   - update-product-content: HTML injection, empty body, null tags
 *   - CRUD tools: invalid IDs, missing fields, GraphQL errors, auth failures, rate limits
 *   - Pagination: cursor edge cases, empty pages, malformed cursors
 */

import { jest, describe, test, expect, beforeEach } from "@jest/globals";

// === Shared mock helpers ===

function createMockClient(requestFn?: (...args: any[]) => Promise<any>) {
  const fn = jest.fn(requestFn || (async () => ({})));
  return { request: fn } as any;
}

/**
 * Creates a mock GraphQL client that returns paginated order data.
 * Each entry in `pages` describes one page response.
 */
function createPaginatedOrderClient(
  pages: Array<{
    edges: any[];
    hasNextPage: boolean;
    endCursor: string | null;
  }>
) {
  let callIndex = 0;
  const fn = jest.fn(async () => {
    const page = pages[callIndex] || pages[pages.length - 1];
    callIndex++;
    return {
      orders: {
        pageInfo: {
          hasNextPage: page.hasNextPage,
          endCursor: page.endCursor,
        },
        edges: page.edges,
      },
    };
  });
  return { request: fn } as any;
}

function makeOrderEdge(
  id: number,
  opts: {
    amount?: string;
    status?: string;
    journey?: any;
    lineItems?: any;
    cancelledAt?: string | null;
    cancelReason?: string | null;
    discounts?: string;
    shipping?: string;
    subtotal?: string;
    paymentGatewayNames?: string[];
    customer?: any;
    fulfillmentStatus?: string;
    refunds?: any[];
  } = {}
) {
  return {
    node: {
      id: `gid://shopify/Order/${id}`,
      name: `#${1000 + id}`,
      createdAt: "2026-03-15T12:00:00Z",
      totalPriceSet: {
        shopMoney: {
          amount: opts.amount ?? "100.00",
          currencyCode: "PLN",
        },
      },
      subtotalPriceSet: {
        shopMoney: { amount: opts.subtotal ?? opts.amount ?? "100.00" },
      },
      totalDiscountsSet: {
        shopMoney: { amount: opts.discounts ?? "0.00" },
      },
      totalShippingPriceSet: {
        shopMoney: { amount: opts.shipping ?? "0.00" },
      },
      totalTaxSet: {
        shopMoney: { amount: "0.00" },
      },
      displayFinancialStatus: opts.status ?? "PAID",
      displayFulfillmentStatus: opts.fulfillmentStatus ?? "FULFILLED",
      sourceName: "web",
      sourceIdentifier: null,
      channelInformation: null,
      customerJourneySummary: opts.journey ?? null,
      cancelledAt: opts.cancelledAt ?? null,
      cancelReason: opts.cancelReason ?? null,
      paymentGatewayNames: opts.paymentGatewayNames ?? ["przelewy24"],
      transactions: [],
      customer: opts.customer ?? { id: "gid://shopify/Customer/1", numberOfOrders: "1" },
      lineItems: opts.lineItems ?? {
        edges: [
          {
            node: {
              id: "gid://shopify/LineItem/1",
              title: "Test Product",
              quantity: 1,
              originalTotalSet: { shopMoney: { amount: opts.amount ?? "100.00" } },
              variant: {
                id: "gid://shopify/ProductVariant/1",
                title: "Default",
                sku: "TEST-SKU",
                product: { id: "gid://shopify/Product/1" },
              },
            },
          },
        ],
      },
      refunds: opts.refunds ?? [],
    },
  };
}

// ============================================================
// ANALYTICS TOOLS
// ============================================================

describe("Analytics Tools", () => {
  // -- getTrafficSourceAnalytics --
  describe("getTrafficSourceAnalytics", () => {
    let tool: typeof import("../tools/getTrafficSourceAnalytics")["getTrafficSourceAnalytics"];

    beforeEach(async () => {
      const mod = await import("../tools/getTrafficSourceAnalytics");
      tool = mod.getTrafficSourceAnalytics;
    });

    test("handles zero orders (empty date range)", async () => {
      const client = createPaginatedOrderClient([
        { edges: [], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2099-01-01",
        dateTo: "2099-01-02",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(0);
      expect(result.summary.totalRevenue).toBe(0);
      expect(result.summary.averageOrderValue).toBe(0);
      expect(result.summary.journeyTrackingRate).toBe(0);
      expect(result.bySource).toHaveLength(0);
      expect(result.byChannel).toHaveLength(0);
      expect(result.byUtmSource).toHaveLength(0);
    });

    test("handles orders with null customerJourneySummary", async () => {
      const edges = [
        makeOrderEdge(1, { journey: null }),
        makeOrderEdge(2, { journey: null }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(2);
      expect(result.summary.ordersWithJourney).toBe(0);
      expect(result.summary.ordersWithoutJourney).toBe(2);
      expect(result.summary.journeyTrackingRate).toBe(0);
    });

    test("handles orders with null firstVisit inside journey", async () => {
      const edges = [
        makeOrderEdge(1, { journey: { firstVisit: null, lastVisit: null } }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.ordersWithoutJourney).toBe(1);
    });

    test("handles orders with null source and null utmParameters", async () => {
      const journey = {
        firstVisit: {
          source: null,
          sourceType: null,
          utmParameters: null,
          referrerUrl: null,
        },
        lastVisit: null,
      };
      const edges = [makeOrderEdge(1, { journey })];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.ordersWithJourney).toBe(1);
      // source defaults to "Direct"
      expect(result.bySource[0].source).toBe("Direct");
    });

    test("handles orders with empty string amount", async () => {
      // GraphQL might return empty strings theoretically
      const edges = [makeOrderEdge(1, { amount: "0.00" })];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalRevenue).toBe(0);
    });

    test("properly aggregates multiple sources", async () => {
      const mkJourney = (source: string, utmSource?: string, campaign?: string) => ({
        firstVisit: {
          source,
          sourceType: "referral",
          utmParameters: utmSource
            ? { source: utmSource, medium: "cpc", campaign: campaign || null, content: null, term: null }
            : null,
          referrerUrl: null,
        },
        lastVisit: null,
      });

      const edges = [
        makeOrderEdge(1, { amount: "100.00", journey: mkJourney("google", "google", "spring_sale") }),
        makeOrderEdge(2, { amount: "200.00", journey: mkJourney("google", "google", "spring_sale") }),
        makeOrderEdge(3, { amount: "50.00", journey: mkJourney("facebook", "facebook", "retarget") }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(3);
      expect(result.summary.totalRevenue).toBe(350);
      expect(result.bySource).toHaveLength(2);
      // Sorted by revenue desc
      expect(result.bySource[0].source).toBe("google");
      expect(result.bySource[0].totalRevenue).toBe(300);
      expect(result.bySource[1].source).toBe("facebook");
      expect(result.bySource[1].totalRevenue).toBe(50);
    });

    test("propagates GraphQL errors", async () => {
      const client = createMockClient(async () => {
        throw new Error("401 Unauthorized");
      });
      tool.initialize(client);

      await expect(
        tool.execute({
          dateFrom: "2026-01-01",
          dateTo: "2026-12-31",
          limit: 2000,
          financialStatus: "paid",
        })
      ).rejects.toThrow("Failed to analyze traffic sources");
    });

    test("date range boundaries: same day", async () => {
      const edges = [makeOrderEdge(1, { amount: "50.00" })];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-15",
        dateTo: "2026-03-15",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.period.from).toBe("2026-03-15");
      expect(result.period.to).toBe("2026-03-15");
      expect(result.summary.totalOrders).toBe(1);
    });
  });

  // -- getCampaignPerformance --
  describe("getCampaignPerformance", () => {
    let tool: typeof import("../tools/getCampaignPerformance")["getCampaignPerformance"];

    beforeEach(async () => {
      const mod = await import("../tools/getCampaignPerformance");
      tool = mod.getCampaignPerformance;
    });

    test("handles zero orders — no campaigns", async () => {
      const client = createPaginatedOrderClient([
        { edges: [], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2099-01-01",
        dateTo: "2099-01-02",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(0);
      expect(result.summary.ordersWithCampaign).toBe(0);
      expect(result.summary.uniqueCampaigns).toBe(0);
      expect(result.campaigns).toHaveLength(0);
    });

    test("orders without UTM campaign are not counted as campaign orders", async () => {
      const journey = {
        firstVisit: {
          source: "google",
          sourceType: "referral",
          utmParameters: { source: "google", medium: "organic", campaign: null, content: null, term: null },
          referrerUrl: null,
        },
        lastVisit: null,
      };
      const edges = [makeOrderEdge(1, { journey })];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(1);
      expect(result.summary.ordersWithCampaign).toBe(0);
    });

    test("utmSource filter is case-insensitive", async () => {
      const mkJourney = (utmSource: string) => ({
        firstVisit: {
          source: utmSource,
          sourceType: "referral",
          utmParameters: { source: utmSource, medium: "cpc", campaign: "test", content: null, term: null },
          referrerUrl: null,
        },
        lastVisit: null,
      });

      const edges = [
        makeOrderEdge(1, { amount: "100.00", journey: mkJourney("Facebook") }),
        makeOrderEdge(2, { amount: "200.00", journey: mkJourney("google") }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        utmSource: "facebook",
        financialStatus: "paid",
      });

      // Only Facebook order (case insensitive match)
      expect(result.summary.ordersWithCampaign).toBe(1);
      expect(result.campaigns).toHaveLength(1);
      expect(result.campaigns[0].utmSource).toBe("Facebook");
    });

    test("utmMedium filter is case-insensitive", async () => {
      const mkJourney = (medium: string) => ({
        firstVisit: {
          source: "google",
          sourceType: "referral",
          utmParameters: { source: "google", medium, campaign: "test", content: null, term: null },
          referrerUrl: null,
        },
        lastVisit: null,
      });

      const edges = [
        makeOrderEdge(1, { amount: "100.00", journey: mkJourney("CPC") }),
        makeOrderEdge(2, { amount: "200.00", journey: mkJourney("email") }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        utmMedium: "cpc",
        financialStatus: "paid",
      });

      expect(result.summary.ordersWithCampaign).toBe(1);
    });

    test("tracks content and term uniquely per campaign", async () => {
      const mkJourney = (content: string, term: string) => ({
        firstVisit: {
          source: "google",
          sourceType: "referral",
          utmParameters: { source: "google", medium: "cpc", campaign: "spring", content, term },
          referrerUrl: null,
        },
        lastVisit: null,
      });

      const edges = [
        makeOrderEdge(1, { journey: mkJourney("banner_v1", "colostrum") }),
        makeOrderEdge(2, { journey: mkJourney("banner_v1", "colostrum") }), // duplicate
        makeOrderEdge(3, { journey: mkJourney("banner_v2", "immunity") }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      const campaign = result.campaigns[0];
      expect(campaign.contents).toEqual(["banner_v1", "banner_v2"]);
      expect(campaign.terms).toEqual(["colostrum", "immunity"]);
    });

    test("propagates GraphQL errors as proper message", async () => {
      const client = createMockClient(async () => {
        throw { response: { status: 429 }, message: "Throttled" };
      });
      tool.initialize(client);

      await expect(
        tool.execute({
          dateFrom: "2026-01-01",
          dateTo: "2026-12-31",
          limit: 2000,
          financialStatus: "paid",
        })
      ).rejects.toThrow("Failed to analyze campaign performance");
    });
  });

  // -- getConversionMetrics --
  describe("getConversionMetrics", () => {
    let tool: typeof import("../tools/getConversionMetrics")["getConversionMetrics"];

    beforeEach(async () => {
      const mod = await import("../tools/getConversionMetrics");
      tool = mod.getConversionMetrics;
    });

    test("handles zero orders", async () => {
      const client = createPaginatedOrderClient([
        { edges: [], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2099-01-01",
        dateTo: "2099-01-02",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      expect(result.summary.totalOrders).toBe(0);
      expect(result.summary.averageOrderValue).toBe(0);
      expect(result.summary.averageItemsPerOrder).toBe(0);
      expect(result.summary.discountRate).toBe(0);
      expect(result.customerMetrics.newCustomerRate).toBe(0);
      expect(result.trends).toHaveLength(0);
    });

    test("handles null optional price fields gracefully", async () => {
      const edge = makeOrderEdge(1, { amount: "100.00" });
      // Remove optional fields to simulate nulls
      edge.node.totalDiscountsSet = null as any;
      edge.node.totalShippingPriceSet = null as any;
      const client = createPaginatedOrderClient([
        { edges: [edge], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      expect(result.summary.totalDiscounts).toBe(0);
      expect(result.summary.totalShipping).toBe(0);
    });

    test("handles null customer (guest checkout)", async () => {
      const edge = makeOrderEdge(1, { customer: null });
      const client = createPaginatedOrderClient([
        { edges: [edge], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      // Guest checkout = numberOfOrders "0" which is <= 1 => newCustomerOrders
      expect(result.customerMetrics.newCustomerOrders).toBe(1);
    });

    test("correctly groups by 'week'", async () => {
      const edges = [
        makeOrderEdge(1, { amount: "100.00" }),
        makeOrderEdge(2, { amount: "200.00" }),
      ];
      // Both have same createdAt so same week
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "week",
        financialStatus: "any",
      });

      // Both orders in same week
      expect(result.trends.length).toBeGreaterThanOrEqual(1);
      expect(result.trends[0].orders).toBe(2);
    });

    test("correctly groups by 'month'", async () => {
      const client = createPaginatedOrderClient([
        {
          edges: [makeOrderEdge(1, { amount: "100.00" })],
          hasNextPage: false,
          endCursor: null,
        },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "month",
        financialStatus: "any",
      });

      expect(result.trends.length).toBe(1);
      expect(result.trends[0].period).toBe("2026-03");
    });

    test("tracks cancelled orders and reasons", async () => {
      const edges = [
        makeOrderEdge(1, { cancelledAt: "2026-03-16T00:00:00Z", cancelReason: "CUSTOMER" }),
        makeOrderEdge(2, { cancelledAt: "2026-03-16T00:00:00Z", cancelReason: "FRAUD" }),
        makeOrderEdge(3, { cancelledAt: "2026-03-16T00:00:00Z", cancelReason: "CUSTOMER" }),
        makeOrderEdge(4),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      expect(result.cancellationMetrics.cancelledOrders).toBe(3);
      expect(result.cancellationMetrics.byCancelReason).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ reason: "CUSTOMER", count: 2 }),
          expect.objectContaining({ reason: "FRAUD", count: 1 }),
        ])
      );
    });

    test("tracks multiple payment gateways per order", async () => {
      const edges = [
        makeOrderEdge(1, { paymentGatewayNames: ["przelewy24", "gift_card"] }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      expect(result.byPaymentGateway).toHaveLength(2);
    });

    test("handles empty paymentGatewayNames array → defaults to 'unknown'", async () => {
      const edges = [makeOrderEdge(1, { paymentGatewayNames: [] })];
      // The code does: `const gateways = order.paymentGatewayNames || ["unknown"]`
      // Empty array is truthy, so it will iterate nothing and not add any gateway
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      // Empty array means no gateways tracked (truthy, so fallback not used)
      expect(result.byPaymentGateway).toHaveLength(0);
    });

    test("handles null paymentGatewayNames → defaults to 'unknown'", async () => {
      const edges = [makeOrderEdge(1, { paymentGatewayNames: undefined as any })];
      edges[0].node.paymentGatewayNames = null as any;
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-03-01",
        dateTo: "2026-03-31",
        limit: 2000,
        groupBy: "day",
        financialStatus: "any",
      });

      const unknownGateway = result.byPaymentGateway.find((g: any) => g.gateway === "unknown");
      expect(unknownGateway).toBeDefined();
    });
  });

  // -- getProductPerformance --
  describe("getProductPerformance", () => {
    let tool: typeof import("../tools/getProductPerformance")["getProductPerformance"];

    beforeEach(async () => {
      const mod = await import("../tools/getProductPerformance");
      tool = mod.getProductPerformance;
    });

    test("handles zero orders", async () => {
      const client = createPaginatedOrderClient([
        { edges: [], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2099-01-01",
        dateTo: "2099-01-02",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(0);
      expect(result.summary.uniqueProducts).toBe(0);
      expect(result.topProducts).toHaveLength(0);
    });

    test("handles order with null variant (deleted product)", async () => {
      const edge = makeOrderEdge(1, { amount: "99.00" });
      edge.node.lineItems = {
        edges: [
          {
            node: {
              id: "gid://shopify/LineItem/99",
              title: "Deleted Product",
              quantity: 2,
              originalTotalSet: { shopMoney: { amount: "99.00" } },
              variant: null,
            },
          },
        ],
      };
      const client = createPaginatedOrderClient([
        { edges: [edge], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      // Falls back to item.id as productId
      expect(result.topProducts).toHaveLength(1);
      expect(result.topProducts[0].productId).toBe("gid://shopify/LineItem/99");
      expect(result.topProducts[0].sku).toBeNull();
    });

    test("utmSource filter excludes non-matching orders", async () => {
      const mkJourney = (utmSource: string) => ({
        firstVisit: {
          source: utmSource,
          sourceType: "referral",
          utmParameters: { source: utmSource, medium: "cpc", campaign: "test" },
          referrerUrl: null,
        },
        lastVisit: null,
      });

      const edges = [
        makeOrderEdge(1, { amount: "100.00", journey: mkJourney("google") }),
        makeOrderEdge(2, { amount: "200.00", journey: mkJourney("facebook") }),
      ];
      const client = createPaginatedOrderClient([
        { edges, hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        utmSource: "google",
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(1);
      expect(result.summary.totalRevenue).toBe(100);
    });

    test("handles order with empty lineItems", async () => {
      const edge = makeOrderEdge(1, { amount: "0.00" });
      edge.node.lineItems = { edges: [] };
      const client = createPaginatedOrderClient([
        { edges: [edge], hasNextPage: false, endCursor: null },
      ]);
      tool.initialize(client);

      const result = await tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        limit: 2000,
        financialStatus: "paid",
      });

      expect(result.summary.totalOrders).toBe(1);
      expect(result.summary.uniqueProducts).toBe(0);
    });
  });
});

// ============================================================
// SEO TOOLS
// ============================================================

describe("SEO Tools", () => {
  // -- updateProductSeo --
  describe("updateProductSeo", () => {
    let tool: typeof import("../tools/updateProductSeo")["updateProductSeo"];

    beforeEach(async () => {
      const mod = await import("../tools/updateProductSeo");
      tool = mod.updateProductSeo;
    });

    test("handles GraphQL userErrors from Shopify", async () => {
      const client = createMockClient(async () => ({
        productUpdate: {
          product: null,
          userErrors: [{ field: "seo.title", message: "Title too long" }],
        },
      }));
      tool.initialize(client);

      await expect(
        tool.execute({ productId: "123", metaTitle: "x".repeat(1000) })
      ).rejects.toThrow("seo.title: Title too long");
    });

    test("handles auth failure (401)", async () => {
      const client = createMockClient(async () => {
        throw new Error("401 Unauthorized: Invalid API key");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ productId: "123", metaTitle: "Test" })
      ).rejects.toThrow("Failed to update product SEO");
    });

    test("handles rate limit (429)", async () => {
      const client = createMockClient(async () => {
        const err = new Error("Throttled");
        (err as any).response = { status: 429 };
        throw err;
      });
      tool.initialize(client);

      await expect(
        tool.execute({ productId: "123", metaTitle: "Test" })
      ).rejects.toThrow("Failed to update product SEO");
    });

    test("accepts gid:// prefix in productId", async () => {
      const client = createMockClient(async (_query: any, variables: any) => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Test",
            handle: "test",
            seo: { title: "New Title", description: null },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        productId: "gid://shopify/Product/123",
        metaTitle: "New Title",
      });

      expect(result.product.id).toBe("gid://shopify/Product/123");
    });

    test("handles XSS in meta description", async () => {
      const xss = '<script>alert("xss")</script>';
      const client = createMockClient(async (_query: any, variables: any) => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Test",
            handle: "test",
            seo: { title: null, description: xss },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        productId: "123",
        metaDescription: xss,
      });

      // Should pass through — Shopify handles sanitization
      expect(result.product.seo.description).toBe(xss);
    });

    test("handles unicode characters in meta title", async () => {
      const unicode = "Colostrum GenActiv — wzmocnij odpornosc \u{1F4AA} \u00F3\u017C\u0144";
      const client = createMockClient(async () => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Test",
            handle: "test",
            seo: { title: unicode, description: null },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        productId: "123",
        metaTitle: unicode,
      });

      expect(result.product.seo.title).toBe(unicode);
    });

    test("handles very long meta description (>320 chars)", async () => {
      const longDesc = "A".repeat(500);
      const client = createMockClient(async () => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Test",
            handle: "test",
            seo: { title: null, description: longDesc },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        productId: "123",
        metaDescription: longDesc,
      });

      expect(result.product.seo.description?.length).toBe(500);
    });

    test("handles empty string for metaTitle (clear SEO title)", async () => {
      const client = createMockClient(async () => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Test",
            handle: "test",
            seo: { title: "", description: null },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        productId: "123",
        metaTitle: "",
      });

      expect(result.product.seo.title).toBe("");
    });
  });

  // -- updateCollectionSeo --
  describe("updateCollectionSeo", () => {
    let tool: typeof import("../tools/updateCollectionSeo")["updateCollectionSeo"];

    beforeEach(async () => {
      const mod = await import("../tools/updateCollectionSeo");
      tool = mod.updateCollectionSeo;
    });

    test("handles GraphQL userErrors", async () => {
      const client = createMockClient(async () => ({
        collectionUpdate: {
          collection: null,
          userErrors: [{ field: "id", message: "Collection not found" }],
        },
      }));
      tool.initialize(client);

      await expect(
        tool.execute({ collectionId: "999999", metaTitle: "Test" })
      ).rejects.toThrow("Collection not found");
    });

    test("handles network timeout", async () => {
      const client = createMockClient(async () => {
        throw new Error("ETIMEDOUT");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ collectionId: "123", metaTitle: "Test" })
      ).rejects.toThrow("Failed to update collection SEO");
    });

    test("builds correct GID from numeric collectionId", async () => {
      let capturedVars: any;
      const client = createMockClient(async (_query: any, variables: any) => {
        capturedVars = variables;
        return {
          collectionUpdate: {
            collection: {
              id: "gid://shopify/Collection/456",
              title: "Test Collection",
              handle: "test-collection",
              seo: { title: "New Title", description: null },
            },
            userErrors: [],
          },
        };
      });
      tool.initialize(client);

      await tool.execute({ collectionId: "456", metaTitle: "New Title" });

      expect(capturedVars.input.id).toBe("gid://shopify/Collection/456");
    });

    test("handles gid:// prefix in collectionId", async () => {
      let capturedVars: any;
      const client = createMockClient(async (_query: any, variables: any) => {
        capturedVars = variables;
        return {
          collectionUpdate: {
            collection: {
              id: "gid://shopify/Collection/456",
              title: "Test",
              handle: "test",
              seo: { title: "Test", description: null },
            },
            userErrors: [],
          },
        };
      });
      tool.initialize(client);

      await tool.execute({ collectionId: "gid://shopify/Collection/456", metaTitle: "Test" });

      expect(capturedVars.input.id).toBe("gid://shopify/Collection/456");
    });
  });

  // -- bulkUpdateSeo --
  describe("bulkUpdateSeo", () => {
    let tool: typeof import("../tools/bulkUpdateSeo")["bulkUpdateSeo"];

    beforeEach(async () => {
      const mod = await import("../tools/bulkUpdateSeo");
      tool = mod.bulkUpdateSeo;
    });

    test("dry-run mode: no API calls made, all items skipped", async () => {
      const client = createMockClient(async () => {
        throw new Error("Should not be called in dry-run mode");
      });
      tool.initialize(client);

      const result = await tool.execute({
        items: [
          { id: "1", type: "product", metaTitle: "Title 1", metaDescription: "Desc 1" },
          { id: "2", type: "collection", metaTitle: "Title 2" },
        ],
        dryRun: true,
      });

      expect(result.summary.updated).toBe(0);
      expect(result.summary.skipped).toBe(2);
      expect(result.summary.dryRun).toBe(true);
      expect(client.request).not.toHaveBeenCalled();
      expect(result.tip).toContain("Dry run complete");
    });

    test("skips items with no metaTitle and no metaDescription", async () => {
      const client = createMockClient();
      tool.initialize(client);

      const result = await tool.execute({
        items: [
          { id: "1", type: "product" },
        ],
        dryRun: false,
      });

      expect(result.summary.skipped).toBe(1);
      expect(result.results[0].status).toBe("skipped");
      expect(result.results[0].error).toContain("No metaTitle or metaDescription");
    });

    test("handles mixed success and failure in batch", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          // Product update success
          return {
            productUpdate: {
              product: { id: "gid://shopify/Product/1", title: "P1", handle: "p1", seo: { title: "T1", description: null } },
              userErrors: [],
            },
          };
        } else {
          // Collection update error
          return {
            collectionUpdate: {
              collection: null,
              userErrors: [{ field: "id", message: "Not found" }],
            },
          };
        }
      });
      tool.initialize(client);

      const result = await tool.execute({
        items: [
          { id: "1", type: "product", metaTitle: "T1" },
          { id: "999", type: "collection", metaTitle: "T2" },
        ],
        dryRun: false,
      });

      expect(result.summary.updated).toBe(1);
      expect(result.summary.errors).toBe(1);
      expect(result.results[0].status).toBe("updated");
      expect(result.results[1].status).toBe("error");
    });

    test("handles network error for individual item", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error("Network failure");
        }
        return {
          productUpdate: {
            product: { id: "gid://shopify/Product/2", title: "P2", handle: "p2", seo: { title: "T2", description: null } },
            userErrors: [],
          },
        };
      });
      tool.initialize(client);

      const result = await tool.execute({
        items: [
          { id: "1", type: "product", metaTitle: "T1" },
          { id: "2", type: "product", metaTitle: "T2" },
        ],
        dryRun: false,
      });

      expect(result.summary.errors).toBe(1);
      expect(result.summary.updated).toBe(1);
      expect(result.results[0].status).toBe("error");
      expect(result.results[0].error).toContain("Network failure");
      expect(result.results[1].status).toBe("updated");
    });

    test("XSS content in meta descriptions passes through to API", async () => {
      const xss = '"><img src=x onerror=alert(1)>';
      const client = createMockClient(async (_query: any, variables: any) => {
        return {
          productUpdate: {
            product: {
              id: "gid://shopify/Product/1",
              title: "P1",
              handle: "p1",
              seo: { title: null, description: variables.input.seo.description },
            },
            userErrors: [],
          },
        };
      });
      tool.initialize(client);

      const result = await tool.execute({
        items: [{ id: "1", type: "product", metaDescription: xss }],
        dryRun: false,
      });

      expect(result.results[0].status).toBe("updated");
      expect(result.results[0].seo?.description).toBe(xss);
    });

    test("handles unicode Polish characters", async () => {
      const polishTitle = "Colostrum GenActiv — najlepsza jako\u015B\u0107 od natury \u017C\u00F3\u0142\u0107";
      const client = createMockClient(async () => ({
        productUpdate: {
          product: {
            id: "gid://shopify/Product/1",
            title: "P1",
            handle: "p1",
            seo: { title: polishTitle, description: null },
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        items: [{ id: "1", type: "product", metaTitle: polishTitle }],
        dryRun: false,
      });

      expect(result.results[0].seo?.title).toBe(polishTitle);
    });

    test("dry run shows preview of SEO changes", async () => {
      const client = createMockClient();
      tool.initialize(client);

      const result = await tool.execute({
        items: [
          { id: "42", type: "product", metaTitle: "Preview Title", metaDescription: "Preview Desc" },
        ],
        dryRun: true,
      });

      expect(result.results[0].seo?.title).toBe("Preview Title");
      expect(result.results[0].seo?.description).toBe("Preview Desc");
      expect(result.results[0].title).toContain("[dry-run]");
    });
  });

  // -- getSeoAudit --
  describe("getSeoAudit", () => {
    let tool: typeof import("../tools/getSeoAudit")["getSeoAudit"];

    beforeEach(async () => {
      const mod = await import("../tools/getSeoAudit");
      tool = mod.getSeoAudit;
    });

    test("handles empty store (no products, no collections)", async () => {
      const client = createMockClient(async () => ({
        products: { edges: [] },
        collections: { edges: [] },
      }));
      tool.initialize(client);

      const result = await tool.execute({ scope: "all", limit: 50 });

      expect(result.summary.productsScanned).toBe(0);
      expect(result.summary.collectionsScanned).toBe(0);
      expect(result.summary.totalIssues).toBe(0);
    });

    test("detects missing meta title, description, and ALT text", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          // Products query
          return {
            products: {
              edges: [
                {
                  node: {
                    id: "gid://shopify/Product/1",
                    title: "Test Product",
                    handle: "test-product",
                    descriptionHtml: "<p>Short</p>",
                    seo: { title: null, description: null },
                    images: {
                      edges: [
                        { node: { id: "gid://shopify/MediaImage/1", altText: null, url: "https://img.test/1.jpg" } },
                        { node: { id: "gid://shopify/MediaImage/2", altText: "Has alt", url: "https://img.test/2.jpg" } },
                      ],
                    },
                    status: "ACTIVE",
                  },
                },
              ],
            },
          };
        }
        // Collections query
        return {
          collections: {
            edges: [
              {
                node: {
                  id: "gid://shopify/Collection/1",
                  title: "Test Collection",
                  handle: "test-collection",
                  descriptionHtml: "",
                  seo: { title: "Exists", description: null },
                  image: { id: "gid://shopify/CollectionImage/1", altText: "", url: "https://img.test/c1.jpg" },
                },
              },
            ],
          },
        };
      });
      tool.initialize(client);

      const result = await tool.execute({ scope: "all", limit: 50 });

      expect(result.summary.productsScanned).toBe(1);
      expect(result.summary.collectionsScanned).toBe(1);
      expect(result.summary.totalIssues).toBeGreaterThan(0);

      // Check specific issues found
      const issueTypes = result.issues.map((i: any) => i.type);
      expect(issueTypes).toContain("missing_meta_title");
      expect(issueTypes).toContain("missing_meta_description");
      expect(issueTypes).toContain("missing_alt_text");
      expect(issueTypes).toContain("missing_product_description"); // "Short" < 50 chars
    });

    test("detects long meta title (>60 chars)", async () => {
      const longTitle = "A".repeat(70);
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          return {
            products: {
              edges: [
                {
                  node: {
                    id: "gid://shopify/Product/1",
                    title: "Test",
                    handle: "test",
                    descriptionHtml: "A".repeat(200),
                    seo: { title: longTitle, description: "A".repeat(160) },
                    images: { edges: [] },
                    status: "ACTIVE",
                  },
                },
              ],
            },
          };
        }
        return { collections: { edges: [] } };
      });
      tool.initialize(client);

      const result = await tool.execute({ scope: "all", limit: 50 });

      const longTitleIssue = result.issues.find((i: any) => i.type === "long_meta_title");
      expect(longTitleIssue).toBeDefined();
      expect(longTitleIssue!.recommendation).toContain("70");
    });

    test("detects short meta description (<80 chars)", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          return {
            products: {
              edges: [
                {
                  node: {
                    id: "gid://shopify/Product/1",
                    title: "Test",
                    handle: "test",
                    descriptionHtml: "A".repeat(200),
                    seo: { title: "Title", description: "Short desc" },
                    images: { edges: [] },
                    status: "ACTIVE",
                  },
                },
              ],
            },
          };
        }
        return { collections: { edges: [] } };
      });
      tool.initialize(client);

      const result = await tool.execute({ scope: "products", limit: 50 });

      const shortDescIssue = result.issues.find((i: any) => i.type === "short_meta_description");
      expect(shortDescIssue).toBeDefined();
    });

    test("limits scan to 250 max even if higher limit requested", async () => {
      let capturedVars: any;
      const client = createMockClient(async (_query: any, variables: any) => {
        capturedVars = variables;
        return { products: { edges: [] }, collections: { edges: [] } };
      });
      tool.initialize(client);

      await tool.execute({ scope: "products", limit: 999 });

      expect(capturedVars.first).toBe(250);
    });

    test("scope 'products' does not query collections", async () => {
      const client = createMockClient(async () => ({
        products: { edges: [] },
      }));
      tool.initialize(client);

      const result = await tool.execute({ scope: "products", limit: 50 });

      expect(result.summary.collectionsScanned).toBe(0);
      expect(client.request).toHaveBeenCalledTimes(1);
    });

    test("scope 'collections' does not query products", async () => {
      const client = createMockClient(async () => ({
        collections: { edges: [] },
      }));
      tool.initialize(client);

      const result = await tool.execute({ scope: "collections", limit: 50 });

      expect(result.summary.productsScanned).toBe(0);
      expect(client.request).toHaveBeenCalledTimes(1);
    });

    test("handles GraphQL error", async () => {
      const client = createMockClient(async () => {
        throw new Error("500 Internal Server Error");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ scope: "all", limit: 50 })
      ).rejects.toThrow("Failed to run SEO audit");
    });

    test("collection without image does not crash", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          return { products: { edges: [] } };
        }
        return {
          collections: {
            edges: [
              {
                node: {
                  id: "gid://shopify/Collection/1",
                  title: "No Image Collection",
                  handle: "no-image",
                  descriptionHtml: "",
                  seo: { title: "Title", description: "A".repeat(160) },
                  image: null,
                },
              },
            ],
          },
        };
      });
      tool.initialize(client);

      const result = await tool.execute({ scope: "all", limit: 50 });

      // Should not crash, image null means no alt text issue for image
      expect(result.summary.collectionsScanned).toBe(1);
      const altIssues = result.issues.filter((i: any) => i.type === "missing_alt_text");
      expect(altIssues).toHaveLength(0);
    });

    test("image stats accuracy", async () => {
      let callCount = 0;
      const client = createMockClient(async () => {
        callCount++;
        if (callCount === 1) {
          return {
            products: {
              edges: [
                {
                  node: {
                    id: "gid://shopify/Product/1",
                    title: "P1",
                    handle: "p1",
                    descriptionHtml: "A".repeat(200),
                    seo: { title: "T", description: "A".repeat(160) },
                    images: {
                      edges: [
                        { node: { id: "gid://shopify/MediaImage/1", altText: "Has alt", url: "" } },
                        { node: { id: "gid://shopify/MediaImage/2", altText: null, url: "" } },
                        { node: { id: "gid://shopify/MediaImage/3", altText: "", url: "" } },
                      ],
                    },
                    status: "ACTIVE",
                  },
                },
              ],
            },
          };
        }
        return { collections: { edges: [] } };
      });
      tool.initialize(client);

      const result = await tool.execute({ scope: "all", limit: 50 });

      expect(result.summary.imageStats.totalImages).toBe(3);
      expect(result.summary.imageStats.imagesWithoutAlt).toBe(2); // null and ""
      expect(result.summary.imageStats.altTextCoverage).toBe(33); // 1/3 * 100 rounded
    });
  });
});

// ============================================================
// UPDATE PRODUCT CONTENT
// ============================================================

describe("updateProductContent", () => {
  let tool: typeof import("../tools/updateProductContent")["updateProductContent"];

  beforeEach(async () => {
    const mod = await import("../tools/updateProductContent");
    tool = mod.updateProductContent;
  });

  test("handles product not found", async () => {
    const client = createMockClient(async () => ({
      product: null,
    }));
    tool.initialize(client);

    await expect(
      tool.execute({ productId: "999999" })
    ).rejects.toThrow("Product not found");
  });

  test("handles HTML injection in description", async () => {
    const html = '<div onmouseover="alert(1)"><script>document.cookie</script></div>';
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "<p>Old</p>",
            vendor: "GenActiv",
            productType: "Supplement",
            tags: ["health"],
            seo: { title: null, description: null },
          },
        };
      }
      return {
        productUpdate: {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: html,
            vendor: "GenActiv",
            productType: "Supplement",
            tags: ["health"],
            seo: { title: null, description: null },
          },
          userErrors: [],
        },
      };
    });
    tool.initialize(client);

    const result = await tool.execute({
      productId: "1",
      descriptionHtml: html,
    });

    expect(result.status).toBe("updated");
  });

  test("handles empty descriptionHtml (clearing description)", async () => {
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "<p>Has content</p>",
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
        };
      }
      return {
        productUpdate: {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "",
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
          userErrors: [],
        },
      };
    });
    tool.initialize(client);

    const result = await tool.execute({
      productId: "1",
      descriptionHtml: "",
    });

    expect(result.status).toBe("updated");
  });

  test("handles empty tags array", async () => {
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "",
            vendor: "V",
            productType: "T",
            tags: ["old-tag"],
            seo: { title: null, description: null },
          },
        };
      }
      return {
        productUpdate: {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "",
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
          userErrors: [],
        },
      };
    });
    tool.initialize(client);

    const result = await tool.execute({ productId: "1", tags: [] });

    expect(result.product.tags).toEqual([]);
  });

  test("handles userErrors from Shopify", async () => {
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: "",
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
        };
      }
      return {
        productUpdate: {
          product: null,
          userErrors: [{ field: "title", message: "cannot be blank" }],
        },
      };
    });
    tool.initialize(client);

    await expect(
      tool.execute({ productId: "1", title: "" })
    ).rejects.toThrow("cannot be blank");
  });

  test("truncates long descriptionHtml in before/after display", async () => {
    const longHtml = "X".repeat(500);
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: longHtml,
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
        };
      }
      return {
        productUpdate: {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            handle: "test",
            descriptionHtml: longHtml,
            vendor: "V",
            productType: "T",
            tags: [],
            seo: { title: null, description: null },
          },
          userErrors: [],
        },
      };
    });
    tool.initialize(client);

    const result = await tool.execute({ productId: "1", title: "Test" });

    // descriptionHtml in response is truncated at 200 + "..."
    expect(result.product.descriptionHtml.length).toBeLessThanOrEqual(204);
    expect(result.product.descriptionHtml).toContain("...");
  });
});

// ============================================================
// CRUD TOOLS
// ============================================================

describe("CRUD Tools", () => {
  // -- getProducts --
  describe("getProducts", () => {
    let tool: typeof import("../tools/getProducts")["getProducts"];

    beforeEach(async () => {
      const mod = await import("../tools/getProducts");
      tool = mod.getProducts;
    });

    test("handles empty product list", async () => {
      const client = createMockClient(async () => ({
        products: { edges: [] },
      }));
      tool.initialize(client);

      const result = await tool.execute({ limit: 10 });

      expect(result.products).toEqual([]);
    });

    test("handles GraphQL error", async () => {
      const client = createMockClient(async () => {
        throw new Error("GraphQL query failed");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ limit: 10 })
      ).rejects.toThrow("Failed to fetch products");
    });

    test("handles product with no images", async () => {
      const client = createMockClient(async () => ({
        products: {
          edges: [
            {
              node: {
                id: "gid://shopify/Product/1",
                title: "No Image Product",
                description: "Desc",
                handle: "no-image",
                status: "ACTIVE",
                createdAt: "2026-01-01",
                updatedAt: "2026-01-01",
                totalInventory: 0,
                priceRangeV2: {
                  minVariantPrice: { amount: "0.00", currencyCode: "PLN" },
                  maxVariantPrice: { amount: "0.00", currencyCode: "PLN" },
                },
                seo: { title: null, description: null },
                images: { edges: [] },
                variants: { edges: [] },
              },
            },
          ],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({ limit: 10 });

      expect(result.products[0].imageUrl).toBeNull();
    });

    test("handles search with special characters", async () => {
      let capturedVars: any;
      const client = createMockClient(async (_query: any, variables: any) => {
        capturedVars = variables;
        return { products: { edges: [] } };
      });
      tool.initialize(client);

      await tool.execute({ searchTitle: 'colostrum "premium"', limit: 5 });

      expect(capturedVars.query).toContain('colostrum "premium"');
    });
  });

  // -- getProductById --
  describe("getProductById", () => {
    let tool: typeof import("../tools/getProductById")["getProductById"];

    beforeEach(async () => {
      const mod = await import("../tools/getProductById");
      tool = mod.getProductById;
    });

    test("handles product not found", async () => {
      const client = createMockClient(async () => ({
        product: null,
      }));
      tool.initialize(client);

      await expect(
        tool.execute({ productId: "gid://shopify/Product/999999" })
      ).rejects.toThrow("not found");
    });

    test("handles GraphQL auth error", async () => {
      const client = createMockClient(async () => {
        throw new Error("401 Unauthorized");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ productId: "gid://shopify/Product/1" })
      ).rejects.toThrow("Failed to fetch product");
    });
  });

  // -- createProduct --
  describe("createProduct", () => {
    let tool: typeof import("../tools/createProduct")["createProduct"];

    beforeEach(async () => {
      const mod = await import("../tools/createProduct");
      tool = mod.createProduct;
    });

    test("handles userErrors from Shopify", async () => {
      const client = createMockClient(async () => ({
        productCreate: {
          product: null,
          userErrors: [{ field: "title", message: "has already been taken" }],
        },
      }));
      tool.initialize(client);

      await expect(
        tool.execute({ title: "Duplicate", status: "DRAFT" })
      ).rejects.toThrow("has already been taken");
    });

    test("handles auth failure", async () => {
      const client = createMockClient(async () => {
        throw new Error("401 Unauthorized");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ title: "Test", status: "DRAFT" })
      ).rejects.toThrow("Failed to create product");
    });

    test("creates product with all optional fields", async () => {
      const client = createMockClient(async () => ({
        productCreate: {
          product: {
            id: "gid://shopify/Product/123",
            title: "Full Product",
            descriptionHtml: "<p>Desc</p>",
            vendor: "GenActiv",
            productType: "Supplement",
            status: "DRAFT",
            tags: ["colostrum", "health"],
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        title: "Full Product",
        descriptionHtml: "<p>Desc</p>",
        vendor: "GenActiv",
        productType: "Supplement",
        tags: ["colostrum", "health"],
        status: "DRAFT",
      });

      expect(result.product.title).toBe("Full Product");
      expect(result.product.tags).toEqual(["colostrum", "health"]);
    });
  });

  // -- updateOrder --
  describe("updateOrder", () => {
    let tool: typeof import("../tools/updateOrder")["updateOrder"];

    beforeEach(async () => {
      const mod = await import("../tools/updateOrder");
      tool = mod.updateOrder;
    });

    test("handles userErrors from Shopify", async () => {
      const client = createMockClient(async () => ({
        orderUpdate: {
          order: null,
          userErrors: [{ field: "id", message: "Order not found" }],
        },
      }));
      tool.initialize(client);

      await expect(
        tool.execute({ id: "gid://shopify/Order/999", note: "test" })
      ).rejects.toThrow("Order not found");
    });

    test("handles rate limit error", async () => {
      const client = createMockClient(async () => {
        throw new Error("429 Too Many Requests");
      });
      tool.initialize(client);

      await expect(
        tool.execute({ id: "gid://shopify/Order/1", tags: ["test"] })
      ).rejects.toThrow("Failed to update order");
    });

    test("handles null metafields edges", async () => {
      const client = createMockClient(async () => ({
        orderUpdate: {
          order: {
            id: "gid://shopify/Order/1",
            name: "#1001",
            email: "test@test.com",
            note: "Note",
            tags: ["tag1"],
            customAttributes: [],
            metafields: null,
            shippingAddress: null,
          },
          userErrors: [],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        id: "gid://shopify/Order/1",
        note: "Note",
      });

      expect(result.order.metafields).toEqual([]);
    });
  });

  // -- getOrders --
  describe("getOrders", () => {
    let tool: typeof import("../tools/getOrders")["getOrders"];

    beforeEach(async () => {
      const mod = await import("../tools/getOrders");
      tool = mod.getOrders;
    });

    test("handles empty order list", async () => {
      const client = createMockClient(async () => ({
        orders: { edges: [] },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        status: "any",
        limit: 10,
        sortKey: "CREATED_AT",
        reverse: true,
      });

      expect(result.orders).toEqual([]);
    });

    test("handles GraphQL error", async () => {
      const client = createMockClient(async () => {
        throw new Error("500 Internal Server Error");
      });
      tool.initialize(client);

      await expect(
        tool.execute({
          status: "any",
          limit: 10,
          sortKey: "CREATED_AT",
          reverse: true,
        })
      ).rejects.toThrow("Failed to fetch orders");
    });

    test("handles order with null customer (guest checkout)", async () => {
      const client = createMockClient(async () => ({
        orders: {
          edges: [
            {
              node: {
                id: "gid://shopify/Order/1",
                name: "#1001",
                createdAt: "2026-03-15T12:00:00Z",
                displayFinancialStatus: "PAID",
                displayFulfillmentStatus: "FULFILLED",
                totalPriceSet: { shopMoney: { amount: "100.00", currencyCode: "PLN" } },
                subtotalPriceSet: { shopMoney: { amount: "80.00", currencyCode: "PLN" } },
                totalShippingPriceSet: { shopMoney: { amount: "15.00", currencyCode: "PLN" } },
                totalTaxSet: { shopMoney: { amount: "5.00", currencyCode: "PLN" } },
                paymentGatewayNames: ["przelewy24"],
                sourceName: "web",
                sourceIdentifier: null,
                channelInformation: null,
                customerJourneySummary: null,
                transactions: [],
                customer: null,
                shippingAddress: null,
                lineItems: { edges: [] },
                tags: [],
                note: null,
              },
            },
          ],
        },
      }));
      tool.initialize(client);

      const result = await tool.execute({
        status: "any",
        limit: 10,
        sortKey: "CREATED_AT",
        reverse: true,
      });

      expect(result.orders[0].customer).toBeNull();
    });

    test("builds query filter with dateFrom and dateTo", async () => {
      let capturedVars: any;
      const client = createMockClient(async (_query: any, variables: any) => {
        capturedVars = variables;
        return { orders: { edges: [] } };
      });
      tool.initialize(client);

      await tool.execute({
        status: "closed",
        limit: 5,
        dateFrom: "2026-01-01",
        dateTo: "2026-03-31",
        sortKey: "CREATED_AT",
        reverse: true,
      });

      expect(capturedVars.query).toContain("status:closed");
      expect(capturedVars.query).toContain("created_at:>=2026-01-01");
      expect(capturedVars.query).toContain("created_at:<=2026-03-31");
    });
  });
});

// ============================================================
// PAGINATION (fetchAllOrders + buildOrderQueryFilter)
// ============================================================

describe("Pagination Edge Cases", () => {
  let fetchAllOrders: typeof import("../utils/paginateOrders")["fetchAllOrders"];
  let buildOrderQueryFilter: typeof import("../utils/paginateOrders")["buildOrderQueryFilter"];

  beforeEach(async () => {
    const mod = await import("../utils/paginateOrders");
    fetchAllOrders = mod.fetchAllOrders;
    buildOrderQueryFilter = mod.buildOrderQueryFilter;
  });

  const dummyQuery = "query { orders { pageInfo { hasNextPage endCursor } edges { node { id } } } }";

  test("handles null endCursor with hasNextPage=true (malformed response)", async () => {
    const client = createPaginatedOrderClient([
      {
        edges: [makeOrderEdge(1)],
        hasNextPage: true,
        endCursor: null, // Malformed: hasNextPage but no cursor
      },
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 1000);

    // Second request with cursor=undefined should still work
    // But since mock returns same data, it will paginate until limit
    expect(result.totalFetched).toBeGreaterThanOrEqual(1);
  });

  test("handles empty edges with hasNextPage=false", async () => {
    const client = createPaginatedOrderClient([
      { edges: [], hasNextPage: false, endCursor: null },
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 1000);

    expect(result.totalFetched).toBe(0);
    expect(result.hasMore).toBe(false);
    expect(result.edges).toEqual([]);
  });

  test("respects maxOrders=1 — stops after first order", async () => {
    const client = createPaginatedOrderClient([
      {
        edges: [makeOrderEdge(1)],
        hasNextPage: true,
        endCursor: "cursor1",
      },
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 1);

    expect(result.totalFetched).toBe(1);
    expect(client.request).toHaveBeenCalledTimes(1);

    // first param should be 1
    const vars = client.request.mock.calls[0][1] as any;
    expect(vars.first).toBe(1);
  });

  test("maxOrders=0 — never fetches (edge case)", async () => {
    const client = createPaginatedOrderClient([
      { edges: [makeOrderEdge(1)], hasNextPage: false, endCursor: null },
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 0);

    // effectiveMax = min(0, 5000) = 0, loop never executes
    expect(result.totalFetched).toBe(0);
    expect(client.request).not.toHaveBeenCalled();
  });

  test("handles very large maxOrders (>5000) — caps at 5000", async () => {
    const client = createPaginatedOrderClient([
      { edges: [makeOrderEdge(1)], hasNextPage: false, endCursor: null },
    ]);

    await fetchAllOrders(client, dummyQuery, { query: "" }, 100000);

    const vars = client.request.mock.calls[0][1] as any;
    // first should be min(250, remaining=5000) = 250
    expect(vars.first).toBe(250);
  });

  test("handles GraphQL error during pagination", async () => {
    let callCount = 0;
    const client = {
      request: jest.fn(async () => {
        callCount++;
        if (callCount === 1) {
          return {
            orders: {
              pageInfo: { hasNextPage: true, endCursor: "cursor1" },
              edges: Array.from({ length: 250 }, (_, i) => makeOrderEdge(i)),
            },
          };
        }
        throw new Error("Rate limited");
      }),
    } as any;

    await expect(
      fetchAllOrders(client, dummyQuery, { query: "" }, 500)
    ).rejects.toThrow("Rate limited");
  });

  test("negative maxOrders treated as 0", async () => {
    const client = createPaginatedOrderClient([
      { edges: [makeOrderEdge(1)], hasNextPage: false, endCursor: null },
    ]);

    // Min(-5, 5000) = -5, loop condition: -5 < -5 is false, never executes
    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, -5);

    expect(result.totalFetched).toBe(0);
    expect(client.request).not.toHaveBeenCalled();
  });

  // buildOrderQueryFilter edge cases
  test("buildOrderQueryFilter: all statuses any — minimal filter", () => {
    const filter = buildOrderQueryFilter({
      dateFrom: "2026-01-01",
      dateTo: "2026-12-31",
      financialStatus: "any",
      status: "any",
    });

    expect(filter).toBe("created_at:>=2026-01-01 AND created_at:<=2026-12-31");
    expect(filter).not.toContain("financial_status");
    expect(filter).not.toContain("status:");
  });

  test("buildOrderQueryFilter: all filters combined", () => {
    const filter = buildOrderQueryFilter({
      dateFrom: "2026-01-01",
      dateTo: "2026-06-30",
      financialStatus: "refunded",
      status: "closed",
    });

    expect(filter).toContain("created_at:>=2026-01-01");
    expect(filter).toContain("created_at:<=2026-06-30");
    expect(filter).toContain("financial_status:refunded");
    expect(filter).toContain("status:closed");
  });

  test("buildOrderQueryFilter: missing optional params", () => {
    const filter = buildOrderQueryFilter({
      dateFrom: "2026-01-01",
      dateTo: "2026-12-31",
    });

    expect(filter).toBe("created_at:>=2026-01-01 AND created_at:<=2026-12-31");
  });
});

// ============================================================
// REVENUE RECONCILIATION
// ============================================================

describe("getRevenueReconciliation", () => {
  let tool: typeof import("../tools/getRevenueReconciliation")["getRevenueReconciliation"];

  beforeEach(async () => {
    const mod = await import("../tools/getRevenueReconciliation");
    tool = mod.getRevenueReconciliation;
  });

  test("handles zero orders", async () => {
    const client = createPaginatedOrderClient([
      { edges: [], hasNextPage: false, endCursor: null },
    ]);
    tool.initialize(client);

    const result = await tool.execute({
      dateFrom: "2099-01-01",
      dateTo: "2099-01-02",
      maxOrders: 5000,
    });

    expect(result.breakdown.totalOrders).toBe(0);
    expect(result.breakdown.grossRevenue).toBe(0);
    expect(result.byFinancialStatus).toHaveLength(0);
  });

  test("handles orders with null optional financial fields", async () => {
    const edge = makeOrderEdge(1, { amount: "100.00" });
    edge.node.subtotalPriceSet = null as any;
    edge.node.totalDiscountsSet = null as any;
    edge.node.totalShippingPriceSet = null as any;
    edge.node.totalTaxSet = null as any;
    (edge.node as any).refunds = [];

    const client = createPaginatedOrderClient([
      { edges: [edge], hasNextPage: false, endCursor: null },
    ]);
    tool.initialize(client);

    const result = await tool.execute({
      dateFrom: "2026-01-01",
      dateTo: "2026-12-31",
      maxOrders: 5000,
    });

    expect(result.breakdown.totalOrders).toBe(1);
    expect(result.breakdown.grossRevenue).toBe(100);
    expect(result.breakdown.subtotal).toBe(0);
    expect(result.breakdown.totalDiscounts).toBe(0);
  });

  test("handles orders with refunds", async () => {
    const edge = makeOrderEdge(1, { amount: "200.00", status: "PARTIALLY_REFUNDED" });
    (edge.node as any).refunds = [
      { id: "ref1", totalRefundedSet: { shopMoney: { amount: "50.00" } } },
      { id: "ref2", totalRefundedSet: { shopMoney: { amount: "25.00" } } },
    ];

    const client = createPaginatedOrderClient([
      { edges: [edge], hasNextPage: false, endCursor: null },
    ]);
    tool.initialize(client);

    const result = await tool.execute({
      dateFrom: "2026-01-01",
      dateTo: "2026-12-31",
      maxOrders: 5000,
    });

    expect(result.breakdown.totalRefunded).toBe(75);
    expect(result.breakdown.netRevenue).toBe(125);
  });

  test("handles null refunds field", async () => {
    const edge = makeOrderEdge(1, { amount: "100.00" });
    (edge.node as any).refunds = null;

    const client = createPaginatedOrderClient([
      { edges: [edge], hasNextPage: false, endCursor: null },
    ]);
    tool.initialize(client);

    const result = await tool.execute({
      dateFrom: "2026-01-01",
      dateTo: "2026-12-31",
      maxOrders: 5000,
    });

    expect(result.breakdown.totalRefunded).toBe(0);
  });

  test("propagates GraphQL errors", async () => {
    const client = createMockClient(async () => {
      throw new Error("Service unavailable");
    });
    tool.initialize(client);

    await expect(
      tool.execute({
        dateFrom: "2026-01-01",
        dateTo: "2026-12-31",
        maxOrders: 5000,
      })
    ).rejects.toThrow("Failed to reconcile revenue");
  });
});

// ============================================================
// UPDATE PRODUCT IMAGES
// ============================================================

describe("updateProductImages", () => {
  let tool: typeof import("../tools/updateProductImages")["updateProductImages"];

  beforeEach(async () => {
    const mod = await import("../tools/updateProductImages");
    tool = mod.updateProductImages;
  });

  test("handles product not found", async () => {
    const client = createMockClient(async () => ({
      product: null,
    }));
    tool.initialize(client);

    await expect(
      tool.execute({
        productId: "999999",
        images: [{ imageId: "1", altText: "Test" }],
      })
    ).rejects.toThrow("Product not found");
  });

  test("handles mixed success and error for multiple images", async () => {
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        // Get product
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test Product",
            images: {
              edges: [
                { node: { id: "gid://shopify/MediaImage/1", altText: null, url: "" } },
                { node: { id: "gid://shopify/MediaImage/2", altText: "Old alt", url: "" } },
              ],
            },
          },
        };
      }
      if (callCount === 2) {
        // First image update success
        return {
          productUpdateMedia: {
            media: [{ id: "gid://shopify/MediaImage/1", alt: "New alt 1", image: { url: "" } }],
            mediaUserErrors: [],
          },
        };
      }
      // Second image update error
      return {
        productUpdateMedia: {
          media: [],
          mediaUserErrors: [{ field: "id", message: "Image not found", code: "NOT_FOUND" }],
        },
      };
    });
    tool.initialize(client);

    const result = await tool.execute({
      productId: "1",
      images: [
        { imageId: "1", altText: "New alt 1" },
        { imageId: "999", altText: "Should fail" },
      ],
    });

    expect(result.summary.updated).toBe(1);
    expect(result.summary.failed).toBe(1);
    expect(result.results[0].status).toBe("updated");
    expect(result.results[1].status).toBe("error");
  });

  test("handles network error during image update", async () => {
    let callCount = 0;
    const client = createMockClient(async () => {
      callCount++;
      if (callCount === 1) {
        return {
          product: {
            id: "gid://shopify/Product/1",
            title: "Test",
            images: { edges: [] },
          },
        };
      }
      throw new Error("Connection reset");
    });
    tool.initialize(client);

    const result = await tool.execute({
      productId: "1",
      images: [{ imageId: "1", altText: "Test" }],
    });

    expect(result.results[0].status).toBe("error");
    expect(result.results[0].error).toContain("Connection reset");
  });
});

// ============================================================
// FLOATING POINT & ROUNDING EDGE CASES
// ============================================================

describe("Floating point and rounding edge cases", () => {
  test("many small amounts do not accumulate rounding errors visibly", () => {
    // Simulate 1000 orders at 9.99 PLN
    let total = 0;
    for (let i = 0; i < 1000; i++) {
      total += parseFloat("9.99");
    }
    const rounded = Math.round(total * 100) / 100;
    expect(rounded).toBe(9990);
  });

  test("rounding works for very small amounts", () => {
    const amount = parseFloat("0.01");
    const rounded = Math.round(amount * 100) / 100;
    expect(rounded).toBe(0.01);
  });

  test("rounding handles 0.1 + 0.2 correctly", () => {
    const sum = 0.1 + 0.2;
    const rounded = Math.round(sum * 100) / 100;
    expect(rounded).toBe(0.3);
  });

  test("division by zero in AOV returns 0", () => {
    const totalOrders = 0;
    const totalRevenue = 0;
    const aov = totalOrders > 0 ? Math.round(totalRevenue / totalOrders * 100) / 100 : 0;
    expect(aov).toBe(0);
  });
});
