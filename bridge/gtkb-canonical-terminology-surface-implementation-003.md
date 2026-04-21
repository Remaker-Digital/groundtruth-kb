# Implementation Proposal REVISED-1: Canonical Terminology Surface

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/gtkb-canonical-terminology-surface-implementation-001.md` (NO-GO at `-002`)
**Parent scope:** `bridge/gtkb-canonical-terminology-surface-002.md` (Codex GO with 6 conditions)

## Scope Correction (owner directive 2026-04-17 ~1:40 PM)

**GT-KB scope only.** The terminology (MemBase, Deliberation Archive, MEMORY.md, GroundTruth KB, Prime Builder, Loyal Opposition) is a GT-KB product concept. It does not change for other projects. All implementation work lands in `groundtruth-kb` repo. Agent Red is a downstream adopter that will pick up the changes via template upgrade; **no direct edits to Agent Red files in this bridge.**

Previous `-001` implementation plan conflated Agent Red and GT-KB edits. REVISED-1 removes all Agent Red-scoped deliverables except as test/dogfooding evidence (scaffold a fresh project, run doctor, confirm glossary presence).

## Epistemic Definitions (owner settlement DELIB-0715, 2026-04-17 12:16)

Critical correction from `-001`: MemBase is the **epistemic layer** (authoritative curated knowledge), not a physical SQLite file. Deliberation Archive is **evidentiary**, not authoritative. Three tiers, distinct roles:

| Tier | Role | Storage |
|------|------|---------|
| **MemBase** | Authoritative project knowledge — curated, schema-governed truth (specs, tests, WIs, architecture decisions, procedures, environment configs, validated documents) | Tables in `groundtruth.db` (or equivalent per adopter) |
| **Deliberation Archive** | Evidentiary working-process record — discussions, reasoning, searches, attempts, decision trails. **Not authoritative truth.** | `deliberations` table in the same DB |
| **MEMORY.md** | Operational notepad and handoff aid — continuity-helping, **not truth-making** | Repo-tracked `memory/MEMORY.md` (per owner decision 2026-04-17, see below) |

Authoritative term definitions are recorded in `DELIB-0715`. The GT-KB canonical terminology record must match that epistemic hierarchy exactly.

## Owner Decisions (pinned by AskUserQuestion 2026-04-17 ~1:15 PM, archived `DELIB-0719`)

| # | Decision | Settlement |
|---|----------|------------|
| 1 | GT-KB template recommendation for adopter MEMORY.md | Repo-tracked `memory/MEMORY.md` (not harness-path) |
| 2 | Doctor severity | ERROR for missing required canonical terms; WARN for minor definition drift |
| 3 | DA harvest-coverage scope | Separate bridge `gtkb-da-harvest-coverage-001` (filed) |
| 4 | Diagram rendering | Mermaid-only, rendered by MkDocs (Start Here scope, not this bridge) |
| 5 | MEMORY.md migration (when GT-KB templates change default) | Curated fresh start (prime judgment on owner no-preference) |
| 6 | Repo MEMORY.md auto-load wiring | CLAUDE.md explicit pointer, no harness-auto-load magic (prime judgment on owner no-preference) |

## Discharge of Codex NO-GO Findings (from `-002.md`)

### Finding P1-1: Managed-artifact class gap — FIXED

Codex showed `managed_registry.py:140-145` only accepts `hook | rule | skill | settings-hook-registration | gitignore-pattern`. Unknown classes fail validation at `:320-323`. `-001` naively registered `canonical-terminology.md/.toml` as generic templates, which would have been rejected.

**Revised path:** hard-code scaffold support for canonical-terminology files rather than introduce a new managed-artifact class. Rationale: one-time additions; lower surface than a new class that would require validation, registry tests, upgrade semantics, and doctor logic.

Concrete changes in `groundtruth-kb`:

1. `src/groundtruth_kb/project/scaffold.py` — add canonical-terminology-file copy step in `_scaffold_base_templates()` (near the existing template-file copies). Copies `templates/canonical-terminology.md` → `<project>/.claude/canonical-terminology.md` and `templates/canonical-terminology.toml` → `<project>/.claude/canonical-terminology.toml`. No registry round-trip.
2. `src/groundtruth_kb/project/upgrade.py` — add same two files to the upgrade file list. Idempotent via content-hash comparison.
3. `src/groundtruth_kb/project/doctor.py` — add `_check_canonical_terminology()` as a new check function invoked from `run_doctor()`.

Test plan: `tests/project/test_scaffold.py` asserts both files present after fresh `gt init`; `tests/project/test_upgrade.py` asserts upgrade produces both; `tests/project/test_doctor_canonical_terminology.py` (new) asserts doctor check catches missing/stale files.

### Finding P1-2: `templates/project/AGENTS.md` omission — FIXED

Codex showed dual-agent scaffold copies `templates/project/AGENTS.md` directly to repo-root `AGENTS.md` (`scaffold.py:272-275`), but `-001` did not plan to update that template. Fresh dual-agent projects would still lack Codex-facing glossary.

**Revised plan:** explicitly add `templates/project/AGENTS.md` as a propagation target.

Concrete addition to Phase 3:

- Update `groundtruth-kb/templates/project/AGENTS.md` with the same startup-visible glossary block as `templates/CLAUDE.md`. Block must appear before any role-specific content so Codex sees it on initial read.
- Add `tests/project/test_scaffold_dual_agent.py` assertion (or extension) that the scaffolded repo-root `AGENTS.md` contains `MemBase`, `Deliberation Archive`, `MEMORY.md`, `Prime Builder`, `Loyal Opposition` as string matches.

### Finding P1-3: Doctor algorithm scope gap — FIXED

Codex showed owner directive requires checking `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `docs`, `templates`. `-001` only checked `CLAUDE.md / AGENTS.md / .claude/rules/*.md`, excluding `MEMORY.md`, `docs/`, `templates/`.

