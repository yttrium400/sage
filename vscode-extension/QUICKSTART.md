# Quick Start Guide - Sage VSCode Extension

Get up and running with Sage in 5 minutes!

## ⚡ Fast Track Installation

### 1. Prerequisites (2 minutes)

```bash
# Check Python (need 3.8+)
python3 --version

# Install Ollama
brew install ollama  # macOS
# OR
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull model
ollama pull qwen2.5-coder:3b
```

### 2. Install Extension (1 minute)

```bash
cd vscode-extension
npm install
npm run build
npm run package
```

Then in VSCode:
- Press `Cmd+Shift+P` → "Install from VSIX"
- Select the `.vsix` file
- Reload window

### 3. First Run (2 minutes)

1. **Open the chat**: Press `Cmd+Shift+A`
2. **Index workspace**: Click "⟳ Index" button
3. **Ask a question**: Try "explain this codebase"

## 🎯 Key Features to Try

### 1. Explain Code (30 seconds)
```
1. Select any Python code
2. Right-click → "Sage: Explain Code"
3. Or press Cmd+Shift+E
```

### 2. Generate Code (1 minute)
```
1. Open chat (Cmd+Shift+A)
2. Type: "create a function to parse JSON safely"
3. Click "Apply" to add to workspace
```

### 3. Refactor Code (1 minute)
```
1. Select a Python function
2. Right-click → "Sage: Refactor Code"
3. Review suggestions in chat
```

### 4. Ask About Your Code (30 seconds)
```
Questions to try:
- "How does authentication work?"
- "What files handle database queries?"
- "Show me error handling code"
```

## 🔥 Power User Tips

### Keyboard Shortcuts
- `Cmd+Shift+A` - Open chat
- `Cmd+Shift+E` - Explain selected code

### Chat Commands
- Type naturally - no special syntax needed
- Ask follow-up questions - context is preserved
- Click "⟳ Index" after adding new files
- Click "✕ Clear" to start fresh conversation

### Best Practices
1. **Index before asking** - Better context = Better answers
2. **Be specific** - "refactor the login function" > "improve this"
3. **Select relevant code** - For explanations, select the exact code
4. **Review before applying** - Always check generated code

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No Sage icon | Reload window (`Cmd+Shift+P` → Reload) |
| Python not found | Set path in settings: `sage.pythonPath` |
| Ollama error | Run: `ollama list` to verify models |
| Slow responses | Use smaller model: `qwen2.5-coder:1.5b` |
| Index fails | Delete `.code_assistant_db/` and retry |

## 📚 Example Workflow

### Building a New Feature

```
1. You: "create a user authentication module"
   → Sage generates auth.py

2. You: "add password hashing to the authenticate function"
   → Sage adds bcrypt hashing

3. Select the code → Cmd+Shift+E
   → Sage explains how it works

4. You: "add unit tests for this"
   → Sage generates test_auth.py
```

### Refactoring Existing Code

```
1. Select old code
2. You: "refactor this to use async/await"
   → Sage shows modern version

3. You: "add error handling"
   → Sage adds try/except blocks

4. You: "add type hints"
   → Sage adds typing annotations
```

### Understanding Unfamiliar Code

```
1. Click "⟳ Index" to scan codebase
2. You: "explain the authentication flow"
   → Sage finds and explains relevant code

3. You: "what files depend on auth.py?"
   → Sage shows dependency graph

4. Select complex function → Cmd+Shift+E
   → Sage breaks down the logic
```

## ⚙️ Configuration (Optional)

Open VSCode Settings (`Cmd+,`):

```json
{
  // Use faster model
  "sage.model": "qwen2.5-coder:1.5b",

  // Custom Python path
  "sage.pythonPath": "/usr/local/bin/python3",
}
```

## 🎓 Learning Resources

- **README.md** - Full feature documentation
- **INSTALLATION.md** - Detailed setup guide
- **CHANGELOG.md** - What's new
- **Issues** - Report bugs or request features

## 🚀 Next Steps

Once comfortable with basics:

1. Try multi-file operations
2. Experiment with different models
3. Customize keybindings
4. Integrate into your workflow
5. Share feedback!

---

**Questions?** Open an issue on [GitHub](https://github.com/yttrium400/sage/issues)

**Happy coding!** 🧙‍♂️
