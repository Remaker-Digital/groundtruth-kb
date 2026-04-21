# NO-GO - GT-KB Skill `/gtkb-spec-intake`

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-spec-intake-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `0a60054`

## Verdict

NO-GO.

The skill shape, single helper module, G4 `outcome="deferred"` treatment, and reject-reason fail-fast guard are directionally acceptable. I do not recommend adding a separate `present_candidate()` step for Phase A if the SKILL.md is explicit that `capture_candidate()` writes only a deliberation row and never writes specs, work items, ADRs, DCLs, or documents.

The blocker is that the proposal promises helper-level fixed governance metadata, especially `changed_by="prime-builder/spec-intake-skill"`, while the proposed wrapper-only implementation calls existing `intake.py` functions that hard-code `changed_by="intake-pipeline"`. The proposed tests therefore cannot pass as written, and the audit trail would not match the stated skill actor.

## Findings

### F1 - High - Fixed `changed_by` governance metadata is not implementable with the proposed wrapper-only design

**Claim under review:** The proposal says `capture_candidate()` wraps `intake.capture_requirement()` with fixed governance metadata, including `changed_by="prime-builder/spec-intake-skill"`, and proposes a helper test asserting that captured deliberations have that `changed_by` value.

**Evidence:**

- `groundtruth-kb/src/groundtruth_kb/intake.py:216-218` writes capture deliberations with `source_type="owner_conversation"`, `outcome="deferred"`, and `changed_by="intake-pipeline"`.
- `groundtruth-kb/src/groundtruth_kb/intake.py:260-264` writes the confirmed spec with `changed_by="intake-pipeline"`.
- `groundtruth-kb/src/groundtruth_kb/intake.py:296-298` writes the confirmation deliberation with `outcome="owner_decision"` and `changed_by="intake-pipeline"`.
- `groundtruth-kb/src/groundtruth_kb/intake.py:340-342` writes the rejection deliberation with `outcome="no_go"` and `changed_by="intake-pipeline"`.
- The existing decision-capture precedent owns the write directly through `KnowledgeDB.insert_deliberation`, which is why it can set fixed actor metadata: `groundtruth-kb/templates/skills/decision-capture/helpers/record_decision.py:25`, `:87-93`.
- A smoke command against the inspected checkout confirmed the runtime behavior:

```text
capture deferred owner_conversation intake-pipeline
confirm owner_decision owner_conversation intake-pipeline intake-pipeline
reject no_go owner_conversation intake-pipeline True
```

Command used:

```text
PYTHONPATH=src python - <<script importing KnowledgeDB plus capture_requirement/confirm_intake/reject_intake and printing persisted outcome/source_type/changed_by fields
```

**Risk/impact:**

- `test_capture_candidate_writes_fixed_source_type` as described will fail if it asserts `changed_by == "prime-builder/spec-intake-skill"`.
- More importantly, the resulting audit trail attributes the Phase A skill action to the generic intake pipeline, not to `/gtkb-spec-intake`.
- The proposal's `_CHANGED_BY = "prime-builder/spec-intake-skill"` constant is unused in the shown helper code, which makes the governance claim look satisfied in source while being absent from persisted rows.

**Required action:**

Revise the proposal to choose one consistent implementation contract:

1. If skill-specific actor metadata is required, change the implementation plan so the helper owns the relevant deliberation writes or so `intake.py` accepts explicit governance metadata. That revision must update the "out of scope" section if `intake.py` changes, and tests must assert capture, confirm, and reject actor metadata.
2. If reusing `intake.py` unchanged is the priority, revise the helper contract, SKILL.md language, and tests to state that persistence is attributed to `changed_by="intake-pipeline"`. Remove the unused `_CHANGED_BY` constant and do not claim fixed skill actor metadata.

## Non-Blocking Review Answers

- **Confirm-before-mutate:** Acceptable for Phase A if documented precisely: capture mutates the Deliberation Archive only; confirm is the only spec-writing path; reject writes only a rejection deliberation version. No separate `present_candidate()` step is required for this scoped skill.
- **Helper shape:** One helper module with three top-level functions is acceptable. Splitting into three modules would add friction without reducing the main risk.
- **G4 outcome treatment:** Sufficient. `KnowledgeDB.insert_deliberation()` accepts `deferred` at `groundtruth-kb/src/groundtruth_kb/db.py:4225`, and `capture_requirement()` already writes `outcome="deferred"` at `groundtruth-kb/src/groundtruth_kb/intake.py:217`. No schema migration or new outcome is needed.
- **Reject-reason guard:** Duplicate fail-fast validation in the helper is acceptable and improves skill-boundary ergonomics. Keep the `strip()` check because `intake.reject_intake()` only rejects falsey reasons.
- **Skill granularity:** The proposed single `SKILL.md` plus one helper module matches the Phase A skill pattern and should remain the default.

## Conditions For GO On Revision

1. Resolve the `changed_by` contract mismatch in both prose and tests.
2. If skill actor metadata remains required, include tests for persisted `changed_by` on capture, confirm deliberation, rejected deliberation, and the created spec.
3. Keep G4 exactly as proposed: use the existing `deferred` outcome and do not add `pending_confirmation` or any other schema value.
4. Keep `intake.py`, `db.py`, and `pyproject.toml` untouched only if the revised contract no longer promises metadata that those files currently prevent.

File bridge scan: 1 entries processed.
