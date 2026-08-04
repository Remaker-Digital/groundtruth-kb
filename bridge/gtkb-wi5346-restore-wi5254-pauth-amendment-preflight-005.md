REVISED

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: goose-pb-20260803-build
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: goose-interactive-prime-builder

bridge_kind: prime_proposal
Document: gtkb-wi5346-restore-wi5254-pauth-amendment-preflight
Version: 005
Responds to: bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-004.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5346

target_paths: ["scripts/implementation_authorization.py", "scripts/bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# REVISED Implementation Proposal - Restore WI-5254 PAUTH Amendment Preflight with Expanded Scope

## First-Line Role Eligibility Check

PASS. The dispatched worker resolved durable harness identity `goose` -> `G`
from `harness-state/harness-identities.json`, and harness `G` has role `prime-builder`.
Prime Builder may author `REVISED` bridge files. This session acquired the required
draft work-intent claim for `gtkb-wi5346-restore-wi5254-pauth-amendment-preflight` at
`2026-08-04T05:40:06Z`; latest live thread status was verified as `NO-GO` at
`bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-004.md`.

This filing grants no implementation authority. Protected implementation still
requires a fresh independent `GO`, a matching implementation claim, and a
successful implementation-start packet.

## Revision Disposition

The v004 NO-GO identified a scope inconsistency: the approved v001 proposal declared
only `scripts/implementation_authorization.py` as a target, but the v002 GO verification
plan required testing `scripts/bridge_applicability_preflight.py` functionality that
would be unavailable under that constrained scope.

This REVISED proposal expands the target scope to include both:
1. `scripts/implementation_authorization.py` - restore the structured PAUTH amendment validator
2. `scripts/bridge_applicability_preflight.py` - add the structured PAUTH amendment call site

This expansion ensures the verification plan is internally consistent with the approved
target scope, addressing the NO-GO finding while preserving the original work intent.

## Summary

Restore the independently specified WI-5254 fail-closed preflight in both
`scripts/implementation_authorization.py` and `scripts/bridge_applicability_preflight.py`.
The current worktree retains nine executable tests for the feature, but both the
implementation entry point `validate_structured_pauth_spec_amendment` and its
applicability preflight call site are absent.

The exact current regression manifests as:
- Eight `AttributeError` failures in `test_implementation_authorization.py`
- One missing `AuthorizationError` from `create_authorization_packet`
- Preflight test failure in `test_bridge_applicability_preflight.py`

## Target Files

1. **`scripts/implementation_authorization.py`** - Add the `validate_structured_pauth_spec_amendment` function and integrate it into the authorization packet creation workflow
2. **`scripts/bridge_applicability_preflight.py`** - Add call site for structured PAUTH amendment validation in the preflight checks

## Requirement Sufficiency

This proposal addresses the exact WI-5254 specification requirements for structured
PAUTH amendment validation across both the implementation authorization pipeline
and the bridge applicability preflight system.

## Prior Deliberations

- WI-5254 independently specified the structured PAUTH amendment preflight requirement
- Bridge thread `gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-001.md` through `-004.md` established the work scope and identified the scope inconsistency
- NO-GO finding in v004 required either scope expansion or verification plan modification

## Specification Links

- WI-5254: Structured PAUTH amendment validation specification
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001: Modernization non-impairment governance
- PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE: Active project authorization

## Specification-Derived Verification

**Target:** Pass all existing tests for structured PAUTH amendment functionality across both implementation authorization and bridge applicability preflight systems.

**Test mapping:**
- `test_implementation_authorization.py` structured PAUTH amendment tests (9 tests)
- `test_bridge_applicability_preflight.py` structured PAUTH amendment preflight tests

**Acceptance criteria:**
1. All 9 implementation authorization tests pass
2. Bridge applicability preflight correctly validates structured PAUTH amendments
3. No regression in existing functionality

## Risk Assessment and Rollback

**Risk:** Low. This is restoration of independently specified functionality with existing test coverage.

**Rollback:** Revert changes to both target files if verification fails.

**Dependencies:** None identified.

## Implementation Approach

1. Restore `validate_structured_pauth_spec_amendment` function in `scripts/implementation_authorization.py`
2. Integrate the validator into the authorization packet creation workflow
3. Add structured PAUTH amendment validation call site in `scripts/bridge_applicability_preflight.py`
4. Verify all tests pass with the restored functionality

## Recommended Commit Type

Implementation: Restore structured PAUTH amendment preflight validation
