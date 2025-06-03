import type { CollectionEntry } from "astro:content";

export interface DirectoryNode {
  path: string;
  name: string;
  level: number;
  children: CollectionEntry<"docs">[];
  subdirectories: DirectoryNode[];
  parent?: string;
  type: string;
}

export interface NavigationNode {
  id: string;
  title: string;
  url: string;
  type: 'file' | 'directory';
  template?: string;
  level: number;
  children: NavigationNode[];
  isActive?: boolean;
}

export function getDirectoryStructure(docs: CollectionEntry<"docs">[]): DirectoryNode[] {
  const directoryMap = new Map<string, DirectoryNode>();
  
  // Initialize root directories
  docs.forEach(doc => {
    const parts = doc.id.split('/');
    
    // Create directory nodes for each level
    for (let i = 1; i <= parts.length - 1; i++) {
      const dirPath = parts.slice(0, i).join('/');
      const dirName = parts[i - 1];
      const parentPath = i > 1 ? parts.slice(0, i - 1).join('/') : undefined;
      
      if (!directoryMap.has(dirPath)) {
        directoryMap.set(dirPath, {
          path: dirPath,
          name: dirName,
          level: i,
          children: [],
          subdirectories: [],
          parent: parentPath,
          type: inferDirectoryType(dirName, docs.filter(d => d.id.startsWith(dirPath)))
        });
      }
    }
  });
  
  // Populate children and subdirectories
  directoryMap.forEach((dir, path) => {
    // Add direct child documents
    dir.children = docs.filter(doc => {
      const docParts = doc.id.split('/');
      const dirParts = path.split('/');
      return docParts.length === dirParts.length + 1 && 
             docParts.slice(0, dirParts.length).join('/') === path;
    });
    
    // Add subdirectories
    dir.subdirectories = Array.from(directoryMap.values()).filter(subdir => 
      subdir.parent === path
    );
  });
  
  return Array.from(directoryMap.values()).filter(dir => dir.level === 1);
}

export function inferDirectoryType(dirName: string, contents: CollectionEntry<"docs">[]): string {
  // Analyze directory name and contents to infer type
  const name = dirName.toLowerCase();
  
  if (name.includes('pattern')) return 'patterns';
  if (name.includes('implement')) return 'implementations';
  if (name.includes('guide')) return 'guides';
  if (name.includes('tutorial')) return 'tutorials';
  if (name.includes('api') || name.includes('reference')) return 'reference';
  if (name.includes('example')) return 'examples';
  
  // Analyze content types if directory name is ambiguous
  const contentTypes = contents.map(doc => doc.data.template || 'default');
  const mostCommonType = contentTypes.reduce((a, b, i, arr) => 
    arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b, 'default'
  );
  
  return mostCommonType;
}

export function buildNavigationTree(docs: CollectionEntry<"docs">[], currentPath?: string): NavigationNode[] {
  const directories = getDirectoryStructure(docs);
  
  function buildNode(item: DirectoryNode | CollectionEntry<"docs">, level: number = 0): NavigationNode {
    if ('id' in item) {
      // It's a document
      const isActive = currentPath === `/docs/${item.id}/` || currentPath === item.id;
      return {
        id: item.id,
        title: item.data.sidebar?.label || item.data.title,
        url: `/docs/${item.id}/`,
        type: 'file',
        template: item.data.template,
        level,
        children: [],
        isActive
      };
    } else {
      // It's a directory
      const isActive = currentPath === `/docs/${item.path}/` || currentPath === item.path;
      const children: NavigationNode[] = [];
      
      // Add child documents
      item.children
        .filter(doc => !doc.data.sidebar?.hidden)
        .sort((a, b) => (a.data.sidebar?.order || 999) - (b.data.sidebar?.order || 999))
        .forEach(doc => {
          children.push(buildNode(doc, level + 1));
        });
      
      // Add subdirectories
      item.subdirectories
        .sort((a, b) => a.name.localeCompare(b.name))
        .forEach(subdir => {
          children.push(buildNode(subdir, level + 1));
        });
      
      return {
        id: item.path,
        title: item.name.charAt(0).toUpperCase() + item.name.slice(1),
        url: `/docs/${item.path}/`,
        type: 'directory',
        level,
        children,
        isActive
      };
    }
  }
  
  return directories.map(dir => buildNode(dir));
}

