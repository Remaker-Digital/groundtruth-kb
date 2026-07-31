NEW

# Umbrella Proposal - Session/Activity Envelope Sharding Program

bridge_kind: prime_proposal
Document: gtkb-session-activity-envelope-sharding-umbrella
Version: 001
Date: 2026-07-01 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: S-2026-07-01-CODEX-PB-ENVELOPE-SHARDING
author_model: GPT-5 Codex
author_model_version: 2026-07-01
author_model_configuration: Codex desktop default coding-agent configuration; interactive Prime Builder session via ::init gtkb pb


Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4945-UMBRELLA
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4945

target_paths: ["bridge/gtkb-session-activity-envelope-sharding-umbrella-001.md"]

Umbrella proposal coordinating the new session/activity envelope sharding program. This proposal authorizes only the bridge planning artifact and child-slice decomposition; it does not authorize protected source, config, hook, test, rule, or skill mutations.

## Claim

GT-KB should implement a coherent sharding program that keeps the global session envelope small and governance-safe, then composes activity-specific skills, directives, terminology, history-state recipes, and CLI guidance only when the active activity envelope requires them.

The program responds to two observed failure classes:

1. Agents lose time or bypass governed surfaces when they cannot locate the right resource, skill, or compact CLI view.
2. Oversized sources of truth and raw archival outputs push agents toward token-heavy manipulation or undesirable direct reads.

This umbrella asks Loyal Opposition to approve the program structure, slice order, and child work-item boundaries. Child implementation slices require their own bridge proposals, target paths, and implementation authorization where they mutate protected files.

## Umbrella Inventory

First-class project:

- `PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING` - GT-KB Session and Activity Envelope Sharding.

Work items created under the project:

1. `WI-4945` / `TEST-11250` - Umbrella: session/activity envelope sharding implementation program.
2. `WI-4946` / `TEST-11251` - Define session-vs-activity envelope sharding taxonomy and global baseline.
3. `WI-4947` / `TEST-11252` - Add compact query modes for oversized SoT and transcript surfaces.
4. `WI-4948` / `TEST-11253` - Implement activity-envelope manifest and context-loader stack.
5. `WI-4949` / `TEST-11254` - Shard skills, directives, and knowledge across initial GT-KB activity envelopes.
6. `WI-4950` / `TEST-11255` - Add cross-harness activity-envelope projection and result-envelope parity.
7. `WI-4951` / `TEST-11256` - Measure token/governance load by session and activity envelope.
8. `WI-4952` / `TEST-11257` - Repair envelope-sharding blockers surfaced by transcript and CLI audit.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-session-activity-envelope-sharding-umbrella-001.md`.

## Specification Links

- `SPEC-INTAKE-46594e` - direct owner requirement: terminology and skills must be sharded by activity envelope; base session envelope loads only core GT-KB terminology and requisite global content.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - establishes per-activity context-load profiles at the intent_hint leg.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - requires each activity profile to carry skills, terminology, history_state, and direction.
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` - requires hook-primary context-load injection for activity open/close with agent fallback.
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001` - frames explicit hints as context management / progressive disclosure.
- `ADR-CROSS-HARNESS-PARITY-001` - requires applicable harness-observable behavior parity or typed waivers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this and all child implementation work remain bridge-governed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - decisions, requirements, reports, work items, and remediation candidates must land in durable artifacts when they cross threshold.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - child implementation proposals must cite their governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - child implementation reports must include spec-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes PAUTH, project, and work item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions and activity-lifecycle transitions remain AUQ-governed where required.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - program artifacts remain in-root under `E:\GT-KB`; no Agent Red lifecycle bleed.
- `GOV-STANDING-BACKLOG-001` - child WIs are the backlog authority for future implementation slices.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - activity-envelope loading must account for harnesses without equivalent hook surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the sharding program preserves durable artifact boundaries rather than relying on scratchpad/session memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - migrations and blocker dispositions must preserve explicit lifecycle state.

## Prior Deliberations

- `DELIB-20266631` - gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding — Loyal Opposition Verdict
- `DELIB-20265892` - WI-4730 Disposition-Profile Ratification
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - Authorize envelope-refinement implementation
- `DELIB-20265897` - WI-4729 ::wrap/::close Mechanical Harvest Model
- `DELIB-20266063` - Loyal Opposition Implementation Verification - WI-4687 Ops Activity Status And AUQ Option Surface
- `DELIB-202665110` - owner authorization for this umbrella program and PAUTH.

The transcript/CLI audit immediately preceding this proposal also surfaced practical sharding drivers: bridge helper raw JSON returning archival state by default, missing equivalent session/result envelopes for Cursor/Ollama/OpenRouter, handoff archive mis-resolution, advisory-router and DA-harvest bulk payloads, and provider/UI route visibility drift such as Goose Kimi vs OpenRouter headless DeepSeek routing. These findings are routed into WI-4947, WI-4950, WI-4951, and WI-4952.

## Owner Decisions / Input

- `DELIB-202665110` - owner authorized Codex to create and drive a coherent program to distribute skills, CLI, knowledge, and directives between the global session envelope and specialized activity envelopes.
- `AUQ-20260701-SESSION-ACTIVITY-ENVELOPE-SHARDING-PROGRAM` - fresh owner-evidence source captured by `gt backlog authorize-implementation`; answer summary: authorize Codex to create and drive the session/activity envelope sharding program, including project, umbrella proposal, and child work items; child implementations still require normal bridge GO and authorization.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4945-UMBRELLA` - active PAUTH bounded to WI-4945 only. It permits bridge proposal/project/governance/documentation work and forbids credential lifecycle, production deployment, protected source/config mutation without bridge GO, and child-slice implementation without separate authorization.

