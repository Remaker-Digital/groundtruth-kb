NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 11c6b2a8-6ba5-47b7-8c33-65f576b3b031
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session 11c6b2a8; ::init gtkb pb; WI-4510 Phase-3 default-OFF implementation report (the deferred risky-half) after GO -004; explanatory output style

# WI-4510 Phase 3 — Implementation Report: the default-OFF tafe_canonical write path (post GO -004)

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: ["scripts/bridge_index_writer.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/bridge_authority_cutover.py", "harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py", "groundtruth-kb/tests/test_tafe_authoritative_write_path.py"]

## Bridge-Protocol-Compliance

This report and its review proceed under `GOV-FILE-BRIDGE-AUTHORITY-001`: `bridge/INDEX.md`
remains the canonical, append-only bridge workflow-state surface and the canonical READ
surface for this thread. The INDEX entry for this report was appended via
`python -m groundtruth_kb.cli bridge index set-status gtkb-wi4510-phase-3-authority-flip NEW
--path bridge/gtkb-wi4510-phase-3-authority-flip-007.md` (the serialized writer chokepoint),
never a raw edit (`CLAUSE-INDEX-IS-CANONICAL`). Per the v1 authority that is still in force,
the byte-faithful generated view (`DCL-INDEX-GENERATED-VIEW-001`, proposed at gate-2) keeps
`bridge/INDEX.md` the canonical read surface even after the eventual flip.

## What this report covers (and what it does NOT)

This is the post-implementation report for the **default-OFF half** of WI-4510 Phase 3 — the
deferred "risky half" of the implementation authorized by the GO at
`bridge/gtkb-wi4510-phase-3-authority-flip-004.md`. It implements the full `tafe_canonical`
authoritative bridge write path (the cross-store fail-closed publish contract), behind the
authority-direction switch that **ships default `index_canonical`** and is **behavior-inert**
until a separate gate-2 owner decision flips it.

It does **NOT** perform the irreversible flip, the `GOV-FILE-BRIDGE-AUTHORITY-001` v2 amendment,
the `DCL-INDEX-GENERATED-VIEW-001` insert, the PAUTH expansion, or `formal_spec_promotion` — all
of which remain gate-2 owner/formal-artifact decisions exactly as the GO required (condition 1).
The live switch is verified OFF: `python scripts/bridge_authority_cutover.py status` →
`index_canonical`.

The lowest-risk slice (the switch surface + reversibility backstop: `read_authority_direction`,
`freeze`/`flip`/`revert`, `harness-state/bridge-authority-direction.json`,
`test_bridge_authority_direction.py`) was completed and verified in a prior session (DCL
assertions 3 and 4). This report adds the remaining write-path machinery (DCL assertions
6 through 11) and its failure-injection tests.

## Implemented changes (full target_paths disposition)

### Edited (authorized target_paths)

1. **`groundtruth-kb/src/groundtruth_kb/db.py`** — HIGHEST RISK (hot write surface). Extracted
   no-commit cores `_insert_flow_instance_row` / `_insert_flow_artifact_row` from
   `insert_flow_instance` / `insert_flow_artifact`; the public methods now delegate to the core
   then `commit()`, preserving their exact single-commit behavior byte-for-byte for every
   existing caller (additive; zero behavior change — proven by the unchanged 59 prereq tests).
   Added `insert_bridge_thread_atomic(planned_instances, planned_artifacts, *, changed_by,
   change_reason)`: one `BEGIN IMMEDIATE … COMMIT` over the instance row + all artifact rows,
   `except BaseException: ROLLBACK; raise`. Mirrors the existing VERIFIED stage-lease
   `BEGIN IMMEDIATE` idiom (`acquire_stage_lease`). Fixes the independent-commit hazard the GO
   named (`db.py:5445` / `db.py:6412`).

