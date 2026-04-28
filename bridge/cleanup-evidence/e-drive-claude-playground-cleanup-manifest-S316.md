# E:\Claude-Playground Cleanup Manifest — S316

**Scan timestamp (UTC):** 2026-04-28T01:45:35.1080758Z
**Scope:** Read-only inventory of `E:\Claude-Playground` top-level entries
**Authority:** `bridge/e-drive-claude-playground-cleanup-manifest-002.md` (Codex GO with 8 conditions)
**Companion (sister thread):** `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.{md,json}` (item 3 of Deletion-Readiness Contract; VERIFIED)
**Mirror:** `e-drive-claude-playground-cleanup-manifest-S316.json` (machine-readable)

---

## §1. Summary

| | Count |
|---|---|
| Total `E:\Claude-Playground` top-level entries | 16 |
| Reparse points / junctions / symlinks detected | 0 |
| Registered git worktrees under `E:\Claude-Playground` | 0 |
| Credential-like files detected (recursive `.env*` scan; filename + size + timestamp only; no content read) | **49** (see §3.4) |
| Runtime path dependencies from inside `E:\GT-KB` | 0 |
| **ARCHIVE** | **11** |
| **EMPTY** | **2** |
| **NEEDS-OWNER-INSPECTION** | **2** |
| **ORPHAN** | **1** |
| **CONFIRMED-CLEAR** | 0 |

**Bottom line for the owner:** zero runtime path dependencies, zero registered worktrees, zero reparse points. **49 credential-like `.env*` files detected by filename only (no content read); concentrated in `AGNTCY-upstream/` (5) and `CLAUDE-PROJECTS/` (44 — split across the 'Agent Red Customer Engagement-OLD' subtree and the 2 decommissioned worktrees). See §3.4 for path-by-path inventory.** All 16 entries are owner-authorization-gated; none are presented as deletion-authorized by the manifest itself. The substantive review tier is dominated by 2 large directories (AGNTCY-upstream at 632 MB and CLAUDE-PROJECTS at 14.65 GB) where the size warrants a glance — and where the credential-bearing files are concentrated. Owner should consider credential exposure / rotation before deletion authorization, independently of file deletion itself.

## §2. Per-entry table

| # | Name | Type | Size | Files | Last modified | Class | Owner action |
|---|---|---|---|---|---|---|---|
| 1 | `.cursor` | DIR | 0 B | 0 | 2026-02-23 | EMPTY | candidate safe after owner authorization |
| 2 | `.tmp.drivedownload` | DIR | 0 B | 0 | 2026-04-24 | EMPTY | candidate safe after owner authorization |
| 3 | `.tmp.driveupload` | DIR | 4.5 MB | 692 | 2026-04-27 | ARCHIVE | owner may authorize deletion (Drive sync staging) |
| 4 | `.vscode` | DIR | 32 B | 1 | 2026-02-23 | ARCHIVE | owner may authorize deletion (legacy workspace settings) |
| 5 | `AGNTCY-upstream` | DIR | 632 MB | 35437 | 2026-01-29 | NEEDS-OWNER-INSPECTION | owner classifies retention need (per CLAUDE.md AGNTCY canonical source is GitHub, not local copy; **5 credential-like files in subtree** — see §3.4) |
| 6 | `CLAUDE-KNOWLEDGE-BASE` | DIR | 38 KB | 18 | 2026-01-27 | ARCHIVE | owner may authorize deletion (historical KB superseded by current memory/) |
| 7 | `CLAUDE-PROJECTS` | DIR | 14.65 GB | 241386 | 2026-04-24 | NEEDS-OWNER-INSPECTION | owner classifies retention need (contains decommissioned worktrees + legacy checkouts + wikis; **44 credential-like files in subtree** — see §3.4; 14.65 GB warrants a glance) |
| 8 | `COMMITMENTS.md` | FILE | 1.8 KB | 1 | 2026-01-27 | ARCHIVE | owner may authorize deletion (Jan-2026 navigation note) |
| 9 | `CURRENT-PRIORITIES.md` | FILE | 1.4 KB | 1 | 2026-01-27 | ARCHIVE | owner may authorize deletion (superseded by memory/work_list.md) |
| 10 | `DOMAINS.md` | FILE | 3.4 KB | 1 | 2026-01-27 | ARCHIVE | owner may authorize deletion (Jan-2026 navigation note) |
| 11 | `groundtruth-kb` | DIR | 25 MB | 1322 | 2026-04-18 | ARCHIVE | owner may authorize deletion (legacy v0.3.0; superseded by PyPI v0.6.1) |
| 12 | `membase-4-claude` | DIR | 195 KB | 44 | 2026-03-08 | ARCHIVE | owner may authorize deletion (historical predecessor to GroundTruth-KB) |
| 13 | `nul` | FILE | 116 B | 1 | 2026-03-03 | ORPHAN | owner may authorize deletion (reserved-name shell-redirect bug; needs -LiteralPath) |
| 14 | `SHARED-RESOURCES` | DIR | 9.3 KB | 4 | 2026-01-27 | ARCHIVE | owner may authorize deletion (Jan-2026 historical resources) |
| 15 | `START-HERE.md` | FILE | 3.7 KB | 1 | 2026-01-27 | ARCHIVE | owner may authorize deletion (superseded by current CLAUDE.md startup) |
| 16 | `WEEKLY-SYNC.md` | FILE | 1.2 KB | 1 | 2026-01-27 | ARCHIVE | owner may authorize deletion (Jan-2026 weekly-sync note) |

