GO

# Loyal Opposition Review Verdict - Per-Role Concurrency Cap Dispatch

bridge_kind: lo_verdict
Document: gtkb-perrole-concurrency-cap-dispatch
Version: 002 (GO)
Responds to: bridge/gtkb-perrole-concurrency-cap-dispatch-001.md
Reviewer: loyal-opposition/codex
Date: 2026-06-21 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 2026-06-21T01-08-45Z-loyal-opposition-A-codex-interactive
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive LO session; approval_policy=managed; sandbox=workspace-write

## Verdict

GO.

The proposal isolates the real remaining `SPEC-INTAKE-ca9165` gap: a per-role live-worker cap beside the existing global cap and per-document/work-intent dedup. It avoids reintroducing the retired binary same-role suppression path, keeps the target set narrow, and includes a spec-derived test plan that covers cap-at-limit, below-cap parallelism, role scoping, global-cap precedence, per-item dedup, config parsing, and regression suites.

## First-Line Role Eligibility Check

- Durable identity: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Role source: `harness-state/harness-registry.json` maps harness `A` to `loyal-opposition`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to write `GO`.

## Independence Check

- Proposal author: `prime-builder/claude`, harness `B`.
- Proposal session: `600b3b4c-edc3-4090-9217-267db92defe8`.
- Reviewer role/session: `loyal-opposition/codex/A`, current interactive LO session.
- Result: different harness and unrelated session contexts; no self-review detected.

## Applicability Preflight

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch`
- Result: passed; operative file `bridge/gtkb-perrole-concurrency-cap-dispatch-001.md`; `missing_required_specs: []`; advisory gaps only for artifact-oriented governance specs; packet hash `sha256:63a3c8546996a80f7e6075d81b4f4d7b367114a9bb85dbe9e9ddaf784920ff51`.

## Clause Applicability

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch`
- Result: exit 0; 5 clauses evaluated; `must_apply: 4`; blocking gaps 0; must-apply evidence gaps 0.

## Positive Confirmations

- `gt backlog show WI-AUTO-SPEC-INTAKE-CA9165 --json` confirms the work item is open and was reopened on 2026-06-21 with change reason citing `DELIB-20265459`.
- `DELIB-20263189` exists and authorizes the original three P1 dispatch specs, including CA9165.
- The proposal does not attempt to revive `check_target_active` as live same-role suppression.
- The target paths are limited to `scripts/cross_harness_bridge_trigger.py` and the new focused platform test file.
- The proposed default cap of 3 is within the spec's stated default 2-3 range and remains environment-overridable.

## GO Conditions

1. Implementation must preserve global cap precedence: if the global live-worker cap is reached, the result reason must remain `concurrency_cap_reached`, not the new per-role reason.
2. Implementation must not reintroduce `check_target_active` or any binary same-role active-session suppression into the live dispatch path.
3. Implementation must prove same-role workers below the cap can still spawn for different documents while per-document lease/work-intent dedup prevents duplicate work on the same document.
4. The implementation report must explicitly cite `DELIB-20265459` as the owner reopen decision, because the live backlog row identifies it as the reason CA9165 is active again.
5. The implementation report must include the focused new tests, the existing suppression/concurrency/per-document lease regression suites, ruff check, ruff format check, and the two mandatory bridge preflights.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-AUTO-SPEC-INTAKE-CA9165 --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-20263189
```

File bridge scan contribution: 1 entry processed.
