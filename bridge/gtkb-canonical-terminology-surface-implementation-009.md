# Post-Implementation Report (with scope contradiction): Canonical Terminology Surface

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Authorized by:** GO-006 at `bridge/gtkb-canonical-terminology-surface-implementation-006.md`
**Supersedes/adapts:** **Scope contradiction discovered** — GO-008 at `bridge/gtkb-canonical-terminology-surface-implementation-008.md` issued during this implementation window revised Phase 4's target paths. This report documents what was built per GO-006 AND truthfully reports the scope contradiction for Loyal Opposition disposition.

## Summary

I was authorized to implement the `-005` plan approved at GO-006. I completed all 8 phases, verified all gates, and committed to `feat/canonical-terminology-surface` at `2b4c1e9`. The commit is **functionally complete per GO-006** — but **architecturally obsolete per GO-008**, which was issued in parallel and mandates a different target-path strategy.

Per the parent-thread directive ("If you discover an issue that contradicts the implementation bridge, STOP and report — do not improvise"), I am filing this report to surface the contradiction rather than silently adapting. Loyal Opposition disposition requested.

## Scope contradiction (discovered at post-impl reporting)

### What I was authorized to build (GO-006, -005 plan)

Target paths:
- `templates/canonical-terminology.md` → `.claude/canonical-terminology.md`
- `templates/canonical-terminology.toml` → `.claude/canonical-terminology.toml`

Scaffold mechanism: hard-coded copy in `_copy_base_templates()` per `-005` §Phase 4
(`bridge/gtkb-canonical-terminology-surface-implementation-005.md:141`-`:156`).

Upgrade mechanism: extend `_MANAGED_*` lists + `_plan_missing_managed_files` repair path per `-005` §Phase 4.

### What GT-KB main now requires (GO-008, -007 plan)

Target paths:
- `templates/rules/canonical-terminology.md` → `.claude/rules/canonical-terminology.md`
- `templates/rules/canonical-terminology.toml` → `.claude/rules/canonical-terminology.toml`

Scaffold/upgrade mechanism: register as `class = "rule"` records in `templates/managed-artifacts.toml`; scaffold/upgrade/doctor flow through the registry, which became the single source of truth on GT-KB `main` at commit `e12aab3` (`feat(registry): consolidate _MANAGED_* lists into declarative TOML registry`).

AST gate: `tests/test_no_parallel_manifests.py` on GT-KB `main` **forbids** reintroducing `_MANAGED_*` module-level lists.

### Why I branched off the wrong base

Per the parent-thread directive, I created `feat/canonical-terminology-surface` from `origin/main @ 82c5a85`. At that SHA, `managed_registry.py` and the registry-driven scaffold/upgrade/doctor flow did not yet exist. Commit `e12aab3` was already on the GT-KB `main` branch locally (`git branch --contains e12aab3 → feat/start-here-adopter-rewrite, main`) but was not visible via `origin/main`. I did not audit the full main branch graph before branching.

The mismatch was not visible during Phases 1-8 because my feature branch does not include `e12aab3`, so neither `managed_registry.py` nor the AST gate `test_no_parallel_manifests.py` existed in my working tree. Every local check passed; it was only at post-impl reporting (when I inspected `bridge/INDEX.md` for the correct `-007` numbering) that I saw `-007` and `-008` had already been filed by another thread.

## What was built (per GO-006, commit `2b4c1e9`)

### Phase 1 — Spec recording

All 13 canonical-terminology specs inserted into GT-KB MemBase (`groundtruth.db`), tagged `adopter-onboarding,cto-trial,canonical-terminology`:

| Spec ID | Status | Title |
|---------|--------|-------|
| SPEC-TERMINOLOGY-RECORD | specified v1 | Canonical terminology record set MUST live in GT-KB MemBase |
| SPEC-TERMINOLOGY-MINIMUM-SET | specified v1 | Define 8 owner-listed terms + MEMBASE-4-CLAUDE.md glossary |
| SPEC-TERMINOLOGY-STARTUP-VISIBLE | specified v1 | CLAUDE.md / AGENTS.md startup-visible glossary + assertion ASSERT-TERMINOLOGY-CLAUDE-MD-MEMBASE |
| SPEC-TERMINOLOGY-TEMPLATE-INHERITANCE | specified v1 | Scaffolds produce projects with terminology block by default |
| SPEC-TERMINOLOGY-DOCTOR-CHECK | specified v1 | Doctor flags missing/inconsistent terminology |
| SPEC-TERMINOLOGY-BRIDGE-GATE | specified v1 | Bridge review gate requires propagation targets |
| SPEC-TERMINOLOGY-ASSERTION | specified v1 | Machine-verifiable assertion for startup-visible |
| SPEC-TERMINOLOGY-PROFILE-MATRIX | specified v1 | Profile-specific required-term matrix |
| SPEC-TERMINOLOGY-CONFIG-TOML | specified v1 | Profile-aware TOML config in `.claude/` |
| SPEC-TERMINOLOGY-UPGRADE | specified v1 | Upgrade idempotently adds canonical-terminology files |
| SPEC-TERMINOLOGY-DOCS-REFERENCE | specified v1 | Published reference page + inventory docs |
| SPEC-TERMINOLOGY-AGENTS-MD-PATH | specified v1 | Generated AGENTS.md names MEMORY.md not memory/MEMORY.md |
| SPEC-TERMINOLOGY-ALIAS-CLARITY | specified v1 | Explicit alias vs canonical marking |

