REVISED
::init gtkb pb
::open build

# WI-5364 Codex Hook Batch Parity — Re-Filed REVISED Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5364-codex-hook-batch-parity
Version: 005
Responds to: bridge/gtkb-wi5364-codex-hook-batch-parity-004.md
Date: 2026-08-03 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5364
target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]
implementation_scope: configuration,source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T14-58-52Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: goose-desktop-interactive;skill=bridge-review

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

## Revision Claim

Version 004 (NO-GO) found no defect in the WI-5364 proposal or GO; it blocked
implementation on an authorization-tooling cross-thread collision (a stale
`current.json` naming the unrelated `gtkb-wi5360-peer-solution-defer-trigger-wording`
thread caused the schema-v3 begin gate to reject the WI-5364 GO). This REVISED
proposal re-presents the approved four-path implementation scope unchanged so
Loyal Opposition can issue a fresh independent GO, after which Prime Builder
will acquire the exact claim and mint a new schema-v3 implementation-start
packet against the now-clean authorization context.

Re-observation this filing (current HEAD `588fec312`): all four target paths
are clean. The begin gate now returns the clean error "latest status NO-GO"
(rather than the prior cross-thread collision), confirming the authorization
context is no longer poisoned by the unrelated thread. A fresh GO is the only
remaining prerequisite for implementation-start.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH covers this
configuration/source/test repair; no AUQ was required.

## Prior Deliberations And Chain Evidence

- Version 001 filed the bounded four-path proposal.
- Version 002 (Cursor E) issued GO.
- Version 003 documented the Prime NO-ACTION on an implementation-start gate failure.
- Version 004 (NO-GO) confirmed the GO was substantively valid and prescribed resolving the authorization-tooling collision before re-attempting start.
- This version 005 re-presents the identical four-path scope for a fresh independent GO.

## Findings Addressed

### F (P0) — Implementation-start gate rejected due to authorization-tooling cross-thread collision

**Accepted and resolved at the tooling layer.** The prior `begin` failure named
the unrelated `gtkb-wi5360-peer-solution-defer-trigger-wording` thread from a
stale `current.json`. Re-attempting `implementation_authorization.py begin`
this filing now returns the clean error "latest status NO-GO" — the
cross-thread collision is no longer the blocker. A fresh independent GO on
this REVISED proposal is the sole remaining prerequisite for a valid
schema-v3 implementation-start packet.

## Proposed Scope (unchanged from v001)

1. Replace the obsolete disabled-hooks comment with the current live-Windows/no-window-batch stance and set the project feature flag to true.
2. Preserve the unrelated current `sandbox_mode` line and every other config byte outside the WI-5364 hunk.
3. Remove the wrap-up adapter's helper and command extension that pass `--role-profile`; retain canonical envelope/session role latching.
4. Import and reuse the existing public batch-aware surface enumerator in the Codex parity checker.
5. Evaluate required surfaces per event group and matcher after declarative batch expansion, continuing to accept valid direct no-space wrappers.
6. Treat unreadable/malformed/missing batch definitions or omitted required surfaces as parity errors.
7. Validate the outer batch hook as a command/no-window runner invocation without command substitution; keep child timeout enforcement owned by the existing runner.
8. Update repository assertions to inspect expanded event-group surfaces.
9. Add focused fixtures proving a valid batch route passes, a missing batch surface fails, and direct-wrapper compatibility remains accepted.
10. Leave the Codex hook registration document, batch runner, wrappers, and other harness configuration unchanged.

## Specification-Derived Verification Plan

| Requirement | Verification | Required result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` | All parity tests pass; checker findings 0 |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Wrap-up session-role discovery tests | No `--role-profile` override |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | No-window batch + cross-harness regressions | All green; no duplicate execution |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/check_codex_hook_parity.py` | `authorized: true`, 0 findings |
| Source quality | Ruff check + format on both Python targets | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh GO + claim + schema-v3 begin | Packet authorized for exact four targets |

## Cross-Harness Disposition

No typed parity waiver is requested; this proposal achieves behavioral parity.

