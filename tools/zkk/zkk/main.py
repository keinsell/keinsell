import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from .core import KnowledgeBase
import time

console = Console()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """zkk - Zettelkasten Knowledge base manager
    
    A CLI tool for indexing and managing zettelkasten/wikilinks-based knowledge bases.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

@cli.command()
@click.option('--path', '-p', default='.', help='Path to scan for markdown files')
@click.option('--refresh', '-r', is_flag=True, help='Force refresh index, ignore cache')
@click.option('--no-embeddings', is_flag=True, help='Skip generating embeddings (faster indexing)')
@click.pass_context
def index(ctx, path, refresh, no_embeddings):
    """Index markdown files and generate embeddings for semantic search."""
    
    # Progress tracking state
    progress_state = {
        'current_phase': 'starting',
        'current_task': '',
        'current_progress': 0,
        'model_loading': False,
        'model_loaded': False,
        'embedding_progress': 0,
        'total_files': 0,
        'current_file': 0
    }
    
    def progress_callback(phase, message, progress):
        """Callback to update progress state."""
        progress_state['current_phase'] = phase
        progress_state['current_task'] = message
        if progress is not None:
            progress_state['current_progress'] = progress
        
        if phase == 'model_loading':
            progress_state['model_loading'] = True
        elif phase == 'model_loaded':
            progress_state['model_loaded'] = True
            progress_state['model_loading'] = False
        elif phase == 'embedding_progress':
            progress_state['embedding_progress'] = progress
    
    # Start indexing files
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=30, style="white", complete_style="white", finished_style="white"),
        TaskProgressColumn(style="white"),
        console=console,
        transient=False
    ) as progress:
        
        # File indexing task
        file_task = progress.add_task("Scanning markdown files...", total=None)
        
        kb = KnowledgeBase(path)
        files_indexed = kb.index(force_refresh=refresh)
        
        progress.update(file_task, completed=files_indexed, total=files_indexed)
        progress.stop_task(file_task)
        
        if ctx.obj['verbose']:
            cache_status = "refreshed" if refresh else "from cache/scan"
            console.print(f"Indexed {files_indexed} files from {path} ({cache_status})")
        else:
            console.print(f"Indexed {files_indexed} files")
    
    # Generate embeddings by default unless explicitly disabled
    if not no_embeddings and files_indexed > 0:
        try:
            with Progress(
                TextColumn("{task.description}"),
                BarColumn(bar_width=30, style="white", complete_style="white", finished_style="white"),
                TaskProgressColumn(style="white"),
                console=console,
                transient=False
            ) as embedding_progress:
                
                # Model loading task
                model_task = embedding_progress.add_task("Preparing embedding model...", total=100)
                
                # Total embedding progress task
                total_embedding_task = embedding_progress.add_task("Generating embeddings...", total=100, visible=False)
                
                # Concept extraction task
                concept_task = embedding_progress.add_task("Extracting concepts...", total=100, visible=False)
                
                def enhanced_progress_callback(phase, message, progress_val):
                    """Enhanced callback for embedding progress."""
                    if phase == 'model_loading':
                        embedding_progress.update(model_task, description="Loading model", completed=progress_val or 0)
                    elif phase == 'model_loaded':
                        embedding_progress.update(model_task, completed=100, description="Model ready")
                        embedding_progress.stop_task(model_task)
                        embedding_progress.update(total_embedding_task, visible=True)
                    elif phase == 'model_fallback':
                        embedding_progress.update(model_task, description="Using fallback model", completed=50)
                    elif phase == 'embedding_preparation':
                        embedding_progress.update(total_embedding_task, description="Analyzing files", completed=progress_val or 0)
                    elif phase == 'embedding_start':
                        embedding_progress.update(total_embedding_task, description="Generating embeddings", completed=progress_val or 0)
                    elif phase == 'embedding_total_progress':
                        chunks_info = message.split()[-1] if message else ""
                        embedding_progress.update(total_embedding_task, completed=progress_val, description=f"Processing {chunks_info}")
                    elif phase == 'reindex_complete':
                        embedding_progress.update(total_embedding_task, completed=100, description="Embeddings complete")
                        embedding_progress.stop_task(total_embedding_task)
                        embedding_progress.update(concept_task, visible=True)
                    elif phase == 'concept_reindex_start':
                        embedding_progress.update(concept_task, description="Extracting concepts", completed=0)
                    elif phase == 'concept_reindex_progress':
                        file_info = message.split()[-1] if message else ""
                        embedding_progress.update(concept_task, completed=progress_val, description=f"Analyzing {file_info}")
                    elif phase == 'concept_reindex_complete':
                        embedding_progress.update(concept_task, completed=100, description="Concepts complete")
                        embedding_progress.stop_task(concept_task)
                    elif phase == 'embedding_error':
                        # Don't update progress on individual chunk errors
                        pass
                
                # Set up progress callback before starting
                kb.set_progress_callback(enhanced_progress_callback)
                
                # Start embedding generation
                embedding_count = kb.reindex_embeddings(force_refresh=refresh, progress_callback=enhanced_progress_callback)
                
                if ctx.obj['verbose']:
                    console.print(f"Generated embeddings for {embedding_count} text chunks")
                else:
                    console.print("Processing complete - semantic search and concept analysis ready")
                    
        except Exception as e:
            console.print(f"Warning: Failed to generate embeddings: {e}")
            console.print("You can still use basic text search")
    
    elif not no_embeddings:
        console.print("No files to index - skipping embedding generation")
    else:
        console.print("Skipped embedding generation (run 'zkk index --refresh' to enable semantic search)")

@cli.command()
@click.argument('query')
@click.option('--path', '-p', default='.', help='Path to search in')
@click.option('--text-only', '-t', is_flag=True, help='Use text search instead of semantic search')
@click.option('--top-k', '-k', default=10, help='Number of results to return')
@click.option('--threshold', default=0.1, help='Similarity threshold for semantic search (0.0-1.0)')
@click.pass_context
def search(ctx, query, path, text_only, top_k, threshold):
    """Search for content using semantic search (default) or text search."""
    kb = KnowledgeBase(path)
    
    # Try semantic search first unless text-only is specified
    if not text_only:
        try:
            results = kb.semantic_search(query, top_k, threshold)
            
            if results:
                table = Table(title=f"Semantic Search Results for '{query}' ({len(results)} matches)", show_header=True, header_style="bold")
                table.add_column("File", style="cyan", no_wrap=True, min_width=20)
                table.add_column("Score", style="green", justify="right", width=8)
                table.add_column("Match", style="white", min_width=40)
                
                for result in results:
                    # Show only filename, not full path
                    file_path = Path(result['file_path']).name
                    
                    similarity_str = f"{result['similarity_score']:.2f}"
                    content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    # Clean up the content preview
                    content_preview = content_preview.replace('\n', ' ').strip()
                    
                    table.add_row(file_path, similarity_str, content_preview)
                
                console.print(table)
                console.print(f"[dim]Use --text-only for exact text matching[/dim]")
                return
            else:
                console.print("[yellow]No semantic matches found, trying text search...[/yellow]")
        
        except Exception as e:
            if ctx.obj['verbose']:
                console.print(f"[yellow]Semantic search unavailable: {e}[/yellow]")
            console.print("[yellow]Falling back to text search...[/yellow]")
    
    # Fallback to text search
    results = kb.search(query)
    
    if not results:
        console.print("[yellow]No results found[/yellow]")
        if not text_only:
            console.print("[dim]Try running 'zkk index' to enable semantic search[/dim]")
        return
    
    table = Table(title=f"Text Search Results for '{query}' ({len(results)} matches)", show_header=True, header_style="bold")
    table.add_column("File", style="cyan", no_wrap=True, min_width=20)
    table.add_column("Match", style="white", min_width=40)
    
    for result in results:
        # Show only filename, not full path
        file_name = Path(result['file']).name if '/' in result['file'] else result['file']
        
        content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
        # Clean up the content preview
        content_preview = content_preview.replace('\n', ' ').strip()
        table.add_row(file_name, content_preview)
    
    console.print(table)


@cli.command()
@click.option('--path', '-p', default='.', help='Path to analyze')
@click.pass_context
def stats(ctx, path):
    """Show knowledge base statistics, links analysis, and embedding status."""
    kb = KnowledgeBase(path)
    stats = kb.get_stats()
    
    # Main statistics table
    table = Table(title="Knowledge Base Statistics", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan", min_width=20)
    table.add_column("Value", style="white", justify="right")
    
    table.add_row("Total Notes", str(stats['total_notes']))
    table.add_row("Total Links", str(stats['total_links']))
    table.add_row("Orphaned Notes", str(stats['orphaned_notes']))
    table.add_row("Broken Links", str(stats['broken_links']))
    table.add_row("Average Links per Note", f"{stats['avg_links_per_note']:.2f}")
    
    console.print(table)
    
    # Embedding statistics
    try:
        embedding_stats = kb.get_embedding_stats()
        
        if embedding_stats.get('enabled', False):
            console.print("\nSemantic Search Status")
            embedding_table = Table(show_header=True, header_style="bold")
            embedding_table.add_column("Metric", style="cyan", min_width=20)
            embedding_table.add_column("Value", style="white", justify="right")
            
            embedding_table.add_row("Model", embedding_stats.get('model_name', 'Unknown'))
            embedding_table.add_row("Embedding Dimension", str(embedding_stats.get('embedding_dimension', 0)))
            embedding_table.add_row("Total Chunks", str(embedding_stats.get('total_chunks', 0)))
            embedding_table.add_row("Total Embeddings", str(embedding_stats.get('total_embeddings', 0)))
            embedding_table.add_row("Files with Embeddings", str(embedding_stats.get('files_with_embeddings', 0)))
            
            if embedding_stats.get('last_updated'):
                embedding_table.add_row("Last Updated", embedding_stats['last_updated'])
            
            console.print(embedding_table)
            
            # Show readiness status
            if embedding_stats.get('total_embeddings', 0) > 0:
                console.print("[green]Semantic search is ready[/green]")
            else:
                console.print("[yellow]No embeddings found - run 'zkk index' to enable semantic search[/yellow]")
        else:
            console.print("\n[yellow]Semantic search is not available[/yellow]")
            console.print("[dim]Run 'zkk index' to enable semantic search capabilities[/dim]")
            
    except Exception as e:
        if ctx.obj['verbose']:
            console.print(f"\n[yellow]Could not retrieve embedding stats: {e}[/yellow]")
    
    # Show concept statistics
    try:
        concept_stats = kb.get_concept_stats()
        
        if concept_stats.get('total_concepts', 0) > 0:
            console.print("\nConcept Analysis")
            concept_table = Table(show_header=True, header_style="bold")
            concept_table.add_column("Metric", style="cyan", min_width=20)
            concept_table.add_column("Value", style="white", justify="right")
            
            concept_table.add_row("Total Concepts", str(concept_stats['total_concepts']))
            concept_table.add_row("Files with Concepts", str(concept_stats['files_with_concepts']))
            
            # Show concept types
            if concept_stats.get('concepts_by_type'):
                type_summary = ", ".join([f"{t}: {c}" for t, c in concept_stats['concepts_by_type'].items()])
                concept_table.add_row("By Type", type_summary)
            
            console.print(concept_table)
            
            # Show top concepts
            if concept_stats.get('top_concepts'):
                console.print("\nMost Common Concepts:")
                for i, concept in enumerate(concept_stats['top_concepts'][:5], 1):
                    console.print(f"  {i}. [bold]{concept['name']}[/bold] ({concept['type']}) - {concept['file_count']} files")
        else:
            console.print("\n[yellow]No concepts extracted yet[/yellow]")
            console.print("[dim]Run 'zkk index' to extract concepts from your documents[/dim]")
            
    except Exception as e:
        if ctx.obj.get('verbose'):
            console.print(f"\n[yellow]Could not load concept stats: {e}[/yellow]")
    
    # Show issues if any
    if stats['orphaned_files']:
        console.print("\n[yellow]Orphaned files:[/yellow]")
        for file in stats['orphaned_files']:
            console.print(f"  - {file}")
    
    if stats['broken_link_details']:
        console.print("\n[red]Broken links:[/red]")
        for link in stats['broken_link_details']:
            console.print(f"  - {link['file']}: [[{link['target']}]]")

@cli.command()
@click.argument('note_name')
@click.option('--path', '-p', default='.', help='Path to search in')
@click.pass_context
def links(ctx, note_name, path):
    """Show all links to and from a specific note."""
    kb = KnowledgeBase(path)
    link_info = kb.get_note_links(note_name)
    
    if not link_info:
        console.print(f"[yellow]Note '{note_name}' not found[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Links for: {note_name}[/bold cyan]")
    
    if link_info['outgoing']:
        console.print("\n[green]Outgoing links:[/green]")
        for link in link_info['outgoing']:
            status = "✓" if link['exists'] else "✗"
            console.print(f"  {status} [[{link['target']}]]")
    
    if link_info['incoming']:
        console.print("\n[blue]Incoming links:[/blue]")
        for source in link_info['incoming']:
            console.print(f"  ← {source}")

@cli.command()
@click.option('--path', '-p', default='.', help='Path to list files from')
@click.option('--no-concepts', is_flag=True, help='Hide extracted concepts (show only file names)')
@click.option('--concept-limit', default=3, help='Number of top concepts to show per file')
@click.pass_context
def list(ctx, path, no_concepts, concept_limit):
    """List all indexed files with their concepts and metadata."""
    kb = KnowledgeBase(path)
    
    try:
        files = kb.list_files_with_concepts()
        
        if not files:
            console.print("[yellow]No indexed files found[/yellow]")
            console.print("[dim]💡 Run 'zkk index' to index markdown files[/dim]")
            return
        
        # Create main table - show concepts by default
        show_concepts = not no_concepts
        table = Table(title=f"📚 Knowledge Base Files ({len(files)} files)")
        table.add_column("File", style="cyan", min_width=20)
        table.add_column("Concepts", style="blue", min_width=15)
        
        if show_concepts:
            table.add_column("Top Concepts", style="green", min_width=30)
        
        table.add_column("Created", style="dim", min_width=12)
        
        for file_data in files:
            # Show only filename, not full path
            file_name = Path(file_data['path']).name
            
            # Format concept count
            concept_count = file_data.get('concept_count', 0)
            concept_display = f"{concept_count} concepts" if concept_count > 0 else "No concepts"
            
            # Format creation date
            from datetime import datetime
            try:
                created_date = datetime.fromisoformat(file_data['created_at'].replace('Z', '+00:00'))
                created_str = created_date.strftime('%m/%d/%y')
            except:
                created_str = "-"
            
            if show_concepts:
                # Format top concepts
                concepts = file_data.get('concepts', [])[:concept_limit]
                if concepts:
                    concept_tags = []
                    for concept in concepts:
                        # Color code by type with minimal styling
                        if concept['concept_type'] == 'technical':
                            color = "blue"
                        elif concept['concept_type'] == 'topic':
                            color = "green"
                        elif concept['concept_type'] == 'entity':
                            color = "yellow"
                        else:
                            color = "white"
                        
                        # Simple confidence indicator
                        confidence = concept.get('relevance_score', 0)
                        if confidence > 0.7:
                            indicator = "*"
                        elif confidence > 0.5:
                            indicator = "+"
                        else:
                            indicator = "-"
                        
                        concept_tags.append(f"[{color}]{indicator}{concept['name']}[/{color}]")
                    
                    concepts_display = ", ".join(concept_tags)
                else:
                    concepts_display = "[dim]-[/dim]"
                
                table.add_row(
                    file_data['title'] or file_name,
                    concept_display, 
                    concepts_display,
                    created_str
                )
            else:
                table.add_row(
                    file_data['title'] or file_name,
                    concept_display,
                    created_str
                )
        
        console.print(table)
        
        # Show concept statistics if verbose
        if ctx.obj.get('verbose') or show_concepts:
            try:
                concept_stats = kb.get_concept_stats()
                
                if concept_stats.get('total_concepts', 0) > 0:
                    console.print(f"\nConcept Analysis Summary")
                    
                    stats_table = Table(show_header=True, header_style="bold")
                    stats_table.add_column("Metric", style="cyan", min_width=20)
                    stats_table.add_column("Value", style="white", justify="right")
                    
                    stats_table.add_row("Total Concepts", str(concept_stats['total_concepts']))
                    stats_table.add_row("Files with Concepts", str(concept_stats['files_with_concepts']))
                    
                    # Show concept types
                    if concept_stats.get('concepts_by_type'):
                        type_summary = ", ".join([f"{t}: {c}" for t, c in concept_stats['concepts_by_type'].items()])
                        stats_table.add_row("By Type", type_summary)
                    
                    console.print(stats_table)
                    
                    # Show top concepts
                    if concept_stats.get('top_concepts'):
                        console.print("\nMost Common Concepts:")
                        for i, concept in enumerate(concept_stats['top_concepts'][:5], 1):
                            console.print(f"  {i}. [bold]{concept['name']}[/bold] ({concept['type']}) - {concept['file_count']} files")
                            
            except Exception as e:
                if ctx.obj.get('verbose'):
                    console.print(f"[yellow]Could not load concept stats: {e}[/yellow]")
        
        # Helpful tips
        if no_concepts:
            console.print(f"\n[dim]Remove --no-concepts to see extracted concepts[/dim]")
        elif not any(file_data.get('concepts') for file_data in files):
            console.print(f"\n[dim]Run 'zkk index' to extract concepts from your documents[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing files: {e}[/red]")








if __name__ == "__main__":
    cli()