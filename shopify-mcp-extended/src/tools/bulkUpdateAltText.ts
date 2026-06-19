import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";

const BulkUpdateAltTextInputSchema = z.object({
  items: z.array(z.object({
    productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
    imageId: z.string().min(1).describe("Shopify image/media ID (numeric, without gid prefix)"),
    altText: z.string().describe("New ALT text for the image (SEO-friendly description)"),
  })).min(1).max(25).describe("Array of images to update (max 25 per batch to avoid rate limits)"),
  dryRun: z.boolean().default(false).describe("If true, validates inputs and shows before/after but doesn't make changes"),
});

type BulkUpdateAltTextInput = z.infer<typeof BulkUpdateAltTextInputSchema>;

interface AltUpdateResult {
  productId: string;
  imageId: string;
  status: "updated" | "skipped" | "error";
  previousAltText?: string | null;
  newAltText: string;
  error?: string;
}

let shopifyClient: GraphQLClient;

const GET_PRODUCT_MEDIA = gql`
  query GetProductMedia($id: ID!) {
    product(id: $id) {
      id
      title
      media(first: 100) {
        nodes {
          ... on MediaImage {
            id
            alt
          }
        }
      }
    }
  }
`;

const UPDATE_MEDIA_MUTATION = gql`
  mutation productUpdateMedia($productId: ID!, $media: [UpdateMediaInput!]!) {
    productUpdateMedia(productId: $productId, media: $media) {
      media {
        ... on MediaImage {
          id
          alt
        }
      }
      mediaUserErrors { field message code }
    }
  }
`;

const bulkUpdateAltText = {
  name: "bulk-update-alt-text",
  description:
    "Batch update ALT text for product images across multiple products in one call. Max 25 images per batch. Groups images by product and uses productUpdateMedia. Supports dry-run mode to preview before/after. Use after get-seo-audit to fix missing_alt_text issues in bulk.",
  schema: BulkUpdateAltTextInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: BulkUpdateAltTextInput) => {
    const { items, dryRun } = input;
    const results: AltUpdateResult[] = [];
    let updatedCount = 0;
    let errorCount = 0;
    let skippedCount = 0;

    // Group items by product to batch productUpdateMedia calls and reuse one
    // media fetch per product for before/after reporting.
    const byProduct = new Map<string, typeof items>();
    for (const item of items) {
      const list = byProduct.get(item.productId) ?? [];
      list.push(item);
      byProduct.set(item.productId, list);
    }

    for (const [productId, productItems] of byProduct) {
      const productGid = productId.startsWith("gid://")
        ? productId
        : `gid://shopify/Product/${productId}`;

      // Fetch current alt text for before/after reporting
      const currentAltById = new Map<string, string | null>();
      try {
        const data = (await shopifyClient.request(GET_PRODUCT_MEDIA, { id: productGid })) as {
          product: { media: { nodes: Array<{ id: string; alt: string | null }> } } | null;
        };
        if (data.product) {
          for (const node of data.product.media.nodes) {
            if (node?.id) currentAltById.set(node.id.split("/").pop() as string, node.alt ?? null);
          }
        }
      } catch {
        // Non-fatal: proceed without "previous" values
      }

      const numericId = (gid: string) => gid.replace(/^gid:\/\/shopify\/\w+\//, "");

      if (dryRun) {
        for (const item of productItems) {
          results.push({
            productId,
            imageId: item.imageId,
            status: "skipped",
            previousAltText: currentAltById.get(numericId(item.imageId)) ?? null,
            newAltText: item.altText,
          });
          skippedCount++;
        }
        continue;
      }

      const media = productItems.map((item) => ({
        id: item.imageId.startsWith("gid://")
          ? item.imageId
          : `gid://shopify/MediaImage/${item.imageId}`,
        alt: item.altText,
      }));

      try {
        const updateResult = (await shopifyClient.request(UPDATE_MEDIA_MUTATION, {
          productId: productGid,
          media,
        })) as {
          productUpdateMedia: {
            mediaUserErrors: Array<{ field: string; message: string; code: string }>;
          };
        };

        const errors = updateResult.productUpdateMedia?.mediaUserErrors ?? [];
        if (errors.length > 0) {
          const errMsg = errors.map((e) => `${e.field}: ${e.message}`).join(", ");
          for (const item of productItems) {
            results.push({
              productId,
              imageId: item.imageId,
              status: "error",
              previousAltText: currentAltById.get(numericId(item.imageId)) ?? null,
              newAltText: item.altText,
              error: errMsg,
            });
            errorCount++;
          }
        } else {
          for (const item of productItems) {
            results.push({
              productId,
              imageId: item.imageId,
              status: "updated",
              previousAltText: currentAltById.get(numericId(item.imageId)) ?? null,
              newAltText: item.altText,
            });
            updatedCount++;
          }
        }
      } catch (error) {
        for (const item of productItems) {
          results.push({
            productId,
            imageId: item.imageId,
            status: "error",
            previousAltText: currentAltById.get(numericId(item.imageId)) ?? null,
            newAltText: item.altText,
            error: error instanceof Error ? error.message : String(error),
          });
          errorCount++;
        }
      }
    }

    return {
      summary: {
        totalItems: items.length,
        productsAffected: byProduct.size,
        updated: updatedCount,
        errors: errorCount,
        skipped: skippedCount,
        dryRun,
      },
      results,
      tip: dryRun
        ? "Dry run complete — no changes made. Remove dryRun flag to apply changes."
        : updatedCount > 0
          ? `${updatedCount} image ALT texts updated. Run get-seo-audit to verify coverage.`
          : "No images were updated. Check errors above.",
    };
  },
};

export { bulkUpdateAltText };
