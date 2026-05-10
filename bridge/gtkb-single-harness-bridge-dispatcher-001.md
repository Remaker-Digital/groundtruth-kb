NEW

# Implementation Proposal — Single-Harness Bridge Dispatcher (Architectural Plan + Slice 1 Governance Scaffolding)

bridge_kind: implementation_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC

## Claim

Establish single-harness operation as a first-class GroundTruth-KB configuration with a routine-based bridge dispatcher that fills in for the cross-harness event-driven trigger when only one AI harness is installed. The dispatcher periodically scans `bridge/INDEX.md`, classifies actionable entries by the role required for the next workflow step, and spawns self-targeted worker subprocesses with the appropriate `::init gtkb <mode>` canonical keyword + matching env-var marker.

This thread proposes the **architectural plan** and a **first slice (governance scaffolding)**:

- **Slice 1 (this thread):** governance scaffold — `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, role-set amendment to `.claude/rules/operating-role.md` and `harness-state/role-assignments.json` schema, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`.
- **Slice 2 (separate follow-on thread):** dispatcher implementation — Desktop scheduled task + dispatcher script + tests + system-interface-map.toml entry. Depends on Slice 1 VERIFIED + `gtkb-canonical-init-keyword-syntax-001` VERIFIED.

This thread also subsumes `gtkb-claude-code-bridge-status-thread-automation-001` per owner directive 2026-05-09. The bridge-status thread is paused at NO-GO `-004`; the use case it served (Axis 2 status surfacing) is covered in single-harness configs by this dispatcher and remains unaddressed in multi-harness configs (where the cross-harness trigger handles Axis 1 dispatch and Axis 2 surfacing is owner-manual via `Bridge` scan).

## Why Now

Owner question 2026-05-09: *"It may be possible for GT-KB to operate with only one harness, in which case we may need a routine/automation to fill in for the cross-harness dispatch. Is it possible to use a routine/automation to check the bridge periodically and dispatch work using the session initialization command that is appropriate for the role that is associated with each proposal's state?"*

Today the cross-harness event-driven trigger ([scripts/cross_harness_bridge_trigger.py:216-453](scripts/cross_harness_bridge_trigger.py:216)) registered as PostToolUse + Stop hooks dispatches counterpart harnesses when `bridge/INDEX.md` is updated. The trigger has no counterpart to dispatch to in single-harness configs. Manual `Bridge` scans remain available, but the parity goal of "owner doesn't have to babysit the bridge queue" requires automation when the harness is alone.

Owner directives 2026-05-09 affecting this thread:

- AUQ "Separate thread (Recommended)" — file as standalone, not folded into canonical-syntax.
- AUQ "Pause; subsume into single-harness dispatcher" — bridge-status thread paused; this thread covers its use case in single-harness configs.
- Strict-ignore-on-mismatch refinement to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — the dispatcher's worker subprocesses MUST silently drop dispatches whose keyword mode is not in the harness's durable role set.

## Why Not (alternatives considered)