2. **`groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py`** — added the cross-store
   publish helpers, all I/O-light so they unit-test without the filesystem:
   `plan_bridge_thread_writes` (re-uses the read-only `apply=False` planner, filtered to threads
   that actually append a row), `planned_to_db_kwargs` (plan → atomic-commit kwargs, byte-matching
   `_apply_thread`'s `create_flow_instance`/`link_flow_artifact` shape), `build_prospective_shadow`
   (in-memory projection of the post-write shadow for the regenerate+verify), `assess_publish_state`
   + `PublishReconcileVerdict` (direction-aware classification: `in_sync` / `tafe_ahead` /
   `index_ahead`, detecting INDEX-ahead at both block and per-version granularity),
   `make_archived_extra_oracle` (the same terminal-archived oracle wiring `gt flow regen-verify`
   uses), and `open_flow_service` (opens the canonical `<root>/groundtruth.db` shadow service).

3. **`scripts/bridge_index_writer.py`** — added the authority-direction branch at the
   `atomic_index_update` chokepoint. Under `index_canonical` (default) the path is byte-identical
   to pre-flip behaviour; under `tafe_canonical` it delegates to `_tafe_canonical_publish`, which
   implements the contract ordering inside the held INDEX-write lock: write-start reconcile guard
   (`_reconcile_before_write`) → read → `mutate` → plan → project → regenerate → **verify before
   commit** → **single-transaction commit** (`insert_bridge_thread_atomic`) → **atomic publish** →
   post-publish self-check (`_post_publish_self_check`). Also added `reconcile_publish` (the
   lock-holding publish-reconcile recovery used by the CLI + cutover tooling), a `read_authority_direction`
   lazy reader that fails safe to `index_canonical`, an optional `project_root` override on
   `atomic_index_update`, and `CrossStorePublishError`. (Incidental: `ruff check --fix` modernized
   three pre-existing `timezone.utc` → `UTC` occurrences in untouched `_utc_now_iso`/`_is_stale`
   helpers, so the changed file passes `ruff check` cleanly — behavior-preserving.)

4. **`groundtruth-kb/src/groundtruth_kb/cli.py`** — added `gt flow publish-reconcile` (heals a
   TAFE-ahead split by republishing INDEX from the append-only shadow; quarantines INDEX-ahead;
   no-op when in sync; exits non-zero on the quarantine).

5. **`scripts/bridge_authority_cutover.py`** — added the `reconcile` subcommand delegating to
   `bridge_index_writer.reconcile_publish` (the `--reconcile` recovery entry point named in the
   proposal).

6. **`groundtruth-kb/tests/test_tafe_authoritative_write_path.py`** — NEW failure-injection suite
   (13 tests; see Spec-to-Test below).

### Authorized but deliberately NOT edited (inherit the switch at the chokepoint)

`scripts/gtkb_bridge_writer.py` (`insert_index_status` / `remove_document`),
`groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py` (`add_document` / `set_status`), and
`groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py` were inspected and confirmed to route
**every** INDEX mutation through `atomic_index_update`. Because the authority switch lives at that
single shared chokepoint, all three inherit `tafe_canonical` behaviour with **zero functional
edits** — exactly the proposal's "the switch lives at the shared chokepoint so all writers inherit
it." Editing them cosmetically would risk the byte-identical-under-`index_canonical` invariant
(DCL assertion 5 / assertion 11) for no benefit. `tafe_index_generator.py` is used read-only by the
write path (purity preserved; unchanged). `harness-state/bridge-authority-direction.json` and
`test_bridge_authority_direction.py` were the prior-slice deliverables (unchanged this slice).

## Specification Links

- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the owner-approved authority-flip decision this code
  implements (default-OFF; flip gated at gate-2).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the governance invariant; v1 still in force (the v2 amendment
  is a gate-2 formal-artifact decision). `bridge/INDEX.md` remains canonical read and workflow state.
- `DCL-INDEX-GENERATED-VIEW-001` (proposed) — the machine-checkable cross-store contract; assertions
  6 through 11 are implemented and tested by this report; assertions 3 and 4 were landed earlier.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the terminal-archived classification the
  regenerate-verify reuses (`extra_archived` tolerated; `extra_divergent` gates).
- `ADR-TAFE-SLICE-C-INGESTION-001` — the `fa-bridge-<slug>-<NNN>` / `status_token` / `artifact_ref`
  identity the plan/project/commit path records.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping below derives tests
  from each linked spec and provides executed-test evidence.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `GOV-STANDING-BACKLOG-001` — WI-4510 under the TAFE
  umbrella.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio).

