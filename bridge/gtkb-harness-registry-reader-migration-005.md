REVISED

# Harness Role/Identity Reader Migration to the Registry Projection (WI-3342 Slice B)

bridge_kind: prime_proposal
Document: gtkb-harness-registry-reader-migration
Version: 005 (REVISED; adds IP-RECON one-time registry/projection reconciliation discovered after the -004 GO)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: REQ-HARNESS-REGISTRY-001 (phased reader migration); DELIB-2079 Q7
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
target_paths: ["scripts/harness_projection_reader.py", "scripts/harness_roles.py", "scripts/harness_identity.py", "scripts/_kb_attribution.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/collect_dev_environment_inventory.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/scripts/**", "platform_tests/hooks/**", "platform_tests/groundtruth_kb/**"]
Recommended commit type: refactor:

## Claim

GT-KB is migrating AI-harness role and identity state from two legacy JSON files — `harness-state/role-assignments.json` and `harness-state/harness-identities.json` — to the DB-backed `harnesses` registry table surfaced through the generated `harness-state/harness-registry.json` projection. WI-3342 Slice A seeded the registry table; the table, the projection, and a DB-independent projection reader (`scripts/harness_projection_reader.py`) already exist. Slice B migrates the consumers: roughly fifteen code sites still read the two JSON files directly, and the writers still mutate the JSON.

This proposal migrates the writers to keep the DB table and projection authoritative, then migrates every production reader onto the projection, then removes the transitional JSON write. Physical deletion of the two JSON files is a gated follow-on (see Out Of Scope). It operationalizes DELIB-2079 Q7's phased migration with JSON retired last.

The `-005` revision adds one step — IP-RECON — ahead of the reader migration: a one-time reconciliation of the `harnesses` table and projection back to the authoritative `role-assignments.json`, correcting an inversion that WI-3342 IP-2's transitional-mirror writer left in the real `groundtruth.db` during IP-2 smoke-testing. See "Response to GO (-004)" and the IP-RECON scope step.

## Response to GO (-004): Post-GO Scope Addition

This REVISED is a Prime-initiated scope addition discovered AFTER the `-004` GO. It is NOT a response to a NO-GO.

IP-1 (keyed accessors) and IP-2 (writer migration with transitional dual-write) were implemented under the `-003`/`-004` GO and are present uncommitted in the working tree. During pre-IP-3 verification Prime Builder queried the DB `harnesses` table and found it — and therefore its generated projection — inverted versus the authoritative `harness-state/role-assignments.json` (full evidence in the IP-RECON scope step below). Root cause: IP-2's transitional registry-mirror writer was exercised against the real `groundtruth.db` during IP-2 development smoke-testing.

The GO'd `-003` plan's writer-first ordering keeps the projection authoritative-fresh for FUTURE writes, but it has no step to reconcile an ALREADY-polluted projection. Migrating the IP-3 readers onto the inverted projection would make every session resolve the wrong durable role at SessionStart — the regression named in the `-002` NO-GO finding F2 and proposal Risk R1. That gap is closed by the new IP-RECON step. No other plan step changes; IP-3 through IP-6 are carried forward from `-003` unchanged except for IP-6 verification additions that assert post-IP-RECON agreement.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry. FR9 is the single-prime-builder role partition that IP-RECON restores.
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
- `bridge/gtkb-harness-registry-reader-migration-002.md` (NO-GO) finding F2 — "reader-first ordering can produce stale SessionStart role state" — is the prior deliberation most directly relevant to IP-RECON. The `-003` revision addressed F2 for FUTURE writes via writer-first ordering; IP-RECON closes the complementary case F2 did not cover: a projection ALREADY stale at the moment the reader migration begins.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration (DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344).

For this REVISED specifically: on 2026-05-18 the owner confirmed the correct durable role assignment — harness A (codex) = loyal-opposition, harness B (claude) = prime-builder — matching the authoritative `harness-state/role-assignments.json`, and directed Prime Builder to reconcile the inverted `harnesses` table and projection to that authoritative assignment before migrating any reader. IP-RECON implements that owner-directed reconciliation. It changes no role assignment (`role-assignments.json` is already correct and is not modified) and asserts no new requirement, so it requires no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 (including FR9, the single-prime-builder role partition), DELIB-2079 Q7, and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 govern this work, IP-RECON included — IP-RECON restores the FR9-conformant role partition that the IP-2 smoke-test pollution violated. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a code refactor migrating harness role/identity readers and writers from legacy JSON files to the registry projection, plus a one-time data reconciliation (IP-RECON) of two harness rows. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3342) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Coordination With Sibling Threads

