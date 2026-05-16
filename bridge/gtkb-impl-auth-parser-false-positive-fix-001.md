NEW

# Implementation Proposal - implementation_authorization.py Parser False-Positive Fix (WI-3333)

bridge_kind: implementation_proposal
Document: gtkb-impl-auth-parser-false-positive-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S354

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3333

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Summary

The implementation-start authorization gate `scripts/implementation_authorization.py`
has two parser false-positives that reject legitimately Codex-GO'd bridge
proposals at `begin`. This proposal corrects both. The gate stays equally
strict against genuine defects; it stops false-rejecting correctly-formed
proposals.

Bug 1 - `extract_target_paths()`: the function recognizes an inline
`target_paths` JSON metadata line and a `## Files Expected To Change`
section, but NOT the `## target_paths` heading-plus-backtick-bullet section
that roughly 17 proposal files actually use. Those proposals fail `begin`
with "Approved proposal is missing concrete target_paths or Files Expected
To Change".

Bug 2 - `extract_spec_links()` / `PLACEHOLDER_RE`: the placeholder check
runs `PLACEHOLDER_RE.search()` over the entire `## Specification Links`
body, so a bullet that cites a real specification but uses an ordinary
English word such as "pending" in its prose description false-fails with
"Approved proposal has placeholder text in Specification Links". This was
observed on a GO'd thread whose subject area is the cached owner-decision
section.

Neither bug is exercised by the applicability or clause preflights, so both
escaped Codex GO-time review on every affected thread.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`:
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_implementation_authorization.py`. No
`applications/` paths; no paths outside `E:\GT-KB`.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the file-bridge authority; the implementation-start authorization gate is bridge-protocol infrastructure and this fix keeps its scoping contract intact.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the constraint the gate mechanizes for the target_paths metadata and the Specification Links section; the fix aligns the mechanization with the rule's intent.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping below; each behavior maps to a named test.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - both target paths are in-root.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the authorization gate is a governed tooling artifact; this corrects its behavior.
- GOV-STANDING-BACKLOG-001 - WI-3333 is tracked in the standing backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- `.claude/rules/file-bridge-protocol.md` section "Mandatory Implementation-Start Authorization Metadata" - the rule defining the target_paths metadata requirement the gate parses.
- `.claude/rules/codex-review-gate.md` section "Mechanical Implementation-Start Gate" - the rule describing the authorization packet the gate produces.

## Prior Deliberations

- DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT - the direct precedent: the same gate, the same defect class (a mechanization narrower than the rule's intent). The verified thread `gtkb-impl-auth-verification-heading-gate-alignment` corrected the verification-plan heading whitelist and refactored `section_body()` to delegate to a `_iter_sections()` helper. This proposal reuses that `_iter_sections()`-backed `section_body()` helper for the new `## target_paths` heading recognition rather than adding a parallel parser. No overlap: that thread did not touch `extract_target_paths`, `extract_spec_links`, `TARGET_PATHS_RE`, or `PLACEHOLDER_RE`.
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION - reinforces DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 as the governing enforcement specs.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - frames recurring authorization-gate friction as a defect worth a deterministic service-side fix.
- Sibling impl-gate threads `gtkb-impl-gate-friction-hygiene` (latest NO-GO) and `gtkb-implementation-gate-friction-hygiene` (latest NO-GO) are acknowledged for non-duplication: both target `scripts/implementation_start_gate.py` (the downstream Write-time gate), not `scripts/implementation_authorization.py`, and neither proposes changes to `extract_target_paths` or `PLACEHOLDER_RE`. This proposal does not duplicate or supersede them.
- A `search_deliberations` scan found no prior deliberation addressing the `## target_paths` heading recognition gap or the whole-body placeholder scan.

## Owner Decisions / Input

- 2026-05-15 UTC, S354: owner answered an AskUserQuestion choosing "Fix the authorization gate" when presented the systemic gate-blocker (the two parser false-positives blocking the GO bridge backlog). That AskUserQuestion answer authorizes this proposal.
- 2026-05-15 UTC, S354: owner directive to proceed with implementing approved (GO) bridge proposals and work independently. This proposal is the unblocking prerequisite for that directive.
- This work is filed through the reliability fast-lane: WI-3333 is a member of PROJECT-GTKB-RELIABILITY-FIXES, covered by the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (active, no expiry; allowed mutation classes include `source` and `test_addition`). No per-fix deliberation or new project authorization is created.

## Requirement Sufficiency

Existing requirements sufficient. The target_paths metadata requirement
(`.claude/rules/file-bridge-protocol.md`) and the Specification Links
requirement (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001) are
unchanged. This proposal corrects the gate's mechanization to match those
existing requirements; it does not create or revise a requirement.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. This proposal covers one work item (WI-3333), a member
of PROJECT-GTKB-RELIABILITY-FIXES per the standing authorization. The change
is a two-function source correction plus its regression tests; it performs
no inventory sweep, no batch promotion, and no multi-item standing-backlog
mutation. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is not
triggered.

## Proposed Scope

### IP-1: Recognize the `## target_paths` heading form in `extract_target_paths`

In `scripts/implementation_authorization.py`, `extract_target_paths()` keeps
its current precedence: the inline `target_paths` JSON metadata line is tried
first, then a section fallback. The section fallback is extended:

- `## Files Expected To Change` keeps its established extraction unchanged
  (every backtick span on each bullet line). No regression to that format.
- When `## Files Expected To Change` is absent, the function also reads a
  `## target_paths` heading section via the existing `section_body()` helper
  (the `_iter_sections()`-backed helper from DELIB-S352). Proposals using the
  `## target_paths` heading place the path first in backticks and may add
  parenthetical annotations in additional backtick spans, so this branch
  takes only the FIRST backtick span per bullet line as the path. The
  asymmetry is deliberate and documented in-code: each section name keeps the
  extraction matched to its observed real-world convention.

No change to `TARGET_PATHS_RE` or the inline-JSON branch. The
"missing concrete target_paths" error is still raised when none of the three
forms is present.

### IP-2: Make the Specification Links placeholder check per-bullet

In `extract_spec_links()`, replace the whole-body `PLACEHOLDER_RE.search(body)`
with a per-bullet scan. A new helper `_bullet_has_citation(text)` returns True
when a bullet carries a concrete citation: a backtick-quoted token, or an
uppercase identifier token (matching a `GOV-`/`SPEC-`/`ADR-`/`DCL-`/`DELIB-`
style ID via a regex such as `\b[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9-]*\b`). A
bullet with a concrete citation is a real specification link; ordinary words
in its prose description are not flagged. A bullet with NO concrete citation
that matches `PLACEHOLDER_RE` is a genuine placeholder bullet and still raises
"Approved proposal has placeholder text in Specification Links".

`PLACEHOLDER_RE` itself is unchanged - a bullet that is only a placeholder
token (for example a lone `- TBD` bullet) is still rejected. The fix narrows
WHERE the check applies (placeholder-only bullets), not WHAT it rejects.

### IP-3: Regression tests

Add 12 tests to `platform_tests/scripts/test_implementation_authorization.py`
(the single canonical test file; it uses an importlib-loaded `auth_module`
fixture and synthetic-artifact helpers under `tmp_path`). New tests construct
the `## target_paths` heading form explicitly, since the existing
`_write_proposal` helper emits the inline form.

| ID | Test name | Behavior |
|----|-----------|----------|
| T1 | test_extract_target_paths_accepts_target_paths_heading | `## target_paths` heading, one backtick path per bullet -> paths extracted |
| T2 | test_extract_target_paths_target_paths_heading_first_span_only | `## target_paths` bullets with path + parenthetical backtick annotation -> only the path (first span) extracted |
| T3 | test_extract_target_paths_inline_json_unchanged | inline JSON metadata line -> unchanged behavior (regression) |
| T4 | test_extract_target_paths_files_expected_to_change_unchanged | `## Files Expected To Change`, multi-span bullet -> all spans (regression) |
| T5 | test_extract_target_paths_raises_when_all_forms_absent | none of the three forms -> AuthorizationError still raised |
| T6 | test_extract_target_paths_inline_json_precedence | proposal has both inline JSON and `## target_paths` heading -> inline JSON wins |
| T7 | test_extract_spec_links_substantive_word_in_cited_bullet_not_flagged | bullet citing a backticked spec whose prose contains a placeholder-shaped word -> no raise |
| T8 | test_extract_spec_links_placeholder_only_bullet_still_flagged | lone placeholder-token bullet (no citation) -> raises |
| T9 | test_extract_spec_links_bare_placeholder_word_bullet_still_flagged | bullet that is a bare placeholder word -> raises |
| T10 | test_extract_spec_links_id_token_bullet_with_placeholder_word_not_flagged | bullet citing a bare uppercase ID token (no backticks) + placeholder-shaped word in prose -> no raise |
| T11 | test_extract_spec_links_normal_section_returns_links | normal section, all real citations -> links returned (regression) |
| T12 | test_create_authorization_packet_accepts_target_paths_heading_proposal | end-to-end: a synthetic GO'd proposal using the `## target_paths` heading -> packet created, target_path_globs correct |

## Specification-Derived Verification Plan

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | T1-T6 (target_paths recognition), T7-T11 (spec-links placeholder precision) | 11 PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this table is the spec-to-test mapping; each behavior maps to a named test | 12 tests cover 12 distinct behaviors |
| GOV-FILE-BRIDGE-AUTHORITY-001 | T12 end-to-end packet creation through the gate | 1 PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | both target paths in-root | confirmed in In-Root Placement Evidence |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | `bridge/INDEX.md` updated to insert this NEW entry at the top of the thread version list; no deletion or rewrite | confirmed at filing time |

Commands at implementation time (executed after Codex GO):

1. `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short` - all 12 new tests PASS and the existing suite continues to PASS.
2. `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` - zero new errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix` - `preflight_passed: true`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix` - exit 0; no blocking gaps.
5. Live evidence: after the fix, `python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatch-failures-jsonl-rotation` (a `## target_paths` heading proposal) authorizes successfully where it previously failed.

## Risks and Rollback

- Risk: the `## target_paths` first-span-per-bullet rule mis-extracts if a future proposal places a non-path token first in backticks. Mitigation: the inline JSON form remains the recommended primary metadata form and is tried first; the heading form is a compatibility path for the existing corpus.
- Risk: `_bullet_has_citation` exempts a bullet that has a backtick span but no genuine spec. Mitigation: a bullet with a backtick span is, by the Specification Links convention, citing an artifact; a genuinely empty placeholder bullet has no backtick span and no ID token, so it is still flagged. T8/T9 pin this.
- Risk: the asymmetric extraction (`## Files Expected To Change` all-spans vs `## target_paths` first-span) confuses future maintainers. Mitigation: an in-code comment documents the rationale; T2 and T4 pin both behaviors.
- Rollback: revert the `extract_target_paths` section-fallback extension, restore the whole-body `PLACEHOLDER_RE.search`, remove `_bullet_has_citation`, and remove the 12 tests.

## Recommended Commit Type

`fix` - corrects two false-positive defects in an existing gate. Two-function
source change plus 12 regression tests; no new capability surface, no spec
promotion, no behavior change for genuine defects.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
