#!/usr/bin/env python3
"""
Test script to demonstrate improved context awareness
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from context import (
    get_relevant_context,
    index_codebase,
    infer_target_files,
    search_codebase,
    build_file_dependency_graph,
)

console = Console()


def test_indexing():
    """Test codebase indexing"""
    console.print("\n[bold cyan]1. Testing Codebase Indexing[/bold cyan]")
    console.print("[dim]   Using tree-sitter parsing + ChromaDB vector store[/dim]\n")

    context_dir = os.getcwd()

    try:
        collection = index_codebase(context_dir)
        count = collection.count()

        console.print(f"[green]✓ Successfully indexed {count} code chunks[/green]")
        console.print(f"[dim]  Database location: .code_assistant_db/[/dim]")

        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_search():
    """Test semantic search capabilities"""
    console.print("\n[bold cyan]2. Testing Semantic Search[/bold cyan]")
    console.print("[dim]   Query embeddings + similarity matching[/dim]\n")

    test_queries = [
        "streaming response generation",
        "file operations and writing",
        "user interface and theming",
    ]

    context_dir = os.getcwd()

    for query in test_queries:
        console.print(f"[yellow]Query:[/yellow] {query}")

        try:
            results = search_codebase(query, context_dir, max_results=2)

            if results:
                for result in results:
                    name = result.get('name', 'N/A')
                    file = result.get('file', '').split('/')[-1]
                    chunk_type = result.get('chunk_type', 'code')

                    console.print(f"  [green]→ Found:[/green] {chunk_type} '{name}' in {file}")
            else:
                console.print("  [dim]No results[/dim]")

        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

        console.print()


def test_file_inference():
    """Test smart file path inference"""
    console.print("\n[bold cyan]3. Testing File Path Inference[/bold cyan]")
    console.print("[dim]   Infer target files from natural language queries[/dim]\n")

    test_queries = [
        "create calc.py with add and subtract functions",
        "edit the model.py file to improve response quality",
        "add authentication features",
        "update theme settings",
    ]

    context_dir = os.getcwd()

    for query in test_queries:
        console.print(f"[yellow]Query:[/yellow] {query}")

        files = infer_target_files(query, context_dir)

        if files:
            console.print(f"  [green]→ Inferred files:[/green] {', '.join(files)}")
        else:
            console.print("  [dim]→ No specific files inferred (will use semantic search)[/dim]")

        console.print()


def test_dependency_graph():
    """Test file dependency mapping"""
    console.print("\n[bold cyan]4. Testing Dependency Graph[/bold cyan]")
    console.print("[dim]   Extract and map import relationships[/dim]\n")

    context_dir = os.getcwd()

    try:
        graph = build_file_dependency_graph(context_dir)

        console.print(f"[green]✓ Built dependency graph for {len(graph)} files[/green]\n")

        # Show files with dependencies
        files_with_deps = {k: v for k, v in graph.items() if v}

        if files_with_deps:
            console.print("[yellow]Files with local imports:[/yellow]")
            for file_path, deps in list(files_with_deps.items())[:3]:
                filename = file_path.split('/')[-1]
                console.print(f"  [cyan]{filename}[/cyan] imports from:")
                for dep in deps[:3]:
                    dep_name = dep.split('/')[-1]
                    console.print(f"    • {dep_name}")
                console.print()

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def test_context_retrieval():
    """Test end-to-end context retrieval"""
    console.print("\n[bold cyan]5. Testing Context Retrieval[/bold cyan]")
    console.print("[dim]   Full pipeline: query → embeddings → relevant chunks[/dim]\n")

    test_query = "How does the streaming response work?"
    context_dir = os.getcwd()

    console.print(f"[yellow]Query:[/yellow] {test_query}\n")

    try:
        context = get_relevant_context(test_query, context_dir, max_chunks=3)

        console.print(f"[green]✓ Retrieved {len(context)} characters of context[/green]\n")

        # Show preview
        preview = context[:600]
        console.print(Panel(
            preview + "\n...",
            title="[cyan]Context Preview[/cyan]",
            border_style="cyan",
        ))

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    console.print(Panel(
        "[bold]Code Assistant - Context Awareness Test Suite[/bold]\n"
        "Testing vector search, semantic matching, and smart file inference",
        style="bold blue",
    ))

    # Run tests
    if not test_indexing():
        console.print("\n[red]Indexing failed. Skipping other tests.[/red]")
        return

    test_semantic_search()
    test_file_inference()
    test_dependency_graph()
    test_context_retrieval()

    console.print("\n[bold green]✓ All tests completed![/bold green]\n")


if __name__ == "__main__":
    main()
