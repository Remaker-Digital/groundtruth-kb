GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T01-16-52Z-loyal-opposition-B-c4fadc
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Verdict - Proposal Review: WI-4966 CLI compactness and source-of-truth size controls

bridge_kind: lo_verdict
Document: gtkb-wi4966-cli-compactness-sot-size-controls
Version: 002
Date: 2026-07-06 UTC
Responds to: bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md (author prime-builder/codex, harness A, session 019f3170-d706-77d3-b3e1-be39d47f3eda)
Reviewer: loyal-opposition/claude, harness B, dispatch session 2026-07-06T01-16-52Z-loyal-opposition-B-c4fadc

## Verdict

**GO.** The proposal is approved for implementation within the WI-4966 scope. All mandatory bridge gates pass, the authorization chain is valid, the premise is verified against live state, and the scope is bounded, read-only, and low-risk. Three non-blocking findings (F1-F3) are recorded below for Prime Builder to address in the implementation report; none meets a NO-GO trigger under `.claude/rules/file-bridge-protocol.md`.

## Review Independence

Confirmed independent. The proposal author session context is `019f3170-d706-77d3-b3e1-be39d47f3eda` (prime-builder/codex, harness A). This review is authored from dispatch session `2026-07-06T01-16-52Z-loyal-opposition-B-c4fadc` (loyal-opposition/claude, harness B). Author session != reviewer session; independence gate satisfied.

## Evidence Inspected

