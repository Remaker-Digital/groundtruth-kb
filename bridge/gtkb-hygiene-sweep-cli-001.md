NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-S365-prime-builder-hygiene-sweep-cli-implementation
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal - Deterministic CLI: gt hygiene sweep

bridge_kind: implementation_report
Document: gtkb-hygiene-sweep-cli
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3420
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE

target_paths: ["config/governance/hygiene-sweep-patterns.toml", "groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py", "groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_hygiene_sweep_cli.py"]

Recommended commit type: feat

## Implementation Plan

This is the implementation slice for the `gt hygiene sweep` deterministic CLI scoped under `bridge/gtkb-hygiene-sweep-cli-scoping-003.md` (GO). Implementation authorization derives from `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE` and the S365 AUQ A + AUQ A2 owner-decision chain.

### Component 1 - Pattern-set TOML registry

`config/governance/hygiene-sweep-patterns.toml` is a new configuration artifact. Initial content carries one pattern (`agent-red-config-drift`) seeded from the three S363 observed instances. Schema:

- `version` (integer) - registry schema version (initial: 1)
- `[[patterns]]` array of pattern entries, each with:
  - `id` (string, kebab-case) - stable pattern identifier
  - `class` (string) - drift class (`config_drift`, `workflow_drift`, etc.)
  - `description` (string) - human-readable explanation
  - `file_globs` (array of strings) - paths to scan, in fnmatch / glob syntax
  - `content_patterns` (array of strings) - regex patterns (Python `re` syntax) to match within scanned files
  - `exclusion_globs` (array of strings) - paths to skip
  - `classification` (string) - finding classification tag
  - `remediation_hint` (string) - suggested next-step guidance

Initial pattern (illustrative content; full implementation includes regex escape correctness):

```toml
version = 1

[[patterns]]
id = "agent-red-config-drift"
class = "config_drift"
description = "Agent-Red-inherited config carried in GT-KB repo-root files"
file_globs = ["*.properties", ".github/workflows/*.yml", "pyproject.toml", "scripts/**/*.py", "sonar-project.properties"]
content_patterns = ["Remaker-Digital_agent-red-customer-engagement", "AGENT_RED_GITHUB_REPO", "applications/Agent_Red/", "sonar\\.sources=src/"]
exclusion_globs = ["applications/**", "bridge/**", "memory/**", "independent-progress-assessments/**", ".gtkb-state/**", "archive/**"]
classification = "agent_red_inherited"
remediation_hint = "Verify path/key is in canonical GT-KB scope; relink if not."
```

### Component 2 - Hygiene package

`groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py` is a new package init. Exports the `sweep` module's public API.

`groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` carries the implementation logic:

- `load_pattern_set(toml_path, name=None) -> list[Pattern]` - TOML loader; uses `tomllib` (py3.11+ stdlib); returns dataclass `Pattern` instances. Default returns all patterns when `name=None`; named loads filter by `id`.
- `walk_repo(root, file_globs, exclusion_globs) -> Iterator[Path]` - file walker; honors exclusion globs first, then file glob match.
- `scan_file(path, content_patterns) -> list[Finding]` - per-file content scan; line-by-line regex match; emits `Finding` dataclass per hit (file, line, pattern_id, matched_excerpt up to 200 chars).
- `run_sweep(root, pattern_set_path, pattern_name=None) -> SweepResult` - orchestrator; loads patterns, walks repo, scans files, aggregates findings.
- `emit_json(result, out_path)` and `emit_markdown(result, out_path)` - output writers; JSON schema matches contract; markdown groups findings by pattern class.

