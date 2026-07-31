NEW
::init gtkb lo
::open build

# WI-5628 - Reconcile harness D to the canonical DeepSeek V4 Flash review route

bridge_kind: prime_proposal
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 001
Author: Master Prime Builder (Codex, harness A, interactive)
Date: 2026-07-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive; resolved role prime-builder via ::init gtkb pb; Master Prime Builder program session

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5628

target_paths: ["harness-state/harness-registry.json", "groundtruth-kb/harness-state/harness-registry.json"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Reconcile harness D's canonical headless invocation with the already-active
DeepSeek V4 Flash routing and dispatcher model authorities. The current harness
registry explicitly passes `--model kimi-k2-7-code-cloud`, while
`.api-harness/routing.toml` resolves Ollama bridge review to
`deepseek-v4-flash-cloud` and `gt bridge dispatch config --json` reports the
same DeepSeek label. The Kimi route has just failed live with HTTP 429, while
recent DeepSeek V4 Flash capacity probes completed successfully.

Implementation is one canonical `gt harness set-invocation-surface`
transaction. It changes only D's explicit headless model argument from
`kimi-k2-7-code-cloud` to `deepseek-v4-flash-cloud`; all command paths,
placeholders, skill selection, max-items value, roles, eligibility, ranking,
caps, and unrelated registry records remain unchanged. No source code,
dispatcher rule, API-harness routing, credential, daemon, or live-worker
mutation is in scope.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires truthful canonical
  dispatch identity and a reliable headless Loyal Opposition lane.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires configuration changes to
  flow through governed control surfaces and remain owner-visible.
- `ADR-CROSS-HARNESS-PARITY-001` - requires headless invocation and
  owner-visible model identity to agree.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  projection mutation and independent VERIFIED after live proof.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links the correction to concrete governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries
  the active project, PAUTH, work item, and exact target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires
  executing TEST-11673's authority-agreement and live-completion checks.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires
  this PAUTH, exact GO, work-intent claim, and implementation-start packet.
- `GOV-WORK-TREE-HYGIENE-001` - the transaction must preserve all unrelated
  dirty registry and dispatcher changes.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - authorizes the
  isolated replacement program and makes at least one reliable independent LO
  reviewer a mandatory readiness invariant.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` - establishes that Ollama model
  selection must come from the routing source of truth rather than an
  uncoordinated hardcoded identity.

Prior verified bridge work supplied the control mechanism but does not authorize
this new direction change: WI-4964 implemented canonical invocation-surface
updates, and WI-5070 implemented the governed dispatcher model-label setter.
WI-5047 is terminally WITHDRAWN after its Kimi route work was superseded.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` captures the owner's
instruction to derive and close upstream reliability work while delivering a
reliable headless reviewer. The owner's accepted design also names DeepSeek V4
Fast as the model expected to verify and validate this coarse-grained program.
No additional owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, and
`ADR-CROSS-HARNESS-PARITY-001` require one truthful, governed route identity;
TEST-11673 states an unambiguous live acceptance outcome.

## Specification-Derived Verification Plan

| Specification / decision | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Execute TEST-11673: allow the live daemon to dispatch D against an independently reviewable NEW/REVISED/NO-ACTION thread and inspect the resulting dispatch run plus numbered bridge artifact. | Provider process exits 0 and publishes one valid, substantive, independently authored LO verdict; no HTTP 429, status mismatch, or residual circuit breaker. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Capture `gt harness show --harness D`, run one `gt harness set-invocation-surface` transaction with the existing JSON except for the model argument, then re-run `gt harness show --harness D`. | Canonical version increments once; only the model argument and append-only change metadata differ. |
| `ADR-CROSS-HARNESS-PARITY-001` | Run a resolver probe through `scripts.ollama_harness.load_routing_config` / `resolve_model`, plus `gt bridge dispatch config --json`. | Registry argv, resolver route key, provider model id, and dispatcher label all identify `deepseek-v4-flash-cloud` / `deepseek-v4-flash:cloud`. |
| Existing canonical writer and readiness behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` | Focused harness invocation, projection, and Ollama dispatch tests pass without regression. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare before/after structured D records and `git diff -- harness-state/harness-registry.json groundtruth-kb/harness-state/harness-registry.json`. | No A/B/C/E/F/H record, D role/eligibility/cap/ranking field, routing file, or dispatcher rule changes. |
| Bridge and authorization gates | Run applicability and clause preflights, acquire the exact work-intent claim, and begin implementation authorization after GO. | All gates pass; the packet target set equals the two listed registry projections. |

## Risk / Rollback

Risk is limited but operational: a wrong route key could make D unavailable or
could overwrite unrelated registry state if the full headless object is rebuilt
incorrectly. Mitigation is a structured before/after comparison, use of the
canonical append-only writer, and a live provider proof before VERIFIED.

Rollback uses the same `gt harness set-invocation-surface` command to restore
the exact pre-change headless object if DeepSeek V4 Flash fails the live test.
Bridge and MemBase history remain append-only. Existing F workers and all
dispatcher eligibility, cap, rule, and daemon state remain untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5628-deepseek-v4-flash-route-reconciliation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - reconciles an active model-authority defect without adding a feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
