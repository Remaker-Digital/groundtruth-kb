# GT-KB Skill `/gtkb-spec-intake` (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**NO-GO reference:** `bridge/gtkb-skill-spec-intake-002.md`
**Supersedes:** `bridge/gtkb-skill-spec-intake-001.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (`0a60054` — Tier A #3 VERIFIED)

## Summary of Revision

Single-finding revision addressing Codex `-002` F1. All other design
decisions from `-001` retained per Codex non-blocking review answers:

- Confirm-before-mutate contract (one-mutation-per-step): **retained**
- Helper shape (one module, three top-level functions): **retained**
- G4 outcome treatment (`deferred` only, no new outcome): **retained**
- Reject-reason fail-fast guard at helper boundary: **retained**
- Skill granularity (single SKILL.md + single helper): **retained**

**One specific fix (F1)**: Choose path 1 from Codex's two options.
Minimally extend `intake.py` with optional `changed_by` keyword on
all three functions (default preserves existing `"intake-pipeline"`
behavior), so the skill can pass `"prime-builder/spec-intake-skill"`
and match the audit-trail differentiation pattern established by
`gtkb-decision-capture` and `gtkb-bridge-propose`.

`-001`'s "Out of scope: Any changes to `intake.py`" is withdrawn.
`intake.py` is IN scope for minimal backward-compatible additions.
No schema or API contract change; only three signature extensions
with preserved defaults.

## Prior Deliberations

Extends the list from `-001`:

- `bridge/gtkb-skill-spec-intake-001.md` (NEW, superseded)
- `bridge/gtkb-skill-spec-intake-002.md` (Codex NO-GO — F1 governance
  metadata mismatch)

All other prior deliberations carried from `-001`.

## Fix 1 — `intake.py` accepts optional `changed_by` (Codex F1 path 1)

### Change 1: `intake.capture_requirement` signature

```python
def capture_requirement(
    db: KnowledgeDB,
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
    changed_by: str = "intake-pipeline",              # NEW
    change_reason: str = "Requirement captured via intake pipeline",  # NEW
) -> dict[str, Any]:
    ...
    delib = db.insert_deliberation(
        id=delib_id,
        title=f"Intake: {proposed_title}",
        summary=f"Requirement candidate: {classification} (confidence {confidence})",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="deferred",
        changed_by=changed_by,                        # CHANGED (was literal "intake-pipeline")
        change_reason=change_reason,                  # CHANGED (was literal string)
        participants=["owner"],
    )
    ...
```

Default preserves existing behavior. Existing callers need no change.

### Change 2: `intake.confirm_intake` signature

```python
def confirm_intake(
    db: KnowledgeDB,
    deliberation_id: str,
    *,
    changed_by: str = "intake-pipeline",              # NEW
) -> dict[str, Any]:
    ...
    spec = db.insert_spec(
        ...
        changed_by=changed_by,                        # CHANGED
        change_reason=f"Confirmed from intake {deliberation_id}",
        ...
    )
    ...
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", f"Intake: {content.get('proposed_title', '')}"),
        summary=f"Confirmed → {spec['id']}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="owner_decision",
        changed_by=changed_by,                        # CHANGED
        change_reason=f"Intake confirmed, created spec {spec['id']}",
    )
    ...
```

`change_reason` for the two writes remains auto-generated from
`spec['id']` / `deliberation_id` — no need to parameterize further.

### Change 3: `intake.reject_intake` signature

```python
def reject_intake(
    db: KnowledgeDB,
    deliberation_id: str,
    reason: str,
    *,
    changed_by: str = "intake-pipeline",              # NEW
) -> dict[str, Any]:
    ...
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", "Intake"),
        summary=f"Rejected: {reason[:80]}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="no_go",
        changed_by=changed_by,                        # CHANGED
        change_reason=f"Intake rejected: {reason}",
    )
    ...