## Spec-to-Test Mapping with Execution Evidence (condition 2)

The new failure-injection tests are included, not only the 59 prerequisite tests. Mapping (all in
`groundtruth-kb/tests/test_tafe_authoritative_write_path.py` unless noted):

| Linked spec / assertion | Test | Result |
|---|---|---|
| ADR authority flip + DCL assertion 2 regen-after-write byte fidelity | `test_tafe_canonical_write_records_artifact_and_regenerates` | PASS |
| DCL assertion 6 cross-store write order (verify→commit→publish), AST | `test_write_order_verify_before_commit_before_publish` | PASS |
| DCL assertion 7 single DB commit (atomic helper, not per-row inserters), AST | `test_write_path_uses_atomic_helper_not_per_row_inserters` | PASS |
| DCL assertion 8 fail-closed pre-commit divergence (Codex scenario 1) | `test_divergence_before_publish_writes_nothing` | PASS |
| DCL assertion 9 TAFE-ahead is the only post-commit failure (Codex scenario 2) | `test_publish_failure_after_commit_is_recoverable` | PASS |
| DCL assertion 10 publish-reconcile lossless + idempotent | `test_publish_reconcile_heals_losslessly_and_is_idempotent` | PASS |
| DCL assertion 11 INDEX-ahead quarantine (block-level) | `test_index_ahead_is_quarantined` | PASS |
| DCL assertion 11 INDEX-ahead quarantine (per-version) | `test_assess_classifies_per_version_index_ahead` | PASS |
| Codex scenario 3 — next-writer guard repairs a leftover split | `test_next_writer_guard_repairs_leftover_split` | PASS |
| Codex scenario 3 — revert after a split restores index_canonical (+ frozen) | `test_revert_after_split_restores_index_canonical` | PASS |
| Atomicity regression (independent-commit hazard removed; ROLLBACK) | `test_partial_thread_rolls_back` | PASS |
| GOV v2 read-surface preservation + index_canonical byte-identity | `test_index_canonical_is_byte_identical_and_writes_no_shadow` | PASS |
| Safe-default direction (absent file → index_canonical path) | `test_absent_direction_uses_index_canonical_path` | PASS |
| DCL assertion 3 safe default + assertion 4 reversibility backstop | `test_bridge_authority_direction.py` (prior slice, re-run) | PASS (11) |
| DCL assertion 1 generator purity (AST) | `test_tafe_index_generator.py::test_generator_module_performs_no_write_or_subprocess` | PASS |

Commands executed (Windows, project venv interpreter):

```
python -m pytest groundtruth-kb/tests/test_tafe_authoritative_write_path.py groundtruth-kb/tests/test_bridge_authority_direction.py groundtruth-kb/tests/test_tafe_bridge_ingestion.py groundtruth-kb/tests/test_tafe_index_generator.py -q
  -> 63 passed

python -m pytest groundtruth-kb/tests/test_tafe_cutover_evidence.py groundtruth-kb/tests/test_tafe_index_generator_cli.py -q
  -> 20 passed

python -m pytest groundtruth-kb/tests/test_tafe_authoritative_write_path.py platform_tests/scripts/test_bridge_index_writer.py groundtruth-kb/tests/test_bridge_authority_direction.py -q
  -> 36 passed   (chokepoint contract intact after the authority branch)

python -m ruff check  <6 changed .py>   -> All checks passed!
python -m ruff format --check <6 changed .py>   -> 6 files already formatted
python -m py_compile  <6 changed .py>   -> OK
```

