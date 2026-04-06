#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import dotenv from "dotenv";
import { GraphQLClient } from "graphql-request";
import minimist from "minimist";
import { z } from "zod";

// Import tools
import { getCustomerOrders } from "./tools/getCustomerOrders.js";
import { getCustomers } from "./tools/getCustomers.js";
import { getOrderById } from "./tools/getOrderById.js";
import { getOrders } from "./tools/getOrders.js";
import { getProductById } from "./tools/getProductById.js";
import { getProducts } from "./tools/getProducts.js";
import { updateCustomer } from "./tools/updateCustomer.js";
import { updateOrder } from "./tools/updateOrder.js";
import { createProduct } from "./tools/createProduct.js";
// SEO update tools
import { updateProductSeo } from "./tools/updateProductSeo.js";
import { updateCollectionSeo } from "./tools/updateCollectionSeo.js";
import { updateProductImages } from "./tools/updateProductImages.js";
import { getSeoAudit } from "./tools/getSeoAudit.js";
import { getRevenueReconciliation } from "./tools/getRevenueReconciliation.js";
// Analytics tools
import { getTrafficSourceAnalytics } from "./tools/getTrafficSourceAnalytics.js";
import { getCampaignPerformance } from "./tools/getCampaignPerformance.js";
import { getConversionMetrics } from "./tools/getConversionMetrics.js";
import { getProductPerformance } from "./tools/getProductPerformance.js";

// Parse command line arguments
const argv = minimist(process.argv.slice(2));

// Load environment variables from .env file (if it exists)
dotenv.config();

// Define environment variables - from command line or .env file
const SHOPIFY_ACCESS_TOKEN =
  argv.accessToken || process.env.SHOPIFY_ACCESS_TOKEN;
const MYSHOPIFY_DOMAIN = argv.domain || process.env.MYSHOPIFY_DOMAIN;

// Store in process.env for backwards compatibility
process.env.SHOPIFY_ACCESS_TOKEN = SHOPIFY_ACCESS_TOKEN;
process.env.MYSHOPIFY_DOMAIN = MYSHOPIFY_DOMAIN;

// Validate required environment variables
if (!SHOPIFY_ACCESS_TOKEN) {
  console.error("Error: SHOPIFY_ACCESS_TOKEN is required.");
  console.error("Please provide it via command line argument or .env file.");
  console.error("  Command line: --accessToken=your_token");
  process.exit(1);
}

if (!MYSHOPIFY_DOMAIN) {
  console.error("Error: MYSHOPIFY_DOMAIN is required.");
  console.error("Please provide it via command line argument or .env file.");
  console.error("  Command line: --domain=your-store.myshopify.com");
  process.exit(1);
}

// Create Shopify GraphQL client
const shopifyClient = new GraphQLClient(
  `https://${MYSHOPIFY_DOMAIN}/admin/api/2023-07/graphql.json`,
  {
    headers: {
      "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
      "Content-Type": "application/json"
    }
  }
);

// Initialize tools with shopifyClient
getProducts.initialize(shopifyClient);
getProductById.initialize(shopifyClient);
getCustomers.initialize(shopifyClient);
getOrders.initialize(shopifyClient);
getOrderById.initialize(shopifyClient);
updateOrder.initialize(shopifyClient);
getCustomerOrders.initialize(shopifyClient);
updateCustomer.initialize(shopifyClient);
createProduct.initialize(shopifyClient);
// Initialize SEO update tools
updateProductSeo.initialize(shopifyClient);
updateCollectionSeo.initialize(shopifyClient);
updateProductImages.initialize(shopifyClient);
getSeoAudit.initialize(shopifyClient);
getRevenueReconciliation.initialize(shopifyClient);
// Initialize analytics tools
getTrafficSourceAnalytics.initialize(shopifyClient);
getCampaignPerformance.initialize(shopifyClient);
getConversionMetrics.initialize(shopifyClient);
getProductPerformance.initialize(shopifyClient);

