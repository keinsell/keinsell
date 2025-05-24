import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import markdown
from markdown.extensions import toc
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as ET
from .vector_storage import VectorStorage
from .concept_extractor import ConceptExtractor


@dataclass
class MarkdownFile:
    id: int
    path: str
    title: str
    content: str
    ast_json: str
    checksum: str
    mtime: float
    created_at: str
    updated_at: str


@dataclass
class WikiLink:
    id: int
    source_file_id: int
    target: str
    line_number: int
    context: str
    created_at: str


class ASTExtractor(Treeprocessor):
    """Markdown tree processor that extracts AST structure."""
    
    def __init__(self, md):
        super().__init__(md)
        self.ast_data = {}
    
    def run(self, root):
        """Process the ElementTree and extract structure."""
        self.ast_data = self._element_to_dict(root)
        return root
    
    def _element_to_dict(self, element) -> Dict[str, Any]:
        """Convert ElementTree element to dictionary representation."""
        result = {
            'tag': element.tag,
            'text': element.text,
            'tail': element.tail,
            'attrib': dict(element.attrib),
            'children': []
        }
        
        for child in element:
            result['children'].append(self._element_to_dict(child))
        
        return result


class ASTExtension(Extension):
    """Markdown extension that adds AST extraction capability."""
    
    def __init__(self, **kwargs):
        self.ast_extractor = None
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        self.ast_extractor = ASTExtractor(md)
        md.treeprocessors.register(self.ast_extractor, 'ast_extractor', 0)


