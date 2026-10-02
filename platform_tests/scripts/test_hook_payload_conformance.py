"""Every route hands the content hooks Claude's PreToolUse shape (c123; batch design WP2, G38).

Before c123 four routes reached the content hooks in shapes the hooks did not read. The API harnesses sent the model's
raw arguments (``path``), which the provenance gate and the scanner-safe writer never read, so neither judged an API
harness's Write. Goose's edits arrived without their strings, Codex's apply_patch text sat in ``command``, which the
credential scan never read, and Cursor's writes and edits were rebuilt with the path alone. Each route now translates to
the canonical keys (file_path, content, old_string and new_string, patch, command), and the hooks read through shared
readers that also accept every key a route has used. These tests take each route's payload through the route's own
translation, then run the real content hooks on what the routes deliver.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest

from scripts import antigravity_hook_adapter as antigravity
from scripts import cloud_harness_base as base
from scripts import codex_hook_adapter as codex
from scripts import goose_hook_adapter as goose
from scripts import ollama_harness as ollama


def _import_cursor_adapter():
    """Import the Cursor adapter without keeping the scripts folder its module code puts on sys.path.

    The API harnesses try ``import cloud_harness_base`` before ``scripts.cloud_harness_base``; with that folder left on
    sys.path a harness imported later in the session would load a second base, which the other modules' fixtures do
    not patch.
    """
    saved = list(sys.path)
    try:
        return importlib.import_module("scripts.cursor_hook_adapter")
    finally:
        sys.path[:] = saved


cursor = _import_cursor_adapter()
ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".harness-baseline-configuration" / "hooks"
PATCH = "*** Begin Patch\n*** Add File: docs/new.md\n+# Missing provenance\n*** End Patch\n"
# Built at runtime, as in test_credential_scan.py, so writing this file does not trip the scanners.
FQDN = "".join(['"https://agent-red-api', "-gateway.abc123.eastus", '.azurecontainerapps.io/api"'])
BEARER = "Bearer " + "synthetic-fixture"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


READERS = _load("hook_context_payload_conformance", HOOKS / "_hook_context.py")


# The shared readers.


@pytest.mark.parametrize(
    ("tool_input", "path", "content"),
    [
        ({"file_path": "a.md", "content": "text"}, "a.md", "text"),  # Claude, and every adapter's output
        ({"path": "a.md", "content": "text"}, "a.md", "text"),  # an API harness model's raw arguments
        ({"path": "a.md", "file_text": "text"}, "a.md", "text"),  # Goose's text editor
        ({"path": "a.md", "contents": "text"}, "a.md", "text"),
        ({"TargetFile": "a.md", "CodeContent": "text"}, "a.md", "text"),  # Antigravity's write_to_file
        ({"file_path": 7, "path": "a.md", "content": None, "contents": "text"}, "a.md", "text"),  # not text: skipped
        ({}, "", ""),
    ],
)
def test_the_readers_take_the_path_and_the_written_text_under_every_route_key(tool_input, path, content):
    assert READERS.tool_path(tool_input) == path
    assert READERS.write_content(tool_input) == content


@pytest.mark.parametrize(
    ("tool_input", "new_text"),
    [
        ({"new_string": "b"}, "b"),
        ({"new_text": "b"}, "b"),
        ({"new_str": "b"}, "b"),  # Goose's text editor
        ({"after": "b"}, "b"),  # Goose's edit
        ({"ReplacementContent": "b"}, "b"),  # Antigravity's replace_file_content
        ({"edits": [{"new_string": "b"}, {"old_string": "x"}, {"new_string": "c"}, "not an edit"]}, "b\nc"),
        ({"new_string": "a", "edits": [{"new_string": "b"}]}, "a\nb"),
        ({"old_string": "a"}, ""),
    ],
)
def test_the_edit_reader_takes_every_text_an_edit_writes(tool_input, new_text):
    assert READERS.edit_new_text(tool_input) == new_text


@pytest.mark.parametrize(
    "payload",
    [
        {"tool_input": {"patch": PATCH}},
        {"tool_input": {"command": PATCH}},  # Codex's native apply_patch
        {"tool_input": {"input": PATCH}},
        {"tool_input": {"arguments": {"input": PATCH}}},
        {"input": {"patch": PATCH}},
        {"tool_input": {}, "patch": PATCH},
    ],
)
def test_the_patch_reader_finds_a_patch_under_every_route_key(payload):
    assert READERS.patch_text(payload) == PATCH


def test_the_patch_reader_ignores_a_command_without_a_patch():
    assert READERS.patch_text({"tool_input": {"command": "echo hi"}}) == ""


# Each route's own translation.


def _goose(tool: str, tool_input: dict, root: Path = ROOT) -> dict:
    """Goose 1.45.0's PreToolUse payload through the Goose adapter."""
    payload = {"session_id": "s", "tool_name": tool, "tool_input": tool_input, "working_dir": str(root)}
    adapted = goose._normalize(payload)
    assert adapted is not None
    return adapted


