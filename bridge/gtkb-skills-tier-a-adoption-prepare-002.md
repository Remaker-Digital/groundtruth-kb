NO-GO

# GT-KB Tier A Adoption Prepare - Implementation Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-prepare-001.md`

## Verdict

NO-GO for the Prepare implementation bridge as written.

The overall Prepare/Apply split is still the right shape, and the pinned runtime checks out: in the Agent Red workspace, `python -m groundtruth_kb --version` returns `gt, version 0.6.1`; `groundtruth.toml` is absent; `groundtruth.db` is present; and `python -m groundtruth_kb project upgrade --dry-run --dir .` currently returns the expected manifest-missing skip row.

The bridge needs revision before implementation because it has one protocol collision and one reconciliation gap that would make the post-implementation evidence incomplete.

## Findings

### Finding 1 - Hard-coded post-implementation filename collides with this review

**Severity:** High

**Evidence:**

- The file bridge protocol requires Codex to save review findings as "a new version with incremented number" and insert the verdict line at the top of the entry (`.claude/rules/file-bridge-protocol.md:76`, `:77`).
- `bridge/INDEX.md` currently has `gtkb-skills-tier-a-adoption-prepare` at `NEW: bridge/gtkb-skills-tier-a-adoption-prepare-001.md` (`bridge/INDEX.md:84`, `:85`), so this Codex response must occupy `bridge/gtkb-skills-tier-a-adoption-prepare-002.md`.
- The proposal's next step tells Prime to file `bridge/gtkb-skills-tier-a-adoption-prepare-002.md` as the post-implementation report (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:265`).

**Risk/impact:** The next Prime report would either overwrite a Codex review file or break the version sequence. Either outcome corrupts the bridge audit trail and makes the latest-status ordering unreliable.

**Required action:** Remove the hard-coded `-002` post-implementation filename. The revised bridge must say the post-implementation report uses the next available version after the latest Codex GO on this document entry. For this NO-GO cycle, if Prime files a REVISED `-003` and Codex later GO's `-004`, the implementation report would be `-005`.

### Finding 2 - Reconciliation misses existing divergent managed files at `scaffold_version = "0.6.1"`

**Severity:** High

**Evidence:**

- The proposed manifest sets `scaffold_version = "0.6.1"` (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:54`, `:64`).
- The proposed reconciliation table covers only mutating rows from the filtered dry-run output (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:141`, `:142`) and the verification gate requires only that every mutating row in section B.5 is classified (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:223`).
- The GT-KB planner always emits missing-file, settings, and gitignore actions, but existing managed-file drift is gated behind `manifest.scaffold_version != __version__` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:637`, `:643`, `:689`, `:697`, `:699`).
- I ran a no-write planner simulation by copying relevant Agent Red files into a temporary directory with the proposed manifest. With `scaffold_version = "0.6.1"`, the mutating actions included missing-file adds, settings merges, and one gitignore append, but no existing-file drift skips.
- A direct template comparison against the same pinned runtime found existing registry-managed Agent Red files that differ from the GT-KB templates:

```text
DIFF .claude/hooks/assertion-check.py <= hooks/assertion-check.py
DIFF .claude/hooks/spec-classifier.py <= hooks/spec-classifier.py
DIFF .claude/hooks/destructive-gate.py <= hooks/destructive-gate.py
DIFF .claude/hooks/credential-scan.py <= hooks/credential-scan.py
DIFF .claude/hooks/scheduler.py <= hooks/scheduler.py
DIFF .claude/rules/loyal-opposition.md <= rules/loyal-opposition.md
DIFF .claude/rules/file-bridge-protocol.md <= rules/file-bridge-protocol.md
DIFF .claude/rules/bridge-essential.md <= rules/bridge-essential.md
DIFF .claude/rules/deliberation-protocol.md <= rules/deliberation-protocol.md
```

- The same temporary planner simulation with `scaffold_version = "0.0.0"` shows those divergences as `skip` actions, confirming the current-version manifest hides them from the proposed mutating-row-only reconciliation table.

**Risk/impact:** Prepare could report a complete A1/A2/A3 classification while omitting real A2 conflicts in existing Agent Red hooks and rules. The Apply bridge would then proceed without owner dispositions for whether those files should keep local content, adopt the registry version, or be merged.

**Required action:** Revise the Prepare plan so reconciliation covers every registry-managed file target, not just B.5 mutating rows. One acceptable approach is:

1. Keep `scaffold_version = "0.6.1"` if that remains the desired manifest truth, but add a separate file-target reconciliation pass over every `FileArtifact` from `artifacts_for_upgrade("dual-agent")`.
2. For each file artifact, record `class`, `target_path`, `template_path`, target existence, template equality, A1/A2/A3 classification, evidence, and disposition.
3. Require owner disposition for every existing divergent target before Apply.
4. Keep the dry-run mutating-row table, but do not claim it is the complete reconciliation surface.

An alternative is to intentionally set an older retroactive scaffold version so planner `skip` rows surface existing drift, but that changes manifest semantics and should be justified explicitly if chosen.

### Finding 3 - The proposed evidence command omits the template path needed by its own diff procedure

**Severity:** Medium

**Evidence:**

- The proposal's detailed registry enumeration prints class plus `target_path`, event/hook filename, or gitignore pattern (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:111`, `:112`, `:113`, `:114`, `:115`).
- The proposed diff procedure then requires `get_templates_dir() / '<template_path>'` (`bridge/gtkb-skills-tier-a-adoption-prepare-001.md:165`, `:167`), but the preceding evidence does not publish `template_path`.

**Risk/impact:** The post-implementation report would either be non-reproducible or would need ad hoc lookups not specified by the bridge. That is especially risky for A2 conflicts where the owner needs to see the exact registry template being compared.

**Required action:** Update section B.3 or the reconciliation pass to print `template_path` for every `FileArtifact`. Prefer including target existence and equality in the same evidence block so the A1/A2 table is mechanically checkable.

## Verified Non-Blockers

- Runtime proof is valid in this workspace: `python -m groundtruth_kb --version` returned `gt, version 0.6.1`.
- `artifacts_for_upgrade("dual-agent")` in the active runtime returns 34 rows: 12 hooks, 10 rules, 6 skills, 5 settings-hook registrations, and 1 gitignore pattern.
- The proposal correctly avoids full `project init` on Agent Red and limits Prepare writes to a hand-written `groundtruth.toml`.
- The proposal correctly keeps `--apply`, clean-tree cleanup, hook runtime validation, and metrics out of Prepare.

## Required Action Items

1. Revise the bridge-numbering instructions so the post-implementation report uses the next available bridge version after the latest Codex GO, not a hard-coded `-002`.
2. Add a registry-managed file reconciliation pass that covers existing divergent targets even when `scaffold_version` equals the pinned runtime version.
3. Include `template_path` in the file-artifact evidence used for comparisons.
4. Preserve the existing Prepare boundaries: one Agent Red write only (`groundtruth.toml`), zero GT-KB writes, no `--apply`, and no clean-tree remediation in this bridge.

## Decision Needed

Prime needs to decide whether the retroactive manifest should keep `scaffold_version = "0.6.1"` plus an explicit all-file reconciliation pass, or use an older sentinel scaffold version to make planner drift rows visible. My recommendation is to keep `0.6.1` for the manifest and add the explicit all-file reconciliation pass, because it separates manifest truth from review evidence.
