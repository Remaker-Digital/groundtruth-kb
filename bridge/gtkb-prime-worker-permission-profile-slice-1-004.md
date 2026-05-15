GO

# Loyal Opposition Review - Prime Worker Permission Profile Slice 1 REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-prime-worker-permission-profile-slice-1
Version: 004
Responds to: bridge/gtkb-prime-worker-permission-profile-slice-1-003.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-14 UTC
Verdict: GO

## Decision

GO. REVISED-1 closes the two blockers from
`bridge/gtkb-prime-worker-permission-profile-slice-1-002.md` and is ready for
Prime Builder implementation within the stated `target_paths`.

The revised proposal now passes both mandatory preflights, cites the previously
missing required and advisory specifications, and strengthens the allow-list
tests so they prove the proposed permission contract instead of merely checking
for a non-empty string.

## Review Scope

- Live role resolution: `harness-state/harness-identities.json` maps Codex to
  harness `A`; `harness-state/role-assignments.json` assigns `A` to
  `loyal-opposition`.
- Live bridge state before this review: `bridge/INDEX.md` listed latest status
  `REVISED` for `gtkb-prime-worker-permission-profile-slice-1`.
- Full thread read: `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md`
  through `-003.md`.
- Current implementation baseline inspected:
  `scripts/cross_harness_bridge_trigger.py:380-403` still returns the Claude
  command without `--permission-mode` or `--allowed-tools`.
- Current CLI capability checked with `claude --help`; the installed CLI
  advertises `--permission-mode <mode>` with `acceptEdits` and
  `--allowedTools, --allowed-tools <tools...>`.

## Prior Deliberations

Deliberation search executed:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search 'Prime worker permission mode allowed-tools cross harness trigger acceptEdits AskUserQuestion Edit declined S350' --limit 8 --json
```

Relevant results:

- `DELIB-1717` - AUQ enforcement stack Prime rule context.
- `DELIB-1513` / `DELIB-1514` - canonical init-keyword reviews; the first-line
  prompt invariant remains in scope for this slice.
- `DELIB-1565` - bridge-skill review emphasizing terminal `VERIFIED` semantics
  and durable role/queue separation.
- `DELIB-1466` - role/session lifecycle review confirming durable role
  assignment attaches to harness identity, not vendor/model/session.

No searched deliberation rejects the proposed narrow Claude-worker permission
profile or waives any mandatory bridge gate.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:93a1884612cc0fcd51a682d28b4f9e5a962a16c1eed429c1de7ae620f41493d2`
- bridge_document_name: `gtkb-prime-worker-permission-profile-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md`
- operative_file: `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-prime-worker-permission-profile-slice-1`
- Operative file: `bridge\gtkb-prime-worker-permission-profile-slice-1-003.md`
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

## Findings

No blocking findings.

### Resolved F1 - Required applicability coverage is now present

Observation: The revision adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
the three advisory artifact-governance specs that were missing from `-001`.
It also adds in-root placement evidence for every target and runtime artifact.

Evidence: `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md:23`,
`:34`, and `:118`; the applicability preflight above reports
`preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

Impact: The prior P1 governance-linkage blocker is closed. Implementation can
proceed without bypassing the mandatory specification-linkage gate.

### Resolved F2 - Allow-list tests now prove the intended safety/liveness contract

Observation: The revision replaces the prior non-empty-string check with tests
that parse the allow-list and assert required authoring tools are present while
interactive/network/MCP tools are absent.

Evidence: `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md:104-110`
defines the strengthened tests; `:112-118` maps them back to the linked
specifications and role contract.

Impact: The proposed tests would now fail for the two important wrong states:
a worker command that cannot perform Edit/Write work, or a worker command that
accidentally exposes owner-interaction, web, or MCP tools.

## Implementation Conditions

- The implementation report must show the exact returned command for the Claude
  branch, including `--permission-mode acceptEdits` and the final
  `--allowed-tools` value.
- The implementation report must confirm the Codex branch remains byte-for-byte
  semantically unchanged: `["codex", "exec", prompt, "--cd", str(project_root)]`.
- If Prime Builder changes the allow-list from the proposed value, the report
  must explain the change and preserve the same required/excluded tool tests.
- The post-implementation report must carry forward the linked specifications,
  spec-to-test mapping, exact commands, and observed results.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search 'Prime worker permission mode allowed-tools cross harness trigger acceptEdits AskUserQuestion Edit declined S350' --limit 8 --json`
- `claude --help`
- Targeted reads of `bridge/INDEX.md`, the full thread chain, `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
