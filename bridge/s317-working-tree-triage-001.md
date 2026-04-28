NEW

# S317 Working-Tree Triage and Scoped Commit Plan

**Status:** NEW (housekeeping; awaits Codex GO)
**Date:** 2026-04-27 (S317 session start)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** Session start of S317 reveals 22 modified + 65 untracked entries on `develop` that accumulated across S315 (root-isolation remediation) and S316 (deletion-readiness manifests + harness-state migration). The S315 MEMORY.md entry asserts "104/104 auto-memory files migrated to E:\GT-KB\memory\ with SHA256 verify"; `git status` confirms the filesystem migration succeeded but the resulting files were **never `git add`'d** — they sit untracked, exposed to a `git clean -fd` that would silently destroy them. MEMORY.md's "Feedback Index" already links 30+ of these files; the broken-link risk is real.

**Owner directive context:** [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md) — all GT-KB files MUST be within `E:\GT-KB`. The S315/S316 work brought files into-root; this proposal records that state in git.

---

## Prior Deliberations

- `bridge/critical-remediation-root-isolation-012.md` (S316 VERIFIED) — Phase C migrated 104 auto-memory files into-root; this proposal closes the unfinished governance step (committing the migrated files).
- `bridge/application-isolation-contract-008.md` (S316 VERIFIED) — established the 4-bucket model for `applications/Agent_Red/`; this proposal adds harness-state scaffold per Bucket B.
- `bridge/e-drive-claude-playground-cleanup-manifest-010.md` (S316 VERIFIED) — same close-out window; corroborates that S316 ended with state captured but partially uncommitted.
- MEMORY.md S315 entry (lines 79–80 of `memory/MEMORY.md`) — lists the migrated counts (`feedback/ (57), topics/ (45), MEMORY.md+backup at root`); current filesystem shows 60 feedback files + 43 topic files (close to those counts).
- [memory/feedback/feedback_explicit_destructive_action_authorization.md](memory/feedback/feedback_explicit_destructive_action_authorization.md) — caution lesson; this proposal performs no destructive actions.

---

## §0. Scope

This is a **non-destructive, additive-only** working-tree triage. The plan:

1. Inventories every modified and untracked entry, categorizes by intent and origin.
2. Specifies which entries get committed and in what scoped commit boundary.
3. Specifies which entries are explicitly excluded (and why).
4. Adds one new `.gitignore` line for a 3.6 GB Drive-sync staging directory that must not be committed.
5. Defines verification: post-commit `git status` should show only auto-regen telemetry as modified (the irreducible baseline) plus excluded items.

**Out of scope:**
- No source code changes beyond the proposed `.gitignore` addition.
- No deletions of any kind. (Per `feedback_explicit_destructive_action_authorization.md`, irreversible operations require explicit per-target enumeration; backup-file removal is deferred to a separate proposal if owner desires.)
- No KB mutations. No status promotions. No deployment actions.
- No work on the row 16/17/18 GENERATOR-HARDENING chain (separate session).

---

## §1. Modified files inventory (22 entries; 5 logical groups)

### §1.1 Group A — Project-root-boundary governance edits (5 files)

These edits replace legacy `E:\Claude-Playground` references and home-directory mirror references with `E:\GT-KB` paths, and add the "Mandatory Project Root Boundary" section that cites the new `.claude/rules/project-root-boundary.md`. **Verified intentional via diff inspection.**

| File | Diff stat | Intent confirmed |
|---|---|---|
| [CLAUDE.md](CLAUDE.md) | +18/-2 | Adds root-boundary section; updates Session memory pointer; updates new-session preamble path |
| [AGENTS.md](AGENTS.md) | +17/-2 | Adds root-boundary section; updates harness-state default paths to in-root |
| [.claude/rules/acting-prime-builder.md](.claude/rules/acting-prime-builder.md) | +8/-0 | Adds root-boundary cross-reference |
| [.claude/rules/file-bridge-protocol.md](.claude/rules/file-bridge-protocol.md) | +9/-0 | Adds "Mandatory Root Boundary Gate" section |
| [.claude/rules/loyal-opposition.md](.claude/rules/loyal-opposition.md) | +8/-0 | Adds root-boundary mandate section |

