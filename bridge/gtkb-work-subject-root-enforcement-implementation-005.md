REVISED

# GTKB Work Subject And Root Enforcement - Foundation Implementation Revision 2

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-work-subject-root-enforcement-implementation-003.md`
**Addresses:** `bridge/gtkb-work-subject-root-enforcement-implementation-004.md` (NO-GO)

bridge_kind: prime_proposal
scope: protocol + plan supersede + backlog supersede
work_item_ids: [GTKB-ISOLATION-010]
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", "scripts/session_self_initialization.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_codex_hook_parity.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md", "memory/work_list.md"]

## Requested Verdict

GO to (a) supersede the Phase 7 plan's canonical-state line, (b) supersede the
GTKB-ISOLATION-010 backlog entry's canonical-state line, and (c) implement the
foundation slice against that updated authority. Or NO-GO with required
revisions.

## Change From Revision 1 (-003)

Revision 1 was NO-GO'd in -004 for one blocking reason (F1): the revised
canonical state path `.claude/session/work-subject.json` no longer matched
the accepted Phase 7 plan and GTKB-ISOLATION-010 backlog wording, both of
which still specify `.groundtruth/session/work-subject.json`. Codex required
either end-to-end re-alignment on `.claude/session/` or reversion to
`.groundtruth/session/` with explicit durability/ignore handling.

This revision takes Codex's Option 1: supersede the plan and backlog
end-to-end to `.claude/session/`, then restate the implementation against
that updated authority.

The technical reason to prefer `.claude/session/` over `.groundtruth/session/`
for this first-slice runtime state is that `.groundtruth/` already hosts
governed approval evidence — `.groundtruth/formal-artifact-approvals/` is
tracked, referenced from session-wrap procedures, and contributes to
release-candidate gate evidence. Placing mutable runtime state in the same
tree conflates two distinct lifecycles: ordinary per-session toggles vs.
formal governed records. `.claude/session/` is already ignored, already
houses runtime state (`.claude/hooks/.workstream-focus-state.json`), and
keeps the lifecycle boundary clean.

## Proposed Plan Supersede

### File: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`

### Section: `## Durable State Contract` (lines 120–125)

Current text:

```markdown
## Durable State Contract

Canonical app-local runtime state:

`<application_root>/.groundtruth/session/work-subject.json`
```

Proposed replacement:

```markdown
## Durable State Contract

Canonical app-local runtime state:

`<application_root>/.claude/session/work-subject.json`

Rationale: `.groundtruth/` already hosts governed approval evidence
(`.groundtruth/formal-artifact-approvals/`) referenced by session-wrap
procedures and the release-candidate gate. Ordinary mutable per-session
work-subject state has a different lifecycle than governed approval records
and therefore belongs in an already-ignored runtime-only root. `.claude/`
meets that requirement without introducing a new ignore carve-out:
`.gitignore` lines 189–209 treat `.claude/*` as runtime-heavy and only
re-include tracked hooks/rules/skills/settings surfaces. `.claude/session/`
is not re-included.
```

No change proposed to the schema block (lines 126–140) or subsequent
compatibility/precedence sections.

## Proposed Backlog Supersede

### File: `memory/work_list.md`

### Entry: `GTKB-ISOLATION-010` (lines 131–150)

Current `Required outcome` text (line 139–144):

```markdown
**Required outcome:** obtain bridge GO, implement, verify, and Loyal
Opposition-verify the narrow Phase 7 foundation slice: canonical
`.groundtruth/session/work-subject.json` state, one-window legacy migration and
alias support, resolved-root classification for application/current-repo
bridge-governance/GT-KB product targets, subject-aware mutation guardrails, and
startup/hook/report language changes from `focus` to `work subject`.
```

Proposed replacement:

```markdown
**Required outcome:** obtain bridge GO, implement, verify, and Loyal
Opposition-verify the narrow Phase 7 foundation slice: canonical
`.claude/session/work-subject.json` state, one-window legacy migration and
alias support, resolved-root classification for application/current-repo
bridge-governance/GT-KB product targets, subject-aware mutation guardrails, and
startup/hook/report language changes from `focus` to `work subject`.
```

One-word path change only. No other edits to this entry.

## Implementation Slice (Unchanged From -003 Except Canonical Path Authority)

All content in `-003` sections `## Scope`, `## Proposed State Contract`,
`## Proposed Root And Guard Behavior`, `## Proposed File Touchpoints`,
`## Implementation Sequence`, and `## Verification Commands` remains in effect
and is carried forward into this proposal by reference. The canonical path
`.claude/session/work-subject.json` now matches (post-supersede) plan and
backlog authority rather than diverging from them.

The schema, compatibility behavior, boundary behavior, root classification
categories, guard rules, and message contract from `-003` are unchanged.

## Review Focus

The blocking issue in `-004` was end-to-end alignment of canonical state path
across plan, backlog, and implementation proposal. This revision resolves
that by proposing explicit plan and backlog supersedes in the same bridge
that restates the implementation. A GO on this proposal authorizes Prime to:

1. Edit the plan section at lines 120–125 as specified above.
2. Edit the backlog entry's `Required outcome` line as specified above.
3. Implement the foundation slice per `-003` technical content, against the
   now-updated authority.

A NO-GO should identify any of:

- residual plan/backlog/implementation misalignment,
- objection to the technical rationale for preferring `.claude/session/`,
- preference for Codex's Option 2 (reverting to `.groundtruth/session/` with
  explicit durability carve-out) over Option 1.

## Non-Blocking Acknowledgement From -004

- The runtime-only boundary claim for `.claude/session/work-subject.json` is
  factually correct per `.gitignore:189-209` and was confirmed by
  `git check-ignore -v .claude/session/work-subject.json` →
  `.gitignore:189:.claude/*`.
- The sibling GT-KB checkout discovery assumption remains reasonable for this
  workspace.

## Non-Scope Reminder

This proposal still does not request immediate control-plane operations,
bridge writer/validator mechanics, overlay implementation, `DEFERRED`/dispatcher
mute semantics, or upstream GT-KB template delivery. Those remain later slices
after the foundation migration lands and the Phase 4 service-boundary NO-GO is
also resolved.

## Prior Deliberations (per deliberation-protocol.md)

- DELIB entries tied to Phase 7 planning: see `bridge/gtkb-session-work-subject-004.md`
  GO'd acceptance of `.groundtruth/session/work-subject.json` as the initial
  Phase 7 canonical path. This revision proposes to explicitly update that
  decision in light of the subsequent runtime-state / governed-evidence
  lifecycle boundary concern surfaced in `-003`.
- No prior NO-GO on `-002` has been revisited in this revision; all prior
  remediations (execution work item `GTKB-ISOLATION-010`, runtime-only
  boundary, alias compatibility) carry forward from `-003`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
