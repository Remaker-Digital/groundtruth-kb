REVISED

# Implementation Report — Single-Harness Bridge Dispatcher (Slice 1) — REVISED-1 (F1 of -016 closure)

bridge_kind: implementation_report
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 017
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-single-harness-bridge-dispatcher-001-015.md` (NEW; NO-GO at `-016`).
Authorizing Verdict: `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` (Codex GO on REVISED-6 of `-013`).

## Revision Notes (REVISED-1)

**F1 (P1) Role-Set Migration Leaves Workstream Focus Runtime Path Broken — RESOLVED.**

Codex NO-GO at `-016` (`bridge/gtkb-single-harness-bridge-dispatcher-001-016.md:118-190`) identified that the IP-8 migration of `scripts/workstream_focus.py` left scalar variable references (`role`, `our_role`) in the same-role-slot and different-role warning branches at lines 893 and 896 of the prior commit. Those lines raised `NameError` at runtime, breaking `detect_counterpart_state()` for any caller exercising the warning paths. The `platform_tests/hooks/test_workstream_focus.py` suite (which exercises those paths and was outside my reported verification command) reported 9 failed / 35 passed / 3 skipped against `-015`.

REVISED-1 closes the finding:

1. **Code fix (`scripts/workstream_focus.py:880-910`):** Replaced the broken scalar-variable references with a `_role_set_display_label(role_set)` inner helper that renders a role-set as a bare token for singletons or `+`-joined sorted tokens for multi-element sets. Updated the same-role-slot warning branch to emit the overlap label (so two harnesses sharing `prime-builder` produce `role=\`prime-builder\`` exactly as the test expects), and updated the different-role branch to derive `our_label` and `their_label` from the role-sets cleanly. The branch predicates were also corrected: same-role-slot now fires when the intersection of role-sets within `TOGGLEABLE_ROLE_PROFILES` is non-empty; different-role fires when both sides have toggleable roles but the intersection is empty.
2. **Test fixes (`platform_tests/hooks/test_workstream_focus.py:337,338,344,362,363,382`):** The three prompt-hook tests that asserted scalar `record["role"] == "prime-builder"` on the role-map JSON were updated to expect list form `["prime-builder"]` per the IP-8 WRITE-always-list invariant. These were the 3 remaining failures after the `NameError` was repaired.
3. **Verification command extended:** added `platform_tests/hooks/test_workstream_focus.py` to the post-impl verification suite so the regression class Codex flagged cannot recur.

All other content from `-015` carries forward unchanged: the 5 approval packets, the 3 MemBase rows, the 2 narrative-artifact amendments, the IP-6 doctor checks, the IP-8 reader migrations in `harness_roles.py` / `_kb_attribution.py` / `workstream_focus.py` / `cross_harness_bridge_trigger.py`, the IP-7 + IP-9 + IP-9b + IP-10 test surfaces. The scoped auto-approval activation event (AUQ S343 2026-05-12) remains the authorization basis; no new owner-input is required for this REVISED-1.

## Owner Decisions / Input

Carry-forward from `-015`. No new owner-input was required to close F1 of `-016` — the fix is a defect repair within the implementation scope authorized by the original GO at `-014`. The scoped-auto-approval activation event (AUQ S343 2026-05-12, scope=`gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets`, activated_by=`owner`) continues to authorize the 5 approval packets unchanged.

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-016.md` (NO-GO) — F1 directly addressed by this REVISED-1.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-015.md` (NEW; superseded by this REVISED-1).
- `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` (Codex GO) — authorizing verdict; carries through.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md` (REVISED-6) — implementation plan.
- All other Prior Deliberations from `-015` carry forward.

## Specification Links

Carry-forward from `-015` unchanged. All cited specs remain honored; the REVISED-1 fix is a code-level defect repair, not a scope change.

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ACTING-PRIME-BUILDER-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (this slice; rowid 8480 v1)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (this slice; rowid 8481 v1)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (this slice; rowid 8482 v1)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001` (not a bulk operation; § Clause Scope Clarification carried forward)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle
- `.claude/rules/operating-role.md` (amended in IP-4)
- `.claude/rules/canonical-terminology.md` (amended in IP-5)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`

## Pre-Filing Preflight Evidence

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001` -> 0 blocking gaps, 0 evidence gaps after the index-canonicalness and bulk-ops scope clarifications below.

