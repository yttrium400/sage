/**
 * Service for communicating with the Sage CLI backend
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';

export interface AssistantMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface AssistantResponse {
    content: string;
    codeBlocks?: Array<{
        filename: string | null;
        code: string;
    }>;
}

export class CodeAssistantService {
    private pythonPath: string = 'python3';
    private cliPath: string;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;

        // Find the CLI path relative to the extension
        const extensionPath = context.extensionPath;
        this.cliPath = path.join(extensionPath, '..', 'cli');

        this.initializeService();
    }

    private async initializeService() {
        // Check if Python is available
        const pythonAvailable = await this.checkPythonAvailable();
        if (!pythonAvailable) {
            vscode.window.showErrorMessage(
                'Python 3 not found. Please install Python 3.8+ to use Sage Code Assistant.'
            );
            return;
        }

        // Check if Ollama is available
        const ollamaAvailable = await this.checkOllamaAvailable();
        if (!ollamaAvailable) {
            const action = await vscode.window.showWarningMessage(
                'Ollama not found. Sage requires Ollama for local LLM inference.',
                'Learn More'
            );
            if (action === 'Learn More') {
                vscode.env.openExternal(vscode.Uri.parse('https://ollama.ai/'));
            }
        }
    }

    private async checkPythonAvailable(): Promise<boolean> {
        return new Promise((resolve) => {
            const proc = spawn(this.pythonPath, ['--version']);
            proc.on('error', () => resolve(false));
            proc.on('close', (code) => resolve(code === 0));
        });
    }

    private async checkOllamaAvailable(): Promise<boolean> {
        return new Promise((resolve) => {
            const proc = spawn('ollama', ['list']);
            proc.on('error', () => resolve(false));
            proc.on('close', (code) => resolve(code === 0));
        });
    }

    /**
     * Send a query to the code assistant and get a response
     */
    async query(
        query: string,
        contextDir?: string,
        onToken?: (token: string) => void
    ): Promise<AssistantResponse> {
        const workspaceFolder = contextDir || this.getWorkspaceRoot();

        return new Promise((resolve, reject) => {
            const args = [
                path.join(this.cliPath, 'main.py'),
                'ask',
                query,
                '--context-dir',
                workspaceFolder
            ];

            const proc = spawn(this.pythonPath, args, {
                cwd: this.cliPath
            });

            let stdout = '';
            let stderr = '';

            proc.stdout.on('data', (data) => {
                const text = data.toString();
                stdout += text;
                if (onToken) {
                    onToken(text);
                }
            });

            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            proc.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(`CLI process exited with code ${code}: ${stderr}`));
                    return;
                }

                // Parse response
                const codeBlocks = this.extractCodeBlocks(stdout);
                resolve({
                    content: stdout,
                    codeBlocks
                });
            });

            proc.on('error', (error) => {
                reject(error);
            });
        });
    }

    /**
     * Start a streaming query session
     */
    async streamQuery(
        query: string,
        onToken: (token: string) => void,
        onComplete: (response: AssistantResponse) => void,
        onError: (error: Error) => void
    ): Promise<void> {
        try {
            const response = await this.query(query, undefined, onToken);
            onComplete(response);
        } catch (error) {
            onError(error as Error);
        }
    }

    /**
     * Index the current workspace
     */
    async indexWorkspace(contextDir?: string): Promise<void> {
        const workspaceFolder = contextDir || this.getWorkspaceRoot();

        return new Promise((resolve, reject) => {
            const args = [
                path.join(this.cliPath, 'main.py'),
                'index',
                '--context-dir',
                workspaceFolder
            ];

            const proc = spawn(this.pythonPath, args, {
                cwd: this.cliPath
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Indexing failed with code ${code}`));
                }
            });

            proc.on('error', (error) => {
                reject(error);
            });
        });
    }

    /**
     * Get available models
     */
    async getAvailableModels(): Promise<string[]> {
        return new Promise((resolve, reject) => {
            const args = [
                path.join(this.cliPath, 'main.py'),
                'models'
            ];

            const proc = spawn(this.pythonPath, args, {
                cwd: this.cliPath
            });

            let stdout = '';

            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    // Parse model names from output
                    const models = stdout
                        .split('\n')
                        .filter(line => line.trim().startsWith('•'))
                        .map(line => line.replace('•', '').trim());
                    resolve(models);
                } else {
                    resolve([]);
                }
            });

            proc.on('error', () => {
                resolve([]);
            });
        });
    }

    private getWorkspaceRoot(): string {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return workspaceFolders[0].uri.fsPath;
        }
        return process.cwd();
    }

    private extractCodeBlocks(text: string): Array<{filename: string | null; code: string}> {
        const codeBlocks: Array<{filename: string | null; code: string}> = [];

        // Pattern: ```python:filename.py or ```python
        const pattern = /```python(?::([^\n]+))?\n(.*?)```/gs;
        let match;

        while ((match = pattern.exec(text)) !== null) {
            const filename = match[1] ? match[1].trim() : null;
            const code = match[2].trim();
            codeBlocks.push({ filename, code });
        }

        return codeBlocks;
    }

    dispose() {
        // Cleanup if needed
    }
}
