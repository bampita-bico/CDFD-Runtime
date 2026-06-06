"use strict";

const cp = require("child_process");
const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

const LANGUAGE_ID = "cdfl";
const OUTPUT_NAME = "CDFL Runtime";

const KEYWORDS = [
  "DEFINE",
  "SET",
  "LINK",
  "RUN",
  "SCENARIO",
  "OBSERVE",
  "SWEEP",
  "DISCOVER",
  "PATIENT",
  "APPLY",
  "TO",
  "MODIFY",
  "ANALYZE",
  "BIFURCATE",
  "EMERGE",
  "ATTRACTOR",
  "INFOFLOW",
  "VACUUM",
  "KNOT",
  "SPAWN",
  "RESOLVE",
  "SPECTRUM",
  "SYSTEM",
  "RULE",
  "IF",
  "ACTION",
];

const TYPES = ["Engine", "Field", "Constraint", "Vacuum", "Knot", "Spectrum"];
const TOP_LEVEL = new Set([...KEYWORDS, ...TYPES]);
const NAMED_BLOCKS = new Set(["SYSTEM", "RULE", "SCENARIO", "PATIENT"]);
const BLOCK_KEYWORDS = new Set([
  "DEFINE",
  "PATIENT",
  "SCENARIO",
  "RUN",
  "OBSERVE",
  "DISCOVER",
  "ANALYZE",
  "BIFURCATE",
  "EMERGE",
  "ATTRACTOR",
  "INFOFLOW",
  "SPAWN",
  "SYSTEM",
  "RULE",
  "MODIFY",
]);

const COMMON_KEYS = [
  "domain",
  "flux",
  "constraint",
  "state",
  "duration",
  "dt",
  "metrics",
  "target",
  "resolution",
  "param_a",
  "param_b",
  "source_scenario",
];

const DOMAINS = [
  "physics",
  "origins_of_life",
  "medicine",
  "biology",
  "networks",
  "climate",
  "economics",
];

const METRICS = ["psi", "Psi", "phi", "Phi", "C", "S", "M_s", "LifeNumber"];

const HOVERS = {
  DEFINE: "Declare a named CDFL type or constants block, such as `DEFINE Vacuum { ... }`.",
  SET: "Set runtime context. The common first line is `SET domain: physics`.",
  LINK: "Connect two named CDFL entities with `LINK Source Target`.",
  RUN: "Execute the runtime engine. The current parser expects `RUN Engine { ... }`.",
  SCENARIO: "Group CDFL statements into a named scenario block.",
  OBSERVE: "Declare observed metrics, for example `OBSERVE { metrics: [psi] }`.",
  SWEEP: "Declare a parameter sweep, for example `SWEEP alpha [0.8, 1.0, 1.2]`.",
  DISCOVER: "Declare discovery parameters for a runtime discovery block.",
  PATIENT: "Declare a named patient-style data block for medicine-oriented models.",
  APPLY: "Apply a condition to a target with `APPLY condition TO target`.",
  MODIFY: "Modify a target inside a scenario or block.",
  ANALYZE: "Run an analysis block over the current runtime state.",
  BIFURCATE: "Declare bifurcation analysis parameters.",
  EMERGE: "Request emergence classification for the current field state.",
  ATTRACTOR: "Request attractor analysis for fixed points, cycles, or chaotic behavior.",
  INFOFLOW: "Request information-flow analysis.",
  SPAWN: "Create a knot-style object, for example `SPAWN Knot { n: 5 }`.",
  RESOLVE: "Resolve a spectrum target, for example `RESOLVE Spectrum`.",
  SYSTEM: "Define a named system with `flux`, `constraint`, and `state` entries.",
  RULE: "Define a threshold/action rule using `IF` and `ACTION` lines.",
  IF: "Begin a rule condition, for example `IF psi > 1.1`.",
  ACTION: "Declare the action for a CDFL rule.",
  Engine: "Runtime execution target used by `RUN Engine { ... }`.",
  Field: "CDFL built-in type for field declarations.",
  Constraint: "CDFL built-in type for constraint declarations.",
  Vacuum: "CDFL built-in type for vacuum constants.",
  Knot: "CDFL built-in type for knot-style discovery models.",
  Spectrum: "CDFL built-in target for spectral resolution.",
};

