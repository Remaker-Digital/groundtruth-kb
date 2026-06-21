NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - impl-auth begin target_paths parser: exact-heading match misses annotated headings + slurps ### subsections

bridge_kind: prime_proposal
Document: gtkb-impl-auth-target-paths-parser-annotated-headings
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3499

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

`extract_target_paths()` in `scripts/implementation_authorization.py` resolves the `## target_paths` heading form through `section_body(markdown, "target_paths")`, which matches headings by exact case-insensitive equality (`found_heading.lower() == heading.lower()`). An annotated heading such as `## target_paths (live re-probe; per S376)` is therefore not found, `section_body` returns `""`, and `begin` fails with `"Approved proposal is missing concrete target_paths or Files Expected To Change"` even though the section is present and well-formed. This blocks `implementation_authorization.py begin` on otherwise-GO'd proposals and forces an out-of-band workaround (adding a machine-readable `target_paths:` JSON line by hand).

## Defect / Reproduction

Origin incident (S376): `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-019.md` records verbatim that "`scripts/implementation_authorization.py begin` cannot parse `-017`'s annotated `## target_paths (...)` heading, so no implementation-start packet can be created", which forced Prime Builder to file a REVISED version adding a machine-readable `target_paths:` JSON line as the workaround.

Live reproduction (read-only probe, 2026-06-21, against the current source):

- Defect 1 (annotated heading) — CONFIRMED PRESENT. Input `## target_paths (live re-probe; per S376)` followed by backtick-path bullets: `section_body(md, "target_paths")` returns `''` and `extract_target_paths(md)` raises `AuthorizationError: Approved proposal is missing concrete target_paths or Files Expected To Change`.
- Defect 2 (`###` subsection slurp) — NO LONGER REPRODUCES. The WI text predates HYG-046 (FAB-14), which changed `SECTION_RE` from `^## ` to `^#{2,3}\s+`. With `#{2,3}`, `_iter_sections` now terminates the `## target_paths` body at the following `### Intentionally preserved` heading, so the subsection bullets (`bridge/**`, `archive/**`) are NOT slurped: `extract_target_paths(md)` correctly returns only the parent-section path `['scripts/a.py']`. The slurp defect described in the WI was incidentally closed by the HYG-046 regex widening; this proposal adds a regression guard so it stays closed.