## Requirement Sufficiency

Existing requirements are sufficient for this umbrella proposal.

The direct source requirement is `SPEC-INTAKE-46594e`, and the activity-envelope ADR/DCL set already defines the context-load profile anatomy. This umbrella does not create new normative behavior by itself; it decomposes the already-specified requirement into implementation slices and asks LO to review the program structure.

Some child slices may need additional ADR/DCL/spec amendments before implementation, especially WI-4946 (taxonomy/global baseline), WI-4948 (loader contract), WI-4950 (cross-harness result-envelope parity), and WI-4951 (measurement thresholds). Those requirements must be captured in the relevant child proposal before protected mutations begin.

## Proposed Scope

Slice 0 / Umbrella (`WI-4945`): File this bridge proposal and establish the project, child-WI inventory, and bounded authorization posture. No source/config/test/hook/skill mutation.

Slice 1 (`WI-4946`): Define the sharding taxonomy and global baseline. Output should classify what is mandatory global content, what is activity-only, what is never loaded except on explicit query, and how activity-specific directives/skills/knowledge move through lifecycle states.

Slice 2 (`WI-4947`): Add compact query modes for oversized SoTs and transcript surfaces. Initial surfaces: bridge scan/status helper raw JSON, advisory-router skipped payloads, DA harvest/wrap scan counts, session-envelope/transcript inventories, project/backlog/spec search consistency, generated/runtime cache exclusions.

Slice 3 (`WI-4948`): Implement or extend the activity-envelope manifest/context-loader stack so each activity profile declares skills, terminology, history_state, and direction. The loader composes on top of the global session envelope and avoids broad startup reads.

Slice 4 (`WI-4949`): Inventory and migrate current global startup/rule/skill/knowledge load into activity shards. Initial shard families: bridge review, proposal authoring, implementation, verification, advisory/reporting, session wrap, harness parity/provider readiness, project/backlog work, deliberation/spec intake.

Slice 5 (`WI-4950`): Add cross-harness activity-envelope projection and compact result/session-envelope parity. Registered harnesses must either expose equivalent activity behavior or carry typed waivers; provider harnesses must emit compact structured result envelopes even when full transcript archives are absent.

