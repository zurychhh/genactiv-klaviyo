import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";

const UpdateProductImagesInputSchema = z.object({
  productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
  images: z.array(z.object({
    imageId: z.string().min(1).describe("Shopify image ID (numeric, without gid prefix)"),
    altText: z.string().describe("ALT text for the image (SEO-friendly description)")
  })).min(1).describe("Array of images to update with new ALT text")
});

type UpdateProductImagesInput = z.infer<typeof UpdateProductImagesInputSchema>;

let shopifyClient: GraphQLClient;

const updateProductImages = {
  name: "update-product-images",
  description: "Update ALT text for product images (SEO optimization). Accepts multiple images at once for batch updates.",
  schema: UpdateProductImagesInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: UpdateProductImagesInput) => {
    try {
      const { productId, images } = input;
      const productGid = productId.startsWith("gid://")
        ? productId
        : `gid://shopify/Product/${productId}`;

      // Fetch both images (ProductImage GIDs) and media (MediaImage GIDs)
      // productUpdateMedia requires MediaImage GIDs, but audits/get-product return ProductImage GIDs
      const getQuery = gql`
        query GetProductImages($id: ID!) {
          product(id: $id) {
            id
            title
            images(first: 50) {
              edges {
                node {
                  id
                  altText
                  url
                }
              }
            }
            media(first: 50) {
              edges {
                node {
                  ... on MediaImage {
                    id
                    alt
                    image {
                      url
                    }
                  }
                }
              }
            }
          }
        }
      `;

      const productData = (await shopifyClient.request(getQuery, { id: productGid })) as {
        product: any;
      };

      if (!productData.product) {
        throw new Error(`Product not found: ${productId}`);
      }

      const existingImages = productData.product.images.edges.map((e: any) => e.node);

      // Build ProductImage URL → MediaImage GID mapping
      const mediaNodes = (productData.product.media?.edges || [])
        .map((e: any) => e.node)
        .filter((n: any) => n.id && n.id.includes("MediaImage"));
      const urlToMediaGid = new Map<string, string>();
      for (const m of mediaNodes) {
        if (m.image?.url) {
          urlToMediaGid.set(m.image.url, m.id);
        }
      }
      // Also build ProductImage numeric ID → MediaImage GID via URL match
      const productImageIdToMediaGid = new Map<string, string>();
      for (const pi of existingImages) {
        const piNumericId = pi.id.split("/").pop();
        const mediaGid = urlToMediaGid.get(pi.url);
        if (piNumericId && mediaGid) {
          productImageIdToMediaGid.set(piNumericId, mediaGid);
        }
      }

      // Update each image ALT text using productUpdateMedia
      const results: Array<{
        imageId: string;
        altText: string;
        status: "updated" | "not_found" | "error";
        previousAltText?: string;
        error?: string;
      }> = [];

      for (const img of images) {
        const inputNumericId = img.imageId.replace(/^gid:\/\/shopify\/\w+\//, "");

        // Resolve to MediaImage GID: try mapping first, then direct construction
        let imageGid: string;
        if (img.imageId.startsWith("gid://shopify/MediaImage/")) {
          imageGid = img.imageId;
        } else if (productImageIdToMediaGid.has(inputNumericId)) {
          // Input was a ProductImage ID — resolve via URL mapping
          imageGid = productImageIdToMediaGid.get(inputNumericId)!;
        } else if (img.imageId.startsWith("gid://")) {
          // Some other GID format — try to find by numeric part
          const mapped = productImageIdToMediaGid.get(inputNumericId);
          imageGid = mapped || `gid://shopify/MediaImage/${inputNumericId}`;
        } else {
          // Bare numeric ID — try mapping, fallback to MediaImage construction
          const mapped = productImageIdToMediaGid.get(inputNumericId);
          imageGid = mapped || `gid://shopify/MediaImage/${inputNumericId}`;
        }

        // Check if image exists on this product
        const existingImage = existingImages.find((ei: any) => {
          const existingNumericId = ei.id.split("/").pop();
          return existingNumericId === inputNumericId || ei.id === imageGid;
        });

        if (!existingImage) {
          // Try updating anyway — the ID format might differ
        }

        try {
          // Use productUpdate with images to update ALT text
          // Shopify 2023-07: use productUpdateMedia mutation
          const updateQuery = gql`
            mutation productUpdateMedia($productId: ID!, $media: [UpdateMediaInput!]!) {
              productUpdateMedia(productId: $productId, media: $media) {
                media {
                  ... on MediaImage {
                    id
                    alt
                    image {
                      url
                    }
                  }
                }
                mediaUserErrors {
                  field
                  message
                  code
                }
              }
            }
          `;

          const updateResult = (await shopifyClient.request(updateQuery, {
            productId: productGid,
            media: [{
              id: imageGid,
              alt: img.altText
            }]
          })) as any;

          const errors = updateResult.productUpdateMedia?.mediaUserErrors || [];
          if (errors.length > 0) {
            results.push({
              imageId: img.imageId,
              altText: img.altText,
              status: "error",
              previousAltText: existingImage?.altText || undefined,
              error: errors.map((e: any) => e.message).join(", ")
            });
          } else {
            results.push({
              imageId: img.imageId,
              altText: img.altText,
              status: "updated",
              previousAltText: existingImage?.altText || undefined
            });
          }
        } catch (err) {
          results.push({
            imageId: img.imageId,
            altText: img.altText,
            status: "error",
            error: err instanceof Error ? err.message : String(err)
          });
        }
      }

      const updated = results.filter(r => r.status === "updated").length;
      const failed = results.filter(r => r.status !== "updated").length;

      return {
        product: {
          id: productId,
          title: productData.product.title
        },
        summary: {
          total: images.length,
          updated,
          failed,
          existingImagesCount: existingImages.length
        },
        results
      };
    } catch (error) {
      console.error("Error updating product images:", error);
      throw new Error(
        `Failed to update product images: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }
};

export { updateProductImages };
