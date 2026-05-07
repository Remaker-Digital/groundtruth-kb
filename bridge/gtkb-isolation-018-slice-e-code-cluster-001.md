NEW

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E: Code Cluster (Scoping Proposal — Sub-Sub-Slice Decomposition)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-07 (S334)
**Type:** SCOPING proposal that decomposes 18.E into 3 sub-sub-slices (E.1, E.2, E.3) per S334 owner AUQ "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)". Mirrors the umbrella → 18.A → 18.B/C/D pattern at smaller scale. No file moves performed by this proposal — sub-sub-slices are independent bridge threads filed after this scoping is GO'd.
**Predecessor:** umbrella `bridge/gtkb-isolation-018-agent-red-file-migration-009.md` (GO; inventory re-scope) — defined 18.E as a single cluster; this proposal sub-divides it.
**Risk tier:** Critical (1,999 tracked files; 163 `parents[N]` usages; touches Python imports, JS module resolution, Agent Red CI; mid-migration broken-state risk extreme without atomic move within E.1).

---

## Specification Links

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this scoping proposal lives at `bridge/gtkb-isolation-018-slice-e-code-cluster-001.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: per-sub-sub-slice bridge threads will carry their own Test Plans; this scoping proposal's tests are limited to T-bridge-1 + T-spec-1 + T-spec-2 since no implementation occurs in this scope.

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
- `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (waiver VERIFIED)
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED; pattern precedent for path-rewrite + secret-scan + Pattern G deferral)
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED; pattern precedent for Pattern G + parents[N] deferral)
- `applications/Agent_Red/.gtkb-app-isolation.json` — Will receive 4 new entries via E.1 (src, tests, admin, widget) + 1 via E.2 (scripts subset)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "18.E structure — single atomic slice or sub-split into reviewable sub-sub-slices?" (S334, 2026-05-07) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" | This proposal IS the scoping deliverable. Owner authorized the 3-way decomposition. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete the isolation work as release-gating. | Authorizes 18.E program. |
| "Re-run 18.D + 18.C strictly per proposal" (S334) | "Resume direction" | Strict-scope discipline. | Per-sub-sub-slice proposals will be strict-scope; in-place edits and pattern-G deferrals only when explicitly authorized via AUQ. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Continues to authorize in-flight pre-migration state. |

## Background

The umbrella `-005`/`-008`/`-009` defined 18.E as a single cluster covering src/+tests/+admin/+widget/+scripts/. Live probing for this scoping reveals:

- **1,999 tracked files** total (305 src + 731 tests + 361 admin + 51 widget + 484 scripts + 67 branding deferred from 18.D + 1 stripe deferred from 18.D)
- **163 `parents[N]` usages** in src/+tests/ Python code — implicit cross-reference graph
- **Cross-cluster references** in tests:
  - `tests/multi_tenant/test_blind_key_delivery.py:130` references `parents[2] / "admin" / ...` — admin/ must move atomically with tests/
  - 13+ `tests/hooks/*` files reference `parents[2] / ".claude" / "hooks" / ...` — these are platform-test files testing GT-KB hooks
  - `tests/scripts/*` (10+ files) similarly reference platform code
