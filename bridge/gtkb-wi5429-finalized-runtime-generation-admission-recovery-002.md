NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 33ad40f0-18df-4414-8f55-a11ecc7ad070
author_model: Composer
author_model_version: composer
author_model_configuration: Cursor IDE interactive; resolved role loyal-opposition; ::open build; goal continuous NEW/NO-ACTION drain
author_metadata_source: current interactive session envelope 33ad40f0-18df-4414-8f55-a11ecc7ad070

# WI-5429 NO-GO — Cohort Hash Drift Before Review Acceptance

bridge_kind: lo_verdict
Document: gtkb-wi5429-finalized-runtime-generation-admission-recovery
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-08-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md
Work Item: WI-5429
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING

---

## Verdict Summary

**NO-GO.** The repair design for `materialize_generation()` (undefined
`errors`/`digest`, duplicated manifest loop) is directionally sound and
preflights pass, but the proposal’s own fail-closed currentness rule is
already tripped: one declared target’s SHA-256 no longer matches the Exact
Current Evidence table.

---

## Blocking Finding

### F1 (P0) — `scripts/gtkb_dispatcher_daemon.py` SHA-256 drift

**Claim.** At review time the live file hash differs from the proposal cohort
hash, so implementation cannot start from this NEW under the proposal’s
“any target preimage drift → revise” gate.

**Evidence.**
- Proposal table:
  `scripts/gtkb_dispatcher_daemon.py` =
  `e9a9dfb96d94d6623ace9110a861aa901dffc38864187c5d10b21bd3bfd2de1c`
- Observed SHA-256:
  `754ed8719ce141dba048f8cfd770cdcf88fb94d43d5efc792ab34b307d416c32`
- Other four declared targets MATCH at review time.
- Incomplete materializer body still visible (uses `errors` / `digest` without
  initialization; duplicated manifest loop) in
  `scripts/dispatcher_generation_admission.py` `materialize_generation()`.

**Impact.** Starting against a drifted fifth path would authorize work against
an unpinned preimage and break the recovery’s exact-cohort contract.

**Recommended action.** File `REVISED` with refreshed Exact Current Evidence
hashes (and re-stated baseline test/ruff counts if they changed). Preserve the
materializer repair plan. Do not rewrite v001 in place.

---

## Design Note (non-authorizing)

When a current REVISED lands, the proposed fix (initialize error accumulator,
single `_compute_generation_hash()` identity, one manifest pass, no live
dispatcher/TAFE mutation) remains the right minimum repair for the reproduced
undefined-name failures.

---

## Prior Deliberations

- `DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST`
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`
- Historical `gtkb-wi5429-finalized-runtime-generation-admission` v008 NO-GO
  (substantive defect evidence)

---

## Applicability Preflight

- packet_hash: `sha256:b46a29c4609bbbce8eab67eee3bd06b3a46becaee04b3cc67ec96450933afd8d`
- candidate_evidence_hash: `sha256:d8537da8f91305fd65b33fbd50b2579370ca2c907a5d1ba6e27d4aafe35d0b60`
- bridge_document_name: `gtkb-wi5429-finalized-runtime-generation-admission-recovery`
- declared_target_paths: ["platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py"]
- applicability_path_evidence: ["bridge/gtkb-wi5429-finalized-runtime-generation-admission-005.md`", "bridge/gtkb-wi5429-finalized-runtime-generation-admission-006.md`", "bridge/gtkb-wi5429-finalized-runtime-generation-admission-008.md`", "config/runtime-state", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py`", "platform_tests/scripts/test_dispatcher_generation_admission.py", "platform_tests/scripts/test_dispatcher_generation_admission.py`", "scripts/dispatcher_generation_admission.py", "scripts/dispatcher_generation_admission.py`", "scripts/ensure_dispatcher_daemon.py", "scripts/ensure_dispatcher_daemon.py`", "scripts/gtkb_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md`
- operative_file: `bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md`
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
- authorization_id: `PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`
- authorization_source: `bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py"]
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
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5429-finalized-runtime-generation-admission-recovery`
- Operative file: `bridge\gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — |

---

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5429-finalized-runtime-generation-admission-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5429-finalized-runtime-generation-admission-recovery
# SHA-256 cohort: 4 MATCH; gtkb_dispatcher_daemon.py DRIFT
```

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
