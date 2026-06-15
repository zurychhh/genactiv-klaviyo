import { gql } from "graphql-request";
import { z } from "zod";
// Input schema for getOrders
const GetOrdersInputSchema = z.object({
    status: z.enum(["any", "open", "closed", "cancelled"]).default("any"),
    limit: z.number().default(10),
    dateFrom: z.string().optional().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().optional().describe("End date in ISO format (e.g., 2024-12-31)"),
    sortKey: z.enum(["CREATED_AT", "UPDATED_AT", "PROCESSED_AT", "TOTAL_PRICE", "ID"]).default("CREATED_AT"),
    reverse: z.boolean().default(true).describe("Sort in descending order (newest first)")
});
// Will be initialized in index.ts
let shopifyClient;
const getOrders = {
    name: "get-orders",
    description: "Get orders with optional filtering by status",
    schema: GetOrdersInputSchema,
    // Add initialize method to set up the GraphQL client
    initialize(client) {
        shopifyClient = client;
    },
    execute: async (input) => {
        try {
            const { status, limit, dateFrom, dateTo, sortKey, reverse } = input;
            // Build query filters
            const filters = [];
            if (status !== "any") {
                filters.push(`status:${status}`);
            }
            if (dateFrom) {
                filters.push(`created_at:>=${dateFrom}`);
            }
            if (dateTo) {
                filters.push(`created_at:<=${dateTo}`);
            }
            const queryFilter = filters.join(" AND ");
            const query = gql `
        query GetOrders($first: Int!, $query: String, $sortKey: OrderSortKeys, $reverse: Boolean) {
          orders(first: $first, query: $query, sortKey: $sortKey, reverse: $reverse) {
            edges {
              node {
                id
                name
                createdAt
                displayFinancialStatus
                displayFulfillmentStatus
                totalPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                subtotalPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                totalShippingPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                totalTaxSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                # === EXTENDED FIELDS FOR SOURCE/PAYMENT TRACKING ===
                paymentGatewayNames
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
                transactions(first: 5) {
                  id
                  status
                  kind
                  gateway
                  formattedGateway
                  paymentId
                  createdAt
                  amountSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
                # === END EXTENDED FIELDS ===
                customer {
                  id
                  firstName
                  lastName
                  email
                }
                shippingAddress {
                  address1
                  address2
                  city
                  provinceCode
                  zip
                  country
                  phone
                }
                lineItems(first: 10) {
                  edges {
                    node {
                      id
                      title
                      quantity
                      originalTotalSet {
                        shopMoney {
                          amount
                          currencyCode
                        }
                      }
                      variant {
                        id
                        title
                        sku
                      }
                    }
                  }
                }
                tags
                note
              }
            }
          }
        }
      `;
            const variables = {
                first: limit,
                query: queryFilter || undefined,
                sortKey: sortKey,
                reverse: reverse
            };
            const data = (await shopifyClient.request(query, variables));
            // Extract and format order data
            const orders = data.orders.edges.map((edge) => {
                const order = edge.node;
                // Format line items
                const lineItems = order.lineItems.edges.map((lineItemEdge) => {
                    const lineItem = lineItemEdge.node;
                    return {
                        id: lineItem.id,
                        title: lineItem.title,
                        quantity: lineItem.quantity,
                        originalTotal: lineItem.originalTotalSet.shopMoney,
                        variant: lineItem.variant
                            ? {
                                id: lineItem.variant.id,
                                title: lineItem.variant.title,
                                sku: lineItem.variant.sku
                            }
                            : null
                    };
                });
                return {
                    id: order.id,
                    name: order.name,
                    createdAt: order.createdAt,
                    financialStatus: order.displayFinancialStatus,
                    fulfillmentStatus: order.displayFulfillmentStatus,
                    totalPrice: order.totalPriceSet.shopMoney,
                    subtotalPrice: order.subtotalPriceSet.shopMoney,
                    totalShippingPrice: order.totalShippingPriceSet.shopMoney,
                    totalTax: order.totalTaxSet.shopMoney,
                    // === EXTENDED: Source & Payment Info ===
                    paymentGatewayNames: order.paymentGatewayNames || [],
                    sourceName: order.sourceName,
                    sourceIdentifier: order.sourceIdentifier,
                    channel: order.channelInformation ? {
                        id: order.channelInformation.channelId,
                        name: order.channelInformation.channelDefinition?.channelName,
                        handle: order.channelInformation.channelDefinition?.handle
                    } : null,
                    customerJourney: order.customerJourneySummary ? {
                        firstVisit: order.customerJourneySummary.firstVisit ? {
                            source: order.customerJourneySummary.firstVisit.source,
                            sourceType: order.customerJourneySummary.firstVisit.sourceType,
                            referrerUrl: order.customerJourneySummary.firstVisit.referrerUrl,
                            utm: order.customerJourneySummary.firstVisit.utmParameters
                        } : null,
                        lastVisit: order.customerJourneySummary.lastVisit ? {
                            source: order.customerJourneySummary.lastVisit.source,
                            sourceType: order.customerJourneySummary.lastVisit.sourceType,
                            referrerUrl: order.customerJourneySummary.lastVisit.referrerUrl,
                            utm: order.customerJourneySummary.lastVisit.utmParameters
                        } : null
                    } : null,
                    transactions: order.transactions ? order.transactions.map((txn) => ({
                        id: txn.id,
                        status: txn.status,
                        kind: txn.kind,
                        gateway: txn.gateway,
                        formattedGateway: txn.formattedGateway,
                        paymentId: txn.paymentId,
                        createdAt: txn.createdAt,
                        amount: txn.amountSet?.shopMoney
                    })) : [],
                    // === END EXTENDED ===
                    customer: order.customer
                        ? {
                            id: order.customer.id,
                            firstName: order.customer.firstName,
                            lastName: order.customer.lastName,
                            email: order.customer.email
                        }
                        : null,
                    shippingAddress: order.shippingAddress,
                    lineItems,
                    tags: order.tags,
                    note: order.note
                };
            });
            return { orders };
        }
        catch (error) {
            console.error("Error fetching orders:", error);
            throw new Error(`Failed to fetch orders: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
};
export { getOrders };
