NEW
::init gtkb lo
::open build

# WI-6218 — MemBase Committable via Deterministic SQL Dump

bridge_kind: prime_proposal
Document: gtkb-wi6218-membase-committable-dump
Version: 001
Author: Prime Builder (harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 2da3617e-95da-4957-bd9e-c277c7c6d051
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword

Work Item: WI-6218
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: ["scripts/membase_dump.py", ".groundtruth/membase/groundtruth-dump.sql", ".gitignore", "platform_tests/scripts/test_membase_dump.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation of governed records; it reads the
database to serialize it. (`groundtruth.db` appears in `target_paths` only
because the restore-path test round-trips a fixture copy; the canonical DB
is never written by this slice.)

---

## Summary

The canonical MemBase content is not in git: `groundtruth.db` is gitignored,
so every governed record created tonight (specs, PAUTHs, deliberations,
documents, attestations) exists in exactly one file on one workstation. A
clone cannot reconstruct canonical state; the durability model rests on one
disk. WI-6218 closes this. The owner selected the deterministic-dump
strategy by AUQ this session
(`DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS`): a
canonical, ordered, reproducible SQL text dump is the git artifact;
`groundtruth.db` remains runtime state rebuildable from the dump; a
freshness check ties the dump to the DB at commit time.

## Scope

1. **`scripts/membase_dump.py`** — the dump/restore/check service:
   - `dump`: serialize schema and rows in deterministic order (tables
     sorted; rows ordered by rowid/primary key; stable text encoding; no
     timestamps of its own) to `.groundtruth/membase/groundtruth-dump.sql`.
     Byte-idempotent for an unchanged DB.
   - `restore --target <path>`: rebuild a SQLite database from the dump;
     refuses to overwrite the canonical `groundtruth.db` (restore targets a
     new file; promoting it is a human/owner act).
   - `check`: recompute the dump from the live DB and compare digests;
     exit 1 with a row-level summary on drift. This is the commit-time
     freshness instrument and a future pre-commit-hook candidate (hook
     registration itself is deferred — the hooks surface belongs to other
     live threads).
2. **`.gitignore`** — ensure the dump path is tracked (negation if any
   pattern covers `.groundtruth/membase/`); `groundtruth.db` stays ignored.
3. **First dump committed** as part of implementation, making canonical
   content clonable for the first time.
4. **`platform_tests/scripts/test_membase_dump.py`** — determinism (two
   dumps of an unchanged fixture DB are byte-identical), round-trip
   fidelity (dump → restore → re-dump is byte-identical; row counts match
   per table), canonical-overwrite refusal, drift detection (a fixture row
   insert flips `check` to exit 1 naming the table), and WAL safety (dump
   under an open concurrent writer connection completes consistently via a
   read transaction).

Out of scope: automatic commit cadence and hook registration (follow-on
once WI-6216's gate repairs land); retiring the LOCALAPPDATA snapshot
mechanism (complementary disaster-recovery, unchanged).

## Specification Links

- `GOV-08` / `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — MemBase is the single
  source of truth; the dump is a projection of it with a mechanical
  freshness check, never a second authority.
- `GOV-STANDING-BACKLOG-001` v5 — WI-6218 is the governing backlog item.
- `DCL-PROJECT-ROOT-BOUNDARY-DB-SNAPSHOT-OUTPUT-EXCEPTION-001` — the
  existing snapshot exception stays; the dump lives IN-ROOT and needs no
  exception.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — bridge discipline governing this
  thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.
- `SPEC-1662` (GOV-18) — the tests assert behavior (determinism,
  round-trip, drift), not structure.

## Requirement Sufficiency

Existing requirements sufficient: GOV-08 already requires MemBase to be the
durable single source of truth; this slice makes that durability
git-backed per the owner's recorded strategy decision. No new requirement
surface.

## Spec-Derived Verification Plan

The five test families in Scope item 4, plus: `check` green immediately
after the first dump commit; `ruff check` and `ruff format --check` on the
two Python files; the full
`platform_tests/scripts/test_membase_dump.py` module count reported in the
implementation report.

## Cross-Harness Disposition

No harness-surface file is touched; the service is a shared project script
and a tracked data artifact. All harnesses gain clonability equally; no
parity impact.

## Owner Decisions / Input

- `DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS` — AUQ:
  deterministic SQL dump selected; binary-DB commit and
  snapshot-manifest-only rejected with reasons.
- Owner goal directive (session goal): complete Phase 2 implemented,
  tested, committed.
- No further owner decision required for this slice; commit-cadence
  automation returns as its own follow-on with WI-6216's gates.

## Prior Deliberations

- `DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS` — the
  strategy decision this implements.
- `WI-6266` — the held-receipts population; a committed dump also makes
  attestation/PAUTH/deliberation evidence clonable, shrinking what any
  future capability-class recovery must reconstruct.
- `bridge/gtkb-baseline-correction-and-goose-projector-slice-1-005.md` —
  its MemBase-rows note ("rows ride the canonical DB, gitignored pending
  WI-6218") is the live gap this closes.

## Risk / Rollback

The dump is additive tracked text; runtime behavior of every consumer is
unchanged (all continue reading `groundtruth.db`). A stale dump is caught
by `check`, not silently trusted. Rollback: delete the dump file and the
service; the DB was never touched.

## Recommended Commit Type

`feat` — new durability capability (service + tracked artifact + tests).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
