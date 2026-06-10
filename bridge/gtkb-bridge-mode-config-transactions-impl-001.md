NEW

# Implementation Proposal - Bridge + Operating-Mode Switching Transactions Impl (WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001)

bridge_kind: prime_proposal
Document: gtkb-bridge-mode-config-transactions-impl
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH-MODE-CONFIG-TRANSACTIONS
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/mode_config_transactions.py", "scripts/bridge_mode_config_transaction_cli.py", "tests/scripts/test_bridge_mode_config_transactions.py"]

This NEW proposal implements `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`. Per WI description: "Build or designate the deterministic transaction component for bridge-configuration and operating-mode switch requests, and route agent instructions through it."

## Claim

A deterministic transaction component that wraps every bridge-configuration mutation and operating-mode switch into an atomic, audited unit. Each transaction: validates pre-conditions, applies the mutation, writes an audit record, and emits success/failure status. Agent invocations route through `gt mode` and `gt bridge config` CLI surfaces that internally call this transaction component.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - source spec; this WI is its implementation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; transactions preserve the index invariant.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - mode-switch transactions cited here are the mechanism this proposal lands.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - downstream consumer of the transaction component.
- `GOV-ARTIFACT-APPROVAL-001` - mode/config changes are governance acts.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - batch-6 owner authorization.
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-*` - prior slice work referenced in the WI's spec lineage.

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner directive "I authorize the remaining P0/P1. Please continue to parallelize the implementation proposals."

## Requirement Sufficiency

Existing requirements sufficient. SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 + WI description specify the transaction model.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One P1 WI; member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-15-batch6-p0p1-amendments.json`. Review-packet inventory: IP-1 (transaction component) + IP-2 (CLI) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Transaction component

`groundtruth-kb/src/groundtruth_kb/bridge/mode_config_transactions.py`:

```python
@dataclass
class TransactionResult:
    success: bool
    transaction_id: str
    pre_state: dict
    post_state: dict
    audit_path: Path
    error: str | None

def apply_mode_switch(target_mode: str, owner_decision_delib_id: str) -> TransactionResult:
    """Atomic mode-switch transaction. Validates current mode + target;
    rejects if target equals current; rejects if owner-decision DELIB
    missing. Persists pre/post state to .gtkb-state/mode-transactions/."""

def apply_bridge_config_mutation(key: str, value: Any, owner_decision_delib_id: str) -> TransactionResult:
    """Atomic bridge-config mutation. Same pattern as mode switch."""
```

Audit format: JSONL append to `.gtkb-state/mode-transactions/audit.jsonl`. Each line: `{transaction_id, action, pre, post, delib_id, timestamp, success}`.

### IP-2: CLI surface

`scripts/bridge_mode_config_transaction_cli.py`:
- `gt mode switch <target> --owner-decision DELIB-X` → calls `apply_mode_switch`.
- `gt bridge config set <key> <value> --owner-decision DELIB-X` → calls `apply_bridge_config_mutation`.
- Output: transaction_id + success/failure.

### IP-3: Tests

Tests cover: success path, target=current rejection, missing-delib rejection, audit JSONL append, transaction-id uniqueness, rollback semantics on failure.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Successful mode switch persists | `test_mode_switch_success` |
| Switch to current mode rejected | `test_mode_switch_to_current_rejected` |
| Missing owner-decision rejected | `test_missing_delib_rejected` |
| Audit JSONL appended | `test_audit_jsonl_appended` |
| Transaction-id unique | `test_transaction_id_unique` |
| Failure does not partial-mutate | `test_failure_no_partial_state` |
| Bridge-config mutation success path | `test_bridge_config_mutation_success` |

Run: `python -m pytest tests/scripts/test_bridge_mode_config_transactions.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 7 tests PASS.
- Both preflights PASS.
- Audit file exists after first transaction.

## Risks / Rollback

- Risk: existing mode-switch paths (some manual edits to `harness-state/role-assignments.json`) bypass the transaction component. Mitigation: this WI lands the component; integration of upstream callers is follow-on work.
- Risk: audit file grows unbounded. Mitigation: log rotation via sidecar dispatch-failures-jsonl-rotation work (sibling WI in BRIDGE-TOOLING-ENHANCEMENTS authorization).
- Rollback: remove module + CLI.

## Recommended Commit Type

`feat` - new transaction infrastructure for governance mutations. ~150 LOC + tests.
