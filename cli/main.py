#!/usr/bin/env python3
"""
Code Assistant CLI - Main entry point
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Code Assistant - AI-powered coding assistant for Python"""
    pass


@cli.command()
@click.option(
    "--model",
    default="qwen2.5-coder:3b",
    help="Model to use (Ollama model name)",
)
@click.option(
    "--context-dir",
    default=".",
    type=click.Path(exists=True),
    help="Directory to use as codebase context",
)
def chat(model: str, context_dir: str):
    """Start an interactive chat session"""
    # Import here to avoid slow startup
    from chat import start_chat_session

    start_chat_session(model=model, context_dir=context_dir)


@cli.command()
@click.argument("query")
@click.option(
    "--model",
    default="qwen2.5-coder:3b",
    help="Model to use",
)
@click.option(
    "--context-dir",
    default=".",
    type=click.Path(exists=True),
    help="Directory to use as context",
)
def ask(query: str, model: str, context_dir: str):
    """Ask a single question (non-interactive)"""
    from chat import single_query

    response = single_query(query=query, model=model, context_dir=context_dir)
    console.print(Markdown(response))


@cli.command()
@click.option(
    "--context-dir",
    default=".",
    type=click.Path(exists=True),
    help="Directory to index",
)
def index(context_dir: str):
    """Index a codebase for context retrieval"""
    from context import index_codebase

    console.print(f"[yellow]Indexing codebase in {context_dir}...[/yellow]")

    stats = index_codebase(context_dir)

    console.print(
        Panel.fit(
            f"[green]✓[/green] Indexed {stats['files']} files\n"
            f"[green]✓[/green] Created {stats['chunks']} code chunks\n"
            f"[green]✓[/green] Total size: {stats['size_mb']:.2f} MB",
            title="Indexing Complete",
        )
    )


@cli.command()
def models():
    """List available models"""
    from model import list_available_models

    available = list_available_models()

    if not available:
        console.print("[red]No models found. Please install Ollama and pull a model.[/red]")
        console.print("\nExample: [cyan]ollama pull deepseek-coder:6.7b[/cyan]")
        return

    console.print("[bold]Available Models:[/bold]\n")
    for model_name in available:
        console.print(f"  • {model_name}")


@cli.command()
def setup():
    """Setup wizard for first-time users"""
    console.print(
        Panel.fit(
            "[bold blue]Code Assistant Setup[/bold blue]\n\n"
            "This wizard will help you set up the coding assistant.",
            title="Setup",
        )
    )

    # Check if Ollama is installed
    import shutil
    if not shutil.which("ollama"):
        console.print("\n[red]✗ Ollama not found[/red]")
        console.print("\nPlease install Ollama:")
        console.print("  macOS: [cyan]brew install ollama[/cyan]")
        console.print("  Linux: [cyan]curl -fsSL https://ollama.com/install.sh | sh[/cyan]")
        console.print("  Windows: Download from https://ollama.com")
        return

    console.print("\n[green]✓ Ollama is installed[/green]")

    # Check for models
    from model import list_available_models
    available = list_available_models()

    if not available:
        console.print("\n[yellow]! No models found[/yellow]")
        console.print("\nRecommended model: [cyan]deepseek-coder:6.7b[/cyan]")

        if click.confirm("\nWould you like to download it now?"):
            console.print("\n[yellow]Downloading model (this may take a few minutes)...[/yellow]")
            import subprocess
            subprocess.run(["ollama", "pull", "deepseek-coder:6.7b"])
            console.print("[green]✓ Model downloaded[/green]")
    else:
        console.print(f"\n[green]✓ Found {len(available)} model(s)[/green]")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("\nTry: [cyan]code-assistant chat[/cyan]")


if __name__ == "__main__":
    cli()
