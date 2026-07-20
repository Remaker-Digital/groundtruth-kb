# OPS Dispatcher Portfolio Reconciliation - Read-Only Inventory

Date: 2026-07-02
Role: Prime Builder
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Portfolio-control work item: WI-4960
Bridge thread: gtkb-dispatcher-portfolio-reconciliation

## Claim

This report records a read-only portfolio-control reconciliation for Wave 1 of the OPS Dispatcher Modernization umbrella. It does not mutate protected source/config/test files, MemBase project records, work-item records, bridge statuses, or dispatcher configuration. The portfolio-control bridge thread is latest `NEW`, so cleanup actions are deferred until `WI-4960` receives a live `GO`, a matching work-intent claim, and an implementation-start packet.

## Live Gating State

| Lane | WI | Latest bridge status | Current PB disposition |
| --- | --- | --- | --- |
| Portfolio reconciliation | WI-4960 | NEW | Not implementable. Read-only inventory only. |
| OPS lifecycle/protocol foundation | WI-4957 | GO | Parent GO exists, but LO required NO-ACTION hook registration and the hook files are outside exact target scope. Hook-scope amendment is latest NEW. |
| Dispatch lane-scoring registry/projections | WI-4958 | GO | Parent GO exists, but exact-target preflight rejects helper/test files from directory-shaped target paths. Exact-target amendment is latest NEW. |
| AUQ/headless hook launch hygiene | WI-4959 | NEW | Not implementable. Awaiting LO review. |

Dispatcher coordination evidence:

- `gt bridge dispatch daemon status --json` summarized as running in `shadow` mode with `active_substrate: none`.
- `gt bridge dispatch health --json` summarized as `WARN`.
- The current dispatcher pause has documented owner rationale in `.gtkb-state/mode-switches/20260702T173010Z-393cb661.json`: pause dispatcher spawning to break the WI-4944 blocker treadmill; resume route says reconcile WI-4943 first.

## Governed Inventory Evidence

Commands used:

- `gt bridge show <thread> --json --compact` for the four Wave 1 bridge threads and the two amendment threads.
- `gt backlog list --json --id WI-4960 --id WI-4957 --id WI-4958 --id WI-4959`.
- `gt projects show PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json`.
- `gt projects show PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION --json`.
- `gt projects show PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION --json`.
- `gt projects list --json --all --contains <term>` for dispatcher/OPS/AUQ/lane-scoring terms.
- `gt backlog list --json --all --contains <term>` for dispatcher/OPS/AUQ/lane-scoring terms, then filtered to non-terminal overlaps.
- `gt spec list --json --search <term>` for dispatch, dispatcher, bridge dispatch, TAFE, harness dispatch, runtime orchestration, AUQ, headless, lane scoring, OPS lifecycle, and NO-ACTION.
- `gt projects reconcile-doubled-prefix --project PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json` in dry-run mode.
- `gt projects reconcile-doubled-prefix --project PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION --json` in dry-run mode.

Observed counts:

- 60 project records matched dispatcher/OPS/AUQ/lane-scoring search terms, including active, retired, and adjacent projects.
- 22 non-terminal work items matched dispatcher/OPS/AUQ/lane-scoring search terms.
- 137 specs matched the broad dispatcher/OPS/AUQ/lane-scoring search terms. This is a search inventory, not a retirement list.
- `gt projects reconcile-doubled-prefix` dry-runs returned zero phantoms for both the canonical and backfilled OPS modernization project ids. The duplicate class here is not the old `PROJECT-PROJECT-*` defect; it is display-name/backfill plus parent-id/child-id duplication and needs explicit governed disposition.

## Findings

### F1 - Active duplicate umbrella family

Two active parent records exist for the same Wave 1 program:

- Keep: `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`
- Reconcile: `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION`

Evidence: `gt projects show PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json` shows the canonical parent with all four Wave 1 work items and bridge links. `gt projects show PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION --json` shows a backfilled compatibility parent containing WI-4957, WI-4958, and WI-4959.

Recommended governed disposition after WI-4960 GO: remove or supersede active memberships from the backfilled parent after confirming the canonical parent owns the active membership, then retire the backfilled parent with a change reason citing WI-4960, this report, and the GO bridge file.

### F2 - Active duplicate child-family records

Canonical child projects coexist with backfilled child records:

- Keep: `PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION`
- Keep: `PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION`
- Keep: `PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY`
- Keep: `PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE`
- Reconcile: `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION-OPS-LIFECYCLE-AND-BRIDGE-PROTOCOL-FOUNDATION`
- Reconcile: `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION-DISPATCH-LANE-SCORING-REGISTRY-AND-PROJECTIONS`
- Reconcile: `PROJECT-GT-KB-OPS-DISPATCHER-MODERNIZATION-AUQ-HEADLESS-HOOK-LAUNCH-HYGIENE`
- Reconcile: `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-PROJECT-GTKB-DISPATCHER-PORTFOLIO-RECONCILIATION`

