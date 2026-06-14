NEW

bridge_kind: implementation_report
Document: gtkb-wi4528-sweep-commit-protected-hook-co-stage-helper
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6a1e343d-7ae5-43de-a96d-0378471459c4
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session (dispatch id 2026-06-14T15-01-21Z-prime-builder-B-b3c8f2); Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC
Responds to: bridge/gtkb-wi4528-sweep-commit-protected-hook-co-stage-helper-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4528
target_paths: ["scripts/sweep_commit_helpers.py", "platform_tests/scripts/test_sweep_commit_helpers.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4528 Implementation Report: Sweep-commit protected-hook co-stage planning helper

## Summary

Implemented the GO'd proposal (`-001`, Codex GO at `-002`) within the bounded
`source` + `test_addition` PAUTH scope. Two new in-root files:

- `scripts/sweep_commit_helpers.py` — pure-Python commit-batch planning module
  (~290 lines). Reads `config/governance/protected-artifact-inventory-drift.toml`
  declaratively, partitions a staged set, maps protected paths to their staged
  bridge review evidence, and returns ordered `CommitBatch` records guaranteeing
  every protected hook-config path is co-staged with bridge evidence (or is
  surfaced in a `protected-missing-evidence` diagnostic batch). No git
  invocation, no subprocess, no file mutation, no bridge writes, no KB mutation.
- `platform_tests/scripts/test_sweep_commit_helpers.py` — 14-test suite covering
  all eight acceptance criteria from the proposal Verification Plan plus
  supporting unit checks.

The implementation-start authorization packet was created from the live GO
(`packet_hash: sha256:f179e304a2cf03c79d1614dfe39f856e41aacdbaf9f90b13c5aa04faab4dea0b`)
before any protected edit.

## Specification Links

Carried forward from `-001` (all concretely linked, no placeholders):

- **GOV-STANDING-BACKLOG-001** — WI-4528 backlog authority. `CLAUSE-VISIBILITY-BULK-OPS`
  is `not_applicable`: single-WI scope, one new helper module + one test, no
  bulk operation and no inventory/approval-packet artifact required.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001**
  — proceeded under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2`
  (`source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge; the helper
  INSPECTS bridge artifacts read-only and never modifies `bridge/INDEX.md` or any
  bridge file or workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**,
  **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project /
  work-item / target-path metadata linked above.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — spec-to-test mapping
  below, every acceptance criterion mapped to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both target paths are in-root
  under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**,
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable tracked tooling
  artifact codifying the deterministic co-staging procedure.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner
  AUQ admitting WI-4528 under `PAUTH-…-BATCH-2`.
- **Cycle-13 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner chose
  "Seed both as scripts/ helpers", authorizing this scripts/ slice; skill-doc
  wiring deferred to a follow-on slice.
- The GO verdict (`-002`) and its five Conditions For Implementation Report,
  each addressed below.

## Owner Decisions / Input

This implementation is authorized by durable owner-decision evidence; no new
owner AskUserQuestion was required (and none is possible in an auto-dispatched
worker session).

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner
  AUQ (2026-06-13) admitting WI-4528 under `PAUTH-…-BATCH-2` (allowed: `source`,
  `test_addition`).
- **Cycle-13 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner
  selected "Seed both as scripts/ helpers", explicitly authorizing this scripts/
  slice in pure source+test PAUTH scope.

## GO Conditions — Disposition

1. **Pure planning (no git subprocess, no file mutation, no bridge writes, no KB
   mutation).** Satisfied. The module imports only `fnmatch`, `tomllib`,
   `dataclasses`, and `pathlib`. It performs read-only `.read_text()` on the
   inventory-drift TOML and on staged bridge files; there is no `subprocess`,
   `os.system`, git call, write/unlink, or KB import. `CommitBatch` execution
   (the `git commit -- <paths>`) is explicitly the orchestrator's job in the
   deferred wiring slice.
2. **Report includes pytest, ruff check, ruff format outputs.** See § Verification
   Evidence.
3. **Citation freshness.** The proposal's synthetic verification-plan fixture
   names (the `foo` / `a` / `b` placeholder thread names Codex flagged) are NOT
   used as live-looking citations anywhere in this report or in the implemented
   code. The test fixtures are created on disk under `tmp_path` and use a
   deliberately distinctive `wi4528-fixture-*` naming token that is documented
   in the test module docstring as synthetic; this report references only this
   thread's own live versions (`-001`, `-002`, `-003`). No unresolved real-looking
   bridge citation is carried into the report text.
4. **Declarative TOML read (not hardcoding `.codex/hooks.json`).** Confirmed by
   source inspection: `load_protected_path_globs(project_root)` opens
   `config/governance/protected-artifact-inventory-drift.toml`, iterates every
   `[[protected_artifacts]]` entry, keeps only those with
   `accept_with_inventory_baseline_update == false`, and unions their `patterns`
   list. The path set is never hardcoded. Two tests prove this:
   `test_protected_globs_read_from_toml` (a brand-new protected glob added only to
   a fixture TOML is returned and matched) and
   `test_baseline_update_entries_excluded_from_protected_globs` (an
   `accept=true` entry's patterns are excluded — only co-staged-evidence-required
   entries become protected globs). Note: the live schema field is `patterns`
   (the proposal §Design wrote `protected_paths`); the implementation reads the
   real `patterns` field.
5. **Skill-doc wiring out of scope.** Confirmed. No skill doc was touched; the
   helper is invoked-but-not-yet-wired and cannot affect existing sweep-commit
   behavior until the follow-on slice lands.

## Spec-to-Test Mapping (Specification-Derived Verification)

| Acceptance criterion (proposal) | Governing spec | Test in `test_sweep_commit_helpers.py` | Result |
|---|---|---|---|
| Protected hook-config + co-staged bridge evidence in SAME batch (WI-4528 root) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `test_protected_hook_with_bridge_evidence_grouped` | PASS |
| 2026-06-13 incident regression: protected hook with NO co-stageable evidence → clear diagnostic | DCL-VERIFIED-…-MANDATORY-001 | `test_missing_evidence_diagnostic` | PASS |
| `bridge/INDEX.md` co-stage is universal gate-satisfier | GOV-FILE-BRIDGE-AUTHORITY-001 | `test_index_md_is_universal_evidence` | PASS |
| Bridge-only files batch separately when not tied to a protected path | GOV-FILE-BRIDGE-AUTHORITY-001 | `test_unrelated_bridge_files_separate_batch` | PASS |
| Multiple protected paths each pair with their evidence | DCL-VERIFIED-…-MANDATORY-001 | `test_multiple_protected_paths_each_get_evidence` | PASS |
| Protected globs read declaratively from inventory-drift TOML (no hardcoding) | GOV-STANDING-BACKLOG-001 / GO condition 4 | `test_protected_globs_read_from_toml`, `test_baseline_update_entries_excluded_from_protected_globs` | PASS |
| Fail-soft when TOML missing (no commit-blocking exception) | GOV-RELIABILITY-FAST-LANE-001 (robustness) | `test_fail_soft_when_toml_missing`, `test_fail_soft_when_toml_malformed` | PASS |
| Real-world replay of the 2026-06-13 incident staged set | DCL-VERIFIED-…-MANDATORY-001 | `test_real_world_2026_06_13_incident_replay` | PASS |
| Supporting: partition buckets / bridge-evidence predicate / Windows backslash normalization / frozen dataclass | ADR-ISOLATION-APPLICATION-PLACEMENT-001 (cross-platform) | `test_partition_staged_buckets`, `test_is_bridge_evidence_path`, `test_windows_backslash_paths_normalized`, `test_commit_batch_is_frozen` | PASS |

## Verification Evidence

```text
$ python -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short
collected 14 items
platform_tests\scripts\test_sweep_commit_helpers.py ..............       [100%]
14 passed in 0.32s

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py
All checks passed!   (ruff 0.15.12)

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py
2 files already formatted
```

Note: one ruff finding was resolved during implementation — `B017` (blind
`pytest.raises(Exception)`) was tightened to `pytest.raises(dataclasses.FrozenInstanceError)`
so the immutability test actually asserts immutability.

## Files Changed

- `scripts/sweep_commit_helpers.py` (new) — planning module.
- `platform_tests/scripts/test_sweep_commit_helpers.py` (new) — 14 tests.

No other files touched. No `bridge/INDEX.md` content change beyond this entry's
status line. No KB mutation. WI-4528 MemBase resolution is a separate operational
step after VERIFIED (out of this report's scope).

## Recommended Commit Type

`feat:` — net-new capability (a commit-planning helper module + its test suite),
not a repair of existing broken behavior. The inventory-drift gate is correct as
designed; this helper teaches sweep-commit to satisfy it deterministically. Per
the Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md`.

## Risk / Rollback

Very low. Pure planning module + unit tests; no git, no subprocess, no mutation,
no schema/KB change. The helper is invoked-but-not-yet-wired, so it cannot affect
existing sweep-commit behavior until the deferred wiring slice lands. Rollback:
delete the two new files.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
