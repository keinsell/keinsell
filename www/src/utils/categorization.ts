import type { CollectionEntry } from "astro:content";

// Categorization Theory Implementation
// Based on faceted classification and hierarchical taxonomies

export interface Category {
  id: string;
  name: string;
  parent?: string;
  description?: string;
  level: number;
  children: string[];
}

export interface Tag {
  id: string;
  name: string;
  type: 'concept' | 'technology' | 'difficulty' | 'status' | 'domain';
  weight: number; // Frequency of use
}

export interface Collection {
  id: string;
  name: string;
  description: string;
  type: 'structural' | 'thematic' | 'temporal';
  rules: CollectionRule[];
}

export interface CollectionRule {
  field: string;
  operator: 'equals' | 'contains' | 'startsWith' | 'matches';
  value: string | RegExp;
}

export interface TaxonomyNode {
  id: string;
  label: string;
  type: 'category' | 'tag' | 'collection';
  level: number;
  parent?: string;
  children: TaxonomyNode[];
  metadata?: Record<string, any>;
}

// Predefined category hierarchy following software engineering taxonomy
export const CATEGORY_HIERARCHY: Record<string, Category> = {
  'design-patterns': {
    id: 'design-patterns',
    name: 'Design Patterns',
    level: 0,
    children: ['creational-patterns', 'structural-patterns', 'behavioral-patterns']
  },
  'creational-patterns': {
    id: 'creational-patterns',
    name: 'Creational Patterns',
    parent: 'design-patterns',
    level: 1,
    children: [],
    description: 'Patterns that deal with object creation mechanisms'
  },
  'structural-patterns': {
    id: 'structural-patterns',
    name: 'Structural Patterns',
    parent: 'design-patterns',
    level: 1,
    children: [],
    description: 'Patterns that deal with object composition'
  },
  'behavioral-patterns': {
    id: 'behavioral-patterns',
    name: 'Behavioral Patterns',
    parent: 'design-patterns',
    level: 1,
    children: [],
    description: 'Patterns that deal with object collaboration and responsibilities'
  },
  'architecture': {
    id: 'architecture',
    name: 'Architecture',
    level: 0,
    children: ['microservices', 'monolithic', 'serverless', 'event-driven']
  },
  'best-practices': {
    id: 'best-practices',
    name: 'Best Practices',
    level: 0,
    children: ['code-quality', 'testing', 'documentation', 'security']
  }
};

// Tag facets for multi-dimensional classification
export const TAG_FACETS = {
  concept: ['abstraction', 'encapsulation', 'inheritance', 'polymorphism', 'composition'],
  technology: ['typescript', 'javascript', 'react', 'nodejs', 'python', 'rust'],
  difficulty: ['beginner', 'intermediate', 'advanced', 'expert'],
  status: ['draft', 'review', 'published', 'deprecated'],
  domain: ['web', 'mobile', 'desktop', 'embedded', 'distributed']
};

// Collection definitions based on structural organization
export const COLLECTIONS: Record<string, Collection> = {
  patterns: {
    id: 'patterns',
    name: 'Design Patterns',
    description: 'Reusable solutions to common problems',
    type: 'structural',
    rules: [
      { field: 'id', operator: 'startsWith', value: 'patterns/' }
    ]
  },
  implementations: {
    id: 'implementations',
    name: 'Implementations',
    description: 'Practical code examples',
    type: 'structural',
    rules: [
      { field: 'id', operator: 'startsWith', value: 'implementations/' }
    ]
  },
  guides: {
    id: 'guides',
    name: 'Guides',
    description: 'Step-by-step tutorials',
    type: 'structural',
    rules: [
      { field: 'id', operator: 'startsWith', value: 'guides/' }
    ]
  },
  references: {
    id: 'references',
    name: 'References',
    description: 'API and technical documentation',
    type: 'structural',
    rules: [
      { field: 'id', operator: 'startsWith', value: 'references/' }
    ]
  }
};

// Validate and normalize categories
export function validateCategory(category: string): string | null {
  // Check if category exists in hierarchy
  if (CATEGORY_HIERARCHY[category]) {
    return category;
  }
  
  // Check if it's a valid subcategory format (parent/child)
  const parts = category.split('/');
  if (parts.length === 2 && CATEGORY_HIERARCHY[parts[0]]) {
    return category;
  }
  
  // Try to find a close match
  const normalized = category.toLowerCase().replace(/\s+/g, '-');
  if (CATEGORY_HIERARCHY[normalized]) {
    return normalized;
  }
  
  return null;
}

