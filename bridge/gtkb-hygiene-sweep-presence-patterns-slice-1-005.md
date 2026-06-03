NEW

bridge_kind: implementation_report
Document: gtkb-hygiene-sweep-presence-patterns-slice-1
Version: 005
Responds to GO: bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-004.md
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

# Post-Implementation Report — Hygiene-sweep presence-mode + patterns (WI-4249)

## Summary

Implemented WI-4249 (this slice) per GO at `-004` (Codex LO), within the three
GO'd target paths. The hygiene-sweep engine gains a back-compatible
presence-detection mode, and two presence patterns (runtime-residue,
snapshots-non-manifest-recursion) are added to the registry. 10 spec-derived
tests pass; `ruff check` + `ruff format --check` clean. Detection/reporting
only; no MemBase mutation; pytest-basetemp deferred (WI-3469).

## Specification Links

Carried forward from `-003`; exercised below.

- `GOV-FILE-BRIDGE-AUTHORITY-001` — thread lifecycle recorded in INDEX.
- `GOV-STANDING-BACKLOG-001` — WI-4249 governed backlog item.
- `GOV-08` — sweep findings reflect real repository drift state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — under the hygiene-cluster PAUTH.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — extends the deterministic
  discovery surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — pattern registry extended via the
  bridge GO/VERIFIED cycle (config/governance .toml outside the narrative gate).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — detection feeds WI-4259 remediation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — recurring drift detection is a
  lifecycle trigger.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-hygiene-sweep-presence-patterns-slice-1
-> latest_status: GO; go_file: bridge/...-004.md; expires_at: 2026-06-04T01:44:38Z
```

## GO -004 Conditions — Satisfaction Evidence

1. **Two approved classes only.** Added `runtime-residue-paths` and
   `snapshots-non-manifest-recursion` to the registry; no other new pattern.
   `test_pytest_basetemp_class_not_present` asserts `pytest-basetemp-acl` is
   absent. **Satisfied.**
2. **No pytest-basetemp ACL detection.** Not added (deferred to WI-3469
   reconciliation). **Satisfied** (+ test above).
3. **Preserve content-pattern behavior (regression).**
   `test_content_mode_unchanged` + `test_content_mode_empty_content_patterns_emits_nothing`
   confirm content patterns still emit only on regex hits and empty
   content_patterns remain a no-op. **Satisfied.**
4. **Report-only.** `presence_finding` reads no content and mutates nothing; the
   sweep writes only its own `.gtkb-state/hygiene-sweep/<run-id>/` output. No
   residue is remediated/deleted/moved. **Satisfied.**

## Spec-to-Test Mapping / Verification Evidence

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_hygiene_sweep_patterns.py -q`
→ **10 passed in 0.33s**.

| Specification / GO condition | Test | Result |
|---|---|---|
| presence-mode emits per file (line 0, path excerpt) | `test_presence_mode_emits_finding_per_matched_file` | PASS |
| presence ignores content_patterns | `test_presence_mode_ignores_content` | PASS |
| back-compat: no `match_mode` → content | `test_pattern_without_match_mode_defaults_content` | PASS |
| invalid match_mode rejected | `test_invalid_match_mode_rejected` | PASS |
| GO-3 content-mode regression | `test_content_mode_unchanged`, `test_content_mode_empty_content_patterns_emits_nothing` | PASS |
| runtime-residue detection (real pattern) | `test_runtime_residue_paths_detected` | PASS |
| snapshots-non-manifest detection (real pattern) | `test_snapshots_non_manifest_detected` | PASS |
| `GOV-08` clean tree = no findings | `test_clean_tree_has_no_findings` | PASS |
| GO-1/GO-2 pytest-basetemp absent | `test_pytest_basetemp_class_not_present` | PASS |

Code-quality gates (changed Python): `ruff check` → **All checks passed!**;
`ruff format --check` → **2 files already formatted**.

Registry load smoke: `load_pattern_set` loads all 3 patterns
(`agent-red-config-drift`, `runtime-residue-paths`,
`snapshots-non-manifest-recursion`) without error.

## No-MemBase-Mutation Evidence

The implementation changes only the three target paths (sweep.py +36,
hygiene-sweep-patterns.toml +44, the new test module). `groundtruth.db` is not
touched; all tests construct temp trees + temp pattern sets and scan only those.
No `gt hygiene sweep` was run against the live repo during implementation.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` (+36 — `match_mode` field,
  validation, `presence_finding`, run_sweep branch)
- `config/governance/hygiene-sweep-patterns.toml` (+44 — 2 presence patterns)
- `groundtruth-kb/tests/test_hygiene_sweep_patterns.py` (new — 10 tests)

All three are the GO'd target paths; no other files touched.

## Owner Decisions / Input

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision authorizing the
  hygiene cluster under `PAUTH-...-HYGIENE-CLUSTER`.
- WI-3469 dependency: the pytest-basetemp class remains deferred; the apparent
  reverse-modeled `WI-4249 depends_on WI-3469` edge is flagged for separate
  reconciliation (not changed here).

## Recommended Commit Type

`feat` (engine capability + detection patterns + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
