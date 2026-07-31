NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: A-2026-07-24T21-07-11Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; transcript-resolved loyal-opposition; build review profile

bridge_kind: lo_verdict
Document: gtkb-wi5670-resolver-legacy-provenance-tolerance
Version: 002
Responds to: bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-001.md
Date: 2026-07-24 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670
target_paths: []

# Loyal Opposition Review â€” WI-5670 resolver legacy-provenance tolerance

## Verdict

NO-GO. The legacy-tolerance design is sound, but both declared target files are already dirty with unrelated lifecycle hunks while WI-5670 remains latest `NEW`. The proposal has no foreign-hunk ownership or isolation plan, so GO could absorb unrelated work into the eventual source/test commit.

## Review Independence and Evidence

- Reviewer session `A-2026-07-24T21-07-11Z` (Codex A, transcript-resolved Loyal Opposition) differs from proposal author session `302c4543-bd90-4fe9-b169-e90390e528b1` (Claude B Prime Builder).
- Read the complete WI-5670 chain (only `001 NEW`), `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, WI-5670/PAUTH state, relevant WI-5152 versions, resolver source, and its focused tests.
- `resolve_bridge_lifecycle(..., "gtkb-wi5152-modernization-hard-invariant-registry")` currently fails `MISSING_BRIDGE_METADATA` on `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md`; that historic NO-GO has valid Document/Version fields but no `author_identity`, so the substantive defect is reproduced.
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: 46 passed. Ruff check and format check passed.

## Blocking Finding

### F1 â€” P1 â€” Pre-GO foreign changes occupy both WI-5670 target files

**Observation.** `git diff -- scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py` shows a 19/3 source hunk enabling post-GO `NEW -> REVISED` and a 39-line test hunk covering deferred-report handling. Neither hunk is the proposalâ€™s legacy-`author_identity` classification/revalidation change.

**Impact.** The proposal lists those same two files but neither declares the foreign changes, their owner, nor an exact hunk-isolated commit method. A GO would permit a later commit to misattribute those bytes to WI-5670.

**Required revision.** Preserve the foreign hunks without reverting or staging them. Resolve them through their owning governed thread/commit, then refile from a clean baseline. If that is not possible, the revision must name their owner and include an exact reviewed hunk-isolation and verification plan proving only the WI-5670 change is staged.

## Positive Confirmation

`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` is explicitly forward-only. The proposalâ€™s plan to tolerate only non-operative legacy versions while retaining role-correct operative proposal/GO checks, plus `scripts/implementation_authorization.py::_go_self_review_error`, is an appropriate eventual remediation once scope hygiene is restored.

## Applicability Preflight

- packet_hash: `sha256:b61c77a725c3d9003bd91a1078a605eb149ce48b57e01b590b2a5c52c2218636`
- bridge_document_name: `gtkb-wi5670-resolver-legacy-provenance-tolerance`
- content_file: `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-001.md`
- operative_file: `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []
- candidate_evidence_hash: `sha256:4f08bba186c4547b28997ca5e7c2ea6b5e3be30dc1ca19e545b17bcf36f766f9`

## Clause Applicability

- Operative file: `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-001.md`
- Mandatory clause preflight: 5 clauses; 3 must-apply; 0 evidence gaps; 0 blocking gaps; exit 0.

## Prior Deliberations

- `DELIB-20261032` â€” author-provenance gap advisory.
- `DELIB-20260683` â€” author-provenance contract review.
- `DELIB-20260666` â€” bounded PAUTH-scope decision.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` â€” concrete legacy failure.

## Owner Decisions / Input

No owner action is required. A revised, scope-clean proposal may proceed through the normal independent review path.

Skills applied: gtkb-bridge, gtkb-proposal-review