Recording script kept for audit: `scripts/record_canonical_terminology_specs.py` on the feature branch.

### Phase 2 — Content authoring

- `templates/canonical-terminology.md` (185 lines) — full glossary with 8 canonical terms, alias disposition table, project-specific section; uses "tenant" language instead of Agent Red to avoid leakage.
- `templates/canonical-terminology.toml` (42 lines) — profile matrix (`local-only`, `dual-agent`, `dual-agent-webapp`, `harness-memory` via `extends = "dual-agent"`), `missing_severity = "ERROR"`, `drift_severity = "WARN"`, standard `ignore_paths` list.

### Phase 3 — Template content updates

- `templates/CLAUDE.md` — 15-line glossary block added above Project Identity section.
- `templates/project/AGENTS.md` — glossary block added + **P1-1 Codex condition discharged**: `memory/MEMORY.md` → `MEMORY.md` on line 69 of the startup checklist. Pointer to `.claude/canonical-terminology.md` added to loadable-docs list.
- `templates/MEMORY.md` — one-line pointer added near top.
- `templates/rules/deliberation-protocol.md` — "Canonical Term Propagation Gate" section added requiring 5 propagation targets before Codex GO on any bridge introducing a new canonical term.
- `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` — pointer added to document-loading list.

### Phase 4 — Scaffold + upgrade code

- `src/groundtruth_kb/project/scaffold.py` — `_copy_base_templates()` hard-coded copy of both canonical-terminology files into `.claude/` for every profile.
- `src/groundtruth_kb/project/upgrade.py` — added `_MANAGED_CANONICAL_TERMINOLOGY`, `_filter_canonical_terminology_for_profile`, `_plan_managed_canonical_terminology`, and `_map_managed_to_template` branch. Wired into `_plan_missing_managed_files` (unconditional repair) and `plan_upgrade` (version-gated drift check).

**This is the part GO-008 obsoletes.** The registry-driven flow on GT-KB main would register these files as `class = "rule"` records in `managed-artifacts.toml` with target paths under `.claude/rules/`, not `.claude/`.

### Phase 5 — Doctor extension

- `src/groundtruth_kb/project/doctor.py` — added `_check_canonical_terminology()` with `_load_canonical_terminology_config()` + `_resolve_profile_config()` (extends inheritance). Profile-aware per matrix; honours `memory_md_location = "harness"` to skip MEMORY.md content check under the `harness-memory` opt-in profile. ERROR on missing canonical terms; WARN on drift.

### Phase 6 — Tests at real paths (P1-2 Codex condition discharged)

- `tests/test_doctor_canonical_terminology.py` — 16 new tests:
  - Local-only: present check, missing-MemBase → ERROR, no AGENTS.md check
  - Dual-agent: present check, missing-Prime-Builder → ERROR, **AGENTS.md names MEMORY.md not memory/MEMORY.md (P1-1 assertion)**
  - Dual-agent-webapp: present check, verifies `extends` inheritance
  - Harness-memory: MEMORY.md content-check skip
  - Config loading: extends inheritance, missing-config → ERROR
  - run_doctor integration: parametrized across 3 profiles, zero-ERROR assertion

Tests live at `tests/test_doctor_canonical_terminology.py` (repo-root `tests/`, **not** `tests/project/`), per P1-2.

### Phase 7 — Docs

- `docs/reference/canonical-terminology.md` — new published reference page with Mermaid diagram of ADR-0001 three-tier architecture.
- `mkdocs.yml` — Canonical Terminology added to Reference nav section.
- `docs/reference/templates.md` — two new entries added to Project Files inventory (**P2-2 Codex condition discharged**).
- `templates/README.md` — two new entries added to Contents table (**P2-2 Codex condition discharged**).
- `CHANGELOG.md` — new `[Unreleased]` section with Added/Fixed/Docs/Tests subsections.

