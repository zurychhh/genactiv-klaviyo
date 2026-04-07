import type { GraphQLClient } from "graphql-request";
import { gql } from "graphql-request";
import { z } from "zod";

const GetSeoAuditInputSchema = z.object({
  scope: z.enum(["products", "collections", "all"]).default("all").describe("What to audit: products, collections, or all"),
  limit: z.number().default(50).describe("Max items to scan per type (max 250)")
});

type GetSeoAuditInput = z.infer<typeof GetSeoAuditInputSchema>;

interface SeoIssue {
  type: "missing_meta_title" | "missing_meta_description" | "missing_alt_text" | "short_meta_description" | "long_meta_title" | "missing_product_description";
  severity: "high" | "medium" | "low";
  itemType: "product" | "collection";
  itemId: string;
  itemTitle: string;
  handle: string;
  itemUrl: string;
  field: string;
  currentValue: string | null;
  recommendation: string;
}

let shopifyClient: GraphQLClient;

const getSeoAudit = {
  name: "get-seo-audit",
  description: "Scan products and collections for SEO issues: missing meta titles, descriptions, ALT texts, and other SEO problems. Returns prioritized list of issues with recommendations.",
  schema: GetSeoAuditInputSchema,

  initialize(client: GraphQLClient) {
    shopifyClient = client;
  },

  execute: async (input: GetSeoAuditInput) => {
    try {
      const { scope, limit } = input;
      const effectiveLimit = Math.min(limit, 250);
      const issues: SeoIssue[] = [];

      let productsScanned = 0;
      let collectionsScanned = 0;
      let totalImages = 0;
      let imagesWithoutAlt = 0;

      // Scan products
      if (scope === "products" || scope === "all") {
        const productsQuery = gql`
          query GetProductsSeo($first: Int!) {
            products(first: $first, sortKey: UPDATED_AT, reverse: true) {
              edges {
                node {
                  id
                  title
                  handle
                  descriptionHtml
                  seo {
                    title
                    description
                  }
                  images(first: 20) {
                    edges {
                      node {
                        id
                        altText
                        url
                      }
                    }
                  }
                  status
                }
              }
            }
          }
        `;

        const productsData = (await shopifyClient.request(productsQuery, {
          first: effectiveLimit
        })) as { products: any };

        for (const edge of productsData.products.edges) {
          const product = edge.node;
          const numericId = product.id.split("/").pop();
          productsScanned++;

          const productHandle = product.handle || "";
          const productUrl = `/products/${productHandle}`;

          // Check meta title
          if (!product.seo?.title) {
            issues.push({
              type: "missing_meta_title",
              severity: "high",
              itemType: "product",
              itemId: numericId,
              itemTitle: product.title,
              handle: productHandle,
              itemUrl: productUrl,
              field: "seo.title",
              currentValue: null,
              recommendation: `Dodaj meta title dla "${product.title}" (50-60 znaków, z frazą kluczową)`
            });
          } else if (product.seo.title.length > 60) {
            issues.push({
              type: "long_meta_title",
              severity: "medium",
              itemType: "product",
              itemId: numericId,
              itemTitle: product.title,
              handle: productHandle,
              itemUrl: productUrl,
              field: "seo.title",
              currentValue: product.seo.title,
              recommendation: `Meta title ma ${product.seo.title.length} znaków (max 60). Skróć do ~55-60 znaków.`
            });
          }

          // Check meta description
          if (!product.seo?.description) {
            issues.push({
              type: "missing_meta_description",
              severity: "high",
              itemType: "product",
              itemId: numericId,
              itemTitle: product.title,
              handle: productHandle,
              itemUrl: productUrl,
              field: "seo.description",
              currentValue: null,
              recommendation: `Dodaj meta description dla "${product.title}" (120-160 znaków, z CTA)`
            });
          } else if (product.seo.description.length < 80) {
            issues.push({
              type: "short_meta_description",
              severity: "medium",
              itemType: "product",
              itemId: numericId,
              itemTitle: product.title,
              handle: productHandle,
              itemUrl: productUrl,
              field: "seo.description",
              currentValue: product.seo.description,
              recommendation: `Meta description ma tylko ${product.seo.description.length} znaków (min 120). Rozbuduj opis.`
            });
          }

          // Check product description (body)
          if (!product.descriptionHtml || product.descriptionHtml.trim().length < 50) {
            issues.push({
              type: "missing_product_description",
              severity: "medium",
              itemType: "product",
              itemId: numericId,
              itemTitle: product.title,
              handle: productHandle,
              itemUrl: productUrl,
              field: "descriptionHtml",
              currentValue: product.descriptionHtml ? `${product.descriptionHtml.length} znaków` : null,
              recommendation: `Produkt "${product.title}" ma zbyt krótki lub brak opisu HTML. Dodaj min. 200 znaków unikalnego opisu.`
            });
          }

          // Check image ALT texts
          for (const imgEdge of product.images.edges) {
            const img = imgEdge.node;
            const imgNumericId = img.id.split("/").pop();
            totalImages++;

            if (!img.altText || img.altText.trim() === "") {
              imagesWithoutAlt++;
              issues.push({
                type: "missing_alt_text",
                severity: "high",
                itemType: "product",
                itemId: numericId,
                itemTitle: product.title,
                handle: productHandle,
                itemUrl: productUrl,
                field: `image:${imgNumericId}`,
                currentValue: null,
                recommendation: `Dodaj ALT text do zdjęcia produktu "${product.title}" (opisz co widać na zdjęciu, 5-15 słów)`
              });
            }
          }
        }
      }

      // Scan collections
      if (scope === "collections" || scope === "all") {
        const collectionsQuery = gql`
          query GetCollectionsSeo($first: Int!) {
            collections(first: $first, sortKey: UPDATED_AT, reverse: true) {
              edges {
                node {
                  id
                  title
                  handle
                  descriptionHtml
                  seo {
                    title
                    description
                  }
                  image {
                    id
                    altText
                    url
                  }
                }
              }
            }
          }
        `;

        const collectionsData = (await shopifyClient.request(collectionsQuery, {
          first: effectiveLimit
        })) as { collections: any };

        for (const edge of collectionsData.collections.edges) {
          const collection = edge.node;
          const numericId = collection.id.split("/").pop();
          collectionsScanned++;
          const collectionHandle = collection.handle || "";
          const collectionUrl = `/collections/${collectionHandle}`;

          // Check meta title
          if (!collection.seo?.title) {
            issues.push({
              type: "missing_meta_title",
              severity: "high",
              itemType: "collection",
              itemId: numericId,
              itemTitle: collection.title,
              handle: collectionHandle,
              itemUrl: collectionUrl,
              field: "seo.title",
              currentValue: null,
              recommendation: `Dodaj meta title dla kolekcji "${collection.title}" (50-60 znaków)`
            });
          }

          // Check meta description
          if (!collection.seo?.description) {
            issues.push({
              type: "missing_meta_description",
              severity: "high",
              itemType: "collection",
              itemId: numericId,
              itemTitle: collection.title,
              handle: collectionHandle,
              itemUrl: collectionUrl,
              field: "seo.description",
              currentValue: null,
              recommendation: `Dodaj meta description dla kolekcji "${collection.title}" (120-160 znaków)`
            });
          } else if (collection.seo.description.length < 80) {
            issues.push({
              type: "short_meta_description",
              severity: "medium",
              itemType: "collection",
              itemId: numericId,
              itemTitle: collection.title,
              handle: collectionHandle,
              itemUrl: collectionUrl,
              field: "seo.description",
              currentValue: collection.seo.description,
              recommendation: `Meta description kolekcji ma tylko ${collection.seo.description.length} znaków (min 120).`
            });
          }

          // Check collection image ALT
          if (collection.image) {
            totalImages++;
            if (!collection.image.altText || collection.image.altText.trim() === "") {
              imagesWithoutAlt++;
              const imgNumericId = collection.image.id?.split("/").pop();
              issues.push({
                type: "missing_alt_text",
                severity: "medium",
                itemType: "collection",
                itemId: numericId,
                itemTitle: collection.title,
                handle: collectionHandle,
                itemUrl: collectionUrl,
                field: `image:${imgNumericId}`,
                currentValue: null,
                recommendation: `Dodaj ALT text do zdjęcia kolekcji "${collection.title}"`
              });
            }
          }
        }
      }

      // Sort by severity (high first), then by type
      const severityOrder = { high: 0, medium: 1, low: 2 };
      issues.sort((a, b) => {
        const sevDiff = severityOrder[a.severity] - severityOrder[b.severity];
        if (sevDiff !== 0) return sevDiff;
        return a.type.localeCompare(b.type);
      });

      // Summary by type
      const byType: Record<string, number> = {};
      for (const issue of issues) {
        byType[issue.type] = (byType[issue.type] || 0) + 1;
      }

      const highCount = issues.filter(i => i.severity === "high").length;
      const mediumCount = issues.filter(i => i.severity === "medium").length;
      const lowCount = issues.filter(i => i.severity === "low").length;

      return {
        summary: {
          productsScanned,
          collectionsScanned,
          totalIssues: issues.length,
          bySeverity: { high: highCount, medium: mediumCount, low: lowCount },
          byType,
          imageStats: {
            totalImages,
            imagesWithoutAlt,
            altTextCoverage: totalImages > 0
              ? Math.round((totalImages - imagesWithoutAlt) / totalImages * 100)
              : 100
          }
        },
        issues
      };
    } catch (error) {
      console.error("Error running SEO audit:", error);
      throw new Error(
        `Failed to run SEO audit: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }
};

export { getSeoAudit };
