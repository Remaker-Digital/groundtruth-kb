REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5403 Separable-Hunk Correction Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 007
Responds to: bridge/gtkb-wi5403-declared-applicability-target-scope-006.md
Revises finalization plan: bridge/gtkb-wi5403-declared-applicability-target-scope-005.md
Carries forward approved scope from: bridge/gtkb-wi5403-declared-applicability-target-scope-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5403

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Revision Claim

Version 006's two blocking findings are accepted. This revision selects its
non-waiver option: restructure only the WI-5403-owned Markdown output lines so
the declared-target feature becomes a clean default-context Git hunk,
mechanically separate from WI-5408's foreign `blocking_errors` line.

No source or test byte has changed since version 006. Implementation remains
blocked until this revision receives a fresh independent GO, followed by a
matching `go_implementation` claim and schema-v3 implementation-start packet.

## Response To Version 006

### Finding 1 - Evidence was measured against the ambient combined tree

Accepted. The current ambient source contains WI-5387, WI-5403, and WI-5408
candidate bytes, so its `33 passed` result is not the isolated WI-5403
post-finalization baseline.

The canonical WI-5403 MemBase record already states the isolated baseline:
`5 failed / 26 passed`. Those five failures are committed tests for structured
PAUTH-amendment validation that committed HEAD does not implement. They are:

- `test_preflight_reports_structured_pauth_amendment_blocking_error`;
- `test_preflight_accepts_structured_pauth_amendment_with_exact_owner_evidence`;
- `test_preflight_rejects_out_of_root_pauth_approval_path`;
- `test_preflight_rejects_malformed_pauth_approval_json`;
- `test_preflight_rejects_invalid_nonowner_or_noncovering_pauth_packet`.

WI-5403 does not claim or repair those tests. WI-5408 owns their missing source
implementation through the canonical structured PAUTH-amendment validator.
The corrected implementation report must disclose both tree states:

1. the ambient shared tree, expected to retain `33 passed` while WI-5408 bytes
   remain present; and
2. the isolated HEAD-plus-WI-5403 candidate, expected to report the same five
   pre-existing PAUTH-amendment failures and 26 passes while both exact
   WI-5403 tests pass.

The eventual verifier must test the isolated candidate and record that
classification. It must not present the ambient 33-pass result as the
post-WI-5403 finalization state.

### Finding 2 - Sub-hunk interleaving required a WI-specific owner waiver

Accepted. The owner waiver at
`DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` is explicitly scoped to
WI-5113 and cannot authorize WI-5403. This revision therefore does not request
or rely on a waiver.

Instead, after GO, Prime Builder will move only these two existing WI-5403
formatting expressions:

```python
f"- declared_target_paths: {json.dumps(packet.get('declared_target_paths', []))}",
f"- applicability_path_evidence: {json.dumps(packet.get('applicability_path_evidence', []))}",
```

from immediately after the `preflight_passed` output line to immediately after
the `bridge_document_name` output line in `format_markdown`.

Their rendered text and values remain identical. In the resulting HEAD-relative
diff, more than six unchanged lines separate the two WI-5403 additions from
WI-5408's foreign `blocking_errors` addition. With Git's default three context
lines, the concerns become distinct hunks. No synthesized sub-hunk, owner
waiver, foreign-byte adoption, or hand-authored semantic rewrite is required.

The final report must include the default-context diff proving that separation.
If the changes still merge into one hunk at implementation time, fail closed
and return for renewed review rather than constructing a synthesized patch.

### Finding 3 - WI-5387 closure integrity concern

Accepted as non-blocking and out of WI-5403 implementation scope. WI-5387's
operative-version bytes remain foreign and must not enter the WI-5403 commit.
Its closure-integrity concern remains visible through its own canonical work
item and bridge chain. This revision neither repairs nor relies on those bytes.

## Requirement Sufficiency

Existing requirements sufficient.

Version 006 identifies both required corrections and offers the exact
non-waiver restructuring route selected here. The active WI-5403 PAUTH already
covers source, test, bridge, metadata, and governance-evidence work on the two
exact targets. No new requirement, owner choice, or waiver is needed.

