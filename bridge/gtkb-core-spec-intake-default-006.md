GO

# Loyal Opposition Review - Core Spec Intake Default REVISED-2

bridge_kind: lo_verdict
Document: gtkb-core-spec-intake-default
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-core-spec-intake-default-005.md`
Verdict: GO

## Claim

The `-005` revision resolves the remaining blocker from `-004`. The proposal
now includes the CLI parser file in `target_paths`, describes the
`gt project init --opt-out-core-spec-intake` Click option, threads it through
`ScaffoldOptions`, and adds a CLI-level regression test. The earlier scope
narrowing remains intact: this GO authorizes only default-on enrollment,
initial prompt emission, the init opt-out flag, and the listed tests. It does
not authorize the cross-session repeated prompt driver or a pre-existing-project
enable command.

## Prior Deliberations

Deliberation Archive searches and lookups were run before review:

```text
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GTKB-CORE-001 core spec intake default enrollment opt out init" --limit 10 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS --json
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` records owner authorization
  for `PROJECT-GTKB-ADOPTER-EXPERIENCE`, including GTKB-CORE-001.
- `DELIB-0875` records the Phase 0 owner direction: default enrollment,
  explicit opt-out, persisted stop conditions, one missing question at a time,
  and continued prompting as the broader direction.
- `DELIB-0898` / `DELIB-1181` record the prior core-spec-intake bridge thread.
- `DELIB-0893` records the prior read-only CLI slice context, supporting the
  need to scope command-surface changes explicitly.

No retrieved deliberation rejects this first implementation slice.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-default
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:8ebafe1fdf0ccb3031511eac10c3077f3b7fa8d814fc15bb874424cc8b3e4714`
- bridge_document_name: `gtkb-core-spec-intake-default`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-default-005.md`
- operative_file: `bridge/gtkb-core-spec-intake-default-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-default
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-core-spec-intake-default`
- Operative file: `bridge\gtkb-core-spec-intake-default-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Review Findings

No blocking findings.

Positive confirmations:

- Live `bridge/INDEX.md` listed this document latest as `REVISED` and
  `show_thread_bridge.py` reported no thread drift for the selected chain.
- The round-2 blocker is resolved. `target_paths` now includes
  `groundtruth-kb/src/groundtruth_kb/cli.py`
  (`bridge/gtkb-core-spec-intake-default-005.md:17`, `:27-31`).
- The proposal identifies the live `gt project init` command surface in
  `groundtruth-kb/src/groundtruth_kb/cli.py`, where the current command is
  declared at `groundtruth-kb/src/groundtruth_kb/cli.py:1972-2017` and constructs
  `ScaffoldOptions(...)` at `groundtruth-kb/src/groundtruth_kb/cli.py:2075-2088`.
- The proposed IP-2a describes the new Click option, function parameter, and
  `ScaffoldOptions` threading (`bridge/gtkb-core-spec-intake-default-005.md:109-117`).
- The proposal preserves the narrower slice boundary: cross-session repeated
  prompting and pre-existing-project enablement are explicitly out of scope
  (`bridge/gtkb-core-spec-intake-default-005.md:134-141`).
- The spec-derived verification plan includes both engine-layer and CLI-layer
  opt-out tests, plus initial prompt emission and persisted slot-state tests
  (`bridge/gtkb-core-spec-intake-default-005.md:143-159`).
- Mandatory applicability preflight passed with no missing required or advisory
  specs, and mandatory clause preflight passed with no blocking gaps.

## Implementation Scope Authorized By This GO

Prime Builder may implement only the scope described by
`bridge/gtkb-core-spec-intake-default-005.md`:

- Add `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`.
- Update `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` for default
  enrollment, initial prompt emission, and the engine-layer opt-out field.
- Update `groundtruth-kb/src/groundtruth_kb/cli.py` only to add and thread the
  `gt project init --opt-out-core-spec-intake` flag.
- Add or update `groundtruth-kb/tests/test_core_spec_intake.py` for the listed
  spec-derived tests.

This GO does not authorize the cross-session prompt driver, doctor/dashboard
surfaces, or a `gt project core-spec-intake enable` command.

## Expected Post-Implementation Verification Evidence

The implementation report should carry forward the linked specifications and
show exact observed results for:

```text
cd groundtruth-kb && python -m pytest tests/test_core_spec_intake.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

It should also identify any additional targeted command smoke tests used to
prove `gt project init --opt-out-core-spec-intake` routes through the live Click
command.

## Decision

GO. Prime Builder may implement `gtkb-core-spec-intake-default` as revised in
`bridge/gtkb-core-spec-intake-default-005.md`.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-core-spec-intake-default --format json --preview-lines 80
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-default
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-default
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GTKB-CORE-001 core spec intake default enrollment opt out init" --limit 10 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS --json
rg -n "project_init|ScaffoldOptions|core_spec_intake|project\.command" groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py
```

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
