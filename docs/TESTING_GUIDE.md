# Context Awareness Testing Guide

This guide contains challenging test scenarios to push the new context awareness system to its limits.

## Setup

1. Start the CLI:
```bash
cd cli
source .venv/bin/activate
python3 main.py
```

2. The first query will automatically index your codebase (takes ~5 seconds)

## Test Categories

### 🔥 Level 1: Basic Semantic Understanding

These tests verify the system can find relevant code without explicit file mentions.

#### Test 1.1: Function Discovery
```
Query: "How does streaming work?"
Expected: Should find generate_response_streaming() in model.py
```

#### Test 1.2: UI/Theme Queries
```
Query: "What colors are used in the interface?"
Expected: Should find theme.py and color definitions
```

#### Test 1.3: File Operations
```
Query: "How are files written?"
Expected: Should find write_file() in file_ops.py
```

#### Test 1.4: Error Handling
```
Query: "Show me error handling code"
Expected: Should find try/except blocks across multiple files
```

---

### 🔥🔥 Level 2: Implicit File Inference

These tests check if the system can infer which files to create/modify.

#### Test 2.1: Explicit File Creation
```
Query: "create test_utils.py with helper functions"
Expected: System should infer target file: test_utils.py
```

#### Test 2.2: Keyword-Based Inference
```
Query: "add authentication to the project"
Expected: System should suggest auth.py or authentication.py
```

#### Test 2.3: Multiple File Mentions
```
Query: "edit model.py and theme.py to improve colors"
Expected: System should detect both files: model.py, theme.py
```

#### Test 2.4: Subdirectory Files
```
Query: "create utils/string_helpers.py"
Expected: System should handle subdirectory paths correctly
```

---

### 🔥🔥🔥 Level 3: Cross-File Understanding

These tests verify dependency tracking and relationship understanding.

#### Test 3.1: Import Dependencies
```
Query: "What files does chat.py depend on?"
Expected: Should mention model.py, context.py, file_ops.py, theme.py
```

#### Test 3.2: Function Usage Tracking
```
Query: "Where is generate_response_streaming used?"
Expected: Should find chat.py which imports and uses it
```

#### Test 3.3: Related Code Discovery
```
Query: "Show me all file operation functions"
Expected: Should find write_file, read_file, list_files, etc. in file_ops.py
```

#### Test 3.4: Architecture Understanding
```
Query: "Explain the codebase structure"
Expected: Should identify main modules: chat, model, context, file_ops, theme
```

---

### 🔥🔥🔥🔥 Level 4: Complex Queries

Push the semantic search to handle ambiguous or complex requests.

#### Test 4.1: Multi-Concept Query
```
Query: "How does the system handle user input, process it with the model, and display results?"
Expected: Should find chat.py (input), model.py (processing), theme.py (display)
```

#### Test 4.2: Performance-Related Query
```
Query: "What might be slow in this codebase?"
Expected: Should find embedding generation, file parsing, model inference
```

#### Test 4.3: Refactoring Opportunity
```
Query: "Find duplicate code patterns"
Expected: Should identify similar error handling or file filtering logic
```

#### Test 4.4: Natural Language Intent
```
Query: "I want to make the chat interface more responsive"
Expected: Should find chat.py, specifically the streaming and UI sections
```

---

### 🔥🔥🔥🔥🔥 Level 5: Stress Tests

Break the system or find edge cases.

#### Test 5.1: Non-Existent Concepts
```
Query: "Show me database connection pooling code"
Expected: Should gracefully handle (no DB code exists) or suggest closest match
```

#### Test 5.2: Very Generic Query
```
Query: "code"
Expected: Should return most representative chunks, likely main functions
```

#### Test 5.3: Very Specific Query
```
Query: "find the exact line where spinner style is set to random"
Expected: Should find chat.py:139 - spinner_styles = [...] and random.choice()
```

#### Test 5.4: Multiple Languages (Future)
```
Query: "show me javascript code"
Expected: Currently won't find much (Python-only), but system should handle gracefully
```

#### Test 5.5: Large Result Set
```
Query: "show me all functions"
Expected: Should return top-K (5 by default), not crash with too many results
```

---

## Commands to Test

### `/index` Command
```
/index
```
**Expected:**
- Re-indexes entire codebase
- Shows count of code chunks (should be 30-40 for current project)
- Creates/updates `.code_assistant_db/`

### `/context` Command
```
/context
```
**Expected:**
- Shows current context directory
- Displays path being indexed

---

## File Creation Tests

These test the end-to-end flow: query → semantic search → code generation → file proposal.

