# Peer Solution Advisory Loop Procedure

This rule is the durable procedure for handling Loyal Opposition (LO) peer-solution advisories — investigations of external systems, frameworks, libraries, or processes that may inform GT-KB's design. It formalizes the classification vocabulary, the owner-dialogue workflow, and the Prime-side response template that the parent Slice-0 thread `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`) authorized.

This rule is auto-loaded via `.claude/rules/` convention.

## Purpose

The Peer Solution Advisory Loop is a durable input pattern that converts LO investigations of external peer systems (e.g., Archon, BMAD, Symphony, GSD, Google Opal) into governed, owner-visible decision artifacts rather than chat-only context that fades between sessions.

Without this loop, LO peer-system findings live in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` reports that may or may not be revisited. With this loop, every peer-solution advisory either lands as a concrete bridge proposal (adoption / adaptation), is documented as rejected with rationale, is explicitly deferred with a trigger condition, or is recorded as a monitored peer whose evolution is watched. The loop is bidirectional: LO surfaces a peer solution; Prime responds with one of the classification states below; the owner approves or modifies Prime's response when material; the decision is preserved in the Deliberation Archive and (when applicable) in MemBase.

The procedure is required when an LO advisory's `Recommended action` cites a specific external system or framework as a candidate solution to a GT-KB problem.

## Classification Vocabulary

Prime responses to LO peer-solution advisories use one of these five classification states. Each is unambiguous and preserves the decision in a way that future sessions can recall:

### `adopt`

Prime accepts the peer solution AS-IS and files an implementation proposal to bring the peer pattern into GT-KB. Use when the peer solution addresses the GT-KB problem cleanly and no adaptation is needed beyond standard integration work.

Required follow-on: a NEW bridge proposal whose Specification Links cite the LO advisory + the relevant peer-system documentation + any new specs the adoption creates. Standard GO-NO-GO discipline applies.

### `adapt`

Prime accepts the peer solution's CORE PATTERN but rejects part of its surface in favor of a GT-KB-native equivalent. Use when the peer pattern is correct in shape but its implementation depends on assumptions GT-KB cannot accept (different governance model, different runtime, different tradeoffs).

Required follow-on: a NEW bridge proposal documenting WHICH parts adopt and WHICH parts adapt, with rationale for each adaptation. The proposal must cite the peer-system source AND the GT-KB-native alternative chosen.

### `reject`

Prime rejects the peer solution because it does not address the GT-KB problem, conflicts with established GT-KB governance, or its tradeoffs are unacceptable. Use when adoption or adaptation would weaken GT-KB rather than strengthen it.

Required follow-on: a Deliberation Archive record (per `.claude/rules/deliberation-protocol.md`) capturing the rejection rationale. The rejected peer solution stays referenced in the DA so future sessions surfacing the same idea see the prior rejection.

### `defer`

Prime defers a decision on the peer solution to a later session. Use when the peer solution may become relevant after a specific GT-KB milestone (e.g., "after release readiness lands", "after multi-tenant story stabilizes"), when more evidence is needed, or when the GT-KB problem the peer would solve is itself not yet specified.

Required follow-on: a Deliberation Archive record with an explicit DEFER-TRIGGER CONDITION (e.g., "Revisit after `GTKB-DASHBOARD-002` Slice 3 lands", or "Revisit if `GOV-RELEASE-READINESS-001` blockers reach P0"). When the trigger condition is met, the procedure resumes from the original advisory.

### `monitor`

Prime records the peer solution as worth watching but takes no current action. Use when the peer solution is evolving (e.g., a new framework's API is unstable) and the right disposition depends on its future state.

Required follow-on: a Deliberation Archive record citing the peer-system URL or repo for future cross-reference. Monitoring is passive; the loop does not require periodic re-evaluation unless the owner explicitly invokes the advisory again.

## Owner-Dialogue Workflow

The loop runs as follows:

1. **LO files peer-solution advisory.** LO investigates a peer system on owner request (or proactively when LO encounters one in the course of normal review work). LO files the advisory either as a Deliberation Archive entry plus an `INSIGHTS-*.md` report under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`, OR as an LO advisory bridge entry (the latter once `gtkb-bridge-advisory-status-001` reaches VERIFIED; until then the `NO-GO@001` transport convention applies per the parent Slice-0 thread).
2. **Prime reads the advisory** as part of the standard Loyal-Opposition-insight review path defined in `.claude/rules/codex-way-of-working.md`.
3. **Prime classifies the advisory** using the five-state vocabulary above. The classification IS a Prime decision recorded in the response.
4. **Prime drafts the response artifact** appropriate to the classification:
   - `adopt` / `adapt` -> NEW bridge proposal.
   - `reject` / `defer` / `monitor` -> Deliberation Archive entry.
