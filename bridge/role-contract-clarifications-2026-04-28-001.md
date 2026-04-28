# Bridge Proposal — Role-Contract Clarifications (2026-04-28)

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `role-contract-clarifications-2026-04-28`
**Owner pre-approval:** Yes — owner authored the original drafts in working tree between sessions; Prime Builder facilitated revisions in S319 review pass; final clauses confirmed by owner.

## 1. Summary

Two-clause governance amendment to the Prime Builder / Loyal Opposition role contract:

- **Clause A — LO simplicity-questioning empowerment.** Loyal Opposition is empowered to challenge Prime Builder design choices when a simpler / more efficient path satisfies the same requirements. Affects `.claude/rules/loyal-opposition.md` (+7 lines) and `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md` (+11 lines, revised from working-tree draft to align dimension lists).

- **Clause B — PB autonomy + active-questioning duty.** Prime Builder defaults to advancing the standing backlog when no GO/NO-GO bridge work is pending and no item-specific owner decision is pending; PB actively questions ambiguous owner direction across nine dimensions. Affects `.claude/rules/prime-builder-role.md` (+12 lines, revised from working-tree draft to add skip-on-owner-block guard and shortlist-if-ambiguous relief valve).

Net working-tree change vs. `develop` HEAD: 4 files touched, ~30 added lines, 1 file reverted from prior owner draft (`CODEX-SESSION-BOOTSTRAP.md` — the autonomy default lives only in the role rule, not duplicated in the bootstrap doc).

## 2. Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, all prior deliberations on related topics:

- **DELIB-S310-ROLE-DEFINITION-ASSESSMENT** (S310, owner_conversation, informational) — parent assessment identifying 9 underdefined gaps in the role contract. Three gaps directly addressed by this proposal:
  - *Gap 1 (review-depth methodology)* — Clauses 3A + 3B in `CODEX-REVIEW-OPERATING-CONTRACT.md` provide methodology guidance for simplicity-class findings.
  - *Gap 4 (LO investigation authority)* — Clause A in `loyal-opposition.md` formalizes LO's empowerment to challenge design choices, beyond just code/test correctness.
  - *Gap 6 (quality-bar asymmetry)* — Clauses A + B together create symmetric "challenge-upward" duty: LO challenges PB design; PB challenges owner ambiguity.
- **DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE** (S312, owner_conversation, informational) — extends DELIB-S310 with empirical evidence from GTKB-ISOLATION-016 Wave 2 Slice 4 (4 NO-GOs across proposal + post-impl review). Confirms LO already exercises simplicity-questioning informally; this proposal formalizes existing practice. **Out of scope here**: the recommended near-term review-depth heuristic clause (LO walks proposal §4 output-layout diagrams against `output_files` lists) — should be filed separately as `report-depth-prime-builder-context.md` amendment if desired.
- **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** (S312, owner_conversation, owner_decision) — owner directive: repetitive AI work is a defect; do not silently absorb friction. Supports Addition 2A (PB advances backlog rather than idling) and 2B (PB asks decision-oriented questions rather than re-deriving).
- **DELIB-0838** (S2026-04-20, owner_conversation, owner_decision) — owner decision: standing backlog is governed cross-session work authority. Direct support for Addition 2A: backlog-as-authority means PB acting on it without per-item approval is consistent with prior owner decision.
- **DELIB-0830 / 0831 / 0832** (2026-04-20-agent-red-acting-prime, owner_conversation, owner_decision) — role portability decisions. This proposal's clauses are harness-neutral (they speak to roles, not specific harnesses), consistent with these decisions.

No prior deliberation addresses the specific simplicity-questioning empowerment language or the active-questioning-with-9-dimensions language; this proposal is the first formalization of those clauses.

## 3. Rationale

### 3.1 Why now

The owner authored these drafts in the working tree between sessions. They sat as untracked drift through S318 (S318 wrap-up MEMORY.md noted them as "deferred for owner triage"). At the start of S319, the owner chose Option A (drift triage) and confirmed each clause through a 4-file review pass:

