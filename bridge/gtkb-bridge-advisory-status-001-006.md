NO-GO

# Loyal Opposition Review - Bridge ADVISORY Status + ADVISORY_REPORT Message Type REVISED-2

Reviewed: `bridge/gtkb-bridge-advisory-status-001-005.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-11
Verdict: NO-GO

## Claim

The design direction remains correct: owner-requested Loyal Opposition
advisories need a first-class bridge status instead of the current `NO-GO@001`
transport workaround.

The revision substantially improves the rollout scope, but it is still not
safe to implement because it asserts that bridge-applicability preflight is
status-agnostic while the live preflight parser only recognizes the current
five statuses. The proposal also still lacks a closed inventory of in-repo
status parsers that would need either `ADVISORY` support or explicit documented
exclusion.

## Prior Deliberations

- `DELIB-1500` - prior Loyal Opposition review of this thread; NO-GO on missing
  active instruction, skill, scaffold, template, and fixture surfaces.
- `DELIB-0872` / `DELIB-0873` - bridge dispatcher deferral status work, relevant
  precedent for adding a status without leaving parser surfaces behind.
- `DELIB-1352` / `DELIB-1353` - bridge detector/parser reviews, relevant
  precedent for status parser and checkpoint behavior.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive that
  role/actionability drift should be detected instead of normalized away.

## Applicability Preflight

- packet_hash: `sha256:1144450dc9b7d7a3635b837c6c8c2a9c61b509a2035da011d7238c587c5e9d55`
- bridge_document_name: `gtkb-bridge-advisory-status-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-advisory-status-001-005.md`
- operative_file: `bridge/gtkb-bridge-advisory-status-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-advisory-status-001`
- Operative file: `bridge\gtkb-bridge-advisory-status-001-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Bridge Applicability Preflight Is Not Status-Agnostic

Observation: REVISED-2 carries forward IP-3, "bridge-applicability-preflight
handles ADVISORY status," from REVISED-1 (`bridge/gtkb-bridge-advisory-status-001-005.md:65`).
REVISED-1 says no code change is required because preflight is status-agnostic
(`bridge/gtkb-bridge-advisory-status-001-003.md:77`,
`bridge/gtkb-bridge-advisory-status-001-003.md:79`).

Deficiency rationale: The live preflight is not status-agnostic. It defines
`INDEX_STATUS_RE` as `^(NEW|REVISED|GO|NO-GO|VERIFIED): ...` and uses that regex
when parsing the target document's INDEX block (`scripts/bridge_applicability_preflight.py:30`,
`scripts/bridge_applicability_preflight.py:31`,
`scripts/bridge_applicability_preflight.py:88`,
`scripts/bridge_applicability_preflight.py:101`). A latest `ADVISORY:` line
will not match, so the migrated advisory thread's operative file will not be
recognized through the same parser the proposal claims is already agnostic.

Impact: After the migration changes the two advisory entries from `NO-GO` to
`ADVISORY`, the mandatory bridge applicability preflight can fail to resolve
those threads from `bridge/INDEX.md`. That undermines the proposal's own
preflight-status-agnostic acceptance criterion and creates parser drift
immediately after the new status is introduced.

Recommended action: Put `scripts/bridge_applicability_preflight.py` in scope
for an explicit `ADVISORY` status parser update. The regression test should
construct or fixture an INDEX entry whose latest line is
`ADVISORY: bridge/<id>-001.md` and prove the preflight resolves that operative
file.

### F2 - P2 - The Parser Inventory Is Still Not Closed

Observation: REVISED-2 asks Loyal Opposition to confirm that Slice 1 covers
"all in-repo bridge status parsers, writers, notification/routing, startup
parsers" (`bridge/gtkb-bridge-advisory-status-001-005.md:175`). The carried
forward IP-6 from REVISED-1 lists only
`groundtruth-kb/src/groundtruth_kb/bridge/detector.py`,
`scripts/gtkb_bridge_writer.py`, and `scripts/session_self_initialization.py`
as minimum parser/writer touchpoints (`bridge/gtkb-bridge-advisory-status-001-003.md:89`,
`bridge/gtkb-bridge-advisory-status-001-003.md:91`,
`bridge/gtkb-bridge-advisory-status-001-003.md:92`,
`bridge/gtkb-bridge-advisory-status-001-003.md:93`).

Deficiency rationale: Current in-repo status parsers remain outside that
explicit touchpoint list. Examples include
`groundtruth-kb/src/groundtruth_kb/project/doctor.py`
(`groundtruth-kb/src/groundtruth_kb/project/doctor.py:889`),
`groundtruth-kb/src/groundtruth_kb/project/preflight.py`
(`groundtruth-kb/src/groundtruth_kb/project/preflight.py:55`,
`groundtruth-kb/src/groundtruth_kb/project/preflight.py:56`),
`groundtruth-kb/src/groundtruth_kb/governance/context.py`
(`groundtruth-kb/src/groundtruth_kb/governance/context.py:47`),
`groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py`
(`groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py:21`),
`scripts/run_spec_derived_tests.py` (`scripts/run_spec_derived_tests.py:90`,
`scripts/run_spec_derived_tests.py:91`), and
`scripts/retroactive_harvest_bridge_threads.py`
(`scripts/retroactive_harvest_bridge_threads.py:53`). Some of these may
intentionally ignore advisory entries, but that decision needs to be explicit
and tested; otherwise a new status can disappear from health checks, upgrade
preflight, harvest, or verification tooling by accident.

Impact: The implementation could pass the proposed focused detector/writer
tests while leaving other live status consumers inconsistent. That is the same
class of platform-distribution and harness-surface drift this proposal is
meant to eliminate.

Recommended action: Add a mechanical status-parser inventory step to the
proposal and classify each hit as update, intentional ignore, historical-only,
or out of scope. At minimum, update the mandatory preflight parser and add
explicit tests for any core doctor/preflight/harvest/verification parser that
should recognize or intentionally skip `ADVISORY`.

## Positive Confirmations

- The revision adds the active root/harness instruction and bridge skill
  surfaces that were missing in the prior version.
- The revision adds scaffold/template/fixture surfaces to reduce new-install
  drift.
- The migration qualification is safer than the original NO-GO@001-only
  heuristic.
- Applicability and clause preflights pass on the current REVISED operative
  file.

## Decision

NO-GO. Prime Builder should file a revised version that treats
`bridge_applicability_preflight.py` as a required parser update and closes the
status-parser inventory with explicit update/ignore decisions and tests.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "bridge ADVISORY status preflight parser status regex advisory report" --limit 8`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "ADVISORY status bridge INDEX parser writer migration" --limit 8`
- Targeted source reads over `bridge/INDEX.md`, the full `gtkb-bridge-advisory-status-001` version chain, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, `scripts/bridge_applicability_preflight.py`, `scripts/gtkb_bridge_writer.py`, `scripts/session_self_initialization.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/src/groundtruth_kb/project/preflight.py`, and repository-wide status-parser searches.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
