
import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";

// Input schema for updating product SEO
const UpdateProductSeoInputSchema = z.object({
  productId: z.string().min(1).describe("Shopify product ID (numeric, without gid prefix)"),
  metaTitle: z.string().optional().describe("SEO meta title for the product"),
  metaDescription: z.string().optional().describe("SEO meta description for the product"),
});

type UpdateProductSeoInput = z.infer<typeof UpdateProductSeoInputSchema>;

// Will be initialized in index.ts
let shopifyClient: GraphQLClient;

const updateProductSeo = {
  name: "update-product-seo",
  description: "Update SEO meta title and/or meta description for a product",
  schema: UpdateProductSeoInputSchema,

  // Add initialize method to set up the GraphQL client
  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: UpdateProductSeoInput) => {
    try {
      // Build the GID from numeric ID
      const productGid = input.productId.startsWith("gid://")
        ? input.productId
        : `gid://shopify/Product/${input.productId}`;

      const query = gql`
        mutation productUpdate($input: ProductInput!) {
          productUpdate(input: $input) {
            product {
              id
              title
              handle
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

      // Build SEO object only with provided fields
      const seo: { title?: string; description?: string } = {};
      if (input.metaTitle !== undefined) {
        seo.title = input.metaTitle;
      }
      if (input.metaDescription !== undefined) {
        seo.description = input.metaDescription;
      }

      const variables = {
        input: {
          id: productGid,
          seo,
        },
      };

      const data = (await shopifyClient.request(query, variables)) as {
        productUpdate: {
          product: {
            id: string;
            title: string;
            handle: string;
            seo: {
              title: string | null;
              description: string | null;
            };
          };
          userErrors: Array<{
            field: string;
            message: string;
          }>;
        };
      };

      // If there are user errors, throw an error
      if (data.productUpdate.userErrors.length > 0) {
        throw new Error(
          `Failed to update product SEO: ${data.productUpdate.userErrors
            .map((e) => `${e.field}: ${e.message}`)
            .join(", ")}`
        );
      }

      return {
        product: {
          id: data.productUpdate.product.id,
          title: data.productUpdate.product.title,
          handle: data.productUpdate.product.handle,
          seo: data.productUpdate.product.seo,
        },
      };
    } catch (error) {
      console.error("Error updating product SEO:", error);
      throw new Error(
        `Failed to update product SEO: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },
};

export { updateProductSeo };
