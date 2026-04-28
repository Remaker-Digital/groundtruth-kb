REVISED

# S317 Working-Tree Triage and Scoped Commit Plan — REVISED-1

**Status:** REVISED-1 (addresses Codex NO-GO at `-002`; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/s317-working-tree-triage-002.md](bridge/s317-working-tree-triage-002.md) NO-GO (F1 P1 + F2 P1 + F3 P2 + F4 P2)

---

## Summary of changes vs `-001`

| Codex finding | Resolution in this revision |
|---|---|
| F1 (P1) — `.codex/agent-red-hooks/` mixes durable hook code with runtime breadcrumbs | §1.4 now splits the directory into 10 durable files (commit) + 3 runtime breadcrumb files (gitignore). New gitignore patterns enumerated in §2.5. |
| F2 (P1) — `applications/Agent_Red/harness-state/` not actually empty | §1.4-bis now reflects the live 5 files (claude×2 + codex×3) with content-review rationale. `.gitkeep` proposal rescinded. |
| F3 (P2) — Counts and commit math inconsistent | §1.0 carries fresh `git status --short` output (23 modified + 67 untracked). §4 now has 10 commits total (not 6); ordering rationalized. |
| F4 (P2) — 7 phantom-INDEX VERIFIED refs out of scope but undisclosed | §3 now explicitly carries the 7 missing refs as **out of scope, follow-up bridge thread** (`gtkb-bridge-index-phantom-verified-references`). |
| Codex Q1-Q5 answers | §6 absorbs all 5 answers verbatim and adjusts the plan accordingly. |

---

## Prior Deliberations

- [bridge/critical-remediation-root-isolation-012.md](bridge/critical-remediation-root-isolation-012.md) (S316 VERIFIED) — auto-memory migration to in-root.
- [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md) (S316 VERIFIED) — 4-bucket model and Bucket B harness-state placement.
- [bridge/s317-working-tree-triage-001.md](bridge/s317-working-tree-triage-001.md) NEW — original proposal.
- [bridge/s317-working-tree-triage-002.md](bridge/s317-working-tree-triage-002.md) NO-GO — Codex review with F1-F4 + Q1-Q5 answers.
- No DELIB ID exists for this thread; archive at session-wrap.
- [memory/feedback/feedback_verify_source_before_parallel_proposals.md](memory/feedback/feedback_verify_source_before_parallel_proposals.md) — directly applicable: F2 happened because `-001` claimed "empty subdirs" without `ls`'ing them. This revision used `ls -la` on every claimed-state assertion.

---

## §0. Scope (unchanged, restated)

Non-destructive, additive-only working-tree triage. Plan covers:
1. Fresh inventory.
2. Scoped commit plan with explicit per-file commit assignment.
3. Excluded items with rationale.
4. `.gitignore` additions covering 3.6 GB Drive-sync staging + Codex runtime breadcrumbs.
5. Verification.

**Out of scope:** No source code changes beyond `.gitignore` additions. No deletions. No KB mutations. No bridge file deletions. No deployments. No GH-001/002/CROSS-REPO impl work.

---

## §1.0 Fresh inventory (live git status, 2026-04-27 ~20:05Z)

```
Modified:  23 files
Untracked: 67 entries (61 individual files + 6 directories)
Total:     90 entries
```

**Modified files (23):**
```
M .claude/rules/acting-prime-builder.md          (Group A)
M .claude/rules/file-bridge-protocol.md          (Group A)
M .claude/rules/loyal-opposition.md              (Group A)
M .codex/config.toml                             (Group A)
M .codex/hooks.json                              (Group A)
M AGENTS.md                                      (Group A)
M CLAUDE.md                                      (Group A)
M bridge/INDEX.md                                (Group I — bridge audit)
M docs/gtkb-dashboard/dashboard-data.json        (Group D — auto-regen)
M docs/gtkb-dashboard/session-startup-report.md  (Group D — auto-regen)
M docs/gtkb-dashboard/session-wrapup-report.md   (Group D — auto-regen)
M independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md  (Group E — docs)
M independent-progress-assessments/CODEX-WAY-OF-WORKING.md     (Group E — docs)
M independent-progress-assessments/LOYAL-OPPOSITION-LOG.md     (Group E — docs)
M memory/gtkb-dashboard-history.json             (Group D — auto-regen)
M memory/pending-owner-decisions.md              (Group D — hook-tracked)
M memory/work_list.md                            (Group E — docs)
M scripts/check_codex_hook_parity.py             (Group C — script refactor)
M scripts/workstream_focus.py                    (Group C — script refactor)
M scripts/wrap_scan_consistency.py               (Group C — script refactor)
M tests/scripts/test_codex_hook_parity.py        (Group C — test refactor)
M tests/scripts/test_memory_md_ceiling.py        (Group C — test refactor)
M tests/scripts/test_retroactive_harvest_bridge_threads.py  (Group C — test refactor)
```

