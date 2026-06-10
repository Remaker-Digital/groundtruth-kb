NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-prime-builder-hygiene-sweep-cli-scoping
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Scoping Proposal - Deterministic CLI: gt hygiene sweep

bridge_kind: governance_advisory
Document: gtkb-hygiene-sweep-cli-scoping
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3420
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Scoping Claim

This is a non-mutating scoping proposal for a new deterministic CLI surface
`gt hygiene sweep` whose purpose is to enumerate config-drift instances across
the GT-KB repository against an owner-curated pattern set. The CLI emits a
machine-readable JSON inventory plus a human-readable markdown summary.
This proposal does NOT authorize implementation; it requests Loyal Opposition
review of scope, design, target paths, and integration with the existing
deterministic-services portfolio.

After GO and explicit per-slice project authorization, a follow-on implementation
bridge will land the CLI module, the pattern-set TOML registry, and tests.

## Motivation - S363 Class Observation

Three independent bridge items in session S363 (2026-05-27/28) surfaced the
same underlying defect class: Agent-Red-inherited config drift carried in
GT-KB repo-root files that were not relinked after the GroundTruth-KB rename
and isolation work.

The three observed instances:

1. WI-3409 (work-subject-aware testing/tool integration probe; VERIFIED at
   `bridge/gtkb-work-subject-aware-testing-integration-probe-008.md`):
   `scripts/session_self_initialization.py` queried `AGENT_RED_GITHUB_REPO`
   unconditionally for GT-KB sessions, producing stale GitHub Actions probe
   results.
2. WI-3417 (SonarCloud config relink; GO at
   `bridge/gtkb-sonarcloud-config-relink-gt-kb-002.md`):
   `sonar-project.properties` carried `sonar.projectKey=Remaker-Digital_agent-red-customer-engagement`
   and `sonar.sources=src/`, producing the SonarCloud Analysis workflow
   ERROR `The folder 'src/' does not exist`.