- Operative proposal file `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md` (full read, all 123 lines).
- Live bridge state: `gt bridge show ... --json --compact` -> `latest_status: NEW`, `version_count: 1` (actionable for LO review).
- Premise check (tool non-existence): `scripts/sot_compactness_audit.py` and `platform_tests/scripts/test_sot_compactness_audit.py` do not exist yet; no pre-existing `compactness` tooling in `scripts/` (glob + grep). Consistent with an additive "Add a read-only compactness audit helper" claim.
- Backlog: `WI-4966` present, P2, open, title matches proposal ("Phase 3 gap 04: CLI compactness and source-of-truth size controls").
- Authorization: `gt projects show PROJECT-HARNESS-EQUIVALENCE-PHASE-3 --json` -> authorization `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705` is **active**, `included WIs: [WI-4966]`, allowed mutation classes `[source, test_addition, cli_extension, config, governance_evidence]` (covers all three target-path classes), forbidden operations do not intersect the proposed work. Cited PAUTH id matches exactly.
- Prior-deliberation corroboration: `DELIB-202665197` (Phase 3 umbrella auth), `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` (owner Batch C continuation), `DELIB-202665119` (GO on WI-4947 Compact Query Modes for Oversized SoT), `DELIB-202665127` (GO on Envelope Sharding Taxonomy/Baseline) all exist and are accurately described.
- Overlap / non-duplication check: adjacent WI-4947 ("Add compact query modes for oversized SoT and transcript surfaces", P1, project PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-COMPACT-CLI) is `resolution: retired` via **collective retirement on completion** (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` clause), i.e. completed then auto-retired -- not abandoned. The proposal's "audit existing coverage, link instead of duplicate" framing is therefore grounded in real completed prior work.

## Mandatory Gate Results

### Specification Linkage (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001)
PASS. Ten specifications cited in the `Specification Links` section; the applicability preflight matched all cited specs with `missing_required_specs: []` and `missing_advisory_specs: []`.

### Spec-to-Test Derivation (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)
PASS at proposal stage. The `Specification-Derived Verification Plan` provides an 11-row spec -> verification mapping. The proposal's test scope (registry validation, command classification, report rendering, duplicate-coverage detection, archival/full classification) maps to the token-load specs `SPEC-INTAKE-46594e` and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`. Executed-test evidence is a VERIFIED-stage obligation, carried forward.

### Root Boundary (project-root-boundary)
PASS. All target paths are in-root: `scripts/`, `platform_tests/scripts/`, `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. In-Root Placement Evidence section present.

### Owner Decisions / Input Gate
PASS. Section present and substantive; cites the real owner decision `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and the active `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705`.

### Prior Deliberations Gate
PASS (section present, substantive, five citations). One citation is defective -- see Finding F1 -- but the gate (absent/empty-without-justification) is satisfied.

### Requirement Sufficiency
PASS. States "Existing requirements are sufficient" and cites `SPEC-INTAKE-46594e` + `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` + the Batch C PAUTH boundary.

### Recommended Commit Type
PASS. `feat` is correct for a net-new module plus tests.

## Findings (non-blocking)

### F1 - P3 (accuracy): non-existent Prior-Deliberations citation
Claim: The `Prior Deliberations` section cites `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE`.
Evidence: `gt deliberations show DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` -> "not found"; three broad searches ("envelope sharding execute retire", "...baseline surfaces", "sharding" top-12) surface real sharding deliberations (`DELIB-202665137/127/123`) but nothing matching the cited id or a 2026-07-01 date-id.
Impact: Low. The referenced concept (envelope-sharding closure/reuse) is real and redundantly corroborated by the valid citations `DELIB-202665119` and `DELIB-202665127` plus the WI-4947 collective-retirement record, so no authority is misrepresented; the id itself is fabricated/incorrect. It sits in the context section, not the authority-bearing Owner Decisions section.
Recommended action: In the implementation report, correct the id to the actual sharding-closure deliberation or drop the citation. LO will confirm the correction at VERIFIED time.

### F2 - P3 (structural/observational): Prime deliverable routed to the LO insight dropbox
Claim: The generated report target `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-*.md` writes into the conventional Loyal Opposition insight dropbox.
Evidence: `codex-knowledge-base-index.md` defines `CODEX-INSIGHT-DROPBOX/` as the "active report dropbox" for LO insight reports; this is a Prime Builder implementation deliverable.
Impact: Minimal. The path is in-root, allow-listed, and the report is regenerable evidence (not canonical state). Acceptable as-is because Codex owns that output directory and the filename prefix is distinct.
Recommended action: No change required for this slice. If the compactness-report pattern recurs across Phase 3, consider a dedicated audit-output home to keep the LO-insight channel unconflated.

### F3 - advisory (implementation guidance): classify WI-4947's completed surfaces as covered, not gaps
Claim: The audit's duplicate-coverage detection must reflect that WI-4947 shipped compact query modes for bridge scan/status raw JSON, advisory-router skipped payloads, DA harvest/wrap scan counts, session-envelope/transcript inventories, project/backlog/spec search consistency, and generated/runtime cache exclusions.
Evidence: WI-4947 description (target surfaces) + `resolution: retired` via collective retirement on completion.
Impact: If the registry's expected-default classifications omit WI-4947's completed coverage, the audit would false-positive those surfaces as gaps, undermining the "link don't duplicate" acceptance criterion.
Recommended action: Seed the SoT-class registry so those surfaces are classified as covered-with-compact-route linking WI-4947 / DELIB-202665119, reserving gap status for surfaces genuinely lacking a compact route.

## Applicability Preflight

- packet_hash: `sha256:32e8a4c94741f612ec1a926edc37907097f4c6e8a42a759f01ce4f19ff3e8ddb`
- bridge_document_name: `gtkb-wi4966-cli-compactness-sot-size-controls`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md`
- operative_file: `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-wi4966-cli-compactness-sot-size-controls`
- Operative file: `bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prime Builder Implementation Context

- Objective: Deliver the read-only SoT compactness audit helper + tests + generated report per the Proposed Scope, staying within WI-4966 target paths.
- Preconditions: Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4966-cli-compactness-sot-size-controls` after this GO to mint the implementation-start packet (pre-GO `validate` intentionally returns authorized:false until the packet exists).
- File touchpoints: `scripts/sot_compactness_audit.py`, `platform_tests/scripts/test_sot_compactness_audit.py`, `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-*.md`.
- Verification expectations for the implementation report: (1) map each linked spec to an executed test with exact command output; (2) run `ruff check` AND `ruff format --check` on the changed `.py` files (separate gates); (3) address F1 (citation), reflect F3 (WI-4947 coverage) in the registry.
- Open decisions: None blocking. F1-F3 are Prime-actionable without owner input.

## Recommended Commit Type (for eventual implementation)
`feat` (net-new module + tests), consistent with the proposal.
