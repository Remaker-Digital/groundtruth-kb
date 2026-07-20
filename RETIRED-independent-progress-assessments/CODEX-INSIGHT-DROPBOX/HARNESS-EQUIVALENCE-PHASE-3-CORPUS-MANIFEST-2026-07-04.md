# Harness Equivalence Phase 3 Corpus Manifest

Status: IMPLEMENTED
Date: 2026-07-04
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4963
Bridge: gtkb-wi4963-harness-corpus-manifest
GO: bridge/gtkb-wi4963-harness-corpus-manifest-002.md
Implementation authorization packet: sha256:b1a9f032bc2fe3138b2463f2f56de07222c8e9517ed648504af65185801f096b

## Claim

WI-4963 is satisfied by this governed corpus manifest. It inventories the available transcript, session-envelope, compact-result, provider-result, missing-archive, and typed-waiver evidence that downstream Phase 3 harness-equivalence work must consume before proposing implementation changes. No protected source, config, test, hook, skill, credential, provider, dispatcher-routing, or durable-role mutation was performed.

## Evidence Sources

| Source | Role in this manifest | State |
| --- | --- | --- |
| bridge/harness-equivalence-phase-3-umbrella-004.md | Confirms the Phase 3 umbrella is VERIFIED and child WIs WI-4963 through WI-4972 are governed child work, each implementation-gated separately. | Canonical bridge state reports VERIFIED. |
| independent-progress-assessments/CODEX-INSIGHT-DROPBOX/_verify-body-harness-equivalence-phase-3-umbrella-004.md | Records the verified creation of ten child WIs/tests, the owner authorization DELIB-202665197, and the no-protected-implementation boundary. | Read as controlling umbrella evidence. |
| config/agent-control/harness-capability-registry.toml | Declares compact/session/result envelope modes for Claude, Codex, Antigravity, Cursor, Ollama, and OpenRouter. | Active registry evidence. |
| config/harness-parity/phase2-waivers.toml | Declares active provider full-transcript archive waivers for Ollama and OpenRouter, and retired historical waivers for Claude/Codex/Cursor/Antigravity dispatcher receive/event-source gaps. | Active typed-waiver registry. |
| independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md | Classifies B7 provider transcript/archive absence as fixed/covered by WI-4950 compact-provider projection and typed waivers. | Active blocker-disposition evidence. |
| bridge/gtkb-envelope-sharding-harness-projection-parity-004.md and WI-4950 | Confirms cross-harness activity-envelope projection/result-envelope parity is VERIFIED/retired. | Verified baseline; do not reopen in WI-4963. |
| independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-03-18-32.md | Maps harness+model benchmarking activation into WI-4969 and WI-4791; distinguishes live reliability/latency evidence from missing real token/adjudication capture. | Required downstream benchmark input. |
| .gtkb-state/bridge-poller/dispatch-state.json and .gtkb-state/bridge-poller/dispatch-failures.jsonl | Live dispatcher reliability/provider failure evidence available for future scorecards. | Read-only operational evidence; not treated as transcript authority. |

## Corpus Coverage By Lane

