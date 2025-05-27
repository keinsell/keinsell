#!/usr/bin/env python3
"""
Grimoire - A CLI tool for managing markdown knowledge bases.
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING
import click
import yaml
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.progress import track
from sentence_transformers import SentenceTransformer
import faiss

console = Console()


class KnowledgeBase:
    """Manages markdown files in the knowledge base."""

    def __init__(self, directory: Path = Path.cwd()):
        self.directory = directory
        self.index_dir = self.directory / ".grimoire"
        self.index_file = self.index_dir / "index.ann"
        self.metadata_file = self.index_dir / "metadata.pkl"
        self.config_file = self.index_dir / "config.json"
        self.model = None
        self.index = None
        self.metadata = None

    def list_files(self, pattern: str = "*.md") -> List[Path]:
        """List all markdown files in the knowledge base."""
        # Use explicit list() to avoid conflict with Click command
        import builtins
        
        # Directories to exclude
        exclude_dirs = {'.venv', 'venv', '.git', '__pycache__', 'node_modules', '.tox', '.mypy_cache'}
        
        files = []
        for file_path in self.directory.rglob(pattern):
            # Check if any parent directory is in the exclude list
            if not any(part in exclude_dirs for part in file_path.parts):
                files.append(file_path)
        
        return files

    def read_file(self, filepath: Path) -> dict:
        """Read a markdown file and parse frontmatter."""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        content = filepath.read_text()
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                except yaml.YAMLError:
                    pass
                body = parts[2].strip()

        return {
            'path': filepath,
            'frontmatter': frontmatter or {},
            'body': body,
            'title': frontmatter.get('title', filepath.stem)
        }

    def create_file(self, filename: str, title: str, content: str = "", tags: Optional[List[str]] = None) -> Path:
        """Create a new markdown file with frontmatter."""
        filepath = self.directory / filename
        if not filename.endswith('.md'):
            filepath = self.directory / f"{filename}.md"

        if filepath.exists():
            raise FileExistsError(f"File already exists: {filepath}")

        frontmatter = {
            'title': title,
            'created': datetime.now().isoformat(),
            'tags': tags or []
        }

        file_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n{content}"
        filepath.write_text(file_content)

        return filepath

    def update_file(self, filepath: Path, content: Optional[str] = None,
                   frontmatter_updates: Optional[dict] = None) -> None:
        """Update an existing markdown file."""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        file_data = self.read_file(filepath)

        if frontmatter_updates:
            file_data['frontmatter'].update(frontmatter_updates)
            file_data['frontmatter']['modified'] = datetime.now().isoformat()

        if content is not None:
            file_data['body'] = content

        new_content = f"---\n{yaml.dump(file_data['frontmatter'], default_flow_style=False)}---\n\n{file_data['body']}"
        filepath.write_text(new_content)

    def delete_file(self, filepath: Path) -> None:
        """Delete a markdown file."""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        filepath.unlink()

    def search_files(self, query: str) -> List[dict]:
        """Search for files containing the query in title or content."""
        results = []
        query_lower = query.lower()

        for filepath in self.list_files():
            try:
                file_data = self.read_file(filepath)
                if (query_lower in file_data['title'].lower() or
                    query_lower in file_data['body'].lower()):
                    results.append(file_data)
            except Exception:
                continue

        return results

    def load_embedding_model(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """Load the sentence transformer model for embeddings."""
        console.print(f"[cyan]Loading embedding model: {model_name}[/cyan]")
        self.model = SentenceTransformer(model_name)
        return self.model

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts."""
        if not self.model:
            self.load_embedding_model()
        assert self.model is not None  # Type guard for pyright
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    def build_index(self, model_name: str = "BAAI/bge-large-en-v1.5") -> None:
        """Build or rebuild the vector index for all markdown files."""
        # Import ML dependencies only when needed
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
        except ImportError as e:
            console.print("[red]Error: ML dependencies not available.[/red]")
            console.print("[yellow]This feature requires sentence-transformers and torch.[/yellow]")
            console.print("[yellow]Note: PyTorch doesn't fully support Python 3.13 yet.[/yellow]")
            raise click.ClickException("ML dependencies not available") from e

        # Create index directory if it doesn't exist
        self.index_dir.mkdir(exist_ok=True)

        # Load model
        self.load_embedding_model(model_name)

        # Collect all documents
        try:
            files = self.list_files()
        except Exception as e:
            console.print(f"[red]Error listing files: {e}[/red]")
            console.print(f"[red]Type of error: {type(e)}[/red]")
            import traceback
            traceback.print_exc()
            raise
        if not files:
            console.print("[yellow]No markdown files found to index.[/yellow]")
            return

        console.print(f"[green]Found {len(files)} files to index[/green]")

        documents = []
        metadata = []

        for filepath in track(files, description="Reading files..."):
            try:
                file_data = self.read_file(filepath)
                # Combine title and body for embedding
                full_text = f"{file_data['title']}\n\n{file_data['body']}"
                documents.append(full_text)
                metadata.append({
                    'path': str(filepath),
                    'title': file_data['title'],
                    'frontmatter': file_data['frontmatter']
                })
            except Exception as e:
                console.print(f"[red]Error reading {filepath}: {e}[/red]")

        if not documents:
            console.print("[red]No documents could be read for indexing.[/red]")
            return

        # Create embeddings
        console.print("[cyan]Creating embeddings...[/cyan]")
        embeddings = self.create_embeddings(documents)

        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add all embeddings to index
        console.print("[cyan]Adding embeddings to index...[/cyan]")
        index.add(embeddings)

        # Save index
        faiss.write_index(index, str(self.index_file))
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(metadata, f)

        # Save config
        config = {
            'model_name': model_name,
            'dimension': dimension,
            'num_documents': len(documents),
            'created_at': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        console.print(f"[green]Index built successfully with {len(documents)} documents![/green]")

    def load_index(self) -> bool:
        """Load the existing index from disk."""
        if not all(f.exists() for f in [self.index_file, self.metadata_file, self.config_file]):
            return False

        try:
            # Load config
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Load model
            if not self.model:
                self.load_embedding_model(config['model_name'])

            # Load index
            import faiss
            self.index = faiss.read_index(str(self.index_file))

            # Load metadata
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)

            return True
        except Exception as e:
            console.print(f"[red]Error loading index: {e}[/red]")
            return False

    def vector_search(self, query: str, k: int = 5) -> List[Tuple[dict, float]]:
        """Search using vector similarity."""
        # Import ML dependencies only when needed
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
        except ImportError as e:
            console.print("[red]Error: ML dependencies not available.[/red]")
            console.print("[yellow]This feature requires sentence-transformers and torch.[/yellow]")
            console.print("[yellow]Note: PyTorch doesn't fully support Python 3.13 yet.[/yellow]")
            raise click.ClickException("ML dependencies not available") from e
        if not self.load_index():
            raise ValueError("No index found. Please run 'grimoire index' first.")

        # Type guards for pyright
        assert self.index is not None
        assert self.metadata is not None

        # Create query embedding
        query_embedding = self.create_embeddings([query])
        
        # Normalize query embedding for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search using FAISS
        # search returns (distances, indices)
        distances, indices = self.index.search(query_embedding, k)
        
        # FAISS returns results as 2D arrays, get first row
        distances = distances[0]
        indices = indices[0]

        results = []
        for idx, distance in zip(indices, distances):
            if idx >= 0 and idx < len(self.metadata):  # FAISS uses -1 for no match
                metadata = self.metadata[idx]
                file_data = self.read_file(Path(metadata['path']))
                # For normalized vectors with IndexFlatIP, distance is cosine similarity
                similarity = float(distance)
                results.append((file_data, similarity))

        return results


