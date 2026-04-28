---
name: Session-start ORIENT block (self-imposed gate, pre-formalization)
description: At S301+ session start, after memory read and bridge scan, produce a 7-item ORIENT block in fixed format from LIVE SOURCES. Self-imposed behavior pending formal bridge adoption.
type: feedback
originSessionId: S300
---
**Rule:** At session start, after the mandatory memory read and `bridge/INDEX.md` scan,
produce an ORIENT block as the first substantive output to the owner. Seven items,
fixed format, each answer sourced from a live command (not from memory).

**Why:** Owner settled 2026-04-17 evening (S300) on a two-tier orientation design
after rejecting a 25-50 item questionnaire proposal. Rationale: mandatory short
gate + on-demand extended audit maps correctly to how cost/value distributes across
sessions. Static questionnaires create stale-answer factories; live-state queries
force actual investigation. Aviation checklist literature: checklists work when
minimal and critical, fail when comprehensive and aspirational.

**How to apply:**

Output format (verbatim, mirrors POLLER block discipline):

```
ORIENT S{N} @ HH:MMZ
  1 bridge:     <status>              # from bridge/INDEX.md head scan
  2 branch:     <repo>@<sha-short>  (<ahead/behind N>)   # git rev-parse + git status -sb
  3 worktree:   <N modified, M untracked>  [relevant: <scoped subset>]   # git status --short
  4 wrap:       DELIB-<id> / INSIGHTS-<date>-<topic>.md  # DA search + CODEX-INSIGHT-DROPBOX latest
  5 blockers:   <list or 'none'>       # bridge/INDEX.md active NO-GO + GO-unverified + release-blocking
  6 refresh:    <list or 'none'>       # evidence that must be refreshed before acting
  7 next:       <action>               # synthesis of 1-6
```

Each answer must come from a live source, not from memory. Acceptable sources:
`git` commands, `bridge/INDEX.md` read, `search_deliberations()` call, `gh run list`,
file reads. If a live source can't be obtained for any of the 7 items, mark it
`UNKNOWN — <reason>` rather than inferring from memory.

**Extended audit trigger:** If the owner uses phrases like "baseline status,"
"release readiness," "production readiness," "project handoff," "baseline audit,"
"where do we stand," or "full status," run the extended 25-29 question audit
(integrated list from S300 DELIB with Codex's additions, evidence-tagged per
`{command_output, bridge_status, DA_row, CI_result, release_tag, doc_inference}`).

**Scope:** Self-imposed voluntary behavior. NOT yet formalized in
CLAUDE.md/AGENTS.md. A bridge proposal
(`gtkb-session-start-orientation-gate-001`) will formalize and mechanically
enforce this after `gtkb-da-governance-completeness-implementation` VERIFIED
(sequencing avoids scope-forking the in-flight wrap-side governance hooks).

**Integration with POLLER block:** ORIENT block is produced ONCE at session
start. POLLER block continues per-turn as today. They coexist; ORIENT doesn't
replace the POLLER cadence.

**Retire this memory when:** the formal bridge lands and ORIENT becomes
mechanically enforced by a GT-KB hook. At that point the feedback file is
superseded by the hook/template and can be deleted.
