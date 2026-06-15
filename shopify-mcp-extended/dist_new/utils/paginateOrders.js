/**
 * Cursor-based pagination helper for Shopify orders GraphQL queries.
 * Fetches ALL orders matching the query, not just the first 250.
 *
 * @param client - GraphQL client instance
 * @param query - GraphQL query string (MUST include pageInfo { hasNextPage endCursor } and $after: String parameter)
 * @param variables - Query variables (without 'after')
 * @param maxOrders - Maximum total orders to fetch (default: 2000, safety cap: 5000)
 * @param pageSize - Orders per page (max 250, Shopify limit)
 * @returns Array of order edge nodes
 */
export async function fetchAllOrders(client, query, variables, maxOrders = 2000, pageSize = 250) {
    const effectiveMax = Math.min(maxOrders, 5000); // Safety cap
    const effectivePageSize = Math.min(pageSize, 250); // Shopify max per page
    let allEdges = [];
    let cursor = null;
    let hasMore = true;
    while (hasMore && allEdges.length < effectiveMax) {
        const remaining = effectiveMax - allEdges.length;
        const fetchCount = Math.min(effectivePageSize, remaining);
        const pageVariables = {
            ...variables,
            first: fetchCount,
            after: cursor || undefined
        };
        const data = (await client.request(query, pageVariables));
        const edges = data.orders.edges || [];
        allEdges = allEdges.concat(edges);
        hasMore = data.orders.pageInfo.hasNextPage && edges.length > 0;
        cursor = data.orders.pageInfo.endCursor;
        // Safety: if no new edges returned, stop
        if (edges.length === 0)
            break;
    }
    return {
        edges: allEdges,
        totalFetched: allEdges.length,
        hasMore: hasMore && allEdges.length >= effectiveMax
    };
}
/**
 * Builds a Shopify order query filter string from common parameters.
 */
export function buildOrderQueryFilter(params) {
    const filters = [];
    filters.push(`created_at:>=${params.dateFrom}`);
    filters.push(`created_at:<=${params.dateTo}`);
    if (params.financialStatus && params.financialStatus !== "any") {
        filters.push(`financial_status:${params.financialStatus}`);
    }
    if (params.status && params.status !== "any") {
        filters.push(`status:${params.status}`);
    }
    return filters.join(" AND ");
}
