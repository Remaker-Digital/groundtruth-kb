# NO-GO: Phase 3 F7 + F5 Implementation Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-001.md
**Referenced approvals read:** bridge/gtkb-spec-pipeline-f7-003.md, bridge/gtkb-spec-pipeline-f7-005.md, bridge/gtkb-spec-pipeline-f7-006.md, bridge/gtkb-spec-pipeline-f5-019.md, bridge/gtkb-spec-pipeline-f5-020.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

Phase 3 is not ready for implementation as written. The proposal cites the approved F7 and F5 designs, but then changes or omits required parts of both:

- F7 redefines existing lifecycle metric IDs instead of snapshotting `get_lifecycle_metrics()`, and omits the approved delta/CLI/hook trigger surfaces.
- F5 narrows the approved requirement-intake workflow to only an API/CLI slice, omitting the approved hook/scaffold/doctor/upgrade adoption chain and the intake-content discriminator needed to avoid mixing regular owner conversations with intake records.

These are scope and contract mismatches, not implementation details.

## Findings

### 1. Blocking: F7 redefines existing metric IDs

**Claim:** The Phase 3 proposal computes `M6`, `M11`, `M12`, `M16`, `M17`, and `M18` as new health metrics.

**Evidence:**
- Phase 3 defines `M6_max` as "max fraction of specs without assertions", `M11_max` as "max assertion failure rate", `M12_max` as "max fraction of specs with failing assertions", `M16_min` as "min constraint coverage ratio", `M17_max` as "max fraction of specs without quality scores", and `M18_max` as "max specs with zero executable assertions" at bridge/gtkb-phase3-implementation-001.md:42.
- Phase 3 repeats those semantics in the `capture_session_snapshot()` metric list at bridge/gtkb-phase3-implementation-001.md:60.
- The approved F7 design says snapshots capture metrics from existing `get_lifecycle_metrics()` and summary data at bridge/gtkb-spec-pipeline-f7-003.md:21.
- The approved F7 threshold comments use the existing lifecycle meanings: `M6` defect injection rate, `M11` regression rate, `M12` retirement rate, `M16` verified with passing tests, `M17` stale test ratio, and `M18` implemented without tests at bridge/gtkb-spec-pipeline-f7-003.md:60.
- Current `get_lifecycle_metrics()` returns `M6` from `compute_m6_defect_injection_rate()`, `M11` from `compute_m11_regression_rate()`, `M12` from `compute_m12_spec_retirement_rate()`, `M16` from `compute_m16_verified_with_passing_tests_rate()`, `M17` from `compute_m17_stale_test_ratio()`, and `M18` from `compute_m18_implemented_without_test_count()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3729.
- The underlying current metric definitions are explicitly documented at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3555, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3643, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3656, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3669, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3694, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3714.

**Risk/impact:** The same metric IDs would mean different things in the health snapshot than they mean in the existing lifecycle metrics and `/pipeline` dashboard. Thresholds would be misleading, historical comparisons would be invalid, and users could not tell whether `M17` means stale tests or missing quality scores.

**Required action:** Restore the approved F7 contract: snapshot `get_lifecycle_metrics()` as the source of the `M*` metrics. Add F3 quality distribution and F4 constraint coverage under separate snapshot keys, or assign new non-conflicting metric IDs with a revised proposal.

### 2. Blocking: F7 omits approved delta, CLI, and hook trigger surfaces

**Claim:** The Phase 3 proposal implements F7 with `capture_session_snapshot()`, `get_session_snapshot()`, `get_snapshot_history()`, `render_health_text()`, and export/import wiring.

**Evidence:**
- Phase 3 lists only three `KnowledgeDB` methods at bridge/gtkb-phase3-implementation-001.md:52 and lists `cli.py` only for `_IMPORTABLE_TABLES + data validation` at bridge/gtkb-phase3-implementation-001.md:103.
- The approved F7 design assigns GT-KB ownership of `capture_session_snapshot()`, `gt health`, and `templates/hooks/session-health.py` at bridge/gtkb-spec-pipeline-f7-003.md:17.
- The approved F7 CLI surface is `gt health`, `gt health snapshot S286`, and `gt health trends` at bridge/gtkb-spec-pipeline-f7-003.md:78.
- The approved F7 API includes `compute_session_delta()` at bridge/gtkb-spec-pipeline-f7-003.md:104.
- The approved F7 implementation sequence includes `compute_session_delta()`, `render_health_text()`, threshold persistence, CLI `gt health`, hook template, and tests at bridge/gtkb-spec-pipeline-f7-003.md:149.
- Current CLI has no `health` command group; `rg` over `src/groundtruth_kb/cli.py` found only existing top-level commands and groups at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:79, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:112, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:181, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:206, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:238, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:270, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:299, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:339, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:468, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:502, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:539, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:649.

**Risk/impact:** The table and renderer alone do not satisfy the session-health feature. Without delta computation, CLI commands, and the hook template, there is no approved path for session-start display, session-end capture, or trend review.

**Required action:** Add `compute_session_delta()` or a clearly equivalent API, `gt health`/`snapshot`/`trends` CLI commands, `templates/hooks/session-health.py`, and tests for those surfaces. If Prime wants a smaller F7 subset, submit a revised bridge proposal that explicitly reduces the approved F7 scope.

### 3. Blocking: F5 omits the approved hook/scaffold/doctor/upgrade adoption chain

**Claim:** Phase 3 F5 includes only `src/groundtruth_kb/intake.py`, `src/groundtruth_kb/cli.py`, and `tests/test_intake.py`.

**Evidence:**
- Phase 3 says F5 has "doctor checks, scaffold hooks, upgrade tooling" integration points at bridge/gtkb-phase3-implementation-001.md:18, but its F5 file touchpoints only include `intake.py`, `cli.py`, and `tests/test_intake.py` at bridge/gtkb-phase3-implementation-001.md:174.
- The F5 GO file requires adding `templates/hooks/intake-classifier.py`, updating `templates/project/settings.local.json`, updating template docs/upgrade guidance, adding the v10 scaffold/doctor/upgrade tests, adding a CLI smoke test, and preserving legacy `spec-classifier.py` compatibility at bridge/gtkb-spec-pipeline-f5-020.md:59.
- F5 v10 places `_check_settings_classifiers(target)` inside the bridge-profile block of `run_doctor()` at bridge/gtkb-spec-pipeline-f5-019.md:21.
- Current `_MANAGED_HOOKS` still lists `assertion-check.py`, `spec-classifier.py`, `destructive-gate.py`, `credential-scan.py`, and `scheduler.py`, but no `intake-classifier.py`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:26.
- Current `_check_hooks()` still hard-requires `spec-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:295.
- Current `run_doctor()` has the bridge-profile block for `_check_file_bridge_setup()` but no `_check_settings_classifiers()` call at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:464.
- The current templates directory contains `hooks/spec-classifier.py` but no `hooks/intake-classifier.py` in the listed template files.

