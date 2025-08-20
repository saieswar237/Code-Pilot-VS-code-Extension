//
// Code-Pilot: The Real-Time Coding Mentor
// Final Reliable Version: This version sends the code as a direct argument.
//

const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

let diagnosticCollection;
let debounceTimer;

function activate(context) {
    console.log('Code-Pilot is now active!');

    diagnosticCollection = vscode.languages.createDiagnosticCollection('code-pilot');
    context.subscriptions.push(diagnosticCollection);

    if (vscode.window.activeTextEditor) {
        triggerAnalysis(vscode.window.activeTextEditor.document);
    }
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                triggerAnalysis(editor.document);
            }
        })
    );

    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                triggerAnalysis(event.document);
            }, 500);
        })
    );
}

function triggerAnalysis(document) {
    if (document.languageId !== 'python') {
        return;
    }
    
    console.log('Code-Pilot: Analyzing a Python file...');
    diagnosticCollection.clear();
    
    const scriptPath = path.join(__dirname, 'analyzer.py');
    const fileContent = document.getText();

    // --- NEW RELIABLE METHOD ---
    // We now pass the entire file content as a command-line argument.
    const pythonProcess = spawn('python', [scriptPath, fileContent]);
    
    pythonProcess.on('error', (err) => {
        console.error('Code-Pilot: FAILED to start the Python process.', err);
        vscode.window.showErrorMessage('Code-Pilot: Failed to start the Python analyzer. Make sure Python is installed and in your PATH.');
    });

    let scriptOutput = '';
    pythonProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
    });

    let scriptError = '';
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Code-Pilot (Python stderr): ${data}`);
        scriptError += data.toString();
    });

    pythonProcess.on('close', (code) => {
        console.log(`Code-Pilot: Python process finished with exit code ${code}.`);
        
        if (scriptError && code !== 0) {
            console.error("Code-Pilot: The Python script exited with an error. Aborting.");
            return;
        }
        if (!scriptOutput.trim()) {
            return;
        }

        try {
            const errors = JSON.parse(scriptOutput);
            const diagnostics = [];

            errors.forEach(error => {
                const line = error.line;
                const message = error.message;
                const lineOfText = document.lineAt(line);
                
                const range = new vscode.Range(line, 0, line, lineOfText.text.length);
                const diagnostic = new vscode.Diagnostic(
                    range,
                    message,
                    vscode.DiagnosticSeverity.Warning
                );
                diagnostics.push(diagnostic);
            });

            diagnosticCollection.set(document.uri, diagnostics);
            console.log(`Code-Pilot: Successfully found and displayed ${diagnostics.length} issues.`);
        } catch (e) {
            console.error("Code-Pilot: FAILED to parse JSON from analyzer script.", e);
        }
    });
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
