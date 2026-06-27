"""Spec-derived tests for the cross-harness parity discovery-diff (WI-4877, Slice 3).

Verifies ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` assertions:

- **PARITY-DIFF-EXISTS** — the discovery-diff enumerates actual harness hook
  surfaces and diffs them; it detects the live ``::open`` /
  ``session_wrapup_trigger_dispatch`` asymmetry (acceptance criterion 1) and a
  synthetic unregistered single-harness hook (acceptance criterion 2).
- **PARITY-DIFF-WIRED** — the ``_check_parity_discovery_diff`` doctor check
  returns WARN on a live asymmetry and PASS on a symmetric fixture (never FAIL
  at Slice 3).
- **PARITY-APPLICABILITY-RULE** — surface-not-applicable harnesses (no
  hook-config file) are excluded from the hook-surface population; a valid typed
  waiver suppresses a registered asymmetry.

Hermetic: synthetic surfaces / registries / projections are constructed in-test;
the live-tree checks are read-only.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
_GROUNDTRUTH_SRC = _PROJECT_ROOT / "groundtruth-kb" / "src"
for _extra in (str(_SCRIPTS), str(_GROUNDTRUTH_SRC)):
    if _extra not in sys.path:
        sys.path.insert(0, _extra)

import parity_discovery_diff as diff  # noqa: E402

_OPEN_KEY = "hook:session_wrapup_trigger_dispatch"


def _projection(*active: str) -> dict:
    return {"harnesses": [{"harness_name": name, "status": "active", "role": ["prime-builder"]} for name in active]}


# ── enumeration (PARITY-DIFF-EXISTS) ─────────────────────────────────────────


def test_enumerate_hook_surfaces_extracts_stems_across_separators() -> None:
    config = {
        "hooks": {
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {"type": "command", "command": 'python "$CLAUDE_PROJECT_DIR/.claude/hooks/spec-classifier.py"'},
                        {
                            "type": "command",
                            "command": "python E:\\GT-KB\\.codex\\gtkb-hooks\\session_wrapup_trigger_dispatch.py",
                        },
                        {
                            "type": "command",
                            "command": "cmd /d /s /c E:\\GT-KB\\.codex\\gtkb-hooks\\workstream-focus.cmd",
                        },
                    ]
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {"type": "command", "command": "python scripts/cross_harness_bridge_trigger.py --stop-hook"}
                    ]
                }
            ],
        }
    }
    stems = diff.enumerate_hook_surfaces(config)
    assert "spec-classifier" in stems
    assert "session_wrapup_trigger_dispatch" in stems
    assert "workstream-focus" in stems  # .cmd wrapper reduces to its stem
    assert "cross_harness_bridge_trigger" in stems


def test_live_codex_userpromptsubmit_discovers_session_wrapup() -> None:
    surfaces, errors = diff.discover_surfaces_by_harness(_PROJECT_ROOT)
    assert not errors, errors
    assert "session_wrapup_trigger_dispatch" in surfaces.get("codex", set())
    assert "session_wrapup_trigger_dispatch" not in surfaces.get("claude", set())


# ── acceptance: ::open asymmetry detected on the live tree (PARITY-DIFF-EXISTS) ──


def test_open_asymmetry_resolved_post_slice5() -> None:
    """Acceptance criterion 1 (post-Slice-5): the ::open routing asymmetry is resolved.

    This was a pre-Slice-5 checkpoint (it formerly asserted the asymmetry was
    present, codex-only). Slice 5 (WI-4891) wired the behavioral equivalent of
    ``session_wrapup_trigger_dispatch`` into the Claude UserPromptSubmit chain
    (``.claude/hooks/session-topic-envelope-router.py``) and registered both
    harness surfaces under the single capability ``hook.session-topic-envelope-routing``,
    so the discovery-diff no longer reports the asymmetry under either the old
    unregistered key or the new capability id. The diff's *detection* capability
    remains proven independently by
    ``test_synthetic_unregistered_single_harness_hook_caught``.
    """
    report = diff.run_discovery_diff(_PROJECT_ROOT)
    resolved_keys = {_OPEN_KEY, "hook.session-topic-envelope-routing"}
    offending = {f.capability_key for f in report.findings if f.capability_key in resolved_keys}
    assert not offending, f"::open conformance asymmetry still reported post-Slice-5: {offending}"


# ── regression: synthetic unregistered single-harness hook (PARITY-DIFF-EXISTS) ──


def test_synthetic_unregistered_single_harness_hook_caught() -> None:
    surfaces = {"claude": {"shared-a", "shared-b"}, "codex": {"shared-a", "shared-b", "codex-only-evil"}}
    report = diff.compute_diff(surfaces, {}, _projection("claude", "codex"))
    keys = {f.capability_key for f in report.findings}
    assert "hook:codex-only-evil" in keys
    finding = next(f for f in report.findings if f.capability_key == "hook:codex-only-evil")
    assert finding.present_on == ["codex"]
    assert finding.absent_on == ["claude"]
    assert finding.registered is False


def test_symmetric_surfaces_produce_no_findings() -> None:
    surfaces = {"claude": {"shared-a", "shared-b"}, "codex": {"shared-a", "shared-b"}}
    report = diff.compute_diff(surfaces, {}, _projection("claude", "codex"))
    assert report.overall_status == "PASS"
    assert report.findings == []


# ── waiver suppression + applicability (PARITY-APPLICABILITY-RULE) ───────────


def _registry_with_registered_hook() -> dict:
    return {
        "parity_schema_version": 1,
        "capabilities": [
            {
                "id": "hook.x",
                "kind": "hook",
                "canonical_name": "x",
                "required_for_roles": ["prime-builder"],
                "claude": {"surface": ".claude/hooks/x.py", "status": "native"},
                "codex": {"surface": ".claude/hooks/x.py", "status": "native"},
            }
        ],
    }


def test_registered_asymmetry_without_waiver_is_reported() -> None:
    registry = _registry_with_registered_hook()
    surfaces = {"claude": set(), "codex": {"x"}}
    report = diff.compute_diff(surfaces, registry, _projection("claude", "codex"))
    finding = next((f for f in report.findings if f.capability_key == "hook.x"), None)
    assert finding is not None
    assert finding.registered is True
    assert finding.absent_on == ["claude"]


def test_valid_waiver_suppresses_registered_asymmetry() -> None:
    registry = _registry_with_registered_hook()
    registry["parity_waivers"] = [
        {
            "capability_id": "hook.x",
            "harness": "claude",
            "reason_class": "harness-surface-difference",
            "rationale": "claude routes this capability through a different surface",
            "owner_approval_ref": "DELIB-EXAMPLE-0001",
            "review_trigger": "slice-6-coverage-audit",
        }
    ]
    surfaces = {"claude": set(), "codex": {"x"}}
    report = diff.compute_diff(surfaces, registry, _projection("claude", "codex"))
    assert all(f.capability_key != "hook.x" for f in report.findings)


def test_surface_not_applicable_harness_excluded_from_population() -> None:
    # A harness with no hook-config file is omitted from discovery (not an error).
    config_files = dict(diff.HOOK_CONFIG_FILES)
    config_files["ghost"] = "nonexistent/none.json"
    surfaces, errors = diff.discover_surfaces_by_harness(_PROJECT_ROOT, config_files=config_files)
    assert "ghost" not in surfaces
    assert not errors


def test_live_population_is_hook_config_declaring_only() -> None:
    report = diff.run_discovery_diff(_PROJECT_ROOT)
    assert report.population == ["claude", "codex"]
    for shim in ("ollama", "cursor", "openrouter", "antigravity"):
        assert shim not in report.population


# ── doctor wiring (PARITY-DIFF-WIRED) ────────────────────────────────────────


def test_doctor_check_warns_on_live_asymmetry_never_fails() -> None:
    from groundtruth_kb.project.doctor import _check_parity_discovery_diff

    result = _check_parity_discovery_diff(_PROJECT_ROOT)
    # Slice 3: WARN ramp — must never be ``fail``.
    assert result.status != "fail"
    # The live tree has unwaived asymmetries (incl. ::open), so the check WARNs.
    assert result.status == "warning"
    assert "asymmetry" in result.message.lower()
