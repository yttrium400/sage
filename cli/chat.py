"""
Interactive chat interface
"""

from typing import Optional
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import os
import re
import sys

from model import generate_response, generate_response_streaming
from context import get_relevant_context, infer_target_files
from file_ops import (
    read_file,
    write_file,
    list_files,
    propose_file_changes,
)
from theme import (
    get_console,
    get_banner,
    format_user_message,
    format_assistant_message,
    format_system_message,
    THINKING_SPINNER,
    CONTEXT_TEXT,
)

console = get_console()


def format_response_with_syntax(response: str):
    """Format response with syntax highlighting for code blocks"""
    # Split response by code blocks (```python ... ```)
    parts = re.split(r'(```(?:python)?\n.*?\n```)', response, flags=re.DOTALL)

    for part in parts:
        # Check if this is a code block
        if part.startswith('```'):
            # Extract code content
            code_match = re.match(r'```(?:python)?\n(.*?)\n```', part, re.DOTALL)
            if code_match:
                code = code_match.group(1)
                # Render with syntax highlighting
                syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                console.print(syntax)
            else:
                # Fallback if regex doesn't match
                console.print(part, markup=False)
        else:
            # Regular text
            if part.strip():
                console.print(part, markup=False, end="")


def start_chat_session(model: str, context_dir: str):
    """Start an interactive chat session"""

    # Get terminal width and show banner with integrated session info
    width = console.width
    banner = get_banner(width, model=model, context=context_dir)
    console.print(f"[primary]{banner}[/primary]")
    console.print()

    # Create history file
    history_file = os.path.expanduser("~/.code_assistant_history")
    session = PromptSession(history=FileHistory(history_file))

    conversation_history = []

    # Define style for transparent bottom toolbar
    style = Style.from_dict({
        'bottom-toolbar': 'bg:default noreverse',
    })

    while True:
        try:
            with patch_stdout():
                # Get user input with colored prompt and bottom padding
                # The bottom_toolbar creates empty space at the bottom
                # We use a transparent style to avoid the white bar
                user_input = session.prompt(
                    HTML("\n<style fg='#444444'>──────────────────────────────────────────────────────────────────────────────────────────────────</style>\n<ansigreen><b>You:</b></ansigreen> "), 
                    multiline=False,
                    bottom_toolbar=HTML("\n" * 1),  # Reserve 1 empty line at the bottom
                    style=style
                )

            if not user_input.strip():
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\n[dim]Goodbye![/dim]")
                break

            # Special commands
            if user_input.startswith("/"):
                handle_command(user_input, context_dir)
                continue

            # Get relevant context from codebase
            with console.status(CONTEXT_TEXT):
                context = get_relevant_context(user_input, context_dir)

            # Generate response with streaming
            console.print()
            console.print(Rule(format_assistant_message(""), style="border"))
            console.print()

            response = ""
            in_code_block = False
            code_block_started = False  # Track if we've seen any code blocks yet
            code_buffer = ""
            code_header = ""  # Track the code block header (```python:file.py or ```python)
            first_chunk = True
            shown_codes = set()  # Track code content we've already displayed
            plain_text_buffer = ""  # Buffer for text before first code block

            # Show animated thinking indicator until first token arrives
            from rich.spinner import Spinner
            import random
            spinner_styles = ["dots", "dots2", "dots3", "line", "arc", "arrow3", "bouncingBall", "clock"]
            thinking_messages = [
                "[cyan]Thinking...[/cyan]",
                "[cyan]Processing your request...[/cyan]",
                "[cyan]Analyzing...[/cyan]",
                "[cyan]Generating response...[/cyan]",
            ]
            spinner = Spinner(
                random.choice(spinner_styles),
                text=random.choice(thinking_messages),
                style="cyan"
            )
            with Live(spinner, console=console, refresh_per_second=10) as live:
                # Stream response with real-time syntax highlighting
                for chunk in generate_response_streaming(
                    query=user_input,
                    context=context,
                    model=model,
                    history=conversation_history,
                ):
                    # Clear "Thinking..." on first chunk
                    if first_chunk:
                        live.stop()
                        first_chunk = False

                    response += chunk

                    # Check if entering/exiting code block
                    if "```" in chunk:
                        if not in_code_block:
                            # Starting code block - stop spinner if still running
                            if first_chunk:
                                live.stop()
                                first_chunk = False

                            in_code_block = True
                            code_block_started = True
                            code_buffer = ""
                            code_header = ""

                            # If we had plain text buffered before first code block, print it now
                            if plain_text_buffer and not code_block_started:
                                console.print(plain_text_buffer, end="", markup=False)
                                plain_text_buffer = ""
                        else:
                            # Ending code block
                            # Extract just the code (skip header line like "python:calc.py")
                            lines = code_buffer.split('\n', 1)
                            if len(lines) > 1:
                                # First line is header (python:filename or just python)
                                code_content = lines[1].strip()
                            else:
                                code_content = code_buffer.strip()

                            # Check if this is a duplicate (same code already shown)
                            if code_content and code_content not in shown_codes:
                                # Show highlighted version
                                console.print("\n[dim]```[/dim]\n", markup=True)

                                # Show full code automatically
                                syntax = Syntax(code_content, "python", theme="monokai", line_numbers=True)
                                console.print(syntax)
                                shown_codes.add(code_content)

                            else:
                                # Skip duplicate
                                console.print("\n[dim]... (duplicate code block skipped) ...[/dim]\n")

                            in_code_block = False
                            code_buffer = ""
                            code_header = ""
                    elif in_code_block:
                        # Accumulate everything in buffer (including header)
                        # Don't print anything while accumulating - we'll show syntax highlighted version at the end
                        code_buffer += chunk
                    else:
                        # Regular text - only print if we've already shown a code block
                        # OR if it doesn't look like code (to avoid duplicate plain-text code)
                        if code_block_started:
                            # After first code block, print explanatory text normally
                            console.print(chunk, end="", markup=False)
                        else:
                            # Before first code block, buffer it (might be duplicate plain code)
                            plain_text_buffer += chunk

                # Handle unclosed code block
                if in_code_block and code_buffer:
                    code_content = code_buffer.strip()
                    if code_content not in shown_codes:
                        syntax = Syntax(code_content, "python", theme="monokai", line_numbers=True)
                        console.print(syntax)
                        shown_codes.add(code_content)

            console.print("\n")
            console.print(Rule(style="dim"))  # Separator after response

            # Check if response contains file changes to apply
            # Get inferred files for smart matching
            inferred_files = infer_target_files(user_input, context_dir)
            proposals = propose_file_changes(response, context_dir, inferred_files)
            if proposals:
                console.print(f"\n[yellow]📝 Found {len(proposals)} file change(s) in response[/yellow]\n")

                for filepath, content in proposals:
                    filename = os.path.basename(filepath)
                    console.print(f"[cyan]• {filename}[/cyan]")

                # Use prompt_toolkit for confirmation to maintain bottom padding
                confirm_response = session.prompt(
                    HTML("\n<style fg='#444444'>──────────────────────────────────────────────────────────────────────────────────────────────────</style>\n<ansiyellow>Apply these changes? [y/n] (n): </ansiyellow>"),
                    bottom_toolbar=HTML("\n" * 1),
                    style=style
                )
                
                if confirm_response.lower() in ['y', 'yes']:
                    for filepath, content in proposals:
                        write_file(filepath, content, confirm=False)  # Already confirmed above
                else:
                    console.print("[dim]Skipped applying changes. Use /read or /edit commands to apply manually.[/dim]")

                console.print()

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Keep history manageable (last 10 exchanges)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

        except KeyboardInterrupt:
            console.print("\n\n[dim]Use 'exit' to quit.[/dim]\n")
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