The module is read-only against the repository. It mutates only its own output directory under `.gtkb-state/hygiene-sweep/`. No bridge proposals, MemBase rows, or governance artifacts are created. Lifecycle decisions (per Codex's `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` advisory in the scoping GO) are orchestrated by the sibling hygiene-sweep skill (WI-3421), not by this CLI.

### Component 3 - CLI extension

`groundtruth-kb/src/groundtruth_kb/cli.py` adds a `hygiene` command group with a `sweep` subcommand:

```text
gt hygiene sweep [--pattern-set NAME] [--patterns-path PATH] [--output PATH]
                 [--format json|md|both] [--report-only|--fail-on-findings]
                 [--root PATH]
```

Defaults:
- `--patterns-path` = `config/governance/hygiene-sweep-patterns.toml`
- `--output` = `.gtkb-state/hygiene-sweep/<UTC-ISO-run-id>/`
- `--format` = `both`
- `--report-only` (default) - exit 0 regardless of finding count
- `--fail-on-findings` - exit 2 if any findings emitted (for CI gate use)
- `--root` = current working directory

Click integration; no new top-level dependencies (uses `pathlib`, `tomllib`, `re`, `fnmatch` from stdlib).

### Component 4 - Tests

`platform_tests/scripts/test_hygiene_sweep_cli.py` is a new pytest module. Test coverage:

- `test_load_pattern_set_valid` - loads the shipped TOML; returns N >= 1 patterns
- `test_load_pattern_set_named` - filter by pattern id returns single-pattern list
- `test_load_pattern_set_missing_id` - filter by unknown id returns empty list
- `test_load_pattern_set_malformed_toml` - raises ValueError on syntactically invalid TOML
- `test_walk_repo_honors_exclusions` - tmp_path fixture with `applications/**` directory; walker skips
- `test_walk_repo_matches_file_globs` - tmp_path fixture; only matching files returned
- `test_scan_file_matches_content_patterns` - tmp_path fixture file with known drift; finding emitted
- `test_scan_file_no_matches_empty_findings` - clean tmp_path file; empty list
- `test_run_sweep_e2e_synthetic` - tmp_path with mixed files; full pipeline emits expected findings
- `test_emit_json_schema_matches_contract` - JSON output validates against documented schema
- `test_emit_markdown_groups_by_class` - markdown summary has per-pattern-class section headings
- `test_cli_default_invocation_exit_zero` - `gt hygiene sweep` default invocation against tmp_path root; exit 0
- `test_cli_fail_on_findings_exit_two` - `--fail-on-findings` against drift-bearing tmp_path; exit 2
- `test_cli_report_only_overrides_fail_on_findings` - both flags emit warning + report-only wins (defensive)

Tests use `pytest`'s `tmp_path` fixture exclusively for filesystem isolation; no committed fixture files needed. Mock pattern set defined inline per-test using `(tmp_path / "patterns.toml").write_text(...)`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this is an implementation NEW following scoping GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the CLI surface and its pattern-set TOML registry are durable governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below maps every cited spec to executed verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + Project Authorization metadata present in header.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - explicitly cited per Codex's scoping-GO advisory; the CLI deliberately does NOT participate in lifecycle decisions (the orchestrating skill in WI-3421 carries lifecycle responsibility). Verification table includes a row asserting non-participation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are within `E:\GT-KB`; no `applications/**` paths touched. Pattern set's `exclusion_globs` carve out `applications/**` to preserve application-side Agent Red references as valid.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the CLI is a durable artifact serving the deterministic-services principle; the pattern-set TOML is a durable configuration artifact.
- `GOV-ARTIFACT-APPROVAL-001` - the pattern-set TOML's future revisions go through formal-artifact-approval-packet workflow; initial implementation content is owner-approved via the bridge GO at this thread.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions on pattern-set scope and authorization captured via AskUserQuestion (this proposal's owner-decision chain).
- `GOV-STANDING-BACKLOG-001` - WI-3420 has active project membership in PROJECT-GTKB-DETERMINISTIC-SERVICES-001 and is included in the PAUTH-...-LAYER-A-HYGIENE-COHERENCE authorization.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the governing principle that motivates extracting repetitive plumbing into a deterministic service.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the governing principle. The three S363 instances (WI-3409, WI-3417, WI-3418 below) crossed the threshold to extract drift discovery into a service.
- `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION` - the S365 PAUTH-creation deliberation; carries owner AUQ A + AUQ A2 decisions.
- `DELIB-2142` - prior VERIFIED `gtkb-gov-010-followup-observations-s342` hygiene sweep thread; format and concept precedent.
- `DELIB-2496` - prior artifact recorder CLI GO; adjacent deterministic CLI precedent (CLI shape and PAUTH integration pattern).
- `DELIB-2471`, `DELIB-2470`, `DELIB-2469` - discoverability CLI NO-GO/GO history; precedent for deterministic CLI review-cycle expectations and target_paths discipline.
- `DELIB-1473` - Loyal Opposition Advisory: LO Hygiene Assessment Skill; sibling concept on the LO side. This CLI is the Prime-side counterpart for drift inventory.
- `DELIB-2070`, `DELIB-1416` - bridge thread `session-hygiene-drift-triage-s321-2026-04-29` (VERIFIED); session-bounded predecessor that motivated service extraction.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - Agent Red migration window context driving the drift class.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - relevant for WI-3419 (initial use case of this CLI against agent-red-drift); reliability fast-lane pattern enables small remediation child-WIs after the CLI surfaces drift instances.

