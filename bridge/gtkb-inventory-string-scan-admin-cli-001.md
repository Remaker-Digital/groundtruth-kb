NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-desktop-gtkb-cleanout-2026-06-16
author_model: gpt-5-codex
author_model_configuration: Codex desktop session; Prime Builder under owner-directed bridge cleanup

# Implementation Proposal - Inventory String Scan Admin CLI

bridge_kind: prime_proposal
Document: gtkb-inventory-string-scan-admin-cli
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/admin/**","groundtruth-kb/src/groundtruth_kb/inventory/**","groundtruth-kb/tests/test_inventory_string_scan*.py","platform_tests/groundtruth_kb/**","config/agent-control/**","config/registry/**",".claude/skills/**",".codex/skills/**",".agent/skills/**",".api-harness/skills/**","groundtruth-kb/templates/skills/**","groundtruth-kb/tests/fixtures/scaffold_golden/**"]

## Summary

Add a deterministic administrative CLI process for string scans across the
declared GT-KB artifact inventory. The tool must support the workflow Mike
specified:

1. Update the inventory declaration.
2. Provide search strings to match.
3. Run the scan across the whole inventory.
4. Distinguish critical artifact hits from warn-level artifact hits.
5. Emit a repeatable fail ledger for investigation, remediation, and re-scan.

## Owner Decisions / Input

Mike requested the deterministic string scan/find capability as a CLI
administrative tool and specified that it must operate as a process, not an ad
hoc grep.

Mike also stated that all mutating GT-KB requirements should be captured through
the CLI as the internal AI/agent system UI, and that skills should use the CLI
underneath where practical instead of requiring agents to edit GT-KB artifacts
directly.

## Prior Deliberations

- Owner directive in this session: identify tracked artifacts fully, scan each
  artifact mechanically, record failures, investigate, remediate, and tick each
  failure off the list.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-004.md` - GO for the first
  cleanup slice that exposed the need for a reusable deterministic scanner.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - classifies artifact lifecycle trigger
  categories and supports owner-gated remediation child bridges.

## Specification Links

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `config/agent-control/system-interface-map.toml`
- `config/registry/sot-artifacts.toml`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Proposed CLI Shape

Implement an administrative inventory scan command family with these behaviors:

- `gt admin inventory refresh` updates the declared tracked-artifact inventory
  from the current git-tracked platform files and records artifact class,
  lifecycle category, owner surface, and severity default.
- `gt admin inventory scan-strings --match <string> ...` scans the full
  declared inventory for one or more literal strings.
- `gt admin inventory scan-strings --match-file <path>` accepts a newline/JSON
  list of search strings so agents do not have to place sensitive or confusing
  strings directly in prompts.
- `--critical-class` and `--warn-class` allow deterministic severity overrides
  by artifact class, path glob, lifecycle trigger category, or explicit path.
- `--json` emits machine-readable results with stable IDs.
- Markdown output emits a fail ledger grouped by severity and artifact class.
- The command exits nonzero when critical hits are present unless explicitly
  run in report-only mode.

## Skill Integration

Add or update a skill so agents use the CLI for deterministic inventory string
scans instead of hand-written grep loops. The skill should:

- require an inventory refresh/check before scan;
- ask for or derive the string list;
- run the full inventory scan;
- classify critical and warn hits;
- preserve a fail ledger for bridge proposals and implementation reports;
- never mutate target artifacts as part of the scan phase.

## Acceptance Criteria

- [ ] CLI can refresh/check the declared inventory from git-tracked artifacts.
- [ ] CLI can scan all declared artifacts for one or more literal strings.
- [ ] CLI supports critical/warn classification by artifact class and path.
- [ ] CLI output includes path, line, matched string ID, artifact class,
  severity, and remediation status placeholder.
- [ ] CLI exits nonzero on critical hits by default.
- [ ] A skill routes agents to the CLI and bars ad hoc scans when the
  deterministic process is required.
- [ ] Tests cover inventory refresh, multi-string scan, critical/warn
  classification, JSON output, markdown ledger output, and nonzero exit
  behavior.
- [ ] The implementation does not require any AI/agent to mutate GT-KB code in
  order to operate the scanner.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification evidence |
| --- | --- |
| `config/registry/sot-artifacts.toml` | Inventory refresh/check tests prove the scanner has a declared artifact boundary rather than an ad hoc search scope. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Classification tests prove critical and warn hits are derived from artifact lifecycle category and path class. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Markdown/JSON ledger tests prove scan findings are durable artifact candidates for follow-up bridge work. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward and records exact commands plus observed results. |
| `.claude/rules/file-bridge-protocol.md` | Skill integration tests prove mutating remediation still routes through bridge protocol rather than scanner-side edits. |

Planned command families:

- `python -m pytest groundtruth-kb/tests/test_inventory_string_scan*.py -q --tb=short`
- `python -m pytest platform_tests/groundtruth_kb -q --tb=short`
- `python -m pytest platform_tests/skills -q --tb=short`
- `gt admin inventory scan-strings --match-file <fixture> --json`

## Risk And Rollback

The main risk is creating a second artifact inventory authority. The command
must either update the existing inventory declaration or clearly define the new
declaration as the scanner's only source of truth. Rollback is removal of the
new CLI command, tests, and skill updates.
