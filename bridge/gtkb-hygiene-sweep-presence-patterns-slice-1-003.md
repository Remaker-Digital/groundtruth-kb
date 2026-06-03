REVISED

bridge_kind: implementation_proposal
Document: gtkb-hygiene-sweep-presence-patterns-slice-1
Version: 003
Responds to: bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-002.md NO-GO
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

# Response to NO-GO -002

## F1 (-002, P2) — missing advisory specs — CORRECTED

Added `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to Specification Links. Re-running the
applicability preflight now yields empty `missing_required_specs` and
`missing_advisory_specs`.

## F2 (-002, P1) — unresolved WI-3469 dependency — CORRECTED (scope deferral)

WI-4249's backlog row declares `depends_on_work_items: [WI-3420, WI-3421,
WI-3469]`. WI-3420/WI-3421 are resolved; **WI-3469 is open** ("Reclaim
`.pytest-tmp/` from ACL contamination by parallel-session python") — the same
pytest-basetemp ACL class this proposal's third pattern would detect.

**Resolution: defer the pytest-basetemp detection class out of this slice.** This
slice now scopes to the two dependency-free classes — runtime residue paths and
`snapshots_non_manifest` self-recursion. The pytest-basetemp detection pattern
moves to a follow-on sub-slice, after the WI-3469 relationship is reconciled.
This removes the entangled class from scope, so the F2 ordering question no
longer gates this slice.

**Dependency-direction observation (flagged, not acted on):** WI-3469 is
*remediation* (reclaim contaminated `.pytest-tmp/`); pytest-basetemp *detection*
normally *enables* remediation rather than depending on it, so the declared
`WI-4249 depends_on WI-3469` edge appears reverse-modeled. I am NOT changing the
metadata (that is a separate authorized MemBase operation); I flag it for
owner/metadata reconciliation and sidestep it here by deferral.

## Summary

Implement WI-4249 (this slice): add a presence-detection mode to the
`gt hygiene sweep` engine, then two new detection patterns — runtime residue
paths and `snapshots_non_manifest` self-recursion. Detection/reporting only;
remediation stays child-bridge-gated (WI-4259). The pytest-basetemp class is
deferred (see F2 above). Engine discovery from -001 stands: `scan_file` emits
findings only on content-pattern hits, so path-presence classes require the
presence-mode extension.

## Scope (this slice)

### (a) Engine: presence-detection mode (`hygiene/sweep.py`)

- Add optional `match_mode` to the `Pattern` dataclass (default `"content"`;
  new `"presence"`), read by `load_pattern_set` from an optional TOML key
  (absent → `"content"`, back-compatible).
- In the scan flow: `match_mode == "presence"` emits one `Finding` per matched,
  non-excluded file (`line = 0`, `matched_excerpt` = relative path); no content
  read. `"content"` behavior unchanged (regression-protected).

### (b) Patterns: two new `[[patterns]]` (`hygiene-sweep-patterns.toml`)

1. `runtime-residue-paths` (presence) — `file_globs` for runtime residue
   (e.g. `**/PASS/bridge/.claude/**` and other transcript-observed residue),
   `class = "runtime_residue"`, with `exclusion_globs` for legitimate `.claude/`.
2. `snapshots-non-manifest-recursion` — detect snapshot artifacts that
   self-recurse / are not manifest-listed, `class = "config_drift"`. Match mode
   finalized during implementation against a real residue sample.

### Deferred to a follow-on sub-slice (NOT this slice)

`pytest-basetemp-acl` detection — deferred pending WI-3469 reconciliation
(F2 above).

## Owner Decisions / Input

- The owner this session redirected from the contended operational-load CLI
  thread to the hygiene cluster; `DELIB-20260623` ("tackle the 5") authorizes
  WI-4249.
- Implementation authorized by
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` (active;
  WI-4249; `source`, `test_addition`, `config_change`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/tracked through the file bridge;
  `bridge/INDEX.md` is canonical for this thread's lifecycle.
- `GOV-STANDING-BACKLOG-001` — WI-4249 is a governed backlog item.
- `GOV-08` — sweep findings reflect real repository drift state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the
  hygiene-cluster PAUTH.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — extends the deterministic
  hygiene-sweep discovery surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the pattern registry is a governed
  config artifact extended via the bridge GO/VERIFIED cycle
  (`config/governance/*.toml` registries are outside the narrative-artifact gate
  per `narrative-artifact-approval.toml` `excluded_by_design`).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the detection→backlog→remediation
  trace: this slice is the detection surface feeding WI-4259 remediation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — recurring drift detection is a
  lifecycle trigger for follow-on remediation work items.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision; hygiene cluster
  is the post-CLI work.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic discovery surface.
- `DELIB-2679` — verified `gt hygiene sweep` CLI baseline (the engine this slice
  extends); `DELIB-2675`/`DELIB-2673` — hygiene-sweep skill context.
- WI-4259 — the parallel scanner-owned-artifact remediation this detection feeds
  (out of scope here; detection only).
- WI-3469 — open pytest-tmp ACL remediation; the deferred pytest-basetemp class
  relates to it (see F2).

## target_paths

- `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` (modify — presence-mode)
- `config/governance/hygiene-sweep-patterns.toml` (modify — 2 new patterns)
- `groundtruth-kb/tests/test_hygiene_sweep_patterns.py` (new — tests)

**No `groundtruth.db` / MemBase mutation:** detection/reporting only;
`gt hygiene sweep` is read-only against the repo and writes only its own
`.gtkb-state/hygiene-sweep/<run-id>/` output. `groundtruth.db` is deliberately
absent from `target_paths`.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-4249's description is the operative
requirement; `GOV-STANDING-BACKLOG-001`, `GOV-08`, and `DELIB-S312` govern. No
new specification capture required.

## Design (reuse-first)

Presence-mode is one optional dataclass field + a branch in the scan loop
emitting a path-presence `Finding`. The TOML gains one optional `match_mode`
key, back-compatible with all existing content patterns. No change to
`emit_json`/`emit_markdown`/CLI wiring.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| presence-mode emits on file match | `test_presence_mode_emits_finding_per_matched_file` | one Finding per matched file (line=0, excerpt=path), no content read |
| content-mode unchanged (regression) | `test_content_mode_unchanged` | content patterns still emit only on regex hits; empty content_patterns + content mode = no findings |
| back-compat TOML load | `test_pattern_without_match_mode_defaults_content` | a pattern with no `match_mode` loads as `content` |
| runtime-residue detection | `test_runtime_residue_paths_detected` | residue path under a temp root is reported; excluded legitimate paths are not |
| snapshots-non-manifest detection | `test_snapshots_non_manifest_detected` | a self-recursing/non-manifest snapshot residue is reported |
| `GOV-08` real-state | `test_clean_tree_has_no_findings` | a clean temp tree yields zero findings for the new patterns |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_hygiene_sweep_patterns.py -q`
plus `ruff check` and `ruff format --check`. Tests build temp trees; none mutate
the live repo or `groundtruth.db`.

## Acceptance Criteria

1. `Pattern` supports `match_mode` (`content` default, `presence` new);
   back-compatible load.
2. `presence` patterns emit one Finding per matched, non-excluded file; content
   patterns behave exactly as before.
3. The two new patterns (runtime-residue, snapshots-non-manifest) detect their
   classes against temp-tree fixtures with no false positives on a clean tree.
4. The pytest-basetemp class is NOT in this slice (deferred per F2).
5. New test module passes; `ruff check` + `ruff format --check` clean.
6. Pre/post bridge preflights pass (no missing required OR advisory specs;
   0 blocking gaps).
7. Detection only: no remediation/source-mutation of detected residue.

## Risks / Rollback

- **Risk: presence patterns over-match.** Mitigation: `exclusion_globs` +
  clean-tree no-findings test; report-only, so a false positive is noise.
- **Risk: engine change regresses content-mode.** Mitigation: content-mode
  regression test + back-compat load test.
- **Rollback:** engine field + scan branch, 2 TOML entries, one test file; clean
  `git revert`. Report-only; no canonical-state mutation.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/hygiene/`,
`config/governance/`, `groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (engine capability + detection patterns + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