// Set up MCP server
const server = new McpServer({
  name: "shopify",
  version: "1.0.0",
  description:
    "MCP Server for Shopify API, enabling interaction with store data through GraphQL API"
});

// Add tools individually, using their schemas directly
server.tool(
  "get-products",
  {
    searchTitle: z.string().optional(),
    limit: z.number().default(10)
  },
  async (args) => {
    const result = await getProducts.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

server.tool(
  "get-product-by-id",
  {
    productId: z.string().min(1)
  },
  async (args) => {
    const result = await getProductById.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

server.tool(
  "get-customers",
  {
    searchQuery: z.string().optional(),
    limit: z.number().default(10)
  },
  async (args) => {
    const result = await getCustomers.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

server.tool(
  "get-orders",
  {
    status: z.enum(["any", "open", "closed", "cancelled"]).default("any"),
    limit: z.number().default(10),
    dateFrom: z.string().optional().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().optional().describe("End date in ISO format (e.g., 2024-12-31)"),
    sortKey: z.enum(["CREATED_AT", "UPDATED_AT", "PROCESSED_AT", "TOTAL_PRICE", "ID"]).default("CREATED_AT"),
    reverse: z.boolean().default(true).describe("Sort in descending order (newest first)")
  },
  async (args) => {
    const result = await getOrders.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Add the getOrderById tool
server.tool(
  "get-order-by-id",
  {
    orderId: z.string().min(1)
  },
  async (args) => {
    const result = await getOrderById.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Add the updateOrder tool
server.tool(
  "update-order",
  {
    id: z.string().min(1),
    tags: z.array(z.string()).optional(),
    email: z.string().email().optional(),
    note: z.string().optional(),
    customAttributes: z
      .array(
        z.object({
          key: z.string(),
          value: z.string()
        })
      )
      .optional(),
    metafields: z
      .array(
        z.object({
          id: z.string().optional(),
          namespace: z.string().optional(),
          key: z.string().optional(),
          value: z.string(),
          type: z.string().optional()
        })
      )
      .optional(),
    shippingAddress: z
      .object({
        address1: z.string().optional(),
        address2: z.string().optional(),
        city: z.string().optional(),
        company: z.string().optional(),
        country: z.string().optional(),
        firstName: z.string().optional(),
        lastName: z.string().optional(),
        phone: z.string().optional(),
        province: z.string().optional(),
        zip: z.string().optional()
      })
      .optional()
  },
  async (args) => {
    const result = await updateOrder.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Add the getCustomerOrders tool
server.tool(
  "get-customer-orders",
  {
    customerId: z
      .string()
      .regex(/^\d+$/, "Customer ID must be numeric")
      .describe("Shopify customer ID, numeric excluding gid prefix"),
    limit: z.number().default(10)
  },
  async (args) => {
    const result = await getCustomerOrders.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Add the updateCustomer tool
server.tool(
  "update-customer",
  {
    id: z
      .string()
      .regex(/^\d+$/, "Customer ID must be numeric")
      .describe("Shopify customer ID, numeric excluding gid prefix"),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    email: z.string().email().optional(),
    phone: z.string().optional(),
    tags: z.array(z.string()).optional(),
    note: z.string().optional(),
    taxExempt: z.boolean().optional(),
    metafields: z
      .array(
        z.object({
          id: z.string().optional(),
          namespace: z.string().optional(),
          key: z.string().optional(),
          value: z.string(),
          type: z.string().optional()
        })
      )
      .optional()
  },
  async (args) => {
    const result = await updateCustomer.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Add the createProduct tool
server.tool(
  "create-product",
  {
    title: z.string().min(1),
    descriptionHtml: z.string().optional(),
    vendor: z.string().optional(),
    productType: z.string().optional(),
    tags: z.array(z.string()).optional(),
    status: z.enum(["ACTIVE", "DRAFT", "ARCHIVED"]).default("DRAFT"),
  },
  async (args) => {
    const result = await createProduct.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// === SEO UPDATE TOOLS ===

// Update Product SEO - meta title and description
server.tool(
  "update-product-seo",
  {
    productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
    metaTitle: z.string().optional().describe("SEO meta title for the product"),
    metaDescription: z.string().optional().describe("SEO meta description for the product"),
  },
  async (args) => {
    const result = await updateProductSeo.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Update Collection SEO - meta title and description
server.tool(
  "update-collection-seo",
  {
    collectionId: z.string().min(1).describe("Shopify collection ID (numeric, without gid prefix)"),
    metaTitle: z.string().optional().describe("SEO meta title for the collection"),
    metaDescription: z.string().optional().describe("SEO meta description for the collection"),
  },
  async (args) => {
    const result = await updateCollectionSeo.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Update Product Images - ALT text for SEO
server.tool(
  "update-product-images",
  {
    productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
    images: z.array(z.object({
      imageId: z.string().min(1).describe("Shopify image ID (numeric, without gid prefix)"),
      altText: z.string().describe("ALT text for the image (SEO-friendly description)")
    })).min(1).describe("Array of images to update with new ALT text")
  },
  async (args) => {
    const result = await updateProductImages.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// SEO Audit - scan for missing meta titles, descriptions, ALT texts
server.tool(
  "get-seo-audit",
  {
    scope: z.enum(["products", "collections", "all"]).default("all").describe("What to audit: products, collections, or all"),
    limit: z.number().default(50).describe("Max items to scan per type (max 250)")
  },
  async (args) => {
    const result = await getSeoAudit.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Revenue Reconciliation - cross-validate revenue data
server.tool(
  "get-revenue-reconciliation",
  {
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    maxOrders: z.number().default(5000).describe("Max orders to fetch for reconciliation (default 5000)")
  },
  async (args) => {
    const result = await getRevenueReconciliation.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// === ANALYTICS TOOLS ===

// Traffic Source Analytics - analyze orders by traffic source (with pagination)
server.tool(
  "get-traffic-source-analytics",
  {
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
    financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid — excludes cancelled/refunded)")
  },
  async (args) => {
    const result = await getTrafficSourceAnalytics.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Campaign Performance - detailed UTM campaign analysis (with pagination)
server.tool(
  "get-campaign-performance",
  {
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
    utmSource: z.string().optional().describe("Filter by UTM source (e.g., facebook, instagram, google)"),
    utmMedium: z.string().optional().describe("Filter by UTM medium (e.g., cpc, email, social)"),
    financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid)")
  },
  async (args) => {
    const result = await getCampaignPerformance.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Conversion Metrics - payment, fulfillment, and conversion trends (with pagination)
server.tool(
  "get-conversion-metrics",
  {
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
    groupBy: z.enum(["day", "week", "month"]).default("day").describe("Time grouping for trends"),
    financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("any").describe("Filter by financial status (default: any — shows all for conversion funnel)")
  },
  async (args) => {
    const result = await getConversionMetrics.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Product Performance - product sales by traffic source (with pagination)
server.tool(
  "get-product-performance",
  {
    dateFrom: z.string().describe("Start date in ISO format (e.g., 2024-01-01)"),
    dateTo: z.string().describe("End date in ISO format (e.g., 2024-12-31)"),
    limit: z.number().default(2000).describe("Max orders to analyze (default 2000, max 5000 — uses pagination)"),
    utmSource: z.string().optional().describe("Filter by UTM source to see product performance from specific source"),
    financialStatus: z.enum(["any", "paid", "pending", "refunded", "voided", "authorized"]).default("paid").describe("Filter by financial status (default: paid)")
  },
  async (args) => {
    const result = await getProductPerformance.execute(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }]
    };
  }
);

// Start the server
const transport = new StdioServerTransport();
server
  .connect(transport)
  .then(() => {})
  .catch((error: unknown) => {
    console.error("Failed to start Shopify MCP Server:", error);
  });
