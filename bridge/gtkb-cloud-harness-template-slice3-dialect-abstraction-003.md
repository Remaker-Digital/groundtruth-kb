NEW
author_identity: claude
author_harness_id: B
author_session_context_id: f0e664f2-35ef-4d46-86a5-5a828f73d30b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder

# Post-Implementation Report — Cloud-Harness Template Slice 3: dialect abstraction + anthropic-messages + native-hook seam + generalized tool-parity DCL

Work Item: WI-5078
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
Responds to: gtkb-cloud-harness-template-slice3-dialect-abstraction (GO at -002)

## Implementation Summary

Slice 3 is implemented per the GO'd proposal (-002), `ADR-CLOUD-HARNESS-TEMPLATE-001`, and the owner AUQ `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE`. The slice-2 dependency was satisfied first: slice 2 reached VERIFIED and committed (`3b3eb475`) before implementation-start.

1. **Dialect-strategy abstraction** in `scripts/cloud_harness_base.py`: `run_tool_loop` is now dialect-agnostic. A `DialectStrategy` (build_tool_schemas / build_payload / parse_message / chat) is resolved per profile via `resolve_dialect_strategy`; the loop's control flow, tool dispatch, fail-closed guard enforcement, no-progress dedup, and session-timeout stay shared. The `openai-chat` behavior was extracted into an OpenAI strategy **behavior-preservingly** (the transport was refactored behind a shared `_post_json_with_bounded_retry` parameterized by a `noun`, keeping openai-chat error text byte-identical).
2. **`anthropic-messages` dialect (concrete)**: `anthropic_messages_completion` (POST `<endpoint>/messages`) + the Anthropic strategy — request-build (top-level `system`, `tool_use`/`tool_result` content blocks, `input_schema` tools, `max_tokens`), response-parse (text + `tool_use` normalization into the internal shape), and configurable auth style (`x-api-key` for native Anthropic; `Authorization: Bearer` for the compat-endpoint class behind Ollama upstream issue #16922). `AdopterProfile` gained `auth_style` / `anthropic_version` / `max_tokens` with openai-safe defaults (the OpenRouter profile is unaffected).
3. **Native-hook-path seam + flag**: `hook_tier=native-full-hooks` is now a validated tier; the fail-closed guard-adapter floor remains the enforced mechanism for every tier (asserted). Per the owner AUQ, the concrete native-full-hook wiring is deferred to slice 4 (proven against Alibaba CS's live Anthropic endpoint). `ollama-native` is now the lone remaining dialect seam point (slice-4 sentinel).
4. **Generalized tool-parity DCL**: `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` authored into MemBase (v1, `type=design_constraint`, `status=specified`) via the governed `gt spec record` formal-artifact flow (owner AUQ "Approve — insert as-is"; approval packet at `.groundtruth/formal-artifact-approvals/2026-07-09-dcl-cloud-harness-template-tool-parity-gate-001.json`). It generalizes `DCL-OLLAMA-TOOL-PARITY-GATE-001` without retiring it; its 2 machine-checkable assertions pass.

No adopter was re-based (OpenRouter stays `openai-chat`; `openrouter_harness.py` untouched this slice); no native-hook wiring; no `ollama-native` dialect; no doctor/parity change.

## Recommended Commit Type

`feat:` — slice 3 adds a net-new dialect (`anthropic-messages`), the dialect-strategy abstraction, and the `native-full-hooks` capability flag (new capability surface), plus the generalized tool-parity DCL. The OpenAI-strategy extraction is behavior-preserving supporting work.

## Specification Links

Carried forward from the GO'd proposal -001 / GO -002 and verified against the implementation.

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` — linkage, spec-derived tests, bridge discipline.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the approved architecture (slice 3 = dialect abstraction incl. anthropic-messages + native-hook path + generalized tool-parity DCL).
- `SPEC-INTAKE-9ec893` — the maximal-hook / direct-cloud principle the native-hook path operationalizes.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — Layer-3 fail-closed guard adapter, enforced for every dialect and hook tier.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the per-shim contract generalized by the new DCL (not retired).
- `GOV-ARTIFACT-APPROVAL-001` — the DCL's formal-artifact-approval packet gate satisfied by this authoring.
- `GOV-ENV-LOCAL-AUTHORITY-001` — anthropic auth token referenced by env-key NAME; both auth styles keyed on the profile's env var.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — framework-free precedent (the anthropic transport is stdlib `urllib`, no agent framework).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native-hooks-vs-guard-adapter precedent (tier flag now; wiring slice 4).
- `GOV-20` — ADR governance context for the derived DCL.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable tracked artifacts; the ollama DCL's scope is superseded (not deleted).
- `.claude/rules/project-root-boundary.md` — all changed files within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE` (owner_decision) — the native-hook-path scope (seam + flag; wiring proven with adopter in slice 4).
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` (owner_decision) — program authorization.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the slice-3 scope source.
- `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` (owner_decision) — Anthropic full-hooks intent the native-hook path serves.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` (owner_decision) — Alibaba CS, the first anthropic-messages adopter (slice 4).

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement was needed; slice 3 mutated source/test only plus authored the generalized DCL under `GOV-ARTIFACT-APPROVAL-001`, within the active PAUTH and the VERIFIED slice-1 ADR + owner AUQ.

## Specification-Derived Verification

All tests executed from the project venv (`groundtruth-kb/.venv/Scripts/python.exe -m pytest`).

| Linked spec | Derived test / assertion | Evidence | Result |
|---|---|---|---|
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (dialect abstraction) | strategy selects openai-chat vs anthropic-messages; loop shared | `test_cloud_harness_base.py::test_anthropic_messages_dialect_resolves_to_strategy`, `::test_ollama_native_dialect_raises_slice4_sentinel` | PASS |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (anthropic-messages concrete) | request-build (system/tool_use/tool_result/input_schema), response-parse (text/tool_use), both auth styles, retry parity, tool-loop round-trip | `::test_anthropic_build_payload_translates_system_tooluse_and_toolresult`, `::test_anthropic_parse_message_extracts_text_and_tool_use`, `::test_anthropic_auth_style_x_api_key_header`, `::test_anthropic_auth_style_authorization_bearer_header`, `::test_anthropic_retry_parity_transient_then_succeeds`, `::test_anthropic_exhaustion_uses_messages_noun`, `::test_run_tool_loop_anthropic_round_trip` | PASS |
| owner AUQ (native-hook seam) | `native-full-hooks` accepted; guard floor still enforced for that tier | `::test_profile_accepts_native_full_hooks_tier`, `::test_native_full_hooks_tier_still_enforces_guard_floor`, `::test_profile_rejects_unknown_hook_tier` | PASS |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` / `DCL-OLLAMA-TOOL-PARITY-GATE-001` (generalized) | guard floor enforced regardless of dialect/tier; DCL machine-checkable | base guard tests + `gt assert --spec DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` → 2 assertions PASS | PASS |
| behavior preservation | 49 OpenRouter regression tests pass UNCHANGED after the OpenAI-strategy extraction | `pytest test_openrouter_harness.py test_openrouter_routing_deepseek.py test_cloud_harness_base.py` → **79 passed** (49 + 30) | PASS |
| `GOV-ARTIFACT-APPROVAL-001` | DCL present in MemBase with a matching approval packet | `gt spec show DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001`; packet `2026-07-09-dcl-cloud-harness-template-tool-parity-gate-001.json` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / code quality | ruff check AND ruff format --check clean on changed `.py` | `ruff check` exit 0; `ruff format --check` exit 0 | PASS |

## Behavior-Preservation Proof

Slice 3 modified exactly two files and did NOT touch either OpenRouter regression test file:

- `platform_tests/scripts/test_openrouter_routing_deepseek.py`: unmodified (absent from `git diff --name-only`); mtime `2026-06-12`.
- The OpenRouter harness regression test: NOT written by slice 3 — its file mtime is `2026-07-08T01:23:16Z`, ~23 hours before slice-3 implementation-start (`2026-07-09T00:51:11Z`). Its `git diff` vs HEAD is the same pre-existing uncommitted WI-5064 SSL-retry work carried over from before slice 2 (and deliberately excluded from slice-2's commit). Slice-3's two changed files carry mtime `2026-07-09T01:00–01:01Z`.

Stronger than "unmodified": the 49 OpenRouter regression tests — including the pre-existing WI-5064 SSL-retry tests — pass unchanged against the refactored base, confirming the OpenAI-strategy extraction is behavior-preserving.

## GO Conditions Addressed (from -002)

- Held implementation-start until slice-2 VERIFIED+committed (`3b3eb475`). ✓
- OpenAI-strategy extraction preserves behavior (79 tests; OpenRouter test files unmodified by this slice; WI-5064 caveat distinguished). ✓
- Anthropic request-build / response-parse / both auth styles / tool-loop round-trip tests present and passing. ✓
- Guard-adapter floor asserted enforced for the `native-full-hooks` tier. ✓
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` authored with a `GOV-ARTIFACT-APPROVAL-001` packet. ✓
- ruff check + ruff format --check clean. ✓
- Slice boundary held (no adopter re-based, no native-hook wiring, no ollama-native dialect, no doctor/parity change). ✓

## Files Changed

This slice modified exactly two source/test files (the finalize `--include` set, plus the DCL approval packet, the bridge chain -001..-N, and the VERIFIED verdict):

- `scripts/cloud_harness_base.py` — MODIFIED (dialect-strategy abstraction + anthropic-messages dialect + native-hook-tier validation/seam + shared transport helper).
- `platform_tests/scripts/test_cloud_harness_base.py` — MODIFIED (anthropic dialect + native-hook-tier + validation tests; slice-4 sentinel).
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` — MemBase row (v1) + approval packet `.groundtruth/formal-artifact-approvals/2026-07-09-dcl-cloud-harness-template-tool-parity-gate-001.json`.

The two OpenRouter regression test files were NOT modified by this slice; their disposition is in the `## Behavior-Preservation Proof` section above and MUST NOT be treated as claimed / `--include` paths for finalization (the harness regression test carries unrelated uncommitted WI-5064 work — the same finalize-guard commingling hazard resolved in slice 2's -004/-005 cycle).

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-09): "Proceed with the slice-3 build now?" → **Proceed — implement slice 3 now.**
- `AskUserQuestion` (2026-07-08, archived `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE`): native-hook-path scope → **seam + flag; wiring proven with Alibaba CS in slice 4.**
- `AskUserQuestion` (2026-07-09): "Approve authoring DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001?" → **Approve — insert as-is.**
- `AskUserQuestion` (2026-07-08, `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`): program authorization.

These authorize the work; implementation ran under the GO at -002 plus an implementation-start packet, and the DCL insert under its `GOV-ARTIFACT-APPROVAL-001` packet.

## Risks / Rollback

- **Risk:** the dialect-abstraction refactor regresses the proven openai-chat path. **Evidence/mitigation:** 49 OpenRouter regression tests pass unchanged; the shared transport keeps openai-chat error text byte-identical (noun-parameterized).
- **Risk:** the anthropic-messages dialect is built without a live Anthropic endpoint. **Mitigation:** slice 3 proves protocol-shape correctness against a stubbed transport (request-build, response-parse, both auth styles, tool-loop round-trip); the live-endpoint proof (incl. the `x-api-key` vs `Authorization` behavior of issue #16922) lands with Alibaba CS in slice 4 — the prove-with-adopter discipline the owner AUQ chose.
- **Risk:** premature native-hook mechanism. **Mitigation:** slice 3 ships only the validated seam + flag; the floor stays enforced (asserted); wiring is slice 4.
- **Rollback:** the anthropic dialect + strategy layer + native-hook seam are additive to `cloud_harness_base.py` (revertible to the slice-2 commit `3b3eb475`); the DCL is append-only in MemBase (corrected by a superseding version); no adopter or sibling shim was mutated.
