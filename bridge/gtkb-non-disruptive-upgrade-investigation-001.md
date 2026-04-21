# GT-KB Non-Disruptive Upgrade Investigation (Scope Bridge)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Target repo:** `groundtruth-kb`
**Phase A gate:** All six Tier A bridges VERIFIED; v0.6.0 shipped to PyPI VERIFIED at `-006`.
**Owner authorization:** S299 Option C (`DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL`) — this bridge and `gtkb-azure-enterprise-readiness-taxonomy-001` run in parallel after Phase A.

## Purpose

Scope the investigation of GT-KB's non-disruptive upgrade capability
**before** implementing any changes. Goal: the CTO's adopter
environment can receive a new GT-KB release (v0.7.x, v0.8.x, …)
without losing customizations, breaking in-flight bridges, requiring
re-scaffold, or introducing silent inert-hook states.

This is an **investigation and scoping** bridge, not an
implementation bridge. The output is a taxonomy of upgrade concerns,
a current-state audit, and a catalog of gap-specific child bridges
that would implement the repairs. No upgrade-code changes are
proposed in this scope.

## Prior Deliberations

- `memory/project_gtkb_non_disruptive_upgrade_priority.md` (owner
  S298 directive — pre-Azure priority)
- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner S299 decision —
  parallel with Azure taxonomy)
- `bridge/gtkb-hook-scanner-safe-writer-010.md` (NO-GO that forced
  introduction of `_plan_missing_managed_files` — first down-payment
  on non-disruptive upgrade)
- `bridge/gtkb-skill-decision-capture-009.md` (NO-GO that extended
  missing-file repair to skills)

## Scope

### In scope for this investigation bridge

1. **Current-state audit** of `src/groundtruth_kb/project/upgrade.py`
   as of v0.6.0 (`3786f49`). Catalogue what `gt project upgrade` does
   today, what file classes it manages, what drift it repairs, and
   what it skips.
2. **Gap catalog** — enumerate all upgrade concerns **not yet
   addressed** by current behavior, with evidence (line references
   to current source).
3. **Customization-preservation model** — document the current
   skip-if-drift-unless-force contract; identify cases where it fails
   (e.g., adopter-extended managed file) and propose named gaps.
4. **Atomicity and rollback** — audit what happens if
   `execute_upgrade()` fails partway; document `.bak` behavior and
   identify gaps (no rollback command, no transaction).
5. **Pre-flight check model** — what should `gt project upgrade
   --dry-run` verify BEFORE modifying anything? (Git state, in-flight
   bridges, settings.json parseability, backup dir writability,
   profile change detection.)
6. **Same-version drift surface** — catalog ALL classes of drift that
   can exist at current scaffold version (hook registrations,
   gitignore patterns, settings.json shape, skill files, rule files,
   bridge rules, workflow files, BRIDGE-INVENTORY.md, MemBase
   schema, `groundtruth.toml` schema).
7. **Version semantics** — document current `scaffold_version`
   semantics, identify gaps (no UPGRADE_NOTES.md, no breaking-change
   annotation).
8. **Adopter-facing UX** — audit the current `gt project upgrade
   --dry-run` / `--apply` output against adopter-centric usability
   criteria.

### Out of scope (deferred to child bridges)

1. Any code changes to `upgrade.py`, `scaffold.py`, `doctor.py`, or
   manifest/config code.
2. New CLI sub-commands (e.g., `gt project upgrade --rollback`).
3. Test additions beyond what's needed to verify the investigation.
4. Documentation writes beyond this scope bridge and its ultimate
   investigation-report document.
5. Migration scripts for existing adopter projects.
6. Azure-related upgrade concerns (those are Azure taxonomy scope).

## Investigation deliverables

When this scope bridge completes (VERIFIED), the following artifacts
exist on GT-KB main:

1. **Investigation report document** at
   `docs/reports/non-disruptive-upgrade-audit.md` — enumerates
   current state, gaps, and recommended child-bridge scopes with
   priority ordering.
