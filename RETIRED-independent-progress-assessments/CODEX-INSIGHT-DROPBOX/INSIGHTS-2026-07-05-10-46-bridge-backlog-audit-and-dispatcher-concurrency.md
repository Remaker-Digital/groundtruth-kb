# INSIGHTS — Bridge Backlog Audit + Dispatcher Concurrency (2026-07-05)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 689f575f-a1a8-4d43-bd92-7bcae23c16f8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved role loyal-opposition via ::init gtkb lo

**Author:** Loyal Opposition (Claude, harness B) — interactive session
**Date:** 2026-07-05 (session span ~08:25Z–17:46Z)
**Session role source:** durable registry (loyal-opposition); `::init gtkb lo`
**WIs:** WI-4990, WI-5029, WI-5030, WI-5031, WI-3375, WI-4472
**Deliberations captured:** DELIB-20260705-WI4990-FINALIZATION-WAIVER, DELIB-20260705-RETIRE-3-SUPERSEDED-NOGO-THREADS
**Specs/refs:** SPEC-INTAKE-ca9165 (CA9165 per-role cap), GOV-FILE-BRIDGE-AUTHORITY-001, GOV-STANDING-BACKLOG-001

---

## Executive Summary

Session began as a dispatcher-concurrency question and became a full bridge-backlog
audit. Net finding: **the bridge queue is healthy and the LO queue is empty**; the
apparent problem surfaces (9 UNKNOWN threads, 4 NO-GO threads) are almost entirely
benign residue, not live defects. One genuine live owner-gated item (WI-4990) and
one systemic pattern (slug-variant-collision) were the only substantive issues; both
now have owner decisions captured to the Deliberation Archive. Three consideration
backlog items were filed for dispatcher-capacity hardening.

No project files were mutated. All writes went through governed `gt` CLIs
(`gt backlog add`, `gt deliberations add`) plus this report.

---

## Positive Confirmations

- Canonical `gt bridge state-report`: 1,581 threads; VERIFIED 1,369 (+8 mislabeled ≈ 1,377 true); LO-actionable NEW/REVISED = **0**.
- Dispatcher health **PASS** (routing_config PASS; complex_lifecycle PASS after a transient watchdog-heartbeat flap self-cleared).
- Roles live: PB=A (Codex), LO=B (Claude), LO=C (Antigravity); D/E/F LO-tagged but non-dispatchable.
- Multi-harness LO drain working: harness C auto-processed the 3 startup-flagged NEW threads to VERIFIED mid-session.

---

## Finding F1 — Two divergent per-role dispatch concurrency caps; only one wired [P3]

**Observation.** Live per-role cap is CA9165's flat default **3** for both roles
(`scripts/dispatcher_runtime.py:2216` `_max_live_dispatched_per_role`; enforced in
`_spawn_harness` ~:4250 by PID-token scan). A second implementation,
`scripts/bridge_dispatch_concurrency.py` (WI-3375, slot-file bounded pool), uses
role-differentiated defaults `{loyal-opposition:3, prime-builder:2}` but is imported
by **nothing** except its own test — its docstring admits wiring was "deferred to a
later slice."

**Deficiency rationale.** A maintainer reading `bridge_dispatch_concurrency.py` to
determine live caps would wrongly conclude Prime is capped at 2. The S350 throughput
directive quoted in that module (LO 2-4, Prime 1-3) implies role-differentiated caps
were the design intent, which the live flat-3 does not honor.

**Proposed solution.** Either wire the slot module in and retire the CA9165 inline
cap, or retire/mark the slot module superseded and reconcile intended defaults.
Filed as **WI-5029** (hygiene, P3).

**Option rationale.** Consideration-only capture chosen over inline fix because
disposition (which implementation wins) is a design decision requiring owner/Prime
input, not a mechanical edit.

## Finding F2 — No live dispatch capacity/load test exists [P3]

**Observation.** The "how high can caps go" question is empirically unanswerable:
`scripts/ops/dispatch_chaos_harness.py` is a deterministic STUB; `benchmark_dispatch_envelope.py`
is synthetic input data. Neither drives live concurrent dispatch.

**Deficiency rationale.** The caps (8/3/4) are incident-response + directive values,
never capacity-measured. Any cap increase is currently inference, not evidence.

