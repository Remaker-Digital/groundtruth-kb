NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

bridge_kind: governance_review
Document: gtkb-advisory-pauth-exposure-sweep-mixed-snapshot-indexed-resolution
Version: 001
Date: 2026-07-30 UTC

Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5743

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Proposal — PAUTH Exposure Sweep Snapshot Coherence And Indexed Lifecycle Resolution

## Executive Summary

WI-5760 exposed a reusable concurrency and append-only source-of-truth access problem while adding the PAUTH finalization exposure sweep. The implemented sweep now uses one run-wide decision time, one initial numbered-file index, and start/end source fingerprints; it discards its rows if ordinary bridge or SQLite-file movement is detected. That mitigation closes the immediate silent mixed-file-snapshot failure in the new command, but it does not provide a reusable strict lifecycle snapshot or a transactionally coherent PAUTH/project/membership read.

The platform's strict lifecycle resolver still enumerates the entire bridge directory separately for each requested thread. The PAUTH validation path still opens separate SQLite connections for authorization, project status, work-item membership, and ancestry and validates PAUTH expiry against wall time before the canonical evaluator receives the sweep's selected decision time. A long-running reader can therefore either pay millions of repeated directory comparisons for strictness or use a faster indexed projection that cannot prove all bridge and MemBase facts came from one declared observation.

This is already a material append-only SoT cost. The current root contains 14,128 top-level bridge Markdown files totaling 145,701,997 bytes, including 14,111 exact numbered files across 2,349 threads; `groundtruth.db` is 844,025,856 bytes. Strict-resolving every thread through the current resolver implies approximately 33,210,162 directory-entry comparisons before content parsing. Restricting that pattern to the 279 currently non-terminal threads still implies approximately 3,944,502 comparisons.

This Advisory proposes one governed disposition only: after independent confirmation, update existing WI-5743 to own the reusable indexed lifecycle-snapshot and coherent query contract. It does not create a duplicate work item and does not authorize implementation.

## Advisory Classification

- Category: concurrency, snapshot coherence, deterministic query service, append-only SoT access latency.
- Severity: high for authority correctness; high and worsening for repository-scale latency.
- Affected readers: PAUTH exposure inventory, bridge query/currentness surfaces, strict lifecycle consumers, and any future batch authorization report.
- Desired property: one bounded read operation must declare and prove one bridge/PAUTH observation while retaining append-only history.
- Current mitigation status: WI-5760 detects ordinary source movement and discards mixed rows, but reusable transaction/snapshot infrastructure remains absent.

## Explicit Non-Mutation Boundary

This Advisory performs no MemBase, KB, or `groundtruth.db` mutation, write, insert, change, or edit. It performs no source, test, configuration, metadata, Git index/history, dispatcher, TAFE, deployment, credential, or external-system mutation. `target_paths` is intentionally empty because this is a review artifact, not an implementation proposal. A later confirmed route may append a new WI-5743 backlog version through the governed backlog command, but that action is outside this filing.

## Claim

An authority-sensitive sweep is not trustworthy unless every row is derived from one declared observation. GT-KB lacks a reusable service that combines:

1. one immutable exact-thread file index;
2. strict lifecycle parsing against that index without per-thread directory rescans;
3. one read-only SQLite transaction for PAUTH, project, membership, and ancestry facts;
4. one operation-time instant used by both validation and evaluation; and
5. an optimistic end-of-run source check that fails closed when bridge or database state moved.

Without that service, callers must choose between unbounded repeated SoT access and a faster but weaker projection. Either choice can produce false `authorized`, false exposure, omitted new bridge versions, or internally incomparable rows under concurrency.

## Evidence E1 — The New Sweep Needed A Local Mixed-Snapshot Guard

`scripts/pauth_finalization_exposure_sweep.py:118-229` now demonstrates the minimum safe pattern:

