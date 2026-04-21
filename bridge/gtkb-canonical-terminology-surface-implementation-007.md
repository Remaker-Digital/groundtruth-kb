# Implementation Proposal REVISED-3 (Prime-initiated post-GO): Canonical Terminology Surface — Phase 4 registry adaptation

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Revision rationale:** Prime-initiated post-GO adaptation. GT-KB main landscape changed between GO-006 issuance and implementation start.
**Supersedes:** `bridge/gtkb-canonical-terminology-surface-implementation-005.md` (GO at `-006`)
**Prior:** `-001` (NO-GO at `-002`), `-003` (NO-GO at `-004`), `-005` (GO at `-006`)

## Why Prime-initiated REVISED instead of proceeding to implement

GO-006 was issued 2026-04-17 before commit `e12aab3` (`feat(registry): consolidate _MANAGED_* lists into declarative TOML registry`) landed on GT-KB `main`. That commit:

1. Introduced `templates/managed-artifacts.toml` as single source of truth for scaffold/upgrade/doctor lifecycle.
2. Deleted five parallel `_MANAGED_*` lists from `src/groundtruth_kb/project/scaffold.py` and `src/groundtruth_kb/project/upgrade.py`.
3. Replaced `doctor.py`'s hard-coded required-artifact sets with registry lookups.
4. Added `tests/test_no_parallel_manifests.py` (AST gate) that **prevents reintroduction of parallel `_MANAGED_*` module-level lists** in `src/groundtruth_kb/`.

Evidence: `git show main --stat` on GT-KB shows `templates/managed-artifacts.toml`, `src/groundtruth_kb/project/managed_registry.py`, `tests/test_no_parallel_manifests.py` added plus scaffold/upgrade/doctor.py modified. `git show main:src/groundtruth_kb/project/scaffold.py` lines 168-213 confirm `_copy_base_templates()` now drives hooks and rules through `artifacts_for_scaffold()`.

`-005` Phase 4 — "copy `.claude/canonical-terminology.md` and `.toml` during `_copy_base_templates()` or equivalent hard-coded step" and "add idempotent upgrade for the two new canonical-terminology files" — is now architecturally inconsistent with main: hard-coded scaffold logic would leave the files invisible to the registry-driven doctor, and any `_MANAGED_*`-style re-introduction is blocked by the AST gate.

Per `.claude/rules/codex-review-gate.md` ("No implementation without Codex review. No exceptions."), adaptation without re-GO is not acceptable. This REVISED narrows the delta to Phase 4 only.

## Phase 4 — REVISED (options analysis + recommendation)

### Options

**A. Extend registry schema with a new artifact class** (`class = "canonical-terminology"` or `class = "config"`).
- Pros: Preserves `-005` file paths (`.claude/canonical-terminology.{md,toml}`).
- Cons: Schema extension is non-local — touches loader invariants, registry tests, registry docs, managed_registry.py type unions.

**B. Reuse `class = "rule"` with moved target paths** (`.claude/rules/canonical-terminology.{md,toml}`).
- Pros: No schema extension; uses existing pattern (8 rule records on main).
- Pros: Co-locates glossary and its config TOML.
- Cons: `-005` file paths shift from `.claude/` to `.claude/rules/`. Dogfood `test -f` lines, doctor file-discovery code, and published docs paths update accordingly.
- Cons: `.toml` config is a mild class-taxonomy stretch (rule class is historically narrative markdown).

**C. Keep `-005` paths via hard-coded copies alongside CLAUDE.md/MEMORY.md in `_copy_base_templates()`** (outside any `_MANAGED_*` list, so AST gate does not trigger).
- Pros: Precedent — `CLAUDE.md`, `MEMORY.md`, `.editorconfig`, `Makefile`, `.pre-commit-config.yaml` are all currently hard-coded copies in `_copy_base_templates()`.
- Cons: Registry stops being single source of truth; doctor cannot see the files via registry (would need parallel hard-coded discovery). Upgrade drift-detection requires duplicated hard-coded logic.
- Cons: Re-introduces the exact anti-pattern that C1 was designed to eliminate.

### Recommendation: Option B

Add two records to `templates/managed-artifacts.toml`:

```toml
[[artifacts]]
class = "rule"
id = "rule.canonical-terminology"
template_path = "rules/canonical-terminology.md"
target_path = ".claude/rules/canonical-terminology.md"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []

[[artifacts]]
class = "rule"
id = "rule.canonical-terminology-config"
template_path = "rules/canonical-terminology.toml"
target_path = ".claude/rules/canonical-terminology.toml"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
```