The 59 prerequisite TAFE tests Codex cited in -004 (`test_tafe_bridge_ingestion.py`,
`test_tafe_cutover_evidence.py`, `test_tafe_index_generator.py`, `test_tafe_index_generator_cli.py`)
remain GREEN, confirming the `db.py` no-commit-core refactor is behavior-preserving for every
existing flow-write caller.

### Broader regression + transparently-reported pre-existing failures

```
python -m pytest groundtruth-kb/tests/ -k "tafe or flow or bridge or knowledge_db or cli_bridge" -q
  -> 3 failed, 792 passed, 2025 deselected
```

The 3 failures are PRE-EXISTING and live in subsystems this change does not touch; they fail
identically in isolation (not a test-ordering artifact) and are unrelated to the TAFE write path:

- `test_bridge_status_driver.py::test_bridge_status_driver_reports_role_actionability_without_verified`
  — asserts an actionable-list shape against `groundtruth_kb.bridge.notify`/live-INDEX state; the
  live INDEX now carries `ADVISORY` entries the driver surfaces (`[…, 'advisory'] != […,
  'revise-me']`). Not a file in this change set.
- `test_governance_hooks.py::test_bridge_compliance_blocks_bridge_proposal_without_spec_links` and
  `::test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` — the
  `.claude/hooks/bridge-compliance-gate.py` claim-step check fires before the spec-links /
  spec-to-test check, so the tests (which set up no claim) see the claim message. The gate hook and
  the claim CLI are not in this change set.

`git diff --stat HEAD` for this change touches only `cli.py`, `db.py`, `tafe_bridge_ingestion.py`,
`scripts/bridge_index_writer.py` (tracked) plus the untracked prior-slice `scripts/bridge_authority_cutover.py`
and the new `test_tafe_authoritative_write_path.py` — none overlap the three failing tests' subsystems.

## Flip-readiness is NOT claimed here (condition 3)

