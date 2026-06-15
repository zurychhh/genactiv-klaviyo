import { gql } from "graphql-request";
import { z } from "zod";
const BulkUpdateSeoInputSchema = z.object({
    items: z.array(z.object({
        id: z.string().min(1).describe("Shopify product or collection ID (numeric, without gid prefix)"),
        type: z.enum(["product", "collection"]).describe("Whether this is a product or collection"),
        metaTitle: z.string().optional().describe("New SEO meta title"),
        metaDescription: z.string().optional().describe("New SEO meta description"),
    })).min(1).max(25).describe("Array of items to update (max 25 per batch to avoid rate limits)"),
    dryRun: z.boolean().default(false).describe("If true, validates inputs but doesn't make changes — shows what would be updated"),
});
let shopifyClient;
const PRODUCT_UPDATE_MUTATION = gql `
  mutation productUpdate($input: ProductInput!) {
    productUpdate(input: $input) {
      product {
        id
        title
        handle
        seo { title description }
      }
      userErrors { field message }
    }
  }
`;
const COLLECTION_UPDATE_MUTATION = gql `
  mutation collectionUpdate($input: CollectionInput!) {
    collectionUpdate(input: $input) {
      collection {
        id
        title
        handle
        seo { title description }
      }
      userErrors { field message }
    }
  }
`;
const bulkUpdateSeo = {
    name: "bulk-update-seo",
    description: "Batch update SEO meta titles and descriptions for multiple products and/or collections in one call. Max 25 items per batch. Supports dry-run mode to preview changes. Use after get-seo-audit to fix issues in bulk.",
    schema: BulkUpdateSeoInputSchema,
    initialize(client) {
        shopifyClient = client;
    },
    execute: async (input) => {
        const { items, dryRun } = input;
        const results = [];
        let updatedCount = 0;
        let errorCount = 0;
        let skippedCount = 0;
        for (const item of items) {
            const gid = item.type === "product"
                ? (item.id.startsWith("gid://") ? item.id : `gid://shopify/Product/${item.id}`)
                : (item.id.startsWith("gid://") ? item.id : `gid://shopify/Collection/${item.id}`);
            // Skip items with no actual changes
            if (!item.metaTitle && !item.metaDescription) {
                results.push({
                    id: item.id,
                    type: item.type,
                    title: "",
                    handle: "",
                    status: "skipped",
                    error: "No metaTitle or metaDescription provided",
                });
                skippedCount++;
                continue;
            }
            if (dryRun) {
                results.push({
                    id: item.id,
                    type: item.type,
                    title: `[dry-run] ${item.type} ${item.id}`,
                    handle: "",
                    status: "skipped",
                    seo: {
                        title: item.metaTitle || null,
                        description: item.metaDescription || null,
                    },
                });
                skippedCount++;
                continue;
            }
            try {
                const seo = {};
                if (item.metaTitle !== undefined)
                    seo.title = item.metaTitle;
                if (item.metaDescription !== undefined)
                    seo.description = item.metaDescription;
                if (item.type === "product") {
                    const data = (await shopifyClient.request(PRODUCT_UPDATE_MUTATION, {
                        input: { id: gid, seo },
                    }));
                    if (data.productUpdate.userErrors.length > 0) {
                        const errMsg = data.productUpdate.userErrors.map(e => `${e.field}: ${e.message}`).join(", ");
                        results.push({ id: item.id, type: item.type, title: "", handle: "", status: "error", error: errMsg });
                        errorCount++;
                    }
                    else {
                        const p = data.productUpdate.product;
                        results.push({ id: item.id, type: item.type, title: p.title, handle: p.handle, status: "updated", seo: p.seo });
                        updatedCount++;
                    }
                }
                else {
                    const data = (await shopifyClient.request(COLLECTION_UPDATE_MUTATION, {
                        input: { id: gid, seo },
                    }));
                    if (data.collectionUpdate.userErrors.length > 0) {
                        const errMsg = data.collectionUpdate.userErrors.map(e => `${e.field}: ${e.message}`).join(", ");
                        results.push({ id: item.id, type: item.type, title: "", handle: "", status: "error", error: errMsg });
                        errorCount++;
                    }
                    else {
                        const c = data.collectionUpdate.collection;
                        results.push({ id: item.id, type: item.type, title: c.title, handle: c.handle, status: "updated", seo: c.seo });
                        updatedCount++;
                    }
                }
            }
            catch (error) {
                results.push({
                    id: item.id,
                    type: item.type,
                    title: "",
                    handle: "",
                    status: "error",
                    error: error instanceof Error ? error.message : String(error),
                });
                errorCount++;
            }
        }
        return {
            summary: {
                totalItems: items.length,
                updated: updatedCount,
                errors: errorCount,
                skipped: skippedCount,
                dryRun,
            },
            results,
            tip: dryRun
                ? "Dry run complete — no changes made. Remove dryRun flag to apply changes."
                : updatedCount > 0
                    ? `${updatedCount} items updated. Run get-seo-audit to verify changes.`
                    : "No items were updated. Check errors above.",
        };
    },
};
export { bulkUpdateSeo };