- **Re-enable retired pollers**: rejected; the OS poller and smart poller were retired (Slice 4 VERIFIED) for token-cost regression. The dispatcher uses Desktop scheduled task + per-spawn env-var injection, with idle suppression at the routine layer.
- **Cloud Routines (`/schedule`)**: rejected per `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` F1. Cloud Routines run in cloud sessions against fresh repo clones with no local-file access. The dispatcher needs live `bridge/INDEX.md` reads, `harness-state/role-assignments.json` reads, and `claude -p` subprocess spawning with env-var injection. All require Desktop scheduled task semantics.
- **Session-scoped `/loop`**: rejected; works only while a session is running; doesn't survive `/exit`. The dispatcher must operate when no session is active.
- **Multi-harness assumption only**: rejected; the operating-model permits single-harness configs; the bridge protocol must serve them.
- **Per-session role override** (rejected per prior owner AUQ on canonical-syntax thread): would let the dispatcher force a role on its workers regardless of durable record. Conflicts with `operating-role.md` invariant. The role-set semantic is the chosen path: single-harness durable record holds `{pb, lo}`; worker checks set membership; mismatch = silent drop.

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001.md` (NEW; awaiting Codex review) — defines the `::init gtkb <mode>` syntax this dispatcher emits. Owner refinement 2026-05-09: strict-ignore-on-mismatch + role-set membership semantics. The canonical-syntax thread will land as REVISED with these refinements after Codex review; this dispatcher thread depends on its VERIFIED state for Slice 2 implementation.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` (NO-GO; paused per owner) — F1 surfaced the cloud-Routine vs Desktop-scheduled-task distinction; F2 surfaced the env-var-pre-SessionStart constraint. Both findings inform this dispatcher's Desktop-scheduled-task choice.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — Slice 4 retired Axis-1 dispatch pollers in multi-harness config. This dispatcher is single-harness-only; not in the retired class. The token-cost-regression lesson informs idle suppression design.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) — articulates the two-axis bridge automation model. In single-harness configs, the dispatcher serves both axes (dispatchable + non-dispatchable) since there is no counterpart harness for Axis 1 to target.
- `.claude/rules/operating-role.md` (canonical) — current single-role-per-harness assumption. This thread proposes role-set semantics as an extension.
- Auto-memory `feedback_init_keyword_as_role_symmetric_activator.md` and `feedback_investigate_claude_code_native_primitives_first.md` — owner principles informing the design.
- `DELIB-S339-2026-05-09-SINGLE-HARNESS-DISPATCHER-OWNER-DIRECTIVE` (pending DA harvest) — owner directive establishing the single-harness dispatcher requirement.
- `DELIB-S339-2026-05-09-STRICT-IGNORE-ON-MISMATCH-REFINEMENT` (pending DA harvest) — owner refinement to canonical-syntax DCL.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical workflow state; the dispatcher reads but does not author verdicts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`. Out-of-repo state (the installed Desktop scheduled task) is owner-managed inventory mirroring the cross-harness trigger pattern.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets required for new ADR + SPEC + DCL artifact insertions; narrative-artifact-approval packet required for `.claude/rules/operating-role.md` edit.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new ADR + SPEC + DCL are lifecycle events.

**Specs created by this slice (Slice 1):**

- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW) — single-harness operating mode as first-class GT-KB config; multi-harness assumption documented as one of two supported topologies.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW) — dispatcher behavior contract: Desktop scheduled task wakes; reads bridge state; classifies entries; spawns workers with canonical keyword + env-var marker; durable-role-set membership check on worker side; idle suppression on routine side.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW) — the dispatcher MUST be a Desktop scheduled task (local filesystem + tool access required); cloud Routines and `/loop` mechanisms are rejected.
- Amendment to `.claude/rules/operating-role.md` — role-set semantics replace single-role semantics; backward-compatible (singleton sets continue to work; multi-element sets enable single-harness configs).

**Specs to be exercised by Slice 2 (follow-on thread, not this slice):**

- The dispatcher implementation, Desktop scheduled task setup script, tests, system-interface-map.toml entry.

## Owner Decisions / Input

This proposal cites four explicit AskUserQuestion approvals plus standing parity directives. The bridge-compliance-gate hook checks this section is non-empty and substantive.

1. **AUQ 2026-05-09: file separate thread** — owner answer "Separate thread (Recommended)". Authorizes filing this NEW proposal as a standalone thread (not folded into canonical-syntax).
2. **AUQ 2026-05-09: subsume bridge-status thread** — owner answer "Pause; subsume into single-harness dispatcher". Bridge-status `-004` NO-GO is the terminal state of that thread; this dispatcher covers the use case in single-harness configs.
3. **AUQ 2026-05-09: strict-ignore semantic refinement** — owner directive: *"the hook should check the durable role record and ignore the notification if it doesn't match."* Drives the worker-side strict-ignore-on-mismatch contract in `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` and the parallel refinement to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (in canonical-syntax thread).
4. **AUQ 2026-05-09: consistency-assertion authority** (prior, on canonical-syntax thread) — keyword derived from durable role, not override. Carries forward to dispatcher worker semantics.

Owner-input dependencies during Slice 1 implementation:

- 1 narrative-artifact-approval packet for the `.claude/rules/operating-role.md` amendment.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase insertions.
- 1 acknowledgement of the role-set semantic before MemBase amendment lands.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection. Re-run after this NEW entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, no blocking clause gaps.

## Architectural Plan

### Topology

**Multi-harness config** (current default):
- Harness A (Codex), durable role set: `{lo}`
- Harness B (Claude Code), durable role set: `{pb}`
- Cross-harness event-driven trigger active; PostToolUse + Stop hooks dispatch counterpart on actionable INDEX changes.
- This dispatcher: NOT active. (Optional: could be enabled as supplementary status reporting; out of scope for this thread.)

**Single-harness config**:
- Single harness (Claude Code OR Codex), durable role set: `{pb, lo}`
- Cross-harness event-driven trigger registered but spawns nothing (no counterpart resolves).
- This dispatcher: ACTIVE. Desktop scheduled task wakes periodically, classifies INDEX entries by needed role, spawns workers via subprocess invocation.

The role-set on `harness-state/role-assignments.json` is the durable record that distinguishes the two topologies. Backward-compatible: singleton sets `{pb}` and `{lo}` are valid; doctor recognizes both topologies.

### Dispatcher behavior (single-harness)

```
[Desktop scheduled task wakes routine]
  routine prompt body:
  1. Read bridge/INDEX.md current SHA-256.
  2. Compare to last-wake hash at .gtkb-state/single-harness-dispatcher/last-index-hash.txt.
  3. If unchanged AND no fresh actionable entries: exit (idle suppression).
  4. Otherwise: parse INDEX; for each Document entry's latest status:
       - NEW or REVISED  → required role: lo  (work: review)
       - GO              → required role: pb  (work: implement after approval)
       - NO-GO           → required role: pb  (work: revise after rejection)
       - VERIFIED        → terminal; do not spawn
  5. For each actionable entry, decide whether the work is dispatchable
     to a fresh worker session or non-dispatchable (owner-input-required):
       - Dispatchable     → spawn worker subprocess with canonical keyword
       - Non-dispatchable → surface in routine conversation only
  6. Worker subprocess invocation (mirrors cross_harness_bridge_trigger.py):
       claude -p "<prompt>" --add-dir E:/GT-KB --output-format json
       OR
       codex exec "<prompt>" --cd E:/GT-KB
       env: GTKB_BRIDGE_POLLER_RUN_ID=<dispatch-id>
       prompt first line: ::init gtkb <mode>  (mode = lo or pb based on entry status)
  7. Worker SessionStart hook:
       - Reads env-var → bridge auto-dispatch context.
       - Reads first prompt line → keyword recognition.
       - Reads durable role set → set-membership check.
       - If keyword mode in role set: process the dispatch task.
       - If keyword mode not in role set: silently drop; exit.
  8. Persist new INDEX hash; routine session exits.
