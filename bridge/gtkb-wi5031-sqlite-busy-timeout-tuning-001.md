NEW
author_identity: Codex Prime Builder A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

# Implementation Proposal - Tune SQLite busy_timeout / connect timeout for concurrent dispatched-worker MemBase writes (latent contention, worsens if dispatch caps raised)

bridge_kind: prime_proposal
Document: gtkb-wi5031-sqlite-busy-timeout-tuning
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5031-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5031

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db_busy_timeout.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Tune MemBase SQLite connection busy-timeout behavior so concurrent dispatched-worker writes degrade predictably instead of failing after the sqlite3 stock timeout.

Work item description: MemBase connection at groundtruth-kb/src/groundtruth_kb/db.py:1531-1540 (_get_conn) opens sqlite3.connect(str(db_path), check_same_thread=...) with NO timeout argument and sets only PRAGMA journal_mode=WAL and PRAGMA foreign_keys=ON; there is no PRAGMA busy_timeout anywhere in the package (verified by grep). Consequence: WAL gives concurrent readers, but writers serialize and fall back to Python sqlite3's stock 5s busy wait, after which a concurrent writer raises OperationalError: database is locked. Not confirmed failing at current caps (worker startup is read-heavy; writes are occasional), so classified hygiene/latent rather than active defect. But it is a degradation vector precisely at the write concurrency the dispatcher caps permit (VERIFIED finalization, backlog adds, KB inserts, deliberation writes), and its severity rises if the global (8) or per-role (3) caps are raised. Recommend: set an explicit PRAGMA busy_timeout (and/or connect(timeout=)) sized for expected concurrent writers, and decide a writer retry/backoff policy. Depends on / pairs with WI-5030 (capacity benchmark) which would measure the actual write-contention ceiling. Consideration-only; not implementation approval.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5031` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/tests/test_db_busy_timeout.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `ADR-0001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260705-WI5029-5031-IMPLEMENT-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5031-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5031`.

## Proposed Scope

- Add explicit SQLite connect timeout and/or PRAGMA busy_timeout configuration in the MemBase KnowledgeDB connection path.
- Choose a conservative default suitable for dispatched-worker write bursts while preserving WAL mode and foreign-key enforcement.
- Add focused regression coverage that verifies the configured busy timeout is applied on KnowledgeDB connections without requiring long wall-clock lock contention in tests.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-0001` | Run focused MemBase DB tests proving the authoritative groundtruth.db connection config preserves append-only SQLite operation while adding explicit busy_timeout behavior. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run the busy-timeout regression test and any capacity-benchmark tests that exercise MemBase write-contention configuration under dispatched-worker assumptions. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify the change supports dispatcher daemon worker concurrency without changing dispatch ownership, routing, or harness isolation. |

## Acceptance Criteria

- KnowledgeDB connections apply an explicit busy-timeout policy instead of relying on Python sqlite3 stock defaults.
- WAL and foreign_keys PRAGMAs remain active after the timeout change.
- Regression coverage proves the timeout PRAGMA/connection timeout is configured deterministically.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/tests/test_db_busy_timeout.py`

## Recommended Commit Type

`feat`
