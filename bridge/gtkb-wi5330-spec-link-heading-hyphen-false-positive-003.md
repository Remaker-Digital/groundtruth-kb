REVISED

# WI-5330: Correct Specification-Link Heading Recognition

bridge_kind: prime_proposal
Document: gtkb-wi5330-spec-link-heading-hyphen-false-positive
Version: 003
Responds to: bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive Prime Builder; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-5330-SPEC-LINK-HYPHEN
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5330

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

## Revision Claim

This revision preserves the independently confirmed technical diagnosis and
fix from version 001 while correcting the sole blocking project-linkage
finding in version 002. WI-5330 is now an active member of
`PROJECT-GTKB-RELIABILITY-FIXES`, and the bounded active authorization
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-5330-SPEC-LINK-HYPHEN` covers exactly
WI-5330 with `source` and `test_addition` mutation classes.

No source, test, dispatcher, TAFE, database, Git, deployment, credential, or
formal-artifact mutation is performed by this revision.

## Summary

`SPEC_LINK_HEADING_RE` currently accepts a bare hyphen immediately after the
word `Specification`. Consequently, a heading such as
`Specification-Derived Verification Plan` can be mistaken for the canonical
Specification Links section. Because `extract_spec_links()` stops at the first
matching heading, a real later Specification Links section can be silently
ignored.

After GO, the implementation will require whitespace around the ASCII hyphen
separator while retaining the existing parenthesis, colon, en-dash, and
em-dash qualifier forms. Focused tests will prove both the rejected compound
headings and the retained legitimate qualifier headings.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` through
  `-004.md` established the intended qualifier tolerance that this repair
  narrows without removing.
- `DELIB-20260716-WI5330-PAUTH-DECISION` authorizes the bounded WI-5330 PAUTH
  used by this revision.
- The version-002 Loyal Opposition verdict independently confirmed the regex
  defect and identified project-linkage metadata as the only blocking finding.

## Owner Decisions / Input

Owner decision `DELIB-20260716-WI5330-PAUTH-DECISION` selected a bounded per-WI
authorization for the two declared target paths. The authorization preserves
all ordinary bridge GO, matching claim, implementation-start, independent
verification, and focused-finalization gates. No additional owner decision is
required for this revision.

## Findings Addressed

### F1 (P0, blocking) - Missing mandatory project-linkage metadata

Resolved. This revision carries the required machine-readable `Project
Authorization:`, `Project:`, and `Work Item:` lines. Canonical project state
shows active WI-5330 membership, and canonical project-authorization state
shows the cited bounded PAUTH active with WI-5330 in its included work-item
set.

## Scope And Dirty-Tree Boundary

The target paths remain exactly the two paths reviewed in version 001. Both
currently contain foreign WI-5307/PAUTH-amendment work. Those existing hunks
are quarantined and are not part of WI-5330.

After GO, WI-5330 may add only:

- the minimal `SPEC_LINK_HEADING_RE` change that prevents a no-whitespace
  ASCII hyphen from acting as a qualifier separator; and
- focused regression tests for compound-heading rejection and legitimate
  qualifier preservation.

Implementation and finalization must use an exact WI-5330-only patch or wait
for the foreign target-path ownership to become terminal. Existing imports,
PAUTH-amendment validation, `blocking_errors` behavior, fixture builders, and
their tests are excluded. Broad staging and commingled finalization are
prohibited.

## Requirement Sufficiency

Existing requirements are sufficient. This is a bounded correctness repair to
the already-governed bridge proposal preflight and introduces no new product or
governance requirement.

## Pre-Filing Preflight Subsection

- Applicability command: `python scripts/bridge_applicability_preflight.py --content-file <candidate> --json`
- Applicability result: exit 0; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; packet hash
  `sha256:d49d54f61635de229ae12e669ab958c10dfa354dd418f1442274ccd174f5d5f8`.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --content-file <candidate>`
- Clause result: exit 0; 5 clauses evaluated; 3 `must_apply`; 2
  `may_apply`; 0 evidence gaps; 0 blocking gaps.

## Verification Plan (Spec-Derived)

| Governing requirement | Focused verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File only through the governed revision helper; preserve PB authorship and append-only versioning. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run the live bridge compliance audit and assert the project, PAUTH, and work-item lines are accepted. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability preflight and require no missing blocking or advisory specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Add tests proving `Specification-Derived` and `Specification-Driven` headings are rejected while canonical, parenthetical, colon, Unicode-dash, and whitespace-ASCII-hyphen qualifier forms remain accepted. Run the focused preflight test module and Ruff checks on both targets. |
| Artifact-oriented governance records | Preserve WI-5330, its project membership, bounded PAUTH, bridge chain, test evidence, and independent verdict as the durable lifecycle. |

## Acceptance Criteria

1. Hyphenated compound headings beginning with `Specification-` do not match
   `SPEC_LINK_HEADING_RE` and cannot preempt the true Specification Links
   section.
2. Canonical headings and WI-4542 qualifier forms continue to match.
3. The focused test module passes from an exact WI-5330-only candidate.
4. Ruff check and format verification pass for both declared targets.
5. No foreign dirty hunk enters the WI-5330 patch, report, or focused commit.
6. Independent Loyal Opposition verification is required before completion.

## Risk And Rollback

Risk is limited to making the heading recognizer too strict. The positive
regression matrix protects every intentionally supported form. Rollback is the
single regex hunk plus its focused tests from the exact WI-5330 patch; no
runtime, database, dispatcher, TAFE, credential, deployment, or formal
artifact state is involved.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
