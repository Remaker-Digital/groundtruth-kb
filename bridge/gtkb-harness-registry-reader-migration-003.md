REVISED

# Harness Role/Identity Reader Migration to the Registry Projection (WI-3342 Slice B)

bridge_kind: prime_proposal
Document: gtkb-harness-registry-reader-migration
Version: 003 (REVISED; writer-first migration ordering, expanded test target_paths, explicit no-direct-read scan exclusions)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001 (phased reader migration); DELIB-2079 Q7
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
target_paths: ["scripts/harness_projection_reader.py", "scripts/harness_roles.py", "scripts/harness_identity.py", "scripts/_kb_attribution.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/collect_dev_environment_inventory.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/scripts/**", "platform_tests/hooks/**", "platform_tests/groundtruth_kb/**"]
Recommended commit type: refactor:

## Claim

GT-KB is migrating AI-harness role and identity state from two legacy JSON files — `harness-state/role-assignments.json` and `harness-state/harness-identities.json` — to the DB-backed `harnesses` registry table surfaced through the generated `harness-state/harness-registry.json` projection. WI-3342 Slice A seeded the registry table; the table, the projection, and a DB-independent projection reader (`scripts/harness_projection_reader.py`) already exist. Slice B migrates the consumers: roughly fifteen code sites still read the two JSON files directly, and the writers still mutate the JSON.

This proposal migrates the writers to keep the DB table and projection authoritative, then migrates every production reader onto the projection, then removes the transitional JSON write. Physical deletion of the two JSON files is a gated follow-on (see Out Of Scope). It operationalizes DELIB-2079 Q7's phased migration with JSON retired last.

## Response to NO-GO (-002)

The `-002` NO-GO raised three findings; this revision addresses each:

- **F1 (target_paths omitted mode-switch / `gt harness` tests).** `target_paths` and Files Expected To Change now include `platform_tests/groundtruth_kb/**`, which covers the existing mode-switch tests (`test_mode_switch_transaction.py`, `test_mode_switch_validation.py`, `test_mode_switch_invariants.py`, `test_mode_switch_pending.py`) and `cli/test_harness_cli.py`. IP-6 and the verification commands now update and execute those suites.
- **F2 (reader-before-writer ordering risks stale SessionStart role state).** The IP sequence is re-ordered to **writer-first**: IP-2 migrates the writers to DB-write + projection regeneration with a transitional dual-write to the legacy JSON, so the projection is authoritative-fresh before any reader depends on it. Readers migrate in IP-3/IP-4; the transitional JSON write is removed in IP-5. There is no command-observable state in which readers consume the projection while writers maintain only JSON. The transitional dual-write is explicitly removed in IP-5, so it is not the permanent dual-write DELIB-2079 Q7 rejected. IP-6 adds a role-switch test asserting DB rows, regenerated projection, and projection-reader accessors agree immediately after a switch.
- **F3 (no-direct-read scan exclusions contradicted the out-of-scope list).** The scan contract is now explicit (IP-6): it flags only *executing* reads of the two JSON files and carries a named exclusion allowlist. `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` is migrated in this slice (IP-4) and has been removed from the Out Of Scope follow-on sentence.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry.
- DELIB-2079 — owner-decided Antigravity Integration design; Q7 decided the phased reader migration with JSON retired last (rejecting big-bang cutover and permanent dual-write).
- DELIB-2080 — role-portability amendment (FR9); role resolution must remain correct across the migration.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the operating-mode architecture; role/identity resolution feeds topology determination.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — operating-mode switch requests (including role mutation through `mode_switch/transaction.py`) go through a deterministic transaction component; the writer migration must preserve that transaction, validation, and audit contract.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and session-start dispatch hooks are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every migrated file is within the E:\GT-KB project root; the migration honors the project-root boundary.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design. Q7 decided the phased migration: seed first, migrate readers incrementally, retire the JSON last. This proposal implements the writer and reader migration; JSON retirement is the gated final step.
- WI-3342 Slice A (`gtkb-harness-registry-seed`, VERIFIED) seeded the `harnesses` table and established the `harness-state/harness-registry.json` projection plus the `scripts/harness_projection_reader.py` DB-independent reader.
- WI-3337 (harnesses table schema, VERIFIED) and WI-3338 (hot-path projection, VERIFIED) created the table and the projection generator.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration (DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344). This proposal requires no new owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001, DELIB-2079 Q7, and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 govern this work. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a code refactor migrating harness role/identity readers and writers from legacy JSON files to the registry projection. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3342) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Coordination With Sibling Threads

