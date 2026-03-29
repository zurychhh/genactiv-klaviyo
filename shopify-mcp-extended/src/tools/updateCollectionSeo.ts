
import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";

// Input schema for updating collection SEO
const UpdateCollectionSeoInputSchema = z.object({
  collectionId: z.string().min(1).describe("Shopify collection ID (numeric, without gid prefix)"),
  metaTitle: z.string().optional().describe("SEO meta title for the collection"),
  metaDescription: z.string().optional().describe("SEO meta description for the collection"),
});

type UpdateCollectionSeoInput = z.infer<typeof UpdateCollectionSeoInputSchema>;

// Will be initialized in index.ts
let shopifyClient: GraphQLClient;

const updateCollectionSeo = {
  name: "update-collection-seo",
  description: "Update SEO meta title and/or meta description for a collection",
  schema: UpdateCollectionSeoInputSchema,

  // Add initialize method to set up the GraphQL client
  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: UpdateCollectionSeoInput) => {
    try {
      // Build the GID from numeric ID
      const collectionGid = input.collectionId.startsWith("gid://")
        ? input.collectionId
        : `gid://shopify/Collection/${input.collectionId}`;

      const query = gql`
        mutation collectionUpdate($input: CollectionInput!) {
          collectionUpdate(input: $input) {
            collection {
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
          id: collectionGid,
          seo,
        },
      };

      const data = (await shopifyClient.request(query, variables)) as {
        collectionUpdate: {
          collection: {
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
      if (data.collectionUpdate.userErrors.length > 0) {
        throw new Error(
          `Failed to update collection SEO: ${data.collectionUpdate.userErrors
            .map((e) => `${e.field}: ${e.message}`)
            .join(", ")}`
        );
      }

      return {
        collection: {
          id: data.collectionUpdate.collection.id,
          title: data.collectionUpdate.collection.title,
          handle: data.collectionUpdate.collection.handle,
          seo: data.collectionUpdate.collection.seo,
        },
      };
    } catch (error) {
      console.error("Error updating collection SEO:", error);
      throw new Error(
        `Failed to update collection SEO: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  },
};

export { updateCollectionSeo };
