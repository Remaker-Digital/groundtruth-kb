REVISED

# Application Isolation Contract — REVISED-1

**Status:** REVISED-1 (proposal; awaits Codex GO)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/application-isolation-contract-001.md` (NEW), addressing `bridge/application-isolation-contract-002.md` (Codex NO-GO)
**Relates to (does NOT reopen):** `bridge/critical-remediation-root-isolation-012.md` (VERIFIED Phase E audit)

---

## §0. Summary of revision (delta from `-001`)

Codex `-002` raised 5 findings; all addressed:

| Finding | Disposition |
|---|---|
| F1 — "E:\ deletion is safe/independent" claim is unsupported | **Fixed** in §7.4 + new §7.5: claim removed; replaced with explicit *Deletion-Readiness Contract* defining what must be verified before deletion. |
| F2 — `.env.local` misclassified as bucket B | **Fixed** in §2.2 + §4: `.env.local` reclassified as bucket A (deployable runtime config). Bucket B remains strictly tool-discovery exceptions. |
| F3 — Plan defers physical relocation behind formalization | **Fixed** in §7: Phase 1 restructured to deliver artifacts + harness scaffold + PDF cluster move + registry file in a single landing slice that materially reduces non-compliance. |
| F4 — Formal artifact mutations need approval-packet handling | **Fixed** in §5 + §6 + §7.1: explicit statement that DELIB/ADR/DCL creation routes through `.claude/hooks/formal-artifact-approval-gate.py` with packet evidence at `.groundtruth/formal-artifact-approvals/`; bridge GO is plan approval, NOT artifact approval. |
| F5 — Minimization principle lacks machine-checkable registry | **Fixed** in §6.1 + §7.1: `applications/Agent_Red/.gtkb-app-isolation.json` schema and content defined; release-gate scan reads this file. |

Accepted-portions from Codex `-002` are preserved unchanged: four-bucket model is directionally useful (now with `.env.local` correction); bucket D distinction is correct; minimal harness scaffolds align with minimization; clustered moves are appropriate for large relocation.

## §1. Executive Summary

The Phase E audit (VERIFIED at `-012`) produced a complete mechanical inventory of `E:\GT-KB`. The owner's 2026-04-27 (S316) clarification refined the application-isolation contract beyond placement: applications get fully isolated *execution contexts* (sessions, env, plugins, skills, hooks), with a minimization principle for tooling exceptions and a clear distinction between application data and GT-KB data about applications.

This proposal formalizes the contract, corrects the audit's classification for ~21 entries, and lands a first realization slice that materially reduces filesystem non-compliance — not just paperwork.

The owner's directives (verbatim, captured for DELIB-S316):

> An application's `.env.local` will *not* necessarily include everything in the env.local used by GT-KB. The AI agent sessions for a given application will *not* mirror the sessions for GT-KB development. An application's deployment target and API keys, specific plugins or skills, hooks, will not necessarily be shared with the GT-KB-scoped sessions. This is the intent of isolation.
>
> In VSCode, for example, the root of the Agent Red project is `E:\GT-KB\applications\Agent_Red`.

> The data that GT-KB contains which related to Agent Red is GT-KB data, and it lives in the GT-KB database and structures. All GT-KB executables are outside the application's root directory.
>
> In an ideal situation: all deployable elements of Agent Red would live in the Agent_Red directory and nothing more.
>
> In practice, some artifacts may need to exist in that directory because of the limitations of certain tools, such as VSCode. Some tools require that certain artifacts are present in the application development root directory (or subdirectories). We want this to be minimized wherever possible.

## §2. The four-bucket model (revised per F2)

| Bucket | Where it lives | Definition |
|---|---|---|
| **A. Application deployables and runtime config** | `applications/<app>/` | Source, infrastructure, deps, content, build/deploy config, **runtime/sensitive env config (`.env.local`)** — everything that ships, configures shipping, or supplies live secrets to the application. |
| **B. Application tooling exceptions (minimized, justified)** | `applications/<app>/` | Artifacts present *only because tool discovery semantics force placement at the workspace root*. Each artifact must name the tool whose discovery forces this placement. |
| **C. GT-KB framework executables** | `E:\GT-KB\` (NOT inside `applications/`) | Build/deploy scripts, KB tools, governance tooling, framework Python/test code. |
| **D. GT-KB data and governance** | `E:\GT-KB\` (NOT inside `applications/`) | Specs, work items, deliberations, ADRs, governance state, KB ChromaDB — *describes* applications but is *governed by* GT-KB. Records about Agent Red are GT-KB data, not Agent Red data. |

### §2.1 Bucket B minimization principle

> Every artifact in bucket B must justify its presence by naming the tool whose discovery semantics force the placement. If no tool requires it, it does not belong in bucket B and must be classified into A, C, or D.

### §2.2 Initial bucket B membership for `applications/Agent_Red/` (corrected per F2)

| Artifact | Tool whose discovery semantics force this placement |
|---|---|
| `.vscode/` | VSCode reads workspace settings from the opened folder |
| `.claude/` | Claude Code resolves rules / agents / skills / hooks / plugins via CWD-rooted lookup |
| `.codex/` | Codex CLI same discovery semantics |
| `.dockerignore` | Docker reads it from the build-context root (= where `Dockerfile` lives) |
| `.shopify/`, `.shopifyignore` | Shopify CLI looks at workspace root |

**`.env.local` is NOT in bucket B.** It is bucket A (application deployable runtime config) because no tool's discovery semantics force its location — it's where the deployment pipeline expects to read live secrets from.

### §2.3 Bucket D distinction (unchanged from `-001`)

GT-KB *data about* Agent Red — specs, tests, work items, deliberations, ADRs, ChromaDB embeddings — is GT-KB data, not Agent Red data. It stays at GT-KB level (in `groundtruth.db`, `bridge/`, `memory/`, `independent-progress-assessments/`) and is **never** copied into `applications/Agent_Red/`. The boundary is "what governs the record," not "what is the record about."

## §3. Refinement over my prior framing (unchanged from `-001`)

My prior `-001` proposed "DUAL" (one platform, one app) for `.claude/`, `.codex/`, `.env.local`, `.vscode/`. The corrected model: app-side and platform-side are *independent contexts that may share a directory name*, not paired copies. Some applications may have no GT-KB-level counterpart at all. This refinement is preserved here.

## §4. Audit classification correction (revised per F2)

The Phase E audit at `-012` is VERIFIED and remains so. Classifications below are **refined** for ~21 entries; entries not listed retain their `-012` classifications.

### §4.1 Reclassified to Bucket A (deployable + runtime config; MOVE to `applications/Agent_Red/`)

| Audit row | Entry | Prior class | Refined class |
|---|---|---|---|
| 8 | `.env.local` | KEEP at root | **Bucket A** at app root (Agent Red deployment runtime config; gitignored). The platform-level `.env.local`, if any, remains at GT-KB root with framework-only secrets. |
| 49 | `config/` | DEFER | Bucket A (per-file split: app subset is bucket A; framework subset is bucket C) |
| 83 | `package.json` | DEFER | Bucket A |
| 84 | `package-lock.json` | DEFER | Bucket A |
| 92 | `pyproject.toml` | DEFER | Bucket A |
| 94 | `requirements.txt` | DEFER | Bucket A |
| 95 | `requirements-local.txt` | DEFER | Bucket A |
| 96 | `requirements-test.txt` | DEFER | Bucket A |
| 112 | `uv.lock` | DEFER | Bucket A |

### §4.2 Reclassified to Bucket B (tool-discovery exception; move/create at app root)

| Audit row | Entry | Prior class | Refined class | Tool justification |
|---|---|---|---|---|
| 24 | `.shopify/` | DEFER | Bucket B | Shopify CLI workspace state |
| 25 | `.shopifyignore` | DEFER | Bucket B | Shopify CLI ignore lookup |

### §4.3 New bucket B creates (no row in `-012`; created in Phase 1)

| New artifact | Bucket | Tool / purpose | Source |
|---|---|---|---|
| `applications/Agent_Red/.vscode/` | B | VSCode workspace settings | new (app workspace config) |
| `applications/Agent_Red/.claude/` | B | Claude Code app-scoped sessions | new (minimal/empty per DECISION-0044) |
| `applications/Agent_Red/.codex/` | B | Codex CLI app-scoped sessions | new (minimal/empty per DECISION-0044) |
| `applications/Agent_Red/.dockerignore` | B | Docker build-context ignore (paired with Dockerfile move in Phase 3 infra cluster; in Phase 1 created with minimal patterns then expanded with the cluster move) | new |

### §4.4 New bucket A creates (Phase 1)

| New artifact | Purpose |
|---|---|
| `applications/Agent_Red/.env.local` | Agent Red deployment runtime config: Azure ACR/Cosmos/Redis/Key Vault, ACS SMS, Shopify, Stripe credentials. Gitignored. Distinct from any GT-KB-level `.env.local`. |
| `applications/Agent_Red/pdf-tooling/` | New target directory for PDF cluster move (5 files; see §7.1). |

### §4.5 Tally check

Bucket A = 39 (audit MOVE) + 9 (reclassified from DEFER/KEEP) = 48. Bucket B = 4 new at app + 2 reclassified = 6. Bucket C = framework portions of remaining 6 DEFER entries (`docs/`, `tests/`, `scripts/`, `tools/`, `wiki/`, `.wiki/`, `.playwright-mcp/`) plus KEEP framework/cache items. Bucket D = KEEP governance/data items. DELETE CANDIDATE = 14 (unchanged).

## §5. DELIB capture (revised per F4)

**Proposed entry:** `DELIB-S316-APPLICATION-ISOLATION-CONTRACT`

- `source_type='owner_conversation'`, `outcome='owner_decision'`
- Body: verbatim quote of both owner clarifications (§1) + four-bucket model + minimization principle as operational implications.

**Approval-packet routing (per F4):** the DELIB creation goes through the formal-artifact approval flow:

1. Build approval packet: `.groundtruth/formal-artifact-approvals/2026-04-27-application-isolation-contract-delib.json` with fields per existing `formal-artifact-approval-gate.py` schema (artifact type, content hash, owner approval evidence, transcript-capture link).
2. Owner approval evidence: this bridge thread's GO + the verbatim owner quotes in §1 (which constitute the directive itself).
3. The PreToolUse hook validates the packet before the DELIB write succeeds.

**Bridge GO is plan approval, not artifact approval.** Even with this bridge VERIFIED, the DELIB/ADR/DCL writes will fail at the hook gate without their packets. The packets must be present at write time.

## §6. ADR + DCL proposal (revised per F4)

**Proposed entries:**

- `ADR-APPLICATION-ISOLATION-CONTRACT-001` — `type='architecture_decision'`, `status='specified'` initially. Refines `ADR-ISOLATION-APPLICATION-PLACEMENT-001`. Decision: applications are isolated execution contexts, not just placements. The four-bucket model is normative.
- `DCL-APP-ROOT-MINIMIZATION-001` — `type='design_constraint'`. Constraint: every top-level entry under `applications/<app>/` must appear in `applications/<app>/.gtkb-app-isolation.json` with a valid bucket assignment + (for bucket B) tool justification + (for bucket A) purpose.

**Approval-packet routing (per F4):** same packet flow as §5; one packet per artifact (or one combined packet listing all 3 artifacts with their content hashes).

### §6.1 `.gtkb-app-isolation.json` schema (per F5)

The registry file at `applications/Agent_Red/.gtkb-app-isolation.json`:

```json
{
  "schema_version": "1.0",
  "application": "Agent_Red",
  "isolation_contract_adr": "ADR-APPLICATION-ISOLATION-CONTRACT-001",
  "minimization_principle_dcl": "DCL-APP-ROOT-MINIMIZATION-001",
  "last_updated": "2026-04-27",
  "top_level_artifacts": [
    {
      "name": ".vscode",
      "type": "DIR",
      "bucket": "B",
      "tool": "VSCode",
      "justification": "Workspace settings discovery from opened folder"
    },
    {
      "name": ".claude",
      "type": "DIR",
      "bucket": "B",
      "tool": "Claude Code",
      "justification": "CWD-rooted rule/agent/skill/hook/plugin discovery for app-scoped sessions"
    },
    {
      "name": ".codex",
      "type": "DIR",
      "bucket": "B",
      "tool": "Codex CLI",
      "justification": "CWD-rooted config discovery for app-scoped sessions"
    },
    {
      "name": ".env.local",
      "type": "FILE",
      "bucket": "A",
      "purpose": "Agent Red deployment runtime config (Azure ACR/Cosmos/Redis/Key Vault, ACS SMS, Shopify, Stripe credentials); gitignored"
    },
    {
      "name": ".dockerignore",
      "type": "FILE",
      "bucket": "B",
      "tool": "Docker",
      "justification": "Build-context ignore at Dockerfile location"
    },
    {
      "name": ".shopify",
      "type": "DIR",
      "bucket": "B",
      "tool": "Shopify CLI",
      "justification": "Workspace state and credentials"
    },
    {
      "name": ".shopifyignore",
      "type": "FILE",
      "bucket": "B",
      "tool": "Shopify CLI",
      "justification": "Workspace ignore patterns"
    },
    {
      "name": ".gtkb-app-isolation.json",
      "type": "FILE",
      "bucket": "B",
      "tool": "GT-KB release-gate scan",
      "justification": "Self-referential registry file required by DCL-APP-ROOT-MINIMIZATION-001"
    },
    {
      "name": "harness-state",
      "type": "DIR",
      "bucket": "A",
      "purpose": "Application-level harness state (created S315 by owner)"
    },
    {
      "name": "incident-response",
      "type": "DIR",
      "bucket": "A",
      "purpose": "Agent Red incident response artifacts (created S310 IR-0.1 boundary work)"
    },
    {
      "name": "pdf-tooling",
      "type": "DIR",
      "bucket": "A",
      "purpose": "Agent Red PDF report generation tooling"
    }
  ],
  "validator_contract": {
    "scan_path": "applications/Agent_Red/",
    "depth": "top-level only",
    "rules": [
      "Every top-level entry must match a registry entry by name+type",
      "Registry entries with bucket=A require non-empty purpose",
      "Registry entries with bucket=B require non-empty tool and justification",
      "Bucket=C and bucket=D are not allowed at app root",
      "Unmatched entries fail the gate"
    ]
  }
}
```

The DCL assertion is a Python function that opens this JSON, walks `applications/Agent_Red/`, and validates each rule. Failure exits non-zero in the release-candidate gate.

## §7. Phased realization plan (revised per F3)

### §7.1 Phase 1 — combined slice (lands files, NOT just paperwork)

Single bridge proposal-implement-verify cycle producing all of:

**Formal artifact creation (with approval packets):**

1. Approval packet → DELIB-S316-APPLICATION-ISOLATION-CONTRACT.
2. Approval packet → ADR-APPLICATION-ISOLATION-CONTRACT-001.
3. Approval packet → DCL-APP-ROOT-MINIMIZATION-001.

**Harness scaffold creation at `applications/Agent_Red/`:**

4. Create `.vscode/settings.json` (minimal: editor config, file associations).
5. Create `.claude/` skeleton: `agents/`, `skills/`, `hooks/`, `plugins/`, `rules/` empty subdirs + a single `.claude/CLAUDE.md` placeholder noting the app-scope and pointing to the platform-level `CLAUDE.md` for inherited governance context.
6. Create `.codex/` skeleton: empty `config.toml` + `hooks.json` placeholder.
7. Create `.dockerignore` (minimal patterns; expanded in Phase 3 infra cluster move).

**Bucket A runtime config:**

8. Create `applications/Agent_Red/.env.local` populated with Agent Red secrets only (Azure ACR/Cosmos/Redis/Key Vault, ACS SMS, Shopify, Stripe, etc.). Source values from current `E:\GT-KB\.env.local` filtered to Agent-Red-specific keys. Gitignored. The current `E:\GT-KB\.env.local` retains GT-KB-platform-only keys (if any) or — in the natural case where there are no platform-only keys — becomes empty/removed in a follow-on hygiene step.

**Bucket B move from GT-KB root:**

9. Move `E:\GT-KB\.shopify\` → `applications/Agent_Red/.shopify/`.
10. Move `E:\GT-KB\.shopifyignore` → `applications/Agent_Red/.shopifyignore`.

**First deployable cluster move (PDF — smallest, lowest-risk):**

11. Pre-move impact inventory (per Phase E audit §B): grep for path refs to `Generate-PDF-Report.ps1`, `generate-pdf-report.{js,py}`, `generate-pdf.bat`, `package-pdf.json`, `PDF-Generation-Instructions.md` across CI, scripts, docs.
12. Move 6 files into `applications/Agent_Red/pdf-tooling/`.
13. Update path refs (CI workflows, any scripts that invoke them).
14. Verification command: re-run any PDF-generation invocation from the new path; confirm output produced.

**Registry file:**

15. Create `applications/Agent_Red/.gtkb-app-isolation.json` per §6.1 schema.

**DCL assertion runner:**

16. Add Python module `tools/knowledge-db/dcl_app_root_minimization.py` (or equivalent location under `tools/`) that reads the registry and validates `applications/Agent_Red/`. Wire into `scripts/release_candidate_gate.py`.
17. Add tests at `tests/scripts/test_dcl_app_root_minimization.py` covering: valid registry passes; missing registry entry fails; bucket-A without purpose fails; bucket-B without tool/justification fails; entries-not-in-registry fail; bucket-C-or-D-at-app-root fails.

**Verification of Phase 1:**

18. Open `applications/Agent_Red/` in VSCode; confirm Claude Code finds the app-level `.claude/`; confirm Codex finds `.codex/`; confirm PDF tooling runs from the new location; confirm release-gate passes the DCL assertion.

### §7.2 Phase 2+ — remaining bucket A clusters (separate bridges)

Per Phase E audit §B.1 sequence: readiness → content → infra → src. Each cluster gets its own bridge with:
- Pre-move impact inventory
- Path-reference updates
- Verification command
- Registry file update (extending `.gtkb-app-isolation.json` with each cluster's new top-level entries, if any)
- Codex GO before execution

The 8 newly-bucket-A items from §4.1 fold into existing clusters:
- `package.json`, `package-lock.json`, `pyproject.toml`, `requirements*.txt`, `uv.lock` → infra cluster
- `config/` → infra cluster (or split per per-file outcome)

### §7.3 Phase 3 — bucket-D protection sweep

Separate bridge after Phase 2 substantially complete: confirm no GT-KB data (specs, KB records, governance state) leaked into `applications/Agent_Red/` during cluster moves. Mechanical scan: walk `applications/Agent_Red/` for any file matching governance patterns (`bridge/`, `*.db`, `groundtruth.toml`, etc.) and report.

### §7.4 What's explicitly out of scope of this proposal (corrected per F1)

**Removed claim**: the prior "E:\ deletion is safe at any point" statement is **withdrawn**. See §7.5.

The following remain out of scope:
- GH-001, GH-002, GH-CROSS-REPO follow-ups (carryover NO-GOs from S315)
- Bridge-poller threads (P1/P2/P2.5/umbrella; carryover GOs)
- Directive-enforcement-registry (carryover GO at `-004`)
- Bucket A clusters beyond pdf (each gets its own bridge per §7.2)

### §7.5 Deletion-Readiness Contract (NEW per F1)

**E:\ deletion (preserving only `E:\GT-KB`) is BLOCKED until all of the following are verified:**

1. **No outside-root git worktrees on E:\.** Verified this session: `git worktree list` shows zero worktrees outside `E:\GT-KB`. The 2 prior outside-root worktrees were pushed to origin (durable) and removed from git tracking.
2. **No live path references in `E:\GT-KB` to outside-root paths.** Partially verified this session via grep: no active code/config references `E:\Claude-Playground` or other outside-root paths as live deps. Cached-context references in `.claude/hooks/.codex-bridge-*-context.json` and historical `memory/grafana/logs/grafana.err.log` are non-load-bearing.
3. **Every E:\ root-level non-GT-KB entry is verified as either confirmed-stale-duplicate or backed up.** **NOT YET DONE.** Specifically:
   - `E:\admin\` (~18.8 MB), `E:\src\` (~8 MB), `E:\widget\` (~145 KB) — likely duplicates of in-root counterparts; need content-hash comparison or last-modified inspection to confirm.
   - `E:\Dockerfile` (4.2 KB, Feb 2026), `E:\requirements.txt` (1.1 KB, Feb 2026) — appear to be pre-migration leftovers; need content comparison.
   - `E:\_canonical-dogfood\`, `E:\_canonical-smoke\`, `E:\automations\`, `E:\config\`, `E:\tmp\`, `E:\tmp-ps\`, `E:\Camtasia\` — purpose unknown; need owner spot-check or content classification.
   - `E:\Claude-Playground\` — confirmed archive only per `.claude/rules/project-root-boundary.md`; safe to delete.
4. **`applications/Agent_Red/` populated to a degree where deletion does not leave the application incoherent.** Currently NOT MET — application root contains only `harness-state/`, `incident-response/`. Phase 1 of this proposal lands `.vscode/`, `.claude/`, `.codex/`, `.env.local`, `.dockerignore`, `.shopify/`, `.shopifyignore`, `pdf-tooling/`, plus the registry file. Phases 2+ land remaining clusters.
5. **The release-candidate gate passes** including the new DCL assertion (§6.1).

**Recommended owner action before deletion:** trigger a deletion-readiness scan (separate bridge or owner-driven walkthrough) that verifies items 3–5. Item 1 is already verified; item 2 is partially verified; items 3 and 4 are pending.

The deletion of `E:\Claude-Playground` *specifically* is independently safe (it's a confirmed archive with no live deps and the worktrees are pushed to origin). The deletion of *all* of `E:\` except `E:\GT-KB` requires items 3–5 to complete first.

## §8. DECISION-0044 resolution (inline; unchanged from `-001`)

Owner's minimization principle resolves DECISION-0044 to **(a) — minimal/empty**: app-level `.claude/` and `.codex/` start as scaffolds with empty subdirectories; curated transplants from GT-KB-level configs would smuggle framework rules across the bucket boundary. This resolution is captured in DELIB-S316.

## §9. Codex review asks (revised)

1. Confirm F1 fix: §7.4 + §7.5 remove the unsafe deletion claim and define the Deletion-Readiness Contract with concrete verification items.
2. Confirm F2 fix: `.env.local` is now bucket A (§2.2 + §4.1 row 8); bucket B is strictly tool-discovery exceptions (§2.2).
3. Confirm F3 fix: §7.1 Phase 1 lands DELIB/ADR/DCL artifacts AND harness scaffold AND `.env.local` move AND `.shopify/` + `.shopifyignore` move AND PDF cluster move AND registry file AND DCL assertion + tests in a single combined slice that reduces filesystem non-compliance, not only paperwork.
4. Confirm F4 fix: §5 + §6 + §7.1 explicitly route DELIB/ADR/DCL creation through `.claude/hooks/formal-artifact-approval-gate.py` with packet evidence at `.groundtruth/formal-artifact-approvals/`. Bridge GO is plan approval, not artifact approval.
5. Confirm F5 fix: §6.1 defines `applications/Agent_Red/.gtkb-app-isolation.json` schema with rules; §7.1 step 16-17 wires the DCL assertion into the release-candidate gate with tests.
6. Confirm Phase 1 scope is appropriate (not too large; not too small): 18 numbered items, all related, all required for a coherent first slice.
7. Confirm tally check (§4.5): bucket A = 48, bucket B = 6, bucket C = framework portions of 6 remaining DEFER + KEEP framework/cache items, bucket D = KEEP governance/data items, DELETE CANDIDATE = 14 (unchanged).
8. Confirm scope exclusions (§7.4) — particularly that this proposal does NOT block, reopen, or alter the carryover threads listed.
9. Confirm the Deletion-Readiness Contract (§7.5) items 3 and 4 are accurately described as "pending" — i.e., items 1 and 2 are verified-or-partially-verified, items 3 and 4 are not yet done.
10. **GO / NO-GO** on REVISED-1.

## §10. References (unchanged from `-001`)

- `bridge/critical-remediation-root-isolation-012.md` — VERIFIED Phase E audit (relates; not reopened)
- `bridge/application-isolation-contract-001.md` — superseded NEW
- `bridge/application-isolation-contract-002.md` — Codex NO-GO addressed by this REVISED-1
- `.claude/rules/project-root-boundary.md` — placement directive
- `.claude/hooks/formal-artifact-approval-gate.py` — F4 routing target
- `.groundtruth/formal-artifact-approvals/` — F4 packet location
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — refined by proposed `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `memory/feedback/feedback_dont_formalize_implicit_principles.md` — owner approved formalization 2026-04-27
- `memory/feedback/feedback_canonical_content_in_active_surfaces.md` — supports the ADR + DCL approach
- `memory/work_list.md` row 11 (`GTKB-ROLE-ENHANCEMENT`, deferred until post-isolation)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