### Phase 8 — Dogfood

Both performed. Transcripts:

```text
=== DUAL-AGENT DOGFOOD (E:/_canonical-dogfood/dual/dogfood-demo) ===
Scaffolded at: E:\_canonical-dogfood\dual\dogfood-demo

CLAUDE.md OK (MemBase present)
AGENTS.md OK (MemBase present)
MEMORY.md OK (MemBase present)
glossary file OK   (.claude/canonical-terminology.md)
config file OK     (.claude/canonical-terminology.toml)
0                  (grep count of "memory/MEMORY.md" in AGENTS.md — P1-1 discharged)

=== DUAL-AGENT DOCTOR ===
[OK]  Canonical-terminology surface OK — 5 required terms present in 4 required files (profile: dual-agent)
...
Overall: [WARN] WARNING      (ruff missing, pollers not started — not canonical-terminology findings)
ERROR count: 0
```

```text
=== LOCAL-ONLY DOGFOOD (E:/_canonical-dogfood/local/dogfood-local) ===
Scaffolded at: E:\_canonical-dogfood\local\dogfood-local

local-only correctly has no AGENTS.md
CLAUDE.md OK (MemBase present)
MEMORY.md OK (MemBase present)
glossary file OK
config file OK

=== LOCAL-ONLY DOCTOR ===
[OK]  Canonical-terminology surface OK — 3 required terms present in 2 required files (profile: local-only)
...
Overall: [WARN] WARNING
ERROR count: 0
```

Both profiles: zero ERROR from `gt project doctor`.

## Verification gates (all green on `feat/canonical-terminology-surface` @ `2b4c1e9`)

### Pytest

**Targeted run (P1-2 Codex paths):**

```text
python -m pytest tests/test_scaffold_project.py tests/test_upgrade.py \
                 tests/test_scaffold_smoke.py tests/test_doctor_canonical_terminology.py -q
57 passed, 1 warning in 11.95s
```

**Full GT-KB suite (1225 tests):**

```text
python -m pytest tests/ -q
1225 passed, 1 warning in 324.69s (0:05:24)
```

Second run at a later time also showed `1225 passed, 1 warning in 325.86s`.

### mypy --strict

```text
python -m mypy --strict src/groundtruth_kb/project/doctor.py \
                         src/groundtruth_kb/project/scaffold.py \
                         src/groundtruth_kb/project/upgrade.py \
                         tests/test_doctor_canonical_terminology.py
Success: no issues found in 4 source files
```

### mkdocs build --strict

```text
python -m mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: E:\...\groundtruth-kb\site
INFO    -  Documentation built in 1.34 seconds
```

Only informational messages remain (pre-existing pages not in nav — unchanged from baseline).

### scripts/check_docs_cli_coverage.py

```text
python scripts/check_docs_cli_coverage.py
All documentation checks passed.
```

## Commit SHAs on the GT-KB feature branch

- Branch: `feat/canonical-terminology-surface`
- Base: `origin/main` @ `82c5a85`
- Single commit: **`2b4c1e9`** — `feat(governance): canonical terminology surface (adopter-onboarding)`
- Diff stats: 17 files changed, 1242 insertions, 7 deletions

## Discharge statement for GO-006 4 conditions

All four Codex conditions from GO-006 are discharged on `feat/canonical-terminology-surface @ 2b4c1e9`:

- **P1-1 AGENTS.md startup path bug** — `templates/project/AGENTS.md` updated (memory/MEMORY.md → MEMORY.md); scaffold test `test_dual_agent_scaffold_agents_md_names_memory_md_not_memory_subdir` asserts generated AGENTS.md names MEMORY.md and does NOT name memory/MEMORY.md. PASS.
- **P1-2 Test paths** — all four test files reside at repo-root `tests/` (`tests/test_scaffold_project.py`, `tests/test_upgrade.py`, `tests/test_scaffold_smoke.py`, `tests/test_doctor_canonical_terminology.py`). Directive's specified invocation pattern verified green.
- **P2-1 Post-impl report numbering** — original directive specified `-007`. By the time I reached post-impl reporting, `-007` and `-008` had been filed by another thread for the post-GO REVISED-3 adaptation cycle. Filing this report as `-009` per GO-008's §Carried-Forward Conditions ("File the post-implementation report as `bridge/gtkb-canonical-terminology-surface-implementation-009.md`") — the later GO number supersedes the earlier.
- **P2-2 Template inventory docs** — `docs/reference/templates.md` (lines ~13-14 area, depending on where inserted) and `templates/README.md` (Contents table) both list the new canonical-terminology files.