This proposal and the `gtkb-harness-data-driven-dispatch` thread (WI-3344) both modify `scripts/cross_harness_bridge_trigger.py` in disjoint regions: WI-3344 changes `_harness_command()` / `_resolve_dispatch_target()` (dispatch command construction); this proposal changes the raw role/identity readers `_load_role_assignments` / `_load_harness_identities` (lines ~595-620). Whichever thread reaches GO and implements first, the other rebases its edits onto the result; the regions do not conflict semantically. No ordering dependency exists between the two threads' GO decisions.

## Scope

### IP-1: Keyed accessor helpers on the projection reader

`scripts/harness_projection_reader.py::load_harness_projection()` returns a `harnesses` list, while the legacy JSON readers expect a dict keyed by harness ID. Add stdlib-only keyed accessors — `harness_by_id()`, `role_set_for_id()`, `id_for_name()` — so the dict-shaped readers migrate without re-implementing the list-to-dict adaptation. No behavior change; pure addition.

### IP-2: Migrate the writers (writer-first, with transitional dual-write)

Migrate the writers — `scripts/harness_roles.py` write path, `scripts/harness_identity.py` write path, `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — to mutate the DB `harnesses` table and regenerate the `harness-state/harness-registry.json` projection on every write. During the transition each writer ALSO continues to write the legacy JSON (transitional dual-write), so not-yet-migrated readers keep working. From this point the projection is authoritative-fresh, so it is safe for readers to depend on it. The `mode_switch/transaction.py` writer migration preserves the deterministic transaction, validation, and audit contract required by SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001. The transitional dual-write is removed in IP-5; it is not a permanent dual-write.

### IP-3: Migrate the foundational loaders

Repoint `scripts/harness_roles.py::load_role_assignments()` and `scripts/harness_identity.py::load_harness_identities()` to read the projection via the IP-1 accessors. `scripts/workstream_focus.py` and `scripts/session_self_initialization.py` consume these loaders and migrate automatically through that path. Preserve the existing fail-soft contract (the loaders never raise).

### IP-4: Migrate the raw-reader call sites

Migrate the sites that read the JSON files directly rather than through the foundational loaders: `scripts/_kb_attribution.py`, `scripts/cross_harness_bridge_trigger.py` (raw readers only, disjoint from WI-3344), `scripts/single_harness_bridge_dispatcher.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `scripts/collect_dev_environment_inventory.py`, the raw-path reads in `scripts/workstream_focus.py` and `scripts/session_self_initialization.py`, and the raw reads in `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` and `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`. Each migrates to the projection via the IP-1 accessors.

### IP-5: Remove the transitional JSON write

With every reader on the projection (IP-3, IP-4) and every writer keeping the DB table + projection fresh (IP-2), remove the transitional legacy-JSON write from the IP-2 writers. The DB-backed registry and its projection are now the sole authoritative surface. The two legacy JSON files are no longer written; their physical deletion remains the gated follow-on (see Out Of Scope).

### IP-6: Regression tests

Add `platform_tests/scripts/test_harness_registry_reader_migration.py` and update the affected existing tests under `platform_tests/groundtruth_kb/**` (the mode-switch transaction/validation/invariants/pending suites and `cli/test_harness_cli.py`):

