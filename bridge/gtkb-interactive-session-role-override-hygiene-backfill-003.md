REVISED
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: keep-working-2026-06-02-pb
author_model: GPT-5
author_model_version: codex-session-2026-06-02
author_model_configuration: default-reasoning
author_metadata_source: explicit-codex-automation

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3474
target_paths: ["groundtruth.db"]

# GT-KB Interactive Session Role Override - Hygiene Backfill for Slices 4-7

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-hygiene-backfill
Version: 003 (REVISED)
Date: 2026-06-02 UTC
Responds to: bridge/gtkb-interactive-session-role-override-hygiene-backfill-002.md

## Revision Claim

This revision keeps the original cleanup objective and closes all three NO-GO
findings from `-002`.

The implementation remains metadata-only. It backfills project/work-item MemBase
linkage for `WI-3474` through `WI-3477`, adds project `implements` artifact
links for the already-VERIFIED Slice 4 through Slice 7 bridge threads, and then
runs the existing verified-backlog reconciler. It does not modify source code,
tests, hooks, rules, scripts, configuration, credential files, release state, or
repository-state files.

## NO-GO Finding Responses

### F1 - PAUTH mutation-class gap

Resolved. Prime Builder created the bounded authorization
`PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001`
under existing owner-decision evidence `DELIB-2507`.

The active authorization is scoped to
`PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`, includes only `WI-3474`,
`WI-3475`, `WI-3476`, and `WI-3477`, and allows only these mutation classes:

- `work-item-related-bridge-thread-update`
- `project-artifact-link-insert`
- `backlog-reconciler-resolution`

It forbids source code, tests, hook scripts, rule files, credential files,
release publishing, and backlog bulk operations. The original project PAUTH
remains active for implementation slices, but this revision no longer asks the
bridge GO to broaden that PAUTH by prose.

### F2 - Missing one-off script

Resolved. The revised plan removes the previously proposed session-tmp backfill
script entirely. No new one-off script is created or run.

The backfill uses existing governed commands only:

- `gt backlog update` for the four `related_bridge_threads` field updates.
- `gt projects link-bridge` for the four project `implements` links.
- `scripts/bridge_verified_backlog_reconciler.py --apply` for the existing
  owner-authorized reconciliation service.

Because no script is created, no script path is included in `target_paths`.
The only target path remains `groundtruth.db`.

### F3 - Missing artifact-oriented advisory specs

Resolved. The `Specification Links` section now cites
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and the verification plan maps this
metadata-hygiene action back to those lifecycle-governance expectations.

## Multi-WI Scope Acknowledgement

This proposal coordinates one bounded hygiene action across four work items:
`WI-3474`, `WI-3475`, `WI-3476`, and `WI-3477`. The declared primary `Work
Item` field is `WI-3474` because the bridge metadata model accepts a single
work-item declaration. The additional WI IDs are explicit operational scope,
not hidden duplicate implementation work.

This is not a backlog bulk operation. It is a single-project, four-work-item
metadata repair with complete inventory, a dedicated PAUTH, and a live bridge
review before implementation.

## Premise Verification

Live `gt projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` reports
that `WI-3474` through `WI-3477` are still open and the project has `implements`
links only for Slices 1 through 3. The Slice 4 through Slice 7 bridge threads
are already VERIFIED and map as follows:

- `WI-3474`: `gtkb-interactive-session-role-override-slice-4-axis2-role-awareness`
- `WI-3475`: `gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness`
- `WI-3476`: `gtkb-interactive-session-role-override-slice-6-attribution-role-awareness`
- `WI-3477`: `gtkb-interactive-session-role-override-slice-7-doctor-marker-checks`

All operations target MemBase at `E:\GT-KB\groundtruth.db`, inside the GT-KB
project root. No Agent Red file or dependency is used.

## Implementation Plan

### Step 1 - Backfill `work_items.related_bridge_threads`

Run the existing backlog update CLI once per work item:

```text
groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-3474 --related-bridge-threads "[\"gtkb-interactive-session-role-override-slice-4-axis2-role-awareness\"]" --owner-approved --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-3475 --related-bridge-threads "[\"gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness\"]" --owner-approved --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-3476 --related-bridge-threads "[\"gtkb-interactive-session-role-override-slice-6-attribution-role-awareness\"]" --owner-approved --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-3477 --related-bridge-threads "[\"gtkb-interactive-session-role-override-slice-7-doctor-marker-checks\"]" --owner-approved --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
```

