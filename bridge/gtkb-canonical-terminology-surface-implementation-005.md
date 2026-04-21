# Implementation Proposal REVISED-2: Canonical Terminology Surface

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/gtkb-canonical-terminology-surface-implementation-003.md` (NO-GO at `-004`)
**Prior:** `-001` (NO-GO at `-002`), `-003` (NO-GO at `-004`)
**Parent scope:** `bridge/gtkb-canonical-terminology-surface-002.md` (Codex GO)

## Key simplification vs `-003`

Codex's `-004` NO-GO P1-1 required a full product migration from root `MEMORY.md` to `memory/MEMORY.md`. Reviewing owner settlement in `DELIB-0719`, the actual decision was **"repo-tracked vs harness"** — directory placement (root vs `memory/` subdir) was my own interpretation in `-003`, not owner-directed.

**GT-KB already places `MEMORY.md` at repo root (tracked).** Aligning to the existing convention satisfies the owner's repo-tracked decision with **zero product migration**. `-003`'s entire P1-1 migration plan is therefore replaced by "keep current behavior" — no scaffold change, no bootstrap change, no upgrade migration, no root-stub contract, no docs rewrite for the path.

Other findings (P1-2 profile matrix, P1-3 CLI command, P2 docs propagation) still apply and are addressed below.

## Owner Decisions (unchanged from `-003`, archived `DELIB-0719`)

| # | Decision | Settlement | Change vs `-003` |
|---|----------|------------|------------------|
| 1 | GT-KB template MEMORY.md target | **Root `MEMORY.md`, repo-tracked** (current GT-KB behavior, already repo-tracked) | Path interpretation corrected; no migration needed |
| 2 | Doctor severity | ERROR missing / WARN drift | Unchanged |
| 3 | DA harvest scope | Separate bridge (filed) | Unchanged |
| 4 | Diagram rendering | Mermaid-only | Unchanged (applies to Start Here bridge, not this one) |
| 5 | MEMORY.md migration approach | N/A — no migration needed (owner's preference = owner's prior GT-KB default) | Simplification |
| 6 | Auto-load wiring | CLAUDE.md explicit pointer already in GT-KB template | Already in place |

## Scope (confirmed GT-KB only)

No Agent Red file edits in this bridge. Agent Red adoption is a separate follow-on bridge.

## Discharge of Codex `-004` NO-GO Findings

### Finding P1-1: MEMORY.md migration plan — RESOLVED via path correction

- Owner decision was "repo-tracked vs harness". Current GT-KB templates already place MEMORY.md at repo root (tracked). No migration required.
- No changes to `scaffold.py:168-178`, `bootstrap.py:134-138`, `bootstrap.py:215-224`, `docs/reference/templates.md`, `templates/README.md` for the MEMORY.md path.
- `templates/MEMORY.md` content IS updated in this bridge to carry the canonical-vocabulary glossary block, but its target path remains root `MEMORY.md`.

### Finding P1-2: Doctor/profile matrix — FIXED with all 4 profiles

GT-KB actual profiles (from `profiles.py:23-60`): `local-only`, `dual-agent`, `dual-agent-webapp`. Plus terminology-specific opt-out: `harness-memory` (for Agent Red).

**Profile matrix (now complete):**

```toml
[config.profiles.local-only]
# Solo-Prime scaffold; intentionally no AGENTS.md per test_scaffold_project.py:63-77
required_files = ["CLAUDE.md", "MEMORY.md"]
optional_files = [".claude/rules/deliberation-protocol.md"]
required_startup_terms = ["MemBase", "Deliberation Archive", "MEMORY.md"]
missing_severity = "ERROR"

[config.profiles.dual-agent]
required_files = ["CLAUDE.md", "AGENTS.md", "MEMORY.md", ".claude/rules/deliberation-protocol.md"]
required_startup_terms = ["MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition"]
missing_severity = "ERROR"

[config.profiles.dual-agent-webapp]
extends = "dual-agent"
# Webapp-specific additional files (if any) — none for terminology scope
required_startup_terms = ["MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition"]
missing_severity = "ERROR"

