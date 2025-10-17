# Define technical terms with an AI-driven glossary builder

This README describes how to install and use a Python CLI tool that extracts technical terms from documents and creates glossaries that are tailored to audiences with different expertise levels.

To use these instructions, you'll need to have an Anthropic account with an API key.

## How It Works

1. The tool reads and analyzes your technical documentation.
2. Claude AI analyzes the content and identifies terms that might be unfamiliar to your target audience.
3. For each term, Claude generates:
   - A clear, concise definition appropriate for the expertise level of the target audience
   - Context-specific notes about how the term is used in your document
   - Links to official documentation when available

The tool automatically limits results to 8 most important terms to maintain focus and readability.

## Install the glossary builder

1. Clone the glossary builder repository:

```bash
git clone https://github.com/your-username/glossary-builder.git
cd glossary-builder
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add your API key
```

To get your Anthropic API key, use the [Anthropic Console](https://console.anthropic.com/).

## Run the Python command

Use the glossary builder to extract and define terms from a technical document:

```bash
python glossary_builder_ai.py example-document.md
```

Available command flags are the following:

- `FILE`: The path to the document to analyze. Required.
- `--api-key`: Your Anthropic API key. If not set, the value of the `ANTHROPIC_API_KEY` environment variable is used.
- `--expertise-level, -e`: The target audience level. Values are: `junior`, `mid`, or `senior`. If not set, defaults to `junior`.
- `--output, -o`: The output file path. If not set, prints to stdout.
- `--format, -f`: The output format. Values are: `markdown`, `json`, `html`, `plain`, or `table`. If not set, defaults to `markdown`.
- `--estimate-cost`: Show estimated API costs before processing.
- `--no-progress`: Disable progress indicators.

### Example commands

#### Specify an audience expertise level

The glossary builder generates fewer, more complex terms for **senior developers** and more terms with simpler explanations for **junior developers**.

```bash
python glossary_builder_ai.py blog_post.md --expertise-level senior
```

```bash
python glossary_builder_ai.py tutorial.md --expertise-level junior
```

#### Control output formats

Generate an HTML glossary as output:

```bash
python glossary_builder_ai.py doc.md --format html --output glossary.html
```

Display the output as an interactive table:

```bash
python glossary_builder_ai.py doc.md --format table
```

Export the output as JSON:

```bash
python glossary_builder_ai.py doc.md --format json --output terms.json
```

### Example Output

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
