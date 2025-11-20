# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────┐
│   Custom Fine-tuned Python Model        │
│   (CodeLlama/DeepSeek-Coder base)       │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐    ┌────▼──────────┐
    │ CLI Tool │    │ VSCode Extension│
    └──────────┘    └────────────────┘
         │                │
         └────────┬───────┘
                  │
         ┌────────▼─────────┐
         │  Core Engine     │
         │  - Context Mgmt  │
         │  - Model Inference│
         │  - File Ops      │
         └──────────────────┘
```

## Components

### 1. Core Engine (Python)
**Location**: `/cli/core/`

**Responsibilities**:
- Model inference (llama.cpp, vllm, or Ollama)
- Context management (codebase indexing, RAG)
- File operations (read, edit, search)
- Code parsing (tree-sitter)

**Key modules**:
- `model.py` - Model loading and inference
- `context.py` - Codebase context retrieval
- `files.py` - File operations
- `parser.py` - Code parsing and analysis

### 2. CLI Tool
**Location**: `/cli/`

**Tech Stack**:
- `rich` - Terminal UI
- `prompt_toolkit` - Interactive prompts
- `click` - CLI framework

**Features**:
- Interactive chat
- File editing
- Codebase search
- Multi-turn conversations

### 3. VSCode Extension
**Location**: `/extension/`

**Tech Stack**:
- TypeScript
- VSCode Extension API
- Communication via stdio/HTTP

**Features**:
- Sidebar chat
- Inline editing (Cmd+K)
- Autocomplete
- Code actions

### 4. Model Training Pipeline
**Location**: `/models/`

**Tech Stack**:
- Axolotl or Unsloth for training
- Hugging Face transformers
- PEFT (LoRA/QLoRA)

**Components**:
- Data collection scripts
- Training configs
- Evaluation harness
- Quantization tools

## Data Flow

### Chat Request Flow
```
User Input → CLI/Extension → Core Engine → Context Retrieval → Model → Response → User
```

### Context Retrieval
```
Query → Vector Search (ChromaDB) → Top-K Files → Tree-sitter Parse → Relevant Code → Context
```

## Model Integration Options

### Phase 1: Existing Models
- Use Ollama (easiest)
- Or vLLM (faster)
- Or llama.cpp (most portable)

Models: DeepSeek-Coder, CodeLlama

### Phase 2: Custom Model
- Fine-tuned on Python
- Quantized to GGUF
- Deployed via llama.cpp

## Technology Decisions

| Component | Technology | Why |
|-----------|-----------|-----|
| CLI Framework | Click + Rich | Best Python CLI experience |
| Model Inference | Ollama → llama.cpp | Easy start → Production ready |
| Context Store | ChromaDB | Simple, fast, embeddable |
| Code Parser | tree-sitter | Fast, accurate, language-agnostic |
| VSCode Comm | stdio pipes | Simple, reliable |
| Training | Unsloth | 2x faster, less memory |

## Deployment Architecture

### Development
- Local model via Ollama
- CLI runs directly
- Extension in debug mode

### Production
- Quantized GGUF model
- CLI as pip package
- Extension on VSCode marketplace
- Optional: API server for remote inference

## Security Considerations

- No code sent to external APIs (privacy)
- Local inference only
- User controls all data
- Open source for transparency