The root cause of the live defect is the exact-equality heading match in `section_body`. `section_body` is shared by four consumers (`Specification Links`, `Files Expected To Change`, `Requirement Sufficiency`, and the `target_paths` heading form), and `test_section_body_exact_match_preserved` pins its exact-match semantics; the fix therefore must add annotated-heading tolerance for the `target_paths` heading form specifically, in `extract_target_paths`, without weakening `section_body`'s exact-match contract for the other consumers.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the implementation-start authorization packet derives from bridge `GO` state; a parser defect that prevents `begin` from minting a packet from a valid GO'd proposal directly degrades the bridge's authority chain, so the fix restores correct GO-to-packet resolution.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix keeps the durable proposal artifact parseable by the authorization tooling so an annotated-but-valid `## target_paths` section remains an actionable governance artifact rather than requiring an out-of-band edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing spec (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from the cited spec clauses (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory project linkage).
- `SPEC-AUQ-POLICY-ENGINE-001` - the change touches no owner-decision policy surface and adds no AUQ-gated behavior; relevance is the negative assertion that owner-decision routing is unaffected by this parser-only fix.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform tooling (`scripts/...`) and platform tests; no application-placement boundary is crossed and no adopter/application surface is touched.
- `GOV-STANDING-BACKLOG-001` - WI-3499 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the change is a pure parser fix to a Python helper invoked identically from both harnesses; relevance is the negative assertion that no harness-specific hook/parity surface is added or altered.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - authorization remains artifact-backed (the GO'd proposal file) rather than inferred; the fix preserves that by parsing the artifact's `target_paths` section robustly.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching this previously-defective parser brings the annotated-heading behavior under explicit, tested control per specify-on-contact.

## Prior Deliberations

- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3499 is in scope.
- _No prior deliberations on this specific parser surface: the originating evidence is the S376 incident recorded in `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-019.md` (the workaround that motivated WI-3499), not a prior Deliberation Archive review of `extract_target_paths`. The seeded DA candidates (`DELIB-2748`, `DELIB-20263969`, `DELIB-2442`, `DELIB-20263935`, `DELIB-20263919`) are unrelated (DA-enforcement and skill-loading threads) and are pruned._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing reliability fast-lane authorization, via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3499 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, and is bounded to one source file plus one test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work-item batch; WI-3499 (P2 defect) is in that batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that establishes PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING as the authorization envelope for small reliability defect fixes such as this one.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes that the implementation-start authorization must derive from valid bridge `GO` state; this fix simply makes the `target_paths` parser correctly recognize an annotated-but-valid heading so a GO'd proposal yields a packet as the existing contract intends. No new or revised requirement/specification is introduced; the canonical `target_paths: [JSON]` line and the `## target_paths` heading form both remain supported.

## Proposed Scope

1. In `scripts/implementation_authorization.py`, add annotated-heading tolerance for the `target_paths` heading form inside `extract_target_paths()`, without changing `section_body`'s exact-match semantics (preserved for `Specification Links`, `Files Expected To Change`, and `Requirement Sufficiency`, and pinned by `test_section_body_exact_match_preserved`).
   - Introduce a small private helper `_target_paths_heading_body(markdown) -> str` that scans sections via the existing level-aware `_iter_section_spans()` and returns the body of the first section whose heading equals `target_paths` OR begins with `target_paths` followed by a word boundary (whitespace, `(`, `:`, or end), case-insensitive. Using `_iter_section_spans()` terminates the returned body at the next heading of equal-or-shallower level, so any nested `### ` subsection (e.g. `### Intentionally preserved`) is excluded from the parent body by construction — making the subsection-isolation behavior explicit and robust rather than incidental to the current `SECTION_RE` width.
   - Replace the `heading_body = section_body(markdown, "target_paths")` call in `extract_target_paths()` with `heading_body = _target_paths_heading_body(markdown)`. The downstream per-bullet "first backtick span is the path" extraction is unchanged.
   - Keep extraction precedence unchanged: inline `target_paths:` JSON first, then `## Files Expected To Change`, then the `## target_paths` heading form. The matcher is anchored to the canonical word `target_paths` at the start of the heading so an unrelated heading is never matched.
2. Add regression tests in `platform_tests/scripts/test_implementation_authorization.py` (see verification plan): one for the annotated-heading match (Defect 1), one asserting a nested `###` subsection under `## target_paths` is not slurped (Defect 2 guard), and one asserting the `section_body` exact-match contract for the other consumers is unchanged.

The WI's alternative remediation framings ("prefix/startswith heading match for the canonical name" and "terminate section body at next heading of any level") are both realized by the single `_target_paths_heading_body` helper above. Documenting `target_paths: [JSON]` as the sole canonical form (the WI's third candidate) is a behavior/contract change that would deprecate the heading form and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (GO'd proposal must yield an authorization packet) | `test_extract_target_paths_accepts_annotated_target_paths_heading` | `extract_target_paths("## target_paths (live re-probe; per S376)\n\n- \`scripts/a.py\`\n- \`tests/b.py\`\n")` returns `["scripts/a.py", "tests/b.py"]` (previously raised `missing concrete target_paths`). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (subsection isolation under the touched parser) | `test_extract_target_paths_annotated_heading_excludes_nested_subsection` | A `## target_paths` (annotated or plain) body containing a nested `### Intentionally preserved` subsection with `bridge/**`/`archive/**` bullets yields only the parent-section path(s); the subsection bullets are excluded. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no regression for the canonical/plain forms) | `test_extract_target_paths_plain_heading_and_inline_json_unchanged` | The plain `## target_paths` heading form and the inline `target_paths:` JSON form both still return their paths and JSON precedence is preserved (no regression vs existing T1/T3/T6). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (section_body exact-match contract preserved for other consumers) | `test_section_body_exact_match_preserved` (existing, re-run) | `section_body` still returns `""` for `"Test Plan (spec-to-test mapping)"` and matches only exact (case-insensitive, first-match) headings for the non-`target_paths` consumers. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short`
- `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py`
- `python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py`

## Acceptance Criteria

1. `extract_target_paths()` resolves an annotated `## target_paths (...)` heading and returns the section's backtick paths (Defect 1 fixed); `begin` no longer fails `missing concrete target_paths` on such a proposal.
2. A nested `### ` subsection under a `## target_paths` heading is not slurped into the extracted path list (Defect 2 guard holds), for both annotated and plain headings.
3. `section_body`'s exact-match semantics are unchanged for `Specification Links`, `Files Expected To Change`, and `Requirement Sufficiency`; `test_section_body_exact_match_preserved` and all existing `extract_target_paths` tests (T1–T6) still pass.
4. The new and existing tests pass; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: the annotated-heading matcher could over-match an unrelated heading that merely begins with the word "target". Mitigation: the matcher requires the heading to equal `target_paths` or start with `target_paths` followed by a word boundary (whitespace / `(` / `:` / end), so `## target_paths_notes` or `## targeting` are not matched.
- Risk: switching the `target_paths` heading lookup from `section_body` (`_iter_sections`) to `_iter_section_spans` could change body boundaries in an edge case. Mitigation: `_iter_section_spans` already terminates at the next equal-or-shallower heading; the dedicated guard test asserts subsection exclusion, and the plain-heading regression test asserts no change to existing extraction. `section_body` itself is untouched, so its other consumers are unaffected.
- Risk: the inline `target_paths:` JSON precedence path must remain dominant. Mitigation: precedence ordering in `extract_target_paths` is unchanged; the existing precedence test (T6) is retained.
- Rollback: revert the `extract_target_paths` change and remove `_target_paths_heading_body` plus the new tests in `lifecycle`-adjacent test file; the change is a single helper plus one call-site swap plus tests, fully reversible with no migration and no schema/state impact.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`fix`
