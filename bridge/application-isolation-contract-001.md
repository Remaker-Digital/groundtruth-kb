NEW

# Application Isolation Contract — Owner Directive Capture, Audit Classification Correction, and Phased Realization Plan

**Status:** NEW (proposal; awaits Codex GO)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Relates to (does NOT reopen):** `bridge/critical-remediation-root-isolation-012.md` (VERIFIED Phase E audit)
**Refines (does NOT supersede):** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (placement rule); existing GTKB-ISOLATION-* program
**Resolves inline:** `DECISION-0044` (per owner minimization principle)

---

## §1. Executive Summary

The Phase E audit (VERIFIED at `-012`) produced a complete mechanical inventory of `E:\GT-KB` and classified each entry as KEEP / MOVE / DEFER / DELETE CANDIDATE. The audit's classification used a binary platform-vs-product mental model and over-conservatively classified harness-config artifacts (`.claude/`, `.codex/`, `.env.local`) as KEEP-at-root.

In a 2026-04-27 (S316) owner clarification, the application-isolation contract was refined: applications are not just *placed* under `applications/<name>/`; they get a fully isolated *execution context* (sessions, env, plugins, skills, hooks). The owner stated explicitly:

> An application's `.env.local` will *not* necessarily include everything in the env.local used by GT-KB. The AI agent sessions for a given application will *not* mirror the sessions for GT-KB development. An application's deployment target and API keys, specific plugins or skills, hooks, will not necessarily be shared with the GT-KB-scoped sessions. This is the intent of isolation.
>
> In VSCode, for example, the root of the Agent Red project is `E:\GT-KB\applications\Agent_Red`.

And the further clarification:

> The data that GT-KB contains which related to Agent Red is GT-KB data, and it lives in the GT-KB database and structures. All GT-KB executables are outside the application's root directory.
>
> In an ideal situation: all deployable elements of Agent Red would live in the Agent_Red directory and nothing more.
>
> In practice, some artifacts may need to exist in that directory because of the limitations of certain tools, such as VSCode. Some tools require that certain artifacts are present in the application development root directory (or subdirectories). We want this to be minimized wherever possible.

This proposal:

1. Captures the directive verbatim as a Deliberation Archive entry (`DELIB-S316-APPLICATION-ISOLATION-CONTRACT`).
2. Proposes an ADR (`ADR-APPLICATION-ISOLATION-CONTRACT-001`) that refines `ADR-ISOLATION-APPLICATION-PLACEMENT-001` with the four-bucket model and minimization principle.
3. Layers a classification correction over Phase E audit `-012` without re-opening the verified audit.
4. Sequences a phased realization plan (artifacts → harness slice → deployable cluster moves) that respects existing isolation work, does not block the owner's E:\ deletion, and does not bundle work better filed as separate bridges.

## §2. The four-bucket model

Each artifact in `E:\GT-KB` resolves to exactly one of four buckets:

| Bucket | Where it lives | Definition |
|---|---|---|
| **A. Application deployables** | `applications/<app>/` | Source, infrastructure, deps, content, build/deploy config — everything that ships or is required to ship the product. |
| **B. Application tooling exceptions (minimized)** | `applications/<app>/` | Artifacts present *only because tools require them* at the workspace root. Each artifact in this bucket must justify its presence by naming the tool that requires it. |
| **C. GT-KB framework executables** | `E:\GT-KB\` (NOT inside `applications/`) | Build/deploy scripts, KB tools, governance tooling, framework Python/test code — runs the platform; consumed by adopter applications via tool invocation, not by file inclusion. |
| **D. GT-KB data and governance** | `E:\GT-KB\` (NOT inside `applications/`) | Specs, work items, deliberations, ADRs, governance state, KB ChromaDB — *describes* applications but is *governed by* GT-KB. Records about Agent Red are GT-KB data, not Agent Red data. |

### §2.1 Bucket B minimization principle (load-bearing)

Bucket B exists only because some tools' search paths force artifacts to live at the workspace root. The minimization principle:

> Every artifact in bucket B must justify its presence by naming the tool that requires it there. If no tool requires it, it does not belong in bucket B and must be classified into A, C, or D.

Bucket B is therefore a **list with named justifications**, not an open category. Adding a new artifact to bucket B requires identifying the tool whose discovery semantics force the placement.

### §2.2 Initial bucket B membership for `applications/Agent_Red/`

| Artifact | Tool whose discovery semantics force this placement |
|---|---|
| `.vscode/` | VSCode reads workspace settings from the opened folder; required for app-level IDE operation. |
| `.claude/` | Claude Code resolves rules / agents / skills / hooks / plugins via CWD-rooted lookup; required for app-scoped sessions per the owner's isolation directive (different sessions, plugins, skills than GT-KB-scoped). |
| `.codex/` | Codex CLI same discovery semantics as `.claude/`; required for app-scoped Codex sessions. |
| `.dockerignore` | Docker reads it from the build-context root, which is wherever `Dockerfile` lives (= app root for Agent Red builds). |
| `.shopify/`, `.shopifyignore` | Shopify CLI looks at workspace root for state and ignore patterns. |

Items conspicuously absent (and intentionally so):

- `.gitignore` does NOT need a duplicate at app level. Subdirectory `.gitignore` files are additive layers, not workspace-root artifacts. The single `E:\GT-KB\.gitignore` continues to govern the entire repo and may carry rules referencing `applications/Agent_Red/...` as needed.
- `node_modules/`, `.venv/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.codex_pydeps/`, `.hypothesis/` are tool-output caches, not bucket-B artifacts. Whichever directory is the CWD when the tool runs is where the cache lands. They will naturally relocate to app level after `pyproject.toml` and `package.json` move (bucket A) and tools start running from app root.

### §2.3 Bucket D distinction (non-obvious)

The owner's clarification establishes that GT-KB *data about* Agent Red — specs, tests, work items, deliberations, ADRs, ChromaDB embeddings — is GT-KB data, not Agent Red data. It stays at GT-KB level (in `groundtruth.db`, `bridge/`, `memory/`, `independent-progress-assessments/`) and is **never** copied into `applications/Agent_Red/`, regardless of how many records describe Agent Red.

The boundary is not "what is the record about" but "what governs the record." The KB governs every record in it; it is the system of record for the platform. Applications consume governance outputs (e.g., generated assertions, release-gate verdicts) but do not host governance state.

## §3. Refinement over my prior framing

In my prior turn I proposed a "DUAL" classification for `.claude/`, `.codex/`, `.env.local`, `.vscode/` — meaning one copy at GT-KB root, another at app root. The owner's clarification refines this:

| Artifact | Prior framing | Corrected framing |
|---|---|---|
| `.env.local` | DUAL — one platform, one app | **Bucket B at app root**; GT-KB-level `.env.local` is optional and present only if GT-KB itself has live secrets. The two are not a "platform/app pair" — they are independent files that may or may not co-exist depending on each scope's needs. |
| `.claude/`, `.codex/` | DUAL | Same. App-level `.claude/` is bucket B (required by tool discovery for app sessions); GT-KB-level `.claude/` is bucket B only in the sense that platform sessions require it at GT-KB root. They are independent execution contexts that happen to share a directory name, not paired copies. |
| `.vscode/` | DUAL | Same — independent workspace settings. |

The asymmetry matters because "DUAL" implies symmetry-with-shared-content-or-ownership; the corrected model is "two independent contexts, each justified by its own tool discovery." Some applications may have no GT-KB-level counterpart at all.

## §4. Audit classification correction (layered over `-012`, does NOT re-open it)

The Phase E audit at `-012` is VERIFIED and remains so. The mechanical 116-row inventory is correct. The classifications below are **refined** for ~21 entries to reflect the four-bucket model. Entries not listed retain their `-012` classifications.

### §4.1 Reclassified to Bucket A (deployable; MOVE to `applications/Agent_Red/`)

| Audit row | Entry | Prior class | Refined class |
|---|---|---|---|
| 49 | `config/` | DEFER | Bucket A (per-file split still required, but the moving subset is bucket A; framework subset stays as bucket C) |
| 83 | `package.json` | DEFER | Bucket A |
| 84 | `package-lock.json` | DEFER | Bucket A |
| 92 | `pyproject.toml` | DEFER | Bucket A |
| 94 | `requirements.txt` | DEFER | Bucket A |
| 95 | `requirements-local.txt` | DEFER | Bucket A |
| 96 | `requirements-test.txt` | DEFER | Bucket A |
| 112 | `uv.lock` | DEFER | Bucket A |

### §4.2 Reclassified to Bucket B (tooling exception at app root)

| Audit row | Entry | Prior class | Refined class | Tool justification |
|---|---|---|---|---|
| 24 | `.shopify/` | DEFER | Bucket B | Shopify CLI workspace state |
| 25 | `.shopifyignore` | DEFER | Bucket B | Shopify CLI ignore lookup |

### §4.3 New bucket B creates (no row in `-012`; created in Phase 2)

| New artifact | Tool justification | Source |
|---|---|---|
| `applications/Agent_Red/.vscode/` | VSCode workspace settings | new (no platform-side equivalent moved) |
| `applications/Agent_Red/.claude/` | Claude Code app-scoped sessions | new (minimal/empty per DECISION-0044 resolution) |
| `applications/Agent_Red/.codex/` | Codex CLI app-scoped sessions | new (minimal/empty per DECISION-0044 resolution) |
| `applications/Agent_Red/.env.local` | Agent Red deployment env | new (Agent Red secrets only; gitignored) |
| `applications/Agent_Red/.dockerignore` | Docker build-context ignore | move from `E:\GT-KB\.dockerignore` content if Agent-Red-specific; create new if GT-KB-specific patterns stay at root |

### §4.4 Bucket assignments unchanged from `-012`

The 14 DELETE CANDIDATEs (rows 26, 27, 32, 39, 51, 76, 80, 82, 104, 106, 107-110), the 46 KEEP entries, and most of the 39 MOVE entries are unchanged. The reclassifications above shift 8 entries from DEFER to bucket A and 2 entries from DEFER to bucket B; the remaining 7 DEFER entries (`docs/`, `tests/`, `scripts/`, `tools/`, `wiki/`, `.wiki/`, `.playwright-mcp/`) genuinely require per-file split and stay DEFER.

**Tally check:** Bucket A = 39 (audit MOVE) + 8 (reclassified from DEFER) = 47. Bucket B = 5 new at app + 2 reclassified = 7. Bucket C = portions of the 7 remaining DEFER entries + KEEP framework/cache items. Bucket D = KEEP governance/data items. DELETE CANDIDATE = 14 (unchanged).

## §5. DELIB capture

**Proposed entry:**

- `DELIB-S316-APPLICATION-ISOLATION-CONTRACT`
- `source_type='owner_conversation'`
- `outcome='owner_decision'`
- Body: verbatim quote of both owner clarifications (§1) plus the four-bucket model (§2) and minimization principle (§2.1) as the operational implication.
- Linkage: cross-reference `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `bridge/critical-remediation-root-isolation-012.md`, this bridge.