2. **Gap catalog** as a KB document (category:
   `investigation_report`) with per-gap severity, dependency
   ordering, and candidate child-bridge names.
3. **Assertion registry updates** (if any): `architecture_decision`
   type specs (ADRs) for new upgrade-specific architectural
   commitments, with machine-checkable `design_constraint` (DCL)
   entries where the commitment is assertable.
4. **No code changes** in this scope bridge. Subsequent child bridges
   implement repairs.

## Proposed child-bridge sequence (preview only — not authorized by this GO)

This scope bridge, when GO'd and executed, will propose a sequence
of child bridges for implementation. Anticipated shape:

1. `gtkb-upgrade-pre-flight-checks` — add `gt project upgrade
   --dry-run` pre-flight guards (git state, parseability, backup
   readiness, in-flight-bridge detection)
2. `gtkb-upgrade-rollback` — add `gt project upgrade --rollback`
   command + transaction/backup model
3. `gtkb-upgrade-settings-merge` — generalize `settings.json` merge
   beyond PreToolUse to PostToolUse/Stop/UserPromptSubmit hook
   classes; preserve adopter-added entries
4. `gtkb-upgrade-changelog-integration` — pull release CHANGELOG
   into `gt project upgrade --dry-run` output; add
   `UPGRADE_NOTES.md` convention
5. `gtkb-upgrade-interactive-mode` — `gt project upgrade
   --interactive` for choose-per-file adoption
6. `gtkb-upgrade-managed-workflows` — extend managed-file class to
   `.github/workflows/*.yml` (with skip-if-customized semantics)
7. `gtkb-upgrade-toml-migration` — `groundtruth.toml` schema
   migration support

Order is dependency-informed but not fixed; final sequence lives in
the investigation report.

## Exit Criteria (for this scope bridge)

1. `docs/reports/non-disruptive-upgrade-audit.md` exists with the
   investigation content.
2. Investigation report catalogues all 8 in-scope audit areas with
   line-referenced evidence from current `3786f49` source.
3. Gap catalog identifies at least the 7 candidate child bridges
   (above or equivalents) with rationale.
4. KB document entry for the investigation report registered via
   `db.insert_document(category="investigation_report")`.
5. ADR entries added for any new architectural commitments needed
   for the child bridges.
6. No code changes to `upgrade.py` / `scaffold.py` / `doctor.py` /
   `project/manifest.py` in this bridge's commits.
7. Single commit on GT-KB main: `docs(upgrade):
   non-disruptive-upgrade investigation scope + gap catalog` or
   equivalent.

## Why this is a scope bridge, not an implementation bridge

The investigation surface is broad (8 audit areas) and each area
deserves its own focused implementation review. Packaging the
investigation + 7 implementation changes in a single bridge would
produce a proposal that's too large to review meaningfully and a
commit that's too large to roll back cleanly.

Scope-bridge-first is the established pattern
(`bridge/gtkb-operational-skills-tier-a-003.md` → scope GO → 6
child bridges).

## GO Request

Codex: please review this investigation scope for:

1. **Audit area completeness** — are 8 areas enough? Missing any
   upgrade concern (e.g., cross-platform path differences,
   concurrent-upgrade safety, pip-install-time checks)?
2. **Deliverable granularity** — investigation report + gap catalog
   + ADRs. Is a separate machine-checkable DCL per ADR required?
   Or is the investigation report sufficient for Phase A of the
   workstream?
3. **Child-bridge preview accuracy** — are the 7 anticipated child
   bridges well-partitioned (disjoint scope) or should any be merged
   or split?
4. **Ordering** — should any child bridge happen first as a
   precondition for the others (e.g., pre-flight checks block
   everything else)?
5. **Azure parallelism** — does this investigation have any
   dependency on the Azure taxonomy bridge (parallel per Option C)
   that should be explicit here?

If approved: investigation work proceeds. Expected single commit
with the audit report + KB document insert + any new ADRs/DCLs.
Approximate 300-500 lines of new prose in the report.

## Scanner Safety

Pre-flight scan: this proposal describes upgrade concerns in prose
only. No literal credential values. Expected hook verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
