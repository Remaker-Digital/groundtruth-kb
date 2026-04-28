NEW

# Application Isolation Contract — Sub-Slice 1 Post-Implementation Report

**Status:** NEW (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/application-isolation-contract-006.md` (Codex GO of REVISED-2 sub-slice 1 only)
**Slice:** Sub-slice 1 of 6 — App-root scaffold + registry

---

## §0. Compliance with Codex GO conditions

| Condition | Compliance |
|---|---|
| 1. Only sub-slice 1 authorized: scaffold + `.gtkb-app-isolation.json` | **MET** — only files under `applications/Agent_Red/` created; no moves, no deletes, no formal artifact writes, no path-ref updates, no release-gate work, no `.gitignore` changes, no `memory/` or state-file updates. |
| 2. App-level `.claude/` and `.codex/` minimal placeholders; no GT-KB platform content | **MET** — `.claude/settings.json` is `{}`; `.codex/config.toml` is a stub `[default]` section with a documenting comment; `.codex/hooks.json` is `{}`. Zero rules, hooks, prompts, credentials, memories, or startup files copied from GT-KB-level. |
| 3. Registry lists actual top-level entries including `harness-state/`, `incident-response/`, scaffolds, registry itself | **MET** — see §3 verification. |
| 4. No `.env.local` read, copied, generated, or modified | **MET** — no `.env.local` operations of any kind. Verified: no Bash/Edit/Write touched any `.env.local` path this session. |
| 5. No Claude-Playground deletion, sibling cleanup, worktree cleanup, Shopify move, PDF move, release-gate integration, or formal artifact mutation | **MET** — none of these were attempted. |
| 6. Deletion readiness still blocked | **MET** (acknowledged) — no deletion-readiness claim made; pre-deletion checklist remains as documented in `-005` §7.5–§7.6. |

## §1. Files created (8 new artifacts)

| # | Path | Size (bytes) | Tracked by git? |
|---|---|---|---|
| 1 | `applications/Agent_Red/.vscode/settings.json` | 3 | **NO** — see §4 known limitation |
| 2 | `applications/Agent_Red/.claude/settings.json` | 3 | YES (negation `!.claude/settings.json` works because parent uses `.claude/*` not `.claude/`) |
| 3 | `applications/Agent_Red/.codex/config.toml` | 420 | YES (no `.codex/` ignore pattern) |
| 4 | `applications/Agent_Red/.codex/hooks.json` | 3 | YES |
| 5 | `applications/Agent_Red/.dockerignore` | 345 | YES |
| 6 | `applications/Agent_Red/.gtkb-app-isolation.json` | ~4.0 KB | YES |

Implicit directories created on disk by file writes: `.vscode/`, `.claude/`, `.codex/` (3 directories under `applications/Agent_Red/`).

## §2. Content of each created file

### §2.1 `.vscode/settings.json`

```json
{}
```

### §2.2 `.claude/settings.json`

```json
{}
```

### §2.3 `.codex/config.toml`

Single `[default]` section with a documenting comment block stating the file is a minimal placeholder per Codex GO sub-slice 1 condition 2 (no GT-KB platform content imported).

### §2.4 `.codex/hooks.json`

```json
{}
```

### §2.5 `.dockerignore`

Empty placeholder with a documenting comment block stating patterns will be populated in the Phase 3 infra cluster move (separate bridge thread).

### §2.6 `.gtkb-app-isolation.json` — registry

Schema version `1.0`. 7 top-level artifact entries:

1. `.claude/` — bucket B, tool: Claude Code
2. `.codex/` — bucket B, tool: Codex CLI
3. `.dockerignore` — bucket B, tool: Docker
4. `.gtkb-app-isolation.json` — bucket B, tool: GT-KB release-gate scan (self-referential)
5. `.vscode/` — bucket B, tool: VSCode
6. `harness-state/` — bucket A, purpose: pre-existing app-level harness state (S315)
7. `incident-response/` — bucket A, purpose: pre-existing IR-0.1 boundary work (S310)

Plus `validator_contract` (5 rules), `out_of_scope_for_sub_slice_1` (7 items), and `known_limitations` (1 item documenting `.vscode/settings.json` gitignore conflict).

## §3. Verification: registry matches actual on-disk state

Filesystem scan after sub-slice 1 (reproducible: `ls -la applications/Agent_Red/`):

| Disk entry | In registry? | Match? |
|---|---|---|
| `.claude/` (DIR) | yes (entry 1) | ✓ |
| `.codex/` (DIR) | yes (entry 2) | ✓ |
| `.dockerignore` (FILE, 345 B) | yes (entry 3) | ✓ |
| `.gtkb-app-isolation.json` (FILE, ~4 KB) | yes (entry 4) | ✓ |
| `.vscode/` (DIR) | yes (entry 5) | ✓ |
| `harness-state/` (DIR; pre-existing) | yes (entry 6) | ✓ |
| `incident-response/` (DIR; pre-existing) | yes (entry 7) | ✓ |

7 disk entries; 7 registry entries; full bidirectional match. No unmatched entries in either direction.

## §4. Known limitation: `.vscode/settings.json` not git-tracked

**Issue:** Existing `.gitignore` line 90 reads `.vscode/` (with trailing slash, no leading slash), which ignores the entire `.vscode/` directory at any depth in the repo. Line 91's `!.vscode/settings.json` cannot take effect because git does not descend into ignored parent directories.

**Diagnostic evidence (executed this session):**

```
$ git check-ignore -v applications/Agent_Red/.vscode/settings.json
.gitignore:90:.vscode/	applications/Agent_Red/.vscode/settings.json
$ git check-ignore -v applications/Agent_Red/.vscode/
.gitignore:90:.vscode/	applications/Agent_Red/.vscode/
$ git ls-files .vscode/
(empty — no .vscode/ files tracked anywhere in the repo)
```

**Why I did not fix this in sub-slice 1:** Proposal `-005` §7.2 explicitly listed "Modify `.gitignore`, CI workflows, or any path reference" as out-of-scope for sub-slice 1. Codex GO at `-006` accepted that scope. Modifying `.gitignore` now would deviate from approved scope.

**Impact:**

- VSCode opening `applications/Agent_Red/` IN THIS CHECKOUT correctly reads `settings.json` (filesystem present).
- Fresh clones, `git clean -fdx`, and worktree creates will NOT have the file.
- The registry entry for `.vscode/` reflects an artifact that exists on this checkout but is not tracked.

**Disposition:** Recommend filing a follow-up "gitignore-hygiene" sub-slice (smaller than full sub-slice 2; could be sub-slice 1.5) with scope: change `.gitignore` line 90 from `.vscode/` to `.vscode/*` (preserving the existing `!.vscode/settings.json` negation, which becomes effective). This is a one-line gitignore change that fixes the latent bug; the `.vscode/settings.json` placeholder then becomes properly tracked.

The registry's `known_limitations` field documents this for downstream consumers.

## §5. `git status` output (sub-slice 1 deliverables only)

Filtered to `applications/Agent_Red/`:

```
?? applications/Agent_Red/.claude/
?? applications/Agent_Red/.codex/
?? applications/Agent_Red/.dockerignore
?? applications/Agent_Red/.gtkb-app-isolation.json
?? applications/Agent_Red/harness-state/
```

5 untracked entries (4 new from sub-slice 1; 1 pre-existing). `harness-state/` was created S315 by owner; `incident-response/` is already tracked in develop.

`.vscode/` is absent from `git status` because it's gitignored (per §4).

When committed, these become 4 new tracked entries plus whatever `harness-state/` content the owner intends to track.

## §6. What sub-slice 1 did NOT do (compliance with negative-scope statements)

Cross-checking against `-005` §7.2:

| Negative-scope item | Compliance |
|---|---|
| Move any existing file | ✓ no `git mv`, no copy, no delete |
| Touch `.env.local` at any path | ✓ no `.env.local` operations |
| Modify `E:\GT-KB\.shopify*` or any GT-KB-root artifact | ✓ no GT-KB-root modifications |
| Write any DELIB, ADR, DCL, GOV, SPEC, or PB record | ✓ no formal artifact writes |
| Modify `.gitignore`, CI workflows, or any path reference | ✓ no such modifications (the gitignore limitation in §4 was discovered as a consequence, not as a deliberate choice) |
| Wire any release-gate assertion | ✓ no release-gate touches |
| Update `memory/work_list.md`, `MEMORY.md`, or any other state file | ✓ no state-file updates |

## §7. What's next

After Codex VERIFIED on this report:

- Owner direction needed before sub-slice 2 (`.env.local` migration). Per F3 of Codex `-004` and the resulting redesign in `-005` §7.1 sub-slice 2, this is owner-action-only — Prime cannot autonomously read or copy live secrets. Owner manually populates `applications/Agent_Red/.env.local`; Prime updates the registry entry and verifies key NAMES only.
- The follow-up gitignore-hygiene sub-slice (1.5) recommended in §4 is a small standalone bridge; can be filed in parallel with sub-slice 2 if owner wants the `.vscode/` track to be repo-portable before further work lands.
- Sub-slices 3–6 follow the §7.1 sequence in `-005`.

## §8. Codex review asks

1. Confirm all 6 GO conditions met (§0).
2. Confirm registry contents match disk state (§3).
3. Confirm content of each placeholder is minimal and contains no GT-KB platform content (§2).
4. Confirm the `.vscode/` gitignore limitation (§4) was correctly identified, transparently documented, and not silently worked around.
5. Confirm no negative-scope items were violated (§6).
6. **VERIFIED / NO-GO** on sub-slice 1 implementation.

## §9. References

- `bridge/application-isolation-contract-005.md` — REVISED-2 proposal (the one Codex GO'd)
- `bridge/application-isolation-contract-006.md` — Codex GO (the one this report implements)
- `applications/Agent_Red/.gtkb-app-isolation.json` — registry deliverable
- `.gitignore` lines 90–91 — source of the `.vscode/` limitation in §4

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
