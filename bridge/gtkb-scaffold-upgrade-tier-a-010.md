GO

# Scaffold Upgrade Tier A - Loyal Opposition REVISED-4 Review

Reviewed: `bridge/gtkb-scaffold-upgrade-tier-a-009.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-11
Verdict: GO

## Claim

REVISED-4 resolves the remaining blocker from `-008`. The proposal now treats
`enforce_isolation` as an existing prerequisite instead of a new Tier A change,
places the new `update_manifest` test in the established
`groundtruth-kb/tests/test_upgrade.py` layout, and places the applier tests
under the established `platform_tests/scripts/` test surface.

The proposal is approved for implementation within the scope stated in
`bridge/gtkb-scaffold-upgrade-tier-a-009.md`: 12 ADD targets, 3
APPEND-GITIGNORE patterns, a scoped `update_manifest` option on
`execute_upgrade()` / `_apply_file_actions()`, one `test_upgrade.py` regression
test for manifest suppression, and a tested Tier A applier script.

## Prior Deliberations

Deliberation search was run before review using the `gt deliberations search`
CLI surface against `groundtruth.db`.

Relevant records:

- `DELIB-0736` - bridge thread `gtkb-hook-scanner-safe-writer`, VERIFIED.
  Confirms the hook was previously installed and verified.
- `DELIB-1198` - same hook thread reclassified ORPHAN. Supports the
  proposal's glossary-vs-reality framing.
- `DELIB-0895` / `DELIB-1255` - prior `gtkb-tier-a-current-main-integration`
  bridge history. Relevant because earlier Tier A upgrade work involved broad
  apply behavior rather than this narrowed pure-ADD + APPEND-GITIGNORE subset.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - recovered by direct
  deliberation search and relevant to the default-preserving deterministic
  service parameter pattern.
- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` - relevant
  context for the existing `execute_upgrade()` isolation gate and bypass
  semantics.
- `DELIB-0738` / `DELIB-1185` - credential-pattern-catalog bridge history,
  relevant to the `scanner-safe-writer` credential-scan surface.

## Findings

No blocking findings.

### POSITIVE-P2-001 - REVISED-4 corrects the existing-API and test-layout drift

Observation:
The latest proposal explicitly removes the stale claim that this thread adds
`enforce_isolation`, documents that parameter as an existing prerequisite, and
relocates the proposed tests to the current repository test layout.

Evidence:

- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-009.md:16` states
  `enforce_isolation` is reclassified from "new parameter" to "existing
  prerequisite".
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-009.md:18` states the
  `update_manifest` test moves to `groundtruth-kb/tests/test_upgrade.py` and
  applier tests move to `platform_tests/scripts/`.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-009.md:85` through `:101`
  limits the upgrade API change to `update_manifest` and names the exact file
  touchpoints.
- Current code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1192`
  through `:1199` already defines `execute_upgrade(...,
  enforce_isolation: bool = True)`.
- Current code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1253`
  through `:1266` gates the existing isolation preflight on
  `enforce_isolation`.
- Current code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1433`
  through `:1434` still performs the unconditional manifest write that
  `update_manifest=False` is designed to suppress.
- Current tests: `groundtruth-kb/tests/test_upgrade.py:236` through `:246`
  already cover default manifest update behavior.
- Current filesystem check: `groundtruth-kb/src/groundtruth_kb/project/tests`
  is absent; `groundtruth-kb/tests/test_upgrade.py` and
  `platform_tests/scripts/` both exist.

Deficiency rationale:
No deficiency remains at proposal-review stage. The prior `-008` blocker was
that the implementation plan authorized stale or nonexistent surfaces; the
latest proposal now names executable, current surfaces.

Impact:
Prime can implement without inventing a new test tree or making a no-op claim
about an already-existing parameter. The later implementation report can be
verified against explicit tests and file touchpoints.

Recommended action:
Proceed with implementation exactly within the `-009` scope. The
post-implementation report should carry forward the `-009` specification links
and include observed results for all tests listed in steps 12 through 16.

## Scope Approval

Approved implementation scope:

- Add `update_manifest: bool = True` to `execute_upgrade()` and
  `_apply_file_actions()` in
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`.
- Gate only the manifest mutation block on `update_manifest`; preserve default
  behavior for existing callers.
- Add `test_execute_upgrade_update_manifest_false_skips_manifest_write` to
  `groundtruth-kb/tests/test_upgrade.py`.
- Add `scripts/scaffold_upgrade_tier_a_apply.py`.
- Add `platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py`.
- Apply only the 12 ADD targets and 3 APPEND-GITIGNORE patterns listed in
  `bridge/gtkb-scaffold-upgrade-tier-a-009.md`.

Out of scope remains unchanged: MERGE-EVENT-HOOKS, SKIP rows, warning rows,
`scanner-safe-writer.py` registration in `.claude/settings.json`, and any
`enforce_isolation` semantic change.

## Applicability Preflight

- packet_hash: `sha256:6c247850b3150d380be69246a2761fabe4ef29089fe4ab24ed426471411aa0e3`
- bridge_document_name: `gtkb-scaffold-upgrade-tier-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-scaffold-upgrade-tier-a-009.md`
- operative_file: `bridge/gtkb-scaffold-upgrade-tier-a-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-scaffold-upgrade-tier-a`
- Operative file: `bridge\gtkb-scaffold-upgrade-tier-a-009.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Verification Performed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS; no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS; zero blocking gaps.
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "scaffold upgrade tier a update_manifest enforce_isolation" --limit 10` - completed; relevant record included `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE`.
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "gtkb-scaffold-upgrade-tier-a Tier A current main integration DELIB-S312 deterministic services" --limit 8` - completed; relevant records included `DELIB-1255`, `DELIB-0895`, and related upgrade history.
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE" --limit 5` - completed; recovered the deterministic services principle.
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "scanner-safe-writer credential pattern catalog DELIB-0736 DELIB-1198 DELIB-0687" --limit 8` - completed; relevant records included `DELIB-0736`, `DELIB-1198`, `DELIB-0738`, and `DELIB-1185`.
- `rg -n "def execute_upgrade|enforce_isolation|accept_migration|update_manifest|manifest\.scaffold_version|def _apply_file_actions|_apply_file_actions\(" groundtruth-kb/src/groundtruth_kb/project/upgrade.py groundtruth-kb/tests/test_upgrade.py` - confirmed `enforce_isolation` exists, `update_manifest` does not yet exist, and the manifest write is currently unconditional.
- `Test-Path groundtruth-kb\src\groundtruth_kb\project\tests` - false.
- `Test-Path groundtruth-kb\tests\test_upgrade.py` - true.
- `Test-Path platform_tests\scripts` - true.
- `plan_upgrade(Path('E:/GT-KB'), ignore_inflight_bridges=True)` - current live counts remain `informational: 30`, `skip: 13`, `add: 12`, `warning: 6`, `merge-event-hooks: 4`, `append-gitignore: 3`; Tier A selected actions remain the 12 ADDs and 3 APPEND-GITIGNORE rows.

## Implementation Instructions For Prime

Implement only the approved scope. The post-implementation report should cite
this GO file, carry forward the `-009` specification links, list the files
changed, include the recommended commit type, and report exact observed results
for:

- `pytest platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py -v`
- `pytest groundtruth-kb/tests/test_upgrade.py::test_execute_upgrade_update_manifest_false_skips_manifest_write -v`
- `pytest groundtruth-kb/tests/test_upgrade.py::test_execute_upgrade_updates_manifest_version -v`
- `pytest groundtruth-kb/tests/test_upgrade.py -v`
- `pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py -q`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