def _codex(tool_input: dict, root: Path = ROOT) -> dict:
    """Codex's native apply_patch payload through the Codex adapter."""
    return codex._payload(
        {"session_id": "s", "cwd": str(root), "tool_name": "apply_patch", "tool_input": tool_input}, "PreToolUse"
    )


def _cursor(tool: str, tool_input: dict, root: Path = ROOT) -> dict:
    """A Cursor 3.21.18 preToolUse payload through the Cursor adapter."""
    payload = {"conversation_id": "c", "tool_name": tool, "tool_input": tool_input, "cwd": str(root)}
    return cursor._to_claude_pretooluse(payload)


def _antigravity(name: str, args: dict) -> dict:
    """An Antigravity tool call through the Antigravity adapter (its paths are absolute)."""
    payload = {
        "conversationId": "c",
        "workspacePaths": [str(antigravity.PROJECT_ROOT)],
        "toolCall": {"name": name, "args": args},
    }
    return antigravity._native_payload(payload, "PreToolUse")


def _api(tool: str, tool_input: dict, root: Path) -> dict:
    """An API harness tool call as the shared base hands it to the native hooks."""
    metadata = base.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture")
    return base._native_hook_payload(
        base.NATIVE_HOOK_PRE_TOOL_USE,
        metadata,
        root,
        ollama._OLLAMA_HOOK_PROFILE,
        tool_name=tool,
        tool_input=tool_input,
    )


@pytest.mark.parametrize(
    ("tool", "tool_input", "expected"),
    [
        ("write", {"path": "a.md", "content": "t"}, {"file_path": "a.md", "content": "t"}),
        (
            "edit",
            {"path": "a.md", "before": "x", "after": "y"},
            {"file_path": "a.md", "old_string": "x", "new_string": "y"},
        ),
        (
            "developer__text_editor",
            {"command": "write", "path": "a.md", "file_text": "t"},
            {"file_path": "a.md", "content": "t"},
        ),
        (
            "developer__text_editor",
            {"command": "str_replace", "path": "a.md", "old_str": "x", "new_str": "y"},
            {"file_path": "a.md", "old_string": "x", "new_string": "y"},
        ),
        (
            "developer__text_editor",
            {"command": "insert", "path": "a.md", "insert_line": 1, "new_str": "y"},
            {"file_path": "a.md", "new_string": "y"},
        ),
    ],
)
def test_goose_writes_and_edits_reach_the_hooks_with_their_text(tool, tool_input, expected):
    assert _goose(tool, tool_input)["tool_input"] == expected


def test_codex_apply_patch_text_is_also_the_canonical_patch():
    native = {"command": PATCH}
    assert _codex(native)["tool_input"] == {"command": PATCH, "patch": PATCH}
    assert native == {"command": PATCH}, "the native payload itself is not changed"


def test_cursor_writes_and_edits_keep_their_text():
    edit = _cursor("StrReplace", {"path": "README.md", "old_string": "a", "new_string": "b"})
    assert edit["tool_name"] == "Edit"
    assert edit["tool_input"] == {"path": "README.md", "file_path": "README.md", "old_string": "a", "new_string": "b"}
    write = _cursor("Write", {"path": "a.md", "content": "t"})
    assert write["tool_name"] == "Write"
    assert write["tool_input"] == {"path": "a.md", "file_path": "a.md", "content": "t"}


