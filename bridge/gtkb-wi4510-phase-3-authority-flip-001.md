NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session c50a9788; ::init gtkb pb; autonomous WI-4510 cutover driver; explanatory output style

# WI-4510 Phase 3 — TAFE-authoritative bridge state: the irreversible authority flip

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: ["scripts/bridge_index_writer.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "scripts/bridge_authority_cutover.py", "harness-state/bridge-authority-direction.json", "groundtruth-kb/tests/test_bridge_authority_direction.py", "groundtruth-kb/tests/test_tafe_authoritative_write_path.py"]

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
review the **design, the amended-GOV text, the new DCL, the writer-migration plan, the reversibility
backstop, and the swarm-quiesce/final-re-ingest runbook** so the gate-2 package is review-complete.

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
  from the now-authoritative TAFE shadow, still written atomically under the same lock, and immediately
  checked byte-faithful via `verify_against_index` (regen-verify GREEN: `missing=[]`,
  `extra_divergent=[]`). On any divergence the write fails closed (INDEX left unchanged, error raised),
  so a non-byte-faithful INDEX can never be published.

The switch lives at the shared chokepoint so all writers inherit it; any writer found bypassing the
chokepoint is routed through it as part of the migration.

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

Machine-checkable constraints for the generated-view regime:

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

## Writer migration inventory (Phase-3 execution scope)

- `scripts/bridge_index_writer.py::atomic_index_update` — the chokepoint; add the authority-direction
  branch (default `index_canonical` = current behavior; `tafe_canonical` = TAFE-first write + regenerate
  + byte-verify-or-fail-closed). All callers below inherit it.
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
  `scripts/bridge_authority_cutover.py` (freeze backstop + flip + `--revert`).

## Reversibility backstop (carried forward from the WITHDRAWN governed-cutover thread)

At cutover, `scripts/bridge_authority_cutover.py` (1) writes a timestamped immutable frozen copy of the
live `bridge/INDEX.md` (e.g. `bridge/.authority-cutover/INDEX.frozen-<UTC-stamp>.md`, read-only), then
(2) flips `harness-state/bridge-authority-direction.json` to `tafe_canonical`. Revert
(`--revert`): flip the direction back to `index_canonical` and, if the post-flip INDEX is suspect,
restore the frozen copy. Because writers under `index_canonical` are byte-identical to today's, revert
returns the system to exactly the pre-cutover behavior. The frozen copy is the disaster-recovery floor.

## Swarm-quiesce + final pre-cutover re-ingest runbook

1. Quiesce: confirm the bridge dispatcher is OFF (`harness-state/bridge-substrate.json` → `none`,
   already set) and no concurrent Prime/LO sessions are writing the bridge (sole-agent window).
2. Final re-ingest: `gt flow ingest-bridge-index --apply` so the TAFE shadow is current with the live
   INDEX, then `gt flow cutover-evidence --json` → `ok=True` and `gt flow regen-verify --json` →
   `ok=True` (`missing=[]`, `extra_divergent=[]`).
3. Freeze + flip: `scripts/bridge_authority_cutover.py` (freeze backstop, then set `tafe_canonical`).
4. Post-flip smoke: perform one bridge write through each writer path; assert INDEX stays
   byte-faithful (`regen-verify` GREEN) and readers/dispatchers see the change.
5. On any anomaly: `scripts/bridge_authority_cutover.py --revert`.

## Phased rollout

Dual-authority shadow-verify (Phases 0-2, VERIFIED) → **flip** (this Phase 3, gate-2) →
INDEX-generated steady state. Not a single blind flip: the shadow has been proven byte-faithful before
the switch, and the switch is reversible.

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

## Owner Decisions / Input

This proposal depends on owner approval at gate-2. The decisions to be captured via `AskUserQuestion`
(the only valid owner-decision channel) before execution:

1. **Gate-2 final-execute AUQ** — confirm the irreversible flip (TAFE becomes the bridge authority),
   having reviewed the rollback runbook + reversibility backstop.
2. **GOV-FILE-BRIDGE-AUTHORITY-001 amendment approval** — formal-artifact-approval packet for the v2
   statement above.
3. **DCL-INDEX-GENERATED-VIEW-001 creation approval** — formal-artifact-approval packet.
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
decision.

## Spec-to-Test Plan

| Linked spec | Derived test / verification |
|---|---|
| `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (authority flip) | `test_tafe_authoritative_write_path.py`: under `tafe_canonical`, a status write records the TAFE `flow_artifacts` row and INDEX is regenerated byte-faithful; under `index_canonical`, behavior is byte-identical to today. |
| `DCL-INDEX-GENERATED-VIEW-001` #1 generator purity | existing `test_tafe_index_generator.py::test_generator_module_performs_no_write_or_subprocess` (AST). |
| `DCL-INDEX-GENERATED-VIEW-001` #2 regen-after-write fidelity | `test_tafe_authoritative_write_path.py`: post-write `verify_against_index` → `missing=[]`, `extra_divergent=[]`; divergence fails the write closed. |
| `DCL-INDEX-GENERATED-VIEW-001` #3 single direction surface + safe default | `test_bridge_authority_direction.py`: absent file == `index_canonical`; reader returns the one canonical value. |
| `DCL-INDEX-GENERATED-VIEW-001` #4 reversibility backstop | `test_bridge_authority_direction.py`: `bridge_authority_cutover.py` freezes an immutable INDEX copy and `--revert` restores `index_canonical`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` v2 read-surface preservation | regression: readers/dispatchers parse the regenerated INDEX unchanged (existing trigger/notify tests stay green). |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2 | `extra_archived` tolerated / `extra_divergent` gates in the post-write verify path. |

## Risk / Rollback

Highest-risk change in the cutover (it changes the authority invariant). Mitigations: (a) the flip is a
single config switch at one chokepoint, default-off; (b) INDEX stays byte-faithful so readers are
unaffected; (c) writes fail closed on any byte-divergence; (d) a timestamped immutable frozen INDEX
copy is the disaster-recovery floor; (e) `--revert` returns to the byte-identical `index_canonical`
behavior; (f) execution only in a swarm-quiesced window after a GREEN final re-ingest. No reader,
dispatcher, hook, or schema changes.

## Recommended Commit Type

Recommended commit type: `feat:` — adds the authority-direction switch + TAFE-first write path + the
cutover/revert tooling (new capability), with the GOV amendment (`docs:`-adjacent governance change
folded into the feat) and spec-derived tests. The eventual Phase-3 impl report will restate the type
against the final diff stat.