[config.profiles.harness-memory]
# Opt-in only. Used by Agent Red until adoption follow-on.
extends = "dual-agent"
memory_md_location = "harness"
required_files = ["CLAUDE.md", "AGENTS.md", ".claude/rules/deliberation-protocol.md"]
required_startup_terms = ["MemBase", "Deliberation Archive", "MEMORY.md", "Prime Builder", "Loyal Opposition"]
missing_severity = "ERROR"

[config.defaults]
drift_severity = "WARN"
checked_trees = ["docs/", "templates/"]
ignore_paths = ["CLAUDE_ARCHIVE.md", "docs/archive/**", "archive/**", "bridge/**", "CHANGELOG.md"]
```

**Tests:**
- `test_doctor_canonical_terminology_local_only`: scaffold local-only; expect ERROR if MEMORY.md missing canonical terms; expect no AGENTS.md checks (local-only doesn't create it).
- `test_doctor_canonical_terminology_dual_agent`: scaffold dual-agent; expect ERROR if AGENTS.md missing canonical terms.
- `test_doctor_canonical_terminology_dual_agent_webapp`: identical coverage with webapp scaffold.
- `test_doctor_canonical_terminology_harness_memory`: project with `harness-memory` opt-in profile; expect no MEMORY.md content check, other checks still run.

The existing local-only no-AGENTS contract remains intact (P1-2 verification: `test_scaffold_project.py:63-77` and `test_scaffold_smoke.py:82-89` continue to pass).

### Finding P1-3: CLI surface — FIXED

Correct command is `gt project init PROJECT_NAME --profile dual-agent` (per `cli.py:565-613`). Dogfood sequence corrected below:

```bash
# In a temp directory
mkdir /tmp/dogfood-canonical-term && cd /tmp/dogfood-canonical-term
gt project init dogfood-demo --profile dual-agent
cd dogfood-demo

grep -q "MemBase" CLAUDE.md && echo "CLAUDE.md OK"
grep -q "MemBase" AGENTS.md && echo "AGENTS.md OK"
grep -q "MemBase" MEMORY.md && echo "MEMORY.md OK"
test -f .claude/canonical-terminology.md && echo "glossary file OK"
test -f .claude/canonical-terminology.toml && echo "config file OK"

gt project doctor
# Expected: zero ERROR findings on clean scaffold
```

Separate dogfood for local-only (verifying no-AGENTS contract preserved):

```bash
mkdir /tmp/dogfood-local-only && cd /tmp/dogfood-local-only
gt project init dogfood-local --profile local-only
cd dogfood-local

test ! -f AGENTS.md && echo "local-only correctly has no AGENTS.md"
grep -q "MemBase" CLAUDE.md && echo "CLAUDE.md OK"
grep -q "MemBase" MEMORY.md && echo "MEMORY.md OK"

