NEW

# gtkb-wi4550-dispatch-cost-budget-policy (Slice 1) — Dispatch Cost/Token Budget Gate

bridge_kind: prime_proposal
Document: gtkb-wi4550-dispatch-cost-budget-policy
Version: 001
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T16:43:22Z

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4550

target_paths: ["config/dispatcher/rules.toml", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatch_cost_budget.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source | config | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4550 Slice 1 by adding a declarative budget gate for dispatched bridge workers. The slice keeps the Omnigent Alignment project inside its patterns-only boundary: mirror the cost-policy shape in GT-KB-native code/config, do not import Omnigent, and do not introduce a runtime dependency.

The immediate risk being addressed is repeated headless dispatch consuming large token/cost budgets during loops or stuck-worker conditions. Existing GT-KB dispatch controls cap concurrency and rank candidates by a cost score, but they do not provide a hard per-session or daily spend/token budget gate. This slice adds that missing launch-path guard before a worker is spawned.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal requests Loyal Opposition authorization before protected source/config/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the work item, project, PAUTH, target paths, and verification plan are explicit in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal is linked to `PROJECT-OMNIGENT-ALIGNMENT`, `WI-4550`, and `PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification maps the bridge-governed dispatch budget behavior to focused regression tests and dispatcher config tests.
- `GOV-STANDING-BACKLOG-001` — WI-4550 is the active governed backlog item being processed.
- `GOV-AUTOMATION-VALUE-VS-COST-001` — cost/token gates reduce uncontrolled automation spend and make budget exhaustion visible instead of silently continuing background dispatch.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` — established the Omnigent advisory review that identified cost/token budget enforcement as the top Omnigent-alignment risk.
- `DELIB-20263229` — owner decision for patterns-only Omnigent emulation: borrow design shape, no runtime dependency.
- `DELIB-20265586` — owner-approved project authorization snapshot covering WI-4550 through WI-4555.
- `INTAKE-2ce995f2` — bounded parallel cross-harness auto-dispatch is the dispatch substrate that needs budget boundaries in addition to concurrency caps.
- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` — dispatch-track implementation authorization context; this proposal stays in the same governed dispatch lane and does not bypass bridge authority.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. WI-4550 is already created and prioritized P1 by the 2026-06-14 owner directive, and `PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23` authorizes bounded implementation of WI-4550. The open decision for LO is technical GO/NO-GO on this specific source/config/test slice.

## Requirement Sufficiency

Existing requirements are sufficient for Slice 1. The work item description requires per-session and per-user-daily budget gates, soft ASK checkpoints, a hard cap that prevents expensive continuation, fail-closed unknown-model behavior, fail-open unpriced behavior, and Omnigent-shape mirroring without importing Omnigent. This proposal implements the launch-path budget gate and observable config/reporting pieces; any later unified policy-registry consolidation belongs to WI-4551 and is intentionally out of scope.

External reference, non-authoritative for GT-KB governance: Omnigent's current policy source at `https://github.com/omnigent-ai/omnigent/blob/main/omnigent/policies/builtins/cost.py` and policy docs at `https://github.com/omnigent-ai/omnigent/blob/main/docs/POLICIES.md` were checked on 2026-06-28 to confirm the cost-policy shape before filing. GT-KB will mirror the pattern only.

## Spec-Derived Verification Plan

Expected implementation tests:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: before protected mutation, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4550-dispatch-cost-budget-policy ...` after LO `GO`; expected: authorization packet created for only the listed target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run bridge preflights; expected: `preflight_passed: true` and blocking clause gaps 0.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and `GOV-AUTOMATION-VALUE-VS-COST-001`: add `platform_tests/scripts/test_dispatch_cost_budget.py` covering default budget parsing, invalid config fallback behavior, fail-closed unknown priced-model behavior, fail-open unpriced behavior, hard-cap launch suppression without `subprocess.Popen`, and durable `dispatch-failures.jsonl` evidence.
- Dispatcher status visibility: extend `platform_tests/scripts/test_bridge_dispatch_config.py` so `config/dispatcher/rules.toml` budget fields parse/report without breaking existing harness selection.

Focused verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_dispatch_cost_budget.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_dispatch_concurrency_cap.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy
```

## Risk / Rollback

Risk: a mis-specified budget could suppress legitimate dispatch. Mitigation: default config must preserve current behavior unless a budget is configured, hard suppressions must be explicit in `dispatch-failures.jsonl`, and unpriced/unknown data behavior must follow WI-4550 rather than surprising operators. Rollback is a single-commit revert of the config/parser/launch-gate/test changes; no database migration is proposed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4550-dispatch-cost-budget-policy`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat — this adds a dispatch capability gate and its tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