- line 125 builds one exact numbered-file index;
- line 126 captures the initial bridge plus SQLite-file fingerprint;
- line 205 supplies one run-wide decision time to the canonical evaluator;
- lines 227-229 rebuild and compare the source fingerprint; and
- a mismatch discards all rows and classifies `concurrent_source_change`.

The focused `test_sweep_discards_mixed_snapshot` mutation-injection test proves that the command does not emit partially trusted rows after detected movement. The live WI-5760 run at decision time `2026-07-30T12:27:30Z` returned exit 0 with `scan_consistent=true`, fingerprint `sha256:0893ec7c2104795ae8804ff0ed878aa9654aef168e89afa612aa038ff1ecc4e6`, and one coherent inventory of 2,349 threads.

This guard is intentionally optimistic. It detects ordinary file metadata movement; it is not a substitute for a strict indexed resolver or a single database snapshot.

## Evidence E2 — Strict Lifecycle Resolution Rescans The Whole Directory Per Thread

`scripts/bridge_thread_files.py:61-76` already provides a useful one-pass exact numbered-file index. `versioned_bridge_files` can consume that index, but the strict lifecycle resolver does not.

`scripts/bridge_lifecycle_resolver.py:131-166` constructs a thread-specific regex and runs `bridge_dir.iterdir()` for every resolution. `resolve_bridge_lifecycle` at lines 653-670 always enters that path. No API accepts a previously captured immutable `file_index`, so a batch caller cannot obtain strict chain validation with one enumeration.

Current measured scale on 2026-07-30:

| Metric | Value |
| --- | ---: |
| Top-level bridge files | 14,138 |
| Top-level bridge Markdown files | 14,128 |
| Bridge Markdown bytes | 145,701,997 |
| Exact numbered Markdown files | 14,111 |
| Exact numbered threads | 2,349 |
| Non-terminal threads in live PAUTH sweep | 279 |
| All-thread repeated directory comparisons | 33,210,162 |
| Non-terminal-only repeated comparisons | 3,944,502 |
| `groundtruth.db` bytes | 844,025,856 |

These comparison counts exclude strict UTF-8 reads, metadata parsing, chain validation, and database work, so they are a lower bound on repeated access cost.

## Evidence E3 — PAUTH Facts Are Read Through Separate SQLite Connections

The current PAUTH decode path does not hold one read snapshot across its related facts:

- `scripts/implementation_authorization.py:1053-1105` loads authorization and related records through separate SQLite connections;
- project status opens another connection at lines 1176-1184;
- direct work-item membership opens another at lines 1189-1200;
- descendant membership and ancestry open further connections at lines 1203-1263; and
- `validate_project_authorization_row` begins at line 1266 after those helper boundaries are available independently.

A concurrent PAUTH, project lifecycle, membership, or dependency mutation can therefore make one logical evaluation combine facts that never coexisted in one SQLite snapshot. Start/end database-file fingerprints detect ordinary movement but cannot identify which exact database snapshot each separate connection observed.

## Evidence E4 — Decision Time Is Split Between Validation And Evaluation

`validate_project_authorization_row` checks expiry against `now_utc()` at `scripts/implementation_authorization.py:1284`. The new sweep passes its selected decision time only to the canonical operation evaluator. Thus a fixed-input report can still change when wall time crosses the PAUTH expiry boundary before evaluation begins.

The correction must thread one explicit decision time through PAUTH load/validation and canonical evaluation. It must not reimplement PAUTH policy locally or monkeypatch a process-global clock.

## Evidence E5 — The Append-Only Corpus Changed During The Investigation

The bridge remained active while this read-only investigation ran:

- an earlier sample contained 14,127 top-level Markdown files;
- the current sample contains 14,128; and
- the additional file is the typed, consumed WI-5760 implementation report published during the same session.

That growth is correct append-only behavior. It also proves that long-running inventories must expect concurrent additions and cannot treat a one-time filename list as an eternal snapshot. The corrective design should preserve retained history while making current reads bounded and explicit.

