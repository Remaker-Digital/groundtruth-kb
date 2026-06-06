from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED_FILENAME = "-".join(("role", "assignments.json"))
RETIRED_PATH = ROOT / "harness-state" / RETIRED_FILENAME
RETIRED_TOKEN = "/".join(("harness-state", RETIRED_FILENAME))
PRODUCTION_SCAN_ROOTS = (
    ROOT / "scripts",
    ROOT / "groundtruth-kb" / "src",
)
READ_WRITE_METHODS = frozenset({"open", "read_text", "read_bytes", "write_text", "write_bytes"})


def test_retired_role_assignments_file_absent() -> None:
    assert not RETIRED_PATH.exists()


def test_protected_artifact_drift_registry_drops_retired_mirror() -> None:
    registry = ROOT / "config" / "governance" / "protected-artifact-inventory-drift.toml"

    assert RETIRED_TOKEN not in registry.read_text(encoding="utf-8")


def test_dev_environment_inventory_uses_harness_registry_evidence() -> None:
    inventory = json.loads(
        (ROOT / ".groundtruth" / "inventory" / "dev-environment-inventory.json").read_text(encoding="utf-8")
    )
    rendered = json.dumps(inventory, sort_keys=True)

    assert RETIRED_TOKEN not in rendered
    assert "harness-state/harness-registry.json" in rendered


def test_role_writer_does_not_recreate_retired_mirror(tmp_path: Path) -> None:
    from scripts.harness_roles import ROLE_PRIME_BUILDER, write_role_assignments

    document = {
        "schema_version": 1,
        "harnesses": {
            "A": {"role": [ROLE_PRIME_BUILDER]},
        },
    }

    returned_path = write_role_assignments(tmp_path, document)

    assert returned_path == tmp_path / "harness-state" / "harness-registry.json"
    assert not (tmp_path / "harness-state" / RETIRED_FILENAME).exists()


def _contains_retired_path(node: ast.AST, retired_names: set[str]) -> bool:
    try:
        rendered = ast.unparse(node)
    except Exception:  # pragma: no cover - defensive scan fallback
        rendered = ""
    normalized = rendered.replace("\\", "/")
    if RETIRED_TOKEN in normalized or RETIRED_FILENAME in normalized:
        return True
    return any(isinstance(child, ast.Name) and child.id in retired_names for child in ast.walk(node))


def _assigned_names_for_retired_path(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _contains_retired_path(node.value, set()):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and node.value is not None and _contains_retired_path(node.value, set()):
            if isinstance(node.target, ast.Name):
                names.add(node.target.id)
    return names


def _live_retired_path_reads_or_writes(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    retired_names = _assigned_names_for_retired_path(tree)
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        target: ast.AST | None = None
        if isinstance(func, ast.Attribute) and func.attr in READ_WRITE_METHODS:
            target = func.value
        elif isinstance(func, ast.Name) and func.id == "open":
            target = node.args[0] if node.args else None
        if target is None:
            continue
        if _contains_retired_path(target, retired_names):
            try:
                rendered = ast.unparse(node)
            except Exception:  # pragma: no cover - defensive scan fallback
                rendered = "<unparseable call>"
            findings.append((node.lineno, rendered[:160]))
    return findings


def _production_python_files() -> list[Path]:
    paths: list[Path] = []
    for root in PRODUCTION_SCAN_ROOTS:
        paths.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(paths)


def test_no_live_python_reader_or_writer_uses_retired_mirror() -> None:
    offenders: dict[str, list[tuple[int, str]]] = {}
    for path in _production_python_files():
        findings = _live_retired_path_reads_or_writes(path)
        if findings:
            offenders[path.relative_to(ROOT).as_posix()] = findings

    assert not offenders, "Live production Python still reads or writes the retired role mirror:\n" + "\n".join(
        f"{path}: " + ", ".join(f"line {line}: {expr}" for line, expr in findings)
        for path, findings in offenders.items()
    )
