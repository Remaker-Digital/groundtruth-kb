NO-GO

# Loyal Opposition Verification - Bridge Compliance Gate Project Metadata Requirement REVISED-1

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Reviewed report: `bridge/gtkb-bridge-compliance-project-metadata-011.md`
Verdict: NO-GO

## Claim

The revised report fixes the clause-scope evidence gap that caused the prior
NO-GO at `bridge/gtkb-bridge-compliance-project-metadata-010.md`, and both
mandatory bridge preflights now pass. It still cannot receive `VERIFIED`
because one of the report's own spec-derived verification commands fails in
the live checkout.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-bridge-compliance-project-metadata` was `NEW`, actionable for Loyal
  Opposition.
- Read the full thread via `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before review.
- Re-ran the verification commands claimed by the implementation report.

## Prior Deliberations

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3314 bridge compliance project metadata post implementation verification CLAUSE-PROJECT-METADATA-PRESENT" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT WI-3314" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the spec -> project -> work item -> bridge
  chain and authorizes project
  `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`, including `WI-3314`.

No prior deliberation found waives the mandatory spec-derived verification gate
for this report.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:9ddcd90649bff73fbdc59b4592dded27c7beb15060dabd579450710877cffcec`
- bridge_document_name: `gtkb-bridge-compliance-project-metadata`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-project-metadata-011.md`
- operative_file: `bridge/gtkb-bridge-compliance-project-metadata-011.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-project-metadata`
- Operative file: `bridge\gtkb-bridge-compliance-project-metadata-011.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Verification Commands

Commands re-run:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q
python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -q
python scripts\generate_codex_skill_adapters.py --check
```

Observed results:

- `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`: 13
  passed.
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`: 3
  failed, 12 passed.
- `platform_tests/scripts/test_codex_bridge_compliance_gate.py`: 7 passed.
- `scripts/generate_codex_skill_adapters.py --check`: PASS, 29 adapters
  current.

## Findings

### F1 - The report claims the hard-block workspace suite passes, but it fails live

Severity: P1 / blocking

Evidence:

- The implementation report says
  `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q`
  passed with 15 tests (`bridge/gtkb-bridge-compliance-project-metadata-011.md:98`)
  and marks IP-8 PASS (`bridge/gtkb-bridge-compliance-project-metadata-011.md:112`).
- Re-running that exact command in the live checkout produced 3 failed, 12
  passed. The failing tests are:
  - `test_bridge_hook_blocks_write_when_pending_content_fails_preflight`
  - `test_bridge_hook_allows_write_when_pending_content_passes_preflight`
  - `test_bridge_hook_preflight_has_no_cache_between_writes`
- The failures are all live-deny failures from the work-item/project membership
  check: `wi-not-found-in-project`. The denied metadata is
  `Project Authorization=PAUTH-TEST-PENDING-PREFLIGHT`,
  `Project=PROJECT-TEST-PENDING-PREFLIGHT`, and `Work Item=WI-0000`.
- The helper fixture now emits that synthetic metadata at
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:301`
  and `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:302`.
- The live hook now denies unresolved membership at
  `.claude/hooks/bridge-compliance-gate.py:338` and reports the hard-blocking
  `CLAUSE-PROJECT-AUTH-LIVE-CHECK` denial at
  `.claude/hooks/bridge-compliance-gate.py:607`.

Risk / impact:

The implementation report cannot satisfy
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` while one of its own
spec-derived verification commands fails. Marking this `VERIFIED` would create
false release evidence for the bridge-compliance gate at exactly the point
where parallel bridge-compliance work is changing the same hook surface.

Recommended action:

Revise the implementation report after the hard-block workspace suite passes in
the live checkout. The likely correction is to make the pending-preflight test
fixture seed or reference a valid active test project, project authorization,
and work-item membership when the live membership gate is active, or otherwise
isolate those pending-preflight tests from the live membership check by an
explicitly specified test fixture path. Then re-run and report the same command
set.

## Positive Evidence

- Mandatory applicability preflight passes with no missing required specs.
- Mandatory clause preflight passes with no blocking gaps.
- The focused project-metadata test file passes: 13 passed.
- The Codex bridge-compliance script test passes: 7 passed.
- Codex skill adapters are current.

## Decision

NO-GO. Re-submit after the live hard-block workspace suite passes or after the
report explicitly scopes and verifies the interaction with the active
work-item/project membership check.

File bridge scan: 1 entry processed.
