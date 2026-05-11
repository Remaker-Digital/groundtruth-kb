NEW

# Implementation Proposal - Isolation Aftermath Startup Baseline (Scoping)

**Document:** `gtkb-isolation-aftermath-startup-baseline-001`
**Status:** `NEW`
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal (Slice 0; scoping-only)
**Recommended commit type:** `docs:` (scoping proposal; no source mutation under this thread)

## Claim

Five tests in `platform_tests/scripts/test_session_self_initialization.py` fail at the current `develop` HEAD (`3bf1c927`) with a single shared root cause: an `assert "GTKB-GOV-007" not in <output>` (or equivalent membership assertion) that contradicts the live standing-backlog rendering, which DOES surface `GTKB-GOV-007` as a top-priority item.

This Slice 0 scoping proposal asks Codex for `GO` to file ONE follow-on implementation bridge that fixes the root cause and unblocks the verification surface for any other thread that runs the full `test_session_self_initialization.py` suite as its acceptance command.

The immediate consumer of this scoping bridge is `gtkb-role-session-lifecycle-simplification` (NO-GO at `-008`), where Codex's recommended action path #3 (`bridge/gtkb-role-session-lifecycle-simplification-008.md:180-182`) is to "file that thread and make this report wait for either the follow-on fix or an explicit waiver cited in this thread's verification evidence." This proposal IS that thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking) - bridge/INDEX.md is the canonical bridge workflow state; this proposal is filed as `-001` NEW with a corresponding INDEX line.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking) - every proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking) - VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this scoping thread's eventual report will map test-fix verification to the listed test sites.
- `GOV-STANDING-BACKLOG-001` (blocking) - standing backlog as governed work authority; the failing tests assert what is and is NOT a current top-priority backlog item, so the standing-backlog rendering contract is in-scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) - in-root placement; all test and source touchpoints live within `E:\GT-KB` per `.claude/rules/project-root-boundary.md`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - this scoping proposal status is `candidate` -> `specified` upon Codex GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `.claude/rules/file-bridge-protocol.md` - bridge protocol gates apply.
- `.claude/rules/codex-review-gate.md` - review obligations apply.
- `.claude/rules/deliberation-protocol.md` - deliberation-search obligation satisfied by `## Prior Deliberations` below.
- `.claude/rules/project-root-boundary.md` - root boundary; all touchpoints in-root.
- `.claude/rules/canonical-terminology.md` - canonical terms used in this proposal resolve to the glossary.

## Prior Deliberations

Deliberation search command (run 2026-05-11 in S341):

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "isolation aftermath startup baseline test failures GTKB-GOV-007 standing backlog rendering" --limit 8
```

Returned candidates (8 results; semantic scores 0.773-0.848):

- `DELIB-1049` v1 - "GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 1" (NO-GO). Relevance: prior isolation-aftermath context only; not load-bearing for this scoping decision.
- `DELIB-1004` v1 - "GTKB-ISOLATION-015 - Loyal Opposition Review" (GO). Relevance: isolation precedent.
- `DELIB-1036` v1 - "GTKB Work Subject And Root Enforcement - Foundation Review Revision 5" (NO-GO). Relevance: root-boundary precedent only.
- `DELIB-1520` v1 - "Loyal Opposition Verification - Trigger-Awareness + Two-Axis Bridge Automation Model" (VERIFIED). Relevance: governance-precedent only.
- `DELIB-1047` v1 - "GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 2" (GO). Same as 1049 v1.
- `DELIB-0988` v1 - "GTKB-ISOLATION-015 Slice 2 Reconciliation Review" (NO-GO). Same.
- `DELIB-1029` v1 - "GTKB Scoped Service Boundary Baseline Review Revision 2" (NO-GO). Same.
- `DELIB-1008` v1 - "GTKB-ISOLATION-015 - Loyal Opposition Review" (NO-GO). Same.

_No prior deliberations directly address the GTKB-GOV-007 not-reappear assertion drift discovered in this scoping. The returned results are isolation-context precedent only and do not contradict the proposed scoping-only direction._

Additionally cited as immediate cross-thread context:

- `bridge/gtkb-role-session-lifecycle-simplification-008.md` - NO-GO verdict that requires THIS scoping bridge be filed to satisfy Codex's path #3 recommendation.
- `bridge/gtkb-role-session-lifecycle-simplification-007.md:79` - Prime Builder's prior tag of "Scope disposition on 5 pre-existing baseline failures" as outstanding work.

## Owner Decisions / Input

This Slice 0 scoping proposal depends on owner input collected via:

- **Owner pickup directive 2026-05-11 (S341)** - owner explicitly listed "File gtkb-isolation-aftermath-startup-baseline-001 scoping bridge for the 5 pre-existing test failures" as item 4 of the session pickup queue. This authorizes filing this scoping bridge.

The scoping proposal does NOT require a waiver decision at this point. A waiver decision will be required at the moment `gtkb-role-session-lifecycle-simplification` REVISED-3 cites this thread as path #3 evidence, but that AUQ is handled in that thread's revision rather than here.

No owner-AUQ-required decisions are pending for this scoping bridge's review by Codex.

## Live State Probed

Test command (run 2026-05-11 in S341 against `develop` HEAD `3bf1c927`):

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=line --timeout=120
```

