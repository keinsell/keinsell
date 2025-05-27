# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Grimoire is a comprehensive command-line tool for managing markdown-based knowledge bases. It provides full CRUD operations for markdown files, YAML frontmatter management, full-text search, and AI-powered vector search capabilities using sentence embeddings.

## Development Commands

```bash
# Run the application
python main.py

# Install dependencies (requires Python 3.13+)
pip install -e .

# Run specific commands
python main.py list                  # List all markdown files
python main.py create -t "Title"     # Create new file
python main.py read filename         # Read a file
python main.py search "query"        # Text search
python main.py index                 # Build vector index
python main.py vsearch "query"       # Vector similarity search
```

## Architecture

### Core Components

1. **KnowledgeBase Class** (`main.py:27-249`)
   - Central class managing all markdown file operations
   - Handles file I/O, frontmatter parsing, and indexing
   - Methods:
     - `list_files()` - Find markdown files recursively
     - `read_file()` - Parse markdown with YAML frontmatter
     - `create_file()` - Create new markdown with frontmatter
     - `update_file()` - Update content and frontmatter
     - `delete_file()` - Remove markdown files
     - `search_files()` - Full-text search
     - `build_index()` - Create vector embeddings index
     - `vector_search()` - Semantic similarity search

2. **CLI Commands** (Using Click framework)
   - `list` - Display all files in table format
   - `read` - View file content (raw or rendered)
   - `create` - Interactive file creation
   - `update` - Modify files (content, tags, metadata)
   - `delete` - Remove files with confirmation
   - `search` - Text-based search with context
   - `index` - Build FAISS vector index
   - `vsearch` - Vector similarity search

3. **Data Storage**
   - Markdown files with YAML frontmatter
   - `.grimoire/` directory for indexes:
     - `index.faiss` - Vector embeddings index
     - `metadata.pkl` - File metadata cache
     - `config.json` - Index configuration

### Key Technologies

- **Click**: CLI framework for command parsing
- **Rich**: Terminal formatting (tables, markdown, progress bars)
- **PyYAML**: YAML frontmatter parsing
- **Sentence Transformers**: Text embeddings (BGE-large model)
- **FAISS**: Vector similarity search
- **NumPy**: Numerical operations

### File Format

Markdown files use YAML frontmatter:
```markdown
---
title: Document Title
created: 2024-01-01T10:00:00
modified: 2024-01-02T15:30:00
tags:
  - tag1
  - tag2
---

# Content goes here
```

## Module Structure

### Current Structure (Monolithic)
```
grimoire/
├── main.py           # All functionality in single file
├── pyproject.toml    # Project configuration
├── CLAUDE.md         # Project documentation
└── README.md         # User documentation
```

### Phase 1: Simple Module Structure (Start Here)
```
grimoire/
├── grimoire/
│   ├── __init__.py
│   ├── cli.py       # Click commands (extracted from main.py)
│   ├── db.py        # KnowledgeBase class and data operations
│   └── ui.py        # Console output and formatting helpers
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_db.py
│   └── test_ui.py
├── main.py          # Simple entry point: from grimoire.cli import cli; cli()
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

### Phase 2: As Complexity Grows
```
grimoire/
├── grimoire/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py    # Click command definitions
│   │   └── options.py     # Shared CLI options
│   ├── db/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py
│   │   ├── search.py      # Text and vector search
│   │   └── models.py      # Data structures
│   └── ui/
│       ├── __init__.py
│       ├── console.py     # Rich console instance
│       ├── formatters.py  # Table, markdown formatting
│       └── prompts.py     # Interactive prompts
├── tests/
│   └── (test structure mirrors source)
└── (config files)
```

## Development Workflow

### 1. Code Quality Tools

```bash
# Install development dependencies
pip install pyright ruff pytest pytest-cov

# Run type checking
pyright

# Run linter and formatter
ruff check --fix .
ruff format .

# Run tests
pytest
pytest --cov=grimoire --cov-report=html
```

### 2. pyproject.toml Configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]
ignore = ["E501"]  # Line length handled by formatter

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "strict"
```

### 3. Development Process

1. **Write code** - Start simple, iterate
2. **Run pyright** - Fix type errors
3. **Run ruff** - Fix linting issues and format
4. **Write tests** - Ensure functionality works
5. **Run tests** - Verify implementation
6. **Refactor** - Only when needed, keeping it simple

### Module Responsibilities

**Phase 1 Modules:**

1. **cli.py**: Command-line interface
   - All Click command definitions
   - Argument parsing and validation
   - Calls into db.py for operations

2. **db.py**: Database/storage operations
   - KnowledgeBase class
   - File I/O operations
   - Search functionality
   - Index management

3. **ui.py**: User interface helpers
   - Console instance (Rich)
   - Table formatting
   - Markdown rendering
   - Progress bars

### Testing Strategy

1. **Unit tests** for each module
2. **Integration tests** for CLI commands
3. **Fixtures** for sample markdown files
4. **Mock** external dependencies (embeddings)

## Key Implementation Notes

- Previously renamed from "zkk" to "grimoire"
- Full implementation complete with all core features
- Vector search requires building index first (`grimoire index`)
- Supports interactive file selection for ambiguous queries
- Editor integration via `$EDITOR` environment variable
- Cosine similarity search using inner product on normalized vectors
- Progress bars for long operations (indexing, embedding)

## Future Enhancements

- AI-powered automatic tagging (original goal, not yet implemented)
- Batch operations for multiple files
- Export/import functionality
- Graph visualization of document relationships
- Custom embedding models support
- Real-time index updates