#!/usr/bin/env python3

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

console = Console()

EXPERTISE_LEVELS = {
    'junior': 'junior developer with 2-3 years of experience',
    'mid': 'mid-level developer with 4-6 years of experience', 
    'senior': 'senior developer with 7+ years of experience'
}

DOC_LINKS = {
    'kubernetes': 'https://kubernetes.io/docs/',
    'docker': 'https://docs.docker.com/',
    'react': 'https://react.dev/',
    'python': 'https://docs.python.org/3/',
    'javascript': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
    'typescript': 'https://www.typescriptlang.org/docs/',
    'aws': 'https://docs.aws.amazon.com/',
    'git': 'https://git-scm.com/doc',
    'postgresql': 'https://www.postgresql.org/docs/',
    'mongodb': 'https://www.mongodb.com/docs/',
    'redis': 'https://redis.io/docs/',
    'graphql': 'https://graphql.org/learn/',
    'rest': 'https://restfulapi.net/',
    'oauth': 'https://oauth.net/2/',
    'jwt': 'https://jwt.io/introduction',
    'nginx': 'https://nginx.org/en/docs/',
    'terraform': 'https://developer.hashicorp.com/terraform/docs',
    'ansible': 'https://docs.ansible.com/',
    'jenkins': 'https://www.jenkins.io/doc/',
    'github': 'https://docs.github.com/',
}

class AIGlossaryBuilder:
    def __init__(self, api_key: Optional[str] = None, expertise_level: str = 'junior'):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            console.print("[red]Error: ANTHROPIC_API_KEY not found. Set it in .env or pass via --api-key[/red]")
            sys.exit(1)
        
        self.client = Anthropic(api_key=self.api_key)
        self.expertise_level = expertise_level
        self.expertise_desc = EXPERTISE_LEVELS.get(expertise_level, EXPERTISE_LEVELS['junior'])
        
    def read_document(self, file_path: Path) -> str:
        """Read document content from file."""
        if not file_path.exists():
            console.print(f"[red]Error: File '{file_path}' not found.[/red]")
            sys.exit(1)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            sys.exit(1)
    
    def chunk_document(self, content: str, max_chars: int = 8000) -> List[str]:
        """Split document into chunks for processing."""
        if len(content) <= max_chars:
            return [content]
        
        chunks = []
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_terms(self, content: str) -> List[str]:
        """Use Claude to extract technical terms from document."""
        prompt = f"""You are analyzing technical documentation for a {self.expertise_desc}.
        
Extract technical terms, acronyms, and concepts that this audience might not fully understand or would benefit from clarification.

Document content:
{content}

Instructions:
1. Identify technical terms, acronyms, jargon, and complex concepts
2. Focus on terms a {self.expertise_desc} might find challenging
3. Include terms that are used in specific contexts in this document
4. Return ONLY a JSON array of terms (no explanations yet)
5. Limit to the 8 most important/complex terms if there are many
6. Order by importance/complexity for the target audience

Return format: ["term1", "term2", "term3", ...]"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            terms_text = response.content[0].text.strip()
            # Extract JSON array from response
            match = re.search(r'\[.*\]', terms_text, re.DOTALL)
            if match:
                terms = json.loads(match.group())
                return [term.lower() for term in terms[:8]]  # Ensure max 8 terms
            else:
                console.print("[yellow]Warning: Could not parse terms from API response[/yellow]")
                return []
                
        except Exception as e:
            console.print(f"[red]Error extracting terms: {e}[/red]")
            return []
    
    def generate_definitions(self, terms: List[str], context: str) -> Dict[str, Dict]:
        """Generate definitions for extracted terms using Claude."""
        if not terms:
            return {}
        
        prompt = f"""You are creating a glossary for a {self.expertise_desc}.

Document context (for reference):
{context[:2000]}...

Generate clear, concise definitions for these technical terms:
{json.dumps(terms)}

For each term:
1. Provide a clear definition (2-3 sentences max)
2. If the term has a specific meaning in the document context, mention it
3. Keep explanations appropriate for a {self.expertise_desc}

