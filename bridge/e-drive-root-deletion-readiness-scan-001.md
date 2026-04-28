NEW

# E:\ Root-Level Deletion-Readiness Scan

**Status:** NEW (proposal; awaits Codex GO)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Relates to:** `bridge/application-isolation-contract-005.md` §7.5 item 3 (Deletion-Readiness Contract)
**Companion to (separate thread, not bundled):** future `bridge/e-drive-claude-playground-cleanup-manifest-001.md` (item 2)

---

## §1. Goal

Materially reduce the deletion-readiness gap on Deletion-Readiness Contract item 3:

> **E:\ root-level non-GT-KB entries:** NOT YET VERIFIED. `E:\admin/`, `E:\src/`, `E:\widget/`, `E:\Dockerfile`, `E:\requirements.txt`, `E:\config/`, `E:\_canonical-dogfood/`, `E:\_canonical-smoke/`, `E:\automations/`, `E:\tmp/`, `E:\tmp-ps/`, `E:\Camtasia/` need content-hash comparison or owner spot-check before deletion can be classified as safe.

Produce a manifest classifying each E:\ root-level non-GT-KB, non-system, non-Claude-Playground entry so the owner can authorize deletion with evidence.

## §2. Scope (read-only; no modifications)

### §2.1 In scope

For each E:\ root-level entry NOT in {`GT-KB`, `$RECYCLE.BIN`, `System Volume Information`, `Claude-Playground`}:

- Capture metadata: name, type (DIR/FILE), size, last-modified, file count (DIR), recursive byte total (DIR)
- For files: compute SHA256 hash
- For directories whose name matches an in-root counterpart at `E:\GT-KB\<name>` (e.g., `E:\admin` ↔ `E:\GT-KB\admin`):
  - Recursive file-by-file comparison: per-file SHA256, structure overlap
  - Identify outside-only files (in `E:\<name>` but not `E:\GT-KB\<name>`)
  - Identify diverged files (same path, different hash)
- For files at E:\ root with in-root counterparts: SHA256 compare
- For unknown directories: enumerate contents, infer purpose where possible

### §2.2 Classifications produced

Each entry classified as exactly one of:

| Class | Definition |
|---|---|
| **STALE-DUPLICATE** | In-root counterpart contains same or superset of content; outside copy is older or fully redundant; safe to delete |
| **DIVERGED** | In-root and outside copies differ; owner must inspect before deletion (one or both could be valuable) |
| **NOT-A-PAIR** | Name overlaps with in-root entry but content is unrelated; outside entry is independent — owner classifies retention need |
| **ORPHAN** | No in-root counterpart; outside entry is independent — owner classifies retention need |
| **EXCLUDED** | System or already-tracked-elsewhere (`$RECYCLE.BIN`, `System Volume Information`, `Claude-Playground`) — not classified by this scan |

### §2.3 Out of scope (explicitly)

- `E:\Claude-Playground` — separate cleanup-manifest bridge per `-005` §7.6
- `E:\GT-KB` — the preserved root; not under scan
- `E:\$RECYCLE.BIN`, `E:\System Volume Information` — Windows system; never touched
- C:\ worktrees (`claude-design-backlog`, `gh-dep2`) — separate project-root-boundary disposition track
- Any actual deletion — this scan produces a manifest; deletion is a separate step the owner authorizes
- Any modification to GT-KB content — pure read-only scan

## §3. Deliverables

1. **Manifest file** at `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` (Markdown table) and `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` (machine-readable mirror)
2. **Per-entry rows** with: name, type, size, last-modified, classification, recommended-action, evidence summary
3. **Scan timestamp** captured from `[DateTime]::UtcNow` at scan start
4. **Reproducibility commands** included in the manifest

## §4. Procedure

For the post-implementation execution (after Codex GO):

1. Enumerate E:\ entries via `Get-ChildItem -LiteralPath "E:\" -Force`. Capture timestamp.
2. Filter out the 4 excluded entries (`GT-KB`, `$RECYCLE.BIN`, `System Volume Information`, `Claude-Playground`).
3. For each remaining entry:
   - Capture base metadata
   - If file: compute SHA256
   - If directory: enumerate top-level contents; recursive file count + byte total
4. For each directory whose name matches an in-root counterpart:
   - Build file lists for both sides (path-relative)
   - Compare SHA256 per common path; flag diverged
   - Flag outside-only files (potential unique content)
5. For files matching in-root names: SHA256 compare
6. Classify each entry per §2.2
7. Recommend action per classification:
   - STALE-DUPLICATE → safe to delete with E:\ wholesale operation
   - DIVERGED → owner inspects diverged paths before deletion
   - NOT-A-PAIR / ORPHAN → owner classifies retention need
8. Write manifest (Markdown + JSON)
9. File post-implementation report citing the manifest

## §5. Risk and safety

- **Read-only:** the scan does not modify, move, copy, or delete any file. It computes hashes and reads metadata.
- **No secret exposure:** if the scan encounters a file resembling a credential (e.g., `.env*`), it captures the hash and metadata only — never values. (E:\ root has no `.env.local` per prior PowerShell inventory; this is defense-in-depth.)
- **No GT-KB modification:** the scan reads E:\ entries; in-root reads are restricted to `E:\GT-KB\<name>` directories that share names with E:\ root entries (for content-hash comparison). All in-root reads are read-only.
- **Performance:** total bytes across the candidate dirs is ~33 MB based on prior inventory. Hashing SHA256 over ~33 MB is single-digit seconds. The scan is non-burdensome.

## §6. What this scan does NOT authorize

- Deletion of any file or directory
- Modification of any file (in-root or outside)
- Modification of `.gitignore`, CI workflows, or any path reference
- Cleanup of C:\ outside-root worktrees
- Cleanup of `E:\Claude-Playground` (separate bridge)
- Any application-isolation-contract sub-slice work

## §7. Success criteria (for Codex VERIFIED)

1. Manifest exists at the named path and contains rows for every E:\ root-level entry except the 4 excluded.
2. Each row has: name, type, size, last-modified, SHA256 (files only), classification, recommended-action, evidence summary.
3. Tally check: rows-in-manifest + 4-excluded-entries = total `Get-ChildItem` count at scan time.
4. No in-root content modified during the scan (verifiable via `git status` showing only the manifest files as new).
5. Post-implementation report references the manifest paths and summarizes classifications.

## §8. Codex review asks

1. Confirm scope (§2) is read-only and does not bundle work better filed as separate bridges.
2. Confirm classification taxonomy (§2.2) is exhaustive and unambiguous for the entries listed.
3. Confirm the manifest deliverable (§3) provides sufficient evidence for the owner to authorize deletion.
4. Confirm the procedure (§4) does not include any modification step.
5. Confirm the negative-scope statements (§6) are comprehensive.
6. **GO / NO-GO** on the proposal.

## §9. References

- `bridge/application-isolation-contract-005.md` §7.5 — Deletion-Readiness Contract
- `bridge/application-isolation-contract-008.md` — Codex VERIFIED of sub-slice 1 (which kept item 3 as still-pending)
- `.claude/rules/project-root-boundary.md` — placement directive
- Prior PowerShell scan output (this session) — informal evidence used to size the scan; this proposal supersedes it with formal content-hash comparison

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
