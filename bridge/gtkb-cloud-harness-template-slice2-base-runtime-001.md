NEW
author_identity: claude
author_harness_id: B
author_session_context_id: f0e664f2-35ef-4d46-86a5-5a828f73d30b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder

# Reusable Direct-Cloud Harness Template — Slice 2: shared base runtime + OpenRouter re-base (first-adopter proof)

Work Item: WI-5078
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
target_paths: ["scripts/cloud_harness_base.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_openrouter_harness.py"]

## Summary

Slice 2 of `PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE` implements the source that slice 1's `ADR-CLOUD-HARNESS-TEMPLATE-001` (VERIFIED at bridge `gtkb-cloud-harness-template-slice1-adr-004`) decided: a single, config-driven **cloud harness runtime base** (`scripts/cloud_harness_base.py`) that cloud harnesses instantiate by configuration, and the **re-base of the OpenRouter harness (F)** onto that base as the first-adopter proof. The base owns the machinery every current shim hand-rolls — connection, retry/backoff, fail-closed guard-adapter enforcement, author-metadata injection, and the framework-free tool-call loop — leaving adopters to supply only the varying axes `{endpoint, auth-env-key, API dialect, model, hook-tier}`. OpenRouter is the readiest adopter (already direct-cloud, token auth via an Authorization header keyed on `OPENROUTER_API_KEY`, OpenAI `chat/completions` dialect, guard-adapter floor, mature retry/backoff), so re-basing it validates the base against a real consumer before the sibling adoptions. Per the ADR consequences, **no shim is deleted until its adopter passes on the base**, and full dialect abstraction (`anthropic-messages` native-hook path) plus the generalized tool-parity `DCL` are slice 3 — this slice builds the base + the `openai-chat` dialect concretely + the dialect seam, and re-bases exactly one adopter.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives executable tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal and its implementation report.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the approved architecture this slice implements: config-driven base runtime, the five varying axes, guard-adapter enforcement by construction, and the slice 2 = base + OpenRouter-re-base plan.
- `SPEC-INTAKE-9ec893` — governing principle: harness = integration+model+config; prefer non-GUI, maximal-hook, direct-cloud integrations. The base makes the *integration* reusable so only model/config/endpoint/dialect/hook-tier vary.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract, especially the Layer-3 fail-closed guard adapter, which the base runtime must enforce for every adopter by construction.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the existing fail-closed guard-adapter/tool-parity contract; slice 2 generalizes its *enforcement mechanism* into the shared base (the generalized `DCL` artifact itself is authored in slice 3).
- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the authoritative env SoT; the base references each adopter's auth token by env-key NAME only (`OPENROUTER_API_KEY` for the proof), never by value.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — precedent: the shims are framework-free by design; the base preserves that (no heavyweight agent framework).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the base runtime is a durable, tracked module surface; the superseded per-shim machinery consolidates behind it.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across the template, its base runtime, the OpenRouter adopter, and the confirmed principle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the OpenRouter shim's hand-rolled machinery moves to a superseded state (thinned to config) as it re-bases; no artifact is deleted this slice.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the guard-adapter floor is a cross-cutting requirement the base enforces mechanically for every adopter rather than per-shim.
- `.claude/rules/project-root-boundary.md` — the base module, re-base, and tests all remain within `E:\GT-KB`; the External Harness Executable Resolution Exception continues to govern how the harness resolves its own external executable, unchanged by this slice.

## Prior Deliberations

- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` (owner_decision, 2026-07-08) — the owner directive authorizing the template as a first-class effort with OpenRouter as the first adopter/proof; the authorization this slice implements.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` (architecture_decision, specified, 2026-07-08) — the slice-1 design output; this slice is its slice-2 consequence.
- `DELIB-S422-OR-FRAMEWORK-CHOICE` — selected Python + a framework-free tool loop for the OpenRouter harness; the base preserves the framework-free approach when it absorbs that loop.
- `DELIB-S422-OR-CONFIG-GENERALIZATION` — generalized API-harness configuration into `.api-harness/`; the base reads the same generalized config surface the shim reads, so no config migration is required this slice.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — OpenRouter's registry identity (harness F, type `openrouter`, single-harness model routing); the re-base preserves this identity and the invocation surface unchanged.
- `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` — the sibling Ollama adoption that will re-base onto this same base in a later slice; informs the dialect seam.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CLOUD-HARNESS-TEMPLATE-001` (VERIFIED slice-1 decision) fixes the base-runtime architecture, the five varying axes, and the slice 2 scope (base + OpenRouter re-base, no shim deleted until its adopter passes). `SPEC-INTAKE-9ec893` fixes the reusable-integration principle; `GOV-HARNESS-ONBOARDING-CONTRACT-001` fixes the guard-adapter conformance floor; `DCL-OLLAMA-TOOL-PARITY-GATE-001` fixes the fail-closed guard semantics to generalize. No new or revised requirement is required before this implementation; slice 2 mutates source only, not governance.

## Proposed Change / Scope

On GO plus an implementation-start packet, implement the following within the declared `target_paths`:

1. **New base module `scripts/cloud_harness_base.py`** (framework-free, stdlib + existing project helpers only, following the shims' dual-import pattern so it is importable both as `cloud_harness_base` and `scripts.cloud_harness_base`). The base owns, generalized out of the OpenRouter shim:
   - **Connection + HTTP transport** with the direct-cloud endpoint supplied by config (no localhost-service bridge for adopters).
   - **Retry/backoff** — the OpenRouter shim's mature retry surface (`_retry_after_delay_seconds`, `_http_retry_delay_seconds`, `_is_retryable_provider_transport_error`, deadline-budgeted sleeps) becomes the shared retry policy.
   - **Fail-closed guard-adapter enforcement** — the shim's `invoke_guard_adapter` / `_default_guard_runner` / guard-path derivation becomes the base's mandatory pre-dispatch gate, enforced for every adopter by construction (generalizing the `DCL-OLLAMA-TOOL-PARITY-GATE-001` enforcement mechanism). Every tool call routes through the guard; a deny or an unavailable guard fails closed (no tool execution).
   - **Author-metadata injection** — `set_author_metadata_env` / session-id resolution becomes shared.
   - **Framework-free tool-call loop** — `run_tool_loop` and the tool-dispatch surface (`_dispatch_read/write/edit/grep/glob/bash`, `dispatch_tool_call`, `build_tool_schemas`) become the shared loop.
   - **Config loading** — the routing-config surface (`load_routing_config`, `resolve_model`, `build_system_prompt`) is parameterized by the adopter's config.

2. **Config surface (the five varying axes)** expressed as an explicit adopter configuration object: `endpoint`; `auth-env-key` (token auth via an Authorization header keyed on the adopter's `.env.local` env var NAME, per `GOV-ENV-LOCAL-AUTHORITY-001`); `dialect` (an enum with all three values defined — `ollama-native`, `openai-chat`, `anthropic-messages`); `model` routing; `hook-tier` (guard-adapter floor vs native full hooks). The dialect enum defines all three values so the surface is complete, but only `openai-chat` is *implemented concretely* this slice (see Scope Boundary).

3. **Dialect seam.** The dialect-specific request/response translation is a strategy selected by the `dialect` config value. The `openai-chat` strategy is extracted from the shim's `call_openrouter_chat` (request shaping, tool-call parsing, message extraction). `ollama-native` and `anthropic-messages` are defined seam points that raise an explicit slice-3 `NotImplementedError` sentinel when selected, so the seam is real and the slice-3 build-out is a localized addition rather than a refactor.

4. **Re-base OpenRouter (F).** `scripts/openrouter_harness.py` is reduced to: its adopter config (endpoint `https://openrouter.ai/api/v1`, auth-env-key `OPENROUTER_API_KEY`, dialect `openai-chat`, model routing, hook-tier floor) plus its CLI entry point, delegating all machinery to the base. Behavior is preserved: same routing config, same guard enforcement, same author metadata, same CLI arguments and exit codes.

5. **Regression tests.** Add `platform_tests/scripts/test_cloud_harness_base.py` covering the base directly (config-axis parsing, dialect dispatch incl. the slice-3 sentinel for the two unimplemented dialects, retry/backoff decisions, author-metadata injection, fail-closed guard enforcement, and a tool-loop happy path against a stubbed transport). The existing `platform_tests/scripts/test_openrouter_harness.py` (and `test_openrouter_routing_deepseek.py`) must pass **unchanged** — that unchanged pass is the behavior-preservation proof of the re-base.

6. **No deletion.** `scripts/openrouter_harness.py` stays on disk (now thin). No other shim (`ollama_harness.py`, `cursor_harness.py`) is touched this slice; their consolidation is slice 4 per the ADR.

## Scope Boundary (Slice 2 vs Slice 3 / Slice 4)

Per `ADR-CLOUD-HARNESS-TEMPLATE-001` Consequences, this slice deliberately does NOT:

- implement the `anthropic-messages` dialect or the native full-hook path (slice 3);
- author the generalized tool-parity `DCL` artifact — slice 2 generalizes the *enforcement code*; the generalized `DCL` *spec* is slice 3;
- implement the `ollama-native` dialect or re-base Ollama / Cursor (slice 4 sibling adoptions + remaining consolidation);
- add or change doctor checks or harness-parity surfaces (slice 4).