Return a JSON object with this structure:
{{
  "term": {{
    "definition": "Clear explanation of the term",
    "context_note": "Optional: How it's specifically used in this document (if applicable)"
  }}
}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            definitions_text = response.content[0].text.strip()
            # Extract JSON object from response
            match = re.search(r'\{.*\}', definitions_text, re.DOTALL)
            if match:
                definitions = json.loads(match.group())
                # Add documentation links
                for term in definitions:
                    definitions[term]['doc_link'] = self._find_doc_link(term)
                return definitions
            else:
                console.print("[yellow]Warning: Could not parse definitions from API response[/yellow]")
                return {}
                
        except Exception as e:
            console.print(f"[red]Error generating definitions: {e}[/red]")
            return {}
    
    def _find_doc_link(self, term: str) -> Optional[str]:
        """Find relevant documentation link for a term."""
        term_lower = term.lower()
        for key, url in DOC_LINKS.items():
            if key in term_lower or term_lower in key:
                return url
        return None
    
    def estimate_cost(self, content: str) -> Tuple[float, str]:
        """Estimate API costs for processing document."""
        # Rough estimates based on current Anthropic pricing
        input_tokens = len(content) / 4  # Rough estimate
        
        # Haiku for extraction: $0.25 per million input tokens
        haiku_cost = (input_tokens / 1_000_000) * 0.25
        
        # Sonnet for definitions: $3 per million input tokens  
        sonnet_cost = (input_tokens / 1_000_000) * 3
        
        total_cost = haiku_cost + sonnet_cost
        
        breakdown = f"Extraction: ${haiku_cost:.4f}, Definitions: ${sonnet_cost:.4f}"
        return total_cost, breakdown
    
    def process_document(self, file_path: Path, show_progress: bool = True) -> Dict[str, Dict]:
        """Process document to extract terms and generate glossary."""
        console.print(f"\n[bold blue]Processing: {file_path.name}[/bold blue]")
        
        content = self.read_document(file_path)
        chunks = self.chunk_document(content)
        
        all_terms = []
        all_definitions = {}
        
        for i, chunk in enumerate(chunks):
            if show_progress and len(chunks) > 1:
                console.print(f"Processing chunk {i+1}/{len(chunks)}...")
            
            # Extract terms from chunk
            with console.status("[bold green]Extracting technical terms..."):
                terms = self.extract_terms(chunk)
            
            if terms:
                console.print(f"  ✓ Found {len(terms)} technical terms")
                all_terms.extend(terms)
                
                # Generate definitions
                with console.status("[bold green]Generating definitions..."):
                    definitions = self.generate_definitions(terms, chunk)
                    all_definitions.update(definitions)
        
        # Limit to 8 most important terms across all chunks
        if len(all_definitions) > 8:
            console.print(f"[yellow]Limiting to 8 most important terms (found {len(all_definitions)})[/yellow]")
            all_definitions = dict(list(all_definitions.items())[:8])
        
        return all_definitions
    
    def generate_output(self, glossary: Dict[str, Dict], format: str = 'markdown') -> str:
        """Generate formatted output."""
        if not glossary:
            return "No technical terms found requiring clarification."
        
        if format == 'markdown':
            return self._generate_markdown(glossary)
        elif format == 'json':
            return json.dumps(glossary, indent=2)
        elif format == 'html':
            return self._generate_html(glossary)
        else:
            return self._generate_plain(glossary)
    
    def _generate_markdown(self, glossary: Dict[str, Dict]) -> str:
        """Generate Markdown formatted glossary."""
        lines = ["# Technical Glossary\n"]
        lines.append(f"*Generated for: {self.expertise_desc}*\n")
        
        for term, info in sorted(glossary.items()):
            lines.append(f"## {term.title()}\n")
            lines.append(f"{info['definition']}\n")
            
            if info.get('context_note'):
                lines.append(f"*Context: {info['context_note']}*\n")
            
            if info.get('doc_link'):
                lines.append(f"📚 [Documentation]({info['doc_link']})\n")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(self, glossary: Dict[str, Dict]) -> str:
        """Generate HTML formatted glossary."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Technical Glossary</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 { color: #2563eb; }
        .subtitle { color: #6b7280; font-style: italic; margin-bottom: 2em; }
        .term {
            margin-bottom: 25px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .term-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .definition { margin-bottom: 10px; }
        .context {
            font-style: italic;
            opacity: 0.9;
            margin-top: 10px;
        }
        .doc-link {
            display: inline-block;
            margin-top: 10px;
            padding: 5px 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            color: white;
            text-decoration: none;
        }
        .doc-link:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <h1>Technical Glossary</h1>
"""
        html += f'    <div class="subtitle">Generated for: {self.expertise_desc}</div>\n'
        
        for term, info in sorted(glossary.items()):
            html += '    <div class="term">\n'
            html += f'        <div class="term-title">{term.title()}</div>\n'
            html += f'        <div class="definition">{info["definition"]}</div>\n'
            
            if info.get('context_note'):
                html += f'        <div class="context">Context: {info["context_note"]}</div>\n'
            
            if info.get('doc_link'):
                html += f'        <a href="{info["doc_link"]}" class="doc-link" target="_blank">📚 Documentation</a>\n'
            
            html += '    </div>\n'
        
        html += """</body>
</html>"""
        return html
    
    def _generate_plain(self, glossary: Dict[str, Dict]) -> str:
        """Generate plain text formatted glossary."""
        lines = ["TECHNICAL GLOSSARY\n" + "="*50]
        lines.append(f"For: {self.expertise_desc}\n")
        
        for term, info in sorted(glossary.items()):
            lines.append(f"\n{term.upper()}")
            lines.append("-" * len(term))
            lines.append(info['definition'])
            
            if info.get('context_note'):
                lines.append(f"\nContext: {info['context_note']}")
            
            if info.get('doc_link'):
                lines.append(f"\nDocumentation: {info['doc_link']}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def display_table(self, glossary: Dict[str, Dict]) -> None:
        """Display glossary as a rich table."""
        table = Table(title="Technical Glossary", show_header=True, header_style="bold magenta")
        table.add_column("Term", style="cyan", no_wrap=False)
        table.add_column("Definition", style="white", no_wrap=False)
        table.add_column("Documentation", style="blue")
        
        for term, info in sorted(glossary.items()):
            doc = "✓" if info.get('doc_link') else "—"
            table.add_row(term.title(), info['definition'], doc)
        
        console.print(table)


@click.command()
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('--api-key', envvar='ANTHROPIC_API_KEY', help='Anthropic API key')
@click.option('--expertise-level', '-e',
              type=click.Choice(['junior', 'mid', 'senior']),
              default='junior',
              help='Target audience expertise level (default: junior)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f',
              type=click.Choice(['markdown', 'json', 'html', 'plain', 'table']),
              default='markdown',
              help='Output format (default: markdown)')
@click.option('--estimate-cost', is_flag=True, help='Estimate API costs before processing')
@click.option('--no-progress', is_flag=True, help='Disable progress indicators')
def main(file, api_key, expertise_level, output, format, estimate_cost, no_progress):
    """
    AI-powered glossary builder that intelligently extracts and defines technical terms.
    
    Uses Claude AI to identify terms that might be unfamiliar to the target audience
    and generates clear, contextual definitions with documentation links.
    
    EXAMPLES:
    
        glossary_builder_ai.py article.md
        
        glossary_builder_ai.py blog_post.md --expertise-level senior
        
        glossary_builder_ai.py doc.md --format html --output glossary.html
        
        glossary_builder_ai.py technical_doc.md --estimate-cost
    """
    
    console.print("[bold blue]AI-Powered Glossary Builder[/bold blue]")
    console.print(f"Expertise Level: {expertise_level}\n")
    
    file_path = Path(file)
    builder = AIGlossaryBuilder(api_key=api_key, expertise_level=expertise_level)
    
    # Estimate costs if requested
    if estimate_cost:
        content = builder.read_document(file_path)
        total_cost, breakdown = builder.estimate_cost(content)
        console.print(f"[yellow]Estimated API cost: ${total_cost:.4f}[/yellow]")
        console.print(f"[dim]{breakdown}[/dim]\n")
        
        if not click.confirm("Proceed with processing?"):
            console.print("[red]Aborted.[/red]")
            return
    
    # Process document
    glossary = builder.process_document(file_path, show_progress=not no_progress)
    
    if not glossary:
        console.print("[yellow]No technical terms found requiring clarification.[/yellow]")
        return
    
    console.print(f"\n[green]✓ Generated glossary with {len(glossary)} terms[/green]")
    
    # Generate output
    if format == 'table':
        builder.display_table(glossary)
    else:
        output_content = builder.generate_output(glossary, format)
        
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            console.print(f"[green]Glossary saved to: {output_path}[/green]")
        else:
            console.print("\n" + output_content)


if __name__ == '__main__':
    main()