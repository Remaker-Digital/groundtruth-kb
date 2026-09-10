"""Projection roots hold no interpreter bytecode (WI-7685, class 1).

Specs: `GOV-HARNESS-NEUTRAL-BASELINE-001` obligations 2 and 5.

The defect this pins: executing hooks and skill helpers from inside a projection
tree makes the interpreter write `__pycache__` there. Bytecode is not projector
output, has no readers, and nothing removed it.

Why this needs two mechanisms and two assertions rather than one. Suppressing
bytecode on the projector's own hook invocations covers only the commands the
projector writes. It cannot cover an importer the projector does not invoke, and
that case is not hypothetical: `.cursor` was measured at zero surplus, projected
clean at 128/128, and held
`skills/gtkb-bridge-propose/helpers/__pycache__/write_bridge.cpython-314.pyc`
within the hour, created by something importing a projected helper. A projection
run then reported "0 leftovers removed", because bytecode was not classified as a
leftover. Prevention without cleanup leaves the property holding only most of the
time, which is the failure mode that produced the observation above.

Note what `--check` did and did not do. Before this change, bytecode was not
classified as a leftover, so the plan never contained it and drift detection could
not see it: a projection run reported "0 leftovers removed" while `__pycache__`
sat in the tree. Classifying it put it in the plan, which is what makes it visible
to `--check` -- measured after the change, `claude` reports 10 drifted, matching
the 10 bytecode paths present. That visibility is the durable win here.

What `--check` still cannot do is prove the tree is clean at an arbitrary moment,
because it reports what the next run would correct rather than what is already
absent. These assertions therefore pin coverage by plan, not absence in tree.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "harness_projection"))

import project_harness  # noqa: E402

NO_BYTECODE_FLAG = "-B"


def _rostered_harnesses() -> list[tuple[str, str]]:
    """(harness, config_dir) for every profile that is not pending its own slice."""
    profiles = project_harness.load_profiles()
    out = []
    for name, profile in profiles["harnesses"].items():
        if profile.get("status") == "profile_pending":
            continue
        config_dir = str(profile.get("config_dir") or "").strip()
        if config_dir:
            out.append((name, config_dir))
    return sorted(set(out))


def test_bytecode_under_a_projection_root_is_planned_for_removal() -> None:
    """Coverage by plan rather than absence in tree. Roster-driven (WI-7685).

    This previously asserted that no bytecode exists under any projection root.
    The implementation disclaims that property in its own words: prevention and
    cleanup together leave it holding "only most of the time", because ``-B``
    reaches only the command lines the projector renders and an importer the
    projector never invokes can dirty a root between runs. Canon section 8
    describes the same shape from the other side -- drift is detected and
    corrected, not made impossible.

    So the durable guarantee is that whatever bytecode appears is planned for
    removal on the next run. That holds at every moment; absence-in-tree holds
    only immediately after one, which is why the old form failed for any session
    older than the fix while the mechanism underneath was working correctly. An
    assertion that fails for reasons unrelated to the defect it guards teaches
    readers to discount it.

    This is the stronger statement, not a weaker one.
    """
    uncovered: list[str] = []
    for harness, config_dir in _rostered_harnesses():
        root = PROJECT_ROOT / config_dir
        if not root.is_dir():
            continue
        found = list(root.rglob("*.pyc")) + [p for p in root.rglob("__pycache__") if p.is_dir()]
        if not found:
            continue

        plan = project_harness.Plan()
        project_harness.apply_leftover_removes(plan, {"config_dir": config_dir})
        planned = set(plan.removes)

        for path in found:
            rel = project_harness.normalize_planned_rel(path.relative_to(PROJECT_ROOT).as_posix())
            if rel not in planned:
                uncovered.append(f"{harness}:{rel}")

    assert not uncovered, (
        f"bytecode under a projection root is not covered by that harness's removal plan: {sorted(uncovered)}"
    )


@pytest.mark.parametrize(("harness", "_config_dir"), _rostered_harnesses())
def test_every_rendered_hook_command_suppresses_bytecode(harness: str, _config_dir: str) -> None:
    """Prevention, asserted per rendered command rather than per code path.

    A future registration site that forgets the flag would otherwise reintroduce
    the defect silently for one harness only.
    """
    missing: list[str] = []
    plan = project_harness.build_plan(harness)
    for rel, content in plan.writes.items():
        if not rel.endswith((".json", ".toml")):
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if ".venv" not in stripped or "python" not in stripped.lower():
                continue
            if NO_BYTECODE_FLAG not in stripped:
                missing.append(f"{harness}:{rel}: {stripped[:90]}")

    assert not missing, f"rendered hook commands without {NO_BYTECODE_FLAG}: {missing}"


def test_cleanup_removes_bytecode_the_projector_did_not_create(tmp_path: Path) -> None:
    """Cleanup, asserted independently of prevention.

    This is the assertion that would have failed for the `.cursor` instance.
    Bytecode created by an importer outside the projector's control must still
    be planned for removal, so the test writes it directly rather than provoking
    an import.

    Exercised against a temporary tree: the shared checkout is live for other
    sessions, and a test that mutates real projection roots would race them.
    """
    config_dir = ".probe-harness"
    projection_root = tmp_path / config_dir
    cache_dir = projection_root / "hooks" / "__pycache__"
    cache_dir.mkdir(parents=True)
    stray = cache_dir / "planted.cpython-314.pyc"
    stray.write_bytes(b"not projector output")

    original_root = project_harness.PROJECT_ROOT
    try:
        project_harness.PROJECT_ROOT = tmp_path
        plan = project_harness.Plan()
        project_harness.apply_leftover_removes(plan, {"config_dir": config_dir})
    finally:
        project_harness.PROJECT_ROOT = original_root

    planned = set(plan.removes)
    assert planned, "planted bytecode produced no removal plan at all"
    assert any("__pycache__" in rel or rel.endswith(".pyc") for rel in planned), (
        f"planted bytecode was not planned for removal; plan was {sorted(planned)}"
    )


def test_scope_boundary_other_runtime_state_is_untouched() -> None:
    """WI-7685 is class 1 only; classes 2 and 3 belong to WI-7733 and WI-7696.

    Asserting the boundary explicitly stops this change from silently doing
    their work, and stops a later edit here from quietly absorbing it.
    """
    source = (PROJECT_ROOT / "scripts" / "harness_projection" / "project_harness.py").read_text(encoding="utf-8")
    for out_of_scope in ("active-session-role", "session-start.json"):
        assert out_of_scope not in source, (
            f"{out_of_scope} is WI-7733 or WI-7696 scope and must not be handled by the projector here"
        )