```

### Operating-role.md amendment shape

Current text (excerpt from `.claude/rules/operating-role.md`):

> "When a harness is assigned Prime Builder, all other recorded harnesses are demoted to Loyal Opposition in the same role-map update."
> "When a harness is assigned Loyal Opposition, only that harness's role changes; if this leaves no Prime Builder, the next harness startup self-corrects."

Proposed amendment (role-set semantics; backward-compatible):

> The `harness-state/role-assignments.json` schema records each harness ID's durable role as a SET of roles drawn from `{pb, lo}`. Multi-harness configs use singleton sets (e.g., harness A = `{lo}`, harness B = `{pb}`); single-harness configs use the multi-element set `{pb, lo}` on the lone harness.
> When a harness is assigned Prime Builder in a multi-harness config, all other recorded harnesses are demoted such that their role sets do not include `pb`. The "demote LO to keep one Prime Builder" invariant becomes "exactly one harness has `pb` in its role set" in multi-harness; in single-harness, the lone harness has both.
> When a harness is assigned Loyal Opposition in a multi-harness config, only that harness's set changes; if this leaves no `pb` in any harness's set, the next harness startup self-corrects per the existing rule.
> Single-harness configs require `{pb, lo}` on the lone harness; doctor flags singleton-only sets in single-harness configs as a configuration defect.

The amendment preserves the durable-role principle: roles attach to harness IDs, not to transient sessions. The set-membership check at SessionStart hook layer (proposed in canonical-syntax thread) operates on the set; per-dispatch role is asserted by keyword and validated by set membership.

### Idle suppression model (per Codex F3 lesson)

Per Codex `gtkb-claude-code-bridge-status-thread-automation-001-004.md` F3: idle suppression on the prompt body cannot cancel the scheduled session start; every wake pays the session-start cost.

This dispatcher's idle suppression is **routine-side** (acts on the Desktop scheduled task wake's outcome): the routine prompt body's hash check determines whether to spawn worker subprocesses. The routine itself still pays the per-wake cost (Desktop scheduled task starts a session that runs the routine prompt). Worker subprocesses are spawned only when the hash changes; worker cost is per-spawn.

Per-wake cost budget (60-min cadence):
- Routine session start: ~50k tokens (one wake regardless of bridge state).
- Worker subprocess(es): ~50k each (only when actionable entries exist).
- Quiet bridge: 24 routine wakes × 50k = 1.2M tokens/day; 0 worker spawns.
- Active bridge (4 actionable changes/day): 24 routine wakes + 4 workers × 50k = ~1.4M tokens/day.

Budget is comparable to the smart poller's pre-retirement profile. Worth owner-AUQ explicit approval before Slice 2 implementation. Cost-tuning options for Slice 2:
- Lower cadence (e.g., 4-hourly: 6 routine wakes/day; 0.3M tokens/day quiet baseline).
- Suppress worker spawns when a foreground harness session is detected (active-session suppression mirroring `gtkb-cross-harness-trigger-active-session-suppression-001` VERIFIED).
- Owner opt-in only.

These cost-tuning details are Slice 2 design; this slice (Slice 1) only proposes governance scaffold + architecture.

## Implementation Plan (Slice 1)

### IP-1 — `ADR-SINGLE-HARNESS-OPERATING-MODE-001`

MemBase insertion (`type='architecture_decision'`) with formal-artifact-approval packet. Body:

- **Decision:** GT-KB supports two harness topologies — multi-harness (default; current implementation) and single-harness (lone harness holds both `pb` and `lo` roles). Both are first-class.
- **Context:** Operating-model permits single-harness configs (one of Claude Code / Codex installed). Cross-harness event-driven trigger has no counterpart to dispatch to in single-harness; bridge protocol stalls without an alternative dispatch surface.
- **Failed approaches:** rejected per `Why Not` section above (re-enable pollers; cloud Routines; `/loop`; per-session role override).
- **Alternatives considered:** see `Why Not` section.
- **Consequences:** role-set semantics replace single-role semantics in `harness-state/role-assignments.json` (backward-compatible); doctor adds single-harness-config check; the dispatcher SPEC governs the routine implementation.

### IP-2 — `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`

MemBase insertion (`type='specification'`) with formal-artifact-approval packet. Body:

- **Title:** Single-Harness Bridge Dispatcher Behavior Contract.
- **Behavior:** as specified in "Architectural Plan / Dispatcher behavior" above. Preserves `bridge/INDEX.md` canonical-state authority; preserves bridge protocol audit trail; works around absence of counterpart harness by self-targeting.
- **Activation:** active when `harness-state/role-assignments.json` shows exactly one harness with role set `{pb, lo}`.
- **Cadence:** owner-tunable; default 60-min (subject to Slice 2 owner cost-approval AUQ).
- **Spawning contract:** workers spawned via the same subprocess invocation pattern as `cross_harness_bridge_trigger.py` with the env-var marker set pre-launch and the canonical `::init gtkb <mode>` keyword as first prompt line.
- **Worker-side contract (per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` strict-ignore refinement):** SessionStart hook reads env-var; if present, reads first prompt line; checks keyword mode against durable role set; if member, processes the dispatch; if not member, exits silently with audit-log entry.
- **Idle suppression:** routine-side hash-of-INDEX comparison gates worker spawns; per-wake routine cost accepted.

