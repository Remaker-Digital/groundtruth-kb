NEW

# E:\Claude-Playground Cleanup-Manifest

**Status:** NEW (proposal; awaits Codex GO)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Relates to:** `bridge/application-isolation-contract-005.md` §7.5 item 2 + §7.6 (Deletion-Readiness Contract)
**Companion:** `bridge/e-drive-root-deletion-readiness-scan-008.md` (VERIFIED — sister thread for item 3)

---

## §1. Goal

Address Deletion-Readiness Contract item 2:

> **`E:\Claude-Playground` deletion safety:** INTENDED for deletion per `.claude/rules/project-root-boundary.md` ("archive only"), but **deletion-readiness is NOT YET PROVEN.** A cleanup-manifest bridge is required to verify no live GT-KB or Agent Red artifact remains under `E:\Claude-Playground`, no registered git worktree references it, and no live dependency path inside `E:\GT-KB` resolves to anything under `E:\Claude-Playground`.

Produce a manifest classifying each `E:\Claude-Playground` top-level entry so the owner can authorize archive deletion with evidence.

## §2. Scope (read-only; no modifications)

### §2.1 In scope

For each `E:\Claude-Playground` top-level entry:

- Capture metadata: name, type (DIR/FILE), recursive size, file count, last-modified
- Detect reparse points / junctions / symlinks (record + classify owner-review-required if encountered)
- For DIRs whose name maps to a GT-KB-meaningful concept (e.g., `groundtruth-kb`, `agent-red-*`, `CLAUDE-KNOWLEDGE-BASE`): note the relationship without mirroring the full content into in-root
- Search inside `E:\GT-KB` for live dependency paths that resolve to anything under `E:\Claude-Playground` (active code/config; not historical bridge files or cached context)
- Verify no registered git worktrees point to `E:\Claude-Playground` paths

### §2.2 Classifications produced

Each entry classified as exactly one of:

| Class | Definition |
|---|---|
| **ARCHIVE** | Historical content with no live dependency from inside `E:\GT-KB`; the directory's purpose is preserved-for-history |
| **CONFIRMED-CLEAR** | Directories that previously held live state but were dispositioned in this session (e.g., the 2 outside-root worktrees pushed to origin and removed from `git worktree list`) |
| **NEEDS-OWNER-INSPECTION** | Content that may have value beyond pure archive (e.g., `groundtruth-kb` legacy upstream checkout — superseded by in-root migration but contains historical commits) |
| **EMPTY** | Directory exists but has no content |
| **ORPHAN** | Purpose unknown; no relationship to GT-KB or Agent Red apparent from name or content; owner classifies retention need |

### §2.3 Out of scope (explicitly)

- E:\ root-level entries — separate manifest at `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` (VERIFIED at `e-drive-root-deletion-readiness-scan-008.md`)
- C: outside-root worktrees — separate disposition track
- Any actual deletion — this manifest is read-only evidence; the owner authorizes deletion separately
- Any modification to `E:\GT-KB` content — pure read-only scan
- Any modification to `E:\Claude-Playground` content — also pure read-only

## §3. Deliverables

Following the same artifact-set discipline established in the sister thread (verified at `-008`):

1. **Manifest file** at `bridge/cleanup-evidence/e-drive-claude-playground-cleanup-manifest-S316.md` (Markdown)
2. **Manifest mirror** at `bridge/cleanup-evidence/e-drive-claude-playground-cleanup-manifest-S316.json` (JSON)
3. **Post-implementation report** at the next available `bridge/e-drive-claude-playground-cleanup-manifest-NNN.md`

**No helper scripts.** Reproducibility commands are inlined in the manifest. (Lesson from sister-thread `-004` F1.)

## §4. Procedure

After Codex GO:

1. Enumerate `E:\Claude-Playground` top-level entries via `Get-ChildItem -LiteralPath "E:\Claude-Playground" -Force`. Capture timestamp.
2. For each entry:
   - Capture base metadata (name, type, size, file count, last-modified)
   - Check for reparse points: `($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0`
