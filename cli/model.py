"""
Model interaction and inference
"""

from typing import List, Dict, Optional
import subprocess
import ollama


def list_available_models() -> List[str]:
    """List available Ollama models"""
    try:
        models_list = ollama.list()
        return [model['name'] for model in models_list.get('models', [])]
    except Exception:
        # Fallback to subprocess
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True,
            )
            lines = result.stdout.strip().split("\n")[1:]
            models = [line.split()[0] for line in lines if line.strip()]
            return models
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []


def generate_response(
    query: str,
    context: str,
    model: str,
    history: List[Dict[str, str]],
) -> str:
    """Generate a response using Ollama"""

    # Build the full prompt with system instructions and context
    prompt_parts = []

    # System instructions for better code quality
    prompt_parts.append("""You are an expert Python coding assistant. Follow these guidelines:

1. Write clean, idiomatic Python code
2. Use type hints for function parameters and return values
3. Include docstrings for functions and classes
4. Follow PEP 8 style guidelines
5. Use meaningful variable names
6. Add error handling where appropriate
7. Keep functions focused and concise

CODE BLOCK FORMAT - Use this EXACT format (no deviations):

```python:filename.py
def example():
    pass
```

For multiple files:

```python:file1.py
code here
```

```python:utils/file2.py
code here
```

CRITICAL RULES:
- First line: ```python:filename (backticks, python, colon, filename - NO spaces, NO comments)
- Last line: ``` (just backticks)
- PRESERVE paths: utils/helper.py stays utils/helper.py (not just helper.py)
- Use EXACT filename from "Inferred target files" if shown in context
- Multiple files = multiple SEPARATE code blocks
- NO explanatory text between ``` and code
- NO numbered lines, NO function headers like "# Function: ..."

""")

    if context:
        prompt_parts.append("Relevant code from the codebase:\n")
        prompt_parts.append(f"```python\n{context}\n```\n\n")

    prompt_parts.append(f"User request: {query}")

    full_prompt = "\n".join(prompt_parts)

    # Call Ollama using Python library (much faster!)
    try:
        response = ollama.generate(
            model=model,
            prompt=full_prompt,
        )

        return response['response']

    except Exception as e:
        return f"Error calling model: {str(e)}"


def generate_response_streaming(
    query: str,
    context: str,
    model: str,
    history: List[Dict[str, str]],
):
    """Generate a streaming response (yields tokens as they come)"""

    # Build the full prompt with system instructions and context
    prompt_parts = []

    # System instructions for better code quality
    prompt_parts.append("""You are an expert Python coding assistant. Follow these guidelines:

1. Write clean, idiomatic Python code
2. Use type hints for function parameters and return values
3. Include docstrings for functions and classes
4. Follow PEP 8 style guidelines
5. Use meaningful variable names
6. Add error handling where appropriate
7. Keep functions focused and concise

CODE BLOCK FORMAT - Use this EXACT format (no deviations):

```python:filename.py
def example():
    pass
```

For multiple files:

```python:file1.py
code here
```

```python:utils/file2.py
code here
```

CRITICAL RULES:
- First line: ```python:filename (backticks, python, colon, filename - NO spaces, NO comments)
- Last line: ``` (just backticks)
- PRESERVE paths: utils/helper.py stays utils/helper.py (not just helper.py)
- Use EXACT filename from "Inferred target files" if shown in context
- Multiple files = multiple SEPARATE code blocks
- NO explanatory text between ``` and code
- NO numbered lines, NO function headers like "# Function: ..."

""")

    if context:
        prompt_parts.append("Relevant code from the codebase:\n")
        prompt_parts.append(f"```python\n{context}\n```\n\n")

    prompt_parts.append(f"User request: {query}")

    full_prompt = "\n".join(prompt_parts)

    # Stream from Ollama using Python library
    try:
        stream = ollama.generate(
            model=model,
            prompt=full_prompt,
            stream=True,
        )

        for chunk in stream:
            if 'response' in chunk:
                yield chunk['response']

    except Exception as e:
        yield f"Error: {str(e)}"


def check_ollama_running() -> bool:
    """Check if Ollama is running"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
