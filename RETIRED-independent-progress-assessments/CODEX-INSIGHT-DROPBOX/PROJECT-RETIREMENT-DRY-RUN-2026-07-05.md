# Project Retirement Dry-Run Packet - 2026-07-05

## Claim

Fresh project/backlog status recomputation found 24 active projects with no open work items. This differs from the earlier 23-project estimate because `PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP` currently qualifies as active with only retired work.

This packet is a dry run only. No `gt projects retire` command was run, and no source, test, or configuration files were changed.

## Evidence

Commands run from `E:\GT-KB`:

- `gt backlog status --json`
- `gt projects list --json`
- `gt projects authorizations <PROJECT_ID> --json` for each no-open active project

Summary from `gt backlog status --json`:

- Active projects: 46
- Active projects with open work: 22
- Active projects without open work: 24
- Total project records: 309
- Total active memberships: 781
- Doubled-prefix project count: 10

## Candidates Requiring PAUTH Disposition First

These projects have no open work items but still have active project authorizations. Retiring them without a PAUTH disposition risks recreating the orphaned-PAUTH failure class already seen in dispatcher work.

| Project | Work status mix | Active PAUTHs |
| --- | ---: | --- |
| `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` | `resolved:1` | `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012` |
| `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` | `resolved:1` | `PAUTH-PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION-WI-5005-IMPLEMENTATION-PROPOSAL-FILING` |
| `PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP` | `retired:1` | `PAUTH-PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP-PROTECTED-ARTIFACT-DRIFT-ROLLUP-BOUNDED-IMPLEMENTATION-2026-06-23` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:7` | `PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA`; `PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-WI5011-UMBRELLA` |

Recommended handling: revoke, complete, supersede, or otherwise close the active PAUTHs through the governed project authorization surface before retiring these project records.

## Straightforward Retirement Candidates

These projects have active project status, no open work items, and no active PAUTHs in the project authorization surface.

| Project | Parent | Work status mix |
| --- | --- | ---: |
| `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-STABILITY` | `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION` | `resolved:1` |
| `PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY` | `PROJECT-GTKB-MAY29-HYGIENE` | `resolved:1` |
| `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-STABILITY` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` | `resolved:13, retired:1` |
| `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-FINALIZATION-TOOLING` | `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` | `resolved:1` |
| `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION-IMPLEMENTATION-PROPOSAL` | `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` | `resolved:1` |
| `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-ADVERSARIAL-REVIEW` | `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` | `resolved:1` |
| `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-SESSIONS` | `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` | `resolved:1` |
| `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FORMALIZATION-PREP` | `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-AUDIT-BRIDGE-RUNTIME-CACHE` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-AUDIT-HARNESS-CONTROL` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-AUDIT-MEMBASE-GOVERNANCE` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-AUDIT-NARRATIVE-DOCS-SCAFFOLD` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-COVERAGE-AUDIT` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-GOVERNANCE-FOUNDATION` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-MECHANICAL-GUARD` | `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS` | `resolved:1` |
| `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-01-TRANSCRIPT-RESULT-CORPUS` | `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` | `resolved:1` |
| `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-02-HARNESS-MODEL-CONFIG-TRUTH` | `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` | `resolved:1` |
| `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-05-DIRECT-MANIPULATION-PREVENTION` | `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` | `resolved:1` |
| `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-07-HARNESS-QUALITY-BENCHMARK-INTEGRATION` | `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` | `resolved:1` |
| `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-10-PRIORITIZATION-RELEASE-GATING` | `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` | `resolved:1` |

Recommended handling: retire these 20 projects through `gt projects retire` only after a final bridge/backlog freshness check immediately before mutation.

## Risk / Impact

Leaving active no-open projects in place keeps project dashboards and startup reports inflated and makes live prioritization harder. Retiring them improves current-state readability.

The main risk is premature retirement while an active PAUTH still exists. The PAUTH-bearing candidates should be handled separately so dispatch and implementation-start gates do not inherit stale authorization references.

## Recommended Action

1. Treat this packet as the dry-run inventory for a future governed retirement batch.
2. First close or supersede active PAUTHs on the 4 blocked candidates.
3. Then retire the 20 no-PAUTH candidates in one bounded project-retirement pass after re-running the no-open project query.
4. Re-run the query after retirement to confirm `active_without_open_count` drops as expected and no active PAUTH points at a retired project.
