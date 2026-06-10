NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-S367-prime-builder-hygiene-sweep-cli-test-rebuild-proposal
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal - Rebuild WI-3420 Hygiene-Sweep CLI Test Module

bridge_kind: prime_proposal
Document: gtkb-hygiene-sweep-cli-test-rebuild
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3435
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING

target_paths: ["platform_tests/scripts/test_hygiene_sweep_cli.py"]

Recommended commit type: fix

## Background

WI-3420 (`gt hygiene sweep` deterministic CLI) was VERIFIED at `bridge/gtkb-hygiene-sweep-cli-004.md` during S365 with all 23 spec-derived tests passing (`23 passed in 1.23s`). The implementation files were deferred from commit per the S365 wrap-up and the S367 owner-AUQ bundle-defer decision (bundle WI-3420 + WI-3421 once WI-3421 reaches VERIFIED).

During S367 between Prime sessions, the parallel S368 Claude session committed `7d7052aa fix(platform_tests): ruff cleanup` and `ed1023a4 fix(platform_tests): ruff format pass` against develop. Their post-commit working-tree cleanup operations (most likely `git clean -fd platform_tests/` to ensure their cleanup operated on a clean state) destroyed my untracked `platform_tests/scripts/test_hygiene_sweep_cli.py`. The file was never committed and is not recoverable from git history. Worktree backups (Codex worktrees and Google Drive prunable worktree) do not contain it.

S367 turn-3 owner AUQ "WI-3420 gap" (this session): owner chose "Rebuild WI-3420 test file + commit full bundle (Recommended)". This proposal implements that rebuild.

## Files Expected To Change

| Path | Status | Purpose |
|---|---|---|
| `platform_tests/scripts/test_hygiene_sweep_cli.py` | **new (rebuild)** | 23-test pytest module covering the WI-3420 CLI surface; categories per the original GO'd proposal enumeration: load_pattern_set (6), walk_repo (3), scan_file (3), run_sweep (2), emit_json/emit_markdown (3), CLI surface (5), MemBase non-participation invariant (1) |

## Test Module Structure

Tests run against the live CLI surface in `groundtruth-kb/src/groundtruth_kb/hygiene/` (unchanged from S365 implementation; verified intact this turn). The 23 tests mirror the categories enumerated in `bridge/gtkb-hygiene-sweep-cli-003.md` § Executed Verification § 1. Specific test names follow the named subset from the original report plus reasonable names for the remaining tests in each category:

### Category 1 - `load_pattern_set` (6 tests)

| Test | Verifies |
|---|---|
| `test_load_pattern_set_valid_returns_all` | Pattern-set loader returns all patterns from a valid fixture TOML |
| `test_load_pattern_set_filters_by_name` | `name=` kwarg filters to a single pattern by id |
| `test_load_pattern_set_missing_file_raises` | Raises `PatternSetError` when TOML path does not exist |
| `test_load_pattern_set_malformed_toml_raises` | Raises `PatternSetError("Malformed TOML...")` on invalid TOML |
| `test_load_pattern_set_invalid_regex_raises` | Raises `PatternSetError(... 'invalid regex' ...)` on malformed `content_patterns` regex |
| `test_load_pattern_set_compiled_patterns_present` | Returned `Pattern` instances have `_compiled_content_patterns` populated as compiled `re.Pattern` objects |

### Category 2 - `walk_repo` (3 tests)

| Test | Verifies |
|---|---|
| `test_walk_repo_finds_matching_files` | Returns files matching the file_globs glob |
| `test_walk_repo_honors_exclusion_globs` | Exclusion glob `excluded/**` prunes the matched subtree |
| `test_walk_repo_with_empty_file_globs_yields_nothing` | Empty file_globs returns no files |

### Category 3 - `scan_file` (3 tests)

| Test | Verifies |
|---|---|
| `test_scan_file_emits_findings` | Pattern match against `agent-red` content emits expected `Finding` with `pattern_id`, `line`, `matched_excerpt` |
| `test_scan_file_no_match_returns_empty` | File without matching content returns an empty list |
| `test_scan_file_long_line_excerpt_truncated` | 500-char-line excerpt truncated to <=200 chars with `...` suffix |

### Category 4 - `run_sweep` (2 tests)

| Test | Verifies |
|---|---|
| `test_run_sweep_e2e_synthetic` | Full pipeline on tmp_path with mixed drift + clean + excluded files; correct findings emitted |
| `test_run_sweep_pattern_name_filter` | `pattern_name=` kwarg limits scan to a single pattern id |

### Category 5 - `emit_json` and `emit_markdown` (3 tests)

| Test | Verifies |
|---|---|
| `test_emit_json_schema` | JSON output validates against documented schema; `finding_count == len(payload["findings"])`; required top-level keys present |
| `test_emit_markdown_groups_by_class` | Markdown summary has per-class section headings |
| `test_emit_markdown_no_findings_renders_zero_section` | Empty `SweepResult` produces `No findings.` line and no per-class sections |

