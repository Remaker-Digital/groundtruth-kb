NEW
author_identity: claude
author_harness_id: B
author_session_context_id: c6f54cd8-c03e-4eda-bb2f-97d2c392b40f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

# Defect-Fix Proposal - OpenRouter Routing Re-Pointed to Cost-Optimized DeepSeek Models (WI-4476)

bridge_kind: prime_proposal
Document: gtkb-openrouter-routing-deepseek-cost-optimization
Version: 001
Date: 2026-06-12 UTC

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4476
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Program: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH (top-priority program; priority grouping)

target_paths: [".api-harness/routing.toml", "platform_tests/scripts/test_openrouter_routing_deepseek.py"]

## Claim

The OpenRouter LO harness (harness F, precedence 30) dispatches but every request returns HTTP 404 `No allowed providers are available for the selected model`, because `.api-harness/routing.toml` points its `provider="openrouter"` models at `google/gemini-2.5-pro` and `qwen/qwen-2.5-coder-32b-instruct` — providers the owner's OpenRouter account does NOT allow (Gemini/GPT are not available on this account). The owner widened the account guardrail so DeepSeek/Qwen are eligible and confirmed `deepseek/deepseek-v4-pro` as the target.

This proposal re-points the two `provider="openrouter"` rows (and the `[routing.openrouter]` default + skill routes) at cost-optimized, account-eligible, tool-calling DeepSeek models, verified live against the account's `/models` surface. No `openrouter_harness.py` code change is required (the harness already reaches the API and is provider-aware; the 404 was purely the configured model slugs). This makes harness F (the precedence-30 middle backstop in the cost-optimized dispatch ladder) actually dispatchable.

## Defect / Reproduction

**Root cause (config).** `.api-harness/routing.toml` `[models.gemini-2-5-pro].model_id = "google/gemini-2.5-pro"` and `[models.qwen-2-5-coder].model_id = "qwen/qwen-2.5-coder-32b-instruct"`; `[routing.openrouter].default_model = "gemini-2-5-pro"`. The account allows providers `[alibaba, deepseek, moonshotai]`; the configured models are hosted by `[google, openai, azure]` → every OpenRouter request 404s with `No allowed providers`. `dispatch-failures.jsonl` records `loyal-opposition:F` `subprocess_execution_failed` → circuit breaker tripped.

**Verified-good (already confirmed in WI-4476 diagnosis).** `OPENROUTER_API_KEY` valid (`GET /api/v1/auth/key` -> 200); endpoint correct; `GET /models` -> 200. The failure is solely the configured model slugs vs. the account allow-list.

**Live slug verification (2026-06-12, this session).** Queried `https://openrouter.ai/api/v1/models` with the account key; confirmed exact eligible slugs + pricing:
- `deepseek/deepseek-v4-pro` — ctx 1,048,576, $0.44 / $0.87 per M (owner-confirmed primary).
- `deepseek/deepseek-v4-flash` — ctx 1,048,576, $0.10 / $0.20 per M (cheapest DeepSeek; cost-optimized secondary).
- (Also eligible: `qwen/qwen3-235b-a22b-thinking-2507` $0.10/$0.10, and others — not selected here.)

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `.api-harness/routing.toml` and `platform_tests/scripts/test_openrouter_routing_deepseek.py`. Note: `.api-harness/routing.toml` is NOT a gate-protected path under `scripts/implementation_start_gate.py` (it is outside the protected-path set), so its edit is authorized by the bridge GO per `.claude/rules/codex-review-gate.md` rather than by an implementation-start packet. The new test under `platform_tests/` IS gate-protected and is a clean `test_addition`.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` governs the `.api-harness/routing.toml` schema (per-model `model_id`, `provider`, `tool_calling_supported`, `allowed_tools`; a `[routing.<provider>]` table with `default_model`). This change conforms to that schema; the model_id values change, the structure does not. No new or revised requirement is required.

## Standing Fast-Lane Eligibility

WI-4476 qualifies for `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` governed by `GOV-RELIABILITY-FAST-LANE-001`:
- **Defect/Reliability focus:** P1 defect fix removing a 404 failure class for the OpenRouter LO backend.
- **Authorized mutation classes:** the new test is `test_addition` (within the PAUTH); the routing.toml edit is on a non-gate-protected config path (authorized by the GO, not by a mutation-class packet).
- **No forbidden mutations:** no deploy, force-push, or spec deletion; no formal spec mutation.
- **Membership coverage:** WI-4476 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES` (membership-based PAUTH) and of the top-priority `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH` program.

