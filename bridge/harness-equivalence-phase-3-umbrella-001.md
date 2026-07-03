NEW

# Umbrella Proposal - HARNESS-EQUIVALENCE-PHASE-3

bridge_kind: prime_proposal
Document: harness-equivalence-phase-3-umbrella
Version: 001
Date: 2026-07-01 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: S-2026-07-01-CODEX-PB-HARNESS-EQUIVALENCE-PHASE-3
author_model: GPT-5 Codex
author_model_version: 2026-07-01
author_model_configuration: Codex desktop interactive Prime Builder session via owner-directed GT-KB work

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4955-UMBRELLA
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4955

target_paths: ["bridge/harness-equivalence-phase-3-umbrella-001.md"]

## Claim

GT-KB needs a Phase 3 harness-equivalence program that turns the current transcript and durable research evidence into explicit child work items. Phase 2 established broad parity baselines and several envelope-sharding repairs; Phase 3 should measure how each harness/model actually behaves inside GT-KB work and close the gaps that cause agents to waste tokens, miss skills, confuse configuration, or fall back to direct manipulation of controlled artifacts.

This umbrella is a planning and backlog-formation proposal only. It authorizes filing this bridge artifact and directing Prime Builder to create child work items. It does not authorize protected implementation or child work execution.

## Research And Evidence References

- Current owner decision: `DELIB-202665197` and approval packet `.groundtruth/formal-artifact-approvals/2026-07-01-DELIB-202665197.json` authorize this project/proposal and capture the OpenRouter/Goose model-configuration clarification.
- Current transcript finding: OpenRouter interactive/UI evidence shows Kimi-k2.6; Goose is not configured to match the OpenRouter headless configuration; the harness config is believed correct at `deepseek-v4-pro`.
- `docs/harness-parity-phase-2.md` and `docs/harness-parity-phase-2-matrix.md` define the Phase 2 evaluator and baseline gaps across Codex, Claude, Cursor, Antigravity, Ollama, and OpenRouter.
- `bridge/gtkb-wi4930-harness-parity-role-readiness-orchestration-004.md` verifies role-readiness orchestration and documents truthful WARN states for downstream adapters and event-source gaps.
- `bridge/gtkb-session-activity-envelope-sharding-umbrella-001.md` and `bridge/gtkb-session-activity-envelope-sharding-umbrella-004.md` define and verify the session/activity envelope sharding program.
- `bridge/gtkb-envelope-sharding-compact-query-modes-001.md` covers compact query modes for oversized bridge/project/authorization/transcript surfaces.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` records concrete blockers B1-B7: raw bridge archival JSON, oversized implementation-authorization output, noisy implementation-report planning, handoff/session archive drift, broad generated-cache searches, glossary load risk, and provider transcript/result gaps.
- `bridge/gtkb-envelope-sharding-harness-projection-parity-004.md` verifies cross-harness activity-envelope and compact result/session-envelope projection across all six registered harness families.
- `bridge/gtkb-envelope-sharding-load-measurement-001.md` proposes measuring global and per-activity token/governance load.
- `config/registry/sot-artifacts.toml` is the SoT artifact registry and names the authority/mutation APIs for bridge files, MemBase classes, harness state, and control registries.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4516-openrouter-bash-bridge-bypass.md` is a concrete direct-manipulation/bypass case: OpenRouter/Ollama Bash could mutate bridge artifacts without bridge-compliance guards.
- `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-005.md` verifies the hardening fix for that specific Bash bridge-bypass class and should be treated as precedent, not full closure for all direct-manipulation modes.

## Current Harness Difference Map

- Codex has the strongest current event/dispatch support in the Phase 2 matrix, but still needs deterministic readiness/no-window evidence and remains sensitive to Codex-vs-Claude helper/hook parity.
- Claude has native `.claude` hooks/skills and strong rule inheritance, but Phase 2 evidence showed dispatcher receive/event-source gaps and readiness/no-window evidence gaps under the current topology.
- Cursor has a usable fallback hook/skill surface but requires provider/adapter settings, dispatcher/event-source clarification, and headless parity hardening.
- Antigravity uses an optimized startup path and generated skill projection; it differs intentionally from full startup loading and needs typed waivers/evidence when activity envelopes or transcript archives are not equivalent.
- Ollama and OpenRouter are provider/API harness lanes with compact-provider result/session-envelope semantics; they can receive dispatched work but lack full event-source and transcript-archive equivalence unless represented by compact result envelopes and typed limitations.
- Goose/OpenRouter model configuration has diverged in the current investigation: interactive OpenRouter showed Kimi-k2.6 while the headless/goose-related configuration is believed correct at deepseek-v4-pro. Phase 3 must model UI, headless, provider-shim, and dispatch model identity as separate evidence fields rather than treating one label as universal.