- Codex: activates the already-registered no-window batch topology and corrects its parity evaluator plus dynamic wrap-up role behavior; each handler continues to execute once. The `.codex/config.toml` and `.codex/gtkb-hooks/**` targets are the Codex-specific surfaces in scope; the parity checker (`scripts/check_codex_hook_parity.py`) and its test assert the resulting Codex surface set equals the reference behavior.
- Claude: no hook or settings change; existing direct registrations remain the reference behavior compared by the parity checker.
- Cursor, Antigravity, Ollama, OpenRouter, Alibaba: no hook mutation; shared role and governance semantics remain green in cross-harness tests (Antigravity remains an architectural surface difference with interval-driven dispatch, not a target for Codex registration cloning).

## Requirement Sufficiency

Existing requirements sufficient. The approved four-path design in version 001,
the governing ADR/spec/DCL carriers, and the version 004 NO-GO (which found no
technical defect in the proposal or GO) fully define the required behavior. No
new or revised formal requirement is required before implementation.

## Acceptance Criteria

1. The four declared targets are the only modified protected paths.
2. Hooks enabled via existing no-window batches; no duplicate handler registration.
3. Parity checker resolves each batch to actual handler surfaces and fails closed on missing/malformed batches.
4. Wrap-up discovers session role canonically (no role-profile override).
5. All focused parity, no-window, and cross-harness tests pass; Ruff clean.
6. A valid schema-v3 implementation-start packet authorizes the exact four targets.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5364; NO-GO v004; re-observation at HEAD 588fec312",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governing ADR/spec/DCL carriers",
  "primary_route": "python scripts/check_codex_hook_parity.py",
  "before_behavior": "The project disables a supported live hook surface, the checker reports gaps because it ignores committed batch fan-out, and wrap-up explicitly passes a role profile.",
  "after_behavior": "Hooks are enabled through the existing no-window batches, parity resolves each batch to its actual handler surfaces exactly once, and wrap-up discovers session role canonically.",
  "self_descriptive_naming": "Event-group surface expansion distinguishes configured outer batch commands from their actual handler surfaces and keeps direct-wrapper compatibility explicit.",
  "obsolete_guidance_disposition": "The stale disabled-hooks comment and explicit role-profile override are removed; the v3 fallback remains applicable only when empirical hook availability regresses.",
  "history_preservation": "The committed batch runner and hook registration history remain unchanged; the foreign current sandbox configuration hunk remains independently owned.",
  "baseline": "Four target paths clean at HEAD 588fec312; begin gate returns clean 'latest status NO-GO' (no cross-thread collision).",
  "expected_result": "Fresh GO -> claim -> schema-v3 start authorizes the exact four targets; focused parity and no-window tests green; checker findings 0.",
  "rollback": "Revert only the WI-5364 hunks through a separately governed transaction; preserve foreign config bytes and all existing batch registrations.",
  "hard_invariants": [
    "no governance or lifecycle handler executes twice",
    "all hook subprocesses remain under the existing no-window runner",
    "missing or malformed batch evidence fails parity closed",
    "interactive session role is not forced by the wrap-up adapter",
    "no harness is disabled, deprioritized, rerouted, or made ineligible",
    "no dispatcher, TAFE, registry, or hook registration document is mutated"
  ],
  "fail_closed_conditions": [
    "hooks remain disabled on the supported runtime",
    "a required batch surface cannot be parsed or is absent",
    "a hook command bypasses the no-window runner",
    "the role-profile override remains",
    "focused parity, runtime containment, or cross-harness regression tests fail"
  ],
  "essential_context_preservation": "Preserve the existing hook registration document, batch runner, wrappers, foreign sandbox_mode config hunk, and all other harness configuration byte-for-byte; only the WI-5364 feature-flag/comment, wrap-up role-override, checker, and test hunks change."
}
```

## Risk And Rollback

Rollback is a focused revert of only the WI-5364 feature-flag/comment, wrap-up
role-override, checker, and test hunks through a separately governed
transaction; foreign config bytes and all existing batch registrations are
preserved. Bridge/MemBase/history remain append-only.
