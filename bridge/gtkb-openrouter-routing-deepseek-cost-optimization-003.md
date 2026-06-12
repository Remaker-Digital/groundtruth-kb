NEW
author_identity: claude
author_harness_id: B
author_session_context_id: c6f54cd8-c03e-4eda-bb2f-97d2c392b40f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

# Post-Implementation Report - OpenRouter Routing Re-Pointed to Cost-Optimized DeepSeek (WI-4476)

bridge_kind: prime_report
Document: gtkb-openrouter-routing-deepseek-cost-optimization
Version: 003
Date: 2026-06-12 UTC

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4476
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Program: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Implements: bridge/gtkb-openrouter-routing-deepseek-cost-optimization-001.md (NEW)
Authorized by: bridge/gtkb-openrouter-routing-deepseek-cost-optimization-002.md (GO, Loyal Opposition)
Implementation-start packet: sha256:b2f978e54338f2dab64a97fdb0f7f50796d487c812db3eeae07c335f2bc0be78

target_paths: [".api-harness/routing.toml", "platform_tests/scripts/test_openrouter_routing_deepseek.py"]

## Summary

Implemented the GO'd proposal (`-001`, GO at `-002`): re-pointed the two `provider="openrouter"`
rows in `.api-harness/routing.toml` (and the `[routing.openrouter]` default + skill routes) from
the account-ineligible `google/gemini-2.5-pro` / `qwen/qwen-2.5-coder-32b-instruct` (which 404'd
with "No allowed providers") to cost-optimized, account-eligible DeepSeek models. No
`openrouter_harness.py` code change. Diff is `8 insertions / 8 deletions` to the config plus a new
test file — exactly the two authorized target paths. A live OpenRouter call confirms the 404 class
is closed (HTTP 200, tool-calling accepted).

## Implemented Changes

**IP-1 - `.api-harness/routing.toml` (openrouter-scoped only; ollama rows untouched).**

- `[models.gemini-2-5-pro]` (`google/gemini-2.5-pro`) -> `[models.deepseek-v4-pro]` (`deepseek/deepseek-v4-pro`; $0.44/$0.87 per M, 1.05M ctx).
- `[models.qwen-2-5-coder]` (`qwen/qwen-2.5-coder-32b-instruct`) -> `[models.deepseek-v4-flash]` (`deepseek/deepseek-v4-flash`; $0.10/$0.20 per M, 1.05M ctx).
- `[routing.openrouter].default_model` and all three skill routes (`bridge-review`, `verification`, `implementation`) -> `deepseek-v4-pro` (keys renamed in lockstep so `load_routing_config`'s `default_model in models` + skill-route validation still pass).
- Slugs were verified live against the account's `GET /models` before editing.

**IP-2 - Tests (`platform_tests/scripts/test_openrouter_routing_deepseek.py`; new file = clean test_addition).** 6 tests: fixture loader behavior + a live-config invariant guarding against regression to account-ineligible providers.

## Specification Links

Carried forward from the GO'd proposal `-001`:

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - the routing.toml schema preserved (model_id values changed, structure unchanged).
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - static-routing.toml mechanism.
- `GOV-RELIABILITY-FAST-LANE-001` - fast-lane scope (test is `test_addition`; the `.api-harness/routing.toml` edit is on a non-gate-protected path, authorized by the GO).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`;
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Spec-to-Test Mapping

| Spec / requirement (clause) | Derived test / evidence | Result |
|---|---|---|
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (schema preserved; default/skills resolve) | `test_openrouter_default_resolves_to_deepseek`, `test_openrouter_skill_route_resolves` | PASS |
| WI-4476 (account-eligible models; no `google/`/`openai/`) | `test_live_openrouter_models_are_account_eligible` | PASS |
| WI-4476 (no 404; tool-calling) | **live OpenRouter call** `deepseek/deepseek-v4-pro` with a tool | PASS (HTTP 200, reply "OK", finish_reason stop) |
| cross-provider isolation (ollama loader ignores openrouter) | `test_ollama_loader_ignores_openrouter_rows`, `test_openrouter_loads_only_openrouter_models` | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` scope | `git diff --stat` = exactly the two target paths | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the changed Python | PASS |

## Commands Executed And Results

```text
python -m pytest platform_tests/scripts/test_openrouter_routing_deepseek.py -q
=> 6 passed in 0.22s

python -m ruff check platform_tests/scripts/test_openrouter_routing_deepseek.py
=> All checks passed!
python -m ruff format --check platform_tests/scripts/test_openrouter_routing_deepseek.py
=> 1 file already formatted

git diff --stat -- .api-harness/routing.toml
=> 1 file changed, 8 insertions(+), 8 deletions(-)   (+ new test file; only the two target paths)

# Live readiness (acceptance criterion 3 - the unit tests cannot assert "no 404"):
POST https://openrouter.ai/api/v1/chat/completions  model=deepseek/deepseek-v4-pro  (with a tool)
=> HTTP 200 ; model=deepseek/deepseek-v4-pro-20260423 ; reply="OK" ; finish_reason=stop ;
   usage prompt=261 completion=21   (tool-calling accepted; the 404 class is closed)
```

## Acceptance Criteria Check (from proposal -001)

1. `provider="openrouter"` rows resolve to account-eligible DeepSeek models; default -> `deepseek-v4-pro` - PASS.
2. `openrouter_harness.load_routing_config` loads the new config; ollama routing unaffected - PASS.
3. Live request for `deepseek/deepseek-v4-pro` returns non-404 - PASS (HTTP 200, tool accepted).
4. New tests pass; ruff clean; change set is exactly the two target paths - PASS.
5. Applicability preflight `missing_required_specs: []`; clause preflight no blocking gaps - PASS (carried from GO-002 evidence on -001).

## Owner Decisions / Input

- **Owner directive (2026-06-12):** owner confirmed `deepseek/deepseek-v4-pro` as the OpenRouter target and directed cost-optimized automatic dispatch as top-priority work (`DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`); the account guardrail was widened so DeepSeek/Qwen are eligible. "on GO, implement."
- **Project authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (membership-based; `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`); impl-start packet `sha256:b2f978e...` minted from the `-002` GO.
- No NEW owner decision required for verification.

## Prior Deliberations

- `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-001.md` (NEW) + `-002.md` (GO).
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`; `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.
- `bridge/gtkb-ollama-harness-provider-scoped-model-validation-003.md` - the sibling cheap-harness fix (WI-4473) post-impl report (same program).

## Recommended Commit Type

`fix` - repairs a P1 defect (OpenRouter 404 from account-ineligible model slugs) restoring a cost-optimized LO dispatch backend; no new capability surface.

## Bridge Protocol Compliance

Filed as `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-003.md` with status `NEW` (post-implementation report) at the top of this Document's INDEX entry, per the `GO -> NEW` post-impl transition. Append-only; `bridge/INDEX.md` canonical. Awaits Loyal Opposition `VERIFIED`. Working-tree changes left uncommitted pending VERIFIED.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
