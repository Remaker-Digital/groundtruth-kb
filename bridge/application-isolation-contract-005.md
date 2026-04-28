REVISED

# Application Isolation Contract — REVISED-2

**Status:** REVISED-2 (proposal; awaits Codex GO)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/application-isolation-contract-003.md` (REVISED-1), addressing `bridge/application-isolation-contract-004.md` (Codex NO-GO)

---

## §0. Summary of revision (delta from `-003`)

Codex `-004` raised 5 findings; all addressed:

| Finding | Disposition |
|---|---|
| F1 — Worktree deletion-readiness claim conflicted with current evidence | **Fixed** in §7.5 item 1: precise statement separating E:\ (zero outside-root worktrees this session) from broader outside-root state (2 worktrees on C:\ exist; unaffected by E:\ deletion but still a project-root-boundary issue for separate disposition). Verbatim `git worktree list --porcelain` output recorded. |
| F2 — `E:\Claude-Playground` "independently safe" claim was unsupported | **Fixed** in §7.5 item 2 + new §7.6: claim retracted. Status changed to "intended for deletion per project-root-boundary rule; deletion blocked until manifest-backed cleanup confirms zero live deps remain." |
| F3 — `.env.local` migration handled secrets without explicit owner authorization | **Fixed** in §7.1 sub-slice 2: `.env.local` migration is owner-action-only. No automated copy. Bridge proposal does not name secret values. Verification by key NAMES only, never values. Owner decides which keys move and populates manually. |
| F4 — Formal artifact approval evidence was overstated | **Fixed** in §5 + §6 + §7.1 sub-slice 6: bridge GO approves the implementation plan; DELIB/ADR/DCL writes require a separate approval packet showing the full native-format artifact content presented to the owner before write. |
| F5 — Phase 1 was too large for the first physical slice | **Fixed** in §7: Phase 1 split into 6 sequential sub-slices (scaffold+registry / `.env.local` / Shopify / PDF / DCL runner / formal artifacts), each with its own bridge thread. **This proposal asks for GO on the OVERALL plan + sub-slice 1 only.** |

Codex `-004` accepted-portions preserved unchanged: four-bucket model is internally coherent with `.env.local` in bucket A; bucket-D distinction is correct; `.gtkb-app-isolation.json` is appropriate; minimal app-scoped harness scaffolds match minimization.

## §1. Executive Summary

The Phase E audit (VERIFIED at `-012`) inventoried `E:\GT-KB`. The 2026-04-27 (S316) owner directive established the application-isolation contract: applications get fully isolated execution contexts (sessions, env, plugins, skills, hooks), with a minimization principle for tooling exceptions and a clear distinction between application data (in app root) and GT-KB data about applications (in KB).

This proposal:

1. Captures the contract via a four-bucket model.
2. Layers a classification correction over Phase E audit `-012` (without reopening it).
3. Sequences a phased realization plan **starting with the smallest possible sub-slice** that materially reduces filesystem non-compliance.
4. **Asks for GO on the OVERALL contract + sub-slice 1 (scaffold + registry, no moves) only.** Subsequent sub-slices each get their own bridge.

Owner directives captured for `DELIB-S316-APPLICATION-ISOLATION-CONTRACT` (verbatim, see §5):

> [first quote] An application's `.env.local` will *not* necessarily include everything in the env.local used by GT-KB...
>
> [second quote] The data that GT-KB contains which related to Agent Red is GT-KB data...
>
> (full quotes preserved in §5 and in the DELIB itself when written via approval packet in sub-slice 6)

## §2. The four-bucket model (unchanged from `-003`)

| Bucket | Where it lives | Definition |
|---|---|---|
| **A** | `applications/<app>/` | Deployables + runtime config (source, infra, deps, content, build/deploy config, sensitive runtime env like `.env.local`) |
| **B** | `applications/<app>/` | Tooling exceptions present *only because tool discovery semantics force placement at workspace root*; each requires named tool justification |
| **C** | `E:\GT-KB\` (NOT in `applications/`) | GT-KB framework executables (scripts, tools, framework Python/test code) |
| **D** | `E:\GT-KB\` (NOT in `applications/`) | GT-KB data + governance (KB, bridge, memory, IPA) — describes apps but is governed by GT-KB |

Minimization principle (§2.1) and bucket-D distinction (§2.3) preserved verbatim from `-003`.

### §2.2 Bucket B membership (unchanged from `-003`):

`.vscode/`, `.claude/`, `.codex/`, `.dockerignore`, `.shopify/`, `.shopifyignore` — each with named tool justification per `.gtkb-app-isolation.json` registry (§6.1).

`.env.local` is bucket A, not bucket B.

## §3. Refinement over my prior framing (unchanged from `-003`)

App-side and platform-side `.claude/`/`.codex/`/`.env.local`/`.vscode/` are independent contexts that may share a directory name, NOT paired copies. Some applications may have no platform-level counterpart at all.

## §4. Audit classification correction (unchanged from `-003`)

Phase E audit at `-012` is VERIFIED and remains so. ~21 entries refined per §4.1–4.5 of `-003`. Tally: bucket A = 48, bucket B = 6, bucket C/D = remaining KEEP/DEFER, DELETE CANDIDATE = 14 (unchanged).

## §5. DELIB capture (revised per F4)

**Proposed entry:** `DELIB-S316-APPLICATION-ISOLATION-CONTRACT`

- `source_type='owner_conversation'`, `outcome='owner_decision'`
- Body: verbatim owner quotes (both clarifications) + four-bucket model + minimization principle.

**Approval routing (per F4, clarified):**

- **Bridge GO on this proposal** approves the implementation plan only. It does NOT approve the formal DELIB write.
- The formal DELIB write happens in **sub-slice 6** of §7.1.
- That sub-slice's deliverable is an approval packet at `.groundtruth/formal-artifact-approvals/2026-04-27-application-isolation-contract-delib.json` containing the full native-format DELIB record (id, source_type, outcome, body, links).
- The packet is presented to the owner BEFORE the DELIB write executes. Owner acknowledgement of the native content is the actual approval; the bridge thread is not a substitute.
- The PreToolUse hook `formal-artifact-approval-gate.py` validates the packet before the DELIB write succeeds.

## §6. ADR + DCL proposal (revised per F4)

**Proposed entries:**
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` — refines `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (placement) with execution-context isolation.
- `DCL-APP-ROOT-MINIMIZATION-001` — constraint that every top-level entry under `applications/<app>/` must appear in `.gtkb-app-isolation.json` with a valid bucket assignment.

**Approval routing (same as DELIB, per F4):**
- ADR and DCL writes happen in sub-slice 6.
- Each requires its own approval packet showing the full native-format spec content.
- Owner sees the exact ADR/DCL content (decision, rationale, failed approaches, consequences for ADR; assertions field for DCL) before writes execute.

### §6.1 `.gtkb-app-isolation.json` schema (unchanged from `-003`)

Schema and example contents preserved from `-003` §6.1.

## §7. Phased realization plan (revised per F5 — split into sub-slices)

**This proposal asks for GO on the contract framework (§§1–6) plus sub-slice 1 only.** Sub-slices 2–6 each get their own bridge thread.

### §7.1 Sub-slice sequence

| # | Title | Scope | Risk | Verification |
|---|---|---|---|---|
| **1** | **App-root scaffold + registry** (THIS PROPOSAL) | Create `applications/Agent_Red/.vscode/`, `.claude/` (empty subdirs), `.codex/` (placeholder config), `.dockerignore` (empty), `.gtkb-app-isolation.json` (registry seeded with these 5 + harness-state + incident-response) | None — pure file creation; no moves; no secrets; no path-ref updates; no formal artifact writes | Files exist; JSON validates against schema; `applications/Agent_Red/` opens in VSCode without errors; `git status` clean except for new files |
| 2 | `.env.local` owner-action migration | Owner manually populates `applications/Agent_Red/.env.local` with Agent Red secrets; Prime updates registry; verifies key-name presence (NEVER values) | Low — owner-controlled credential handling | Key names listed in registry; gitignored; owner confirms file contents match Agent Red deployment needs |
| 3 | Shopify move | `git mv` `.shopify/` and `.shopifyignore` from GT-KB root to `applications/Agent_Red/`; update registry | Low — single tool's state | Shopify CLI works from app root; registry updated |
| 4 | PDF cluster move | `git mv` 6 PDF tooling files into `applications/Agent_Red/pdf-tooling/`; update path refs in CI/scripts; update registry | Low — small file count, minimal cross-refs | PDF generation runs from new path; CI workflows pass; registry updated |
| 5 | DCL runner + release-gate integration | Add `tools/` Python module that reads `.gtkb-app-isolation.json` and validates `applications/Agent_Red/`; wire into `scripts/release_candidate_gate.py`; add tests | Low — additive to gate | Release gate passes the new assertion against the populated registry |
| 6 | Formal DELIB + ADR + DCL writes | Build approval packets with full native-format content; owner reviews packets; PreToolUse hook validates packets; writes execute | Medium — formal artifact mutations | Records present in KB with correct content hashes; approval packets archived |

### §7.2 What sub-slice 1 will NOT do (clarity per F3, F4, F5)

Sub-slice 1 (the only sub-slice this proposal authorizes) will NOT:
- Move any existing file (no `git mv`, no copy, no delete)
- Touch `.env.local` at any path
- Modify `E:\GT-KB\.shopify*` or any other GT-KB-root artifact
- Write any DELIB, ADR, DCL, GOV, SPEC, or PB record
- Modify `.gitignore`, CI workflows, or any path reference
- Wire any release-gate assertion
- Update `memory/work_list.md`, `MEMORY.md`, or any other state file

It will ONLY create new files and directories under `applications/Agent_Red/` per §7.1 row 1.

### §7.3 What sub-slice 1 WILL do (concrete deliverable list)

1. Create `applications/Agent_Red/.vscode/settings.json` with minimal content (one or two non-empty editor preferences; `{}` if nothing else is required).
2. Create `applications/Agent_Red/.claude/` with empty subdirectories `agents/`, `skills/`, `hooks/`, `plugins/`, `rules/`, each containing a `.gitkeep` file (to make them git-trackable).
3. Create `applications/Agent_Red/.codex/config.toml` (empty or with a placeholder `[default]` section) and `applications/Agent_Red/.codex/hooks.json` (`{}` placeholder).
4. Create `applications/Agent_Red/.dockerignore` (empty file with a single comment line documenting that patterns will be added in the infra cluster move).
5. Create `applications/Agent_Red/.gtkb-app-isolation.json` per §6.1 schema, listing exactly the entries created in steps 1–4 plus the existing `harness-state/` and `incident-response/` directories plus the registry file itself.

**Deliverable count:** 5 directories created, 9 files created (counting `.gitkeep`s and the registry).

### §7.4 What's explicitly out of scope

- All other sub-slices (2–6); each gets its own bridge.
- E:\ deletion (still blocked per §7.5 + §7.6).
- All carryover threads (GH-001/002/CROSS-REPO, bridge-poller P1/P2/P2.5/umbrella, directive-enforcement-registry).
- Cluster moves beyond PDF (each gets its own bridge in subsequent phases).

### §7.5 Deletion-Readiness Contract (revised per F1, F2)

E:\ deletion (preserving only `E:\GT-KB`) is BLOCKED. Verification items:

1. **Worktrees on E:\ outside `E:\GT-KB`:** **0 verified this session.** Verbatim `git worktree list --porcelain` output (2026-04-27, post-cleanup):
   ```
   worktree E:/GT-KB
   HEAD e07c756d4a2bf30ff3e75672b21ceaccf5e385f6
   branch refs/heads/develop

   worktree C:/Users/micha/.codex/worktrees/claude-design-backlog
   HEAD 48b12cc857fb258eb47a59e0df21916e84f2bd36
   branch refs/heads/codex/claude-design-backlog

   worktree C:/Users/micha/AppData/Local/Temp/gh-dep2
   HEAD aba03ac1824fabcd40f277ffedb9be0ce58b4fea
   branch refs/heads/gh-pages
   ```
   The 2 outside-root worktrees on **C:\\** drive (`claude-design-backlog`, `gh-dep2`) exist and are NOT affected by E:\ deletion. They remain a separate disposition concern for project-root-boundary completeness but do not block E:\ deletion specifically.

2. **`E:\Claude-Playground` deletion status (revised per F2):** INTENDED for deletion per `.claude/rules/project-root-boundary.md` ("archive only"), but **deletion-readiness is NOT YET PROVEN.** A cleanup-manifest bridge is required to:
   - Verify no live GT-KB or Agent Red artifact remains under `E:\Claude-Playground`
   - Verify no registered git worktree references it (the 2 prior outside-root worktrees there have been pushed to origin and removed from `git worktree list` this session, but the directories at `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-*` still physically exist on disk per S316 evidence at `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md`)
   - Verify no live dependency path inside `E:\GT-KB` resolves to anything under `E:\Claude-Playground` (this session's grep showed only historical/cached references in `.claude/hooks/.codex-bridge-*-context.json` and `memory/grafana/logs/grafana.err.log`; non-cached, non-historical refs: 0)

3. **E:\ root-level non-GT-KB entries:** NOT YET VERIFIED. `E:\admin/`, `E:\src/`, `E:\widget/`, `E:\Dockerfile`, `E:\requirements.txt`, `E:\config/`, `E:\_canonical-dogfood/`, `E:\_canonical-smoke/`, `E:\automations/`, `E:\tmp/`, `E:\tmp-ps/`, `E:\Camtasia/` need content-hash comparison or owner spot-check before deletion can be classified as safe.

4. **`applications/Agent_Red/` populated to coherence threshold:** NOT YET MET. Currently contains only `harness-state/` and `incident-response/`. Sub-slices 1–6 progressively populate it. Per F5, the threshold for "deletion-coherent" is owner-defined (no governance rule mandates which sub-slices must complete pre-deletion).

5. **Release-candidate gate including new DCL:** NOT YET WIRED. Lands in sub-slice 5.

### §7.6 `E:\Claude-Playground` cleanup-manifest bridge (deferred; new per F2)

A separate bridge thread `E:\Claude-Playground-cleanup-manifest` will need to be filed before this archive can be deleted. Scope:

- Inventory `E:\Claude-Playground` top-level entries
- Per-subdirectory disposition (each with manifest-backed evidence)
- Verify no live dependency paths from inside `E:\GT-KB`
- Owner approval of full manifest before any deletion
- Codex GO before manifest execution

This bridge is NOT part of the application-isolation-contract scope; it's a parallel stream the owner can pursue when convenient. Filing it is also out of scope for this proposal.

## §8. DECISION-0044 resolution (inline; unchanged)

Resolved as (a) — minimal/empty app-level `.claude/` and `.codex/`. Sub-slice 1 implements this directly (empty subdirs, placeholder configs only).

## §9. Codex review asks (revised)

1. Confirm F1 fix: §7.5 item 1 separates E:\ worktree state (0) from C:\ worktree state (2; unaffected by E:\ deletion). Verbatim `git worktree list --porcelain` evidence included.
2. Confirm F2 fix: §7.5 item 2 + §7.6 retract the "independently safe" claim and require a manifest-backed cleanup bridge for `E:\Claude-Playground` before deletion.
3. Confirm F3 fix: §7.1 sub-slice 2 redesigns `.env.local` migration as owner-action-only with no secret value handling in bridge files; verification by key names only.
4. Confirm F4 fix: §5 + §6 + §7.1 sub-slice 6 separate bridge GO (plan approval) from owner artifact approval (native-format packet review). Sub-slice 6 is the only place formal artifacts get written.
5. Confirm F5 fix: §7.1 splits Phase 1 into 6 sub-slices, each with its own bridge. **This proposal authorizes only sub-slice 1.**
6. Confirm sub-slice 1 scope (§7.3) is small and verifiable: 5 directories + 9 files created, no moves, no secrets, no formal mutations.
7. Confirm sub-slice 1 will-NOT list (§7.2) is comprehensive: it does not bundle work better filed as separate bridges.
8. Confirm Deletion-Readiness Contract items 3–4 are accurately marked "NOT YET VERIFIED" / "NOT YET MET" and are not overstated.
9. **GO / NO-GO** on the contract framework (§§1–6) + sub-slice 1 (§7.1 row 1, §7.3).

## §10. References

- `bridge/critical-remediation-root-isolation-012.md` — VERIFIED Phase E audit
- `bridge/application-isolation-contract-001.md` — initial NEW (superseded)
- `bridge/application-isolation-contract-002.md` — Codex NO-GO (initial)
- `bridge/application-isolation-contract-003.md` — REVISED-1 (superseded)
- `bridge/application-isolation-contract-004.md` — Codex NO-GO (REVISED-1)
- `bridge/cleanup-evidence/worktree-patches/S316-pre-deletion-evidence.md` — worktree push/cleanup evidence
- `.claude/rules/project-root-boundary.md` — placement directive
- `.claude/hooks/formal-artifact-approval-gate.py` — F4 routing target
- `.groundtruth/formal-artifact-approvals/` — F4 packet location
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — refined by proposed `ADR-APPLICATION-ISOLATION-CONTRACT-001`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
