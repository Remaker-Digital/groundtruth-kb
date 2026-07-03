NEW

# WI-4991 Headless-Ineligible Dispatch Suppression

bridge_kind: prime_proposal
Document: gtkb-wi4991-headless-ineligible-dispatch-suppression
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Desktop interactive; Prime Builder via ::init gtkb pb; approval_policy=never; danger-full-access local session; dispatcher headless target remains gpt-5.5/xhigh/workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4991-HEADLESS-INELIGIBLE-SUPPRESSION
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4991

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "groundtruth-kb/tests/test_bridge_notify.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Fix a live dispatcher-selection defect found during the 2026-07-03 headless bridge soak: Codex A was dispatched to `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-010.md` even though that latest NO-GO explicitly says the dispatch loop must be broken and that no further Codex headless redispatch should occur for that task until an interactive Claude Prime Builder session or owner-approved ACL remediation changes the execution context.

The existing owner-hold mechanism already keeps exact `Hold for Owner Decision` GO/NO-GO verdicts Prime-visible but non-dispatchable. This proposal extends that same dispatchability pattern to explicit headless-ineligibility verdict language such as "do not re-dispatch to Codex headless", "dispatch loop must be broken", or equivalent latest-file instructions. Manual Prime visibility remains unchanged; only unattended headless auto-dispatch is suppressed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs role/status correctness for latest bridge files and requires the dispatcher to respect the current numbered bridge chain rather than stale summaries.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete proposal linkage to the governing specifications and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires this proposal to carry PAUTH, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the implementation report and verification verdict to map this dispatchability behavior to concrete tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires an active bounded PAUTH before protected source/test mutation.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires the dispatcher to select only runnable work for appropriate harness targets.
- `ADR-DISPATCHER-ARCHITECTURE-001` — governs shared behavior across daemon/runtime dispatch paths instead of one-off harness logic.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — requires cross-harness enforcement of harness boundaries and prohibits direct harness-to-harness fallback.
- `GOV-STANDING-BACKLOG-001` — governs the newly captured WI-4991 backlog item and its linked GOV-12 test.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires preserving the live soak defect as governed backlog/bridge evidence rather than scratchpad-only state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — governs durable source, test, bridge, and decision artifacts for this repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governs promoting the live dispatch-loop observation into active backlog, bridge, and verification artifacts.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directed Codex to keep stabilizing unattended headless dispatch with Codex as PB and Claude/Ollama as LO, while mechanically prohibiting direct harness-to-harness fallback.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — owner prohibited direct harness-to-harness interaction; this proposal preserves dispatcher-only processing rather than ad hoc standby launches.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` and `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` — timer/hung decisions explain why the fix should classify explicit ineligibility instead of shortening worker lifetimes to mask loops.
- `bridge/gtkb-wi4885-owner-hold-dispatch-suppression-001.md` through `-004.md` — verified precedent for keeping latest GO/NO-GO owner-hold verdicts manual-visible but non-dispatchable for headless automation.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-010.md` — live reproduction: latest NO-GO explicitly says the Codex headless dispatch loop must be broken, yet the daemon selected it for Codex A.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` — verified exact-thread/LO-lease/Ollama advancement repair; this proposal is a follow-on selector-classification defect, not a duplicate of WI-4977.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` — verified direct harness launch guard; this proposal preserves the same no-direct-fallback rule inside dispatcher recovery behavior.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` captures Mike's explicit directive to enable stable unattended headless bridge processing with Codex A as Prime Builder and Claude B/Ollama D as Loyal Opposition targets.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4991-HEADLESS-INELIGIBLE-SUPPRESSION` is active and covers WI-4991 for bridge/source/test mutation only.
- The proposal does not authorize direct harness-to-harness fallback, model/provider changes, topology changes, credential mutation, production deployment, or destructive cleanup.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, the verified owner-hold suppression precedent from WI-4885, and the active WI-4991 PAUTH provide enough governing requirement detail. No new or revised specification is required before implementation.

## Spec-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add a fixture mirroring WI-4929 latest NO-GO language and prove `compute_actionable_pending` keeps it Prime-visible with `dispatchable=false`; prove ordinary NO-GO remains dispatchable. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify the classifier reads only the latest status-bearing file for the exact bridge document and does not depend on cached summaries. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run dispatcher runtime/daemon tests showing headless selected batches omit headless-ineligible verdicts across the shared dispatcher path. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Verify the remediation suppresses direct fallback pressure instead of adding any shell/harness launch path. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run implementation-start authorization before source/test mutation and carry the PAUTH/project/WI metadata into the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include exact commands, observed results, and this spec-to-test mapping. |

Expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Risk / Rollback

Risk: broad text matching could suppress a legitimate NO-GO that merely discusses headless dispatch historically. Mitigation: require explicit latest-verdict imperative language that prohibits or breaks headless redispatch, and preserve ordinary NO-GO dispatchability with regression coverage.

Risk: under-broad matching could leave a differently worded non-headlessable verdict dispatchable. Mitigation: start from the observed WI-4929 language and add later markers through governed follow-up if needed.

Rollback: revert the source/test changes made under this bridge thread; manual Prime visibility for latest GO/NO-GO entries remains unchanged.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4991-headless-ineligible-dispatch-suppression`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