## Owner Decisions / Input

- `S365 AskUserQuestion A "Layer A implementation slicing" (2026-05-28)`: owner answered "Sequential: 3420 -> 3421 -> 3424 (Recommended)". Recorded at `memory/pending-owner-decisions.md` (S365 resolved entries) and captured in `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION`.
- `S365 AskUserQuestion A2 "PAUTH approval" (2026-05-28)`: owner answered "Approve as drafted". Authorization packet at `.groundtruth/formal-artifact-approvals/2026-05-28-delib-s365-layer-a-hygiene-coherence-authorization.json`.
- `S365 AskUserQuestion "Next move" (2026-05-28)`: owner answered "File WI-3420 implementation proposal (Recommended)". Authorizes this NEW filing.
- `S363 AskUserQuestion answers (2026-05-27/28)`: prior owner decisions to file WI-3420 scoping bridge and draft implementation as parallel-safe work.

## Requirement Sufficiency

Existing requirements sufficient. The cited specifications above govern bridge protocol authority (`GOV-FILE-BRIDGE-AUTHORITY-001`), artifact governance (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-ARTIFACT-APPROVAL-001`), implementation-proposal linkage (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`), verification (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`), and project linkage (`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`). No new GOV/SPEC/ADR/DCL is required for this implementation. If the test fixtures or sweep behavior surfaces a new constraint during Codex review, it will be addressed in a REVISED version under the same PAUTH coverage.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One implementation proposal, one work item (WI-3420), three component file additions (TOML registry + hygiene package + test module) plus one targeted extension (cli.py subcommand). The pattern-set TOML registry is a single config file; the hygiene package adds two new Python files; the test module is a single file. References to "work item", "standing backlog", "inventory", and "formal-artifact-approval" in this proposal describe this implementation's deterministic-service scope and its compliance posture under `GOV-STANDING-BACKLOG-001`, not a backlog mutation or formal-artifact-approval batch.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Evidence at post-impl |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX inspection: `gtkb-hygiene-sweep-cli` thread NEW -> GO/NO-GO -> implementation -> VERIFIED | Bridge INDEX visible at `bridge/INDEX.md` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `gt hygiene sweep --help` lists the subcommand; `config/governance/hygiene-sweep-patterns.toml` validates against schema | CLI invocation output + TOML parse test |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This Specification Links section + applicability preflight `preflight_passed: true` | Preflight output in post-impl report |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table; every cited spec maps to executed verification at post-impl | Post-impl table with command outputs |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection (Project, Work Item, Project Authorization) | Header lines in this file |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Source inspection: `sweep.py` exposes no MemBase mutation calls (no `insert_*`, `update_*`, no `KnowledgeDB(...)` construction); no lifecycle state transitions | grep verification at post-impl |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths under `E:\GT-KB`, none in `applications/**`; pattern set `exclusion_globs` includes `applications/**` | Header `target_paths` inspection + TOML inspection |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Pattern-set TOML + CLI command tree lifecycle inspection | TOML file present; `gt hygiene sweep --help` succeeds |
| `GOV-ARTIFACT-APPROVAL-001` | Initial TOML content approved via this bridge GO; future revisions will require packet | bridge GO record at this thread |
| `SPEC-AUQ-POLICY-ENGINE-001` | AUQ answers from S365 archived in `DELIB-S365-...` and `pending-owner-decisions.md` | Deliberation row + decisions file |
| `GOV-STANDING-BACKLOG-001` | WI-3420 `project_work_item_memberships` active row in PROJECT-GTKB-DETERMINISTIC-SERVICES-001; PAUTH includes WI-3420 | SQL query output |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Service extraction motivation: CLI replaces three per-instance investigations | Scope motivation section above |

## Test Plan and Spec-to-Test Mapping

Executable verification at post-impl:

```text
# 1. Smoke test the CLI surface
python -m groundtruth_kb hygiene sweep --help

# 2. Run the test module
python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py -v

# 3. Verify TOML parses
python -c "import tomllib; tomllib.load(open('config/governance/hygiene-sweep-patterns.toml', 'rb'))"

# 4. Run sweep against this very repo (canary; exit 0 with --report-only)
python -m groundtruth_kb hygiene sweep --root . --report-only --format json
test $? -eq 0

# 5. Verify the lifecycle-non-participation claim
grep -rE "insert_|update_|KnowledgeDB\(" groundtruth-kb/src/groundtruth_kb/hygiene/ || echo "OK: no MemBase mutation surfaces"
```

Each command's output captured in the post-implementation report.

## Acceptance Criteria

1. `gt hygiene sweep --help` lists the subcommand with documented options.
2. `python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py` reports all tests PASS.
3. Pattern-set TOML at `config/governance/hygiene-sweep-patterns.toml` parses without errors and contains at least the seeded `agent-red-config-drift` pattern.
4. Sweep against this repo's working tree with default pattern set emits a `findings.json` and `summary.md` under `.gtkb-state/hygiene-sweep/<run-id>/`. The repo SHOULD surface the three S363 instances (WI-3409's `AGENT_RED_GITHUB_REPO` reference, WI-3417's SonarCloud `sonar.sources=src/` line, WI-3418's `applications/Agent_Red/tests/fixtures/...` workflow comment) when sweeping un-remediated working state.
5. No MemBase mutation surfaces in `hygiene/` package (verified via grep at post-impl).
6. Applicability preflight passes; clause preflight passes with no blocking gaps.

## Risks / Rollback

- Risk: pattern set produces false positives (e.g., legitimate Agent-Red references in `applications/Agent_Red/` that the CLI shouldn't flag). Mitigation: `exclusion_globs` carves out `applications/**`, `bridge/**`, `memory/**`, `independent-progress-assessments/**`, `.gtkb-state/**`, `archive/**`.
- Risk: pattern set misses real drift instances (false negatives). Mitigation: WI-3419 is the initial use case for validation against the three S363-observed instances; gap findings expand the pattern set via formal-artifact-approval-packet flow.
- Risk: CLI surface overlaps with `gt project doctor`. Mitigation: clear separation -- doctor reports health/configuration validity; hygiene sweep reports drift-class patterns for remediation child-WI filing. The skill at WI-3421 is the orchestrator that ties findings to remediation, not the doctor.
- Risk: tomllib not available (py <3.11). Mitigation: the GT-KB platform requires py >= 3.11 per `pyproject.toml`; no fallback needed. Verification at post-impl: `python --version` confirms >= 3.11.
- Rollback: delete the four new files (`hygiene/__init__.py`, `hygiene/sweep.py`, `hygiene-sweep-patterns.toml`, `test_hygiene_sweep_cli.py`) and revert the cli.py subcommand registration. No MemBase rows, no bridge files mutated beyond this thread, no shared-state changes.

## Files Changed

New files:
- `config/governance/hygiene-sweep-patterns.toml` - initial pattern-set registry
- `groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py` - new package init
- `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` - implementation module
- `platform_tests/scripts/test_hygiene_sweep_cli.py` - test suite

Modified file:
- `groundtruth-kb/src/groundtruth_kb/cli.py` - register `hygiene` command group with `sweep` subcommand

## In-Root Placement Evidence

All target paths above are within `E:\GT-KB`. No `applications/**` paths touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied at both the design level (in this proposal) and at the implementation level (the file writes will occur under in-root paths only). The pattern set's `exclusion_globs` explicitly preserves `applications/**` as out-of-scope for the sweep, honoring the boundary in both directions.

## Sibling Threads / Sequencing

This is the first of three sequential Layer A implementation proposals per the S365 AUQ A owner decision:

1. WI-3420 (this thread) - hygiene sweep CLI
2. WI-3421 - gtkb-hygiene-sweep skill (Claude + Codex parity), filed after this thread reaches GO
3. WI-3424 - gt validate spec-coherence CLI, filed after WI-3421 reaches GO

WI-3421 depends on this CLI existing. WI-3424 shares `cli.py` with this proposal; sequential implementation avoids shared-file contention.

Adjacent threads not in this sequence:
- WI-3419 (initial use: agent-red-drift sweep) - blocked by WI-3420 + WI-3421; in `PROJECT-GTKB-RELIABILITY-FIXES`.
- WI-3425 / WI-3426 (seed-batch supersession scoping) - currently NO-GO at -002; their REVISED-2 is independent of this Layer A pipeline.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is added. Expected: `preflight_passed: true`; `missing_required_specs: []`. The advisory `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is explicitly cited per the scoping-GO advisory.

## Clause Applicability

Clause preflight will be run after this file is written. Expected exit 0 with no blocking gaps; implementation-clauses (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`) satisfied by the Specification-Derived Verification Plan above; in-root placement (`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`) satisfied by target paths and pattern-set exclusions.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
