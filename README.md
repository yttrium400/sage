# Sage - AI Python Coding Assistant

<div align="center">

**Your intelligent Python coding companion with context-aware semantic search**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)](https://ollama.ai/)

</div>

---

## ✨ Features

- 🧠 **Context-Aware**: Uses vector embeddings and semantic search to understand your codebase
- ⚡ **Fast & Local**: Runs locally using Ollama - no API keys, no data leaves your machine
- 🎯 **Smart File Inference**: Automatically detects which files you want to edit from natural language
- 🔍 **Tree-Sitter Parsing**: Function-level code understanding, not just file-level
- 💬 **Interactive Chat**: Streaming responses with syntax highlighting
- 📝 **File Operations**: Create, edit, and modify files with confirmation
- 🎨 **Beautiful UI**: Rich terminal interface with syntax highlighting and themes

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama** (for running models locally)
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Windows
   # Download from https://ollama.com
   ```

2. **Pull a coding model**
   ```bash
   # Recommended: Balanced speed and quality
   ollama pull qwen2.5-coder:3b

   # Alternative options:
   # ollama pull qwen2.5-coder:1.5b  # Faster, lower quality
   # ollama pull deepseek-coder:6.7b # Slower, higher quality
   ```

### Installation

```bash
# Clone the repository
git clone https://github.com/yttrium400/sage.git
cd sage

# Install dependencies
cd cli
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run setup wizard
python3 main.py setup
```

### Usage

```bash
# Start interactive chat
python3 main.py chat

# Ask a single question
python3 main.py ask "how does streaming work?"

# Index your codebase
python3 main.py index

# List available models
python3 main.py models
```

## 💡 Example Queries

### Natural Language File Operations
```
You: create a calculator with add, subtract, multiply, divide
Sage: [Creates calc.py with proper functions]

You: add authentication to the project
Sage: [Creates auth.py with authentication logic]

You: edit model.py to add error handling
Sage: [Finds model.py and adds error handling]
```

### Context-Aware Code Search
```
You: How does streaming work?
Sage: [Finds generate_response_streaming in model.py]

You: Show me all file operations
Sage: [Finds write_file, read_file functions]

You: What files use the model?
Sage: [Identifies chat.py imports model.py]
```

## 🏗️ Architecture

### Technology Stack

- **Vector Search**: ChromaDB + sentence-transformers for semantic code search
- **Code Parsing**: Tree-sitter for AST-based Python parsing
- **LLM Backend**: Ollama for local model inference
- **UI**: Rich library for beautiful terminal output
- **CLI Framework**: Click for command-line interface

### How It Works

1. **Indexing**: Tree-sitter parses your Python files into function/class chunks
2. **Embedding**: Each chunk is converted to a 384-dim vector using sentence-transformers
3. **Storage**: Vectors stored in ChromaDB for fast similarity search
4. **Query**: Your question is embedded and matched against code chunks
5. **Context**: Top-K relevant chunks sent to LLM with your query
6. **Response**: LLM generates answer with full codebase understanding

```
┌─────────────────┐
│   Your Query    │
└────────┬────────┘
         │
         ├──► File Inference (regex patterns)
         │
         ├──► Embedding (sentence-transformers)
         │
         ├──► Vector Search (ChromaDB)
         │
         └──► Context Assembly
              │
              ├──► Top-K Code Chunks
              ├──► Import Dependencies
              └──► File Metadata
                   │
                   ▼
          ┌──────────────────┐
          │  LLM + Context   │
          └──────────────────┘
```

## 📊 Performance

- **Indexing**: ~5 seconds for typical project (7 files, 40 chunks)
- **Query Speed**: <300ms per semantic search
- **Memory**: ~100MB for embedding model + vectors
- **Model Size**: 1.9GB (qwen2.5-coder:3b)

## 🧪 Testing

```bash
# Run automated test suite
python3 run_tests.py

# Run manual tests
python3 test_context_awareness.py

# Quick smoke test (5 minutes)
# See docs/QUICK_TEST_REFERENCE.md
```

**Test Coverage**:
- ✅ Semantic search accuracy: 91.7%
- ✅ File inference: Keyword and explicit path detection
- ✅ Cross-file understanding: Import dependency tracking
- ✅ Multiple file operations

## 📚 Documentation

- [Context Awareness](docs/CONTEXT_AWARENESS.md) - Technical implementation details
- [Testing Guide](docs/TESTING_GUIDE.md) - Comprehensive test scenarios
- [Quick Test Reference](docs/QUICK_TEST_REFERENCE.md) - Fast 5-minute smoke tests
- [Architecture](docs/ARCHITECTURE.md) - System design and components

## 🛠️ Development

### Project Structure

```
sage/
├── cli/
│   ├── main.py           # Entry point (Click commands)
│   ├── chat.py           # Interactive chat interface
│   ├── model.py          # Ollama integration
│   ├── context.py        # Vector search & code parsing
│   ├── file_ops.py       # File read/write/edit operations
│   ├── theme.py          # UI themes and styling
│   ├── run_tests.py      # Automated test runner
│   └── requirements.txt  # Python dependencies
└── docs/                 # Documentation
```

### Key Components

- **context.py**: Core intelligence - semantic search, file inference, tree-sitter parsing
- **chat.py**: User interaction - streaming, syntax highlighting, file proposals
- **model.py**: LLM integration - prompts, streaming, model management
- **file_ops.py**: File operations - smart code extraction, diff preview, confirmation

## 🎯 Roadmap

- [x] Context-aware semantic search
- [x] Smart file inference from natural language
- [x] Tree-sitter AST parsing
- [x] Interactive chat with streaming
- [x] File creation/editing with confirmation
- [ ] Multi-language support (JavaScript, TypeScript, Go)
- [ ] VSCode extension
- [ ] Incremental indexing (watch mode)
- [ ] Custom model fine-tuning for Python

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

**Technologies Used**:
- [Ollama](https://ollama.ai/) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Text embeddings
- [tree-sitter](https://tree-sitter.github.io/) - Code parsing
- [Rich](https://rich.readthedocs.io/) - Terminal UI

---

<div align="center">

**Built with ❤️ for Python developers**

[Report Bug](https://github.com/yourusername/sage/issues) · [Request Feature](https://github.com/yourusername/sage/issues)

</div>