## Risk And Impact

- False authorization: report targets or bridge versions may be evaluated against a PAUTH/project membership combination that never existed atomically.
- False exposure: a thread may be labeled denied using a PAUTH state newer than the bridge bytes used to derive its cohort.
- Omission: a version appended after the initial index may be absent without a machine-readable concurrent-change result.
- Structural under-validation: a fast index consumer may miss strict chain defects because strict validation cannot reuse its captured index.
- Latency amplification: per-thread rescans and repeated DB opens compound with append-only bridge and MemBase growth.
- Lock-pressure temptation: fixing coherence with a long-held global registry lock would worsen the publication convoy and timeout class already tracked by WI-5788.

## Recommended Corrective Direction

### 1. Add an immutable indexed strict lifecycle resolver

- Extend the canonical resolver with a batch/index input produced by one exact directory enumeration.
- Bind the index to a stable digest covering canonical path, version, size, and content identity.
- Preserve every current strict diagnostic: noncontiguous versions, malformed metadata, wrong author role, wrong `Responds to`, duplicate version, correction-chain rules, and unknown status.
- Make one-thread and batch callers use the same strict parser so speed does not create a weaker authority path.

### 2. Add one coherent read context

- Open one read-only SQLite transaction/snapshot for PAUTH, project status, memberships, and ancestry.
- Pass one explicit UTC decision time through validation and evaluation.
- Record a bridge snapshot digest plus an SQLite snapshot identity in output.
- Recheck bridge fingerprint and `PRAGMA data_version` at completion; fail closed as `concurrent_source_change` if the declared observation cannot be proven.

### 3. Keep expensive validation outside publication locks

- Use optimistic snapshot validation for read reports.
- Do not hold the global registry control-plane lock for a long scan.
- Do not activate, wake, configure, or mutate TAFE/dispatcher as part of query coherence.
- Coordinate with WI-5788 rather than moving the latency problem into a longer critical section.

### 4. Establish bounded scale budgets

- Exercise deterministic 1k, 5k, 15k, and projected-future numbered-file corpora.
- Measure enumerations, bytes read, strict parse count, DB connection count, wall time, cancellation latency, and peak memory.
- Require one bridge enumeration and one coherent database snapshot per query regardless of thread count.
- Preserve a full rebuild/audit path that reconstructs the same result from append-only history.

## Exact Governed Disposition

If Loyal Opposition confirms this Advisory, update existing WI-5743 rather than creating a duplicate. Extend that item's bounded actionable-query acceptance contract to include:

- reusable indexed strict lifecycle resolution;
- bridge snapshot identity and concurrent-change failure;
- one coherent PAUTH/project/membership read context;
- one run-wide validation/evaluation decision time;
- repository-scale latency and cancellation budgets; and
- parity between the new query service, `gt bridge show`, the PAUTH exposure sweep, and existing exact-thread semantics.

Cross-link but do not absorb these adjacent carriers:

- WI-5719 — generation-bound bridge currentness and full-tree digest cost;
- WI-5715 — coherent scalable registry authority reads;
- WI-5788 — global control-plane lock timeout, fairness, and publication latency; and
- WI-4835 — broader cached/snapshot-surface audit.

WI-5743 is open, unapproved, and an active member of active `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. That project has no active list-free whole-project PAUTH. Therefore neither this Advisory nor a future backlog update authorizes implementation. After the already-pending DCL-v2 owner decision is resolved and after Advisory confirmation, Prime Builder must present one owner AUQ for a bounded whole-project PAUTH before any implementation proposal or protected mutation begins.

## Current Specification-Derived Verification Evidence

- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_pauth_finalization_exposure_sweep.py -q --tb=short` — exit `0`; 49 tests passed, including matching-GO binding, canonical-evaluator parity, malformed-latest visibility, fixed-input output, and mixed-snapshot discard.
- `python scripts/pauth_finalization_exposure_sweep.py --project-root E:\\GT-KB --decision-time 2026-07-30T12:27:30Z --json --output .gtkb-state/pauth-exposure/wi5760-live-20260730.json` — exit `0`; `scan_consistent=true`; 2,349 threads, 279 non-terminal, and 259 implementation-bearing threads evaluated.
- Direct corpus measurement through one `bridge/` enumeration observed 14,111 exact numbered files and produced the repeated-comparison lower bounds recorded above.

