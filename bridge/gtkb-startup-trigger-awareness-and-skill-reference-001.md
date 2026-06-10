NEW

# Implementation Proposal — Startup Payload Trigger Awareness + Skill Reference + Parallel-Automation Guidance

bridge_kind: prime_proposal
Document: gtkb-startup-trigger-awareness-and-skill-reference-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC

## Claim

Close the architectural gap between "cross-harness event-driven trigger exists and is correctly registered" and "agents create their own bridge-monitoring automations because the startup payload doesn't explain the trigger's role."

Three coordinated edits:

1. **Expand `BRIDGE_DISPATCH_ROLE_TEXT` in `scripts/session_self_initialization.py:151`** from descriptive ("trigger is registered as PostToolUse and Stop hooks; fires on tool-use and Stop; manual scans available; smart poller and OS poller archived") to **prescriptive** — declare the trigger as the canonical bridge dispatch mechanism, name the verification command (`gt project doctor`), acknowledge the refresh-already-running-session gap as a separate concern (covered by inventory entries `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread`), and reference the bridge skill at `.claude/skills/bridge/SKILL.md`.

2. **Add a startup-payload bridge-skill pointer.** New line in `_render_role_governance_stance` output: "Bridge skill: `.claude/skills/bridge/` (proposal/review/verification protocol; both harnesses load this skill at session start)." Agents discover the skill via the startup payload rather than by chance.

3. **Update `.claude/rules/bridge-essential.md`** with explicit parallel-automation guidance: a new subsection "Parallel Bridge Monitoring Automations" that (a) names the legitimate gap the trigger does NOT cover (refresh-already-running-session view of INDEX), (b) identifies the inventoried Codex-side automations as legitimate gap-fillers, (c) prohibits creating NEW parallel automations as substitutes for the trigger's dispatch responsibility, (d) requires owner approval before any new bridge-monitoring automation is added (whether GT-KB-side or harness-app-side).

This is a targeted, narrow slice. It does NOT modify the trigger itself, the bridge protocol, or the in-flight umbrella thread `gtkb-loyal-opposition-startup-symmetry-001`.

## Why Now

Owner observation 2026-05-09 — Codex created two Codex-app-side bridge-monitoring automations in the past two days (`monitor-gt-kb-bridge` 3-min cadence, then `gt-kb-bridge-monitor` 30-min cadence) despite the cross-harness event-driven trigger being live and correctly registered on both `.claude/settings.json` and `.codex/hooks.json`. Owner asked: "If Codex is aware of the cross-harness event trigger, why is it creating an automation? Shouldn't the session startup include a mention of this service and how to access it?"

Investigation confirmed:

- `BRIDGE_DISPATCH_ROLE_TEXT` (Slice 4 D5e) is descriptive but not prescriptive; it explains what the trigger IS, not what role it plays vs. parallel automations.
- `.claude/rules/bridge-essential.md` (Slice 4 D5 item 1) prohibits restoring the retired OS poller OR retired smart poller as substitutes — but does NOT prohibit creating NEW parallel automations under fresh names.
- `.claude/skills/bridge/` exists and is comprehensive, but the startup payload doesn't reference it; agents discover it incidentally.
- The trigger spawns NEW counterpart sessions on actionable INDEX changes; it does NOT refresh already-running sessions. That's a legitimate gap, but Codex was filling it without explicit owner authorization.

Closing this gap reduces the chance of governance drift via "third Codex-side automation" patterns, and gives agents a clear startup-time framing of "use the trigger; the bridge skill explains how; refresh-while-running is a separately-governed inventory item."

## Prior Deliberations

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` (VERIFIED at `-020`) — Slice 4 retirement; established the cross-harness event-driven trigger as canonical dispatch mechanism.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — owner authorization for Slice 4.
- `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` and `id = "gt-kb-bridge-monitor-codex-thread"` — inventory entries for the two existing Codex-side automations (per AUQs "Inventory only" 2026-05-09 and "Capture -006 verdicts + inventory new gt-kb-bridge-monitor + file umbrella REVISED-3" 2026-05-09).
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-007` — in-flight umbrella REVISED-3; this thread is independent and does not modify the umbrella's scope.
- `.claude/skills/bridge/SKILL.md` — comprehensive bridge protocol skill; current source of truth for proposal/review/verification mechanics.
- `feedback_init_keyword_as_role_symmetric_activator.md` — owner-confirmed framing 2026-05-09; the init keyword IS the role-symmetric activator. This proposal complements that framing by ensuring the startup payload describes WHAT activates rather than just relaying neutral text.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; this slice does not modify the bridge protocol, only the startup-time framing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps each cited specification to at least one test.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packet required for the `.claude/rules/bridge-essential.md` edit (narrative-authority surface per `narrative-artifact-approval.toml` `role-and-governance-rules` family) AND for the new DCL.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner direction interpreted as design choice flowing through formal artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — supersession of prior descriptive `BRIDGE_DISPATCH_ROLE_TEXT` content with prescriptive content.