- File 1 (`loyal-opposition.md`): kept as-written
- File 2 2A (`prime-builder-role.md` autonomy): revised to Option ε (skip-on-owner-block + shortlist-if-ambiguous)
- File 2 2B (`prime-builder-role.md` active-questioning): kept as-written
- File 3 3A (`CODEX-REVIEW-OPERATING-CONTRACT.md` responsibility): revised to Option β (mirror File 1 verbatim)
- File 3 3B (`CODEX-REVIEW-OPERATING-CONTRACT.md` methodology): revised to Option δ (4-dimension list aligned to File 1)
- File 4 (`CODEX-SESSION-BOOTSTRAP.md`): revert (autonomy default lives in File 2 only)

### 3.2 What gaps from DELIB-S310 are closed

Of DELIB-S310's 9 underdefined gaps, this proposal addresses 3:

| Gap | Coverage |
|---|---|
| 1. review-depth methodology | Partial — covers simplicity-class findings only; doesn't add the recommended §4 output-layout walk (DELIB-S312 follow-on) |
| 4. LO investigation authority | Full — Clause A formalizes empowerment to challenge design choices |
| 6. quality-bar asymmetry | Symmetric "challenge-upward" duty added for both roles |

The remaining 6 gaps remain open under `GTKB-ROLE-ENHANCEMENT` (work_list row 11), deferred until post-isolation per owner directive.

### 3.3 Why two principles bundled

Clause A (LO direction) and Clause B (PB direction) form a coupled pattern — both formalize "challenge-upward" as a role responsibility:

- LO challenges PB design when simpler is sufficient.
- PB challenges owner direction when ambiguous.

Bundling preserves their conceptual unity in the audit trail and avoids two thread cycles for related governance changes. If reviewers prefer separation, the two clauses can be split into two threads.

### 3.4 Cross-file consistency contract

After revision, the dimension lists are aligned:

- File 1 (`loyal-opposition.md`) "Required Focus Areas" lists 4 simplicity dimensions: artifact count, operation count, operational steps, long-term stability.
- File 3 (`CODEX-REVIEW-OPERATING-CONTRACT.md`) methodology block (3B-δ) lists the same 4 dimensions verbatim.
- File 3 responsibility item (3A-β) mirrors File 1's empowerment clause word-for-word.

Single source of truth: when the dimensions evolve, both files update together rather than drifting.

### 3.5 Single-source-of-truth contract for autonomy default

After File 4 revert: the PB-mode standing-backlog autonomy default lives only in `.claude/rules/prime-builder-role.md` (auto-loaded by Codex at session start via the `.claude/rules/` convention). The bootstrap doc does not duplicate it. If the autonomy clause evolves, the bootstrap can't drift.

## 4. Verbatim Diffs (proposed final state vs. `develop` HEAD)

### 4.1 File 1 — `.claude/rules/loyal-opposition.md` (+7)

Kept as-written from owner working-tree draft. Two additions in existing sections (no new sections).

```diff
@@ -9,6 +9,11 @@ assignment remains in force.
 - Loyal Opposition mission: inspect, critique, and analyze implementation, plans, and documentation.
 - Loyal Opposition output: evidence-based reports that improve quality, correctness, and readiness.
 - Prime Builder role: receives Loyal Opposition findings via the file bridge in `bridge/` and implements approved remediations.
+- Loyal Opposition may question Prime Builder technology choices, approaches,
+  and designs when a simpler or more efficient path appears to satisfy the same
+  requirements with fewer artifacts, fewer operations, or better foreseeable
+  stability. These challenges must be evidence-based and framed as review
+  findings, not preference objections.

 ## Mandatory Project Root Boundary

@@ -37,6 +42,8 @@ agent to the Prime Builder role.
 - hook behavior and safety controls
 - MCP/tooling configuration and external integration risk
 - architecture, testing, operational readiness, and documentation drift
+- simplicity and efficiency of proposed technologies, approaches, shared
+  subsystems, artifact count, operational steps, and long-term stability

 ## Required Reporting Standard
```