### IP-3 — `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`

MemBase insertion (`type='design_constraint'`) with formal-artifact-approval packet. Body:

- **Constraint:** the dispatcher MUST be implemented as a Windows Desktop scheduled task (or platform-equivalent local scheduler with local-filesystem and subprocess-spawning capability). Cloud Routines (`/schedule`) MUST NOT be used; session-scoped `/loop` MUST NOT be used; Codex app-thread automations MUST NOT be repurposed for this role.
- **Rationale:** per Codex F1/F2 of `gtkb-claude-code-bridge-status-thread-automation-001-004.md` — cloud Routines lack local-file access; routine prompt bodies cannot set env vars pre-SessionStart; only Desktop scheduled tasks can both (a) read live `bridge/INDEX.md` and (b) spawn worker subprocesses with env vars set pre-launch.
- **Assertions (machine-checkable):** Slice 2 setup script registers a Windows Desktop scheduled task; doctor check verifies the task exists when single-harness config is active; greps confirm the dispatcher script does not invoke `/schedule` or `ScheduleWakeup`.

### IP-4 — Amend `.claude/rules/operating-role.md`

Narrative-artifact-approval packet required (path is in the `narrative-artifact-approval.toml` protected list). Amendment shape per "Operating-role.md amendment shape" above.

### IP-5 — Amend `.claude/rules/canonical-terminology.md`