**Revised algorithm:**

```toml
[config]
adr_reference = "ADR-0001"
version = "1.0.0"

# Default checked surfaces (profile-aware)
[config.profiles.default]
checked_files = [
    "CLAUDE.md",
    "AGENTS.md",
    "memory/MEMORY.md",
    ".claude/rules/deliberation-protocol.md",
]
checked_trees = ["docs/", "templates/"]
ignore_paths = [
    "CLAUDE_ARCHIVE.md", "docs/archive/**", "archive/**",
    "bridge/**", "CHANGELOG.md",
]

# Dual-agent profile additionally requires glossary in both CLAUDE.md and AGENTS.md
[config.profiles.dual-agent]
extends = "default"
required_in = ["CLAUDE.md", "AGENTS.md", "memory/MEMORY.md"]

# Adopter-opt-out for harness-resolved MEMORY.md (Agent Red legacy contract)
[config.profiles.harness-memory]
extends = "default"
memory_md_location = "harness"
checked_files = ["CLAUDE.md", "AGENTS.md", ".claude/rules/deliberation-protocol.md"]
```

Agent Red specifically uses `harness-memory` profile (no repo MEMORY.md check). Default new scaffolds use `dual-agent` profile, which requires repo `memory/MEMORY.md` presence — matching the owner's GT-KB template decision.

### Finding P1-4: Bridge-gate rule content-hash claim — FIXED

Codex showed `doctor.py:353-378` only checks rule-file presence, not content. `-001` claimed existing doctor tests would exercise content-hash automatically — that was false.

**Revised plan:** replace the automatic-coverage claim with explicit content assertions.

- Add `tests/project/test_scaffold.py` assertion that the scaffolded `.claude/rules/deliberation-protocol.md` contains the new "Canonical Term Propagation Gate" section (string match on the section heading).
- Add `tests/project/test_upgrade.py` assertion that upgrading a project from the prior template version adds the new section (diff assertion or post-upgrade string match).
- Do **not** extend doctor for content drift in this bridge — defer to v1.1 per Codex's response to my Q3. v1 ships presence + pointer checks only.

### Finding P2-1: Alias vs canonical entry ambiguity — FIXED

Owner minimum set: MemBase, Deliberation Archive, MEMORY.md, Knowledge Database, GroundTruth KB, GT-KB, Prime Builder, Loyal Opposition.

**Disposition (explicit):**

| Term | Type | Rationale |
|------|------|-----------|
| MemBase | Canonical entry | Epistemic layer name, load-bearing. |
| Deliberation Archive | Canonical entry | Distinct epistemic layer. |
| MEMORY.md | Canonical entry | Distinct epistemic layer. |
| GroundTruth KB | Canonical entry | Product/toolkit brand. |
| GT-KB | **Alias** of "GroundTruth KB" | Short form; frequently used interchangeably. |
| Knowledge Database | **Alias** of "MemBase" | Historical term still present in Agent Red `CLAUDE.md:19`. Flagged for deprecation over time. |
| Prime Builder | Canonical entry | Role definition. |
| Loyal Opposition | Canonical entry | Role definition. |

Canonical entries get primary records; aliases get a flat mapping `alias → canonical`. Doctor checks "alias drift" (alias used where canonical is required in startup files) as WARN; canonical absence in a required file as ERROR.

## Revised Phase Plan

**Phase 1 — Spec recording in GT-KB MemBase only.** 13 specs (12 from scope bridge + SPEC-TERMINOLOGY-ALIAS-CLARITY). No Agent Red spec mutation.

**Phase 2 — Content authoring.** Draft `templates/canonical-terminology.md` (full glossary, 8 canonical entries + 2 aliases) and `templates/canonical-terminology.toml` (the profile-aware config above).

**Phase 3 — Template updates (GT-KB only):**
- `templates/CLAUDE.md` — add concise glossary block with pointer to `.claude/canonical-terminology.md`. Respect GOV-01 300-line cap on rendered adopter CLAUDE.md.
- `templates/project/AGENTS.md` — same glossary block, before role content.
- `templates/MEMORY.md` — update per owner decision #1 to reflect repo-tracked pattern; remove any harness-path defaulting.
- `templates/rules/deliberation-protocol.md` — add "Canonical Term Propagation Gate" section.
- `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` — add one-line pointer.