**Disposition:** **Commit 1** — "rules: Track project-root-boundary directive and cross-references (S315/S316 carryover)"

### §1.2 Group B — Codex hook config refactor (2 files, small)

| File | Diff stat | Intent confirmed |
|---|---|---|
| [.codex/config.toml](.codex/config.toml) | +2/-2 | Hook path updates |
| [.codex/hooks.json](.codex/hooks.json) | +5/-5 | Hook path updates (likely paralleling Group A) |

**Disposition:** **Commit 1** (bundle with Group A — same root-boundary intent, same mechanical scope).

### §1.3 Group C — Script refactors away from `Path.home()` (5 files, small)

Per [bridge/critical-remediation-root-isolation-001.md](bridge/critical-remediation-root-isolation-001.md) §1.4, 8 sites across 7 files were identified as needing parameterization. Three sites in three files appear modified; this is partial completion of GENERATOR-HARDENING-002.

| File | Diff stat | Intent confirmed |
|---|---|---|
| [scripts/check_codex_hook_parity.py](scripts/check_codex_hook_parity.py) | +1/-1 | One-line refactor (sample shows in-root resolution) |
| [scripts/workstream_focus.py](scripts/workstream_focus.py) | +10/-7 | Path resolution refactor |
| [scripts/wrap_scan_consistency.py](scripts/wrap_scan_consistency.py) | +2/-9 | Replaces `Path.home() / ".claude/projects/..."` with `project_root / "memory" / "MEMORY.md"` (verified via diff) |
| [tests/scripts/test_codex_hook_parity.py](tests/scripts/test_codex_hook_parity.py) | +3/-3 | Mirrors check_codex_hook_parity.py refactor |
| [tests/scripts/test_memory_md_ceiling.py](tests/scripts/test_memory_md_ceiling.py) | +9/-26 | Removes home-directory MEMORY.md path references |
| [tests/scripts/test_retroactive_harvest_bridge_threads.py](tests/scripts/test_retroactive_harvest_bridge_threads.py) | +2/-2 | Likely path refactor |

**Disposition:** **Commit 2** — "scripts: Resolve auto-memory paths from project root, not home dir (GENERATOR-HARDENING-002 partial)"

**Note on traceability:** This commit progresses GENERATOR-HARDENING-002 row 17 toward closure, but does NOT claim to close it (Codex NO-GO at `-008` is still in force; full closure is its own bridge thread). The commit message will say "partial" and reference the open bridge.

### §1.4 Group D — Auto-regenerated session telemetry (5 files)

These files regenerate on every `SessionStart` hook (per [scripts/session_self_initialization.py](scripts/session_self_initialization.py)). They do not represent unstaged work; they're the natural drift produced by the lifecycle hook.

| File | Diff stat | Source |
|---|---|---|
| [docs/gtkb-dashboard/dashboard-data.json](docs/gtkb-dashboard/dashboard-data.json) | ~4900 lines churn | SessionStart |
| [docs/gtkb-dashboard/session-startup-report.md](docs/gtkb-dashboard/session-startup-report.md) | +13/-11 | SessionStart |
| [docs/gtkb-dashboard/session-wrapup-report.md](docs/gtkb-dashboard/session-wrapup-report.md) | +1/-1 | SessionStart (proactive wrap-up) |
| [memory/gtkb-dashboard-history.json](memory/gtkb-dashboard-history.json) | ~1080 lines churn | SessionStart (KPI append) |
| [memory/pending-owner-decisions.md](memory/pending-owner-decisions.md) | +14/-0 | owner-decision-tracker.py hook |

**Disposition:** **Commit 5 (LAST)** — "telemetry: S317 session-start dashboard + history regen (auto)" — committed last so the rest of the work doesn't pollute the diff. The 14-line `pending-owner-decisions.md` addition (DECISION-0042..0045) is real state and should be tracked.

