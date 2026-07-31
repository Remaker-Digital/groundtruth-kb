NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

bridge_kind: implementation_report
Document: gtkb-wi5757-advisory-router-dedup-starvation
Version: 003
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5757-advisory-router-dedup-starvation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5757

target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py"]

# WI-5757 Implementation Report — Advisory Router Versioned Dedup And Starvation Visibility

## Outcome

Implemented the independently approved two-file WI-5757 correction. Bridge advisory candidate identity is now the numbered document identity (`slug-NNN`) instead of the bare thread slug; bounded legacy compatibility prevents duplicate restaging of the same physical file without starving later advisory versions; the router exposes a deterministic `starvation_signal`; and a single-writer live backfill staged the seven currently reachable versioned advisory heads that were not already represented.

The router remains stage-only. The implementation and backfill created no `work_items` row, made no MemBase mutation, promoted no candidate, changed no bridge artifact, and neither activated nor mutated TAFE/dispatcher.

## Implementation Authority And Start Evidence

- Approved proposal: `bridge/gtkb-wi5757-advisory-router-dedup-starvation-001.md`.
- Independent verdict: `bridge/gtkb-wi5757-advisory-router-dedup-starvation-002.md`, latest `GO` at implementation start.
- Active parent project: `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`.
- Active list-free whole-project authorization: `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM`, version 3.
- Work item: WI-5757, active member, order 1.
- GO-implementation claim: held by session `019fb19b-7814-73c1-8707-204e432cbf00` for the exact thread and target pair.
- Schema-v3 packet pre-start hash: `sha256:7117a028c591441b49da7d33cacc48d82a99f96c1a35f4cda5482ca908db00f3`.
- Finalized schema-v3 packet hash: `sha256:1bace810670534db9f519d7ab097e95088139d23032a80710c7bc3343e2dc2d1`.
- Operation-time decisions: `implementation_packet_create` and `implementation_start` both returned `allowed=true` for the exact source/test target cohort.

## Changed Files

### `scripts/advisory_backlog_router.py`

- `collect_bridge_advisories()` now uses `f"{doc_id}-{version:03d}"` as the bridge candidate `source_key` while retaining the bare slug as `provenance_bridge_thread`.
- Candidate-store dedup first checks the versioned key, then treats a legacy bare-slug record as the same candidate only when its recorded `relative_path` is the current physical advisory file.
- Work-item dedup queries the versioned key first. A legacy bare-slug work-item association blocks only the version represented by the legacy candidate record, with version 001 as the conservative default when no usable legacy path exists.
- `RouterResult.starvation_signal` is true exactly when `scanned > 0`, nothing staged, and every scanned item was skipped as existing.
- Normal JSON, compact JSON, and `.gtkb-state/advisory-router/last-scan.json` now carry `starvation_signal`.
- The CLI emits one stdout `WARNING:` line before its JSON result when the starvation signal is true.

### `platform_tests/scripts/test_advisory_backlog_router.py`

Expanded the fixture-rooted suite from 14 to 22 tests. New coverage proves:

- a `-002` head stages after the same slug's `-001` candidate;
- a legacy bare-slug candidate for the same physical file does not duplicate;
- a versioned work-item key blocks its exact version;
- a legacy bare-slug work item does not block a newer version;
- a legacy work item still blocks the version recorded by its legacy candidate evidence;
- starvation state is returned, serialized, persisted, and warned exactly once;
- a multi-head backfill stages each new head once and is idempotent on the immediate rerun; and
- router execution leaves fixture bridge bytes unchanged.

All tests remain fixture-rooted and do not read or mutate the live candidate store or live MemBase.

## Live Backfill Evidence

The live backfill was deliberately single-writer because inspection found a separate candidate-store check/append race. Immediately before each live pass, process inspection confirmed no other `advisory_backlog_router.py` process was active.

### Before / dry-run inventory

- `scanned`: 95
- `would stage`: 7
- `skipped existing`: 83
- `skipped expired by the governed 60-day policy`: 5
- `errors`: 0
- `starvation_signal`: false

The seven versioned heads were:

1. `gtkb-lo-tooling-defect-advisory-011`
2. `gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-002`
3. `gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory-002`
4. `gtkb-modernization-gate-1-25-bootstrap-prefix-design-review-004`
5. `gtkb-role-gated-hook-envelope-fragility-advisory-003`
6. `gtkb-sot-access-latency-append-only-growth-cost-advisory-001`
7. `gtkb-wi5330-governance-gate-bypass-advisory-002`

### First non-dry-run pass

- `scanned`: 95
- `staged`: 7
- `skipped existing`: 83
- `skipped expired`: 5
- `errors`: 0
- no `work_items` row or other MemBase state was created.

### Immediate second non-dry-run pass

- `scanned`: 95
- `staged`: 0
- `skipped existing`: 90
- `skipped expired`: 5
- `errors`: 0
- `starvation_signal`: false because five scanned records were expired rather than existing.

