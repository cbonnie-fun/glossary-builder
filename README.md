# Technical terms glossary builder

An intelligent Python CLI tool that uses Claude AI to automatically extract technical terms from documentation and generate contextual glossaries tailored to different expertise levels.

## Features

- **AI-powered extraction**: Uses Claude to intelligently identify technical terms that your target audience might not understand
- **Audience-aware**: Configurable expertise levels (junior, mid, senior developers)
- **Smart definitions**: Generates both general and context-specific definitions
- **Documentation links**: Automatically adds links to official documentation
- **Cost estimation**: Preview API costs before processing
- **Multiple output formats**: Markdown, HTML, JSON, plain text, or interactive tables
- **Efficient processing**: Handles large documents through intelligent chunking
- **Beautiful output**: Rich terminal UI with progress indicators

## How It Works

1. The tool reads and analyzes your technical documentation.
2. Claude AI analyzes the content and identifies terms that might be unfamiliar to your target audience.
3. For each term, Claude generates:
   - A clear, concise definition appropriate for the expertise level
   - Context-specific notes about how the term is used in your document
   - Links to official documentation when available
4. The tool automatically limits to 8 most important terms to maintain focus and readability.

## Install the glossary builder

1. Clone the repository:
```bash
git clone https://github.com/yourusername/glossary-builder.git
cd glossary-builder
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Anthropic API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

Get your API key from [Anthropic Console](https://console.anthropic.com/)

## Example input

### Basic Usage

Extract and define technical terms from a document:
```bash
python glossary_builder_ai.py article.md
```

### Specify Expertise Level

Target senior developers (will extract fewer, more complex terms):
```bash
python glossary_builder_ai.py blog_post.md --expertise-level senior
```

Target junior developers (default - extracts more terms with simpler explanations):
```bash
python glossary_builder_ai.py tutorial.md --expertise-level junior
```

### Output Formats

Generate HTML glossary:
```bash
python glossary_builder_ai.py doc.md --format html --output glossary.html
```

Display as interactive table:
```bash
python glossary_builder_ai.py doc.md --format table
```

Export as JSON:
```bash
python glossary_builder_ai.py doc.md --format json --output terms.json
```

### Command Options

- `FILE`: Path to the document to analyze (required)
- `--api-key`: Anthropic API key (can also use ANTHROPIC_API_KEY env var)
- `--expertise-level, -e`: Target audience level - junior, mid, or senior (default: junior)
- `--output, -o`: Output file path (if not specified, prints to stdout)
- `--format, -f`: Output format - markdown, json, html, plain, or table (default: markdown)
- `--estimate-cost`: Show estimated API costs before processing
- `--no-progress`: Disable progress indicators

## Example Output

```markdown
# Technical Glossary

*Generated for: junior developer with 2-3 years of experience*

## Kubernetes

An open-source container orchestration platform that automates deployment, 
scaling, and management of containerized applications across clusters of hosts.

*Context: Used in this document for managing microservices architecture*

📚 [Documentation](https://kubernetes.io/docs/)

## GraphQL

A query language and runtime for APIs that allows clients to request exactly 
the data they need, reducing over-fetching compared to REST APIs.

📚 [Documentation](https://graphql.org/learn/)
```

## Use Cases

- 📝 **Technical Blogs**: Automatically generate glossaries for blog posts
- 📚 **Documentation**: Add glossaries to API docs or tutorials
- 🎓 **Educational Content**: Create learning aids for technical courses
- 👥 **Onboarding**: Generate glossaries for team documentation
- 🎯 **Content Accessibility**: Make technical content more accessible

## Development

### Project Structure
```
glossary-builder/
├── glossary_builder_ai.py  # Main AI-powered CLI tool
├── glossary_builder.py      # Original JSON-based version
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
├── docs/                   # Sample documentation
└── README.md              # This file
```

### Extending the Tool

- **Add More Doc Links**: Edit the `DOC_LINKS` dictionary in `glossary_builder_ai.py`
- **Customize Prompts**: Modify the extraction and definition prompts for different use cases
- **Add Expertise Levels**: Extend `EXPERTISE_LEVELS` for more granular targeting

## Original Version

The repository also includes `glossary_builder.py`, which uses a pre-defined JSON database of terms instead of AI. This version is useful for:
- Consistent term definitions across projects
- Offline usage without API access
- Complete control over term selection