def test_antigravity_writes_and_edits_reach_the_hooks_with_their_text(tmp_path):
    target = str(tmp_path / "a.md")
    write = _antigravity("write_to_file", {"TargetFile": target, "CodeContent": "t"})
    assert (write["tool_name"], write["tool_input"]) == ("Write", {"file_path": target, "content": "t"})
    edit = _antigravity("replace_file_content", {"TargetFile": target, "TargetContent": "x", "ReplacementContent": "y"})
    assert (edit["tool_name"], edit["tool_input"]) == (
        "Edit",
        {"file_path": target, "old_string": "x", "new_string": "y", "replace_all": False},
    )


def test_api_harness_file_tools_reach_the_hooks_in_the_canonical_shape(tmp_path):
    root = tmp_path.resolve()
    write = _api("Write", {"path": "docs/new.md", "content": "t"}, root)["tool_input"]
    assert write == {"path": "docs/new.md", "file_path": str(root / "docs" / "new.md"), "content": "t"}
    (root / "a.txt").write_text("x", encoding="utf-8")
    edit = _api("Edit", {"path": "a.txt", "old_string": "x", "new_string": "y"}, root)["tool_input"]
    assert edit == {"path": "a.txt", "file_path": str(root / "a.txt"), "old_string": "x", "new_string": "y"}
    assert _api("Read", {"path": "a.txt"}, root)["tool_input"] == {"path": "a.txt", "file_path": str(root / "a.txt")}
    assert _api("Bash", {"command": "echo hi"}, root)["tool_input"] == {"command": "echo hi"}
    assert _api("Glob", {"pattern": "*.md"}, root)["tool_input"] == {"pattern": "*.md"}


@pytest.mark.parametrize("tool", ["Edit", "Read"])
@pytest.mark.parametrize("path", ["missing.txt", "../outside.txt", "", "a\x00b"])
def test_an_api_file_call_whose_path_cannot_be_resolved_reaches_the_hooks_as_it_came(tmp_path, tool, path):
    """Building the hook payload never ends the run; the tool itself refuses such a call."""
    tool_input = {"path": path, "old_string": "x", "new_string": "y"} if tool == "Edit" else {"path": path}
    assert _api(tool, tool_input, tmp_path.resolve())["tool_input"] == tool_input


# The real content hooks on what each route delivers.


