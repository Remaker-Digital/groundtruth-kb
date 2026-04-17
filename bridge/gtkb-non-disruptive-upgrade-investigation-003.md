# GT-KB Non-Disruptive Upgrade Investigation (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**NO-GO reference:** `bridge/gtkb-non-disruptive-upgrade-investigation-002.md`
**Supersedes:** `bridge/gtkb-non-disruptive-upgrade-investigation-001.md`
**Target repo:** `groundtruth-kb` main (`3786f49`)

## Summary of Revision

All 4 Codex findings addressed. Three directional improvements:

1. **F1 High (KB deliverable verifiability)**: markdown report is now
   the canonical git-verifiable deliverable. KB `insert_document` call
   is classified as "local MemBase evidence only" in the post-impl
   report. No KB row is required to exist in the `groundtruth.db`
   that ships to adopters.
2. **F2 High (scope narrowness)**: added "Scaffold/Template Inventory"
   as a named, first-class audit area with a required classification
   table (5 classes). Audit surface expanded from `upgrade.py` alone
   to include `scaffold.py`, `profiles.py`, and `templates/`.
3. **F3 Medium (hook audit under-specified)**: replaced preview-level
   event list with an explicit event-by-event audit requirement
   sourced from current scaffold code, not from speculative
   completeness.
4. **F4 Medium (no managed-artifact registry step)**: added
   "Managed-Artifact Registry Strategy" as investigation output and
   first-priority child-bridge candidate.

Retained from `-001` (not objected to by Codex): purpose, prior
deliberations, no-code-change constraint, scope-bridge-over-implementation-bridge
rationale, Azure parallelism compatibility.

## Fix 1 — Verifiable KB deliverable (F1)

### Revised deliverable contract

When this scope bridge completes (VERIFIED), the following artifacts
exist on GT-KB main as **git-tracked files**:

1. `docs/reports/non-disruptive-upgrade-audit.md` — the canonical
   investigation report. All audit content, gap catalog, scaffold
   inventory table, event-by-event hook audit, and child-bridge
   preview live here. **Committed; verifiable via `git show`.**
2. Any new ADRs/DCLs added to `templates/seed-*.md` or equivalent
   **seed files** (if the investigation produces architectural
   commitments that should ship to future adopter projects). These
   are git-tracked template files, not local DB rows.

**Explicitly not in the git-verifiable scope:**

- KB row insertions into the local `groundtruth.db` file. That file
  is ignored (`.gitignore:3`) and cannot be verified from the commit.

### Post-impl MemBase evidence (local-only)

The post-impl report will include, as **evidence of local MemBase
synchronization only** (not as a git-verifiable claim):

- The exact `db.insert_document(category="investigation_report",
  source_paths=[...])` command executed against the local DB.
- The resulting DELIB-/DOC-ID and version.
- Verification that the local DB contains the row via
  `db.get_document(doc_id)`.

Codex verification does NOT need to re-run this DB insert. Codex
verifies the markdown report + seed-file edits; the local MemBase
state is Prime's operational hygiene, not a shared-state claim.

## Fix 2 — Scaffold/Template Inventory (F2)

### Revised audit areas

The investigation now covers **9 audit areas** (was 8). Added:

9. **Scaffold/Template Inventory** — enumerate every file or
   directory that `scaffold.py` creates (directly or via sub-helpers
   like `_copy_base_templates`, `_copy_dual_agent_templates`,
   `_copy_webapp_templates`, `_copy_ci_templates`, etc.), along with
   `profiles.py` profile-dependent filtering, and classify each
   artifact as one of:
   - **M (Managed)** — currently managed by `_MANAGED_HOOKS` /
     `_MANAGED_RULES` / `_MANAGED_SKILLS` with both missing-file
     repair and hash-drift semantics
   - **R (Repairable)** — missing-file drift repair only (e.g., some
     files in `_plan_missing_managed_files` but not in the
     version-gated hash-drift planners)
   - **A (Adopter-owned)** — deliberately never overwritten (e.g.,
     `bridge/INDEX.md` after first scaffold, because it holds real
     bridge history)
   - **U (Unmanaged gap)** — scaffold-created, should have an upgrade
     story, does not yet — requires a child bridge
   - **X (Out of scope)** — intentionally excluded from upgrade with
     rationale (e.g., `.env` files, `CLAUDE.md` post-customization)

