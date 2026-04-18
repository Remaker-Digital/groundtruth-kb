# GT-KB v0.6.1 Release Notes

**Release date:** 2026-04-17
**PyPI:** `pip install groundtruth-kb==0.6.1`
**Prior release:** v0.6.0 (2026-04-17)

## Highlights

v0.6.1 bundles three VERIFIED governance + adopter-experience feature
branches on top of v0.6.0's Phase A Tier A operational-skills bundle.
Together these ship the canonical-terminology governance surface, a rewritten
adopter-facing Start Here experience, live DA harvest coverage metrics,
and a declarative artifact-ownership matrix.

Thirteen merged commits (11 + 1 + 1 from three feature branches) plus two
follow-up integration commits (merge conflict resolution + test-baseline
alignment) under one release-prep commit.

## Adopter-visible changes

### Canonical terminology surface

Every fresh `gt project init` now scaffolds two new managed rule artifacts:

- `.claude/rules/canonical-terminology.md` — full ADR-0001 glossary (MemBase,
  Deliberation Archive, MEMORY.md, Knowledge Database, GroundTruth KB,
  GT-KB, Prime Builder, Loyal Opposition, plus the full
  `MEMBASE-4-CLAUDE.md` term set and alias disposition table).
- `.claude/rules/canonical-terminology.toml` — profile-aware doctor config
  (`local-only`, `dual-agent`, `dual-agent-webapp`, `harness-memory`).

`templates/CLAUDE.md` and `templates/project/AGENTS.md` gain concise
glossary blocks at the top so startup-visible orientation carries the
canonical vocabulary.

A new `gt project doctor` check validates terminology presence against the
profile-aware matrix. ERROR on missing canonical terms; WARN on minor
drift. Fresh adopter projects pass by construction; upgrading projects get
the files via `gt project upgrade --apply` idempotently.

### Adopter-facing Start Here rewrite

`docs/start-here.md`, `README.md`, `docs/day-in-the-life.md`,
`docs/evidence.md`, and `docs/known-limitations.md` rewritten for
**zero-context adopters**: new protagonist "Allison," Mermaid block
diagrams for the 14-entity workflow, refreshed day-in-life with six named
activities, evidence page with metrics collector and drift check, and
explicit Known Limitations with audit cross-links.

New reference page: `docs/reference/canonical-terminology.md`, with a
Mermaid diagram of the ADR-0001 three-tier memory architecture.

### DA harvest coverage helper + doctor check

New `gt project doctor` output computes thread-level DA harvest coverage
against `bridge/INDEX.md` + the `bridge/*.md` roll-up. Uncovered threads
surface as a regular doctor finding rather than only at session wrap.

### Artifact Ownership Matrix

New module `src/groundtruth_kb/project/ownership.py` exposes
`OwnershipResolver`, `OwnershipRecord`, and `ClassificationRow`. Every
managed artifact now carries an explicit ownership block
(`ownership` / `upgrade_policy` / `adopter_divergence_policy`) with five
ownership enum values, five upgrade-policy enum values, and three
divergence-policy enum values.

New CLI subcommand `gt project classify-tree` — manifest-independent
tree classifier that walks an arbitrary directory and writes an ownership
classification report, without requiring `groundtruth.toml` in the target
tree. Read-only dogfood proof: the classification run against Agent Red
produced byte-identical `git status --short` before and after.

New sibling file `templates/scaffold-ownership.toml` carries 8
`ownership-glob` rows for adopter-tree paths outside the registry.

## Technical changes

### Managed registry loader

`src/groundtruth_kb/project/managed_registry.py` now merges records from
both `templates/managed-artifacts.toml` (42 records, including the two
new canonical-terminology rule rows) and `templates/scaffold-ownership.toml`
(8 ownership-glob records) into a single list with enforced cross-file
`id` uniqueness. New `ownership-glob` artifact class. Existing
`artifacts_for_scaffold` / `artifacts_for_upgrade` / `artifacts_for_doctor`
helpers filter out `ownership-glob` rows so scaffold/upgrade/doctor
behavior remains bit-identical on the 40 pre-existing registry rows.

### Upgrade planner

`plan_upgrade` now consults each artifact's `OwnershipMeta` and skips rows
whose `upgrade_policy` is `preserve` / `transient` / `adopter-opt-in`.
Zero effect on current-HEAD behavior (all 42 rows use `overwrite` or
`structured-merge`), but unlocks preserve/transient semantics for future
adopter artifacts.

### Tests

1339 tests total (1300 pre-v0.6.1 + 39 new). Targeted coverage for
canonical-terminology doctor (16 tests), harvest coverage helper + doctor
(full coverage), ownership loader/resolver/scaffold/upgrade/doctor
isolation/CLI smoke (82 tests across 7 test files).

## Breaking changes

None.

## Upgrade path

From v0.6.0:

```bash
pip install --upgrade groundtruth-kb==0.6.1
gt project upgrade --apply
```

`gt project upgrade --apply` idempotently scaffolds the two new
canonical-terminology files into existing adopter projects via the
existing registry-driven `_plan_missing_managed_files` path. No manual
intervention required.

From v0.5.x: follow the v0.6.0 upgrade path first, then apply the v0.6.1
upgrade above.

## Release provenance

- Authorizing bridge: `bridge/gtkb-v061-release-006.md` (Codex GO)
- In-flight addenda: `-010` (test count fix) + `-012` (three baseline
  fixes)
- Merge commits: `32e625f` (start-here+canonical-terminology),
  `323bd9f` (harvest-coverage), `4e010ea` (ownership-matrix)
- Integration commit: `91e63b1` (test baseline post-canonical updates)
- Release-prep commit: this release's `chore(release)` commit

## Out of scope for this release

Deferred to v0.6.2 or later tracks:

- `gtkb-da-governance-completeness-implementation-016` GO — hook family
  (delib-preflight-gate, owner-decision-capture, turn-marker,
  wrap-gate coverage assertion, gov09-capture); authorized but not yet
  implemented.
- `gtkb-rollback-receipts-008` NO-GO — still in bridge review cycle.
- `gtkb-session-start-orientation-gate-001` — filed S300, awaiting
  governance-completeness VERIFIED before Codex review.
- Agent Red adoption of v0.6.1 — separate downstream bridge after this
  release VERIFIED.
- Stale "40-row" narration cleanup in `src/groundtruth_kb/project/upgrade.py`
  and adjacent test files — hygiene item noted in `-012` N2; non-behavioral.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
