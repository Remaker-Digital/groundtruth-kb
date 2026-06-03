NEW

bridge_kind: implementation_proposal
Document: gtkb-hygiene-sweep-presence-patterns-slice-1
Version: 001
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER
Work Item: WI-4249
Owner Decision: DELIB-20260623
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# Hygiene-sweep presence-mode + expanded patterns (WI-4249)

## Summary

Implement WI-4249: expand `gt hygiene sweep` detection coverage for three
recurring transcript-observed drift classes — `snapshots_non_manifest`
self-recursion, runtime residue paths (e.g. `$base/PASS/bridge/.claude`), and
pytest basetemp ACL contamination. Detection/reporting only; remediation stays
child-bridge-gated (WI-4259 is the parallel remediation item).

A scoping discovery against the live engine: `hygiene/sweep.py:scan_file`
emits a `Finding` **only** on a `content_patterns` regex hit within a matched
file. A pattern with `file_globs` but no `content_patterns` scans the file and
emits nothing — there is no presence detection. Two of WI-4249's three classes
(runtime residue paths, pytest basetemp residue) are **path-presence**
detections (the file's existence is the finding). So this slice adds a
presence-detection mode to the engine, then the three patterns, then tests.

## Scope

### (a) Engine: presence-detection mode (`hygiene/sweep.py`)

- Add an optional `match_mode` field to the `Pattern` dataclass (default
  `"content"`; new value `"presence"`), read by `load_pattern_set` from an
  optional `match_mode` TOML key (back-compatible: absent → `"content"`).
- In `run_sweep`/`scan_file`: when `match_mode == "presence"`, emit one
  `Finding` per file matching `file_globs` (and not excluded), with `line = 0`
  and `matched_excerpt` = the relative path. No content read is required.
  `match_mode == "content"` behavior is unchanged (regression-protected).
- Validation: a `presence` pattern with non-empty `content_patterns` is
  accepted but the content_patterns are ignored for presence (documented);
  a `content` pattern with empty `content_patterns` remains a no-op as today.

### (b) Patterns: three new `[[patterns]]` entries (`hygiene-sweep-patterns.toml`)

1. `runtime-residue-paths` (presence) — `file_globs` for runtime residue under
   sweep roots (e.g. `**/PASS/bridge/.claude/**`, other transcript-observed
   residue), `class = "runtime_residue"`, with `exclusion_globs` for legitimate
   `.claude/` etc.
2. `pytest-basetemp-acl` (presence) — `file_globs` for pytest basetemp residue
   committed into the tree, `class = "runtime_residue"`.
3. `snapshots-non-manifest-recursion` (content or presence per implementation
   finding) — detect snapshot artifacts that self-recurse / are not manifest-
   listed, `class = "config_drift"`. The exact match mode is finalized during
   implementation against a real residue sample; the verification plan covers
   whichever mode is used.

Each entry carries `description`, `classification`, `remediation_hint`, and
`exclusion_globs` per the existing schema. Remediation hints point at WI-4259
(scanner-owned artifact severity) for the wrap-scan-noise class.

### (c) Tests (`groundtruth-kb/tests/test_hygiene_sweep_patterns.py`, new)

Engine presence-mode behavior + the three patterns, against temp-tree fixtures.
Read-only against the repo; tests build their own temp roots.

## Owner Decisions / Input

- The owner this session redirected from the contended operational-load CLI
  thread to the hygiene cluster as the next work; `DELIB-20260623` ("tackle the
  5") authorizes WI-4249.
- Implementation authorized by
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` (active;
  includes WI-4249; allowed mutations `source`, `test_addition`,
  `config_change`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/tracked through the file bridge;
  `bridge/INDEX.md` is canonical for this thread's lifecycle.
- `GOV-STANDING-BACKLOG-001` — WI-4249 is a governed backlog item.
- `GOV-08` — sweep findings reflect real repository drift state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the
  hygiene-cluster PAUTH.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — extends the deterministic
  hygiene-sweep discovery surface rather than per-instance manual investigation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the pattern registry is a governed
  config artifact; this slice extends it via the bridge GO/VERIFIED cycle (the
  `config/governance/*.toml` registries are outside the narrative-artifact gate
  per `config/governance/narrative-artifact-approval.toml` `excluded_by_design`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision; the hygiene
  cluster is the post-CLI work.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic discovery surface.
- The `gt hygiene sweep` CLI thread (`gtkb-hygiene-sweep-cli`, VERIFIED at -004)
  — established the engine + the `hygiene-sweep-patterns.toml` registry this
  slice extends; surface/test precedent.
- WI-4259 (`gtkb`-tracked) — the parallel scanner-owned-artifact remediation
  this detection feeds; out of scope here (detection only).

## target_paths

- `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` (modify — presence-mode)
- `config/governance/hygiene-sweep-patterns.toml` (modify — 3 new patterns)
- `groundtruth-kb/tests/test_hygiene_sweep_patterns.py` (new — tests)

**No `groundtruth.db` / MemBase mutation:** this slice is detection/reporting
only. `gt hygiene sweep` is read-only against the repo and writes only to its
own `.gtkb-state/hygiene-sweep/<run-id>/` output; no `work_items`, spec,
deliberation, or membership rows are written. `groundtruth.db` is deliberately
absent from `target_paths` (the KB-mutation-completeness checkpoint is satisfied
by this confirmation).

## Requirement Sufficiency

**Existing requirements sufficient.** WI-4249's description is the operative
requirement; `GOV-STANDING-BACKLOG-001`, `GOV-08`, and `DELIB-S312` govern. No
new specification capture required.

## Design (reuse-first)

The presence-mode is the minimal engine addition: one optional dataclass field
+ a branch in the scan loop that emits a path-presence `Finding` when
`match_mode == "presence"`. The TOML schema gains one optional key
(`match_mode`), back-compatible with all existing content patterns (absent →
`content`). No change to `emit_json`/`emit_markdown`/CLI wiring.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| presence-mode emits on file match | `test_presence_mode_emits_finding_per_matched_file` | a `presence` pattern emits one Finding per matched file (line=0, excerpt=path), no content read |
| content-mode unchanged (regression) | `test_content_mode_unchanged` | existing content patterns still emit only on regex hits; empty content_patterns + content mode = no findings |
| back-compat TOML load | `test_pattern_without_match_mode_defaults_content` | a pattern with no `match_mode` loads as `content` |
| runtime-residue detection | `test_runtime_residue_paths_detected` | residue path under a temp root is reported; legitimate excluded paths are not |
| pytest-basetemp detection | `test_pytest_basetemp_residue_detected` | basetemp residue file is reported |
| snapshots-non-manifest detection | `test_snapshots_non_manifest_detected` | a self-recursing/non-manifest snapshot residue is reported |
| `GOV-08` real-state | `test_clean_tree_has_no_findings` | a clean temp tree yields zero findings for the new patterns |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_hygiene_sweep_patterns.py -q`
plus `ruff check` and `ruff format --check` on the changed Python files. All
tests build temp trees; none mutate the live repo or `groundtruth.db`.

## Acceptance Criteria

1. `Pattern` supports `match_mode` (`content` default, `presence` new); load is
   back-compatible (absent key → `content`).
2. `presence` patterns emit one Finding per matched, non-excluded file; content
   patterns behave exactly as before.
3. The three new patterns are added to `hygiene-sweep-patterns.toml` and detect
   their classes against temp-tree fixtures with no false positives on a clean
   tree.
4. New test module passes; `ruff check` + `ruff format --check` clean.
5. Pre/post bridge preflights pass (no missing required specs; 0 blocking gaps).
6. Detection only: no remediation/source-mutation of the detected residue in
   this slice (that is WI-4259).

## Risks / Rollback

- **Risk: presence patterns over-match** (flag legitimate `.claude/` etc.).
  Mitigation: `exclusion_globs` per pattern + a clean-tree no-findings test;
  patterns are report-only (no remediation), so a false positive is noise, not
  damage.
- **Risk: engine change regresses content-mode.** Mitigation: explicit
  content-mode-unchanged regression test + back-compat load test.
- **Rollback:** engine field + scan branch, 3 TOML entries, one test file;
  clean `git revert`. Report-only; no canonical-state mutation.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/hygiene/`,
`config/governance/`, `groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (engine capability + detection patterns + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