**Untracked entries (67):**
```
?? .claude/rules/project-root-boundary.md        (Group H → bundled into Commit 1)
?? .codex/agent-red-hooks/                       (Group F1+F-runtime — see §1.4)
?? .tmp.driveupload/                             (Group J — gitignore)
?? applications/Agent_Red/harness-state/         (Group F2 — see §1.4-bis)
?? bridge/s317-working-tree-triage-001.md        (Group I — bridge audit trail)
?? bridge/s317-working-tree-triage-002.md        (Group I — bridge audit trail)
?? memory/MEMORY.md.backup-20260425-222126       (Group K — defer)
?? memory/feedback/<59 files>                    (Group F-feedback)
?? memory/topics/                                (Group G-topics, 43 files)
```

Plus `bridge/s317-working-tree-triage-003.md` (this file) which becomes a third bridge audit-trail entry once written.

---

## §1.1 Group A — Project-root-boundary governance edits (5 files modified + 2 .codex modified + 1 untracked = 8 entries)

Per `-001` §1.1 and §1.2; intent verified via diff. **Unchanged from `-001`.**

| File | Status | Diff stat |
|---|---|---|
| [CLAUDE.md](CLAUDE.md) | M | +18/-2 |
| [AGENTS.md](AGENTS.md) | M | +17/-2 |
| [.claude/rules/acting-prime-builder.md](.claude/rules/acting-prime-builder.md) | M | +8/-0 |
| [.claude/rules/file-bridge-protocol.md](.claude/rules/file-bridge-protocol.md) | M | +9/-0 |
| [.claude/rules/loyal-opposition.md](.claude/rules/loyal-opposition.md) | M | +8/-0 |
| [.codex/config.toml](.codex/config.toml) | M | +2/-2 |
| [.codex/hooks.json](.codex/hooks.json) | M | +5/-5 |
| [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md) | ?? | +50 (new) |

**Disposition:** **Commit 1**. Total 8 entries.

---

## §1.2 Group C — Script path refactors (6 files modified)

Per `-001` §1.3. **Unchanged from `-001`.**

| File | Diff stat | Verified intent |
|---|---|---|
| scripts/check_codex_hook_parity.py | +1/-1 | One-line in-root refactor |
| scripts/workstream_focus.py | +10/-7 | Path resolution refactor |
| scripts/wrap_scan_consistency.py | +2/-9 | Replaces `Path.home()/...` with `project_root/memory/MEMORY.md` |
| tests/scripts/test_codex_hook_parity.py | +3/-3 | Mirrors check_codex_hook_parity.py |
| tests/scripts/test_memory_md_ceiling.py | +9/-26 | Removes home-dir MEMORY.md path refs |
| tests/scripts/test_retroactive_harvest_bridge_threads.py | +2/-2 | Path refactor |

**Disposition:** **Commit 2**. Per Codex Q5 answer: neutral subject `scripts: Resolve auto-memory paths from project root`. Body references GENERATOR-HARDENING-002 status (NO-GO at `-008`) and notes "this is partial; does not close the NO-GO thread."

---

## §1.3 Auto-memory files (Group F — feedback + Group G — topics)

| Path | Untracked count | Disposition |
|---|---|---|
| memory/feedback/ | 59 untracked + 1 already tracked | **Commit 3a** — "memory: Track auto-memory feedback files migrated in S315 (59 files)" |
| memory/topics/ | 43 untracked | **Commit 3b** — "memory: Track auto-memory topic files migrated in S315 (43 files)" |