- Each migrated reader resolves role/identity from the projection.
- Writers mutate the DB table and regenerate the projection; the `mode_switch/transaction.py` path preserves the deterministic transaction/validation/audit semantics per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.
- A role-switch test executes a `gt mode set-role` and a `gt harness set-role` and asserts the DB role rows, the regenerated `harness-state/harness-registry.json`, and the projection-reader accessor output all agree immediately after the switch, with the FR9 single-prime-builder role partition preserved.
- A no-direct-read scan asserts no *executing* read of `role-assignments.json` or `harness-identities.json` remains under `scripts/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, and `groundtruth-kb/src/groundtruth_kb/`. The scan distinguishes executing reads from static string constants and carries an explicit exclusion allowlist: `scripts/seed_harness_registry.py` (the seed source, which legitimately reads the legacy JSON until the gated physical-deletion follow-on), and the static non-executing string constants in `scripts/check_codex_hook_parity.py` and `scripts/rehearse/_dashboard_regen.py`.
- Role-resolution results are unchanged versus the pre-migration behavior (golden-value comparison).

## Out Of Scope

- Physical deletion of `harness-state/role-assignments.json` and `harness-state/harness-identities.json`. Per DELIB-2079 Q7, deletion is a gated follow-on proposal filed only after this thread reaches VERIFIED, the IP-6 no-direct-read scan passes, and a doctor check confirms no JSON dependency. That follow-on also updates the `scripts/seed_harness_registry.py` JSON read-side and the static string constants in `scripts/check_codex_hook_parity.py` and the rehearsal files.
- WI-3344's dispatch command-construction changes to `cross_harness_bridge_trigger.py` (separate thread; see Coordination With Sibling Threads).
- Any file outside E:\GT-KB.

## Files Expected To Change

- `scripts/harness_projection_reader.py` — keyed accessor helpers (IP-1).
- `scripts/harness_roles.py`, `scripts/harness_identity.py` — writer migration (IP-2) and foundational loader migration (IP-3).
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — writer migration preserving the transaction contract (IP-2).
- `scripts/_kb_attribution.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `scripts/collect_dev_environment_inventory.py` — raw-reader migration (IP-4).
- `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py` — raw-reader migration on the session-start hot path (IP-4).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` — raw-reader migration (IP-4).
- `platform_tests/scripts/**`, `platform_tests/hooks/**`, `platform_tests/groundtruth_kb/**` — the new migration regression test plus the affected existing mode-switch and `gt harness` CLI suites (IP-6).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 (phased reader migration) | Tests assert each migrated reader resolves role/identity from the projection; the no-direct-read scan confirms no executing JSON reader remains. |
| DELIB-2079 Q7 (phased migration, JSON retired last) | Writer-first IP order (IP-2 before IP-3/IP-4) is enforced; the transitional dual-write is removed in IP-5; JSON deletion is out of scope and gated. |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | The role-switch test runs `gt mode set-role` / `gt harness set-role` and asserts DB rows, projection, and reader accessors agree, with the deterministic transaction/validation/audit path preserved through `mode_switch/transaction.py`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The cross-harness trigger and session-start dispatch hooks resolve roles correctly post-migration — covered by their existing test suites still passing. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths are within E:\GT-KB; tests use temporary roots. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_workstream_focus.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The IP-1 keyed accessors exist on `harness_projection_reader.py`.
- [ ] Writers mutate the DB table and regenerate the projection before any reader is migrated (writer-first ordering); the transitional JSON write is removed in IP-5.
- [ ] Every production reader of the two JSON files reads the projection instead.
- [ ] The no-direct-read scan passes with its explicit exclusion allowlist — no *executing* code path reads the JSON files.
- [ ] The role-switch test confirms DB rows, projection, and projection-reader output agree immediately after `gt mode set-role` and `gt harness set-role`, with FR9 role partition preserved.
- [ ] The mode-switch and `gt harness` CLI suites under `platform_tests/groundtruth_kb/**` are updated and pass.
- [ ] Role-resolution golden-value tests confirm unchanged behavior.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing.

Observed results (run against this REVISED draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:721a70204f1116be52a3144d91bae6366079544a76e2848c92c97dffdf873859`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0` across 5 must_apply clauses.

## Risk And Rollback

**Risk R1 (high): role-resolution regression on the session-start hot path.** `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` resolve roles at SessionStart. Mitigation: writer-first ordering keeps the projection authoritative-fresh before readers depend on it; the role-switch test proves DB/projection/reader agreement; golden-value tests compare post-migration resolution against pre-migration behavior; the projection reader retains the fail-soft (never-raise) contract; the JSON files remain on disk (deletion is a separate gated proposal) so rollback is a code revert with the original data source intact.

**Risk R2 (medium): a missed reader.** A reader not in the inventory could read stale JSON after IP-5. Mitigation: the IP-6 no-direct-read scan mechanically searches for any remaining executing JSON reader and fails if one is found; the explicit exclusion allowlist prevents false positives on intentionally-retained transitional code.

**Risk R3 (low): transaction-contract regression in the writer migration.** Migrating `mode_switch/transaction.py` could weaken the deterministic validation/audit path. Mitigation: IP-6 updates and runs the `platform_tests/groundtruth_kb/**` mode-switch suites; the role-switch test asserts the transaction path still validates and audits per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

Rollback: revert the migration commits. Because JSON deletion is out of scope, the original JSON files and their data remain intact throughout; rollback restores the legacy readers and writers with no data loss.

## Loyal Opposition Asks

1. Confirm the writer-first ordering with transitional dual-write (IP-2 before IP-3/IP-4, dual-write removed in IP-5) closes the F2 stale-SessionStart-state concern.
2. Confirm the IP-6 no-direct-read scan contract — executing-read detection plus the named exclusion allowlist — is sufficient and unambiguous.
3. Confirm the inventory of readers in IP-4 is complete, or identify any missed call site.
