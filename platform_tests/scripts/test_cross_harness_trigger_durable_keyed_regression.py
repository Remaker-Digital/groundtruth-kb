"""Slice 10: cross-harness trigger remains durable-role-keyed regardless of
any interactive session-role marker.

bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md
(Codex GO at -006).

Module scope (per the slice proposal):

- Verification that ``scripts/cross_harness_bridge_trigger.py`` continues
  to dispatch counterpart bridge work using durable role authority and
  that the session-state role marker has no effect on:
    1. Recipient selection (``_resolve_dispatch_target``).
    2. Init-keyword emission (first line of ``_dispatch_prompt``).
    3. Actionable signature computation (``_signature``).
    4. Dispatch-failure audit log (no marker-state fields).
- This is the load-bearing safety contract behind
  ``GOV-SESSION-ROLE-AUTHORITY-001``: the interactive session-stated role
  governs in-session surfaces only; headless dispatch routing remains
  keyed to the durable role per ``DCL-SESSION-ROLE-RESOLUTION-001``.

Tests stand up a synthetic project root (claude=B=prime-builder,
codex=A=loyal-opposition) with optional session-role marker present, then
call the trigger's pure functions and inspect the trigger source for
forbidden marker references.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_TRIGGER_PATH = REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"

_CODEX_INVOCATION_SURFACES = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}
_CLAUDE_INVOCATION_SURFACES = {
    "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
}


def _load_trigger() -> ModuleType:
    """Load the trigger module by file path and register in sys.modules."""
    module_name = "_slice10_cross_harness_trigger"
    spec = importlib.util.spec_from_file_location(module_name, _TRIGGER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _make_synthetic_project(root: Path) -> Path:
    """Stage the harness-state fixtures the trigger reads.

    Mirrors the fixture in ``test_cross_harness_bridge_trigger.py`` so this
    module's tests share the same role/harness mapping (claude=B=prime-builder,
    codex=A=loyal-opposition) and any fixture drift surfaces in both modules.
    """
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSyntheticSlice10"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}},
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": "prime-builder", "harness_type": "claude"},
                    "A": {"role": "loyal-opposition", "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": _CODEX_INVOCATION_SURFACES,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": ["prime-builder"],
                        "invocation_surfaces": _CLAUDE_INVOCATION_SURFACES,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root


def _write_session_role_marker(project_root: Path, role: str, session_id: str) -> Path:
    """Plant a session-state role marker at the canonical location."""
    marker = project_root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"role": role, "session_id": session_id}), encoding="utf-8")
    return marker


# ---------------------------------------------------------------------------
# Test 1: recipient selection ignores the session-state marker.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "needed_role,expected_handle,expected_mode",
    [
        ("prime-builder", "claude", "pb"),
        ("loyal-opposition", "codex", "lo"),
    ],
)
def test_resolve_dispatch_target_ignores_session_role_marker(
    tmp_path: Path,
    needed_role: str,
    expected_handle: str,
    expected_mode: str,
) -> None:
    """``_resolve_dispatch_target`` resolves the recipient strictly from the
    durable role map; the presence of any session-state marker (with any
    role, including the opposite of the durable mapping) must not change
    the resolved target.

    This is the load-bearing safety contract: a session-stated role flip
    on one harness must NOT redirect headless dispatch traffic. The
    cross-harness trigger reads the durable map and only the durable map.
    """
    project_root = _make_synthetic_project(tmp_path)
    # Plant a marker whose role contradicts the durable mapping for the
    # recipient. If the trigger were to read the marker, the resolved
    # target would change; the test asserts it does not.
    contradicting_role = "loyal-opposition" if needed_role == "prime-builder" else "prime-builder"
    _write_session_role_marker(project_root, role=contradicting_role, session_id="S375-test-marker-id")

    trigger = _load_trigger()
    target = trigger._resolve_dispatch_target(needed_role, project_root)

    assert target.command_handle == expected_handle, (
        f"recipient command handle drifted from durable mapping under marker influence: "
        f"got {target.command_handle!r}, expected {expected_handle!r}"
    )
    assert target.canonical_mode == expected_mode
    assert target.needed_role_label == needed_role


# ---------------------------------------------------------------------------
# Test 2: dispatched init keyword is keyed to durable role, not marker role.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "needed_role,expected_first_line",
    [
        ("prime-builder", "::init gtkb pb"),
        ("loyal-opposition", "::init gtkb lo"),
    ],
)
def test_dispatch_prompt_first_line_emits_durable_keyed_keyword(
    tmp_path: Path,
    needed_role: str,
    expected_first_line: str,
) -> None:
    """The first line of the dispatch prompt is the canonical init keyword
    derived from the resolved target's canonical_mode, NOT from any
    session-state marker.

    Receiver-side ``_bridge_dispatch_keyword_check`` performs
    set-membership against the receiver's own durable role set. If the
    emitter ever drifted to mark the prompt with the marker's role, a
    durable-Prime harness receiving a marker-derived LO keyword would
    STRICT_DROP — the cross-harness round-trip would silently break.
    """
    project_root = _make_synthetic_project(tmp_path)
    _write_session_role_marker(project_root, role="loyal-opposition", session_id="S375-test-marker-id")

    trigger = _load_trigger()
    target = trigger._resolve_dispatch_target(needed_role, project_root)
    prompt = trigger._dispatch_prompt(target, items=[], max_items=2)
    first_line = prompt.splitlines()[0]
    assert first_line == expected_first_line, (
        f"dispatch prompt first line drifted from durable canonical mode under marker influence: "
        f"got {first_line!r}, expected {expected_first_line!r}"
    )


# ---------------------------------------------------------------------------
# Test 3: actionable signature is marker-independent.
# ---------------------------------------------------------------------------


def test_signature_is_marker_independent(tmp_path: Path) -> None:
    """The trigger's actionable signature is a pure function of the
    normalized INDEX items (document_name, top_status, top_file). Planting
    or mutating a session-state marker must not change the signature, so
    dispatch-state idempotence (the loop-prevention contract) is preserved
    across marker writes.
    """
    project_root = _make_synthetic_project(tmp_path)
    trigger = _load_trigger()

    # The trigger's ``_signature`` reads only ``document_name``,
    # ``top_status``, ``top_file`` attributes (per its docstring + the
    # smart-poller's frozen reference shape). A SimpleNamespace with those
    # three attributes is a drop-in stand-in for the real ActionablePending
    # dataclass without coupling this test to the package's import path.
    from types import SimpleNamespace

    items = [
        SimpleNamespace(document_name="example-thread", top_status="NEW", top_file="bridge/example-thread-001.md"),
    ]

    signature_before = trigger._signature(items)

    _write_session_role_marker(project_root, role="loyal-opposition", session_id="S375-marker-A")
    signature_after_marker_a = trigger._signature(items)

    _write_session_role_marker(project_root, role="prime-builder", session_id="S375-marker-B")
    signature_after_marker_b = trigger._signature(items)

    (project_root / ".claude" / "session" / "active-session-role.json").unlink()
    signature_after_unlink = trigger._signature(items)

    assert signature_before == signature_after_marker_a == signature_after_marker_b == signature_after_unlink, (
        "signature drifted across marker writes; loop-prevention idempotence would break"
    )


# ---------------------------------------------------------------------------
# Test 4: trigger source carries no session-role-marker references.
# ---------------------------------------------------------------------------


def test_trigger_source_carries_no_session_role_marker_references() -> None:
    """The trigger module source MUST NOT reference the session-state
    marker by name. The marker is a UserPromptSubmit-time mechanism for
    in-session surfaces only; surfacing it in the trigger source would
    be either (a) a marker-influencing-dispatch defect or (b) a marker-
    field leaking into the dispatch-failure audit log. Either is a
    GOV-SESSION-ROLE-AUTHORITY-001 violation.

    Forbidden tokens cover the marker filename, the writer/resolver
    constant name, and the resolver function names so a regression that
    introduced any of those would be caught at this gate.
    """
    src = _TRIGGER_PATH.read_text(encoding="utf-8")
    forbidden = (
        "active-session-role.json",
        "_SESSION_ROLE_MARKER_NAME",
        "_session_role_marker_path",
        "resolve_interactive_session_role",
        "_session_role_override",
    )
    leaked = [token for token in forbidden if token in src]
    assert leaked == [], (
        "cross-harness trigger source references session-role-marker tokens "
        f"that would violate GOV-SESSION-ROLE-AUTHORITY-001: {leaked!r}"
    )
