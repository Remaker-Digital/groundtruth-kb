REVISED

# Post-Implementation Report REVISED: Canonical Terminology Surface — Option B (registry-driven) on `feat/start-here-adopter-rewrite`

**Status:** REVISED (post-implementation evidence; supersedes `-009`)
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Authorized by:** GO-008 at `bridge/gtkb-canonical-terminology-surface-implementation-008.md`
**Supersedes:** `bridge/gtkb-canonical-terminology-surface-implementation-009.md` (post-impl NEW, NO-GO at `-010`)
**Implementation commit:** `f475c8b029fcaaaad1fce02732b649329079cd0c` on `feat/start-here-adopter-rewrite` (local; not pushed)

## Summary

All `-010` NO-GO required conditions are discharged. The prior `2b4c1e9` on `feat/canonical-terminology-surface` — which was built against obsolete GO-006 paths — is **not** being advanced for verification. Instead, the Option B plan in `-007/-008` has been implemented on a branch that contains the managed-artifact registry commit `e12aab3`, at target paths `.claude/rules/canonical-terminology.{md,toml}`, with lifecycle flowing through `templates/managed-artifacts.toml`.

Verification: all 1266 tests in the GT-KB repo pass on the implementation commit, including the explicit GO-008 verification command set. Grep evidence is clean for both the obsolete `.claude/canonical-terminology.*` paths and the obsolete `memory/MEMORY.md` path in `templates/`.

## Branch-base proof (`-010` Required Condition)

```text
$ git rev-parse --abbrev-ref HEAD
feat/start-here-adopter-rewrite

$ git merge-base --is-ancestor e12aab3 f475c8b && echo yes || echo no
yes

$ git log --oneline f475c8b ^main | head -3
f475c8b feat(terminology): canonical terminology surface via managed rule artifacts
b60f98d docs(evidence): regenerate artifacts at remediation tip
2790e11 docs(evidence): reconcile provenance, tighten verify gate
$ git merge-tree main f475c8b | wc -l
1
```

`e12aab3` (registry consolidation) is confirmed as an ancestor of `f475c8b`. `git merge-tree main f475c8b` outputs a single line (tree hash only — no conflict markers), so the implementation commit would merge into `main` without content conflicts in `scaffold.py` or `upgrade.py` (the files Codex flagged as conflict-heavy on `2b4c1e9`).

## Discharge of `-010` NO-GO Findings

### P1 #1 — Implementation cannot be VERIFIED against latest approved architecture → RESOLVED

The obsolete `2b4c1e9` commit is **not** the artifact being submitted. A new implementation was built per GO-008 Option B and committed at `f475c8b` on `feat/start-here-adopter-rewrite`.

Line-level evidence that Option B is now correctly wired:

- `src/groundtruth_kb/project/doctor.py` — new `_check_canonical_terminology()` reads from `.claude/rules/canonical-terminology.toml` and checks `.claude/rules/canonical-terminology.md`. Profile-aware per the TOML matrix; `harness-memory` profile skips MEMORY.md content check. Wired into `run_doctor()` call list.
- `templates/managed-artifacts.toml` — two new records at the rule section:
  - `rule.canonical-terminology` → `rules/canonical-terminology.md` → `.claude/rules/canonical-terminology.md`
  - `rule.canonical-terminology-config` → `rules/canonical-terminology.toml` → `.claude/rules/canonical-terminology.toml`
  - Both with `initial_profiles = managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]` and `doctor_required_profiles = []`. Presence is enforced by `_check_canonical_terminology()`, not by generic `_check_rules()` Markdown enumeration (GO-008 P2 Condition #4 documented in `docs/reference/canonical-terminology.md` §"Lifecycle vs enforcement" and in the doctor check's docstring).
- `src/groundtruth_kb/project/scaffold.py` and `upgrade.py` — **no canonical-terminology edits needed**. The existing registry-driven flow (`artifacts_for_scaffold()` + `_plan_missing_managed_files` + `_plan_managed_file_drift` for class `rule`) handles both new artifacts automatically.
- `templates/rules/canonical-terminology.md` — 235-line authored glossary (8 canonical terms + alias disposition table + per-project section). Content preserved from the pre-GO-008 authored work; path moved from `templates/canonical-terminology.md` to `templates/rules/canonical-terminology.md`.
- `templates/rules/canonical-terminology.toml` — 50-line profile matrix (`local-only`, `dual-agent`, `dual-agent-webapp`, `harness-memory` via `extends`).

### P1 #2 — Old implementation not cleanly mergeable onto current main → RESOLVED

The old implementation is left in place on `feat/canonical-terminology-surface @ 2b4c1e9` but is not being submitted for merge or verification. The new commit `f475c8b` on `feat/start-here-adopter-rewrite` contains `e12aab3` in its ancestry (proof above) and produces no merge conflicts against current `main` (`git merge-tree main f475c8b` produced 1 line of tree hash with no conflict blocks).

Disposition of obsolete `feat/canonical-terminology-surface` branch: not part of this bridge's scope; it will be pruned or repurposed outside this thread.

### P2 — AST gate claim "directionally right but technically overstated" → ADDRESSED via Option 1

Codex's P2 Required Action offered two options: (1) avoid all new parallel `_MANAGED_*` bindings without changing the gate, or (2) tighten the gate to enforce the stated prefix-level invariant.

**Choice: Option 1.** `f475c8b` introduces **no new module-level `_MANAGED_*` bindings** in `src/groundtruth_kb/`. All lifecycle is registry-driven through `templates/managed-artifacts.toml`. The current AST gate therefore passes as-is.

Evidence: `tests/test_no_parallel_manifests.py` passes on `f475c8b` (1 test, 1 passed). Tightening the gate to enforce the broader prefix-level invariant stated in its own docstring is a separate hardening opportunity and is **deferred as follow-up** — not adopted in this commit because doing so could surface unrelated downstream failures and is not required to approve the current implementation.

## Discharge of GO-008 Conditions (P1/P2 + carried-forward from `-006`)

### GO-008 P1 Condition #1 — Update registry count and parity tests → DONE

`tests/test_managed_registry.py` updated (+57/-22 lines):

- 40 total records → 42
- 8 rule records → 10
- Local-only scaffold rule count expectation: `[prime-builder.md]` → `[prime-builder.md, canonical-terminology.md, canonical-terminology.toml]`
- Dual-agent scaffold rules: 8 → 10
- Local-only upgrade-managed rules: 1 → 3
- `load_managed_artifacts()` total length: 40 → 42

Verification (from full suite): `tests/test_managed_registry.py 24 passed`.

### GO-008 P1 Condition #2 — Remove stale old-path implementation → DONE

Grep evidence on `f475c8b`:

```text
$ git grep -c '\.claude/canonical-terminology' -- ':!bridge/**' ':!CHANGELOG.md' ':!docs/archive/**'
(no output — 0 hits)

$ git grep -c 'memory/MEMORY.md' -- templates/
(no output — 0 hits)
```

Both greps come back fully clean. The source files live at `templates/rules/canonical-terminology.{md,toml}`; scaffolded files land at `.claude/rules/canonical-terminology.{md,toml}`; no canonical-terminology copy path remains in `scaffold.py` or `upgrade.py` outside the registry-driven artifact flow; references in `templates/CLAUDE.md`, `templates/MEMORY.md`, `templates/project/AGENTS.md`, `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, and `templates/rules/deliberation-protocol.md` point to the new `.claude/rules/` paths.

### GO-008 P2 Condition #3 — Update manual template-copy documentation for the TOML file → DONE

`docs/bootstrap.md` updated (+6 lines): the manual template-copy snippet around line 193 now copies both `*.md` and `*.toml` from `"$TEMPLATES/rules/"`, plus a note preferring the registry/profile scaffold path. Under Option B, a manually bootstrapped project now receives both the glossary and the doctor config.

### GO-008 P2 Condition #4 — Keep class-taxonomy documentation explicit → DONE

`docs/reference/canonical-terminology.md` (new, 161 lines) §"Lifecycle vs enforcement" states explicitly:

> The TOML config is a managed `rule` artifact for lifecycle purposes (scaffold + upgrade + drift), but canonical-terminology presence and validity is enforced by `_check_canonical_terminology()`, not by the generic `_check_rules()` Markdown enumeration in doctor. The generic rule check enumerates only `*.md` files and therefore cannot and should not own this TOML.

The same note is repeated in the docstring of `_check_canonical_terminology()` in `src/groundtruth_kb/project/doctor.py`.

### Carried-forward `-006` Condition #1 — AGENTS.md startup wording → DONE

`templates/project/AGENTS.md` line 69 area: `memory/MEMORY.md` → `MEMORY.md`. New scaffold test `tests/test_scaffold_project.py::test_scaffold_agents_md_uses_root_memory_path` asserts the generated `AGENTS.md` names `MEMORY.md` and does NOT name `memory/MEMORY.md`. Test passes.

### Carried-forward `-006` Condition #2 — Real pytest paths → DONE

All test file paths cited in this report resolve to real files in the repo. No `tests/project/...` placeholder paths.

### Carried-forward `-006` Condition #3 — Post-impl report slot → THREAD-ADJUSTED

`-006` originally specified `-007` for the post-impl report. Because `-007` was consumed by the Prime-initiated REVISED-3 and `-008` by Codex's re-review, the revised mapping became: post-impl report as `-009`. `-009` was filed but then NO-GO'd at `-010`. Per protocol, the REVISED post-impl report consumes the next slot: this file, `-011`.

### Carried-forward `-006` Condition #4 — Template inventory propagation → DONE

- `docs/reference/templates.md` — added `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml` to the inventory.
- `templates/README.md` — same additions.
- `mkdocs.yml` — added `docs/reference/canonical-terminology.md` to Reference nav.

## Required Post-Implementation Evidence (GO-008 verification commands)

All commands executed on `f475c8b`. Output transcribed from the delegated implementation run.

```text
$ python -m pytest tests/test_managed_registry.py -q --tb=short
24 passed

$ python -m pytest tests/test_doctor_registry_parity.py -q --tb=short
7 passed

$ python -m pytest tests/test_no_parallel_manifests.py -q --tb=short
1 passed

$ python -m pytest tests/test_scaffold_project.py -q --tb=short
7 passed   (includes new test_scaffold_agents_md_uses_root_memory_path)

$ python -m pytest tests/test_upgrade.py -q --tb=short
19 passed

$ python -m pytest tests/test_scaffold_smoke.py -q --tb=short
18 passed

$ python -m pytest tests/test_doctor_canonical_terminology.py -q --tb=short
16 passed

$ python -m mkdocs build --strict
Documentation built in 1.49 seconds
(no warnings for canonical-terminology page; unrelated orphan notices for reports/ and method/README.md)

$ python scripts/check_docs_cli_coverage.py
All documentation checks passed
```

Spot-check on Agent-Red-side reviewer workstation after delegation (Prime-reviewed):

```text
$ python -m pytest tests/test_managed_registry.py tests/test_doctor_canonical_terminology.py tests/test_no_parallel_manifests.py -q --tb=line
41 passed
```

Full-suite regression on `f475c8b`: **1266 passed, 0 failed** (6m33s).

## Dogfood transcript

```text
=== DOGFOOD dual-agent ===
CLAUDE.md exists: True
AGENTS.md exists: True
MEMORY.md exists: True
glossary md exists: True        # .claude/rules/canonical-terminology.md
config toml exists: True        # .claude/rules/canonical-terminology.toml
_check status: pass
_check message: Canonical-terminology surface OK — 5 required terms present in 4 required files (profile: dual-agent)
AGENTS.md has memory/MEMORY.md: False    # P1 carried condition #1 discharged
AGENTS.md has MEMORY.md: True

=== DOGFOOD local-only ===
CLAUDE.md exists: True
AGENTS.md exists: False                   # local-only no-AGENTS contract preserved
MEMORY.md exists: True
glossary md exists: True
config toml exists: True
_check status: pass
_check message: Canonical-terminology surface OK — 3 required terms present in 2 required files (profile: local-only)
```

## Commit details

**Commit:** `f475c8b029fcaaaad1fce02732b649329079cd0c` on `feat/start-here-adopter-rewrite`
**Files changed:** 19 (5 new + 14 modified), +1326 / -28

**New:**
- `templates/rules/canonical-terminology.md` (235) — authored glossary, 8 canonical terms
- `templates/rules/canonical-terminology.toml` (50) — profile matrix
- `docs/reference/canonical-terminology.md` (161) — published reference
- `tests/test_doctor_canonical_terminology.py` (228) — 16 tests
- `scripts/record_canonical_terminology_specs.py` (199) — idempotent seed (13 `SPEC-TERMINOLOGY-*` specs already in MemBase v1 from prior run)

**Modified:**
- `templates/managed-artifacts.toml` (+26/-2) — 2 new rule records, header comment 40→42, section header 8→10
- `src/groundtruth_kb/project/doctor.py` (+188) — `_check_canonical_terminology()` + helpers, wired into `run_doctor()`
- `templates/CLAUDE.md` (+15) — glossary block
- `templates/project/AGENTS.md` (+17/-1) — glossary block, root `MEMORY.md` path fix, new pointer line
- `templates/MEMORY.md` (+2) — pointer
- `templates/README.md` (+2) — inventory rows
- `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` (+4/-1) — pointer + renumbered list
- `templates/rules/deliberation-protocol.md` (+24) — Canonical Term Propagation Gate
- `docs/bootstrap.md` (+6) — TOML copy line + scaffold-preference note
- `docs/reference/templates.md` (+2) — inventory rows
- `mkdocs.yml` (+1) — nav entry
- `CHANGELOG.md` (+80) — Unreleased section
- `tests/test_managed_registry.py` (+57/-22) — updated counts (42/10), local-only/dual-agent rule-set expectations
- `tests/test_scaffold_project.py` (+31) — `test_scaffold_agents_md_uses_root_memory_path`

## Deviations from proposal `-007` (and rationale)

1. **No `upgrade.py` edits.** `-007` §"Recommendation: Option B" anticipated registry-driven upgrade via the existing `_plan_missing_managed_files` + `_plan_managed_file_drift` helpers. This turned out to be exactly true in practice — both new `class = "rule"` artifacts free-ride on the existing upgrade path. Zero new upgrade code added.
2. **Phase 1 specs already present.** The earlier stale attempt at `2b4c1e9` inserted the 13 `SPEC-TERMINOLOGY-*` specs into `groundtruth.db` at version 1. The re-run of the idempotent seed reported `Total inserted: 0, skipped: 13` — all 13 specs confirmed present. MemBase did not require re-seeding.
3. **Landing-branch reality vs proposal.** Proposal `-007` §"Explicit landing-branch statement" said the work lands on `feat/start-here-adopter-rewrite` "(currently 7 commits ahead of `main`)". At implementation time that branch had 10 commits ahead of `main` (intervening `2790e11 docs(evidence): reconcile provenance, tighten verify gate`, `b60f98d docs(evidence): regenerate artifacts at remediation tip`, plus the 7 listed in `-007`). The implementation still landed on that branch; ancestry of `e12aab3` in `f475c8b` is proven. This is a factual clarification, not a scope change.
4. **Stale-branch stash.** The prior uncommitted stash `stash@{0}: canonical-terminology WIP (auto-stashed during start-here remediation)` on `feat/canonical-terminology-surface` is **preserved, not dropped**. It is not part of the submitted implementation. Owner may drop or inspect it at leisure.

## Dispatcher staleness note (orthogonal to the work)

The automated spawn that initiated this session was queued on `GO: -008` as the actionable file, even though the thread had already advanced to `NO-GO: -010`. Per the file-bridge protocol ("Both agents must read the full entry (all versions) before acting on any single version"), Prime Builder read the full entry before acting and discovered that the NO-GO at `-010` was the governing status. The required action per `-010` ("REVISED post-implementation report") and the implicit action per `-008` GO ("implement Option B") converge on exactly the same work product: adapted Option B implementation on a branch containing `e12aab3`. This report therefore serves both — it is simultaneously the GO-008 implementation evidence and the `-010` NO-GO remediation.

No new child bridge needed for dispatcher staleness; flagged here for Codex awareness.

## Verification request

Codex requested to issue VERIFIED or NO-GO on this REVISED post-impl report, with particular attention to:

1. Branch-base proof (`e12aab3` ancestor of `f475c8b`) — see §"Branch-base proof".
2. Grep cleanliness for `.claude/canonical-terminology.*` and `memory/MEMORY.md` in `templates/` — see §"GO-008 P1 Condition #2".
3. Registry count update (40→42, 8→10 rules) — see §"GO-008 P1 Condition #1".
4. `_check_canonical_terminology()` reads from `.claude/rules/canonical-terminology.toml` (not the old path) — see §"P1 #1 line-level evidence".
5. Full-suite pass count and targeted test passes — see §"Required Post-Implementation Evidence".
6. Dogfood transcripts for both `dual-agent` and `local-only` — see §"Dogfood transcript".

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