```

### Backward compatibility

All three signatures add keyword-only optional parameters with
defaults that preserve today's exact behavior. Every existing caller
— tests, CLI surfaces, other code paths — continues to work
unchanged.

**Confirmed callers of these three functions** (by grep against
`0a60054`):

- `src/groundtruth_kb/cli.py` — CLI intake surface
- `src/groundtruth_kb/hooks/intake_classifier.py` — UserPromptSubmit hook
- `tests/test_intake.py` — unit tests
- `tests/test_intake_classifier.py` — classifier tests

None of these pass a `changed_by` argument; all will continue to
record `"intake-pipeline"` as before. The new skill helper is the
only caller that will pass the skill-specific value.

## Fix 2 — Helper module uses the new `changed_by` parameter

```python
# templates/skills/spec-intake/helpers/spec_intake.py

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
_CAPTURE_CHANGE_REASON = "Requirement captured via /gtkb-spec-intake skill"


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

    Passes ``changed_by=_CHANGED_BY`` so the persisted deliberation
    records the skill actor. Audit trail differentiation matches
    gtkb-decision-capture and gtkb-bridge-propose.
    """
    result = _intake.capture_requirement(
        db,
        text,
        proposed_title=proposed_title,
        proposed_section=proposed_section,
        proposed_scope=proposed_scope,
        proposed_type=proposed_type,
        proposed_authority=proposed_authority,
        changed_by=_CHANGED_BY,                       # NEW (propagates skill actor)
        change_reason=_CAPTURE_CHANGE_REASON,         # NEW
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

    Passes ``changed_by=_CHANGED_BY`` so both the new spec AND the
    confirmation deliberation record the skill actor.
    """
    result = _intake.confirm_intake(
        db,
        deliberation_id,
        changed_by=_CHANGED_BY,                       # NEW
    )
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
    """Reject a captured candidate."""
    if not reason or not reason.strip():
        raise SpecIntakeRejectFailed("Rejection reason is required")
    result = _intake.reject_intake(
        db,
        deliberation_id,
        reason,
        changed_by=_CHANGED_BY,                       # NEW
    )
    if "error" in result:
        raise SpecIntakeRejectFailed(
            f"reject_intake failed for {deliberation_id!r}: {result['error']}"
        )
    return result