class MarkdownStorage:
    """SQLite-based storage for markdown files with AST parsing and wikilink relations."""
    
    def __init__(self, db_path: Optional[Path] = None, enable_vectors: bool = True):
        if db_path is None:
            from platformdirs import user_data_dir
            data_dir = Path(user_data_dir("zkk", "zkk"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "knowledge_base.db"
        
        self.db_path = db_path
        self.md_processor = self._setup_markdown_processor()
        self.vector_storage = VectorStorage(db_path) if enable_vectors else None
        self.concept_extractor = ConceptExtractor()
        self._progress_callback = None
        self._init_db()
    
    def _setup_markdown_processor(self) -> markdown.Markdown:
        """Setup markdown processor with AST extraction."""
        self.ast_extension = ASTExtension()
        return markdown.Markdown(
            extensions=[
                'toc',
                'tables',
                'fenced_code',
                'codehilite',
                self.ast_extension
            ]
        )
    
    def _init_db(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS markdown_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ast_json TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    mtime REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS wikilinks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file_id INTEGER NOT NULL,
                    target TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    context TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_file_id) REFERENCES markdown_files (id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    concept_type TEXT NOT NULL, -- 'technical', 'entity', 'topic', 'keyword'
                    category TEXT, -- 'programming', 'tool', 'framework', 'concept', 'api', etc.
                    confidence REAL NOT NULL DEFAULT 0.0,
                    normalized_name TEXT NOT NULL, -- for deduplication
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS file_concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    concept_id INTEGER NOT NULL,
                    relevance_score REAL NOT NULL DEFAULT 0.0,
                    frequency INTEGER NOT NULL DEFAULT 1,
                    first_mention_line INTEGER,
                    context_snippet TEXT,
                    extraction_method TEXT, -- 'ner', 'keyword', 'pattern', 'embedding'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES markdown_files (id) ON DELETE CASCADE,
                    FOREIGN KEY (concept_id) REFERENCES concepts (id) ON DELETE CASCADE,
                    UNIQUE(file_id, concept_id)
                );
                
                CREATE TABLE IF NOT EXISTS concept_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_concept_id INTEGER NOT NULL,
                    target_concept_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL, -- 'similar', 'related', 'part_of', 'used_with'
                    strength REAL NOT NULL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_concept_id) REFERENCES concepts (id) ON DELETE CASCADE,
                    FOREIGN KEY (target_concept_id) REFERENCES concepts (id) ON DELETE CASCADE,
                    UNIQUE(source_concept_id, target_concept_id, relationship_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_wikilinks_source ON wikilinks(source_file_id);
                CREATE INDEX IF NOT EXISTS idx_wikilinks_target ON wikilinks(target);
                CREATE INDEX IF NOT EXISTS idx_markdown_files_path ON markdown_files(path);
                CREATE INDEX IF NOT EXISTS idx_markdown_files_checksum ON markdown_files(checksum);
                CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(normalized_name);
                CREATE INDEX IF NOT EXISTS idx_concepts_type ON concepts(concept_type);
                CREATE INDEX IF NOT EXISTS idx_file_concepts_file ON file_concepts(file_id);
                CREATE INDEX IF NOT EXISTS idx_file_concepts_concept ON file_concepts(concept_id);
                CREATE INDEX IF NOT EXISTS idx_file_concepts_relevance ON file_concepts(relevance_score);
                CREATE INDEX IF NOT EXISTS idx_concept_relationships_source ON concept_relationships(source_concept_id);
                CREATE INDEX IF NOT EXISTS idx_concept_relationships_target ON concept_relationships(target_concept_id);
                
                CREATE TRIGGER IF NOT EXISTS update_markdown_files_timestamp 
                AFTER UPDATE ON markdown_files
                BEGIN
                    UPDATE markdown_files SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;
            """)
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate MD5 checksum of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return file_path.stem
    
    def _extract_wikilinks(self, content: str) -> List[Dict[str, Any]]:
        """Extract wikilinks from markdown content."""
        import re
        wikilink_pattern = re.compile(r'\[\[([^\[\]]+)\]\]')
        links = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for match in wikilink_pattern.finditer(line):
                target = match.group(1).strip()
                # Handle aliases: [[Target|Alias]] -> Target
                if '|' in target:
                    target = target.split('|')[0].strip()
                
                links.append({
                    'target': target,
                    'line_number': line_num,
                    'context': line.strip()
                })
        
        return links
    
    def _parse_to_ast(self, content: str) -> Dict[str, Any]:
        """Parse markdown content to AST."""
        # Reset the processor for fresh parsing
        self.md_processor.reset()
        
        # Process the markdown
        html = self.md_processor.convert(content)
        
        # Get AST data from the extension
        if self.ast_extension.ast_extractor:
            return self.ast_extension.ast_extractor.ast_data
        
        return {}
    
    def store_file(self, file_path: Path, force_update: bool = False) -> Optional[int]:
        """Store or update a markdown file in the database."""
        if not file_path.exists() or not file_path.suffix.lower() in ['.md', '.markdown']:
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            checksum = self._calculate_checksum(content)
            mtime = file_path.stat().st_mtime
            path_str = str(file_path.resolve())
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if file exists and if update is needed
                cursor = conn.execute(
                    "SELECT id, checksum, mtime FROM markdown_files WHERE path = ?",
                    (path_str,)
                )
                existing = cursor.fetchone()
                
                if existing and not force_update:
                    existing_id, existing_checksum, existing_mtime = existing
                    if existing_checksum == checksum and existing_mtime == mtime:
                        return existing_id  # No update needed
                
                # Extract data
                title = self._extract_title(content, file_path)
                ast_data = self._parse_to_ast(content)
                ast_json = json.dumps(ast_data, indent=2)
                wikilinks = self._extract_wikilinks(content)
                
                if existing:
                    # Update existing file
                    file_id = existing[0]
                    conn.execute("""
                        UPDATE markdown_files 
                        SET title = ?, content = ?, ast_json = ?, checksum = ?, mtime = ?
                        WHERE id = ?
                    """, (title, content, ast_json, checksum, mtime, file_id))
                    
                    # Delete existing wikilinks
                    conn.execute("DELETE FROM wikilinks WHERE source_file_id = ?", (file_id,))
                else:
                    # Insert new file
                    cursor = conn.execute("""
                        INSERT INTO markdown_files (path, title, content, ast_json, checksum, mtime)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (path_str, title, content, ast_json, checksum, mtime))
                    file_id = cursor.lastrowid
                
                # Insert wikilinks
                for link in wikilinks:
                    conn.execute("""
                        INSERT INTO wikilinks (source_file_id, target, line_number, context)
                        VALUES (?, ?, ?, ?)
                    """, (file_id, link['target'], link['line_number'], link['context']))
                
                conn.commit()
                
                # Generate embeddings if vector storage is enabled
                if self.vector_storage:
                    try:
                        self.vector_storage.store_document_embeddings(file_id, content, force_update, path_str, self._progress_callback)
                    except Exception as e:
                        print(f"Warning: Failed to generate embeddings for {file_path}: {e}")
                
                # Extract and store concepts
                try:
                    if self._progress_callback:
                        self._progress_callback("concept_extraction_start", f"Analyzing concepts in {file_path.name}", None)
                    
                    concepts, relations = self.concept_extractor.extract_all_concepts(content, file_id)
                    
                    if self._progress_callback:
                        self._progress_callback("concept_storage", f"Storing {len(concepts)} concepts", None)
                    
                    concept_count = self.concept_extractor.store_concepts(self.db_path, file_id, concepts, relations)
                    
                    if self._progress_callback:
                        self._progress_callback("concept_extraction_complete", f"Extracted {concept_count} concepts from {file_path.name}", None)
                except Exception as e:
                    if self._progress_callback:
                        self._progress_callback("concept_extraction_error", f"Failed to extract concepts: {e}", None)
                    print(f"Warning: Failed to extract concepts for {file_path}: {e}")
                
                return file_id
                
        except Exception as e:
            print(f"Error storing file {file_path}: {e}")
            return None
    
    def get_file(self, file_id: int) -> Optional[MarkdownFile]:
        """Retrieve a markdown file by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM markdown_files WHERE id = ?
            """, (file_id,))
            row = cursor.fetchone()
            
            if row:
                return MarkdownFile(**dict(row))
            return None
    
    def get_file_by_path(self, path: str) -> Optional[MarkdownFile]:
        """Retrieve a markdown file by path."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM markdown_files WHERE path = ?
            """, (str(Path(path).resolve()),))
            row = cursor.fetchone()
            
            if row:
                return MarkdownFile(**dict(row))
            return None
    
    def get_wikilinks_from_file(self, file_id: int) -> List[WikiLink]:
        """Get all wikilinks from a specific file."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM wikilinks WHERE source_file_id = ?
                ORDER BY line_number
            """, (file_id,))
            
            return [WikiLink(**dict(row)) for row in cursor.fetchall()]
    
    def get_wikilinks_to_target(self, target: str) -> List[WikiLink]:
        """Get all wikilinks pointing to a target."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM wikilinks WHERE target = ?
                ORDER BY source_file_id, line_number
            """, (target,))
            
            return [WikiLink(**dict(row)) for row in cursor.fetchall()]
    
    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Search for content across all files."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, path, title, content FROM markdown_files 
                WHERE title LIKE ? OR content LIKE ?
            """, (f"%{query}%", f"%{query}%"))
            
            results = []
            for row in cursor.fetchall():
                content_lines = row['content'].split('\n')
                for line_num, line in enumerate(content_lines, 1):
                    if query.lower() in line.lower():
                        results.append({
                            'file_id': row['id'],
                            'path': row['path'],
                            'title': row['title'],
                            'line': line_num,
                            'content': line.strip()
                        })
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total files
            cursor = conn.execute("SELECT COUNT(*) FROM markdown_files")
            stats['total_files'] = cursor.fetchone()[0]
            
            # Total wikilinks
            cursor = conn.execute("SELECT COUNT(*) FROM wikilinks")
            stats['total_wikilinks'] = cursor.fetchone()[0]
            
            # Broken links (targets that don't exist as files)
            cursor = conn.execute("""
                SELECT DISTINCT target FROM wikilinks 
                WHERE target NOT IN (
                    SELECT title FROM markdown_files
                    UNION
                    SELECT REPLACE(REPLACE(path, '.md', ''), '.markdown', '') FROM markdown_files
                )
            """)
            broken_targets = [row[0] for row in cursor.fetchall()]
            stats['broken_links'] = len(broken_targets)
            stats['broken_targets'] = broken_targets
            
            # Orphaned files (files with no incoming links)
            cursor = conn.execute("""
                SELECT path, title FROM markdown_files 
                WHERE id NOT IN (
                    SELECT DISTINCT mf.id FROM markdown_files mf
                    JOIN wikilinks wl ON (
                        wl.target = mf.title OR 
                        wl.target = REPLACE(REPLACE(mf.path, '.md', ''), '.markdown', '')
                    )
                )
            """)
            orphaned_files = [(row[0], row[1]) for row in cursor.fetchall()]
            stats['orphaned_files'] = len(orphaned_files)
            stats['orphaned_file_list'] = orphaned_files
            
            # Average links per file
            if stats['total_files'] > 0:
                stats['avg_links_per_file'] = stats['total_wikilinks'] / stats['total_files']
            else:
                stats['avg_links_per_file'] = 0
            
            return stats
    
    def index_directory(self, directory: Path, force_refresh: bool = False) -> int:
        """Index all markdown files in a directory."""
        if not directory.exists() or not directory.is_dir():
            return 0
        
        markdown_files = []
        for pattern in ['*.md', '*.markdown']:
            markdown_files.extend(directory.rglob(pattern))
        
        indexed_count = 0
        for file_path in markdown_files:
            if self.store_file(file_path, force_refresh):
                indexed_count += 1
        
        return indexed_count
    
    def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Perform semantic search across the knowledge base."""
        if not self.vector_storage:
            raise ValueError("Vector storage is not enabled. Initialize with enable_vectors=True")
        
        matches = self.vector_storage.semantic_search(query, top_k, similarity_threshold)
        
        results = []
        for match in matches:
            # Convert file path to relative path if possible
            try:
                file_path = Path(match.file_path)
                relative_path = match.file_path  # Keep full path as fallback
            except:
                relative_path = match.file_path
            
            results.append({
                'file_path': relative_path,
                'file_title': match.file_title,
                'content': match.chunk.content,
                'similarity_score': match.similarity_score,
                'chunk_index': match.chunk.chunk_index,
                'start_char': match.chunk.start_char,
                'end_char': match.chunk.end_char
            })
        
        return results
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""
        if not self.vector_storage:
            return {'enabled': False}
        
        stats = self.vector_storage.get_embedding_stats()
        stats['enabled'] = True
        return stats
    
    def set_progress_callback(self, callback):
        """Set progress callback for operations."""
        self._progress_callback = callback
        if self.vector_storage:
            self.vector_storage.progress_callback = callback
    
    def reindex_embeddings(self, force_refresh: bool = False, progress_callback=None) -> int:
        """Reindex all embeddings."""
        if not self.vector_storage:
            raise ValueError("Vector storage is not enabled")
        
        # Set the progress callback
        if progress_callback:
            self.set_progress_callback(progress_callback)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, content FROM markdown_files")
            files = cursor.fetchall()
        
        # Add concept extraction progress tracking
        def enhanced_callback(phase, message, progress):
            if progress_callback:
                progress_callback(phase, message, progress)
        
        # First pass: embeddings
        embedding_result = self.vector_storage.reindex_all_embeddings(files, enhanced_callback)
        
        # Second pass: concept extraction for all files
        if progress_callback:
            progress_callback("concept_reindex_start", f"Extracting concepts from {len(files)} files", 0)
        
        total_concepts = 0
        for file_idx, (file_id, content) in enumerate(files):
            file_data = self.get_file(file_id)
            if file_data:
                progress_pct = (file_idx / len(files)) * 100 if files else 0
                if progress_callback:
                    progress_callback("concept_reindex_progress", f"Analyzing concepts in file {file_idx + 1}/{len(files)}", progress_pct)
                
                try:
                    concepts, relations = self.concept_extractor.extract_all_concepts(content, file_id)
                    concept_count = self.concept_extractor.store_concepts(self.db_path, file_id, concepts, relations)
                    total_concepts += concept_count
                except Exception as e:
                    print(f"Warning: Failed to extract concepts for file {file_id}: {e}")
        
        if progress_callback:
            progress_callback("concept_reindex_complete", f"Extracted {total_concepts} concepts from {len(files)} files", 100)
        
        return embedding_result
    
    def remove_file(self, file_path: Path) -> bool:
        """Remove a file from the database."""
        path_str = str(file_path.resolve())
        
        with sqlite3.connect(self.db_path) as conn:
            # Get file_id before deletion for vector cleanup
            cursor = conn.execute("SELECT id FROM markdown_files WHERE path = ?", (path_str,))
            file_data = cursor.fetchone()
            
            if file_data and self.vector_storage:
                file_id = file_data[0]
                self.vector_storage.remove_file_embeddings(file_id)
            
            cursor = conn.execute("DELETE FROM markdown_files WHERE path = ?", (path_str,))
            return cursor.rowcount > 0
    
    def get_file_concepts(self, file_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top concepts for a specific file."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT c.name, c.concept_type, c.category, c.confidence,
                       fc.relevance_score, fc.frequency, fc.extraction_method
                FROM concepts c
                JOIN file_concepts fc ON c.id = fc.concept_id
                WHERE fc.file_id = ?
                ORDER BY fc.relevance_score DESC, fc.frequency DESC
                LIMIT ?
            """, (file_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_files_with_concepts(self) -> List[Dict[str, Any]]:
        """Get all files with their top concepts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT mf.id, mf.path, mf.title, mf.created_at,
                       COUNT(fc.concept_id) as concept_count
                FROM markdown_files mf
                LEFT JOIN file_concepts fc ON mf.id = fc.file_id
                GROUP BY mf.id, mf.path, mf.title, mf.created_at
                ORDER BY mf.title
            """)
            
            files = []
            for row in cursor.fetchall():
                file_data = dict(row)
                # Get top 5 concepts for this file
                file_data['concepts'] = self.get_file_concepts(file_data['id'], 5)
                files.append(file_data)
            
            return files
    
    def get_concept_stats(self) -> Dict[str, Any]:
        """Get statistics about extracted concepts."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total concepts
            cursor = conn.execute("SELECT COUNT(*) FROM concepts")
            stats['total_concepts'] = cursor.fetchone()[0]
            
            # Concepts by type
            cursor = conn.execute("""
                SELECT concept_type, COUNT(*) as count
                FROM concepts
                GROUP BY concept_type
                ORDER BY count DESC
            """)
            stats['concepts_by_type'] = dict(cursor.fetchall())
            
            # Concepts by category
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM concepts
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
            stats['top_categories'] = dict(cursor.fetchall())
            
            # Files with concepts
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT file_id) FROM file_concepts
            """)
            stats['files_with_concepts'] = cursor.fetchone()[0]
            
            # Top concepts overall
            cursor = conn.execute("""
                SELECT c.name, c.concept_type, COUNT(fc.file_id) as file_count,
                       AVG(fc.relevance_score) as avg_relevance
                FROM concepts c
                JOIN file_concepts fc ON c.id = fc.concept_id
                GROUP BY c.id, c.name, c.concept_type
                ORDER BY file_count DESC, avg_relevance DESC
                LIMIT 10
            """)
            stats['top_concepts'] = [
                {
                    'name': row[0],
                    'type': row[1], 
                    'file_count': row[2],
                    'avg_relevance': round(row[3], 3)
                }
                for row in cursor.fetchall()
            ]
            
            return stats