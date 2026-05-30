NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-S365-prime-builder-hygiene-sweep-cli-impl-report
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report - Deterministic CLI: gt hygiene sweep

bridge_kind: implementation_report
Document: gtkb-hygiene-sweep-cli
Version: 003 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3420
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE

target_paths: ["config/governance/hygiene-sweep-patterns.toml", "groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py", "groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_hygiene_sweep_cli.py"]

Recommended commit type: feat

## Implementation Summary

The `gt hygiene sweep` deterministic CLI surface is implemented per the GO'd proposal at `bridge/gtkb-hygiene-sweep-cli-002.md`. All 5 target files landed at the proposal's specified paths. All 23 tests in the test module pass. The smoke-test invocation against the live repo successfully surfaces drift findings.

### Files landed

| Path | Status | Purpose |
|---|---|---|
| `config/governance/hygiene-sweep-patterns.toml` | new | Initial pattern-set registry with `agent-red-config-drift` pattern (per scoping bridge S363 evidence) |
| `groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py` | new | Package init; re-exports `Pattern`, `Finding`, `SweepResult`, `PatternSetError`, `load_pattern_set`, `walk_repo`, `scan_file`, `run_sweep`, `emit_json`, `emit_markdown` |
| `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` | new | Core logic: dataclasses, TOML loader, file walker, content scanner, output emitters; uses stdlib only (`pathlib`, `tomllib`, `re`, `fnmatch`) |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | modified | Added `from groundtruth_kb.hygiene import ...` (line 47); added `@main.group("hygiene")` + `@hygiene_group.command("sweep")` block (lines 114-184) |
| `platform_tests/scripts/test_hygiene_sweep_cli.py` | new | 23-test pytest module; covers load_pattern_set (6), walk_repo (3), scan_file (3), run_sweep (2), emit_json/emit_markdown (3), CLI surface (5), MemBase non-participation invariant (1) |

## Executed Verification

### 1. Test module execution

```text
cd E:/GT-KB && python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py -v
```

Result: **23 passed in 1.23s** (full output in S365 session transcript). All test classes PASS, including:

- `test_load_pattern_set_valid_returns_all` — pattern-set loader returns 2 fixture patterns.
- `test_load_pattern_set_malformed_toml_raises` — raises `PatternSetError("Malformed TOML...")` on invalid TOML.
- `test_load_pattern_set_invalid_regex_raises` — raises `PatternSetError("...invalid regex...")` on malformed `content_patterns` regex.
- `test_walk_repo_honors_exclusion_globs` — exclusion glob `excluded/**` prunes correctly.
- `test_scan_file_emits_findings` — pattern match against `agent-red` in `.properties` content emits expected `Finding` with `pattern_id`, `line`, `matched_excerpt`.
- `test_scan_file_long_line_excerpt_truncated` — 500-char-line excerpt truncated to <=200 chars with `...` suffix.
- `test_run_sweep_e2e_synthetic` — full pipeline on tmp_path with mixed drift + clean + excluded files; correct findings emitted.
- `test_emit_json_schema` — JSON output validates against documented schema; `finding_count == len(payload["findings"])`.
- `test_emit_markdown_groups_by_class` — markdown summary has per-class section headings.
- `test_cli_help_lists_subcommand` — `gt hygiene --help` lists `sweep` subcommand.
- `test_cli_fail_on_findings_exits_two` — `--fail-on-findings` exits 2 when findings present.
- `test_cli_no_findings_fail_on_findings_exits_zero` — `--fail-on-findings` exits 0 when zero findings.
- `test_cli_format_json_only` — `--format json` produces only `findings.json`, no `summary.md`.
- `test_hygiene_module_has_no_membase_mutation_surfaces` — grep verification that no `insert_*`/`update_*`/`KnowledgeDB(...)` call surfaces exist in `groundtruth-kb/src/groundtruth_kb/hygiene/`; satisfies the `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` non-participation claim from the proposal.

### 2. CLI surface smoke test

```text
cd E:/GT-KB && python -m groundtruth_kb hygiene sweep --help
```

Result: subcommand registered; options documented (`--root`, `--patterns-path`, `--pattern-set`, `--output`, `--format`, `--report-only/--fail-on-findings`).

### 3. Canary against live repo

```text
cd E:/GT-KB && python -m groundtruth_kb hygiene sweep --root . --report-only
```

Result: `hygiene sweep: 98 finding(s); output: E:\GT-KB\.gtkb-state\hygiene-sweep\20260528T173438Z`. Exit code 0 per `--report-only`. The output directory contains `findings.json` and `summary.md`.