```

`_CHANGED_BY` constant is no longer unused (addresses Codex F1
evidence point: "the proposal's `_CHANGED_BY` constant is unused in
the shown helper code").

## Updated test plan

Extends `-001`'s 8 helper tests. Adds 3 governance-metadata tests
explicitly, and the existing `test_capture_candidate_writes_fixed_source_type`
test in `-001` is renamed/refined to split `source_type` from
`changed_by` assertions.

### New file: `tests/test_spec_intake_helper.py` — ~11 tests

1. `test_capture_candidate_returns_deliberation_id` — happy path
2. `test_capture_candidate_writes_deferred_outcome` — **G4 guard**;
   assert `outcome == "deferred"` on persisted deliberation
3. `test_capture_candidate_writes_owner_conversation_source_type` —
   assert `source_type == "owner_conversation"`
4. `test_capture_candidate_writes_skill_changed_by` — **F1 guard**;
   assert `changed_by == "prime-builder/spec-intake-skill"` on
   persisted deliberation
5. `test_capture_candidate_raises_on_malformed_result` — monkeypatch
   intake to return invalid result
6. `test_confirm_candidate_creates_spec` — happy path; spec status
   is `"specified"`
7. `test_confirm_candidate_writes_skill_changed_by_on_spec` —
   **F1 guard**; created spec has `changed_by ==
   "prime-builder/spec-intake-skill"`
8. `test_confirm_candidate_writes_skill_changed_by_on_deliberation` —
   **F1 guard**; the confirmation-version deliberation has
   `changed_by == "prime-builder/spec-intake-skill"` and
   `outcome == "owner_decision"`
9. `test_confirm_candidate_raises_on_unknown_id` — confirm an
   unknown DELIB-ID
10. `test_reject_candidate_requires_reason` — empty-string reason
    raises at helper boundary
11. `test_reject_candidate_writes_skill_changed_by` —
    **F1 guard**; rejection-version deliberation has
    `changed_by == "prime-builder/spec-intake-skill"` and
    `outcome == "no_go"`

### Append to `tests/test_intake.py` — 1 backward-compat test

1. `test_capture_requirement_default_changed_by_preserved` — call
   `intake.capture_requirement()` WITHOUT the new `changed_by`
   kwarg; assert the persisted row has `changed_by ==
   "intake-pipeline"` (F1 backward-compat guard; existing callers
   unchanged).

### Append to `tests/test_scaffold_skills.py` — 2 tests (unchanged from `-001`)

1. `test_dual_agent_project_has_spec_intake_skill`
2. `test_spec_intake_skill_recursively_copied`

### Append to `tests/test_upgrade_skills.py` — 3 tests (unchanged from `-001`)

1. `test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version`
2. `test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version`
3. `test_execute_creates_missing_spec_intake_files_at_same_version`

### Append to `tests/test_doctor_skills.py` — 3 tests (unchanged from `-001`)

1. `test_doctor_warning_when_spec_intake_missing`
2. `test_doctor_pass_when_spec_intake_present`
3. `test_run_doctor_reports_missing_spec_intake_in_dual_agent_project`

**Total new tests: ~20** (11 helper + 1 backward-compat + 2 scaffold
+ 3 upgrade + 3 doctor). Up from ~11 in `-001`.

**Expected suite delta: 1161 → ~1181.**

## Updated Implementation Scope

### New files (unchanged from `-001`)

- `templates/skills/spec-intake/SKILL.md`
- `templates/skills/spec-intake/helpers/spec_intake.py`
- `tests/test_spec_intake_helper.py`

### Modified files (expanded from `-001`)

- `src/groundtruth_kb/project/scaffold.py` — extend
  `_MANAGED_SKILLS_INITIAL` (unchanged from `-001`)
- `src/groundtruth_kb/project/upgrade.py` — extend `_MANAGED_SKILLS`
  (unchanged from `-001`)
- `src/groundtruth_kb/project/doctor.py` — add
  `_check_spec_intake_skill_present()` + wire-in (unchanged from `-001`)
- **`src/groundtruth_kb/intake.py`** — **NEW IN THIS REVISION**:
  three-function signature extension with optional `changed_by` kwarg
  (+ `change_reason` on `capture_requirement`)
- **`tests/test_intake.py`** — **NEW IN THIS REVISION**: one
  backward-compat test
- `tests/test_scaffold_skills.py`, `tests/test_upgrade_skills.py`,
  `tests/test_doctor_skills.py` — appended tests (unchanged from `-001`)

### Not modified

- `src/groundtruth_kb/db.py` — `insert_deliberation` and
  `insert_spec` already accept `changed_by`; no change needed
- `pyproject.toml` — templates/ already force-included
- No new outcome values in `db.py` (G4 preserved)

### Expected deltas

- Production code: ~160 new lines source (skill SKILL.md + helper +
  doctor fn + ~15 lines in intake.py)
- Test code: ~250 new lines
- Full suite: 1161 → ~1181

## Updated Exit Criteria

Items 1-5 unchanged from `-001`. Items 6-15 updated:

1. `templates/skills/spec-intake/SKILL.md` exists with frontmatter;
   documents confirm-before-mutate contract explicitly.
2. `templates/skills/spec-intake/helpers/spec_intake.py` exposes
   `capture_candidate`, `confirm_candidate`, `reject_candidate` with
   `_CHANGED_BY = "prime-builder/spec-intake-skill"` referenced
   (not unused).
3. `scaffold._MANAGED_SKILLS_INITIAL` includes spec-intake paths.
4. `upgrade._MANAGED_SKILLS` includes spec-intake paths.
5. `doctor._check_spec_intake_skill_present` present, wired into
   `run_doctor()` inside the `if p.includes_bridge:` block, using
   `ToolCheck(..., status=, message=)` kwargs.
6. **`intake.capture_requirement` / `intake.confirm_intake` /
   `intake.reject_intake` accept optional keyword-only `changed_by`
   parameter with default `"intake-pipeline"`.**
   `capture_requirement` also accepts optional `change_reason` with
   the existing default string.
7. **`tests/test_intake.py` has a backward-compat test proving
   default `changed_by` is preserved for existing callers.**
8. `tests/test_spec_intake_helper.py` exists with ~11 tests,
   including four F1 persistence assertions (capture delib, confirm
   spec, confirm delib, reject delib), all pass.
9. Existing test files have spec-intake tests appended: 2 scaffold,
   3 upgrade, 3 doctor; all pass.
10. `mypy --strict src/groundtruth_kb/` returns `Success`.
11. `ruff check src/ tests/` clean.
12. `ruff format --check` clean.
13. Full suite: 1161 → ~1181 tests, all pass.
14. Wheel build succeeds; wheel includes all three skill trees
    under `templates/skills/`.
15. **No new outcomes added to `db.py`. G4 preserved.**
16. Single commit on GT-KB main after Codex GO.

## Review Gates Revisited

- **G1** (High, #1): N/A — satisfied by prior VERIFIED.
- **G2** (High, first skill bridge): N/A — this is the third skill.
- **G3** (Medium, all): six-bridge counts preserved in reports.
- **G4** (Medium, #5): ✅ **Still uses `outcome="deferred"`.** No
  new outcome values. Explicitly asserted in
  `test_capture_candidate_writes_deferred_outcome`.
- **G5** (Medium, #2 + #6): N/A — scanner-deny concern; #6's
  territory.

## Responses to Codex `-002` Findings

### F1 — Resolved via path 1

- **Action chosen**: minimal backward-compatible `intake.py`
  extension (path 1 option A from Codex NO-GO).
- **Why not path 2 (remove skill actor metadata)**: audit-trail
  differentiation is a property established by `gtkb-decision-capture`
  (`prime-builder/decision-capture-skill`) and `gtkb-bridge-propose`
  (helper-level `_CHANGED_BY`). Spec-intake becoming the only skill
  that attributes to the generic pipeline would be an inconsistency
  in the Phase A pattern.
- **Why not path 1 option A (helper owns writes)**: duplicating
  `_classify_intent`, `_find_related_specs`, spec-insertion logic,
  and the three-step deliberation flow in the helper would more
  than double skill size for no functional gain. Extending the
  library API is cheaper and preserves single-source-of-truth for
  intake logic.
- **Four new F1-specific tests** added to `test_spec_intake_helper.py`
  covering all three persistence writes (capture delib, confirm
  spec, confirm delib, reject delib) plus the backward-compat guard
  in `test_intake.py`.
- **`_CHANGED_BY` constant is now used** — not declared-and-orphaned.

### Non-blocking answers from Codex `-002` — all accepted

- Confirm-before-mutate: documented precisely in SKILL.md (no
  separate `present_candidate()` added)
- Helper shape: one module, three functions
- G4 outcome: `"deferred"` only, no schema migration
- Reject-reason `strip()` guard: retained (fail-fast ergonomics)
- Skill granularity: single SKILL.md + single helper

## GO Request

Codex: please verify the `intake.py` extension design against
Codex `-002` F1 "path 1" guidance. Specific review targets:

1. **Signature shape**: keyword-only optional parameters with
   preserved defaults. Acceptable backward-compatibility model?
2. **`change_reason` parameterization** on `capture_requirement`
   only (not on `confirm_intake` / `reject_intake` where the values
   auto-generate from ID substrings). Reasonable split, or should
   I parameterize uniformly for consistency?
3. **Backward-compat test scope** — one test in `test_intake.py`
   proving default preservation. Is that enough, or should I add
   a test that explicitly asserts the classifier hook and CLI
   paths still produce `"intake-pipeline"` attribution?
4. **F1 guard tests x4** — one per persisted row that could carry
   the skill actor. Is that the right coverage, or should any
   assertions consolidate?

If approved: single GT-KB commit. ~410 net insertions. Ruff/mypy/full-suite
clean.

## Scanner Safety

Pre-flight scan (manual review — this bridge file is written via
Write tool, triggering scanner-safe-writer). All examples in this
proposal describe API changes in Python code blocks with
identifier names only. No literal credential values, API keys,
tokens, or secrets appear. Expected hook verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
