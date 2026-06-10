REVISED

# Revised Implementation Proposal - AXIS 2 Surface: Filter Terminal-Kind GO Entries by Dispatchable Flag (WI-4278)

bridge_kind: prime_proposal
Document: gtkb-axis-2-dispatchable-filter
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-03 UTC
Session: S386
Recommended commit type: fix
Responds to: bridge/gtkb-axis-2-dispatchable-filter-002.md (NO-GO; FINDING-P1-001)

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

This REVISED proposal responds to the NO-GO at `-002` (FINDING-P1-001). The single revision narrows the filter expression from direct attribute access (`item.dispatchable`) to the compatibility-safe `getattr(item, "dispatchable", True)` idiom already used in `scripts/cross_harness_bridge_trigger.py`. Nothing else in the proposal changes: same target_paths, same WI, same PAUTH, same fast-lane routing, same Specification Links, same Prior Deliberations, same four-test verification plan, same risks. The defect, the scope, the rollback, and the empirical acceptance criterion are unchanged.

The proposal declares one work item: WI-4278. The historical bridge thread for WI-3442 (`gtkb-axis-2-scoping-terminal-classifier-fix-002`) is cited only as precedent for the same class of AXIS 2 classifier bug; this proposal does NOT co-declare or re-open WI-3442.

## Revision Claim

Codex NO-GO at `-002` cited a single P1 finding: the proposed filter line at IP-1 used direct attribute access (`item.dispatchable`), but existing AXIS 2 hook tests (`test_bridge_axis_2_role_aware.py`, `test_bridge_axis_2_surface_work_intent.py`) construct lightweight `SimpleNamespace` stubs with only `document_name`, `top_status`, and `top_file` - no `dispatchable` field. Direct attribute access on those stubs would raise `AttributeError` and break the no-regression guarantee in this proposal's own acceptance criteria. Codex noted that `scripts/cross_harness_bridge_trigger.py` already uses the compatibility-safe idiom `getattr(item, "dispatchable", True)`, so the AXIS 2 hook should mirror it for consistency and for stub-tolerance.

This revision adopts that recommendation verbatim. The semantic is identical for real `ActionablePending` instances (the `dispatchable` field is always present and defaults to True in the dataclass), but stub-based tests that omit the field continue to pass.

## Defect Evidence (unchanged from -001)

Live state at original filing (2026-06-03 19:40Z surface):

