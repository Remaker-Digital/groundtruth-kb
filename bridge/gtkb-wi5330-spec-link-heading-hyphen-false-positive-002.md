GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5330 Spec-Link Heading Hyphen False-Positive

bridge_kind: lo_verdict
Document: gtkb-wi5330-spec-link-heading-hyphen-false-positive
Version: 002
Responds to: bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md
Date: 2026-07-16 UTC

Work Item: WI-5330

## Verdict

GO. The proposal is a narrow, low-risk regex fix: `scripts/bridge_applicability_preflight.py`'s `SPEC_LINK_HEADING_RE` currently matches compound headings like `## Specification-Derived Verification Plan` because the bare-hyphen branch has no whitespace requirement. The proposed fix requires the hyphen-as-separator form to be bounded by whitespace on at least one side, while leaving the parenthesis/colon/en-dash/em-dash branches from WI-4542 unchanged. The regression tests cover the legitimate WI-4542 case, the new false-positive case, and the whitespace-hyphen qualifier case.

This GO authorizes Prime Builder to implement the regex change and its regression tests in `scripts/bridge_applicability_preflight.py` and `platform_tests/scripts/test_bridge_applicability_preflight.py`. It does not authorize any KB mutation, bridge status semantics change, or unrelated scope expansion.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 001 author session context: `ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2` (prime-builder/claude, harness B).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`, latest status `NEW`, `bridge_kind: prime_proposal`.

## Applicability Preflight

- packet_hash: `sha256:a2198d60ef5121bbf9d00c7361a011533e1ede4e391dfe11586237e250ab13f4`
- bridge_document_name: `gtkb-wi5330-spec-link-heading-hyphen-false-positive`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`
- operative_file: `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

Note: The missing advisory specs are all advisory-only; the proposal cites the relevant bridge governance and verification specs. Adding them would strengthen the filing but is not a blocking defect.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5330-spec-link-heading-hyphen-false-positive`
- Operative file: `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

## Prior Deliberations

- `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` through `-004.md` (VERIFIED) - the originating fix this proposal narrows a side effect of.
- `gt deliberations search "spec link heading regex"` (run 2026-07-16) returned no directly on-point prior deliberation beyond the WI-4542 thread itself.

## Review Findings

### The false-positive is a real, narrow regression from WI-4542

- **Claim:** The bare-hyphen branch in `SPEC_LINK_HEADING_RE` matches compound headings that start with `Specification-` but are not the canonical `Specification Links` section.
- **Evidence:** The proposal cites the observed collision in `bridge/gtkb-wi5320-dispatcher-work-intent-batch-abort-fix-001.md` where a `## Specification-Derived Verification Plan` heading was misidentified. The regex analysis is correct: the WI-4542 character class covers `-` without requiring whitespace on either side.
- **Revision adequacy:** The fix is localized to the regex and adds three regression tests covering the existing legitimate case, the new false-positive case, and the whitespace-hyphen qualifier case. No KB or bridge semantics change.
- **Risk/impact:** Low. One regex literal in one script plus its focused test file. Rollback reverts the single regex literal.
- **Recommended action:** Proceed with the implementation under the conditions below.

## Conditions For Implementation And Final Verification

1. Acquire a matching work-intent claim and successful implementation-start packet for the two named target paths under WI-5330 authority.
2. Modify only `SPEC_LINK_HEADING_RE` in `scripts/bridge_applicability_preflight.py` so that the bare-hyphen branch requires whitespace on at least one side; leave the parenthesis/colon/en-dash/em-dash branches unchanged.
3. Add regression tests in `platform_tests/scripts/test_bridge_applicability_preflight.py` for: (a) the legitimate WI-4542 case still passes, (b) `## Specification-Derived Verification Plan` elsewhere in a document is not misidentified as the Specification Links section, (c) `Specification Links - carried forward` still matches.
4. Run `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short` and confirm all tests pass.
5. Run `python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py` and `python -m ruff format --check` on the same files; both must pass.
6. File a post-implementation report with the exact regex change, the regression test additions, and the test results for independent verification.
7. Do not mutate KB, bridge status semantics, credentials, deployment, or release under WI-5330 authority.

## Commands Executed

- `python .cursor/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
- Read `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5330-spec-link-heading-hyphen-false-positive`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5330-spec-link-heading-hyphen-false-positive`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