**Open question for Codex review:** Should auto-regen telemetry be committed at all? Alternative — add `docs/gtkb-dashboard/dashboard-data.json` and `memory/gtkb-dashboard-history.json` to `.gitignore`. Tradeoff: gitignoring loses historical KPI snapshots from git history but ends the per-session diff churn. Recommendation: **commit for now** (preserves history); revisit as a separate bridge if churn becomes a maintenance burden.

### §1.5 Group E — Other modified files (1 file)

| File | Diff stat | Intent |
|---|---|---|
| [memory/work_list.md](memory/work_list.md) | +5/-5 | Likely S316 close-out edit; needs diff inspection before commit |
| [independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md](independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md) | (size unknown) | Codex bootstrap doc; likely S315/S316 update |
| [independent-progress-assessments/CODEX-WAY-OF-WORKING.md](independent-progress-assessments/CODEX-WAY-OF-WORKING.md) | (size unknown) | Codex doc; likely S315/S316 update |
| [independent-progress-assessments/LOYAL-OPPOSITION-LOG.md](independent-progress-assessments/LOYAL-OPPOSITION-LOG.md) | (size unknown) | LO log; cumulative session history |

**Disposition:** **Commit 4** — "docs: S316 wrap-up updates to work_list, Codex bootstrap, and LO log" — preceded by a per-file diff inspection step; if any diff appears unintentional or destructive, that file is excluded and flagged for owner review.

---

## §2. Untracked entries inventory (65 entries; 6 logical groups)

### §2.1 Group F — Auto-memory feedback files (59 files)

[memory/feedback/](memory/feedback/) contains 60 files; 1 (`feedback_explicit_destructive_action_authorization.md`) was committed in S316 commit `b1d21aa0`; 59 remain untracked. All sampled files (3 read in full) have proper YAML frontmatter (`name`, `description`, `type: feedback`) per the Claude Code auto-memory spec. MEMORY.md's "Feedback Index" links to ~30 of them — the broken-link surface if these were deleted is concrete.

**Disposition:** **Commit 3a** — "memory: Track auto-memory feedback files migrated in S315 (59 files)"

### §2.2 Group G — Auto-memory topic files (43 files)

[memory/topics/](memory/topics/) is similarly untracked (43 files). Same migration class as Group F. Sample filenames suggest topic-domain knowledge (`activation-model.md`, `admin-ui.md`, `cosmos-db.md`, `decision_spec1840_cors.md`, `deployment.md`, `email.md`).

**Disposition:** **Commit 3b** — "memory: Track auto-memory topic files migrated in S315 (43 files)" — separate from 3a so each scope is independently revertable. Both commits in the same logical commit-group.

### §2.3 Group H — Project-root-boundary rule file (1 file)

[.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md) — owner-authored S315; cited in CLAUDE.md/AGENTS.md/the three modified rule files in Group A. Can NOT be committed separately from Group A without breaking the cross-references.

**Disposition:** **Bundled into Commit 1** with Group A.

### §2.4 Group I — Harness-state scaffold (2 dirs)

| Path | Contents |
|---|---|
| [.codex/agent-red-hooks/](.codex/agent-red-hooks/) | 13 files (dispatch scripts, telemetry JSON, .cmd shims, role records) |
| [applications/Agent_Red/harness-state/](applications/Agent_Red/harness-state/) | 2 empty subdirs (`claude/`, `codex/`) |

The `.codex/agent-red-hooks/` content is functional — it's the Codex hook adapter dispatch surface. The `applications/Agent_Red/harness-state/` subdirs are empty placeholders.

**Disposition:** **Commit 4a (.codex/agent-red-hooks/)** — "harness-state: Track Codex hook adapter dispatch surface (S315 migration)". For empty subdirs in `applications/Agent_Red/harness-state/`, **add `.gitkeep` files** to preserve directory structure or **defer until populated** (recommendation: add `.gitkeep` since the bucket model in [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md) marks these as expected presence).

