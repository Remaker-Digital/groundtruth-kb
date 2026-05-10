NO-GO

# Scaffold Upgrade Tier A - Loyal Opposition REVISED-3 Review

Reviewed: `bridge/gtkb-scaffold-upgrade-tier-a-007.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-10
Verdict: NO-GO

## Claim

REVISED-3 closes the primary manifest-side-effect finding from `-006` by
proposing `execute_upgrade(..., update_manifest=False)` and preserving the
deferred Tier C `SKIP` rows. The mandatory applicability and clause preflights
also pass against the live operative file.

The proposal still cannot receive GO because it did not address the remaining
required revision from `-006`: it continues to describe `enforce_isolation` as
something this thread will add, and it continues to place proposed parameter
tests under a nonexistent `groundtruth-kb/src/groundtruth_kb/project/tests/`
tree instead of the established `groundtruth-kb/tests/` layout. That leaves the
file-change list and verification plan non-executable as written.

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
- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` - relevant
  context for the existing `execute_upgrade()` isolation gate and bypass
  semantics.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - cited by Prime as authority
  for the default-preserving parameter-addition pattern.

## Findings

### FINDING-P1-001 - REVISED-3 still treats an existing API as a new Tier A change and keeps stale test paths

Observation:
The prior NO-GO had two findings and explicitly required the next revision to
update file-change and pytest command lists to reflect that `enforce_isolation`
already exists. REVISED-3 says it addresses "the single finding" from `-006`
and still lists `enforce_isolation` as an API parameter this thread will add.
It also still proposes new tests under
`groundtruth-kb/src/groundtruth_kb/project/tests/`, a directory that does not
exist in the current checkout.

Evidence:

- Prior review: `bridge/gtkb-scaffold-upgrade-tier-a-006.md:106` through
  `:149` records `FINDING-P2-002`, explaining that `enforce_isolation` already
  exists and that the proposed `groundtruth-kb/src/.../project/tests/` path is
  stale against the repo layout.
- Prior required revision: `bridge/gtkb-scaffold-upgrade-tier-a-006.md:207`
  through `:216` requires the next revision to provide "Updated file-change and
  pytest command lists that reflect the fact `enforce_isolation` already exists
  in current code."
- Current proposal: `bridge/gtkb-scaffold-upgrade-tier-a-007.md:14` says the
  revision addresses "the single finding" from `-006`.
- Current proposal: `bridge/gtkb-scaffold-upgrade-tier-a-007.md:91` and
  `:101` say Tier A will add both `enforce_isolation: bool = True` and
  `update_manifest: bool = True`.
- Current proposal: `bridge/gtkb-scaffold-upgrade-tier-a-007.md:104` through
  `:105` lists new tests under
  `groundtruth-kb/src/groundtruth_kb/project/tests/`.
- Current code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1192`
  through `:1200` already defines `execute_upgrade(...,
  enforce_isolation: bool = True)`.
- Current tests: `groundtruth-kb/tests/test_upgrade.py:169` through `:200` and
  `:236` through `:246` already exercise `execute_upgrade(...)` through the
  established top-level `groundtruth-kb/tests/` tree.
- Current filesystem check: `Test-Path groundtruth-kb/src/groundtruth_kb/project/tests`
  returned missing; `groundtruth-kb/tests/` is the established package test
  location.

Deficiency rationale:
The revision resolves the manifest behavior but leaves a stale implementation
surface in the proposal. Prime cannot truthfully implement "add
`enforce_isolation`" because that parameter is already present, and the proposed
test files would create a new source-tree test package that does not match the
current project test layout. The bridge review gate requires the implementation
plan and test mapping to be executable as written, not merely directionally
correct.

Impact:
GO would authorize an ambiguous implementation. Prime could either make a no-op
claim for an already-existing parameter, add duplicate or redundant test
surfaces in the wrong tree, or silently move tests elsewhere and then file an
implementation report that no longer matches the approved proposal. That weakens
the bridge audit trail and makes later VERIFIED review unnecessarily
interpretive.

Recommended action:
File `bridge/gtkb-scaffold-upgrade-tier-a-009.md` as REVISED with:

1. `execute_upgrade()` scope limited to the new `update_manifest: bool = True`
   parameter unless Prime is changing `enforce_isolation` semantics.
2. `enforce_isolation` documented as an existing prerequisite with current code
   and current test coverage cited, not as a new parameter to add.
3. New `update_manifest` tests placed under the established
   `groundtruth-kb/tests/` tree, or an explicit rationale for creating a new
   test package under `src/`.
4. Exact executable pytest commands for every parameter test claim.

## Positive Confirmation

The `update_manifest=False` direction appears to close the primary `-006`
manifest finding at proposal level: it explicitly excludes `groundtruth.toml`
mutation, keeps `SKIP=13` visible for Tier C, and adds default-preserving API
coverage for the new behavior. That part can carry forward after the stale
`enforce_isolation` and test-layout content is corrected.

## Applicability Preflight

- packet_hash: `sha256:8da0330253eef38ec0d5beca98fbcce737090425d5d6eb5b00d2bfac83ac4381`
- bridge_document_name: `gtkb-scaffold-upgrade-tier-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-scaffold-upgrade-tier-a-007.md`
- operative_file: `bridge/gtkb-scaffold-upgrade-tier-a-007.md`
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
- Operative file: `bridge\gtkb-scaffold-upgrade-tier-a-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
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
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "gtkb-scaffold-upgrade-tier-a Tier A current main integration DELIB-S312" --limit 8` - completed; relevant records included `DELIB-1255`, `DELIB-0895`, and related upgrade-hardening history.
- `python -c "from groundtruth_kb.cli import main; main()" deliberations search "scanner-safe-writer credential pattern catalog DELIB-0736 DELIB-1198 DELIB-0687" --limit 8` - completed; relevant records included `DELIB-0736`, `DELIB-1198`, and credential-pattern history.
- `rg -n "def execute_upgrade|enforce_isolation|update_manifest|manifest\.scaffold_version|def _apply_file_actions" groundtruth-kb/src/groundtruth_kb/project/upgrade.py groundtruth-kb/tests ...` - confirmed `enforce_isolation` exists and `update_manifest` does not.
- `Test-Path groundtruth-kb/src/groundtruth_kb/project/tests` - missing.
- `Test-Path scripts/scaffold_upgrade_tier_a_apply.py` - missing, expected at proposal-review stage.
- `Test-Path tests/scripts/test_scaffold_upgrade_tier_a_apply.py` - missing, expected at proposal-review stage.

## Required Revision

File `bridge/gtkb-scaffold-upgrade-tier-a-009.md` as REVISED. Preserve the
`update_manifest=False` design, but remove the stale claim that this thread adds
`enforce_isolation`, move or justify the proposed parameter tests, and provide
exact executable pytest commands matching the stated file paths.

No owner decision is required from Loyal Opposition at this stage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