The dialect enum names all three values (complete config surface, matching the ADR's axis list and the owner's slice-2 axis description), but only `openai-chat` is implemented so the OpenRouter proof is real and the abstraction is validated against exactly one adopter before generalizing further.

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08, `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`): "How should I structure the reusable direct-cloud harness template program?" → **Template + OpenRouter as first adopter**. This is the standing authorization for the program and for building the base + re-basing OpenRouter.
- Owner session directive (2026-07-08): continue the program at slice 2 (implementation), starting with the Template slice-2 base runtime + OpenRouter re-base proof.

These are the authorization for this proposal. No new owner decision is required to proceed: slice 2 is source implementation inside the already-active `PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708` and the VERIFIED `ADR-CLOUD-HARNESS-TEMPLATE-001`. Implementation remains gated by Loyal Opposition GO plus an implementation-start packet derived from that GO.

## Specification-Derived Verification

Executable verification runs from the project venv interpreter. The pre-file code-quality gates (`ruff check` AND `ruff format --check` on every changed `.py`) run before the implementation report is filed.

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (base owns machinery; config-driven) | base module parses the five-axis adopter config and exposes shared connection/retry/guard/author-metadata/tool-loop entry points | `python -m pytest platform_tests/scripts/test_cloud_harness_base.py -q` |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (OpenRouter re-base preserves behavior) | existing OpenRouter regression tests pass unchanged against the re-based shim | `python -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_openrouter_routing_deepseek.py -q` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` (Layer-3 fail-closed guard) | base refuses to execute a tool call when the guard adapter denies OR is unavailable (fail-closed), for every configured adopter | guard-enforcement tests in `test_cloud_harness_base.py` |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` (generalized enforcement) | base guard enforcement mirrors the ollama fail-closed tool-parity semantics (deny/​unavailable → no execution) | guard-parity test in `test_cloud_harness_base.py` |
| `SPEC-INTAKE-9ec893` (direct-cloud, config-driven) | adopter config requires a direct-cloud endpoint; no localhost-service bridge path in the base | config-validation test in `test_cloud_harness_base.py` |
| `GOV-ENV-LOCAL-AUTHORITY-001` (auth by env-key NAME) | base reads the auth token from the environment via the configured env-key NAME; no literal token embedded in source | env-key-resolution test in `test_cloud_harness_base.py` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | spec-to-test mapping present in the implementation report; both ruff gates green on changed `.py` | `ruff check` + `ruff format --check` on changed files |

## Acceptance Criteria

1. `scripts/cloud_harness_base.py` exists — framework-free, config-driven, exposing the shared connection/retry/guard/author-metadata/tool-loop machinery and the five-axis adopter config surface.
2. Dialect seam present: `openai-chat` implemented concretely; `ollama-native` and `anthropic-messages` are defined seam points raising the slice-3 sentinel.
3. `scripts/openrouter_harness.py` re-based to a thin config + CLI adopter on the base; its registry identity, invocation surface, and CLI behavior are unchanged.
4. `platform_tests/scripts/test_openrouter_harness.py` and `test_openrouter_routing_deepseek.py` pass unchanged (behavior-preservation proof).
5. `platform_tests/scripts/test_cloud_harness_base.py` added and passing, covering config parsing, dialect dispatch (incl. slice-3 sentinel), retry, author-metadata, and fail-closed guard enforcement.
6. `ruff check` and `ruff format --check` clean on every changed `.py`.
7. No shim deleted; no dialect beyond `openai-chat` implemented; no doctor/parity change (slice-boundary respected).

## Risks / Rollback

- **Risk:** premature abstraction — a base fit to one adopter may under-serve `anthropic-messages`. **Mitigation:** the dialect seam is explicit and the OpenRouter proof validates the base against a real re-base before sibling adoption; the config surface is the minimal five-axis set the ADR fixed.
- **Risk:** the re-base regresses OpenRouter-specific behavior (retry maturity, guard details, routing). **Mitigation:** the existing OpenRouter regression tests must pass unchanged; the shim is not deleted; the change is one adopter behind the guard-adapter floor.
- **Risk:** guard-enforcement generalization weakens the fail-closed semantics. **Mitigation:** explicit deny-and-unavailable fail-closed tests in the base test module, derived from `DCL-OLLAMA-TOOL-PARITY-GATE-001`.
- **Rollback:** the base module is new (removable) and the OpenRouter re-base is a single-file revert to its pre-slice-2 content; no governance, config, registry, or sibling shim is mutated, so rollback is a two-file revert plus removal of the new test.

## Recommended Commit Type

`feat:` — slice 2 adds a net-new base runtime module and a new capability surface (config-driven cloud-harness base), with the OpenRouter re-base and new regression tests as supporting changes.