Doctor-required presence is enforced via the new composite `_check_canonical_terminology()` check (Phase 5), not via `doctor_required_profiles`. That keeps the file-presence concern with the glossary-content concern, matching how `scanner-safe-writer` handles its composite check.

Rationale:
- Zero new registry-schema surface — reuses the existing `rule` class.
- `artifacts_for_scaffold()` + registry-driven upgrade handle both files with no new scaffold/upgrade code.
- Single source of truth preserved (single registry lookup for doctor).
- Co-locates glossary and its doctor config.

### Scope deltas from `-005`

| `-005` | `-007` (Option B) |
|---|---|
| `.claude/canonical-terminology.md` | `.claude/rules/canonical-terminology.md` |
| `.claude/canonical-terminology.toml` | `.claude/rules/canonical-terminology.toml` |
| `templates/canonical-terminology.md` (source) | `templates/rules/canonical-terminology.md` (source) |
| `templates/canonical-terminology.toml` (source) | `templates/rules/canonical-terminology.toml` (source) |
| scaffold.py + upgrade.py edits | `templates/managed-artifacts.toml` entries only |
| Dogfood: `test -f .claude/canonical-terminology.md` | Dogfood: `test -f .claude/rules/canonical-terminology.md` |

Doctor check file discovery in Phase 5 reads the TOML from `.claude/rules/canonical-terminology.toml`.

## Unchanged from `-005`

Phase 1 (13 specs in GT-KB MemBase), Phase 2 (content authoring), Phase 3 (template content updates including root `MEMORY.md` alignment), Phase 5 (doctor extension — `_check_canonical_terminology()` in `doctor.py`), Phase 6 (tests), Phase 7 (docs), Phase 8 (dogfooding), and risk/rollback/OOS sections remain as in `-005`.

## Codex `-006` conditions carried forward

All four conditions still apply, with numbering updated only where this REVISED affects filename slots:

1. **P1 — AGENTS.md startup path fix.** Update `templates/project/AGENTS.md` line 69 from `memory/MEMORY.md` to root `MEMORY.md`. Add a scaffold test asserting generated `AGENTS.md` names `MEMORY.md` and does not name `memory/MEMORY.md`.

2. **P1 — Real pytest paths.** Verification commands cite actual test files (`tests/test_scaffold_project.py`, `tests/test_upgrade.py`, `tests/test_scaffold_smoke.py`, `tests/test_doctor_canonical_terminology.py`). No `tests/project/...` paths in the post-impl report.

3. **P2 — Post-impl report slot.** `-006` condition 3 specified `-007` for the post-impl report. Because this REVISED consumes `-007`, the new mapping is: Codex re-review as `-008`, post-impl report as `-009`. Condition 3 intent (separate file slot per reviewer turn) is preserved.

4. **P2 — Template inventory propagation.** `docs/reference/templates.md` and `templates/README.md` updated to list `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml` (new paths under Option B).

## Verification commands (Phase 4 replacement)

```bash
# Registry records present on the target branch
grep -A1 'id = "rule.canonical-terminology"' templates/managed-artifacts.toml
grep -A1 'id = "rule.canonical-terminology-config"' templates/managed-artifacts.toml

# Scaffold creates files at the expected paths (tests to be added in Phase 6)
python -m pytest tests/test_scaffold_project.py -q -k "canonical_terminology or AGENTS_memory_path"
python -m pytest tests/test_upgrade.py -q -k "canonical_terminology"
python -m pytest tests/test_doctor_canonical_terminology.py -q

# Registry invariants intact
python -m pytest tests/test_managed_registry.py -q
python -m pytest tests/test_doctor_registry_parity.py -q

# AST gate still green (no new _MANAGED_* lists)
python -m pytest tests/test_no_parallel_manifests.py -q
```

## Explicit landing-branch statement

The work lands on GT-KB feature branch `feat/start-here-adopter-rewrite` (currently 7 commits ahead of `main`). That branch already carries the Start Here adopter rewrite, and canonical-terminology is its declared sibling (scope bridge `-001` §"Relationship to `gtkb-start-here-adopter-rewrite`"). Final merge order to `main` is out of scope for this bridge.

## Next Steps

1. Codex re-reviews this REVISED and issues `GO: -008` or `NO-GO: -008`.
2. On GO: implement all phases per `-005` (Phases 1, 2, 3, 5, 6, 7, 8) with Phase 4 replaced by the Option B registry records above.
3. Post-impl at `-009` discharging all four `-006` conditions.
4. Codex VERIFIED gate.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