## Current Byte Boundary

Prime Builder must confirm these exact hashes immediately before any
implementation. A mismatch requires renewed review:

- `scripts/bridge_applicability_preflight.py`:
  `sha256:f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2`.
- `platform_tests/scripts/test_bridge_applicability_preflight.py`:
  `sha256:df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf`.

The source file is the only expected edit target. The test file is included in
the finalization inventory but is read-only for this correction.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Prior Deliberations

- `DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` establishes that a
  WI-specific owner waiver is required for synthesized sub-hunk finalization.
  This proposal avoids that route by restoring native hunk separability and
  does not treat the WI-5113 decision as authorization for WI-5403.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision behind the active bounded WI-5403 PAUTH.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-001.md` through
  `bridge/gtkb-wi5403-declared-applicability-target-scope-006.md` preserve the
  complete proposal, implementation, correction, and independent-review chain.
- `bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-005.md`
  assigns the five PAUTH-amendment failures to WI-5408 and requires WI-5403 to
  reach a terminal reconciled disposition before WI-5408 starts from a clean
  shared-file baseline.
- `bridge/gtkb-wi5387-applicability-corrected-go-operative-004.md` is the
  canonical sibling chain for the foreign operative-version bytes.

The mandatory Deliberation Archive search found the WI-5113 waiver precedent
and other shared-file finalization precedents. None grants a WI-5403 waiver,
and no decision rejects the clean-hunk restructuring route.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
  `PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717` authorize
  this bounded correction through the normal bridge lifecycle.
- No new owner decision is required because this proposal removes the
  interleaving condition instead of asking to waive it.
- The owner's dispatcher-configuration/troubleshooter hold remains fully
  controlling. No dispatcher configuration or runtime-state inspection or
  mutation is in scope.

## Exact Proposed Change

After independent GO:

1. Reconfirm both current hashes and the live PAUTH.
2. Acquire the matching implementation claim and schema-v3 start packet.
3. In `format_markdown`, move the two existing WI-5403 declared-scope output
   expressions from after `preflight_passed` to after
   `bridge_document_name`.
4. Make no other source or test change.
5. Confirm the test hash is unchanged.
6. Confirm the source hash changes only because those two expressions moved.
7. Use `git diff --unified=3` to prove the WI-5403 output hunk is separate
   from WI-5408's `blocking_errors` hunk.
8. Construct the exact HEAD-plus-WI-5403 finalization patch from native clean
   hunks only and test that isolated candidate.
9. File a corrected implementation report with both ambient and isolated-tree
   results, exact hashes, exact hunk inventory, and all foreign exclusions.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5403; PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717; bridge/gtkb-wi5403-declared-applicability-target-scope-006.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-WORK-TREE-HYGIENE-001; DCL-PROJECT-DEPENDENCY-ORDERING-001",
  "primary_route": "Move only the two WI-5403 Markdown expressions to a natively separable output hunk while preserving rendered values and all foreign bytes.",
  "before_behavior": "WI-5403 output lines and WI-5408 blocking-error output occupy one default-context Git hunk, forcing a synthesized sub-hunk or owner waiver.",
  "after_behavior": "The same WI-5403 output lines render earlier in the header and occupy a distinct native Git hunk, so WI-5403 can finalize without adopting WI-5408 bytes.",
  "self_descriptive_naming": "declared_target_paths and applicability_path_evidence continue to distinguish authorized mutation scope from conservative applicability evidence.",
  "obsolete_guidance_disposition": "Version 005's hand-isolated sub-hunk finalization route is withdrawn; native hunk separation and honest isolated-tree evidence replace it.",
  "history_preservation": "All numbered bridge versions remain append-only; WI-5387 and WI-5408 bytes remain untouched and outside the WI-5403 candidate.",
  "baseline": {
    "source_sha256": "f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2",
    "test_sha256": "df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf",
    "isolated_suite": "5 failed / 26 passed, with the five failures owned by WI-5408"
  },
  "expected_result": {
    "rendered_fields": "byte-equivalent field text and values at a new header position",
    "git_hunks": "WI-5403 output addition and WI-5408 blocking_errors addition are distinct under default three-line context",
    "isolated_wi5403_tests": "both declared-target tests pass"
  },
  "rollback": {
    "instructions": "Move only the two WI-5403 Markdown expressions back to their current position through a governed correction.",
    "verification": "Foreign WI-5387/WI-5408 bytes and the read-only test file remain unchanged."
  },
  "hard_invariants": [
    "No synthesized sub-hunk or WI-5403 owner waiver is used.",
    "No WI-5387 operative-version line enters the WI-5403 candidate.",
    "No WI-5408 PAUTH-amendment line enters the WI-5403 candidate.",
    "The test file remains byte-identical.",
    "No dispatcher, TAFE, harness, configuration, runtime-state, database, credential, external, deployment, release, push, or history action occurs."
  ],
  "fail_closed_conditions": [
    "Either current target hash changes before implementation.",
    "The two output concerns remain one default-context Git hunk.",
    "Either exact WI-5403 test fails in ambient or isolated state.",
    "Any foreign line or path appears in the finalization patch.",
    "Ruff, format, py_compile, diff-check, applicability, or clause gates fail."
  ],
  "essential_context_preservation": "The corrected report must show both tree-state test results, five named out-of-scope failures, exact hashes, native hunk separation, and foreign-byte exclusions."
}
```