## Scope-contradiction disposition (required from Loyal Opposition)

The work on `2b4c1e9` is **architecturally inconsistent with GO-008** in three ways:

1. **Target paths** — files live at `.claude/canonical-terminology.*`, not `.claude/rules/canonical-terminology.*`.
2. **Scaffold mechanism** — `_copy_base_templates` hard-codes copy via direct `shutil.copy2`; GO-008 requires registry-driven copy via `templates/managed-artifacts.toml` + `artifacts_for_scaffold()`.
3. **Upgrade mechanism** — `_MANAGED_CANONICAL_TERMINOLOGY` was added to `upgrade.py` as a new hard-coded list; GO-008 implicitly forbids this via the AST gate `tests/test_no_parallel_manifests.py` on GT-KB main.

**If GO-006-authorized work is retained:** the commit `2b4c1e9` cannot merge to GT-KB main without re-work, because:
- `e12aab3` on main deleted the `_MANAGED_*` lists this commit re-introduces.
- `test_no_parallel_manifests.py` would fail on this commit after a main rebase.
- Doctor expects registry-driven artifact metadata; my hard-coded `.claude/` paths don't appear in the registry.

**If GO-008 adaptation is to proceed:** the canonical-terminology work needs to be redone on a branch rebased on GT-KB main (which includes `e12aab3`), with:
- Template files moved to `templates/rules/canonical-terminology.{md,toml}`.
- Scaffold targets at `.claude/rules/canonical-terminology.{md,toml}`.
- Two new records in `templates/managed-artifacts.toml` (`class = "rule"`, `initial_profiles`/`managed_profiles` for all three scaffold profiles, `doctor_required_profiles = []`).
- Updates to `tests/test_managed_registry.py` for 40→42 records, 8→10 rules, local-only +2 rules, dual-agent +2 rules.
- Update to `docs/bootstrap.md` manual-copy snippet to include the `.toml`.
- Doctor check (`_check_canonical_terminology`) repointed at `.claude/rules/canonical-terminology.*`.
- Template pointers (CLAUDE.md / AGENTS.md / MEMORY.md / CODEX-SESSION-BOOTSTRAP.md) re-pointed at `.claude/rules/canonical-terminology.md`.

## Evidence paths

- Feature branch commit: `feat/canonical-terminology-surface @ 2b4c1e9`
- Implementation log (gitignored): `.implementation-log-canonical-terminology.md` in GT-KB root
- Spec recording script: `scripts/record_canonical_terminology_specs.py` on branch
- Dogfood evidence: `E:/_canonical-dogfood/dual/dogfood-demo/`, `E:/_canonical-dogfood/local/dogfood-local/`
- GT-KB DB state: 13 canonical-terminology specs in `groundtruth.db` (verified with `db.list_specs()` filter)

## Recommended Loyal Opposition disposition

**Option 1 (preferred):** NO-GO on `2b4c1e9` as post-impl evidence for GO-006 because it conflicts with GO-008. Spawn a follow-on bridge (`-010` or equivalent) authorizing adaptation of the scope-contradiction findings into the GO-008 architecture. I can execute that adaptation given explicit authorization. The 13 specs already in MemBase need no change; only Phase 3-5 code changes require redo on a main-rebased branch.

**Option 2:** VERIFIED on `2b4c1e9` as evidence that GO-006's plan is *internally consistent and testable* (57/57 + 1225/1225 + mypy + mkdocs + doctor all green on this branch), with explicit acknowledgement that GO-008 now supersedes and adaptation is required in a separate bridge. This preserves the audit trail of what GO-006 meant, rather than silently discarding it.

**Option 3:** NO-GO with guidance that a later plan refactor should consolidate GO-006 and GO-008 into a single clean implementation cycle. My branch becomes a rejected-alternative record referenced by future deliberation.

The parent-thread directive said "Do NOT improvise" on contradictions, so I stopped at the reporting boundary and surface the choice to Loyal Opposition disposition.

## What this report does NOT do

- **No merge to GT-KB main.** The feature branch remains unmerged per parent-thread rule ("Do NOT commit to the main branch").
- **No Agent Red mutation.** The only Agent Red changes are this `-009` post-impl report file and the corresponding INDEX entry — both explicitly allowed by the parent-thread rules.
- **No KB mutation on Agent Red.** Only GT-KB MemBase was touched (the 13 canonical-terminology specs), per scope.
- **No adaptation to GO-008.** I have not moved files to `.claude/rules/` or updated the registry, because that would implement without Codex review per `.claude/rules/codex-review-gate.md`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
