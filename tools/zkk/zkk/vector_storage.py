import sqlite3
import json
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import pickle
import ast
import os
import time
import logging
import warnings
from contextlib import redirect_stdout, redirect_stderr
import io


@dataclass
class TextChunk:
    id: int
    file_id: int
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    embedding_checksum: str
    created_at: str


@dataclass
class SemanticMatch:
    chunk: TextChunk
    similarity_score: float
    file_path: str
    file_title: str


class TextChunker:
    """Intelligent text chunking for markdown documents."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.heading_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
        self.sentence_pattern = re.compile(r'[.!?]+\s+')
    
    def chunk_document(self, content: str, file_id: int) -> List[Dict[str, Any]]:
        """Chunk document intelligently based on structure."""
        chunks = []
        
        # First, try to chunk by markdown sections
        section_chunks = self._chunk_by_sections(content)
        
        if not section_chunks:
            # Fallback to sentence-aware chunking
            section_chunks = self._chunk_by_sentences(content)
        
        for i, (chunk_content, start_char, end_char) in enumerate(section_chunks):
            if chunk_content.strip():  # Skip empty chunks
                chunks.append({
                    'file_id': file_id,
                    'chunk_index': i,
                    'content': chunk_content.strip(),
                    'start_char': start_char,
                    'end_char': end_char
                })
        
        return chunks
    
    def _chunk_by_sections(self, content: str) -> List[Tuple[str, int, int]]:
        """Chunk content by markdown sections with code block awareness."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_start = 0
        current_char_pos = 0
        in_code_block = False
        code_fence_pattern = re.compile(r'^```')
        
        for line in lines:
            line_with_newline = line + '\n'
            
            # Track code block boundaries
            if code_fence_pattern.match(line):
                in_code_block = not in_code_block
            
            # Only split on headings if we're not in a code block
            if not in_code_block and re.match(r'^#{1,6}\s+', line) and current_chunk:
                # Save current chunk
                chunk_content = '\n'.join(current_chunk)
                if len(chunk_content.strip()) > 0:
                    chunks.append((chunk_content, current_start, current_char_pos))
                
                # Start new chunk
                current_chunk = [line]
                current_start = current_char_pos
            else:
                current_chunk.append(line)
            
            current_char_pos += len(line_with_newline)
            
            # If chunk is getting too large, split it (but try to preserve code blocks)
            if len('\n'.join(current_chunk)) > self.chunk_size and not in_code_block:
                chunk_content = '\n'.join(current_chunk)
                chunks.append((chunk_content, current_start, current_char_pos))
                current_chunk = []
                current_start = current_char_pos
        
        # Add remaining content
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) > 0:
                chunks.append((chunk_content, current_start, current_char_pos))
        
        return chunks
    
    def _chunk_by_sentences(self, content: str) -> List[Tuple[str, int, int]]:
        """Chunk content by sentences with overlap."""
        chunks = []
        sentences = self.sentence_pattern.split(content)
        
        current_chunk = ""
        current_start = 0
        char_position = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Calculate positions
            sentence_start = content.find(sentence, char_position)
            sentence_end = sentence_start + len(sentence)
            
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append((current_chunk.strip(), current_start, char_position))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_start = max(0, char_position - self.overlap)
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                    current_start = sentence_start
            
            char_position = sentence_end
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append((current_chunk.strip(), current_start, char_position))
        
        return chunks


