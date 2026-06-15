NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code autonomous Prime Builder session; WI-4510 Phases 0-2 impl report under GO -006
author_metadata_source: env runtime envelope (WI-4522)

# WI-4510 — Implementation Report: TAFE-authoritative-cutover Phases 0–2 (byte-faithful generator + shadow-verify; NOT the flip)

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
Responds to: bridge/gtkb-wi4510-tafe-authoritative-cutover-006.md (GO)
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_generator.py", "groundtruth-kb/tests/test_tafe_index_generator_cli.py", "groundtruth.db"]

## Summary

Implemented WI-4510 **Phases 0–2** per GO `bridge/gtkb-wi4510-tafe-authoritative-cutover-006.md`
(impl-start packet `sha256:619422c0797c828ed1ef338819b3a4d90b2c92cc03464acc71914e94f5ea87fb`). This is
the cutover **prerequisite**: a byte-faithful `flow_artifacts`-based INDEX generator and a shadow-verify
gate (`gt flow regen-verify`), proven against the live INDEX. **The irreversible Phase 3 authority flip
is NOT in this report** — it remains gated by the WI-4510 closing owner AUQ (gate-2) and a separate
REVISED carrying the `GOV-FILE-BRIDGE-AUTHORITY-001` amendment.

GO `-006` Implementation Constraints — all satisfied: (1) Phase 0 ran before any Phase-2 equality claim;
(2) the Phase-0 DB mutation evidence is recorded below; (3) the generator/CLI tests + ruff (check AND
format) were executed; (4) no Phase 3 / authority flip was performed.

## Implementation Provenance (honest attribution)

The Phase 1–2 source/test surface was built across the swarm: the original `flow_artifacts` generator
+ `regen-verify` CLI by a concurrent Prime session, then corrected this session
(`c50a9788-517e-4adc-a32d-a14594942b91`) with the **Refined Option B** partition fix (the adversarially-
designed fix for the live regen-verify divergence — `verify_against_index` partitions extra threads into
ungated `extra_archived_in_generated` vs gating `extra_divergent_in_generated`, via the shared
`tafe_index_completeness._candidate_is_archived` oracle, generator kept pure). Phase 0 (re-ingest) was
run this session under the GO + impl-start packet. All changes are uncommitted in the working tree;
only the five GO-authorized `target_paths` are in scope.

## Changes Implemented

- **Phase 0 — shadow-currency recovery (`dual_write` of `groundtruth.db`).** `gt flow ingest-bridge-index
  --apply` brought the shadow current with the live INDEX (append-only `flow_instances` /
  `flow_artifacts`); this session's run wrote **1 instance + 7 artifacts** (the now-VERIFIED WI-4574
  thread that was missing from the shadow). Idempotent under fingerprint-gating.
- **Phase 1 — byte-faithful generator (`groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py`).**
  `render_index_from_flow_artifacts` (pure: reconstructs `Document:` blocks + ordered version lines from
  `flow_artifacts`), `verify_against_index` (round-trip comparison with the semantic-vs-byte distinction
  + the Refined-Option-B extra-thread partition, classifier dependency-injected to preserve purity), and
  the `RegenVerifyResult` dataclass (with `extra_archived_in_generated` / `extra_divergent_in_generated`).
- **Phase 2 — shadow-verify CLI (`groundtruth-kb/src/groundtruth_kb/cli.py`, `flow regen-verify`).**
  Read-only of the canonical INDEX (refuses to write it, per GOV-FILE-BRIDGE-AUTHORITY-001); wires the
  `_candidate_is_archived` oracle so legitimate terminal-archived residue is tolerated while phantoms /
  non-terminal shadow rows gate.
- **Tests:** `test_tafe_index_generator.py` (round-trip byte-fidelity, multi-version, token coverage,
  terminal-archived trimming, ordering, reformat-vs-divergent, the 5 partition cases, read-only AST
  guard) + `test_tafe_index_generator_cli.py` (equal / divergent / refuses-canonical-INDEX / writes-
  evidence + the 3 partition CLI cases).

## Specification Links (carried forward from -005)

- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the owner-approved cutover decision; the generator
  contract + round-trip fidelity criterion + phased reversible rollout implemented here (Phases 0–2).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — honored: the generator is pure (no INDEX write), `regen-verify` is
  read-only of the canonical INDEX and refuses to write it; `bridge/INDEX.md` remains authoritative
  through Phases 0–2 (the authority flip is Phase 3, out of scope).