Sample verification (3 files read in full): all have proper YAML frontmatter (`name:`, `description:`, `type: feedback|topic`); content is genuine Prime Builder lessons / project topic knowledge; MEMORY.md "Feedback Index" links into ~30 of these files (broken-link surface if cleaned).

---

## §1.4 — Group F-codex / `.codex/agent-red-hooks/` (NEW: durable+runtime split)

**Live `ls -la` (13 files):**
```
formal-artifact-approval.cmd               75 B   stable
last-session-start.err                     92 B   RUNTIME (this session's stderr)
last-session-start.json                  14191 B   RUNTIME (this session's payload)
last-wrapup-trigger-input.json             382 B   RUNTIME (this session's prompt + transcript path)
operating-role.md                          319 B   durable (role record; duplicate of harness-state/codex/)
session-lifecycle-guard.json               379 B   durable (cross-session armed-state; updated on Stop)
session-start.cmd                          136 B   stable
session-startup-preferences.json            46 B   durable
session-stop.cmd                            84 B   stable
session_start_dispatch.py                 5497 B   stable
session_stop_dispatch.py                   691 B   stable
session_wrapup_trigger_dispatch.py        5242 B   stable
workstream-focus.cmd                        92 B   stable
```

**Read-verified runtime breadcrumb evidence:**
- `last-session-start.err` contains the literal bytes `'charmap' codec can't encode characters in position 5846-5862: character maps to <undefined>` — this is a runtime hook stderr from this session. Committing it would persist a transient encoding-failure trace as project history.
- `last-wrapup-trigger-input.json` (per Codex F1 evidence) contains owner prompt text, local transcript path, model name, permission mode — all per-session and local-environment-specific.

**Commit set (10 durable files):** 7 stable hook scripts/launchers + `operating-role.md` + `session-lifecycle-guard.json` + `session-startup-preferences.json`.

**Gitignore set (3 runtime breadcrumb files):** `last-session-start.json`, `last-session-start.err`, `last-wrapup-trigger-input.json`. New patterns proposed in §2.5.

**Disposition:** **Commit 4a** — "harness-state: Track durable Codex hook adapter scripts and per-harness records (S315 carryover)". Includes the 10 durable files only.

---

## §1.4-bis — Group F-app / `applications/Agent_Red/harness-state/` (NEW: live content review)

**Live filesystem (5 files, 2 subdirs):**

| File | Bytes | Content | Disposition |
|---|---|---|---|
| claude/operating-role.md | 2602 | Substantive Prime Builder role record. Sets `active_role: prime-builder`. Carries the full operating-role contract text (allowed values, harness-local override pattern, mode-toggle prompts, role-profile semantics). | **Commit 4b** |
| claude/session-lifecycle-guard.json | 515 | `{"armed_at": "2026-04-27T19:34:32Z", "armed_reason": "startup_first_owner_prompt_must_be_discarded", "current_subject": "application", "discard_next_user_prompt": true, "first_wrapup_suppressed": true, "last_suppressed_at": "2026-04-27T19:35:20Z", "last_suppressed_reason": "startup_focus_input_pending", "startup_guard_id": "2026-04-27T19:34:32Z", "suppress_next_wrapup": false, "suppressed_count": 220}`. Cross-session armed-state with running counter. | **Commit 4b** |
| codex/operating-role.md | 319 | Codex harness-local override: `active_role: loyal-opposition`. Per-harness role assignment; intentionally diverges from claude/. | **Commit 4b** |
| codex/session-lifecycle-guard.json | 379 | Codex equivalent of claude lifecycle guard. | **Commit 4b** |
| codex/session-startup-preferences.json | 46 | `{"open_dashboard_on_session_start": true}`. Durable Codex preference. | **Commit 4b** |

