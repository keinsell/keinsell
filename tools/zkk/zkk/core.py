import re
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from platformdirs import user_cache_dir
from .storage import MarkdownStorage

@dataclass
class WikiLink:
    source_file: str
    target: str
    line_number: int
    context: str

@dataclass
class Note:
    path: Path
    title: str
    content: str
    links: List[WikiLink]
    mtime: float = 0.0  # File modification time for cache invalidation

class KnowledgeBase:
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path).resolve()
        self.notes: Dict[str, Note] = {}
        self.wikilink_pattern = re.compile(r'\[\[([^\[\]]+)\]\]')
        self.cache_dir = Path(user_cache_dir("zkk", "zkk"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.storage = MarkdownStorage()
    
    def _get_cache_key(self) -> str:
        """Generate cache key based on root path."""
        return hashlib.sha256(str(self.root_path).encode()).hexdigest()[:16]
    
    def _get_cache_file(self) -> Path:
        """Get cache file path for this knowledge base."""
        return self.cache_dir / f"index_{self._get_cache_key()}.json"
    
    def _save_cache(self):
        """Save indexed notes to cache."""
        cache_file = self._get_cache_file()
        cache_data = {
            'root_path': str(self.root_path),
            'notes': {}
        }
        
        # Convert notes to serializable format
        unique_notes = {}
        for note in self.notes.values():
            unique_notes[str(note.path)] = note
        
        for path_str, note in unique_notes.items():
            cache_data['notes'][path_str] = {
                'path': str(note.path),
                'title': note.title,
                'content': note.content,
                'mtime': note.mtime,
                'links': [asdict(link) for link in note.links]
            }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            # Silently fail if cache write fails
            pass
    
    def _load_cache(self) -> bool:
        """Load notes from cache if valid. Returns True if cache was loaded."""
        cache_file = self._get_cache_file()
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verify cache is for the same root path
            if cache_data.get('root_path') != str(self.root_path):
                return False
            
            # Load notes and verify file modification times
            self.notes.clear()
            for path_str, note_data in cache_data.get('notes', {}).items():
                file_path = Path(note_data['path'])
                
                # Check if file still exists and hasn't been modified
                if not file_path.exists():
                    continue
                
                current_mtime = file_path.stat().st_mtime
                cached_mtime = note_data.get('mtime', 0)
                
                if current_mtime != cached_mtime:
                    # File has been modified, cache is invalid
                    return False
                
                # Reconstruct WikiLink objects
                links = []
                for link_data in note_data.get('links', []):
                    links.append(WikiLink(
                        source_file=link_data['source_file'],
                        target=link_data['target'],
                        line_number=link_data['line_number'],
                        context=link_data['context']
                    ))
                
                note = Note(
                    path=file_path,
                    title=note_data['title'],
                    content=note_data['content'],
                    links=links,
                    mtime=cached_mtime
                )
                
                # Use both filename and title as keys for lookup
                relative_path = str(file_path.relative_to(self.root_path))
                self.notes[relative_path] = note
                self.notes[self._normalize_title(note.title)] = note
                self.notes[self._normalize_title(file_path.stem)] = note
            
            return True
            
        except Exception as e:
            # Cache is corrupted or invalid
            return False
        
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extract title from content or use filename."""
        # Look for H1 markdown title
        title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # Use filename without extension as fallback
        return file_path.stem
    
    def _extract_wikilinks(self, content: str, source_file: str) -> List[WikiLink]:
        """Extract all wikilinks from content."""
        links = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for match in self.wikilink_pattern.finditer(line):
                target = match.group(1).strip()
                # Handle aliases: [[Target|Alias]] -> Target
                if '|' in target:
                    target = target.split('|')[0].strip()
                
                links.append(WikiLink(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    context=line.strip()
                ))
        
        return links
    
    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the knowledge base."""
        markdown_files = []
        for pattern in ['*.md', '*.markdown']:
            markdown_files.extend(self.root_path.rglob(pattern))
        return markdown_files
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        return title.lower().strip()
    
    def index(self, force_refresh: bool = False) -> int:
        """Index all markdown files in the knowledge base using SQLite storage."""
        # Use the new storage system
        indexed_count = self.storage.index_directory(self.root_path, force_refresh)
        
        # Populate notes dict for backward compatibility
        self.notes.clear()
        markdown_files = self._find_markdown_files()
        
        for file_path in markdown_files:
            try:
                stored_file = self.storage.get_file_by_path(str(file_path))
                if stored_file:
                    # Convert storage format to legacy Note format
                    storage_links = self.storage.get_wikilinks_from_file(stored_file.id)
                    links = [
                        WikiLink(
                            source_file=str(file_path.relative_to(self.root_path)),
                            target=link.target,
                            line_number=link.line_number,
                            context=link.context
                        ) for link in storage_links
                    ]
                    
                    note = Note(
                        path=file_path,
                        title=stored_file.title,
                        content=stored_file.content,
                        links=links,
                        mtime=stored_file.mtime
                    )
                    
                    # Use both filename and title as keys for lookup
                    relative_path = str(file_path.relative_to(self.root_path))
                    self.notes[relative_path] = note
                    self.notes[self._normalize_title(stored_file.title)] = note
                    self.notes[self._normalize_title(file_path.stem)] = note
                    
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return indexed_count
    
    def search(self, query: str) -> List[Dict[str, str]]:
        """Search for content across all notes using storage system."""
        storage_results = self.storage.search_content(query)
        
        results = []
        for result in storage_results:
            # Convert file path to relative path
            file_path = Path(result['path'])
            try:
                relative_path = str(file_path.relative_to(self.root_path))
            except ValueError:
                relative_path = result['path']
            
            results.append({
                'file': relative_path,
                'line': result['line'],
                'content': result['content'],
                'title': result['title']
            })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics using storage system."""
        storage_stats = self.storage.get_stats()
        
        # Convert orphaned files to relative paths
        orphaned_files = []
        for file_path, title in storage_stats['orphaned_file_list']:
            try:
                relative_path = str(Path(file_path).relative_to(self.root_path))
            except ValueError:
                relative_path = file_path
            orphaned_files.append(relative_path)
        
        # Convert storage stats to legacy format
        return {
            'total_notes': storage_stats['total_files'],
            'total_links': storage_stats['total_wikilinks'],
            'broken_links': storage_stats['broken_links'],
            'broken_link_details': [{'file': target, 'target': target, 'line': 0} for target in storage_stats['broken_targets']],
            'orphaned_notes': storage_stats['orphaned_files'],
            'orphaned_files': orphaned_files,
            'avg_links_per_note': storage_stats['avg_links_per_file']
        }
    
    def get_note_links(self, note_name: str) -> Optional[Dict]:
        """Get all links to and from a specific note."""
        if not self.notes:
            self.index()
        
        normalized_name = self._normalize_title(note_name)
        
        if normalized_name not in self.notes:
            return None
        
        target_note = self.notes[normalized_name]
        
        # Get outgoing links
        outgoing = []
        for link in target_note.links:
            target_exists = self._normalize_title(link.target) in self.notes
            outgoing.append({
                'target': link.target,
                'exists': target_exists,
                'line': link.line_number,
                'context': link.context
            })
        
        # Get incoming links
        incoming = []
        target_names = [
            self._normalize_title(target_note.title),
            self._normalize_title(target_note.path.stem)
        ]
        
        unique_notes = {}
        for note in self.notes.values():
            unique_notes[str(note.path)] = note
        
        for note in unique_notes.values():
            if note.path == target_note.path:
                continue
            
            for link in note.links:
                if self._normalize_title(link.target) in target_names:
                    incoming.append(str(note.path.relative_to(self.root_path)))
                    break
        
        return {
            'outgoing': outgoing,
            'incoming': list(set(incoming))  # Remove duplicates
        }
    
    def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Perform semantic search across the knowledge base."""
        return self.storage.semantic_search(query, top_k, similarity_threshold)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""
        return self.storage.get_embedding_stats()
    
    def set_progress_callback(self, callback):
        """Set progress callback for operations."""
        self.storage.set_progress_callback(callback)
    
    def reindex_embeddings(self, force_refresh: bool = False, progress_callback=None) -> int:
        """Reindex all embeddings."""
        return self.storage.reindex_embeddings(force_refresh, progress_callback)
    
    def list_files_with_concepts(self) -> List[Dict[str, Any]]:
        """List all files with their extracted concepts."""
        return self.storage.get_all_files_with_concepts()
    
    def get_concept_stats(self) -> Dict[str, Any]:
        """Get statistics about extracted concepts."""
        return self.storage.get_concept_stats()