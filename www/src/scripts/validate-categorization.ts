import { getCollection } from "astro:content";
import { validateDocumentCategorization, CATEGORY_HIERARCHY, TAG_FACETS } from "../utils/categorization";

export async function validateAllDocuments() {
  const allDocs = await getCollection("docs");
  const results = {
    total: allDocs.length,
    valid: 0,
    invalid: 0,
    issues: [] as Array<{
      file: string;
      issues: string[];
      suggestions: any;
    }>
  };

  console.log("\n📋 Validating Knowledge Base Categorization...\n");

  allDocs.forEach(doc => {
    const validation = validateDocumentCategorization(doc);
    
    if (validation.valid) {
      results.valid++;
    } else {
      results.invalid++;
      results.issues.push({
        file: doc.id,
        issues: validation.issues,
        suggestions: validation.suggestions
      });
      
      console.log(`❌ ${doc.id}`);
      validation.issues.forEach(issue => {
        console.log(`   - ${issue}`);
      });
      
      if (validation.suggestions.categories.length > 0) {
        console.log(`   💡 Suggested categories: ${validation.suggestions.categories.join(', ')}`);
      }
      if (validation.suggestions.tags.length > 0) {
        console.log(`   💡 Suggested tags: ${validation.suggestions.tags.join(', ')}`);
      }
      console.log('');
    }
  });

  // Summary
  console.log("\n📊 Validation Summary:");
  console.log(`   Total documents: ${results.total}`);
  console.log(`   ✅ Valid: ${results.valid}`);
  console.log(`   ❌ Invalid: ${results.invalid}`);
  
  if (results.invalid > 0) {
    console.log("\n⚠️  Please fix the categorization issues above to maintain knowledge base quality.");
  } else {
    console.log("\n✨ All documents are properly categorized!");
  }

  // Print available categories and tags
  console.log("\n📚 Available Categories:");
  Object.values(CATEGORY_HIERARCHY).forEach(cat => {
    if (!cat.parent) {
      console.log(`   - ${cat.id}: ${cat.name}`);
      cat.children.forEach(childId => {
        const child = CATEGORY_HIERARCHY[childId];
        if (child) {
          console.log(`     └─ ${child.id}: ${child.name}`);
        }
      });
    }
  });

  console.log("\n🏷️  Available Tag Facets:");
  Object.entries(TAG_FACETS).forEach(([facet, tags]) => {
    console.log(`   ${facet}: ${tags.join(', ')}`);
  });

  return results;
}