Per `DCL-CONCEPT-ON-CONTACT-001`, touching the load-bearing concept "single-harness operating mode" requires a glossary entry. Add new entries:

- **single-harness operating mode** — the GT-KB topology in which exactly one AI harness is installed; the lone harness holds both `pb` and `lo` roles. Defined by `ADR-SINGLE-HARNESS-OPERATING-MODE-001`. Contrast: multi-harness operating mode (current default).
- **role set** — the canonical durable role record of an AI harness in `harness-state/role-assignments.json`; a subset of `{pb, lo}`. Replaces the prior single-role semantic. Defined by `ADR-SINGLE-HARNESS-OPERATING-MODE-001`.
- **single-harness bridge dispatcher** — the routine-based dispatcher specified by `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` that fills in for the cross-harness event-driven trigger in single-harness configs.

Narrative-artifact-approval packet required.

### IP-6 — Doctor check additions (Slice 1 governance verification)

Add two doctor checks that run during health diagnostics:

- `_check_role_set_topology_consistency` — verifies `harness-state/role-assignments.json` schema matches the role-set semantic; flags singleton-only sets in single-harness configs as a defect.
- `_check_single_harness_dispatcher_when_required` — when single-harness topology is active, verifies the dispatcher Desktop scheduled task exists (or surfaces "single-harness without dispatcher" as a recommendation).

These checks are governance verification; the dispatcher implementation itself is Slice 2.

### IP-7 — Tests (Slice 1 scope)

- `tests/scripts/test_role_set_schema.py` (NEW) — schema test for `harness-state/role-assignments.json`; valid and invalid role-set forms; backward-compatible singleton acceptance.
- `tests/scripts/test_doctor_role_set_topology.py` (NEW) — exercises both new doctor checks against fixtures.
- `tests/scripts/test_operating_role_amendment_present.py` (NEW) — greps for the role-set semantic clauses landing in `.claude/rules/operating-role.md` post-amendment.
- `tests/scripts/test_canonical_terminology_single_harness_entries.py` (NEW) — greps for the three new glossary entries.