**Question for Codex review:** Should empty `harness-state/{claude,codex}/` subdirs be committed with `.gitkeep`, or deferred until they're populated? Recommendation: `.gitkeep` to make the bucket model visible in tree.

### §2.5 Group J — `.gitignore` candidates (2 entries)

| Path | Reason |
|---|---|
| `.tmp.driveupload/` | **3.6 GB**. Drive-sync staging directory. Adding to .gitignore prevents accidental commit. |
| `memory/MEMORY.md.backup-20260425-222126` | S309 MEMORY.md trim backup. Per S309 entry, MEMORY.md trim was VERIFIED at `gtkb-startup-enhancements-p1-006.md` — backup is no longer load-bearing. **However, deletion is destructive — defer to separate proposal.** Keep in working tree as untracked for now; do not commit. |

**Disposition:** **Commit 6 (separate)** — "gitignore: Exclude .tmp.driveupload/ Drive-sync staging dir". Single-line .gitignore addition.

---

## §3. Files explicitly NOT in this proposal

| Item | Reason |
|---|---|
| `.tmp.driveupload/` (3.6 GB) | Excluded via .gitignore (Group J). Owner can decide separately whether to delete the contents. |
| `memory/MEMORY.md.backup-20260425-222126` | Deletion is destructive; deferred to separate owner-approved proposal per `feedback_explicit_destructive_action_authorization.md`. |
| `groundtruth.db` and other KB binaries | Not in working-tree status; outside this proposal. |
| Bridge protocol changes | None proposed. |
| KB status promotions | None proposed. |
| Deployment actions | None. (Production hibernating per S314.) |

---

## §4. Proposed scoped commit plan

| # | Commit message | Scope |
|---|---|---|
| 1 | `rules: Track project-root-boundary directive and cross-references (S315/S316 carryover)` | Group A (5 files) + Group B (2 files) + Group H (1 file). 8 entries. All same-intent. |
| 2 | `scripts: Resolve auto-memory paths from project root, not home dir (GENERATOR-HARDENING-002 partial)` | Group C (6 files: 3 scripts + 3 tests). References open bridge thread. |
| 3a | `memory: Track auto-memory feedback files migrated in S315 (59 files)` | Group F. |
| 3b | `memory: Track auto-memory topic files migrated in S315 (43 files)` | Group G. |
| 4 | `docs: S316 wrap-up updates to work_list, Codex bootstrap, LO log + harness-state scaffold` | Group E (4 files) + Group I (.codex/agent-red-hooks/ + 2 .gitkeep stubs). |
| 5 | `telemetry: S317 session-start dashboard + history regen + DECISION-0042..0045 captured (auto)` | Group D (5 files). LAST commit so other diffs are clean. |
| 6 | `gitignore: Exclude .tmp.driveupload/ Drive-sync staging dir` | Single-line .gitignore addition. Order-flexible; can be Commit 0 if desired. |

**Total: 6 commits.** Each scoped, each independently revertable, each with a one-line subject ≤72 chars.

**Ordering rationale:** Commit 6 first (prevents accidental .tmp.driveupload commit during later steps). Then 1, 2, 3a, 3b, 4, 5. Auto-regen telemetry last so the human-meaningful work is reviewable in isolation.

---

## §5. Verification

After all 6 commits:

```
git status --short
```

**Expected output:**
- Modified: only telemetry that regenerated *during* this session's commit work (likely empty if no SessionStart fires mid-work).
- Untracked: only `.tmp.driveupload/` (now gitignored, will not appear), `memory/MEMORY.md.backup-20260425-222126` (deferred per §3).

```
git log --oneline -7
```

**Expected output:** 6 new commits with the §4 messages, atop `b1d21aa0`.

**Test execution (release-candidate gate — non-deploying):**
- Skip frontend per established pattern: `python scripts/release_candidate_gate.py --skip-frontend`
- Expected: pass. Commits 1, 2, 3a, 3b, 4, 5, 6 introduce no new test surface — they record state. The Group C script edits already exist on disk (modified, not new) and the test files are already-modified state being committed; existing test suites will exercise them as-is.

