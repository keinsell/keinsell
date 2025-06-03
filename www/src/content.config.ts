import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  // Load Markdown and MDX files in the `src/content/blog/` directory.
  loader: glob({ base: "./src/content/blog", pattern: "**/*.{md,mdx}" }),
  // Type-check frontmatter using a schema
  schema: z.object({
    title: z.string(),
    description: z.string(),
    // Transform string to Date object
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).optional(),
    collection: z.string().optional(), // Which collection this post belongs to
    order: z.number().optional(), // Order within the collection
  }),
});

const story = defineCollection({
  loader: glob({ base: "./src/content", pattern: "story.md" }),
  schema: z.object({
    title: z.string(),
    seo: z
      .object({
        title: z.string(),
        description: z.string(),
        type: z.string(),
        keywords: z.string(),
      })
      .optional(),
  }),
});

const docs = defineCollection({
  loader: glob({ base: "./src/content/docs", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),

    // Simple tagging system
    tags: z.array(z.string()).optional(),

    // Basic relationships for wikilinks
    relatedPages: z.array(z.string()).optional(),

    // Optional technical metadata
    language: z.string().optional(),
    framework: z.string().optional(),

    // Navigation and display
    sidebar: z
      .object({
        hidden: z.boolean().optional(),
        label: z.string().optional(),
        order: z.number().optional(),
      })
      .optional(),

    // Meta information
    publishedAt: z.coerce.date().optional(),
    updatedAt: z.coerce.date().optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = {
  blog,
  story,
  docs,
};
