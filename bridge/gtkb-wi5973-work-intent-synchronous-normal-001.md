NEW
::init gtkb pb
::open build

# Set SQLite synchronous=NORMAL on the WAL work-intent write connection (WI-5973)

bridge_kind: prime_proposal
Document: gtkb-wi5973-work-intent-synchronous-normal
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-08-06 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5973

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source + focused test (per-connection PRAGMA tuning; no lock-semantics change)
kb_mutation_in_scope: false
requires_review: true
requires_verification: true

**No KB mutation.** This proposal performs no MemBase write beyond the WI-5973
backlog candidate already captured; the implementation touches only the two
declared source/test paths. `groundtruth.db` is deliberately NOT in target_paths.

## Summary

This is the second (companion) contention lever the owner authorized under the
"broaden the fix" AskUserQuestion decision, after WI-5971 (relax the work-intent
write retry deadline). The first-proposed lever, "move the git commit outside the
DB write lock during finalization," was **investigated and found unfounded**:
`finalize_verified_commit` in `.claude/skills/gtkb-verify/helpers/write_verdict.py`
performs its DB write (`write_bridge_file`, line 1316) first and separately, then
runs the git commit via git's own index-lock retry (lines 1327-1355). The git
commit is already sequential and outside any SQLite/registry write lock, so there
is nothing to move. That lever is therefore not proposed; this founded lever
replaces it.

The claim/finalization write path
(`scripts/bridge_work_intent_registry.py`, connection opened at ~line 505 via
`sqlite3.connect(str(db_path), timeout=...)`) never sets `PRAGMA synchronous`.
The database file is persistently in WAL mode (`journal_mode=wal`), which every
connection inherits, but each connection's `synchronous` defaults to `FULL (2)`.
Under `FULL`, every commit fsyncs the WAL, lengthening the time the single writer
holds the database write lock. That prolonged hold is precisely what makes the
`BEGIN IMMEDIATE` acquisition on the claim/finalization path exhaust its retry
budget (`contention_exhausted`) under the concurrent multi-harness bulk-drain
load — the same class blocking the finalization-contention NO-GO cluster
(`gtkb-wi5939-*`, `gtkb-wi5941-*`).

Setting `PRAGMA synchronous=NORMAL` on this connection (valid and safe because
the file is in WAL mode) removes the per-commit WAL fsync, shortening the
write-lock hold time and reducing contention, with a bounded and acceptable
durability tradeoff (see Risk / Rollback).

## Proposed Scope

1. At the work-intent registry write-connection open in
   `scripts/bridge_work_intent_registry.py`, after `sqlite3.connect(...)`,
   execute `PRAGMA synchronous=NORMAL`. Because `synchronous=NORMAL` is only
   safe under WAL, defensively confirm/assert `journal_mode` is `wal` for that
   connection before/at the same point (the file is already WAL-persisted, so
   this is an assertion, not a mode switch).
2. Leave the read-only connection (`?mode=ro`, ~line 1171), lock ordering,
   retry deadline/backoff, and per-attempt busy_timeout unchanged.
3. Add a focused test asserting the write connection reports
   `PRAGMA synchronous` == `1` (NORMAL) and `PRAGMA journal_mode` == `wal`.

Out of scope (explicit follow-on threads, not bundled here per scoped-change
discipline): applying the same `synchronous=NORMAL` to
`groundtruth_kb/project/registry_control_plane.py` write connections and the
`groundtruth_kb/db.py` KnowledgeDB connection. This proposal is deliberately
confined to the single demonstrated `contention_exhausted` source.

## Requirement Sufficiency

Existing requirements sufficient. This is a per-connection PRAGMA conformance/
performance change on the demonstrated contended write path; the WAL invariant
and the finalization-contention evidence already define the boundary. No new or
revised requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge-state authority whose atomic VERIFIED finalization writes contend on this connection; the change preserves append-only / fail-closed guarantees.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing specs linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the focused test below derives from this change and is executed before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-5973 bound to PROJECT-GTKB-HOUSEKEEPING-HARDENING via the whole-project PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-5973 recorded as the governed backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact lifecycle preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — no lifecycle transition triggered.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; artifact-first delivery.

## Prior Deliberations

- `bridge/gtkb-wi5971-work-intent-write-deadline-config-relax-001.md` — the primary companion lever (retry-deadline relax); this proposal is the second lever of the same owner-authorized root-cause fix.
- WI-5788 / WI-5869 — registry-lock hardening precedent (backoff/jitter, relaxed-first timers) on the adjacent control-plane path.
- Finalization-contention NO-GO cluster: `bridge/gtkb-wi5939-false-terminal-finalization-recovery-004.md`, `bridge/gtkb-wi5941-deterministic-release-deadline-test-008.md` — green substance, VERIFIED finalization blocked by the write-lock contention this lever reduces.
- Verified-unfounded lever: `finalize_verified_commit` (write_verdict.py L1316-1355) already sequences the git commit after and outside the DB write, so the "git-outside-DB-lock" lever has no work to do.

## Owner Decisions / Input

This proposal is authorized by the owner AskUserQuestion decision on 2026-08-06
("Broaden the fix" — propose the companion contention levers as separate
threads). The owner-directed lever set was `synchronous=NORMAL` on WAL and
git-commit-outside-DB-lock; the latter was verified unfounded (see Summary), so
only the founded `synchronous=NORMAL` lever is proposed here. No further owner
decision is required to file this proposal for review. Implementation remains
gated on independent Loyal Opposition `GO`, a matching claim, and an
implementation-start packet.

## Specification-Derived Verification Plan

| Spec / requirement | Verification (command) |
| --- | --- |
| Write connection uses synchronous=NORMAL under WAL | `pytest platform_tests/scripts/test_bridge_work_intent_registry.py -k synchronous` — asserts `PRAGMA synchronous`==1 and `PRAGMA journal_mode`==wal on the write connection |
| No-regression (claim/finalization semantics unchanged) | full `pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q` stays green |
| Code-quality gates | `ruff check` AND `ruff format --check` on both target paths |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | clause preflight; both paths under `E:\GT-KB` |

## Acceptance Criteria

- The work-intent registry write connection sets `PRAGMA synchronous=NORMAL`,
  applied only under the WAL invariant (assert `journal_mode==wal`).
- Lock ordering, retry deadline/backoff, per-attempt busy_timeout, and the
  read-only connection are unchanged (diff confined to the write-connection
  PRAGMA + test).
- The focused synchronous test passes and the existing work-intent registry
  suite continues to pass.

## Risk / Rollback

Low, bounded risk. `synchronous=NORMAL` under WAL cannot corrupt the database;
its only effect is that, on an OS crash or power loss, transactions committed
since the last WAL checkpoint may be rolled back. For this registry that is
acceptable: the work-intent claim and the DB VERIFIED projection are both
re-derivable — a lost claim is simply re-acquired, and the VERIFIED state is
reconstructable from the git-committed, append-only bridge files (the git commit,
which is the durable record, is unaffected by this PRAGMA). This is the standard
WAL+NORMAL tradeoff. Rollback is removing the single PRAGMA and its test.

## Recommended Commit Type

`perf:` — reduces per-commit fsync cost and write-lock hold time on the
demonstrated-contended work-intent write connection, without changing lock
semantics or any observable claim/finalization behavior. Diff stat: one PRAGMA
(+ a WAL assertion) in one source file plus a focused test.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