let diagnostics;
let output;

function activate(context) {
  diagnostics = vscode.languages.createDiagnosticCollection("cdfl");
  output = vscode.window.createOutputChannel(OUTPUT_NAME);

  const selector = { language: LANGUAGE_ID, scheme: "file" };

  context.subscriptions.push(
    diagnostics,
    output,
    vscode.workspace.onDidOpenTextDocument(updateDiagnostics),
    vscode.workspace.onDidChangeTextDocument((event) => updateDiagnostics(event.document)),
    vscode.workspace.onDidCloseTextDocument((document) => diagnostics.delete(document.uri)),
    vscode.languages.registerCompletionItemProvider(selector, new CdflCompletionProvider(), " ", ":", "["),
    vscode.languages.registerHoverProvider(selector, new CdflHoverProvider()),
    vscode.languages.registerDocumentSymbolProvider(selector, new CdflSymbolProvider()),
    vscode.languages.registerDocumentFormattingEditProvider(selector, new CdflFormattingProvider()),
    vscode.commands.registerCommand("cdfl.validateCurrentFile", () => runModelCommand("validate")),
    vscode.commands.registerCommand("cdfl.runCurrentFile", () => runModelCommand("run")),
    vscode.commands.registerCommand("cdfl.lintCurrentFile", () => runModelCommand("lint")),
    vscode.commands.registerCommand("cdfl.showAst", () => runModelCommand("ast")),
    vscode.commands.registerCommand("cdfl.formatViaRuntime", () => formatWithRuntime()),
    vscode.commands.registerCommand("cdfl.doctor", () => runUtilityCommand("doctor")),
    vscode.commands.registerCommand("cdfl.openLanguageReference", () => openLanguageReference(context)),
    vscode.commands.registerCommand("cdfl.createHeatFlowSample", () => createHeatFlowSample())
  );

  for (const document of vscode.workspace.textDocuments) {
    updateDiagnostics(document);
  }
}

function deactivate() {
  if (diagnostics) {
    diagnostics.dispose();
  }
  if (output) {
    output.dispose();
  }
}

function isCdflDocument(document) {
  return document && document.languageId === LANGUAGE_ID;
}

function updateDiagnostics(document) {
  if (!isCdflDocument(document) || !configuration().get("diagnostics.enabled", true)) {
    return;
  }
  diagnostics.set(document.uri, analyzeDocument(document));
}