**New specs created by this slice:**

- `DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001` v1 (NEW; design_constraint) — machine-checkable: the session startup payload (per `scripts/session_self_initialization.py`) MUST inform agents that the cross-harness event-driven trigger is the canonical bridge dispatch mechanism; MUST reference `.claude/skills/bridge/`; MUST acknowledge the refresh-already-running-session gap by pointing to `system-interface-map.toml` inventory entries; MUST NOT describe the trigger as merely "registered as hooks" without explaining its canonical-mechanism role. Approval-packet-gated.

## Owner Decisions / Input

- AUQ "File a separate bridge thread to expand startup payload (Recommended)" 2026-05-09 — owner authorized this thread.
- Prior AUQs on inventory work for `monitor-gt-kb-bridge` and `gt-kb-bridge-monitor` are referenced as context; this proposal does not re-open those decisions.

The new DCL + the bridge-essential.md edit each require an owner formal-artifact-approval packet during the implementation phase (per IP-IIa + IP-IIb below). Each AUQ presents the full content; verbatim answer captured in packet's `explicit_change_request` field. Per-artifact packet (no scoped-auto-approval batch this round).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Implementation Plan

### IP-1 — Expand `BRIDGE_DISPATCH_ROLE_TEXT`

In `scripts/session_self_initialization.py:151` (the constant currently set in Slice 4 D5e), replace:

```python
BRIDGE_DISPATCH_ROLE_TEXT = (
    "cross-harness event-driven trigger registered as PostToolUse and Stop hooks "
    "(.claude/settings.json, .codex/hooks.json); fires on tool-use and Stop "
    "rather than on a fixed interval; manual bridge/INDEX.md scans available "
    "as fallback; retired smart poller and OS poller remain archived"
)
```

With:

```python
BRIDGE_DISPATCH_ROLE_TEXT = (
    "the cross-harness event-driven trigger (scripts/cross_harness_bridge_trigger.py) "
    "is the canonical bridge dispatch mechanism; registered as PostToolUse and Stop "
    "hooks in .claude/settings.json and .codex/hooks.json; fires on tool-use and Stop "
    "rather than on a fixed interval. Verify health via 'gt project doctor' "
    "(_check_cross_harness_trigger and _check_bridge_dispatch_liveness checks). "
    "The trigger spawns counterpart harness sessions on actionable INDEX changes; "
    "it does NOT refresh already-running sessions — that's a separate concern "
    "covered by inventoried Codex-side automations (system-interface-map.toml ids "
    "monitor-gt-kb-bridge-codex-thread, gt-kb-bridge-monitor-codex-thread). "
    "Do NOT create additional parallel monitoring automations without owner approval. "
    "Manual bridge/INDEX.md scans remain available as fallback; retired smart poller "
    "and OS poller are archived under archive/smart-poller-2026-05-09/"
)
```

This is a one-line constant edit (with a longer string value); `scripts/session_self_initialization.py` is NOT in the narrative-artifact-approval protected list; direct edit, no packet required.

### IP-2 — Add bridge-skill startup-payload pointer

In `scripts/session_self_initialization.py` `_render_role_governance_stance` output (the bullet list emitted under `### Role And Governance Stance`), add a new bullet after the existing "Bridge dispatch:" line:

```
- Bridge skill: `.claude/skills/bridge/` — proposal/review/verification protocol; both harnesses load this skill at session start. Use this for filing proposals, reviewing NEW/REVISED entries, and writing verdicts.
```

The bullet is rendered for all three role profiles (prime-builder, acting-prime-builder, loyal-opposition).

### IP-3 — Update `.claude/rules/bridge-essential.md`

Add a new subsection "## Parallel Bridge Monitoring Automations" after the existing "## Bridge Dispatch Enablement Contract" section. Content:

```markdown
## Parallel Bridge Monitoring Automations

The cross-harness event-driven trigger spawns NEW counterpart harness sessions
on actionable INDEX changes. It does NOT refresh already-running sessions'
view of INDEX. That's a legitimate gap, currently filled by Codex-side
thread automations inventoried in `config/agent-control/system-interface-map.toml`:

- `monitor-gt-kb-bridge-codex-thread` (3-minute cadence; lifecycle_state=active).
- `gt-kb-bridge-monitor-codex-thread` (30-minute cadence; lifecycle_state=active).

Both are owner-managed via the Codex app UI; both are out-of-repo. Both are
supplemental_monitoring (concept_vs_artifact); neither dispatches counterpart
harnesses or modifies dispatch state. Both are deliberate gap-fillers for
the refresh-already-running-session pattern.

DO NOT create additional bridge-monitoring automations (Codex-side, Claude-side,
or otherwise) as substitutes for the cross-harness event-driven trigger's
dispatch responsibility. Adding a new bridge-monitoring automation requires:

1. Owner approval via AskUserQuestion (the canonical decision channel per
   the AUQ-only enforcement stack).
2. A new `[[systems]]` entry in `config/agent-control/system-interface-map.toml`
   classifying the automation's role (supplemental_monitoring vs dispatch
   vs other) and lifecycle_state.
3. Update to this section if the new automation's role overlaps with the
   trigger's dispatch responsibility.

This rule is intended to prevent governance drift via well-intentioned but
duplicative monitoring automations.
```

`.claude/rules/bridge-essential.md` is in the narrative-artifact-approval `role-and-governance-rules` family; requires formal-artifact-approval packet per IP-IIa.

### IP-IIa — Approval packet for `.claude/rules/bridge-essential.md` edit

Before applying the IP-3 edit:

1. Present full updated content to owner via AUQ (full file text rendered).
2. Owner AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-bridge-essential-md-second-edit.json` with the schema-correct fields (per `formal-artifact-approval-gate.py`):
    - `artifact_type: "narrative_artifact"` (per narrative-artifact-approval.toml schema)
    - `artifact_id: "claude-rules-bridge-essential-md"`
    - `action: "update"`
    - `target_path: ".claude/rules/bridge-essential.md"`
    - `source_ref: "bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md"`
    - `full_content`, `full_content_sha256` (post-edit)
    - `approval_mode: "approve"`
    - `presented_to_user: true`, `transcript_captured: true`
    - `explicit_change_request: <verbatim AUQ answer>`
    - `changed_by: "claude-prime-builder"`
    - `change_reason`
4. Apply the edit via Python write (matches the Slice 4 D5 item 1 pattern; sha256 reconciled with on-disk content).

### IP-IIb — Approval packet for `DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001` v1

Before MemBase insert:

1. Present full DCL content (id, title, description, assertions) to owner via AUQ.
2. Owner AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001.json` with schema-correct fields (per `formal-artifact-approval-gate.py`):
    - `artifact_type: "design_constraint"`
    - `artifact_id: "DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001"`
    - `action: "create"`
    - `source_ref: "bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md"`
    - `full_content` (TITLE + DESCRIPTION + assertions), `full_content_sha256`
    - `approval_mode: "approve"`, `approved_by: "owner"`
    - `presented_to_user: true`, `transcript_captured: true`
    - `explicit_change_request: <verbatim AUQ answer>`
    - `changed_by: "claude-prime-builder"`
    - `change_reason`
4. Pre-insertion dry-run validation (mirroring decision-tracker IP-IIa pattern).
5. Run `db.insert_spec(...)` with `GTKB_FORMAL_APPROVAL_PACKET=<packet path>` env var.

### IP-3b — Tests

New tests in `tests/scripts/test_session_self_initialization.py`:

- `test_bridge_dispatch_role_text_declares_canonical_mechanism` — assert `BRIDGE_DISPATCH_ROLE_TEXT` contains "canonical bridge dispatch mechanism".
- `test_bridge_dispatch_role_text_references_doctor_verification` — assert text contains "gt project doctor" and the two doctor check names.
- `test_bridge_dispatch_role_text_acknowledges_refresh_running_gap` — assert text references the inventoried Codex-side automation IDs.
- `test_bridge_dispatch_role_text_prohibits_parallel_automations` — assert text contains "Do NOT create additional parallel monitoring automations".
- `test_startup_payload_includes_bridge_skill_pointer` — assert role-governance stance section contains `.claude/skills/bridge/` reference.

