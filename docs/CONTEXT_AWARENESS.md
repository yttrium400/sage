# Context Awareness - Technical Implementation

## Overview

The Code Assistant now features **advanced context awareness** using vector embeddings, semantic search, and intelligent file inference. You no longer need to explicitly mention files in your queries - the system automatically finds relevant code.

## Key Features Implemented

### 1. Vector Search with ChromaDB

**Technology Stack:**
- ChromaDB for persistent vector storage
- sentence-transformers (all-MiniLM-L6-v2) for embeddings
- Cosine similarity for semantic matching

**How it works:**
```
User Query → Embedding Model → Query Vector → ChromaDB Search → Top-K Results
```

The system converts code and queries into 384-dimensional vectors, enabling semantic similarity matching.

### 2. Tree-sitter Code Parsing

**Structured Code Analysis:**
- Parses Python files into AST (Abstract Syntax Tree)
- Extracts functions, classes, docstrings separately
- Preserves line numbers and structure metadata
- Tracks import relationships

**Benefits:**
- More precise context retrieval (function-level, not file-level)
- Understands code structure, not just text
- Can return specific functions relevant to query

### 3. Smart File Inference

**Pattern-based Detection:**

The system infers target files from natural language:

| Query Pattern | Inferred Files |
|--------------|---------------|
| "create calc.py" | calc.py (explicit) |
| "edit model.py" | model.py (explicit) |
| "add authentication" | auth.py, authentication.py (heuristic) |
| "update config" | config.py, settings.py (heuristic) |

**Example:**
```python
# Query: "add error handling to response generation"
# → Automatically finds: model.py (generate_response function)
# → No need to mention "model.py" explicitly!
```

### 4. File Dependency Graph

**Import Relationship Mapping:**
- Analyzes all `import` and `from ... import` statements
- Builds directed graph of file dependencies
- Helps understand which files are related

**Use case:**
When modifying a function, the system knows which other files import it.

### 5. Persistent Vector Index

**Database Location:**
```
.code_assistant_db/
```

**Automatic Indexing:**
- First query automatically triggers indexing
- Re-index manually with `/index` command
- Stores embeddings locally (no API calls needed)

## Usage Examples

### Before (Without Context Awareness)

```
You: "Edit model.py and add error handling to generate_response"
```
→ User must specify file explicitly

### After (With Context Awareness)

```
You: "Add error handling to response generation"
```
→ System automatically finds `generate_response` in model.py
→ Semantic search identifies the right function
→ No file names needed!

## Technical Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Query                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ├─► File Inference (regex patterns)
                   │
                   ├─► Query Embedding (sentence-transformers)
                   │
                   ├─► Vector Search (ChromaDB)
                   │
                   └─► Context Assembly
                       │
                       ├─► Top-K Functions/Classes
                       ├─► Import Dependencies
                       └─► File Metadata
                           │
                           ▼
                   ┌──────────────────┐
                   │  LLM with Context│
                   └──────────────────┘
```

## Performance Metrics

**Indexing Speed:**
- ~39 code chunks from 7 files in <5 seconds
- One-time operation (cached after first run)

**Query Speed:**
- Semantic search: ~100-200ms
- Embedding generation: ~50ms
- Total context retrieval: <300ms

**Memory Usage:**
- Embedding model: ~100MB RAM
- ChromaDB: ~10MB on disk per 1000 chunks

## Commands

### `/index` - Re-index Codebase
```
/index
```
Scans all Python files, parses with tree-sitter, generates embeddings, stores in ChromaDB.

### Context Retrieval (Automatic)
Every query automatically retrieves relevant context using vector search.

## Code Changes

### Files Modified:
- [context.py](../cli/context.py) - Complete rewrite with vector search
- [chat.py](../cli/chat.py) - Updated `/index` command

### New Functions:

#### `get_relevant_context(query, context_dir, max_chunks=5)`
Main entry point for context retrieval using semantic search.

#### `index_codebase(context_dir)`
Indexes entire codebase with vector embeddings.

#### `infer_target_files(query, context_dir)`
Extracts file paths from queries using pattern matching.

#### `parse_file_with_treesitter(file_path)`
Parses Python files into structured chunks (functions, classes).

#### `build_file_dependency_graph(context_dir)`
Maps import relationships between files.

## Testing

Run the test suite:
```bash
cd cli
source .venv/bin/activate
python3 test_context_awareness.py
```

Tests cover:
1. ✓ Codebase indexing with vector embeddings
2. ✓ Semantic search across code chunks
3. ✓ File path inference from natural language
4. ✓ Dependency graph construction
5. ✓ End-to-end context retrieval

## Future Enhancements

**Potential Improvements:**
1. Multi-language support (JavaScript, TypeScript, Go, etc.)
2. Incremental indexing (only re-index changed files)
3. Weighted search (prioritize recently modified files)
4. Cross-file refactoring detection
5. Automatic documentation generation from code structure

## Comparison: Before vs After

| Feature | Before | After |
|---------|--------|-------|
| Context Method | Most recent files | Semantic search |
| File Selection | Manual | Automatic inference |
| Code Granularity | Whole files | Functions/classes |
| Query Understanding | Keywords only | Semantic meaning |
| Import Tracking | None | Full dependency graph |
| Indexing | None | Vector embeddings |

## Impact

**Developer Experience:**
- ✅ More natural queries (no file names needed)
- ✅ Faster context retrieval
- ✅ Better understanding of codebase structure
- ✅ Smarter file suggestions

**Code Quality:**
- ✅ More accurate context → better LLM responses
- ✅ Understands relationships between files
- ✅ Can suggest relevant code even if not explicitly mentioned

## Credits

**Technologies Used:**
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Text embeddings
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Code parsing
- [Ollama](https://ollama.ai/) - Local LLM inference