3. WI-3418 (RC Gate seed-resilient; NO-GO at
   `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-002.md` F1): the
   release-candidate-gate workflow comment names
   `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` as the
   canonical seed fixture, but `scripts/membase_ci_seed.py:36` defaults to
   `tests/fixtures/ci_membase_seed.json` (a path that doesn't exist).

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: repetitive plumbing work
performed by AI on a per-instance basis is a defect. Three session-by-session
investigations of the same drift class is the threshold to extract the
discovery work into a service. Other candidates not yet investigated:
`.github/workflows/sonarcloud.yml` pytest paths, `.github/workflows/security-scan.yml`,
`pyproject.toml` test paths, other `*.properties` files, and any remaining
`applications/Agent_Red/` references in repo-root scripts/ and workflows/.

## Proposed Scope

### Component 1 - Pattern-set TOML registry

Location: `config/governance/hygiene-sweep-patterns.toml`

Schema (illustrative):

```toml
[[patterns]]
id = "agent-red-config-drift"
class = "config_drift"
description = "Agent-Red-inherited config carried in GT-KB repo-root files"
file_globs = [
  "*.properties",
  ".github/workflows/*.yml",
  "pyproject.toml",
  "scripts/**/*.py",
  "sonar-project.properties",
]
content_patterns = [
  "Remaker-Digital_agent-red-customer-engagement",
  "AGENT_RED_GITHUB_REPO",
  "applications/Agent_Red/",
  "sonar\\.sources=src/",
]
exclusion_globs = [
  "applications/**",
  "bridge/**",
  "memory/**",
  "independent-progress-assessments/**",
]
classification = "agent_red_inherited"
remediation_hint = "Verify path/key is in canonical GT-KB scope; relink if not."
```

Pattern sets are versioned via the standard MemBase append-only model; owner
expands or refines the set via formal-artifact-approval-packet flow when
new drift classes are identified.

### Component 2 - CLI surface

Location: `groundtruth-kb/src/groundtruth_kb/cli.py` (extension of existing
`gt` command tree)

Command: `gt hygiene sweep [--pattern-set NAME] [--output PATH] [--format json|md|both]`

Behavior:

1. Load the named pattern set (default: all patterns in the registry).
2. Walk the repository (respecting `exclusion_globs`).
3. For each file matching `file_globs`, scan content for
   `content_patterns`.
4. Emit findings to `.gtkb-state/hygiene-sweep/<run-id>/`:
   - `findings.json` - structured inventory (per-finding: file, line, pattern
     ID, matched text excerpt, classification, remediation hint).
   - `summary.md` - human-readable rollup grouped by pattern class.
5. Exit 0 with `--report-only` (default) regardless of finding count; exit
   non-zero with `--fail-on-findings` for CI gate use.

The CLI is read-only against the repository. It mutates only its own output
directory under `.gtkb-state/`. No bridge proposals, MemBase rows, or
governance artifacts are created by the CLI itself; remediation child-WI
filing is the responsibility of the orchestrating skill (WI-3421).

### Component 3 - Tests

Location: `platform_tests/scripts/test_hygiene_sweep_cli.py`

Coverage:

- Pattern-set loading from TOML (valid + malformed).
- File-glob walking honors exclusions.
- Content-pattern matching produces expected findings against a fixture
  with known drift instances.
- JSON output schema matches contract.
- Markdown summary contains pattern-class section headings.
- `--fail-on-findings` exit code behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal
  follows NEW status with scoping (no GO/NO-GO discipline change).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the hygiene-sweep CLI itself becomes
  a governed artifact (CLI surface) and its pattern-set registry is a governed
  configuration artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived
  Verification Plan below maps acceptance to verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item +
  Project Authorization metadata present; authorization explicitly disclaims
  implementation per the governance_review pattern.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation target paths
  are within `E:\GT-KB` (under `config/governance/`,
  `groundtruth-kb/src/groundtruth_kb/`, `platform_tests/`); no `applications/**`
  paths touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the CLI is a durable artifact
  serving the deterministic-services principle; the pattern-set TOML is a
  durable configuration artifact.
- `GOV-ARTIFACT-APPROVAL-001` - the pattern-set TOML is a configuration
  artifact whose initial content and future revisions go through standard
  formal-artifact-approval-packet workflow.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions on pattern-set scope and
  authorization will be captured via AskUserQuestion at the per-slice
  implementation bridges.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - establishes the governing
  principle that repetitive plumbing belongs in services, not sessions. This
  proposal is a concrete manifestation: the three S363 instances trigger the
  deterministic-service extraction.
- `DELIB-1473` - Loyal Opposition Advisory: LO Hygiene Assessment Skill;
  sibling concept on the LO side. This CLI is the Prime-side counterpart for
  drift inventory.
- `DELIB-2070` and `DELIB-1416` - bridge thread
  `session-hygiene-drift-triage-s321-2026-04-29` (VERIFIED); precedent for
  session-hygiene-class work, but session-bounded, not service-extracted.
- `DELIB-2142` - bridge thread `gtkb-gov-010-followup-observations-s342`
  (VERIFIED); adjacent governance-hygiene work; provides format precedent.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  - the Agent Red migration window context that drives the drift class. The
  hygiene-sweep service is the discovery surface for "files inherited from
  Agent Red without relinking" residuals.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - relevant for WI-3419 (initial
  use case of this CLI against the agent-red-drift class); the fast-lane
  pattern enables small remediation child-WIs after the CLI surfaces them.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: owner selected
  "Repair Testing/Tool Integrations" as session focus.
- `S363 AskUserQuestion answer 2026-05-28 (next action)`: owner selected
  "Implement WI-3417 with isolation" followed by "draft WI-3420/3421
  proposals (parallel-safe, no commit)".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner-articulated principle
  that motivates the extraction.