Slice 6 (`WI-4951`): Measure global and per-activity token/governance load. Track token estimates, file/read counts, CLI payload sizes, loaded shards, and avoided archival surfaces; add regression thresholds or warnings for focused activities loading unrelated content.

Slice 7 (`WI-4952`): Repair blockers discovered by the transcript/CLI audit. This includes handoff archive selection, raw archival bridge JSON defaults, advisory-router/DA-harvest verbosity, broad search over generated/cache surfaces, provider synthetic metadata, and missing compact provider result envelopes.

## Specification-Derived Verification Plan

| Work item | Linked test | Spec-derived verification expectation |
| --- | --- | --- |
| `WI-4945` | `TEST-11250` | Umbrella proposal links the project/WI/PAUTH, defines base-vs-activity sharding, enumerates child slices, and forbids direct child implementation under this PAUTH. |
| `WI-4946` | `TEST-11251` | Sharding taxonomy classifies global baseline and activity-only context, with explicit exclusion criteria for extraneous startup content. |
| `WI-4947` | `TEST-11252` | Targeted SoT/CLI surfaces expose compact current/actionable summaries by default; archival/full output is opt-in. |
| `WI-4948` | `TEST-11253` | Representative activity open loads only manifest-declared skills/terminology/history/direction on top of the global envelope. |
| `WI-4949` | `TEST-11254` | Migrated global surfaces no longer load activity-only content, and each initial activity envelope carries the needed content for that activity. |
| `WI-4950` | `TEST-11255` | Each registered harness either matches applicable activity-envelope behavior or has a typed waiver; provider lanes emit compact result envelopes. |
| `WI-4951` | `TEST-11256` | Benchmark/report output measures global and per-activity load and flags unrelated shard loads or oversized raw SoT payloads. |
| `WI-4952` | `TEST-11257` | Each transcript/CLI blocker has a filed disposition, fix, or narrower child proposal; routine focused workflows no longer require direct DB/file manipulation or huge raw object reads. |

This umbrella thread itself is verified structurally: LO should confirm metadata, PAUTH scope, child WI/test existence, specification links, prior deliberation relevance, and target_paths parse. Runtime pytest/ruff evidence lands in child implementation reports.

## Acceptance Criteria

- The program has one active project, one bounded umbrella PAUTH, and child WIs for taxonomy, compact CLI, loader, shard migration, harness projection, measurement, and blocker repair.
- The global session envelope target is explicitly lightweight: basic governance, role/session authority, bridge/project safety, and operation essentials only.
- Activity envelopes carry activity-centric skills, directives, terminology, history-state recipes, and CLI guidance.
- Oversized SoT surfaces gain compact current/actionable CLI modes before agents are expected to consume them routinely.
- Harness/provider differences become explicit activity-envelope projection data, not hidden transcript availability drift.
- No child implementation proceeds under this umbrella PAUTH without its own bridge-reviewed target paths and authorization where required.

## Risks / Rollback

Risk: The umbrella becomes a blanket permission slip. Mitigation: PAUTH and this proposal are bounded to WI-4945 and the bridge planning artifact only; child WIs require their own proposal/authorization path.

Risk: Sharding removes necessary safety context from startup. Mitigation: WI-4946 defines the mandatory global baseline before migration; WI-4951 adds load/regression measurement.

Risk: Activity shards diverge across harnesses. Mitigation: WI-4950 requires cross-harness projection evidence or typed waivers.

Risk: Compact CLI surfaces hide necessary archival evidence. Mitigation: compact/current outputs become default, but archival/full outputs remain explicit opt-in for audit work.

Rollback: supersede this umbrella with a revised bridge version; retire or re-scope child WIs through normal backlog lifecycle; revoke the PAUTH if the program shape is rejected. No source/config/test mutation is performed by this umbrella thread.

## Files Expected To Change

- `bridge/gtkb-session-activity-envelope-sharding-umbrella-001.md`

## Recommended Commit Type

`docs`
