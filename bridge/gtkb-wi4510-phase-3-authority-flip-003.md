REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b5f59b69-b22c-4e00-9e09-677a999addb1
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session b5f59b69; ::init gtkb pb; WI-4510 Phase-3 REVISED after NO-GO -002; cross-store fail-closed contract from recovered adversarial design panel; explanatory output style

# WI-4510 Phase 3 — TAFE-authoritative bridge state: the irreversible authority flip (REVISED after NO-GO -002)

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: ["scripts/bridge_index_writer.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/bridge_authority_cutover.py", "harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py", "groundtruth-kb/tests/test_tafe_authoritative_write_path.py"]

## Revision Summary

This REVISED version responds to the single P1 finding (F1) in
`bridge/gtkb-wi4510-phase-3-authority-flip-002.md`: the `tafe_canonical` write path needs an
**explicit cross-store fail-closed + recovery contract** between the TAFE-authoritative DB write and the
generated `bridge/INDEX.md` filesystem publish, before GO.

Everything Codex confirmed sound in -001 is preserved unchanged: the gate-2 owner-decision structure, the
PAUTH caveat (`cutover` + `formal_spec_promotion` remain forbidden until owner approval), the
`GOV-FILE-BRIDGE-AUTHORITY-001` v2 amendment text, the byte-faithful-generator architecture, the
writer-migration plan, the reversibility backstop, and the swarm-quiesce/final-re-ingest runbook. New
material added by this revision, all in service of F1:

1. A new section **"Cross-store fail-closed publish contract"** specifying the exact ordered write steps,
   the DB transaction boundary that fixes the independent-commit hazard, per-phase failure semantics, the
   recovery path, the residual window and how it is bounded/closed, and reader-staleness handling.
2. `DCL-INDEX-GENERATED-VIEW-001` assertions **#6–#11** (the machine-checkable cross-store contract).
3. Expanded writer-migration scope: `groundtruth-kb/src/groundtruth_kb/db.py` gains a single-transaction
   `insert_bridge_thread_atomic` helper; `tafe_bridge_ingestion.py` and a `gt flow publish-reconcile` CLI
   surface gain the self-healing guard. `target_paths` is updated accordingly.
4. Failure-injection tests added to the spec-to-test plan, targeting
   `groundtruth-kb/tests/test_tafe_authoritative_write_path.py`, covering Codex's three required scenarios
   plus atomicity, INDEX-ahead-quarantine, and `index_canonical` byte-identity regressions.

The cross-store contract below was designed by an adversarial design panel (three candidate strategies —
transactional-no-publish, write-ahead-recoverable, and a pure-function hybrid — each stress-tested through
crash-safety, split-brain/reader-staleness, and recovery-determinism lenses); the lowest-regret synthesis
for an irreversible migration is the hybrid recorded here.

## Findings Addressed

### F1 [P1] The TAFE-first write path needs an explicit cross-store fail-closed contract before GO — RESOLVED

The new §"Cross-store fail-closed publish contract" specifies the contract Codex required. In one sentence:
under `tafe_canonical`, the affected `flow_instance` + all its `flow_artifacts` rows commit in **one** DB
transaction **after** an in-memory regenerate-and-byte-verify of the prospective INDEX, and the INDEX atomic
publish happens **after** that single commit — so a pre-commit divergence fails closed with **both stores
byte-identical to pre-write**, and the only post-commit failure mode is a bounded, self-healing **TAFE-ahead**
window that a publish-reconcile guard re-derives losslessly (because `INDEX = render(TAFE)` and TAFE is
append-only). INDEX-ahead-of-TAFE is shown to be structurally impossible through the chokepoint and is
quarantined (never auto-ingested) if a chokepoint-bypassing edit ever produces it. The spec-to-test plan adds
failure-injection tests for Codex's three scenarios with assertions across `flow_instances`, `flow_artifacts`,
`harness-state/bridge-authority-direction.json`, live `bridge/INDEX.md`, and `regen-verify`/cutover-evidence.

## Summary

This is the **irreversible Phase 3** of WI-4510: flipping bridge authority so the **TAFE shadow
(`flow_instances` / `flow_artifacts` in `groundtruth.db`) becomes the authoritative source of bridge
workflow state**, and **`bridge/INDEX.md` becomes a byte-faithful generated view**, regenerated from
the TAFE shadow after every authoritative bridge write. It reverses today's data-flow
(`GOV-FILE-BRIDGE-AUTHORITY-001`: INDEX.md is the sole authority, TAFE is ingested *from* it).

Phase 3 is gated and does NOT execute on this proposal's GO alone. Execution requires, at gate-2:
(1) the owner **final-execute AUQ** confirming the irreversible flip; (2) the
`GOV-FILE-BRIDGE-AUTHORITY-001` amendment + the new `DCL-INDEX-GENERATED-VIEW-001`, each with its own
formal-artifact-approval packet; and (3) a project authorization that permits the `cutover` and
`formal_spec_promotion` mutation classes (the cited PHASE-6-7-CUTOVER PAUTH currently FORBIDS both —
its expansion or a gate-2 owner decision is itself part of the gate). This proposal asks Codex to
review the **design, the cross-store contract, the amended-GOV text, the new DCL, the writer-migration
plan, the reversibility backstop, and the swarm-quiesce/final-re-ingest runbook** so the gate-2 package is
review-complete.

