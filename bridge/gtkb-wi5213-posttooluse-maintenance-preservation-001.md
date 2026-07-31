NEW

# WI-5213 - Preserve governed provider work across PostToolUse maintenance failures

bridge_kind: prime_proposal
Document: gtkb-wi5213-posttooluse-maintenance-preservation
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5213-POSTTOOLUSE-PRESERVATION-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5213

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: shared native-full hook lifecycle source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

A genuine dispatcher-produced Alibaba H Loyal Opposition run,
`2026-07-12T14-39-53Z-loyal-opposition-H-aacaa0`, completed 34 provider turns
and 55 governed tool calls before the shared native-full runtime aborted on a
ten-second `PostToolUse` timeout from
`bridge_verified_backlog_reconciler.py` after a successful Bash call. The
failure discarded the completed tool result and the remaining 566 turns of H's
generous session envelope before H could invoke the independently approved
governed verdict publisher.

This proposal gives the informational `PostToolUse` lifecycle event
event-specific failure handling: timeout, nonzero exit, malformed JSON, and
non-object output do not replace an already-completed tool outcome. Valid
structured hook output remains consumable, and a valid explicit block decision
continues to stop the provider loop. `PreToolUse`, implementation-start, raw
protected-write, and guard-adapter failures remain fail-closed. The correction
does not alter hook registrations, dispatcher routing, or the approved D/F/H
600-turn, 900-second operation, 28,800-second session, and 29,400-second worker
allowances.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001` - assigns shared native-hook and tool-loop lifecycle behavior to `cloud_harness_base.py`.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - requires H to operate through the shared native-full hook adopter rather than bypassing hooks.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires genuine governed end-to-end H proof rather than registration smoke.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - keeps the separate mutating-tool guard floor fail-closed.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires an explicit disposition for all active harnesses when shared harness behavior changes.
- `ADR-CROSS-HARNESS-PARITY-001` - requires semantic parity by declared applicability rather than identical hook tiers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct proposal, verdict, implementation report, and verification artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete governing-spec linkage before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project, PAUTH, and work-item headers above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent execution of every mapped lifecycle and enforcement regression.
- `GOV-STANDING-BACKLOG-001` - governs WI-5213 and linked TEST-11367 in PHASE-015.

## Prior Deliberations

- `DELIB-202666173` - directs genuine governed A/B/C/D/F/H proof and correction of every defect discovered during that proof.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - requires generous initial timing and sufficient evidence before classifying a long-running model as failed.
- `bridge/gtkb-wi5198-native-hook-empty-allow-001.md` - established generic fail-closed native-hook handling; the live H evidence now justifies an event-specific `PostToolUse` exception while retaining its enforcement boundaries.
- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md` through `-005.md` - established the separate Stop-only lifecycle repair and expressly did not authorize this `PostToolUse` behavior.
- `bridge/gtkb-wi5210-provider-lo-governed-verdict-publication-001.md` and `-002.md` - approved H's governed verdict route; run `aacaa0` failed before reaching that route because of the present lifecycle defect.

## Owner Decisions / Input

Mike explicitly directed genuine proof for every named harness and correction
of every discovered defect. That authority is recorded in `DELIB-202666173`.
The bounded implementation authorization is
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5213-POSTTOOLUSE-PRESERVATION-20260712`.
No additional owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. The shared-runtime and Alibaba-adoption
ADRs define lifecycle ownership; the onboarding contract requires truthful
genuine proof; the guard and bridge controls define the fail-closed enforcement
boundary. The reproduced failure resolves the previously unknown applicability
question for informational `PostToolUse` errors.

## Spec-Derived Verification Plan

1. `ADR-CLOUD-HARNESS-TEMPLATE-001`: shared-base tests prove
   `PostToolUse` timeout, nonzero, malformed JSON, and non-object output return
   without masking the successful tool outcome; valid structured output remains
   available and an explicit valid block remains fatal.
2. `DCL-OLLAMA-TOOL-PARITY-GATE-001`: focused tests prove `PreToolUse`
   timeout, nonzero, malformed output, and guard-adapter failures remain fatal.
3. `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` and
   `GOV-HARNESS-ONBOARDING-CONTRACT-001`: H-specific regression proves the
   native-full loop continues after a `PostToolUse` maintenance timeout, then a
   genuine dispatcher-produced H run performs real governed work and publishes
   the required role-correct verdict.
4. Cross-harness disposition: A and B retain their native runtimes; C does not
   consume `cloud_harness_base.py`; D and F use the guard-adapter floor so the
   event-specific branch is unreachable; H is the affected native-full adopter.
   Existing D/F allowance tests and shared guard tests must remain green.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
```

Expected result: all focused and cross-provider tests pass; H retains
600/900/28800/29400 allowances; the genuine H dispatch publishes its governed
verdict; no PreToolUse, guard-adapter, bridge, or implementation-start denial is
weakened.

## Risk / Rollback

The primary risk is accidentally treating an enforcement event as
informational. The implementation must key only on `PostToolUse`, preserve the
separate valid structured block path, and retain explicit regression coverage
for `PreToolUse` and the guard floor. Rollback is the focused WI-5213 commit;
H must return to ineligible until genuine proof is restored if rolled back.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5213-posttooluse-maintenance-preservation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects a reproduced provider lifecycle failure without adding a new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
