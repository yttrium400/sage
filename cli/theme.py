"""
Color theme and styling for the CLI
"""

from rich.theme import Theme
from rich.console import Console

# Color palette - Blue/Cyan theme (professional, like Claude Code)
THEME = Theme({
    # Primary colors
    "primary": "#5B9FFF bold",          # Bright blue
    "accent": "#00D9FF",                # Cyan
    "secondary": "#7B68EE",             # Medium slate blue

    # Status colors
    "success": "#00E676 bold",          # Bright green
    "warning": "#FFD54F bold",          # Amber
    "error": "#FF5252 bold",            # Red
    "info": "#64B5F6",                  # Light blue

    # Text colors
    "text": "#E0E0E0",                  # Light gray text
    "dim": "#808080",                   # Dim gray
    "bright": "#FFFFFF bold",           # White

    # Code colors
    "code": "#A5D6FF",                  # Light blue (for code)
    "code_bg": "#0D1117",               # Dark background

    # UI elements
    "border": "#5B9FFF",                # Blue border
    "prompt": "#00D9FF bold",           # Cyan prompt
    "assistant": "#5B9FFF bold",        # Blue for assistant
    "user": "#00E676 bold",             # Green for user
})


def get_console() -> Console:
    """Get a themed console instance"""
    return Console(theme=THEME, width=None)  # None = full width


# ASCII Art Banner
BANNER_TEMPLATE = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ██████╗ ██████╗ ██████╗ ███████╗                           ║
║   ██╔════╝██╔═══██╗██╔══██╗██╔════╝                           ║
║   ██║     ██║   ██║██║  ██║█████╗                             ║
║   ██║     ██║   ██║██║  ██║██╔══╝                             ║
║   ╚██████╗╚██████╔╝██████╔╝███████╗                           ║
║    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝                           ║
║                                                               ║
║   ╔═╗ ╔═╗ ╔═╗ ╦ ╔═╗ ╔╦╗ ╔═╗ ╔╗╔ ╔╦╗                           ║
║   ╠═╣ ╚═╗ ╚═╗ ║ ╚═╗  ║  ╠═╣ ║║║  ║                            ║
║   ╩ ╩ ╚═╝ ╚═╝ ╩ ╚═╝  ╩  ╩ ╩ ╝╚╝  ╩                            ║
║                                                               ║
║   AI-Powered Python Coding Assistant                          ║
║   Built for developers who demand excellence                  ║
║                                                               ║
║───────────────────────────────────────────────────────────────║
║                                                               ║
║   Model: {model:<51}  ║
║   Context: {context:<49}  ║
║                                                               ║
║   Type your question or /help for commands.                   ║
║   Type 'exit' to quit.                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

# Simpler banner for smaller terminals
BANNER_SIMPLE_TEMPLATE = """
┌─────────────────────────────────────────────────┐
│  CODE ASSISTANT                                 │
│  AI-Powered Python Coding Assistant             │
│─────────────────────────────────────────────────│
│  Model: {model:<39}                             │
│  Context: {context:<37}                         │
│                                                 │
│  Type your question or /help. 'exit' to quit.   │
└─────────────────────────────────────────────────┘
"""


def get_banner(width: int, model: str = "", context: str = "") -> str:
    """Get appropriate banner based on terminal width with session info"""
    # Truncate long strings
    model_display = model if len(model) <= 50 else model[:47] + "..."
    context_display = context if len(context) <= 48 else "..." + context[-45:]

    if width >= 80:
        return BANNER_TEMPLATE.format(model=model_display, context=context_display)
    else:
        return BANNER_SIMPLE_TEMPLATE.format(model=model_display, context=context_display)


# Styled messages
def format_user_message(message: str) -> str:
    """Format user message with style"""
    return f"[user]You:[/user] {message}"


def format_assistant_message(message: str) -> str:
    """Format assistant message with style"""
    return f"[assistant]Assistant:[/assistant]"


def format_system_message(message: str, type: str = "info") -> str:
    """Format system message with appropriate style"""
    icons = {
        "success": "✓",
        "error": "✗",
        "warning": "!",
        "info": "ℹ",
    }
    icon = icons.get(type, "•")
    return f"[{type}]{icon} {message}[/{type}]"


def format_code_block(code: str) -> str:
    """Format code block with syntax highlighting"""
    return f"[code]{code}[/code]"


# Progress indicators
THINKING_SPINNER = "dots"
THINKING_TEXT = "[accent]Thinking...[/accent]"
CONTEXT_TEXT = "[info]Retrieving context...[/info]"
