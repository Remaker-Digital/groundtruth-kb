NEW
author_identity: claude
author_harness_id: B
author_session_context_id: f0e664f2-35ef-4d46-86a5-5a828f73d30b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder

# Reusable Direct-Cloud Harness Template — Slice 3: dialect abstraction (anthropic-messages) + native-hook-path seam + generalized tool-parity DCL

Work Item: WI-5078
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", ".groundtruth/formal-artifact-approvals/*DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001.json"]

## Summary

Slice 3 of `PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE` implements the second consequence of `ADR-CLOUD-HARNESS-TEMPLATE-001`: **dialect abstraction incl. `anthropic-messages` + the native-hook-path seam + the generalized tool-parity DCL**. Slice 2 built the base runtime with a dialect *seam* (enum + `resolve_dialect_chat_func`) and one concrete dialect (`openai-chat`, proven by re-basing OpenRouter). Slice 3 (a) generalizes the tool loop into a dialect-strategy abstraction so request-build and response-parse are dialect-owned (the loop control flow stays shared), (b) implements the `anthropic-messages` dialect concretely (the Anthropic `/v1/messages` protocol: top-level `system`, content-block `tool_use`/`tool_result`, `input_schema` tools, configurable `x-api-key` vs `Authorization` auth), (c) adds the native-hook-path **seam + `hook_tier=native-full-hooks` capability flag** while keeping the fail-closed guard-adapter floor as the enforced mechanism, and (d) authors the generalized tool-parity DCL that binds every cloud-harness-base adopter (generalizing `DCL-OLLAMA-TOOL-PARITY-GATE-001`). Per the owner AUQ (`DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE`), the concrete native-full-hook *wiring* is deferred to slice 4, proven against the first real Anthropic adopter (Alibaba Cloud Studio). No adopter re-bases in this slice (OpenRouter stays `openai-chat`; Ollama/Alibaba adopt in slice 4).

## Implementation Dependency / Sequencing

This slice modifies `scripts/cloud_harness_base.py`, which slice 2 created and which is **awaiting `VERIFIED`** on thread `gtkb-cloud-harness-template-slice2-base-runtime` (currently `NEW` at -003). This proposal is filed for **design review in parallel**; its implementation-start is gated on: (1) slice-2 `VERIFIED` and its verified paths committed, and (2) this slice's own Loyal Opposition `GO` plus an implementation-start packet. Loyal Opposition may `GO` the design; Prime Builder will not run `implementation_authorization begin` for this slice until slice 2 is VERIFIED+committed, to avoid stacking unverified base-runtime changes.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives executable tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the approved architecture: slice 3 = dialect abstraction incl. `anthropic-messages` + native-hook path + generalized tool-parity DCL.
- `SPEC-INTAKE-9ec893` — the maximal-hook / direct-cloud principle the native-hook path operationalizes; the dialect abstraction keeps integration reusable so only dialect/model/config vary.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the Layer-3 fail-closed guard adapter the base enforces for every adopter and dialect (the native-hook tier does not relax it).
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the per-shim tool-parity contract this slice generalizes into a template-wide DCL.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — framework-free precedent; the anthropic-messages transport stays stdlib `urllib`, no agent framework.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the native-hooks-vs-guard-adapter-fallback precedent; the native-hook path is the template's expression of that distinction (tier flag now; wiring slice 4).
- `GOV-20` — Architecture Decision Governance context for the generalized DCL (a design_constraint derived from `ADR-CLOUD-HARNESS-TEMPLATE-001`).
- `GOV-ARTIFACT-APPROVAL-001` — the generalized tool-parity DCL is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `GOV-ENV-LOCAL-AUTHORITY-001` — the anthropic-messages auth token is referenced by env-key NAME; the dialect supports `x-api-key` and `Authorization` auth styles without embedding a literal token.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the base + generalized DCL are durable tracked artifacts; the generalized DCL supersedes the ollama-specific DCL's scope (the ollama DCL remains valid for the not-yet-re-based ollama shim until slice 4).
- `.claude/rules/project-root-boundary.md` — all changed files remain within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE` (owner_decision, 2026-07-08) — the owner AUQ fixing this slice's native-hook-path scope (seam + flag; prove wiring with adopter in slice 4).
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` (owner_decision) — the program authorization.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the slice-3 scope source (Consequences).
- `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` (owner_decision) — owner intent for Anthropic-compatible full hooks on a cloud harness; the native-hook path is the template mechanism that will serve it (Ollama re-base is slice 4).
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` (owner_decision) — Alibaba Cloud Studio (Anthropic endpoint) is the first anthropic-messages adopter (slice 4) that will prove the native-hook wiring.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the per-shim contract being generalized.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CLOUD-HARNESS-TEMPLATE-001` fixes the dialect-abstraction + native-hook-path + generalized-DCL scope; the owner AUQ (`DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE`) fixes the native-hook depth; `DCL-OLLAMA-TOOL-PARITY-GATE-001` fixes the tool-parity semantics to generalize. No new or revised requirement is needed before implementation; the generalized DCL is authored (not a pre-req requirement) under `GOV-ARTIFACT-APPROVAL-001`.

## Proposed Change / Scope

On slice-2 VERIFIED, a slice-3 GO, and an implementation-start packet, implement within the declared `target_paths`:

1. **Dialect-strategy abstraction in `cloud_harness_base.py`.** Introduce a dialect-strategy layer so `run_tool_loop` is dialect-agnostic. Each dialect owns: `chat(endpoint, api_key, payload, timeout)` (transport), `build_request(messages, model_route, system_prompt, tool_schemas)` (dialect-shaped payload), `parse_message(response)` (→ the normalized internal `{content, tool_calls}` shape the loop already consumes), `build_tool_schemas(allowed_tools)` (dialect tool format), and `response_model_id(response)` (author-metadata). The existing `openai-chat` behavior is **extracted into an OpenAI-chat strategy with byte-identical behavior** — the slice-2 regression + base tests (49 + 18 = 67) must pass **unchanged**; the loop's tool-dispatch, guard enforcement, no-progress dedup, session-timeout, and author-metadata paths stay shared and unchanged.

2. **`anthropic-messages` dialect (concrete).** Implement `anthropic_messages_completion` + the Anthropic strategy:
   - URL `<endpoint>/messages`; headers configurable by adopter `auth_style` — `x-api-key: <token>` + `anthropic-version` (native Anthropic) OR `Authorization: Bearer <token>` for Anthropic-compatible cloud endpoints that reject `x-api-key` (the class behind Ollama upstream issue #16922); token by env-key NAME per `GOV-ENV-LOCAL-AUTHORITY-001`.
   - Request: top-level `system` (from system_prompt), `max_tokens`, `messages` translated to Anthropic content blocks (assistant `tool_use` blocks, user `tool_result` blocks), `tools` with `input_schema`.
   - Response parse: concatenate `text` blocks for final text; normalize `tool_use` blocks (`id`/`name`/`input`) into the internal tool-call shape so tool dispatch is unchanged; treat `stop_reason == "tool_use"` as tool-call turns.
   - Same bounded retry/backoff + fail-closed transport-error handling as `openai-chat` (shared helpers), with the provider `label` parameterized.
   - `AdopterProfile` gains the fields the dialect needs (e.g., `auth_style`, `anthropic_version`, `max_tokens`) with `openai-chat`-safe defaults so the OpenRouter profile is unaffected.

3. **Native-hook-path seam + `hook_tier=native-full-hooks` flag.** Accept and validate `native-full-hooks` as a hook tier; document the seam (the extension point where slice 4 wires the full hook lifecycle for a live Anthropic adopter). **The enforced mechanism remains the fail-closed guard-adapter floor for all tiers** — a test asserts that mutating tools route through the floor regardless of `hook_tier`. No full-hook lifecycle wiring is implemented this slice (owner AUQ; slice 4 proves it with Alibaba CS).

4. **Generalized tool-parity DCL.** Author `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` (MemBase `type=design_constraint`) via the governed `gt spec record` formal-artifact path (`GOV-ARTIFACT-APPROVAL-001` packet, owner-presented). Constraint: any cloud harness instantiating `cloud_harness_base` MUST route mutating tools (Write/Edit/Bash) through the base's fail-closed guard adapter, for **all dialects and hook tiers**; `allowed_tools ⊆` the canonical six; fail-closed on any guard deny/error/missing/out-of-root/empty/malformed; author-metadata rule; destructive-gate delegation. It generalizes `DCL-OLLAMA-TOOL-PARITY-GATE-001` (which remains valid for the not-yet-re-based ollama shim until slice 4) and records the base's by-construction enforcement as the satisfying mechanism.

5. **Regression tests** in `test_cloud_harness_base.py`: anthropic-messages request-build (system/messages/tools/tool_result translation), response-parse (text + tool_use normalization), both auth styles (`x-api-key` and `Authorization`), retry parity, a full tool-loop round-trip against a stubbed anthropic transport, the `native-full-hooks` tier acceptance + floor-still-enforced assertion, and the OpenAI-strategy behavior-preservation (existing tests unchanged).

## Scope Boundary (Slice 3 vs Slice 4)

Slice 3 does NOT: re-base any adopter (OpenRouter stays `openai-chat`; Alibaba/Ollama adopt in slice 4); wire the concrete native-full-hook lifecycle (slice 4, proven on Alibaba's live endpoint per the owner AUQ); implement `ollama-native` dialect (slice 4 with the Ollama re-base); change doctor/parity surfaces (slice 4); or retire `DCL-OLLAMA-TOOL-PARITY-GATE-001` (it remains valid until the ollama shim re-bases).

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08, archived as `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE`): native-hook-path scope for slice 3 → **seam + `hook_tier` flag; guard-adapter floor stays enforced; concrete native-full-hook wiring proven with Alibaba CS in slice 4.**
- `AskUserQuestion` (2026-07-08, `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`): the standing program authorization (template + first-adopter proof).
- Owner session directive (2026-07-08): draft the slice-3 proposal.

These authorize the proposal. Implementation remains gated on slice-2 VERIFIED + a slice-3 Loyal Opposition GO + an implementation-start packet; the generalized DCL insert remains gated on its `GOV-ARTIFACT-APPROVAL-001` packet.

## Specification-Derived Verification

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (dialect abstraction) | dialect-strategy layer selects openai-chat vs anthropic-messages; loop control flow shared | `python -m pytest platform_tests/scripts/test_cloud_harness_base.py -q` |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (anthropic-messages concrete) | request-build (system/tool_result/input_schema) + response-parse (text/tool_use) + both auth styles + tool-loop round-trip against a stubbed anthropic transport | new anthropic tests in `test_cloud_harness_base.py` |
| owner AUQ (native-hook seam) | `hook_tier=native-full-hooks` accepted; mutating tools still route through the fail-closed floor regardless of tier | native-hook-tier test in `test_cloud_harness_base.py` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` / `DCL-OLLAMA-TOOL-PARITY-GATE-001` (generalized) | guard floor enforced for the anthropic-messages dialect too (deny/unavailable fail closed) | anthropic guard tests in `test_cloud_harness_base.py` |
| behavior preservation | slice-2 regression + base tests pass unchanged after the OpenAI-strategy extraction | `pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_openrouter_routing_deepseek.py platform_tests/scripts/test_cloud_harness_base.py` (67 passing) + `git diff` showing the OpenRouter test files unmodified |
| `GOV-ARTIFACT-APPROVAL-001` | `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` present in MemBase with a matching approval packet | `gt spec show DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / code-quality | ruff check AND ruff format --check clean on changed `.py` | `ruff check` + `ruff format --check` on `scripts/cloud_harness_base.py`, `platform_tests/scripts/test_cloud_harness_base.py` |

## Acceptance Criteria

1. `cloud_harness_base.py` has a dialect-strategy abstraction; `run_tool_loop` is dialect-agnostic; the OpenAI-chat strategy preserves slice-2 behavior (67 tests pass unchanged).
2. `anthropic-messages` dialect implemented (request-build, response-parse, both auth styles, retry parity) with tests, including a stubbed-transport tool-loop round-trip.
3. `hook_tier=native-full-hooks` accepted as a seam/flag; the guard-adapter floor remains the enforced mechanism for all tiers (asserted).
4. `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` authored with a `GOV-ARTIFACT-APPROVAL-001` packet; generalizes the ollama DCL without retiring it.
5. `ruff check` and `ruff format --check` clean on changed `.py`.
6. Scope boundary held: no adopter re-based, no native-hook wiring, no `ollama-native` dialect, no doctor/parity change.

## Risks / Rollback

- **Risk:** the dialect-abstraction refactor regresses the proven `openai-chat` path. **Mitigation:** the OpenAI strategy is an extraction with the 67 existing tests as an unchanged behavior-preservation gate (same discipline as slice 2's re-base).
- **Risk:** the anthropic-messages dialect is built without a live Anthropic endpoint to validate against. **Mitigation:** slice 3 proves it against a stubbed transport (protocol-shape correctness); the live-endpoint proof (incl. the `x-api-key` vs `Authorization` behavior of issue #16922) lands with the first real adopter (Alibaba CS) in slice 4 — the same prove-with-adopter discipline the owner AUQ chose for the native-hook path.
- **Risk:** premature native-hook mechanism. **Mitigation:** slice 3 ships only the seam + flag; the floor stays enforced; concrete wiring is slice 4.
- **Rollback:** the anthropic dialect + native-hook seam are additive to `cloud_harness_base.py` (revertible); the generalized DCL is append-only in MemBase (corrected by a superseding version); no adopter or sibling shim is mutated.

## Recommended Commit Type

`feat:` — slice 3 adds a net-new dialect (`anthropic-messages`), the dialect-strategy abstraction, and the native-hook-path capability flag (new capability surface), plus the generalized tool-parity DCL. The OpenAI-strategy extraction is behavior-preserving supporting work.
