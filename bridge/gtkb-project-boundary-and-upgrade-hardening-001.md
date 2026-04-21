# Scope Proposal: GT-KB Product/Project Boundary + Non-Disruptive Upgrade Hardening

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb` (GT-KB product scope — no direct Agent Red edits in scope per the adopter-not-author pattern)
**Origin:** Owner question 2026-04-17 ~3:55 PM: "Are you confident Agent Red is sufficiently disentangled from GT-KB? Can new projects upgrade cleanly without conflicts?" → Codex 14-min audit answered NO on both with concrete evidence.

## Problem Statement

Codex audit evidence (cited verbatim):

1. **Agent Red `groundtruth.db` tracking vs fresh-scaffold gitignore** — fresh scaffold (`bootstrap.py:25`) gitignores `groundtruth.db` but Agent Red tracks it. Historical entanglement.
2. **Agent Red pins older GT-KB versions** (`requirements-local.txt:17`, `requirements-test.txt:49`) — upgrade path not clean.
3. **`gt project upgrade` gaps** — no transactional rollback, no full settings-event merge, no managed workflow/integration upgrade surface, no mature per-file opt-out/merge strategy.
4. **Docs drift** — `docs/reference/templates.md` says 30 template files while managed-artifact registry currently has 42 records.
5. **`gt project init` requires empty target** (`bootstrap.py:75` `_validate_target()`) — no retrofit path for existing projects.

Codex confidence levels:

| Dimension | Confidence |
|-----------|------------|
| Fresh new GT-KB projects scaffolded without Agent Red contamination | Medium-high |
| Product/project boundary conceptually sound | Medium-high |
| Existing projects upgrade without touching adopter files normally | Medium |
| Agent Red sufficiently disentangled from GT-KB | **Low to medium** |
| GT-KB upgrades will never conflict with user projects | **Low** |

The "never" bar explicitly requires: stronger upgrade receipts, rollback, preflight, migration policy, managed/adopter-owned classification docs, retrofit tests.

## Codex's Acceptance Bar (adopted as scope)

1. Fresh-project scaffold tests
2. Retrofit-project tests (`gt project init` on non-empty dir)
3. Dirty-tree upgrade refusal (or confirm-and-merge flow)
4. Rollback receipt (transactional upgrade with audit trail)
5. Managed-vs-adopter artifact matrix (documented + machine-checkable)
6. Docs parity (templates.md synced with registry truth)
7. Dogfood Agent Red run proving `gt project doctor` and `gt project upgrade --dry-run` distinguish GT-KB-owned from Agent Red-owned files

## Scope (in)

### A. Artifact Ownership Matrix

Define explicit categories for every file/directory in a GT-KB-adopted project:

| Category | Who owns | Upgrade behavior |
|----------|----------|-------------------|
| GT-KB managed | GT-KB product | Overwritten on upgrade; customization signals doctor WARN |
| GT-KB scaffolded (adopter-owned) | Adopter | Provided once at scaffold; upgrade never touches unless `--force` with adopter opt-in |
| Adopter-owned | Adopter | GT-KB never reads or writes |
| Shared (structured data) | Both | Schema-governed merge (e.g., `.claude/settings.json` hook registrations) |

Output: `groundtruth-kb/docs/reference/artifact-ownership-matrix.md` published; machine-readable version in `templates/managed-artifacts.toml` (already exists — extend with explicit `ownership` field if not present).

### B. Transactional upgrade with rollback receipt

`gt project upgrade` becomes transactional:
- Stage all pending changes to a side tree first (pattern: `.gt-upgrade-staging/`)
- Generate receipt: JSON of `{file_path, pre_hash, post_hash, action}` for every touched file
- Commit atomically if all staging succeeds; rollback-safe if any step fails
- Receipt persisted at `.claude/upgrade-receipts/YYYY-MM-DDTHH-MM-SS.json`
- `gt project upgrade --rollback <receipt>` reverses a prior upgrade

### C. Dirty-tree upgrade refusal (or safe-merge path)

- Current `gt project upgrade` behavior TBD (Codex noted no strong rollback; need to verify what happens on dirty tree today)
- Target: hard refusal on uncommitted changes in managed files; clear diagnostic pointing at which files
- Adopter-owned dirty changes are fine (GT-KB doesn't touch them)

### D. Retrofit path for existing projects

`gt project init --retrofit <existing-dir>`:
- Does NOT require empty directory
- Scans existing contents; classifies each file per ownership matrix
- Reports conflicts before writing anything
- Offers `--dry-run` mode (default, with `--execute` for live)
- Enables Agent Red-class adopters to be retroactively onboarded cleanly

### E. Managed workflow/integration upgrade surface

GitHub Actions workflows, CI integration files, `.claude/settings.json` hook registrations — currently not fully covered by upgrade. Extend registry + upgrade logic to handle:
- `.github/workflows/*.yml` (managed workflow files with adopter-override escape hatch)
- `.claude/settings.json` hook registrations (structured-merge, not overwrite)
- Integration metadata (e.g., `sonar-project.properties`, `pyproject.toml` adopter-vs-managed sections)

### F. Docs parity automation

- `scripts/check_docs_vs_registry.py` that compares `docs/reference/templates.md` content against live `templates/managed-artifacts.toml` registry entries
- CI gate: failing parity check blocks PR merge
- Regenerate docs from registry where practical (similar to `docs/evidence.md` pattern from start-here rewrite)

### G. Dogfood: Agent Red retrofit proof

- Run `gt project upgrade --dry-run` against Agent Red
- Assert: managed files all identified as managed, adopter-owned files (bridges, tenant configs, product code) identified as adopter-owned
- Expected mismatches on the `groundtruth.db` tracking divergence — this is the artifact that proves the boundary classification works
- Document: which Agent Red files are "history burden" vs which are "still adopter-owned"
- Produces a Codex-reviewable artifact-classification report

### H. Version-pinning freshness

- Agent Red `requirements-local.txt` and `requirements-test.txt` pinned to older GT-KB version
- After this bridge lands, Agent Red adoption follow-on bumps version pin
- This is out of scope for this bridge (Agent-Red-local cleanup), but the cleanup is enabled by the product work here

## Scope (out)

- Agent Red's own cleanup of `groundtruth.db` tracking decision (separate follow-on bridge after this VERIFIED; needs owner decision on "should adopters track DB or not" — see Open Questions)
- Agent Red's GT-KB version pin bump (follow-on)
- Retroactive data migration tooling beyond the retrofit path
- Full monitoring/telemetry for upgrade success rates (instrument later)

## Prior Deliberations

- `DELIB-0715`, `DELIB-0817`, `DELIB-0818` — S299 governance foundation
- `bridge/gtkb-canonical-terminology-surface-implementation-011.md` (VERIFIED) — architectural precedent for managed-artifact-registry-based scaffold/upgrade
- `bridge/gtkb-managed-artifact-registry-010.md` (VERIFIED) — the registry infrastructure this bridge extends
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED) — earlier audit that surfaced the known limitations (Gap 2.8 etc.); this bridge operationalizes the findings
- Codex 2026-04-17 14-minute audit (not yet archived as DELIB — will archive as part of this bridge's filing evidence)

## Open Questions for Owner

1. **`groundtruth.db` tracking decision.** Current state: Agent Red tracks the DB file, fresh scaffold gitignores it. These are contradictory defaults. Which should win for the product contract?
   - (a) Adopters SHOULD track DB (version-controlled history, reviewable via diff) — Agent Red pattern wins
   - (b) Adopters SHOULD gitignore DB (local operational state, portable projects) — fresh scaffold pattern wins
   - (c) Adopter opt-in per project (gt init flag) — most flexible but more config surface
2. **Retrofit path opt-in.** Should `gt project init --retrofit` require explicit confirmation for each conflict, or offer a bulk-accept mode? First-principles: retrofit is risky, so require-per-conflict is safer for v1.
3. **Rollback receipt retention.** How long to keep receipts in `.claude/upgrade-receipts/`? Proposal: all kept indefinitely (append-only, like DELIBs). Pruning decision deferred.
4. **Agent Red "history burden" policy.** If the retrofit/boundary work reveals Agent Red has accumulated files that don't fit either managed or adopter-owned cleanly, do we: (a) keep them as adopter-owned with notes, (b) migrate them to GT-KB management retroactively, (c) mark them as legacy-exception with sunset date?

## Open Questions for Codex

1. Is the `.gt-upgrade-staging/` pattern the right choice for transactional upgrade, or is there a cleaner approach (e.g., git-based via a staging branch)?
2. Should the artifact ownership matrix extend the existing `managed-artifacts.toml` schema with new fields, or live as a sibling file?
3. Dirty-tree upgrade refusal: pre-existing tests to extend, or fresh test suite?
4. Is a retrofit path feasible for Agent Red specifically, given its 128+ session history and accumulated custom files? Or should Agent Red be treated as a special "grandfathered-in" adopter where retrofit is not attempted?

## Implementation Approach

**Phase 1 — Spec recording** (~8 specs covering A-H above)

**Phase 2 — Artifact Ownership Matrix** (docs + registry extension)

**Phase 3 — Transactional upgrade with rollback** (code in `src/groundtruth_kb/project/upgrade.py`)

**Phase 4 — Dirty-tree upgrade refusal** (safety gate)

**Phase 5 — Retrofit path** (`gt project init --retrofit`)

**Phase 6 — Managed workflow/integration upgrade surface**

**Phase 7 — Docs parity automation** (script + CI gate)

**Phase 8 — Dogfood against Agent Red** (dry-run report)

**Phase 9 — Tests** (fresh-project scaffold, retrofit, dirty-tree refusal, rollback round-trip, docs parity, Agent Red dogfood)

**Phase 10 — Post-impl report + Codex VERIFIED**

## Relationship to other in-flight work

- **Umbrella `gtkb-da-governance-completeness-001`:** complementary. That bridge covers DA-specific governance. This bridge covers the product/project boundary. Both land in GT-KB.
- **Session-wrap hooks `agent-red-session-wrap-automation-002` REVISED:** the hooks this lands need the managed-artifact-registry infrastructure, which this bridge hardens. If this bridge GOs first, session-wrap hook integration is cleaner.
- **Harvest-coverage `gtkb-da-harvest-coverage-implementation-*`:** Phase 5 GT-KB doctor + helper lives in this same product surface. Non-conflicting.

## Timeline

- **Now (evening):** scope bridge NEW. Codex review.
- **On Codex GO:** implementation. Large scope; likely needs to split into sub-bridges per phase or sub-phase at implementation-bridge time.
- **Agent Red retrofit dogfood:** produces a concrete report showing current entanglement vs post-fix state.

## Risk / Blast Radius

- HIGH. Changes affect every GT-KB adopter's upgrade behavior.
- Transactional upgrade + rollback is the primary safety net.
- Managed-artifact matrix documents the contract explicitly, so surprises are reduced.
- Phase 8 dogfood against Agent Red surfaces edge cases before they hit real adopters.

## Why this is critical now

The in-flight bridges (canonical-terminology, start-here rewrite, harvest-coverage) all VERIFIED or near-VERIFIED for GT-KB. Each adds to the product surface. Without the boundary/hardening work, those additions compound the upgrade-conflict risk for every adopter, including Agent Red.

Codex's "low confidence" on upgrades-never-conflict is the real product readiness gate.

## Next Steps After Codex GO

1. File implementation bridge (may split into sub-bridges per phase).
2. Archive Codex's 14-min audit as a DELIB with source_type='report' or 'lo_review'.
3. Execute phases on GT-KB feature branch.
4. Dogfood Agent Red + produce conflict report.
5. Codex VERIFIED.
6. File Agent Red adoption follow-on bridge (DB tracking decision, version pin bump, retrofit if applicable).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
