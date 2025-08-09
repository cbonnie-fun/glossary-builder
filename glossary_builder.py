#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()


class GlossaryBuilder:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.terms_db = self._load_database()
        self.found_terms = {}
        
    def _load_database(self) -> Dict[str, Dict]:
        if not self.database_path.exists():
            console.print(f"[red]Error: Database file '{self.database_path}' not found.[/red]")
            sys.exit(1)
        
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {term.lower(): info for term, info in data.items()}
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing JSON database: {e}[/red]")
            sys.exit(1)
    
    def scan_document(self, file_path: Path) -> Set[str]:
        if not file_path.exists():
            console.print(f"[yellow]Warning: File '{file_path}' not found, skipping.[/yellow]")
            return set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read '{file_path}': {e}[/yellow]")
            return set()
        
        found_terms = set()
        
        for term in self.terms_db.keys():
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, content, re.IGNORECASE):
                found_terms.add(term)
        
        return found_terms
    
    def scan_multiple_documents(self, file_paths: List[Path]) -> None:
        all_terms = set()
        
        with console.status("[bold green]Scanning documentation files...") as status:
            for file_path in file_paths:
                status.update(f"[bold green]Scanning: {file_path.name}...")
                terms = self.scan_document(file_path)
                all_terms.update(terms)
                if terms:
                    console.print(f"  ✓ Found {len(terms)} terms in {file_path.name}")
        
        for term in all_terms:
            self.found_terms[term] = self.terms_db[term]
        
        console.print(f"\n[bold green]Total unique terms found: {len(self.found_terms)}[/bold green]")
    
    def generate_glossary(self, output_format: str = 'markdown', output_file: Optional[str] = None):
        if not self.found_terms:
            console.print("[yellow]No technical terms found in the scanned documents.[/yellow]")
            return
        
        sorted_terms = sorted(self.found_terms.items())
        
        if output_format == 'markdown':
            content = self._generate_markdown(sorted_terms)
        elif output_format == 'json':
            content = self._generate_json(sorted_terms)
        elif output_format == 'html':
            content = self._generate_html(sorted_terms)
        elif output_format == 'table':
            self._display_table(sorted_terms)
            return
        else:
            content = self._generate_plain(sorted_terms)
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]Glossary saved to: {output_path}[/green]")
        else:
            console.print("\n" + content)
    
    def _generate_markdown(self, terms: List[tuple]) -> str:
        lines = ["# Glossary\n"]
        
        current_letter = ""
        for term, info in terms:
            first_letter = term[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                lines.append(f"\n## {current_letter}\n")
            
            lines.append(f"### {term.title()}\n")
            lines.append(f"{info['definition']}\n")
            
            if 'category' in info:
                lines.append(f"*Category: {info['category']}*\n")
            
            if 'examples' in info:
                lines.append("\n**Examples:**")
                for example in info['examples']:
                    lines.append(f"- {example}")
                lines.append("")
            
            if 'related' in info:
                lines.append(f"\n**Related terms:** {', '.join(info['related'])}\n")
        
        return "\n".join(lines)
    
    def _generate_json(self, terms: List[tuple]) -> str:
        glossary = {term: info for term, info in terms}
        return json.dumps(glossary, indent=2)
    
    def _generate_html(self, terms: List[tuple]) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Glossary</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .term { margin-bottom: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px; }
        .term-title { font-weight: bold; color: #0066cc; font-size: 1.2em; }
        .definition { margin-top: 10px; }
        .category { color: #666; font-style: italic; }
        .examples { margin-top: 10px; }
        .related { margin-top: 10px; color: #666; }
    </style>
</head>
<body>
    <h1>Glossary</h1>
"""
        
        for term, info in terms:
            html += f'    <div class="term">\n'
            html += f'        <div class="term-title">{term.title()}</div>\n'
            html += f'        <div class="definition">{info["definition"]}</div>\n'
            
            if 'category' in info:
                html += f'        <div class="category">Category: {info["category"]}</div>\n'
            
            if 'examples' in info:
                html += '        <div class="examples"><strong>Examples:</strong><ul>\n'
                for example in info['examples']:
                    html += f'            <li>{example}</li>\n'
                html += '        </ul></div>\n'
            
            if 'related' in info:
                html += f'        <div class="related"><strong>Related:</strong> {", ".join(info["related"])}</div>\n'
            
            html += '    </div>\n'
        
        html += """</body>
</html>"""
        return html
    
    def _generate_plain(self, terms: List[tuple]) -> str:
        lines = ["GLOSSARY\n" + "="*50 + "\n"]
        
        for term, info in terms:
            lines.append(f"\n{term.upper()}")
            lines.append("-" * len(term))
            lines.append(info['definition'])
            
            if 'category' in info:
                lines.append(f"Category: {info['category']}")
            
            if 'examples' in info:
                lines.append("\nExamples:")
                for example in info['examples']:
                    lines.append(f"  * {example}")
            
            if 'related' in info:
                lines.append(f"\nRelated: {', '.join(info['related'])}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _display_table(self, terms: List[tuple]) -> None:
        table = Table(title="Glossary", show_header=True, header_style="bold magenta")
        table.add_column("Term", style="cyan", no_wrap=False)
        table.add_column("Definition", style="white", no_wrap=False)
        table.add_column("Category", style="yellow")
        
        for term, info in terms:
            category = info.get('category', 'N/A')
            table.add_row(term.title(), info['definition'], category)
        
        console.print(table)


@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--database', '-d', default='glossary_db.json', 
              help='Path to JSON database file (default: glossary_db.json)')
@click.option('--output', '-o', help='Output file path (if not specified, prints to stdout)')
@click.option('--format', '-f', 
              type=click.Choice(['markdown', 'json', 'html', 'plain', 'table']), 
              default='markdown',
              help='Output format (default: markdown)')
@click.option('--pattern', '-p', help='File pattern to scan (e.g., "*.md", "*.txt")')
def main(files, database, output, format, pattern):
    """
    Scan documentation files for technical terms and generate a glossary.
    
    EXAMPLES:
    
        glossary_builder.py doc.md README.md
        
        glossary_builder.py docs/*.md --format html --output glossary.html
        
        glossary_builder.py . --pattern "*.md" --format table
    """
    
    console.print("[bold blue]Glossary Builder[/bold blue]")
    console.print(f"Database: {database}\n")
    
    file_paths = []
    
    for file_arg in files:
        path = Path(file_arg)
        if path.is_dir():
            if pattern:
                file_paths.extend(path.rglob(pattern))
            else:
                file_paths.extend(path.rglob('*.md'))
                file_paths.extend(path.rglob('*.txt'))
                file_paths.extend(path.rglob('*.rst'))
        else:
            file_paths.append(path)
    
    if not file_paths:
        console.print("[red]No files to scan.[/red]")
        sys.exit(1)
    
    builder = GlossaryBuilder(database)
    builder.scan_multiple_documents(file_paths)
    builder.generate_glossary(format, output)


if __name__ == '__main__':
    main()