// Validate tags against facets
export function validateTag(tag: string): Tag | null {
  const normalizedTag = tag.toLowerCase().replace(/\s+/g, '-');
  
  for (const [facet, values] of Object.entries(TAG_FACETS)) {
    if (values.includes(normalizedTag)) {
      return {
        id: normalizedTag,
        name: tag,
        type: facet as Tag['type'],
        weight: 1
      };
    }
  }
  
  // Allow custom tags but classify them
  return {
    id: normalizedTag,
    name: tag,
    type: 'concept', // Default type
    weight: 1
  };
}

// Build taxonomy tree from documents
export function buildTaxonomy(docs: CollectionEntry<"docs">[]): TaxonomyNode {
  const root: TaxonomyNode = {
    id: 'root',
    label: 'Knowledge Base',
    type: 'collection',
    level: 0,
    children: []
  };
  
  // Build collection nodes
  Object.values(COLLECTIONS).forEach(collection => {
    const collectionNode: TaxonomyNode = {
      id: `collection:${collection.id}`,
      label: collection.name,
      type: 'collection',
      level: 1,
      parent: 'root',
      children: [],
      metadata: { description: collection.description }
    };
    
    // Add documents to collection
    docs.forEach(doc => {
      const matchesRules = collection.rules.every(rule => {
        const value = doc[rule.field] || doc.data[rule.field];
        switch (rule.operator) {
          case 'equals':
            return value === rule.value;
          case 'contains':
            return value?.includes(rule.value);
          case 'startsWith':
            return value?.startsWith(rule.value);
          case 'matches':
            return rule.value instanceof RegExp ? rule.value.test(value) : false;
          default:
            return false;
        }
      });
      
      if (matchesRules) {
        const docNode: TaxonomyNode = {
          id: doc.id,
          label: doc.data.title,
          type: 'category',
          level: 2,
          parent: collectionNode.id,
          children: [],
          metadata: {
            category: doc.data.category,
            tags: doc.data.tags,
            template: doc.data.template
          }
        };
        collectionNode.children.push(docNode);
      }
    });
    
    if (collectionNode.children.length > 0) {
      root.children.push(collectionNode);
    }
  });
  
  // Build category hierarchy
  const categoryRoot: TaxonomyNode = {
    id: 'categories',
    label: 'Categories',
    type: 'category',
    level: 1,
    parent: 'root',
    children: []
  };
  
  Object.values(CATEGORY_HIERARCHY).forEach(category => {
    if (!category.parent) {
      const categoryNode: TaxonomyNode = {
        id: `category:${category.id}`,
        label: category.name,
        type: 'category',
        level: 2,
        parent: 'categories',
        children: [],
        metadata: { description: category.description }
      };
      
      // Add subcategories
      category.children.forEach(childId => {
        const child = CATEGORY_HIERARCHY[childId];
        if (child) {
          categoryNode.children.push({
            id: `category:${child.id}`,
            label: child.name,
            type: 'category',
            level: 3,
            parent: categoryNode.id,
            children: [],
            metadata: { description: child.description }
          });
        }
      });
      
      categoryRoot.children.push(categoryNode);
    }
  });
  
  root.children.push(categoryRoot);
  
  // Build tag cloud
  const tagCloud = buildTagCloud(docs);
  const tagRoot: TaxonomyNode = {
    id: 'tags',
    label: 'Tags',
    type: 'tag',
    level: 1,
    parent: 'root',
    children: tagCloud.map(tag => ({
      id: `tag:${tag.id}`,
      label: tag.name,
      type: 'tag',
      level: 2,
      parent: 'tags',
      children: [],
      metadata: { weight: tag.weight, facet: tag.type }
    }))
  };
  
  root.children.push(tagRoot);
  
  return root;
}

// Build weighted tag cloud
export function buildTagCloud(docs: CollectionEntry<"docs">[]): Tag[] {
  const tagMap = new Map<string, Tag>();
  
  docs.forEach(doc => {
    if (doc.data.tags) {
      doc.data.tags.forEach(tag => {
        const validatedTag = validateTag(tag);
        if (validatedTag) {
          const existing = tagMap.get(validatedTag.id);
          if (existing) {
            existing.weight += 1;
          } else {
            tagMap.set(validatedTag.id, validatedTag);
          }
        }
      });
    }
  });
  
  return Array.from(tagMap.values()).sort((a, b) => b.weight - a.weight);
}

