GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 33ad40f0-18df-4414-8f55-a11ecc7ad070
author_model: Composer
author_model_version: composer
author_model_configuration: Cursor IDE interactive; resolved role loyal-opposition; ::open build; goal continuous NEW/NO-ACTION drain
author_metadata_source: current interactive session envelope 33ad40f0-18df-4414-8f55-a11ecc7ad070

# WI-5370/WI-4856 GO — Tracked Terminal Evidence Strict Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-08-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery-001.md
Work Item: WI-5370
Project: PROJECT-GTKB-TREE-STABILIZATION

---

## Verdict Summary

**GO** for this targetless, zero-mutation recovery thread: fresh observation
report + independent evidence verdict path only. Predecessor remains
quarantined evidence (`WRONG_BRIDGE_VERSION_METADATA` on decorated v003).

Independent evidence confirms:

1. Live carrier `bridge/gtkb-wi4856-daemon-status-liveness-accurate-004.md` is
   clean `VERIFIED`, 1612 bytes, SHA-256
   `0A18DEE434D86E0CF75E96EFE456D5C068D771397AB4A13A7FCA06EC55F0F305`.
2. Historical 1,562-byte payload exists as tracked Git blob
   `cba39b5e29a82cb4ab3388821479e2cff87c5d2b` (SHA-256
   `BF9A7B5A9AF76F7F673A4A3C3A282C8A2689C39FBB7ED52A3EA09F86F4D30981`) at the
   BARRED assessment path; working-tree copy is deleted (`D`) as foreign
   cleanup — not owned by this thread.
3. Batch archive service preconditions (untracked bridge Markdown) do not
   apply to this shape.

**Durability finding (corrected):** the reachable, content-addressed tracked
Git blob satisfies the outstanding historical-byte durability requirement for
the 1,562-byte payload without executing the live-source batch archive
service. The BARRED path is not live project authority. The live 1612-byte
`VERIFIED` carrier must not be rolled back.

---

## Binding Holds

1. `target_paths: []` — no restore/stage/commit/relocate of BARRED deletions.
2. No MemBase/approval-packet/Git mutation under this GO.
3. Observation report + independent VERIFIED remain mandatory
   (`requires_verification: true`).
4. Do not treat predecessor GO/start packets as authority.

---

## Prior Deliberations

- As cited: project-authority inheritance / Tree Stabilization PAUTH
  deliberations; predecessor v006 findings corrected by evidence above.

---

## Applicability Preflight

- packet_hash: `sha256:afddb52ef4e92034dcf8d1892b061bd982d59ef35c5ff115a682e82de588c91a`
- candidate_evidence_hash: `sha256:c8997b33fc88d73c20fda7d50de0b26ed805cb3423d080913adf078dce14def3`
- bridge_document_name: `gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery`
- declared_target_paths: []
- applicability_path_evidence: ["bridge/`", "bridge/`,", "bridge/gtkb-wi4856-daemon-status-liveness-accurate-004.md", "bridge/gtkb-wi5370-batched-archive-preserve-service-011.md`", "bridge/gtkb-wi5370-tracked-terminal-wi4856-byte-ownership-repair-001.md", "bridge/gtkb-wi5370-tracked-terminal-wi4856-byte-ownership-repair-001.md`", "bridge/gtkb-wi5370-tracked-terminal-wi4856-byte-ownership-repair-003.md", "bridge/gtkb-wi5370-tracked-terminal-wi4856-byte-ownership-repair-006.md", "bridge/start/verification", "scripts/batch_archive_terminal_verdicts.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery-001.md`
- operative_file: `bridge/gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery`
- Blocking gaps: 0

---

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi4856-tracked-terminal-evidence-recovery
# live carrier + git cat-file blob cba39b5e... verified
```

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
