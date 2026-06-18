NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Fix `## Spec-Derived Verification Plan` heading/subheading boundary defect in `scripts/implementation_authorization.py`

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4617

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Summary

WI-4617 (P2 defect, component `scripts`). `has_spec_derived_verification()` in
`scripts/implementation_authorization.py` falsely reports a proposal as
"missing a spec-derived verification plan" when the proposal's
`## Spec-Derived Verification Plan` section places its content under a `### `
subheading. This blocks `implementation_authorization.py begin` (the
implementation-start gate) on otherwise-compliant, Loyal-Opposition-GO'd
proposals.

## Problem (root cause)

`SECTION_RE = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.MULTILINE)` matches both
`## ` (h2) and `### ` (h3) headings. `_iter_sections()` ends each section body
at the *next heading of any level*. So for a proposal written as:

    ## Spec-Derived Verification Plan
    ### Spec-to-test mapping
    <evidence>

`_iter_sections()` yields `("Spec-Derived Verification Plan", "")` — an EMPTY
body, because the `### ` subheading immediately terminates the h2 section.
`has_spec_derived_verification()` then hits `if not body: continue` and skips
the very heading that names the plan, returning `False`. The h3 subheading is
the boundary defect.

This is a false-negative governance-gate failure: the proposal genuinely
carries a spec-derived verification plan, but the begin gate rejects it with
"Approved proposal is missing a spec-derived verification plan".

## Proposed fix (heading-level-aware span; scoped to the verification detector)

Add a heading-level-aware span iterator and use it ONLY in
`has_spec_derived_verification()`, so an h2 section's body spans to the next
heading of the *same or shallower* level (including nested h3 content). Leave
`_iter_sections()` and `section_body()` unchanged so Specification Links,
target_paths, and Requirement Sufficiency parsing keep byte-identical behavior
(zero blast radius outside the verification detector).

New internal helper:

    _SECTION_LEVEL_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)

    def _iter_section_spans(markdown):
        """Yield (level, heading, body) where body extends to the next heading
        of the same or shallower level, so an h2 section includes its h3
        subsections."""
        matches = list(_SECTION_LEVEL_RE.finditer(markdown))
        for index, match in enumerate(matches):
            level = len(match.group(1))
            start = match.end()
            end = len(markdown)
            for later in matches[index + 1:]:
                if len(later.group(1)) <= level:
                    end = later.start()
                    break
            yield level, match.group(2).strip(), markdown[start:end].strip()

`has_spec_derived_verification()` is rewritten to iterate `_iter_section_spans`
instead of `_iter_sections`. The matching logic (verification heading tokens;
"test plan" + `VERIFICATION_TEST_EVIDENCE_RE`) is unchanged. The change is
strictly MORE permissive (a wider span can only turn an additional case True;
it cannot turn an existing True into False), preserving the documented design
intent that the begin-gate detector be at least as permissive as the GO-time
clause-preflight detector for `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the spec-derived
  verification requirement that `has_spec_derived_verification` enforces; the
  defect causes a false-negative against this DCL's begin-gate.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications per the linkage mandate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated implementation and
  verification must honor the file-bridge authority model.
- `GOV-RELIABILITY-FAST-LANE-001` — single-file defect fix with a derived
  regression test (reliability fast-lane class).
- `.claude/rules/file-bridge-protocol.md` § Mandatory Specification-Derived
  Verification Gate — the rule this parser operationalizes.
- `.claude/rules/project-root-boundary.md` — both target paths are in-root
  (`scripts/`, `platform_tests/scripts/`); no out-of-root dependency.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- Deliberation search (`gt deliberations search "spec-derived verification plan
  heading parser implementation_authorization"`) returned no on-topic prior
  decision; the nearest semantic matches (DELIB-20263862, DELIB-2293,
  DELIB-20264423, DELIB-20264666, DELIB-2298) concern unrelated topics (bridge
  VERIFIED backlog retirement, the grill-me-for-clarification skill, an Ollama
  dispatch target-paths amendment, and the projects skill).