## Gap Families To Convert Into Child Work Items

Prime Builder must create child work items after LO review of this umbrella. Each child WI must include a linked GOV-12/GOV-13 test, source evidence references, and a child bridge proposal before protected implementation.

1. Transcript/result corpus coverage by harness and model: inventory available transcripts, session envelopes, compact result envelopes, missing archives, and typed waivers for Codex, Claude, Cursor, Antigravity, Ollama, OpenRouter, and Goose/provider-adjacent lanes.
2. Harness/model configuration truth: reconcile UI model labels, headless dispatch routes, provider shim routing, registry entries, and owner-visible status so Kimi/OpenRouter/Goose/deepseek divergences cannot silently mislead evaluation.
3. Skill effectiveness by specialized activity envelope: evaluate whether proposal, review, verification, bridge reconciliation, project/backlog, SoT query, session wrap, and harness parity skills are discoverable and actually used across harnesses.
4. CLI compactness and SoT size: extend compact/current/actionable query defaults beyond already-covered bridge/auth/helper cases to MemBase, Deliberation Archive, dispatcher state, transcript inventories, advisory-router output, and any other large SoT class.
5. Direct-manipulation prevention: generalize the WI-4516 precedent to all controlled artifacts and all harness tool paths, including direct DB access, direct bridge/file writes, helper bypasses, shell-mediated writes, and mutation of generated runtime state.
6. Cross-harness activity/result envelope equivalence: use WI-4950 as a baseline and verify with transcript/result evidence that each harness either exposes equivalent behavior or carries a specific typed waiver.
7. Harness-quality benchmark integration: connect the Phase 3 transcript/equivalence findings to the harness testing and quality benchmark project so model/harness differences are measured repeatedly, not as a one-off audit.
8. Child-WI generator/checklist: add a deterministic checklist or helper that converts each identified gap into a governed WI/test/proposal skeleton without dumping full SoT payloads into context.
9. Evidence freshness and archival boundaries: define when agents should read compact summaries, when archival/full output is justified, and how to cite archived transcripts without loading entire historical state into routine sessions.
10. Prioritization and release gating: classify which gaps are release-blocking, which are advisory, and which are typed-waiver candidates; avoid duplicating active Phase 2 and envelope-sharding work by linking or superseding instead of reimplementing.

## In-Root Placement Evidence

All target paths for this umbrella are inside `E:\GT-KB`: `bridge/harness-equivalence-phase-3-umbrella-001.md`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - equivalence is behavioral/intent-based across applicable harnesses, with typed waivers for legitimate differences.
- `SPEC-INTAKE-46594e` - oversized base-session context and unsharded skills/terminology are a direct cause of token waste and missed focused behavior.
- `GOV-STANDING-BACKLOG-001` - child work items are the durable authority for future implementation work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this umbrella PAUTH is bounded to WI-4955 and does not authorize child execution.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - child proposals and protected mutations remain bridge-governed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - findings crossing from research into action must be preserved as projects, WIs, specs, reports, or bridge artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - child proposals must cite concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - child implementation reports must map specifications to executed evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal links project, work item, and PAUTH.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness behavior cannot assume a single hook/tool implementation model.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the research must become governed artifacts instead of scratchpad/session memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - child WIs must classify whether gaps are new work, defects, supersession, waivers, or retirements.

## Prior Deliberations

- `DELIB-202665197` - owner authorization for this Phase 3 project, umbrella proposal, and child-WI direction.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner directive for Phase 2 harness parity scope.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - source decision for the cross-harness parity invariant.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - prior parity implementation authorization context.
- `DELIB-202665110` - owner authorization for the session/activity envelope sharding umbrella.
- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete envelope-sharding child work.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - prior envelope refinement authorization.

## Owner Decisions / Input

