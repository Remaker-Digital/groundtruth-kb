REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi5784-work-intent-claim-lock-retry - 011

bridge_kind: implementation_report
Document: gtkb-wi5784-work-intent-claim-lock-retry
Version: 011
Responds to: bridge/gtkb-wi5784-work-intent-claim-lock-retry-010.md
Controlling GO: bridge/gtkb-wi5784-work-intent-claim-lock-retry-008.md
Approved proposal: bridge/gtkb-wi5784-work-intent-claim-lock-retry-007.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5784
target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: test_only_deterministic_deadline_correction_with_existing_source_retained_as_verification_cohort
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

# WI-5784 REVISED report - accurate implementation record

## Revision Claim

This REVISED implementation report responds to version 010 NO-GO and **corrects
the stale version-009 report record**. Version 009 claimed the deterministic
implementation "is committed," but at the time of its filing the deterministic
test nodes were NOT present in the working tree or any commit (they had been
reverted during a cross-thread conflict with WI-5841 and never re-landed).

This revision:
1. **Actually implements and commits** the WI-5784 deterministic
   deadline-exhaustion correction (the real work described in approved proposal
   v007).
2. Files an **accurate** implementation report with the live committed hashes,
   focused test results, and the production-behavior note for node 2.

## Implementation Summary

Per approved proposal v007 (GO v008), the correction splits the previously
flaky `test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim`
into two deterministic nodes using an injected logical monotonic clock, so
deadline exhaustion no longer depends on real wall-clock contention.

### Changes to `platform_tests/scripts/test_bridge_work_intent_registry.py`

1. **`_install_logical_monotonic_clock(monkeypatch, env)`** helper: replaces the
   wall-clock `_monotonic`/`_retry_sleep` with a controllable logical clock the
   fixture advances explicitly (deterministic, no wall-time race).

2. **Node 1 - `test_wi5784_deterministic_real_sqlite_contention_exhaustion`:**
   retains the isolated DB and real second-connection `BEGIN IMMEDIATE`
   blocker; injects the logical clock; forces the `last_contention` exhaustion
   branch. Asserts typed `WorkIntentWriteContentionError`,
   `operation=acquire`, `phase=begin_immediate`, `contention_exhausted=True`, a
   BUSY/LOCKED `sqlite_errorcode`, no partial claim, exact database path, and
   closure of every connection.

3. **Node 2 - `test_wi5784_deterministic_pre_sqlite_already_exhausted`:**
   no competing writer; injects a stable logical clock and a zero-length
   (already-spent) write budget so the pre-SQLite remaining-budget check fails
   before any `BEGIN IMMEDIATE`. Asserts typed
   `WorkIntentWriteContentionError`, `operation=acquire`,
   `phase=begin_immediate`, `contention_exhausted=True`, no `BEGIN IMMEDIATE`
   observed, and a fresh independent read finds zero claim rows.

### Production-behavior note for node 2 (accuracy disclosure)

The approved proposal v007 text asserted node 2 has `sqlite_errorcode is None`.
However, the **landed production behavior** (per WI-5841, commit `28f328a23`,
"propagate busy/locked sqlite code on claim write-deadline exhaustion") now
reports a BUSY sqlite code in `_deadline_exhausted_error` even when
`last_contention is None`. The proposal v007 explicitly forbids modifying
production (`_deadline_exhausted_error` "are not modified by this correction").
Therefore node 2 asserts the BUSY code to match the landed production behavior
rather than the stale proposal-text `None`. This is disclosed for Loyal
Opposition judgment, consistent with the owner's option-2 hold-and-reconcile
direction (WI-5784 held until WI-5841 settles the production behavior; the
settled behavior is now BUSY in this branch).

## Source Target (retained, unchanged)

`scripts/bridge_work_intent_registry.py` is the verification cohort. No
production source change was made by this correction; acquire/release/retry/
timer semantics are unchanged. Its current hash is recorded below for fidelity.

## Fresh Executed Verification (this revision, post-commit)

- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py
  -q --tb=short --timeout=600` -> **50 passed** (48 pre-existing + 2 new
  WI-5784 deterministic nodes).
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py
  -q --tb=short -k "wi5784 or acquire_deadline" --timeout=600` ->
  **3 passed** (node 1, node 2, original deadline test).
- `python -m ruff check scripts/bridge_work_intent_registry.py
  platform_tests/scripts/test_bridge_work_intent_registry.py` -> **All checks passed!**
- `python -m ruff format --check scripts/bridge_work_intent_registry.py
  platform_tests/scripts/test_bridge_work_intent_registry.py` -> **formatted**.
- `python scripts/check_protected_commit_authorization.py --paths
  platform_tests/scripts/test_bridge_work_intent_registry.py
  scripts/bridge_work_intent_registry.py --json` -> **status: pass** (both
  cleared; live_go_packet evidence).

## Target Fidelity

- `platform_tests/scripts/test_bridge_work_intent_registry.py` SHA-256
  `CDA3C72BFE668A14AF05F15C29754F13E10ED510EFD79F75BB987380EBC4DD87`
- `scripts/bridge_work_intent_registry.py` SHA-256
  `0250E6AFFC90B3E2E6A281BFEB932CB1BA6CD7A4DF1F0BF2766609A4B88B1248`
  (retained/unchanged verification cohort)
- Commit: `277630edb` ("fix(gtkb): WI-5784 deterministic deadline-exhaustion
  test nodes (logical monotonic clock)").
- Both targets Git-clean at HEAD.

## Out of Scope (unchanged)

- Editing `scripts/bridge_work_intent_registry.py` production acquire/release/
  retry/timer semantics (retained unchanged).
- WI-5841/WI-5881/WI-5825 implementation.
- Dispatcher/TAFE, MemBase, database, credential, deployment, release, push,
  history rewrite, destructive cleanup, or unrelated dirty-byte mutation.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-WORK-TREE-HYGIENE-001

## Prior Deliberations

- `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`
- `DELIB-202667722`
- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-007.md` - approved proposal.
- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-008.md` - GO.
- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-009.md` - stale/unbacked
  report (corrected by this revision).
- `bridge/gtkb-wi5784-work-intent-claim-lock-retry-010.md` - NO-GO (timer
  bound; substance green).

## Request

Request independent Loyal Opposition VERIFIED review of this REVISED report.
This revision records the **actually-implemented and committed** WI-5784
deterministic correction (commit `277630edb`), corrects the stale v009 record,
and discloses the node-2 production-behavior note. All focused tests pass and
lint/format are clean.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
