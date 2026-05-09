REVISED

# Implementation Proposal — Two-Axis Bridge Automation Articulation in Startup Payload — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-startup-trigger-awareness-and-skill-reference-001
Version: 003 (REVISED-1 post NO-GO at `-002` + owner architectural reframe 2026-05-09)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses ALL three Loyal Opposition findings F1 (P1), F2 (P2), F3 (P3) from `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-002.md` AND incorporates the owner's architectural clarification 2026-05-09 ("the automation should scan the bridge and update the chat on the status of all work that is in-flight; the interactive session will take the work which cannot be dispatched to a sub-agent").

Per owner AUQ "Minimal: rewrite BRIDGE_OPERATION_INSTRUCTIONS_TEXT + bridge-essential.md two-axis section only (Recommended)" 2026-05-09, scope is dramatically reduced from `-001`:

- **DROPPED:** new DCL `DCL-BRIDGE-STARTUP-TRIGGER-AWARENESS-001` (Codex F1: would ratify Codex-app automations as canonical without explicit owner authorization).
- **DROPPED:** new bullet `Bridge skill: .claude/skills/bridge/` (Codex F2: `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` already exists at `scripts/session_self_initialization.py:157-162` and references the skill).
- **DROPPED:** new DELIB `DELIB-S339-OWNER-THREAD-AUTOMATION-AS-FIRST-CLASS-ARCHITECTURAL-PEER-2026-05-09` (no MemBase mutation needed for this slice).
- **DROPPED:** owner disposition AUQ for existing Codex-app automations (separate concern; not blocking this slice).
- **DROPPED:** `system-interface-map.toml` `concept_vs_artifact` rename for the two thread automations (separate concern; this slice doesn't need to rename them to articulate the architecture).

What remains: a tightly scoped two-edit slice that rewrites the existing `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` to articulate the two-axis model and adds a corresponding "Two-Axis Bridge Automation Model" section to `.claude/rules/bridge-essential.md`.

### Codex NO-GO findings — closure

**F1 (P1):** Don't ratify existing automations as canonical/legitimate without explicit owner approval.

- **Closure:** REVISED-1 does NOT claim the existing automations are "legitimate gap-fillers" or "deliberate gap-fillers" (those phrases removed). Instead, REVISED-1 articulates the two-axis ARCHITECTURE without naming specific existing automations as canonical examples. The architecture is owner-articulated (axis 1 = dispatchable, trigger; axis 2 = non-dispatchable, thread-automation pattern). Whether `monitor-gt-kb-bridge` and `gt-kb-bridge-monitor` continue, retire, or get formalized is a SEPARATE owner-disposition concern not addressed here.
- The `system-interface-map.toml` inventory entries remain unchanged in this slice (their `concept_vs_artifact` value `"supplemental_monitoring"` stays; rename is deferred).

**F2 (P2):** Don't duplicate `BRIDGE_OPERATION_INSTRUCTIONS_TEXT`; rewrite it.

- **Closure:** REVISED-1's IP-1 REWRITES the existing `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` constant in place. No new bullet added. The skill reference (`gtkb-bridge` skill, both `.claude/` and `.codex/` paths) carries forward unchanged. The trigger entry-point reference carries forward unchanged. The narrow prohibition wording (`"do not create Codex app heartbeat/cron automations as bridge monitors"`) is REPLACED with axis-aware guidance.

**F3 (P3):** Test plan should guard against contradictory startup policy, not just substring presence.

- **Closure:** REVISED-1 UPDATES the existing test assertions at `tests/scripts/test_session_self_initialization.py:114-116, 692-693, 882-884, 1349-1351` to match the new wording. No new test methods are added; the existing test methods are updated to assert the two-axis-aware wording. This guarantees no contradiction between old and new assertions because the old assertions are removed in the same edit.

## Claim

Articulate the two-axis bridge automation model at startup time so agents understand the architecture from session start: axis 1 (dispatchable work → cross-harness event-driven trigger) and axis 2 (non-dispatchable work → thread automation pattern). The current `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` contains a narrow prohibition that's mechanically right but architecturally incomplete; REVISED-1 replaces it with axis-aware guidance that fits the owner-articulated two-axis model.

This is a minimal, surgical slice: 1 startup-payload constant rewrite + 1 narrative-authority subsection addition + corresponding test-assertion updates.

## Why Now

(Carried forward from `-001`; refined per owner reframe.)

Owner observation 2026-05-09 — Codex created two Codex-app-side thread automations (`monitor-gt-kb-bridge` 3-min, `gt-kb-bridge-monitor` 30-min) despite `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` containing the prohibition. Owner clarified the architectural model: thread automation is a first-class peer for non-dispatchable work, not a duplicative monitor. The current prohibition wording is too narrow to cover the legitimate non-dispatchable role; agents reading it interpreted it as "automations that REPLACE the trigger are forbidden" (correct) and inferred "automations for OTHER roles (e.g., interactive status reporting) are permitted" (also correct under the two-axis model, but not articulated).

REVISED-1 closes the architecture-articulation gap: replace the narrow prohibition with axis-aware guidance that says "dispatchable work uses the trigger; non-dispatchable work uses thread automation; do not create new automations without owner approval and axis classification."

## Prior Deliberations

- All records cited in `-001` carry forward unchanged.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-002.md` — Codex NO-GO with F1/F2/F3. All three addressed in this REVISED-1.
- Owner architectural clarification 2026-05-09: thread automation is first-class peer of trigger, handling non-dispatchable work. Captured as an observation in this proposal's Why Now / Claim sections; no new MemBase deliberation inserted (per scope reduction).
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-007` — in-flight umbrella REVISED-3; this thread is independent and does not modify the umbrella's scope.
- `feedback_init_keyword_as_role_symmetric_activator.md` — owner-confirmed framing 2026-05-09. The two-axis model in this proposal complements (does not contradict) the init-keyword-as-activator framing.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; this slice does not modify the bridge protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packet required for the `.claude/rules/bridge-essential.md` edit (narrative-authority surface per `role-and-governance-rules` family).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` content supersession.

**Specs preserved unchanged (no new specs created in REVISED-1):**

- No new DCL (per scope reduction).
- No new DELIB (per scope reduction).

## Owner Decisions / Input

- AUQ "File a separate bridge thread to expand startup payload (Recommended)" 2026-05-09 — owner authorized this thread.
- AUQ "File Prime-side REVISED-1 -002 now incorporating the new model (Recommended)" 2026-05-09 — owner authorized REVISED-1 (Codex landed NO-GO -002 in parallel; this becomes -003).
- AUQ "Minimal: rewrite BRIDGE_OPERATION_INSTRUCTIONS_TEXT + bridge-essential.md two-axis section only (Recommended)" 2026-05-09 — owner approved the scope reduction.
- 1 owner-AUQ acknowledgement required during implementation: the formal-artifact-approval packet for the `.claude/rules/bridge-essential.md` edit (per IP-IIa). No new MemBase artifact AUQs (no new DCL, no new DELIB).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED-1 lands at `-003`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Clause preflight expected exit 0.

## Implementation Plan

### IP-1 — Rewrite `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` (REVISED PER F2)

In `scripts/session_self_initialization.py:157-162`, replace:

```python
BRIDGE_OPERATION_INSTRUCTIONS_TEXT = (
    "use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter "
    "`.codex/skills/bridge/SKILL.md`) for manual bridge scans, reviews, and verifications; "
    "dispatch service entry point: `scripts/cross_harness_bridge_trigger.py`; do not create "
    "Codex app heartbeat/cron automations as bridge monitors"
)
```

With:

```python
BRIDGE_OPERATION_INSTRUCTIONS_TEXT = (
    "Bridge automation has two complementary axes. "
    "AXIS 1 (DISPATCHABLE WORK): the cross-harness event-driven trigger "
    "(`scripts/cross_harness_bridge_trigger.py`) is the canonical mechanism for "
    "self-contained work — reviews, verdicts, tests, work that a freshly-spawned "
    "counterpart harness can complete without further owner input. Registered as "
    "PostToolUse and Stop hooks. "
    "AXIS 2 (NON-DISPATCHABLE WORK): a thread automation pattern wakes the "
    "interactive chat session periodically to scan `bridge/INDEX.md` and surface "
    "work that requires interactive owner input mid-stream — owner-AUQ-required "
    "decisions, multi-turn review with accumulating context, cross-thread "
    "coordination, AUQ-heavy implementation. "
    "Both axes are required; their roles do not overlap. "
    "Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter "
    "`.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. "
    "Manual `bridge/INDEX.md` scans remain available as fallback. "
    "Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) "
    "without owner approval; any new automation must be classified by axis "
    "(dispatchable vs non-dispatchable) and inventoried in "
    "`config/agent-control/system-interface-map.toml`."
)
```

The skill reference, trigger entry-point reference, and the prohibition all carry forward; the prohibition wording is broadened from "Codex app heartbeat/cron automations as bridge monitors" (axis-narrow) to "new bridge automations ... without owner approval" (axis-aware).

### IP-2 — Update existing test assertions (REVISED PER F3)

In `tests/scripts/test_session_self_initialization.py`, update the existing assertions at lines 114-116, 692-693, 882-884, 1349-1351 (per Codex `-002` evidence) to match the new wording. The old assertions match strings like `"do not create Codex app heartbeat/cron automations as bridge monitors"`; the new assertions match strings like `"two complementary axes"` AND `"DISPATCHABLE WORK"` AND `"NON-DISPATCHABLE WORK"` AND `"Both axes are required"` AND `"Do NOT create new bridge automations"`.

This is REPLACE-not-ADD — no new test methods, just updated assertions. Guarantees no contradiction between old and new wording per F3.

### IP-3 — Add "Two-Axis Bridge Automation Model" section to `.claude/rules/bridge-essential.md` (REVISED FROM `-001` IP-3)

Add a new subsection placed after `## Bridge Dispatch Enablement Contract`:

```markdown
## Two-Axis Bridge Automation Model

Bridge automation has two complementary first-class axes, each with a
distinct role in the bridge protocol's autonomous-vs-interactive dispatch
model:

### Axis 1: Dispatchable work — cross-harness event-driven trigger

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`)
is the canonical mechanism for **dispatchable work** — work that can be
completed by a freshly-spawned counterpart harness session without further
owner input. Registered as PostToolUse and Stop hooks in
`.claude/settings.json` and `.codex/hooks.json`. Fires on tool-use and Stop.
Spawns counterpart harness sessions when actionable INDEX changes are
detected.