Slice 2 (separate follow-on thread) adds dispatcher script, Desktop scheduled task tests, system-interface-map entry, integration tests against the worker SessionStart bypass.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-role-set-schema-valid | IP-2 + IP-4 | `test_role_set_schema::test_valid_role_sets_accepted` — singleton `{pb}`, singleton `{lo}`, multi `{pb, lo}` all valid. |
| T-SHD-role-set-schema-invalid | IP-2 + IP-4 | `test_role_set_schema::test_invalid_role_sets_rejected` — empty set, unknown role tokens, scalars rejected. |
| T-SHD-doctor-role-set-topology | IP-6 | `test_doctor_role_set_topology::test_single_harness_singleton_flagged` and `::test_multi_harness_dual_role_flagged`. |
| T-SHD-doctor-dispatcher-recommendation | IP-6 | `test_doctor_role_set_topology::test_single_harness_without_dispatcher_recommendation`. |
| T-SHD-operating-role-amendment-present | IP-4 | `test_operating_role_amendment_present::test_role_set_semantic_clause_present` — greps for amendment text. |
| T-SHD-canonical-terminology-entries | IP-5 | `test_canonical_terminology_single_harness_entries` — three new glossary entries present with correct field shape. |
| T-SHD-adr-spec-dcl-membase-insertion | IP-1 + IP-2 + IP-3 | MemBase rows for `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` exist with formal-artifact-approval packet evidence. |

## Acceptance Criteria

