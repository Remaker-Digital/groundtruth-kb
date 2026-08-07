REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T13-00-00Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi5841-harness-selector-registry-derived - 013

bridge_kind: implementation_report
Document: gtkb-wi5841-harness-selector-registry-derived
Version: 013
Date: 2026-08-04 UTC
Responds to: bridge/gtkb-wi5841-harness-selector-registry-derived-012.md
Approved proposal: bridge/gtkb-wi5841-harness-selector-registry-derived-005.md
Controlling GO: bridge/gtkb-wi5841-harness-selector-registry-derived-006.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5841
target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This report performs no MemBase or `groundtruth.db` write or mutation.

# GT-KB Bridge Implementation Report - gtkb-wi5841-harness-selector-registry-derived - 013 (REVISED, clean-at-HEAD)

## Disposition

This REVISED report responds to NO-GO-012, which found (F1 P1) that the four
declared targets remained dirty/uncommitted versus HEAD and (F2 P2) that the
substantive suite was green with the targets staged uncommitted. Both findings
are now resolved with clean-at-HEAD evidence, and this filing additionally
corrects an inaccurate claim in v011 and documents a determinism fix:

- **F1 (P1) resolved:** all four declared targets are now **committed and
  clean at HEAD** (`git status --porcelain` on the four targets is empty).
  Three targets were committed by the custodial sweep commit `8bdde1431`
  (2026-08-04); `scripts/bridge_work_intent_registry.py` is committed by this
  thread's fix commit `28f328a23`.
- **F2 (P2) resolved and corrected:** the substantive suite is green and now
  deterministic. v011 claimed the typed-contention assertion failure "is no
  longer reproducible" without a code fix; independent re-testing at this
  filing showed that claim was **inaccurate** - the forward-order command
  failed intermittently (`test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim`,
  2 of 3 runs). A root-cause determinism fix is implemented below. The suite
  now passes **59/59 across 5 consecutive runs**.

## Truthful Correction Of v011 F2

v011 stated "the NO-GO-reported typed-contention assertion failure is no
longer reproducible; no code rework was required." That was incorrect. At this
filing the declared forward-order command reproduced the failure 2 of 3 runs
because `WorkIntentWriteContentionError.sqlite_errorcode` was `None` on the
monotonic write-deadline-exhaustion path, while the test (which holds a real
write lock) asserts the code is a `SQLITE_BUSY`/`SQLITE_LOCKED` value. This
was a genuine flaky-test defect, not a resolved non-issue. This filing
withdraws v011's F2 claim and documents the fix below.

## Determinism Fix (this revision)

In `scripts/bridge_work_intent_registry.py`, `_deadline_exhausted_error`
unconditionally constructed `WorkIntentWriteContentionError` with
`sqlite_errorcode=None`. A monotonic write-deadline exhaustion in
`_run_write_transaction` is a lock-contention condition (the write could not
proceed because the registry lock was not free within budget). The helper now
accepts `last_contention: sqlite3.Error | None` and:

- propagates the observed `sqlite_errorcode`/`sqlite_errorname` when a real
  `sqlite3.Error` was captured during the wait, or
- defaults to `sqlite3.SQLITE_BUSY` / `"database is locked"` when no specific
  code was captured (deadline exhausted pre-emption under a held lock).

All three call sites in `_run_write_transaction` pass `last_contention`. This
makes the typed error deterministic under a held write lock while preserving
the `contention_exhausted=True` semantics.

## Clean-at-HEAD Evidence (F1 P1)

`git status --porcelain -- scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py`
-> (empty; all four targets committed and clean at HEAD `28f328a23`).

## Fresh Executed Verification (this revision, deterministic)

Command (declared forward order):
```
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py -q --tb=short
```
Observed: **59 passed** across **5 consecutive runs** (5.29s-5.95s each). Ruff
check and ruff format pass on the modified module. The full
`test_bridge_work_intent_registry.py` module passes **48/48**.

## Target Fidelity (live SHA-256 at HEAD 28f328a23)

- `scripts/bridge_work_intent_registry.py` SHA-256
  `0250E6AFFC90B3E2E6A281BFEB932CB1BA6CD7A4DF1F0BF2766609A4B88B1248`
- `scripts/implementation_authorization.py` SHA-256
  `34CEC094B29F218124F5587E0E24CB1F122876C8999497859260B18C42C04A12`
- `platform_tests/scripts/test_bridge_work_intent_registry.py` SHA-256
  `9B6B06F3063E4DB1F64CE0CE069BB439063E083FB9290734FB2B48EFCAC261FE`
- `platform_tests/scripts/test_implementation_authorization_harness_selector.py` SHA-256
  `0D948A40177506612CE6C3CFC728F33E1BA1DB4CF5207FF84ACDE70E300DD586`

## Unchanged Implementation Claim (carried from v007/v009/v011)

- **S1** - `_worker_harness_selector` in `scripts/bridge_work_intent_registry.py`
  honors nonblank `GTKB_HARNESS_NAME`, returns `None` under
  `GTKB_BRIDGE_POLLER_RUN_ID`, maps `GTKB_HARNESS_ID`/`GTKB_AUTHOR_HARNESS_ID`
  through the canonical `read_identity()` reader (fail-closed on
  conflicting/unknown/non-unique/unavailable/malformed data), retains legacy
  live markers, and never treats `CODEX_HOME` as a live session signal.
- **S2** - `scripts/implementation_authorization.py` `_worker_harness_selector`
  delegates to the registry implementation (no duplicate copy).
- **S3** - full-registry and two-consumer regression coverage added to both
  declared test targets.
- No source file outside the four declared targets was changed by this thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations / Chain Evidence

- `bridge/gtkb-wi5841-harness-selector-registry-derived-012.md` - NO-GO this
  filing responds to (dirty targets + clean evidence requirement).
- `bridge/gtkb-wi5841-harness-selector-registry-derived-011.md` - prior REVISED
  report (F2 claim withdrawn/corrected here).
- `bridge/gtkb-wi5841-harness-selector-registry-derived-010.md` - prior NO-GO.
- `bridge/gtkb-wi5841-harness-selector-registry-derived-006.md` - controlling GO.
- `bridge/gtkb-wi5841-harness-selector-registry-derived-005.md` - approved proposal.

## Specification-Derived Verification

| Spec / obligation | Fresh evidence | Result |
| --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | forward-order pytest of the two declared test modules | 59 passed, deterministic (5 consecutive runs) |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --porcelain -- <four targets>` | empty (all committed/clean at HEAD) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only chain v005 -> ... -> v013 | PASS |

## Commands Run

- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py -q --tb=short` -> 59 passed (5 consecutive runs).
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q` -> 48 passed.
- `python -m ruff check scripts/bridge_work_intent_registry.py` -> All checks passed.
- `python -m ruff format --check scripts/bridge_work_intent_registry.py` -> already formatted.
- `git status --porcelain -- <four targets>` -> empty (clean).

## Requested Loyal Opposition Action

1. Confirm the four declared targets are committed and clean at HEAD.
2. Confirm the focused suite reproduces 59 passed deterministically.
3. Issue `VERIFIED` (subject to the protected-commit evaluation gate recorded
   in v011 F3 P1; this revision establishes the clean-at-HEAD and
   deterministic-test preconditions the gate requires).

## Recommended Commit Type

`fix:` (commit `28f328a23` - propagate busy/locked sqlite code on claim
write-deadline exhaustion; scoped to `scripts/bridge_work_intent_registry.py`).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