If a work item already has an existing list at implementation time, preserve
the existing list and append only the missing matching slice slug. Do not remove
existing `related_bridge_threads` values.

### Step 2 - Add project `implements` artifact links

Run the existing project-link CLI once per slice:

```text
groundtruth-kb\.venv\Scripts\gt.exe projects link-bridge PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE gtkb-interactive-session-role-override-slice-4-axis2-role-awareness --relationship implements --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe projects link-bridge PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness --relationship implements --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe projects link-bridge PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE gtkb-interactive-session-role-override-slice-6-attribution-role-awareness --relationship implements --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
groundtruth-kb\.venv\Scripts\gt.exe projects link-bridge PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE gtkb-interactive-session-role-override-slice-7-doctor-marker-checks --relationship implements --change-reason "Bridge hygiene backfill per gtkb-interactive-session-role-override-hygiene-backfill GO; PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001." --json
```

### Step 3 - Run verified-backlog reconciliation

Run the existing owner-authorized reconciler service:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_verified_backlog_reconciler.py --apply --json
```

This step may resolve `WI-3474` through `WI-3477` only if their linked bridge
threads are live, VERIFIED, and carry sufficient parent evidence. If the
reconciler reports no eligible row, the post-implementation report must explain
the fail-closed reason instead of forcing a manual resolution.

## Acceptance Criteria

1. `WI-3474` retains its existing related bridge threads and includes
   `gtkb-interactive-session-role-override-slice-4-axis2-role-awareness`.
2. `WI-3475`, `WI-3476`, and `WI-3477` each have the matching Slice 5, Slice 6,
   or Slice 7 bridge thread in `related_bridge_threads`.
3. `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` has active `implements`
   artifact links for Slice 4, Slice 5, Slice 6, and Slice 7.
4. The verified-backlog reconciler is run after the linkage backfill and its
   exact result is reported.
5. `gt projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` reflects
   the cleaned-up project state.
6. No source code, tests, hooks, rules, scripts, credential files, release
   state, or repository-state files are modified.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Commands use bridge slugs and work-item IDs only; no credential material is read or written. | Bridge helper credential scan plus staged secret scan before commit. | n/a |
| CQ-PATHS-001 | Yes | The only implementation target is in-root `groundtruth.db`; no path outside `E:\GT-KB` is used. | Implementation-start packet and MemBase command paths. | n/a |
| CQ-COMPLEXITY-001 | N/A | n/a | n/a | No source logic is added or changed. |
| CQ-CONSTANTS-001 | N/A | n/a | n/a | No source constants are added or changed. |
| CQ-SECURITY-001 | Yes | Forbid credentials, release publishing, and source or hook mutation in the PAUTH. | `gt projects authorizations PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE --json`. | n/a |
| CQ-DOCS-001 | N/A | n/a | n/a | No user-facing docs or API docs change. |
| CQ-TESTS-001 | Yes | Verify through MemBase read-back and reconciler dry-run/apply evidence instead of source tests. | Spec-derived verification commands in this proposal. | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | No logging behavior or runtime log surface changes. |
| CQ-VERIFICATION-001 | Yes | Carry forward bridge preflights, PAUTH read-back, project read-back, backlog read-back, and reconciler evidence. | Commands in Spec-Derived Verification Plan. | n/a |

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - parent architecture decision
  for the session-role override project.
- `DCL-SESSION-ROLE-RESOLUTION-001` - resolution-table architecture whose
  Slice 4 through Slice 7 verified work is being linked.
- `GOV-SESSION-ROLE-AUTHORITY-001` - session-role authority boundary for the
  project being cleaned up.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge/INDEX state is the authority
  for this proposal/revision thread.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item, and
  PAUTH metadata are present in the header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is scoped by
  the dedicated hygiene PAUTH.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH envelope bounds work
  items, specs, mutation classes, and forbidden operations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this PAUTH does not replace
  the need for a live bridge GO and implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all known
  governing specs are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation
  report must carry forward spec-to-test evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target artifacts remain under
  `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - multi-WI backlog visibility is satisfied by the
  full inventory and no hidden lifecycle bulk operation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves durable project/work-item
  metadata rather than leaving stale operational state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - verified implementation state
  triggers lifecycle hygiene and possible work-item resolution.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the bridge and MemBase artifacts
  keep the project state reviewable and auditable.