Examples of dispatchable work:
- Loyal Opposition reviews of NEW or REVISED proposals.
- Loyal Opposition verifications of post-implementation reports.
- Self-contained test runs.
- Verdict file authoring.

### Axis 2: Non-dispatchable work — thread automation pattern

A thread automation pattern wakes the interactive chat session
periodically. Its role is to scan `bridge/INDEX.md` and surface work that
**cannot be dispatched to a sub-agent** — work requiring interactive owner
input mid-stream, accumulating context across turns, or coordination across
threads.

Examples of non-dispatchable work:
- Owner-AUQ-required decisions (approvals, waivers, priority choices,
  formal artifact approvals).
- Multi-turn review where context accumulates and a fresh harness would
  lose thread.
- Cross-thread coordination (e.g., umbrella proposal referencing sibling
  threads needing owner sequencing).
- Implementation work that interleaves owner approval packets with code
  changes.

Currently the thread automation pattern is implemented Codex-side only
(the inventoried automations under `config/agent-control/system-interface-map.toml`).
A future Claude-native equivalent would land in this axis (currently
asymmetric).

### Both axes required; roles do not overlap

The cross-harness trigger does NOT refresh already-running interactive
sessions, and the thread automation does NOT spawn counterpart harness
sessions. They are complementary, not duplicative.