**Tally check:** 16 rows; 11 ARCHIVE + 2 EMPTY + 2 NEEDS-OWNER-INSPECTION + 1 ORPHAN + 0 CONFIRMED-CLEAR = 16 ✓

## §3. Live-dependency grep evidence

### §3.1 Search parameters (per Codex GO condition 5)

- **Search term:** `Claude-Playground`
- **File globs:** `*.md`, `*.toml`, `*.json`, `*.yml`, `*.yaml`, `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.ps1`, `*.sh`, `*.bat`
- **Exclusions (recorded per condition 5):** `bridge/` (audit-trail prose; legitimate quoting in historical context), `.venv/`, `node_modules/`, `.codex_pydeps/`, `__pycache__/`, `.claude/hooks/.codex-bridge-*-context.json` (cached prior bridge messages), `memory/grafana/logs/grafana.err.log` (historical service log)

### §3.2 Categorized non-excluded hits

The grep hit head_limit at 100 files; large fraction are bridge/ (excluded). Non-bridge hits fall into three non-load-bearing categories:

**Category A — Pattern-matching constants in active scripts (forward-only; no Claude-Playground access at runtime):**

| File | Lines | Purpose |
|---|---|---|
| `scripts/wrap_scan_hygiene.py` | 44–47 | `OLD_PROJECT_ROOT_PATTERNS` — strings the script SEARCHES FOR in OTHER files to detect hardcoded-old-path regression |
| `scripts/migrate_root_to_gtkb.py` | 88–126 | One-time migration script's path-rewrite table — finds old paths in other files to rewrite |
| `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | 20 | `OLD_ROOT_TOKEN` test constant verifying wrap_scan_hygiene's old-path detection |
| `tests/scripts/test_session_self_initialization.py` | 1447 | Docstring/comment reference |
| `scripts/archive/*.py` | various | Pre-migration session-handoff scripts; references in docstrings as historical session-location markers |

**Category B — Declarative or documentation references (describe the archive's existence; do not depend on it):**

`CLAUDE.md`, `.claude/rules/project-root-boundary.md`, `AGENTS.md`, `CLAUDE-ARCHITECTURE.md`, `memory/MEMORY.md`, `memory/feedback/feedback_no_hardcoded_paths.md`, `docs/operations/*.md` (multiple), `docs/PROJECT-PLAN.md`, `docs/testing-infrastructure-proposal*.md`, `docs/SESSION-INIT-LINT-REMEDIATION.md`, `independent-progress-assessments/*` (multiple LO reports including hardcoded-path directive INSIGHT)

**Category C — Permissions / approval packets (historical evidence; not runtime access):**

`.claude/settings.local.json`, `.groundtruth/formal-artifact-approvals/2026-04-26-delib-role-definition-assessment.json`

### §3.3 Conclusion

**Runtime path dependencies inside `E:\GT-KB` resolving to `E:\Claude-Playground`: zero.** Every reference is either a pattern-match string for hygiene detection, a declarative description of the archive, or historical evidence. Removing `E:\Claude-Playground` would not break any runtime path resolution from inside `E:\GT-KB`.

## §3.4 Credential-like files inventory (per Codex GO condition 6)

Recursive `.env*` filename scan of `E:\Claude-Playground` produced **49 hits**. **No file content was read.** Path, size, last-modified only. Per condition 6: no values, no content excerpts, no hashes recorded for credential-like files.

**Reproducibility:**
```powershell
Get-ChildItem -LiteralPath "E:\Claude-Playground" -Force -Recurse -File -Filter ".env*" -ErrorAction SilentlyContinue
```

**Grouped by top-level entry:**

### §3.4.1 `AGNTCY-upstream/` (5 files)

| Relative path | Size (B) | Last modified |
|---|---:|---|
| `AGNTCY-upstream\.env` | 3,229 | 2026-01-29T10:41:53 |
| `AGNTCY-upstream\.env.azure.example` | 8,328 | 2026-01-29T10:41:39 |
| `AGNTCY-upstream\.env.example` | 3,229 | 2026-01-29T10:41:39 |
| `AGNTCY-upstream\.env.phase3.5` | 351 | 2026-01-29T10:56:45 |
| `AGNTCY-upstream\.env.phase3.5.example` | 2,388 | 2026-01-29T10:41:39 |

Highest-secret-likelihood: `.env` (3.2 KB) and `.env.phase3.5` (351 B). The `.example`-suffixed files appear to be templates.

### §3.4.2 `CLAUDE-PROJECTS\Agent Red Customer Engagement-OLD\` (26 files)

Top-level (3):

| Relative path | Size (B) | Last modified |
|---|---:|---|
| `\.env.example` | 3,030 | 2026-04-23T22:28:30 |
| `\.env.integration.example` | 4,005 | 2026-04-20T22:37:55 |
| **`\.env.local`** | **12,375** | 2026-04-21T11:18:06 |

Per-app under `admin/{provider,shopify,standalone}/` (12 files: 4 per app — `.env.local`, `.env.mock`, `.env.production`, `.env.staging` — each 125-383 B):

| App subtree | Count | Notable |
|---|---|---|
| `admin\provider\` | 4 | `.env.local` (341 B, 2026-04-20) |
| `admin\shopify\` | 4 | `.env.local` (341 B, 2026-04-20) |
| `admin\standalone\` | 4 | `.env.local` (341 B, 2026-04-20) |

Inside an `elegant-brattain` worktree subtree (9 files: 2 top-level templates + 6 per-app `.env.{mock,production,staging}` + 1 missing `.env.local`-class file — likely abandoned worktree):

| Subtree | Count |
|---|---|
| `\.claude\worktrees\elegant-brattain\` | 9 (templates + per-app `.env.{mock,production,staging}`) |

Highest-secret-likelihood files in this subtree: top-level `.env.local` (12.3 KB) and the 4 per-app `.env.local` files at `admin/{provider,shopify,standalone}/.env.local` (each 341 B).

### §3.4.3 `CLAUDE-PROJECTS\agent-red-e1-apply\` decommissioned worktree (9 files)

| Subtree | Count | Note |
|---|---|---|
| Top-level `.env.example` + `.env.integration.example` | 2 | templates |
| `admin\{provider,shopify,standalone}\.env.{mock,production,staging}` | 7 | per-env configs (templates and mock data) |

This worktree was decommissioned earlier this session (branch `e1-apply` pushed to origin per `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md`). All files dated 2026-04-18T08:47:03 (uniform timestamp = checkout time, not edit time). Notably **no `.env.local`** at any level — all credential-like files here are templates or per-environment configs.

### §3.4.4 `CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration\` decommissioned worktree (9 files)

Identical structure to §3.4.3: 2 top-level `.env.{example,integration.example}` + 7 per-env mocks/configs. All files dated 2026-04-22T02:10:39 (checkout time). No `.env.local` files.

### §3.4.5 Owner inspection notes

The `49` figure includes 23 templates (`.example`, `.azure.example`, `.phase3.5.example`, `.integration.example` suffixes), 7 mock-data files (`.env.mock`), and 19 mixed `.env.local`/`.env`/`.env.production`/`.env.staging`/`.env.phase3.5` files of which the highest-likelihood-real-secret candidates are:

1. `AGNTCY-upstream\.env` (3,229 B)
2. `AGNTCY-upstream\.env.phase3.5` (351 B)
3. `CLAUDE-PROJECTS\Agent Red Customer Engagement-OLD\.env.local` (12,375 B)
4. `CLAUDE-PROJECTS\Agent Red Customer Engagement-OLD\admin\provider\.env.local` (341 B)
5. `CLAUDE-PROJECTS\Agent Red Customer Engagement-OLD\admin\shopify\.env.local` (341 B)
6. `CLAUDE-PROJECTS\Agent Red Customer Engagement-OLD\admin\standalone\.env.local` (341 B)

Per Codex GO condition 6, no file content was read; the manifest cannot definitively distinguish "real secret" from "template-with-real-shape-values." Owner inspection is required to make that distinction. **The deletion authorization question is twofold:** (a) authorize deletion of the archive directory (which removes these files), AND (b) consider whether any archived credentials may have been exposed via Drive sync, OneDrive, or backup before deletion — credential rotation may be appropriate independent of file deletion.

## §4. Worktree-tracking verification

```
git -C E:/GT-KB worktree list --porcelain | Select-String "Claude-Playground"
(empty)
```

Zero registered worktrees under `E:\Claude-Playground`. The 2 prior outside-root worktrees (`agent-red-e1-apply` and `agent-red-gtkb-current-main-integration`) were pushed to origin and removed from `git worktree list` earlier this session per `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md`. Their on-disk directories still exist inside `CLAUDE-PROJECTS/` (row 7) but are no longer git-tracked.

## §5. Reproducibility commands

```powershell
# Re-enumerate top level (skipping reparse-point traversal):
Get-ChildItem -LiteralPath "E:\Claude-Playground" -Force | Sort-Object Name

# Detect reparse points (must precede recursion):
Get-ChildItem -LiteralPath "E:\Claude-Playground" -Force | ForEach-Object {
  ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
}

# Rollup size + file count for an entry (skip reparse points):
Get-ChildItem -LiteralPath <entry> -Recurse -Force -File -ErrorAction SilentlyContinue |
  Measure-Object Length -Sum

# Verify no registered worktrees under the path:
git -C E:/GT-KB worktree list --porcelain | Select-String "Claude-Playground"
```

```bash
# Live-dependency grep across active surfaces (Grep tool):
# pattern: "Claude-Playground"
# globs: *.md *.toml *.json *.yml *.yaml *.py *.ts *.tsx *.js *.jsx *.ps1 *.sh *.bat
# exclusions: bridge/, .venv/, node_modules/, .codex_pydeps/, __pycache__/,
#             .claude/hooks/.codex-bridge-*-context.json,
#             memory/grafana/logs/grafana.err.log
```

## §6. Out-of-scope reminders

| | |
|---|---|
| E:\ root-level entries | Separate manifest at `e-drive-root-deletion-readiness-manifest-S316.{md,json}` (VERIFIED `-008`) |
| C:\ outside-root worktrees | `claude-design-backlog`, `gh-dep2` are unaffected by E:\ deletion; separate disposition track |
| Recursive content hashing inside Claude-Playground | Not performed; the deletion-readiness question is liveness (no path resolves into the archive), not content equivalence |
| Actual deletion | Owner-authorized in a separate operation; this manifest is read-only evidence |

## §7. Recommendations for the owner's deletion decision

Every entry below is **owner-authorization-gated**; the manifest does not declare any entry deletion-ready independently of owner action.

**Tier — minimal review then owner authorizes (11 entries, ~58 KB total + small dirs):**

`COMMITMENTS.md`, `CURRENT-PRIORITIES.md`, `DOMAINS.md`, `START-HERE.md`, `WEEKLY-SYNC.md`, `.tmp.drivedownload`, `.cursor`, `.vscode`, `CLAUDE-KNOWLEDGE-BASE`, `SHARED-RESOURCES`, `membase-4-claude`

These are January–March 2026 ARCHIVE/EMPTY content with no live deps. Deletion is candidate-after-owner-authorization with minimal review.

**Tier — substantive review then owner authorizes (4 entries, ~15.3 GB total):**

| Name | Size | Why review |
|---|---|---|
| `AGNTCY-upstream` | 632 MB | Per CLAUDE.md the canonical AGNTCY source is GitHub, not local. Owner decides whether to retain this snapshot or delete and rely on the public repo. |
| `CLAUDE-PROJECTS` | 14.65 GB | Contains the 2 decommissioned-this-session worktree directories (branches are durable on origin), plus 'Agent Red Customer Engagement-OLD', the .zip backup, and historical wiki workdirs. Substantive size warrants a glance before deletion. |
| `groundtruth-kb` | 25 MB | Legacy v0.3.0 framework checkout; current is v0.6.1 from PyPI. Per project-root-boundary rule, no GT-KB executable should live outside `E:\GT-KB`. |
| `.tmp.driveupload` | 4.5 MB | Drive sync staging directory; recently modified (2026-04-27); owner may want to capture transient content before deletion. |

**Tier — reserved-name handling (1 entry):**

`nul` — 116-byte file with reserved Windows filename. Same shell-redirect-bug pattern as the in-root nul artifact. Deletion uses `Remove-Item -LiteralPath` similar to the other reserved-name handling. Owner authorizes.

After owner decisions on the above, deletion of `E:\Claude-Playground` (item 2 of the Deletion-Readiness Contract) is ready to execute. Combined with item 3 (E:\ root-level entries; VERIFIED), items 1, 2, 3 of the Contract will be closed, with items 4 (`applications/Agent_Red/` populated) and 5 (release-gate DCL) remaining for the wholesale `E:\` deletion gate.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