- `ADR-TAFE-SLICE-C-INGESTION-001` — the `fa-bridge-<slug>-<NNN>` / `status_token` / `artifact_ref`
  derivation the generator reconstructs.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the terminal-archived classification the
  Refined-Option-B partition reuses (shared `_candidate_is_archived` oracle); fidelity defined against
  the live trimmed INDEX.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
  — cross-cutting; the spec-to-test mapping + executed evidence below comply.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio).
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `GOV-STANDING-BACKLOG-001`.

## Spec-to-Test Mapping

| Spec clause | Test / evidence |
|---|---|
| `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` Phase-1 round-trip | `test_tafe_index_generator.py::test_roundtrip_is_byte_identical_in_index_order` + multi-version / token / ordering tests |
| Refined-Option-B partition (archived vs divergent) | `test_verify_terminal_archived_extra_is_non_gating`, `test_verify_phantom_extra_gates`, `test_verify_extra_partition_default_gates_all`, `test_verify_version_mismatch_still_gates_with_archived_extra_present`, `test_verify_missing_thread_still_gates_with_partition` + 3 CLI partition tests |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (terminal-archived tolerated) | read-only `gt flow regen-verify` → `extra_archived` = [gtkb-wi4572, sp1], `extra_divergent` = [] |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no INDEX write) | `test_generator_module_performs_no_write_or_subprocess` (AST) + `test_cli_regen_verify_refuses_canonical_index` |
| Phase-0 acceptance | `gt flow cutover-evidence --json` → `ok=True` after re-ingest |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the executed commands + results below |

## Verification Evidence (executed this session)

```text
# Phase 0 (dual_write of groundtruth.db; GO Implementation Constraint 1+2)
gt flow ingest-bridge-index --apply --json   -> applied=True, instances_written=1, artifacts_written=7
gt flow cutover-evidence --json              -> ok=True, parity.ok=True, contention_zero=True,
                                                fidelity.ok=True, lost_blocks=0, extra_blocks=0
# Phase 2 acceptance (READ-ONLY; no further --apply)
gt flow regen-verify --json                  -> ok=True, status=reformat_only, missing_in_generated=[],
                                                extra_divergent_in_generated=[],
                                                extra_archived_in_generated=[gtkb-wi4572-..., sp1-...]
# Phase 1-2 source/test gates (GO Implementation Constraint 3)
python -m pytest groundtruth-kb/tests/test_tafe_index_generator.py groundtruth-kb/tests/test_tafe_index_generator_cli.py -q
                                             -> 23 passed
python -m ruff check  (4 target files)       -> All checks passed!
python -m ruff format --check (4 files)      -> 4 files already formatted
```

`regen-verify` is GREEN (`ok=True`): the shadow now faithfully reconstructs the live INDEX — every live
thread present (`missing=[]`), no phantom/non-terminal divergence (`extra_divergent=[]`), with the
terminal-archived residue (`gtkb-wi4572`, `sp1`) correctly tolerated. `status=reformat_only` is the
documented one-time reformat (line terminators / document-block ordering) surfaced for the gate-2
decision, never applied silently.

## Owner Decisions / Input

- `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614` — owner approved the cutover ADR.
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — owner gate-1 (file the proposal).
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — owner reconciliation (canonical thread).
- `DELIB-20263195` — cutover-sequence authorization (the cutover PAUTH's owner decision).

The irreversible Phase 3 flip is NOT performed here; it requires the deferred WI-4510 **closing owner AUQ
(gate-2)** plus the `GOV-FILE-BRIDGE-AUTHORITY-001` amendment (its own formal-artifact-approval packet),
carried in a separate REVISED. No new owner decision arose during Phases 0–2.

## Risk / Rollback

Phases 0–2 change no authority and are reversible/additive: Phase 0 is idempotent append-only
`dual_write` shadow maintenance; Phases 1–2 are a new module + a read-only-of-INDEX CLI subcommand +
tests. Reverting the four source/test files to HEAD restores prior behavior; the append-only shadow is
never deleted. No INDEX mutation, no schema change, no authority flip.

## Recommended Commit Type

Recommended commit type: `feat:` — Phases 1–2 add a new authoritative `flow_artifacts`-based INDEX
generator and a shadow-verify CLI surface (new capability), with their spec-derived tests. (Phase 0 is
an operational `dual_write` DB refresh, not a source commit.)

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_tafe_index_generator.py`
- `groundtruth-kb/tests/test_tafe_index_generator_cli.py`
- `groundtruth.db` (append-only Phase-0 shadow refresh)
