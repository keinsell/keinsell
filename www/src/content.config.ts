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

const pattern = defineCollection({
  loader: glob({ base: "./src/content/pattern", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.string().optional(),
    relatedPatterns: z.array(z.string()).optional(),
    implementations: z.array(z.string()).optional(),
  }),
});

const implementation = defineCollection({
  loader: glob({ base: "./src/content/implementation", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pattern: z.string(),
    language: z.string().optional(),
    framework: z.string().optional(),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = {
  blog,
  story,
  pattern,
  implementation,
};
