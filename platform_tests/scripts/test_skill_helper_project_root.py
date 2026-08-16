"""Every skill-helper module must resolve the repository root, never an ancestor.

WI-6444 Part A. Six helper modules under ``scripts/skill-helpers/`` computed
their project root with ``Path(__file__).resolve().parents[4]``. Those modules
sit three levels below the repository root, so index 4 resolved one level
*above* the root -- to the drive root on Windows. Every derived path (bridge
directory, draft directory, ``sys.path`` inserts, helper lookups) therefore
pointed outside the mandatory project-root boundary, and ``revise_bridge.py``
was outright inoperable.

The test enumerates the tree rather than hard-coding the modules that existed
when it was written, so a ninth module copied in at the wrong depth fails
immediately instead of silently inheriting the defect.

Two resolution styles are accepted:

* a marker-walking resolver that ascends until it finds a stable repository
  marker file, which is correct at any depth; or
* a bare ``parents[N]`` index, which must equal the module's actual depth.

Specifications: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (project-root
boundary), GOV-FILE-BRIDGE-AUTHORITY-001 (bridge helper invocability),
GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (canonical reader entrypoints).
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

# The marker used to identify the repository root by upward walk. It is a
# tracked, load-bearing file that has no counterpart above the root.
ROOT_MARKER_PARTS = ("scripts", "bridge_author_metadata.py")

# Module-level names that hold a computed project/repository root.
ROOT_BINDING_NAMES = frozenset({"PROJECT_ROOT", "_PROJECT_ROOT", "REPO_ROOT", "_REPO_ROOT"})


def _discover_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if parent.joinpath(*ROOT_MARKER_PARTS).is_file():
            return parent
    raise RuntimeError(f"repository root not found by walking parents for {'/'.join(ROOT_MARKER_PARTS)}")


REPO_ROOT = _discover_repo_root()
SKILL_HELPER_DIR = REPO_ROOT / "scripts" / "skill-helpers"


def _skill_helper_modules() -> list[Path]:
    if not SKILL_HELPER_DIR.is_dir():
        return []
    return sorted(p for p in SKILL_HELPER_DIR.rglob("*.py") if p.is_file())


def _expected_parents_index(module: Path) -> int:
    """Return the ``parents[N]`` index that resolves to the repository root.

    ``scripts/skill-helpers/<skill>/<module>.py`` has four relative parts, so
    ``parents[3]`` is the repository root: [0]=<skill>, [1]=skill-helpers,
    [2]=scripts, [3]=root.
    """
    return len(module.resolve().relative_to(REPO_ROOT).parts) - 1


def _parents_index(node: ast.AST) -> int | None:
    """Return N for a ``...parents[N]`` subscript, else None."""
    if not isinstance(node, ast.Subscript):
        return None
    value = node.value
    if not (isinstance(value, ast.Attribute) and value.attr == "parents"):
        return None
    index = node.slice
    if isinstance(index, ast.Constant) and isinstance(index.value, int):
        return index.value
    return None


def _walks_for_marker(tree: ast.Module, func_name: str) -> bool:
    """True when ``func_name`` ascends parents testing a filesystem marker."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != func_name:
            continue
        has_parents_loop = any(
            isinstance(inner, ast.For) and isinstance(inner.iter, ast.Attribute) and inner.iter.attr == "parents"
            for inner in ast.walk(node)
        )
        has_marker_probe = any(
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr in {"is_file", "exists", "is_dir"}
            for inner in ast.walk(node)
        )
        return has_parents_loop and has_marker_probe
    return False


def _root_bindings(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    bindings: list[tuple[str, ast.AST]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in ROOT_BINDING_NAMES:
                bindings.append((target.id, node.value))
    return bindings


MODULES = _skill_helper_modules()


def test_skill_helper_tree_is_discoverable() -> None:
    """Guard the guard: an empty enumeration would make every case vacuous."""
    assert MODULES, f"no skill-helper modules found under {SKILL_HELPER_DIR}"


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_module_resolves_repository_root(module: Path) -> None:
    """A module's root binding must resolve the repo root, never an ancestor."""
    tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
    bindings = _root_bindings(tree)
    if not bindings:
        pytest.skip(f"{module.name} binds no project-root constant")

    expected = _expected_parents_index(module)
    for name, value in bindings:
        index = _parents_index(value)
        if index is not None:
            assert index == expected, (
                f"{module.relative_to(REPO_ROOT)}: {name} uses parents[{index}] but the "
                f"repository root is parents[{expected}]. "
                f"parents[{index}] resolves "
                f"{'above the project root' if index > expected else 'below the project root'}."
            )
            continue

        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
            assert _walks_for_marker(tree, value.func.id), (
                f"{module.relative_to(REPO_ROOT)}: {name} calls {value.func.id}(), which "
                "does not ascend parents testing a repository marker"
            )
            continue

        pytest.fail(
            f"{module.relative_to(REPO_ROOT)}: {name} uses an unrecognized root-resolution "
            f"form ({type(value).__name__}); extend this test to classify it"
        )


def test_marker_based_resolvers_unchanged() -> None:
    """The two already-compliant modules must keep their marker-based resolver.

    Guards against a mechanical ``parents[N]`` rewrite converting a correct,
    depth-independent resolver into a brittle index constant.
    """
    compliant = (
        SKILL_HELPER_DIR / "gtkb-bridge-propose" / "write_bridge.py",
        SKILL_HELPER_DIR / "gtkb-verify" / "write_verdict.py",
    )
    for module in compliant:
        assert module.is_file(), f"expected compliant module missing: {module}"
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        bindings = dict(_root_bindings(tree))
        assert bindings, f"{module.name}: project-root binding disappeared"
        for name, value in bindings.items():
            assert isinstance(value, ast.Call) and isinstance(value.func, ast.Name), (
                f"{module.name}: {name} is no longer a marker-based resolver call"
            )
            assert _walks_for_marker(tree, value.func.id), (
                f"{module.name}: {value.func.id}() no longer walks parents for a marker"
            )


def test_repository_marker_is_present() -> None:
    """The marker every resolver walks for must actually exist."""
    marker = REPO_ROOT.joinpath(*ROOT_MARKER_PARTS)
    assert marker.is_file(), f"repository marker missing: {marker}"


@pytest.mark.parametrize(
    "relative_helper",
    [
        "gtkb-bridge/revise_bridge.py",
        "gtkb-bridge/impl_report_bridge.py",
    ],
)
def test_bridge_helper_is_invocable(relative_helper: str) -> None:
    """The repaired helpers must import and build their CLI without a path error.

    ``revise_bridge.py`` was not merely misresolving: several derived paths --
    including a ``project_root`` default argument bound at function-definition
    time -- were computed from the bad constant, so the module raised
    ``FileNotFoundError`` on an out-of-root path before any argument could
    override it. Running ``--help`` exercises full module import plus parser
    construction, which is exactly the surface that was broken, without
    mutating any bridge state.
    """
    helper = SKILL_HELPER_DIR.joinpath(*relative_helper.split("/"))
    assert helper.is_file(), f"helper missing: {helper}"

    completed = subprocess.run(  # noqa: S603 - fixed in-repo interpreter and path
        [sys.executable, str(helper), "--help"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO_ROOT),
    )
    combined = f"{completed.stdout}\n{completed.stderr}"
    assert completed.returncode == 0, f"{relative_helper} exited {completed.returncode}; output:\n{combined}"
    assert "FileNotFoundError" not in combined, f"{relative_helper} raised FileNotFoundError during import:\n{combined}"
    assert "usage:" in completed.stdout, f"{relative_helper} produced no usage banner:\n{combined}"