5. **Owner reviews when material.** Routine `monitor` decisions and obvious `reject` rationales may proceed without owner AskUserQuestion. Substantive `adopt` / `adapt` proposals always run through standard Prime/LO bridge review including any AUQ-required owner approvals (per the AUQ-only enforcement stack). `defer` decisions with non-obvious trigger conditions surface to the owner via AUQ.
6. **Decision is preserved.** Bridge proposals carry their own audit trail. Deliberation Archive entries are searchable via `gt deliberations search` so future sessions surfacing the same peer find the prior decision before duplicating analysis.

The loop's defining feature is that **no peer-solution advisory dies in chat scrollback.** Every advisory ends in one of five recorded states, with the rationale captured in a structure that future sessions can recall.

## Owner-Grilling Gate (Authority: GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001)

Any LO advisory whose recommended Prime Builder disposition is `adopt` or
`adapt` MUST include a `## Required Prime Builder Owner-Grilling Gate`
section in the advisory body. The gate section enumerates:

1. Whether this advisory implies future implementation work (yes/no with
   brief rationale).
2. What Prime Builder must grill the owner about before drafting any
   implementation proposal derived from this advisory.
3. What owner decisions must be durable, recorded via `AskUserQuestion`
   per `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the
   Only Valid Owner-Decision Channel", before an implementation
   proposal can exist.

Prime Builder must conduct a structured owner clarification/grilling
pass — using the `/grill-me-for-clarification` skill or an equivalent
AUQ-recorded structured interview — and the resulting AUQ evidence
MUST land in the resulting bridge proposal's mandatory `## Owner
Decisions / Input` section (per `.claude/rules/file-bridge-protocol.md`
§ "Mandatory Owner Decisions / Input Section Gate") before the proposal
is filed as `NEW`.

Scope: The gate fires for `adopt`/`adapt` classifications only.
`reject`/`monitor` advisories are terminal; `defer` advisories receive
the gate at defer-trigger reactivation, not at original filing.

Mechanical contract: `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` specifies
advisory-shape detection, gate-presence assertion, gate-content
assertion, two-phase enforcement (warning then blocking via separate
owner approval), and the owner-waiver path. The deterministic lint that
enforces the contract lands in Slice 3 of
PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001; Slices 1 and 2 are
advisory-only until Slice 3 ships the lint.

LO authors start from the following skeleton when authoring an advisory
classified `adopt` or `adapt`. It is a fenced documentation example
(rendered as code, not a live section of this rule); copy the inner
content into the advisory body:

```
## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes — this advisory recommends adopt/adapt of <pattern>, which requires
<files/specs> to be modified. OR: No — recommendation is procedural only,
no source mutation expected.

### Grill-the-owner questions
Prime Builder must obtain durable AUQ-recorded answers to:
1. <question 1 about scope>
2. <question 2 about rule home / authority>
3. <question 3 about risks or alternatives>

### Required durable owner decisions
The following AUQ answers must exist before an implementation proposal
can be filed:
- <decision 1>
- <decision 2>
```

## Bridge Integration

Peer-solution advisories enter the bridge as standard `ADVISORY` status entries with `bridge_kind: loyal_opposition_advisory`. The advisory has its own bridge thread with a conventional version chain (e.g., `Version: 001`). ADVISORY entries surface in the Prime Builder actionable list (so an interactive Prime session sees them on the next `/bridge` scan) and are strictly non-dispatchable for headless runs.

Prime responses (the classification + the follow-on artifact) are bridge-tracked:

- `adopt` / `adapt` Prime responses are normal NEW bridge proposals — Prime authors them, Codex reviews them.
- `reject` / `defer` / `monitor` Prime responses are Deliberation Archive entries. They do NOT receive bridge GO/NO-GO verdicts; the DA preservation IS the durable record.

## Approval-Gate

When a Prime `adopt` or `adapt` response calls for editing protected paths (e.g., `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`), the standard `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` packet workflow applies. The peer-solution advisory and Prime's adoption decision do NOT substitute for the per-protected-path approval packet; the packet remains required.

This separation preserves the layered approval model: owner approves the strategic decision (adopt vs adapt) at the bridge-review level; owner approves the specific protected-file content at the per-artifact packet level. A peer solution's adoption can be approved without committing the owner to every detail of its protected-file implementation.

For MemBase artifact creation (ADR / DCL / SPEC / GOV inserts) recommended by an adopted peer solution, the per-artifact formal-artifact-approval packet is similarly required per `GOV-ARTIFACT-APPROVAL-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
