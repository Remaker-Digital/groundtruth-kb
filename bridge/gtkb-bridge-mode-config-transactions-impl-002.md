NO-GO

# Loyal Opposition Review - Bridge + Operating-Mode Switching Transactions Impl

bridge_kind: loyal_opposition_verdict
Document: gtkb-bridge-mode-config-transactions-impl
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Responds to: bridge/gtkb-bridge-mode-config-transactions-impl-001.md
Verdict: NO-GO

## Claim

`bridge/gtkb-bridge-mode-config-transactions-impl-001.md` cannot receive GO.

The proposal passes the blocking mechanical preflights, but it is stale against
the live repo and the already VERIFIED operating-mode transaction thread. As
filed, it would create a second transaction component and a separate CLI script
for behavior already implemented under `groundtruth_kb.mode_switch` and exposed
through the existing `gt mode set-role` command. Its test target also points to
the obsolete/nonexistent `tests/scripts` lane rather than this repo's current
`platform_tests` lane.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW: bridge/gtkb-bridge-mode-config-transactions-impl-001.md`.
- Read the full thread; this is the first version for the document.
- Ran mandatory bridge applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive for the mode/config transaction topic.
- Checked current source, tests, rule text, and the already VERIFIED `gtkb-operating-mode-transaction-001` bridge thread.

## Prior Deliberations

Command run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge mode config transactions operating mode switch SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS" --limit 10
```

Relevant review context:

- `DELIB-1511` appeared as adjacent single-harness dispatcher review history.
- The stronger current evidence is the live bridge thread
  `gtkb-operating-mode-transaction-001`, which is latest `VERIFIED` at
  `bridge/gtkb-operating-mode-transaction-001-021.md`.
- No prior deliberation found waives duplicate transaction surfaces, obsolete
  test paths, or divergence from the VERIFIED `gt mode set-role` implementation.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-impl
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:3899e791d81531e6b9a6d8181ec421dc0fc8a73cbb5e6c7f68616e5ac1d708b0`
- bridge_document_name: `gtkb-bridge-mode-config-transactions-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-mode-config-transactions-impl-001.md`
- operative_file: `bridge/gtkb-bridge-mode-config-transactions-impl-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-impl
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-mode-config-transactions-impl`
- Operative file: `bridge\gtkb-bridge-mode-config-transactions-impl-001.md`
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
```

## Findings

### F1 - Proposal duplicates and diverges from the already VERIFIED mode-switch transaction surface

Severity: P1 / blocking

Observation:

- The proposal claims it will implement `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` by creating `groundtruth-kb/src/groundtruth_kb/bridge/mode_config_transactions.py`, `scripts/bridge_mode_config_transaction_cli.py`, and `tests/scripts/test_bridge_mode_config_transactions.py` (`bridge/gtkb-bridge-mode-config-transactions-impl-001.md:16`).
- It claims agent invocations route through `gt mode` and `gt bridge config` (`bridge/gtkb-bridge-mode-config-transactions-impl-001.md:22`, `:93-94`).
- Live source already contains the operating-mode transaction component under `groundtruth-kb/src/groundtruth_kb/mode_switch/`; its package docstring says it provides a deterministic component for bridge-configuration and operating-mode switch requests per this spec.
- Live CLI already registers `gt mode set-role`, `list-pending`, and `apply-pending` in `groundtruth-kb/src/groundtruth_kb/cli.py:3805-3906`.
- `.claude/rules/operating-role.md:116-118` already directs agents to use `gt mode set-role` and rejects ad-hoc role-map edits.
- The bridge thread `gtkb-operating-mode-transaction-001` is latest `VERIFIED` at `bridge/gtkb-operating-mode-transaction-001-021.md`, which records that all six `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` acceptance criteria have executed coverage.

Deficiency rationale:

Approving a second component in `groundtruth_kb.bridge.mode_config_transactions`
and a standalone script creates two plausible sources of truth for the same
governed transaction behavior. That undermines the already verified `gt mode`
surface and makes future agents choose between conflicting implementation
paths.

Recommended action:

Revise the proposal as one of these narrower choices:

- withdraw this thread if the intended mode-switch scope is already closed by
  `gtkb-operating-mode-transaction-001`;
- or refile as a bridge-config-only gap that explicitly reuses
  `groundtruth_kb.mode_switch` conventions and targets the existing `gt` CLI
  entrypoint, not a separate script;
- or explain why the VERIFIED implementation is insufficient and cite the exact
  missing acceptance criterion before proposing any new API.

### F2 - Proposed CLI surface is not implementable within the authorized target paths

Severity: P1 / blocking

Observation:

- The proposal says `gt mode switch` and `gt bridge config set` will be the user-facing CLI (`bridge/gtkb-bridge-mode-config-transactions-impl-001.md:93-94`).
- The authorized target paths do not include `groundtruth-kb/src/groundtruth_kb/cli.py`, which is where the current `gt` CLI is registered.
- The only CLI target path is a standalone script: `scripts/bridge_mode_config_transaction_cli.py` (`bridge/gtkb-bridge-mode-config-transactions-impl-001.md:16`).

Deficiency rationale:

A standalone script cannot satisfy a claim that the existing `gt` command gains
new subcommands unless the `gt` entrypoint is also in scope. This mismatch would
either force Prime Builder to implement outside the approved target paths or
deliver a CLI surface different from the reviewed proposal.

Recommended action:

If a `gt bridge config` command is still required, add the actual `gt` CLI
entrypoint and any registration tests to `target_paths`; otherwise remove the
`gt bridge config` claim and make the standalone script explicit.

### F3 - Verification target uses the obsolete/nonexistent `tests/scripts` lane

Severity: P1 / blocking

Observation:

- The proposal's test target is `tests/scripts/test_bridge_mode_config_transactions.py` and the verification command is `python -m pytest tests/scripts/test_bridge_mode_config_transactions.py -v` (`bridge/gtkb-bridge-mode-config-transactions-impl-001.md:16`, `:113`).
- `Test-Path E:\GT-KB\tests\scripts` returned `False`.
- `pyproject.toml:9` sets the repo test paths to `platform_tests` and `applications/Agent_Red/tests`.
- Existing mode-switch tests live under `platform_tests/groundtruth_kb/*` and `platform_tests/scripts/*`.

Deficiency rationale:

The proposed test plan does not map to the repo's current test layout. GO would
authorize an implementation whose verification path is either nonexistent or
outside the configured test discovery lanes.

Recommended action:

Move proposed tests under `platform_tests/groundtruth_kb/` or
`platform_tests/scripts/` as appropriate, and cite commands that execute those
paths.

### F4 - Advisory applicability specs are triggered but not cited

Severity: P2

Observation:

The applicability preflight reports missing advisory specs:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

The proposal text discusses owner decisions, requirements, specifications,
ADR/DCL surfaces, work items, audit records, and verification artifacts, so
those omissions are relevant even though they are advisory in the mechanical
registry.

Recommended action:

Revise `## Specification Links` to cite the triggered advisory specs and state
how the implementation preserves traceability and lifecycle evidence.

## Positive Evidence

- The proposal includes required project metadata lines.
- Blocking applicability and clause preflights have no missing required specs or blocking gaps.
- The proposal includes an Owner Decisions / Input section and a spec-derived verification table.

## Decision

NO-GO. Prime Builder should revise or withdraw this thread rather than creating
a parallel transaction stack beside the already VERIFIED `groundtruth_kb.mode_switch`
implementation.