## Future Spec-To-Test Plan

| Requirement | Future behavioral evidence | Required result |
| --- | --- | --- |
| Exact indexed lifecycle parity | Run every strict resolver fixture through one-thread and batch-index APIs | Byte-identical lifecycle views and diagnostic codes; one directory enumeration. |
| Concurrent bridge append | Append a numbered version after index capture and during parse | Entire query returns `concurrent_source_change`; no mixed rows. |
| Concurrent PAUTH/project/member mutation | Mutate each related table between logical reads | One transaction sees one state or the query fails closed; no impossible fact combination. |
| Decision-time expiry boundary | Evaluate just before, at, and after `expires_at` with a fixed instant | Validation and canonical evaluation use the same instant deterministically. |
| Unknown/malformed chain visibility | Seed missing status, wrong author, wrong reference, gap, and duplicate fixtures | Every invalid thread remains visible with exact stable diagnostics. |
| Scale | 1k/5k/15k/future corpus benchmark | One enumeration, bounded duration/memory, clean cancellation, no orphan process. |
| Append-only reconstruction | Rebuild snapshot/index from retained numbered history | Rebuilt digest and query results exactly match the incremental/current projection. |
| Disabled dispatch | Run all query/snapshot tests with TAFE disabled | No process start, wake, configuration change, or dispatcher/TAFE mutation. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — exact numbered-chain state remains the bridge authority surface.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — authorization must be evaluated at one declared operation-time instant.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active whole-project PAUTH and project membership facts must be read coherently.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — deterministic bounded services should replace repeated ad-hoc scans.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — performance improvements may not weaken strict lifecycle or PAUTH authority.
- `GOV-WORK-TREE-HYGIENE-001` — query correction must remain read-only and preserve unrelated concurrent work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve this fix-worthy concurrency/latency case as durable governed work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — a later implementation proposal must cite the exact coherence and performance requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — later verification must cover concurrency, expiry, malformed chains, scale, and append-only reconstruction.

## Prior Deliberations And Related Governed Evidence

- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — establishes the project-only approval model and prevents treating WI-5743's legacy authorization rows as executable authority.
- `bridge/gtkb-wi5760-pauth-preflight-visibility-005.md` through `-007.md` — approved PAUTH visibility design, GO, and the implementation that exposed and locally mitigated the mixed-snapshot case.
- `bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md` — broader append-only SoT access-latency precedent.
- `bridge/gtkb-advisory-manual-bridge-publication-receipt-bypass-001.md` and confirmed `-002.md` — typed-publication/global-lock latency and receipt-authority evidence.
- WI-5743 owner-source directive — create a bounded filterable bridge query and eliminate scanner hangs instead of repeatedly relying on a suboptimal scan path.

## Owner Decisions / Input

No owner decision is required to file or independently review this Advisory Proposal. The later WI-5743 implementation route is deliberately not approved here. Its whole-project PAUTH AUQ is queued behind the already-visible pending DCL-v2 decision so owner input remains one decision at a time.

## Explicit Non-Approval And TAFE Exclusion

This Advisory is not a GO, PAUTH, implementation proposal, implementation-start packet, commit authority, terminal verdict, release authority, or deployment authority. It authorizes no future mutation. The dispatcher/TAFE remained deliberately disabled and is outside both the evidence collection and the recommended correction.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
