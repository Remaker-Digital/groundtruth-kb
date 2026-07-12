NEW

# WI-5203 - Targeted dispatcher reoffer and neutral NO-ACTION completion

bridge_kind: prime_proposal
Document: gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5203-DISPATCH-RECOVERY-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5203

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/dispatcher_runtime.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source, CLI, and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

A genuine dispatcher-routed Alibaba H recovery exposed two lifecycle defects after the WI-5200 repair. First, an earlier failed H dispatch stored the open WI-5199 report in `last_dispatched_signatures_by_document`; the canonical soft reset intentionally retained that map, but no narrower governed control exists to reoffer one recipient/document pair. WI-5199 is therefore open and actionable yet permanently filtered unless an operator performs a prohibited direct runtime-state edit or a destructive owner-gated hard reset.

Second, H correctly inspected a latest `NO-ACTION` thread, exited 0, and declined to author a Loyal Opposition verdict because the referenced work item was already terminal. The completion monitor nevertheless recorded `no_verdict_produced` / `missing_bridge_verdict`, adding false failure and circuit-breaker evidence. This proposal adds an audited, dry-runnable targeted reoffer to `gt bridge dispatch reset` that removes only the selected document signature and thread-reoffer suppression for one recipient while refusing a live lease. It also makes selected latest `NO-ACTION` plus exit 0 plus no verdict a neutral successful stand-down. `NEW` and `REVISED` no-verdict exits remain fail-closed.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires centralized dispatch, deterministic eligibility, truthful lifecycle outcomes, and operator-safe recovery.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — requires dispatcher mutation through canonical CLI control surfaces rather than direct configuration or runtime JSON edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs role-correct append-only proposal, verdict, report, and verification artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite its governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the active project, work item, and PAUTH linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent execution of the mapped checks before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5203 and TEST-11357 preserve the two observed defects and their acceptance contract before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the live H evidence, owner decision, work item, test, proposal, report, and verdict to remain traceable.

## Prior Deliberations

- `DELIB-202666173` — owner-directed completion of genuine governed proof across all six named harnesses and correction of every defect discovered in that work; this proposal is the bounded carrier for the two dispatcher defects exposed by H.
- `INTAKE-f8bc08a3` — establishes the Dispatcher/Bridge CLI as the primary mutating UI; targeted reoffer belongs there rather than in a manual JSON procedure.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` — requires generous runtime allowances and evidence before failure; neutral stand-down prevents correct role behavior from becoming false failure evidence.

## Owner Decisions / Input

Mike explicitly set the goal that each harness be verified functioning and every discovered defect be corrected, then required genuine governed dispatcher-produced work for Codex, Claude Code, Alibaba, OpenRouter, Ollama, and Antigravity. That decision is recorded as `DELIB-202666173` and authorizes the bounded WI-5203 repair. The active project authorization is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5203-DISPATCH-RECOVERY-20260711`.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` defines truthful centralized dispatch lifecycle behavior, `SPEC-DISPATCHER-CONTROL-SURFACE-001` requires governed operator mutation through the CLI, and the cited bridge, verification, backlog, and artifact-governance controls define the approval and evidence boundaries. No new product-policy choice is needed.

## Spec-Derived Verification Plan

1. `SPEC-DISPATCHER-CONTROL-SURFACE-001`: focused reset module and CLI tests prove `--recipient` plus `--document` is dry-runnable and audited, removes only that document's signature/reoffer state, preserves unrelated recipient evidence, and refuses a matching live lease.
2. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: focused runtime tests prove selected latest `NO-ACTION` plus exit 0 plus no verdict records neutral success, clears no circuit evidence, and retains the signature; matched `NEW` and `REVISED` cases remain `no_verdict_produced` failures.
3. `GOV-FILE-BRIDGE-AUTHORITY-001`: bridge compliance and status inspection prove only the LO reviewer writes GO/NO-GO/VERIFIED and this Prime Builder writes only NEW/REVISED/report states.
4. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: an independent LO harness runs the exact focused suite plus lint and records command-level evidence in the verdict.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/dispatcher_runtime.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_dispatcher_runtime.py
```

Expected result: all selected tests pass, lint exits 0, the live targeted reoffer makes the still-open WI-5199 report dispatchable to H without disturbing other recipient/document state, and no direct runtime JSON mutation occurs.

## Risk / Rollback

The principal risk is clearing too much dispatcher state or accidentally treating a missing verdict on actionable review work as success. The implementation must key the reset by exact recipient and normalized bridge document, reject ambiguous/missing matches and live leases, and branch neutral completion only on the selected top status `NO-ACTION` with process exit 0. Rollback is one focused commit; runtime evidence remains append-only and the pre-repair stale signature can be regenerated only by a real dispatch, not fabricated.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - this corrects two observed dispatcher lifecycle defects and adds their regression coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
