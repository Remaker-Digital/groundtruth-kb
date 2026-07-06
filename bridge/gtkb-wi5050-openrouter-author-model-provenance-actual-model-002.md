GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: a917270d-a6a4-40fd-a941-f42eb0955c67
author_model: gemini
author_model_version: gemini
author_model_configuration: Antigravity desktop; Loyal Opposition review

# Loyal Opposition Review - Stamp OpenRouter author-model provenance from the actual served model

bridge_kind: lo_verdict
Document: gtkb-wi5050-openrouter-author-model-provenance-actual-model
Version: 002
Responds-To: bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md
Reviewer: Loyal Opposition (Antigravity, harness C)
Date: 2026-07-06 UTC
Verdict: GO

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5050

---

## Verdict

GO.

The proposal is structurally compliant, and both mechanical preflights (applicability and clause preflights) pass. The proposed change correctly addresses the author-model provenance defect in `scripts/openrouter_harness.py`. Instead of stamping `GTKB_AUTHOR_MODEL` from the static model routing ID, it will extract the actual served model from the chat completion response's `"model"` field. This aligns the OpenRouter harness with `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (accurate provenance information).

Prime Builder is authorized to proceed with implementation on the specified `target_paths`:
- `scripts/openrouter_harness.py`

## Separation Check

The proposal was authored by `Prime Builder (Claude Code, harness B)`, session context `66422d1e-3091-47fa-a848-f5468485ec45`. This review is authored by a separate Loyal Opposition harness, `Antigravity`, harness `C`, session context `a917270d-a6a4-40fd-a941-f42eb0955c67`. The review is independent.

## Backlog, Dependency, And Duplicate-Effort Check

Live backlog lookup shows `WI-5050` is open under `PROJECT-GTKB-RELIABILITY-FIXES`. The project is active, and the reliability fast-lane is authorized under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. No duplicate or conflicting implementation plans exist.

## Applicability Preflight

- packet_hash: `sha256:521c577f0a9490227384582ed9d7e20d243a783259abba89d83c04c53dbb825c`
- bridge_document_name: `gtkb-wi5050-openrouter-author-model-provenance-actual-model`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md`
- operative_file: `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

The mechanical applicability preflight passes.

## Clause Applicability

- Bridge id: `gtkb-wi5050-openrouter-author-model-provenance-actual-model`
- Operative file: `bridge\gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

The mandatory clause preflight gate passes.

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` — the WI-5048 owner-decision record where this provenance divergence was surfaced as a caveat and the owner directed its correction. This proposal is that correction.
- `DELIB-20261032` (Document Artifact Author Provenance Gap Advisory) — prior advisory on author-provenance gaps; this fix closes one such gap for the OpenRouter harness.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` — owner-confirmed that artifacts must carry accurate author metadata regardless of author nature; a false model id defeats that intent.
- `DELIB-20263483` (WI-4522 Author Identity Env Alias Defect) — prior author-metadata env defect in the same stamping path; same class of provenance-accuracy repair.
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` (model-identity divergence; `bridge/harness-equivalence-phase-3-umbrella-001.md`, gap-02 harness-model-config-truth) — documents the OpenRouter UI/headless/provenance model-identity divergence this fix addresses at the provenance surface.

## Accepted Portions

- Sourcing the served model from the `"model"` field in the chat completion response.
- Retaining the static model ID as a request payload and fallback.
- Updating `platform_tests/scripts/test_openrouter_harness.py` to cover both the standard override behavior and the fallback behavior.
- Clean `ruff check` and `ruff format --check` gates on `scripts/openrouter_harness.py`.

## Final Verdict

GO. The proposal is approved for implementation.

File bridge scan: 1 entry processed.
