NO-GO

# Loyal Opposition Review - Approval-Gate Read-Only-Flag Skip

bridge_kind: lo_verdict
Document: gtkb-approval-gate-readonly-flag-skip
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`
Verdict: NO-GO

## Claim

The defect is real: formal-artifact approval checks should not block genuinely
read-only help, version, dry-run, or validate-only invocations. The proposal is
not ready for GO because the proposed whole-command flag check can exempt a
real formal mutation when a read-only flag appears in a different shell segment,
its verification command targets a non-existent top-level test path, and the
mandatory applicability preflight still reports missing advisory
specifications.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-approval-gate-readonly-flag-skip` was `NEW`, actionable for Loyal
  Opposition.
- Read the full thread version chain. This thread currently has only
  `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory bridge applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before review.
- Inspected the current formal-artifact approval gate and matching platform
  tests.

## Prior Deliberations

Commands:

```text
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3273 formal artifact approval gate read-only --help --dry-run --validate-only" --limit 8 --json
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0835 --json
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS WI-3272 WI-3273" --limit 8 --json
```

Relevant results:

- `DELIB-0835` is the controlling owner decision for strict formal artifact
  approval and audit-trail discipline, including the requirement that formal
  artifacts not become canonical without approval, acknowledgement, or scoped
  auto-approval evidence.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` records the 2026-05-14
  owner authorization for
  `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`, including `WI-3273`.
- The targeted WI-3273 search did not surface a prior deliberation that
  contradicts adding a read-only exemption for true help/dry-run/validation
  invocations.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:ce5ef3a41710f5d0d580ca440f043c6890d56d2efaf9f88e3dd43fc439aa992b`
- bridge_document_name: `gtkb-approval-gate-readonly-flag-skip`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`
- operative_file: `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-approval-gate-readonly-flag-skip`
- Operative file: `bridge\gtkb-approval-gate-readonly-flag-skip-001.md`
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

### F1 - P1 - Whole-command read-only flag matching can bypass a real formal mutation

Observation:

- The proposal says that after `_is_formal_mutation(command)` returns true, the
  implementation should check whether the command tokens contain `--help`,
  `-h`, `--dry-run`, `--validate-only`, `--version`, or `-V`, and then return
  early without packet validation (`bridge/gtkb-approval-gate-readonly-flag-skip-001.md:62`).
- The current gate detects formal mutations across the entire command string
  with `FORMAL_MUTATION_PATTERNS` and `_is_formal_mutation()`
  (`.claude/hooks/formal-artifact-approval-gate.py:54`,
  `.claude/hooks/formal-artifact-approval-gate.py:128`,
  `.claude/hooks/formal-artifact-approval-gate.py:129`).
- The file already has command separator helpers for script-invocation
  handling (`.claude/hooks/formal-artifact-approval-gate.py:72`,
  `.claude/hooks/formal-artifact-approval-gate.py:153`,
  `.claude/hooks/formal-artifact-approval-gate.py:174`), but the proposal does
  not say the read-only flag must belong to the same command segment that
  matched the formal mutation.
- The proposed tests cover read-only flags and a quoted-value negative case,
  but do not cover semicolon, pipeline, `&&`, or `||` multi-command cases
  (`bridge/gtkb-approval-gate-readonly-flag-skip-001.md:77`,
  `bridge/gtkb-approval-gate-readonly-flag-skip-001.md:95`).

Deficiency rationale:

The formal-artifact gate protects canonical artifact writes. A whole-command
token scan can treat this shape as read-only even though the first segment is a
real mutation:

```text
python -m groundtruth_kb deliberations upsert ; echo --help
```

The mutation regex matches the first segment; the read-only flag appears in a
separate non-mutating segment. A global early return would skip packet
validation for the mutation.

Impact:

Prime Builder could accidentally or deliberately bypass `DELIB-0835` and
`GOV-ARTIFACT-APPROVAL-001` for formal artifact mutations by including a
read-only-looking token elsewhere in a compound shell command.

Recommended action:

Revise IP-1 to split the token stream into command segments using the existing
separator logic, then exempt only the segment that both matches a formal
mutation pattern and carries a read-only flag for that same invocation. Add
negative tests proving these stay blocked without a packet:

- `python -m groundtruth_kb deliberations upsert ; echo --help`
- `python -m groundtruth_kb deliberations upsert && python -m groundtruth_kb deliberations --help`
- `python -m groundtruth_kb deliberations upsert | echo --dry-run`

Keep the quoted-value negative test.

### F2 - P2 - The verification command targets a non-existent test path

Observation:

- The proposal authorizes both `tests/hooks/test_formal_artifact_approval_gate.py`
  and `platform_tests/hooks/test_formal_artifact_approval_gate.py` in
  `target_paths` (`bridge/gtkb-approval-gate-readonly-flag-skip-001.md:16`).
- The verification command runs only the top-level `tests/...` path
  (`bridge/gtkb-approval-gate-readonly-flag-skip-001.md:95`).
- Live checkout inspection found `E:\GT-KB\tests` and
  `E:\GT-KB\tests\hooks` do not exist.
- The existing matching test file is
  `platform_tests/hooks/test_formal_artifact_approval_gate.py`; it currently
  passes as part of
  `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
  with 18 total tests passing.

Deficiency rationale:

The proposal's stated verification command is not executable against the
current checkout unless Prime creates a new top-level `tests` tree. The proposal
does not explain that as an intended new test root, and it duplicates the
existing `platform_tests` location for the same hook surface.

Impact:

Prime Builder could implement tests in the wrong location or file a
post-implementation report whose command cannot be rerun by Loyal Opposition.

Recommended action:

Revise the proposal to target and run
`platform_tests/hooks/test_formal_artifact_approval_gate.py`. If a new
top-level `tests` root is intentional, state why it is needed, authorize the
parent directory creation explicitly, and add an acceptance criterion proving
the new layout is correct.

### F3 - P3 - The applicability preflight still reports missing advisory specifications

Observation:

The mandatory applicability preflight passes with `missing_required_specs: []`,
but reports:

```text
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

Deficiency rationale:

The missing advisory specs are not the primary blocker for this verdict, but
`.claude/rules/file-bridge-protocol.md` says non-empty `missing_*_specs` is a
self-detected proposal defect that should be revised before filing.

Impact:

Leaving the advisory surfaces uncited weakens traceability for a proposal that
changes a formal-artifact governance hook and discusses owner decision, work
item, specification, and verification surfaces.

Recommended action:

Add the three missing advisory specs to `Specification Links`, explain their
relevance, and rerun the bridge applicability preflight after filing the
revision.

## Positive Confirmations

- The underlying usability defect is valid: true `--help`, `--dry-run`,
  `--validate-only`, and version-only invocations should not need formal
  approval packets.
- The proposal includes owner authorization evidence, target-path metadata,
  requirement sufficiency, and a spec-derived verification table.
- Mandatory blocking preflights report no missing required specs and no
  mandatory clause evidence gaps.

## Decision

NO-GO. Revise the proposal to make read-only exemption segment-aware, use the
current `platform_tests` verification path, and clear the missing advisory
applicability items.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3273 formal artifact approval gate read-only --help --dry-run --validate-only" --limit 8 --json`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0835 --json`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS WI-3272 WI-3273" --limit 8 --json`
- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
- Targeted `Select-String`, `Test-Path`, and `rg` checks over the reviewed
  bridge file, `.claude/hooks/formal-artifact-approval-gate.py`, and the
  platform test files.

## Review Boundary

I did not modify source code or tests. This review adds only this bridge verdict
file and the corresponding `NO-GO` line in `bridge/INDEX.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
