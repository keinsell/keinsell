# zkk - Zettelkasten Knowledge base manager

A CLI tool for indexing and managing zettelkasten/wikilinks-based knowledge bases stored in markdown files.

## Features

- **Index**: Scan and index markdown files with wikilinks
- **Search**: Full-text search across your knowledge base
- **Stats**: Analyze your knowledge graph (orphaned notes, broken links, etc.)
- **Links**: Show incoming and outgoing links for specific notes

## Installation

```bash
pip install -e .
```

## Usage

### Index your knowledge base
```bash
zkk index                          # Index with caching
zkk index --refresh                # Force refresh, ignore cache
zkk index --path /path/to/notes    # Index specific directory
```

### Search for content
```bash
zkk search "machine learning"
zkk search "algorithm" --path /path/to/notes
```

### View knowledge base statistics
```bash
zkk stats
```

### Show links for a specific note
```bash
zkk links "Note Title"
zkk links filename
```

## Wikilink Format

zkk supports standard wikilink syntax:
- `[[Note Title]]` - Links to a note by title
- `[[Note Title|Display Text]]` - Links with custom display text
- Note matching is case-insensitive and works with both filenames and H1 titles

## Commands

- `zkk index` - Index markdown files with intelligent caching
- `zkk index --refresh` - Force refresh index, ignore cache
- `zkk search QUERY` - Search for content across indexed notes
- `zkk stats` - Show knowledge base statistics and analysis
- `zkk links NOTE_NAME` - Show all links to/from a specific note

## Caching

zkk uses XDG-compliant caching to speed up indexing:
- Cache location: `~/.cache/zkk/` (or platform equivalent)
- Automatic invalidation based on file modification times
- Use `--refresh` flag to force cache rebuild

All commands support `--path` to specify a different directory and `--verbose` for detailed output.

## Requirements and Product Specification

See: [[research]]]