This proves backfill idempotency without weakening the configured retention policy. After the backfill the append-only candidate store contained 285 lines and 286,104 bytes. The measured live scans took approximately 5–11 seconds; this implementation does not claim independently extreme candidate-store latency. Scaling measurement and writer atomicity are preserved in the separate concurrency advisory.

## Verification Results

| Verification | Result |
| --- | --- |
| `python -m pytest platform_tests/scripts/test_advisory_backlog_router.py -q --tb=short` | 22 passed; one pre-existing `asyncio_mode` configuration warning |
| `python -m ruff check scripts/advisory_backlog_router.py platform_tests/scripts/test_advisory_backlog_router.py` | pass |
| `python -m ruff format --check scripts/advisory_backlog_router.py platform_tests/scripts/test_advisory_backlog_router.py` | pass |
| `git diff --check -- scripts/advisory_backlog_router.py platform_tests/scripts/test_advisory_backlog_router.py` | pass; informational future CRLF-conversion warning on the test file |
| implementation authorization target validation | authorized for the exact two target paths |
| live backfill first pass | 7 staged, 0 errors |
| live backfill immediate repeat | 0 staged, 0 errors |

## Specification Links

- `GOV-STANDING-BACKLOG-001`
- `DCL-STANDING-BACKLOG-SCHEMA-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `SPEC-1830`
- `SPEC-1662`
- `GOV-10`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required for this implementation report. The exact
two-file implementation was performed under the active whole-project PAUTH and
independent v002 GO. This report does not authorize terminal commit, corrective
work from the adjacent Advisory Reports, dispatcher/TAFE action, or any scope
beyond the reviewed implementation.

## Specification-Derived Evidence

| Requirement | Implementation/test evidence | Result |
| --- | --- | --- |
| `GOV-STANDING-BACKLOG-001` / `DCL-STANDING-BACKLOG-SCHEMA-001` | versioned keys plus legacy-compatible candidate/WI gates | newer advisory versions are reachable; candidate schema and owner-gated promotion remain intact |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | fixture bridge snapshot test and live router semantics | bridge is read-only; versioned append-only heads are respected |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` / `SPEC-1830` | single service pass plus repeat | seven live heads staged once; repeat stages zero |
| `SPEC-1662` / `GOV-10` | 22 production-interface behavioral tests | pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | implementation remained within the linked exact two-file proposal | pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | proposal-derived T1-T6 behavior executed and expanded into concrete tests | pass |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | starved advisory graph edges re-enter explicit staged lifecycle without promotion | pass |

## Concurrency Findings And Advisory Reports

Two concurrency defects were found and are being preserved as separate `NEW` governance-review Advisory Reports; neither is silently absorbed into WI-5757's approved two-file behavior:

1. Implementation-start orchestration lost a nested long-running session handle, leading to three duplicate `implementation_authorization.py begin` process trees (nine processes total) for one logical WI-5757 start. The duplicate trees were identified exactly and terminated before any target mutation; one controlled invocation then completed. The advisory recommends per-bridge/session single-flight start, surfaced handles, packet/current-alias coherence, and phase telemetry.
2. The candidate store's load/check/append sequence has no interprocess lock or under-lock reload, so two router processes could both miss and append the same candidate. The current backfill was single-writer. The advisory recommends a project-rooted writer lock, stable idempotency receipt, crash-safe append, atomic last-scan publication, deterministic concurrency tests, and measured append-only growth benchmarks.

No TAFE/dispatcher action occurred in either incident or the implementation.

## Scope And Worktree

Only the two approved tracked files are modified. The live candidate JSONL and last-scan JSON are ignored runtime evidence surfaces explicitly exercised by the approved backfill, not source targets. No unrelated dirty file was adopted or changed. No staging, commit, push, history rewrite, release, deployment, credential, external-system, destructive-cleanup, dispatcher, or TAFE action occurred.

## Risk And Rollback

Residual risk is bounded but real: concurrent router writers can still duplicate a staged event until the separate advisory is implemented. Owner-gated promotion contains the immediate blast radius; live backfill was serialized.

Code rollback is the exact two-file revert. Candidate events already appended are append-only evidence and should not be deleted or rewritten; if their later owner review rejects them, disposition them through the existing governed candidate lifecycle. No MemBase rollback is required because the router created no work-item rows.

## Loyal Opposition Verification Questions

1. Do the versioned primary key and the exact-path legacy compatibility rule prevent duplicate restaging without recreating slug-wide starvation?
2. Does legacy work-item compatibility block only the legacy-represented version and allow newer numbered heads?
3. Does the starvation signal satisfy the reviewed exact predicate across result JSON, last-scan evidence, and CLI warning?
4. Do the 22 tests and live 7-then-0 backfill prove the linked requirements without relying on TAFE or autonomous backlog promotion?
5. Are the two adjacent concurrency flaws correctly separated into governed Advisory Reports rather than smuggled into this implementation scope?

Recommended commit type: fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