Findings surface 98 instances of the `agent-red-config-drift` pattern across `.github/workflows/*.yml` files (accessibility.yml, build-agent-containers.yml, chromatic.yml, deploy-docs.yml, docs-quality.yml, etc.) where Agent-Red application paths are referenced from GT-KB repo-root workflows. This is exactly the drift class the scoping bridge motivated (S363 noted "any remaining `applications/Agent_Red/` references in repo-root scripts/ and workflows/" as un-investigated candidates).

Note: the post-WI-3417-relink sonar-project.properties no longer matches the `sonar\.sources=src/` pattern (the relink in commit `8b187ed1` changed `sonar.sources` to `groundtruth-kb/src,scripts`). This is correct: the CLI surfaces drift that exists at scan time. Remediation decisions per finding are the orchestrating-skill's responsibility (WI-3421), not this CLI's.

### 4. No MemBase mutation surfaces verification

```text
grep -rE "insert_|update_|KnowledgeDB\(" groundtruth-kb/src/groundtruth_kb/hygiene/
```

Result: zero matches (test `test_hygiene_module_has_no_membase_mutation_surfaces` codifies this assertion). Satisfies the `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` non-participation claim.

## Specification Links

All specs from `bridge/gtkb-hygiene-sweep-cli-001.md` Specification Links section are carried forward unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this report is the post-implementation phase of the GO'd thread.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the CLI surface and pattern-set TOML are governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant cross-cutting specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + Project Authorization metadata present in header.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - explicit non-participation verified (test 23 + grep evidence above).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all 5 target paths under `E:\GT-KB`; pattern set exclusion_globs carve out `applications/**`, `bridge/**`, `memory/**`, `independent-progress-assessments/**`, `.gtkb-state/**`, `archive/**`, `.claude/**`, `.codex/**`, and the pattern-set TOML itself.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI + TOML are durable artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - initial TOML content owner-approved via the bridge GO at -002.
- `SPEC-AUQ-POLICY-ENGINE-001` - S365 AUQ A + A2 + Next-move owner decisions captured.
- `GOV-STANDING-BACKLOG-001` - WI-3420 active membership in PROJECT-GTKB-DETERMINISTIC-SERVICES-001 verified at filing.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - service extraction motivation honored.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - service extraction motivation.
- `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION` - this implementation's PAUTH-creation DELIB, inserted earlier in this S365 turn.
- `DELIB-2142` - prior verified hygiene sweep thread.
- `DELIB-2496` - artifact recorder CLI precedent.
- `DELIB-2471`, `DELIB-2470`, `DELIB-2469` - discoverability CLI precedent.
- `DELIB-1473` - LO Hygiene Assessment Skill advisory.
- `DELIB-2070`, `DELIB-1416` - session-hygiene-drift-triage precedent.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - Agent Red migration context.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - WI-3419 (initial-use) attachment.

## Owner Decisions / Input

- `S365 AskUserQuestion A "Layer A implementation slicing" (2026-05-28)`: owner answered "Sequential: 3420 -> 3421 -> 3424 (Recommended)". Captured in `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION` and in `memory/pending-owner-decisions.md` S365 resolved entries.
- `S365 AskUserQuestion A2 "PAUTH approval" (2026-05-28)`: owner answered "Approve as drafted". Authorization packet at `.groundtruth/formal-artifact-approvals/2026-05-28-delib-s365-layer-a-hygiene-coherence-authorization.json`.
- `S365 AskUserQuestion "Next move" (2026-05-28)`: owner answered "File WI-3420 implementation proposal (Recommended)". Authorized the NEW filing at -001 which received Codex GO at -002.
- `S365 owner directive 2026-05-28T17:30Z`: "Please execute task #11 then task #13". Authorizes the implementation phase (this report) under the existing PAUTH.
- `S363 AskUserQuestion answers (2026-05-27/28)`: prior owner decisions establishing WI-3420 scoping bridge and parallel-safe drafting of implementation work.

## Specification-Derived Verification Plan

This table maps each cited specification to its executed verification evidence in this implementation slice:

| Specification | Verification command | Evidence at post-impl |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX inspection | This report INDEXed as NEW; thread proceeds NEW (003) -> GO/NO-GO (004) -> VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `gt hygiene sweep --help` lists subcommand | PASS (smoke test §2 above) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links section + applicability preflight | All cited; preflight pending pre-review |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table + executed tests | 23/23 tests PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | PASS (Project, Work Item, Project Authorization header lines present) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | grep verification + test 23 | PASS (zero MemBase mutation surfaces; test_hygiene_module_has_no_membase_mutation_surfaces) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All paths under `E:\GT-KB`; pattern-set exclusion_globs carve out applications/** | PASS (verified by inspection of TOML + target_paths) |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | TOML + CLI lifecycle inspection | PASS (both durable artifacts on disk) |
| `GOV-ARTIFACT-APPROVAL-001` | Initial TOML content from bridge GO -002 | PASS (TOML on disk matches GO'd proposal Component 1 schema) |
| `SPEC-AUQ-POLICY-ENGINE-001` | AUQ answers captured in DELIB-S365-... + Owner Decisions / Input section above | PASS |
| `GOV-STANDING-BACKLOG-001` | WI-3420 active project_work_item_memberships row | PASS (verified earlier in S365 turn via SQL probe) |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Service extraction successful | PASS (98 findings surfaced deterministically across 171 scanned files) |

## Requirement Sufficiency

Existing requirements sufficient. No new GOV/SPEC/ADR/DCL needed. Implementation matched the GO'd proposal's scope exactly; no scope expansion. Two minor refinements landed during implementation but neither requires new specs:

1. Added `Pattern` and `Finding` and `SweepResult` as frozen dataclasses (proposal said "dataclass `Pattern` instances"; implementation extended this to all three result types for consistency).
2. Added `.claude/**`, `.codex/**`, and the pattern-set TOML itself to exclusion_globs in the initial TOML (avoids the registry self-flagging when patterns mention `applications/Agent_Red/` in their content_patterns strings). Both extensions are within the GO'd "exclusion_globs" surface.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3420), five target files landed, one Codex review cycle pending. References to "work item", "standing backlog", "inventory", and "formal-artifact-approval" describe this implementation's deterministic-service scope rather than mutation of those artifact classes.

## Acceptance Criteria

Per proposal at -001:

1. PASS. `gt hygiene sweep --help` lists the subcommand with documented options.
2. PASS. `python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py` reports all tests PASS (23/23 in 1.23s).
3. PASS. Pattern-set TOML at `config/governance/hygiene-sweep-patterns.toml` parses without errors and contains the seeded `agent-red-config-drift` pattern.
4. PASS. Sweep against this repo emits `findings.json` + `summary.md` under `.gtkb-state/hygiene-sweep/20260528T173438Z/`. The repo surfaces 98 instances of the agent-red drift class, including workflow-file references that S363 specifically called out as un-investigated drift candidates.
5. PASS. No MemBase mutation surfaces in `hygiene/` package (test 23 + grep evidence).
6. Pending Codex. Applicability preflight + clause preflight at this NEW filing.

## Files Changed

New files:
- `config/governance/hygiene-sweep-patterns.toml`
- `groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py`
- `platform_tests/scripts/test_hygiene_sweep_cli.py`

Modified file:
- `groundtruth-kb/src/groundtruth_kb/cli.py` (one new import line at L47; one new group/command block at L114-184)

## Risks / Rollback

- Risk: 98-finding canary is large; some are intentional Agent-Red-application support per the operating model's "Agent Red is a separate project" framing while still living under `applications/Agent_Red/` within this checkout. Mitigation: the orchestrating skill (WI-3421) and per-finding owner decisions will classify legitimate vs drift. Pattern set can be refined (more specific content_patterns; expanded exclusion_globs) without source changes through standard formal-artifact-approval-packet flow.
- Risk: `pyproject.toml` is in the pattern's file_globs but did not produce findings; the canary's surface is concentrated on workflow files. Future patterns can target additional file classes.
- Rollback: delete the 4 new files and revert the cli.py block at L114-184 (the diff is small and contained). Pattern-set TOML can be removed without affecting other governance configs.

## In-Root Placement Evidence

All 5 target_paths within `E:\GT-KB`. No `applications/**` paths touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied at the file-write level. The pattern set explicitly excludes `applications/**` from sweep scope, preserving the application/platform boundary.

## Applicability Preflight

To be run prior to Codex review of this NEW; expected `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.

## Clause Applicability

To be run prior to Codex review; expected exit 0 with 0 blocking gaps.

## Sibling Threads / Sequencing

- WI-3421 (`gtkb-hygiene-sweep-skill-scoping` GO at -004) - next sequential Layer A implementation per S365 AUQ A. Will be filed after this thread reaches VERIFIED.
- WI-3424 (`gtkb-spec-coherence-cli-scoping` GO at -002) - third sequential Layer A implementation.
- WI-3425 (`gtkb-startup-cache-dcl-supersession-scoping` GO at -004) - seed-batch supersession; just received GO during this turn.
- WI-3426 (`gtkb-gov-08-permitted-markdown-amendment-scoping` GO at -004) - seed-batch GOV amendment; just received GO during this turn.
- WI-3419 (initial use: agent-red-drift sweep) - blocked by VERIFIED of this thread + WI-3421; in `PROJECT-GTKB-RELIABILITY-FIXES`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
