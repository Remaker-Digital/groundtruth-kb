NEW
::init gtkb lo
::open build

# WI-5456: Align MCP status-summary provenance with current bridge authority

bridge_kind: prime_proposal
Document: gtkb-wi5456-mcp-status-summary-versioned-file-provenance
Version: 001
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5456

target_paths: ["groundtruth-kb/tests/test_mcp_surface_foundation.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Update the single T8 status-summary assertion so it expects
`bridge/versioned-files+groundtruth.db`, the value already emitted by the
production MCP surface and required by current bridge authority. The obsolete
aggregate-era expectation prevents the complete MCP foundation lane from
passing after WI-5411 restores MCP as a production dependency.

This is a one-line test-only correction. It does not change production MCP
source, package metadata, dispatcher or TAFE behavior, harness configuration,
MemBase, credentials, deployment, release state, or Git history.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the durable bridge history is the status-bearing numbered-file chain; the test must expect the production summary's current provenance value.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - current-state reporting must identify current canonical read surfaces rather than an obsolete aggregate-era substitute.
- `SPEC-1526` - the verified MCP production-dependency requirement supplies the parent WI-5411 lane whose complete foundation suite must pass.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the correction must preserve production behavior and change only the stale test expectation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the one-line correction requires independently executable focused evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation still requires project authorization, independent GO, a matching work-intent claim, and implementation-start authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal is linked to WI-5456 and its active project authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact test target and verification map are bound to the governing source-of-truth requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires the complete MCP foundation lane plus exact-scope quality evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the exact test target and every verification input remain inside the GT-KB project root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the discovered acceptance residue is preserved as WI-5456/TEST-11557 and this governed proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the correction proceeds through proposal, independent review, implementation report, and terminal verification states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - work-item, test, authorization, and bridge traceability are explicit rather than left in session memory.

## Prior Deliberations

- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` - owner decision adopting the current no-index bridge operating direction.
- `DELIB-20264361` - independent GO for runtime tooling to consume current versioned-file and dispatcher/TAFE bridge surfaces.
- `DELIB-20264330` - prior independent verification of the MCP stable harness surface and its foundation suite.

## Owner Decisions / Input

No additional owner decision is required. The active project authorization is
project-wide, includes the test mutation class, and preserves all ordinary
independent GO, claim, implementation-start, spec-derived testing, and VERIFIED
gates. The owner's dispatcher-configuration hold remains binding; this proposal
does not request a dispatcher configuration change.

## Requirement Sufficiency

Existing requirements are sufficient. TEST-11557 specifies the exact expected
source reference, the complete 15-test lane, and the prohibition on production
MCP source changes. There is no design choice or behavior ambiguity.

## Spec-Derived Verification Plan

| Requirement | Executable verification | Required result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `TEST-11557` | Run `groundtruth-kb/tests/test_mcp_surface_foundation.py` in the dependency-complete GroundTruth-KB test environment. | 15 passed; T8 expects exactly `bridge/versioned-files+groundtruth.db`. |
| `SPEC-1526` | Run the WI-5411 dependency-contract test together with the MCP foundation suite. | All tests pass with MCP available as a base dependency. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Inspect the exact target diff and production MCP source status. | Only the single approved test file changes; production MCP source remains unchanged. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run Ruff check, Ruff format check, and `git diff --check` on the exact target. | All commands exit zero. |

Independent Loyal Opposition verification must rerun the complete mapped lane
against the exact implementation bytes. A partial lane or an environment that
lacks the already-required MCP dependency is not sufficient for VERIFIED.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5456 and TEST-11557",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001 and GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "GroundTruth-KB MCP status-summary envelope",
  "before_behavior": "the production envelope emits current numbered-file provenance while T8 expects an obsolete aggregate-era value",
  "after_behavior": "T8 expects exactly bridge/versioned-files+groundtruth.db and the complete MCP foundation lane passes",
  "self_descriptive_naming": "the test name continues to describe the status-summary envelope behavior and the equality assertion states the canonical provenance value directly",
  "obsolete_guidance_disposition": "the obsolete expectation is replaced in the only approved test target; no production or historical artifact is rewritten",
  "history_preservation": "the numbered bridge thread, WI-5456, TEST-11557, and independent verdicts preserve the change history",
  "baseline": {
    "approved_targets": 1,
    "production_source_changes": 0,
    "expected_complete_lane": "15 MCP foundation tests"
  },
  "expected_result": {
    "source_ref": "bridge/versioned-files+groundtruth.db",
    "mcp_foundation_tests": "15 passed",
    "production_source_changes": 0
  },
  "rollback": {
    "instructions": "under separate authority, reverse only the one-line T8 expectation and rerun the same mapped verification lane",
    "test": "rerun the MCP foundation module, dependency-contract tests, Ruff checks, and exact-target whitespace check"
  },
  "hard_invariants": [
    "only groundtruth-kb/tests/test_mcp_surface_foundation.py may change",
    "production MCP source and package metadata remain unchanged",
    "dispatcher/TAFE behavior and configuration remain unchanged",
    "harness configuration, credentials, deployment, release, and Git history remain unchanged",
    "all paths remain in-root under E:/GT-KB"
  ],
  "fail_closed_conditions": [
    "the complete MCP foundation lane does not pass 15/15",
    "the equality assertion differs from bridge/versioned-files+groundtruth.db",
    "any file outside the exact target changes",
    "independent GO, claim, implementation-start, or VERIFIED evidence is absent"
  ],
  "essential_context_preservation": "the production status-summary envelope, MCP dependency contract, no-index bridge authority, exact project linkage, and independent review lifecycle remain intact"
}
```

## Acceptance Criteria

1. T8 expects exactly `bridge/versioned-files+groundtruth.db`.
2. The complete MCP foundation module passes 15/15 in the dependency-complete environment.
3. The WI-5411 dependency-contract tests and the MCP foundation module pass together.
4. No production MCP source, package metadata, dispatcher/TAFE surface, harness configuration, or other file changes under WI-5456.
5. Ruff check, Ruff format check, and exact-target whitespace validation pass.

## Pre-Filing Preflight

- Candidate-content applicability preflight: required to pass with `missing_required_specs: []`.
- Candidate-content ADR/DCL clause preflight: required to pass with zero blocking gaps.
- Exact target inventory: one clean tracked test file.
- Canonical-reference review: the filed proposal contains no dependency on a noncanonical artifact.

## Bridge Filing

This proposal will be filed as
`bridge/gtkb-wi5456-mcp-status-summary-versioned-file-provenance-001.md`, the
first numbered bridge file in an append-only thread. No prior version is
deleted or rewritten. All proposal, implementation, and verification paths are
in-root under `E:/GT-KB`.

## Risk / Rollback

Risk is limited to encoding the wrong provenance value in the test. The
complete MCP lane and direct equality assertion make that visible. Rollback,
under separate authority, is the inverse one-line test change followed by the
same verification commands. No production behavior rollback is involved.

## Recommended Commit Type

`test` - align one stale integration expectation with current canonical bridge
authority.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