export function generateBreadcrumbs(slug: string): Array<{name: string, url: string}> {
  const parts = typeof slug === 'string' ? slug.split('/') : [];
  const breadcrumbs = [{ name: 'wiki', url: '/docs/' }];
  
  for (let i = 0; i < parts.length; i++) {
    const path = parts.slice(0, i + 1).join('/');
    const name = parts[i];
    const url = `/docs/${path}/`;
    breadcrumbs.push({ name, url });
  }
  
  return breadcrumbs;
}

export function findRelatedContent(
  currentDoc: CollectionEntry<"docs">, 
  allDocs: CollectionEntry<"docs">[]
): CollectionEntry<"docs">[] {
  const related = new Set<CollectionEntry<"docs">>();
  
  // Same directory siblings
  const currentDir = currentDoc.id.split('/').slice(0, -1).join('/');
  const siblings = allDocs.filter(doc => {
    const docDir = doc.id.split('/').slice(0, -1).join('/');
    return doc.id !== currentDoc.id && docDir === currentDir;
  });
  siblings.slice(0, 3).forEach(doc => related.add(doc));
  
  // Tag-based relationships
  if (currentDoc.data.tags) {
    const tagMatches = allDocs.filter(doc => 
      doc.id !== currentDoc.id &&
      doc.data.tags?.some(tag => currentDoc.data.tags?.includes(tag))
    );
    tagMatches.slice(0, 2).forEach(doc => related.add(doc));
  }
  
  // Explicit relationships
  if (currentDoc.data.relatedPages) {
    currentDoc.data.relatedPages.forEach(pageId => {
      const relatedDoc = allDocs.find(doc => doc.id === pageId);
      if (relatedDoc) related.add(relatedDoc);
    });
  }
  
  // Cross-type relationships (patterns <-> implementations)
  if (currentDoc.data.pattern) {
    const patternDoc = allDocs.find(doc => doc.id === `patterns/${currentDoc.data.pattern}`);
    if (patternDoc) related.add(patternDoc);
  }
  
  if (currentDoc.data.implementations) {
    currentDoc.data.implementations.forEach(impl => {
      const implDoc = allDocs.find(doc => doc.id === `implementations/${impl}`);
      if (implDoc) related.add(implDoc);
    });
  }
  
  return Array.from(related).slice(0, 5);
}

// Note: getPageType has been moved to categorization.ts as inferContentType

export function isDirectoryIndex(slug: string, docs: CollectionEntry<"docs">[]): boolean {
  // Check if this slug represents a directory that should have an index page
  const hasChildrenInDirectory = docs.some(doc => {
    const docParts = doc.id.split('/');
    const slugParts = slug.split('/');
    return docParts.length > slugParts.length && 
           docParts.slice(0, slugParts.length).join('/') === slug;
  });
  
  return hasChildrenInDirectory;
}

export function getDirectoryContents(directoryPath: string, docs: CollectionEntry<"docs">[]): {
  childDocs: CollectionEntry<"docs">[],
  subdirectories: string[]
} {
  const childDocs = docs.filter(doc => {
    const docParts = doc.id.split('/');
    const dirParts = directoryPath.split('/');
    return docParts.length === dirParts.length + 1 && 
           docParts.slice(0, dirParts.length).join('/') === directoryPath;
  });
  
  const subdirSet = new Set<string>();
  docs.forEach(doc => {
    const docParts = doc.id.split('/');
    const dirParts = directoryPath.split('/');
    if (docParts.length > dirParts.length + 1 && 
        docParts.slice(0, dirParts.length).join('/') === directoryPath) {
      const subdir = docParts.slice(0, dirParts.length + 1).join('/');
      subdirSet.add(subdir);
    }
  });
  
  return {
    childDocs,
    subdirectories: Array.from(subdirSet)
  };
}