- The most relevant prior work is the in-code thread
  `gtkb-impl-auth-verification-heading-gate-alignment`
  (`WI GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT`), which aligned
  `has_spec_derived_verification` heading-token recognition with the GO-time
  clause-preflight detector (tests at
  `platform_tests/scripts/test_implementation_authorization.py:660-703`). This
  proposal extends the same detector to fix the orthogonal h2/h3 boundary
  defect without regressing the heading-token recognition that thread added.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20261896` — seed=search; bridge_thread; Bridge thread: gtkb-impl-auth-verification-heading-gate-alignment (4 versions, V
- DA: `DELIB-2300` — seed=search; bridge_thread; Loyal Opposition Review - Implementation-Start Verification Heading Gate Alignme
- DA: `DELIB-2101` — seed=search; bridge_thread; Bridge thread: gtkb-impl-auth-parser-false-positive-fix (6 versions, VERIFIED)
- DA: `DELIB-20263439` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-15T20:23:02Z
- DA: `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` — seed=search; owner_conversation; Owner decision: authorize impl-start gate verification-heading alignment fix und

## Requirement Sufficiency

Existing requirements are sufficient. The governing requirement
(`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the file-bridge-protocol
Specification-Derived Verification Gate) already mandates that proposals carry a
spec-derived verification plan; this is a defect fix that makes the gate's
detector correctly recognize a compliant plan whose content lives under an h3
subheading. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — each linked specification clause maps to a test in
`platform_tests/scripts/test_implementation_authorization.py`:

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (detector must recognize a
  compliant spec-derived plan): new test
  `test_has_spec_derived_verification_accepts_h2_heading_with_h3_subsection`
  asserts `has_spec_derived_verification` returns True for
  `"## Spec-Derived Verification Plan\n\n### Spec-to-test mapping\n\nDerived from the linked specs.\n"`
  (returns False before the fix — this is the defect under repair).
- Boundary generality: new test
  `test_has_spec_derived_verification_accepts_verification_plan_with_h3_only_evidence`
  asserts a `## Verification Plan` whose evidence lives entirely under a `### `
  subheading is recognized.
- Permissiveness invariant (no True→False regression): new test
  `test_has_spec_derived_verification_h3_boundary_preserves_token_recognition`
  re-asserts the four legacy exact headings remain recognized.
- Regression floor preserved (no false-positive widening): existing
  `test_has_spec_derived_verification_rejects_bare_test_plan_without_evidence`
  and `test_has_spec_derived_verification_rejects_missing_verification_section`
  continue to pass.
- `section_body` exact-match semantics unchanged: existing
  `test_section_body_exact_match_preserved` continues to pass (the fix does not
  touch `_iter_sections`/`section_body`).

Commands (resolved against the GT-KB venv interpreter, which carries `ruff`):

    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q
    .venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
    .venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py

Expected: all tests pass (the three new boundary tests fail before the fix and
pass after); `ruff check` and `ruff format --check` clean on both changed files.

## Acceptance Criteria

1. `has_spec_derived_verification()` returns True for a `## Spec-Derived
   Verification Plan` (or `## Verification Plan`) section whose content sits
   under a `### ` subheading.
2. No regression: all existing `test_implementation_authorization.py` tests
   pass; the four legacy headings and the bare-test-plan / missing-section
   reject cases are unchanged.
3. `_iter_sections()` and `section_body()` remain byte-for-byte unchanged.
4. `ruff check` and `ruff format --check` are clean on both changed files.

## Risk and Rollback

- Risk: LOW. The change is additive permissiveness in a single detector
  function; a wider section span cannot turn an existing True into False, so no
  previously-accepted verification plan stops being recognized. The begin-gate's
  purpose is to avoid rejecting GO-able proposals, so more-permissive
  recognition is aligned with intent.
- Blast radius: `has_spec_derived_verification()` plus one new private helper
  (`_iter_section_spans` / `_SECTION_LEVEL_RE`). No change to
  `_iter_sections`/`section_body`, so Specification Links, target_paths, and
  Requirement Sufficiency extraction are unaffected.
- Rollback: revert the two-file diff; prior behavior returns. No data migration,
  no state change, no schema impact.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`), which authorizes
implementation proposals for all unimplemented work items in
PROJECT-GTKB-MAY29-HYGIENE. WI-4617 is an unimplemented work item in that
project. No AskUserQuestion decision is needed for this defect fix.

## Recommended Commit Type

`fix:` — repairs broken governance-gate behavior (a false-negative) with no new
capability surface.