This report does **not** claim readiness for the authority flip. The final pre-cutover shadow
refresh + GREEN `cutover-evidence` / `regen-verify` are the **first steps of the gate-2 execution
window**, run immediately before the flip in the swarm-quiesced window — not part of this default-OFF
implementation. This is consistent with the GO verdict's own statement at
`bridge/gtkb-wi4510-phase-3-authority-flip-004.md` (the current RED state "is not a GO blocker …
the proposal explicitly requires final `gt flow ingest-bridge-index --apply`, GREEN
`cutover-evidence`, and GREEN `regen-verify` in the gate-2 execution window before the flip").

Current read-only state captured at report time (expected RED, documented, NOT a blocker for this
report because the flip is deferred):

```
gt flow cutover-evidence --json -> ok=false; status=evidence_gaps
  (non-zero re-plan writes: 3 instance(s), 8 artifact(s); 5 fidelity mismatch(es))
gt flow regen-verify --json    -> ok=false; status=divergent
  missing_in_generated=["gtkb-wi4510-phase-3-authority-flip"]; extra_divergent_in_generated=[]
  (the in-flight phase-3 + swarm threads are in the INDEX but not yet shadow-ingested)
```

The gate-2 execution sequence (post owner-AUQ + formal packets) closes this: `gt flow
ingest-bridge-index --apply` → GREEN `cutover-evidence`/`regen-verify` → freeze backstop →
`bridge_authority_cutover.py flip --confirm-irreversible` → post-flip smoke → resolve WI-4510.

## WI-4508 vs WI-4510 closure separation (condition 4)

This report advances **WI-4510** Phase-3 *implementation* only (the default-OFF write path). It does
**not** resolve WI-4510 (the irreversible flip and WI-4510 closure are gate-2). It does **not** touch
**WI-4508** — WI-4508 is the separate Phase-6 compatibility-view lane (the byte-faithful generator +
dual-write, VERIFIED at `bridge/gtkb-wi4510-tafe-authoritative-cutover-008.md`); this Phase-3 work
consumes that generator read-only and adds no WI-4508 closure evidence. No backlog item is resolved
by this report; WI-4510 remains open/backlogged pending gate-2. (WI-4508 and WI-4574 appear in this
report only as references — the upstream compatibility lane and the prior ingestion phantom-guard —
not as work items advanced or closed; the declared work item is WI-4510.)

## Requirement Sufficiency

Existing requirements sufficient. `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (owner-approved) governs;
`DCL-INDEX-GENERATED-VIEW-001` (assertions 6 through 11) is the derived machine-checkable
formalization this code satisfies and is created at gate-2 under `formal_spec_promotion` with its own
formal-artifact packet. No new requirement is introduced by this implementation.

## Owner Decisions / Input

This thread depends on owner approval at **gate-2** before the irreversible flip. This report does
not request those decisions; it makes the default-OFF code review-complete so the gate-2 package can
follow once Codex records VERIFIED. The gate-2 decisions, collected via `AskUserQuestion` (the only
valid owner-decision channel), remain exactly as enumerated in `-003` §"Owner Decisions / Input":

1. Gate-2 final-execute AUQ confirming the irreversible flip.
2. `GOV-FILE-BRIDGE-AUTHORITY-001` v2 amendment — formal-artifact-approval packet.
3. `DCL-INDEX-GENERATED-VIEW-001` creation (assertions 1 through 11) — formal-artifact-approval packet.
4. PAUTH expansion to permit `cutover` + `formal_spec_promotion` (the PHASE-6-7-CUTOVER PAUTH forbids
   both).

Already on record (carried forward): `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`,
`DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614`, `DELIB-20263195`. No new owner decision is required for
Codex to verify this report.

## Prior Deliberations

- `bridge/gtkb-wi4510-phase-3-authority-flip-003.md` (REVISED) + `-004` (Codex GO) — the proposal +
  GO this report implements, including the four implementation conditions addressed above.
- `bridge/gtkb-wi4510-phase-3-authority-flip-002.md` — the prior NO-GO whose F1 (cross-store
  fail-closed contract) the -003 design and these failure-injection tests satisfy.
- `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614` — owner ADR approval.
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — owner gate-1.
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — owner selection of this canonical Phase-3 path.
- `DELIB-20263195` — cutover-sequence authorization / PAUTH basis.
- Phases 0-2 VERIFIED at `bridge/gtkb-wi4510-tafe-authoritative-cutover-008.md` (byte-faithful
  generator + shadow-verify); the prior ingestion phantom-guard work eliminating the `sp1` orphan.
- Related TAFE pilot/reconciliation records: `DELIB-20263408`, `DELIB-20263285`, `DELIB-20263164`,
  `DELIB-20263283`, `DELIB-20263370`.

## Recommended Commit Type

Recommended commit type: `feat:` — adds the `tafe_canonical` cross-store fail-closed write path
(single-transaction `insert_bridge_thread_atomic` + chokepoint authority branch + publish-reconcile
guard), the `gt flow publish-reconcile` CLI + cutover `reconcile` subcommand, and the
failure-injection test suite. The default `index_canonical` path is byte-identical, and the live
switch ships OFF, so the change is purely additive new capability gated behind a default-off switch.
Commit is deferred until the full Phase-3 thread is VERIFIED, per the no-commit-until-VERIFIED rule.

## Risk / Rollback

The change is behavior-inert until gate-2 (`index_canonical` default; reader fails safe to it on any
error). The highest-risk surface — the `db.py` no-commit-core refactor on the hot
`insert_flow_instance`/`insert_flow_artifact` path — keeps the public methods byte-for-byte
behavior-preserving (cores + commit), proven by the unchanged 59 prerequisite tests and the
atomicity regression test. The `tafe_canonical` path fails closed on any pre-commit divergence
(nothing written) and self-heals a post-commit TAFE-ahead window losslessly from the append-only
shadow; INDEX-ahead is structurally impossible through the chokepoint and quarantined otherwise.
Rollback for the eventual flip remains `bridge_authority_cutover.py revert` (+ frozen INDEX
restore); for this report, nothing is committed and the switch is OFF.