def single_query(query: str, model: str, context_dir: str) -> str:
    """Process a single query and return the response"""

    # Get context
    context = get_relevant_context(query, context_dir)

    # Generate response
    response = generate_response(
        query=query,
        context=context,
        model=model,
        history=[],
    )

    return response


def handle_command(command: str, context_dir: str):
    """Handle special commands"""

    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/help":
        console.print(
            """
[bold]Available Commands:[/bold]

  /help          - Show this help message
  /context       - Show current context directory
  /clear         - Clear conversation history
  /index         - Re-index the codebase
  /read <file>   - Read and display a file
  /edit <file>   - Edit a file interactively
  /create <file> - Create a new file
  /ls [pattern]  - List files (default: *.py)

[bold]File Editing:[/bold]
  • Use ```python:filename.py in chat to propose file changes
  • Assistant will ask for confirmation before writing files
  • View diffs before applying changes

[bold]Tips:[/bold]
  • Ask about code in your project
  • Request code generation
  • Ask for explanations or refactoring
  • Use natural language
"""
        )

    elif cmd == "/context":
        console.print(f"\n[dim]Current context directory: {context_dir}[/dim]\n")

    elif cmd == "/clear":
        console.print("\n[dim]Conversation history cleared.[/dim]\n")
        # History is cleared by the caller

    elif cmd == "/index":
        from context import index_codebase

        console.print("\n[yellow]Re-indexing codebase with vector embeddings...[/yellow]")
        try:
            collection = index_codebase(context_dir)
            count = collection.count()
            console.print(f"[green]✓ Indexed {count} code chunks with semantic search[/green]")
            console.print(f"[dim]  Vector embeddings stored in .code_assistant_db/[/dim]\n")
        except Exception as e:
            console.print(f"[red]✗ Error indexing codebase: {e}[/red]\n")

    elif cmd == "/read":
        if not args:
            console.print("[red]Usage: /read <file>[/red]\n")
            return

        filepath = os.path.join(context_dir, args)
        content = read_file(filepath)
        if content:
            from rich.syntax import Syntax
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"[cyan]{args}[/cyan]", border_style="cyan"))

    elif cmd == "/edit":
        if not args:
            console.print("[red]Usage: /edit <file>[/red]\n")
            return

        filepath = os.path.join(context_dir, args)
        content = read_file(filepath)
        if content:
            console.print(f"\n[yellow]Editing: {args}[/yellow]")
            console.print("[dim]Current content shown above. Use chat to request changes.[/dim]\n")

    elif cmd == "/create":
        if not args:
            console.print("[red]Usage: /create <file>[/red]\n")
            return

        filepath = os.path.join(context_dir, args)
        console.print(f"\n[yellow]Will create: {args}[/yellow]")
        console.print("[dim]Use chat to specify the content.[/dim]\n")

    elif cmd == "/ls":
        pattern = args if args else "*.py"
        files = list_files(context_dir, pattern)
        if files:
            console.print(f"\n[cyan]Files matching '{pattern}':[/cyan]")
            for f in files[:50]:  # Limit to 50 files
                console.print(f"  • {f}")
            if len(files) > 50:
                console.print(f"\n[dim]... and {len(files) - 50} more[/dim]")
            console.print()
        else:
            console.print(f"\n[dim]No files found matching '{pattern}'[/dim]\n")

    else:
        console.print(f"\n[red]Unknown command: {cmd}[/red]")
        console.print("[dim]Type /help for available commands[/dim]\n")
