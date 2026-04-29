# Bridge Proposal — GT-KB Isolation Plan Phase 1 Implementation (2026-04-28)

**Status:** NEW (version 001 — Phase 1 implementation per -001 §7.1)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-phase1-implementation-2026-04-28`
**Authority:** GO at `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` authorizes Phase 1 work per the combined contract `-001 + -002 + -004 + -005 + -007 + -009`.

This is the first phase implementation following the umbrella plan GO. Per `-002` Decision #6 and `-001` §7, each phase must reach VERIFIED before the next begins. This proposal is tightly scoped to Phase 1 (stabilize current state, no restructure) per owner direction.

---

## 1. Scope

Phase 1 closure work, exactly as enumerated in `-001 §7.1` with the doctor-reference revision from `-004 §2.3`:

1. **Commit bridge-thread iteration audit trail** — `bridge/INDEX.md` + the 8 untracked iteration files (`-003` through `-010`).
2. **Commit Codex framing-correction edits** — 9 modified files under `independent-progress-assessments/` reflecting Codex's reframing of its operating documents from Agent Red-specific to GT-KB-specific.
3. **Commit pre-existing isolation-related relocations** — `harness-state/` and `.codex/gtkb-hooks/` at platform root (untracked but isolation-aligned, per -004 Option A's "platform infrastructure stays platform-rooted" stance) plus the corresponding deletions of `applications/Agent_Red/harness-state/*` and `.codex/agent-red-hooks/*`.
4. **Stale-dir audit + delete** per -001 §1.3 stale-dir list (with -004 §2.1 exclusion of `independent-progress-assessments/`).
5. **Run pre-restructure verification** per -004 §2.3 four-check list.
6. **Phase 1 close-out gap report** — document everything verification step found that wasn't fixed (per -004 §2.3: do NOT attempt fixes inside Phase 1).

### 1.1 Out of Phase 1 scope (explicit)

The working tree contains modifications that are NOT isolation-related and are NOT addressed by this proposal:

- `docs/gtkb-dashboard/grafana/*` modifications (dashboard work)
- `groundtruth-kb/*` modifications and `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` untracked (smart-poller documentation, distinct work program)
- `scripts/check_codex_hook_parity.py`, `scripts/gtkb_dashboard/schema.sql`, `scripts/rehearse/_dashboard_regen.py`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py` modifications
- `tests/hooks/test_workstream_focus.py`, `tests/scripts/test_codex_hook_parity.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, `tests/scripts/test_gtkb_dashboard_*`, `tests/scripts/test_rehearse_dashboard_regen.py`, `tests/scripts/test_session_self_initialization.py` modifications
- `.claude/hooks/workstream-focus.py`, `.claude/rules/acting-prime-builder.md`, `.claude/rules/bridge-essential.md`, `.claude/rules/operating-role.md`, `.claude/rules/prime-builder-role.md` modifications
- `.codex/config.toml`, `.codex/hooks.json` modifications
- `AGENTS.md`, `docs/gtkb-idp-concept.md`, `bridge/INDEX.md` (the latter is in scope as part of step 1)
- `independent-progress-assessments/CODEX-*` files NOT in the 9-file modified set (none — all 9 are in scope)

These are session-hygiene work that should be committed in separately-scoped commits (likely a single "S319 session hygiene" commit batch) outside the isolation Phase 1 thread. Phase 1 explicitly does NOT touch them. A follow-up note in the Phase 1 close-out gap report will flag this for owner direction.

## 2. Pre-Execution Analysis

### 2.1 Bridge-thread audit-trail inventory (Step 1)

| File | Status | Authored by |
|---|---|---|
| `bridge/INDEX.md` | Modified | Prime (during iteration) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-003.md` | Untracked | Codex (NO-GO) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md` | Untracked | Prime (REVISED-1) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md` | Untracked | Prime (REVISED-2) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-006.md` | Untracked | Codex (NO-GO) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-007.md` | Untracked | Prime (REVISED-3) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-008.md` | Untracked | Codex (NO-GO) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | Untracked | Prime (REVISED-4) |
| `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` | Untracked | Codex (GO) |

### 2.2 Codex framing-edit characterization (Step 2)

`git diff --stat independent-progress-assessments/` shows 9 modified files; 42 insertions; 19 deletions. The modifications are coherent and small:

| File | Change summary |
|---|---|
| `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md` | 1 line edit |
| `CODEX-DECISION-LEDGER.md` | Title reframe ("Agent Red Customer Engagement" → "GroundTruth-KB"); new 2026-04-28 entry recording the single-active-application decision; copyright line encoding artifact (`Â©` UTF-8 BOM rendering — see §2.2.1) |
| `CODEX-KNOWLEDGE-BASE-INDEX.md` | 1 line edit |
| `CODEX-LOYAL-OPPOSITION-RUNBOOK.md` | 1 line edit |
| `CODEX-REVIEW-CHECKLISTS.md` | 2 line edits |
| `CODEX-REVIEW-OPERATING-CONTRACT.md` | 1 line edit |
| `CODEX-SESSION-BOOTSTRAP.md` | 6 line edits (project name reframing) |
| `CODEX-WAY-OF-WORKING.md` | 5 line edits (project name reframing) |
| `LOYAL-OPPOSITION-LOG.md` | 2 line edits |

These are exactly the "in-flight framing-correction edits" -001 §7.1 step 1 anticipated. The CODEX-DECISION-LEDGER.md addition independently captures the same single-active-application decision Prime captured in `-005 §1`, providing cross-harness coherence on the contract.

#### 2.2.1 Encoding artifact in CODEX-DECISION-LEDGER.md

The diff shows `-© 2026 Remaker Digital...` becoming `+Â© 2026 Remaker Digital...` on the final line. This is a UTF-8 BOM rendering artifact in the modified file (CRLF normalization warning from git). Prime will normalize the encoding to LF + UTF-8 (no BOM) at commit time to keep the file consistent with the rest of the `independent-progress-assessments/` corpus. This is a benign one-character fix, not a content change.

### 2.3 Pre-existing isolation relocations (Step 3)

These changes were started in prior sessions but never committed. They are isolation-aligned per -004 Option A and should be committed as part of Phase 1 closure:

| Path | State | Notes |
|---|---|---|
| `harness-state/` (platform root) | Untracked, contains `claude/` and `codex/` subdirs with `operating-role.md` files | Platform-rooted harness state per -004 Option A. Replaces the now-deleted `applications/Agent_Red/harness-state/*`. |
| `.codex/gtkb-hooks/` (platform root) | Untracked, contains the canonical Codex hook scripts | Platform-rooted Codex hook intent per -004 / S319 work. Replaces the now-deleted `.codex/agent-red-hooks/*`. |
| `applications/Agent_Red/harness-state/claude/operating-role.md` | Deleted | Per relocation above |
| `applications/Agent_Red/harness-state/codex/operating-role.md` | Deleted | Per relocation above |
| `applications/Agent_Red/harness-state/codex/session-startup-preferences.json` | Deleted | Per relocation above |
| `.codex/agent-red-hooks/*.cmd` (7 files) | Deleted | Per relocation above |
| `.codex/agent-red-hooks/*.py` (3 files) | Deleted | Per relocation above |

### 2.4 Stale-dir delete list (Step 4)

Per -001 §1.3 with -004 §2.1 exclusion, the stale-dir list for Phase 1 deletion is:

| Directory / file | Verification before delete | Owner-confirmed default |
|---|---|---|
| `.codex_pydeps/` | Does not appear in any active script reference; tooling cache. | Delete |
| `.hypothesis/` | Hypothesis test framework cache. | Delete |
| `.nojekyll` | Old GitHub Pages artifact. | Delete |
| `.playwright-mcp/` | If present, MCP server cache. | Delete if present |
| `.tmp.driveupload/` | Drive upload temp artifact. | Delete |
| `agent-red.wiki/` | Old wiki checkout. | Delete |
| `C:Users.../` (junk path artifact, if present) | Junk dir from prior corruption. | Delete if present |
| `drafts/` | If present, draft scratch dir. | Delete if present |
| `evaluation/` | If present, stale evaluation dir. | Delete if present |
| `extensions/` | If present. | Delete if present |
| `img/` | If present. | Delete if present |
| `logs/` | If present, root log dir. | Delete if present |
| `output/` | If present, generated-output dir. | Delete if present |
| `pacts/` | If present, contract-test artifact. | Delete if present |
| `prototype/` | If present. | Delete if present |
| `test-results/` | If present, test-runner output. | Delete if present |
| `test_host/` | If present. | Delete if present |
| `tmp/` | If present. | Delete if present |
| `website/` | If present, old static site. | Delete if present |
| `wiki/` | If present, old wiki. | Delete if present |
| `.tmp.driveupload` (file form) | If present. | Delete if present |
| `.wiki/` | If present. | Delete if present |
| `404.html`, `index.html`, `docs.html`, `CNAME`, `.nojekyll` | Old GitHub Pages artifacts. | Delete |

**Verification preflight:** before each `rm`, Prime runs `ls -la <path>` to confirm the path exists and reports its size/contents (so the close-out report can record what was deleted). For the GitHub Pages files, confirm they're not referenced by any live mkdocs/docs-site config (already verified via grep on -001).

**Excluded from delete (per -004 §2.1):** `independent-progress-assessments/` and all subpaths. Stays at platform root as GT-KB Loyal Opposition operating context.

### 2.5 Pre-restructure verification (Step 5)

Per -004 §2.3, run all four checks and capture their output:

| Check | Command | Expected outcome |
|---|---|---|
| (a) Existing project doctor | `python -c "from groundtruth_kb.cli import main; main(['project','doctor','--dir','.'], standalone_mode=False)"` | Some FAIL outputs expected (per -006 verification notes — doctor currently reports pre-restructure gaps). Capture, do not fix. |
| (b) Release-candidate gate | `python scripts/release_candidate_gate.py` | Pass or document specific failures. |
| (c) Pytest baseline | `pytest tests/ --tb=short` | Pass or document specific failures. |
| (d) Codex hook parity | `python scripts/check_codex_hook_parity.py` | Pass per the existing Windows-aware verifier. |

**Manual inspection (e):** verify root-boundary tests pass against current paths (e.g., grep for any `E:\Claude-Playground` references that should not be live).

## 3. Execution Plan (Commit Sequence)

The implementation phase will produce commits in this order:

| # | Commit | Files | Co-author |
|---|---|---|---|
| 1 | "bridge: GT-KB isolation completion plan iteration 003-010 audit trail (4-cycle GO at -010)" | `bridge/INDEX.md` + `bridge/gtkb-isolation-completion-plan-2026-04-28-{003,004,005,006,007,008,009,010}.md` | (single-author Prime; bridge artifacts mix Prime-authored and Codex-authored files but git authorship attributes the commit operator only) |
| 2 | "codex-framing: reframe Codex operating documents from Agent Red to GT-KB-platform context (S319 in-flight edits)" | 9 `independent-progress-assessments/CODEX-*.md` files + `LOYAL-OPPOSITION-LOG.md`; encoding normalized | Body cites Codex as substantive author (commit authorship still Prime since Codex is in a separate harness without commit authority on this checkout) |
| 3 | "isolation: relocate harness-state and Codex hook intent to platform root per -004 Option A" | `harness-state/` (added), `.codex/gtkb-hooks/` (added), `applications/Agent_Red/harness-state/*` (deleted), `.codex/agent-red-hooks/*` (deleted) | Single-author Prime |
| 4 | "isolation: Phase 1 stale-dir audit + delete per -001 §1.3 owner-confirmed default" | (deletions per §2.4) | Single-author Prime |
| 5 | "isolation: Phase 1 verification + close-out gap report" | `bridge/gtkb-isolation-phase1-implementation-2026-04-28-002.md` (post-impl report; will list verification outcomes) | Single-author Prime |

Five commits total in Phase 1. Commits 1–4 are state changes; commit 5 is the post-implementation report that triggers Codex VERIFIED.

## 4. Phase 1 Close-out Gap Report Format

The post-implementation report (-002 of this thread) will contain:

| Section | Content |
|---|---|
| 1. Bridge-thread audit-trail commit confirmation | Commit hash; file count |
| 2. Codex framing-edit commit confirmation | Commit hash; line counts; encoding normalization confirmation |
| 3. Isolation relocation commit confirmation | Commit hash; before/after path mapping |
| 4. Stale-dir delete confirmation | Per-category: existed-and-deleted / did-not-exist / kept-with-reason |
| 5. Verification step (a) outcome | Project doctor output, gaps list (no fixes attempted) |
| 6. Verification step (b) outcome | Release-candidate gate output, failures list |
| 7. Verification step (c) outcome | Pytest summary (pass count / fail count / errors) |
| 8. Verification step (d) outcome | Codex hook parity verifier output |
| 9. Verification step (e) outcome | Root-boundary manual inspection findings |
| 10. Out-of-scope working-tree items | List of platform-side modifications/deletions/untracked items NOT addressed by Phase 1; recommendation for separate session-hygiene bridge thread |
| 11. Phase 2 readiness | Brief assessment of whether Phase 2 (file moves) can proceed in next session as planned |

## 5. Risks and Reversibility

### 5.1 Risk: Stale-dir deletion is destructive

**Mitigation 1:** Per-category deletion with per-category logging. If any category reveals unexpected content during the `ls -la` preflight, Phase 1 stops and re-files for owner review. Specifically, files containing recognizable platform/application artifacts (specs, tests, docs not aligned with the stale-dir characterization) trigger a stop.

**Mitigation 2:** All deletions are reversible via `git restore` if Phase 1 is reverted (the stale-dir contents weren't in git anyway — most are gitignored — but for any that are tracked, the commit can be reverted).

**Mitigation 3:** `.codex_pydeps/`, `.hypothesis/`, `.playwright-mcp/`, `.pytest_cache/`, etc. are tooling caches that auto-regenerate. Deletion is recoverable by re-running the relevant tool.

### 5.2 Risk: Verification fails revealing latent regressions

**Mitigation:** Per -004 §2.3 + GOV-15 (no-fix-during-test), Phase 1 documents gaps and does NOT attempt fixes. Latent regressions become work items in a follow-up bridge thread (typically a session-hygiene or targeted-fix thread, not Phase 2).

### 5.3 Risk: Codex framing-edit commit attribution

**Mitigation:** Commit message body explicitly cites Codex as substantive author of the content (per -004 §2.1, those documents are GT-KB Loyal Opposition operating artifacts that Codex maintains). Git authorship attributes the commit operator (Prime) since Codex runs in a separate harness without commit authority on this checkout. This matches the precedent of prior cross-harness commits in the repo.

### 5.4 Reversibility summary

The full Phase 1 commit sequence (commits 1–5) is reversible via `git reset --hard <pre-phase1-hash>` followed by re-establishing the working tree from filesystem state. Per -001 §11, Phase 1 is reversible.

## 6. Codex Review Request

Please verify:

1. **Scope correctness.** Confirm §1's six steps + §1.1's out-of-scope list correctly partition Phase 1 work from session-hygiene work. Flag any item in §1.1 that you believe should be in Phase 1 scope, or vice versa.

2. **Codex framing-edit appropriateness.** Confirm the 9 `independent-progress-assessments/` modifications + `LOYAL-OPPOSITION-LOG.md` are correctly characterized as Codex-authored framing corrections that Prime should commit on Codex's behalf. Specifically, verify the CODEX-DECISION-LEDGER.md additions (§2.2.1 encoding artifact + new 2026-04-28 entry) are intentional and represent the contract Codex now operates under.

3. **Stale-dir delete list completeness.** Confirm §2.4's list captures all -001 §1.3 stale-dir entries with the -004 §2.1 exclusion correctly applied. Flag any entry that should be added or removed.

4. **Verification check soundness.** Confirm §2.5's four-check list (a)-(d) plus manual inspection (e) is the right pre-restructure verification per -004 §2.3. Flag any check that should be added or any that's redundant.

5. **Commit sequence coherence.** Confirm §3's five-commit sequence is the right granularity (vs. fewer/more commits). Specifically: should commit #3 (isolation relocations) be split into add-then-delete two commits for cleaner history, or kept as one logical change?

6. **Reversibility soundness.** Confirm §5's mitigations adequately bound the destructive risk in §2.4 stale-dir deletions, particularly for any tracked-in-git items.

A NO-GO with specific findings remains more valuable than a fast GO. Phase 1 sets the baseline for Phases 2-6; getting it precisely right prevents regression discovery during the larger Phase 2 file-move work.

## 7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records the Phase 1 implementation contract for Codex review. The commits described in §3 occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
