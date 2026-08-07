GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: b54e5dab-d06d-48e7-b3ec-9de4a3b223b5
author_model: Cursor Grok 4.5
author_model_version: cursor-grok-4.5
author_model_configuration: Cursor IDE interactive Loyal Opposition; harness E; newest-first LO auto-process drain
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: lo_verdict
Document: gtkb-wi5950-publication-capability-recovery
Version: 002
Author: Loyal Opposition (cursor, harness E)
Date: 2026-08-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5950-publication-capability-recovery-001.md

# Loyal Opposition Review — WI-5950 publication-capability recovery (NEW 001)

## Verdict

GO on bridge/gtkb-wi5950-publication-capability-recovery-001.md. The stranded pre-fix no-capability defect is real: ordinary mint refuses already-existing candidates and consume binds a moving aggregate preimage, so pre-fix filings from before WI-5942 helper integration cannot be healed through the normal mint/consume path. The proposed owner-authorized control-plane recovery command is correctly scoped, fail-closed, and does not weaken ordinary publication gates.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`; verdict envelope uses `::open test`).
- Reviewed artifact author_session_context_id `G-2026-08-05T17-03-48Z` differs from reviewer `b54e5dab-d06d-48e7-b3ec-9de4a3b223b5`.
- Active draft claim held by this session before publication.

## Applicability Preflight

- packet_hash: `sha256:8da06e38232cbf7dfb8913d7357ae0b05678a6ff5398a7c46bdda8e54d774118`
- candidate_evidence_hash: `sha256:406a8aaab925788488ca3ebb151e36ba04d03a4b9a1db8399264caf9a57dd9e4`
- bridge_document_name: `gtkb-wi5950-publication-capability-recovery`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
- applicability_path_evidence: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`,", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`.", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`."]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5950-publication-capability-recovery-001.md`
- operative_file: `bridge/gtkb-wi5950-publication-capability-recovery-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
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
- authorization_source: `bridge/gtkb-wi5950-publication-capability-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `30729C621B931EFD3D495FC764195AE2D76470ED29EA4B0A55D3FB71601500B3`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5950-publication-capability-recovery`
- Operative file: `bridge\gtkb-wi5950-publication-capability-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | â€” | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- Owner decision B (2026-08-06): add governed recovery for stranded pre-fix bridge files.
- Surfacing NO-GOs: WI-5942 -010, WI-5314 -016, WI-5368 -030.
- Related lineage: WI-5825-class atomic VERIFIED stranding; WI-5942 mint/consume helper fix.

## Positive Confirmations

1. Live `_bridge_publication_transition_digest` still raises `candidate bridge version already exists` for existing paths (`registry_control_plane.py` ~3195).
2. Consume path still validates `aggregate_preimage_digest` against live aggregate state (multiple consume/check sites in the same module).
3. Proposal requires explicit owner-authorization evidence, recomputes live aggregate preimage at recover/consume time, and lists fail-closed mismatch conditions.
4. Targets are limited to control-plane + focused recovery test; ordinary mint/consume/write_bridge_file called out of scope.
5. Applicability preflight_passed true; clause blocking gaps 0; PAUTH present.

## Residual Risks (non-blocking)

- Recovery must remain owner-authority gated and must not become a general bypass for ordinary writes.
- Implementation should pin exact owner-authorization evidence shape (token/DELIB id) in the command contract and tests.
- Clearing named stranded versions (5942 001/003, 5314 015, 5368 023/027/028) is an operational follow-through after the command lands — keep that as exercise of the command, not silent auto-heal.

## Spec-to-Test Mapping

| Spec / requirement | Proposed verification | Adequacy |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 recovery yields consumed capability | focused recovery test + protected-commit acceptance | adequate |
| Ordinary mint/consume unchanged | non-impairment / regression on existing paths | adequate |
| Fail-closed on auth/byte/session/aggregate mismatch | negative cases in recovery test module | adequate |

## Commands Executed

1. Applicability + clause preflights against `-001`
2. Live read of mint existing-file guard and aggregate preimage consume checks
3. Compact LO scan confirming this as sole remaining actionable item before publish

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
