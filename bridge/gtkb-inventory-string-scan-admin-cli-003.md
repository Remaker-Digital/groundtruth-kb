REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-desktop-resume-2026-06-16
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder session

# Revised Implementation Proposal - Inventory String Scan Admin CLI

bridge_kind: prime_proposal
Document: gtkb-inventory-string-scan-admin-cli
Version: 003
Revises: bridge/gtkb-inventory-string-scan-admin-cli-001.md
Responds to: bridge/gtkb-inventory-string-scan-admin-cli-002.md
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/admin/**","groundtruth-kb/src/groundtruth_kb/inventory/**","groundtruth-kb/tests/test_inventory_string_scan*.py","platform_tests/groundtruth_kb/**","config/agent-control/**","config/registry/**",".claude/skills/**",".codex/skills/**",".agent/skills/**",".api-harness/skills/**","groundtruth-kb/templates/skills/**","groundtruth-kb/tests/fixtures/scaffold_golden/**"]

## Revision Claim

This revision addresses the single blocking finding in
`bridge/gtkb-inventory-string-scan-admin-cli-002.md`: the original proposal did
not include the mandatory `## Requirement Sufficiency` section and did not
state exactly one operative sufficiency state.

This is a proposal-only repair. No scanner source, test, skill, template,
registry, or configuration implementation is claimed in this revision. A fresh
Loyal Opposition `GO` remains required before implementation can begin.

## Summary

Add a deterministic administrative CLI process for string scans across the
declared GT-KB artifact inventory. The tool must support the workflow Mike
specified:

1. Update the inventory declaration.
2. Provide search strings to match.
3. Run the scan across the whole inventory.
4. Distinguish critical artifact hits from warn-level artifact hits.
5. Emit a repeatable fail ledger for investigation, remediation, and re-scan.

The intent is to replace ad hoc grep loops with a repeatable platform command
that agents can invoke through skills and CLI, while leaving actual remediation
to separate bridge-reviewed implementation work.

## Owner Decisions / Input

Mike requested the deterministic string scan/find capability as a CLI
administrative tool and specified that it must operate as a process, not an ad
hoc grep.

Mike also stated that all mutating GT-KB requirements should be captured through
the CLI as the internal AI/agent system UI, and that skills should use the CLI
underneath where practical instead of requiring agents to edit GT-KB artifacts
directly.

No new owner decision is required for this revised proposal. The revision is
limited to making the already-reviewed implementation proposal structurally
complete.

## Prior Deliberations

- `bridge/gtkb-inventory-string-scan-admin-cli-001.md` - original Prime Builder
  implementation proposal.
- `bridge/gtkb-inventory-string-scan-admin-cli-002.md` - Loyal Opposition
  NO-GO requiring a mandatory Requirement Sufficiency section and clarification
  of intentional new package surfaces.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-004.md` - GO for the first
  cleanup slice that exposed the need for a reusable deterministic scanner.
- `DELIB-2539` and `DELIB-20262206` - prior inventory-regeneration bridge
  context cited by the NO-GO verdict; relevant to avoiding a second inventory
  source of truth.
- `DELIB-2467` - prior inventory-work review context where mutation boundaries
  and deterministic output contracts needed precision.
- `DELIB-20263447` - CLI-first operation and skill-wrapped CLI usage context
  cited by the NO-GO verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger categories
  and remediation child-bridge guidance.

## Specification Links

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
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

## Requirement Sufficiency

Existing requirements are sufficient for this implementation proposal.

The owner directives cited in `Owner Decisions / Input`, the standing
CLI-first operating direction, the artifact-oriented governance specifications,
the SoT artifact registry, and the file-bridge implementation-start rules
jointly authorize the implementation of a deterministic administrative scanner.
The proposal does not create a new governance doctrine; it implements a CLI and
skill surface that operationalize the already stated requirement to make
inventory-backed string scans deterministic, repeatable, and auditable.

No new or revised formal requirement is needed before implementation can
proceed. If implementation discovers that a formal GOV/ADR/DCL/SPEC mutation is
needed, that formal mutation must use the applicable governed approval path and
must not be bundled into scanner implementation without its own authority.

## Findings Addressed

### P1 - Mandatory Requirement Sufficiency section is absent

Response: added `## Requirement Sufficiency` with exactly one operative state:
`Existing requirements are sufficient for this implementation proposal.`

The section cites the existing owner direction, CLI-first operating model,
artifact-oriented governance, SoT registry, and bridge implementation-start
rules as sufficient authority for implementation. It also preserves the
boundary that any newly discovered formal-artifact mutation must follow its own
approval path.

### Parent-directory warning for new package surfaces

Response: the missing parent directories reported by the preflight are
intentional new implementation surfaces. The scanner may add
`groundtruth_kb.admin` for administrative command grouping and
`groundtruth_kb.inventory` for inventory refresh/scan support code.

Those package paths are included in `target_paths` so implementation can create
them if the detailed design confirms that new modules are cleaner than placing
all code in the existing CLI module. Creating those packages remains bounded by
this bridge scope and by the implementation-start packet.

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
- accept or derive the string list;
- run the full inventory scan;
- classify critical and warn hits;
- preserve a fail ledger for bridge proposals and implementation reports;
- never mutate target artifacts as part of the scan phase.

## Scope Changes

The implementation scope is unchanged from version 001 except for the explicit
clarification that the two missing parent-directory warnings are intentional
new package surfaces. No target paths are removed.

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

## Pre-Filing Preflight Subsection

Prime Builder ran the mandatory preflights against this exact completed draft
before live filing:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-inventory-string-scan-admin-cli --content-file .gtkb-state/bridge-revisions/drafts/gtkb-inventory-string-scan-admin-cli-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-inventory-string-scan-admin-cli --content-file .gtkb-state/bridge-revisions/drafts/gtkb-inventory-string-scan-admin-cli-003.md
```

Observed applicability result:

- packet hash: `sha256:6d174f4bf8e43c23f9dcc12818f37baf6db1c74fcb25a7e822085a7702f2f5d2`
- `preflight_passed`: `true`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `[]`
- warnings: missing parent directories for `groundtruth-kb/src/groundtruth_kb/admin/**` and `groundtruth-kb/src/groundtruth_kb/inventory/**`

Observed clause result:

- exit code: `0`
- clauses evaluated: `5`
- `must_apply`: `2`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`

The existing missing-parent warning for `groundtruth_kb.admin` and
`groundtruth_kb.inventory` is acknowledged above as intentional new package
surface scope, not a typo.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification evidence |
| --- | --- |
| `config/registry/sot-artifacts.toml` | Inventory refresh/check tests prove the scanner has a declared artifact boundary rather than an ad hoc search scope. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Classification tests prove critical and warn hits are derived from artifact lifecycle category and path class. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Markdown/JSON ledger tests prove scan findings are durable artifact candidates for follow-up bridge work. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward and records exact commands plus observed results. |
| `.claude/rules/file-bridge-protocol.md` | Skill integration tests prove mutating remediation still routes through bridge protocol rather than scanner-side edits. |
| `.claude/rules/codex-review-gate.md` | Implementation-start packet proves the source/test/skill/config work begins only after LO GO. |

Planned command families:

```powershell
python -m pytest groundtruth-kb/tests/test_inventory_string_scan*.py -q --tb=short
python -m pytest platform_tests/groundtruth_kb -q --tb=short
python -m pytest platform_tests/skills -q --tb=short
gt admin inventory scan-strings --match-file <fixture> --json
```

## Risk And Rollback

The main risk is creating a second artifact inventory authority. The command
must either update the existing inventory declaration or clearly define the new
declaration as the scanner's only source of truth, and the implementation
report must prove that boundary.

Rollback is removal of the new CLI command, tests, skill updates, and any new
scanner package modules. Since this proposal does not authorize scanner-side
remediation, rollback does not require reversing user artifacts changed by a
scan.

## Recommended Commit Type

Recommended commit type for the eventual implementation: `feat:`.

Rationale: the scanner adds a net-new administrative CLI and skill-supported
capability.
