NEW
::init gtkb pb
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5973-work-intent-synchronous-normal - 003

bridge_kind: implementation_report
Document: gtkb-wi5973-work-intent-synchronous-normal
Version: 003 (NEW; post-implementation report)
Responds to: bridge/gtkb-wi5973-work-intent-synchronous-normal-002.md
Approved proposal: bridge/gtkb-wi5973-work-intent-synchronous-normal-001.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5973
Recommended commit type: perf:
kb_mutation_in_scope: false

**No KB mutation.** This implementation report performs no MemBase write and does not modify groundtruth.db. Its entire scope is the two declared source/test target paths.

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

## Implementation Claim

WI-5973 implements the founded contention lever: the work-intent registry write
connection now applies PRAGMA synchronous=NORMAL when the connection is in WAL
mode (the production DB is persistently WAL), shortening the per-commit WAL
fsync on the contended single-writer path. No lock semantics change.

- scripts/bridge_work_intent_registry.py, _get_conn: after opening the write
  connection and before _ensure_schema, reads PRAGMA journal_mode and, when it
  is wal, executes PRAGMA synchronous=NORMAL. Non-WAL connections (e.g. fresh
  fixture DBs) keep the default synchronous setting; no raise, no behavior
  change for them.
- platform_tests/scripts/test_bridge_work_intent_registry.py: added
  test_write_connection_uses_synchronous_normal_under_wal, which initializes a
  WAL fixture DB and asserts the write connection reports synchronous == 1
  (NORMAL) and journal_mode == wal.

## Specification Links

- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- GOV-WORK-TREE-HYGIENE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Owner Decisions / Input

No new owner decision required. The owner authorized the contention lever set
(synchronous=NORMAL on WAL) under the broaden-the-fix AskUserQuestion; the
companion deadline-relax lever is WI-5971. The active bounded PAUTH
PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 was verified
active; the active GO (v002), matching claim, and implementation-start packet
were in place before any protected mutation.

## Prior Deliberations

- bridge/gtkb-wi5973-work-intent-synchronous-normal-001.md - approved implementation proposal.
- bridge/gtkb-wi5973-work-intent-synchronous-normal-002.md - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | pytest platform_tests/scripts/test_bridge_work_intent_registry.py -> 52 passed (includes new synchronous test). |
| DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | Implementation-start authorized under active PAUTH for the exact two targets. |
| GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 | Existing 51 work-intent registry tests remain green (no regression); conditional WAL guard is non-disruptive. |
| GOV-WORK-TREE-HYGIENE-001 | Only the two declared targets changed; 702 unrelated dirty paths excluded. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Both targets under E:/GT-KB. |
| Python quality / importability | ruff check and ruff format --check on both changed files -> clean. |

## Commands Run

- python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -k synchronous -q --tb=short
- python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
- python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
- python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py

## Observed Results

- Focused synchronous test: 1 passed.
- Full registry suite: 52 passed, 5 warnings.
- Ruff check: All checks passed; format: 2 files already formatted.

## In-Root Placement Evidence

Both declared implementation targets are in-root under E:\\GT-KB:
- scripts/bridge_work_intent_registry.py
- platform_tests/scripts/test_bridge_work_intent_registry.py
Neither target is out-of-root; all generated artifacts and the bridge file reside under E:\\GT-KB (in-root), satisfying ADR-ISOLATION-APPLICATION-PLACEMENT-001.

## Files Changed

- scripts/bridge_work_intent_registry.py (conditional synchronous=NORMAL under WAL in _get_conn)
- platform_tests/scripts/test_bridge_work_intent_registry.py (new synchronous-under-WAL test)

Excluded out-of-scope dirty paths: 702.

## Recommended Commit Type

- Recommended commit type: perf: (per-connection PRAGMA tuning; no lock-semantics change).

## Acceptance Criteria Status

- Write connection uses synchronous=NORMAL under WAL - MET (conditional guard; focused test asserts synchronous==1 + journal_mode==wal on a WAL connection).
- Applied only under the WAL invariant - MET (PRAGMA journal_mode checked first; non-WAL connections unaffected).
- Focused synchronous test passes - MET.
- Existing work-intent registry tests remain green - MET (52 passed).
- Diff stat: one PRAGMA + WAL guard in one source file plus one focused test - MET.

## Risk And Rollback

Residual risk is low and bounded. synchronous=NORMAL under WAL cannot corrupt
the database; it only relaxes the durability of the last WAL checkpoint (the
registry's durable record and claim semantics are unaffected). Non-WAL
connections are unmodified. Rollback is the revert of the two changed files
under separately governed Git mechanics; bridge files and authorization records
remain append-only.

## Loyal Opposition Asks

1. Verify the conditional synchronous=NORMAL-under-WAL change and the focused test evidence.
2. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