| Lane | Current in-root corpus | Coverage state | Typed waiver or missing-evidence disposition | Downstream consumer |
| --- | --- | --- | --- | --- |
| Claude / harness B | harness-state/claude/session-envelope.json plus session-envelope-archive/*.json; native activity/session/result envelope modes in capability registry. | Covered for compact session/result evidence; raw transcript archives should not be loaded as routine authority. | No active full-transcript waiver needed; parity checks must use compact result/session fields. | WI-4972, WI-4967, WI-4969. |
| Codex / harness A | harness-state/codex/session-envelope.json plus session-envelope-archive/*.json; native compact modes in capability registry. | Covered for compact session/result evidence; local app-thread history is not a governed artifact unless promoted. | No active full-transcript waiver needed; use compact fields for provider-comparable parity. | WI-4972, WI-4967, WI-4969. |
| Antigravity / harness C | harness-state/antigravity/session-envelope.json plus session-envelope-archive/*.json; optimized-startup activity/session projection and native compact result envelope mode. | Covered with optimized-startup caveat. | Historical dispatcher/event-source waivers are retired; Antigravity is active and dispatchable to the harness limit. | WI-4972, WI-4967, WI-4969. |
| Cursor / harness E | harness-state/cursor/session-lifecycle-guard.json; fallback activity/session/result envelope modes in capability registry. | Partial. No current session-envelope archive was present in harness-state/cursor during this manifest pass. | Treat as missing compact-session archive evidence until a future Cursor run emits or registers comparable envelopes; do not infer full transcript parity. | WI-4972 first, then WI-4967 if controlled-artifact paths include Cursor. |
| Ollama / harness D | Provider harness evidence is in dispatcher state/logs and scripts/ollama_harness.py, not a harness-state/ollama transcript directory; compact-provider modes in capability registry. | Covered by compact-provider projection for dispatch/result/session comparisons; not covered for full transcript archive. | Active WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE; active WAIVER-P2-OLLAMA-EVENT-SOURCE. | WI-4969 reliability/latency scorecard; WI-4791 later quality adjudication. |
| OpenRouter / harness F | harness-state/openrouter currently contains old draft verdict scratch files, not a governed session envelope; compact-provider modes in capability registry and scripts/openrouter_harness.py. | Covered only through compact-provider dispatch/result evidence; harness-state/openrouter scratch is not authoritative corpus. | Active WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE; active WAIVER-P2-OPENROUTER-EVENT-SOURCE. | WI-4969 and WI-4791; any direct manipulation concerns route to WI-4967. |
| Goose / provider-adjacent lane | No active in-root harness-state directory or current dispatch lane found in this manifest pass. | Missing current evidence. | Treat as not in current Phase 3 execution set until a governed lane, registry row, or provider envelope exists. | WI-4972 classification only; no implementation proposal should depend on Goose evidence yet. |

## Downstream Work-Item Routing

| Work Item | Manifest-derived next use | Readiness |
| --- | --- | --- |
| WI-4972 | Classify each Phase 3 gap as release-blocking, advisory, typed-waiver, or duplicate-work-controlled, using this manifest as the evidence inventory. | Ready for proposal after WI-4963 verification. |
| WI-4967 | Generalize direct-manipulation prevention only after WI-4972 decides which controlled-artifact paths are release-blocking. | Not first; depends on WI-4972 classification. |
| WI-4969 | Activate benchmark scorecards from existing dispatch logs and benchmark scaffold, using this manifest to avoid treating full transcripts as universal evidence. | Ready after WI-4972 or as a narrow advisory scorecard slice if LO approves. |
| WI-4791 | Quality adjudication/consensus remains the hard downstream quality dimension, not a prerequisite for this manifest. | Later Phase 4 work; do not fold into WI-4963. |

## Architecture Alignment Ledger

| Architecture concern | Alignment evidence |
| --- | --- |
| OPS consolidation | This slice does not change dispatcher behavior or ranking. It prepares evidence for downstream dispatcher/harness quality work without silently folding harness-equivalence scope into OPS dispatcher modernization. |
| Dispatcher daemon architecture | Dispatcher evidence is consumed through existing daemon state/log surfaces and bridge status, not by recreating a parallel queue or poller. |
| Lifecycle-first, scoring-last precedence | The manifest classifies corpus availability and waivers before any scoring or ranking activation. WI-4969/WI-4791 remain downstream, not implicit changes here. |
| Portfolio reconciliation findings | The slice preserves the distinction between verified WI-4950 envelope projection, Phase 3 harness-equivalence child WIs, and OPS dispatcher modernization work. |
| Cross-harness parity | The manifest uses compact/result/session envelope modes and typed waivers from the active registries instead of assuming every harness has a comparable raw transcript archive. |

## Residual Risks

| Risk | Impact | Routed action |
| --- | --- | --- |
| Cursor lacks a current session-envelope archive in harness-state/cursor. | Cursor cannot be treated as fully evidenced for compact session parity from this manifest alone. | WI-4972 should classify Cursor evidence as partial until a governed Cursor run emits comparable envelopes. |
| Provider harnesses lack full transcript archives by design. | Raw-transcript comparisons across desktop and provider harnesses would create false drift. | Use active typed waivers and compact-provider envelopes; route measurement to WI-4969. |
| OpenRouter harness-state contains draft verdict scratch rather than canonical envelopes. | Scratch files cannot satisfy corpus authority. | Treat scratch as non-authoritative and require compact dispatch/result evidence. |
| Token cost and quality adjudication remain partial. | Benchmark comparison cannot yet claim real per-work-item cost or fit-for-purpose quality. | WI-4969 handles observed scorecards; WI-4791 handles consensus/adjudication later. |

## Verification

| Requirement | Evidence | Result |
| --- | --- | --- |
| ADR-CROSS-HARNESS-PARITY-001 | Manifest covers every active/adjacent lane with compact/session/result evidence or typed waiver disposition. | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Implementation followed latest GO at bridge/gtkb-wi4963-harness-corpus-manifest-002.md, a Prime Builder go_implementation claim, and implementation-start packet sha256:b1a9f032bc2fe3138b2463f2f56de07222c8e9517ed648504af65185801f096b. | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Project-relevant evidence is preserved as this governed in-root manifest and routed to existing WIs rather than scratch memory. | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Verification is manual/documentary because WI-4963 is an evidence manifest; no runtime behavior was changed. | PASS |

## Files Changed

- independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-2026-07-04.md