- `bridge/INDEX.md`: `gtkb-control-plane-placeholder-test-remediation-slice-1-revert` top status is `GO@-006`. Operative Prime version `-005` declares `bridge_kind: governance_review`, `target_paths: []`, `requires_verification: false`, `implementation_scope: none`. Per `groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS` (line 89-106 of `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`), `governance_review` is a terminal-kind token; per `_derive_dispatchable` (line 218-238), a GO + terminal classification yields `dispatchable=False`.
- `bridge/INDEX.md`: `gtkb-startup-refractor-scoping` top status is `GO@-002`. Operative Prime version `-001` declares `bridge_kind: governance_review`. Same terminal classification.
- Today's AXIS 2 surface (system-reminders at 19:40Z AND 20:13Z) flagged both as Prime-actionable alongside one true `implementation_proposal` entry (`gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`). The terminal-kind entries are the noise; the implementation entry should remain.
- `.claude/hooks/bridge-axis-2-surface.py:154-156`: `_compute_actionable_for_role` calls `compute_actionable_pending(parse_result, project_root=PROJECT_ROOT)`, which returns `(actionable_prime, actionable_codex)` lists with `dispatchable` already attached.
- `.claude/hooks/bridge-axis-2-surface.py:164`: `items = actionable_prime if role_profile == ROLE_PRIME else actionable_codex`. No `dispatchable` consumption follows.
- `.claude/hooks/bridge-axis-2-surface.py:168-177`: the normalized signature drops the `dispatchable` field entirely (`document_name`, `top_status`, `top_file` only), so the signature changes whenever a terminal-kind entry appears or disappears.
- Direct precedent (same compute path, same class of bug): the historical thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` (GO) added `_scoping_terminal_with_successor` to `compute_actionable_pending` to exclude scoping threads whose successor exists.
- Compatibility-safe precedent (this revision mirrors it): `scripts/cross_harness_bridge_trigger.py` uses `getattr(item, "dispatchable", True)` when filtering for headless dispatch.

Reproduction (post-fix verification target):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
```

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`: `.claude/hooks/bridge-axis-2-surface.py` and `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`. This bridge file is at `E:\GT-KB\bridge\gtkb-axis-2-dispatchable-filter-003.md`. No application file and no out-of-root path is touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root boundary satisfied.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; this proposal follows the NEW/REVISED/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing specification concretely in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the fixed behavior to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths and this bridge file are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the singular declared work item WI-4278 is the tracked backlog item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix is delivered as a durable hook change plus a regression test, not an undocumented patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the AXIS 2 surface hook triggers matching test artifacts; this proposal adds one.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the work is governed through the bridge artifact chain and the linked work item.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) - established the reliability fast-lane under which this fix is routed; for an eligible defect fix no per-fix deliberation or formal-artifact-approval packet is required.
- Bridge thread `gtkb-axis-2-dispatchable-filter-002` (NO-GO at -002; same thread, prior version) - cited the compatibility-safe `getattr(item, "dispatchable", True)` idiom from `scripts/cross_harness_bridge_trigger.py` as the precedent this proposal must mirror. Adopted verbatim.
- Bridge thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` (GO) - historical precedent: the same `compute_actionable_pending` function received a different terminal-condition filter (scoping-thread-with-successor). The pattern of "AXIS 2 classifier missed a terminal condition; cross-harness trigger correctly suppressed it; in-session surface still flagged it" is documented there. Cited as precedent only; no co-declaration of that historical thread's work item.
- Bridge thread `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 (GO at -010) - established the `dispatchable` + `classification` fields on `ActionablePending` and the `_derive_dispatchable` rule used here. The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) already filters on `dispatchable` (via `getattr` for stub-tolerance); this proposal extends the same filter pattern to the AXIS 2 in-session surface with the same idiom.
- Bridge thread `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006` (Codex GO) - original AXIS 2 surface authorization. The hook was scoped to "byte-identical to `_signature`" but the signature in the cross-harness trigger is computed AFTER `dispatchable` filtering, not over the raw `actionable_prime` list. This proposal closes that gap.
- Memory parking - `feedback_claude_hooks_template_lock` records that `.claude/hooks/*.py` files often have template companions under `groundtruth-kb/templates/hooks/`. Confirmed at original filing: no template companion exists for `bridge-axis-2-surface.py` (`find groundtruth-kb/templates/hooks -name "bridge-axis-2*"` returns empty), so a template-paired edit is not required.

## Owner Decisions / Input

- 2026-06-03 owner input (this turn's predecessor turn): the owner described the AXIS 2 surface re-flagging defect, identified `.claude/hooks/bridge-axis-2-surface.py` as the operative file, and proposed the test path `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`. The owner framed it as a follow-up from the /loop iter-5 session today and explicitly noted "not blocking; just removing AXIS 2 noise."
- 2026-06-03 owner input (interactive /loop steward mode): the owner left this Prime session in autonomous /loop mode to advance established work. Codex's NO-GO at -002 was mechanical and non-owner-interactive ("Owner Action Required: None"). This REVISED proceeds under continuing-established-work scope - the revision narrows ONE line of the IP-1 prescription and the acceptance criterion to the Codex-recommended compatibility-safe idiom; no scope expansion, no new authority claim.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-4278 by active project membership and authorizes `source`, `test_addition`, and `hook_upgrade` mutation classes. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required.
- No CLI surface change: this proposal adds no subcommand and no new flag.
- No blocking owner decision is pending. This REVISED needs only a Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-4278 ("AXIS 2 surface: filter terminal-kind GO entries by dispatchable flag") is the operative requirement. The dispatchable contract is already specified by `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 GO at -010. No new or revised specification is required.

## Reliability Fast-Lane Eligibility

Per `GOV-RELIABILITY-FAST-LANE-001` (unchanged from -001):

- Origin is `defect` - the AXIS 2 surface is producing noise that does not reflect actionable Prime work.
- No new public API/CLI/behavior beyond removing the defect - the `dispatchable` flag and the terminal classification are already published by `compute_actionable_pending`.
- No new or revised requirement or specification.
- Small and single-concern: 2 files (1 hook source, 1 new test file). Source change is ~3 net lines. Test file is ~80 lines.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-4278) is targeted. No backlog bulk mutation, no multi-item promotion or retirement, no multi-item inventory sweep. The reliability fast-lane waives the per-fix formal-artifact-approval packet; this proposal creates no GOV/ADR/DCL/SPEC artifact and no Deliberation Archive record.

## Bridge INDEX Update Evidence

REVISED filed at `E:\GT-KB\bridge\gtkb-axis-2-dispatchable-filter-003.md`; a `REVISED` line will be prepended to the existing thread entry at `bridge/INDEX.md`. `bridge/INDEX.md` remains the canonical bridge workflow state.

## Proposed Scope

### IP-1 (REVISED): Filter selected items on `getattr(item, "dispatchable", True)` in `_compute_actionable_for_role`

In `.claude/hooks/bridge-axis-2-surface.py`, between the role-selection step and the signature normalization step (currently line 164-178), add a one-line filter that drops entries whose `dispatchable` flag is False, using the compatibility-safe `getattr(..., True)` idiom that the cross-harness trigger already uses for the same purpose:

```python
items = actionable_prime if role_profile == ROLE_PRIME else actionable_codex
# Per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4: compute_actionable_pending
# attaches a centrally-computed `dispatchable` flag that reflects bridge_kind
# classification. Terminal-kind GO entries (governance_review, scoping, closure,
# parking, index/thread reconciliation, operational_state_change,
# candidate_spec_intake, loyal_opposition_advisory) have dispatchable=False and
# must be excluded from the in-session surface, mirroring the cross-harness
# event-driven trigger's dispatch suppression (which uses the same
# getattr(item, "dispatchable", True) compatibility-safe idiom). NEW/REVISED/NO-GO
# entries are always dispatchable=True, so this filter is a no-op for the Loyal
# Opposition role and for Prime NO-GO entries. The `getattr(..., True)` default
# preserves stub-tolerance for existing test doubles that omit the field.
items = [item for item in items if getattr(item, "dispatchable", True)]
```

Semantic delta vs -001: identical for production `ActionablePending` instances (which always carry `dispatchable`); strictly more tolerant for lightweight test stubs (no `AttributeError`); behaviorally aligned with `scripts/cross_harness_bridge_trigger.py`'s existing filter idiom.

Effect: the surface signature is computed only over dispatchable entries. A `governance_review` GO at any version no longer contributes to the signature, no longer triggers re-surfacing, and no longer prints in the markdown table. NEW/REVISED entries (Loyal Opposition role) are unaffected because they always have `dispatchable=True`. Prime NO-GO entries are unaffected for the same reason. Stub items in `test_bridge_axis_2_role_aware.py` and `test_bridge_axis_2_surface_work_intent.py` continue to pass because the `getattr(..., True)` default treats stubs as dispatchable. The hook continues to honor the `GTKB_NO_AXIS_2_SURFACE=1` env-var emergency stop and the `dismiss bridge surface` owner-keyword suppression.

Bytes touched: ~3 net lines (one filter line plus the explanatory comment, slightly expanded to document the stub-tolerance default).

### IP-2 (unchanged from -001): Regression test in `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`

Add a new test file with four tests:

1. `test_governance_review_go_excluded_from_axis_2_surface` - primary regression. Writes a fixture INDEX with one `GO` entry whose operative Prime version declares `bridge_kind: governance_review`; asserts items list is empty after filtering.
2. `test_implementation_proposal_go_remains_actionable` - non-regression for dispatchable GO entries.
3. `test_no_go_entry_remains_actionable_regardless_of_kind` - non-regression for NO-GO entries (always dispatchable=True).
4. `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` - non-regression for NEW/REVISED entries (always dispatchable=True).

Tests use the importlib-based hook loader pattern from `platform_tests/hooks/test_bridge_axis_2_role_aware.py`.

## Specification-Derived Verification Plan

Spec-to-test mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Requirement (WI-4278 / specs) | Behavior verified | Test |
|---|---|---|
| Terminal-kind GO entries must not appear on the AXIS 2 surface (WI-4278; smart-poller-kind-aware-routing -009 REVISED-4) | `_compute_actionable_for_role(ROLE_PRIME)` returns empty items + empty-list signature for a fixture with one `governance_review` GO | `test_governance_review_go_excluded_from_axis_2_surface` |
| Dispatchable GO entries remain on the surface (no over-suppression) | `_compute_actionable_for_role(ROLE_PRIME)` returns one item for a fixture with one `implementation_proposal` GO | `test_implementation_proposal_go_remains_actionable` |
| NO-GO entries remain actionable regardless of classification (`_derive_dispatchable` invariant) | `_compute_actionable_for_role(ROLE_PRIME)` returns the entry for a fixture with one `governance_review` NO-GO | `test_no_go_entry_remains_actionable_regardless_of_kind` |
| NEW/REVISED entries remain actionable for Loyal Opposition regardless of classification | `_compute_actionable_for_role(ROLE_LO)` returns the entry for a fixture with one `governance_review` NEW | `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` |
| Existing role-aware selection and signature semantics preserved (NO MODIFICATION to existing tests; stub-tolerance preserved by `getattr` default) | Existing tests `test_bridge_axis_2_role_aware.py` continue to pass unchanged | existing suite (regression) |
| Existing work-intent claim split semantics preserved (NO MODIFICATION to existing tests; stub-tolerance preserved by `getattr` default) | Existing tests `test_bridge_axis_2_surface_work_intent.py` continue to pass unchanged | existing suite (regression) |

Verification commands (run from `E:\GT-KB`):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py -q --tb=short` (regression; MUST PASS without modification of either file)
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`

## Acceptance Criteria (REVISED)

- IP-1 landed; the filter line and comment present at the documented location; the semantic line is exactly `items = [item for item in items if getattr(item, "dispatchable", True)]` (compatibility-safe idiom matching `scripts/cross_harness_bridge_trigger.py`).
- IP-2 landed; all four new tests PASS.
- The existing AXIS 2 hook tests (`test_bridge_axis_2_role_aware.py`, `test_bridge_axis_2_surface_work_intent.py`) PASS WITHOUT MODIFICATION. If either file requires modification to pass, the implementation is incorrect (the `getattr(..., True)` default exists precisely to keep their lightweight stubs working).
- `ruff check` and `ruff format --check` are clean on both target files.
- Mandatory applicability and clause preflights PASS for this bridge id.
- Empirical confirmation in the post-implementation report: the next SessionStart wake after the fix lands shows the AXIS 2 surface excluding `gtkb-control-plane-placeholder-test-remediation-slice-1-revert` and `gtkb-startup-refractor-scoping` while continuing to include any `implementation_proposal`-kind entries that remain actionable.

## Risks / Rollback

- Risk: over-suppression. Mitigated by IP-2 tests 2-4. The `getattr(..., True)` default also means stubs that omit `dispatchable` are treated as dispatchable (preserved on the surface), which is the safer fallback for any future test double or compatibility shim.
- Risk: signature collision. If a thread changes between dispatchable and non-dispatchable, the surface signature changes at the next signature-recompute, not retroactively. Acceptable; mirrors cross-harness trigger semantics.
- Risk: ambiguous-classification entries. `_derive_dispatchable` returns True for `classification != "terminal"`, which includes `"ambiguous"`. So bridge files with no `bridge_kind:` header continue to surface. No regression.
- Risk: dispatchable-flag drift from cross-harness trigger. Both consumers (cross-harness trigger and AXIS 2 surface) now use byte-identical `getattr(item, "dispatchable", True)` filtering against the same `compute_actionable_pending` output. They move together.
- Rollback: revert the single filter line and its comment in `_compute_actionable_for_role`, and delete the new test file. Fully reversible.

## Observations (Not in Scope, Unchanged from -001)

- The user's task description suggested a finer-grained filter (`bridge_kind == "governance_review" AND requires_verification == false`). This proposal uses the broader `dispatchable=False` filter because `governance_review` is already classified terminal by `notify.py:103` regardless of `requires_verification`, and the upstream cross-harness trigger also filters on the broader rule. If a future need emerges to surface `governance_review` proposals with `requires_verification=true`, the right place to refine that distinction is `_KIND_TERMINAL_TOKENS` / `_derive_dispatchable` in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, not in the AXIS 2 hook.
- The scoping-with-successor filter (added by the historical thread `gtkb-axis-2-scoping-terminal-classifier-fix-002`) is structurally separate from the `dispatchable` flag. The two filters compose cleanly: scoping-with-successor is applied inside `compute_actionable_pending`; dispatchable filtering is applied per-consumer.

## Files Changed (Planned)

- `.claude/hooks/bridge-axis-2-surface.py` - one-line filter plus explanatory comment in `_compute_actionable_for_role`, between role selection (line 164) and signature normalization (line 168-177). Semantic line: `items = [item for item in items if getattr(item, "dispatchable", True)]`.
- `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py` - new test file; four tests; importlib-based hook loader pattern mirroring `test_bridge_axis_2_role_aware.py`.

NO modification of `platform_tests/hooks/test_bridge_axis_2_role_aware.py` or `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py`. These existing tests must pass unchanged under the `getattr` default.

## Bridge Self-Check Preflights

Codex MUST rerun both `scripts/bridge_applicability_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter` against this operative file (now `-003`) and include the regenerated sections in any verdict.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
