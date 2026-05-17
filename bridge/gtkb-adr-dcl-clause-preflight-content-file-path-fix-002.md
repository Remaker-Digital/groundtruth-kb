GO

# Loyal Opposition Review - adr_dcl_clause_preflight.py Relative --content-file Fix

Reviewed file: `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`
Bridge document: `gtkb-adr-dcl-clause-preflight-content-file-path-fix`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-17 UTC

## Verdict

GO for implementation under:

- Project Authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- Project: `PROJECT-GTKB-RELIABILITY-FIXES`
- Work Item: `WI-3325`
- Target paths: `scripts/adr_dcl_clause_preflight.py`, `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

No blocking findings.

## Review Evidence

- Live `bridge/INDEX.md` was read before acting. Latest status for this document was `NEW`, so the selected entry was actionable for Loyal Opposition.
- Durable Codex harness id `A` is assigned `loyal-opposition` in `harness-state/role-assignments.json`.
- Direct reproduction from `E:\GT-KB` confirmed the defect: `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-preflight-content-file-path-fix --content-file bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md` exits 1 with `ValueError: 'bridge\\gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md' is not in the subpath of 'E:\\GT-KB'`.
- The absolute-path workaround succeeds and emits a clean clause report with zero blocking gaps.
- Current code evidence matches the proposal: `render_markdown()` calls `operative_file.relative_to(PROJECT_ROOT)` after `_is_under()` at `scripts/adr_dcl_clause_preflight.py:257-269`; `_is_under()` resolves first at `scripts/adr_dcl_clause_preflight.py:337-342`; `main()` assigns `args.content_file` directly to `operative_file` at `scripts/adr_dcl_clause_preflight.py:379-381`.
- Current test surface has absolute `--content-file` coverage but not the project-root-relative regression at `platform_tests/scripts/test_adr_dcl_clause_preflight.py:445-523`.
- Live MemBase/CLI checks confirm `GOV-RELIABILITY-FAST-LANE-001` exists as a specified governance spec; `PROJECT-GTKB-RELIABILITY-FIXES` is active; `WI-3325` is an open defect work item; and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active with allowed mutation classes `source`, `test_addition`, and `hook_upgrade`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` exists with `outcome = owner_decision`; it records the owner's decision to create the standing reliability fast-lane with a project, standing authorization, and GOV spec while preserving bridge review and safety gates.
- `python -m groundtruth_kb ... deliberations search "adr_dcl_clause_preflight relative content-file path crash preflight CLI reliability fix WI-3325" --limit 10 --json` returned `[]`; I found no prior deliberation rejecting this specific fix approach.
- Prior reliability fast-lane thread evidence at `bridge/gtkb-reliability-fast-lane-005.md` and `bridge/gtkb-reliability-fast-lane-006.md` confirms the fast-lane eligibility model and active authorization pattern.

## Specification-Linkage Review

The proposal links the governing bridge and verification specs, the reliability fast-lane GOV spec, the project-root boundary ADR, the standing-backlog visibility spec, and the artifact-oriented advisory specs. The linked set is sufficient for this single-defect implementation proposal.

The proposed test mapping is adequate:

- The new integration regression covers the relative `--content-file` crash.
- The new helper unit test covers project-root-relative resolution, CWD fallback, and absolute-path preservation.
- Existing absolute `--content-file` tests remain as regression coverage.

The proposal's explicit out-of-scope note for relative `--bridge-dir` is acceptable for WI-3325 because the reported owner-scoped defect is the documented `--content-file` path. Hardening `render_markdown()` more broadly can be considered later, but it is not required for this GO.

## Applicability Preflight

- packet_hash: `sha256:bc19240a31f1c5f8a2e743658868e22ef3958fa818b152fd9358c3ac2be50d13`
- bridge_document_name: `gtkb-adr-dcl-clause-preflight-content-file-path-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`
- operative_file: `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-adr-dcl-clause-preflight-content-file-path-fix`
- Operative file: `bridge\gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Opportunity Radar

No material new deterministic-service or token-savings candidate is raised from this review. The only recurring friction observed was ad hoc work-item detail lookup; that is already represented by existing backlog work for CLI discoverability.

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
