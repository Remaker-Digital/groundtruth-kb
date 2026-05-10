# GTKB-ISOLATION-018 Slice 0 — Establish git boundary at applications/Agent_Red/

**Document:** `gtkb-isolation-018-slice-0-git-boundary`
**Status:** `NEW`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `feat:` (new boundary infrastructure + regression tests)

## Goal

Make the operating-model invariant "Agent Red content must never be pushed to the GT-KB repo" mechanically enforced by establishing a real git boundary at `applications/Agent_Red/`. Today the boundary is convention only: 269 files under that directory are tracked by GT-KB git, and the GT-KB checkout has the `agent-red` remote configured (so `git push agent-red <branch>` from inside GT-KB would publish GT-KB tree state to the agent-red repo).

This slice is the foundational boundary. It does NOT relocate any Agent Red feature code currently at GT-KB root (~475 files in `src/multi_tenant/`, `src/app/`, `tests/multi_tenant/`, etc.). That is Slice 1+ of GTKB-ISOLATION-018 and requires a separate divergence-comparison probe at design time.

## Specification Links

- `DELIB-1537` (S330 owner decision, 2026-05-04) — GT-KB project root boundary topology: Agent Red nested in applications/Agent_Red/. Three binding rules: GT-KB root containment; GT-KB-vs-application partition; Agent Red MUST live at applications/Agent_Red/.
- `DELIB-893` (GTKB-ISOLATION-002 Phase 2 root and repository topology plan, 2026-04-22).
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` — transient exception authorizing CI-evidence capture against `Remaker-Digital/agent-red-customer-engagement` while canonical migration to `mike-remakerdigital/agent-red` completes; v0.7.0-rc1 unauthorized until canonical migration completes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — establishes the applications/<name>/ placement convention for GT-KB-managed applications. This proposal directly operationalizes that ADR for Agent Red by establishing the git boundary at `applications/Agent_Red/` so the placement is mechanically enforceable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications. This proposal cites the specifications listed in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from the linked specifications and executed against the implementation. This proposal includes a spec-to-test mapping in section "Tests Derived From Linked Specifications" and the proposed verification commands run those tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented development as the GT-KB working model. The boundary slice produces durable artifacts: a gitignore rule, a nested checkout, and four regression tests; their existence is the verifiable evidence of the invariant.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle-state transitions for specifications. This slice does NOT promote any spec status; status changes for SPEC-1831/1832/1833 are downstream work in Lane B.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance discipline. Bridge proposal plus tests plus post-implementation report form the audit-trail artifacts for this slice.
- `.claude/rules/project-root-boundary.md` — three binding rules governing GT-KB and applications/Agent_Red/ paths.
- `.claude/rules/canonical-terminology.md` Agent Red entry — names `mike-remakerdigital/agent-red` as current canonical.
- `.claude/rules/operating-model.md` §1 and §2 — application/platform/hosted-application terminology; isolation as lifecycle independence.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Pre-Filing Preflight Subsection; Mandatory Specification Linkage Gate; Mandatory Owner Decisions / Input Section Gate; Mandatory Specification-Derived Verification Gate; Mandatory Applicability Preflight Gate.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review obligations; Owner Decisions / Input Section NO-GO Obligation; Prior Deliberations Section Requirement.
- `.claude/rules/bridge-essential.md` — bridge protocol invariants; Two-Axis bridge automation model.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline; this slice does NOT mutate canonical artifacts (no GOV/SPEC/ADR/DCL/PB/DA writes).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This proposal was filed via the bridge-propose helper which inserted a NEW entry at the top of bridge/INDEX.md per the protocol; no prior versions of this thread exist; nothing is rewritten or deleted.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed cross-session work authority; GTKB-ISOLATION-018 entry is in scope as the parent slice umbrella.

Carry-forward note: this is the first version of GTKB-ISOLATION-018. Predecessor isolation work landed under GTKB-ISOLATION-016 (Phase 8 Wave 3, VERIFIED) and GTKB-ISOLATION-017 (Slices 1-7 plus 8.5/8.6, all VERIFIED).

## Prior Deliberations

(Helper pre-populates this section from glossary-source seeds and semantic search. Author will review and prune.)


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-0955` — seed=search; bridge_thread; GO: GTKB-ISOLATION-016 Phase 8 rehearsal implementation
- DA: `DELIB-0988` — seed=search; bridge_thread; GTKB-ISOLATION-015 Slice 2 Reconciliation Review
- DA: `DELIB-1004` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Review
- DA: `DELIB-0958` — seed=search; bridge_thread; GTKB-ISOLATION-016 Phase 8 Rehearsal Implementation Review
- DA: `DELIB-1200` — seed=search; bridge_thread; Bridge thread: gtkb-isolation-004-service-boundary-plan-review (6 versions, ORPH

## Owner Decisions / Input

This proposal depends on owner approval per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate and `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel:

1. **Lane scope authorization (this session, 2026-05-10).** Owner answered "Full parallel (Recommended)" to AskUserQuestion: "Authorize me to open these lanes in parallel for maximum throughput?" — authorizing first-wave filings: A.1 (this proposal), C.1 (backlog annotation), C.2 (terminology corrective), Lane B owner-decision questions, and Lane D.1 investigation. This proposal is A.1 in that authorization.

2. **Owner directives in this session establishing the operational scope.** Direct chat statements from the owner:
   - "All Agent Red artifacts and data should be relocated to E:\GT-KB\applications\Agent_Red." (in-tree relocation directive)
   - "Agent Red is a separate project and the entire content of the Agent_Red directory should never be pushed to the GT-KB repo, because the Agent_Red directory is a different project: it is the Agent Red project, and it has its own repo." (boundary directive — direct motivation for this slice)
   - "GT-KB and Agent Red are separate projects that are interdependent. Agent Red lives within the Agent_Red directory because GT-KB and Agent Red interoperate in a shared, fixed directory structure that allows relative paths to remain consistent even though both Agent Red and GT-KB may evolve with asynchronous lifecycles." (interdependent-projects model — explains why nested-checkout topology is the right fit)

3. **Pending owner decisions deferred to later slices** (NOT blocking this slice):
   - SPEC-1831/1832/1833 substantive disposition choices — Lane B; not material to the boundary.
   - Slice 1+ relocation strategy — wholesale `git rm` from GT-KB root vs. content-divergence reconciliation. Requires probe at Slice 1 design time.
   - Disposition of CI-evidence reference target — `Remaker-Digital/agent-red-customer-engagement` vs `mike-remakerdigital/agent-red`. Currently scoped to `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` and outside this slice.

## Live State Probed

Probed 2026-05-10 in this session via Bash tool from `E:\GT-KB\`:

- `applications/Agent_Red/.git` — MISSING. No nested checkout currently exists.
- `git ls-files applications/Agent_Red | wc -l` returns **269** files tracked by GT-KB git.
  - Distribution by top-level subdirectory: 168 under `docs/`, 88 under `docs-site/`, 4 under `legal/`, 3 under `pdf-tooling/`, 1 under `incident-response/`, 2 under `.codex/` (`config.toml` + `hooks.json`), 1 each at root: `.claude/settings.json`, `.dockerignore`, `.gtkb-app-isolation.json`.
- `git remote -v` from GT-KB checkout shows TWO remotes:
  - `origin` → `https://github.com/Remaker-Digital/groundtruth-kb.git`
  - `agent-red` → `https://github.com/mike-remakerdigital/agent-red.git`
- `git remote show agent-red` — reachable; HEAD branch `main` at commit `6eff9f61aeb90b3cee05fc5015f9802bb70028ff`; multiple feature branches and active Dependabot updates.
- `git ls-tree --name-only agent-red/main` — agent-red repo is a complete Agent Red project containing 305 files in `src/`, 618 in `tests/`, 397 in `scripts/`, 361 in `admin/`, 155 in `docs/`, 81 in `docs-site/`, 4 in `legal/`, plus `.gtkb-app-isolation.json`, `.claude/settings.json`, `AGENTS.md`, `CLAUDE.md`, etc. at agent-red repo root.
- The 269 currently-tracked GT-KB files have canonical counterparts in agent-red repo. Cloning `mike-remakerdigital/agent-red` into `applications/Agent_Red/` provides their canonical content.

Existing `.gitignore` references to `applications/Agent_Red/` (to be consolidated):
- Lines 183-190: per-file pdf-tooling patterns (S331 sub-slice 18.B migration evidence).
- Line 426: `applications/Agent_Red/harness-state/*/session-lifecycle-guard.json`.
- Lines 437-438: `.codex/agent-red-hooks/operating-role.md` and `session-startup-preferences.json` (hardlink alias references).
- Line 457: comment referencing migration of harness-state.

## Implementation Plan

### Sequenced Steps

**Step 1 — `.gitignore` boundary**

Add a single wholesale line `applications/Agent_Red/` to `.gitignore` with a comment block explaining the boundary per DELIB-1537 and the owner directives. Consolidate or remove the existing per-file negation patterns at lines 183-190 (pdf-tooling), 426 (harness-state lifecycle-guard), 437-438 (agent-red-hooks aliases), and the explanatory comment at 457. The wholesale `applications/Agent_Red/` line supersedes them.

Verify: `git check-ignore applications/Agent_Red/probe.txt` returns positive.

**Step 2 — Untrack the 269 files from GT-KB index**

Run: `git rm -r --cached applications/Agent_Red/`

The working-tree files remain on disk (they are replaced by the agent-red clone in Step 4). Index removal is the goal.

Verify: `git ls-files applications/Agent_Red/ | wc -l` returns 0.

**Step 3 — Move existing applications/Agent_Red/ working-tree contents aside**

`git clone` requires an empty target directory. Move the existing working-tree contents to a backup location for verification at Step 6:

- `mv applications/Agent_Red applications/.Agent_Red.pre-clone-backup`
- `mkdir applications/Agent_Red`

The backup directory is in-tree (per project-root-boundary.md it must remain inside `E:\GT-KB`) and is gitignored as a side-effect of the wholesale `applications/Agent_Red/` ignore — no, wait: the backup path `applications/.Agent_Red.pre-clone-backup` is NOT gitignored because the dot-prefix and trailing suffix don't match the wholesale pattern. It is therefore visible to `git status` until cleanup. That is intentional for auditability during the slice; cleanup removes it after Step 6 verification.

Pre-conditions (assert in script): target backup directory does not pre-exist; source `applications/Agent_Red/` exists and is non-empty. Failure mid-step leaves clearly-named state for manual recovery.

**Step 4 — Clone agent-red into the directory**

Run: `git clone https://github.com/mike-remakerdigital/agent-red.git applications/Agent_Red/`

Verify:
- `applications/Agent_Red/.git` exists.
- `git -C applications/Agent_Red status` returns "On branch main, nothing to commit, working tree clean".
- `git -C applications/Agent_Red rev-parse HEAD` matches the commit fetched at Step 0 probing (or a newer canonical main HEAD; record the actual commit in the post-implementation report).

**Step 5 — Remove agent-red remote from GT-KB checkout**

Run: `git remote remove agent-red`

Verify: `git remote -v` from GT-KB checkout returns only `origin` → `Remaker-Digital/groundtruth-kb`.

**Step 6 — Verify backup matches clone**

Compare `applications/.Agent_Red.pre-clone-backup/` against `applications/Agent_Red/` for each of the 269 ex-tracked file paths. Use SHA-256 hash equivalence per path.

Discrepancy outcomes:
- (a) backup version newer/edited (GT-KB had local edits not yet pushed to agent-red): manually reconcile, document each in the post-implementation report. Possible follow-up: commit GT-KB-side edits to agent-red repo as a separate operation.
- (b) clone version is canonical and backup was stale: discard backup record; no further action.
- (c) divergence (both sides edited): flag for owner decision in the post-implementation report.

The slice does NOT auto-resolve divergence. All discrepancies are reported for triage. Acceptance criterion: zero un-triaged discrepancies.

**Step 7 — Commit GT-KB-side changes**

Two scoped commits to GT-KB repo (origin):

- Commit A: `feat(isolation): gitignore applications/Agent_Red/ wholesale per DELIB-1537`. Touches `.gitignore` only.
- Commit B: `chore(isolation): untrack 269 files at applications/Agent_Red/`. Touches the GT-KB index only (no working-tree changes; the files remain on disk in the nested checkout).

Commits do NOT include any agent-red repo content. The nested checkout's working tree is gitignored at GT-KB level.

**Step 8 — Add regression tests**

Create new file `tests/governance/test_agent_red_git_boundary.py` with these tests:

- `test_applications_agent_red_is_gitignored` — runs `git check-ignore applications/Agent_Red/probe.txt` (or equivalent subprocess call). Asserts the directory is gitignored.
- `test_applications_agent_red_has_nested_git_checkout` — asserts `Path("applications/Agent_Red/.git").exists()`.
- `test_applications_agent_red_no_files_tracked_by_gt_kb_git` — runs `git ls-files applications/Agent_Red/`. Asserts empty output.
- `test_gt_kb_checkout_has_no_agent_red_remote` — runs `git remote`. Asserts `agent-red` not in the remote list.

These tests exercise the live filesystem and live git state via subprocess, not source-code internals. They are outside-in per GOV-19.

**Step 9 — Run release-candidate gate**

Execute `python scripts/release_candidate_gate.py`. Confirm no regression. Capture full output for the post-implementation report.

**Step 10 — Cleanup**

After successful Step 6 verification (zero un-triaged discrepancies):

- Remove `applications/.Agent_Red.pre-clone-backup/`. Recoverable from local git reflog if needed (the directory was on disk; not committed; no GT-KB commit to revert).

If discrepancies were found and triaged, the cleanup step is deferred to the post-implementation report's follow-up actions.

### Out of Scope for Slice 0

- Relocating the ~475 Agent Red feature files at GT-KB root (`src/multi_tenant/`, `src/app/`, `src/agents/`, `src/chat/`, `src/integrations/`, `src/jobs/`, `src/migrations/`, `src/quality_metrics/`, `tests/agents/`, `tests/chat/`, `tests/integrations/`, `tests/e2e_*`, etc.) — Slice 1+ of this thread.
- Any modification to canonical-terminology.md or work_list.md — separate parallel-lane bridges C.1 and C.2 in this session's plan.
- v0.7.0-rc1 tag authorization — still gated on canonical migration completion per DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE.
- Updating or regenerating `applications/Agent_Red/.gtkb-app-isolation.json` in either repo — the agent-red-repo copy becomes the new canonical; if GT-KB tooling needs to read it, it reads from the nested checkout via direct filesystem access.
- Reviewing whether any GT-KB tooling depends on the `agent-red` remote being on the GT-KB checkout — Risk R2 mitigation is a pre-implementation grep covered in this slice, not a separate scope item.

## Tests Derived From Linked Specifications

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate, this proposal includes a spec-to-test mapping:

| Linked specification | Acceptance check | New test |
|----------------------|------------------|----------|
| DELIB-1537 Rule 1 (root containment) | No GT-KB-tracked content under `applications/Agent_Red/` | `test_applications_agent_red_no_files_tracked_by_gt_kb_git` |
| DELIB-1537 Rule 3 (Agent Red at applications/Agent_Red/) | Nested agent-red checkout present at the path | `test_applications_agent_red_has_nested_git_checkout` |
| DELIB-1537 boundary mechanism (gitignore as enforcement) | `applications/Agent_Red/` is gitignored in GT-KB | `test_applications_agent_red_is_gitignored` |
| Owner directive "never push Agent Red to GT-KB repo" | No `agent-red` remote on GT-KB checkout | `test_gt_kb_checkout_has_no_agent_red_remote` |

The tests directly verify the slice's mechanical invariants. Pass criteria: all four green.

## Verification Commands

The post-implementation report will include the actual output of these commands:

```text
$ git check-ignore applications/Agent_Red/test-probe.txt
applications/Agent_Red/test-probe.txt
$ git ls-files applications/Agent_Red | wc -l
0
$ test -d applications/Agent_Red/.git && echo PRESENT
PRESENT
$ git -C applications/Agent_Red status --short
(empty — clean working tree)
$ git remote -v | grep -E '^agent-red\b' || echo "(no agent-red remote)"
(no agent-red remote)
$ python -m pytest tests/governance/test_agent_red_git_boundary.py -q
....                                                                     [100%]
4 passed
$ python scripts/release_candidate_gate.py
(gate passes; full output captured)
```

## Risks and Rollback

### R1 — Backup-vs-clone divergence at Step 6

Some of the 269 ex-tracked files may have GT-KB-side edits not yet pushed to agent-red repo. Cloning would replace those edits with the agent-red repo version, losing GT-KB edits silently if backup verification is skipped.

**Mitigation:** Step 3 backup. Step 6 SHA-256 content-hash comparison per path. Discrepancies surfaced in the post-implementation report rather than silently ignored.

**Rollback:** `git restore --staged applications/Agent_Red/`, restore `.gitignore` to pre-slice state, remove `applications/Agent_Red/.git` and contents, restore from `applications/.Agent_Red.pre-clone-backup/`, re-add the agent-red remote. Recoverable from local git reflog and the backup directory until cleanup runs at Step 10.

### R2 — `agent-red` remote removal breaks unrelated tooling

Some script or Codex hook may depend on the `agent-red` remote being configured on the GT-KB checkout (e.g., a CI helper that fetches agent-red branches for cross-repo validation, or a doctor check that probes the remote).

**Mitigation:** Pre-implementation grep. Run `grep -rn "agent-red" .claude/ .codex/ scripts/ tools/ groundtruth-kb/ tests/` and inspect each match. Any genuine dependency requires a paired update to read from the nested checkout instead of from a GT-KB-side remote. Findings included in the post-implementation report.

**Rollback:** `git remote add agent-red https://github.com/mike-remakerdigital/agent-red.git` — single command; idempotent.

### R3 — `git clone` into a non-empty directory

Step 4 (`git clone`) requires the target directory to be empty. Step 3's move-aside handles this, but if Step 3 fails partway, the working tree may be in an inconsistent state.

**Mitigation:** Step 3 checks pre-conditions (target backup directory does not pre-exist; source directory exists and is non-empty). Failure mid-step leaves clearly-named state for manual recovery.

**Rollback:** `mv applications/.Agent_Red.pre-clone-backup applications/Agent_Red` recovers the pre-slice working tree.

### R4 — Nested-checkout discoverability for tooling

GT-KB tooling that reads `applications/Agent_Red/.gtkb-app-isolation.json` or other application-marker files now reads them from a nested checkout. Tooling that uses GT-KB's `git ls-files` against `applications/Agent_Red/` will see no files at all.

**Mitigation:** Tooling that needs to read application state should use direct filesystem reads (`open()`, `Path.read_text()`), not `git ls-files`. Pre-implementation grep confirms no tooling uses `git ls-files` against `applications/Agent_Red/`. Findings included in the post-implementation report.

**Rollback:** Same as R2 plus restore the gitignore plus restore tracked files from reflog.

### R5 — IDE / editor caches stale state

The Codex CLI, Claude Code CLI, VS Code, etc. running against the GT-KB checkout may cache file lists or git state that becomes stale during the slice. After the boundary lands, an editor may show ghost files at `applications/Agent_Red/` (the working-tree files that are now gitignored but on disk via the nested clone).

**Mitigation:** Document in the post-implementation report that operators should reload editor windows, restart language servers, and refresh Codex / Claude Code CLI sessions after the slice lands. Not a blocker for VERIFIED; an operator-experience note.

**Rollback:** Same as R2.

## Acceptance Criteria

The slice is complete and ready for VERIFIED when:

1. `git ls-files applications/Agent_Red/` returns 0 files in the GT-KB checkout.
2. `applications/Agent_Red/.git` exists and is a valid git directory pointing at `mike-remakerdigital/agent-red`.
3. `git remote -v` from GT-KB shows only `origin` → `Remaker-Digital/groundtruth-kb`.
4. `applications/Agent_Red/` is gitignored in GT-KB (`git check-ignore` succeeds for any path under it).
5. The four new tests in `tests/governance/test_agent_red_git_boundary.py` pass.
6. `python scripts/release_candidate_gate.py` passes.
7. Step 6 backup-vs-clone verification: zero un-triaged discrepancies.
8. Step 10 cleanup: `applications/.Agent_Red.pre-clone-backup/` removed.
9. Risk R2 grep findings: zero genuine dependencies on the GT-KB-side `agent-red` remote, OR all findings have paired updates landed in this slice.
10. Risk R4 grep findings: zero tooling using `git ls-files` against `applications/Agent_Red/`, OR all findings have paired updates landed in this slice.

## Pre-Filing Applicability Preflight

Run by Prime Builder pre-Codex-review on 2026-05-10:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-0-git-boundary
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-0-git-boundary
```

### Initial run (-001 first-pass; defects detected)

- Applicability: `preflight_passed: false`. Missing required: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Missing advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
- Clause preflight: 1 blocking gap at `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` (regex `bridge/INDEX\.md|INDEX update|insert.+top of.+(?:INDEX|entry)` did not match the proposal text).

### Self-detected revision (in-place, pre-Codex-review)

- Specification Links section expanded to cite all six missing specs with substantive descriptions of how each applies.
- `GOV-FILE-BRIDGE-AUTHORITY-001` line revised to literally reference `bridge/INDEX.md` and explain the helper-mediated file path.

### Final preflight (post-revision, this is the operative state)

- Applicability: `preflight_passed: true`. `missing_required_specs: []`. `missing_advisory_specs: []`.
- Clause preflight: `Evidence gaps in must_apply clauses: 0`. `Blocking gaps (gate-failing): 0`.
- Final operative `packet_hash`: `sha256:94e9232fa78049db68107aca55a8ec772e133b40826b5c05c86d309ad1dc6ac1`.
- Operative file (verified by preflight tool): `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