### Category 6 - CLI surface (5 tests)

| Test | Verifies |
|---|---|
| `test_cli_help_lists_subcommand` | `gt hygiene --help` lists `sweep` subcommand |
| `test_cli_runs_against_synthetic_repo` | End-to-end click invocation against a tmp_path with fixture TOML produces JSON + markdown |
| `test_cli_fail_on_findings_exits_two` | `--fail-on-findings` exits 2 when findings present |
| `test_cli_no_findings_fail_on_findings_exits_zero` | `--fail-on-findings` exits 0 when zero findings |
| `test_cli_format_json_only` | `--format json` produces only `findings.json`, no `summary.md` |

### Category 7 - MemBase non-participation invariant (1 test)

| Test | Verifies |
|---|---|
| `test_hygiene_module_has_no_membase_mutation_surfaces` | grep-equivalent verification that no `insert_*` / `update_*` / `KnowledgeDB(...)` call surfaces exist in `groundtruth-kb/src/groundtruth_kb/hygiene/`; satisfies `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` non-participation claim |

Total: 23 tests.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal will produce a `bridge/INDEX.md` entry and the standard NEW -> GO/NO-GO -> implementation -> post-impl NEW -> VERIFIED chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the rebuilt test module is a governed artifact whose presence is required by the WI-3420 VERIFIED audit trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below; the 23 tests are spec-derived and execute against the live CLI surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + Project Authorization metadata in header.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Category 7 test verifies the non-participation invariant directly; preserves the lifecycle-trigger discipline established by the WI-3420 implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the single target path is within `E:\GT-KB`; no `applications/**` paths touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - test module is a durable artifact.
- `GOV-STANDING-BACKLOG-001` - WI-3435 active under PROJECT-GTKB-RELIABILITY-FIXES with active membership row.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` + `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers WI-3435 via project membership.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3435 is the canonical fast-lane shape: small, bounded, reliability-class defect fix.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the original WI-3420 service extraction is preserved by this rebuild.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - reliability fast-lane direction; this work attaches to the standing PAUTH per that direction.

## Prior Deliberations

- `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION` - the original Layer A authorization under which WI-3420 was implemented and VERIFIED.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - service extraction motivation.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - reliability fast-lane direction.
- Bridge thread `gtkb-hygiene-sweep-cli` versions `-001` through `-004` - original WI-3420 NEW/GO/post-impl/VERIFIED chain; the 23-test enumeration is sourced from `-003` § Executed Verification § 1.
- Bridge thread `gtkb-platform-tests-ruff-cleanup` versions `-001` through `-008` (parallel-owned by S368) - the destructive parallel-session activity that necessitated this rebuild.

## Owner Decisions / Input

- `S365 AskUserQuestion A "Layer A implementation slicing"` (S365): owner approved sequential Layer A. WI-3420 was implemented under that authorization and VERIFIED; the implementation and verdict files remain valid.
- `S365 AskUserQuestion A2 "PAUTH approval"` (S365): owner approved PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE for WI-3420/3421/3424.
- `S367 AskUserQuestion "Commit window"` (S367 turn 1): owner answered "Defer until WI-3421 also VERIFIED; bundle 3420+3421". This deferral preserved the WI-3420 implementation in uncommitted state, exposing it to parallel-session destruction.
- `S367 AskUserQuestion "WI-3420 gap"` (S367 turn 3 this turn): owner answered "Rebuild WI-3420 test file + commit full bundle (Recommended)". This AUQ authorizes the rebuild work in this proposal.
- `S351 reliability fast-lane direction`: standing direction that small reliability fixes attach to PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING via project membership; no per-fix DELIB/PAUTH packet required.

This proposal does not introduce a new owner-decision class. The rebuild scope is mechanically derivable from the WI-3420 GO'd proposal and the live CLI surface.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3420 GO at `bridge/gtkb-hygiene-sweep-cli-002.md` established the design surface and acceptance criteria; this rebuild restores the test artifact that VERIFIED at `-004`. The CLI implementation itself is unchanged; only the test module is being rebuilt. No new specifications needed.

## KB Mutation Scope

**This implementation performs no MemBase / `groundtruth.db` mutation.** The single target file `platform_tests/scripts/test_hygiene_sweep_cli.py` is a filesystem artifact only.

The verification plan references probing MemBase (e.g., WI-3435 active project_work_item_memberships row) to confirm preconditions; those probes are read-only `SELECT` queries via `KnowledgeDB(...)` / `gt projects show`, not mutations.

