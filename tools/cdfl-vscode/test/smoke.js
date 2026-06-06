"use strict";

const assert = require("assert");
const path = require("path");
const vscode = require("vscode");

async function run() {
  const runtimeRoot = path.resolve(__dirname, "..", "..", "..");
  const samplePath = path.join(runtimeRoot, "examples", "heat_flow.cdfl");
  const sampleUri = vscode.Uri.file(samplePath);

  await vscode.workspace.getConfiguration("cdfl").update("runtime.cwd", runtimeRoot, vscode.ConfigurationTarget.Global);
  await vscode.workspace.getConfiguration("cdfl").update("runtime.command", "", vscode.ConfigurationTarget.Global);

  const document = await vscode.workspace.openTextDocument(sampleUri);
  assert.strictEqual(document.languageId, "cdfl");

  await vscode.window.showTextDocument(document);
  await wait(700);

  const commands = await vscode.commands.getCommands(true);
  for (const command of [
    "cdfl.validateCurrentFile",
    "cdfl.runCurrentFile",
    "cdfl.lintCurrentFile",
    "cdfl.showAst",
    "cdfl.formatViaRuntime",
    "cdfl.doctor",
    "cdfl.openLanguageReference",
    "cdfl.createHeatFlowSample",
  ]) {
    assert.ok(commands.includes(command), `${command} command is registered`);
  }

  const diagnostics = vscode.languages.getDiagnostics(sampleUri);
  assert.deepStrictEqual(diagnostics.map((row) => row.message), []);

  const completions = await vscode.commands.executeCommand(
    "vscode.executeCompletionItemProvider",
    sampleUri,
    new vscode.Position(0, 1)
  );
  assert.ok(completions.items.some((item) => String(item.label) === "SET"));

  const hovers = await vscode.commands.executeCommand(
    "vscode.executeHoverProvider",
    sampleUri,
    new vscode.Position(0, 1)
  );
  assert.ok(hovers.length > 0, "SET hover is available");

  const symbols = await vscode.commands.executeCommand("vscode.executeDocumentSymbolProvider", sampleUri);
  assert.ok(symbols.some((symbol) => symbol.name === "HeatChannel"));
  assert.ok(symbols.some((symbol) => symbol.name === "HeatOverload"));

  const messyUri = vscode.Uri.file(path.join(runtimeRoot, "tools", "cdfl-vscode", ".tmp-format-smoke.cdfl"));
  await vscode.workspace.fs.writeFile(
    messyUri,
    Buffer.from("SET domain: physics\nSYSTEM Messy {\nflux: 1.2\nconstraint: 0.9\nstate: psi\n}\n")
  );
  const messyDocument = await vscode.workspace.openTextDocument(messyUri);
  await vscode.window.showTextDocument(messyDocument);
  const edits = await vscode.commands.executeCommand(
    "vscode.executeFormatDocumentProvider",
    messyUri,
    { tabSize: 2, insertSpaces: true }
  );
  assert.ok(edits.length > 0, "formatter returns at least one edit");
  const runtimeFormat = await vscode.commands.executeCommand("cdfl.formatViaRuntime");
  assert.ok(runtimeFormat, "runtime formatter returns execution result");
  assert.strictEqual(runtimeFormat.parsed.status, "ok");
  assert.strictEqual(runtimeFormat.parsed.kind, "cdfl_format");
  assert.ok(vscode.window.activeTextEditor.document.getText().includes("  flux: 1.2"));
  await vscode.workspace.fs.delete(messyUri);

  await vscode.window.showTextDocument(document);

  const lint = await vscode.commands.executeCommand("cdfl.lintCurrentFile");
  assert.ok(lint, "lint command returns execution result");
  assert.strictEqual(lint.parsed.status, "ok");
  assert.strictEqual(lint.parsed.kind, "cdfl_lint");

  const validation = await vscode.commands.executeCommand("cdfl.validateCurrentFile");
  assert.ok(validation, "validate command returns execution result");
  assert.strictEqual(validation.parsed.status, "ok");
  assert.strictEqual(validation.parsed.payload.valid, true);

  const ast = await vscode.commands.executeCommand("cdfl.showAst");
  assert.ok(ast, "AST command returns execution result");
  assert.strictEqual(ast.parsed.status, "ok");
  assert.strictEqual(ast.parsed.kind, "cdfl_ast");
  assert.ok(ast.parsed.payload.nodes.some((node) => node.type === "SystemNode"));

  const runResult = await vscode.commands.executeCommand("cdfl.runCurrentFile");
  assert.ok(runResult, "run command returns execution result");
  assert.strictEqual(runResult.parsed.status, "ok");
  assert.strictEqual(runResult.parsed.kind, "cdfl_run");

  await vscode.commands.executeCommand("cdfl.createHeatFlowSample");
  assert.strictEqual(vscode.window.activeTextEditor.document.languageId, "cdfl");
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

module.exports = { run };
