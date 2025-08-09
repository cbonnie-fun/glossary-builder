# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered Python CLI tool that uses Claude to intelligently extract and define technical terms from documentation, generating glossaries tailored to different expertise levels.

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

### Running the AI-Powered Tool
```bash
# Basic usage
python glossary_builder_ai.py docs/sample_documentation.md

# Specify expertise level
python glossary_builder_ai.py docs/sample_documentation.md --expertise-level senior

# Generate HTML output
python glossary_builder_ai.py docs/sample_documentation.md --format html --output glossary.html

# Display as terminal table
python glossary_builder_ai.py docs/sample_documentation.md --format table

# Estimate costs first
python glossary_builder_ai.py docs/sample_documentation.md --estimate-cost
```

### Running Original JSON-Based Tool
```bash
# Basic usage with predefined database
python glossary_builder.py docs/sample_documentation.md

# Display as terminal table
python glossary_builder.py docs/sample_documentation.md --format table
```

### Testing
```bash
# Test AI version with different formats
python glossary_builder_ai.py docs/sample_documentation.md --format markdown
python glossary_builder_ai.py docs/sample_documentation.md --format json --output test.json
python glossary_builder_ai.py docs/sample_documentation.md --format html --output test.html
python glossary_builder_ai.py docs/sample_documentation.md --format table

# Test with different expertise levels
python glossary_builder_ai.py docs/sample_documentation.md --expertise-level junior
python glossary_builder_ai.py docs/sample_documentation.md --expertise-level senior
```

## Architecture Notes

### AI-Powered Version (glossary_builder_ai.py)
- **Core**: Uses Anthropic Claude API for intelligent term extraction and definition
- **Models**: Claude 3 Haiku for extraction, Claude 3 Sonnet for definitions
- **Features**: Expertise level targeting, cost estimation, documentation links
- **Dependencies**: anthropic, click, rich, python-dotenv

### Original Version (glossary_builder.py)
- **Core**: JSON database-based term matching
- **Database**: glossary_db.json with 25+ predefined technical terms
- **Features**: Pattern matching, multiple output formats

### Shared Components
- **Output formats**: Markdown, HTML, JSON, plain text, and terminal table
- **CLI framework**: Click for command-line interface
- **UI**: Rich for terminal formatting and progress indicators

## Project-Specific Guidelines

### AI Version Guidelines
- API key required (ANTHROPIC_API_KEY environment variable)
- Processes documents in chunks for large files
- Limits to 8 most important terms per run
- Expertise levels: junior (default), mid, senior
- Documentation links automatically added when available

### Original Version Guidelines
- Terms matched case-insensitively using word boundaries
- JSON database must include "definition" field
- Optional fields: "category", "examples", "related"
- Supports .md, .txt, and .rst files by default

### Adding Features
- New output formats: implement `_generate_<format>` method
- New doc links: add to DOC_LINKS dictionary
- New expertise levels: extend EXPERTISE_LEVELS