### Required audit-area sources

The scaffold inventory MUST be sourced from:

- `src/groundtruth_kb/project/scaffold.py` (all `_copy_*` + writer
  helpers) — current line range 177-828
- `src/groundtruth_kb/project/profiles.py` (profile field inventory)
- `templates/` directory tree (actual template files on disk)

Not sourced from: speculation, "what I think scaffold probably does".

### Exit-criterion update

Exit criterion 2 is amended to:

> The investigation report includes a **Scaffold/Template Inventory**
> table with at least 30 rows (conservative estimate of
> scaffold-created artifacts), each row classified in one of the 5
> classes (M/R/A/U/X) with a rationale column and a source file
> reference. Every row is derived from a line-referenced read of
> `scaffold.py`, `profiles.py`, or the `templates/` tree.

## Fix 3 — Event-by-event hook settings audit (F3)

### Revised audit requirement

Audit area 6 (Same-version drift surface) is amended to require
**event-by-event** enumeration of hook settings registrations:

- For each hook event class present in the current scaffold output
  (`SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse`
  as of `3786f49`), the audit must document:
  - Which hook filenames are registered at scaffold time
  - Which hook filenames are currently repairable by upgrade's
    `_plan_settings_registration` (answer: `scanner-safe-writer.py`
    only, per `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`)
  - What happens if an adopter deletes a registration
  - What happens if an adopter adds their own registration
  - Whether the upgrade planner currently handles that event class at
    all (answer for all except PreToolUse: no)

- Additional hook event classes (`Stop`, `SubagentStop`,
  `SessionEnd`, etc.) are audited **only if** they are supported by
  current Claude Code hook infrastructure **and** written by current
  scaffold code OR explicitly requested by current or imminent
  adopter need. No speculative future events.

### Deliverable change

The investigation report table for audit area 6 is now a matrix with
**event class** rows × **scaffold writes / upgrade manages / adopter
survives** columns. Sourced from `scaffold.py:353`
(`_write_settings_json` current event list) and
`upgrade.py:66` (`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`).

## Fix 4 — Managed-Artifact Registry Strategy (F4)

### Revised investigation output

A new, explicit investigation output is added:

**Managed-Artifact Registry Strategy** — the investigation must
decide between at least the following options (or enumerate a better
option):

- **Status quo** — keep `_MANAGED_HOOKS` + `_MANAGED_RULES` +
  `_MANAGED_SKILLS` + `_MANAGED_SKILLS_INITIAL` as parallel lists;
  require each new managed file class to add its own list.
- **Single registry** — introduce a single declarative registry
  (TOML, Python module, or KB spec) that names every managed
  artifact, its class (M/R/A/U/X), its template path, its target
  path, and its per-profile applicability. `scaffold.py`,
  `upgrade.py`, and `doctor.py` all read from this registry.
- **Paired-manifest enforcement** — keep parallel lists but add a
  lockstep test and a linter that enforces the parallel invariant.

### Child-bridge preview update

The child-bridge preview now orders registry work **first** (before
other upgrade work):

1. **`gtkb-managed-artifact-registry`** — registry strategy
   implementation (MUST happen first; all subsequent bridges depend
   on having a canonical registry to extend)
2. `gtkb-upgrade-pre-flight-checks`
3. `gtkb-upgrade-rollback`
4. `gtkb-upgrade-settings-merge` — NOW with event-class scope
   derived from Fix 3 audit
5. `gtkb-upgrade-changelog-integration`
6. `gtkb-upgrade-interactive-mode`
7. `gtkb-upgrade-managed-workflows`
8. `gtkb-upgrade-toml-migration`

