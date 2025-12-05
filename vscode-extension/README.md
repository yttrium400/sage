# Sage Code Assistant - VSCode Extension

> AI-powered Python coding assistant with local LLM and semantic search

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![VSCode](https://img.shields.io/badge/vscode-%5E1.80.0-blue.svg)

## Features

- 🧙‍♂️ **Chat Interface**: Interactive chat sidebar for code assistance
- 🔍 **Semantic Search**: Context-aware code understanding using ChromaDB
- 🎯 **Code Actions**: Right-click menu for explaining and refactoring code
- 💬 **Inline Help**: Select code and get instant explanations
- 🔧 **Code Generation**: Generate code from natural language descriptions
- 🌐 **Fully Local**: Runs locally using Ollama - no API keys required

## Prerequisites

Before using this extension, you need to have:

1. **Python 3.8+** installed
2. **Ollama** installed and running
3. **Sage CLI** installed (bundled with extension)

### Installing Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com
```

### Pull a Model

```bash
# Recommended model
ollama pull qwen2.5-coder:3b

# Or other options
ollama pull qwen2.5-coder:1.5b  # Faster
ollama pull deepseek-coder:6.7b # More capable
```

## Installation

### From VSIX (Recommended)

1. Download the latest `.vsix` file from releases
2. Open VSCode
3. Go to Extensions view (`Cmd+Shift+X` or `Ctrl+Shift+X`)
4. Click `...` menu → `Install from VSIX`
5. Select the downloaded file

### From Source

```bash
cd vscode-extension
npm install
npm run build
```

Then press `F5` to launch the extension in a new VSCode window.

## Usage

### Opening the Chat

- Click the Sage icon in the Activity Bar (left sidebar)
- Or press `Cmd+Shift+A` (Mac) / `Ctrl+Shift+A` (Windows/Linux)
- Or use Command Palette: `Sage: Open Chat`

### Explaining Code

1. Select code in your editor
2. Right-click → `Sage: Explain Code`
3. Or press `Cmd+Shift+E` (Mac) / `Ctrl+Shift+E` (Windows/Linux)

The explanation will appear in the chat interface.

### Generating Code

1. Open the chat interface
2. Describe what you want to build
3. Sage will generate code and offer to create files

Example prompts:
- "create a function to validate email addresses"
- "add error handling to the authenticate function"
- "refactor this code to use async/await"

### Refactoring Code

1. Select code in your Python file
2. Right-click → `Sage: Refactor Code`
3. Sage will suggest improvements

### Indexing Your Workspace

Click the **⟳ Index** button in the chat header to index your codebase. This enables semantic search for better context awareness.

## Commands

| Command | Keybinding (Mac) | Keybinding (Win/Linux) | Description |
|---------|------------------|------------------------|-------------|
| `Sage: Open Chat` | `Cmd+Shift+A` | `Ctrl+Shift+A` | Open chat interface |
| `Sage: Explain Code` | `Cmd+Shift+E` | `Ctrl+Shift+E` | Explain selected code |
| `Sage: Generate Code` | - | - | Generate code from prompt |
| `Sage: Refactor Code` | - | - | Suggest code improvements |

## Configuration

Configure Sage in your VSCode settings (`Cmd+,` or `Ctrl+,`):

```json
{
  "sage.model": "qwen2.5-coder:3b",
  "sage.pythonPath": "python3"
}
```

### Settings

- **sage.model**: Ollama model to use (default: `qwen2.5-coder:3b`)
- **sage.pythonPath**: Path to Python executable (default: `python3`)

## How It Works

1. **Indexing**: Your Python codebase is parsed with tree-sitter and embedded using sentence-transformers
2. **Vector Search**: Queries are matched against code using ChromaDB for semantic similarity
3. **Context Assembly**: Relevant code chunks are gathered and sent to the LLM
4. **Generation**: Ollama generates responses with full codebase context
5. **Application**: Code can be directly applied to your workspace

## Troubleshooting

### Extension Not Activating

- Check that Python 3.8+ is installed: `python3 --version`
- Check that Ollama is running: `ollama list`
- Check VSCode Developer Console: `Help` → `Toggle Developer Tools`

### No Models Available

```bash
# Pull a model
ollama pull qwen2.5-coder:3b

# List available models
ollama list
```

### Slow Responses

- Use a smaller model: `qwen2.5-coder:1.5b`
- Ensure Ollama is running locally (not in container)
- Check system resources (RAM, CPU)

### Code Not Being Applied

- Ensure you have a workspace folder open
- Check file permissions
- Try manually creating the file first

## Development

### Building from Source

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (auto-recompile)
npm run watch

# Build production bundle
npm run build
```

### Debugging

1. Open the extension folder in VSCode
2. Press `F5` to launch Extension Development Host
3. Set breakpoints in TypeScript files
4. Reload window to test changes (`Cmd+R` in dev host)

### Testing

```bash
# Lint code
npm run lint

# Package extension
npm run package
```

## Architecture

```
┌─────────────────────────────────────┐
│      VSCode Extension (TypeScript)   │
│  - Chat Webview                     │
│  - Code Actions                     │
│  - Command Handlers                 │
└──────────────┬──────────────────────┘
               │ (spawn child process)
               ▼
┌─────────────────────────────────────┐
│      Sage CLI (Python)              │
│  - Context Management (ChromaDB)    │
│  - Code Parsing (tree-sitter)       │
│  - Model Interface (Ollama)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Ollama (Local LLM)             │
│  - qwen2.5-coder:3b                 │
└─────────────────────────────────────┘
```

## Roadmap

- [ ] Multi-language support (JavaScript, TypeScript, Go, Rust)
- [ ] Inline code completion
- [ ] Git integration (commit message generation)
- [ ] Code review assistant
- [ ] Incremental indexing (watch mode)
- [ ] Model management UI
- [ ] Chat history persistence
- [ ] Export conversations

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Credits

Built with:
- [VSCode Extension API](https://code.visualstudio.com/api)
- [Ollama](https://ollama.ai/) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Text embeddings
- [tree-sitter](https://tree-sitter.github.io/) - Code parsing

---

**Made with ❤️ for Python developers**

[Report Bug](https://github.com/yttrium400/sage/issues) · [Request Feature](https://github.com/yttrium400/sage/issues)