Evidence: `gt projects list --json --all --contains dispatcher` and related filtered searches list these records as active. The explicit `gt projects show` for the parent-plus-child-ID portfolio record shows it owns WI-4960 as a backfilled subproject membership even though the canonical parent already owns WI-4960 as a program member.

Recommended governed disposition after WI-4960 GO: for each duplicate child-family record, verify canonical active membership first, then use `gt projects remove-item` or `gt projects retire-item` as appropriate, followed by `gt projects retire` for the duplicate project record. Do not use the doubled-prefix helper; dry-run evidence shows it does not cover this duplicate class.

### F3 - Compatibility fields still point at display-name project strings

WI-4957, WI-4958, and WI-4959 still surface compatibility names such as `GT-KB OPS Dispatcher Modernization` and display-name subprojects. The canonical parent record owns explicit active memberships for the WIs, but the backfilled project family persists from compatibility fields.

Recommended governed disposition after WI-4960 GO: prefer project membership authority over direct database edits. If compatibility fields keep recreating backfilled project records, file a follow-up exact-scope proposal to add a governed CLI correction path rather than editing MemBase tables ad hoc.

### F4 - Adjacent release dispatcher work is a dependency, not Wave 1 scope

Two active release-adjacent dispatcher work items remain important but should not be silently folded into Wave 1 implementation:

- `WI-4943` - Release-branch dispatcher substrate reconciliation.
- `WI-4944` - Release dispatcher LO dispatch unblock.

Evidence: both appear in the non-terminal dispatcher-overlap work-item inventory. The dispatcher pause audit points to WI-4943 as the resume route.

Recommended disposition: leave scoped under `PROJECT-GTKB-AD-HOC-RELEASE-20260701`, record as a prerequisite/constraint for resuming headless dispatch, and do not mix their source/config changes into WI-4957, WI-4958, WI-4959, or WI-4960 without a separate live GO.

### F5 - Lower-priority active dispatcher-overlap work should be classified, not bulk-folded

The non-terminal overlap scan found older or adjacent open items including `WI-4702`, `WI-4725`, `WI-4791`, `WI-4792`, `WI-4956`, and several low-priority advisory-routing rows. These may inform Wave 1 design, but they are not automatically in implementation scope.

Recommended disposition: classify each as one of `fold-into-umbrella`, `leave-scoped-elsewhere`, `defer-with-reason`, `supersede`, or `retire`. Do this under WI-4960 after GO. The default should be `leave-scoped-elsewhere` unless the item directly affects Wave 1 acceptance criteria.

### F6 - Spec overlap is broad; Wave 1 should cite a narrowed controlling set

The spec search returned 137 broad matches. The Wave 1 implementation lanes should avoid treating the whole search set as authoritative. The controlling set for near-term implementation should include, at minimum:

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001`
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`
- `SPEC-INTAKE-57a736`
- `SPEC-INTAKE-ca9165`
- `SPEC-AUQ-*` records for WI-4959 hook/AUQ hygiene
- TAFE records only when a slice touches TAFE flow-state authority

Recommended disposition: include the narrowed controlling set in implementation reports. Do not retire, supersede, or amend specs from the broad search list until WI-4960 has a GO and each spec has deterministic evidence for a terminal disposition.

## Architecture Alignment Ledger

| Axis | Alignment evidence |
| --- | --- |
| OPS consolidation | This report treats the OPS consolidation model as the parent authority and uses WI-4960 as the portfolio-control lane before broad implementation cleanup. |
| Dispatcher daemon architecture | No dispatcher config or substrate mutation was made. The live daemon remains in shadow mode with `active_substrate: none` per owner-directed pause evidence. |
| Lifecycle-first/scoring-last | WI-4958 remains paused on exact target authorization rather than implementing scoring helpers outside governed scope. This preserves lifecycle-first/scoring-last sequencing. |
| Portfolio reconciliation | Duplicate project families and adjacent dispatcher work are classified before any cleanup. Mutating disposition is deferred to a live WI-4960 GO. |

## Next Governed Actions After WI-4960 GO

1. Acquire a work-intent claim for `gtkb-dispatcher-portfolio-reconciliation`.
2. Begin implementation authorization for `gtkb-dispatcher-portfolio-reconciliation`.
3. Re-run the project/work-item/spec inventory with the same governed CLI filters.
4. Produce a concrete mutation plan for duplicate active project records and memberships.
5. Apply project membership removals/retirements only through `gt projects` commands with change reasons citing WI-4960, this report, and the GO bridge file.
6. File a WI-4960 implementation report that includes the final disposition table, commands run, and before/after project membership evidence.