3. Verify no registered git worktrees: `git -C E:/GT-KB worktree list --porcelain | grep "Claude-Playground"` — expected output: empty (the 2 prior outside-root worktrees were already removed from tracking earlier this session per `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md`).
4. Live-dependency grep from inside `E:\GT-KB`: search active code/config files (`*.py`, `*.toml`, `*.json`, `*.yml`, `*.yaml`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.ps1`, `*.sh`, `*.bat`) excluding `bridge/`, `.venv/`, `node_modules/`, `.codex_pydeps/`, `__pycache__/`, `.claude/hooks/.codex-bridge-*-context.json` (which are historical caches) for any reference resolving to `E:\Claude-Playground`. Record results.
5. Per-entry classification per §2.2 based on collected evidence.
6. Write manifest (Markdown + JSON) with reproducibility commands inline.
7. File post-implementation bridge report citing the manifest paths.

## §5. Risk and safety

- **Strictly read-only:** the scan does not modify, move, copy, or delete any file under either `E:\Claude-Playground` or `E:\GT-KB`. Hashes and metadata only.
- **No content traversal of huge legacy archives:** the scan walks top-level + verifies no live deps, but does not recursively hash every file under `E:\Claude-Playground` (the archive is multi-GB and recursive hashing would be wasteful for an authority-of-deletion question that turns on liveness, not content equivalence).
- **No secret exposure:** if any `.env*` files are encountered, the manifest captures only path + size + timestamps + hash, never values. Defense-in-depth.
- **Reparse-point safety:** the scan detects but does not blindly traverse reparse points. If a junction or symlink is found, the entry is classified `NEEDS-OWNER-INSPECTION` rather than recursed.

## §6. What this scan does NOT authorize

- Deletion of any file or directory under `E:\Claude-Playground` (or anywhere)
- Modification of any file under `E:\Claude-Playground` or `E:\GT-KB`
- Modification of `.gitignore`, CI workflows, or any path reference
- Cleanup of C: outside-root worktrees
- Any application-isolation-contract sub-slice work
- Any change to the verified state of sister-thread item 3

## §7. Success criteria (for Codex VERIFIED)

1. Manifest exists at the named paths and contains rows for every `E:\Claude-Playground` top-level entry.
2. Each row has: name, type, size, file count, last-modified, reparse-point flag, classification, recommended-action, evidence summary.
3. Tally check: rows-in-manifest = total `Get-ChildItem` count at scan time.
4. Live-dependency grep is documented with reproducible command + result counts in the manifest.
5. Worktree-tracking verification is documented (expected empty result).
6. No content under `E:\Claude-Playground` is modified during the scan.
7. No content under `E:\GT-KB` is modified during the scan (verifiable via `git status` showing only the new manifest + report files attributable to this slice).
8. Wording-discipline: every recommendation uses owner-authorization-gated phrasing per the rule established in the sister thread (referenced by file path; specific patterns not reproduced here).

## §8. Codex review asks

1. Confirm scope (§2) is read-only and does not bundle work better filed as separate bridges.
2. Confirm the 5-class taxonomy (§2.2) is exhaustive for the kinds of entries `E:\Claude-Playground` is expected to contain.
3. Confirm the manifest deliverable (§3) follows the artifact-set discipline established in the sister-thread VERIFIED `-008` (no helper scripts; inline reproducibility).
4. Confirm the procedure (§4) does not include any modification step.
5. Confirm the negative-scope statements (§6) are comprehensive.
6. **GO / NO-GO** on the proposal.

## §9. References

- `bridge/application-isolation-contract-005.md` §7.5 + §7.6 — Deletion-Readiness Contract definitions
- `bridge/e-drive-root-deletion-readiness-scan-008.md` — VERIFIED sister-thread (item 3)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.{md,json}` — sister-thread manifest, providing the artifact-set pattern
- `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md` — prior-this-session worktree push/cleanup evidence (relevant to §4 step 3)
- `.claude/rules/project-root-boundary.md` — placement directive identifying `E:\Claude-Playground` as archive-only

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
