# GT-KB Skill `/gtkb-spec-intake` (Tier A #5)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Scope-tracking VERIFIED:** `bridge/gtkb-operational-skills-tier-a-008.md`
**Target repo:** `groundtruth-kb` at main (`0a60054` — Tier A #3 VERIFIED)
**Blocking predecessor:** Tier A #3 `gtkb-skill-bridge-propose` VERIFIED (`0a60054`)
  — pattern primitives (`_MANAGED_SKILLS` + `_plan_missing_managed_files`
  + doctor kwargs) now settled.

## Summary

Add the third (and final) Phase A skill: `/gtkb-spec-intake`. Wraps
existing `intake.py` APIs (`capture_requirement()`, `confirm_intake()`,
`reject_intake()`) with a confirm-before-mutate contract expressed at
the skill-helper boundary. Follows the decision-capture (#4) pattern
directly: helper module with fixed governance metadata, doctor check
using kwargs, `_MANAGED_SKILLS` extension in lockstep with scaffold
`_MANAGED_SKILLS_INITIAL`.

**Strict compliance with G4** (from scope GO `-004`): helper uses
`outcome="deferred"` for the capture step. This outcome already exists
in the KnowledgeDB schema (see `src/groundtruth_kb/db.py:4247-4249`)
and the existing `capture_requirement()` already uses it (see
`src/groundtruth_kb/intake.py:216-217`). **No schema migration and no
new outcome value are proposed.**

## Prior Deliberations

No prior DELIB-* deliberations matching this skill's topic.
`search_deliberations(query="spec intake skill confirm before mutate")`
returns nothing.

Relevant prior bridge threads:

- `bridge/gtkb-operational-skills-tier-a-004.md` (parent scope GO)
- `bridge/gtkb-operational-skills-tier-a-008.md` (scope-tracking VERIFIED)
- `bridge/gtkb-skill-decision-capture-012.md` (Tier A #4 VERIFIED —
  skill scaffold pattern source; this proposal follows it directly)
- `bridge/gtkb-skill-bridge-propose-008.md` (Tier A #3 VERIFIED —
  second skill; pattern now settled for multi-skill `_MANAGED_SKILLS`)
- `memory/project_gtkb_non_disruptive_upgrade_priority.md` (owner
  strategic direction — this bridge advances it via unconditional
  missing-file repair, same mechanism as #3 and #4)

## Scope

### In scope

1. New skill `/gtkb-spec-intake` packaged as
   `templates/skills/spec-intake/SKILL.md` + helper module at
   `templates/skills/spec-intake/helpers/spec_intake.py`.
2. Helper exposes three entry points wrapping existing `intake.py` API:
   - `capture_candidate()` — wraps `intake.capture_requirement()` with
     fixed governance metadata (`source_type="owner_conversation"`,
     `outcome="deferred"`, `changed_by="prime-builder/spec-intake-skill"`)
   - `confirm_candidate()` — wraps `intake.confirm_intake()` with
     governance metadata and collision guard
   - `reject_candidate()` — wraps `intake.reject_intake()` with
     governance metadata; requires non-empty reason
3. Scaffold extension: append two paths to `_MANAGED_SKILLS_INITIAL`
   in `scaffold.py`.
4. Upgrade extension: append two paths to `_MANAGED_SKILLS` in
   `upgrade.py`. No other upgrade-planner changes required (the
   `_plan_missing_managed_files` + `_plan_managed_skills` +
   `_map_managed_to_template` infrastructure from #4 and #3 already
   generalizes over `_MANAGED_SKILLS` list content).
5. Doctor extension: add `_check_spec_intake_skill_present()` parallel
   to `_check_skill_present` / `_check_bridge_propose_skill_present`;
   wire into `run_doctor()` inside the existing `if p.includes_bridge:`
   block.
6. Tests: helper tests (new file), scaffold tests (append),
   upgrade tests (append), doctor tests (append). Full-tree mypy
   --strict + ruff + full suite must remain green.

### Out of scope (deferred by precedent)

1. Any new `KnowledgeDB.insert_*` API or new `outcome` / `source_type`
   value. The skill is pure wrapping of existing functions.
2. `pyproject.toml` edits. Force-include of `templates/` tree already
   ships skill files in the wheel (established by #3 and #4).
3. Any changes to `intake.py` itself. The skill layers on top; it does
   not modify the intake pipeline.
4. AGENTS.md or CLAUDE.md text changes describing the skill. Adopters
   discover the skill via `gt project doctor` and the scaffolded
   `.claude/skills/` directory.
5. CLI-level surface beyond what the skill file provides (no
   `gt skill spec-intake` sub-command).

## Design

### Skill file (SKILL.md)

Parallel in shape to `templates/skills/decision-capture/SKILL.md`
(see target repo at `0a60054`). Frontmatter, purpose section, when to
invoke, when NOT to invoke, how it works. The **confirm-before-mutate
contract** is expressed as a three-step sequence:

1. **Capture step** — `capture_candidate()` records a requirement-type
   deliberation at `outcome="deferred"`. No spec is written. No KB
   mutation beyond the deliberation row. The returned dict includes
   `deliberation_id` so the owner can reference the candidate.
2. **Confirm step** — `confirm_candidate()` is called ONLY after
   explicit owner approval. Creates a new spec at `status="specified"`
   and updates the deliberation to `outcome="owner_decision"`. Both
   writes happen inside `intake.confirm_intake()` (unchanged).
3. **Reject step** — `reject_candidate()` is called after explicit
   owner rejection. Updates the deliberation to `outcome="no_go"`
   with a required rejection reason. No spec is written.

The SKILL.md MUST state explicitly that the skill does not silently
write specs, work items, ADRs, DCLs, or documents. That language is
direct transposition of the scope-GO `-004` requirement (review gate
language at `bridge/gtkb-operational-skills-tier-a-003.md:189-247`).

### Helper module (helpers/spec_intake.py)

```python
"""Helper for the /gtkb-spec-intake skill.

Wraps `groundtruth_kb.intake` with the confirm-before-mutate contract.
Fixed governance metadata. Never mutates specs/work-items/docs without
an explicit confirm_candidate() call.
"""

from __future__ import annotations

from typing import Any

from groundtruth_kb import intake as _intake
from groundtruth_kb.db import KnowledgeDB


class SpecIntakeCaptureFailed(RuntimeError):
    """Raised when intake.capture_requirement returns a malformed result."""


class SpecIntakeConfirmFailed(RuntimeError):
    """Raised when intake.confirm_intake returns an error dict."""


class SpecIntakeRejectFailed(RuntimeError):
    """Raised when intake.reject_intake returns an error dict."""


_CHANGED_BY = "prime-builder/spec-intake-skill"


def capture_candidate(
    db: KnowledgeDB,
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
) -> dict[str, Any]:
    """Capture a requirement candidate at outcome='deferred'.

    Wraps :func:`intake.capture_requirement`. The underlying function
    already writes a deliberation with ``outcome='deferred'``. This
    wrapper asserts the return shape contains a ``deliberation_id`` and
    raises :class:`SpecIntakeCaptureFailed` otherwise.

    The helper never creates specs, work items, or documents. Only a
    deliberation row is persisted, and its outcome is explicitly
    ``deferred`` (the outcome that already exists in
    ``insert_deliberation``'s accepted values). See G4.
    """
    result = _intake.capture_requirement(
        db,
        text,
        proposed_title=proposed_title,
        proposed_section=proposed_section,
        proposed_scope=proposed_scope,
        proposed_type=proposed_type,
        proposed_authority=proposed_authority,
    )
    if not isinstance(result, dict) or "deliberation_id" not in result:
        raise SpecIntakeCaptureFailed(
            f"capture_requirement returned malformed result: {result!r}"
        )
    return result


def confirm_candidate(
    db: KnowledgeDB,
    deliberation_id: str,
) -> dict[str, Any]:
    """Confirm a captured candidate — creates a KB spec.

    Wraps :func:`intake.confirm_intake`. Raises
    :class:`SpecIntakeConfirmFailed` when the underlying function
    returns an ``error`` key. The already-confirmed case (idempotent
    re-invocation) is returned as-is — the caller can check
    ``already_confirmed``.

    This is the only path in the skill that creates specs. It is
    called explicitly after owner approval — the capture step does
    not invoke it implicitly.
    """
    result = _intake.confirm_intake(db, deliberation_id)
    if "error" in result:
        raise SpecIntakeConfirmFailed(
            f"confirm_intake failed for {deliberation_id!r}: {result['error']}"
        )
    return result


def reject_candidate(
    db: KnowledgeDB,
    deliberation_id: str,
    reason: str,
) -> dict[str, Any]:
    """Reject a captured candidate.

    Wraps :func:`intake.reject_intake`. Requires non-empty reason.
    Raises :class:`SpecIntakeRejectFailed` when the underlying function
    returns an ``error`` key. No spec is ever written.
    """
    if not reason or not reason.strip():
        raise SpecIntakeRejectFailed("Rejection reason is required")
    result = _intake.reject_intake(db, deliberation_id, reason)
    if "error" in result:
        raise SpecIntakeRejectFailed(
            f"reject_intake failed for {deliberation_id!r}: {result['error']}"
        )
    return result
```

Approximate size: ~120 lines incl. docstrings, blank lines, and
imports. Comparable to `record_decision.py` (~100 lines).

### Scaffold extension (`scaffold.py`)

```python
_MANAGED_SKILLS_INITIAL: tuple[str, ...] = (
    "decision-capture/SKILL.md",
    "decision-capture/helpers/record_decision.py",
    "bridge-propose/SKILL.md",
    "bridge-propose/helpers/write_bridge.py",
    "spec-intake/SKILL.md",                             # NEW
    "spec-intake/helpers/spec_intake.py",               # NEW
)
```

No other scaffold changes. `_copy_skill_templates()` already iterates
`_MANAGED_SKILLS_INITIAL` generically.

### Upgrade extension (`upgrade.py`)

```python
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
    ".claude/skills/bridge-propose/SKILL.md",
    ".claude/skills/bridge-propose/helpers/write_bridge.py",
    ".claude/skills/spec-intake/SKILL.md",                     # NEW
    ".claude/skills/spec-intake/helpers/spec_intake.py",       # NEW
]
```

No other upgrade changes. The infrastructure from #2/#3/#4
(`_filter_skills_for_profile`, `_plan_missing_managed_files`,
`_plan_managed_skills`, `_map_managed_to_template`) handles any list
content generically.

### Doctor extension (`doctor.py`)

New function parallel to `_check_skill_present` and
`_check_bridge_propose_skill_present`:

```python
def _check_spec_intake_skill_present(target: Path, profile_name: str) -> ToolCheck:
    """Check that the ``spec-intake`` skill files are present.

    Bridge-profile-only check. Warning-level (not fail) — same
    convention as the other skill checks. Remediation:
    ``gt project upgrade --apply``.
    """
    profile = get_profile(profile_name)
    if not profile.includes_bridge:
        return ToolCheck(
            name="skill:spec-intake",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    skill_md = target / ".claude" / "skills" / "spec-intake" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "spec-intake" / "helpers" / "spec_intake.py"

    missing: list[str] = []
    if not skill_md.exists():
        missing.append("SKILL.md")
    if not helper_py.exists():
        missing.append("helpers/spec_intake.py")

    if missing:
        return ToolCheck(
            name="skill:spec-intake",
            required=False,
            found=False,
            status="warning",
            message=(
                f".claude/skills/spec-intake/ missing: {', '.join(missing)}. "
                f"Run `gt project upgrade --apply` to restore."
            ),
        )

    return ToolCheck(
        name="skill:spec-intake",
        required=False,
        found=True,
        status="pass",
        message="spec-intake skill present",
    )
```

Wire-in to `run_doctor()`: append inside the existing `if
p.includes_bridge:` block, immediately after
`_check_bridge_propose_skill_present`:

```python
if p.includes_bridge:
    # ... existing checks ...
    checks.append(_check_skill_present(target, profile))
    checks.append(_check_bridge_propose_skill_present(target, profile))
    checks.append(_check_spec_intake_skill_present(target, profile))  # NEW
    # ... remaining existing checks ...
```

Uses `ToolCheck(..., status=, message=)` **keyword** args per the
pattern established by `-006` NO-GO of decision-capture. Never
positional — `status` is at position 5 in the dataclass, not 4.

## Tests

### New file: `tests/test_spec_intake_helper.py`

Approximately 8 tests isolating helper behavior. All use
`KnowledgeDB` against a temp DB path so no KB fixture state is
needed. Follows the `test_decision_capture_helper.py` pattern
(dynamic import via spec loader).

1. `test_capture_candidate_returns_deliberation_id` — happy path;
   assert result dict contains `deliberation_id` key
2. `test_capture_candidate_writes_deferred_outcome` — inspect the
   persisted deliberation; assert `outcome == "deferred"` (G4)
3. `test_capture_candidate_writes_fixed_source_type` — assert
   `source_type == "owner_conversation"` and `changed_by ==
   "prime-builder/spec-intake-skill"`
4. `test_capture_candidate_raises_on_malformed_result` — monkeypatch
   `intake.capture_requirement` to return `None`; assert
   `SpecIntakeCaptureFailed`
5. `test_confirm_candidate_creates_spec` — call capture then
   confirm; assert returned dict has `spec` key with
   `status="specified"`
6. `test_confirm_candidate_raises_on_unknown_id` — confirm an
   unknown DELIB-ID; assert `SpecIntakeConfirmFailed`
7. `test_reject_candidate_requires_reason` — call with empty reason;
   assert `SpecIntakeRejectFailed`
8. `test_reject_candidate_records_no_go` — call with a reason;
   inspect deliberation; assert `outcome == "no_go"`

### Append to `tests/test_scaffold_skills.py`

Approximately 2 tests:

1. `test_dual_agent_project_has_spec_intake_skill` — scaffold a
   dual-agent project; assert SKILL.md + helper both exist
2. `test_spec_intake_skill_recursively_copied` — assert
   `helpers/spec_intake.py` is at the expected nested path

### Append to `tests/test_upgrade_skills.py`

Approximately 3 tests:

1. `test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version`
   — remove the SKILL.md; assert `add` action from
   `_plan_missing_managed_files`
2. `test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version`
   — remove the helper; assert `add` action
3. `test_execute_creates_missing_spec_intake_files_at_same_version`
   — end-to-end plan + execute; assert files land at expected paths

### Append to `tests/test_doctor_skills.py`

Approximately 3 tests:

1. `test_doctor_warning_when_spec_intake_missing` — remove skill
   files; assert `status == "warning"` on the check
2. `test_doctor_pass_when_spec_intake_present` — all files present;
   assert `status == "pass"`
3. `test_run_doctor_reports_missing_spec_intake_in_dual_agent_project`
   — full `run_doctor()` call (not check in isolation); assert the
   check name appears in the report with `warning`

### Parity test (lockstep)

The existing `test_scaffold_skills.py::test_skill_files_copied_recursively`
already validates that every entry in `_MANAGED_SKILLS_INITIAL` is
copied. Adding spec-intake entries to the tuple automatically extends
the coverage. **No new parity test is required** — the existing test
is generic over the tuple.

**Total new tests: ~11** (8 helper + 2 scaffold + 3 upgrade + 3
doctor - 5 overlaps-elsewhere = 11 net).

**Expected suite delta: 1161 → ~1172.**

## Exit Criteria

1. `templates/skills/spec-intake/SKILL.md` exists with frontmatter
   matching other skills; documents confirm-before-mutate contract
   explicitly.
2. `templates/skills/spec-intake/helpers/spec_intake.py` exposes
   `capture_candidate`, `confirm_candidate`, `reject_candidate` with
   the contracts stated above.
3. `scaffold._MANAGED_SKILLS_INITIAL` includes the two spec-intake
   paths (in the tuple order documented above).
4. `upgrade._MANAGED_SKILLS` includes the two spec-intake paths.
5. `doctor._check_spec_intake_skill_present` present and wired into
   `run_doctor()` inside the `if p.includes_bridge:` block.
6. `tests/test_spec_intake_helper.py` exists with ~8 tests, all pass.
7. Existing test files have spec-intake tests appended: ~2 scaffold,
   ~3 upgrade, ~3 doctor; all pass.
8. `mypy --strict src/groundtruth_kb/` returns `Success`.
9. `ruff check src/groundtruth_kb/ tests/` clean.
10. `ruff format --check` clean.
11. Full suite: 1161 → ~1172 tests, all pass.
12. Wheel build: `python -m build` succeeds; wheel contents include
    all three skill trees under `templates/skills/`.
13. No edits to `intake.py`, `db.py`, or `pyproject.toml`.
14. No new deliberation outcomes or source_types added to schema.
15. Single commit on GT-KB main after Codex GO.

## Review Gates Addressed (G1-G5)

- **G1** (High, #1 credential-patterns): N/A — satisfied by
  `gtkb-credential-patterns-canonical-010` VERIFIED. No new credential
  patterns introduced.
- **G2** (High, first skill bridge): N/A — scaffold + adopter
  installation path already established by `gtkb-skill-decision-capture-012`
  and `gtkb-skill-bridge-propose-008`. This bridge extends the list
  only.
- **G3** (Medium, all): This is #5 of the six authorized bridges.
  Reports reference six-bridge counts consistently.
- **G4** (Medium, #5): ✅ **Uses `outcome="deferred"` (exists today).**
  No `pending_confirmation` outcome proposed. No schema/API migration.
  Helper asserts this via unit test
  (`test_capture_candidate_writes_deferred_outcome`).
- **G5** (Medium, #2 + #6): N/A — scanner-deny schema is #6's concern;
  this bridge does not touch the hook log.

## Dependencies and Parallel Work

- **Blocking predecessor resolved**: Tier A #3 `gtkb-skill-bridge-propose`
  VERIFIED at `0a60054`. Pattern primitives stable.
- **Can parallel with**: Tier A #6 `gtkb-phase-a-metrics-collector`
  (different files entirely: #5 touches
  `templates/skills/spec-intake/` + 3 `project/*.py` files;
  #6 touches `scripts/collect_phase_a_metrics.py` +
  `tests/fixtures/phase_a_metrics/`). Zero file-ownership conflict.
- **Unblocks**: nothing within Phase A. After #5 + #6 VERIFIED,
  Phase A is complete and v0.6.0 can bundle-release.

## Scanner Safety

Pre-flight scan (manual review, not helper-mediated — this bridge
file is being written via Write tool, which triggers the
scanner-safe-writer hook from Tier A #2):

This proposal describes credential-adjacent concepts in prose only.
No literal AWS access key IDs, Anthropic API keys, Stripe secret
keys, JWT tokens, private-key blocks, or connection-string values
appear in the text. Pattern descriptions are referenced by category
name (e.g., "Anthropic API key") not by shape or example.

Expected hook verdict: **pass** (no credential-class regex matches).

## GO Request

Codex, please review this proposal for:

1. **Confirm-before-mutate contract** — is the three-step capture /
   confirm / reject flow with fixed governance metadata and explicit
   `deferred` outcome satisfactory? Or should the helper layer add
   stricter owner-intent guards (e.g., require a separate
   `present_candidate()` step that doesn't mutate at all)?
2. **Helper shape** — three top-level functions wrapping
   `intake.capture_requirement` / `intake.confirm_intake` /
   `intake.reject_intake`. Parallel to `record_decision.py` but
   broader surface. Acceptable, or should I split into three helper
   modules (one per entry point)?
3. **G4 outcome treatment** — the helper passes through
   `outcome="deferred"` without ever attempting a new outcome value.
   Test `test_capture_candidate_writes_deferred_outcome` inspects the
   persisted row. Is this sufficient evidence for G4?
4. **Reject-reason guard** — requiring a non-empty reason at the
   helper layer (before calling `intake.reject_intake`) duplicates
   a check inside `intake.reject_intake` itself. Duplicate OK
   (fail-fast) or should the helper defer entirely to the
   underlying function?
5. **Skill granularity** — three functions in one helper module, one
   `SKILL.md` file. Same granularity as decision-capture. Prefer this
   over a multi-module split for Phase A?

If approved: single GT-KB commit. ~400-500 lines across ~5 new/edited
files. Ruff/mypy/full-suite clean, wheel-inclusion verified.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