## Why this is a switch, not a rewrite (architecture)

Phases 0-2 (VERIFIED at `bridge/gtkb-wi4510-tafe-authoritative-cutover-008.md`) deliberately built a
**byte-faithful** generator and a shadow-verify gate. Byte-fidelity is the load-bearing property:
because the generated `bridge/INDEX.md` is byte-identical to today's, **every reader, dispatcher,
hook, and automation that parses the INDEX file stays unchanged**. The migration therefore collapses
to the **writers** plus one already-built generator.

Every INDEX write funnels through a single chokepoint:
`scripts/bridge_index_writer.py::atomic_index_update(index_path, mutate, *, state_dir, ...)` —
acquire the exclusive INDEX-write lock → read INDEX → `new_text = mutate(current_text)` → atomic
write → release. The higher-level writers (`gtkb_bridge_writer.insert_index_status` / `remove_document`,
`bridge.index_mutation.add_document` / `set_status`, the `cli_bridge_index` commands, and the
propose/revise/impl-report skill helpers) all produce `new_text` through this chokepoint.

**The flip integrates at the `new_text` boundary, behind an authority-direction switch:**

- **`index_canonical` (default; current behavior, unchanged):** `new_text = mutate(current_text)`; the
  TAFE shadow continues to be ingested *from* INDEX post-write (`tafe_bridge_ingestion`).
- **`tafe_canonical` (post-flip):** the authoritative write is recorded in the TAFE shadow first
  (the `flow_artifacts` row for the affected `Document:`/status), then
  `new_text = tafe_index_generator.render_index_from_flow_artifacts(...)` — i.e. INDEX is *regenerated*
  from the now-authoritative TAFE shadow, still written atomically under the same lock, and checked
  byte-faithful via `verify_against_index` (regen-verify GREEN: `missing=[]`, `extra_divergent=[]`).
  On any divergence the write fails closed, so a non-byte-faithful INDEX can never be published. The
  exact ordering, transaction boundary, and recovery semantics are specified in the next section.

The switch lives at the shared chokepoint so all writers inherit it; any writer found bypassing the
chokepoint is routed through it as part of the migration.

## Cross-store fail-closed publish contract (resolves NO-GO -002 F1)

This section is the explicit cross-store publish/recovery contract Codex required. It is the **prepare →
single-transaction commit → atomic publish** hybrid: do all expensive work (plan, regenerate, byte-verify)
*before* the DB commit (so the common divergence case never splits the stores), make the commit a single
all-or-nothing transaction (so the DB side is never a half-thread), and back the irreducible
commit→publish residue with a self-healing publish-reconcile guard (so a crash in that window self-heals).

### Foundational asymmetry

Post-flip, `bridge/INDEX.md = render_index_from_flow_artifacts(TAFE)`. INDEX carries **no information not
derivable from the authoritative TAFE shadow**, and the TAFE store is **append-only** (no UPDATE/DELETE per
the MemBase versioning invariant). Two consequences drive the whole contract:

- A **TAFE-ahead** split (DB committed, INDEX not yet republished) is **losslessly repairable** by
  re-deriving INDEX from TAFE. No committed `flow_instances`/`flow_artifacts` row is ever rolled back or
  deleted to recover; recovery only *finishes* an interrupted publish.
- An **INDEX-ahead** split (INDEX shows a state the authority never recorded) would be **unrecoverable**.
  Therefore the write order must make INDEX-ahead structurally impossible (see "INDEX-ahead is impossible").

### Exact write order (integrated at the `atomic_index_update` chokepoint, under `tafe_canonical`)

All steps run inside the single exclusive INDEX-write lock (`index_write_lock`, `O_CREAT|O_EXCL`,
bounded-wait, TTL-reclaimed). Under `index_canonical` the path is byte-identical to today
(`new_text = mutate(current_text)`; `_atomic_write`); the steps below are the `tafe_canonical` branch only.

1. **Acquire** the exclusive INDEX-write lock (the cross-store mutex). Read `authority_direction` from
   `harness-state/bridge-authority-direction.json` inside the lock (absent ⇒ `index_canonical`).
2. **Write-start reconcile guard.** Before any new work, run the publish-reconcile guard (below) so a
   leftover split from a previously-crashed writer is healed *before* this write builds on the read surface.
3. **Read** live `bridge/INDEX.md` (`current_text`; missing ⇒ `""`) and capture the preamble/header the
   regen-verify CLI uses.
4. **Plan** (no DB write, no FS write): compute the intended TAFE mutation for the affected
   `Document:`/status (instance row + per-version `fa-bridge-<slug>-<NNN>` artifacts), reusing the existing
   `tafe_bridge_ingestion` planning shape (the `apply=False` dry-run path).
