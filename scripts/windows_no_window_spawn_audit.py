#!/usr/bin/env python3
"""Audit Python subprocess launch sites for Windows visible-console risk.

The scanner is intentionally conservative for release-runtime surfaces:
background hooks, dispatcher, daemon, and bridge launch paths must either pass
an explicit Windows no-window disposition (``creationflags`` or
``startupinfo``) or be reported as violations. Test, archive, adopter, and
explicitly interactive tooling is classified separately so the release gate can
focus on owner-focus-stealing launchers without losing inventory coverage.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

NO_WINDOW_KEYWORDS = {"creationflags", "startupinfo"}
NO_WINDOW_KWARGS_HELPERS = {"_no_window_run_kwargs", "_no_window_subprocess_kwargs"}
LAUNCH_CALLS = {
    "subprocess.Popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "os.popen",
    "os.startfile",
    "os.system",
}

NON_RELEASE_PREFIXES = (
    ".api-harness/",
    ".claude/skills/",
    ".codex/skills/",
    ".cursor/skills/",
    "applications/",
    "archive/",
    "groundtruth-kb/examples/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "tests/",
)

RELEASE_RUNTIME_FILES = {
    "groundtruth-kb/src/groundtruth_kb/cli.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/launcher.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/poller.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/worker.py",
    "scripts/cross_harness_bridge_trigger.py",
    "scripts/cursor_harness.py",
    "scripts/ensure_dispatcher_daemon.py",
    "scripts/gtkb_dispatcher_daemon.py",
    "scripts/ollama_harness.py",
    "scripts/openrouter_harness.py",
    "scripts/run_with_status.py",
    "scripts/single_harness_bridge_dispatcher.py",
    "scripts/verify_ollama_dispatch.py",
}

RELEASE_RUNTIME_PREFIXES = (
    ".claude/hooks/",
    ".codex/gtkb-hooks/",
    "groundtruth-kb/src/groundtruth_kb/dispatcher/",
)

INTERACTIVE_TOOL_PREFIXES = (
    "scripts/",
    "groundtruth-kb/src/groundtruth_kb/project/",
)


@dataclass(frozen=True)
class SpawnFinding:
    path: str
    line: int
    column: int
    call: str
    state: str
    reason: str
    no_window: bool


def _windows_creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _no_window_run_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    creationflags = _windows_creationflags()
    if creationflags:
        kwargs["creationflags"] = creationflags
    return kwargs


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _normalize_path(path: Path, root: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = path
    return rel.as_posix()


def _string_literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _subscript_key(node: ast.AST) -> str | None:
    if isinstance(node, ast.Subscript):
        return _string_literal(node.slice)
    return None


def _kwargs_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "cast"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Name)
    ):
        return node.args[1].id
    return None


def _is_no_window_kwargs_helper_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id in NO_WINDOW_KWARGS_HELPERS
    if isinstance(node.func, ast.Attribute):
        return node.func.attr in NO_WINDOW_KWARGS_HELPERS
    return False


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return f"{func.value.id}.{func.attr}"
    return None


def _dict_has_no_window_key(node: ast.AST) -> bool:
    if not isinstance(node, ast.Dict):
        return False
    return any(_string_literal(key) in NO_WINDOW_KEYWORDS for key in node.keys)


class _Scope:
    def __init__(self) -> None:
        self.no_window_kwargs_names: set[str] = set()


class _NoWindowAssignmentCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        if _dict_has_no_window_key(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.names.add(target.id)
        for target in node.targets:
            self._visit_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        if isinstance(node.target, ast.Name) and node.value is not None and _dict_has_no_window_key(node.value):
            self.names.add(node.target.id)
        self._visit_target(node.target)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "update"
            and isinstance(node.func.value, ast.Name)
            and node.args
            and _dict_has_no_window_key(node.args[0])
        ):
            self.names.add(node.func.value.id)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "setdefault"
            and isinstance(node.func.value, ast.Name)
            and node.args
            and _string_literal(node.args[0]) in NO_WINDOW_KEYWORDS
        ):
            self.names.add(node.func.value.id)
        self.generic_visit(node)

    def _visit_target(self, target: ast.AST) -> None:
        if not isinstance(target, ast.Subscript):
            return
        if _subscript_key(target) not in NO_WINDOW_KEYWORDS:
            return
        if isinstance(target.value, ast.Name):
            self.names.add(target.value.id)


def _scope_for_node(node: ast.AST) -> _Scope:
    collector = _NoWindowAssignmentCollector()
    collector.visit(node)
    scope = _Scope()
    scope.no_window_kwargs_names = collector.names
    return scope


def _call_has_no_window(call: ast.Call, scope: _Scope) -> bool:
    for keyword in call.keywords:
        if keyword.arg in NO_WINDOW_KEYWORDS:
            return True
        if keyword.arg is None:
            if _is_no_window_kwargs_helper_call(keyword.value):
                return True
            name = _kwargs_name(keyword.value)
            if name and name in scope.no_window_kwargs_names:
                return True
    return False


def _is_non_release_path(rel_path: str) -> bool:
    return rel_path.startswith(NON_RELEASE_PREFIXES)


def _is_release_runtime_path(rel_path: str) -> bool:
    return rel_path in RELEASE_RUNTIME_FILES or rel_path.startswith(RELEASE_RUNTIME_PREFIXES)


def _classification(rel_path: str, call_name: str, has_no_window: bool) -> tuple[str, str]:
    if has_no_window:
        return "compliant_no_window", "explicit creationflags/startupinfo or kwargs carrying one"
    if _is_non_release_path(rel_path):
        return "non_release_runtime", "test, archive, skill, fixture, or adopter path"
    if _is_release_runtime_path(rel_path):
        return "violation", "release-runtime launcher lacks Windows no-window disposition"
    if call_name in {"os.system", "os.popen", "os.startfile"}:
        return "interactive_allowlist", "non-release utility shell/open call; not dispatcher or hook runtime"
    if rel_path.startswith(INTERACTIVE_TOOL_PREFIXES):
        return "interactive_allowlist", "support or operator-invoked tooling outside release-runtime dispatch path"
    return "non_release_runtime", "outside release-runtime dispatch and hook path"


class _LaunchVisitor(ast.NodeVisitor):
    def __init__(self, rel_path: str) -> None:
        self.rel_path = rel_path
        self.findings: list[SpawnFinding] = []
        self._scopes: list[_Scope] = []

    def visit_Module(self, node: ast.Module) -> None:  # noqa: N802
        self._scopes.append(_scope_for_node(node))
        self.generic_visit(node)
        self._scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._scopes.append(_scope_for_node(node))
        self.generic_visit(node)
        self._scopes.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self.visit_FunctionDef(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        call_name = _call_name(node)
        if call_name in LAUNCH_CALLS:
            scope = self._scopes[-1] if self._scopes else _Scope()
            no_window = _call_has_no_window(node, scope)
            state, reason = _classification(self.rel_path, call_name, no_window)
            self.findings.append(
                SpawnFinding(
                    path=self.rel_path,
                    line=node.lineno,
                    column=node.col_offset,
                    call=call_name,
                    state=state,
                    reason=reason,
                    no_window=no_window,
                )
            )
        self.generic_visit(node)


def scan_file(path: Path, *, root: Path | None = None) -> list[SpawnFinding]:
    root = root or _repo_root()
    rel_path = _normalize_path(path, root)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(text, filename=rel_path)
    visitor = _LaunchVisitor(rel_path)
    visitor.visit(tree)
    return visitor.findings


def _tracked_python_files(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        **_no_window_run_kwargs(),
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "git ls-files failed").strip())
    return [root / line.strip() for line in completed.stdout.splitlines() if line.strip()]


def scan_paths(paths: Iterable[Path], *, root: Path | None = None) -> list[SpawnFinding]:
    root = root or _repo_root()
    findings: list[SpawnFinding] = []
    for path in paths:
        findings.extend(scan_file(path, root=root))
    return sorted(findings, key=lambda finding: (finding.state == "violation", finding.path, finding.line))


def _summary(findings: list[SpawnFinding]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.state] = counts.get(finding.state, 0) + 1
    violations = [finding for finding in findings if finding.state == "violation"]
    return {
        "total_findings": len(findings),
        "counts": dict(sorted(counts.items())),
        "violation_count": len(violations),
        "release_ready": not violations,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit Python launch sites for Windows no-window compliance")
    parser.add_argument("--root", type=Path, default=_repo_root(), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional file paths to scan instead of tracked Python")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    paths = (
        [path if path.is_absolute() else root / path for path in args.paths]
        if args.paths
        else _tracked_python_files(root)
    )
    findings = scan_paths(paths, root=root)
    payload = {"summary": _summary(findings), "findings": [asdict(finding) for finding in findings]}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print(json.dumps(summary, sort_keys=True))
        for finding in findings:
            if finding.state == "violation":
                print(f"{finding.path}:{finding.line}: {finding.call}: {finding.reason}")
    return 1 if payload["summary"]["violation_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