class VectorStorage:
    """Local vector storage system with semantic search capabilities."""
    
    def __init__(self, db_path: Optional[Path] = None, model_name: str = "BAAI/bge-en-icl", fallback_model: str = "all-MiniLM-L6-v2", progress_callback: Optional[Callable] = None):
        if db_path is None:
            from platformdirs import user_data_dir
            data_dir = Path(user_data_dir("zkk", "zkk"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "knowledge_base.db"
        
        self.db_path = db_path
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.model = None  # Lazy load
        self.chunker = TextChunker()
        self.progress_callback = progress_callback
        
        # Set environment variables early to suppress output
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        
        self._init_db()
    
    def _init_db(self):
        """Initialize vector storage database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS text_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    embedding_checksum TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES markdown_files (id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chunk_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    embedding_data BLOB NOT NULL,
                    dimension INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chunk_id) REFERENCES text_chunks (id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS embedding_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT UNIQUE NOT NULL,
                    dimension INTEGER NOT NULL,
                    total_embeddings INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON text_chunks(file_id);
                CREATE INDEX IF NOT EXISTS idx_chunks_checksum ON text_chunks(embedding_checksum);
                CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);
                CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model_name);
            """)
    
    def _suppress_transformers_output(self):
        """Suppress noisy output from transformers and related libraries."""
        # Suppress transformers logging
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("sentence_transformers").setLevel(logging.ERROR) 
        logging.getLogger("torch").setLevel(logging.ERROR)
        logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
        
        # Suppress specific warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        # Set environment variables to reduce output
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    
    def _load_model(self):
        """Lazy load the embedding model with fallback and progress tracking."""
        if self.model is None:
            self._suppress_transformers_output()
            
            try:
                if self.progress_callback:
                    self.progress_callback("model_loading", f"Preparing {self.model_name}", 10)
                
                start_time = time.time()
                
                # Create a download progress simulation
                import threading
                
                def simulate_download_progress():
                    if self.progress_callback:
                        # Simulate gradual progress for potential downloads
                        for i in range(30, 90, 5):
                            time.sleep(0.3)  # Small delay to show progress
                            self.progress_callback("model_loading", f"Loading model files", i)
                
                # Start progress simulation in background
                progress_thread = threading.Thread(target=simulate_download_progress, daemon=True)
                progress_thread.start()
                
                if self.progress_callback:
                    self.progress_callback("model_loading", f"Initializing {self.model_name}", 20)
                
                # Capture stdout/stderr to prevent interference with progress bars
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    self.model = SentenceTransformer(self.model_name)
                
                # Stop the simulation thread
                progress_thread.join(timeout=0.1)
                
                load_time = time.time() - start_time
                
                if self.progress_callback:
                    self.progress_callback("model_loaded", f"Loaded {self.model_name} ({load_time:.1f}s)", 100)
                    
            except Exception as e:
                if self.progress_callback:
                    self.progress_callback("model_fallback", f"Using fallback: {self.fallback_model}", 0)
                
                start_time = time.time()
                
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    self.model = SentenceTransformer(self.fallback_model)
                    
                self.model_name = self.fallback_model
                load_time = time.time() - start_time
                
                if self.progress_callback:
                    self.progress_callback("model_loaded", f"Loaded {self.fallback_model} ({load_time:.1f}s)", 100)
                    
            self._update_metadata()
    
    def _update_metadata(self):
        """Update embedding metadata."""
        if self.model is None:
            return
        
        dimension = self.model.get_sentence_embedding_dimension()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO embedding_metadata (model_name, dimension, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (self.model_name, dimension))
    
    def _calculate_content_checksum(self, content: str) -> str:
        """Calculate checksum for content to detect changes."""
        return hashlib.md5(f"{content}{self.model_name}".encode('utf-8')).hexdigest()
    
    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize numpy embedding to bytes."""
        return pickle.dumps(embedding.astype(np.float32))
    
    def _deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserialize bytes to numpy embedding."""
        return pickle.loads(data)
    
    def _detect_content_type(self, content: str, file_path: str = "") -> str:
        """Detect if content is primarily code or text."""
        # Check file extension
        if file_path:
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go', '.rb', '.php'}
            if any(file_path.endswith(ext) for ext in code_extensions):
                return 'code'
        
        # Check content patterns
        lines = content.split('\n')
        code_indicators = 0
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines == 0:
            return 'text'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Code indicators
            if (line.startswith(('def ', 'class ', 'import ', 'from ', 'function ', 'const ', 'let ', 'var ')) or
                '{' in line or '}' in line or line.endswith(';') or line.startswith('#include') or
                re.match(r'^\s*(if|for|while|try|catch)\s*\(', line)):
                code_indicators += 1
        
        # If more than 30% of lines look like code, treat as code
        if code_indicators / total_lines > 0.3:
            return 'code'
        
        # Check for code blocks in markdown
        if '```' in content:
            code_blocks = content.count('```') // 2
            if code_blocks > 2:  # Multiple code blocks suggest code-heavy content
                return 'mixed'
        
        return 'text'
    
    def _extract_ast_features(self, code_content: str) -> List[str]:
        """Extract AST features from Python code for enhanced embeddings."""
        features = []
        try:
            tree = ast.parse(code_content)
            
            # Extract function and class names
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    features.append(f"function:{node.name}")
                elif isinstance(node, ast.ClassDef):
                    features.append(f"class:{node.name}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        features.append(f"import:{alias.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    features.append(f"from:{node.module}")
        except SyntaxError:
            # Not valid Python code
            pass
        except Exception:
            # Other parsing errors
            pass
        
        return features
    
    def _enhance_content_for_embedding(self, content: str, content_type: str, file_path: str = "") -> str:
        """Enhance content with metadata for better embeddings."""
        enhanced_content = content
        
        if content_type == 'code':
            # Add AST features for Python files
            if file_path.endswith('.py'):
                ast_features = self._extract_ast_features(content)
                if ast_features:
                    enhanced_content = content + "\n\n" + " ".join(ast_features)
            
            # Add file type context
            file_ext = os.path.splitext(file_path)[1] if file_path else ""
            if file_ext:
                enhanced_content = f"File type: {file_ext}\n\n" + enhanced_content
        
        elif content_type == 'mixed':
            # For markdown with code blocks, add context
            enhanced_content = "Documentation with code examples:\n\n" + content
        
        return enhanced_content
    
    def store_document_embeddings(self, file_id: int, content: str, force_refresh: bool = False, file_path: str = "", progress_callback: Optional[Callable] = None) -> int:
        """Store embeddings for a document's chunks."""
        self._load_model()
        
        # Use provided callback or instance callback
        callback = progress_callback or self.progress_callback
        
        # Detect content type and enhance for better embeddings
        content_type = self._detect_content_type(content, file_path)
        enhanced_content = self._enhance_content_for_embedding(content, content_type, file_path)
        
        # Generate chunks from enhanced content
        chunks = self.chunker.chunk_document(enhanced_content, file_id)
        stored_count = 0
        total_chunks = len(chunks)
        
        with sqlite3.connect(self.db_path) as conn:
            # Remove existing chunks and embeddings for this file if refreshing
            if force_refresh:
                conn.execute("""
                    DELETE FROM text_chunks WHERE file_id = ?
                """, (file_id,))
            
            for chunk_idx, chunk_data in enumerate(chunks):
                if callback:
                    progress = (chunk_idx / total_chunks) * 100 if total_chunks > 0 else 0
                    callback("embedding_progress", f"Processing chunk {chunk_idx + 1}/{total_chunks}", progress)
                
                content_checksum = self._calculate_content_checksum(chunk_data['content'])
                
                # Check if chunk already exists with same content
                cursor = conn.execute("""
                    SELECT id FROM text_chunks 
                    WHERE file_id = ? AND chunk_index = ? AND embedding_checksum = ?
                """, (file_id, chunk_data['chunk_index'], content_checksum))
                
                existing_chunk = cursor.fetchone()
                
                if existing_chunk and not force_refresh:
                    continue  # Skip if already processed
                
                # Delete existing chunk if it exists (content changed)
                if existing_chunk:
                    conn.execute("DELETE FROM text_chunks WHERE id = ?", (existing_chunk[0],))
                
                # Insert new chunk
                cursor = conn.execute("""
                    INSERT INTO text_chunks (file_id, chunk_index, content, start_char, end_char, embedding_checksum)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chunk_data['file_id'],
                    chunk_data['chunk_index'],
                    chunk_data['content'],
                    chunk_data['start_char'],
                    chunk_data['end_char'],
                    content_checksum
                ))
                
                chunk_id = cursor.lastrowid
                
                # Generate and store embedding with content-aware processing
                try:
                    chunk_content = chunk_data['content']
                    
                    # For code content, add instruction for better encoding
                    if content_type == 'code':
                        embedding_text = f"Code snippet: {chunk_content}"
                    elif content_type == 'mixed':
                        embedding_text = f"Technical documentation: {chunk_content}"
                    else:
                        embedding_text = chunk_content
                    
                    embedding = self.model.encode(embedding_text)
                    embedding_blob = self._serialize_embedding(embedding)
                    
                    conn.execute("""
                        INSERT INTO embeddings (chunk_id, model_name, embedding_data, dimension)
                        VALUES (?, ?, ?, ?)
                    """, (chunk_id, self.model_name, embedding_blob, len(embedding)))
                    
                    stored_count += 1
                    
                except Exception as e:
                    if callback:
                        callback("embedding_error", f"Error generating embedding for chunk {chunk_id}: {e}", None)
                    conn.execute("DELETE FROM text_chunks WHERE id = ?", (chunk_id,))
            
            # Update metadata
            conn.execute("""
                UPDATE embedding_metadata 
                SET total_embeddings = (
                    SELECT COUNT(*) FROM embeddings WHERE model_name = ?
                ), last_updated = CURRENT_TIMESTAMP
                WHERE model_name = ?
            """, (self.model_name, self.model_name))
        
        if callback and total_chunks > 0:
            callback("embedding_complete", f"Generated {stored_count} embeddings", 100)
        
        return stored_count
    
    def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.1) -> List[SemanticMatch]:
        """Perform semantic search across all stored embeddings."""
        self._load_model()
        
        # Generate query embedding
        query_embedding = self.model.encode(query)
        
        matches = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get all embeddings with associated data
            cursor = conn.execute("""
                SELECT 
                    tc.id as chunk_id,
                    tc.file_id,
                    tc.chunk_index,
                    tc.content,
                    tc.start_char,
                    tc.end_char,
                    tc.embedding_checksum,
                    tc.created_at,
                    e.embedding_data,
                    mf.path as file_path,
                    mf.title as file_title
                FROM text_chunks tc
                JOIN embeddings e ON tc.id = e.chunk_id
                JOIN markdown_files mf ON tc.file_id = mf.id
                WHERE e.model_name = ?
                ORDER BY tc.file_id, tc.chunk_index
            """, (self.model_name,))
            
            for row in cursor.fetchall():
                try:
                    # Deserialize embedding
                    stored_embedding = self._deserialize_embedding(row['embedding_data'])
                    
                    # Calculate similarity
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        stored_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity >= similarity_threshold:
                        chunk = TextChunk(
                            id=row['chunk_id'],
                            file_id=row['file_id'],
                            chunk_index=row['chunk_index'],
                            content=row['content'],
                            start_char=row['start_char'],
                            end_char=row['end_char'],
                            embedding_checksum=row['embedding_checksum'],
                            created_at=row['created_at']
                        )
                        
                        match = SemanticMatch(
                            chunk=chunk,
                            similarity_score=float(similarity),
                            file_path=row['file_path'],
                            file_title=row['file_title']
                        )
                        
                        matches.append(match)
                        
                except Exception as e:
                    print(f"Error processing embedding for chunk {row['chunk_id']}: {e}")
                    continue
        
        # Sort by similarity score (descending) and return top_k
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:top_k]
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total chunks and embeddings
            cursor = conn.execute("SELECT COUNT(*) FROM text_chunks")
            stats['total_chunks'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM embeddings WHERE model_name = ?", (self.model_name,))
            stats['total_embeddings'] = cursor.fetchone()[0]
            
            # Files with embeddings
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT file_id) FROM text_chunks
            """)
            stats['files_with_embeddings'] = cursor.fetchone()[0]
            
            # Model metadata
            cursor = conn.execute("""
                SELECT dimension, last_updated FROM embedding_metadata 
                WHERE model_name = ?
            """, (self.model_name,))
            
            metadata = cursor.fetchone()
            if metadata:
                stats['embedding_dimension'] = metadata[0]
                stats['last_updated'] = metadata[1]
            else:
                stats['embedding_dimension'] = 0
                stats['last_updated'] = None
            
            stats['model_name'] = self.model_name
            
            return stats
    
    def remove_file_embeddings(self, file_id: int) -> int:
        """Remove all embeddings for a specific file."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM text_chunks WHERE file_id = ?", (file_id,))
            count = cursor.fetchone()[0]
            
            conn.execute("DELETE FROM text_chunks WHERE file_id = ?", (file_id,))
            
            # Update metadata
            conn.execute("""
                UPDATE embedding_metadata 
                SET total_embeddings = (
                    SELECT COUNT(*) FROM embeddings WHERE model_name = ?
                ), last_updated = CURRENT_TIMESTAMP
                WHERE model_name = ?
            """, (self.model_name, self.model_name))
            
            return count
    
    def reindex_all_embeddings(self, markdown_files: List[Tuple[int, str]], progress_callback: Optional[Callable] = None) -> int:
        """Reindex all embeddings for given markdown files."""
        total_stored = 0
        total_files = len(markdown_files)
        callback = progress_callback or self.progress_callback
        
        # Calculate total chunks for accurate progress
        total_chunks = 0
        chunks_per_file = []
        
        if callback:
            callback("embedding_preparation", "Analyzing files for embedding generation", 10)
        
        for file_id, content in markdown_files:
            content_type = self._detect_content_type(content, "")
            enhanced_content = self._enhance_content_for_embedding(content, content_type, "")
            chunks = self.chunker.chunk_document(enhanced_content, file_id)
            chunks_per_file.append(len(chunks))
            total_chunks += len(chunks)
        
        if callback:
            callback("embedding_start", f"Processing {total_chunks} text chunks from {total_files} files", 20)
        
        processed_chunks = 0
        
        for file_idx, (file_id, content) in enumerate(markdown_files):
            if callback:
                file_progress = (file_idx / total_files) * 100 if total_files > 0 else 0
                callback("reindex_file_progress", f"Processing file {file_idx + 1}/{total_files}", file_progress)
            
            # Custom callback for this file that updates total progress
            def file_progress_callback(phase, message, progress_val):
                nonlocal processed_chunks
                if phase == "embedding_progress":
                    # Update total progress based on chunks processed
                    chunk_index = int(message.split('/')[0].split()[-1]) - 1 if '/' in message else 0
                    current_total_chunks = processed_chunks + chunk_index
                    total_progress = (current_total_chunks / total_chunks) * 100 if total_chunks > 0 else 0
                    if callback:
                        callback("embedding_total_progress", f"Embedding chunk {current_total_chunks + 1}/{total_chunks}", total_progress)
                elif phase == "embedding_complete":
                    processed_chunks += chunks_per_file[file_idx]
            
            stored_count = self.store_document_embeddings(
                file_id, content, force_refresh=True, 
                progress_callback=file_progress_callback
            )
            total_stored += stored_count
        
        if callback:
            callback("reindex_complete", f"Generated {total_stored} embeddings from {total_chunks} chunks", 100)
        
        return total_stored