REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-07-05T12-48-36Z-prime-builder-A-a1ef5d
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex auto-dispatched prime-builder worker; dispatch id 2026-07-05T12-48-36Z-prime-builder-A-a1ef5d; approval_policy=never; sandbox=workspace-write; resolved_role=prime-builder

# Implementation Proposal - Neutralize vestigial harness event-source configuration

bridge_kind: prime_proposal
Document: gtkb-wi5020-retire-event-source-config
Version: 003
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi5020-retire-event-source-config-002.md (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5020-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5020

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json", "config/agent-control/declarative-agent-role-manifest.yaml", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "groundtruth-kb/tests/test_agent_role_manifest.py", "groundtruth-kb/tests/test_harness_projection.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This revision chooses the narrower and safer meaning of "retire" from the NO-GO path to GO: neutralize configured harness event-source state while retaining the honest compatibility schema fields.

The implementation will remove active event-source configuration from the current dispatcher and manifest surfaces: no harness should be configured with the `event-source` tag, `dispatch_mode: event_source`, `can_fire_events: true`, or `event_driven_hooks: true`. It will preserve `can_receive_dispatch`, reviewer precedence, cost/quality/availability ranking fields, and headless worker routing.

Full schema/API removal of `can_fire_events`, `event_driven_hooks`, `event_source`, CLI setter arguments, harness operations arguments, and legacy runtime readers is explicitly out of scope for this WI-5020 slice. Those fields remain as compatibility/read-model surfaces and as possible future cleanup under a separate schema-removal proposal.

## Claim

Prime Builder proposes a bounded WI-5020 implementation slice that corrects the event-source configuration drift without converting this proposal into a full dispatcher schema removal. The revised scope addresses every NO-GO finding by aligning target paths, acceptance criteria, and verification to the configured-state interpretation.

## Requirement Sufficiency

Existing requirements are sufficient for this revised proposal. `DELIB-20265888` and `ADR-DISPATCHER-ARCHITECTURE-001` establish that harnesses must not trigger dispatch; `DELIB-202665470` identifies the vestigial `can_fire_events` / `event_driven_hooks` cleanup as a follow-on to resumed dispatcher operation. No new owner decision is required because the revision narrows scope and preserves compatibility surfaces.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, `config/agent-control/declarative-agent-role-manifest.yaml`, `groundtruth-kb/src/groundtruth_kb/harness_projection.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`, `groundtruth-kb/tests/test_agent_role_manifest.py`, `groundtruth-kb/tests/test_harness_projection.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_bridge_dispatch_transactions.py`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`, and `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher architecture rejects harness-triggered dispatch; dispatch is daemon/service-owned.
- `DELIB-20265888` - owner directive capturing harness/dispatch isolation after the 2026-06-25 dispatch storm.
- `DELIB-202665470` - owner AUQ resume decision identifying vestigial `can_fire_events` / `event_driven_hooks` cleanup as separate follow-on work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governs durable artifact capture and proposal lifecycle.
- `GOV-STANDING-BACKLOG-001` - preserves work item/backlog visibility.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - keeps Codex hook/event terminology aligned with the current Windows hook posture without treating harness hooks as dispatcher triggers.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports artifact-first change control.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs artifact lifecycle trigger discipline.

## Prior Deliberations

- `DELIB-20265888` - direct `gt deliberations get` read succeeded. This owner decision records the dispatch-storm root cause and the invariant that harnesses must not trigger or influence dispatch; this is the primary design authority for neutralizing event-source configuration.
- `DELIB-202665470` - direct `gt deliberations get` read succeeded. This owner decision resumes dispatch supervision and names vestigial `can_fire_events` / `event_driven_hooks` cleanup as separate follow-on work.
- `bridge/gtkb-wi4788-slice-1-dispatch-config-state-gate-001.md` and `bridge/gtkb-wi4848-slice-3a-daemon-substrate-gated-live-dispatch-001.md` cite `DELIB-20265888` as the dispatcher-service ownership precedent this proposal continues.
- Live Deliberation Archive semantic searches run before drafting returned empty result sets for `"WI-5020 event source dispatcher"`, `"DELIB-20265888 dispatch storm event source"`, and `"DELIB-202665470 WI-5020"`; direct ID reads supplied the authoritative records above.

## Owner Decisions / Input

- `DELIB-202665470` - owner AUQ decision resuming dispatch and authorizing the follow-on cleanup context.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5020-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5020`.
- No new owner decision is required for this revision because it selects the narrower NO-GO remediation option and keeps schema/API removal out of scope.

## Revised Scope

- Remove active event-source configuration from `config/dispatcher/rules.toml` for all currently tagged harnesses A, B, and E.
- Regenerate or adjust `harness-state/harness-registry.json` so every harness projects `can_fire_events: false`, `event_driven_hooks: false`, and no `event-source` dispatch tag.
- Update the inventory-only declarative manifest so no harness uses `dispatch_mode: event_source`; retain a boolean `can_fire_events` key for every harness and set it to `false`.
- Update projection/config/state-report code only where needed so current runtime status no longer presents a configured event-source harness while preserving the compatibility schema fields.
- Preserve `can_receive_dispatch` and the legacy `event_driven_hooks` receive-dispatch fallback behavior in out-of-scope readers. No implementation may remove the `event_driven_hooks` fallback used by `scripts/dispatcher_runtime.py` or `groundtruth-kb/src/groundtruth_kb/project/doctor.py` in this slice.
- Update tests for the current configured-state contract: no configured event-source harnesses, receive-dispatch still works, and the manifest parser still requires explicit boolean `can_fire_events` keys.

## Findings Addressed

### F1 - target_paths insufficient: in-scope YAML edit breaks out-of-scope parser

Resolution: This revision does not remove `can_fire_events` keys from the manifest and does not edit the parser. The manifest remains parser-compatible by keeping explicit boolean `can_fire_events: false` entries. The manifest regression test path `groundtruth-kb/tests/test_agent_role_manifest.py` is added to `target_paths` because the expected `event_sources` set must change when A and E stop being event sources.

### F2 - retire is ambiguous; neither in-scope reading satisfies Acceptance Criterion 2

Resolution: This revision chooses Option B from the NO-GO: neutralize current configured event-source state while retaining the honest schema field. Acceptance criteria are rewritten to avoid promising full field removal. The retained schema/API fields must not be interpreted as active dispatcher trigger authority when all live configured values are false.

### F3 - dead reader in dispatcher_runtime.py not scoped

Resolution: `scripts/dispatcher_runtime.py` remains out of scope because this revision does not pursue full field removal. The dead `_record_can_fire_events` reader is acknowledged as a future cleanup candidate, not a blocker for the configured-state neutralization slice.

### F4 - event_driven_hooks double-duty entanglement not addressed

Resolution: The revised scope explicitly preserves the receive-dispatch compatibility path. `event_driven_hooks` is neutralized in current generated/configured data by setting it false, but legacy readers that use it only as a fallback for records lacking `can_receive_dispatch` remain untouched in this slice.

### F5 - premise precision: only harness B named, but three sources diverge

Resolution: This revision reconciles all observed event-source surfaces, not only B. Current direct reads show `rules.toml` tags A, B, and E with `event-source`; the manifest marks A and E as `dispatch_mode: event_source` with `can_fire_events: true`; the registry projects A as `can_fire_events: true` while E is false. The implementation target is A/B/E reconciliation across these surfaces. A live `gt bridge dispatch health --json` run on 2026-07-05 returned routing-config PASS with `consistency_findings: []`; the nonzero command exit was due to unrelated supervisor/watchdog scheduled-task lifecycle failures.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `DELIB-20265888` | `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py groundtruth-kb/tests/test_agent_role_manifest.py groundtruth-kb/tests/test_harness_projection.py -q --tb=short` confirms no configured event-source harnesses remain while dispatch-target selection still works. |
| `DELIB-202665470` | `gt bridge dispatch status --json` and `gt bridge dispatch health --json` evidence in the implementation report must show dispatch remains live/routable and the cleanup does not quiesce the dispatcher. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge applicability preflights must pass before filing; implementation must begin only after a future GO and implementation-start packet. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config` must report no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must carry this mapping forward with exact command output and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance must retain PAUTH, Project, Work Item, and `target_paths` metadata in this revised proposal. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target paths remain under `E:\GT-KB` and do not touch Agent Red or adopter fixtures. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge proposal, implementation report, and verification artifacts preserve the lifecycle audit chain without mutating unrelated formal artifacts. |

## Acceptance Criteria

- No currently configured harness has `event-source` in `config/dispatcher/rules.toml`.
- No current harness record in `harness-state/harness-registry.json` has `can_fire_events: true`, `event_driven_hooks: true`, or `event-source` in dispatch tags.
- No harness in `config/agent-control/declarative-agent-role-manifest.yaml` uses `dispatch_mode: event_source`; every harness still declares an explicit boolean `can_fire_events: false`.
- Runtime status/report output no longer presents any current harness as an active event source.
- `can_receive_dispatch` semantics, selected Prime Builder and Loyal Opposition dispatch targets, reviewer precedence, and quality/cost/availability routing metadata remain intact.
- Focused dispatcher, projection, manifest, and state-report tests pass.

## Pre-Filing Preflight Subsection

Candidate preflight commands were run against this completed draft before live filing:

- `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5020-retire-event-source-config-003.md --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5020-retire-event-source-config-003.md`

Observed applicability result:

- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- content_source: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5020-retire-event-source-config-003.md`

Observed clause result:

- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Exit code: 0

The governed revision helper reruns these candidate-content preflights before live filing.

## Risks / Rollback

Risk is moderate because the proposal changes dispatcher configuration and generated harness projection semantics after GO. The largest implementation risk is accidentally treating schema retention as trigger authority, or accidentally removing the `event_driven_hooks` fallback that protects legacy receive-dispatch records.

Rollback is a revert of source/config/test changes from the future implementation commit. Bridge files, project authorization records, and deliberation evidence are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/dispatcher/rules.toml`
- `harness-state/harness-registry.json`
- `config/agent-control/declarative-agent-role-manifest.yaml`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `groundtruth-kb/tests/test_agent_role_manifest.py`
- `groundtruth-kb/tests/test_harness_projection.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_transactions.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Out Of Scope

- Full removal of the `can_fire_events`, `event_driven_hooks`, or `event_source` schema/API fields.
- Edits to `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/harness_ops.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` beyond the already listed transaction tests, `scripts/dispatcher_runtime.py`, or `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
- WI-5012 duplicate-SoT consolidation of the broader dispatch fields (`can_fire_events`, `can_receive_dispatch`, `dispatch_availability`, `dispatch_cost`, and `dispatch_quality`) across persistent artifacts.

## Recommended Commit Type

`fix`
