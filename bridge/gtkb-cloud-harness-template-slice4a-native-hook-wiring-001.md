NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a6d97151-27d2-41c8-8e3b-1d88f3960cf8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder; resolved role prime-builder via ::init gtkb pb

# Reusable Direct-Cloud Harness Template — Slice 4a: concrete native-full-hook lifecycle wiring (stubbed-transport proof)

bridge_kind: prime_proposal
Document: gtkb-cloud-harness-template-slice4a-native-hook-wiring
Version: 001
Date: 2026-07-09 UTC

Work Item: WI-5078
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 4a implements the concrete native-full-hook lifecycle in
`scripts/cloud_harness_base.py`, the piece slice 3 deferred. Slice 3 shipped the
`hook_tier=native-full-hooks` seam/flag (validated as accepted, floor still
enforced) but did NOT wire the concrete lifecycle. Per the owner scope split
(`DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT`), slice 4a wires the
lifecycle and proves it against a STUBBED transport (the same prove-with-stub
discipline slice 3 used for the `anthropic-messages` dialect); Alibaba Cloud
Studio adopter onboarding (identity H) and the live-endpoint proof are slice 4b
(credential-gated, not executable by an interactive Prime session per
DIRECT-HARNESS-INVOKE-BAN).

Concretely: when `AdopterProfile.hook_tier == "native-full-hooks"`, the base
runs the full GT-KB hook lifecycle at the loop's lifecycle points —
`SessionStart` at loop entry, `UserPromptSubmit` before the initial user
message, `PreToolUse` before EVERY tool dispatch (honoring a hook
`{"decision": "block"}` by refusing the tool and feeding the block reason back
to the model), `PostToolUse` after each dispatch, and `Stop` at loop
termination. For the default `guard-adapter-floor` tier, behavior is unchanged.
**Crucially, the fail-closed guard-adapter floor remains enforced for mutating
tools under BOTH tiers** — native-full-hooks ADDS the full lifecycle, it does
not REPLACE the floor. No adopter is re-based and no adopter runs
`native-full-hooks` in this slice (OpenRouter stays `guard-adapter-floor` /
`openai-chat`); the tier is exercised only by tests against a stubbed transport.

## Implementation Dependency / Sequencing

Slice 3 (`gtkb-cloud-harness-template-slice3-dialect-abstraction`) is VERIFIED
(`-004`) and its base is committed (`scripts/cloud_harness_base.py` at
`3b3eb475`), so the slice-3 dependency is satisfied. Slice 4a modifies that
committed base. Implementation-start is gated on this slice's own Loyal
Opposition `GO` plus an implementation-start packet.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives executable tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the approved architecture; slice 4 = native-hook path concrete wiring. This slice implements the 4a portion.
- `SPEC-INTAKE-9ec893` — the maximal-hook / direct-cloud principle the native-hook path operationalizes.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the Layer-3 fail-closed guard adapter the base enforces for every adopter and tier; native-full-hooks does not relax it.
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` — the generalized tool-parity gate (authored in slice 3) requiring mutating tools route through the fail-closed floor for all dialects and hook tiers; this slice preserves that invariant while adding the lifecycle.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — framework-free precedent; the lifecycle runner stays stdlib, no agent framework.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the native-hooks-vs-guard-adapter-fallback precedent; slice 4a ships the concrete native-hook expression of that distinction (floor remains the fallback/floor).
- `ADR-CROSS-HARNESS-PARITY-001` — `cloud_harness_base.py` is a shared harness surface; behavioral parity is required (see Cross-Harness Disposition).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires the Cross-Harness Disposition section because a harness-surface file is targeted.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the base is a durable tracked artifact; the lifecycle wiring is encoded in deterministic code + tests, not operating memory.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed files remain within `E:\GT-KB`; no adopter/application file is touched.

## Prior Deliberations

- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` — owner decision (this session) splitting slice 4 into 4a (native-hook wiring, stubbed proof) and 4b (Alibaba H onboarding + live proof); the authority for this slice's scope.
- `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE` — owner AUQ fixing the native-hook depth: slice 3 = seam + flag; concrete wiring proven with an adopter in slice 4.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` — the program authorization.
- `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` — owner intent for Anthropic-compatible full hooks on a cloud harness; the native-hook lifecycle is the template mechanism that serves it (adopter re-base is 4b).
- `bridge/gtkb-cloud-harness-template-slice3-dialect-abstraction-001.md` (VERIFIED at `-004`) — the slice-3 seam/flag this slice makes concrete.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` — AskUserQuestion (this session): the owner selected "4a: native-hook wiring, stubbed proof", authorizing the concrete lifecycle wiring proven against a stubbed transport and deferring the credential-gated Alibaba live proof + adopter onboarding to slice 4b.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` — standing program authorization.
- Standing `PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708` covers WI-5078 by project membership.

These authorize the proposal. Implementation remains gated on this slice's Loyal Opposition `GO` plus an implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CLOUD-HARNESS-TEMPLATE-001` fixes the native-hook-path scope; `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` fixes this slice's 4a boundary; the generalized tool-parity gate (`DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001`) fixes the floor invariant the lifecycle must preserve. No new or revised requirement is needed before implementation; no new formal artifact is authored in this slice.

## Cross-Harness Disposition

Applicable harness-observable surface: `scripts/cloud_harness_base.py` is the shared runtime base every cloud harness instantiates. This slice changes only the native-full-hooks tier's behavior (additive) and leaves the default guard-adapter-floor tier byte-behavior unchanged.

