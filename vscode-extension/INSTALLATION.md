# Installation Guide - Sage Code Assistant

This guide will help you install and set up the Sage Code Assistant VSCode extension.

## Prerequisites

### 1. Python 3.8+

Check if Python is installed:
```bash
python3 --version
```

If not installed:
- **macOS**: `brew install python3`
- **Linux**: `sudo apt install python3` (Debian/Ubuntu) or `sudo dnf install python3` (Fedora)
- **Windows**: Download from [python.org](https://python.org)

### 2. Ollama

Ollama is required for local LLM inference.

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows
Download the installer from [ollama.ai](https://ollama.ai)

### 3. Pull a Model

After installing Ollama, pull a coding model:

```bash
# Recommended (3B parameters, good balance)
ollama pull qwen2.5-coder:3b

# Alternatives:
ollama pull qwen2.5-coder:1.5b  # Faster, less capable
ollama pull deepseek-coder:6.7b # Slower, more capable
```

Verify the model is available:
```bash
ollama list
```

## Installation Methods

### Method 1: Install from VSIX (Easiest)

1. **Build the extension** (if not already built):
   ```bash
   cd vscode-extension
   npm install
   npm run build
   npm run package
   ```

   This creates a `.vsix` file.

2. **Install in VSCode**:
   - Open VSCode
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Install from VSIX"
   - Select the `.vsix` file from `vscode-extension/`

3. **Reload VSCode**:
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type "Reload Window"

### Method 2: Development Mode

For testing and development:

1. **Install dependencies**:
   ```bash
   cd vscode-extension
   npm install
   ```

2. **Open in VSCode**:
   ```bash
   code .
   ```

3. **Start watching** (auto-recompile on changes):
   ```bash
   npm run watch
   ```

4. **Launch Extension Development Host**:
   - Press `F5` in VSCode
   - A new window will open with the extension loaded

## Post-Installation Setup

### 1. Verify Installation

After installation, you should see:
- A Sage icon (✨) in the Activity Bar (left sidebar)
- Status bar item on the right: "$(comment-discussion) Sage"

### 2. Index Your Workspace

1. Open a Python project in VSCode
2. Click the Sage icon in the Activity Bar
3. Click the **⟳ Index** button in the chat header
4. Wait for indexing to complete (~5 seconds for typical project)

### 3. Test the Extension

Try these commands:

#### Open Chat
- Press `Cmd+Shift+A` (Mac) / `Ctrl+Shift+A` (Windows/Linux)
- Or click the Sage icon in the Activity Bar

#### Explain Code
1. Select some Python code
2. Right-click → "Sage: Explain Code"
3. Or press `Cmd+Shift+E` / `Ctrl+Shift+E`

#### Generate Code
1. Open the chat
2. Type: "create a function to validate email addresses"
3. Press Send

## Configuration

Open VSCode Settings (`Cmd+,` or `Ctrl+,`) and search for "Sage":

### Model Selection
```json
{
  "sage.model": "qwen2.5-coder:3b"
}
```

Available models (must be pulled via Ollama first):
- `qwen2.5-coder:1.5b` - Fast, 1.5B parameters
- `qwen2.5-coder:3b` - Balanced (recommended)
- `deepseek-coder:6.7b` - High quality, slower

### Python Path
```json
{
  "sage.pythonPath": "python3"
}
```

If Python is installed in a custom location:
```json
{
  "sage.pythonPath": "/usr/local/bin/python3.11"
}
```

## Troubleshooting

### Extension Not Loading

**Symptom**: No Sage icon in Activity Bar

**Solution**:
1. Check VSCode version: `Help` → `About`
   - Requires VSCode 1.80.0 or higher
2. Reload window: `Cmd+Shift+P` → "Reload Window"
3. Check Developer Console: `Help` → `Toggle Developer Tools`
   - Look for errors in the Console tab

### Python Not Found

**Symptom**: Extension shows "Python 3 not found"

**Solution**:
1. Verify Python is installed: `python3 --version`
2. Set custom Python path in settings:
   ```json
   {
     "sage.pythonPath": "/path/to/python3"
   }
   ```

### Ollama Not Running

**Symptom**: Extension shows "Ollama not found"

**Solution**:
1. Check if Ollama is installed: `ollama --version`
2. Check if Ollama service is running:
   ```bash
   ollama list
   ```
3. Restart Ollama:
   - **macOS/Linux**: `killall ollama && ollama serve`
   - **Windows**: Restart the Ollama service

### No Models Available

**Symptom**: Chat shows "No model found"

**Solution**:
1. Pull a model:
   ```bash
   ollama pull qwen2.5-coder:3b
   ```
2. Verify it's available:
   ```bash
   ollama list
   ```
3. Reload VSCode window

### Slow Responses

**Symptom**: Chat takes >10 seconds to respond

**Solutions**:
1. **Use smaller model**: Switch to `qwen2.5-coder:1.5b`
2. **Check system resources**:
   - Ensure Ollama has enough RAM (4GB+ recommended)
   - Close other applications
3. **Optimize Ollama**:
   ```bash
   # macOS/Linux: Set environment variable for GPU
   export OLLAMA_NUM_GPU=1
   ```

### Indexing Fails

**Symptom**: "Indexing failed" error

**Solutions**:
1. **Check workspace permissions**: Ensure VSCode can write to workspace
2. **Clear cache**:
   ```bash
   rm -rf .code_assistant_db/
   ```
3. **Check Python dependencies**:
   ```bash
   cd ../cli
   pip install -r requirements.txt
   ```

### Code Not Being Applied

**Symptom**: Click "Apply" but file not created

**Solutions**:
1. Ensure a workspace folder is open: `File` → `Open Folder`
2. Check file permissions in workspace
3. Try manually creating the file first
4. Check for errors in Developer Console

## Uninstallation

### Remove Extension

1. Open Extensions view: `Cmd+Shift+X` / `Ctrl+Shift+X`
2. Find "Sage Code Assistant"
3. Click gear icon → "Uninstall"
4. Reload window

### Clean Up Data

The extension creates a `.code_assistant_db` folder in your workspace for indexing. To remove:

```bash
# In your workspace root
rm -rf .code_assistant_db/
```

## Getting Help

If you encounter issues:

1. **Check logs**:
   - Open Developer Console: `Help` → `Toggle Developer Tools`
   - Check Console tab for errors

2. **Report issues**:
   - [GitHub Issues](https://github.com/yttrium400/sage/issues)
   - Include:
     - VSCode version
     - Extension version
     - Operating system
     - Error messages from Console

3. **Community support**:
   - Check existing issues
   - Search documentation

## Next Steps

Once installed and working:

1. **Index your workspace** (⟳ Index button)
2. **Try example queries** (see README.md)
3. **Customize keybindings** (VSCode Preferences)
4. **Adjust settings** (model selection, etc.)

Happy coding with Sage! 🧙‍♂️
