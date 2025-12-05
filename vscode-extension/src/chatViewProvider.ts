/**
 * Webview provider for the Sage chat interface
 */

import * as vscode from 'vscode';
import { CodeAssistantService, AssistantResponse } from './codeAssistantService';

interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
}

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'codeAssistant.chatView';

    private _view?: vscode.WebviewView;
    private _context: vscode.ExtensionContext;
    private _chatHistory: ChatMessage[] = [];

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _assistantService: CodeAssistantService,
        context: vscode.ExtensionContext
    ) {
        this._context = context;
        this._loadChatHistory();
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Restore chat history
        this._restoreChatHistory();

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'query':
                    await this.handleQuery(data.query);
                    break;
                case 'applyCode':
                    await this.handleApplyCode(data.filename, data.code);
                    break;
                case 'applyCodeWithDiff':
                    await this.handleApplyCodeWithDiff(data.filename, data.code);
                    break;
                case 'indexWorkspace':
                    await this.handleIndexWorkspace();
                    break;
                case 'clearHistory':
                    this.handleClearHistory();
                    break;
                case 'getModels':
                    await this.handleGetModels();
                    break;
                case 'switchModel':
                    await this.handleSwitchModel(data.model);
                    break;
            }
        });
    }

    /**
     * Send a query from external command
     */
    public sendQuery(query: string) {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'externalQuery',
                query: query
            });
        }
    }

    private async handleQuery(query: string) {
        if (!this._view) {
            return;
        }

        // Save user message to history
        this._addToHistory('user', query);

        // Show user message in chat
        this._view.webview.postMessage({
            type: 'userMessage',
            content: query
        });

        // Show loading indicator
        this._view.webview.postMessage({
            type: 'assistantTyping',
            isTyping: true
        });

        try {
            let fullResponse = '';

            // Stream response
            await this._assistantService.streamQuery(
                query,
                (token) => {
                    fullResponse += token;
                    // Send token to webview for real-time display
                    this._view?.webview.postMessage({
                        type: 'assistantToken',
                        token: token
                    });
                },
                (response: AssistantResponse) => {
                    // Save assistant response to history
                    this._addToHistory('assistant', fullResponse);

                    // Complete response received
                    this._view?.webview.postMessage({
                        type: 'assistantComplete',
                        content: response.content,
                        codeBlocks: response.codeBlocks
                    });
                },
                (error: Error) => {
                    // Error occurred
                    this._view?.webview.postMessage({
                        type: 'error',
                        message: error.message
                    });
                }
            );
        } catch (error) {
            this._view.webview.postMessage({
                type: 'error',
                message: error instanceof Error ? error.message : 'Unknown error occurred'
            });
        } finally {
            this._view.webview.postMessage({
                type: 'assistantTyping',
                isTyping: false
            });
        }
    }

    private async handleApplyCode(filename: string | null, code: string) {
        if (!filename) {
            vscode.window.showWarningMessage('No filename specified for code block');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        try {
            const fileUri = vscode.Uri.joinPath(workspaceFolder.uri, filename);

            // Check if file exists
            let fileExists = false;
            try {
                await vscode.workspace.fs.stat(fileUri);
                fileExists = true;
            } catch {
                fileExists = false;
            }

            // Show confirmation
            const action = fileExists ? 'Overwrite' : 'Create';
            const confirmation = await vscode.window.showInformationMessage(
                `${action} ${filename}?`,
                { modal: true },
                'Yes',
                'No'
            );

            if (confirmation !== 'Yes') {
                return;
            }

            // Write file
            const encoder = new TextEncoder();
            await vscode.workspace.fs.writeFile(fileUri, encoder.encode(code));

            // Open the file
            const document = await vscode.workspace.openTextDocument(fileUri);
            await vscode.window.showTextDocument(document);

            vscode.window.showInformationMessage(`Successfully ${action.toLowerCase()}d ${filename}`);
        } catch (error) {
            vscode.window.showErrorMessage(
                `Failed to ${filename}: ${error instanceof Error ? error.message : 'Unknown error'}`
            );
        }
    }

    private async handleIndexWorkspace() {
        if (!this._view) {
            return;
        }

        this._view.webview.postMessage({
            type: 'systemMessage',
            content: 'Indexing workspace...'
        });

        try {
            await this._assistantService.indexWorkspace();
            this._view.webview.postMessage({
                type: 'systemMessage',
                content: 'Workspace indexed successfully!'
            });
        } catch (error) {
            this._view.webview.postMessage({
                type: 'error',
                message: `Indexing failed: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        }
    }

    private async handleApplyCodeWithDiff(filename: string | null, code: string) {
        if (!filename) {
            vscode.window.showWarningMessage('No filename specified for code block');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        try {
            const fileUri = vscode.Uri.joinPath(workspaceFolder.uri, filename);

            // Check if file exists
            let fileExists = false;
            let oldContent = '';
            try {
                const fileData = await vscode.workspace.fs.readFile(fileUri);
                oldContent = new TextDecoder().decode(fileData);
                fileExists = true;
            } catch {
                fileExists = false;
            }

            if (fileExists) {
                // Show diff editor
                const newUri = vscode.Uri.parse(`untitled:${filename}`);
                const newDocument = await vscode.workspace.openTextDocument(newUri);
                const edit = new vscode.WorkspaceEdit();
                edit.insert(newUri, new vscode.Position(0, 0), code);
                await vscode.workspace.applyEdit(edit);

                await vscode.commands.executeCommand('vscode.diff',
                    fileUri,
                    newUri,
                    `${filename} (Current ↔ Proposed)`
                );

                // Ask for confirmation
                const action = await vscode.window.showInformationMessage(
                    `Apply changes to ${filename}?`,
                    { modal: true },
                    'Apply',
                    'Cancel'
                );

                if (action === 'Apply') {
                    const encoder = new TextEncoder();
                    await vscode.workspace.fs.writeFile(fileUri, encoder.encode(code));
                    vscode.window.showInformationMessage(`Successfully updated ${filename}`);

                    // Close diff editor
                    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
                }
            } else {
                // File doesn't exist, just create it
                await this.handleApplyCode(filename, code);
            }
        } catch (error) {
            vscode.window.showErrorMessage(
                `Failed to show diff for ${filename}: ${error instanceof Error ? error.message : 'Unknown error'}`
            );
        }
    }

    private async handleGetModels() {
        try {
            const models = await this._assistantService.getAvailableModels();
            this._view?.webview.postMessage({
                type: 'modelsList',
                models: models
            });
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Failed to get models: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        }
    }

    private async handleSwitchModel(model: string) {
        const config = vscode.workspace.getConfiguration('sage');
        await config.update('model', model, vscode.ConfigurationTarget.Global);

        this._view?.webview.postMessage({
            type: 'systemMessage',
            content: `Switched to model: ${model}`
        });
    }

    private handleClearHistory() {
        this._chatHistory = [];
        this._saveChatHistory();

        this._view?.webview.postMessage({
            type: 'clearChat'
        });
    }

    private _loadChatHistory() {
        const history = this._context.workspaceState.get<ChatMessage[]>('chatHistory', []);
        this._chatHistory = history;
    }

    private _saveChatHistory() {
        // Keep only last 50 messages
        if (this._chatHistory.length > 50) {
            this._chatHistory = this._chatHistory.slice(-50);
        }
        this._context.workspaceState.update('chatHistory', this._chatHistory);
    }

    private _restoreChatHistory() {
        if (!this._view || this._chatHistory.length === 0) {
            return;
        }

        // Send all messages to webview
        for (const message of this._chatHistory) {
            if (message.role === 'user') {
                this._view.webview.postMessage({
                    type: 'userMessage',
                    content: message.content
                });
            } else if (message.role === 'assistant') {
                this._view.webview.postMessage({
                    type: 'assistantMessage',
                    content: message.content
                });
            } else if (message.role === 'system') {
                this._view.webview.postMessage({
                    type: 'systemMessage',
                    content: message.content
                });
            }
        }
    }

    private _addToHistory(role: 'user' | 'assistant' | 'system', content: string) {
        this._chatHistory.push({
            role,
            content,
            timestamp: Date.now()
        });
        this._saveChatHistory();
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sage Code Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            padding: 12px 16px;
            background-color: var(--vscode-sideBar-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header h2 {
            font-size: 14px;
            font-weight: 600;
            color: var(--vscode-foreground);
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        .header-button {
            background: transparent;
            border: none;
            color: var(--vscode-foreground);
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            opacity: 0.8;
        }

        .header-button:hover {
            background-color: var(--vscode-toolbar-hoverBackground);
            opacity: 1;
        }

        .header-select {
            background-color: var(--vscode-dropdown-background);
            color: var(--vscode-dropdown-foreground);
            border: 1px solid var(--vscode-dropdown-border);
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            cursor: pointer;
            outline: none;
        }

        .header-select:focus {
            border-color: var(--vscode-focusBorder);
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            display: flex;
            flex-direction: column;
            gap: 8px;
            animation: fadeIn 0.2s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
        }

        .message.user .message-header {
            color: #4EC9B0;
        }

        .message.assistant .message-header {
            color: #569CD6;
        }

        .message.system .message-header {
            color: #9CDCFE;
        }

        .message-content {
            padding: 12px;
            border-radius: 8px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background-color: var(--vscode-input-background);
            border-left: 3px solid #4EC9B0;
        }

        .message.assistant .message-content {
            background-color: var(--vscode-editor-background);
            border-left: 3px solid #569CD6;
        }

        .message.system .message-content {
            background-color: var(--vscode-textCodeBlock-background);
            border-left: 3px solid #9CDCFE;
            font-size: 11px;
        }

        .code-block {
            margin-top: 8px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            overflow: hidden;
        }

        .code-block-header {
            background-color: var(--vscode-editor-background);
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .code-block-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--vscode-textLink-foreground);
        }

        .code-block-actions {
            display: flex;
            gap: 8px;
        }

        .code-action-btn {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .code-action-btn:hover {
            background-color: var(--vscode-button-hoverBackground);
        }

        .code-block-content {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 12px;
            overflow-x: auto;
            font-family: var(--vscode-editor-font-family);
            font-size: 13px;
            line-height: 1.5;
        }

        .code-block-content code {
            color: var(--vscode-editor-foreground);
            white-space: pre;
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            color: #569CD6;
            font-size: 12px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #569CD6;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                opacity: 0.3;
            }
            30% {
                opacity: 1;
            }
        }

        .input-container {
            padding: 12px 16px;
            background-color: var(--vscode-sideBar-background);
            border-top: 1px solid var(--vscode-panel-border);
        }

        .input-wrapper {
            display: flex;
            gap: 8px;
        }

        #queryInput {
            flex: 1;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 13px;
            font-family: var(--vscode-font-family);
            resize: none;
            outline: none;
            min-height: 38px;
            max-height: 120px;
        }

        #queryInput:focus {
            border-color: var(--vscode-focusBorder);
        }

        #sendButton {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            cursor: pointer;
            transition: background-color 0.2s;
            white-space: nowrap;
        }

        #sendButton:hover {
            background-color: var(--vscode-button-hoverBackground);
        }

        #sendButton:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .error-message {
            padding: 12px;
            background-color: var(--vscode-inputValidation-errorBackground);
            border-left: 3px solid var(--vscode-inputValidation-errorBorder);
            border-radius: 4px;
            color: var(--vscode-errorForeground);
            font-size: 12px;
            margin-top: 8px;
        }

        .empty-state {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 32px;
            color: var(--vscode-descriptionForeground);
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .empty-state-description {
            font-size: 12px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>🧙‍♂️ Sage Assistant</h2>
        <div class="header-actions">
            <select id="modelSelector" class="header-select" onchange="switchModel(this.value)" title="Select Model">
                <option value="">Loading models...</option>
            </select>
            <button class="header-button" onclick="indexWorkspace()" title="Index Workspace">
                ⟳ Index
            </button>
            <button class="header-button" onclick="clearChat()" title="Clear Chat">
                ✕ Clear
            </button>
        </div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">Welcome to Sage</div>
            <div class="empty-state-description">
                Ask me anything about your code, request features, or get help refactoring.
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-wrapper">
            <textarea
                id="queryInput"
                placeholder="Ask me anything about your code..."
                rows="1"
            ></textarea>
            <button id="sendButton" onclick="sendQuery()">Send</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const chatContainer = document.getElementById('chatContainer');
        const queryInput = document.getElementById('queryInput');
        const sendButton = document.getElementById('sendButton');

        let currentAssistantMessage = null;

        // Handle messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'externalQuery':
                    queryInput.value = message.query;
                    sendQuery();
                    break;
                case 'userMessage':
                    addUserMessage(message.content);
                    break;
                case 'assistantToken':
                    appendToAssistantMessage(message.token);
                    break;
                case 'assistantComplete':
                    completeAssistantMessage(message.content, message.codeBlocks);
                    break;
                case 'assistantTyping':
                    if (message.isTyping) {
                        showTypingIndicator();
                    } else {
                        hideTypingIndicator();
                    }
                    break;
                case 'systemMessage':
                    addSystemMessage(message.content);
                    break;
                case 'error':
                    addErrorMessage(message.message);
                    hideTypingIndicator();
                    break;
                case 'clearChat':
                    clearChatUI();
                    break;
                case 'modelsList':
                    updateModelsList(message.models);
                    break;
                case 'assistantMessage':
                    addAssistantMessage(message.content);
                    break;
            }
        });

        // Auto-resize textarea
        queryInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Send on Enter (Shift+Enter for new line)
        queryInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuery();
            }
        });

        function sendQuery() {
            const query = queryInput.value.trim();
            if (!query) return;

            // Clear input
            queryInput.value = '';
            queryInput.style.height = 'auto';

            // Remove empty state
            const emptyState = chatContainer.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            // Send to extension
            vscode.postMessage({
                type: 'query',
                query: query
            });
        }

        function addUserMessage(content) {
            const messageEl = document.createElement('div');
            messageEl.className = 'message user';
            messageEl.innerHTML = \`
                <div class="message-header">You</div>
                <div class="message-content">\${escapeHtml(content)}</div>
            \`;
            chatContainer.appendChild(messageEl);
            scrollToBottom();
        }

        function showTypingIndicator() {
            const typingEl = document.createElement('div');
            typingEl.id = 'typingIndicator';
            typingEl.className = 'typing-indicator';
            typingEl.innerHTML = \`
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>Sage is thinking...</span>
            \`;
            chatContainer.appendChild(typingEl);
            scrollToBottom();
        }

        function hideTypingIndicator() {
            const typingEl = document.getElementById('typingIndicator');
            if (typingEl) {
                typingEl.remove();
            }
        }

        function appendToAssistantMessage(token) {
            if (!currentAssistantMessage) {
                hideTypingIndicator();

                currentAssistantMessage = document.createElement('div');
                currentAssistantMessage.className = 'message assistant';
                currentAssistantMessage.innerHTML = \`
                    <div class="message-header">Sage</div>
                    <div class="message-content"></div>
                \`;
                chatContainer.appendChild(currentAssistantMessage);
            }

            const contentEl = currentAssistantMessage.querySelector('.message-content');
            contentEl.textContent += token;
            scrollToBottom();
        }

        function completeAssistantMessage(content, codeBlocks) {
            currentAssistantMessage = null;

            // Add code blocks if any
            if (codeBlocks && codeBlocks.length > 0) {
                codeBlocks.forEach(block => {
                    addCodeBlock(block.filename, block.code);
                });
            }
        }

        function addCodeBlock(filename, code) {
            const codeBlockEl = document.createElement('div');
            codeBlockEl.className = 'code-block';

            const title = filename || 'Code';
            const escapedCode = escapeHtml(code);

            codeBlockEl.innerHTML = \`
                <div class="code-block-header">
                    <div class="code-block-title">\${escapeHtml(title)}</div>
                    <div class="code-block-actions">
                        <button class="code-action-btn" onclick="copyCode(this)">Copy</button>
                        \${filename ? \`<button class="code-action-btn" onclick="viewDiff('\${escapeHtml(filename)}', this)">View Diff</button>\` : ''}
                        \${filename ? \`<button class="code-action-btn" onclick="applyCode('\${escapeHtml(filename)}', this)">Apply</button>\` : ''}
                    </div>
                </div>
                <div class="code-block-content">
                    <code>\${escapedCode}</code>
                </div>
            \`;

            chatContainer.appendChild(codeBlockEl);
            scrollToBottom();
        }

        function copyCode(button) {
            const codeBlock = button.closest('.code-block');
            const code = codeBlock.querySelector('code').textContent;

            navigator.clipboard.writeText(code).then(() => {
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
        }

        function applyCode(filename, button) {
            const codeBlock = button.closest('.code-block');
            const code = codeBlock.querySelector('code').textContent;

            vscode.postMessage({
                type: 'applyCode',
                filename: filename,
                code: code
            });

            button.textContent = 'Applied!';
            setTimeout(() => {
                button.textContent = 'Apply';
            }, 2000);
        }

        function viewDiff(filename, button) {
            const codeBlock = button.closest('.code-block');
            const code = codeBlock.querySelector('code').textContent;

            vscode.postMessage({
                type: 'applyCodeWithDiff',
                filename: filename,
                code: code
            });

            button.textContent = 'Opening...';
            setTimeout(() => {
                button.textContent = 'View Diff';
            }, 2000);
        }

        function addSystemMessage(content) {
            const messageEl = document.createElement('div');
            messageEl.className = 'message system';
            messageEl.innerHTML = \`
                <div class="message-header">System</div>
                <div class="message-content">\${escapeHtml(content)}</div>
            \`;
            chatContainer.appendChild(messageEl);
            scrollToBottom();
        }

        function addErrorMessage(message) {
            const errorEl = document.createElement('div');
            errorEl.className = 'error-message';
            errorEl.textContent = message;
            chatContainer.appendChild(errorEl);
            scrollToBottom();
        }

        function indexWorkspace() {
            vscode.postMessage({ type: 'indexWorkspace' });
        }

        function clearChat() {
            vscode.postMessage({ type: 'clearHistory' });
        }

        function clearChatUI() {
            while (chatContainer.firstChild) {
                chatContainer.removeChild(chatContainer.firstChild);
            }

            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = \`
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">Welcome to Sage</div>
                <div class="empty-state-description">
                    Ask me anything about your code, request features, or get help refactoring.
                </div>
            \`;
            chatContainer.appendChild(emptyState);
        }

        function switchModel(model) {
            if (model) {
                vscode.postMessage({ type: 'switchModel', model: model });
            }
        }

        function updateModelsList(models) {
            const select = document.getElementById('modelSelector');
            select.innerHTML = '';

            if (!models || models.length === 0) {
                select.innerHTML = '<option value="">No models found</option>';
                return;
            }

            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                select.appendChild(option);
            });
        }

        function addAssistantMessage(content) {
            const messageEl = document.createElement('div');
            messageEl.className = 'message assistant';
            messageEl.innerHTML = \`
                <div class="message-header">Sage</div>
                <div class="message-content">\${escapeHtml(content)}</div>
            \`;
            chatContainer.appendChild(messageEl);

            // Remove empty state if present
            const emptyState = chatContainer.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            scrollToBottom();
        }

        function scrollToBottom() {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Load models on startup
        vscode.postMessage({ type: 'getModels' });

        // Focus input on load
        queryInput.focus();
    </script>
</body>
</html>`;
    }
}