def _hook(name: str, payload: dict, tmp_path: Path) -> dict:
    """Run one authored hook as the harnesses do, outside the repository, with its denial log under tmp_path."""
    package_parent = str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(filter(None, (package_parent, os.environ.get("PYTHONPATH")))),
        "PYTHONIOENCODING": "utf-8",
        "GTKB_GATE_DENIALS_PATH": str(tmp_path / "gate-denials.jsonl"),
    }
    done = subprocess.run(
        [sys.executable, "-B", str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        env=env,
        timeout=60,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def _deny_reason(reply: dict) -> str:
    decision = reply.get("hookSpecificOutput") or {}
    assert decision.get("permissionDecision") == "deny", reply
    return str(decision.get("permissionDecisionReason"))


MISSING_PROVENANCE = "# Missing provenance\n"


def _new_document(route: str, root: Path) -> dict:
    """A Write of a new governed Markdown document without provenance metadata, as ``route`` delivers it."""
    if route == "claude":
        return {"tool_name": "Write", "tool_input": {"file_path": "docs/new.md", "content": MISSING_PROVENANCE}}
    if route == "api arguments":
        return {"tool_name": "Write", "tool_input": {"path": "docs/new.md", "content": MISSING_PROVENANCE}}
    if route == "api harness":
        return _api("Write", {"path": "docs/new.md", "content": MISSING_PROVENANCE}, root)
    if route == "goose write":
        return _goose("write", {"path": "docs/new.md", "content": MISSING_PROVENANCE}, root)
    if route == "goose text editor":
        arguments = {"command": "create", "path": "docs/new.md", "file_text": MISSING_PROVENANCE}
        return _goose("developer__text_editor", arguments, root)
    if route == "codex apply_patch":
        return _codex({"command": PATCH}, root)
    if route == "cursor":
        return _cursor("Write", {"path": "docs/new.md", "content": MISSING_PROVENANCE}, root)
    assert route == "antigravity"
    return _antigravity(
        "write_to_file", {"TargetFile": str(root / "docs" / "new.md"), "CodeContent": MISSING_PROVENANCE}
    )


@pytest.mark.parametrize(
    "route",
    [
        "claude",
        "api arguments",
        "api harness",
        "goose write",
        "goose text editor",
        "codex apply_patch",
        "cursor",
        "antigravity",
    ],
)
def test_the_provenance_gate_judges_a_new_governed_document_from_every_route(tmp_path, route):
    root = tmp_path.resolve() / "project"
    root.mkdir()
    payload = _new_document(route, root)
    payload["cwd"] = str(root)
    assert "docs/new.md" in _deny_reason(_hook("document_author_provenance_gate.py", payload, tmp_path))
    assert not (root / "docs").exists()


def _credential_call(route: str, root: Path) -> dict:
    """A Write, an Edit or a patch that writes a credential-shaped string, as ``route`` delivers it."""
    if route == "api arguments":
        return {"tool_name": "Write", "tool_input": {"path": "src/config.py", "content": FQDN}}
    if route == "api harness write":
        return _api("Write", {"path": "src/config.py", "content": FQDN}, root)
    if route == "api harness edit":
        (root / "src").mkdir()
        (root / "src" / "config.py").write_text("URL = None\n", encoding="utf-8")
        return _api("Edit", {"path": "src/config.py", "old_string": "None", "new_string": FQDN}, root)
    if route == "goose edit":
        return _goose("edit", {"path": "src/config.py", "before": "x", "after": FQDN})
    if route == "goose text editor":
        return _goose("developer__text_editor", {"command": "insert", "path": "src/config.py", "new_str": FQDN})
    if route == "codex apply_patch":
        patch = f"*** Begin Patch\n*** Add File: src/config.py\n+URL = {FQDN}\n*** End Patch\n"
        return {"tool_name": "apply_patch", "tool_input": _codex({"command": patch})["tool_input"]}
    if route == "cursor StrReplace":
        return _cursor("StrReplace", {"path": "src/config.py", "old_string": "x", "new_string": FQDN})
    if route == "antigravity edit":
        arguments = {"TargetFile": str(root / "src" / "config.py"), "TargetContent": "x", "ReplacementContent": FQDN}
        return _antigravity("replace_file_content", arguments)
    assert route == "multi edit"
    return {"tool_name": "MultiEdit", "tool_input": {"file_path": "src/config.py", "edits": [{"new_string": FQDN}]}}


@pytest.mark.parametrize(
    "route",
    [
        "api arguments",
        "api harness write",
        "api harness edit",
        "goose edit",
        "goose text editor",
        "codex apply_patch",
        "cursor StrReplace",
        "antigravity edit",
        "multi edit",
    ],
)
def test_the_credential_scan_reads_the_text_from_every_route(tmp_path, route):
    root = tmp_path.resolve() / "project"
    root.mkdir()
    payload = _credential_call(route, root)
    assert _deny_reason(_hook("credential-scan.py", payload, tmp_path)).startswith("credential_detected")


def test_the_credential_scan_reads_codex_patch_text_without_the_adapter(tmp_path):
    """The reader also finds the patch in the native command, so a route that skips the copy is still judged."""
    patch = f"*** Begin Patch\n*** Add File: src/config.py\n+URL = {FQDN}\n*** End Patch\n"
    payload = {"tool_name": "apply_patch", "tool_input": {"command": patch}}
    assert _deny_reason(_hook("credential-scan.py", payload, tmp_path)).startswith("credential_detected")


@pytest.mark.parametrize("value", [None, 7])
def test_a_write_whose_content_is_not_text_is_still_refused_by_the_credential_scan(tmp_path, value):
    payload = {"tool_name": "Write", "tool_input": {"file_path": "src/config.py", "content": value}}
    assert _deny_reason(_hook("credential-scan.py", payload, tmp_path)).startswith("credential_input_invalid")


@pytest.mark.parametrize("route", ["api arguments", "api harness"])
def test_the_scanner_safe_writer_judges_an_api_harness_bridge_write(tmp_path, route):
    root = tmp_path.resolve() / "project"
    root.mkdir()
    if route == "api arguments":
        payload = {"tool_name": "Write", "tool_input": {"path": "bridge/fixture.md", "content": BEARER}}
    else:
        payload = _api("Write", {"path": "bridge/fixture.md", "content": BEARER}, root)
    payload["project_root"] = str(root)
    assert "scanner-safe-writer" in _deny_reason(_hook("scanner-safe-writer.py", payload, tmp_path))
    assert len((tmp_path / "gate-denials.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    assert not (root / "bridge").exists()