@click.group()
@click.option('--directory', '-d', type=click.Path(exists=True),
              default='.', help='Knowledge base directory')
@click.pass_context
def cli(ctx, directory):
    """Grimoire - Manage your markdown knowledge base."""
    ctx.ensure_object(dict)
    ctx.obj['kb'] = KnowledgeBase(Path(directory))


@cli.command()
@click.option('--sort', type=click.Choice(['name', 'date']), default='name')
@click.pass_context
def list(ctx, sort):
    """List all markdown files in the knowledge base."""
    kb = ctx.obj['kb']
    files = kb.list_files()

    if not files:
        console.print("[yellow]No markdown files found in the knowledge base.[/yellow]")
        return

    table = Table(title="Knowledge Base Files")
    table.add_column("File", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Tags", style="yellow")
    table.add_column("Created", style="blue")

    file_data_list = []
    for filepath in files:
        try:
            data = kb.read_file(filepath)
            file_data_list.append(data)
        except Exception as e:
            console.print(f"[red]Error reading {filepath}: {e}[/red]")

    if sort == 'date':
        file_data_list.sort(key=lambda x: x['frontmatter'].get('created', ''), reverse=True)
    else:
        file_data_list.sort(key=lambda x: x['path'].name)

    for data in file_data_list:
        table.add_row(
            str(data['path'].relative_to(kb.directory)),
            data['title'],
            ', '.join(data['frontmatter'].get('tags', [])),
            data['frontmatter'].get('created', 'N/A')[:10]
        )

    console.print(table)


@cli.command()
@click.argument('filename')
@click.option('--raw', is_flag=True, help='Show raw markdown without rendering')
@click.pass_context
def read(ctx, filename, raw):
    """Read and display a markdown file."""
    kb = ctx.obj['kb']

    # Find the file
    matching_files = [f for f in kb.list_files() if filename in str(f)]

    if not matching_files:
        console.print(f"[red]No file found matching: {filename}[/red]")
        return

    if len(matching_files) > 1:
        console.print(f"[yellow]Multiple files found matching '{filename}':[/yellow]")
        for i, f in enumerate(matching_files):
            console.print(f"{i+1}. {f.relative_to(kb.directory)}")

        choice = Prompt.ask("Select file number", default="1")
        try:
            filepath = matching_files[int(choice) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            return
    else:
        filepath = matching_files[0]

    try:
        data = kb.read_file(filepath)

        # Display frontmatter
        if data['frontmatter']:
            console.print("[bold cyan]Frontmatter:[/bold cyan]")
            console.print(yaml.dump(data['frontmatter'], default_flow_style=False))
            console.print()

        # Display content
        if raw:
            console.print(data['body'])
        else:
            console.print(Markdown(data['body']))

    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")


@cli.command()
@click.option('--title', '-t', prompt=True, help='Title of the note')
@click.option('--tags', '-g', multiple=True, help='Tags for the note')
@click.option('--content', '-c', help='Initial content')
@click.pass_context
def create(ctx, title, tags, content):
    """Create a new markdown file."""
    kb = ctx.obj['kb']

    # Generate filename from title
    filename = title.lower().replace(' ', '-')
    filename = ''.join(c for c in filename if c.isalnum() or c == '-')

    if not content:
        content = Prompt.ask("Enter initial content (optional)", default="")

    try:
        filepath = kb.create_file(filename, title, content, list(tags))
        console.print(f"[green]Created: {filepath.relative_to(kb.directory)}[/green]")

    except FileExistsError:
        console.print(f"[red]File already exists: {filename}.md[/red]")
        if Confirm.ask("Would you like to create with a different name?"):
            new_filename = Prompt.ask("Enter new filename")
            filepath = kb.create_file(new_filename, title, content, list(tags))
            console.print(f"[green]Created: {filepath.relative_to(kb.directory)}[/green]")

    except Exception as e:
        console.print(f"[red]Error creating file: {e}[/red]")


@cli.command()
@click.argument('filename')
@click.option('--content', '-c', help='New content')
@click.option('--title', '-t', help='Update title')
@click.option('--add-tag', '-a', multiple=True, help='Add tags')
@click.option('--remove-tag', '-r', multiple=True, help='Remove tags')
@click.option('--editor', '-e', is_flag=True, help='Open in default editor')
@click.pass_context
def update(ctx, filename, content, title, add_tag, remove_tag, editor):
    """Update an existing markdown file."""
    kb = ctx.obj['kb']

    # Find the file
    matching_files = [f for f in kb.list_files() if filename in str(f)]

    if not matching_files:
        console.print(f"[red]No file found matching: {filename}[/red]")
        return

    if len(matching_files) > 1:
        console.print(f"[yellow]Multiple files found matching '{filename}':[/yellow]")
        for i, f in enumerate(matching_files):
            console.print(f"{i+1}. {f.relative_to(kb.directory)}")

        choice = Prompt.ask("Select file number", default="1")
        try:
            filepath = matching_files[int(choice) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            return
    else:
        filepath = matching_files[0]

    try:
        file_data = kb.read_file(filepath)
        frontmatter_updates = {}

        if title:
            frontmatter_updates['title'] = title

        if add_tag or remove_tag:
            current_tags = set(file_data['frontmatter'].get('tags', []))
            current_tags.update(add_tag)
            current_tags.difference_update(remove_tag)
            frontmatter_updates['tags'] = list(current_tags)

        if editor:
            import tempfile
            import subprocess

            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
                tmp.write(file_data['body'])
                tmp_path = tmp.name

            editor_cmd = os.environ.get('EDITOR', 'nano')
            subprocess.call([editor_cmd, tmp_path])

            with open(tmp_path, 'r') as tmp:
                content = tmp.read()

            os.unlink(tmp_path)

        kb.update_file(filepath, content, frontmatter_updates)
        console.print(f"[green]Updated: {filepath.relative_to(kb.directory)}[/green]")

    except Exception as e:
        console.print(f"[red]Error updating file: {e}[/red]")


@cli.command()
@click.argument('filename')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete(ctx, filename, force):
    """Delete a markdown file."""
    kb = ctx.obj['kb']

    # Find the file
    matching_files = [f for f in kb.list_files() if filename in str(f)]

    if not matching_files:
        console.print(f"[red]No file found matching: {filename}[/red]")
        return

    if len(matching_files) > 1:
        console.print(f"[yellow]Multiple files found matching '{filename}':[/yellow]")
        for i, f in enumerate(matching_files):
            console.print(f"{i+1}. {f.relative_to(kb.directory)}")

        choice = Prompt.ask("Select file number", default="1")
        try:
            filepath = matching_files[int(choice) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            return
    else:
        filepath = matching_files[0]

    if not force:
        if not Confirm.ask(f"Delete {filepath.relative_to(kb.directory)}?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        kb.delete_file(filepath)
        console.print(f"[green]Deleted: {filepath.relative_to(kb.directory)}[/green]")

    except Exception as e:
        console.print(f"[red]Error deleting file: {e}[/red]")


@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search for files containing the query."""
    kb = ctx.obj['kb']

    results = kb.search_files(query)

    if not results:
        console.print(f"[yellow]No files found containing: {query}[/yellow]")
        return

    console.print(f"[green]Found {len(results)} files containing '{query}':[/green]\n")

    for data in results:
        console.print(f"[bold cyan]{data['path'].relative_to(kb.directory)}[/bold cyan]")
        console.print(f"Title: {data['title']}")

        # Show context
        body_lower = data['body'].lower()
        query_lower = query.lower()
        idx = body_lower.find(query_lower)

        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(data['body']), idx + len(query) + 50)
            context = data['body'][start:end].strip()

            if start > 0:
                context = "..." + context
            if end < len(data['body']):
                context = context + "..."

            console.print(f"Context: {context}")

        console.print()


@cli.command()
@click.option('--model', '-m', default='BAAI/bge-large-en-v1.5',
              help='Embedding model to use')
@click.option('--force', '-f', is_flag=True, help='Force rebuild index')
@click.pass_context
def index(ctx, model, force):
    """Build vector index for the knowledge base."""
    kb = ctx.obj['kb']

    if kb.index_file.exists() and not force:
        if not Confirm.ask("Index already exists. Rebuild?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        kb.build_index(model_name=model)
    except Exception as e:
        console.print(f"[red]Error building index: {e}[/red]")


@cli.command()
@click.argument('query')
@click.option('--limit', '-k', default=5, help='Number of results to return')
@click.option('--threshold', '-t', type=float, help='Minimum similarity score')
@click.pass_context
def vsearch(ctx, query, limit, threshold):
    """Vector search using embeddings similarity."""
    kb = ctx.obj['kb']

    try:
        results = kb.vector_search(query, k=limit)

        if not results:
            console.print(f"[yellow]No similar documents found for: {query}[/yellow]")
            return

        console.print(f"[green]Found {len(results)} similar documents:[/green]\n")

        for data, score in results:
            if threshold and score < threshold:
                continue

            console.print(f"[bold cyan]{data['path'].relative_to(kb.directory)}[/bold cyan]")
            console.print(f"Title: {data['title']}")
            console.print(f"Similarity: [yellow]{score:.3f}[/yellow]")

            # Show preview
            preview = data['body'][:200].strip()
            if len(data['body']) > 200:
                preview += "..."
            console.print(f"Preview: {preview}")
            console.print()

    except ValueError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]Error during search: {e}[/red]")


if __name__ == '__main__':
    cli()