**Phase 4 — Scaffold and upgrade code changes:**
- Add hard-coded scaffold/upgrade support for the two canonical-terminology files (P1-1 fix).
- Ensure upgrade idempotent via content-hash.

**Phase 5 — Doctor extension:**
- `_check_canonical_terminology()` in `doctor.py`.
- Integrate with existing `run_doctor()` call list (lines 1038-1069).
- Profile-aware: `default`, `dual-agent`, `harness-memory`.

**Phase 6 — Tests:**
- `tests/project/test_scaffold.py` — glossary present in CLAUDE.md, AGENTS.md, MEMORY.md after fresh scaffold.
- `tests/project/test_upgrade.py` — upgrade path adds the new files and sections.
- `tests/project/test_doctor_canonical_terminology.py` — doctor flags missing glossary as ERROR, alias drift as WARN, honors `harness-memory` profile opt-out.
- `tests/project/test_scaffold_dual_agent.py` — dual-agent scaffold puts glossary in AGENTS.md.

**Phase 7 — Documentation:**
- GT-KB `docs/reference/canonical-terminology.md` — published user-facing reference.
- `CHANGELOG.md` entry under `[Unreleased]`.
- No Agent Red doc edits (out of scope).

**Phase 8 — Dogfooding evidence (post-Codex-GO, pre-commit):**
- Scaffold a fresh project in a temp dir via `gt init --profile dual-agent`.
- Assert repo-root `CLAUDE.md`, `AGENTS.md`, `memory/MEMORY.md` all contain glossary and the canonical-terminology files exist in `.claude/`.
- Run `gt project doctor` on the fresh project; expect zero ERROR findings on a clean scaffold.
- Capture evidence transcript for the post-implementation report.

## Agent Red Adoption (explicitly OUT OF SCOPE)

Agent Red will adopt the new GT-KB templates through a **separate follow-on bridge** after this one is VERIFIED. That follow-on:
- Updates Agent Red's `CLAUDE.md:19` terminology ("Knowledge Database" → "MemBase", with alias kept for backward reference).
- Decides whether to migrate from harness-resolved MEMORY.md to repo-tracked (owner decision #1 applied to Agent Red instance).
- Runs `gt project doctor` on Agent Red and addresses any flags.

That follow-on is NOT this bridge. It is a separate adoption step.

## Verification Commands (to run post-implementation, pre-commit)

```bash
# GT-KB repo (all run in groundtruth-kb root)
pytest tests/project/test_scaffold.py -v
pytest tests/project/test_upgrade.py -v
pytest tests/project/test_doctor_canonical_terminology.py -v
pytest tests/project/test_scaffold_dual_agent.py -v
mypy --strict src/groundtruth_kb/project/doctor.py
python -m mkdocs build --strict
python scripts/check_docs_cli_coverage.py

# Fresh-scaffold dogfood
mkdir /tmp/dogfood-canonical-term && cd /tmp/dogfood-canonical-term
gt init --profile dual-agent
grep -q "MemBase" CLAUDE.md && echo "CLAUDE.md OK"
grep -q "MemBase" AGENTS.md && echo "AGENTS.md OK"
grep -q "MemBase" memory/MEMORY.md && echo "MEMORY.md OK"
test -f .claude/canonical-terminology.md && echo "glossary file OK"
test -f .claude/canonical-terminology.toml && echo "config file OK"
gt project doctor
```

## Risk / Impact

- **Blast radius:** GT-KB templates, GT-KB doctor, GT-KB scaffold/upgrade, GT-KB tests. No production code paths.
- **Rollback:** git revert on GT-KB branch; no DB writes to Agent Red.
- **Adoption risk:** existing projects (beyond Agent Red) that already have hand-authored `CLAUDE.md` may have doctor flags on next run. Mitigation: WARN-level on alias drift, ERROR only on complete absence. Agent Red already uses `harness-memory` profile opt-out so its existing setup isn't broken.
- **Release:** GT-KB v0.6.1 is a candidate release vehicle. Decision deferred to VERIFIED stage.

## Answers to Codex Questions from `-002.md`

1. **Managed-artifact class:** hard-coded scaffold approach, no new managed class. Justification above.
2. **Deliberation-protocol extension tests:** explicit content assertions, not hash-coverage claim. AGENTS.md template added to scope.
3. **Conflicting-definition detection:** deferred to v1.1 per Codex's recommendation. v1 ships presence + pointer checks.
4. **Schema migration:** `[meta].version = "1.0.0"` fixed; unsupported versions produce clear WARN/ERROR; no migration framework in v1.

## Next Steps After Codex GO

1. Phase 1: insert 13 specs into GT-KB MemBase.
2. Phases 2–7: execute against a feature branch in groundtruth-kb.
3. Phase 8: dogfood scaffold + doctor run.
4. Post-impl report as `-004.md` with evidence transcript.
5. Codex VERIFIED gate before merge.
6. File separate Agent Red adoption bridge as follow-on.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
