NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: abf38f9d-9205-44ac-a4c4-92490c175d3e
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder session (::init gtkb pb); workspace E:/GT-KB; envelope-disposition drive

# Implementation Proposal — WI-4689 SoT-Deference Startup-Injected Directive

bridge_kind: prime_proposal
Document: gtkb-wi4689-sot-deference-startup-injection
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4689

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

## Summary

Implements the startup-injection sub-part of WI-4689: surfaces the published-state SoT-deference directive (`GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` v1, owner-ratified 2026-06-25) in the GT-KB-subject startup payload by adding it to the `governance_stance` list in `session_self_initialization.py` — the existing home for standing governance directives (it already carries the strategic self-improvement directive, GOV enforcement, and standing-backlog directives). Lightweight standing-directive form per the owner AUQ (DELIB-20265896); no mechanical fetch service.

## Specification Links

- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` v1 — the rule being injected (GT-KB-subject sessions defer to released Main + public issues/wiki; application sessions emit advisories).
- `GOV-SESSION-SELF-INITIALIZATION-001` — fresh-session self-initialization disclosure governance (the payload this injects into).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root); `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `GOV-STANDING-BACKLOG-001`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` v1 fully specifies the rule; this proposal injects it into the startup payload. No new/revised requirement needed.

## Implementation Plan

1. `scripts/session_self_initialization.py` — append one directive string to the `governance_stance` list (near the strategic self-improvement directive): a concise SoT-deference directive citing `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` (defer to released Main + public issues/wiki before GT-KB changes; GT-KB leads, adopters trail; application sessions emit advisories per WI-4690).
2. `platform_tests/scripts/test_session_self_initialization.py` — extend the existing `governance_stance` assertion (the test that checks "Strict GOV enforcement" / "Formal artifact approval" presence) to assert the SoT-deference directive (and its spec id) is present in `governance_stance`.

## Spec-Derived Verification Plan (spec-to-test mapping)

| Specification | Test / verification | Command |
|---|---|---|
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` (rule surfaced at startup) | extend the `governance_stance` directives test to assert the SoT-deference directive + `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` are present | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -k governance -q` |
| `GOV-SESSION-SELF-INITIALIZATION-001` (payload integrity) | self-init model builds without error | same suite |

Code-quality gates on touched files: `python -m ruff check <files>` and `python -m ruff format --check <files>`.

Note: an unrelated pre-existing failure (`test_harness_role_assignment_map_is_startup_source_of_truth`) exists in this test file, driven by live harness-registry role state (codex=prime-builder vs the test's expected loyal-opposition), not by this change. Verification will scope to the governance-directive test.

## Prior Deliberations

- `DELIB-20265896` — WI-4689 SoT-deference form decision (lightweight standing directive).
- `DELIB-20265891` — envelope-disposition drive owner decision.
- No prior deliberation conflicts with the published-state SoT-deference injection (deliberation search 2026-06-25 found no opposing decision; existing SoT specs govern a distinct concept — canonical-artifact read discipline).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- AUQ 2026-06-25 (`AUQ-2026-06-25-wi4689-sot-deference`, DELIB-20265896): owner chose the lightweight standing-directive form (GOV record + startup-injected directive; agent-applied; mechanical fetch deferred), authorizing this startup-injection source change.
- AUQ 2026-06-25 (DELIB-20265891): owner chose "Drive formal work inline; AUQ each."

## Risk / Rollback

- Risk: minimal — an additive directive string in the startup `governance_stance` list. No behavior change beyond surfacing the directive.
- Rollback: remove the directive string + the test assertion. The GOV rule remains (owner-ratified). `session_self_initialization.py` was clean (no concurrent edit) at proposal time.
