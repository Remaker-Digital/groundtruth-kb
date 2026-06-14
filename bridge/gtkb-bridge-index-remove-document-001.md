NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c2f8c28a-bc49-4158-a509-1ae540eec86d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# WI-4566 — gt bridge index remove-document: phantom-only INDEX entry removal (close the TAFE cutover extra_block gap)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-B-RESIDUAL-CLEANUP-WI-4566
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4566
target_paths: ["scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "groundtruth-kb/tests/test_cli_bridge_index.py"]

## Summary

TAFE Phase-B oracle reconciliation is VERIFIED (`lost_blocks` 74 → 0;
`bridge/gtkb-tafe-phase-b-acknowledged-archived-004.md`). Live `gt flow cutover-evidence`
is now clean on every substantive axis — `lost=0, parity=True, contention_zero=True,
fidelity=True` — EXCEPT one cosmetic phantom: the INDEX `Document:` entry
`sp1-dispatch-reliability-prime-handoff` has **no backing `bridge/sp1-...-*.md` file**
(the real thread `gtkb-sp1-dispatch-reliability-prime-handoff` is correctly archived).
`CutoverEvidenceReport.ok` gates on `extra_blocks == []`, and the serialized bridge-INDEX
writer (`gt bridge index`) exposes only `add-document` + `set-status` — **no remove/prune
verb** — so the phantom cannot be reconciled with sanctioned tooling (raw `bridge/INDEX.md`
edits are forbidden per GOV-FILE-BRIDGE-AUTHORITY-001). This is the F1 tooling gap surfaced
by the Phase-B impl report (`bridge/gtkb-tafe-phase-b-acknowledged-archived-003.md`).

This proposal adds a **phantom-only** `gt bridge index remove-document <slug>` primitive and
uses it to remove the phantom, reaching a fully-clean cutover-evidence gate — the WI-4510
precondition. WI-4510 (the governed cutover itself) stays HELD and OUT OF SCOPE here; it
requires its own separate fresh owner AUQ.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical; INDEX mutations only via
  the serialized writer (never raw edits). Removal is restricted to **phantom** entries
  (no backing file) to preserve the never-delete-real-threads audit invariant.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the completeness contract whose
  `CutoverEvidenceReport.ok` (`extra_blocks == []`) this proposal unblocks.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the cutover-evidence derivation this clears.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — phantom-INDEX-entry reconciliation is an
  artifact-lifecycle disposition.
- `GOV-STANDING-BACKLOG-001` — WI-4566.

## Prior Deliberations

- `DELIB-2003` / `DELIB-1430` — `gtkb-bridge-index-phantom-verified-references-2026-04-27`:
  the prior phantom-INDEX-reference reconciliation precedent (same problem class).
- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614`,
  `DELIB-WI4546-DCL-COMPLETENESS-V2-APPROVE-20260614` — the Phase-B strategy + contract.
- Phase-B oracle VERIFIED (`gtkb-tafe-phase-b-acknowledged-archived-004`); F1 tooling-gap
  finding (`gtkb-tafe-phase-b-acknowledged-archived-003`).
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — WI-4510 HOLD; this proposal
  completes the cutover-evidence precondition without authorizing the cutover.

## Owner Decisions / Input

- AskUserQuestion (session c2f8c28a): the owner chose **"Build remove-document verb"** to
  close the last cutover-evidence gap. WI-4510 cutover itself remains a separate fresh-AUQ
  decision and is NOT authorized by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 governs INDEX-mutation
tooling; this proposal adds a sanctioned phantom-only removal primitive consistent with it.
No new formal artifact is required.

## Proposed Change

**Step 1 — writer (`scripts/gtkb_bridge_writer.py`).** Add `remove_document(slug, *,
bridge_dir=...)`. It removes the `Document: <slug>` block (the `Document:` line plus its
contiguous status/version lines) from `bridge/INDEX.md` atomically, reusing the existing
serialized-writer lock + atomic-index-update path (the same mechanism as `add_document` /
`insert_index_status`). **Guardrail:** refuse (raise) when ANY `bridge/<slug>-*.md` file
exists on disk — only phantom entries (no backing file) are removable, preserving the
never-delete-a-real-thread audit invariant. Absent-slug removal is a no-op / explicit
not-found per existing writer conventions.

**Step 2 — CLI (`groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py`).** Add a
`remove-document <slug>` command wiring to the writer, emitting a JSON result and honoring
the same canonical-write-refusal posture as the sibling index commands.

**Step 3 — tests.** Writer tests (`platform_tests/scripts/test_gtkb_bridge_writer.py`):
removes a phantom block; raises when on-disk files exist (guardrail); atomic; absent-slug
handling. CLI tests (`groundtruth-kb/tests/test_cli_bridge_index.py`): happy path; refusal
on a backed slug; JSON shape.

**Step 4 — apply (post-VERIFY, operational).**
`gt bridge index remove-document sp1-dispatch-reliability-prime-handoff`, then
`gt flow cutover-evidence --json` → confirm `extra_blocks == []` and `ok == True`.

## Spec-Derived Verification Plan

- `platform_tests/scripts/test_gtkb_bridge_writer.py`: `remove_document` removes a phantom
  `Document:` block; raises on a backed slug (guardrail); uses the serialized lock; handles
  an absent slug.
- `groundtruth-kb/tests/test_cli_bridge_index.py`: `remove-document` removes a phantom;
  refuses a backed slug; correct JSON output.
- Integration: after applying to `sp1-dispatch-reliability-prime-handoff`,
  `gt flow cutover-evidence --json` reports `extra_blocks == []` and `ok == True`
  (`lost==0`, `parity`, `contention_zero`, `fidelity` already true).
- `ruff check` + `ruff format --check` on the changed files.

## Risk / Rollback

- **Risk:** removing a real thread's INDEX entry. **Mitigation:** the phantom-only guardrail
  (refuse when `bridge/<slug>-*.md` exists) makes removing a backed thread impossible; only
  no-backing-file phantoms are removable.
- **Risk:** INDEX corruption under concurrent writes. **Mitigation:** reuse the existing
  serialized-writer lock + atomic-index-update path (identical to add-document/set-status).
- **Rollback:** revert the writer + CLI additions; the removed phantom line is recoverable
  from git history if ever needed (it is a no-backing-file phantom, so removal is
  audit-preserving). No schema change; no canonical-content loss.

## Recommended Commit Type

`feat:` — adds the phantom-only `remove-document` INDEX-mutation primitive + CLI command.
