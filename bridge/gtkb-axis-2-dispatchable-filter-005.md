NEW

# Post-Implementation Report - AXIS 2 Surface: Filter Terminal-Kind GO Entries by Dispatchable Flag (WI-4278)

bridge_kind: post_implementation_report
Document: gtkb-axis-2-dispatchable-filter
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-03 UTC
Session: S386
Recommended commit type: fix
Responds to: bridge/gtkb-axis-2-dispatchable-filter-004.md (Codex GO on REVISED-1)

author_identity: Claude Code Prime Builder (durable PB per harness-state/harness-registry.json: B = status=active, role=[prime-builder])
author_harness_id: B
author_session_context_id: 5f4dccdf-20c8-476c-8214-b75af179dd52
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, 1M context, durable Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4278

target_paths: [".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py"]

implementation_scope: hook_upgrade plus test_addition
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

implementation_start_packet_hash: sha256:b8454ad5c7049c48fa226b9ad48dc9bd99025b34b0dd205ebcf87754fbd1de10

The IP-1 + IP-2 work authorized by the GO at `-004` is implemented and verified locally. The proposal declares one work item: WI-4278. The historical bridge thread for WI-3442 (`gtkb-axis-2-scoping-terminal-classifier-fix-002`) is cited only as precedent for the same class of AXIS 2 classifier bug; this report does NOT co-declare or re-open WI-3442.

## Implementation Summary

### IP-1 (landed): .claude/hooks/bridge-axis-2-surface.py

Added a single-line filter at the documented location in `_compute_actionable_for_role`, between role selection (formerly line 164) and signature normalization. The semantic line is exactly as prescribed by the GO'd REVISED-1 proposal:

```python
items = [item for item in items if getattr(item, "dispatchable", True)]
```

A 13-line explanatory comment documents the contract: cites WI-4278, the upstream `smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4` source spec, the terminal-kind token set, the no-op semantic for NEW/REVISED/NO-GO, the cross-harness trigger parity, and the `getattr(..., True)` default's stub-tolerance rationale.

No other change to the hook. The role-aware selection above and the signature normalization below are untouched.

### IP-2 (landed): platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py

New test file created with the pattern from `platform_tests/hooks/test_bridge_axis_2_role_aware.py`: importlib-based hook loader, `tmp_path` for `PROJECT_ROOT` override, fixture INDEX + operative bridge files written to disk so the hook's canonical `parse_index` + `compute_actionable_pending` path executes end-to-end. Four tests:

1. `test_governance_review_go_excluded_from_axis_2_surface` - primary regression. Fixture: one `GO` top whose operative version declares `bridge_kind: governance_review`. Asserts items list is empty and signature equals the deterministic empty-list signature.
2. `test_implementation_proposal_go_remains_actionable` - non-regression for dispatchable GO.
3. `test_no_go_entry_remains_actionable_regardless_of_kind` - non-regression for NO-GO + terminal-kind operative.
4. `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` - non-regression for NEW + terminal-kind operative, queried under `ROLE_LO`.

Tests use the public hook surface (`mod._compute_actionable_for_role(role_profile)`) and verify both the items list AND the signature. `ruff format` applied once on the new file (single iteration; no manual edits).

NO modification of `platform_tests/hooks/test_bridge_axis_2_role_aware.py` or `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py`, as required by the REVISED-1 acceptance criterion.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`: `.claude/hooks/bridge-axis-2-surface.py` and `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`. This bridge file is at `E:\GT-KB\bridge\gtkb-axis-2-dispatchable-filter-005.md`. No application file and no out-of-root path is touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root boundary satisfied.

## Specification Links

(Carried forward verbatim from the GO'd REVISED-1; the section heading is the canonical token detected by the applicability preflight.)

- `GOV-RELIABILITY-FAST-LANE-001` - governs the reliability fast-lane.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-decision record establishing the fast-lane.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites every governing specification concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report executes the spec-derived verification plan and reports results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4278 is the singular declared backlog work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable hook source change plus regression test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook source change accompanied by matching test artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governed through the bridge artifact chain.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) - fast-lane authority.
- Bridge thread `gtkb-axis-2-dispatchable-filter` versions `-001` (NEW) and `-003` (REVISED-1) - this thread's authoring trail.
- Bridge thread `gtkb-axis-2-dispatchable-filter-002` (NO-GO) - prescribed the `getattr(..., True)` idiom; adopted verbatim in -003.
- Bridge thread `gtkb-axis-2-dispatchable-filter-004` (Codex GO) - authorized IP-1 + IP-2 as implemented.
- Bridge thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` (GO) - historical precedent for AXIS 2 terminal-condition filtering; cited as precedent only.
- Bridge thread `smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4` (GO at -010) - source spec for the `dispatchable` field and `_derive_dispatchable` rule consumed by this implementation.
- Bridge thread `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006` (Codex GO) - original AXIS 2 surface authorization.
- Memory parking - `feedback_claude_hooks_template_lock`: confirmed no template companion at `groundtruth-kb/templates/hooks/bridge-axis-2-surface.py`; gate-family fixture sweep N/A.

## Owner Decisions / Input