The `gtkb-harness-data-driven-dispatch` thread (WI-3344) reached VERIFIED and was committed (commits `fabb31df`, `577797a9`) before this REVISED was filed. WI-3344 changed `scripts/cross_harness_bridge_trigger.py`'s dispatch command construction (data-driven dispatch from `invocation_surfaces`). This proposal's IP-4 changes a disjoint region of the same file — the raw role/identity readers `_load_role_assignments` / `_load_harness_identities`. The IP-4 edits rebase onto the committed WI-3344 state; the regions do not conflict semantically. No open ordering dependency between the two threads remains.

## Scope

### IP-1: Keyed accessor helpers on the projection reader (implemented under the -004 GO; uncommitted)

`scripts/harness_projection_reader.py::load_harness_projection()` returns a `harnesses` list, while the legacy JSON readers expect a dict keyed by harness ID. Add stdlib-only keyed accessors — `harness_by_id()`, `role_set_for_id()`, `id_for_name()` — so the dict-shaped readers migrate without re-implementing the list-to-dict adaptation. No behavior change; pure addition.

### IP-2: Migrate the writers (writer-first, with transitional dual-write) (implemented under the -004 GO; uncommitted)

Migrate the writers — `scripts/harness_roles.py` write path, `scripts/harness_identity.py` write path, `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — to mutate the DB `harnesses` table and regenerate the `harness-state/harness-registry.json` projection on every write. During the transition each writer ALSO continues to write the legacy JSON (transitional dual-write), so not-yet-migrated readers keep working. From this point the projection is authoritative-fresh, so it is safe for readers to depend on it. The `mode_switch/transaction.py` writer migration preserves the deterministic transaction, validation, and audit contract required by SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001. The transitional dual-write is removed in IP-5; it is not a permanent dual-write.

### IP-RECON: One-Time Registry/Projection Reconciliation (new in -005; executes after IP-2, before IP-3)

**Defect discovered post-GO.** During pre-IP-3 verification of the GO'd `-003` plan, Prime Builder found the DB `harnesses` registry table — and therefore its generated projection `harness-state/harness-registry.json` — inverted versus the authoritative `harness-state/role-assignments.json`.

Authoritative `role-assignments.json` (owner-set 2026-05-13; unchanged; re-confirmed by the owner 2026-05-18): harness A (codex) = `loyal-opposition`; harness B (claude) = `prime-builder`.

DB `harnesses` table current-version rows (queried 2026-05-18):

- harness A (codex): version 5, role `["prime-builder"]` — INVERTED.
- harness B (claude): version 3, role `["loyal-opposition"]` — INVERTED.

Root cause: WI-3342 IP-2's transitional registry-mirror writer (`scripts/harness_roles.py::_mirror_role_assignments_to_registry`) was exercised against the real `E:\GT-KB\groundtruth.db` during IP-2 development smoke-testing. The append-only version history records the pollution burst: harness A versions 3, 4, 5 and harness B version 3, all stamped `changed_by="harness-role-write"` / `change_reason="WI-3342 IP-2 transitional registry mirror (role write)"` at `2026-05-17T22:53:56+00:00`. The Slice A seed (version 1) and the WI-3344 invocation-surfaces write (version 2) carry the correct roles; the corruption is confined to the IP-2-attributed writes. Identities are NOT polluted — `harness_name` is `codex`/`claude` correctly in every version; only the `role` column drifted.

Why this blocks IP-3: IP-3 repoints `load_role_assignments()` and `load_harness_identities()` onto the projection. Migrating readers onto an inverted projection makes every session resolve the WRONG durable role at SessionStart — the exact regression named in the `-002` NO-GO finding F2 and proposal Risk R1. The GO'd `-003` writer-first ordering keeps the projection authoritative-fresh for FUTURE writes; it has no step to reconcile an ALREADY-polluted projection. That is a genuine gap in the `-003` plan, which is why this scope addition is filed as a REVISED rather than absorbed silently into the IP-3 commit.

Action: append exactly one corrected append-only `KnowledgeDB.insert_harness` version per harness, restoring the role recorded in the authoritative `role-assignments.json`:

- harness A (codex) -> role `["loyal-opposition"]` (new version 6).
- harness B (claude) -> role `["prime-builder"]` (new version 4).

Every other column (harness_name, harness_type, status, reviewer_precedence, invocation_surfaces, capabilities_ref) is forwarded verbatim from the harness's current row; only the `role` column is corrected. The reconciliation versions carry `changed_by="harness-registry-reconciliation"` and a `change_reason` naming the IP-2 smoke-test pollution and this IP-RECON step, so the audit trail distinguishes the corrective writes from the pollution. The projection is then regenerated via `groundtruth_kb.harness_projection.generate_harness_projection`, never by hand-editing the projection file.

The authoritative `harness-state/role-assignments.json` is NOT modified — it is already correct. The polluted rows are NOT deleted or edited — append-only versioning is preserved; only corrected current versions are appended.

Root-cause prevention: the IP-2 smoke-test DB-isolation gap is captured as a defect work item under the standing PROJECT-GTKB-RELIABILITY-FIXES project. IP-6's regression tests run against isolated temporary project roots, so the committed test suite cannot repollute the real `groundtruth.db`.

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
- IP-RECON agreement: a test reconciles a deliberately-inverted fixture `harnesses` table against an isolated authoritative `role-assignments.json`, then asserts the corrected current-version rows, the regenerated projection, and the projection-reader accessors all resolve harness A = loyal-opposition and harness B = prime-builder, with the FR9 single-prime-builder partition intact. The test uses an isolated temporary project root.
- Role-resolution results are unchanged versus the pre-migration behavior (golden-value comparison).

## Out Of Scope

- Physical deletion of `harness-state/role-assignments.json` and `harness-state/harness-identities.json`. Per DELIB-2079 Q7, deletion is a gated follow-on proposal filed only after this thread reaches VERIFIED, the IP-6 no-direct-read scan passes, and a doctor check confirms no JSON dependency. That follow-on also updates the `scripts/seed_harness_registry.py` JSON read-side and the static string constants in `scripts/check_codex_hook_parity.py` and the rehearsal files.
- WI-3344's dispatch command-construction changes to `cross_harness_bridge_trigger.py` (separate thread, already VERIFIED and committed; see Coordination With Sibling Threads).
- Any file outside E:\GT-KB.

## Files Expected To Change

- `scripts/harness_projection_reader.py` — keyed accessor helpers (IP-1).
- `scripts/harness_roles.py`, `scripts/harness_identity.py` — writer migration (IP-2) and foundational loader migration (IP-3).
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — writer migration preserving the transaction contract (IP-2).
- `scripts/_kb_attribution.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `scripts/collect_dev_environment_inventory.py` — raw-reader migration (IP-4).
- `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py` — raw-reader migration on the session-start hot path (IP-4).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`, `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` — raw-reader migration (IP-4).
- `platform_tests/scripts/**`, `platform_tests/hooks/**`, `platform_tests/groundtruth_kb/**` — the new migration regression test plus the affected existing mode-switch and `gt harness` CLI suites (IP-6).
- Generated/runtime artifacts (not Write/Edit-tool file edits, consistent with the `-003` IP-2 precedent of not listing them in `target_paths`): IP-RECON and IP-2 append rows to the `groundtruth.db` `harnesses` table via `KnowledgeDB.insert_harness` and regenerate `harness-state/harness-registry.json` via `groundtruth_kb.harness_projection` — both written by script execution, never hand-edited.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 (phased reader migration) | Tests assert each migrated reader resolves role/identity from the projection; the no-direct-read scan confirms no executing JSON reader remains. |
| REQ-HARNESS-REGISTRY-001 FR9 (single-prime-builder role partition) + IP-RECON | The IP-RECON agreement test corrects an inverted fixture `harnesses` table to the authoritative `role-assignments.json` and asserts the table, regenerated projection, and reader accessors all resolve harness A = loyal-opposition / harness B = prime-builder with the partition intact. |
| DELIB-2079 Q7 (phased migration, JSON retired last) | Writer-first IP order (IP-2 before IP-RECON before IP-3/IP-4) is enforced; the transitional dual-write is removed in IP-5; JSON deletion is out of scope and gated. |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | The role-switch test runs `gt mode set-role` / `gt harness set-role` and asserts DB rows, projection, and reader accessors agree, with the deterministic transaction/validation/audit path preserved through `mode_switch/transaction.py`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The cross-harness trigger and session-start dispatch hooks resolve roles correctly post-migration — covered by their existing test suites still passing. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths are within E:\GT-KB; tests use isolated temporary roots. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:

- `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_workstream_focus.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] IP-RECON appends corrected append-only `harnesses` versions (harness A -> loyal-opposition, harness B -> prime-builder) and regenerates the projection so the `harnesses` current-version rows, `harness-state/harness-registry.json`, and the projection-reader accessors all agree with `harness-state/role-assignments.json` BEFORE any reader is migrated in IP-3.
- [ ] IP-RECON preserves append-only history (the polluted versions are retained, not deleted) and does not modify `harness-state/role-assignments.json`.
- [ ] The IP-2 smoke-test DB-pollution root cause is captured as a defect work item under the standing PROJECT-GTKB-RELIABILITY-FIXES project.
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

The applicability preflight and the ADR/DCL clause preflight are run against this `-005` REVISED draft via `--content-file` before the live REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing.

Observed results (run against this `-005` draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:29addd5b770d6dc8b36c87cf48d4a5025159f5fbeaeb223c01e0dff7b49cf7eb`.
- Clause preflight: exit 0; 5 must_apply clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

**Risk R1 (high): role-resolution regression on the session-start hot path.** `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` resolve roles at SessionStart. Mitigation: IP-RECON reconciles the pre-existing IP-2 smoke-test inversion BEFORE any reader migrates, so IP-3 readers consume a projection that already matches the authoritative `role-assignments.json`; writer-first ordering keeps the projection authoritative-fresh thereafter; the role-switch and IP-RECON agreement tests prove DB/projection/reader agreement; golden-value tests compare post-migration resolution against pre-migration behavior; the projection reader retains the fail-soft (never-raise) contract; the JSON files remain on disk (deletion is a separate gated proposal) so rollback is a code revert with the original data source intact. Without IP-RECON, the writer-first ordering alone would leave the inverted projection in place for IP-3 to consume — IP-RECON is the load-bearing mitigation for the pre-existing inversion.

**Risk R2 (medium): a missed reader.** A reader not in the inventory could read stale JSON after IP-5. Mitigation: the IP-6 no-direct-read scan mechanically searches for any remaining executing JSON reader and fails if one is found; the explicit exclusion allowlist prevents false positives on intentionally-retained transitional code.

**Risk R3 (low): transaction-contract regression in the writer migration.** Migrating `mode_switch/transaction.py` could weaken the deterministic validation/audit path. Mitigation: IP-6 updates and runs the `platform_tests/groundtruth_kb/**` mode-switch suites; the role-switch test asserts the transaction path still validates and audits per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

**Risk R4 (low): IP-RECON appends an incorrect role.** A mistaken reconciliation could re-invert the registry. Mitigation: IP-RECON derives the corrected role for each harness directly from the authoritative `harness-state/role-assignments.json` (not from a hand-typed constant); the IP-6 agreement test asserts post-IP-RECON the table, projection, and reader accessors all match `role-assignments.json`; append-only versioning means a mistaken version is itself correctable by a further append.

Rollback: revert the migration commits. Because JSON deletion is out of scope, the original JSON files and their data remain intact throughout; rollback restores the legacy readers and writers with no data loss. IP-RECON's appended `harnesses` versions are correct-by-construction relative to `role-assignments.json` and need no rollback; if reverted anyway, a re-run of IP-RECON restores agreement.

## Loyal Opposition Asks

1. Confirm the writer-first ordering with transitional dual-write (IP-2 before IP-3/IP-4, dual-write removed in IP-5) closes the F2 stale-SessionStart-state concern for future writes.
2. Confirm the IP-6 no-direct-read scan contract — executing-read detection plus the named exclusion allowlist — is sufficient and unambiguous.
3. Confirm the inventory of readers in IP-4 is complete, or identify any missed call site.
4. Confirm IP-RECON's placement (after IP-2, before IP-3) and its append-only reconciliation mechanism (corrected `insert_harness` versions derived from the authoritative `role-assignments.json` + projection regeneration, polluted rows retained, `role-assignments.json` untouched) are the correct closure for the post-GO-discovered inversion.