Parity declaration: no adopter re-bases or opts into `native-full-hooks` in this slice, so no adopter's observable behavior changes; the OpenRouter adopter stays `guard-adapter-floor`. The lifecycle runner is exercised only by tests against a stubbed transport. When a real adopter opts into `native-full-hooks` (slice 4b, Alibaba CS), that adopter's parity disposition is filed with its onboarding. No owner-approved typed waiver is requested.

## Proposed Change / Scope

On a slice-4a GO and an implementation-start packet, implement within the declared `target_paths`:

1. **Native-full-hook lifecycle runner in `cloud_harness_base.py`.** Add a hook-lifecycle helper that, when `profile.hook_tier == HOOK_TIER_NATIVE_FULL`, runs the registered GT-KB hooks at the loop's lifecycle points. Hook discovery reads the same `.claude/settings.json` hook registration the interactive harness uses (read-only), executed via the existing fail-closed subprocess pattern (`invoke_guard_adapter`'s runner discipline: bounded timeout, JSON payload on stdin, `{"decision": "block", "reason": ...}` honored). Lifecycle points in `run_tool_loop`: `SessionStart` (loop entry), `UserPromptSubmit` (before the first user message is sent), `PreToolUse` (before EVERY tool dispatch — all tools, not only mutating), `PostToolUse` (after each dispatch), `Stop` (loop termination). A `PreToolUse` block refuses the tool and feeds the block reason back to the model as the tool result, matching the interactive harness semantics.

2. **Floor preserved for all tiers.** The existing `invoke_guard_adapter` fail-closed floor for mutating tools (Write/Edit/Bash) continues to run regardless of `hook_tier`; native-full-hooks ADDS the lifecycle and does not bypass the floor. A test asserts a mutating tool under `native-full-hooks` still routes through the floor and fails closed on guard deny/unavailable.

3. **Default tier unchanged.** For `hook_tier == guard-adapter-floor` (the default; OpenRouter), `run_tool_loop` behavior is byte-for-byte preserved — the slice-3 base + regression tests (67) must pass unchanged.

4. **`ollama-native` dialect NOT implemented** (remains the slice-4b/Ollama-re-base seam per `SLICE4_DIALECT_SEAM`); no adopter re-base; no doctor/parity change; no DCL retirement — all slice 4b.

## Scope Boundary (Slice 4a vs Slice 4b)

Slice 4a does NOT: onboard Alibaba Cloud Studio or any adopter (identity H registration is 4b); run any live credentialed endpoint or live harness smoke test; implement the `ollama-native` dialect or re-base Ollama; change doctor/parity surfaces; or retire `DCL-OLLAMA-TOOL-PARITY-GATE-001`. Those are slice 4b, gated on owner-run credentialed proof.

## Specification-Derived Verification

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (native-hook wiring) | `native-full-hooks` tier runs SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop in order against a stubbed transport; ordering + payload-shape asserted | new native-hook-lifecycle tests in `test_cloud_harness_base.py` |
| owner AUQ (`...SLICE4-SCOPE-SPLIT`) | a `PreToolUse` hook returning `{"decision":"block"}` refuses the tool and the block reason is fed back to the model | native-hook-block test in `test_cloud_harness_base.py` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` / `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` | mutating tools under `native-full-hooks` still route through the fail-closed guard-adapter floor (deny/unavailable fail closed) | floor-still-enforced test in `test_cloud_harness_base.py` |
| behavior preservation | the default `guard-adapter-floor` tier is unchanged; slice-3 base + regression tests pass unchanged | `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_openrouter_routing_deepseek.py -q` (67 passing, OpenRouter test files unmodified) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / code-quality | ruff check AND ruff format --check clean on changed `.py` | `ruff check` + `ruff format --check` on the two target files |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | path inspection: both target paths in-root | in-root only |

## Acceptance Criteria

1. `native-full-hooks` tier runs the full lifecycle (SessionStart, UserPromptSubmit, PreToolUse per tool, PostToolUse, Stop) at the correct loop points, proven against a stubbed transport with ordering assertions.
2. A `PreToolUse` block is honored (tool refused, reason returned to the model).
3. The fail-closed guard-adapter floor remains enforced for mutating tools under BOTH tiers (asserted).
4. The default `guard-adapter-floor` tier is byte-behavior unchanged; the 67 slice-3 tests pass unchanged.
5. `ruff check` and `ruff format --check` clean on changed `.py`.
6. Scope boundary held: no adopter onboarded/re-based, no live endpoint, no `ollama-native` dialect, no doctor/parity change, no DCL retirement.

## Risks / Rollback

- **Risk:** the lifecycle runner regresses the proven default-tier path. **Mitigation:** the default tier is guarded by the 67 slice-3 tests as an unchanged behavior-preservation gate; the lifecycle runs only when `hook_tier == native-full-hooks`.
- **Risk:** the native-hook lifecycle is built without a live Anthropic adopter to validate against. **Mitigation:** slice 4a proves lifecycle-firing + ordering + block semantics against a stubbed transport (protocol-shape correctness); the live-endpoint proof lands with Alibaba CS in slice 4b — the same prove-with-adopter discipline the owner chose for the dialect in slice 3.
- **Risk:** a mis-wired native tier could bypass the floor. **Mitigation:** an explicit test asserts the floor still fires under `native-full-hooks`; the floor call is independent of tier.
- **Rollback:** the lifecycle runner is additive to `cloud_harness_base.py` (revertible); no adopter, sibling shim, KB, or bridge-state mutation.

## Recommended Commit Type

`feat:` — slice 4a adds a net-new capability (the concrete native-full-hook lifecycle runner for the `native-full-hooks` tier). The default-tier path is behavior-preserving supporting work.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