// Get category path (breadcrumb)
export function getCategoryPath(categoryId: string): Category[] {
  const path: Category[] = [];
  let current = CATEGORY_HIERARCHY[categoryId];
  
  while (current) {
    path.unshift(current);
    current = current.parent ? CATEGORY_HIERARCHY[current.parent] : null;
  }
  
  return path;
}

// Suggest categories based on content
export function suggestCategories(doc: CollectionEntry<"docs">): string[] {
  const suggestions: string[] = [];
  const content = doc.data.title + ' ' + doc.data.description;
  const contentLower = content.toLowerCase();
  
  // Check for pattern-related keywords
  if (contentLower.includes('pattern') || contentLower.includes('design')) {
    if (contentLower.includes('create') || contentLower.includes('instantiat')) {
      suggestions.push('creational-patterns');
    }
    if (contentLower.includes('structure') || contentLower.includes('compose')) {
      suggestions.push('structural-patterns');
    }
    if (contentLower.includes('behavior') || contentLower.includes('algorithm')) {
      suggestions.push('behavioral-patterns');
    }
  }
  
  // Check for architecture keywords
  if (contentLower.includes('architect') || contentLower.includes('system')) {
    suggestions.push('architecture');
  }
  
  // Check for best practices
  if (contentLower.includes('best') || contentLower.includes('practice') || contentLower.includes('quality')) {
    suggestions.push('best-practices');
  }
  
  return suggestions;
}

// Infer content type from file path and category
export function inferContentType(doc: CollectionEntry<"docs">): string {
  const pathParts = doc.id.split('/');
  const collection = pathParts[0];
  
  // Content type is determined by collection structure
  switch (collection) {
    case 'patterns':
      return 'pattern';
    case 'implementations':
      return 'implementation';
    case 'guides':
      return 'guide';
    case 'tutorials':
      return 'tutorial';
    case 'references':
      return 'reference';
    default:
      return 'article';
  }
}

// Infer difficulty from tags and content
export function inferDifficulty(doc: CollectionEntry<"docs">): string {
  // Check explicit difficulty tags first
  const tags = (doc.data.tags || []).map(t => t.toLowerCase());
  if (tags.includes('beginner') || tags.includes('basic')) return 'beginner';
  if (tags.includes('advanced') || tags.includes('expert')) return 'advanced';
  if (tags.includes('intermediate')) return 'intermediate';
  
  // Infer from content and context
  const content = (doc.data.title + ' ' + doc.data.description).toLowerCase();
  
  if (content.includes('introduction') || content.includes('basic') || content.includes('getting started')) {
    return 'beginner';
  }
  if (content.includes('advanced') || content.includes('expert') || content.includes('complex')) {
    return 'advanced';
  }
  
  return 'intermediate'; // Default
}

// Validate document categorization
export function validateDocumentCategorization(doc: CollectionEntry<"docs">): {
  valid: boolean;
  issues: string[];
  suggestions: {
    categories: string[];
    tags: string[];
  };
} {
  const issues: string[] = [];
  
  // Check category
  if (!doc.data.category) {
    issues.push('Missing category');
  } else {
    const validCategory = validateCategory(doc.data.category);
    if (!validCategory) {
      issues.push(`Invalid category: ${doc.data.category}`);
    }
  }
  
  // Check tags
  if (!doc.data.tags || doc.data.tags.length === 0) {
    issues.push('No tags specified');
  } else if (doc.data.tags.length > 5) {
    issues.push('Too many tags (max 5 recommended)');
  }
  
  return {
    valid: issues.length === 0,
    issues,
    suggestions: {
      categories: suggestCategories(doc),
      tags: suggestTags(doc)
    }
  };
}

// Suggest tags based on content
export function suggestTags(doc: CollectionEntry<"docs">): string[] {
  const suggestions: string[] = [];
  const content = (doc.data.title + ' ' + doc.data.description).toLowerCase();
  
  // Check against tag facets
  Object.values(TAG_FACETS).flat().forEach(tag => {
    if (content.includes(tag)) {
      suggestions.push(tag);
    }
  });
  
  // Add difficulty based on content
  if (!doc.data.difficulty) {
    if (content.includes('basic') || content.includes('simple') || content.includes('introduction')) {
      suggestions.push('beginner');
    } else if (content.includes('advanced') || content.includes('complex')) {
      suggestions.push('advanced');
    } else {
      suggestions.push('intermediate');
    }
  }
  
  return suggestions;
}