function analyzeDocument(document) {
  const found = [];
  const stack = [];
  let ruleDepth = 0;

  for (let lineNumber = 0; lineNumber < document.lineCount; lineNumber += 1) {
    const line = document.lineAt(lineNumber);
    const raw = line.text;
    const text = stripComment(raw).trim();

    if (!text) {
      continue;
    }

    const depthBefore = stack.length;
    const first = firstWord(text);

    if (depthBefore === 0 && first && !TOP_LEVEL.has(first) && first !== "}") {
      found.push(diagnostic(lineNumber, 0, first.length, `Unknown CDFL statement '${first}'.`, vscode.DiagnosticSeverity.Warning));
    }

    if (first === "SET") {
      checkSetLine(found, lineNumber, raw, text);
    }

    if (first === "RUN") {
      checkRunLine(found, lineNumber, raw, text);
    }

    if (NAMED_BLOCKS.has(first)) {
      checkNamedBlockLine(found, lineNumber, raw, text, first);
    }

    if (first === "IF") {
      if (ruleDepth === 0) {
        found.push(diagnostic(lineNumber, 0, 2, "`IF` is only meaningful inside a RULE block.", vscode.DiagnosticSeverity.Information));
      }
      if (!/\bIF\s+[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*\s*(?:>|<|>=|<=|==|!=)\s*\d+(?:\.\d+)?\b/.test(text)) {
        found.push(diagnostic(lineNumber, 0, raw.length, "Expected rule condition like `IF psi > 1.1`.", vscode.DiagnosticSeverity.Warning));
      }
    }

    if (first === "ACTION" && !/^ACTION\s+[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*\s*$/.test(text)) {
      found.push(diagnostic(lineNumber, 0, raw.length, "Expected action line like `ACTION reduce_flux`.", vscode.DiagnosticSeverity.Warning));
    }

    if (depthBefore > 0 && first && shouldLookLikeKeyValue(first, text)) {
      found.push(diagnostic(lineNumber, raw.indexOf(first), first.length, "Expected `key: value` inside this CDFL block.", vscode.DiagnosticSeverity.Warning));
    }

    const events = bracketEvents(raw);
    for (const event of events) {
      if (event.char === "{") {
        stack.push({ char: "{", line: lineNumber, character: event.character, first });
        if (first === "RULE") {
          ruleDepth += 1;
        }
      } else if (event.char === "}") {
        const opened = stack.pop();
        if (!opened || opened.char !== "{") {
          found.push(diagnostic(lineNumber, event.character, event.character + 1, "Unmatched closing brace.", vscode.DiagnosticSeverity.Error));
        } else if (opened.first === "RULE") {
          ruleDepth = Math.max(0, ruleDepth - 1);
        }
      } else if (event.char === "[") {
        stack.push({ char: "[", line: lineNumber, character: event.character, first: null });
      } else if (event.char === "]") {
        const opened = stack.pop();
        if (!opened || opened.char !== "[") {
          found.push(diagnostic(lineNumber, event.character, event.character + 1, "Unmatched closing bracket.", vscode.DiagnosticSeverity.Error));
        }
      }
    }
  }

  for (const opened of stack) {
    found.push(diagnostic(opened.line, opened.character, opened.character + 1, `Unclosed ${opened.char === "{" ? "block" : "list"}.`, vscode.DiagnosticSeverity.Error));
  }

  return found;
}

function checkSetLine(found, lineNumber, raw, text) {
  if (!/^SET\s+[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*\s*:\s*\S+/.test(text)) {
    found.push(diagnostic(lineNumber, 0, raw.length, "Expected `SET key: value`, for example `SET domain: physics`.", vscode.DiagnosticSeverity.Warning));
  }
}

function checkRunLine(found, lineNumber, raw, text) {
  if (!/^RUN\s+Engine\b/.test(text)) {
    found.push(diagnostic(lineNumber, 0, raw.length, "The current parser expects `RUN Engine { ... }`.", vscode.DiagnosticSeverity.Warning));
  }
  if (!text.includes("{")) {
    found.push(diagnostic(lineNumber, 0, raw.length, "`RUN Engine` needs a parameter block.", vscode.DiagnosticSeverity.Warning));
  }
}

function checkNamedBlockLine(found, lineNumber, raw, text, keyword) {
  const pattern = new RegExp(`^${keyword}\\s+[A-Za-z_\\u0370-\\u03FF][\\w.\\u0370-\\u03FF]*\\s*\\{?`);
  if (!pattern.test(text)) {
    found.push(diagnostic(lineNumber, 0, raw.length, `Expected \`${keyword} Name { ... }\`.`, vscode.DiagnosticSeverity.Warning));
  }
  if (!text.includes("{")) {
    found.push(diagnostic(lineNumber, 0, raw.length, `${keyword} declarations need an opening block brace.`, vscode.DiagnosticSeverity.Warning));
  }
}

function shouldLookLikeKeyValue(first, text) {
  if (BLOCK_KEYWORDS.has(first) || first === "IF" || first === "ACTION" || first === "}") {
    return false;
  }
  if (text.includes(":")) {
    return false;
  }
  return /^[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*\s+\S+/.test(text);
}

function diagnostic(lineNumber, start, end, message, severity) {
  return new vscode.Diagnostic(new vscode.Range(lineNumber, start, lineNumber, Math.max(start + 1, end)), message, severity);
}

function stripComment(line) {
  let quote = null;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if ((ch === '"' || ch === "'") && line[i - 1] !== "\\") {
      quote = quote === ch ? null : quote || ch;
      continue;
    }
    if (ch === "#" && quote === null) {
      return line.slice(0, i);
    }
  }
  return line;
}

function firstWord(text) {
  const match = text.match(/^[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*/);
  return match ? match[0] : "";
}

function bracketEvents(line) {
  const events = [];
  let quote = null;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if ((ch === '"' || ch === "'") && line[i - 1] !== "\\") {
      quote = quote === ch ? null : quote || ch;
      continue;
    }
    if (ch === "#" && quote === null) {
      break;
    }
    if (!quote && "{}[]".includes(ch)) {
      events.push({ char: ch, character: i });
    }
  }
  return events;
}

class CdflCompletionProvider {
  provideCompletionItems(document, position) {
    const linePrefix = document.lineAt(position).text.slice(0, position.character);
    const trimmed = linePrefix.trim();
    const items = [];

    if (/SET\s+domain\s*:\s*[A-Za-z_]*$/i.test(linePrefix)) {
      return DOMAINS.map((domain) => completion(domain, vscode.CompletionItemKind.Value, "CDFD Runtime domain"));
    }

    if (/\[\s*[A-Za-z_]*$/i.test(linePrefix)) {
      return METRICS.map((metric) => completion(metric, vscode.CompletionItemKind.Variable, "Common CDFL metric"));
    }

    if (/^\s*RUN\s*$/i.test(linePrefix)) {
      return [completion("Engine", vscode.CompletionItemKind.Class, "Runtime engine target")];
    }

    if (!trimmed || /^\w+$/.test(trimmed)) {
      items.push(...KEYWORDS.map((word) => completion(word, vscode.CompletionItemKind.Keyword, HOVERS[word] || "CDFL keyword")));
      items.push(...snippetCompletions());
      return items;
    }

    if (/^\s*[A-Za-z_]*$/.test(linePrefix) || /^\s+\w*$/.test(linePrefix)) {
      items.push(...COMMON_KEYS.map((key) => completion(`${key}: `, vscode.CompletionItemKind.Property, "CDFL block key")));
    }

    return items;
  }
}

function completion(label, kind, detail) {
  const item = new vscode.CompletionItem(label, kind);
  item.detail = detail;
  return item;
}

function snippetCompletions() {
  return [
    ["SYSTEM block", "SYSTEM ${1:Name} {\n  flux: ${2:1.2}\n  constraint: ${3:0.9}\n  state: ${4:psi}\n}", "Define a CDFL system."],
    ["RULE block", "RULE ${1:Name} {\n  IF ${2:psi} > ${3:1.1}\n  ACTION ${4:reduce_flux}\n}", "Define a CDFL threshold rule."],
    ["RUN Engine", "RUN Engine {\n  duration: ${1:0.05}\n  dt: ${2:0.01}\n}", "Run the CDFD engine."],
    ["OBSERVE metrics", "OBSERVE {\n  metrics: [${1:psi}]\n}", "Observe CDFL metrics."],
  ].map(([label, body, detail]) => {
    const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
    item.insertText = new vscode.SnippetString(body);
    item.detail = detail;
    return item;
  });
}

class CdflHoverProvider {
  provideHover(document, position) {
    const range = document.getWordRangeAtPosition(position, /[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*/);
    if (!range) {
      return undefined;
    }
    const word = document.getText(range);
    const text = HOVERS[word];
    if (!text) {
      return undefined;
    }
    return new vscode.Hover(new vscode.MarkdownString(`**${word}**\n\n${text}`), range);
  }
}

class CdflSymbolProvider {
  provideDocumentSymbols(document) {
    const symbols = [];
    for (let lineNumber = 0; lineNumber < document.lineCount; lineNumber += 1) {
      const line = stripComment(document.lineAt(lineNumber).text);
      const match = line.match(/^\s*(SYSTEM|RULE|SCENARIO|PATIENT)\s+([A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*)/);
      if (!match) {
        continue;
      }
      const keyword = match[1];
      const name = match[2];
      const start = line.indexOf(keyword);
      const range = new vscode.Range(lineNumber, start, lineNumber, line.length);
      symbols.push(new vscode.DocumentSymbol(name, keyword, symbolKind(keyword), range, range));
    }
    return symbols;
  }
}

function symbolKind(keyword) {
  if (keyword === "SYSTEM") {
    return vscode.SymbolKind.Class;
  }
  if (keyword === "RULE") {
    return vscode.SymbolKind.Function;
  }
  if (keyword === "PATIENT") {
    return vscode.SymbolKind.Object;
  }
  return vscode.SymbolKind.Module;
}

class CdflFormattingProvider {
  provideDocumentFormattingEdits(document) {
    const indentSize = configuration().get("format.indentSize", 2);
    const indentUnit = " ".repeat(Math.max(0, indentSize));
    const lines = [];
    let depth = 0;

    for (let i = 0; i < document.lineCount; i += 1) {
      const original = document.lineAt(i).text.trim();
      if (!original) {
        lines.push("");
        continue;
      }
      const startsClosing = original.startsWith("}") || original.startsWith("]");
      const currentDepth = Math.max(0, depth - (startsClosing ? 1 : 0));
      lines.push(`${indentUnit.repeat(currentDepth)}${original}`);
      const events = bracketEvents(original);
      for (const event of events) {
        if (event.char === "{" || event.char === "[") {
          depth += 1;
        } else if (event.char === "}" || event.char === "]") {
          depth = Math.max(0, depth - 1);
        }
      }
    }

    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    return [vscode.TextEdit.replace(fullRange, lines.join("\n"))];
  }
}

async function runModelCommand(command) {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== LANGUAGE_ID) {
    vscode.window.showWarningMessage("Open a .cdfl file first.");
    return;
  }
  const document = editor.document;
  if (document.isUntitled) {
    vscode.window.showWarningMessage("Save the CDFL file before running runtime commands.");
    return;
  }
  if (document.isDirty) {
    await document.save();
  }

  const file = document.uri.fsPath;
  const args = command === "run"
    ? ["run", file, "--nx", String(configuration().get("run.nx", 16)), "--ny", String(configuration().get("run.ny", 16)), "--json"]
    : [command, file, "--json"];
  return executeRuntime("cdfl", args, `${command} ${path.basename(file)}`);
}

async function formatWithRuntime() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== LANGUAGE_ID) {
    vscode.window.showWarningMessage("Open a .cdfl file first.");
    return;
  }
  const document = editor.document;
  if (document.isUntitled) {
    vscode.window.showWarningMessage("Save the CDFL file before running runtime formatting.");
    return;
  }
  if (document.isDirty) {
    await document.save();
  }

  const file = document.uri.fsPath;
  const result = await executeRuntime("cdfl", ["format", file, "--json"], `format ${path.basename(file)}`);
  const formatted = result && result.parsed && result.parsed.payload && result.parsed.payload.formatted;
  if (result && result.parsed && result.parsed.status === "ok" && typeof formatted === "string") {
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    const edit = new vscode.WorkspaceEdit();
    edit.replace(document.uri, fullRange, formatted);
    await vscode.workspace.applyEdit(edit);
  }
  return result;
}

async function runUtilityCommand(command) {
  return executeRuntime(command, ["--json"], command);
}

async function executeRuntime(subcommand, args, label) {
  output.clear();
  output.show(true);
  const invocation = buildRuntimeInvocation(subcommand, args);
  output.appendLine(`$ ${invocation.commandLine}`);
  output.appendLine("");

  return new Promise((resolve) => {
    cp.exec(invocation.commandLine, { cwd: invocation.cwd, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (stdout) {
        output.appendLine(stdout.trimEnd());
      }
      if (stderr) {
        output.appendLine(stderr.trimEnd());
      }
      const parsed = parseJson(stdout);
      if (parsed && parsed.status === "ok") {
        vscode.window.showInformationMessage(`CDFL ${label} completed.`);
      } else if (parsed && parsed.errors) {
        vscode.window.showErrorMessage(`CDFL ${label} failed: ${parsed.errors.join("; ")}`);
      } else if (error) {
        vscode.window.showErrorMessage(`CDFL ${label} failed. See ${OUTPUT_NAME} output.`);
      } else {
        vscode.window.showInformationMessage(`CDFL ${label} finished. See ${OUTPUT_NAME} output.`);
      }
      resolve({ error, stdout, stderr, parsed });
    });
  });
}

function buildRuntimeInvocation(subcommand, args) {
  const config = configuration();
  const configuredCommand = config.get("runtime.command", "").trim();
  const cwd = resolveRuntimeCwd(config.get("runtime.cwd", "").trim());
  const quotedArgs = [subcommand, ...args].map(shellQuote).join(" ");

  if (configuredCommand) {
    return { cwd, commandLine: `${configuredCommand} ${quotedArgs}` };
  }

  const cdfdPy = path.join(cwd, "cdfd.py");
  if (fs.existsSync(cdfdPy)) {
    return { cwd, commandLine: `${shellQuote(defaultPython(cwd))} ${shellQuote(cdfdPy)} ${quotedArgs}` };
  }

  return { cwd, commandLine: `cdfd ${quotedArgs}` };
}

function resolveRuntimeCwd(configuredCwd) {
  if (configuredCwd) {
    return configuredCwd;
  }
  const sourceRoot = path.resolve(__dirname, "..", "..");
  if (fs.existsSync(path.join(sourceRoot, "cdfd.py"))) {
    return sourceRoot;
  }
  const workspace = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  return workspace ? workspace.uri.fsPath : process.cwd();
}

function defaultPython(cwd) {
  const candidates = process.platform === "win32"
    ? [
        path.join(cwd, ".venv", "Scripts", "python.exe"),
        path.join(cwd, "..", ".venv", "Scripts", "python.exe"),
      ]
    : [
        path.join(cwd, ".venv", "bin", "python"),
        path.join(cwd, "..", ".venv", "bin", "python"),
      ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return process.platform === "win32" ? "python" : "python3";
}

function shellQuote(value) {
  const text = String(value);
  if (/^[A-Za-z0-9_./:=+-]+$/.test(text)) {
    return text;
  }
  return `'${text.replace(/'/g, "'\\''")}'`;
}

function parseJson(text) {
  if (!text || !text.trim()) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (_error) {
    return null;
  }
}

async function openLanguageReference(context) {
  const uri = vscode.Uri.file(path.join(context.extensionPath, "docs", "language-reference.md"));
  await vscode.commands.executeCommand("markdown.showPreviewToSide", uri);
}

async function createHeatFlowSample() {
  const doc = await vscode.workspace.openTextDocument({
    language: LANGUAGE_ID,
    content: [
      "SET domain: physics",
      "",
      "SYSTEM HeatChannel {",
      "  flux: 1.2",
      "  constraint: 0.9",
      "  state: psi",
      "}",
      "",
      "RULE HeatOverload {",
      "  IF psi > 1.1",
      "  ACTION reduce_flux",
      "}",
      "",
      "RUN Engine {",
      "  duration: 0.05",
      "  dt: 0.01",
      "}",
      "",
      "OBSERVE {",
      "  metrics: [psi]",
      "}",
      "",
    ].join("\n"),
  });
  await vscode.window.showTextDocument(doc);
}

function configuration() {
  return vscode.workspace.getConfiguration("cdfl");
}

module.exports = {
  activate,
  deactivate,
  analyzeDocument,
  stripComment,
  bracketEvents,
  buildRuntimeInvocation,
};
