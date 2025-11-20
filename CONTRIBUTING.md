# Contributing to Sage

Thank you for your interest in contributing to Sage! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/sage/issues)
2. If not, create a new issue using the Bug Report template
3. Provide as much detail as possible (OS, Python version, error messages, etc.)

### Suggesting Features

1. Check if the feature has already been suggested in [Issues](https://github.com/yourusername/sage/issues)
2. If not, create a new issue using the Feature Request template
3. Clearly describe the feature and its use case

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/sage.git
   cd sage
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate
   - Include docstrings for functions and classes

4. **Test your changes**
   ```bash
   cd cli
   python3 run_tests.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write descriptive variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise (< 50 lines when possible)

## Testing

- Add tests for new features
- Ensure existing tests pass
- Run the test suite before submitting PR:
  ```bash
  python3 run_tests.py
  python3 test_context_awareness.py
  ```

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Update relevant docs in the `docs/` folder

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

Thank you for contributing! 🙏