- `DELIB-202665197` - current owner decision: create HARNESS-EQUIVALENCE-PHASE-3 and file this umbrella proposal with research references and child-WI direction.
- `AUQ-20260701-HARNESS-EQUIVALENCE-PHASE-3-UMBRELLA` - fresh owner evidence captured by `gt backlog authorize-implementation`.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4955-UMBRELLA` - active authorization bounded to WI-4955. It permits project metadata, documentation, and governance-record work for this umbrella, and forbids protected implementation and child execution.

## Requirement Sufficiency

Existing requirements are sufficient for this umbrella proposal. `ADR-CROSS-HARNESS-PARITY-001`, `SPEC-INTAKE-46594e`, and `GOV-STANDING-BACKLOG-001` together establish why the research must become child WIs rather than remaining transcript-only observations. Child WIs may need additional specs or ADR/DCL amendments if they introduce new enforcement mechanisms, thresholds, or source-of-truth schemas.

## Proposed Scope

This umbrella asks Loyal Opposition to approve the Phase 3 program shape and the instruction to create child work items for the gap families above.

After GO, Prime Builder should:

1. Create the child WIs and linked tests through `gt backlog add-work-item`, one gap family at a time.
2. Attach each child WI to `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` with explicit subproject names.
3. Reuse or link existing Phase 2/envelope-sharding WIs where a gap is already covered; do not duplicate work.
4. File child bridge proposals only after each child WI has concrete evidence references, target paths, and spec-derived verification.
5. Keep compact evidence as the default; require explicit justification for full archival transcript/SoT reads.

Out of scope for this umbrella:

- Protected source, config, hook, skill, or test mutations.
- Credential lifecycle, provider key rotation, production deployment, or GitHub/settings mutation.
- Treating Phase 3 as a replacement for already VERIFIED Phase 2 or envelope-sharding work.
- Bulk-creating implementation WIs without preserving evidence and boundaries.

## Specification-Derived Verification Plan

| Requirement / evidence | Verification expectation |
| --- | --- |
| `TEST-11258` linked to `ADR-CROSS-HARNESS-PARITY-001` | PASS when this umbrella links the project/WI/PAUTH, references the transcript/SoT/harness parity research, enumerates gap families, and directs child WI creation before protected implementation. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-HARNESS-EQUIVALENCE-PHASE-3`, `gt backlog show WI-4955`, and `gt projects authorizations PROJECT-HARNESS-EQUIVALENCE-PHASE-3 --json` confirm durable project/WI/PAUTH state. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance gate passes with `Project Authorization`, `Project`, `Work Item`, and parseable `target_paths`. |
| `SPEC-INTAKE-46594e` | Proposal explicitly routes oversized SoT/context-load issues into compact CLI, sharding, transcript/result envelope, and measurement child work. |
| `ADR-CROSS-HARNESS-PARITY-001` | Proposal explicitly distinguishes harness behavioral equivalence from implementation identity and names typed-waiver paths. |

## Acceptance Criteria

- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` exists and is active.
- `WI-4955` and `TEST-11258` exist under the project.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4955-UMBRELLA` is active and bounded to umbrella planning/proposal work only.
- This bridge file is filed as the umbrella proposal and linked to the project.
- The proposal cites the current owner decision plus Phase 2 parity, envelope-sharding, SoT registry, compact-query, harness-projection, load-measurement, blocker-repair, and OpenRouter/Ollama bypass evidence.
- The proposal directs PB to create child WIs covering every named gap family before any protected implementation starts.

## Risks / Rollback

Risk: Phase 3 duplicates Phase 2 or envelope-sharding work. Mitigation: child WIs must link, reuse, supersede, or explicitly exclude existing work before proposing implementation.

Risk: transcript research overfits to partial evidence. Mitigation: first child WI must create a transcript/result corpus manifest and classify missing archives/typed waivers instead of assuming full coverage.

Risk: the umbrella becomes a broad permission slip. Mitigation: PAUTH is bounded to WI-4955 and forbids child execution and protected mutations.

Risk: compact outputs hide audit detail. Mitigation: compact/current is the default for routine work, while archival/full reads remain explicit and justified.

Rollback: file a revised bridge version narrowing or withdrawing the program; revoke the PAUTH; retire or supersede child WIs that have not yet started. No protected implementation is performed by this umbrella.

## Files Expected To Change

- `bridge/harness-equivalence-phase-3-umbrella-001.md`

## Recommended Commit Type

`docs`
