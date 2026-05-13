NEW

# Implementation Proposal - Standard Bridge Automation Status Driver

**Document:** `gtkb-bridge-automation-status-driver`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Active workspace:** `E:\GT-KB`
**Recommended commit type:** `feat:`

## Claim

GT-KB has a canonical bridge dispatch mechanism and a two-axis bridge automation model, but it lacks one standard operational driver that tells agents and the owner what bridge automation is doing, what work is actionable, what is dispatchable, what requires the interactive thread, and whether the automation substrate is healthy.

The result is avoidable manual behavior: the owner can type `Bridge` and get a live scan, but the system does not provide one standard status/driver surface that agents, startup, doctor, and any future thread automation can all use. This proposal introduces that standard surface without restoring the retired smart poller or retired OS poller and without creating another out-of-repo Codex automation.

## Scope Summary

Implement a read-only bridge automation status driver that centralizes:

- live `bridge/INDEX.md` parsing and latest-status classification;
- role-correct actionability semantics;
- dispatchable versus non-dispatchable queue classification per the two-axis model;
- cross-harness trigger health and dispatch-state visibility;
- external thread-automation inventory visibility without treating external automations as canonical dispatch;
- deterministic CLI/status output suitable for startup, manual `Bridge` checks, and future owner-approved thread automation prompts.

This proposal does not authorize live dispatch rewrites, new recurring automations, Codex app automation creation, Claude app automation creation, Windows scheduled tasks, remote operations, or restoration of any retired poller.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains canonical queue state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal includes explicit governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include spec-derived verification and observed command results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB implementation and verification files remain within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge automation status is a durable operational artifact surface, not ad hoc chat-only behavior.
- `.claude/rules/file-bridge-protocol.md` - defines bridge lifecycle states and INDEX authority.
- `.claude/rules/bridge-essential.md` - contains the verified two-axis bridge automation model and retired-poller constraints.
- `.claude/rules/prime-bridge-collaboration-protocol.md` - frames cross-harness trigger failure and manual bridge fallback behavior.
- `config/agent-control/system-interface-map.toml` - current system inventory for `bridge-dispatch`, supplemental Codex thread monitors, retired smart poller, retired OS poller, and single-harness bridge dispatcher.
- `scripts/cross_harness_bridge_trigger.py` - canonical dispatch runtime for dispatchable bridge work.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` - existing shallow `bridge` and `bridge-dispatch` status probes to extend or wrap.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` - existing bridge-dispatch doctor checks to align with the new driver.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` - VERIFIED two-axis bridge automation model.
- `bridge/gtkb-bridge-skill-unified-001-004.md` - active NO-GO identifying incorrect Prime queue semantics around latest `VERIFIED` entries; this proposal must not inherit that error.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` and `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - VERIFIED single-harness dispatcher work that must remain a distinct runtime surface.

## Prior Deliberations

Deliberation searches were run on 2026-05-12 for bridge automation, status driver, cross-harness trigger, thread automation, and owner disposition. Relevant records:

- `DELIB-1520` - Loyal Opposition verification of the trigger-awareness and two-axis bridge automation model. This is the key positive authority for separating dispatchable work from non-dispatchable interactive thread work.
- `DELIB-1521` - Loyal Opposition GO for the two-axis bridge automation articulation.
- `DELIB-1522` - Loyal Opposition NO-GO on an earlier startup-trigger-awareness proposal. Relevant because it rejected ratifying specific Codex-side automations without owner disposition.
- `DELIB-1887` - compressed bridge thread for `gtkb-startup-trigger-awareness-and-skill-reference-001`, verified with six versions.
- `DELIB-1542` - Loyal Opposition verification of smart-poller retirement in favor of the cross-harness event-driven trigger.
- `DELIB-1516` and `DELIB-1517` - Loyal Opposition reviews of Claude Code bridge-status thread automation attempts. Relevant because this proposal must not skip owner disposition or misclassify thread automation as dispatch.
- `DELIB-1499` - Loyal Opposition review of cross-harness trigger Windows rename race and liveness diagnostics. Relevant because status/health should report dispatch-state reliability, not only queue counts.
- `DELIB-0121`, `DELIB-1063`, `DELIB-1064`, and `DELIB-1067` - older bridge ops / reporting / poller visibility context. These are historical context only; they do not supersede the verified two-axis model or the retired-poller prohibition.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` and `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - owner/policy context for the transition away from poller framing toward the cross-harness event-driven trigger.

## Owner Decisions / Input

The owner asked on 2026-05-12: `Shouldn't there be a standard automation to drive this behavior?` Prime Builder answered that the correct path is a standard bridge automation status and driver layer, not restoration of the retired poller. The owner then directed: `Please proceed with an implementation proposal.`

This chat directive authorizes filing this proposal. It is not treated as owner approval to create or modify external Codex app automations, Claude app automations, OS scheduled tasks, formal GOV/ADR/DCL/SPEC records, or any recurring runtime outside the repository.

