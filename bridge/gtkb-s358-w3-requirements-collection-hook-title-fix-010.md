GO

# Loyal Opposition Review: gtkb-s358-w3-requirements-collection-hook-title-fix-009

Document: gtkb-s358-w3-requirements-collection-hook-title-fix
Reviewed proposal: bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-009.md
Verdict: GO
Reviewer: Codex (Loyal Opposition, durable harness A)
Date: 2026-05-18 UTC

## Decision

GO. Version -009 is a revised proposal, not a post-implementation report. It
corrects the target_paths authorization envelope after the -008 NO-GO by naming
the exact approval-packet path produced by the governed `gt spec update`
service, alongside `groundtruth.db`.

This GO authorizes Prime Builder to regenerate the implementation-start packet
from the live -010 GO and file a new post-implementation report. It does not
itself mark the already-landed GOV v4 correction as VERIFIED.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix`

```text
## Applicability Preflight

- packet_hash: `sha256:af02a50b28c883419e6553bab0397bee3c2657b8ca6a5b737d1682b5623ecb26`
- bridge_document_name: `gtkb-s358-w3-requirements-collection-hook-title-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-009.md`
- operative_file: `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s358-w3-requirements-collection-hook-title-fix`
- Operative file: `bridge\gtkb-s358-w3-requirements-collection-hook-title-fix-009.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Prior Deliberations

The required Deliberation Archive search was run. Semantic search returned no
matches for the compound requirements-collection hook query, so the review used
direct retrieval of the cited deliberations and approval evidence.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION authorizes the S358
  combined governance-correction project and records W3 as a metadata-only v4
  dropping the abandoned LLM/retrieval phrase from the title.
- DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION records
  the earlier LLM-classifier and retrieval-augmented-option design whose title
  remnant W3 removes.
- DELIB-1701 records the prior Loyal Opposition GO for the no-LLM regex-gate
  requirements-collection hook proposal.

## Review Evidence

- Live bridge state was read before acting; latest status was `REVISED:
  bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-009.md`.
- Version -009 carries non-empty project linkage metadata, Owner Decisions /
  Input, Requirement Sufficiency, and a specification-derived verification plan.
- Version -009 declares:
  `target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json"]`.
- The exact approval-packet path exists, and `groundtruth.db` exists.
- `implementation_authorization.extract_target_paths()` and
  `implementation_authorization.path_authorized()` return:
  `groundtruth.db -> True`,
  `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json -> True`,
  and the prior lower-case/versionless packet path -> False. This confirms the
  -008 defect is closed by exact-path authorization rather than a broad waiver.
- Direct SQLite inspection confirms the already-landed GOV v4 record remains
  substantively correct: latest version 4, type `governance`, status `verified`;
  v4 title equals the v3 title with only the abandoned parenthetical removed;
  v4 description equals v3 description; the approval packet has
  `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`,
  and matching `full_content_sha256`.

## Findings

None.

## Post-GO Conditions For Prime Builder

Prime Builder should regenerate the implementation-start authorization packet
from this live GO and file a new post-implementation report. That report should
cite this GO, include the regenerated packet hash, and include
reviewer-reproducible `path_authorized()` evidence for both `groundtruth.db` and
the exact approval-packet path.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
