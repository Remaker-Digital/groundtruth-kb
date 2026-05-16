NEW

Document: gtkb-owner-decision-tracker-startup-relay-known-match-suppression

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3332

# Post-Implementation Report: Suppress Already-Known Startup Relay Matches In Owner-Decision Tracker

Status: NEW
Version: 005
Responds to: bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-004.md (Codex Loyal Opposition GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15

## Summary

The WI-3332 fix is implemented and verified. The owner-decision-tracker Stop
hook no longer emits a turn-end block when the assistant relays an
already-recorded owner decision, and the startup disclosure now renders pending
decision questions in a Stop-safe structural form. The change was implemented
within the four GO'd target paths plus one owner-approved test-infrastructure
correction (see Owner Decisions / Input).

Implementation authorized by the Codex GO at -004; implementation-start packet
`sha256:2be4156bedd6a962de0e441027dd958e37d8b7d6009c798e8ec7d6d7b786fb13`,
derived from the live latest GO.

## Changes Implemented

### Part A - owner-decision-tracker.py (Stop hook)

`_stop_handler` now builds a known-decision identity snapshot before scanning:
an exact `question_hash` set plus an exact normalized-question-text set, built
once from all sections (Pending / Resolved / History) of
`memory/pending-owner-decisions.md` and never mutated during the scan. Prose
matches are split into `prose_matches_this_turn` (the raw scan result, which
still drives the durable-append and same-turn-AUQ-correlation path unchanged)
and `fresh_prose_matches_this_turn` (the block-eligible subset, which excludes
any match whose identity is already in the snapshot). The Stop-block emission
now fires from `fresh_prose_matches_this_turn`. A relay of an already-recorded
decision is therefore still detected and idempotence-checked exactly as before,
but no longer refuses turn-end. Identity is exact hash OR exact normalized-text
only; no fuzzy matching was introduced, per the -004 GO scope constraint.

### Part B - session_self_initialization.py (startup renderer)

`_render_pending_decisions_block` now renders the decision id and suffix
metadata on the bullet line and the question on its own column-0 blockquote
line (`> {question}`). The owner-decision-tracker structural-context check
treats a line beginning with `> ` as relay/documentation, so a verbatim relay
of a generated startup disclosure no longer registers the question as a fresh
owner-decision-ask. The decision id, question, and options remain fully visible
to the owner.

### Test-infrastructure correction (owner-approved)

`platform_tests/hooks/test_owner_decision_tracker.py` carried a stale `FIXTURES`
constant resolving to `tests/hooks/fixtures/` after the suite relocated to
`platform_tests/`. Every fixture-backed subprocess test was failing pre-change
(21 of 44). The constant is corrected to resolve relative to the test file's
own location. This correction was approved by the owner via AskUserQuestion
(see Owner Decisions / Input); it is required for the proposal's T5 acceptance
criterion to be testable.

### Tests added

- T1, T2, T3 in `platform_tests/hooks/test_owner_decision_tracker.py`.
- T4 in `platform_tests/scripts/test_session_self_initialization.py`.

## Files Changed

- `.claude/hooks/owner-decision-tracker.py` - Part A.
- `scripts/session_self_initialization.py` - Part B.
- `platform_tests/hooks/test_owner_decision_tracker.py` - FIXTURES correction + T1/T2/T3.
- `platform_tests/scripts/test_session_self_initialization.py` - T4.
- `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-003.md` - one-word Specification Links edit (see Owner Decisions / Input).

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - standing fast-lane governs small defect and
  reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-STANDING-BACKLOG-001` - `WI-3332` is the governed single work item for
  this fix; this report is not a bulk backlog operation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed in the file bridge;
  `bridge/INDEX.md` is the canonical workflow state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-decision records and advisory
  reports are durable operational artifacts, not transient chat content.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect was handled as
  artifact-governed work through a WI, advisory report, and bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect crossed the threshold from
  chat observation to durable work item and implementation.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup disclosure surfaces
  unresolved owner decisions without creating a new blocked interaction.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - init-keyword relay must
  relay cached startup disclosure faithfully; this fix changes the source
  disclosure shape and Stop-hook classification, not the relay obligation.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - owner-decision enforcement remains
  deterministic; no LLM classifier was introduced.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries
  machine-readable Project Authorization, Project, and Work Item headers.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - report lists
  governing specifications and maps them to executed tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report carries forward the
  spec-to-test mapping and the observed test results.

## Prior Deliberations

- `DELIB-1888` - compressed bridge thread for owner-decision-tracker
  pattern-bounds and same-turn AUQ correlation; the behavior baseline this fix
  extends.
- `DELIB-1527` - Loyal Opposition NO-GO on owner-decision tracker pattern
  bounds; conservative false-positive handling.
- `DELIB-1523` - VERIFIED review for the revised pattern-bounds implementation;
  current baseline.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing the
  standing reliability fast-lane that authorizes this work item.
- No prior deliberation rejected the known-relay suppression approach; the
  Codex `-002` and `-004` reviews independently confirmed the deliberation set.

## Spec-Derived Test Plan and Mapping

| Test | Spec / Contract | Result |
|---|---|---|
| T1 `test_wi3332_t1_known_pending_relay_does_not_block` | `GOV-SESSION-SELF-INITIALIZATION-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | PASS |
| T2 `test_wi3332_t2_fresh_prose_ask_still_blocks` | `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | PASS |
| T3 `test_wi3332_t3_known_resolved_relay_does_not_block` | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | PASS |
| T4 `test_wi3332_t4_pending_decisions_block_renders_question_stop_safe` | `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | PASS |
| T5 existing owner-decision-tracker + renderer suites | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | PASS (44/44 hook suite; 11/11 renderer/pending subset) |

## Verification Commands

```powershell
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "render or pending or wi3332"
python -m ruff check .claude/hooks/owner-decision-tracker.py scripts/session_self_initialization.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check .claude/hooks/owner-decision-tracker.py scripts/session_self_initialization.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/scripts/test_session_self_initialization.py
```

Observed results:

- `test_owner_decision_tracker.py`: `44 passed in 6.83s`. Pre-change baseline
  was `21 failed, 20 passed`; all 21 failures were the stale-`FIXTURES`-path
  subprocess tests, resolved by the owner-approved `FIXTURES` correction. 3 of
  the 44 are the new T1/T2/T3.
- `test_session_self_initialization.py` (WI-3332 subset): `11 passed, 53
  deselected in 0.59s`, including T4 and all renderer/pending tests.
- Full-file `test_session_self_initialization.py` run is blocked by a
  pre-existing 30s per-test timeout in
  `test_dashboard_and_report_are_written_with_time_series_kpi`
  (`write_dashboard_and_report` -> `_historical_agent_red_backfill` ->
  `classify_dashboard_scope`). That is dashboard-backfill code; WI-3332 does
  not touch it. The WI-3332-relevant subset above is the scoped verification.
- `ruff check`: 5 errors, all pre-existing and outside the WI-3332 diff -
  `SIM103` x1 in `owner-decision-tracker.py` `_is_inside_structural_context`
  (not modified by WI-3332) and `I001` x4 in `test_owner_decision_tracker.py`
  import blocks (not modified by WI-3332). WI-3332's added code introduced zero
  new `ruff check` errors.
- `ruff format --check`: `owner-decision-tracker.py` and the two test files
  carry pre-existing formatting drift (these files are not under ruff-format
  enforcement; `scripts/session_self_initialization.py` is, and Part B there is
  clean). WI-3332's added code is itself ruff-format-clean: `ruff format
  --diff` shows no reformat hunks within the WI-3332 added line ranges.

## Acceptance Criteria

1. Startup disclosure can surface a recorded decision without causing a Stop
   block - MET (T1, T4).
2. Existing durable decision relays from Pending, Resolved, and History are not
   classified as fresh owner asks - MET (snapshot built from all sections; T1
   covers Pending, T3 covers Resolved).
3. Fresh prose decision asks still block when no same-turn AskUserQuestion
   exists - MET (T2; existing F3 block-emission tests still pass).
4. Pending owner decisions remain visible and actionable through `resolve
   DECISION-NNNN: <answer>`, `defer all`, or `clear pending` - MET (no change
   to that path; the renderer keeps id, question, and options visible).
5. No public CLI or API surface is introduced - MET.
6. Targeted tests and formatting checks pass - Targeted tests PASS (55 total).
   Formatting: WI-3332's added code is ruff-format-clean and introduces zero
   new ruff-check errors; the pre-existing drift on the hook and test files is
   outside the WI-3332 diff and is documented under Verification Commands.

## Cross-Thread Coordination

WI-3332 modified `_stop_handler` (block-emission) in `owner-decision-tracker.py`
and `_render_pending_decisions_block` in `session_self_initialization.py`.
Three sibling bridge threads also target these modules:
`gtkb-prime-worker-context-aware-auq-slice-2` (NO-GO),
`gtkb-prime-worker-delivery-regression-slice-4` (NO-GO), and
`gtkb-startup-refractor-glossary-load-surface` (REVISED). None has reached GO +
implementation, so none has landed code. WI-3332's GO'd implementation lands
first; the sibling threads rebase onto it per normal bridge protocol when they
are revised and GO'd. The designs are orthogonal - WI-3332 narrows block
eligibility by known-relay identity, while slice-2 would branch block emission
by worker context - and compose cleanly at the same control-flow point.

## Owner Decisions / Input

This report depends on owner approval; the relevant AskUserQuestion evidence
(all S354, 2026-05-15):

- Refile authorization: the owner selected "Refile -003 REVISED now" when asked
  how to proceed after the Codex re-review of the thread landed.
- `-003` Specification Links one-word edit: the owner selected "Edit -003 in
  place" when asked how to clear an `implementation_authorization.py`
  placeholder-regex false-positive that flagged the ordinary word "pending" in
  the GO'd `-003` Specification Links. The word was changed to "unresolved";
  the change is cosmetic and non-substantive, and the Codex GO at -004 remains
  valid.
- `FIXTURES` test-infrastructure correction: the owner selected "Fix FIXTURES
  path in this thread" when asked how to handle the 21 pre-existing
  fixture-path test failures blocking the T5 acceptance criterion.
- Fast-lane routing: WI-3332 is routed to the reliability fast-lane by the
  standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
  (owner-decision deliberation `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`);
  durable membership record `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3332`.

## Recommended Commit Type

`fix:` - WI-3332 repairs a recurring Stop-hook false positive (broken behavior)
with no new public capability surface. The added regression tests and the
owner-approved `FIXTURES` test-infrastructure correction are part of the same
defect-fix change set.

## Clause Scope Clarification

This is a single-defect implementation report for one work item, `WI-3332`. It
is not a bulk backlog operation, batch resolve/promote/retire operation, or
multi-WI transition.

Review-packet inventory:

- IP-1: hook classification update in `.claude/hooks/owner-decision-tracker.py`.
- IP-2: startup pending-decision renderer hardening in
  `scripts/session_self_initialization.py`.
- IP-3: owner-decision tracker regression tests (T1, T2, T3).
- IP-4: session-startup renderer regression test (T4).

`WI-3323` is cited only as related context; no dependency, parent-child
relationship, or shared implementation scope is created.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this -005 operative file. Per
`WI-3325`, the clause preflight requires an absolute `--content-file` path; the
path is resolved at runtime with `Resolve-Path`:

```powershell
$file=(Resolve-Path bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-005.md).Path
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression --content-file $file
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression --content-file $file
```

Results: applicability preflight `preflight_passed: true` with no missing
required or advisory specs; clause preflight exit 0 with no gate-failing
blocking gaps. This is the carried-forward posture Codex verified against the
-003 proposal in the -004 GO.
