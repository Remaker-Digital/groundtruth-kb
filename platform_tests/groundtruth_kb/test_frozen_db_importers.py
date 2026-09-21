"""Guard the importer set of the frozen ``groundtruth_kb.db`` module (owner ruling D23, 2026-09-17).

``groundtruth_kb.db`` stays as the frozen export/migration schema. Its runtime
importers are pinned to the one module whose port is explicitly deferred, and
its ``TYPE_CHECKING``-only importers are pinned to the allow-list recorded with
increment c103 (retirement-f19-live-readers). Any new importer must either join
the allow-list here (with its own ruling) or read through the native
repositories instead.

The scan is static (``ast``): it never imports the package or opens a store.
"""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb"
FROZEN_MODULE = "groundtruth_kb.db"

# Runtime importers whose native port is deferred by name (the doctor readers were ported or
# retired by owner ruling D31, 2026-09-19, so project/doctor.py no longer imports the frozen module).
EXPECTED_RUNTIME_IMPORTERS = frozenset(
    {
        "project/chroma.py",  # HAS_CHROMADB/_load_chromadb loader; relocation deferred to the port pass
    }
)

# Importers that only name KnowledgeDB under ``if TYPE_CHECKING:`` (annotations).
ALLOW_LISTED_TYPE_CHECKING_IMPORTERS = frozenset(
    {
        "adr_harness.py",
        "adr_scaffold.py",
        "canonical_terms.py",
        "impact.py",
        "seed.py",
        "spec_scaffold.py",
    }
)


def _is_type_checking_test(test: ast.expr) -> bool:
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def _module_package(path: Path) -> list[str]:
    """Dotted package parts that relative imports in ``path`` resolve against."""
    relative = path.relative_to(PACKAGE_ROOT.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    else:
        parts.pop()  # the module's own name is not part of its package
    return parts


def _resolved_target(node: ast.ImportFrom, package: list[str]) -> str:
    if node.level == 0:
        return node.module or ""
    base = package[: len(package) - (node.level - 1)] if node.level > 1 else list(package)
    if node.module:
        base = base + node.module.split(".")
    return ".".join(base)


def _imports_frozen_module(node: ast.Import | ast.ImportFrom, package: list[str]) -> bool:
    if isinstance(node, ast.Import):
        return any(alias.name == FROZEN_MODULE or alias.name.startswith(FROZEN_MODULE + ".") for alias in node.names)
    target = _resolved_target(node, package)
    if target == FROZEN_MODULE:
        return True
    parent, _, leaf = FROZEN_MODULE.rpartition(".")
    return target == parent and any(alias.name == leaf for alias in node.names)


class _ImporterScan(ast.NodeVisitor):
    def __init__(self, package: list[str]) -> None:
        self._package = package
        self._type_checking_depth = 0
        self.runtime = False
        self.type_checking = False

    def visit_If(self, node: ast.If) -> None:
        if _is_type_checking_test(node.test):
            self._type_checking_depth += 1
            for statement in node.body:
                self.visit(statement)
            self._type_checking_depth -= 1
            for statement in node.orelse:
                self.visit(statement)
            return
        self.generic_visit(node)

    def _record(self, node: ast.Import | ast.ImportFrom) -> None:
        if not _imports_frozen_module(node, self._package):
            return
        if self._type_checking_depth:
            self.type_checking = True
        else:
            self.runtime = True

    def visit_Import(self, node: ast.Import) -> None:
        self._record(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._record(node)


def _scan_importers() -> tuple[set[str], set[str]]:
    runtime: set[str] = set()
    type_checking: set[str] = set()
    frozen_path = PACKAGE_ROOT / "db.py"
    assert frozen_path.is_file(), f"frozen module missing: {frozen_path}"
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        if path == frozen_path:
            continue
        scan = _ImporterScan(_module_package(path))
        scan.visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
        relative = path.relative_to(PACKAGE_ROOT).as_posix()
        if scan.runtime:
            runtime.add(relative)
        if scan.type_checking:
            type_checking.add(relative)
    return runtime, type_checking


def test_runtime_importers_of_frozen_db_are_pinned() -> None:
    runtime, _ = _scan_importers()
    unexpected = sorted(runtime - EXPECTED_RUNTIME_IMPORTERS)
    missing = sorted(EXPECTED_RUNTIME_IMPORTERS - runtime)
    assert not unexpected, f"new runtime importer(s) of {FROZEN_MODULE}: {unexpected}"
    assert not missing, f"deferred runtime importer(s) no longer import {FROZEN_MODULE}; update the pin: {missing}"


def test_type_checking_importers_of_frozen_db_are_allow_listed() -> None:
    _, type_checking = _scan_importers()
    unexpected = sorted(type_checking - ALLOW_LISTED_TYPE_CHECKING_IMPORTERS)
    missing = sorted(ALLOW_LISTED_TYPE_CHECKING_IMPORTERS - type_checking)
    assert not unexpected, f"TYPE_CHECKING importer(s) of {FROZEN_MODULE} outside the allow-list: {unexpected}"
    assert not missing, f"allow-listed module(s) no longer import {FROZEN_MODULE}; update the allow-list: {missing}"


def test_allow_listed_importers_never_import_at_runtime() -> None:
    runtime, _ = _scan_importers()
    promoted = sorted(runtime & ALLOW_LISTED_TYPE_CHECKING_IMPORTERS)
    assert not promoted, f"allow-listed TYPE_CHECKING importer(s) now import {FROZEN_MODULE} at runtime: {promoted}"
