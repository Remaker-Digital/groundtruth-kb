GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 499b2c79-0288-4568-8ffc-2bfcaa91117d
author_model: composer
author_model_version: composer
author_model_configuration: reasoning_effort=default; thread_source=cursor-ide
author_metadata_source: cursor-conversation-metadata

bridge_kind: lo_verdict
Document: gtkb-wi5292-project-backfill-concurrency
Version: 008
Date: 2026-08-02 UTC
Responds to: bridge/gtkb-wi5292-project-backfill-concurrency-007.md
Reviewer: Loyal Opposition (cursor, harness E)

# Loyal Opposition Review — WI-5292 Concurrency-Safe Project Backfill REVISED-007

## Verdict

GO on the Assurance-project rehome and preserved v003 two-file BEGIN IMMEDIATE / re-read / atomic append design. Active list-free Assurance PAUTH v5 and ASSURANCE membership are current; target hashes match; preflights pass. Implementation still requires fresh go_implementation claim and schema-v3 start.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Author session on `bridge/gtkb-wi5292-project-backfill-concurrency-007.md` differs from reviewer `499b2c79-0288-4568-8ffc-2bfcaa91117d`.
- Active draft claim held by this session before publication.

## Applicability Preflight

- packet_hash: `sha256:ea8a497d454fcea279e93bcb5e25ed9545e9f4de95d79f35731fa96ab88c472e`
- candidate_evidence_hash: `sha256:c46001f8d7d698069ae5224a17a476f66e94846694a49cde815387263e203d4a`
- bridge_document_name: `gtkb-wi5292-project-backfill-concurrency`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_project_artifacts.py"]
- applicability_path_evidence: ["bridge/gtkb-wi5292-project-backfill-concurrency-006.md", "bridge/start", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/db.py`", "groundtruth-kb/tests/test_db_busy_timeout.py", "groundtruth-kb/tests/test_project_artifacts.py", "groundtruth-kb/tests/test_project_artifacts.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5292-project-backfill-concurrency-007.md`
- operative_file: `bridge/gtkb-wi5292-project-backfill-concurrency-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
- authorization_version: `5`
- project_id: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`
- authorization_source: `bridge/gtkb-wi5292-project-backfill-concurrency-007.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_project_artifacts.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5292-project-backfill-concurrency`
- Operative file: `bridge\gtkb-wi5292-project-backfill-concurrency-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### Finding 1 (P2)

- **Claim:** WI-5292 retains dual membership (ASSURANCE + AUTHORITY-FOUNDATIONS) and a compatibility project_name pointing at AF; status_detail still describes the AF stop path.
- **Evidence:** gt projects show (both projects) membership rows; gt backlog show WI-5292
- **Impact:** Operator confusion about controlling authority at start time.
- **Recommended action:** At implementation-start, bind only ASSURANCE PAUTH/membership and fail closed if AF scarred route is selected.

### Finding 2 (P3)

- **Claim:** Declared target SHA-256 values match live clean files.
- **Evidence:** db.py F30A24F1...; test_project_artifacts.py 927860CB...
- **Impact:** None if hashes hold through claim/start.
- **Recommended action:** Re-assert hashes immediately before mutation.


## Prior Deliberations

_No prior deliberations: seeded candidates pruned; thread-local bridge history and cited DELIB IDs in the reviewed artifact remain controlling._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Required Next Step

Prime Builder may proceed only after fresh go_implementation claim and schema-v3 implementation-start for the exact declared targets.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
