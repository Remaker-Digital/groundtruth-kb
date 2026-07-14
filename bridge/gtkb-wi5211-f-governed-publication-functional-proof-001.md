NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Governance Review - OpenRouter F governed verdict publication functional proof

bridge_kind: governance_advisory
Document: gtkb-wi5211-f-governed-publication-functional-proof
Version: 001
Date: 2026-07-12 UTC

## Review Assignment

OpenRouter harness F must perform a genuine, substantive Loyal Opposition review of the uncommitted WI-5211 implementation. This is governed dispatcher-produced work under `GOV-HARNESS-ONBOARDING-CONTRACT-001`, not a canned readiness smoke test.

Inspect the actual implementation and tests in:

- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `scripts/cloud_harness_base.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

Also inspect the governing proposal and independent GO:

- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-001.md`
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-002.md`

## Claim To Evaluate

The F adapter now exposes provider-backed `PublishBridgeVerdict` only for bridge-review and verification skills, forwards trusted dispatcher session and model provenance into the shared cloud implementation, grants the model no numbered path or version authority, and preserves raw Write/Edit/Bash denial for numbered bridge verdicts. Canonical role, claim, transition, provenance, exclusive append, and VERIFIED finalization remain delegated to `scripts.gtkb_bridge_writer`.

The route must also preserve 600 turns, 900-second operations, 28,800-second sessions, 29,400-second worker lifetimes, and 29,700-second document leases.

## Required Review Work

1. Read the relevant source and focused tests; do not rely on this claim alone.
2. Verify profile enablement, skill threading, schema filtering, trusted metadata delegation, and fail-closed non-LO or missing-session behavior.
3. Verify the provider schema has no path or version argument and that raw numbered bridge Write/Edit/Bash remains denied.
4. Run the focused OpenRouter tests and any additional bounded checks needed for a defensible verdict.
5. Inspect dispatcher-visible configuration or envelope evidence needed to confirm the generous allowances remain intact.
6. Publish a substantive canonical `GO` or `NO-GO` for this document through `PublishBridgeVerdict`. Do not use raw Write, Edit, or Bash to create the numbered verdict file.

No implementation mutation is authorized by this governance review. If a defect is found, describe the exact evidence and required correction in `NO-GO`; do not patch source.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `DELIB-202666173` - owner-authorized governed D/F publication parity work.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - bounded predecessor finalization authority for the shared publisher capability.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - cross-harness parity implementation authority.

## Expected Outcome

A provider-authored, canonical, substantive `GO` or `NO-GO` verdict with `author_harness_id: F`, backed by actual code and test inspection. A READY marker, canned response, or raw bridge-file mutation does not satisfy this assignment.
