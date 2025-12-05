# Changelog

All notable changes to the Sage Code Assistant VSCode extension will be documented in this file.

## [0.1.0] - 2024-11-21

### Added
- Initial release of Sage Code Assistant for VSCode
- Interactive chat interface with streaming responses
- Semantic code search using ChromaDB and vector embeddings
- Code explanation feature (right-click or Cmd+Shift+E)
- Code generation from natural language descriptions
- Code refactoring suggestions
- Inline code actions for Python files
- Workspace indexing for context-aware assistance
- Status bar integration
- Keybindings for quick access
- Configuration options for model selection and Python path
- Beautiful chat UI with syntax highlighting
- One-click code application to workspace
- Support for multiple code blocks in responses
- Error handling and user feedback

### Features
- **Chat Interface**: Full-featured chat sidebar
- **Context Menu**: Right-click actions for selected code
- **Commands**: 4 main commands accessible via Command Palette
- **Keybindings**: Customizable keyboard shortcuts
- **Settings**: Configurable model and Python path
- **Local Processing**: All inference happens locally via Ollama

### Technical
- TypeScript-based extension
- Webpack bundling for production
- Communication with Python CLI via child process spawning
- WebView-based chat UI with VSCode theme integration
- Real-time streaming responses
- Automatic code block extraction and formatting

## [Unreleased]

### Planned Features
- Multi-language support (JavaScript, TypeScript, Go, Rust)
- Inline code completion
- Git integration (commit message generation)
- Code review assistant
- Incremental indexing (watch mode)
- Model management UI
- Chat history persistence
- Export conversations
- Diff view for code changes
- Multiple chat sessions
- Custom prompt templates