Observed result: `5 failed, 52 passed, 1 warning in 326.82s`.

Failing tests with line references:

| Test | Source line | Assertion |
|---|---|---|
| `test_dashboard_and_report_are_written_with_time_series_kpi` | `platform_tests/scripts/test_session_self_initialization.py:1007` | `assert "GTKB-GOV-007" not in report_text` |
| `test_emit_report_uses_session_start_hook_context_json` | `platform_tests/scripts/test_session_self_initialization.py:1170` | `assert "GTKB-GOV-007" not in report_text` |
| `test_claude_code_startup_discovers_durable_role_without_forced_profile` | `platform_tests/scripts/test_session_self_initialization.py:1397` | `assert any(...)` — generator over hook command list (downstream of the same data-rendering drift) |
| `test_fast_hook_skips_expensive_history_and_pdf_paths` | `platform_tests/scripts/test_session_self_initialization.py:1625` | `assert "GTKB-GOV-007" not in report_text` |
| `test_top_priority_actions_come_from_standing_backlog` | `platform_tests/scripts/test_session_self_initialization.py:1659` | `assert "GTKB-GOV-007" not in action_ids` (list of strings) |

Production rendering evidence (this session's own startup payload):

```text
2. **Top Priority Actions**
   Current signal: ... 49 latest GO/NO-GO bridge responses.
   Prompt details: Focus this session on the established top priority actions.
   Current priorities: GTKB-GOV-007: Revise commercial readiness NO-GO tracks
   for SPEC-1831, SPEC-1832, and SPEC-1833; GTKB-GOV-010: ...
```

`GTKB-GOV-007` is currently a load-bearing item in the standing-backlog top-priority surface. It is rendered, by design, into the startup focus menu's "Top Priority Actions" prompt.

Existing test-file context (`platform_tests/scripts/test_session_self_initialization.py:1649-1661`):

```python
# Per S330 Slice 8.6 row-36 fix: assert top-priority discipline rather than
# exact list equality. Production code returns visible_items[:3] from the
# standing backlog (scripts/session_self_initialization.py:934). The test
# should not pin whichever item is currently first in that governed list;
# it should pin the invariants: actions come from active standing-backlog
# ordering, historically-closed items don't reappear, and the cap is 3.
assert action_ids == expected_action_ids
assert len(action_ids) <= 3, f"top_priority_actions must cap at 3 (visible_items[:3]); got {action_ids}"
assert "GTKB-ISOLATION-007" not in action_ids
assert "GTKB-GOV-012" not in action_ids
assert "GTKB-GOV-007" not in action_ids
assert "GTKB-GOV-002" not in action_ids
assert "GTKB-GOV-006" not in action_ids
```

The comment block explicitly states the intent: "should not pin whichever item is currently first." The assertion list at lines 1657-1661 includes `GTKB-GOV-007` alongside historically-closed items (`GTKB-ISOLATION-007`, `GTKB-GOV-012`, `GTKB-GOV-002`, `GTKB-GOV-006`). Including `GTKB-GOV-007` in this list contradicts the comment's stated intent: GTKB-GOV-007 is NOT historically closed; it is the CURRENT top governance priority.

## Proposed Slice 0 Output (this thread only)

This scoping bridge authorizes filing ONE follow-on implementation bridge:

- `gtkb-isolation-aftermath-startup-baseline-fix-001` (planned name) - implementation proposal that removes `GTKB-GOV-007` from the not-reappear assertion lists at the 5 cited test sites and adds a regression-guard comment explaining why active-priority items must NOT be added to this list. The follow-on proposal will run the full `test_session_self_initialization.py` suite to green as its acceptance criterion.

This thread (`gtkb-isolation-aftermath-startup-baseline`) is scoping-only. It does NOT itself authorize:

- test edits;
- production source changes to `scripts/session_self_initialization.py` or the standing-backlog renderer;
- standing-backlog `memory/work_list.md` or MemBase row mutations;
- waivers for the `gtkb-role-session-lifecycle-simplification` verification surface (that waiver is filed in THAT thread's REVISED-3, not here).

## Spec-To-Test Mapping (Slice 0 verdict)

Slice 0 is a scoping proposal whose acceptance is Codex GO on this file. There is no implementation work to verify under this Slice. The eventual REPORT for this thread will be filed AFTER the follow-on implementation thread lands its post-impl report; this thread's VERIFIED is contingent on:

1. The follow-on proposal `gtkb-isolation-aftermath-startup-baseline-fix-001` is filed as NEW with its own preflights, specification links, and prior-deliberation handling.
2. The follow-on thread receives its own GO and lands its own implementation.
3. The full `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short` command returns `57 passed` (or equivalently `0 failed`).

| Specification | Test or verification step (Slice 0) |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` carries this thread's NEW entry; followups will land as additional INDEX entries. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's `Specification Links` section is non-empty and machine-checkable. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This thread's VERIFIED is reserved for a future report that maps the failed tests to a passing run. |
| `GOV-STANDING-BACKLOG-001` | Standing-backlog rendering contract is preserved; this scoping thread does NOT propose changes to the renderer. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All file touchpoints in this thread and its planned follow-on are within `E:\GT-KB`. |

## Risks / Rollback

- **Low**: scoping-only proposal; no source mutation. Rollback = `git rm bridge/gtkb-isolation-aftermath-startup-baseline-001.md` and remove the INDEX entry.
- **Cross-thread interaction**: `gtkb-role-session-lifecycle-simplification` REVISED-3 will depend on this thread receiving GO before it can cite this thread as path #3 evidence. Mitigation: this scoping proposal is intentionally tight to minimize Codex's review time.
- **Out-of-scope drift**: If the follow-on investigation reveals other test sites with the same antipattern (active-priority IDs added to not-reappear lists), the follow-on proposal will expand its scope to cover them. The expansion will be done as a REVISED in the follow-on thread, not as a scope amendment to this thread.

## Decision Deferred Markers (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence)

This scoping bridge cites `GOV-STANDING-BACKLOG-001` because the failing tests assert standing-backlog rendering invariants. This thread itself does NOT perform any bulk operation on standing-backlog items. To satisfy the bulk-operations visibility clause for this thread's scoping role:

- DECISION DEFERRED: the choice between "update the 5 test assertions" and "update the standing-backlog rendering" is explicitly deferred to the follow-on implementation thread `gtkb-isolation-aftermath-startup-baseline-fix-001`. This scoping thread does not make that determination.
- DECISION DEFERRED: any bulk inventory of "active-priority IDs erroneously listed in not-reappear assertion lists" is deferred to the follow-on thread's pre-implementation investigation.
- DECISION DEFERRED: any standing-backlog `work_list.md` or MemBase row mutation is out of scope for this thread; if the follow-on investigation surfaces standing-backlog data drift, that becomes a separate work item under its own bridge thread, not under this one.
- DECISION DEFERRED: any waiver for the `gtkb-role-session-lifecycle-simplification` verification surface is filed in that thread's REVISED-3, not here. This scoping bridge provides the path #3 reference, not the waiver itself.

No bulk operation on standing-backlog content is performed by this scoping bridge. The follow-on implementation thread will produce its own inventory artifact + review packet at filing time as part of its own clause-preflight evidence.

## Acceptance Criteria (for Codex GO on this scoping proposal)

1. Codex applicability preflight passes on the operative file for `gtkb-isolation-aftermath-startup-baseline-001`.
2. Codex ADR/DCL clause preflight passes on the operative file for `gtkb-isolation-aftermath-startup-baseline-001`.
3. Specification linkage is non-empty and machine-checkable.
4. Prior-deliberation handling cites the deliberation search command + results.
5. Scope is internally consistent: scoping-only proposal authorizing ONE follow-on filing; no implementation work in this thread.

## Commands Already Executed (proposal preparation)

- `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=line --timeout=120` (captured 5 failures + 52 passes).
- Deliberation search for "isolation aftermath startup baseline test failures GTKB-GOV-007 standing backlog rendering" (8 candidate results).
- Targeted source reads over `platform_tests/scripts/test_session_self_initialization.py` lines 990-1024, 1380-1410, 1640-1665.
- Targeted source reads over `bridge/gtkb-role-session-lifecycle-simplification-007.md` (REVISED-2 baseline tag) and `-008.md` (NO-GO path #3 recommendation).

## Commands To Run At Filing Time (Self-Check)

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-aftermath-startup-baseline
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-aftermath-startup-baseline
```

Expected: `preflight_passed: true`, `missing_required_specs: []`, `Blocking gaps: 0`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
