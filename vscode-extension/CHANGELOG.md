# Changelog

All notable changes to the Sage Code Assistant VSCode extension will be documented in this file.

## [0.2.0] - 2024-12-05

### Added
- **Chat History Persistence**: Conversations now persist across VSCode sessions
  - Last 50 messages are saved in workspace state
  - Automatic restoration when chat is reopened
  - Clear history with "✕ Clear" button
- **Diff View**: Preview code changes before applying
  - New "View Diff" button on all code blocks
  - Side-by-side comparison using VSCode's native diff editor
  - Confirmation prompt before applying changes
- **Model Switcher**: Dropdown to switch between Ollama models
  - Automatically loads available models on startup
  - Persists selection in settings
  - Real-time model switching without restart

### Improved
- **Error Handling**: More detailed and user-friendly error messages
- **Loading States**: Better visual feedback during operations
  - Animated typing indicator with dots
  - Button state changes with confirmation
  - Progress messages for indexing
- **UX Polish**: Enhanced overall user experience
  - Smooth fade-in animations for messages
  - Better button hover and active states
  - Auto-scroll to bottom on new messages
  - Theme-aware styling throughout

### Technical
- Added `ChatMessage` interface for type-safe history
- New methods: `handleApplyCodeWithDiff()`, `handleGetModels()`, `handleSwitchModel()`
- Chat history uses VSCode workspace state API
- Improved error boundaries and try-catch blocks

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