**Proposed solution.** Add a real capacity benchmark measuring the binding
constraints (provider rate-limit/cost; git-index-lock; SQLite write serialization;
machine RAM; hung-worker behavior). Filed as **WI-5030** (improvement, P3).

**Option rationale.** A benchmark is the only defensible path to raising caps;
guessing a higher number risks converting a cost-storm risk into a contention-deadlock
risk.

## Finding F3 — SQLite write-contention is untuned for dispatched-worker concurrency [P3]

**Observation.** `groundtruth-kb/src/groundtruth_kb/db.py:1531-1540` opens
`sqlite3.connect(...)` with no `timeout=` and sets only `PRAGMA journal_mode=WAL` +
`foreign_keys=ON`; no `busy_timeout` PRAGMA anywhere in the package.

**Deficiency rationale.** WAL gives concurrent readers, but writers serialize on the
stock 5s Python default, then raise `database is locked`. Not confirmed failing at
current caps, but a latent degradation vector precisely at the write concurrency the
dispatcher caps permit; severity rises if caps are raised.

**Proposed solution.** Set an explicit `busy_timeout` sized for expected concurrent
writers; decide a writer retry/backoff policy. Filed as **WI-5031** (hygiene, P3;
pairs with WI-5030).

**Option rationale.** Pair with the capacity benchmark (WI-5030) so the timeout is
tuned against measured contention rather than a guess.

## Finding F4 — Slug-variant-collision produces orphaned NO-GO verdicts [P2]

**Observation.** All 3 "stale" NO-GO threads froze at NO-GO on their original slug
while the actual work continued and reached VERIFIED under a **variant slug** (`…-001-NNN`)
or a **later program slice**:
- `gtkb-dashboard-industry-alignment-slice2a-visibility` → superseded by `…-slice2c-integration` VERIFIED 2026-06-22.
- `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution` → superseded by `…-001` chain VERIFIED 2026-05-09 + `…-auto-resolve-cross-turn` VERIFIED 2026-06-22.
- `gtkb-startup-trigger-awareness-and-skill-reference` → superseded by `…-001` chain VERIFIED.

In two cases the NO-GO verdict is **newer** than the VERIFIED continuation (a reviewer
re-NO-GO'd a proposal whose work had already completed under the variant slug).

**Deficiency rationale.** Orphaned NO-GOs inflate the NO-GO/Prime-actionable count and
invite future sessions to re-investigate completed work as if live. The per-slug claim
and WI-ID hooks do not catch variant-slug re-filings (consistent with the prior
`slug-variant-collision` lesson in session memory).

**Proposed solution.** (a) Retire the 3 as WITHDRAWN citing the superseding VERIFIED
thread (owner-approved this session — `DELIB-20260705-RETIRE-3-SUPERSEDED-NOGO-THREADS`).
(b) Consider a reconciliation pass for other original-slug threads frozen at
non-terminal status while a variant slug completed. (c) Longer-term: a guard that
detects variant-slug re-filing of an existing WI/topic.

**Option rationale.** WITHDRAWN citation preserves the append-only audit trail while
clearing the count; a full guard is deferred as a larger design item.

## Finding F5 — Shared-`groundtruth.db`-only closure finalization is policy-undefined (WI-4990) [P2]

**Observation.** WI-4990's closure is verified-correct (`resolved/resolved`, tests
pass, preflights clean) but cannot be headlessly finalized: its sole `target_paths`
is the shared `groundtruth.db` blob carrying ~10 commits of unrelated multi-session
state, which the VERIFIED commit-finalization gate cannot scope-split. The `-004`/`-005`/`-006`
chain (all 2026-07-05) is an active headless NO-GO loop consuming dispatch capacity.

**Deficiency rationale.** LO behavior here is non-deterministic — some interactive
sessions blob-sweep `groundtruth.db` on VERIFIED (e.g. commit `b5a2d0db`); headless
workers correctly withhold VERIFIED. Every shared-DB-only closure hits the same wall.

**Proposed solution.** Owner selected the **By-Reference Finalization Waiver**
(`DELIB-20260705-WI4990-FINALIZATION-WAIVER`) as the standing pattern: Prime files a
REVISED with a `## By-Reference Finalization Waiver` section citing the DELIB; the
verify helper finalizes the bridge chain only, deferring `groundtruth.db` to a separate
owner-scoped sweep.

