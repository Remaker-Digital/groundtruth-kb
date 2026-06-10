NEW

# Harness Role/Identity Reader Migration to the Registry Projection (WI-3342 Slice B)

bridge_kind: prime_proposal
Document: gtkb-harness-registry-reader-migration
Version: 001 (NEW; migrate role/identity readers and writers from the legacy JSON files to the harness-registry projection)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001 (phased reader migration); DELIB-2079 Q7
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
target_paths: ["scripts/harness_projection_reader.py", "scripts/harness_roles.py", "scripts/harness_identity.py", "scripts/_kb_attribution.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/collect_dev_environment_inventory.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/scripts/**", "platform_tests/hooks/**"]
Recommended commit type: refactor:

## Claim

GT-KB is migrating AI-harness role and identity state from two legacy JSON files — `harness-state/role-assignments.json` and `harness-state/harness-identities.json` — to the DB-backed `harnesses` registry table surfaced through the generated `harness-state/harness-registry.json` projection. WI-3342 Slice A seeded the registry table from the JSON; the table, the projection, and a DB-independent projection reader (`scripts/harness_projection_reader.py`) already exist. Slice B migrates the consumers: roughly fifteen code sites still read the two JSON files directly, and the writers still mutate the JSON.

This proposal migrates every production reader of the two JSON files to read the registry projection instead, and migrates the writers to mutate the DB `harnesses` table and regenerate the projection — so the projection becomes the authoritative read surface and never goes stale. It operationalizes DELIB-2079 Q7's phased migration ("build table + projection + CLI, seed from the current JSON, cut the readers over to the projection incrementally, retire harness-identities.json and role-assignments.json last"). Physical deletion of the two JSON files is explicitly a gated follow-on (see Out Of Scope), filed only after this thread reaches VERIFIED and a doctor check confirms no code path depends on the JSON.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry.
- DELIB-2079 — owner-decided Antigravity Integration design; Q7 decided the phased reader migration with JSON retired last (rejecting big-bang cutover and permanent dual-write).
- DELIB-2080 — role-portability amendment (FR9); role resolution must remain correct across the migration.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the operating-mode architecture; role/identity resolution feeds topology determination.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and session-start dispatch hooks are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every migrated file is within the E:\GT-KB project root; the migration honors the project-root boundary.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design. Q7 decided the phased migration: seed first, migrate readers incrementally, retire the JSON last. This proposal implements the reader/writer migration; JSON retirement is the gated final step.
- WI-3342 Slice A (`gtkb-harness-registry-seed`, VERIFIED) seeded the `harnesses` table and established the `harness-state/harness-registry.json` projection plus the `scripts/harness_projection_reader.py` DB-independent reader that this proposal's consumers migrate onto.
- WI-3337 (harnesses table schema, VERIFIED) and WI-3338 (hot-path projection, VERIFIED) created the table and the projection generator.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration (DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344). This proposal requires no new owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 and DELIB-2079 Q7 fully govern this work. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a code refactor migrating harness role/identity readers and writers from legacy JSON files to the registry projection. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3342) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Coordination With Sibling Threads

This proposal and the already-filed `gtkb-harness-data-driven-dispatch` thread (WI-3344) both modify two files, in disjoint regions:

- `scripts/cross_harness_bridge_trigger.py` — WI-3344 changes `_harness_command()` / `_resolve_dispatch_target()` (dispatch command construction, lines ~456-479 / ~637); this proposal changes the raw role/identity readers `_load_role_assignments` / `_load_harness_identities` (lines ~595-620).
- `scripts/seed_harness_registry.py` — WI-3344 populates `invocation_surfaces`; this proposal's gated JSON-retirement follow-on updates the seed's JSON read-side.

Whichever thread reaches GO and implements first, the other rebases its edits onto the result; the regions do not conflict semantically. No ordering dependency exists between the two threads' GO decisions.

## Scope

### IP-1: Keyed accessor helpers on the projection reader

`scripts/harness_projection_reader.py::load_harness_projection()` returns a `harnesses` list, while the legacy JSON readers expect a dict keyed by harness ID. Add stdlib-only keyed accessors — `harness_by_id()`, `role_set_for_id()`, `id_for_name()` — so the dict-shaped readers migrate without each re-implementing the list-to-dict adaptation. No behavior change; pure addition.

### IP-2: Migrate the foundational loaders

Repoint `scripts/harness_roles.py::load_role_assignments()` and `scripts/harness_identity.py::load_harness_identities()` to read the projection via the IP-1 accessors. These are the foundational loaders; `scripts/workstream_focus.py` and `scripts/session_self_initialization.py` consume them and migrate automatically through that path. Preserve the existing fail-soft contract (the loaders never raise).

### IP-3: Migrate the raw-reader call sites

