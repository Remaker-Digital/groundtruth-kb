ADVISORY

# Owner Role Switch Record - Codex Loyal Opposition

bridge_kind: governance_advisory
Document: gtkb-owner-role-switch-codex-loyal-opposition
Version: 001
Author: Codex (harness A)
Date: 2026-05-13 UTC

## Source

Owner chat directive on 2026-05-13: "switch role to Loyal Opposition please."

Protected artifact scope:

- `harness-state/harness-identities.json`
- `harness-state/role-assignments.json`
- `.groundtruth/inventory/dev-environment-inventory.json`
- `.groundtruth/inventory/dev-environment-inventory.md`

The role-state mutation is limited to durable harness-role assignment. Codex
harness `A` is assigned `loyal-opposition`; Claude harness `B` is assigned
`prime-builder` to preserve the required Prime Builder slot.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`
- `.claude/rules/file-bridge-protocol.md`
- `config/governance/protected-artifact-inventory-drift.toml`
- `harness-state/harness-identities.json`
- `harness-state/role-assignments.json`

## Claim

The role switch is owner-directed operational state, not implementation work.
The protected role assignment file can be updated when the change is recorded
with governance evidence and the public dev-environment inventory is refreshed
to match the new role map.

All changed active GT-KB artifacts are under `E:\GT-KB`. This bridge file is
filed under `E:\GT-KB\bridge\`, and `bridge/INDEX.md` contains the matching
ADVISORY entry at the top of the index.

Verification evidence collected before this advisory was filed:

- `harness-state/harness-identities.json` resolves Codex to durable harness ID
  `A` and Claude to durable harness ID `B`.
- `harness-state/role-assignments.json` assigns `A` only
  `loyal-opposition` and assigns `B` only `prime-builder`.
- `python scripts\check_harness_parity.py --harness codex --role loyal-opposition --json`
  returned `overall: PASS` with 19 passing checks.
- `python scripts\run_spec_derived_tests.py --bridge-id gtkb-owner-role-switch-codex-loyal-opposition`
  returned `SKIP_ADVISORY` because ADVISORY bridge threads are Loyal
  Opposition advisory reports with no implementation spec-derived test matrix.

## Specification-Derived Verification

This ADVISORY is not a VERIFIED implementation report, so there is no
application behavior spec-to-test matrix. The applicable governance checks map
to the following command evidence:

| Governance surface | Command | Observed result |
| --- | --- | --- |
| Loyal Opposition role capability parity | `python scripts\check_harness_parity.py --harness codex --role loyal-opposition --json` | `overall_status: PASS`; 19 checks passed |
| ADVISORY implementation-test boundary | `python scripts\run_spec_derived_tests.py --bridge-id gtkb-owner-role-switch-codex-loyal-opposition` | `SKIP_ADVISORY` |

## Owner Decision Needed

No further owner decision is needed. The owner already directed the role switch
in chat.

## Recommended Prime Action

Prime should acknowledge the advisory as durable role-switch evidence. No
implementation proposal is required unless Prime later wants to change the
role-assignment policy or the protected-artifact gate.

## Classification Slot

monitor

The record should remain available as audit evidence for this protected role
assignment change. No follow-on implementation is requested by this advisory.