### 4.2 File 2 — `.claude/rules/prime-builder-role.md` (+12, with 2A revised)

Two additions in `Operational implications:` list. 2A is the revised Option ε version (longer than working-tree draft); 2B is unchanged from working-tree draft.

```diff
@@ -29,6 +29,18 @@ Operational implications:
   file-by-file owner approval.
 - This file authority does not waive formal artifact approval, credential
   safety, release/deployment approval gates, or scoped-change discipline.
+- When Prime Builder has no actionable bridge `GO` or `NO-GO` work and no
+  item-specific owner decision is pending, it should advance the
+  highest-priority implementable standing-backlog item, skipping any item
+  flagged "blocked on owner." When the priority ranking is non-obvious,
+  surface a brief ranked shortlist for owner confirmation before
+  committing to the choice. Normal bridge review, artifact governance,
+  credential-safety, and release gates still apply.
+- Prime Builder should actively question owner direction, specifications, and
+  intent when ambiguity could materially affect scope, architecture,
+  user-visible behavior, governance, cost, security, data, release readiness,
+  or maintainability. Ask direct, decision-oriented questions; when the work can
+  safely proceed, state the assumption and continue.
 - Loyal Opposition materials remain available for reference or explicit
   counterpart-review sessions, but they are not the default operating mode while
   this assignment remains active.
```

### 4.3 File 3 — `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md` (+11, with 3A and 3B both revised)

Two additions: 3A as responsibility item #5 (revised to mirror File 1 verbatim); 3B as methodology block (revised to 4-dimension list aligned to File 1).

```diff
@@ -12,6 +12,10 @@ responsible for:
 2. reviewing code, tests, and configuration changes
 3. investigating alternatives, tradeoffs, and technical decisions
 4. producing evidence-based reports and decision memos for the owner and Prime Builder
+5. questioning Prime Builder technology choices, approaches, and designs
+   when a simpler or more efficient path appears to satisfy the same
+   requirements with fewer artifacts, fewer operations, or better
+   foreseeable stability

 ## Default Execution Mode

@@ -66,6 +70,13 @@ does the proposal reduce the owner's role to specifications, clarifications,
 and decisions? If not, identify the remaining owner burden and whether it should
 be automated, specified, or accepted as an explicit trade-off.

+Loyal Opposition may raise design-simplicity findings against Prime Builder's
+choice of technology, approach, or shared-subsystem design. Findings should
+compare the proposed path against simpler alternatives using concrete evidence:
+artifact count, operation count, operational steps, and long-term stability.
+Do not present these objections as style preferences; tie them to requirement
+satisfaction and operational risk.
+
 For P0/P1 items, also include:

 1. affected files or systems
```

### 4.4 File 4 — `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md` (revert)

This proposal does NOT add the bullet from the original working-tree draft. The working-tree state currently has +3 lines that this proposal will revert to discard.

Working-tree current diff (vs. `develop` HEAD) — to be reverted:
```diff
@@ -33,6 +33,9 @@ this workspace and reads `AGENTS.md`:
   entry is included in the continuation scope for the prior session; those
   entries may be Loyal Opposition responses created in a separate previous
   session.
+- In Prime Builder mode, after bridge obligations are clear, continue with the
+  highest-priority implementable standing-backlog item instead of waiting for
+  owner direction, unless an owner decision is required.
 - The poller is separate from the bridge. Activate a poller only when Prime
   Builder and Loyal Opposition are running in separate harnesses or
   asynchronous monitoring is otherwise needed.
```

After implementation: net change to `CODEX-SESSION-BOOTSTRAP.md` vs. `develop` HEAD = 0 lines.

## 5. Codex Review Questions

1. **Coherence with `acting-prime-builder.md` Standing Backlog Principle.** That rule (DELIB-0838) says future sessions must inspect the standing backlog before selecting discretionary work. Addition 2A goes further — PB advances the backlog rather than idling. Are these consistent, or does 2A introduce a tension?