Migrate the sites that read the JSON files directly rather than through the foundational loaders: `scripts/_kb_attribution.py`, `scripts/cross_harness_bridge_trigger.py` (raw readers only, disjoint from WI-3344), `scripts/single_harness_bridge_dispatcher.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `scripts/collect_dev_environment_inventory.py`, the raw-path reads in `scripts/workstream_focus.py` and `scripts/session_self_initialization.py`, and the raw reads in `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` and `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`. Each migrates to the projection via the IP-1 accessors.

### IP-4: Migrate the writers

Migrate the writers — `scripts/harness_roles.py` write path, `scripts/harness_identity.py` write path, `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — to mutate the DB `harnesses` table and regenerate the `harness-state/harness-registry.json` projection, so the projection (the authoritative read surface after IP-2/IP-3) never goes stale. Implementation order: IP-1, IP-2, IP-3 land before IP-4, so every reader consumes the projection before the writers stop maintaining the JSON.

### IP-5: Regression tests

Add `platform_tests/scripts/test_harness_registry_reader_migration.py` and update affected existing tests:

- Each migrated reader resolves role/identity from the projection.
- A scan-based assertion that no production code path under `scripts/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, and `groundtruth-kb/src/` reads `role-assignments.json` or `harness-identities.json` directly after migration. This is the precondition for the gated JSON-retirement follow-on.
- Writers mutate the DB table and regenerate the projection.
- Role-resolution results are unchanged versus the pre-migration behavior (golden-value comparison).

## Out Of Scope

- Physical deletion of `harness-state/role-assignments.json` and `harness-state/harness-identities.json`. Per DELIB-2079 Q7 ("retire ... last"), deletion is a gated follow-on proposal filed only after this thread reaches VERIFIED, the IP-5 no-direct-read assertion passes, and a doctor check confirms no JSON dependency. That follow-on also updates the `seed_harness_registry.py` JSON read-side and the `mcp_surface/roles.py` / `check_codex_hook_parity.py` / rehearsal string constants in one final commit.
- WI-3344's dispatch command-construction changes to `cross_harness_bridge_trigger.py` (separate thread; see Coordination With Sibling Threads).
- Any file outside E:\GT-KB.

## Files Expected To Change

- `scripts/harness_projection_reader.py` — keyed accessor helpers (IP-1).
- `scripts/harness_roles.py`, `scripts/harness_identity.py` — foundational loader migration (IP-2) and writer migration (IP-4).
- `scripts/_kb_attribution.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `scripts/collect_dev_environment_inventory.py` — raw-reader migration (IP-3).
- `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py` — raw-reader migration on the session-start hot path (IP-3).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` — raw-reader migration (IP-3).
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — writer migration (IP-4).
- `platform_tests/scripts/**`, `platform_tests/hooks/**` — the new migration regression test plus affected existing tests (IP-5).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 (phased reader migration) | Tests assert each migrated reader resolves role/identity from the projection; the no-direct-read scan confirms no JSON reader remains. |
| DELIB-2079 Q7 (phased migration, JSON retired last) | Implementation order IP-1 to IP-4 is enforced; JSON deletion is out of scope and gated; tests confirm readers migrate before writers stop maintaining JSON. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The cross-harness trigger and session-start dispatch hooks continue to resolve roles correctly post-migration — covered by their existing test suites still passing. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths are within E:\GT-KB; tests use temporary roots and never touch paths outside the project root. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q`
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_workstream_focus.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The IP-1 keyed accessors exist on `harness_projection_reader.py`.
- [ ] Every production reader of the two JSON files reads the projection instead (IP-2, IP-3).
- [ ] The writers mutate the DB table and regenerate the projection (IP-4).
- [ ] The no-direct-read scan passes — no production code path reads `role-assignments.json` or `harness-identities.json`.
- [ ] Role-resolution golden-value tests confirm unchanged behavior.
- [ ] The existing cross-harness-trigger, workstream-focus, and session-start-dispatch test suites still pass.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live NEW INDEX entry is inserted, and re-run against the indexed operative file after filing.

Observed results (run against this draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:7f3e78e1de63e5c0cc367fdc14eaa8906ee4b86c1118cdf05af297a19957ced7`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0` across 5 must_apply clauses.

## Risk And Rollback

**Risk R1 (high): role-resolution regression on the session-start hot path.** `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` resolve roles at SessionStart; a migration bug there affects every session. Mitigation: golden-value tests compare post-migration resolution against pre-migration behavior; the projection reader retains the fail-soft (never-raise) contract; IP ordering keeps readers and writers consistent; the JSON files remain on disk (deletion is a separate gated proposal) so rollback is a code revert with the original data source intact.

**Risk R2 (medium): a missed reader.** A reader not in the inventory could silently read stale JSON after IP-4. Mitigation: the IP-5 no-direct-read scan mechanically searches the codebase for any remaining JSON reader and fails if one is found.

**Risk R3 (low): projection staleness during migration.** Between IP-2/IP-3 and IP-4, writers still write JSON. Mitigation: the projection is regenerated from the table; during the transition the registry stays consistent because Slice A's seed path keeps the table synced; IP-4 lands promptly after IP-3.

Rollback: revert the migration commits. Because JSON deletion is out of scope, the original JSON files and their data remain intact throughout; rollback restores the legacy readers with no data loss.

## Loyal Opposition Asks

1. Confirm that scoping physical JSON-file deletion as a gated follow-on (rather than including it here) is the correct risk boundary.
2. Confirm the IP-1 to IP-4 implementation ordering adequately prevents a reader/writer consistency window.
3. Confirm the inventory of readers in IP-3 is complete, or identify any missed call site.