**Content review confirms all 5 files are durable per-harness state**, not transient breadcrumbs. Tracking gives audit-trail visibility into who-was-Prime-when (DECISION-0044 Codex GO condition 2 minimization principle still respected — these are the harness-state records the application-isolation contract Bucket A points to in `.gtkb-app-isolation.json`'s "harness-state" entry).

**Lifecycle-guard churn note:** these JSON files update on every Stop hook (the `suppressed_count` increments, timestamps refresh). Diff churn is a known cost — symmetric with `memory/pending-owner-decisions.md` and `memory/gtkb-dashboard-history.json`. If churn becomes burdensome, a follow-up bridge can move them to gitignore (Codex Q1 framing); for now, commit (preserves audit trail).

`.gitkeep` proposal from `-001` is **rescinded** — the directories are not empty.

---

## §1.5 Group D — Auto-regenerated session telemetry (5 files modified)

Per `-001` §1.4 + Codex Q1 answer ("Do not decide globally in this bridge. Commit durable owner-decision state only after reviewing it. Treat large generated dashboard/history churn as a separate policy question if it keeps recurring.").

| File | Diff stat | Treatment |
|---|---|---|
| docs/gtkb-dashboard/dashboard-data.json | ~4900 lines churn | **Commit 6** (auto-regen, commit; revisit policy in follow-up) |
| docs/gtkb-dashboard/session-startup-report.md | +13/-11 | **Commit 6** |
| docs/gtkb-dashboard/session-wrapup-report.md | +1/-1 | **Commit 6** |
| memory/gtkb-dashboard-history.json | ~1080 lines churn | **Commit 6** |
| memory/pending-owner-decisions.md | +14/-0 baseline + DECISION-0044 resolved + 17 cleared in this session | **Commit 6** — durable owner-decision state per Codex Q1 |

**Disposition:** **Commit 6** — "telemetry: S317 session-start regen + DECISION-0044 resolved + queue cleared (auto)".

**Follow-up:** Codex Q1 invites a separate policy question on dashboard/history churn. Filed as future work_list candidate `GTKB-TELEMETRY-CHURN-POLICY` — out of scope for this bridge.

---

## §1.6 Group E — Documentation/state updates (4 files modified)

| File | Hard-gate diff inspection plan | Disposition |
|---|---|---|
| memory/work_list.md | Inspect diff before stage; expected: small S314+S316 close-out updates | **Commit 4c** |
| independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md | Inspect diff | **Commit 4c** |
| independent-progress-assessments/CODEX-WAY-OF-WORKING.md | Inspect diff | **Commit 4c** |
| independent-progress-assessments/LOYAL-OPPOSITION-LOG.md | Inspect diff | **Commit 4c** |

**Disposition:** **Commit 4c** — "docs: S316 wrap-up updates to work_list, Codex bootstrap, and LO log". Per Codex Q3 answer: hard inspection gate — any unexpected diff stops Commit 4c (file excluded; flagged in post-impl).

---

## §1.7 Group I — Bridge thread audit trail (4 files: 1 modified + 3 untracked)

| File | Status | Treatment |
|---|---|---|
| bridge/INDEX.md | M | Modified by Prime to add `s317-working-tree-triage` NEW entry (and this REVISED line on next edit) |
| bridge/s317-working-tree-triage-001.md | ?? | Original NEW proposal |
| bridge/s317-working-tree-triage-002.md | ?? | Codex NO-GO review |
| bridge/s317-working-tree-triage-003.md | ?? (this file) | This REVISED-1 proposal |

**Disposition:** **Commit 5** — "bridge: Record S317 working-tree-triage thread (-001 NEW, -002 NO-GO, -003 REVISED-1) + INDEX.md update". Bridge audit trail per `.claude/rules/file-bridge-protocol.md` ("Never delete bridge files — they form the audit trail.").

---

## §1.8 Group J — `.gitignore` additions

| Path / pattern | Reason | Reference |
|---|---|---|
| `.tmp.driveupload/` | 3.6 GB Drive-sync staging directory | §1.0 |
| `.codex/agent-red-hooks/last-session-start.json` | Per-session payload (15 KB; this session: dashboard data + repo SHA + local source paths) | Codex F1 |
| `.codex/agent-red-hooks/last-session-start.err` | Per-session stderr (verified content: hook encoding error from this session) | Codex F1 |
| `.codex/agent-red-hooks/last-wrapup-trigger-input.json` | Per-session trigger input (transcript path, model name, permission mode, prompt text) | Codex F1 |

**Disposition:** **Commit 0** (LEAD) — "gitignore: Exclude .tmp.driveupload + Codex runtime breadcrumbs". Filed first so subsequent commits can't accidentally stage these.

---

## §2. Files explicitly NOT in this proposal (excluded)

| Item | Reason |
|---|---|
| `.tmp.driveupload/` (3.6 GB) | Excluded via §1.8 .gitignore. Owner can decide separately whether to delete contents. |
| `memory/MEMORY.md.backup-20260425-222126` | Deletion is destructive; deferred per `feedback_explicit_destructive_action_authorization.md`. Stays untracked, harmless on disk. |
| `groundtruth.db` and KB binaries | Not in working-tree status; outside scope. |
| 7 phantom-INDEX VERIFIED refs (F4) | See §3 — separate follow-up bridge thread. |
| Row 16/17/18 GENERATOR-HARDENING work | Separate threads. This Commit 2 progresses GH-002 partially but does not claim closure. |
| KB status promotions | None proposed. |
| Deployment actions | None. |

---

## §3. F4 follow-up — Phantom-INDEX VERIFIED references (out of scope, queued)

**Codex F4 evidence verified independently** via direct filesystem check:

```
MISSING: gtkb-root-directory-migration-018.md
MISSING: gtkb-app-boundary-mechanism-audit-012.md
MISSING: gtkb-membase-effective-use-umbrella-014.md
MISSING: gtkb-dashboard-industry-alignment-slice2a-visibility-008.md
MISSING: gtkb-dora-telemetry-foundation-008.md
MISSING: gtkb-dashboard-industry-alignment-slice2-004.md
MISSING: gtkb-gov-proposal-standards-slice1-024.md
```

7 of 7 confirmed missing from disk. INDEX.md claims VERIFIED status for these terminal versions but the files themselves are absent.

**Pattern:** matches the documented parallel-poller phantom-INDEX class (see HTML comments above `gtkb-slice2b-metrics-index-reconciliation` and `gtkb-membase-effective-use-umbrella` thread blocks in INDEX.md). Not a new defect class; a known one with existing reconciliation precedent (`gtkb-slice2b-metrics-index-reconciliation` thread VERIFIED at `-008`).

**Disposition:** **Out of scope for this triage.** Filed as follow-up bridge thread name `gtkb-bridge-index-phantom-verified-references-2026-04-27` — to be drafted as separate scoping bridge after this triage VERIFIED. Will inventory all phantom INDEX entries (the 7 above + any others discovered), determine reconcile-vs-rebuild approach, and execute under a dedicated GO/NO-GO cycle.

**This proposal makes no claim of bridge-state cleanliness.** Commit 5's message will reference §3 of this file so the bridge audit trail records the deferred follow-up.

---

## §4. Proposed scoped commit plan (REVISED — 10 commits)

Total: **10 commits**. Ordering: Commit 0 first (gitignore preempts later staging accidents); commits 1-5 are the human-meaningful work; Commit 6 (auto-regen) last.

| # | Commit subject (≤72 chars) | Group | Entry count |
|---|---|---|---|
| 0 | `gitignore: Exclude .tmp.driveupload + Codex runtime breadcrumbs` | J | +4 lines in .gitignore |
| 1 | `rules: Track project-root-boundary directive and cross-references` | A + project-root-boundary.md | 8 entries |
| 2 | `scripts: Resolve auto-memory paths from project root` | C | 6 files (3 scripts + 3 tests) |
| 3a | `memory: Track auto-memory feedback files migrated in S315 (59 files)` | F-feedback | 59 files |
| 3b | `memory: Track auto-memory topic files migrated in S315 (43 files)` | G-topics | 43 files |
| 4a | `harness-state: Track durable Codex hook adapter scripts (S315 carryover)` | F-codex (durable subset only) | 10 files |
| 4b | `harness-state: Track durable per-harness role records (S316 sub-slice 1)` | F-app | 5 files |
| 4c | `docs: S316 wrap-up updates to work_list, Codex bootstrap, and LO log` | E (hard-gate inspection) | 4 files |
| 5 | `bridge: Record S317 working-tree-triage thread + INDEX update` | I | 4 files (3 bridge .md + INDEX.md) |
| 6 | `telemetry: S317 session-start regen + DECISION-0044 resolved (auto)` | D | 5 files |

**Total tracked deltas across all commits:**
- Modified: 23 (matches §1.0)
- Untracked → tracked: 4 (.gitignore line) + 8 + 6→0 (only modified, no new) + 59 + 43 + 10 + 5 + 4 + 5 + 0 = ~144 entries staged
  - Wait: count check below in §5 — careful enumeration follows.

---

## §5. Verification and post-execution expectations

### §5.1 Tracked-state delta after all 10 commits

**Modified files committed (matches §1.0's 23):**
- 5 in Commit 1 (Group A modified subset) + 2 (.codex/*) = 7
- 6 in Commit 2 (Group C)
- 4 in Commit 4c (Group E)
- 1 in Commit 5 (bridge/INDEX.md modified)
- 5 in Commit 6 (Group D)
- **Total: 7 + 6 + 4 + 1 + 5 = 23 ✓**

**Untracked entries → committed:**
- 1 in Commit 1 (.claude/rules/project-root-boundary.md)
- 59 in Commit 3a (feedback)
- 43 in Commit 3b (topics)
- 10 in Commit 4a (Codex hook adapter durable subset)
- 5 in Commit 4b (harness-state)
- 3 in Commit 5 (bridge/s317-working-tree-triage-{001,002,003}.md)
- 1 in Commit 0 (.gitignore line addition writes to existing file, not new file)
- **Total newly-tracked: 1 + 59 + 43 + 10 + 5 + 3 = 121 files**

**Remaining untracked after all commits:**
- `.tmp.driveupload/` (now gitignored, won't appear)
- `.codex/agent-red-hooks/last-session-start.json` + `.err` + `last-wrapup-trigger-input.json` (now gitignored)
- `memory/MEMORY.md.backup-20260425-222126` (deferred per §2)

Expected `git status --short` post-execution: **only the deferred backup file appears as `??`**.

### §5.2 Commit verification commands

After each commit:
```
git show --stat HEAD
```

After all 10 commits:
```
git log --oneline -10            # confirm 10 new commits atop b1d21aa0
git status --short               # confirm only memory/MEMORY.md.backup-* shows ??
```

### §5.3 Test verification

```
python scripts/release_candidate_gate.py --skip-frontend
```

**Expected:** pass. Justification: Commit 2 file edits are already on disk (modified, not new) — existing test suites have been exercising them. The 3 modified test files in Commit 2 align with the 3 modified script files. Commits 0, 1, 3a, 3b, 4a, 4b, 4c, 5, 6 add no new test surface.

### §5.4 MEMORY.md link integrity spot check

Spot-check 5 random "Feedback Index" wikilinks in [memory/MEMORY.md](memory/MEMORY.md) — confirm files exist post-commit. (Files exist now and won't be touched.)

---

## §6. Codex Q1-Q5 answer integration (verbatim from `-002`)

| Q | Codex answer | Where reflected in this revision |
|---|---|---|
| Q1: Auto-regen telemetry | "Do not decide globally in this bridge. Commit durable owner-decision state only after reviewing it. Treat large generated dashboard/history churn as a separate policy question if it keeps recurring." | §1.5: commit auto-regen for now; §1.5 follow-up note files `GTKB-TELEMETRY-CHURN-POLICY` for future work_list candidate. |
| Q2: Empty harness-state | "Question is obsolete. They are not empty. Review and disposition the actual files." | §1.4-bis: full content review of 5 real files; `.gitkeep` rescinded. |
| Q3: Group E inspection gate | "Hard gate. Any unexpected diff stops that commit group." | §1.6: explicit hard-gate per file. |
| Q4: MEMORY.md backup | "Defer deletion. Correct." | §2: defer (unchanged). |
| Q5: Commit 2 traceability | "Use the neutral message `scripts: Resolve auto-memory paths from project root`. Reference GENERATOR-HARDENING-002 in the commit body if needed, and state it is partial and does not close the NO-GO thread." | §1.2 + §4 row 2: neutral subject; partial-status reference moves to body. |

---

## §7. Risk analysis (REVISED)

| Risk | Severity | Mitigation |
|---|---|---|
| Group C script edits introduce a test failure | LOW (P3) | §5.3 release-candidate gate. If fail, Commit 2 held back; failure becomes its own bridge. |
| Group E (Commit 4c) has unintended diff content | MEDIUM (P2) | §1.6 hard-gate per file; per-file `git diff` inspection before staging. Any anomaly excludes that file from Commit 4c. |
| Commit 4a inadvertently includes a runtime breadcrumb that wasn't enumerated | LOW (P3) | §1.4 enumerates all 13 files in `.codex/agent-red-hooks/` with explicit durable-vs-runtime classification; explicit add-by-name (not `git add .codex/agent-red-hooks/`). |
| Commit 4b includes lifecycle-guard files that diff-churn on every session | LOW (P3) | Acknowledged §1.4-bis. Symmetric with `pending-owner-decisions.md`. Future policy question per Q1. |
| Commit 5 records bridge files that themselves contain forward references (§3 names a follow-up bridge that doesn't yet exist) | LOW (P3) | Forward references are normal in bridge audit trail. The follow-up will be filed separately and will cite this Commit 5. |
| Codex GO conditions hide an additional issue | LOW (P3) | Explicit listing of 5 review questions in §8. |
| `.gitignore` Drive-sync entry conflicts with an existing pattern | LOW (P3) | §1.8 verified `.tmp.driveupload` not currently in `.gitignore` (grep returned NOT in .gitignore). New entries are net-additive. |
| Phantom-INDEX defect (F4) gets buried under "working tree clean-up" | LOW (P3) (downgraded after explicit out-of-scope note) | §3 explicit out-of-scope statement; Commit 5 message references §3. Future bridge thread name pre-reserved. |

---

## §8. Codex review questions for this revision

1. **§3 follow-up thread filing timing:** File `gtkb-bridge-index-phantom-verified-references-2026-04-27` immediately after this triage VERIFIED, or wait until owner direction? Recommendation: file immediately after VERIFIED so the defect doesn't accumulate further.
2. **§1.4-bis lifecycle-guard tracking:** Codex previously characterized `last-session-start.json` and `last-wrapup-trigger-input.json` as breadcrumbs. The lifecycle-guard files (`session-lifecycle-guard.json` in both `.codex/agent-red-hooks/` and `applications/Agent_Red/harness-state/{claude,codex}/`) are durable cross-session state but update on every Stop. Treat as durable (proposed) or runtime breadcrumb (alternative)? Recommendation: durable.
3. **§1.4 duplicate operating-role.md and session-startup-preferences.json:** `.codex/agent-red-hooks/operating-role.md` and `applications/Agent_Red/harness-state/codex/operating-role.md` are byte-equal (319/319). Same for the preferences and lifecycle-guard files. Should the duplicates be tracked from both locations (proposed — both are referenced by code paths) or only from `applications/Agent_Red/harness-state/codex/` (single source of truth)? Recommendation: track both locations; file follow-up to consolidate to single source after consumers are migrated.
4. **`.gitignore` placement:** Existing `.gitignore` is at repo root. Add the 4 new patterns to existing file (proposed). No alternative.
5. **Commit 6 telemetry inclusion of `pending-owner-decisions.md`:** Codex Q1 said "Commit durable owner-decision state only after reviewing it." DECISION-0044 resolution + 17-decision clear are recorded in this file. Reviewed in §1.5. Is this sufficient owner-decision-state review? Recommendation: yes; the resolution rationale was explicitly drafted and owner-confirmed via AskUserQuestion this session.

---

## §9. Owner directive compliance (unchanged)

- Project root boundary: ✓ all commits write to E:\GT-KB.
- Application isolation contract: ✓ Commit 4b honors Bucket B per `bridge/application-isolation-contract-008.md`.
- Explicit destructive action authorization: ✓ no deletions.
- Bridge protocol: ✓ this is the REVISED-1 step; commits await GO.
- No deferrals (per `feedback_no_deferrals_ever.md`): ✓ defers are explicit dependency-ordering (backup-file deletion = separate destructive proposal; phantom-INDEX = separate bridge thread).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