- `DELIB-2507` - owner-decision evidence for the interactive-session role
  override project and PAUTH authority.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - owner decision
  authorizing the verified-backlog reconciler service.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent
  scoping GO.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
  - Slice 4 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
  - Slice 5 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
  - Slice 6 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`
  - Slice 7 VERIFIED.

## Prior Deliberations

- `DELIB-2507` - owner directive and architecture decisions for the interactive
  session role override project.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - reconciler
  authorization and lifecycle behavior.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` - parent
  10-slice scoping plan.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent
  scoping GO.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md` - prior
  verified backfill pattern for project `implements` links.
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-005.md` - prior
  verified pattern for `related_bridge_threads` metadata backfill while
  preserving lifecycle fields.

## Owner Decisions / Input

No new owner input is required.

This revision carries forward existing owner-decision evidence:

- `DELIB-2507` - owner-approved interactive-session role override project and
  project authorization authority.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - owner-approved
  reconciler behavior.
- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001`
  version 2 - bounded hygiene authorization created from `DELIB-2507`.

## Requirement Sufficiency

Existing requirements sufficient.

The required behavior is metadata hygiene for already-VERIFIED slices under the
owner-approved interactive-session role override architecture. No new user
behavior, source behavior, deployment behavior, or specification semantics are
introduced.

## Spec-Derived Verification Plan

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: run
  `gt projects authorizations PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE --json`.
  Expected result: active hygiene PAUTH includes only `WI-3474` through
  `WI-3477` and the three allowed metadata mutation classes.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001`: run
  `gt projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`.
  Expected result: project shows Slice 4 through Slice 7 artifact links and WI
  state aligned to verified slices.
- `GOV-STANDING-BACKLOG-001`: run `gt backlog show WI-3474 --json` and the
  same command for `WI-3475`, `WI-3476`, and `WI-3477`. Expected result: every
  touched WI is inventoried and only expected metadata/lifecycle fields change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` and
  `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`: run
  `python scripts/bridge_verified_backlog_reconciler.py --dry-run --json` after
  the backfill. Expected result: no remaining unresolved candidate for
  `WI-3474` through `WI-3477`, or a documented fail-closed reason.
- Bridge proposal gates: run
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-interactive-session-role-override-hygiene-backfill`
  and
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-interactive-session-role-override-hygiene-backfill`.
  Expected result: both pass with no missing required/advisory specs and no
  blocking clause gaps.

The post-implementation report must include the exact command outputs or compact
JSON summaries for each command above.

## Pre-Filing Preflight Subsection

Before live filing, Prime Builder runs the revision helper, which enforces:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-interactive-session-role-override-hygiene-backfill --content-file <candidate>
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-interactive-session-role-override-hygiene-backfill --content-file <candidate>
```

The expected filing condition is:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- zero blocking clause gaps
- live helper filing writes `bridge/gtkb-interactive-session-role-override-hygiene-backfill-003.md`, inserts the `REVISED:` line at the top of the existing `bridge/INDEX.md` document entry, and does not delete or rewrite prior versions

## Risk And Rollback

Risk is low and bounded to MemBase metadata.

- Wrong related bridge mapping: mitigated by explicit WI-to-slice table and
  read-back verification.
- Duplicate project artifact link: mitigated by the append-only project link
  API and post-link project read-back.
- Reconciler resolves fewer or more work items than expected: mitigated by
  running and reporting `--dry-run`/read-back evidence after the linkage
  backfill. Any unexpected result is reported instead of manually forcing
  lifecycle state.
- PAUTH overreach: mitigated by the dedicated hygiene PAUTH's narrow mutation
  class list and explicit forbidden operations.

Rollback is append-only: write corrective work-item versions restoring previous
`related_bridge_threads` values, add superseding inactive project artifact-link
versions if a link is wrong, and use the reconciler repair path if it resolves
an ineligible row.

## Recommended Commit Type

`chore` - metadata hygiene only.

## Owner Action Required

None.
