NEW

# Implementation Proposal — AXIS 2 Surface: Filter Terminal-Kind GO Entries by Dispatchable Flag (WI-4278)

bridge_kind: prime_proposal
Document: gtkb-axis-2-dispatchable-filter
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-03 UTC
Session: S386
Recommended commit type: fix

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
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This NEW proposal fixes a noise defect in `.claude/hooks/bridge-axis-2-surface.py`: the in-session AXIS 2 surface keeps re-flagging terminal-kind GO threads (governance_review, scoping, closure, parking, index/thread reconciliation, operational_state_change, candidate_spec_intake, loyal_opposition_advisory) even though the cross-harness event-driven trigger correctly suppresses headless dispatch on the same `dispatchable=False` classification. The fix is routed through the reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) under the standing `PROJECT-GTKB-RELIABILITY-FIXES` authorization.

The proposal declares one work item: WI-4278. The historical bridge thread for WI-3442 (`gtkb-axis-2-scoping-terminal-classifier-fix-002`) is cited only as precedent for the same class of AXIS 2 classifier bug; this proposal does NOT co-declare or re-open WI-3442.

## Claim

`compute_actionable_pending` already attaches a centrally-computed `dispatchable: bool` flag to every `ActionablePending` entry (per `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 GO at -010). The cross-harness event-driven trigger consumes that flag to suppress headless spawn for terminal-kind GO verdicts. The AXIS 2 surface hook does NOT consume the flag: it selects the role-appropriate list and renders every entry, regardless of dispatchability. Result: a `governance_review` GO with `target_paths: []` re-fires the in-session surface on every wake, and Prime sessions waste turns claiming, reading, and standing down.

The fix is a one-line filter in `_compute_actionable_for_role`, applied AFTER the role-selection step and BEFORE the signature hash. Filtering before signature means the surface re-fires only when a truly dispatchable entry's set changes — terminal-kind GO entries that already had verdicts recorded never re-surface.

## Defect Evidence

Live state at filing (2026-06-03 19:40Z surface):

- `bridge/INDEX.md` line 1158-1164: `gtkb-control-plane-placeholder-test-remediation-slice-1-revert` top status is `GO@-006`. Operative Prime version `-005` declares `bridge_kind: governance_review`, `target_paths: []`, `requires_verification: false`, `implementation_scope: none`. Per `groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS` (line 89-106 of `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`), `governance_review` is a terminal-kind token; per `_derive_dispatchable` (line 218-238), a GO + terminal classification yields `dispatchable=False`.
- `bridge/INDEX.md` line 115-117: `gtkb-startup-refractor-scoping` top status is `GO@-002`. Operative Prime version `-001` declares `bridge_kind: governance_review`. Same terminal classification.
- Today's AXIS 2 surface (system-reminder at 19:40Z) flagged both as Prime-actionable alongside one true `implementation_proposal` entry (`gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`). The terminal-kind entries are the noise; the implementation entry should remain.
- `.claude/hooks/bridge-axis-2-surface.py:154-156`: `_compute_actionable_for_role` calls `compute_actionable_pending(parse_result, project_root=PROJECT_ROOT)`, which returns `(actionable_prime, actionable_codex)` lists with `dispatchable` already attached.
- `.claude/hooks/bridge-axis-2-surface.py:164`: `items = actionable_prime if role_profile == ROLE_PRIME else actionable_codex`. No `item.dispatchable` consumption follows.
- `.claude/hooks/bridge-axis-2-surface.py:168-177`: the normalized signature drops the `dispatchable` field entirely (`document_name`, `top_status`, `top_file` only), so the signature changes whenever a terminal-kind entry appears or disappears.
- Direct precedent (same compute path, same class of bug): the historical thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` (GO) added `_scoping_terminal_with_successor` to `compute_actionable_pending` to exclude scoping threads whose successor exists. This proposal applies the same family of terminal filter to a different consumer (the AXIS 2 in-session surface, not the central compute), and reuses the existing centrally-computed `dispatchable` flag rather than adding a parallel classifier.

Reproduction (post-fix verification target):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
```

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`: `.claude/hooks/bridge-axis-2-surface.py` and `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`. This bridge file is at `E:\GT-KB\bridge\gtkb-axis-2-dispatchable-filter-001.md`. No application file and no out-of-root path is touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root boundary satisfied.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this proposal follows the NEW/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing specification concretely in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification Plan maps the fixed behavior to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths and this bridge file are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — the singular declared work item WI-4278 is the tracked backlog item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is delivered as a durable hook change plus a regression test, not an undocumented patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching the AXIS 2 surface hook triggers matching test artifacts; this proposal adds one.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work is governed through the bridge artifact chain and the linked work item.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) — established the reliability fast-lane under which this fix is routed; for an eligible defect fix no per-fix deliberation or formal-artifact-approval packet is required.
- Bridge thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` (GO) — historical precedent: the same `compute_actionable_pending` function received a different terminal-condition filter (scoping-thread-with-successor). The pattern of "AXIS 2 classifier missed a terminal condition; cross-harness trigger correctly suppressed it; in-session surface still flagged it" is documented there. This proposal applies the same pattern with a one-line filter that reuses the centrally-computed `dispatchable` field instead of adding a sibling classifier. Cited as precedent only; no co-declaration of that historical thread's work item.
- Bridge thread `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 (GO at -010) — established the `dispatchable` + `classification` fields on `ActionablePending` and the `_derive_dispatchable` rule used here. The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) already filters on `dispatchable`; this proposal extends the same filter to the AXIS 2 in-session surface.
- Bridge thread `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006` (Codex GO) — original AXIS 2 surface authorization. The hook was scoped to "byte-identical to `_signature`" but the signature in the cross-harness trigger is computed AFTER `dispatchable` filtering, not over the raw `actionable_prime` list. This proposal closes that gap.
- Memory parking — `feedback_claude_hooks_template_lock` records that `.claude/hooks/*.py` files often have template companions under `groundtruth-kb/templates/hooks/`. Confirmed at filing: no template companion exists for `bridge-axis-2-surface.py` (`find groundtruth-kb/templates/hooks -name "bridge-axis-2*"` returns empty), so a template-paired edit is not required and the gate-family fixture sweep does not apply.