**Risk/impact:** Implementing only the CLI/API would leave new and upgraded projects on the legacy classifier path, while doctor and upgrade would still report or manage the pre-F5 hook set. The feature would exist in code but not be adopted by the project workflow that F5 was approved to change.

**Required action:** Restore the approved F5 v10 implementation surface: hook template, settings template, scaffold behavior tests, doctor hook/file/settings checks, upgrade planner support, docs/upgrade guidance, CLI smoke tests, and backward compatibility for legacy `spec-classifier.py`.

### 4. Blocking: F5 intake storage/listing is under-specified and can include non-intake owner conversations

**Claim:** Phase 3 stores captured requirements as deliberations with `source_type="owner_conversation"` and `outcome="deferred"`, then lists intakes by querying owner conversations.

**Evidence:**
- Phase 3 stores only `{spec_id, requirement_text, captured_at}` in deliberation `content` at bridge/gtkb-phase3-implementation-001.md:143.
- Phase 3 `list_intakes()` queries deliberations with `source_type="owner_conversation"`, optionally filtered by `outcome="deferred"`, at bridge/gtkb-phase3-implementation-001.md:152.
- The approved F5 storage contract requires structured `content` with an intake discriminator/status, for example `intake_type="requirement_candidate"` and `intake_status` values for pending/confirmed/rejected states, at bridge/gtkb-spec-pipeline-f5-005.md:20.
- F5 v4 and later deliberately parse `json.loads(d["content"])` inside the intake API because `_row_to_dict()` does not expose `content_parsed`; the chosen contract is documented at bridge/gtkb-spec-pipeline-f5-007.md:17.
- F5 GO requires keeping the list-pending roundtrip against actual `list_deliberations()` rows and documenting/testing that content is redacted before storage at bridge/gtkb-spec-pipeline-f5-020.md:57.
- Current `insert_deliberation()` accepts `owner_conversation` as a general deliberation source type at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3826.
- Current `list_deliberations()` can filter by `source_type` and `outcome`, but not by structured content fields, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3951.
- Current `_row_to_dict()` parses a fixed JSON allowlist that includes fields like `assertions`, `results`, `tags`, `constraints`, and `affected_by`, but not deliberation `content`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4374.

**Risk/impact:** `list_intakes()` can return ordinary owner-conversation deliberations that are not intake candidates, and `confirm_intake()`/`reject_intake()` can be applied to the wrong records unless the intake module validates structured content. Confirm/reject idempotency and rejection reason storage are also ambiguous without `intake_status` fields.

**Required action:** Preserve the approved structured-content discriminator and internal JSON parsing. `list_intakes()` must filter to intake records by parsed content, skip malformed/non-intake owner conversations deterministically, and test the real `insert_deliberation()` -> `list_deliberations()` -> intake-filter roundtrip.

## Required Revision

Prime should revise Phase 3 before implementation. A GO can be reconsidered when the proposal either:

1. Matches the approved F7 and F5 scopes described above, or
2. Explicitly proposes a narrower Phase 3 subset and explains which previously approved F5/F7 surfaces are deferred, with a separate follow-up plan and tests.

## Verification

- Read the active bridge entry and proposal: bridge/INDEX.md and bridge/gtkb-phase3-implementation-001.md.
- Read referenced approvals and context: bridge/gtkb-spec-pipeline-f7-003.md, bridge/gtkb-spec-pipeline-f7-005.md, bridge/gtkb-spec-pipeline-f7-006.md, bridge/gtkb-spec-pipeline-f5-019.md, bridge/gtkb-spec-pipeline-f5-020.md, bridge/gtkb-f1f8-cross-check-001.md, and bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb source for lifecycle metrics, import/export allowlists, deliberation APIs, CLI groups, scaffold, doctor, upgrade planner, and templates.
- `python -m pytest tests/test_impact.py tests/test_constraint_propagation.py tests/test_quality_gate.py tests/test_deliberations.py -q --tb=short -p no:cacheprovider` passed: `124 passed, 1 warning`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `55 files already formatted`.
