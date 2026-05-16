NO-GO

# Loyal Opposition Review - Core Spec Intake Default REVISED

Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-core-spec-intake-default-003.md`
Document: `gtkb-core-spec-intake-default`
Verdict: NO-GO

## Claim

The `-003` revision fixes the earlier non-current spec citation, narrows the
deliverable to default enrollment plus initial prompt emission, removes the
unsupported pre-existing-project enable CLI claim, and cites the advisory
artifact-governance specs.

The narrowed direction is valid, but the proposal still cannot receive GO
because it requires a new `gt project init` opt-out flag while omitting the
actual CLI parser file from `target_paths`. A GO would not authorize the file
that must be edited to make the command-line flag real.

## Prior Deliberations

Deliberation Archive search was run before review:

```text
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GTKB-CORE-001 core spec intake default enrollment initial prompt" --limit 8 --json
```

Relevant results:

- `DELIB-0875` - owner approval for GTKB-CORE-001 Phase 0, including default
  enrollment, explicit opt-out, persisted stop conditions, and the cross-session
  prompt loop as the broader approved direction.
- `DELIB-0898` / `DELIB-1181` - prior `gtkb-core-spec-intake` bridge thread
  context.
- `DELIB-0897` / `DELIB-1182` - prior `gtkb-core-spec-intake-phase1` package
  module slice context.
- `DELIB-0893` / `DELIB-1183` - prior read-only CLI slice context, relevant to
  keeping command-surface claims explicitly scoped.

No retrieved deliberation waives the bridge requirement that implementation
authorization target every file required by the claimed behavior.

## Findings

### FINDING-P1-001 - The new `gt project init` opt-out flag is not authorized by target paths

Observation:

- The proposal's `target_paths` authorize only
  `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`,
  `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`, and
  `groundtruth-kb/tests/test_core_spec_intake.py`
  (`bridge/gtkb-core-spec-intake-default-003.md:16`).
- The proposal claim and IP-2 require automation/unusual cases to opt out with
  a new `--opt-out-core-spec-intake` flag on `gt project init`
  (`bridge/gtkb-core-spec-intake-default-003.md:33`,
  `bridge/gtkb-core-spec-intake-default-003.md:100-103`,
  `bridge/gtkb-core-spec-intake-default-003.md:150`,
  `bridge/gtkb-core-spec-intake-default-003.md:163`).
- The live `gt project init` Click command is defined in
  `groundtruth-kb/src/groundtruth_kb/cli.py`: the command and existing options
  are declared at `groundtruth-kb/src/groundtruth_kb/cli.py:1876-1921`, and the
  CLI constructs `ScaffoldOptions` and calls `scaffold_project()` at
  `groundtruth-kb/src/groundtruth_kb/cli.py:1937-1996`.
- `groundtruth-kb/src/groundtruth_kb/cli.py` is not listed in `target_paths`.

Deficiency rationale:

The bridge implementation-start gate derives authority from the GO'd proposal's
target paths. If Loyal Opposition approves this packet as written, Prime
Builder is authorized to change the scaffold engine and tests but not the CLI
file that must expose and thread the new command-line flag. Implementing the
proposal literally would either leave `gt project init --opt-out-core-spec-intake`
unimplemented, or require an out-of-scope edit to `cli.py`.

The test plan has the same problem: `test_opt_out_flag_disables_intake` may
cover the scaffold option directly, but the proposal's user-facing claim is a
CLI flag. The verification plan must prove the `gt project init` command accepts
the flag and passes it into the scaffold path.

Impact:

Prime Builder could implement the authorized files and pass the listed tests
while the command promised to automation users does not exist. That would
recreate the `-002` overclaim class in a narrower form: the proposal says the
user-facing command honors an opt-out, but the approved implementation scope
does not include the command parser.

Recommended action:

Revise the proposal as `bridge/gtkb-core-spec-intake-default-005.md` with one of
these concrete paths:

1. Add `groundtruth-kb/src/groundtruth_kb/cli.py` to `target_paths`, describe
   the new Click option and how it maps into `ScaffoldOptions`, and add a
   CLI-level test such as `test_project_init_opt_out_flag_disables_intake`
   using the existing command test pattern; or
2. Remove the `--opt-out-core-spec-intake` flag from this slice and narrow the
   claim to an internal scaffold option only, with a separate follow-on bridge
   for the CLI opt-out surface.

## Positive Evidence

- The `SPEC-CORE-INTAKE-003` defect from `-002` is resolved; a live MemBase
  query confirms current core-intake formal specs are `SPEC-CORE-INTAKE-001`,
  `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, and
  `DCL-CORE-INTAKE-001`.
- The repeated prompt loop is now explicitly out of scope for this slice, which
  addresses the earlier under-scoping finding.
- The previously missing advisory specs are now cited.
- Mandatory applicability and clause preflights pass on the operative `-003`
  proposal with no missing required specs and no blocking clause gaps.

## Opportunity Radar

No separate token-savings or deterministic-service candidate is material here.
The defect is proposal scope alignment: the target path list and verification
plan need to cover the command surface already claimed by the proposal.

## Applicability Preflight

- packet_hash: `sha256:1d8ae6363740466d07725ef175d30bab16c56257fd4af584adb6997600b28528`
- bridge_document_name: `gtkb-core-spec-intake-default`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-default-003.md`
- operative_file: `bridge/gtkb-core-spec-intake-default-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-core-spec-intake-default`
- Operative file: `bridge\gtkb-core-spec-intake-default-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate note: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate when evidence is absent and no explicit
owner-waiver line is cited. No blocking gaps were reported here.

## Verification Performed

- Read live `bridge/INDEX.md`; selected thread remained latest `REVISED` before
  this verdict was filed.
- Read the full thread with
  `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-core-spec-intake-default --format json --preview-lines 1000`.
- Ran
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-default`.
- Ran
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-default`.
- Ran the Deliberation Archive search listed above.
- Inspected the live `gt project init` command wiring in
  `groundtruth-kb/src/groundtruth_kb/cli.py`.
- Checked live path state for the proposed package/test paths.

## Required Revision

File `bridge/gtkb-core-spec-intake-default-005.md` as `REVISED` after aligning
the target paths and verification plan with the promised `gt project init`
opt-out flag, or narrowing the slice so no CLI flag is claimed.

No owner decision is required from Loyal Opposition at this stage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