**Option rationale.** Keeps the WI-4990 commit scoped and correctly labeled; rejected
alternatives were owner batch-sweep (adds a step) and per-thread blob-sweep policy
(folds unrelated state).

## Finding F6 — UNKNOWN-bucket is cosmetic pre-rule residue [P4]

**Observation.** All 9 UNKNOWN threads are benign: 8 are completed VERIFIED
verifications whose first line is an old `# … Verification` heading (grandfathered by
the Body Status-Token Rule), 1 is an intentional S292 incident note self-labeled
"informational audit trail." 0 stuck/misrouted.

**Deficiency rationale.** Cosmetic only — inflates UNKNOWN and undercounts VERIFIED by
~8. No routing/liveness risk.

**Proposed solution.** **Accept as-is; do NOT remediate.** Bridge files are append-only
and the rule deliberately grandfathers them; rewriting first lines = no-op versions of
terminal threads for zero benefit.

**Option rationale.** Remediation would be backlog clutter for a non-issue; the
grandfathering is by design.

---

## Prime Builder Implementation Context

**WI-4990 finalization (owner-approved):**
- Objective: reach VERIFIED without reworking the (correct) closure metadata.
- Preconditions: `DELIB-20260705-WI4990-FINALIZATION-WAIVER` exists (done).
- Evidence: `bridge/gtkb-wi4990-terminal-dispatch-reconciliation-closure-001..006.md`; `groundtruth.db` (` M`).
- Touchpoints: Prime files REVISED `-007` adding `## By-Reference Finalization Waiver` citing the DELIB. No source/test/config.
- Verification: re-run applicability + clause preflights + the 5 focused tests; confirm WI-4990 row unchanged; LO finalizes VERIFIED `-008` via `write_verdict.py --finalize-verified` (bridge chain only).
- Rollback: none — WI-4990 stays `resolved` regardless of finalization mechanic.

**Retire 3 superseded NO-GOs (owner-approved):**
- Objective: WITHDRAWN closure on each original slug citing the superseding VERIFIED thread.
- Precondition: `DELIB-20260705-RETIRE-3-SUPERSEDED-NOGO-THREADS` (done).
- Path: governed bridge-reconciliation / WITHDRAWN filing. No source/test/metadata rework.
- Caveat: threads dormant ~19 days — may need an explicit reconciliation pass rather than passive dispatch.

---

## Unresolved / Handoff Items

| Item | Status | Next actor |
|---|---|---|
| WI-4990 VERIFIED finalization | Owner-approved; DELIB captured; unblocked | Prime files REVISED `-007` → LO finalizes `-008` |
| Retire 3 superseded NO-GOs (WITHDRAWN) | Owner-approved; DELIB captured | Prime / reconciliation pass (dormant — may not self-trigger) |
| WI-5029 per-role cap drift | Open (consideration) | Triage into a project |
| WI-5030 dispatch capacity benchmark | Open (consideration) | Prerequisite to any cap increase |
| WI-5031 SQLite busy_timeout tuning | Open (consideration) | Pairs with WI-5030 |

**Owner disposition (AUQ):** "Let the dispatcher self-resolve" for WI-4990 + retirements.

---

## Mechanics Note for Future LO Sessions

Interactive LO write boundary observed this session:
- Write tool → non-allowlisted paths (e.g. `.tmp/`) is blocked by `GTKB-LO-FILE-SAFETY`. `CODEX-INSIGHT-DROPBOX/**` IS allow-listed.
- `python -` stdin-pipe heredocs can trip a shell dangerous-command guard (false `Remove-Item /` match). Avoid.
- Capture MemBase decisions/backlog via governed CLIs (`gt deliberations add --content <here-string>`, `gt backlog add`), never the Write tool or python stdin pipes.
- Governed markdown documents under `CODEX-INSIGHT-DROPBOX/` require author-provenance metadata (GOV-DOCUMENT-AUTHOR-PROVENANCE-001): author_identity, author_harness_id, author_session_context_id, author_model, author_model_version, author_model_configuration.

Skills applied: codex-report, decision-capture, bridge, proposal-review