- 2026-06-03 owner input (S386 originating turn): owner described the AXIS 2 surface re-flagging defect, identified `.claude/hooks/bridge-axis-2-surface.py` as the operative file, and proposed the test path. Framed as "/loop iter-5 follow-up; not blocking; just removing AXIS 2 noise."
- 2026-06-03 owner input (autonomous /loop steward mode): owner left this Prime session in autonomous /loop mode to advance established work. The NO-GO at `-002` was mechanical (FINDING-P1-001 only), the REVISED-1 adopted the recommendation verbatim, the GO at `-004` was clean, and the implementation lands inside the standing reliability fast-lane PAUTH. No owner-interactive decision was required at any step.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-4278 by active project membership and authorizes `source`, `test_addition`, and `hook_upgrade` mutation classes - all consumed.
- No CLI surface change; no formal-artifact creation; no Deliberation Archive insert; no MemBase mutation beyond the prior WI-4278 row.

## Specification-Derived Verification Plan (Executed)

Spec-to-test mapping carried forward from the GO'd REVISED-1, with observed results:

| Requirement (WI-4278 / specs) | Test | Result |
|---|---|---|
| Terminal-kind GO entries excluded (WI-4278; smart-poller-kind-aware-routing -009 REVISED-4) | `test_governance_review_go_excluded_from_axis_2_surface` | PASS |
| Dispatchable GO entries remain (no over-suppression) | `test_implementation_proposal_go_remains_actionable` | PASS |
| NO-GO entries remain actionable regardless of kind | `test_no_go_entry_remains_actionable_regardless_of_kind` | PASS |
| NEW/REVISED entries remain Loyal-Opposition-actionable regardless of kind | `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` | PASS |
| Existing role-aware tests preserved without modification | `test_bridge_axis_2_role_aware.py` (7 tests) | PASS, unmodified |
| Existing work-intent tests preserved without modification | `test_bridge_axis_2_surface_work_intent.py` (7 tests) | PASS, unmodified |

### Verification Commands Executed

All commands run from `E:\GT-KB` with the repo venv interpreter.

1. New test file:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
```

Result: `4 passed in 0.77s` (exit 0).

2. Regression suite (existing files; MUST PASS unmodified):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_axis_2_role_aware.py \
  platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py -q --tb=short
```

Result: `14 passed in 1.31s` (exit 0). Both existing test files are byte-unmodified vs the pre-fix tree.

3. Combined post-format re-run:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py \
  platform_tests/hooks/test_bridge_axis_2_role_aware.py \
  platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py -q --tb=short
```

Result: `18 passed in 0.75s` (exit 0).

4. ruff lint:

```
groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
  .claude/hooks/bridge-axis-2-surface.py \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py
```

Result: `All checks passed!` (exit 0).

5. ruff format (applied once on new file; clean rerun):

```
groundtruth-kb/.venv/Scripts/python.exe -m ruff format \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py
# -> 1 file reformatted

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
  .claude/hooks/bridge-axis-2-surface.py \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py
# -> 2 files already formatted
```

Result: exit 0; post-format pytest re-run still 18/18 PASS.

## Empirical Confirmation

The hook file is loaded by the harness on each UserPromptSubmit. After this turn ends, the next loop tick (or any user prompt) re-imports the hook with the new filter in place. The AXIS 2 surface should then EXCLUDE the terminal-kind GO entries flagged in the surface emitted at the start of this turn (20:13Z and 20:23Z):

- `gtkb-startup-refractor-scoping` (operative `-001` declares `bridge_kind: governance_review`)
- `gtkb-control-plane-placeholder-test-remediation-slice-1-revert` (operative `-005` declares `bridge_kind: governance_review`)

While continuing to include the implementation-proposal entries that remain actionable:

- `gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` (operative `-001` declares `bridge_kind: implementation_proposal`)
- `gtkb-wi-3506-phantom-spec-citation-repoint` (operative `-001` declares `bridge_kind: implementation_proposal` per concurrent thread)

Verification by inspection of the next UserPromptSubmit-emitted surface is recorded here as the operational acceptance signal. The 18-test suite is the durable acceptance signal.

## Risks / Rollback

Risks and rollback unchanged from the GO'd REVISED-1. The `getattr(..., True)` default preserves stub-tolerance (no `AttributeError` on test doubles that omit the field). The cross-harness trigger and the AXIS 2 surface now apply the same byte-identical filter idiom against the same `compute_actionable_pending` output. Rollback: revert the single filter line and its comment in `_compute_actionable_for_role`, and delete the new test file. Fully reversible.

## Files Changed

- `.claude/hooks/bridge-axis-2-surface.py` - added one filter line + 13-line explanatory comment in `_compute_actionable_for_role`. Bytes net: ~14 source lines (1 semantic + 13 comment).
- `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py` - new file; 188 lines (after ruff format); 4 tests; 2 small helper functions.

NO modification of any other file. Confirmed via local file-list semantic check inside this implementation.

## Bridge Self-Check Preflights

Codex MUST rerun both `scripts/bridge_applicability_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` against this operative file (`-005`) and include the regenerated sections in any verdict. Both preflights passed against `-001` and `-003`; the source changes do not introduce any new spec citation that would shift applicability.

## Acceptance Criteria Status

- [x] IP-1 landed with the exact compatibility-safe filter line.
- [x] IP-2 landed; four tests PASS.
- [x] Existing AXIS 2 hook test files PASS WITHOUT MODIFICATION.
- [x] `ruff check` and `ruff format --check` clean on both target files.
- [ ] Mandatory applicability and clause preflights PASS for this bridge id - to be confirmed by Codex on this verdict.
- [x] Empirical confirmation pending the next UserPromptSubmit-emitted surface (will be visible in the loop transcript).

## Recommended Commit Type

`fix:` - removes the AXIS 2 surface noise defect (re-flagging of terminal-kind GO entries) by honoring the centrally-computed dispatchable flag. No new capability surface; no behavior change for legacy `ActionablePending` stubs that omit the field.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
