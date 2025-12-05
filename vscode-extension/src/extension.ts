/**
 * Sage Code Assistant - VSCode Extension
 * Main extension entry point
 */

import * as vscode from 'vscode';
import { ChatViewProvider } from './chatViewProvider';
import { CodeAssistantService } from './codeAssistantService';

let chatViewProvider: ChatViewProvider;
let codeAssistantService: CodeAssistantService;

export function activate(context: vscode.ExtensionContext) {
    console.log('Sage Code Assistant is now active!');

    // Initialize the code assistant service
    codeAssistantService = new CodeAssistantService(context);

    // Register chat view provider
    chatViewProvider = new ChatViewProvider(context.extensionUri, codeAssistantService, context);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            ChatViewProvider.viewType,
            chatViewProvider
        )
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('codeAssistant.openChat', () => {
            // Focus on the chat view
            vscode.commands.executeCommand('codeAssistant.chatView.focus');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codeAssistant.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showInformationMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const text = editor.document.getText(selection);

            if (!text) {
                vscode.window.showInformationMessage('No code selected');
                return;
            }

            // Open chat and ask for explanation
            await vscode.commands.executeCommand('codeAssistant.chatView.focus');
            chatViewProvider.sendQuery(`Explain this code:\n\`\`\`python\n${text}\n\`\`\``);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codeAssistant.generateCode', async () => {
            const input = await vscode.window.showInputBox({
                prompt: 'What code would you like to generate?',
                placeHolder: 'e.g., create a function to validate email addresses'
            });

            if (input) {
                await vscode.commands.executeCommand('codeAssistant.chatView.focus');
                chatViewProvider.sendQuery(input);
            }
        })
    );

    // Register inline code action provider (for Cmd+K style editing)
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { scheme: 'file', language: 'python' },
            new CodeActionProvider(codeAssistantService),
            {
                providedCodeActionKinds: CodeActionProvider.providedCodeActionKinds
            }
        )
    );

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = "$(comment-discussion) Sage";
    statusBarItem.tooltip = "Open Sage Code Assistant";
    statusBarItem.command = 'codeAssistant.openChat';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

export function deactivate() {
    if (codeAssistantService) {
        codeAssistantService.dispose();
    }
}

/**
 * Code Action Provider for inline editing
 */
class CodeActionProvider implements vscode.CodeActionProvider {
    public static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.RefactorRewrite
    ];

    constructor(private codeAssistantService: CodeAssistantService) {}

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection
    ): vscode.CodeAction[] | undefined {
        if (!range.isEmpty) {
            const refactorAction = this.createRefactorAction(document, range);
            const explainAction = this.createExplainAction(document, range);
            return [refactorAction, explainAction];
        }
        return undefined;
    }

    private createRefactorAction(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Sage: Refactor this code',
            vscode.CodeActionKind.RefactorRewrite
        );
        action.command = {
            command: 'codeAssistant.refactorCode',
            title: 'Refactor Code',
            arguments: [document, range]
        };
        return action;
    }

    private createExplainAction(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Sage: Explain this code',
            vscode.CodeActionKind.Empty
        );
        action.command = {
            command: 'codeAssistant.explainCode',
            title: 'Explain Code'
        };
        return action;
    }
}
