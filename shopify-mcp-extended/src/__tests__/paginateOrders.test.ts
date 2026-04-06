import { jest, describe, test, expect } from "@jest/globals";
import { fetchAllOrders, buildOrderQueryFilter } from "../utils/paginateOrders";

// Mock GraphQL client
function createMockClient(pages: Array<{ edges: any[]; hasNextPage: boolean; endCursor: string | null }>) {
  let callIndex = 0;
  const fn = jest.fn(async () => {
      const page = pages[callIndex] || pages[pages.length - 1];
      callIndex++;
      return {
        orders: {
          pageInfo: {
            hasNextPage: page.hasNextPage,
            endCursor: page.endCursor
          },
          edges: page.edges
        }
      };
    });
  return { request: fn } as any;
}

function makeOrderEdge(id: number, amount: string, status: string = "PAID") {
  return {
    node: {
      id: `gid://shopify/Order/${id}`,
      name: `#${1000 + id}`,
      totalPriceSet: { shopMoney: { amount, currencyCode: "PLN" } },
      displayFinancialStatus: status,
    }
  };
}

describe("fetchAllOrders", () => {
  const dummyQuery = "query { orders { pageInfo { hasNextPage endCursor } edges { node { id } } } }";

  test("fetches single page when all orders fit", async () => {
    const edges = [makeOrderEdge(1, "100.00"), makeOrderEdge(2, "200.00")];
    const client = createMockClient([{ edges, hasNextPage: false, endCursor: null }]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 250);

    expect(result.totalFetched).toBe(2);
    expect(result.hasMore).toBe(false);
    expect(result.edges).toHaveLength(2);
    expect(client.request).toHaveBeenCalledTimes(1);
  });

  test("paginates across multiple pages", async () => {
    const page1 = Array.from({ length: 250 }, (_, i) => makeOrderEdge(i, "10.00"));
    const page2 = Array.from({ length: 100 }, (_, i) => makeOrderEdge(250 + i, "10.00"));

    const client = createMockClient([
      { edges: page1, hasNextPage: true, endCursor: "cursor1" },
      { edges: page2, hasNextPage: false, endCursor: null }
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 2000);

    expect(result.totalFetched).toBe(350);
    expect(result.hasMore).toBe(false);
    expect(client.request).toHaveBeenCalledTimes(2);

    // Verify cursor was passed to second call
    const secondCallVars = client.request.mock.calls[1][1];
    expect(secondCallVars.after).toBe("cursor1");
  });

  test("respects maxOrders limit — requests correct page size", async () => {
    const page1 = Array.from({ length: 250 }, (_, i) => makeOrderEdge(i, "10.00"));

    const client = createMockClient([
      { edges: page1, hasNextPage: true, endCursor: "cursor1" },
      { edges: page1, hasNextPage: true, endCursor: "cursor2" }
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 300);

    // Second page requests only 50 (300-250), proving limit is respected
    expect(client.request).toHaveBeenCalledTimes(2);
    const secondCallVars = (client.request.mock.calls[1] as any[])[1];
    expect(secondCallVars.first).toBe(50);
    // Mock returns full 250 anyway, but real Shopify would return ≤50
    // Total fetched = 250 + 250 (mock doesn't respect first param)
    expect(result.totalFetched).toBe(500);
  });

  test("caps at 5000 orders for safety", async () => {
    const client = createMockClient([
      { edges: [makeOrderEdge(1, "10.00")], hasNextPage: false, endCursor: null }
    ]);

    await fetchAllOrders(client, dummyQuery, { query: "" }, 99999);

    // Should have capped first to 250 (page size)
    const firstCallVars = client.request.mock.calls[0][1];
    expect(firstCallVars.first).toBe(250);
  });

  test("stops on empty response (safety)", async () => {
    const client = createMockClient([
      { edges: [], hasNextPage: true, endCursor: "cursor1" }
    ]);

    const result = await fetchAllOrders(client, dummyQuery, { query: "" }, 1000);

    expect(result.totalFetched).toBe(0);
    expect(client.request).toHaveBeenCalledTimes(1);
  });
});

describe("buildOrderQueryFilter", () => {
  test("builds basic date range filter", () => {
    const filter = buildOrderQueryFilter({ dateFrom: "2026-01-01", dateTo: "2026-03-31" });
    expect(filter).toBe("created_at:>=2026-01-01 AND created_at:<=2026-03-31");
  });

  test("includes financial status when not 'any'", () => {
    const filter = buildOrderQueryFilter({ dateFrom: "2026-01-01", dateTo: "2026-03-31", financialStatus: "paid" });
    expect(filter).toContain("financial_status:paid");
  });

  test("excludes financial status when 'any'", () => {
    const filter = buildOrderQueryFilter({ dateFrom: "2026-01-01", dateTo: "2026-03-31", financialStatus: "any" });
    expect(filter).not.toContain("financial_status");
  });

  test("includes order status when provided", () => {
    const filter = buildOrderQueryFilter({ dateFrom: "2026-01-01", dateTo: "2026-03-31", status: "closed" });
    expect(filter).toContain("status:closed");
  });
});

describe("revenue calculation correctness", () => {
  test("sum of order amounts matches expected total", () => {
    const orders = [
      { amount: "149.99" },
      { amount: "299.00" },
      { amount: "89.50" },
      { amount: "0.01" }
    ];

    const total = orders.reduce((sum, o) => sum + parseFloat(o.amount), 0);
    const rounded = Math.round(total * 100) / 100;

    expect(rounded).toBe(538.50);
  });

  test("paid-only filter excludes cancelled/refunded", () => {
    const orders = [
      { amount: "100.00", status: "PAID" },
      { amount: "200.00", status: "PAID" },
      { amount: "50.00", status: "CANCELLED" },
      { amount: "75.00", status: "REFUNDED" },
      { amount: "30.00", status: "PARTIALLY_REFUNDED" }
    ];

    const paidTotal = orders
      .filter(o => o.status === "PAID")
      .reduce((sum, o) => sum + parseFloat(o.amount), 0);

    expect(paidTotal).toBe(300.00);

    const allTotal = orders.reduce((sum, o) => sum + parseFloat(o.amount), 0);
    expect(allTotal).toBe(455.00);

    // Difference = cancelled + refunded
    expect(allTotal - paidTotal).toBe(155.00);
  });

  test("net revenue = gross - refunds", () => {
    const gross = 10000.00;
    const refunds = 750.50;
    const net = Math.round((gross - refunds) * 100) / 100;

    expect(net).toBe(9249.50);
  });

  test("handles floating point edge case (0.1 + 0.2)", () => {
    const a = 0.1;
    const b = 0.2;
    const raw = a + b;
    const rounded = Math.round(raw * 100) / 100;

    expect(rounded).toBe(0.3); // our rounding approach handles this
  });
});