### Adding new bridge automation

DO NOT create additional bridge automations as substitutes for either axis
without owner approval. Adding a new bridge automation requires:

1. Owner approval via AskUserQuestion (the canonical owner-decision channel
   per the AUQ-only enforcement stack).
2. Classification by axis (dispatchable vs non-dispatchable).
3. A new `[[systems]]` entry in `config/agent-control/system-interface-map.toml`
   with `concept_vs_artifact` reflecting the axis.
4. Update to this section if the new automation's role overlaps with an
   existing surface.

This section articulates the architecture; it does NOT ratify any specific
existing automation as canonical. Owner disposition of currently-inventoried
Codex-app automations (`monitor-gt-kb-bridge-codex-thread`,
`gt-kb-bridge-monitor-codex-thread`) is a separate concern not addressed
in this slice.
```

`.claude/rules/bridge-essential.md` is in the narrative-artifact-approval `role-and-governance-rules` family; requires formal-artifact-approval packet per IP-IIa.

### IP-IIa — Approval packet for `.claude/rules/bridge-essential.md` edit

Same recipe as Slice 4 D5 item 1 (which landed an earlier `bridge-essential.md` packet successfully):

1. Present full updated content to owner via AUQ (full file text rendered).
2. Owner AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-bridge-essential-md-second-edit.json` with the schema-correct fields per `narrative-artifact-approval.toml`:
    - `artifact_type: "narrative_artifact"`
    - `artifact_id: "claude-rules-bridge-essential-md"`
    - `action: "update"`
    - `target_path: ".claude/rules/bridge-essential.md"`
    - `source_ref: "bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md"`
    - `full_content`, `full_content_sha256` (post-edit; reconciled with on-disk CRLF content)
    - `approval_mode: "approve"`
    - `presented_to_user: true`, `transcript_captured: true`
    - `explicit_change_request: <verbatim AUQ answer>`
    - `changed_by: "claude-prime-builder"`
    - `change_reason`