- **pyproject.toml** has `testpaths`, `source`, `known-first-party`, `paths_to_mutate` all pointing at src/+tests/ — needs atomic update with the move
- **scripts/** has 220 top-level files + 12 subdirs requiring per-file disposition (most platform per umbrella `-008`/`-009`, but 220 top-level need case-by-case)

A single 18.E commit covering all 1,999 files would have an enormous blast radius and likely require many Codex iterations. Sub-splitting reduces blast radius per iteration.

## Goal

Decompose 18.E into 3 reviewable sub-sub-slices, each filed as its own bridge thread after this scoping is GO'd:

- **E.1 — Code Cluster Atomic Move** (~1,510 files): src/ + Agent Red tests/ + admin/ + widget/ + branding/ + config/stripe_product_ids.json + pyproject.toml import-config update. Atomic single commit due to interlocking parents[N] dependencies.
- **E.2 — Scripts Per-File Split** (~484 files): scripts/ disposition per umbrella `-009` table + per-file decisions for 220 top-level files. Likely 2-3 commits (Agent Red scripts → applications/Agent_Red/scripts/; platform scripts stay at root; archive/ + benchmark-results/ defer to 18.I review).
- **E.3 — Platform-Test Disposition Decision** (≤30 files): determine which `tests/hooks/`, `tests/scripts/`, and similar tests stay at root as a "platform tests" cluster vs. move with E.1's tests/. This is a SCOPE-DECISION sub-sub-slice; once decided, it informs E.1's exact tests/ inventory.

## Sub-Sub-Slice Plan

### 18.E.1 — Code Cluster Atomic Move

**Cluster:** Agent Red code + frontend + brand + Stripe config + import-path config.
**File counts (live probe 2026-05-07):**
- src/ — 305 files (Python application code)
- tests/ — 731 minus E.3-decided platform-test set (estimated ~20-30 files stay; ~700-710 migrate)
- admin/ — 361 files (Vite + React + TypeScript)
- widget/ — 51 files (Vite + Preact + TypeScript)
- branding/ — 67 files (deferred from 18.D per parents[2] dependency)
- config/stripe_product_ids.json — 1 file (deferred from 18.D per parents[3] dependency)
- pyproject.toml updates — 4 fields (testpaths, source, known-first-party, paths_to_mutate)

**Total estimated: ~1,510-1,520 files moved + 1 file edited.**

**Risk factors:**
- 163 `parents[N]` usages in src/+tests/ Python code — atomic move preserves the resolution graph
- admin/ + widget/ have local imports (verified via package.json structure); self-contained post-move
- Python imports rely on `known-first-party = ["src"]` in pyproject.toml — must update to `["applications.Agent_Red.src"]` or similar atomically
- pytest discovers tests via `testpaths = ["tests"]` — must update to `["applications/Agent_Red/tests"]`
- Agent Red CI workflows (`.github/workflows/*.yml`) reference src/, tests/, admin/, widget/ — those workflows are 18.G scope but in-place path-string edits in E.1 needed for working state (similar to 18.C's pattern)

**Pre-move probe required (in E.1's own proposal):**
- Recompute live counts at execution time
- Identify all hardcoded paths in admin/+widget/ build configs (vite.config.ts, package.json paths)
- Identify CI workflow path-string references that need in-place edits in E.1
- Run `python -m pytest --collect-only` to inventory the test discovery state pre-move
- Run admin and widget builds (`npm run build`) to establish pre-move green baseline

**Test plan (per-sub-sub-slice in E.1's own proposal):**
- T-rule-1, T-rule-2, T-platform-stay (cluster move basics)
- T-secret-1 + T-secret-2 (per 18.C pattern)
- T-import-1 (no remaining bare src/+tests/+admin/+widget/+branding/ refs in active code)
- T-pytest-collect (`python -m pytest --collect-only` returns expected count, no collection errors)
- T-pytest-subset (smoke subset of Agent Red tests passes from new location)
- T-admin-build (`npm run build` in applications/Agent_Red/admin/ succeeds)
- T-widget-build (`npm run build` in applications/Agent_Red/widget/ succeeds)
- T-pyproject-1 (pyproject.toml fields updated)
- T-platform-smoke (GT-KB platform tests: pre-existing failures only)
- T-history-1 (git mv preserves history for sample files)
- T-waiver-1 (commit cites DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER)

**Sequencing within E.1:**
- Step 1: T-secret-1 baseline + pre-move count verification
- Step 2: Update applications/Agent_Red/.gtkb-app-isolation.json registry (4 new Bucket-A entries)
- Step 3: `git mv` all 6 clusters into applications/Agent_Red/ (preserve order: src/, tests/ via per-file split, admin/, widget/, branding/, config/stripe_product_ids.json)
- Step 4: Update pyproject.toml import-path config
- Step 5: In-place edits to .github/workflows/*.yml for src/+tests/+admin/+widget/ path strings (similar to 18.C pattern)
- Step 6: Run all T-tests
- Step 7: Single commit on develop

**Estimated bridge cycles:** 2-4 iterations (similar to 18.C; this is the most complex sub-sub-slice).

### 18.E.2 — Scripts Per-File Split

**Cluster:** scripts/ — split per umbrella `-009` table + per-file decisions for 220 top-level files.

**Subdir disposition per umbrella `-009`:**
| Subdir | Files | Disposition |
|---|--:|---|
| `scripts/archive/` | 109 | DEFER to 18.I review |
| `scripts/pre-flight-results/` | 65 | STAYS (platform) |
| `scripts/rehearse/` | 15 | STAYS (platform) |
| `scripts/upgrade-results/` | 14 | STAYS (platform) |
| `scripts/gtkb_dashboard/` | 10 | STAYS (platform) |
| `scripts/deploy/` | 10 | SPLIT per-file in E.2 |
| `scripts/_report_charts_ar/` | 10 | MIGRATES (Agent Red) |
| `scripts/_report_charts/` | 9 | STAYS (platform) |
| `scripts/guardrails/` | 8 | STAYS (platform) |
| `scripts/benchmark-results/` | 7 | DEFER to 18.I review |
| `scripts/lib/` | 3 | STAYS (platform) |
| `scripts/stripe/` | 2 | MIGRATES (Agent Red) |
| `scripts/<top-level scripts>` | 220 | SPLIT per-file at E.2 execution |

**Top-level disposition method:**
- E.2's own proposal will enumerate each of the 220 top-level scripts and propose disposition (Agent Red vs platform vs archive)
- Heuristics: `_archive_*`, `_capture_*`, `_insert_*`, `_defect_reporter`, `_env`, `wire_tests_to_phases`, etc. → likely Agent Red operational
- `verify_*`, `check_*`, `bridge_*`, `gtkb_*`, `harness_*`, `release_*`, `kb_*` → likely platform
- Per-file judgment for ambiguous cases

**Test plan (per-sub-sub-slice in E.2's own proposal):**
- T-rule-1, T-rule-2 (cluster move basics; verify scripts split correctly)
- T-secret-1 + T-secret-2
- T-platform-script-imports (verify GT-KB tooling that imports scripts/ modules still works)
- T-history-1, T-waiver-1

**Sequencing within E.2:**
- Could be 1 commit or 2 commits depending on volume + risk
- Defer scripts/archive/ + scripts/benchmark-results/ to 18.I review per umbrella `-009`

**Estimated bridge cycles:** 1-3 iterations.

### 18.E.3 — Platform-Test Disposition Decision

**Question:** Which tests/* files stay at root (testing GT-KB platform code) vs. migrate with E.1's tests/?

**Live-probed candidates for "stays at root" (platform-test set):**

| Path | Files | Reason to stay |
|---|--:|---|
| `tests/hooks/` | 13 (5 test files + 7 fixtures + __init__.py) | All test GT-KB platform `.claude/hooks/*.py` directly via `parents[2] / ".claude" / "hooks" / ...` |
| `tests/scripts/` (subset) | ~10 files | Test GT-KB platform `scripts/*.py` (test_check_harness_parity, test_codex_hook_parity, test_groundtruth_governance_adoption, test_rehearse_path_rewrite, etc.) |
| `tests/__init__.py` | 1 | Shared (likely stays at root if any platform tests stay) |

**Total estimated platform-test files staying at root: ~20-30.**

**Decision needed:** the SCOPING proposal flags this as Open Question OQ-E3 to be resolved via AUQ before E.1 implementation begins. Two viable resolutions:

- **Option A — Split at the test-subdir level**: tests/hooks/ stays at root; tests/scripts/ splits per-file (Agent Red script tests migrate, platform script tests stay); rest of tests/ migrates. Tests at root keep `parents[2]` resolution; tests at applications/Agent_Red/ get `parents[2]` resolving to applications/Agent_Red/.
- **Option B — Update parents[N] in platform-test files**: All tests migrate; platform-test files have their `parents[2]` updated to `parents[3]` to walk up past applications/Agent_Red/ to repo root. More mechanical edits but no test-subdir split.

**E.3 deliverable:** AUQ + Deliberation Archive entry recording the chosen option. E.1's tests/ inventory is then concretized.

**Test plan (per-sub-sub-slice in E.3's own proposal — likely a thin proposal):**
- T-decision-1 (decision recorded in MemBase Deliberation Archive)
- T-test-list-1 (final platform-test list enumerated for E.1 to use)

**Estimated bridge cycles:** 1-2 iterations (mostly decision-making + light implementation).

## Sequencing Across Sub-Sub-Slices

Recommended order:
1. **This SCOPING proposal** → Codex GO
2. **E.3** (platform-test disposition AUQ + decision artifact) → Codex GO
3. **E.1** (atomic code cluster move using E.3's resolved tests/ scope) → Codex GO + implementation + post-impl REPORT + Codex VERIFIED
4. **E.2** (scripts per-file split) → Codex GO + implementation + post-impl REPORT + Codex VERIFIED

E.1 and E.2 could partially overlap (E.2 doesn't depend on E.1's outcome) but sequential execution reduces simultaneous-disruption risk.

## Goal (Scoping Proposal Specifically)

This scoping proposal's deliverable is the 3-way decomposition above. No file moves occur in this scope. Acceptance is Codex GO on the decomposition + ordering + risk identification.

## Risk / Rollback

**Risks (program-level):**
- 163 parents[N] usages mean implicit cross-references that may surface only at execution time
- E.1's atomic nature means partial-success isn't an option; either all 1,510+ files move or none
- Hidden hardcoded paths in admin/widget Vite/Preact configs may surface during build verification
- Mid-migration broken state risk for any sub-sub-slice that doesn't preserve atomic dependencies

**Mitigations (carried into per-sub-sub-slice proposals):**
- E.1: pre-move probing including `pytest --collect-only` baseline, npm build baselines, hardcoded-path grep
- E.2: per-file disposition table reviewed by Codex before execution
- E.3: AUQ resolution before any tests/* moves
- All sub-sub-slices: secret-scan baseline + post-move verification per 18.C/18.D pattern
- All sub-sub-slices: bridge review evidence staging per pre-commit hook expectation

**Rollback:** per-sub-sub-slice; each is its own commit. `git revert` of E.1 commit reverses 1,510+ moves atomically; same for E.2.

## Acceptance Criteria

This scoping proposal is accepted when:
- [ ] Codex GO on this `-001`
- [ ] 3-way decomposition (E.1 + E.2 + E.3) accepted
- [ ] Sequencing (this → E.3 → E.1 → E.2) accepted
- [ ] Risk identification + mitigation framework accepted
- [ ] OQ-E3 (platform-test disposition: Option A vs Option B) flagged for AUQ resolution before E.1

This scoping proposal does NOT VERIFY the underlying migration. Each sub-sub-slice has its own VERIFIED gate.

The full 18.E program is VERIFIED when:
- [ ] E.1, E.2, E.3 all VERIFIED individually
- [ ] No regression in GT-KB platform tests (T-platform-smoke pattern)
- [ ] Agent Red CI workflows green at applications/Agent_Red/{src,tests,admin,widget,scripts,branding}/ paths
- [ ] All Python imports resolve correctly post-move
- [ ] Both admin/ and widget/ npm builds succeed at new locations

## Open Questions

| ID | Question | Resolution path |
|---|---|---|
| **OQ-E3** | Platform-test disposition: Option A (split at subdir level) vs Option B (update parents[N] in platform-test files)? | Resolve via AUQ before E.1 implementation. Filed as 18.E.3 sub-sub-slice. |
| OQ-E.1.workflow | Should E.1 update Agent Red CI workflow path-strings in-place (per 18.C pattern), or defer to 18.G? | Resolve in E.1's own proposal. Default: in-place edits per 18.C precedent. |
| OQ-E.1.pyproject | Should E.1 update pyproject.toml's testpaths/source/known-first-party fields, or defer to 18.H? | Resolve in E.1's own proposal. Default: update in E.1 (atomic with import-graph relocation). |
| OQ-E.2.archive | scripts/archive/ — defer to 18.I as umbrella `-009` says, or include in E.2? | Resolve in E.2's own proposal. Default: defer per umbrella `-009`. |

## Out of Scope

This scoping proposal does NOT:
- Perform any file moves (sub-sub-slices do that)
- Resolve OQ-E3 or per-sub-sub-slice OQs
- Update any registry, workflow, pyproject, or source code
- Cover 18.F (Dockerfiles + infrastructure/terraform/), 18.G (workflows split), 18.H (manifests), 18.I (identity + memory + archive review), 18.J (repo separation), 18.K (platform docs install), 18.L (verification + cleanup)

## Project Root Boundary Compliance

This scoping proposal:
- Operates entirely within `E:/GT-KB/`
- Does not introduce live dependencies on paths outside `E:/GT-KB/`
- Cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE
- Per `.claude/rules/project-root-boundary.md`

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above
2. KB-search — no prior deliberation rejects 18.E sub-decomposition
3. Bridge-governance specs — cited
4. Preflight to be run after INDEX update
5. `packet_hash` recorded after preflight

## Provenance

| Source | Reference |
|---|---|
| Triggering owner directive (S334 AUQ) | "18.E structure" → "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" answer (2026-05-07) |
| Higher-level S334 directive | "Agent Red isolation — what's the next move?" → "Other": full directive approving completion of the isolation workstream |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Authorizing GOV | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 |
| Authorizing DCL | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 |
| Umbrella scope | `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (GO) + `-009` (re-scope GO) |
| Pattern precedent (sub-decomposition) | umbrella → 18.A scoping → 18.B/C/D pattern |
| Pattern precedent (atomic move) | `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED) |
| Pattern precedent (Pattern G deferral) | `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED) |
| Live probes | `git ls-files` per cluster + parents[N] grep + tests/hooks/ enumeration + pyproject.toml field check (executed 2026-05-07) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
