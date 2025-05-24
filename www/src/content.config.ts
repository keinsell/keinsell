import { glob } from 'astro/loaders';
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
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

const contentCollections = defineCollection({
	loader: glob({ base: './src/content/collections', pattern: '**/*.md' }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		slug: z.string(), // URL-friendly identifier
		order: z.number().optional(), // Display order
		status: z.enum(['draft', 'active', 'completed']).default('active'),
		startDate: z.coerce.date().optional(),
		endDate: z.coerce.date().optional(),
	}),
});

const tags = defineCollection({
	loader: glob({ base: './src/content/tags', pattern: '**/*.md' }),
	schema: z.object({
		name: z.string(), // Display name
		slug: z.string(), // URL-friendly identifier
		description: z.string(),
		color: z.string().optional(), // Hex color for tag
		category: z.string().optional(), // Group tags by category
		order: z.number().optional(), // Display order
	}),
});

const story = defineCollection({
	loader: glob({ base: './src/content', pattern: 'story.md' }),
	schema: z.object({
		title: z.string(),
		seo: z.object({
			title: z.string(),
			description: z.string(),
			type: z.string(),
			keywords: z.string(),
		}).optional(),
	}),
});

export const collections = { blog, collections: contentCollections, tags, story };