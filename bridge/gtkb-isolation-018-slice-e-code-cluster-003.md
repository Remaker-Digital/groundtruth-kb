REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E: Code Cluster (Scoping Proposal REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-07 (S334)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e-code-cluster-002.md` (4 mechanical accuracy fixes; decomposition unchanged).
**Predecessors:** `-001` (initial scoping proposal), `-002` (Codex NO-GO).
**Revision basis:** F1 registry coverage, F2 file-count math, F3 scripts/ inventory omissions, F4 Option-A testpaths consequence.

---

## Codex Findings Addressed (from -002)

| Finding | Disposition |
|---|---|
| **F1** — E.1 registry plan listed 4 entries (`src`, `tests`, `admin`, `widget`) but E.1 also moves `branding/` and `config/stripe_product_ids.json`. Registry validator requires every top-level entry to match a registry entry. | **Fixed.** E.1 registry plan now lists **6 new Bucket-A entries**: `src`, `tests`, `admin`, `widget`, `branding`, `config`. Stripe destination is `applications/Agent_Red/config/stripe_product_ids.json` requiring a `config` Bucket-A entry. See revised E.1 section below. |
| **F2** — Total file count `1,999` doesn't match arithmetic: `305+731+361+51+484+67+1 = 2,000`; live `unique_total=2000` confirms. | **Fixed.** Total updated to **2,000** throughout. |
| **F3** — scripts/ inventory missed 2 tracked subdirs: `scripts/integrity-results/` (1 file) and `scripts/setup/` (1 file). | **Fixed.** Both added to the E.2 disposition table with rationale: `scripts/integrity-results/scan-20260308-222949.json` is a platform scan-output dump (DEFER to 18.I review like `benchmark-results/`); `scripts/setup/initialize_cosmos_containers.py` is Agent Red Cosmos DB setup (MIGRATES to applications/Agent_Red/scripts/setup/). |
| **F4** — Option A's pyproject.toml `testpaths` consequence unaddressed. Under Option A (subdir-level split), `testpaths` needs to discover BOTH root `tests/` (platform tests) AND `applications/Agent_Red/tests/` (Agent Red tests) for the entire migration window until 18.J. Under Option B, single `testpaths` works post-rewrite. | **Fixed.** OQ-E3 section now explicitly enumerates the testpaths consequence as a trade-off factor. The SCOPING proposal does NOT pre-decide OQ-E3 (that's E.3's job via AUQ), but the proposal now equips that AUQ with the testpaths consequence framing. |

---

## Carry-Forward Statement

All sections of `-001` carry forward UNCHANGED EXCEPT the four corrections detailed below. The 3-way decomposition (E.1 + E.2 + E.3), sequencing, risk framework, acceptance criteria for the scoping proposal, and provenance are all preserved from `-001`.

Specifically carried forward unchanged:
- Specification Links (full set)
- Owner Decisions / Input
- Background
- Goal (scoping-level)
- Sub-Sub-Slice Plan structure (E.1, E.2, E.3 boundaries)
- Sequencing Across Sub-Sub-Slices
- Risk / Rollback program-level framework
- Acceptance Criteria for the scoping proposal
- Out of Scope
- Project Root Boundary Compliance
- Pre-Filing Preflight Subsection
- Provenance

The four corrections below replace the corresponding portions of `-001`.

---

## Specification Links

Carried forward from `-001`. Re-cited here for preflight matching:

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)

Cross-cutting advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE)
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO)
- `bridge/gtkb-isolation-018-agent-red-file-migration-009.md` (inventory re-scope GO)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED; pattern precedent)
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED; pattern precedent)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-002.md` (Codex NO-GO triggering this revision)
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "18.E structure — single atomic slice or sub-split into reviewable sub-sub-slices?" (S334, 2026-05-07) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" | This proposal IS the scoping deliverable. |
| "18.E scoping NO-GO at -002 — file the corrected -003 now or pause?" (S334, 2026-05-07) | "18.E next move" | "File -003 corrections now" | Authorizes this REVISED-1 with the 4 mechanical fixes. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation as release-gating; only blocking technical dependencies authorize deferral. | Authorizes 18.E program. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Continues to authorize in-flight pre-migration state. |

## F1 Fix — Revised E.1 Registry Plan

**E.1 — Code Cluster Atomic Move** moves 6 clusters; the registry will receive **6 new Bucket-A entries**:

| Registry entry | Cluster destination | Files | Bucket-A purpose |
|---|---|---:|---|
| `src` | `applications/Agent_Red/src/` | 305 | Agent Red Python application code |
| `tests` | `applications/Agent_Red/tests/` | (E.3-decided subset) | Agent Red test suite (excluding platform-test files per E.3 disposition) |
| `admin` | `applications/Agent_Red/admin/` | 361 | Agent Red admin Vite + React + TypeScript app |
| `widget` | `applications/Agent_Red/widget/` | 51 | Agent Red chat widget (Vite + Preact + TypeScript) |
| `branding` | `applications/Agent_Red/branding/` | 67 | Agent Red product branding (deferred from 18.D per parents[2] dependency) |
| `config` | `applications/Agent_Red/config/` | 1 (just `stripe_product_ids.json`) | Agent Red Stripe pricing config (deferred from 18.D per parents[3] dependency in `src/integrations/stripe_catalog.py:26-27`) |

The `config` registry entry covers only the Stripe pricing config; the GT-KB platform configs in `config/agent-control/` and `config/governance/` STAY at GT-KB root per umbrella `-009`.

## F2 Fix — Corrected Total File Count

Total tracked files in 18.E program: **2,000** (corrected from `-001`'s misstated 1,999).

Arithmetic: `305 src + 731 tests + 361 admin + 51 widget + 484 scripts + 67 branding + 1 stripe_config = 2,000`.

Codex `-002` Evidence Reviewed section confirms `unique_total=2000`.

## F3 Fix — E.2 Scripts Disposition Table (Complete)

`scripts/` total: **484 tracked files** in 14 subdirs + 220 top-level files. (Corrected from `-001`'s table which showed 12 subdirs and missed 2.)

| Subdir | Files | Disposition |
|---|--:|---|
| `scripts/archive/` | 109 | DEFER to 18.I review |
| `scripts/pre-flight-results/` | 65 | STAYS (platform — preflight-output dump) |
| `scripts/rehearse/` | 15 | STAYS (platform — rehearsal scaffolding) |
| `scripts/upgrade-results/` | 14 | STAYS (platform — `gt project upgrade --dry-run` output) |
| `scripts/gtkb_dashboard/` | 10 | STAYS (platform — dashboard tooling) |
| `scripts/deploy/` | 10 | SPLIT per-file in E.2 |
| `scripts/_report_charts_ar/` | 10 | MIGRATES (Agent Red — "ar" suffix) |
| `scripts/_report_charts/` | 9 | STAYS (platform — generic chart-generation library) |
| `scripts/guardrails/` | 8 | STAYS (platform) |
| `scripts/benchmark-results/` | 7 | DEFER to 18.I review (output dump) |
| `scripts/lib/` | 3 | STAYS (platform — shared script lib) |
| `scripts/stripe/` | 2 | MIGRATES (Agent Red — Stripe is Agent Red payment processor) |
| **`scripts/integrity-results/`** | **1** (`scan-20260308-222949.json`) | **DEFER to 18.I review** (platform scan-output dump; same pattern as `benchmark-results/` and `pre-flight-results/`) |
| **`scripts/setup/`** | **1** (`initialize_cosmos_containers.py`) | **MIGRATES** (Agent Red — Azure Cosmos DB initializer for Agent Red multi-tenant data store) |
| `scripts/<top-level scripts>` | 220 | SPLIT per-file at E.2 execution per heuristic + per-file judgment |

Subdir total: 264. Top-level total: 220. Sum: 484 ✓.

## F4 Fix — OQ-E3 testpaths Consequence (Explicit)

**OQ-E3:** Platform-test disposition — Option A (subdir-level split) vs Option B (update parents[N] in platform-test files).

**Option A — Split at the test-subdir level:**
- `tests/hooks/` (13 files) and platform-test subset of `tests/scripts/` stay at root
- Rest of `tests/` (~700 files) migrates to `applications/Agent_Red/tests/`
- Tests at root keep `parents[2]` resolution → repo root → `.claude/hooks/` works
- Tests at `applications/Agent_Red/tests/` get `parents[2]` resolution → `applications/Agent_Red/` → `applications/Agent_Red/admin/` (etc.) works
- **Consequence (per Codex F4):** `pyproject.toml`'s `testpaths` field needs to handle BOTH `tests/` AND `applications/Agent_Red/tests/` for the entire migration window (until 18.J repo separation, possibly indefinitely if platform tests permanently stay at root). Either:
  - Set `testpaths = ["tests", "applications/Agent_Red/tests"]` (dual discovery)
  - OR run pytest twice with different invocations (one for platform, one for app)
  - OR use a custom pytest collection plugin
- **Pro:** Test files remain unchanged (zero source-code edits to test files)
- **Con:** Persistent dual-discovery complexity in pyproject.toml + CI

**Option B — Update parents[N] in platform-test files:**
- All ~731 tests/ files migrate to `applications/Agent_Red/tests/`
- Platform-test files (estimated ~13-25 files) have `parents[2]` rewritten to `parents[3]` to walk up one extra level past `applications/Agent_Red/` to repo root
- Single `testpaths = ["applications/Agent_Red/tests"]` works post-migration
- **Consequence:** ~13-25 platform-test files require one-shot mechanical edits during E.1 (or prior to E.1)
- **Pro:** Clean single testpaths config; no persistent discovery complexity
- **Con:** Requires source-code edits to platform-test files; if any platform-test is later moved or its location-resolution depth changes, the parents[3] would need re-adjustment

**Trade-off summary:** Option A defers code edits but introduces persistent config complexity. Option B does one-shot code edits and ends with clean config.

This SCOPING proposal does NOT pre-decide. E.3 surfaces this as AUQ to the owner; E.1's tests/ scope and pyproject.toml plan depend on the chosen option.

## Carry-Forward — Sub-Sub-Slice E.1 Section (Updated File Counts Only)

E.1's file counts are updated only in this REVISED-1:

**File counts (live probe 2026-05-07):**
- src/ — 305 files
- tests/ — 731 files minus E.3-decided platform-test set (estimated ~13-25 files stay under Option A; 0 stay under Option B)
- admin/ — 361 files
- widget/ — 51 files
- branding/ — 67 files (deferred from 18.D)
- config/stripe_product_ids.json — 1 file (deferred from 18.D)
- pyproject.toml updates — 4 fields (testpaths, source, known-first-party, paths_to_mutate)

**Total estimated under Option B: ~1,516 files moved + 1 file edited.**
**Total estimated under Option A: ~1,491-1,503 files moved + 1 file edited + 0 source edits to platform-test files.**

All other E.1 content (risk factors, pre-move probe requirements, test plan, sequencing, estimated bridge cycles) carries forward from `-001` unchanged.

## Carry-Forward — Sub-Sub-Slice E.2 Section (with F3 Updates)

E.2's disposition table is the corrected one above (F3 Fix). All other E.2 content carries forward from `-001` unchanged.

## Carry-Forward — Sub-Sub-Slice E.3 Section (with F4 Updates)

E.3's Open Question OQ-E3 framing now includes the testpaths consequence (F4 Fix above). All other E.3 content carries forward from `-001` unchanged.

## Acceptance Criteria

This scoping proposal is accepted when:
- [ ] Codex GO on this `-003`
- [ ] 3-way decomposition (E.1 + E.2 + E.3) accepted
- [ ] Sequencing (this → E.3 → E.1 → E.2) accepted
- [ ] Risk identification + mitigation framework accepted
- [ ] Corrected E.1 registry plan (6 entries) accepted
- [ ] Corrected total file count (2,000) accepted
- [ ] Corrected E.2 disposition table (14 subdirs + 220 top-level) accepted
- [ ] OQ-E3 testpaths-consequence framing accepted as input to E.3 AUQ

This scoping proposal does NOT VERIFY the underlying migration. Each sub-sub-slice has its own VERIFIED gate.

## Pre-Filing Preflight Subsection

This `-003` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e-code-cluster` after INDEX update. Expected: `preflight_passed: true`.

## Provenance (additions to `-001`)

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-isolation-018-slice-e-code-cluster-002.md` (F1 registry, F2 count, F3 scripts inventory, F4 testpaths consequence) |
| F3 evidence | `git ls-files scripts/integrity-results/` returns `scripts/integrity-results/scan-20260308-222949.json`; `git ls-files scripts/setup/` returns `scripts/setup/initialize_cosmos_containers.py` |
| Owner directive (S334 AUQ) | "18.E next move" → "File -003 corrections now" |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