## Specification Links

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` — **Primary domain spec.** Governs the routing.toml schema this change edits while preserving structure.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — the static-routing.toml mechanism the multi-provider harness pool consumes.
- `GOV-RELIABILITY-FAST-LANE-001` — standing fast-lane governance; eligibility above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical; this follows the file-bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant cross-cutting specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps the change to an executable test + a live readiness check.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project Authorization metadata present.
- `GOV-STANDING-BACKLOG-001` — WI-4476 is the standing-backlog work item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — captured-defect -> scoped-fix progression.

## Prior Deliberations

- WI-4476 (this work item) — records the 2026-06-12 diagnosis (account allow-list vs configured model slugs) and the GT-KB-side companion fix.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` — owner directive making cost-optimized automatic dispatch a top-priority program (this proposal is a member's enabling fix).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner directive authorizing the reliability fast-lane standing authorization.
- `bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md` (NEW) — the sibling cheap-harness fix (WI-4473, ollama provider validation); both restore a cost-optimized LO backend.
- No prior deliberation specific to the OpenRouter DeepSeek model selection exists; semantic search (2026-06-12) returned no match.

## Owner Decisions / Input

- **Owner directive (2026-06-12, this session):** the owner confirmed `deepseek/deepseek-v4-pro` as the OpenRouter target model and directed cost-optimized automatic dispatch as top-priority work; the account guardrail was widened so DeepSeek/Qwen are eligible (Gemini/GPT are not). This is the owner direction for the model selection in this proposal.
- **Project authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (membership-based; owner authorization `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-4476's `test_addition`; the routing.toml config edit is authorized by this bridge GO (non-gate-protected path).
- No NEW owner decision is required for implementation beyond this GO. (Cross-harness auto-dispatch is currently OFF via the emergency kill-switch; this proposal awaits a MANUAL Loyal Opposition review.)

## Proposed Scope

**IP-1 - Re-point OpenRouter routing (`.api-harness/routing.toml`).**

Replace the two `provider="openrouter"` model rows and the `[routing.openrouter]` references:

```toml
[models.deepseek-v4-pro]
model_id = "deepseek/deepseek-v4-pro"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[models.deepseek-v4-flash]
model_id = "deepseek/deepseek-v4-flash"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.openrouter]
default_model = "deepseek-v4-pro"
timeout_seconds = 240

[routing.openrouter.skills]
bridge-review = "deepseek-v4-pro"
verification = "deepseek-v4-pro"
implementation = "deepseek-v4-pro"
```

- The `provider="ollama"` rows (`qwen3-coder-next-cloud`, `kimi-k2-6-cloud`) and `[routing.ollama]` are UNTOUCHED — this change is openrouter-scoped.
- Model keys are renamed (`gemini-2-5-pro` -> `deepseek-v4-pro`, `qwen-2-5-coder` -> `deepseek-v4-flash`) so the key reflects the model; `default_model` + skill routes updated in lockstep so `load_routing_config`'s `default_model in models` + skill-route validation still pass.

**IP-2 - Test (`platform_tests/scripts/test_openrouter_routing_deepseek.py`; new file = clean test_addition).**

Structural validity (no live API; that is the readiness check below):
- `test_openrouter_routing_loads`: `openrouter_harness.load_routing_config(project_root)` succeeds against the live `.api-harness/routing.toml`.
- `test_openrouter_models_are_deepseek_eligible`: every loaded model's `model_id` starts with `deepseek/` (account-eligible provider) and `provider == "openrouter"`.
- `test_openrouter_default_resolves`: `[routing.openrouter].default_model` resolves to a configured DeepSeek model with `tool_calling_supported` true.
- `test_ollama_rows_unaffected`: the ollama loader still loads only its own provider rows (the openrouter change did not perturb ollama routing) — guards cross-provider isolation.

## Specification-Derived Verification Plan

| Spec / requirement | Derived test / evidence | Command |
|---|---|---|
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (schema preserved; default resolves) | `test_openrouter_routing_loads`, `test_openrouter_default_resolves` | `python -m pytest platform_tests/scripts/test_openrouter_routing_deepseek.py -q` |
| WI-4476 (account-eligible models; no 404) | `test_openrouter_models_are_deepseek_eligible` (config) + **live readiness check** (functional) | pytest above; + `python scripts/openrouter_harness.py` readiness/probe or a single live chat call returning non-404 |
| cross-provider isolation (ollama unaffected) | `test_ollama_rows_unaffected` | same |
| `GOV-RELIABILITY-FAST-LANE-001` scope | `git diff --stat` = exactly the two target paths | `git diff --stat` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on changed Python (the test) | `ruff check`; `ruff format --check` |

The live readiness check (non-404 from `deepseek/deepseek-v4-pro`) is run at implementation time and recorded in the post-impl report; a unit test cannot assert "no 404" without the live API.

## Acceptance Criteria

1. `.api-harness/routing.toml` `provider="openrouter"` rows resolve to account-eligible DeepSeek models; `[routing.openrouter].default_model` resolves to `deepseek-v4-pro`.
2. `openrouter_harness.load_routing_config` loads the new config without error; ollama routing is unaffected.
3. A live OpenRouter request via the harness for `deepseek/deepseek-v4-pro` returns non-404 (the 404 class is closed).
4. New tests pass; `ruff check`/`ruff format --check` clean on the changed Python; change set is exactly the two target paths.
5. Applicability preflight `missing_required_specs: []`; clause preflight no blocking gaps.

## Risks / Rollback

- **Risk - `deepseek/deepseek-v4-pro` lacks tool-calling on OpenRouter.** Mitigation: the live readiness check at implementation verifies a tool-calling request succeeds; DeepSeek v4 supports OpenAI-style tools. If unsupported, fall back to a confirmed tool-calling eligible model (the proposal's secondary or `qwen/qwen3-235b-a22b-thinking-2507`) and re-verify.
- **Risk - key rename misses a `[routing.openrouter]` reference.** Mitigation: `load_routing_config` fails closed if `default_model`/skill routes don't resolve to a configured model; `test_openrouter_default_resolves` catches it.
- **Rollback:** revert the routing.toml rows and delete the new test file; no state migration.

## Files Expected To Change

- `.api-harness/routing.toml` (openrouter rows + `[routing.openrouter]` only)
- `platform_tests/scripts/test_openrouter_routing_deepseek.py` (new)

## Recommended Commit Type

`fix` - repairs a P1 defect (OpenRouter 404 / wrong account-ineligible model slugs) restoring a cost-optimized LO dispatch backend; no new capability surface.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-001.md` with a matching `NEW` status line at the top of this Document's INDEX entry; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` honored. Cross-harness auto-dispatch is OFF (emergency kill-switch); this thread awaits a manual Loyal Opposition review.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