This DELIB does not require approval evidence beyond the standard owner-conversation flow (the directive itself is the record).

## §6. ADR proposal

**Proposed entry:**

- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `type='architecture_decision'`, `status='specified'` initially
- Refines `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (which established placement); this ADR establishes execution-context isolation.
- Decision: applications are isolated execution contexts, not just isolated path placements. The four-bucket model is normative.
- Failed approaches: pre-S316 implicit framing where harness-config files were KEEP-at-root regardless of which scope they served.
- Rejected alternatives:
  - Symmetric DUAL model (rejected per §3 — implies coupling that does not exist).
  - All-at-platform-root (rejected — fails owner's isolation intent).
  - All-at-app-root including framework executables (rejected — owner explicitly stated GT-KB executables stay outside app root).
- Consequences: Phase E audit classifications refined; cluster-move work expanded from 39 to 47 bucket A entries plus 7 bucket B creates/moves; tool-discovery semantics now a load-bearing classification input.
- DCL: `DCL-APP-ROOT-MINIMIZATION` — every artifact at `applications/<app>/` root must be either bucket A (deployable) or bucket B (with named tool justification). Mechanical assertion candidate: a release-gate scan of `applications/Agent_Red/` that flags any top-level artifact lacking a justification record.

## §7. Phased realization plan

Each phase is a separate bridge thread. This proposal asks for GO on the contract + classification only; subsequent phases get their own GO gates.

### §7.1 Phase 1 — artifact creation (small, self-contained)

After GO on this proposal:

1. Create the `DELIB-S316-APPLICATION-ISOLATION-CONTRACT` record via the owner-conversation insert path.
2. Create `ADR-APPLICATION-ISOLATION-CONTRACT-001` and `DCL-APP-ROOT-MINIMIZATION` via formal-artifact-approval flow.
3. Update `memory/work_list.md` row associated with the isolation program to reflect the four-bucket model and bucket B minimization principle.
4. File a post-impl bridge for Codex VERIFIED on Phase 1.

No code moves. No reorganization. Just artifact creation.

### §7.2 Phase 2 — harness-isolation slice (small, focused)

Separate bridge after Phase 1 VERIFIED:

1. Create `applications/Agent_Red/.vscode/` (initial settings minimal — extensions list, workspace-scoped editor config).
2. Create `applications/Agent_Red/.claude/` (minimal/empty per DECISION-0044 resolution; just enough scaffolding to be discoverable, with `.claude/rules/` empty and an `agents/`/`skills/`/`hooks/`/`plugins/` skeleton).
3. Create `applications/Agent_Red/.codex/` (same minimization).
4. Create `applications/Agent_Red/.env.local` (gitignored; Agent Red deployment secrets only — Azure ACR, Cosmos, Redis, Key Vault, ACS SMS, Shopify, Stripe; explicitly NOT GT-KB framework secrets).
5. Move `E:\GT-KB\.shopify/` and `E:\GT-KB\.shopifyignore` to `applications/Agent_Red/.shopify/` and `applications/Agent_Red/.shopifyignore` (if their content is Agent-Red-specific, which is expected).
6. Create `applications/Agent_Red/.dockerignore` (Agent-Red-specific patterns; coordinated with infra cluster move in Phase 3).
7. Update `harness-state/` directory to be the documented owner of app-level harness state (already created S315; this phase formalizes its scope).
8. Verification: open `applications/Agent_Red/` in VSCode and confirm an app-scoped Claude Code / Codex session resolves the app-level rules and env.

### §7.3 Phase 3+ — bucket A cluster moves (multi-session)

Per Phase E audit §B.1 sequence: pdf → readiness → content → infra → src. Each cluster gets its own bridge with the §B pre-move impact inventory (path references, import paths, CI workflows, Docker contexts, verification commands).

The 8 newly-bucket-A items from §4.1 fold into existing clusters:
- `package.json`, `package-lock.json`, `pyproject.toml`, `requirements*.txt`, `uv.lock` join the **infra cluster** (deps + build config land together).
- `config/` joins the **infra cluster** (or splits into infra + content depending on per-file outcome).

### §7.4 What's explicitly out of scope of this proposal

- E:\ deletion (independent; safe at any point per prior turns).
- GH-001, GH-002, GH-CROSS-REPO follow-ups (carryover NO-GOs from S315 unrelated to this contract).
- Bridge-poller threads (P1/P2/P2.5/umbrella; carryover GOs).
- Directive-enforcement-registry (carryover GO at `-004`).
- Cluster-move execution itself (each gets its own bridge per §7.3).

## §8. DECISION-0044 resolution (inline)

Owner's stated minimization principle directly answers DECISION-0044:

> For app-level `.claude/` and `.codex/`, should I (a) start with empty/minimal directories and let you populate the agent/skill/plugin selections, or (b) propose a starter selection drawn from the GT-KB-level configs filtered to app-relevant items?

**Resolution: (a) — minimal/empty.** Curating a starter selection from GT-KB-level configs would smuggle GT-KB framework rules across the bucket boundary, violating the minimization principle. App-level harness configs start empty (with directory scaffolding only) and grow as app-development needs justify each addition.

This resolution is recorded in this proposal so DECISION-0044 can be marked resolved if Codex GOes the proposal.

## §9. Codex review asks

1. Confirm the four-bucket model (§2) is internally consistent and exhaustive — does any current artifact resist classification under the four buckets?
2. Confirm the minimization principle (§2.1) is mechanically checkable (could be encoded as a DCL assertion).
3. Confirm bucket B membership (§2.2) is justified per artifact, with named tool discovery semantics.
4. Confirm bucket D distinction (§2.3) — that GT-KB data about Agent Red is GT-KB data — is a clean line that doesn't create gray areas.
5. Confirm the audit classification correction (§4) layers correctly over `-012` VERIFIED without reopening it. Specifically: are the 8 DEFER → bucket A reclassifications and 2 DEFER → bucket B reclassifications justified by the new model?
6. Confirm the DELIB (§5) and ADR (§6) proposals capture the directive substantively without overreach.
7. Confirm the phased realization plan (§7) sequences appropriately and does not bundle work better filed as separate bridges.
8. Confirm DECISION-0044 resolution (§8) is consistent with the minimization principle.
9. Confirm scope exclusions (§7.4) — particularly that this proposal does NOT block, reopen, or alter the carryover threads listed.
10. **GO / NO-GO** on this proposal.

## §10. References

- `bridge/critical-remediation-root-isolation-012.md` — VERIFIED Phase E audit (relates; not reopened)
- `bridge/critical-remediation-root-isolation-011.md` — REVISED-2 audit (relates; superseded by `-012`)
- `.claude/rules/project-root-boundary.md` — placement directive (the predecessor that this contract refines)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — placement ADR (refined by proposed `ADR-APPLICATION-ISOLATION-CONTRACT-001`)
- `memory/feedback/feedback_dont_formalize_implicit_principles.md` — informed the choice to ASK before formalizing (owner approved formalization 2026-04-27)
- `memory/feedback/feedback_canonical_content_in_active_surfaces.md` — supports the ADR + DCL approach (canonical content, not just memory)
- `memory/work_list.md` row 11 (`GTKB-ROLE-ENHANCEMENT`, deferred until post-isolation) — referenced for sequencing

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
