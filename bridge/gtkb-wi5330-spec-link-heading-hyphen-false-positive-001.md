NEW

# WI-5330: Fix SPEC_LINK_HEADING_RE false-positive on bare-hyphen compound headings like "Specification-Derived Verification Plan"

bridge_kind: prime_proposal
Document: gtkb-wi5330-spec-link-heading-hyphen-false-positive
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive session; session-stated Prime Builder role via literal ::init gtkb pb opening message; explanatory output style

Work Item: WI-5330

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Author Role-Provenance Disclosure (read before review)

This session's `.claude/session/envelope.json` currently resolves `role_resolved: "loyal-opposition"` via `worker_role_provenance.role_resolution_source: "session_resolver_fallback"`, DESPITE this session's literal opening message being the canonical init keyword `::init gtkb pb` (Prime Builder). This is a live, confirmed instance of the exact defect WI-5328 describes: the session-stated role never gets written back into the envelope, so downstream consumers -- including this very claim (`bridge_claim_cli.py claim` recorded `acting_role: "loyal-opposition"` for this filing) -- silently fall back to the durable dispatcher/registry role instead of the actual session-stated Prime Builder role.

The owner has explicitly and repeatedly confirmed in this session's transcript that the session-stated `::init gtkb pb` directive is authoritative over dispatcher/registry configuration, and has explicitly directed proceeding with filing despite this known provenance inconsistency. Reviewers should treat `author_identity: prime-builder/claude` above as the OWNER-CONFIRMED-AUTHORITATIVE role for this proposal, and the `loyal-opposition`-tagged claim/envelope metadata as evidence of the WI-5328 defect this proposal's sibling documents, not as a genuine self-review or role violation.

## Summary

`scripts/bridge_applicability_preflight.py`'s `SPEC_LINK_HEADING_RE` false-positives on any heading that starts with the literal word "Specification" immediately followed by a bare hyphen and another word -- e.g. `## Specification-Derived Verification Plan` -- silently misdirecting `extract_spec_links()` to harvest spec IDs from the wrong section (or none), rather than the actual `## Specification Links` section elsewhere in the same document. This was discovered and worked around by renaming the colliding heading while pre-filing `bridge/gtkb-wi5320-dispatcher-work-intent-batch-abort-fix-001.md` (2026-07-16).

## Root Cause

WI-4542 (VERIFIED, `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` through `-004.md`) correctly widened `SPEC_LINK_HEADING_RE` to tolerate trailing qualifiers on legitimate `Specification Links` headings, using a separator-gated character class covering parenthesis, colon, en-dash, em-dash, or bare hyphen. The bare hyphen has no whitespace requirement around it, so it also matches compound-word headings that merely start with "Specification-" and have nothing to do with the canonical Specification Links section.

## Proposed Fix

Require the hyphen-as-separator form to be bounded by whitespace on at least one side, while leaving the parenthesis/colon/en-dash/em-dash branches exactly as WI-4542 left them. Add regression tests for: (a) the legitimate WI-4542 case keeps passing, (b) the new WI-5330 case ("Specification-Derived Verification Plan" heading elsewhere in a document) is no longer misidentified as the Specification Links section, (c) whitespace-hyphen qualifiers like "Specification Links - carried forward" still match.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` through `-004.md` (VERIFIED) -- the originating fix this proposal narrows a side effect of.
- `gt deliberations search "spec link heading regex"` (run 2026-07-16) returned no directly on-point prior deliberation beyond the WI-4542 thread itself.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Requirement Sufficiency

Existing requirements sufficient. This is a narrow correctness fix to WI-4542's already-documented intent, not a new requirement.

## Owner Decisions / Input

Owner explicitly directed, via AskUserQuestion in this session's transcript, to "resume filing anyway, flag the role mismatch in the proposals" after being shown the write-probe-succeeded-but-role-still-misresolved finding. This proposal's Author Role-Provenance Disclosure section above is the resulting flag.

## Risk / Rollback

Low risk: one regex definition in one script plus its regression tests. No KB mutation. Revert the single regex literal to the WI-4542 form to roll back.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.