### Test F.1: Simple Calculator
```
Query: "create a calculator with add, subtract, multiply, divide"
Expected:
1. System finds relevant context (if any math operations exist)
2. Model generates code
3. Proposes file: ```python:calc.py
4. Asks for confirmation
5. Creates calc.py on approval
```

### Test F.2: Utility Functions
```
Query: "create string helpers for uppercase, lowercase, and reverse"
Expected:
- Proposes utils.py or helpers.py
- Generates clean functions with type hints
```

### Test F.3: Edit Existing File
```
Query: "add a new color scheme to theme.py"
Expected:
1. System retrieves theme.py content
2. Model generates additional color definitions
3. Shows diff preview
4. Applies changes on confirmation
```

### Test F.4: Complex Refactoring
```
Query: "extract the file filtering logic from context.py into a separate function"
Expected:
1. System finds ignore_patterns logic in context.py
2. Model creates new function
3. Proposes changes with diff
```

---

## Performance Benchmarks

### Indexing Performance
```bash
# Time the indexing process
time python3 -c "from context import index_codebase; index_codebase('.')"
```
**Target:** <5 seconds for ~7 files

### Query Performance
```bash
# Test query speed
time python3 -c "from context import get_relevant_context; print(len(get_relevant_context('streaming', '.')))"
```
**Target:** <500ms per query

### Embedding Model Load Time
```bash
# First load (cold start)
time python3 -c "from context import get_embedding_model; get_embedding_model()"
```
**Target:** <2 seconds

---

## Edge Cases to Test

### Edge Case 1: Empty Query
```
Query: ""
Expected: Should handle gracefully, maybe show help or do nothing
```

### Edge Case 2: Query with Special Characters
```
Query: "How does the ```code``` work?"
Expected: Should handle backticks and markdown syntax
```

### Edge Case 3: Very Long Query
```
Query: "Can you explain in great detail with lots of context about how the entire system works from start to finish including all the components and their interactions?"
Expected: Should handle long input, truncate if needed
```

### Edge Case 4: Code Snippet in Query
```
Query: "Why does this code fail: def add(a, b) return a + b"
Expected: Should understand the Python syntax in the query
```

### Edge Case 5: Multiple File Extensions
```
Query: "create config.json with settings"
Expected: Should handle .json extension (though indexing is Python-only)
```

---

## Verification Checklist

After running tests, verify:

- [ ] **Accuracy**: Does it find the RIGHT code for each query?
- [ ] **Speed**: Are queries returning in <500ms?
- [ ] **Relevance**: Are top results actually relevant?
- [ ] **Ranking**: Are the most relevant chunks ranked first?
- [ ] **File Inference**: Does it correctly detect file names from queries?
- [ ] **Error Handling**: Does it fail gracefully on bad input?
- [ ] **Memory Usage**: Does it stay under 500MB RAM?
- [ ] **Persistence**: Does `.code_assistant_db/` persist between sessions?
- [ ] **Incremental**: Does re-indexing work without errors?

---

## Advanced Testing

### Test with Your Own Codebase

1. Create a test directory with diverse Python files:
```bash
mkdir ~/test_codebase
cd ~/test_codebase

# Create some test files
echo "def process_data(data): return data.upper()" > processor.py
echo "class Database: pass" > database.py
echo "API_KEY = 'secret'" > config.py
```

2. Run assistant on that directory:
```bash
cd ~/test_codebase
python3 /path/to/cli/main.py
```

3. Test queries specific to your test files

### Measure Semantic Accuracy

Create a "ground truth" dataset:

```python
test_cases = [
    {
        "query": "streaming response",
        "expected_function": "generate_response_streaming",
        "expected_file": "model.py"
    },
    {
        "query": "file writing",
        "expected_function": "write_file",
        "expected_file": "file_ops.py"
    },
    # Add more...
]
```

Check if top result matches expected.

---

## Troubleshooting

### If queries are slow:
1. Check if embedding model is cached (should load once)
2. Verify ChromaDB collection exists (`.code_assistant_db/`)
3. Try `/index` to rebuild index

### If results are irrelevant:
1. Try more specific queries
2. Check if codebase was indexed properly
3. Verify files aren't in ignore patterns

### If indexing fails:
1. Check disk space (needs ~10-50MB)
2. Verify write permissions in directory
3. Check for syntax errors in Python files (tree-sitter might fail)

### If embeddings are wrong:
1. Delete `.code_assistant_db/` and re-index
2. Check internet connection (first model download needs it)
3. Verify sentence-transformers version: `pip show sentence-transformers`

---

## Metrics to Record

For each test, record:

1. **Query**: The exact query text
2. **Top Result**: The first function/file returned
3. **Relevant?**: Yes/No - was it actually relevant?
4. **Response Time**: How long did it take?
5. **Ranking**: Was the best result in top-3, top-5, or lower?

Example log:
```
Query: "streaming response"
Top Result: generate_response_streaming (model.py:85)
Relevant: YES ✓
Time: 234ms
Ranking: #1 (perfect)
```

---

## Comparison Test (Optional)

To see the improvement, you can temporarily disable semantic search:

1. In [context.py](../cli/context.py:221), modify `get_relevant_context()` to always call `get_simple_context()`
2. Run same queries
3. Compare results (old method returns recent files, new method returns relevant chunks)

---

## Report Template

After testing, create a report:

```markdown
# Context Awareness Test Report

## Test Environment
- Date: [DATE]
- Model: [Qwen 2.5 Coder 1.5B]
- Files Indexed: [COUNT]
- Chunks Created: [COUNT]

## Results Summary
- Total Tests: [X]
- Passed: [Y]
- Failed: [Z]
- Accuracy: [Y/X * 100]%

## Notable Findings
- [What worked well]
- [What needs improvement]
- [Edge cases discovered]

## Performance
- Average Query Time: [X]ms
- Indexing Time: [Y]s
- Memory Usage: [Z]MB
```

---

## Quick Smoke Test

If you just want a quick verification, run these 5 queries:

1. `"How does streaming work?"` → Should find model.py
2. `"create calc.py with add function"` → Should detect calc.py
3. `"What files use the model?"` → Should mention chat.py
4. `"Show me UI code"` → Should find theme.py, chat.py
5. `"/index"` → Should re-index successfully

If all 5 work, the system is functional! 🎉

---

## Next Steps

After testing, consider:

1. **Fine-tuning**: Adjust `max_chunks` parameter if results are too broad/narrow
2. **Weights**: Add recency weighting (prefer recently modified files)
3. **Multi-language**: Extend to JavaScript, TypeScript, etc.
4. **Caching**: Cache query embeddings for repeated queries
5. **Analytics**: Track which queries perform poorly

Happy testing! 🚀
