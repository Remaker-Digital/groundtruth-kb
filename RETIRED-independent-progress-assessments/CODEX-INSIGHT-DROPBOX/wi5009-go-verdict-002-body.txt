GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T21-53-42Z-loyal-opposition-B-f04d05
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# WI-5009 Spec-Before-Code Structured Bridge Coverage — Loyal Opposition Review Verdict: GO

bridge_kind: lo_verdict
Document: gtkb-wi5009-spec-before-code-structured-bridge-coverage
Version: 002
Responds to: bridge/gtkb-wi5009-spec-before-code-structured-bridge-coverage-001.md
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-05 UTC

## Verdict Summary

**GO.** The proposal identifies a real over-permissiveness defect in the managed
`spec-before-code` hook template, scopes the fix precisely to the two paths ratified
by the WI-4455 policy review, cites and maps the governing specifications, and lays
out a test plan that covers the four load-bearing edge cases. Both mandatory
preflights pass clean. Prime Builder may proceed to file an implementation-start
packet and implement within the declared `target_paths`.

This GO authorizes implementation of the proposed template/test hardening only. It
does not authorize any change to the live `.claude/hooks/spec-before-code.py`
recovery stub, KB mutation, or broadened scope. The non-blocking recommendations in
the Findings section should be resolved during implementation and pinned by tests;
they are review guidance, not revision conditions.

## Premise Verification (evidence the defect is real)

The proposal's premise was verified against live code at
`groundtruth-kb/templates/hooks/spec-before-code.py`
(`_bridge_evidence_covers_platform_test`). The current predicate is genuinely too
permissive on all three cases the proposal names:

1. **Stale earlier versions.** The function iterates every `*.md` in `bridge/` and
   evaluates each file independently by its own first-line status token via
   `_is_status_bearing_bridge_file`. A superseded earlier version (e.g. `-001` NEW)
   still counts as coverage regardless of the latest thread status. Confirmed.
2. **Rejected terminal histories.** `BRIDGE_STATUS_TOKENS` includes `NO-GO`,
   `WITHDRAWN`, and `DEFERRED`; a file whose own first line is `NO-GO` (etc.) that
   contains the path token still returns coverage. There is no latest-state grouping.
   Confirmed.
3. **Prose-only mentions.** Coverage is decided by `_contains_path_token`, a
   whole-token regex match over the entire normalized file body. A path mentioned
   only in prose (outside `target_paths` or a mapping table) suppresses the advisory.
   Confirmed.

The three premises are literally true against the current implementation, so the
hardening is well-motivated rather than speculative.

## Scope and Boundary Confirmation

- **target_paths match the ratified predecessor envelope.** The WI-4455 policy-review
  GO (`bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md`,
  Focus-Question 2) fixed the implementation surface to exactly
  `groundtruth-kb/templates/hooks/spec-before-code.py` and
  `groundtruth-kb/tests/test_governance_hooks.py`, with the root `.claude/` stub held
  out of scope and the work carried under `PROJECT-GTKB-RELIABILITY-FIXES`. This
  proposal's `target_paths`, out-of-scope statement, project, and PAUTH match that
  ratified envelope one-for-one.
- **Live hook is a deliberate no-op stub.** `.claude/hooks/spec-before-code.py` is a
  WI-4449 recovery stub that exits 0; the template is the canonical artifact, so
  template-only scope is correct and not a hidden divergence. This mirrors how the
  WI-4455 initial implementation (`242f6039`) landed.
- **No duplication / no slug-variant collision.** `gt bridge threads --wi WI-5009`
  returns a single thread (this one, latest status NEW); `git log --grep=5009` shows
  no prior WI-5009 commit. The predecessor WI-4455 added the *initial* bridge-derived
  coverage; WI-5009 hardens the residual cases. Legitimate follow-up.
- **Root boundary.** Both `target_paths` are within `E:\GT-KB\groundtruth-kb\`.
  Compliant with `.claude/rules/project-root-boundary.md`.
- **Protocol structure.** The proposal carries all required sections: Specification
  Links (mapped to verification), Prior Deliberations, Owner Decisions / Input,
  Requirement Sufficiency, inline `target_paths`, a spec-derived verification plan,
  acceptance criteria, risk/rollback, and a justified Recommended Commit Type
  (`fix:`, correct for a false-positive repair).

## Applicability Preflight

- packet_hash: `sha256:5d25d898368dec24288c2a2b3969a59348bf48959ca08c7f5480f959ff281623`
- bridge_document_name: `gtkb-wi5009-spec-before-code-structured-bridge-coverage`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5009-spec-before-code-structured-bridge-coverage-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: harvested
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)

| Clause | Applicability | Evidence found | Enforcement |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

Both preflights are clean; no missing required specs and no blocking clause gaps.

## Findings and Non-Blocking Recommendations

These are review guidance to resolve during implementation and pin with tests. None
is a revision condition; the GO stands independent of them.

### R1 — Classify ADVISORY status explicitly (P3)

- **Claim:** Proposed step 2 names `NEW`/`REVISED`/`GO`/`VERIFIED` acceptable and
  `NO-GO`/`DEFERRED`/`WITHDRAWN` not-acceptable, but does not classify `ADVISORY`,
  which is a valid token in `BRIDGE_STATUS_TOKENS`.
- **Impact:** The "unrelated/unknown statuses must not suppress" clause is ambiguous
  for a thread whose latest version is `ADVISORY`.
- **Recommended action:** Have the implementation explicitly decide ADVISORY's
  disposition (recommended: non-suppressing — an advisory is not accepted
  implementation evidence, and it is non-dispatchable) and pin it with a test so the
  acceptable-status set is exhaustive and deterministic.

### R2 — Define which structured mapping surfaces count (P3)

- **Claim:** Step 3 names "a Spec-to-Test Mapping section/table" as a structured
  surface. Real proposals title the mapping variously — this very proposal uses
  "Spec-Derived Verification Plan," not "Spec-to-Test Mapping."
- **Impact:** Over-narrow heading matching re-introduces false negatives (advisory
  noise for genuinely-mapped tests); over-broad matching re-introduces the prose-scan
  defect this WI repairs.
- **Recommended action:** Anchor primarily on the inline `target_paths` JSON (the
  machine-canonical, most robust surface) and define precisely which heading(s)
  qualify as mapping evidence. Pin at least the canonical `## Spec-to-Test Mapping`
  form used by the existing positive test
  (`test_spec_before_code_platform_tests_match_via_bridge_evidence`).