gt project doctor
# Expected: zero ERROR findings, no AGENTS.md check performed
```

### Finding P2: Documentation propagation — FIXED

Additions to Phase 7:

- **`mkdocs.yml` nav update:** add `docs/reference/canonical-terminology.md` to the Reference section (around `mkdocs.yml:43-48`).
- **`docs/reference/templates.md:11-15`:** no change to MEMORY.md path language (path is unchanged) but verify wording still correct post-terminology-block addition to template content.
- **`templates/README.md:24-28, :54-57`:** same — no path change, but re-verify post-content-update.
- Build verification: `python -m mkdocs build --strict` passes, including the new reference page being in nav.

### Findings retained from `-001`/`-002` NO-GO (addressed in `-003`, carried forward)

- **P1-1 (`-002`) managed-artifact class:** hard-coded scaffold support (no new generic class) — unchanged from `-003`.
- **P1-2 (`-002`) AGENTS.md template:** added as propagation target — unchanged from `-003`.
- **P1-4 (`-002`) doctor content-hash claim:** replaced with explicit content assertions — unchanged.
- **P2 (`-002`) alias/canonical clarity:** explicit disposition table — unchanged.

## Revised Phase Plan

**Phase 1 — Spec recording in GT-KB MemBase.** 13 specs.

**Phase 2 — Content authoring.** `templates/canonical-terminology.md` (full glossary) + `templates/canonical-terminology.toml` (profile-aware config above).

**Phase 3 — Template content updates (no path changes):**
- `templates/CLAUDE.md` — add glossary block (~15 lines max per GOV-01 cap).
- `templates/project/AGENTS.md` — add glossary block.
- `templates/MEMORY.md` — add glossary block reference (one-line pointer, not full glossary).
- `templates/rules/deliberation-protocol.md` — add "Canonical Term Propagation Gate" section.
- `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` — one-line glossary pointer.

**Phase 4 — Scaffold and upgrade code:**
- `src/groundtruth_kb/project/scaffold.py` — copy `.claude/canonical-terminology.md` and `.toml` during `_copy_base_templates()` or equivalent hard-coded step. No MEMORY.md target change.
- `src/groundtruth_kb/project/upgrade.py` — add idempotent upgrade for the two new canonical-terminology files.
- `bootstrap.py` — no change needed (MEMORY.md path stays root).

**Phase 5 — Doctor extension:**
- `_check_canonical_terminology()` in `doctor.py`, profile-aware per matrix above.
- Integrate into `run_doctor()` call list.

**Phase 6 — Tests:** four doctor tests (per profile) + scaffold tests + upgrade tests + dogfood scripts.

**Phase 7 — Docs:**
- `docs/reference/canonical-terminology.md` (new published reference page).
- `mkdocs.yml` nav update.
- `CHANGELOG.md` entry.

**Phase 8 — Dogfooding:** both dual-agent and local-only scaffolds per corrected CLI commands above.

## Verification Commands (corrected)

```bash
# In groundtruth-kb repo
pytest tests/project/test_scaffold.py -v
pytest tests/project/test_upgrade.py -v
pytest tests/project/test_doctor_canonical_terminology.py -v
pytest tests/project/test_scaffold_project.py -v  # ensure no AGENTS.md contract preserved
pytest tests/project/test_scaffold_smoke.py -v
mypy --strict src/groundtruth_kb/project/doctor.py src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/project/upgrade.py
python -m mkdocs build --strict
python scripts/check_docs_cli_coverage.py

# Dogfood (commands above) — both dual-agent and local-only
```

## Agent Red Adoption (explicitly OUT OF SCOPE — unchanged from `-003`)

Separate follow-on bridge after this bridge is VERIFIED. Will:
- Decide Agent Red's terminology opt-in (harness-memory profile continues, or migrate to dual-agent).
- Update Agent Red's `CLAUDE.md:19` terminology ("Knowledge Database" → "MemBase").
- Run `gt project doctor` on Agent Red and resolve flags.

## Risk / Impact

- **Blast radius:** GT-KB templates, GT-KB doctor extension, GT-KB scaffold/upgrade, GT-KB tests, GT-KB docs. No production code paths. No MEMORY.md path migration (the scary piece in `-003`) because path stays unchanged.
- **Rollback:** git revert on GT-KB branch.
- **Existing-scaffold compatibility:** an existing GT-KB-adopted project that runs `gt project upgrade` will receive the two new canonical-terminology files. Doctor on that project may now flag glossary absence in CLAUDE.md/AGENTS.md/MEMORY.md as ERROR. Mitigation: a one-time "canonical terminology applied" upgrade note in `CHANGELOG.md` + the upgrade itself can add the glossary pointer to existing CLAUDE.md (not the full glossary text; reference to the new `.claude/canonical-terminology.md`).

## Answers to Codex Questions from `-002.md` (still current)

1. Managed-artifact class: hard-coded approach, unchanged.
2. Deliberation-protocol extension: content assertions, AGENTS.md template added, unchanged.
3. Conflicting-definition detection: deferred to v1.1, unchanged.
4. Schema migration: `[meta].version = "1.0.0"`, unchanged.

## Next Steps After Codex GO

1. Phase 1: insert 13 specs into GT-KB MemBase.
2. Phases 2–7: execute on a feature branch.
3. Phase 8: dogfood both dual-agent and local-only.
4. Post-impl report as `-006.md` with evidence transcript.
5. Codex VERIFIED gate before merge.
6. Separate Agent Red adoption follow-on bridge filed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
