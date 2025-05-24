import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import Counter, defaultdict
import hashlib

@dataclass
class ExtractedConcept:
    name: str
    concept_type: str  # 'technical', 'entity', 'topic', 'keyword'
    category: Optional[str] = None
    confidence: float = 0.0
    context: Optional[str] = None
    line_number: Optional[int] = None
    extraction_method: str = 'unknown'

@dataclass 
class ConceptRelation:
    source: str
    target: str
    relationship_type: str  # 'similar', 'related', 'part_of', 'used_with'
    strength: float = 0.0

class ConceptExtractor:
    """Intelligent concept extraction from documentation using multiple NLP techniques."""
    
    def __init__(self):
        # Technical patterns for programming/documentation concepts
        self.technical_patterns = {
            'programming_language': r'\b(Python|JavaScript|TypeScript|Rust|Go|Java|C\+\+|C#|Ruby|PHP|Swift)\b',
            'framework': r'\b(React|Vue|Angular|Django|Flask|FastAPI|Express|Spring|Rails|Laravel)\b',
            'library': r'\b(NumPy|Pandas|TensorFlow|PyTorch|scikit-learn|requests|axios|lodash)\b',
            'tool': r'\b(Docker|Kubernetes|Git|GitHub|GitLab|Jenkins|Terraform|AWS|Azure|GCP)\b',
            'database': r'\b(PostgreSQL|MySQL|MongoDB|Redis|SQLite|Elasticsearch|DynamoDB)\b',
            'api_method': r'\b(GET|POST|PUT|DELETE|PATCH)\s+\/([\w\/\-\{\}]+)',
            'code_element': r'`([^`]+)`',
            'class_name': r'\bclass\s+(\w+)',
            'function_name': r'\bdef\s+(\w+)|function\s+(\w+)',
            'variable_pattern': r'\$\{?(\w+)\}?',
            'file_extension': r'\.(\w+)\b',
            'url_pattern': r'https?:\/\/[\w\.\-\/\?\=\&]+',
            'version_pattern': r'v?\d+\.\d+(\.\d+)?',
        }
        
        # Concept categories for classification
        self.concept_categories = {
            'programming': ['language', 'syntax', 'paradigm', 'algorithm'],
            'tools': ['cli', 'editor', 'debugger', 'profiler', 'linter'],
            'frameworks': ['web', 'mobile', 'desktop', 'testing', 'orm'],
            'concepts': ['design pattern', 'architecture', 'principle', 'methodology'],
            'apis': ['rest', 'graphql', 'rpc', 'webhook', 'endpoint'],
            'data': ['format', 'structure', 'schema', 'model', 'type'],
            'systems': ['distributed', 'microservices', 'monolith', 'serverless'],
            'security': ['authentication', 'authorization', 'encryption', 'vulnerability'],
        }
        
        # Common technical stopwords to filter out
        self.technical_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'ours',
            'theirs', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'here', 'there',
            'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose',
            'if', 'unless', 'until', 'while', 'because', 'since', 'although', 'though',
            'example', 'note', 'see', 'also', 'more', 'information', 'documentation'
        }
    
    def normalize_concept(self, concept: str) -> str:
        """Normalize concept name for deduplication."""
        if not concept or not isinstance(concept, str):
            return ""
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', '', concept.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized
    
    def extract_pattern_concepts(self, content: str, line_number: int = None) -> List[ExtractedConcept]:
        """Extract concepts using regex patterns."""
        concepts = []
        
        for category, pattern in self.technical_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                concept_name = match.group(1) if match.groups() else match.group(0)
                
                # Skip if it's a common word or too short
                if (not concept_name or 
                    not isinstance(concept_name, str) or
                    concept_name.lower() in self.technical_stopwords or 
                    len(concept_name) < 2):
                    continue
                
                # Determine concept type based on category
                if category in ['programming_language', 'framework', 'library', 'tool', 'database']:
                    concept_type = 'technical'
                elif category in ['api_method', 'code_element', 'class_name', 'function_name']:
                    concept_type = 'entity'
                else:
                    concept_type = 'keyword'
                
                concepts.append(ExtractedConcept(
                    name=concept_name.strip(),
                    concept_type=concept_type,
                    category=category,
                    confidence=0.8,  # High confidence for pattern matches
                    context=match.group(0),
                    line_number=line_number,
                    extraction_method='pattern'
                ))
        
        return concepts
    
    def extract_markdown_concepts(self, content: str) -> List[ExtractedConcept]:
        """Extract concepts specific to markdown structure."""
        concepts = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Extract heading concepts
            heading_match = re.match(r'^#{1,6}\s+(.+)$', line)
            if heading_match:
                heading = heading_match.group(1).strip()
                concepts.append(ExtractedConcept(
                    name=heading,
                    concept_type='topic',
                    category='heading',
                    confidence=0.9,
                    context=line,
                    line_number=i,
                    extraction_method='markdown_structure'
                ))
            
            # Extract code block languages
            code_block_match = re.match(r'^```(\w+)', line)
            if code_block_match:
                language = code_block_match.group(1)
                concepts.append(ExtractedConcept(
                    name=language,
                    concept_type='technical',
                    category='programming_language',
                    confidence=0.9,
                    context=line,
                    line_number=i,
                    extraction_method='markdown_structure'
                ))
            
            # Extract bold/italic emphasized terms (likely important concepts)
            emphasis_matches = re.finditer(r'\*\*([^*]+)\*\*|__([^_]+)__|`([^`]+)`', line)
            for match in emphasis_matches:
                emphasized_text = next(group for group in match.groups() if group)
                if len(emphasized_text) > 2 and emphasized_text.lower() not in self.technical_stopwords:
                    concepts.append(ExtractedConcept(
                        name=emphasized_text,
                        concept_type='keyword',
                        category='emphasized',
                        confidence=0.6,
                        context=match.group(0),
                        line_number=i,
                        extraction_method='markdown_structure'
                    ))
        
        return concepts
    
    def extract_keyword_concepts(self, content: str) -> List[ExtractedConcept]:
        """Extract important keywords using frequency and context analysis."""
        # Simple keyword extraction based on frequency and capitalization
        words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b|[a-z]+(?:[A-Z][a-z]+)+\b', content)
        
        # Count frequencies
        word_counts = Counter(words)
        
        concepts = []
        for word, count in word_counts.items():
            if (len(word) > 3 and 
                word.lower() not in self.technical_stopwords and 
                count >= 2):  # Appears at least twice
                
                # Calculate confidence based on frequency and characteristics
                confidence = min(0.9, 0.3 + (count * 0.1) + (0.2 if word[0].isupper() else 0))
                
                concepts.append(ExtractedConcept(
                    name=word,
                    concept_type='keyword',
                    category='frequent_term',
                    confidence=confidence,
                    extraction_method='frequency'
                ))
        
        return concepts
    
    def deduplicate_concepts(self, concepts: List[ExtractedConcept]) -> List[ExtractedConcept]:
        """Remove duplicate concepts, keeping the one with highest confidence."""
        concept_map = {}
        
        for concept in concepts:
            normalized = self.normalize_concept(concept.name)
            if normalized not in concept_map or concept.confidence > concept_map[normalized].confidence:
                concept_map[normalized] = concept
        
        return list(concept_map.values())
    
    def calculate_concept_relations(self, concepts: List[ExtractedConcept], content: str) -> List[ConceptRelation]:
        """Calculate relationships between concepts based on co-occurrence."""
        relations = []
        concept_names = [c.name for c in concepts]
        
        # Simple co-occurrence analysis
        for i, concept1 in enumerate(concept_names):
            for j, concept2 in enumerate(concept_names[i+1:], i+1):
                # Count how often they appear together in the same paragraph/section
                pattern1 = re.escape(concept1)
                pattern2 = re.escape(concept2)
                
                # Check if they appear in the same sentence/paragraph
                sentences = re.split(r'[.!?]\s+', content)
                co_occurrences = 0
                
                for sentence in sentences:
                    if (re.search(pattern1, sentence, re.IGNORECASE) and 
                        re.search(pattern2, sentence, re.IGNORECASE)):
                        co_occurrences += 1
                
                if co_occurrences > 0:
                    # Calculate relationship strength
                    strength = min(1.0, co_occurrences * 0.3)
                    
                    relations.append(ConceptRelation(
                        source=concept1,
                        target=concept2,
                        relationship_type='related',
                        strength=strength
                    ))
        
        return relations
    
    def extract_all_concepts(self, content: str, file_id: int = None) -> Tuple[List[ExtractedConcept], List[ConceptRelation]]:
        """Extract all concepts from content using multiple methods."""
        all_concepts = []
        
        # Extract using different methods
        all_concepts.extend(self.extract_markdown_concepts(content))
        
        # Extract pattern-based concepts line by line for better context
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line_concepts = self.extract_pattern_concepts(line, i)
            all_concepts.extend(line_concepts)
        
        # Extract keyword concepts
        keyword_concepts = self.extract_keyword_concepts(content)
        all_concepts.extend(keyword_concepts)
        
        # Deduplicate concepts
        unique_concepts = self.deduplicate_concepts(all_concepts)
        
        # Calculate relationships
        relations = self.calculate_concept_relations(unique_concepts, content)
        
        return unique_concepts, relations
    
    def store_concepts(self, db_path: Path, file_id: int, concepts: List[ExtractedConcept], 
                      relations: List[ConceptRelation]) -> int:
        """Store extracted concepts and relationships in the database."""
        stored_count = 0
        
        with sqlite3.connect(db_path) as conn:
            concept_id_map = {}
            
            # Store concepts
            for concept in concepts:
                normalized_name = self.normalize_concept(concept.name)
                
                # Check if concept already exists
                cursor = conn.execute("""
                    SELECT id FROM concepts WHERE normalized_name = ? AND concept_type = ?
                """, (normalized_name, concept.concept_type))
                
                existing = cursor.fetchone()
                if existing:
                    concept_id = existing[0]
                    # Update confidence if this one is higher
                    conn.execute("""
                        UPDATE concepts SET confidence = MAX(confidence, ?)
                        WHERE id = ?
                    """, (concept.confidence, concept_id))
                else:
                    # Insert new concept
                    cursor = conn.execute("""
                        INSERT INTO concepts (name, concept_type, category, confidence, normalized_name)
                        VALUES (?, ?, ?, ?, ?)
                    """, (concept.name, concept.concept_type, concept.category, 
                          concept.confidence, normalized_name))
                    concept_id = cursor.lastrowid
                
                concept_id_map[concept.name] = concept_id
                
                # Store file-concept relationship
                conn.execute("""
                    INSERT OR REPLACE INTO file_concepts 
                    (file_id, concept_id, relevance_score, frequency, first_mention_line, 
                     context_snippet, extraction_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (file_id, concept_id, concept.confidence, 1, concept.line_number,
                      concept.context, concept.extraction_method))
                
                stored_count += 1
            
            # Store relationships
            for relation in relations:
                if relation.source in concept_id_map and relation.target in concept_id_map:
                    source_id = concept_id_map[relation.source]
                    target_id = concept_id_map[relation.target]
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO concept_relationships
                        (source_concept_id, target_concept_id, relationship_type, strength)
                        VALUES (?, ?, ?, ?)
                    """, (source_id, target_id, relation.relationship_type, relation.strength))
        
        return stored_count