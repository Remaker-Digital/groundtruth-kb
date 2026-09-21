"""Prevent production readers from reviving retired file-backed harness authority."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]

# ===========================================================================
# Part C — no-direct-read scan: no executing read of the legacy harness JSON.
# ===========================================================================

# Roots whose production code must no longer execute a read of the legacy
# harness-state JSON files (the migrated reader surfaces).
_SCAN_ROOTS = (
    "scripts",
    ".harness-baseline-configuration/hooks",
    ".claude/hooks",
    ".codex/gtkb-hooks",
    "groundtruth-kb/src/groundtruth_kb",
)

# Retired role, identity and combined registry projections.
_LEGACY_JSON_FILENAMES = ("role-assignments.json", "harness-identities.json", "harness-registry.json")

# Attribute calls that constitute an executing read of a path.
_READ_ATTRS = frozenset({"read_text", "read_bytes"})


def _legacy_python_files() -> list[Path]:
    """Every production Python file under authored and projected scan roots."""
    files: list[Path] = []
    for root in _SCAN_ROOTS:
        for path in sorted((_REPO_ROOT / root).rglob("*.py")):
            files.append(path)
    return files


def _expr_text(node: ast.AST) -> str:
    """Best-effort source text for an AST node (empty string on failure)."""
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001 - tolerate any unparse edge case
        return ""


def _contains_legacy_filename(node: ast.AST) -> bool:
    """True iff the node's source text mentions a legacy JSON filename."""
    text = _expr_text(node)
    return any(name in text for name in _LEGACY_JSON_FILENAMES)


def _names_in(node: ast.AST) -> set[str]:
    """Return the set of ``Name`` identifiers referenced anywhere in ``node``."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _executing_reads_of_legacy_json(tree: ast.AST) -> list[tuple[int, str]]:
    """Return ``(lineno, expr)`` for every executing read of a legacy JSON file.

    Two-pass deterministic AST analysis:

    * Pass 1 collects names bound to an expression whose source text contains a
      legacy JSON filename (e.g. ``ROLE_ASSIGNMENTS_PATH = root /
      "role-assignments.json"``).
    * Pass 2 finds executing-read calls — ``X.read_text(...)`` /
      ``X.read_bytes(...)``, ``open(X)``, ``json.load(X)`` / ``json.loads(X)`` —
      whose read target ``X`` either textually contains a legacy filename
      (inline read) or references a Pass-1 legacy-path name (constant-then-read).

    Comments and docstrings never appear inside ``Call`` nodes, so they are
    structurally excluded. A string constant assigned to a name that is never
    read (a path constant used only for ``.name`` / ``.is_file()`` / the unused
    legacy file-writers) is likewise not flagged — only an actual executing
    read is reported.
    """
    legacy_path_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _contains_legacy_filename(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    legacy_path_names.add(target.id)
        elif (
            isinstance(node, ast.AnnAssign)
            and node.value is not None
            and isinstance(node.target, ast.Name)
            and _contains_legacy_filename(node.value)
        ):
            legacy_path_names.add(node.target.id)

    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        read_target: ast.AST | None = None
        if isinstance(func, ast.Attribute) and func.attr in _READ_ATTRS:
            read_target = func.value
        elif (
            (
                isinstance(func, ast.Attribute)
                and func.attr in ("load", "loads")
                and isinstance(func.value, ast.Name)
                and func.value.id == "json"
            )
            or isinstance(func, ast.Name)
            and func.id == "open"
        ):
            read_target = node.args[0] if node.args else None
        if read_target is None:
            continue
        target_text = _expr_text(read_target)
        references_legacy_name = bool(_names_in(read_target) & legacy_path_names)
        if _contains_legacy_filename(read_target) or references_legacy_name:
            findings.append((getattr(node, "lineno", -1), target_text[:120]))
    return findings


def test_no_executing_read_of_legacy_harness_json() -> None:
    """Installation metadata and session roles resolve through native services.

    Historical names in comments, docstrings and inert strings do not count as
    executing readers. No compatibility reader is allowed to reopen these files.
    """
    offenders: dict[str, list[tuple[int, str]]] = {}
    for path in _legacy_python_files():
        # utf-8-sig tolerates a UTF-8 BOM so BOM-prefixed files still parse.
        source = path.read_text(encoding="utf-8-sig")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:  # pragma: no cover - defensive
            pytest.fail(f"could not parse {path} for the no-direct-read scan: {exc}")
        findings = _executing_reads_of_legacy_json(tree)
        if findings:
            offenders[path.as_posix()] = findings

    assert not offenders, (
        "Executing reads of retired harness authority files remain; "
        "use the native installation or session service:\n"
        + "\n".join(
            f"  {path}: " + ", ".join(f"line {ln}: {expr}" for ln, expr in finds)
            for path, finds in sorted(offenders.items())
        )
    )


@pytest.mark.parametrize("filename", _LEGACY_JSON_FILENAMES)
def test_no_direct_read_scan_detects_a_planted_executing_read(tmp_path: Path, filename: str) -> None:
    """The no-direct-read scan's detector is not vacuous.

    A planted module that executes a read of ``role-assignments.json`` — both
    inline and via a path constant — must be flagged; a sibling module that
    mentions the filename only in a docstring, a comment, and a static string
    constant (with no executing read) must NOT be flagged.
    """
    # Planted offender: inline read + constant-then-read.
    offender = tmp_path / "planted_offender.py"
    offender.write_text(
        "from pathlib import Path\n"
        "import json\n"
        f"ROLE_PATH = Path('harness-state') / {filename!r}\n"
        "def read_inline(root: Path):\n"
        "    return json.loads((root / 'harness-identities.json').read_text())\n"
        "def read_via_constant():\n"
        "    return ROLE_PATH.read_text(encoding='utf-8')\n",
        encoding="utf-8",
    )
    offender_tree = ast.parse(offender.read_text(encoding="utf-8"))
    offender_findings = _executing_reads_of_legacy_json(offender_tree)
    offender_lines = {ln for ln, _ in offender_findings}
    # The inline json.loads(...read_text()) read and the ROLE_PATH.read_text()
    # constant-then-read are both detected.
    assert 5 in offender_lines, offender_findings
    assert 7 in offender_lines, offender_findings

    # Clean sibling: legacy filename only in docstring / comment / static const.
    clean = tmp_path / "clean_sibling.py"
    clean.write_text(
        '"""References harness-state/role-assignments.json in this docstring."""\n'
        "# harness-state/harness-identities.json mentioned only in a comment\n"
        "LEGACY_NAME = 'role-assignments.json'  # static constant, never read\n"
        "def describe() -> str:\n"
        "    return LEGACY_NAME\n",
        encoding="utf-8",
    )
    clean_tree = ast.parse(clean.read_text(encoding="utf-8"))
    assert _executing_reads_of_legacy_json(clean_tree) == []
