import { gql } from "graphql-request";
import { z } from "zod";
const UpdateProductContentInputSchema = z.object({
    productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
    descriptionHtml: z.string().optional().describe("New product description in HTML format. Supports full HTML with headings, lists, bold, links etc."),
    title: z.string().optional().describe("New product title (visible in storefront)"),
    tags: z.array(z.string()).optional().describe("Replace product tags (overwrites existing tags)"),
    vendor: z.string().optional().describe("Product vendor/brand name"),
    productType: z.string().optional().describe("Product type/category"),
});
let shopifyClient;
const updateProductContent = {
    name: "update-product-content",
    description: "Update product content: HTML description, title, tags, vendor, productType. Use for SEO fixes (typos in descriptions, enriching content), content editing, and bulk product updates. Does NOT update SEO meta — use update-product-seo for that.",
    schema: UpdateProductContentInputSchema,
    initialize(client) {
        shopifyClient = client;
    },
    execute: async (input) => {
        try {
            const productGid = input.productId.startsWith("gid://")
                ? input.productId
                : `gid://shopify/Product/${input.productId}`;
            // First fetch current product to show before/after
            const fetchQuery = gql `
        query GetProduct($id: ID!) {
          product(id: $id) {
            id
            title
            handle
            descriptionHtml
            vendor
            productType
            tags
            seo {
              title
              description
            }
          }
        }
      `;
            const fetchData = (await shopifyClient.request(fetchQuery, { id: productGid }));
            if (!fetchData.product) {
                throw new Error(`Product not found: ${productGid}`);
            }
            const before = {
                title: fetchData.product.title,
                descriptionHtml: fetchData.product.descriptionHtml?.substring(0, 200) + (fetchData.product.descriptionHtml?.length > 200 ? "..." : ""),
                vendor: fetchData.product.vendor,
                productType: fetchData.product.productType,
                tags: fetchData.product.tags,
            };
            // Build update payload — only include provided fields
            const productInput = { id: productGid };
            if (input.descriptionHtml !== undefined)
                productInput.descriptionHtml = input.descriptionHtml;
            if (input.title !== undefined)
                productInput.title = input.title;
            if (input.tags !== undefined)
                productInput.tags = input.tags;
            if (input.vendor !== undefined)
                productInput.vendor = input.vendor;
            if (input.productType !== undefined)
                productInput.productType = input.productType;
            const updateQuery = gql `
        mutation productUpdate($input: ProductInput!) {
          productUpdate(input: $input) {
            product {
              id
              title
              handle
              descriptionHtml
              vendor
              productType
              tags
              seo {
                title
                description
              }
            }
            userErrors {
              field
              message
            }
          }
        }
      `;
            const data = (await shopifyClient.request(updateQuery, { input: productInput }));
            if (data.productUpdate.userErrors.length > 0) {
                throw new Error(`Failed to update product: ${data.productUpdate.userErrors
                    .map((e) => `${e.field}: ${e.message}`)
                    .join(", ")}`);
            }
            const after = data.productUpdate.product;
            return {
                status: "updated",
                product: {
                    id: after.id,
                    title: after.title,
                    handle: after.handle,
                    url: `https://${process.env.MYSHOPIFY_DOMAIN?.replace('.myshopify.com', '.pl') || 'genactiv.pl'}/products/${after.handle}`,
                    descriptionHtml: after.descriptionHtml?.substring(0, 200) + (after.descriptionHtml?.length > 200 ? "..." : ""),
                    vendor: after.vendor,
                    productType: after.productType,
                    tags: after.tags,
                    seo: after.seo,
                },
                changes: {
                    before,
                    fieldsUpdated: Object.keys(input).filter(k => k !== "productId"),
                },
            };
        }
        catch (error) {
            console.error("Error updating product content:", error);
            throw new Error(`Failed to update product content: ${error instanceof Error ? error.message : String(error)}`);
        }
    },
};
export { updateProductContent };