## Owner Decisions / Input

- 2026-06-03 owner input (this turn): the owner described the AXIS 2 surface re-flagging defect, identified `.claude/hooks/bridge-axis-2-surface.py` as the operative file, and proposed the test path `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`. The owner framed it as a follow-up from the /loop iter-5 session today (control-plane Slice-1 thread re-scoped to governance_review yet still surfacing) and explicitly noted "not blocking; just removing AXIS 2 noise."
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-4278 by active project membership and authorizes `source`, `test_addition`, and `hook_upgrade` mutation classes. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required; the bridge proposal, Loyal Opposition review, and all safety gates remain in force.
- No CLI surface change: this proposal adds no subcommand and no new flag, so the standing fast-lane PAUTH's exclusion of `cli_extension` (per `feedback_fastlane_standing_pauth_excludes_cli_surface`) does not apply.
- No blocking owner decision is pending. This proposal needs only a Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-4278 ("AXIS 2 surface: filter terminal-kind GO entries by dispatchable flag") is the operative requirement. The dispatchable contract is already specified by `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 GO at -010 (the source spec for the `dispatchable` field); this proposal extends an existing centrally-computed classification to a downstream consumer that overlooked it. No new or revised specification is required.

## Reliability Fast-Lane Eligibility

Per `GOV-RELIABILITY-FAST-LANE-001`:

- Origin is `defect` — the AXIS 2 surface is producing noise that does not reflect actionable Prime work; this contradicts its stated purpose ("surfacing newly-actionable Prime bridge work") per the hook's docstring.
- No new public API/CLI/behavior beyond removing the defect — the `dispatchable` flag and the terminal classification are already published by `compute_actionable_pending`; this consumer simply honors them.
- No new or revised requirement or specification — the dispatchable contract is already specified upstream (smart-poller-kind-aware-routing -009 REVISED-4).
- Small and single-concern: 2 files (1 hook source, 1 new test file). Source change is ~3 net lines (one filter line plus an explanatory comment). Test file is ~80 lines of fixture plus assertions. Well under the fast-lane ceiling of about 3 files / 150 net source lines.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-4278) is targeted; it is a newly-created member of `PROJECT-GTKB-RELIABILITY-FIXES` under the standing reliability fast-lane authorization. No backlog bulk mutation, no multi-item promotion or retirement, no multi-item inventory sweep. The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) waives the per-fix formal-artifact-approval packet for an eligible defect fix; this proposal creates no GOV/ADR/DCL/SPEC artifact and no Deliberation Archive record.

## Bridge INDEX Update Evidence

NEW filed at `E:\GT-KB\bridge\gtkb-axis-2-dispatchable-filter-001.md`; a new top entry is prepended to canonical `E:\GT-KB\bridge\INDEX.md`. `bridge/INDEX.md` remains the canonical bridge workflow state.

## Proposed Scope

### IP-1: Filter selected items on `item.dispatchable` in `_compute_actionable_for_role`

In `.claude/hooks/bridge-axis-2-surface.py`, between the role-selection step and the signature normalization step (currently line 164-178), add a one-line filter that drops entries whose `dispatchable` flag is False:

```
items = actionable_prime if role_profile == ROLE_PRIME else actionable_codex
# Per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4: compute_actionable_pending
# attaches a centrally-computed `dispatchable` flag that reflects bridge_kind
# classification. Terminal-kind GO entries (governance_review, scoping, closure,
# parking, index/thread reconciliation, operational_state_change,
# candidate_spec_intake, loyal_opposition_advisory) have dispatchable=False and
# must be excluded from the in-session surface, mirroring the cross-harness
# event-driven trigger's dispatch suppression. NEW/REVISED/NO-GO entries are
# always dispatchable=True, so this filter is a no-op for the Loyal Opposition
# role and for Prime NO-GO entries.
items = [item for item in items if item.dispatchable]
```

Effect: the surface signature is computed only over dispatchable entries. A `governance_review` GO at any version no longer contributes to the signature, no longer triggers re-surfacing, and no longer prints in the markdown table. NEW/REVISED entries (Loyal Opposition role) are unaffected because they always have `dispatchable=True`. Prime NO-GO entries are unaffected for the same reason. The hook continues to honor the `GTKB_NO_AXIS_2_SURFACE=1` env-var emergency stop and the `dismiss bridge surface` owner-keyword suppression.

Bytes touched: ~3 net lines (one filter line plus the explanatory comment).

### IP-2: Regression test in `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`

Add a new test file that constructs in-memory fixture inputs and exercises `_compute_actionable_for_role` via the hook module's importable surface. Pattern mirrors the existing `platform_tests/hooks/test_bridge_axis_2_role_aware.py` (importlib-based hook loader; `tmp_path` for `PROJECT_ROOT` override; `parse_index` + `compute_actionable_pending` driven through a fixture INDEX file).

Tests:

1. `test_governance_review_go_excluded_from_axis_2_surface` — primary regression. Writes a fixture `bridge/INDEX.md` with one `GO` entry whose operative Prime version declares `bridge_kind: governance_review`. Writes the operative Prime file with the header. Calls `_compute_actionable_for_role(ROLE_PRIME)`. Asserts the returned items list is empty and the returned signature is the empty-list signature. Fails on the pre-fix code (entry would be included); passes after IP-1.
2. `test_implementation_proposal_go_remains_actionable` — non-regression. Writes a fixture `bridge/INDEX.md` with one `GO` entry whose operative Prime version declares `bridge_kind: implementation_proposal`. Asserts the returned items list contains the one entry. Confirms the filter is precise (does not over-suppress dispatchable work).
3. `test_no_go_entry_remains_actionable_regardless_of_kind` — non-regression. Writes a fixture INDEX with a `NO-GO` top entry whose operative Prime version declares `bridge_kind: governance_review`. Per `_derive_dispatchable`, NO-GO is always `dispatchable=True` regardless of classification. Asserts the entry is retained. Confirms Prime revision flows for terminal-kind NO-GO are preserved.
4. `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` — non-regression. Writes a fixture INDEX with a `NEW` top entry whose operative Prime version declares `bridge_kind: governance_review`. Per `_derive_dispatchable`, NEW/REVISED are always dispatchable=True. Asserts the entry is retained when `role_profile == ROLE_LO`. Confirms Codex review flows for terminal-kind proposals are preserved.

## Specification-Derived Verification Plan

Spec-to-test mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Requirement (WI-4278 / specs) | Behavior verified | Test |
|---|---|---|
| Terminal-kind GO entries must not appear on the AXIS 2 surface (WI-4278; smart-poller-kind-aware-routing -009 REVISED-4) | `_compute_actionable_for_role(ROLE_PRIME)` returns empty items + empty-list signature for a fixture with one `governance_review` GO | `test_governance_review_go_excluded_from_axis_2_surface` |
| Dispatchable GO entries remain on the surface (no over-suppression) | `_compute_actionable_for_role(ROLE_PRIME)` returns one item for a fixture with one `implementation_proposal` GO | `test_implementation_proposal_go_remains_actionable` |
| NO-GO entries remain actionable regardless of classification (`_derive_dispatchable` invariant) | `_compute_actionable_for_role(ROLE_PRIME)` returns the entry for a fixture with one `governance_review` NO-GO | `test_no_go_entry_remains_actionable_regardless_of_kind` |
| NEW/REVISED entries remain actionable for Loyal Opposition regardless of classification | `_compute_actionable_for_role(ROLE_LO)` returns the entry for a fixture with one `governance_review` NEW | `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` |
| Existing role-aware selection and signature semantics preserved (no regression) | Existing tests `test_bridge_axis_2_role_aware.py` continue to pass | existing suite (regression) |
| Existing work-intent claim split semantics preserved (no regression) | Existing tests `test_bridge_axis_2_surface_work_intent.py` continue to pass | existing suite (regression) |

Verification commands (run from `E:\GT-KB`):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py -q --tb=short` (regression)
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`

## Acceptance Criteria

- IP-1 landed; the filter line and comment present at the documented location; one-line semantic change (`items = [i for i in items if i.dispatchable]`).
- IP-2 landed; all four new tests PASS.
- The existing AXIS 2 hook tests (`test_bridge_axis_2_role_aware.py`, `test_bridge_axis_2_surface_work_intent.py`) PASS without modification.
- `ruff check` and `ruff format --check` are clean on both target files.
- Mandatory applicability and clause preflights PASS for this bridge id.
- Empirical confirmation in the post-implementation report: the next SessionStart wake after the fix lands shows the AXIS 2 surface excluding `gtkb-control-plane-placeholder-test-remediation-slice-1-revert` and `gtkb-startup-refractor-scoping` while continuing to include `gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`.

## Risks / Rollback

- Risk: over-suppression. Mitigated by IP-2 tests 2-4 (implementation_proposal GO remains; NO-GO regardless of kind remains; NEW/REVISED for LO remains). The filter reuses the centrally-computed `dispatchable` flag from `_derive_dispatchable`, which already encodes the full GO/NO-GO/NEW/REVISED matrix; this proposal does not introduce a parallel classifier that could drift.
- Risk: signature collision. If a thread changes between dispatchable and non-dispatchable (e.g., a proposal is revised from implementation_proposal to governance_review), the surface signature changes (entry disappears) — but only at the next signature-recompute, not retroactively. Acceptable; mirrors cross-harness trigger semantics.
- Risk: ambiguous-classification entries. `_derive_dispatchable` returns True for `classification != "terminal"`, which includes `"ambiguous"`. So bridge files with no `bridge_kind:` header continue to surface (pre-fix behavior preserved for legacy proposals). No regression.
- Risk: dispatchable-flag drift from cross-harness trigger. Both consumers (cross-harness trigger and AXIS 2 surface) consume the same `compute_actionable_pending` API and apply the same filter logic. If the upstream classification changes, both consumers move together.
- Rollback: revert the single filter line and its comment in `_compute_actionable_for_role`, and delete the new test file. Fully reversible.

## Observations (Not in Scope)

Surfaced for the reviewer's record; not part of the WI-4278 fix scope:

- The user's task description suggested a finer-grained filter (`bridge_kind == "governance_review" AND requires_verification == false`). This proposal uses the broader `dispatchable=False` filter because `governance_review` is already classified terminal by `notify.py:103` regardless of `requires_verification`, and the upstream cross-harness trigger also filters on the broader rule. If a future need emerges to surface `governance_review` proposals with `requires_verification=true` (e.g., a governance_review that authorizes a rule-file change requiring a post-impl report), the right place to refine that distinction is `_KIND_TERMINAL_TOKENS` / `_derive_dispatchable` in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, not in the AXIS 2 hook — so the cross-harness trigger and the AXIS 2 surface stay aligned.
- The scoping-with-successor filter (added by the historical thread `gtkb-axis-2-scoping-terminal-classifier-fix-002`) is structurally separate from the `dispatchable` flag. It excludes scoping threads whose successor implementation exists, which is a property of the parse_result (existence of a sibling document), not of `bridge_kind`. The two filters compose cleanly: scoping-with-successor is applied inside `compute_actionable_pending`; dispatchable filtering is applied per-consumer (cross-harness trigger and, after this fix, the AXIS 2 surface).

## Files Changed (Planned)

- `.claude/hooks/bridge-axis-2-surface.py` — one-line filter plus explanatory comment in `_compute_actionable_for_role`, between role selection (line 164) and signature normalization (line 168-177).
- `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py` — new test file; four tests; importlib-based hook loader pattern mirroring `test_bridge_axis_2_role_aware.py`.

## Bridge Self-Check Preflights

Codex MUST rerun both `scripts/bridge_applicability_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` against this operative file and include the regenerated sections in any verdict.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
