# GO - GT-KB Skill `/gtkb-spec-intake`

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-spec-intake-003.md`
**Prior versions reviewed:** `bridge/gtkb-skill-spec-intake-001.md`, `bridge/gtkb-skill-spec-intake-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `0a60054`

## Verdict

GO.

The revised proposal resolves the `-002` blocker. The design now extends
`intake.py` with backward-compatible keyword-only governance metadata,
then has the skill helper pass `_CHANGED_BY =
"prime-builder/spec-intake-skill"`. That is the minimal path that makes
the promised persisted audit metadata implementable without duplicating
the intake pipeline.

This GO is for implementation of the revised design, not post-implementation
verification. The verification pass should still require the full proposed
test/format/type/build evidence.

## Rationale

The current GT-KB baseline still hard-codes generic intake attribution:

- `src/groundtruth_kb/intake.py:176-185` defines `capture_requirement()`
  with keyword-only proposal metadata, but no actor metadata.
- `src/groundtruth_kb/intake.py:211-220` writes the capture deliberation
  with `source_type="owner_conversation"`, `outcome="deferred"`,
  `changed_by="intake-pipeline"`, and the fixed capture reason.
- `src/groundtruth_kb/intake.py:228-231` defines `confirm_intake()` with
  no actor parameter.
- `src/groundtruth_kb/intake.py:260-265` writes the created spec with
  `changed_by="intake-pipeline"`.
- `src/groundtruth_kb/intake.py:291-299` writes the confirmation
  deliberation with `outcome="owner_decision"` and
  `changed_by="intake-pipeline"`.
- `src/groundtruth_kb/intake.py:311-315` defines `reject_intake()` with
  no actor parameter.
- `src/groundtruth_kb/intake.py:335-343` writes rejection with
  `outcome="no_go"` and `changed_by="intake-pipeline"`.

The revised proposal changes that exact choke point instead of leaving an
unused helper constant. The new function parameters are keyword-only and
default to the existing `"intake-pipeline"` value, so the existing CLI and
test callers remain source-compatible:

- `src/groundtruth_kb/cli.py:1272-1280` calls `capture_requirement()`
  without actor metadata.
- `src/groundtruth_kb/cli.py:1295` calls `confirm_intake()` without actor
  metadata.
- `src/groundtruth_kb/cli.py:1325` calls `reject_intake()` without actor
  metadata.
- `rg -n "capture_requirement\(|confirm_intake\(|reject_intake\(" src tests`
  found the CLI plus `tests/test_intake.py` as current callers.

The governance-actor precedent remains valid for the write-owning skill:

- `templates/skills/decision-capture/helpers/record_decision.py:25-26`
  defines fixed skill actor/reason constants.
- `templates/skills/decision-capture/helpers/record_decision.py:85-93`
  persists those values through `KnowledgeDB.insert_deliberation()`.

The scaffold/upgrade/doctor extension points also match the settled Phase A
pattern:

- `src/groundtruth_kb/project/scaffold.py:34-39` is the current managed
  skill list for initial scaffold.
- `src/groundtruth_kb/project/upgrade.py:56-61` is the current managed
  skill list for upgrade repair.
- `src/groundtruth_kb/project/upgrade.py:95-106` already maps nested skill
  helper paths generically.
- `src/groundtruth_kb/project/doctor.py:589-685` shows the two existing
  bridge-profile skill checks using keyword arguments to `ToolCheck`.
- `src/groundtruth_kb/project/doctor.py:979-980` wires both existing skill
  checks inside the bridge-profile doctor path.

## Findings

No blocking findings.

### N1 - Low - Caller inventory in `-003` names a non-existent hook path

**Evidence:** The proposal says the confirmed callers include
`src/groundtruth_kb/hooks/intake_classifier.py`. That path does not exist
in the inspected checkout. The shipped hook is
`templates/hooks/intake-classifier.py`, and `templates/hooks/intake-classifier.py:31-38`
imports `classify_requirement`, not `capture_requirement`,
`confirm_intake`, or `reject_intake`.

**Risk/impact:** Low. This does not affect the implementation plan because
the proposed new parameters are optional and the actual current callers
are still source-compatible. It does mean the backward-compat evidence in
the proposal should not cite the hook as a caller of the three modified
functions.

**Recommended action:** Correct the caller inventory in implementation notes
or PR text. Do not add hook-specific backward-compat tests for these three
functions unless the hook is changed to call them.

## Review Answers

1. **Signature shape:** Acceptable. Keyword-only optional parameters with
   defaults of `"intake-pipeline"` are the right backward-compatibility
   model for this narrow actor-metadata extension.
2. **`change_reason` parameterization:** Acceptable on
   `capture_requirement()` only. Confirm/reject reasons are state-transition
   reasons derived from the deliberation/spec IDs; uniform parameterization
   is not required for this skill.
3. **Backward-compat test scope:** A direct unit test is better than CLI/hook
   tests. The proposed capture default test is the minimum. Adding direct
   confirm/reject default-attribution assertions would be cheap and would
   better cover the three changed write paths, but absence of those extra
   tests is not a proposal blocker because the implementation can still be
   reviewed against the explicit default-value exit criterion.
4. **F1 guard tests:** The four proposed persistence assertions are the
   right coverage: capture deliberation, created spec, confirmation
   deliberation, and rejection deliberation. Do not over-consolidate them
   if separate tests keep failure causes clear.

## Implementation Conditions For Verification

1. Keep G4 unchanged: capture uses the existing `outcome="deferred"` and no
   new deliberation outcome value is added.
2. Implement `changed_by` as keyword-only with default `"intake-pipeline"`
   on all three intake functions; implement capture `change_reason` with
   the existing default string.
3. Ensure the helper actually passes `_CHANGED_BY` to all three intake calls
   and passes the skill capture reason for capture.
4. Preserve existing CLI behavior by leaving CLI calls unmodified unless
   there is a separate, explicit reason to expose actor metadata there.
5. Provide the proposed F1 persistence tests, scaffold/upgrade/doctor tests,
   ruff, format-check, mypy strict, full-suite, and wheel-inclusion evidence
   in the implementation report.

File bridge scan: 1 entries processed.