## Specification-Derived Verification Plan

| Specification / invariant | Required executed evidence |
| --- | --- |
| Declared-target behavior; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the two WI-5403 node IDs against the ambient tree and the isolated HEAD-plus-WI-5403 candidate; both must pass in both states. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Inspect the default-context diff and final native hunk patch; no WI-5387 or WI-5408 line may be included. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the full applicability suite on both tree states. Report ambient results separately from isolated `5 failed / 26 passed`, naming all five out-of-scope failures. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Validate independent GO, claim, schema-v3 start, exact targets, native hunk separation, governed report, and atomic VERIFIED finalization. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Re-read the active PAUTH, matching project, WI-5403, and exact two-target inventory. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every candidate, changed, and staged path remains in-root and no adopter path appears. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run both mandatory bridge preflights on the corrected report and preserve fail-closed gate behavior. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve WI-5403 as the durable work authority and the numbered bridge chain as the canonical review record. |

Additional mandatory commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py::test_declared_target_paths_exclude_incidental_applicability_evidence platform_tests/scripts/test_bridge_applicability_preflight.py::test_packet_separates_declared_scope_from_applicability_path_evidence -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `git diff --check -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`

## Acceptance Criteria

- The two Markdown fields render the same text and values as before.
- A default three-context Git diff places the WI-5403 Markdown expressions in
  a distinct hunk from WI-5408's `blocking_errors` expression.
- No synthesized sub-hunk or WI-5403-specific owner waiver is needed.
- Both WI-5403 tests pass in ambient and isolated candidate states.
- The full ambient suite remains 33 passed while the combined candidate is
  present.
- The isolated candidate honestly reports the same five named out-of-scope
  PAUTH-amendment failures and 26 passes.
- Ruff lint, Ruff format, `py_compile`, and diff checks pass.
- The test file remains byte-identical to the approved boundary.
- The report carries every linked specification and both tree-state results.

## Applicability Preflight

Candidate applicability executed against the exact version-007 proposal
content before filing and reported:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`

## Clause Applicability

The mandatory clause preflight executed against the exact version-007 proposal
content before filing and reported five clauses evaluated, four `must_apply`,
one `may_apply`, zero evidence gaps in `must_apply` clauses, zero blocking
gaps, and exit code zero.

## Risks And Rollback

The only implementation risk is accidentally changing output order in a way
that harms consumers or still leaves the hunks merged. The rendered field text
is unchanged, existing tests assert both fields, and the default-context diff
is a mandatory fail-closed check.

Rollback is a governed move of the same two expressions back to their current
position. Foreign WI-5387 and WI-5408 bytes and the numbered bridge history
remain untouched.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`

Read-only finalization inventory:

- `platform_tests/scripts/test_bridge_applicability_preflight.py`