5. **Project** the prospective post-write shadow in memory: overlay the planned rows on the current
   `list_flow_instances()` + `list_flow_artifacts(...)` to produce `prospective_instances` /
   `prospective_artifacts` (no DB write yet).
6. **Regenerate** the prospective INDEX: `prospective_text =
   render_index_from_flow_artifacts(prospective_instances, prospective_artifacts, header=...)` (pure; no I/O).
7. **Byte/semantic verify BEFORE any commit:** `verify_against_index(prospective_text, prospective_*)` must
   be `semantic_equal` (`missing_in_generated==[]`, `extra_divergent_in_generated==[]`, no
   version-line mismatch; `extra_archived` tolerated per `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`).
   If not ⇒ **raise, having written nothing** (no DB, no FS). This is the fail-closed point for the common
   divergence case.
8. **DB commit point (single transaction):** `insert_bridge_thread_atomic(planned_instance,
   planned_artifacts, ...)` issues `BEGIN IMMEDIATE` → instance row + all artifact rows (via no-commit
   cores) → `COMMIT`; on any exception `ROLLBACK` and re-raise. This is the single irreducible DB commit
   for the whole write.
9. **INDEX publish point (atomic rename):** `_atomic_write(index_path, prospective_text)` — sibling-temp +
   `os.replace` (atomic on Windows and POSIX). The published bytes are exactly the already-verified
   `prospective_text`; nothing is recomputed between verify and publish.
10. **Post-publish self-check (in-lock):** re-read INDEX, assert it equals `prospective_text` and that
    `verify_against_index(live_index, committed_*)` is `semantic_equal`. A failure here triggers the
    reconcile republish (it never rolls back the now-durable TAFE; it re-derives INDEX from it).
11. **Release** the lock (context-manager `finally`).

Step 7 (verify) precedes step 8 (DB commit) precedes step 9 (FS publish). The only mutating steps are 8 and
9, made as adjacent and short as possible inside the held lock.

### DB transaction boundary (fixes the independent-commit hazard F1 names)

Today `insert_flow_instance` commits at `db.py:5445` and `insert_flow_artifact` commits at `db.py:6412`,
**independently** — for one instance + N artifacts that is N+1 separate commits, so a crash mid-sequence can
leave a half-written thread. The fix reuses the `BEGIN IMMEDIATE … COMMIT / except: ROLLBACK` idiom already
present in `db.py` (e.g. `acquire_stage_lease` ~5929-5978):

- Refactor the SQL bodies of `insert_flow_instance` / `insert_flow_artifact` into private no-commit cores
  (`_insert_flow_instance_row`, `_insert_flow_artifact_row`) that execute the INSERT on the passed `conn`
  **without** calling `conn.commit()`. The existing public methods keep their exact single-commit behavior
  by wrapping core+commit (zero behavior change for every current caller — ingestion apply path, pilot,
  tests).
- Add `insert_bridge_thread_atomic(planned_instance, planned_artifacts, *, changed_by, change_reason)`:
  `BEGIN IMMEDIATE` → `_insert_flow_instance_row` → each `_insert_flow_artifact_row` → `COMMIT`, with
  `except: ROLLBACK; raise`. The `tafe_canonical` write path (step 8) calls **only** this method, so the
  instance and all its artifacts are one atomic DB commit. `BEGIN IMMEDIATE` takes the SQLite write lock at
  statement start, so even without the file lock two writers serialize rather than interleave partial commits.

### Failure semantics (per phase)