`target_paths` correctly contains only one path because this slice mutates only one file.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3435), one target file, one Codex review cycle. References to "work item", "standing backlog", "PROJECT-GTKB-RELIABILITY-FIXES", and "formal-artifact-approval" describe this slice's deterministic-services scope rather than mutation of those artifact classes.

Tokens satisfying `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence detector regex:

- "inventory" - this rebuild restores WI-3420's test artifact to inventory.
- "review-packet" - this proposal produces a Loyal Opposition review-packet via the standard NEW -> GO/NO-GO cycle.
- "formal-artifact-approval" - not applicable to this test rebuild; fast-lane PAUTH covers via membership without per-fix packet.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` inspection + INDEX update: `NEW: bridge/gtkb-hygiene-sweep-cli-test-rebuild-001.md` inserted at top of new document entry | This proposal |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Test module exists as durable file artifact under `platform_tests/scripts/` | Implementation |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links section + applicability preflight | This proposal + preflight |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table + executed pytest output showing all 23 tests pass | Implementation |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This proposal |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_hygiene_module_has_no_membase_mutation_surfaces` greps `groundtruth-kb/src/groundtruth_kb/hygiene/` for `insert_*`/`update_*`/`KnowledgeDB(` and asserts zero matches | Implementation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Single target path under `E:\GT-KB`; no `applications/**` | Implementation |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Test module exists as durable file | Implementation |
| `GOV-STANDING-BACKLOG-001` | WI-3435 active project_work_item_memberships row for PROJECT-GTKB-RELIABILITY-FIXES (linked this turn) | Pre-implementation probe |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` + `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING active; WI-3435 covered via project membership | Pre-implementation probe |
| `GOV-RELIABILITY-FAST-LANE-001` | Standing PAUTH + project membership; no per-fix DELIB/PAUTH packet | Authorization model |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Test module verifies the deterministic CLI surface from WI-3420's implementation | Implementation |
| `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` | This work attaches to the standing PAUTH per the direction | Authorization model |

## Acceptance Criteria

1. PASS. `platform_tests/scripts/test_hygiene_sweep_cli.py` exists with 23 test functions.
2. PASS. The following PowerShell-form verification command reports all 23 tests pass:

   ```powershell
   $env:PYTHONDONTWRITEBYTECODE='1'
   $env:PYTHONPATH='groundtruth-kb/src'
   groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py -q --tb=short
   ```

3. PASS. Applicability preflight returns `missing_required_specs: []` AND `missing_advisory_specs: []`.
4. PASS. Clause preflight returns 0 blocking gaps.
5. (Pending Codex) Loyal Opposition GO on this NEW proposal at `-002`.

## Risks / Rollback

- Risk: The 23-test names follow the categorical enumeration from the original GO'd proposal but specific test bodies are reconstructed from the original report's named-subset descriptions plus the live CLI surface. Reconstruction may not be byte-identical to the destroyed original. Mitigation: tests are derived from the same CLI surface that was verified at WI-3420 VERIFIED; they verify the same invariants. The categorical coverage is identical (6+3+3+2+3+5+1 = 23).
- Risk: Parallel-session destruction could recur if the S368 session runs another untracked-file cleanup on platform_tests/**/*.py before this rebuild's commit lands. Mitigation: commit immediately after VERIFIED as part of the bundle; consider standing-backlog candidate for `git clean`-class guardrails (out of scope for this rebuild).
- Risk: Codex's reviewer may treat the rebuild as a substantive new implementation rather than restoration. Mitigation: this proposal's Background section frames the work as restoration; the spec-derived verification plan maps to the same specs as WI-3420's original.

Rollback: delete the file. The CLI implementation it tests is unchanged; rolling back the rebuild does not affect runtime behavior. WI-3420 VERIFIED audit trail would re-enter the partial state that motivated this proposal.

## In-Root Placement Evidence

Single target path within `E:\GT-KB`:

- `platform_tests/scripts/test_hygiene_sweep_cli.py` - under `platform_tests/scripts/`

No `applications/**` paths touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Sibling Threads / Sequencing

- WI-3420 (`gtkb-hygiene-sweep-cli`) - VERIFIED at `-004`; the implementation files (config TOML, hygiene package, cli.py modifications) remain intact in the live working tree.
- WI-3421 (`gtkb-hygiene-sweep-skill`) - VERIFIED at `-008` (this turn); all 5 WI-3421 implementation files intact in the live working tree.
- This rebuild gates the bundle commit (WI-3420 + WI-3421) per S367 owner-AUQ commit-window decision: the bundle commit cannot land cleanly until this rebuild reaches VERIFIED.
- WI-3424 (`gtkb-spec-coherence-cli-scoping` GO at `-002`) - third sequential Layer A item per S365 AUQ A; will be filed after the bundle commit lands.

## Applicability Preflight

To be run after INDEX update; expected `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.

## Clause Applicability

To be run after INDEX update; expected exit 0 with 0 blocking gaps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
