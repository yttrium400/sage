# Quick Test Reference Card

Fast reference for testing context awareness manually.

## 🚀 Quick Start

```bash
cd cli
source .venv/bin/activate
python3 main.py
```

## ✅ 5-Minute Smoke Test

Run these queries in order:

### 1. Semantic Search Test
```
Query: How does streaming work?
✓ Expected: Should mention generate_response_streaming in model.py
```

### 2. File Inference Test
```
Query: create calc.py with basic math functions
✓ Expected: Should detect "calc.py" as target file
```

### 3. Cross-File Test
```
Query: What files does chat.py import?
✓ Expected: Should mention model, context, file_ops, theme
```

### 4. Complex Query Test
```
Query: Show me how user input is processed and sent to the model
✓ Expected: Should find chat.py and model.py functions
```

### 5. Command Test
```
Query: /index
✓ Expected: Should re-index codebase successfully
```

**If all 5 pass → System is working! 🎉**

---

## 🔥 Stress Tests (Push to Limits)

### Very Vague Query
```
Query: code
Expected: Should return something (most representative chunks)
```

### Very Specific Query
```
Query: Find where spinner style is randomly chosen
Expected: Should find chat.py line ~139-142
```

### Non-Existent Concept
```
Query: Show me Rust code
Expected: Should handle gracefully (no Rust in project)
```

### Multi-Step Reasoning
```
Query: What happens when a user sends a message?
Expected: Should trace: chat.py input → context.py retrieval → model.py generation
```

### File Creation with Intent
```
Query: I need utilities for string manipulation
Expected: Should propose utils.py or helpers.py
```

---

## ⚡ Performance Checks

### Query Speed
```
Target: <500ms per query
Measure: Time between pressing Enter and seeing results
```

### Indexing Speed
```
Target: <10s for typical project
Command: /index
```

### Memory Usage
```
Target: <500MB RAM
Check: Activity Monitor (Mac) or Task Manager (Windows)
```

---

## 🎯 Accuracy Tests

For each query, check:

1. **Top Result**: Is the first returned chunk relevant?
2. **Ranking**: Is the most relevant result in top-3?
3. **Completeness**: Does it include all necessary context?

### High-Accuracy Queries (Should be 100%)
- "How does streaming work?" → `generate_response_streaming`
- "File writing code" → `write_file`
- "create test.py" → Detects `test.py`

### Medium-Accuracy Queries (Should find something relevant)
- "UI code" → theme.py or chat.py
- "Error handling" → Try/except blocks
- "Code structure" → Multiple files

### Low-Accuracy Expected (Acceptable if imperfect)
- Very vague queries like "code"
- Queries about non-existent features
- Ambiguous intent

---

## 📊 Automated Testing

### Run Full Test Suite
```bash
python3 run_tests.py
```

**Target Score:** >80% accuracy

### Run Specific Module Tests
```bash
python3 test_context_awareness.py
```

---

## 🐛 Debugging Guide

### Problem: Slow queries (>1 second)

**Check:**
```bash
# Delete and rebuild index
rm -rf .code_assistant_db/
# Then run: /index
```

### Problem: Irrelevant results

**Try:**
- More specific query wording
- Mention explicit keywords
- Check if files were indexed: `/index`

### Problem: Files not detected

**Check:**
```bash
# View indexed files
python3 -c "from context import index_codebase; c = index_codebase('.'); print(f'{c.count()} chunks')"
```

### Problem: Index failed

**Solution:**
```bash
# Clear database and retry
rm -rf .code_assistant_db/
python3 main.py  # Will auto-index on first query
```

---

## 📈 Benchmark Your System

Record these metrics:

```
Date: [TODAY]
Model: Qwen 2.5 Coder 1.5B
Test Duration: [X] minutes

Results:
- Indexed chunks: [Y]
- Average query time: [Z]ms
- Accuracy (5 tests): [A]/5 = [B]%

Notes:
[Any observations or issues]
```

---

## 🎨 Example Test Session

```
You: How does streaming work?
Assistant: [Shows generate_response_streaming from model.py]
✓ PASS - Found correct function

You: create calc.py with add and multiply
Assistant: [Generates code, proposes calc.py]
✓ PASS - Detected file correctly

You: What depends on model.py?
Assistant: [Shows chat.py imports]
✓ PASS - Found dependency

You: /index
System: ✓ Indexed 41 code chunks with semantic search
✓ PASS - Re-indexing works

SCORE: 4/4 (100%) ✓
```

---

## 🔍 Advanced Verification

### Check Vector Embeddings
```python
from context import get_embedding_model
model = get_embedding_model()
embedding = model.encode(["test query"])
print(f"Embedding shape: {embedding[0].shape}")  # Should be (384,)
```

### Check ChromaDB Collection
```python
from context import get_chroma_client
client = get_chroma_client('.')
collection = client.get_collection('codebase')
print(f"Total chunks: {collection.count()}")
print(f"Metadata sample: {collection.peek()}")
```

### Check Tree-sitter Parsing
```python
from context import parse_file_with_treesitter
chunks = parse_file_with_treesitter('model.py')
for c in chunks:
    print(f"{c.chunk_type}: {c.name}")
```

---

## 🎓 Interpretation Guide

### Good Results Look Like:
- Top result contains the exact function you're looking for
- Response time <300ms for most queries
- File inference correctly identifies explicit mentions
- Handles edge cases without crashing

### Warning Signs:
- Consistently irrelevant results (may need re-index)
- Queries taking >1 second (embedding model not cached?)
- Missing obvious files (check ignore patterns)
- Crashes on specific queries (syntax errors in files?)

---

## 💡 Pro Tips

1. **First query is slow** - That's normal (loading embedding model)
2. **Use /index after adding files** - New files need indexing
3. **Be specific** - "streaming response generation" > "code"
4. **Check context dir** - Use `/context` to verify working directory
5. **Clear cache if broken** - Delete `.code_assistant_db/` to reset

---

## ✨ What Success Looks Like

After testing, you should be able to:

- [x] Ask "How does X work?" without mentioning file names
- [x] Create files by saying "create calculator" (no explicit path needed)
- [x] Get function-level precision (not whole files)
- [x] Understand relationships ("what imports X?")
- [x] Handle vague queries gracefully (no crashes)

**If you can check all boxes → System is production-ready! 🚀**

---

## 📞 Need Help?

If tests consistently fail:

1. Check [CONTEXT_AWARENESS.md](CONTEXT_AWARENESS.md) for architecture details
2. Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive scenarios
3. Verify dependencies: `pip list | grep -E "(chroma|sentence|tree-sitter)"`
4. Check Python version: `python3 --version` (need 3.8+)

---

*Happy testing! 🎉*
