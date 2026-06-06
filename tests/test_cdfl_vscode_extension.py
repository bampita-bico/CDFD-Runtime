import json
import subprocess
from pathlib import Path

from dsl.lexer import tokenize
from dsl.tokens import TokenType
from runtime.runner import validate_cdfl


ROOT = Path(__file__).resolve().parents[1]
EXTENSION_ROOT = ROOT / "tools" / "cdfl-vscode"


def test_cdfl_lexer_ignores_hash_comments(tmp_path):
    model = tmp_path / "commented.cdfl"
    model.write_text(
        """
# RUN Engine { duration: 99 dt: 1 }
SET domain: physics # RUN Engine { duration: 88 dt: 1 }
SYSTEM PsiChannel {
  flux: 1.2 # ignored_identifier
  constraint: 0.9
  state: Psi
}
RUN Engine {
  duration: 0.05
  dt: 0.01
}
"""
    )

    tokens = tokenize(model.read_text())
    values = [token.value for token in tokens if token.type != TokenType.EOF]

    assert values.count("RUN") == 1
    assert "ignored_identifier" not in values

    validation = validate_cdfl(model)
    assert validation["status"] == "ok"
    assert validation["payload"]["valid"] is True
    assert validation["payload"]["node_count"] == 3


def test_cdfl_vscode_extension_metadata_and_assets_are_consistent():
    package = json.loads((EXTENSION_ROOT / "package.json").read_text())

    assert package["name"] == "cdfl-language-support"
    assert package["displayName"] == "CDFL Language Support"
    assert package["publisher"] == "VuraLabs"
    assert package["version"] == "0.1.0"
    assert package["icon"] == "assets/icon.png"
    assert package["main"] == "./extension.js"
    assert "onLanguage:cdfl" in package["activationEvents"]

    language = package["contributes"]["languages"][0]
    assert language["id"] == "cdfl"
    assert ".cdfl" in language["extensions"]

    grammar = package["contributes"]["grammars"][0]
    assert grammar["scopeName"] == "source.cdfl"

    commands = {row["command"] for row in package["contributes"]["commands"]}
    assert {
        "cdfl.validateCurrentFile",
        "cdfl.runCurrentFile",
        "cdfl.lintCurrentFile",
        "cdfl.showAst",
        "cdfl.formatViaRuntime",
        "cdfl.doctor",
        "cdfl.openLanguageReference",
        "cdfl.createHeatFlowSample",
    } == commands
    assert {"cdfl.runtime.command", "cdfl.runtime.cwd", "cdfl.diagnostics.enabled"} <= set(
        package["contributes"]["configuration"]["properties"]
    )

    contributed_paths = [
        package["icon"],
        package["main"],
        language["configuration"],
        grammar["path"],
        package["contributes"]["snippets"][0]["path"],
    ]
    for relative_path in contributed_paths:
        assert (EXTENSION_ROOT / relative_path).exists(), relative_path

    assert (EXTENSION_ROOT / package["icon"]).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert (EXTENSION_ROOT / "LICENSE").exists()
    assert (EXTENSION_ROOT / "docs" / "language-reference.md").exists()


def test_cdfl_vscode_extension_json_and_scope_docs_are_parseable():
    for relative_path in [
        "package.json",
        "language-configuration.json",
        "syntaxes/cdfl.tmLanguage.json",
        "snippets/cdfl.json",
    ]:
        json.loads((EXTENSION_ROOT / relative_path).read_text())

    grammar_text = (EXTENSION_ROOT / "syntaxes/cdfl.tmLanguage.json").read_text()
    assert "meta.definition.block.cdfl" in grammar_text
    assert "variable.parameter.key.cdfl" in grammar_text

    readme = (EXTENSION_ROOT / "README.md").read_text()
    assert "Runtime Commands" in readme
    assert "CDFL: Run Current File" in readme
    assert "CDFL: Lint Current File" in readme
    assert "cdfd cdfl ast" in readme
    assert "npx @vscode/vsce package" in readme


def test_cdfl_vscode_extension_javascript_is_syntax_valid():
    result = subprocess.run(
        ["node", "--check", str(EXTENSION_ROOT / "extension.js")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    source = (EXTENSION_ROOT / "extension.js").read_text()
    for marker in [
        "createDiagnosticCollection",
        "registerCompletionItemProvider",
        "registerHoverProvider",
        "registerDocumentSymbolProvider",
        "registerDocumentFormattingEditProvider",
        "cdfl.validateCurrentFile",
        "cdfl.runCurrentFile",
        "cdfl.lintCurrentFile",
        "cdfl.showAst",
        "cdfl.formatViaRuntime",
    ]:
        assert marker in source