Implementation authorization for the future per-slice bridges remains owner
authority via AskUserQuestion plus PAUTH coverage.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. `GOV-FILE-BRIDGE-AUTHORITY-001`
governs the bridge protocol; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` governs
artifact creation; `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` motivates the
service extraction. No new GOV/SPEC/ADR/DCL is required for scoping. If the
implementation slice surfaces a new constraint (e.g., a DCL for pattern-set
schema invariants), that will be addressed at implementation-bridge time per
the standard `GOV-ARTIFACT-APPROVAL-001` flow.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One scoping proposal, two named WIs (WI-3420 CLI and the
sibling WI-3421 skill in a parallel proposal). The pattern-set TOML registry
is a single configuration file; the CLI is a single command-tree extension;
the test module is a single file. References to "work item", "standing
backlog", and "inventory" describe this thread's deterministic-service scope.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread NEW -> GO/NO-GO -> implementation slice bridges | This scoping bridge |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Pattern-set TOML schema + CLI registration in `gt` command tree | Implementation slice |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links inspection above | This scoping bridge |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table | This scoping bridge |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This scoping bridge |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All proposed paths under `E:\GT-KB` | Implementation slice |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | CLI + TOML lifecycle inspection | Implementation slice |
| `GOV-ARTIFACT-APPROVAL-001` | Pattern-set TOML formal-artifact-approval packet | Implementation slice |
| `SPEC-AUQ-POLICY-ENGINE-001` | AskUserQuestion answers captured for impl authorization | Implementation slice |

The acceptance test for this scoping proposal is Codex GO on scope, design,
target paths, and prior-art linkage. Implementation slices will carry their
own verification plans with executed evidence.

## Acceptance Criteria (Scoping Bridge)

1. Loyal Opposition GO on the proposed scope, design, target paths, and
   integration with the existing deterministic-services portfolio.
2. Scoping proposal does NOT authorize implementation; per-slice bridges
   required.
3. Pattern-set TOML schema design accepted (initial set may be revised
   during implementation; schema shape is reviewed here).

## Risks / Rollback

- Risk: pattern set may produce false positives (e.g., legitimate Agent-Red
  references in `applications/Agent_Red/` that the CLI shouldn't flag).
  Mitigation: `exclusion_globs` carves out `applications/**`, `bridge/**`,
  `memory/**`, and other operational-state paths.
- Risk: pattern set may miss real drift instances (false negatives).
  Mitigation: WI-3419's initial use case is validation against the three
  S363-observed instances plus any additional drift the CLI surfaces; gap
  findings expand the pattern set via formal-artifact-approval-packet.
- Risk: the CLI surface may overlap with existing surfaces (e.g., `gt project
  doctor` checks). Mitigation: clear separation — `doctor` reports
  health/configuration validity; `hygiene sweep` reports drift-class patterns
  for remediation child-WI filing.
- Rollback: scoping proposal can be withdrawn (no source/config mutation
  occurs at scoping time). Implementation slices will document their own
  rollback paths.

## Files Expected To Change (Implementation Slice, Not This Bridge)

This scoping proposal does NOT touch any of these files. Listed for
implementation slice planning:

- `config/governance/hygiene-sweep-patterns.toml` (new; pattern-set registry)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modified; add `hygiene sweep`
  command tree)
- `platform_tests/scripts/test_hygiene_sweep_cli.py` (new; CLI test suite)
- Possible: `groundtruth-kb/src/groundtruth_kb/hygiene/` (new package
  directory if the CLI logic is non-trivial)

## In-Root Placement Evidence

All proposed paths above are within `E:\GT-KB`. No `applications/**` paths
touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied
at the design level; implementation slice will satisfy the clause at the
file-write level.

## Sibling Proposals

- WI-3421 (gtkb-hygiene-sweep skill) - sibling scoping bridge filed in
  parallel; the skill orchestrates this CLI, classifies findings, and guides
  remediation child-WI filing.
- WI-3419 (initial use: agent-red-drift sweep) - dependent WI; blocked by
  both WI-3420 and WI-3421; in `PROJECT-GTKB-RELIABILITY-FIXES`.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is added.
Expected: `preflight_passed: true`; `missing_required_specs: []`. Cross-cutting
specs cited above match the standard governance-review proposal set.

## Clause Applicability

Clause preflight will be run after this file is written. Expected exit 0 with
no blocking gaps; governance-review kind disclaims implementation, so
implementation-clauses (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`,
etc.) apply to the design-level test plan above rather than executed evidence.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