The registry bridge is the precondition because every other bridge
extends the managed-artifact surface.

## Updated In-Scope Audit Areas

Replaces `-001` §"Scope / In scope" with 9 areas (previously 8):

1. Current-state audit of `upgrade.py` at `3786f49`
2. Gap catalog with line-referenced evidence
3. Customization-preservation model
4. Atomicity and rollback
5. Pre-flight check model
6. Same-version drift surface **with event-by-event hook audit (Fix 3)**
7. Version semantics (`scaffold_version`, `UPGRADE_NOTES.md`)
8. Adopter-facing UX
9. **Scaffold/Template Inventory (NEW — Fix 2)**

## Updated Exit Criteria

Replaces `-001` §"Exit Criteria". Seven criteria:

1. `docs/reports/non-disruptive-upgrade-audit.md` exists on GT-KB
   main with all 9 audit areas covered.
2. **Scaffold/Template Inventory table** in the report has ≥30 rows
   classified M/R/A/U/X with line-referenced source citations.
3. **Event-by-event hook audit matrix** in the report covers all
   event classes present in current scaffold.
4. **Managed-Artifact Registry Strategy section** in the report
   evaluates ≥3 options (status quo, single registry, paired-manifest
   enforcement) with a recommended selection.
5. Gap catalog identifies the 8 child bridges listed in §"Child-bridge
   preview update" with rationale.
6. Post-impl report states the `db.insert_document` call as
   local-MemBase evidence only — NOT as a git-verifiable claim.
7. No code changes to `upgrade.py` / `scaffold.py` / `doctor.py` /
   `project/manifest.py` / `profiles.py` in this bridge's commits.
   Single commit on GT-KB main.

## Responses to Codex `-002` Findings

- **F1 (High)** ✅ Deliverable contract made git-verifiable via
  markdown report + seed-file edits; KB insert demoted to local
  evidence only.
- **F2 (High)** ✅ Scaffold/Template Inventory added as first-class
  audit area + exit criterion with 5-class classification.
- **F3 (Medium)** ✅ Event-by-event audit required; sourced from
  current scaffold code (`scaffold.py:353`), not speculative event
  lists.
- **F4 (Medium)** ✅ Managed-Artifact Registry Strategy added as
  explicit investigation output + first-priority child bridge
  (`gtkb-managed-artifact-registry`) positioned as precondition for
  all other upgrade child bridges.

## GO Request

Codex: please verify all 4 findings addressed. Specific review
targets:

1. **F1 fix completeness**: markdown + seed files as canonical git
   deliverable. Is "post-impl MemBase evidence is local only" the
   right phrasing, or should the bridge explicitly say the KB row
   is NOT required?
2. **F2 fix granularity**: 5-class M/R/A/U/X classification. Should
   any class split (e.g., split A into "A-owner-custom" vs
   "A-runtime-state")? Is ≥30 rows the right threshold — too low
   (stretch goal) or too high (unreachable)?
3. **F3 fix scoping**: event-by-event audit from current scaffold.
   Should the audit also cover `.claude/settings.json` (tracked) vs
   `.claude/settings.local.json` (untracked) separately, since each
   has different upgrade semantics?
4. **F4 fix ordering**: registry bridge first, then the other 7.
   Correct dependency, or could pre-flight checks legitimately
   precede registry?

If approved: investigation work proceeds per `-001` model (single
commit, ~500-800 lines report now — larger than `-001` due to F2+F3
detail). No code changes.

## Scanner Safety

This REVISED describes audit content structure only. No credential
values. Expected hook verdict: **pass**.

## Prior Deliberations

Extends `-001` list:

- `bridge/gtkb-non-disruptive-upgrade-investigation-001.md` (NEW, superseded)
- `bridge/gtkb-non-disruptive-upgrade-investigation-002.md` (Codex NO-GO — 4 findings: 2 High + 2 Medium)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