New tests in `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` (or sibling): assert `.claude/rules/bridge-essential.md` post-edit contains the "Parallel Bridge Monitoring Automations" section header AND the prohibition wording.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-START-canonical-mechanism-declared | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | `BRIDGE_DISPATCH_ROLE_TEXT` contains "canonical bridge dispatch mechanism". |
| T-START-doctor-verification-referenced | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | Text contains "gt project doctor" AND "_check_cross_harness_trigger" AND "_check_bridge_dispatch_liveness". |
| T-START-refresh-gap-acknowledged | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | Text contains both `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread` ids. |
| T-START-parallel-automation-prohibition | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | Text contains "Do NOT create additional parallel monitoring automations". |
| T-START-bridge-skill-pointer | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | Role-governance stance bullets include a `.claude/skills/bridge/` reference. |
| T-START-bridge-essential-parallel-section-present | DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001 | `.claude/rules/bridge-essential.md` contains "## Parallel Bridge Monitoring Automations" section header AND inventoried-automation ids AND prohibition wording. |

## Acceptance Criteria

- [ ] Codex confirms IP-1 prescriptive expansion is correctly scoped (does not over-claim authority on parallel automations beyond what the Codex-side AUQs already established).
- [ ] Codex confirms IP-2 bridge-skill pointer is correctly placed in role-governance stance and applies to all three role profiles.
- [ ] Codex confirms IP-3 bridge-essential.md addition (Parallel Bridge Monitoring Automations section) does not contradict prior text and matches inventory entries' lifecycle states.
- [ ] Codex confirms IP-IIa + IP-IIb approval-packet recipes match `formal-artifact-approval-gate.py` schema (artifact_type valid; approval_mode valid; approved_by present; REQUIRED_PACKET_FIELDS complete).
- [ ] Codex confirms 1 new DCL + 1 narrative-authority edit approval-batch is the right shape.

## Risk / Rollback

- **Risk: prescriptive trigger framing creates a false expectation that all monitoring automations are now forbidden.** Mitigation: IP-3's "Parallel Bridge Monitoring Automations" section explicitly carves out the legitimate gap (refresh-already-running) and names the existing inventoried automations as legitimate gap-fillers. The prohibition is on NEW unsanctioned automations, not on the inventory entries.
- **Risk: bridge-skill pointer adds startup-payload size.** Mitigation: one-line bullet; negligible token cost vs the existing payload.
- **Risk: future architectural changes (e.g., a unified bridge skill that absorbs the monitor automations into a Claude-side service) would require updating both `bridge-essential.md` and `BRIDGE_DISPATCH_ROLE_TEXT`.** Mitigation: that's normal artifact maintenance; not a slice-4-class regression risk.

**Rollback:** revert the three edits + the new DCL (append v2 marking superseded). Spec history preserved.

## Files Expected To Change

- `scripts/session_self_initialization.py` — IP-1 `BRIDGE_DISPATCH_ROLE_TEXT` constant; IP-2 bridge-skill pointer in role-governance stance.
- `.claude/rules/bridge-essential.md` — IP-3 "Parallel Bridge Monitoring Automations" subsection (formal-artifact-approval packet via IP-IIa).
- `tests/scripts/test_session_self_initialization.py` — 5 new test assertions per IP-3b.
- `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` (or sibling) — bridge-essential.md content assertion.
- `groundtruth.db` — 1 new DCL insert (per IP-IIb).
- `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-bridge-essential-md-second-edit.json` (IP-IIa).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001.json` (IP-IIb).
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Open Follow-Ons

1. Future: if the refresh-already-running gap becomes a recurring source of governance friction, evaluate whether a Claude-native equivalent of `gt-kb-bridge-monitor` should be added (currently Codex-only, asymmetric).
2. Future: if Codex's automations evolve (e.g., the 30-min cadence drops further or the 3-min one is retired), update the `system-interface-map.toml` lifecycle_states accordingly.

## Recommended Commit Type

`feat:` — net-new operational capability (prescriptive trigger framing in startup; bridge-skill pointer; parallel-automation governance rule). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the prescriptive expansion of `BRIDGE_DISPATCH_ROLE_TEXT` is correctly framed (canonical mechanism + verification command + refresh gap + parallel-automation prohibition).
2. Confirm the bridge-skill pointer is correctly placed and applies to all three role profiles.
3. Confirm `.claude/rules/bridge-essential.md` "Parallel Bridge Monitoring Automations" subsection content is accurate (legitimate gap-fillers vs prohibited new automations).
4. Confirm the 1-DCL + 1-narrative-authority approval-batch is the right shape.
5. Confirm this thread does not introduce scope conflicts with the in-flight umbrella `gtkb-loyal-opposition-startup-symmetry-001-007`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