### R3 — Add DEFERRED negative control and latest-acceptable-wins positive control (P3)

- **Claim:** The acceptance criteria enumerate the "latest rejected/withdrawn/deferred"
  case as one bullet, and the verification table exercises `NO-GO`/`WITHDRAWN`.
- **Recommended action:** Add explicit tests for (a) earlier mapped version + latest
  `DEFERRED` (owner-parked; must warn) and (b) latest `GO`/`VERIFIED` over an earlier
  `NO-GO` (must still suppress) — the latter mirrors bridge-compliance-gate's
  `test_bridge_compliance_go_over_nogo` and proves latest-acceptable-wins, not only
  latest-rejected-loses. This strengthens `DCL-SPEC-RELEVANCE-CLOSURE-001` coverage.

### R4 — Preserve cross-harness hook parity (P3, carry-forward from WI-4455 GO)

- **Claim:** WI-4455's policy GO (Finding 2) required the template hook to remain
  compatible with both Claude and Codex PreToolUse runners per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- **Recommended action:** Keep the hardened `_bridge_evidence_covers_platform_test`
  pure-stdlib and harness-neutral (no new environment coupling or non-stdlib imports).
  The proposed grouping/parsing appears pure-Python; confirm at implementation time.

### R5 — Positive confirmation (not a defect)

Keeping `NEW`/`REVISED` in the acceptable-status set is necessary, not incidental:
the existing positive test uses a `NEW` bridge file with inline `target_paths` plus a
`## Spec-to-Test Mapping` table and asserts suppression. Dropping `NEW`/`REVISED`
would break that test and violate the proposal's own acceptance criterion that a
current structured `target_paths` mapping still suppresses. The proposal is internally
consistent on this point.

## Prior Deliberations

- Ran `gt deliberations search` on two topic phrasings ("spec-before-code platform
  tests bridge-derived coverage stale prose" and "platform-tests spec-before-code
  policy bridge evidence latest status"); no Deliberation Archive records matched.
  The design reasoning for this line of work lives in the WI-4455 bridge threads,
  which the proposal already cites.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` (LO GO):
  ratified Option A (bridge-derived coverage), fixed the two-path implementation
  envelope, held the `.claude/` stub out of scope, and carried the work under
  `PROJECT-GTKB-RELIABILITY-FIXES`. WI-5009 is consistent with all four.
- `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-004.md`: the
  VERIFIED evidence for the initial Option A implementation that WI-5009 hardens.
- No previously-rejected approach is revisited without acknowledgement.

## Verification Performed (methodology trail)

- Read the operative proposal `bridge/gtkb-wi5009-spec-before-code-structured-bridge-coverage-001.md` (full Document block).
- Read live target `groundtruth-kb/templates/hooks/spec-before-code.py` and confirmed the over-permissive predicate behavior described in Premise Verification.
- Read `groundtruth-kb/tests/test_governance_hooks.py` (existing spec-before-code and bridge-evidence tests) to confirm the hardening keeps current positives green and identify the negative-control gaps in R3.
- `git log` on the hook template and repo (`--grep=5009`, `--grep=spec-before-code`): confirmed WI-4455 lineage (`242f6039`) and no prior WI-5009 work.
- `gt bridge threads --wi WI-5009`: single NEW thread, no slug-variant collision.
- Inspected `.claude/hooks/spec-before-code.py`: confirmed it is a WI-4449 no-op recovery stub (template is canonical).
- Read `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` to confirm scope/PAUTH/target-path consistency with the ratified predecessor policy.
- Ran `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5009-spec-before-code-structured-bridge-coverage`: `preflight_passed: true`, `missing_required_specs: []`.
- Ran `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5009-spec-before-code-structured-bridge-coverage`: exit 0, 0 blocking gaps.
- Ran `gt deliberations search` (two phrasings): no matching DA records.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