2. **Coherence with `report-depth-prime-builder-context.md`.** That rule lists 4 required review-depth elements (Observation / Deficiency Rationale / Proposed Solution / Option Rationale). Clauses A + 3A/3B add a fifth review type — simplicity-class findings. Should the 4-element required structure include a 5th element specific to simplicity findings, or is "Observation + Deficiency Rationale" sufficient?

3. **Cross-file dimension-list consistency.** Verify File 1 lists 4 simplicity dimensions and File 3 (3B) lists the same 4 dimensions verbatim ("artifact count, operation count, operational steps, long-term stability"). Confirm no drift.

4. **Single-source-of-truth check for autonomy default.** Verify File 4 revert is correct — autonomy default lives only in File 2's role rule. Confirm no risk that bootstrap doc readers (e.g., LO-mode Codex sessions) will be unaware of PB's autonomy default.

5. **Asymmetry analysis.** Clause A gives LO "challenge-upward" authority over PB. Clause B gives PB "challenge-upward" authority over the owner. Is this symmetric pattern desirable, or is there an unintended consequence (e.g., owner-direction-questioning becoming a friction class for low-stakes work)?

6. **Materiality threshold for 2B.** The PB active-questioning clause (2B) lists 9 dimensions and uses "could materially affect" as the trigger. Without an explicit threshold, will this produce question-fatigue in low-stakes work? The "state the assumption and continue" relief valve is the mitigation — confirm it's adequate.

7. **Phantom-INDEX risk.** Any concerns this thread will create new phantom-INDEX patterns when files are committed? (S317-S318 cleanup eliminated 7 phantom-INDEX entries; want to confirm this thread's commit pattern preserves on-disk version files.)

## 6. Implementation Plan

After GO:

1. Apply the four working-tree changes:
   - File 1: keep current draft (no change needed)
   - File 2: replace 2A current text (5 lines, working-tree state) with Option ε version (7 lines)
   - File 3: replace 3A with Option β (4 lines vs. 3 currently); replace 3B with Option δ (7 lines vs. 6 currently, with same total stanza shape)
   - File 4: `git checkout -- independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md` to discard working-tree edit
2. Verify diff matches §4 exactly via `git diff` review before committing.
3. Commit with scoped message:
   ```
   governance: Two-clause role-contract amendment (LO simplicity-questioning + PB autonomy/active-questioning)

   Per bridge/role-contract-clarifications-2026-04-28-NNN.md GO.

   Closes 3 of 9 gaps from DELIB-S310-ROLE-DEFINITION-ASSESSMENT (review-depth
   methodology partial; LO investigation authority full; quality-bar asymmetry
   symmetric).
   ```
4. File post-implementation report at `bridge/role-contract-clarifications-2026-04-28-NNN.md`.

After VERIFIED:

5. Mark this drift triage subset as resolved in next session-wrap MEMORY.md update.
6. Codex's `.claude/rules/` auto-loader will pick up the new clauses on next Codex session start.
7. Cross-link the deliberation that gets harvested for this thread to DELIB-S310 (parent assessment) and DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE (effectiveness extension).

## 7. Out-of-Scope

This proposal does NOT cover:

- DELIB-S312's recommended §4 output-layout-walk review-depth heuristic (would be a separate amendment to `report-depth-prime-builder-context.md`).
- The remaining 6 gaps from DELIB-S310 (deferred to `GTKB-ROLE-ENHANCEMENT`, post-isolation).
- Any escalation path when PB and LO disagree on materiality of a simplicity finding (currently handled implicitly by REVISED cycles; could be explicit in a follow-on).
- Changes to LO's reporting structure (`report-depth-prime-builder-context.md` 4-element format unchanged).

## 8. Reversibility

Fully reversible. The four edits can be reverted with a single `git revert` of the implementation commit. No KB mutations, no external state changes, no data migrations. Cost of reversion: ~1 commit.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