- **Pre-commit failure (steps 1-7):** any failure before `BEGIN IMMEDIATE` and before `_atomic_write` leaves
  `groundtruth.db` unchanged (no INSERT issued) and `bridge/INDEX.md` unchanged (no `os.replace` issued);
  `authority_direction` unchanged. The writer raises and the bridge write fails closed. This is the common
  case for a divergence detected by step 7 — the write is rejected *before* it can split the stores. No
  recovery needed; state is byte-identical to pre-write. (Directly satisfies Codex's "test that the TAFE
  shadow is unchanged".)
- **Post-TAFE-commit / pre-INDEX-publish failure (steps 8→9; the F1 window):** the DB commit succeeded, then
  the process/host dies before or during `_atomic_write`. State: TAFE is exactly **one authoritative write
  ahead** of the published INDEX (new `flow_artifacts` row durable; INDEX still shows the prior version).
  Because `_atomic_write` uses sibling-temp + `os.replace`, INDEX is never torn — it is fully-old or
  fully-new; the temp file is orphaned and ignored. The split is bounded to one write and is
  **deterministically repairable** by regenerating INDEX from the durable TAFE rows (recovery path). No TAFE
  rollback is attempted (rolling back committed authoritative append-only rows would itself be lossy/racy).
  Readers in the window see a **stale-but-valid** INDEX (one version behind), never corrupt, never
  ahead-of-authority.
- **INDEX publish failure (step 9):** `_atomic_write` raises after the DB commit (disk full, permission, AV
  lock on Windows during `os.replace`). Same state and same repair as the window case: TAFE committed, INDEX
  still old, temp cleaned by `_atomic_write`'s `BaseException` handler. The in-lock post-publish self-check
  (step 10) catches it in the live process and retries the publish from the already-verified
  `prospective_text` (still in memory); if that also fails, it leaves the deterministic TAFE-ahead state for
  the next-writer guard / `--reconcile` to repair — lossless because `INDEX = render(TAFE)`.

### Recovery path (publish-reconcile guard)

Detection runs (a) at the top of every `tafe_canonical` write inside the lock (step 2), (b) as a standalone
`gt flow publish-reconcile` / `scripts/bridge_authority_cutover.py --reconcile`, and (c) at session startup.
The guard reads live INDEX + the live TAFE shadow and runs `verify_against_index`:

- `semantic_equal` (only `extra_archived`) ⇒ in sync; proceed.
- `extra_divergent_in_generated` / version mismatch where the shadow is **ahead** (the F1 window) ⇒
  **TAFE-ahead**: repair by `_atomic_write(render_index_from_flow_artifacts(instances, artifacts, header))`
  under the held lock, then re-verify `semantic_equal`.
- `missing_in_generated` non-empty (INDEX has a thread/version the shadow lacks) ⇒ **INDEX-ahead**: treated
  as contamination from a chokepoint-bypassing edit; the guard **refuses to auto-apply it** and surfaces a
  repair-required defect for owner/LO disposition, so a stray edit can never silently become authoritative.

**Lossless + idempotent:** republishing from the append-only TAFE shadow cannot lose an authoritative write;
no committed row is deleted/rolled back during recovery; a second run finds `semantic_equal` and a no-op.
Three converging actors guarantee self-heal: the in-lock post-publish self-check (live process), the next
writer's write-start guard (heals before its own write), and the operator `--reconcile` / `--revert`. The
frozen immutable INDEX copy remains the disaster-recovery floor for the `index_canonical` rollback, but
normal F1-window repair never needs it because TAFE alone is sufficient.

### Residual window and how it is bounded/closed

The smallest remaining window is between the DB `COMMIT` returning (step 8) and `os.replace` completing
(step 9) — microseconds-to-low-milliseconds, because all expensive work (plan, project, regenerate, verify)
is already done and the published text is the already-computed in-memory `prospective_text`. SQLite +
filesystem cannot be made one hardware-atomic transaction, so this two-phase-commit residue is irreducible.
It is bounded/closed four ways: (1) **magnitude** — exactly one write can be in the window (the whole
sequence is inside the exclusive lock), so the split is never more than one version line on one Document;
(2) **corruption** — `os.replace` ⇒ INDEX fully-old-or-fully-new (never torn); `BEGIN IMMEDIATE`+`COMMIT` ⇒
DB all-or-nothing (never a half-thread); (3) **time** — closed in the same lock-hold by the post-publish
self-check (live case) or by the very next writer's guard / `--reconcile` (crash case); (4) **direction** —
the window can only leave **TAFE-ahead** (safe, repairable), never INDEX-ahead.

### Reader-staleness handling (no reader migrated)

No reader is migrated — byte-fidelity keeps the blast radius at the writers (DCL #5). In the residual window
a reader/dispatcher re-reading live `bridge/INDEX.md` (as `GOV-FILE-BRIDGE-AUTHORITY-001` v2 still mandates)
observes an INDEX at most one authoritative write behind the shadow — the previous valid bridge state, never
corrupt, never ahead-of-authority. This is safe without migrating readers because: (a) the window only
produces TAFE-ahead, so the worst a reader sees is staleness equivalent to having scanned a few milliseconds
earlier — a condition the async, non-transactional bridge model already tolerates by design; (b) a dispatcher
acts on the prior actionable signature and the next signature recompute (after the guard finishes the
interrupted publish) picks up the change — dispatch is signature-driven, not edge-triggered on a single read,
so no dispatch is missed; (c) the dangerous inverse (reader sees INDEX *ahead* of authority) is structurally
prevented. The next-writer guard republishes before its own write, and `gt flow regen-verify` /
cutover-evidence remain the operator's on-demand GREEN/RED staleness probe.

### INDEX-ahead is structurally impossible (through the chokepoint)

For any write through the chokepoint, the DB commit (step 8) strictly precedes the INDEX publish (step 9),
and the published bytes are regenerated from the prospective shadow that becomes durable at step 8. There is
no `tafe_canonical` path that writes INDEX content not derived from an already-committed TAFE state — so the
window can only leave INDEX *behind*, never ahead. The only way INDEX could become ahead is a write that
**bypasses** the chokepoint (a raw/manual INDEX edit, or a legacy writer not routed through
`atomic_index_update`). This is defended in depth: (1) the writer-migration inventory routes every writer
through the chokepoint; (2) the reconcile guard treats `missing_in_generated` as contamination and refuses
to ingest it; (3) the existing INDEX-write guard (GTKB-INDEX-WRITE-GUARD / WI-4481) already blocks raw
Edit/Write of `bridge/INDEX.md`. Within the protocol INDEX-ahead is impossible by construction; outside it,
it is detected and quarantined rather than promoted.

## Proposed amendment — GOV-FILE-BRIDGE-AUTHORITY-001 (v1 → v2)

Surgical change to the *authority-source* clause only. The **LO permanent bridge-repair authority** and
the **"re-read live INDEX before any operational decision"** read-discipline are PRESERVED verbatim
(the read-discipline survives because the generated INDEX is byte-faithful — INDEX remains the canonical
READ surface even though TAFE becomes the canonical WRITE/authority surface).

Proposed v2 statement (full text for owner approval at gate-2):

> The Prime Builder / Loyal Opposition file bridge is a durable coordination mechanism. The
> authoritative source for bridge queue state is the TAFE shadow — the `flow_instances` and
> `flow_artifacts` tables in `groundtruth.db`. `bridge/INDEX.md` is a byte-faithful **generated view**
> of that authoritative state, regenerated from the TAFE shadow after every authoritative bridge write
> per `DCL-INDEX-GENERATED-VIEW-001`. The authority direction is recorded in a single canonical state
> surface (`harness-state/bridge-authority-direction.json`); `index_canonical` is the legacy/rollback
> direction in which `bridge/INDEX.md` is written directly and TAFE is ingested from it.
>
> Because the generated view is kept byte-faithful, `bridge/INDEX.md` remains the canonical READ
> surface: startup reports, dashboard fields, cached scan counts, copied excerpts, summaries, and any
> other artifacts derived from `bridge/INDEX.md` are context only. They must not be used to determine
> the current bridge queue, latest document status, actionable entry count, bridge health, or
> processing order. Any startup, review, repair, automation, dashboard, or report workflow that needs
> bridge state must re-read the live `bridge/INDEX.md` file before making an operational decision.
>
> Reverting authority to `index_canonical` (restoring `bridge/INDEX.md` as the directly-written
> authority) is the documented rollback for the cutover; see the reversibility backstop in the WI-4510
> Phase-3 thread.
>
> [Paragraphs 3-4 unchanged: Loyal Opposition has permanent owner authority to diagnose and repair
> correct bridge function and correct bridge use … Bridge-scope repairs should stay targeted to bridge
> function/use, preserve the bridge audit trail, and report the resulting changes after the repair.]

## Proposed new spec — DCL-INDEX-GENERATED-VIEW-001 (design_constraint, derived from ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001)

Machine-checkable constraints for the generated-view regime. Assertions #1–#5 are unchanged from -001;
#6–#11 are the cross-store contract added by this revision.

1. **Generator purity.** `tafe_index_generator.render_index_from_flow_artifacts` performs no INDEX
   write and no subprocess (AST-asserted by `test_tafe_index_generator.py::test_generator_module_performs_no_write_or_subprocess`).
2. **Regenerate-after-write byte fidelity.** Under `authority_direction == "tafe_canonical"`, after any
   authoritative bridge write, `verify_against_index` reports `missing_in_generated == []` and
   `extra_divergent_in_generated == []` (terminal-archived residue in `extra_archived_in_generated` is
   tolerated). A divergent regen fails the write closed.
3. **Single canonical direction surface.** The authority direction is readable from exactly one state
   surface (`harness-state/bridge-authority-direction.json`) and defaults to `index_canonical` (safe
   default; absence of the file == `index_canonical`).
4. **Reversibility backstop.** A timestamped immutable frozen copy of `bridge/INDEX.md` is created at
   cutover, and a documented + coded revert (`scripts/bridge_authority_cutover.py --revert`) restores
   `index_canonical` and, if needed, the frozen INDEX content.
5. **Read-surface preservation.** Readers/dispatchers re-read live `bridge/INDEX.md`; no reader is
   migrated to query the TAFE shadow directly (byte-fidelity makes that unnecessary and keeps the blast
   radius at the writers).
6. **Cross-store write order.** Under `tafe_canonical`, the single-transaction DB commit
   (`insert_bridge_thread_atomic`) MUST complete before the generated `bridge/INDEX.md` atomic publish
   (`os.replace`), and the published bytes MUST equal the prospective INDEX that was byte/semantic-verified
   before the commit (AST/ordering test asserts the `tafe_canonical` branch calls
   `insert_bridge_thread_atomic` before `_atomic_write`, and verify before commit).
7. **Single DB commit per authoritative write.** The `tafe_canonical` write path MUST persist the affected
   `flow_instance` row and all its `flow_artifacts` rows in exactly one DB transaction; the per-row
   self-committing `insert_flow_instance`/`insert_flow_artifact` MUST NOT be used on this path (AST
   assertion).
8. **Fail-closed pre-commit divergence.** When the prospective verify is not `semantic_equal`, the write
   MUST raise and MUST NOT issue `BEGIN IMMEDIATE` or `os.replace`; both `groundtruth.db` and
   `bridge/INDEX.md` MUST be byte-identical to their pre-write state (failure-injection test).
9. **Recoverable TAFE-ahead is the only post-commit failure mode.** A failure after commit and before/at
   publish MUST leave TAFE-ahead (never INDEX-ahead, never torn INDEX, never half-thread);
   `verify_against_index(live_index, committed_shadow)` MUST report the split as
   `extra_divergent`/version-mismatch repairable by republish-from-TAFE, never as `missing_in_generated`
   (failure-injection test).
10. **Publish-reconcile is lossless and idempotent.** Given a TAFE-ahead split, `gt flow publish-reconcile`
    / the write-start guard MUST regenerate INDEX from the durable shadow and republish so
    `verify_against_index` becomes `semantic_equal`, WITHOUT deleting or rolling back any committed
    `flow_instances`/`flow_artifacts` row; a second run MUST be a no-op (idempotence test).
11. **INDEX-ahead quarantine.** Publish-reconcile encountering `missing_in_generated` (INDEX content not in
    the authoritative shadow) MUST NOT ingest it into authority and MUST surface it as a repair-required
    defect (test).

## Writer migration inventory (Phase-3 execution scope)

- `scripts/bridge_index_writer.py::atomic_index_update` — the chokepoint; add the authority-direction
  branch (default `index_canonical` = current behavior; `tafe_canonical` = the prepare → single-transaction
  commit → atomic publish path above, including the write-start reconcile guard and post-publish self-check).
  All callers below inherit it.
- `groundtruth-kb/src/groundtruth_kb/db.py` — add `insert_bridge_thread_atomic` + the no-commit cores
  `_insert_flow_instance_row` / `_insert_flow_artifact_row`; the public `insert_flow_instance` /
  `insert_flow_artifact` keep exact single-commit behavior (additive, zero change for current callers).
- `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py` — the publish-reconcile guard (detect
  TAFE-ahead vs INDEX-ahead via `verify_against_index`; repair TAFE-ahead; quarantine INDEX-ahead); reused
  by the chokepoint write-start guard and the CLI.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — `gt flow publish-reconcile` command surfacing the guard.
- `scripts/gtkb_bridge_writer.py::insert_index_status`, `::remove_document` — produce the TAFE-side
  mutation under `tafe_canonical`; `write_bridge_file` (versioned file write) is unaffected.
- `groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py::add_document`, `::set_status` — same.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py` — `add_document_cmd` / `set_status_cmd` /
  `remove_document_cmd` route through the chokepoint.
- `.claude/skills/bridge-propose/helpers/write_bridge.py`, `.../bridge/helpers/revise_bridge.py`,
  `.../bridge/helpers/impl_report_bridge.py` — confirm their `_update_bridge_index` routes through the
  chokepoint; if any bypasses it, route it through.
- `groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py` — used read-only by the writers under
  `tafe_canonical` to regenerate; no new authority logic in the generator (purity preserved).
- New: `harness-state/bridge-authority-direction.json` (the switch) + a small reader; and
  `scripts/bridge_authority_cutover.py` (freeze backstop + flip + `--revert` + `--reconcile`).

## Reversibility backstop (carried forward from the WITHDRAWN governed-cutover thread)

At cutover, `scripts/bridge_authority_cutover.py` (1) writes a timestamped immutable frozen copy of the
live `bridge/INDEX.md` (e.g. `bridge/.authority-cutover/INDEX.frozen-<UTC-stamp>.md`, read-only), then
(2) flips `harness-state/bridge-authority-direction.json` to `tafe_canonical`. `--reconcile` runs the
publish-reconcile guard on demand. `--revert` flips the direction back to `index_canonical` and, if the
post-flip INDEX is suspect, restores the frozen copy. Because writers under `index_canonical` are
byte-identical to today's, revert returns the system to exactly the pre-cutover behavior. The frozen copy is
the disaster-recovery floor; the append-only TAFE shadow is the normal-case recovery source.

## Swarm-quiesce + final pre-cutover re-ingest runbook

1. Quiesce: confirm the bridge dispatcher is OFF (`harness-state/bridge-substrate.json` → `none`,
   already set) and no concurrent Prime/LO sessions are writing the bridge (sole-agent window).
2. Final re-ingest: `gt flow ingest-bridge-index --apply` so the TAFE shadow is current with the live
   INDEX, then `gt flow cutover-evidence --json` → `ok=True` and `gt flow regen-verify --json` →
   `ok=True` (`missing=[]`, `extra_divergent=[]`).
3. Freeze + flip: `scripts/bridge_authority_cutover.py` (freeze backstop, then set `tafe_canonical`).
4. Post-flip smoke: perform one bridge write through each writer path; assert INDEX stays
   byte-faithful (`regen-verify` GREEN), the post-publish self-check passes, `gt flow publish-reconcile`
   is a no-op, and readers/dispatchers see the change.
5. On any anomaly: `scripts/bridge_authority_cutover.py --reconcile` (heal a TAFE-ahead split) or
   `--revert` (return to `index_canonical`).

## Phased rollout

Dual-authority shadow-verify (Phases 0-2, VERIFIED) → **flip** (this Phase 3, gate-2) →
INDEX-generated steady state. Not a single blind flip: the shadow has been proven byte-faithful before
the switch, the cross-store write is fail-closed + self-healing, and the switch is reversible.

## Specification Links

- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the owner-approved cutover decision; this proposal
  executes its authority-flip + byte-faithful-generated-view + phased-reversible-rollout contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the governance invariant amended by this proposal (v1 → v2,
  authority-source clause only; repair authority + read-discipline preserved).
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the terminal-archived classification the
  regen-verify byte-fidelity criterion reuses (`extra_archived` tolerated; `extra_divergent` gates).
- `ADR-TAFE-SLICE-C-INGESTION-001` — the `fa-bridge-<slug>-<NNN>` / `status_token` / `artifact_ref`
  derivation the generator reconstructs and the `tafe_canonical` write path records.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test plan below derives tests from
  each linked spec; execution evidence will accompany the Phase-3 impl report.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio).
- `GOV-ARTIFACT-APPROVAL-001` — the GOV amendment + new DCL each require a formal-artifact-approval
  packet at gate-2 (presented in native review format with full content before insertion).
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `GOV-STANDING-BACKLOG-001` — WI-4510 is the governed work
  item under the TAFE umbrella.

## Prior Deliberations

- `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614` — owner approved the cutover ADR
  (decision: TAFE canonical; INDEX a byte-faithful generated view; 4-phase reversible rollout; flip
  gated by the WI-4510 closing AUQ).
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — owner gate-1 (proceed to file the cutover proposal).
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — owner reconciliation ("new canonical; withdraw
  old"); the WITHDRAWN `gtkb-wi4510-governed-cutover` thread's unique reversibility backstop is folded
  into this Phase-3 thread (above).
- `DELIB-20263195` — cutover-sequence authorization (the cutover PAUTH's owner decision).
- Phases 0-2 VERIFIED at `bridge/gtkb-wi4510-tafe-authoritative-cutover-008.md` (byte-faithful generator
  + shadow-verify; the prerequisite this Phase-3 flip builds on).
- WI-4574 VERIFIED (ingestion phantom-guard + `sp1` reconcile) — eliminated the orphan that would
  otherwise make the post-flip regen-verify gate on a phantom.
- `bridge/gtkb-wi4510-phase-3-authority-flip-002.md` — Codex NO-GO whose F1 this revision resolves.
- Deliberation search for `WI-4510 TAFE authority flip` / `cross-store consistency bridge INDEX` also
  surfaced related TAFE pilot and reconciliation review records: `DELIB-20263408`, `DELIB-20263285`,
  `DELIB-20263164`, `DELIB-20263283`, `DELIB-20263370`.

## Owner Decisions / Input

This proposal depends on owner approval at gate-2. The decisions to be captured via `AskUserQuestion`
(the only valid owner-decision channel) before execution:

1. **Gate-2 final-execute AUQ** — confirm the irreversible flip (TAFE becomes the bridge authority),
   having reviewed the rollback runbook + reversibility backstop + the cross-store fail-closed contract.
2. **GOV-FILE-BRIDGE-AUTHORITY-001 amendment approval** — formal-artifact-approval packet for the v2
   statement above.
3. **DCL-INDEX-GENERATED-VIEW-001 creation approval** — formal-artifact-approval packet (now including
   assertions #6–#11, the cross-store contract).
4. **PAUTH authorization for `cutover` + `formal_spec_promotion`** — expand the PHASE-6-7-CUTOVER PAUTH
   (or a fresh owner decision) to permit the two mutation classes the flip requires.

Already on record (carried forward): `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`
(ADR approval), `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` (gate-1), `DELIB-20263195` (cutover-seq).
No new owner decision is required for Codex to review this design; the four above are the gate-2 package.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (owner-approved) is the
governing requirement that decided the authority flip, the byte-faithful generated view, and the
phased reversible rollout. The `GOV-FILE-BRIDGE-AUTHORITY-001` amendment and the new
`DCL-INDEX-GENERATED-VIEW-001` are *derived formalization* of that decision (conformance + machine-
checkable enforcement), created during Phase-3 execution under the `formal_spec_promotion` mutation
class with their own formal-artifact-approval packets at gate-2 — not new requirements that change the
decision. The cross-store fail-closed contract added by this revision is a *design-level* elaboration of
the same ADR's "byte-faithful generated view, regenerated after every authoritative write" clause; it
introduces no new requirement.

## Spec-to-Test Plan

| Linked spec | Derived test / verification |
|---|---|
| `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (authority flip) | `test_tafe_authoritative_write_path.py`: under `tafe_canonical`, a status write records the TAFE `flow_artifacts` row and INDEX is regenerated byte-faithful; under `index_canonical`, behavior is byte-identical to today. |
| `DCL-INDEX-GENERATED-VIEW-001` #1 generator purity | existing `test_tafe_index_generator.py::test_generator_module_performs_no_write_or_subprocess` (AST). |
| `DCL-INDEX-GENERATED-VIEW-001` #2 regen-after-write fidelity | `test_tafe_authoritative_write_path.py`: post-write `verify_against_index` → `missing=[]`, `extra_divergent=[]`; divergence fails the write closed. |
| `DCL-INDEX-GENERATED-VIEW-001` #3 single direction surface + safe default | `test_bridge_authority_direction.py`: absent file == `index_canonical`; reader returns the one canonical value. |
| `DCL-INDEX-GENERATED-VIEW-001` #4 reversibility backstop | `test_bridge_authority_direction.py`: `bridge_authority_cutover.py` freezes an immutable INDEX copy and `--revert` restores `index_canonical`. |
| `DCL-INDEX-GENERATED-VIEW-001` #6 cross-store write order | `test_tafe_authoritative_write_path.py::test_write_order_commit_before_publish` — AST/ordering: `tafe_canonical` branch verifies before commit and commits (`insert_bridge_thread_atomic`) before `_atomic_write`; published bytes equal the pre-commit-verified text. |
| `DCL-INDEX-GENERATED-VIEW-001` #7 single DB commit | `test_tafe_authoritative_write_path.py::test_thread_is_single_transaction` — AST assertion the path uses `insert_bridge_thread_atomic`, not per-row self-committing inserters. |
| `DCL-INDEX-GENERATED-VIEW-001` #8 fail-closed pre-commit divergence (Codex scenario 1) | `test_tafe_authoritative_write_path.py::test_divergence_before_publish_writes_nothing` — force prospective verify to diverge; assert NO row inserted (instance/artifact counts unchanged), `bridge/INDEX.md` byte-identical, `bridge-authority-direction.json` unchanged, writer raised. |
| `DCL-INDEX-GENERATED-VIEW-001` #9 TAFE-ahead is the only post-commit failure (Codex scenario 2) | `test_tafe_authoritative_write_path.py::test_publish_failure_after_commit_is_recoverable` — monkeypatch `_atomic_write` to raise after commit; assert full thread committed atomically (no half-thread), INDEX still prior + not torn + temp cleaned; `verify_against_index` reports TAFE-ahead (`extra_divergent`/version-mismatch, not `missing_in_generated`). |
| `DCL-INDEX-GENERATED-VIEW-001` #10 publish-reconcile lossless + idempotent | `test_tafe_authoritative_write_path.py::test_publish_reconcile_heals_losslessly` — from the TAFE-ahead state, `publish-reconcile` makes `verify_against_index` `semantic_equal` with zero shadow-row deletions; a second run is a no-op. |
| `DCL-INDEX-GENERATED-VIEW-001` #11 INDEX-ahead quarantine | `test_tafe_authoritative_write_path.py::test_index_ahead_is_quarantined` — plant a thread/version in INDEX absent from the shadow; assert `publish-reconcile` reports `missing_in_generated`, refuses to ingest it, surfaces a repair-required defect. |
| Codex scenario 3 (revert/repair after mid-publish exception) | `test_tafe_authoritative_write_path.py::test_revert_and_next_writer_repair` — from the TAFE-ahead state: (a) the next writer's pre-write guard republishes before its own write; (b) `bridge_authority_cutover.py --reconcile` heals losslessly; (c) `--revert` flips to `index_canonical` and (if INDEX suspect) restores the frozen immutable copy. |
| Atomicity regression (independent-commit hazard removed) | `test_tafe_authoritative_write_path.py::test_partial_thread_rolls_back` — inject a failure between the instance insert and an artifact insert inside `insert_bridge_thread_atomic`; assert `ROLLBACK` leaves zero rows from the attempted thread. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` v2 read-surface preservation + `index_canonical` byte-identity | `test_tafe_authoritative_write_path.py::test_index_canonical_byte_identical` — with the direction absent and `index_canonical`, each writer path is byte-identical to pre-flip; existing trigger/notify reader tests stay green. |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2 | `extra_archived` tolerated / `extra_divergent` gates in the post-write verify path. |

## Risk / Rollback

Highest-risk change in the cutover (it changes the authority invariant). Mitigations: (a) the flip is a
single config switch at one chokepoint, default-off; (b) INDEX stays byte-faithful so readers are
unaffected; (c) the cross-store write does all expensive work + byte-verify BEFORE the single DB commit, so
the common divergence case fails closed with both stores byte-identical to pre-write; (d) the only
post-commit failure mode is a bounded, self-healing TAFE-ahead window (lossless republish from the
append-only shadow; INDEX-ahead structurally impossible through the chokepoint and quarantined otherwise);
(e) a timestamped immutable frozen INDEX copy is the disaster-recovery floor; (f) `--reconcile` heals a
split and `--revert` returns to the byte-identical `index_canonical` behavior; (g) execution only in a
swarm-quiesced window after a GREEN final re-ingest. One added implementation risk: the no-commit-core
refactor touches the hot `insert_flow_instance`/`insert_flow_artifact` surface — mitigated by keeping the
public methods byte-for-byte behavior-preserving (additive cores) and adding the Extra-A atomicity
regression test. No reader, dispatcher, hook, or schema changes.

## Recommended Commit Type

Recommended commit type: `feat:` — adds the authority-direction switch + the cross-store fail-closed
TAFE-first write path (single-transaction `insert_bridge_thread_atomic` + publish-reconcile guard) + the
cutover/revert/reconcile tooling (new capability), with the GOV amendment and spec-derived tests. The
eventual Phase-3 impl report will restate the type against the final diff stat.