**MEMORY.md link integrity:**
- Spot-check 5 random "Feedback Index" wikilinks in MEMORY.md — confirm files exist post-commit. (They do; the commit just adds them to git.)

---

## §6. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Group C script edits introduce a test failure | LOW (P3) | The release-candidate gate runs all relevant tests; if any fail, Commit 2 is held back and the failing path becomes its own bridge proposal. |
| Group D auto-regen telemetry creates merge conflicts on `develop` | LOW (P3) | `develop` has no other active writer this session; conflict surface = 0. |
| Group E `independent-progress-assessments/*` includes unintentional content | MEDIUM (P2) | Plan: per-file `git diff` review before staging. If diff is unintentional, exclude that file and flag for owner. |
| Codex review identifies a categorization error | LOW (P3) | Bridge protocol absorbs revisions naturally via REVISED versions. |
| `.gitkeep` placeholders for `applications/Agent_Red/harness-state/{claude,codex}/` are unwanted | LOW (P3) | If Codex prefers deferral, drop them from Commit 4 and revisit when populated. |
| Commit messages don't accurately reflect content | LOW (P3) | Each commit's `git diff --stat HEAD` is inspected before the commit creates and verified after. |
| A diff under inspection reveals an unintended change from a prior session | MEDIUM (P2) | Per-file `git diff` step in Commit 1 + 2 + 4. Any anomaly halts the relevant commit and is flagged in a follow-up post-impl note. |

**Top concern:** Group E (Commit 4) covers files I haven't fully diff-inspected. The plan includes a per-file diff inspection gate before staging.

---

## §7. What the post-implementation report will contain

After Codex GO and execution:
- Per-commit `git show --stat <sha>` output (8 commits including ordering changes if any).
- Final `git status --short` output (matches §5 expected).
- Final `git log --oneline -7` output (matches §5 expected).
- Release-candidate gate result (pass/fail) + duration.
- Any per-file diff anomalies discovered during Commit 1/2/4 inspection (expected: zero).
- Updated MEMORY.md S317 entry (recording this triage).

---

## §8. Codex review questions (for the Codex GO/NO-GO response)

1. **Auto-regen telemetry:** Commit (preserve history) or gitignore (end churn)? Recommendation: commit. Open question.
2. **Empty `harness-state/{claude,codex}/` subdirs:** Commit `.gitkeep` placeholders, or defer until populated? Recommendation: `.gitkeep`.
3. **Group E inspection gate:** Should the `git diff` step on `work_list.md`, the two CODEX bootstrap docs, and `LOYAL-OPPOSITION-LOG.md` be a hard pre-commit gate (any diff anomaly = stop) or a soft signal (anomaly noted in post-impl)? Recommendation: hard gate.
4. **MEMORY.md backup file:** Defer (current proposal) or include a separate Commit 7 to delete it? Recommendation: defer per `feedback_explicit_destructive_action_authorization.md`.
5. **Commit 2 traceability:** Does referencing GENERATOR-HARDENING-002 (NO-GO at `-008`) in the commit message create a misleading impression of progress on that thread? Should the message instead be neutral ("scripts: Resolve auto-memory paths from project root") with no thread reference?

---

## §9. Owner directive compliance

- **Project root boundary:** All commits write to `E:\GT-KB`. None touch `E:\Claude-Playground` or any home-directory mirror. ✓
- **Application isolation contract:** Group I writes to `applications/Agent_Red/harness-state/` (Bucket B per [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md)). ✓
- **Explicit destructive action authorization:** No deletions in this proposal. ✓
- **Bridge protocol:** This proposal IS the bridge step; commits await GO. ✓
- **No deferrals (per `feedback_no_deferrals_ever.md`):** Backup-file disposition is deferred only because it requires a separate owner-authorized destructive-action proposal — that is dependency ordering, not deferral. ✓

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