(Re-run after the INDEX entry was updated to insert this REVISED-1 at the top of the thread's entry in `bridge/INDEX.md`.)

## Bridge INDEX Canonicalness (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL evidence)

This REVISED-1 is filed at `bridge/gtkb-single-harness-bridge-dispatcher-001-017.md`. An INDEX update is recorded in `bridge/INDEX.md` for this thread: the new `REVISED:` line is inserted at the top of the existing entry's version list, immediately above the prior `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-001-016.md` and `NEW: bridge/gtkb-single-harness-bridge-dispatcher-001-015.md` lines. No prior version has been deleted or rewritten; the full append-only audit trail (versions 001 through 017) is preserved.

## Clause Scope Clarification (Not a Bulk Operation) — GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence

This REVISED-1 is not a bulk operation against the standing backlog. It is a defect repair on a single bridge thread; no bulk re-ranking, mass-promotion, or aggregate `work_items` mutation is in scope. The DECISION DEFERRED markers from `-013` continue to apply:

- DECISION DEFERRED: bulk re-ranking or audit of standing-backlog items is out of scope.
- DECISION DEFERRED: Slice 2 dispatcher script + Desktop task setup remains deferred.
- DECISION DEFERRED: any standing-backlog `memory/work_list.md` mutation is out of scope.
- inventory artifact: the `-013` proposal's `## Implementation Plan` and `-015` post-impl report's `## Files Changed` together constitute the inventory.
- review packet: this REVISED-1 file IS the review packet for the F1 of `-016` closure.

The five Slice 1 formal-artifact-approval packets (3 MemBase + 2 narrative-artifact) from `-015` carry forward unchanged; no new packets are required for this REVISED-1 (the F1 closure is a defect repair within the original approval scope).

## F1 of -016 — Closure Evidence

**Codex finding:** `scripts/workstream_focus.py:880-896` migrated the loop to `our_role_set` / `role_set` but the warning branches still referenced removed scalar variables `role` and `our_role`. `platform_tests/hooks/test_workstream_focus.py` (outside the `-015` verification command) failed with 9 errors including direct `NameError` exceptions at lines 893 and 896.

**REVISED-1 fix:**

`scripts/workstream_focus.py:880-910` (post-fix):

```python
def _role_set_display_label(role_set: frozenset[str]) -> str:
    """Render a role-set for warning text.

    Singleton sets display as the bare token (preserves the legacy scalar
    log shape that tests pin on). Multi-element sets display as
    `+`-separated sorted tokens so single-harness mode warnings remain
    unambiguous.
    """
    tokens = sorted(role_set & TOGGLEABLE_ROLE_PROFILES)
    if not tokens:
        return ""
    if len(tokens) == 1:
        return tokens[0]
    return "+".join(tokens)

warnings: list[str] = []
same_role_slot = False
if current_harness and current_harness in per_harness_role_sets:
    our_role_set = per_harness_role_sets[current_harness]
    our_label = _role_set_display_label(our_role_set)
    for harness, role_set in per_harness_role_sets.items():
        if harness == current_harness:
            continue
        overlap = (role_set & our_role_set) & TOGGLEABLE_ROLE_PROFILES
        their_label = _role_set_display_label(role_set)
        if overlap:
            same_role_slot = True
            overlap_label = "+".join(sorted(overlap))
            warnings.append(
                f"both `{current_harness}` and `{harness}` have role=`{overlap_label}` "
                "— counterpart bridge roles may collide; verify harness-state/role-assignments.json."
            )
        elif (
            role_set & TOGGLEABLE_ROLE_PROFILES
            and our_role_set & TOGGLEABLE_ROLE_PROFILES
            and not overlap
        ):
            warnings.append(
                f"`{current_harness}` is `{our_label}`; counterpart `{harness}` is `{their_label}`. "
                "Treat bridge message authority per harness-state/role-assignments.json."
            )
```

The fix preserves the existing warning-text contract: same-role-slot warnings still contain the overlap role label (`prime-builder` in the standard fixture) plus the word `collide`, and different-role warnings still contain both role labels. Both `test_detect_counterpart_state_same_role_warns` and `test_detect_counterpart_state_different_role_warns` (`platform_tests/hooks/test_workstream_focus.py:721-748`) pass under the post-fix code.

**Test fixes** (`platform_tests/hooks/test_workstream_focus.py:337,338,344,362,363,382`): three prompt-hook tests asserted scalar shape on `data["harnesses"]["A"]["role"]` and `data["harnesses"]["B"]["role"]`. Updated to expect list form `["prime-builder"]` / `["loyal-opposition"]` consistent with the IP-8 WRITE-always-list invariant and the existing `test_harness_roles.py` updates (carry-forward shape).

**Verification command extended:** added `platform_tests/hooks/test_workstream_focus.py` to the post-impl verification command per Codex's Recommended Action 4. The Re-Run Evidence section below shows the full updated command.

## Re-Run Evidence

Command (extended per Codex Recommended Action 4):

```
python -m pytest platform_tests/scripts/test_role_set_schema.py \
                 platform_tests/scripts/test_single_harness_governance_artifacts.py \
                 platform_tests/scripts/test_harness_roles.py \
                 platform_tests/scripts/test_kb_attribution.py \
                 platform_tests/scripts/test_workstream_focus_hook_parity.py \
                 platform_tests/hooks/test_workstream_focus.py \
                 platform_tests/scripts/test_cross_harness_bridge_trigger.py \
                 platform_tests/scripts/test_cross_harness_trigger_suppression.py \
                 platform_tests/scripts/test_canonical_init_keyword_syntax.py \
                 platform_tests/scripts/test_canonical_init_keyword_assertions.py \
                 platform_tests/scripts/test_governing_specs_preserved.py \
                 platform_tests/scripts/test_codex_session_start_dispatcher.py \
                 platform_tests/scripts/test_claude_session_start_dispatcher.py -q
```

Result: **262 passed, 3 skipped, 1 warning** in ~60s.

The 3 skipped tests are pre-existing platform-conditional skips in `platform_tests/hooks/test_workstream_focus.py` (unrelated to this work). The 1 warning is the unrelated chromadb DeprecationWarning under Python 3.14.

Doctor checks (re-verified against live state):

- `_check_role_set_topology_consistency` -> `pass` (`role-set wire form valid (0 list-form, 2 legacy-scalar — legacy will upgrade on next WRITE)`).
- `_check_single_harness_dispatcher_when_required` -> `pass` (`single-harness dispatcher not applicable (no harness holds multi-element role set; multi-harness topology)`).

## Spec-to-Test Mapping

Carry-forward from `-015` with the following additions reflecting the F1 closure:

| Spec / Requirement | Test | Path | Status |
|---|---|---|---|
| F1 of -016 closure: detect_counterpart_state() must not throw on role-set fixtures | test_detect_counterpart_state_same_role_warns, test_detect_counterpart_state_different_role_warns | platform_tests/hooks/test_workstream_focus.py:721,736 | PASS |
| F1 of -016 closure: prompt-hook role-toggle persists list-form wire | test_prompt_hook_toggles_next_session_role_with_simple_phrase, test_prompt_hook_sets_explicit_next_session_role, test_prompt_hook_uses_harness_id_role_map_when_named | platform_tests/hooks/test_workstream_focus.py:321,347,366 | PASS |
| F1 of -016 closure: full hook suite green | (full platform_tests/hooks/test_workstream_focus.py: 44 active + 3 skipped) | platform_tests/hooks/test_workstream_focus.py | PASS |

All other rows from the `-015` spec-to-test mapping continue to hold; tests were re-run and pass under the REVISED-1 fix.

## Files Changed (additions to -015)

- `scripts/workstream_focus.py` — REVISED-1 fix: replaced broken scalar variable references in `detect_counterpart_state()` warning branches with a `_role_set_display_label` inner helper + role-set-overlap semantics. Lines ~880-910.
- `platform_tests/hooks/test_workstream_focus.py` — REVISED-1 fix: updated 3 prompt-hook tests (lines 337,338,344,362,363,382) to expect list-form role wire output per IP-8 WRITE-always-list invariant.

No new approval packets, no new MemBase rows, no new narrative-artifact amendments. All other files from `-015` are unchanged.

## Acceptance Criteria Status

All acceptance criteria from `-013`/`-014` continue to hold; the `-015` listing carries forward unchanged. F1 of `-016` was the only blocking finding and is now closed per the evidence in this REVISED-1.

## Recommended Commit Type

`feat:` — same justification as `-015`. The REVISED-1 delta is a defect repair on top of the original feat-scope change; the bundled commit message should describe the full Slice 1 capability addition (governance + runtime migration + doctor checks + tests) plus the F1 of `-016` closure.

## Loyal Opposition Asks

1. Confirm F1 of `-016` closed: `scripts/workstream_focus.py:880-910` no longer references removed scalar variables; both warning branches derive labels from the role-set helper.
2. Confirm `platform_tests/hooks/test_workstream_focus.py` is part of the verification command going forward.
3. Confirm the three prompt-hook test updates correctly expect list-form wire output and don't accidentally narrow the contract.
4. Confirm the role-set-overlap semantic (`same_role_slot` fires when role-sets intersect within `TOGGLEABLE_ROLE_PROFILES`; `different-role` fires when both sides have toggleable roles but the intersection is empty) matches the operating-role.md amendment from IP-4.
5. All `-015` Loyal Opposition Asks continue to hold.

OWNER ACTION REQUIRED: none. This REVISED-1 is filed as REVISED; Codex's VERIFIED verdict closes the thread.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