## Current-State Evidence

- `config/agent-control/system-interface-map.toml` lists `bridge-dispatch` as the active canonical cross-harness event-driven trigger, with `scripts/cross_harness_bridge_trigger.py` as authoritative source.
- The same map records two Codex-side thread automations as supplemental monitoring and explicitly says their relationship is unconfirmed and owner-observation-only.
- The same map records retired smart poller and retired OS poller entries as retired and not to be restored.
- `.codex/hooks.json` and `.claude/settings.json` register `scripts/cross_harness_bridge_trigger.py` on tool-use/Stop surfaces, and `scripts/active_session_heartbeat.py` maintains active-session suppression state.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` can report bridge counts and dispatch-state presence, but it does not list actionable documents, explain role-specific next actions, detect stale dispatch signatures, distinguish dispatchable from interactive work, or report external automation disposition.
- A live `python -m groundtruth_kb status --component bridge --component bridge-dispatch --json` run on 2026-05-12 produced shallow PASS output, but not enough detail to answer the owner's operational question without an additional manual parse of `bridge/INDEX.md`.
- The active `gtkb-bridge-skill-unified-001` thread is latest `NO-GO` because the bridge skill incorrectly taught Prime Builder to treat latest `VERIFIED` entries as actionable. This proposal must pin the correct semantics in code tests: Prime actionability is latest `GO` or `NO-GO`; Loyal Opposition actionability is latest `NEW` or `REVISED`; latest `VERIFIED` and `WITHDRAWN` are terminal/non-actionable.

## Proposed Implementation

### IP-1 - Shared Bridge Queue Classifier

Add a shared implementation module, tentatively `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`, that parses `bridge/INDEX.md` and returns a stable queue snapshot.

Required behavior:

- Treat the live `bridge/INDEX.md` read as authoritative.
- Parse every `Document:` block and its version lines.
- Preserve unknown status lines in diagnostics rather than silently dropping them.
- Identify the latest status and latest file per document.
- Compute counts by latest status.
- Compute role-correct actionability:
  - Prime Builder: latest `GO` or `NO-GO` only.
  - Loyal Opposition: latest `NEW` or `REVISED` only.
  - `VERIFIED`, `WITHDRAWN`, and advisory/non-dispatch statuses are non-actionable for both roles unless a separate proposal expands the lifecycle contract.
- Include top-N ordered queue items with line numbers, document names, statuses, and paths.
- Include dispatch-axis classification:
  - `dispatchable`: queue items that the cross-harness trigger can hand to a fresh counterpart harness.
  - `interactive`: queue items that require owner input, formal approval packets, broad cross-thread coordination, or other context that a fresh spawned harness should not consume.
  - `terminal`: no action.
  - `unknown`: malformed or unsupported state.

### IP-2 - Bridge Automation Health Snapshot

Extend the same driver with a health snapshot that reads only local project state:

- hook registration status in `.claude/settings.json` and `.codex/hooks.json`;
- presence and parseability of `scripts/cross_harness_bridge_trigger.py`;
- dispatch-state path, recipients, latest known signatures, and last updated timestamps when present;
- active-session heartbeat lock status and age when present;
- external Codex thread-automation inventory entries from `config/agent-control/system-interface-map.toml`, explicitly marked `external_unverified` unless directly inspectable from the current runtime;
- retired smart poller / retired OS poller entries, explicitly marked retired and not usable as fallback.

This is a read-only status surface. It must not spawn harnesses, write dispatch-state, create Codex app automations, create scheduled tasks, or mutate hook configuration.

### IP-3 - CLI / Status Surface

Expose the driver through a deterministic command surface. Preferred implementation path:

- Add a `gt bridge` command group if it can be done without conflicting with the active `gtkb-bridge-skill-unified-001` NO-GO; otherwise add only `gt status --component bridge --component bridge-dispatch --json` enhancements in Slice 1 and defer the `gt bridge` group until the bridge-skill-unified NO-GO is resolved.
- Minimum command surface for this slice:
  - `python -m groundtruth_kb status --component bridge --component bridge-dispatch --json` includes actionable document lists, latest-status counts, and dispatch health evidence.
  - `python -m groundtruth_kb status --component bridge --component bridge-dispatch` renders a compact human-readable queue/health summary suitable for startup and manual `Bridge` responses.
- Optional follow-on command surface after dependency cleanup:
  - `python -m groundtruth_kb bridge status --json`
  - `python -m groundtruth_kb bridge scan --role prime-builder|loyal-opposition --json`
  - `python -m groundtruth_kb bridge health --json`

The implementation must not teach `VERIFIED` as Prime-actionable. Tests must lock that down.

### IP-4 - Startup / Manual Bridge Integration

Update startup/current-state reporting only after the driver exists and tests pass:

- Use the driver snapshot for startup bridge counts and top actionable items.
- Use the same driver output for manual `Bridge` responses where practical.
- Keep output compact: show counts, top Prime queue, top Loyal Opposition queue, dispatch health, and whether any item is classified as interactive rather than dispatchable.
- Do not add a new recurring automation in this slice.

### IP-5 - Documentation / Inventory Alignment

Update only existing documentation or inventory text needed to explain the new standard surface:

- `config/agent-control/system-interface-map.toml`: add or update a `bridge-status-driver` system entry if the implemented driver becomes a named system surface.
- Existing docs/reference page for status/bridge operation if present.
- Do not rename or ratify existing external Codex thread automations without a separate owner disposition.

## Out Of Scope

- Restoring the retired smart poller or retired OS poller.
- Creating new Codex app heartbeat/cron automations.
- Creating Claude-side thread automations.
- Creating Windows Task Scheduler, launchd, or systemd jobs.
- Changing cross-harness dispatch behavior beyond read-only status reuse.
- Treating latest `VERIFIED` entries as actionable queue work.
- Resolving the full `gtkb-bridge-skill-unified-001` NO-GO, except that this proposal's tests must not repeat that incorrect queue rule.
- Formal GOV/ADR/DCL/SPEC mutations without separate approval evidence.

## Specification-Derived Verification Plan

| Test ID | Requirement | Verification |
|---|---|---|
| T-driver-parser | `GOV-FILE-BRIDGE-AUTHORITY-001` | Unit test parses a representative `bridge/INDEX.md` fixture and preserves latest status/file/line for every document. |
| T-role-actionability | File bridge role semantics; `gtkb-bridge-skill-unified-001-004` F1 prevention | Unit test proves Prime queue is only `GO`/`NO-GO`, Loyal Opposition queue is only `NEW`/`REVISED`, and `VERIFIED`/`WITHDRAWN` are non-actionable. |
| T-axis-classification | Verified two-axis bridge automation model | Unit test classifies ordinary role-actionable items as dispatchable and owner-input/formal-approval markers as interactive/non-dispatchable. |
| T-health-hooks | Cross-harness trigger health | Unit test or integration test verifies health output detects `.claude/settings.json`, `.codex/hooks.json`, trigger script presence, and dispatch-state recipients. |
| T-status-json | Deterministic CLI/status surface | CLI test asserts `status --component bridge --component bridge-dispatch --json` emits counts, top actionable lists, dispatch health, and no retired-poller guidance. |
| T-status-text | Startup/manual readability | CLI or formatter test asserts compact text names canonical trigger, marks retired pollers retired, and lists top actionable items without overlong output. |
| T-no-side-effects | Read-only boundary | Test or code inspection verifies status driver does not call subprocess dispatch, write dispatch-state, create automations, or mutate hook files. |

Expected targeted commands:

```powershell
python -m pytest groundtruth-kb/tests/test_operating_state.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py -q --tb=short
python -m ruff check groundtruth-kb/src groundtruth-kb/tests
python -m ruff format --check groundtruth-kb/src groundtruth-kb/tests
```

Use narrower test targets if file names differ after implementation, but the implementation report must justify any substitutions.

## Acceptance Criteria

- A single shared status driver exists for bridge queue classification and bridge automation health.
- The driver reads live `bridge/INDEX.md` and reports latest-status counts plus role-correct top actionable items.
- Prime Builder actionability excludes `VERIFIED`.
- Loyal Opposition actionability is limited to `NEW`/`REVISED`.
- The driver distinguishes canonical dispatch from supplemental external thread monitoring.
- Retired pollers are reported as retired and never suggested as fallback automation.
- Existing `gt status` bridge/dispatch output becomes useful enough to answer the owner's `Bridge` question without ad hoc parsing.
- No new recurring automation is created by this slice.
- Tests pin queue semantics, health evidence, and read-only behavior.

## Risk And Mitigation

- **Risk:** The proposal overlaps with `gtkb-bridge-skill-unified-001` Slice 3.
  **Mitigation:** Implement the shared driver and status enhancements first; defer or gate any `gt bridge` command group until the skill-unified NO-GO is resolved or explicitly reconciled.

- **Risk:** Agents may interpret the driver as a replacement for cross-harness dispatch.
  **Mitigation:** Name it a status/driver surface, not a dispatch runtime, and make the health output identify `scripts/cross_harness_bridge_trigger.py` as canonical dispatch.

- **Risk:** External Codex thread automations are out-of-repo and cannot be verified from local files.
  **Mitigation:** Inventory them as external/unverified unless a future owner-approved connector or Codex app API makes them inspectable.

- **Risk:** Adding more status output could increase startup verbosity.
  **Mitigation:** Provide compact text for startup/manual use and detailed JSON for tools.

## Decision Requested From Loyal Opposition

Return `GO` if this proposal is sufficiently scoped to implement a read-only bridge automation status driver and status-surface enhancement without restoring retired pollers or creating new recurring automations.

Return `NO-GO` with required corrections if the scope should be narrower, if `gtkb-bridge-skill-unified-001` must be resolved first, or if the proposal needs different boundaries between dispatch, monitoring, and manual bridge scanning.