4. Apply the edit via Python write (matches the Slice 4 D5 item 1 pattern).

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| (existing tests at `tests/scripts/test_session_self_initialization.py:114-116, 692-693, 882-884, 1349-1351` — REPLACED, not added) | F2/F3 fix; current `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` assertion | Updated to assert "two complementary axes", "DISPATCHABLE WORK", "NON-DISPATCHABLE WORK", "Both axes are required", "Do NOT create new bridge automations". |
| T-START-bridge-essential-two-axis-section | F1 fix; `.claude/rules/bridge-essential.md` content | Read `bridge-essential.md` post-edit; assert presence of "## Two-Axis Bridge Automation Model" header + both axis subsection headers + "Both axes required; roles do not overlap" wording + "DO NOT create additional bridge automations as substitutes for either axis without owner approval" wording. |

## Acceptance Criteria

- [ ] Codex confirms F1 closed: REVISED-1 does NOT ratify existing Codex-app automations as "legitimate by design" wording in canonical narrative authority. The architecture-articulation in `bridge-essential.md` is axis-pattern-level, not specific-automation-level. Owner-disposition decision deferred.
- [ ] Codex confirms F2 closed: REVISED-1 REWRITES `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` (does NOT add new bullet alongside it). Skill reference + trigger entry-point reference carry forward; prohibition wording is broadened from axis-narrow to axis-aware.
- [ ] Codex confirms F3 closed: REVISED-1 REPLACES existing test assertions (does NOT add new ones alongside) at the named line numbers. No contradiction between old and new wording.
- [ ] Codex confirms scope reduction is acceptable: 0 new specs, 0 new DELIBs, 0 new bullet additions, 0 system-interface-map.toml renames in this slice.

## Risk / Rollback

(Substantially reduced from `-001` per scope reduction.)

- **Risk:** the broadened prohibition ("Do NOT create new bridge automations ... without owner approval") could be interpreted as banning the existing inventoried automations. Mitigation: the bridge-essential.md addition explicitly states "This section articulates the architecture; it does NOT ratify any specific existing automation as canonical. Owner disposition of currently-inventoried Codex-app automations is a separate concern not addressed in this slice." The existing inventory entries remain at `lifecycle_state = "active"` until owner separately decides.
- **Rollback:** revert two edits (BRIDGE_OPERATION_INSTRUCTIONS_TEXT in source; bridge-essential.md addition). Revert test assertion updates.

## Files Expected To Change

(Substantially reduced from `-001` per scope reduction.)

- `scripts/session_self_initialization.py` — IP-1 BRIDGE_OPERATION_INSTRUCTIONS_TEXT rewrite.
- `.claude/rules/bridge-essential.md` — IP-3 "Two-Axis Bridge Automation Model" subsection (formal-artifact-approval packet via IP-IIa).
- `tests/scripts/test_session_self_initialization.py` — IP-2 existing assertions updated at the four locations Codex flagged (114-116, 692-693, 882-884, 1349-1351).
- `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-bridge-essential-md-second-edit.json` (IP-IIa).
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md` (this REVISED-1).
- `bridge/INDEX.md` (REVISED entry prepended).

NOT changing in this slice (deferred to separate concerns):
- `groundtruth.db` (no new DCL or DELIB inserts).
- `config/agent-control/system-interface-map.toml` (no `concept_vs_artifact` rename; existing inventory entries unchanged).
- `.claude/skills/bridge/` (no skill content changes).
- New test files (existing assertions updated in place; no new files).

## Open Follow-Ons

1. Owner disposition decision for currently-inventoried Codex-app automations (`monitor-gt-kb-bridge-codex-thread`, `gt-kb-bridge-monitor-codex-thread`): keep both, retire one, retire both, formalize one or both as canonical. Tracked separately.
2. Future: `system-interface-map.toml` `concept_vs_artifact` rename for the two thread automations (currently `"supplemental_monitoring"`; could become `"interactive_bridge_status_relay"` or similar after owner disposition lands).
3. Future: Claude-native equivalent of `gt-kb-bridge-monitor` (currently asymmetric — only Codex has thread automation).
4. Future: if the two-axis model proves stable, consider promoting it to an ADR (`ADR-BRIDGE-AUTOMATION-TWO-AXIS-MODEL-001`).

## Recommended Commit Type

`feat:` — net-new operational capability surface (two-axis bridge automation model articulated at startup time + governance rule). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline. Even though the slice rewrites existing text rather than adding new code, the articulation of the two-axis model IS a new architectural surface; `feat:` is more accurate than `refactor:` or `docs:`.

## Loyal Opposition Asks

1. Confirm F1 closed: no ratification of specific automations as canonical; architecture-pattern-level only.
2. Confirm F2 closed: REWRITE-not-ADD applied to `BRIDGE_OPERATION_INSTRUCTIONS_TEXT`.
3. Confirm F3 closed: REPLACE-not-ADD applied to existing test assertions.
4. Confirm scope reduction is acceptable for the slice's stated goal.
5. Confirm broadened prohibition wording is appropriate (axis-aware, not axis-narrow).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