- [ ] Codex confirms the architectural plan covers single-harness operation as a first-class config without compromising multi-harness defaults.
- [ ] Codex confirms the role-set semantic (replacing single-role) is backward-compatible with current multi-harness deployments.
- [ ] Codex confirms the worker-side strict-ignore-on-mismatch contract (silent drop when keyword mode not in role set) is the correct refinement of the original consistency-assertion semantic.
- [ ] Codex confirms the Desktop-scheduled-task choice is correctly justified by the F1/F2 findings of bridge-status `-004` (cloud Routines lack local-file access; routine prompt bodies can't set env vars pre-SessionStart).
- [ ] Codex confirms the Slice 1 / Slice 2 split is appropriate (governance scaffold lands first; impl follows after canonical-syntax + this slice both VERIFIED).
- [ ] Codex confirms the bridge-status thread subsumption (single-harness use case covered; multi-harness Axis 2 parity gap deferred) is consistent with owner directive.
- [ ] Codex confirms the cost model (per-wake routine cost regardless of suppression; worker cost only on actionable changes) addresses the F3 lesson from bridge-status `-004`.

## Risk / Rollback

- **Risk:** role-set amendment to `operating-role.md` could be misread by tools or scripts that assume singleton role. Mitigation: backward-compatible by construction; doctor checks the topology and flags inconsistencies; existing tests for singleton multi-harness pass unchanged.
- **Risk:** the dispatcher could mis-classify entries (e.g., misread INDEX as having a NEW when it's GO). Mitigation: SPEC defines exact classification rules; tests exercise classification; bridge protocol audit trail surfaces any mis-action via subsequent verdict.
- **Risk:** cost overrun if single-harness config is enabled with default 60-min cadence on a quiet bridge. Mitigation: 1.2M tokens/day is below the retired smart poller's pre-Slice-4 baseline; Slice 2 design includes owner-AUQ for explicit cadence approval and active-session suppression option.
- **Risk:** the dispatcher activates incorrectly in a multi-harness config (where the cross-harness trigger should handle it). Mitigation: SPEC activation predicate checks role set; doctor-test verifies; dispatcher script self-checks before spawning.
- **Risk:** narrative-artifact-approval gate on `operating-role.md` blocks the amendment due to packet mismatch. Mitigation: owner-AUQ packet authoring is part of the Slice 1 implementation work; sha256 of git-staged blob (LF-normalized) is the canonical hash per Slice C universal-floor pre-commit gate.

**Rollback:**
- Revert `.claude/rules/operating-role.md` amendment.
- Revert `.claude/rules/canonical-terminology.md` glossary entries.
- Mark `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` MemBase rows as superseded.
- Revert doctor checks.
- Delete the new test files.
- Revert `harness-state/role-assignments.json` to singleton schema (only required if any owner workstation has been migrated; for the GT-KB checkout, the schema is defined by tests).

## Files Expected To Change (Slice 1 only)

- `bridge/gtkb-single-harness-bridge-dispatcher-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).
- `.claude/rules/operating-role.md` — IP-4 amendment (narrative-artifact-approval packet required).
- `.claude/rules/canonical-terminology.md` — IP-5 glossary entries (narrative-artifact-approval packet required).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — IP-6 two new checks.
- `tests/scripts/test_role_set_schema.py` (NEW) — IP-7.
- `tests/scripts/test_doctor_role_set_topology.py` (NEW) — IP-7.
- `tests/scripts/test_operating_role_amendment_present.py` (NEW) — IP-7.
- `tests/scripts/test_canonical_terminology_single_harness_entries.py` (NEW) — IP-7.
- MemBase: `ADR-SINGLE-HARNESS-OPERATING-MODE-001` insertion (with packet); `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` insertion (with packet); `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` insertion (with packet).

## Subsumed Threads

- `gtkb-claude-code-bridge-status-thread-automation-001` (terminal at NO-GO `-004`) — paused per owner directive 2026-05-09. Single-harness use case covered by this dispatcher; multi-harness Axis 2 parity gap deferred to a future thread (no owner directive to revive at this time).

## Open Follow-Ons

1. **Slice 2** (separate thread, after Slice 1 + canonical-syntax both VERIFIED): dispatcher Desktop scheduled task implementation; setup/teardown scripts; system-interface-map.toml entry; integration tests; cadence + active-session suppression cost-tuning.
2. Future: multi-harness Axis 2 parity — if the owner re-prioritizes Claude-side bridge-status visibility in multi-harness configs, file a separate thread with a different mechanism (likely active-session in-process refresh hook rather than a routine).
3. Future: doctor topology detection automation — auto-promote a singleton harness to `{pb, lo}` when only one harness is installed; today this is owner-driven via explicit `harness_identity.py set` invocation.
4. Future: canonical-syntax thread `-002` REVISED-1 (after Codex review of `-001`) — incorporates strict-ignore-on-mismatch + role-set membership refinements per owner 2026-05-09 directive.

## Recommended Commit Type

`feat:` — net-new capability surface (single-harness operating mode as first-class config; role-set semantic; dispatcher governance scaffolding). Net-new ADR + SPEC + DCL artifacts; net-new doctor checks; canonical glossary expansion. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the architectural plan is sufficient for single-harness operation as a first-class config.
2. Confirm role-set semantics (replacing single-role) preserves the durable-role principle while enabling single-harness configs.
3. Confirm strict-ignore-on-mismatch is the correct refinement (silent drop > warn-and-fall-back).
4. Confirm the Slice 1 / Slice 2 split is reasonable (governance + spec + glossary + doctor land first; implementation follows after canonical-syntax + this slice are VERIFIED).
5. Confirm the Desktop-scheduled-task constraint in `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` is correctly motivated by Codex F1/F2 findings on bridge-status `-004`.
6. Confirm the bridge-status thread subsumption is consistent with owner directive (single-harness use case covered; multi-harness gap deferred without owner objection).
7. Confirm the cost model is realistic (per-wake routine cost ~50k regardless of idle suppression; worker spawn cost only on actionable changes).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
