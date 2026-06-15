NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code autonomous Prime Builder session; ::init gtkb pb; WI-4510 TAFE cutover driver; explanatory output style
author_metadata_source: env runtime envelope (WI-4522)

# WI-4510 — Governed TAFE-authoritative bridge cutover: build the byte-faithful INDEX generator + shadow-verify, then flip authority (gate-2)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_generator.py", "groundtruth-kb/tests/test_tafe_index_generator_cli.py"]

## Summary

WI-4510 is the governed cutover that makes the TAFE typed-artifact store the **authoritative** source
of bridge workflow state and demotes `bridge/INDEX.md` to a **byte-faithful generated view**. This
reverses the bridge data-flow direction established by `GOV-FILE-BRIDGE-AUTHORITY-001` (today INDEX.md
is canonical and the TAFE shadow is ingested FROM it). It is a fundamental-architecture migration, not
a flag flip, and is governed by the owner-approved `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (v1,
specified; formal-artifact-approval packet
`.groundtruth/formal-artifact-approvals/2026-06-15-ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001.json`).

The reconciliation precursor (WI-4546 Phase A/B) is COMPLETE and live cutover-evidence is GREEN
(session re-verified read-only, `bridge/INDEX.md` not mutated): `gt flow cutover-evidence --json` →
`ok=True`, `parity.ok=True` (345/345 threads; `derived_artifacts=1956 == index_version_lines=1956`),
`lost_blocks=0`, `extra_blocks=0`, `contention_zero=true`, `fidelity.ok=true` (345 threads checked).
The shadow is a verified-faithful mirror; the data needed to regenerate INDEX from TAFE is present in
`flow_artifacts` (parity-confirmed 1956==1956).

**The de-risking architecture (per the ADR).** Keeping `bridge/INDEX.md` a faithful generated view
collapses the migration surface from "every reader + dispatcher" to "the writer paths + one new
generator." `bridge.detector.parse_index` operates on a *string*; `bridge.notify.compute_actionable_pending`
operates on the parse result (reads `bridge_kind` from disk files); the cross-harness trigger,
single-harness dispatcher, AXIS-2 hook, session-start governance hook, and preflights all read the
INDEX *file*. If writers write TAFE-first then regenerate a byte-faithful INDEX, **no reader changes**.

**Prerequisite gap (the central finding).** No byte-faithful TAFE→INDEX generator exists. The only
generator, `tafe_index_preview.render_tafe_bridge_index_preview` (WI-4507), is explicitly
NON-authoritative and renders from `stage_instances`, which are *not written for bridge threads* in
Slice C (Slice C wrote `flow_instances` + `flow_artifacts` only). A new generator that reconstructs the
version-line history from `flow_artifacts` is required and is the first deliverable.

**Scope of THIS proposal's `target_paths`.** This proposal authorizes the do-now, PAUTH-permitted
Phases 1–2 (the `flow_artifacts`-based generator, its round-trip golden test, and the dual-authority
shadow-verify CLI + test). The irreversible flip (Phase 3 — writer migration, the authority switch, the
`GOV-FILE-BRIDGE-AUTHORITY-001` amendment, write-guard hardening) is `cutover`/`formal_spec_promotion`,
both PAUTH-FORBIDDEN, and is implemented only after the WI-4510 closing owner AUQ (gate-2) via a REVISED
proposal version that expands `target_paths` and carries the gate-2 + formal-artifact-approval evidence.
Phase 1–2 produce the round-trip + shadow-verify evidence that informs gate-2.

## Applicability Preflight

- packet_hash: `sha256:86b14fbbac34e71c8026cdfb5c4b7807ed9a68ee45d7ce19983534e80a3304ba`
- bridge_document_name: `gtkb-wi4510-tafe-authoritative-cutover`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4510-tafe-authoritative-cutover-001.md`
- operative_file: `bridge/gtkb-wi4510-tafe-authoritative-cutover-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |


## Clause Applicability Preflight

- Bridge id: `gtkb-wi4510-tafe-authoritative-cutover`
- Operative file: `bridge\gtkb-wi4510-tafe-authoritative-cutover-002.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps (gate-failing): 1
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | — | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | **no** | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

### Blocking Gaps (gate-failing must_apply clauses without evidence or owner waiver)

- **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`** (blocking, blocking)
  - Gap: Evidence missing: Implementation report includes a `Specification-Derived Verification` (or equivalent spec-to-test) section AND command evidence (pytest/python -m pytest/etc.) AND observed results.
  - Evidence required: Implementation report includes a `Specification-Derived Verification` (or equivalent spec-to-test) section AND command evidence (pytest/python -m pytest/etc.) AND observed results.
  - Detector note: evidence pattern `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)` did not match

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Specification Links

- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the owner-approved decision this proposal implements:
  TAFE becomes canonical, `bridge/INDEX.md` becomes a byte-faithful generated view, 4-phase reversible
  rollout, flip gated by the WI-4510 closing AUQ.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the P0 invariant being reversed ("the live contents of
  bridge/INDEX.md are the sole authoritative source for bridge queue state"). Phases 1–2 do NOT change
  it; the Phase-3 amendment (own formal-artifact-approval packet) repoints authority to the TAFE store
  while preserving the derived-surface prohibition, the read-live-before-deciding rule, and the LO
  permanent bridge-repair authority. Until then, INDEX.md remains canonical and Phases 1–2 are
  read/derive-only against it.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the canonical D1–D4 ingestion derivation; the generator must
  reconstruct exactly the version-line set Slice C wrote into `flow_artifacts`
  (`fa-bridge-<slug>-<NNN>`, `metadata.status_token`, `artifact_ref`).
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the completeness contract: terminal-archived
  threads are legitimately absent from INDEX. The generator must reproduce INDEX *as it is* (i.e. it
  must NOT re-emit terminal-archived/trimmed threads that the protocol has trimmed); round-trip fidelity
  is defined against the live, trimmed INDEX, consistent with this completeness semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting: every
  implementation proposal must cite all relevant governing specifications; this Specification Links
  section complies.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: VERIFIED requires
  spec-derived tests with executed evidence; the Spec-Derived Verification Plan below derives its tests
  from the generator's byte-faithfulness contract and the ADR's Phase-1/2 exit criteria.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio) — the cutover is an artifact-lifecycle
  transition of the bridge-state authority; the ADR + DELIB capture, the phased lifecycle, and the
  GOV amendment at flip are the governed lifecycle actions.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — WI-4510 is the umbrella program's terminal step; the
  "structured, queryable canonical bridge state" objective is what authority-flip delivers.
- `GOV-STANDING-BACKLOG-001` — WI-4510 is the governed standing-backlog work item driving this cutover.

## Prior Deliberations

- `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614` — owner AUQ (this session) approving
  creation of `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` ("Approve & insert ADR").
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — owner gate-1: proceed to FILE this cutover proposal.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — the prior owner HOLD on WI-4510 until the
  WI-4546 reconciliation landed (now satisfied; evidence GREEN).
- `DELIB-20263195` — TAFE cutover-sequence authorization (the governance gate this work feeds; the
  cutover PAUTH's `owner_decision_deliberation_id`).
- `DELIB-WI4546-{RECONCILE-STRATEGY-REFINE-ORACLE,DCL-COMPLETENESS-APPROVE,DCL-COMPLETENESS-V2-APPROVE,PHASE-B-DISPOSITION-STRATEGY}-20260614`
  — the reconciliation decisions that made cutover-evidence GREEN.
- WI-4508 Slice C (`gtkb-tafe-slice-c-ingestion-consolidated`, VERIFIED) — `flow_instances` +
  `flow_artifacts` ingestion the generator reads. WI-4509 (`gtkb-wi4509-cutover-evidence`, VERIFIED) —
  the evidence tool whose parity/fidelity this cutover relies on. WI-4507
  (`tafe_index_preview`, non-authoritative) — the generator explicitly NOT reused.

## Owner Decisions / Input

This proposal depends on owner approval, captured via AskUserQuestion this session
(session c50a9788):

1. **Gate-1 (file the proposal)** — recorded as `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614`:
   owner authorized proceeding to FILE this cutover proposal after reconciliation completed.
2. **ADR formal-artifact approval** — "Approve creation of ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001?"
   → owner selected **"Approve & insert ADR"** (recorded as
   `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`); the ADR is inserted (v1, specified).

No further owner decision is required to REVIEW this proposal or to implement Phases 1–2 after GO
(covered by the cutover PAUTH). The following owner decisions are explicitly DEFERRED and gate Phase 3:

- **Gate-2 (final irreversible execute AUQ)** — confirms the rollback runbook is understood and
  authorizes the `cutover` operation (PAUTH-forbidden). Presented after Phase 1–2 evidence is GREEN.
- **GOV-FILE-BRIDGE-AUTHORITY-001 amendment** — its own formal-artifact-approval packet at Phase 3.

## Requirement Sufficiency

**Existing requirements sufficient** for Phases 1–2 (the surface of this proposal's `target_paths`).
The governing requirement is the owner-approved `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`, which defines
the generator contract, the round-trip fidelity criterion, the dual-authority shadow-verify exit
criterion, the rollback model, and the phase gates. The generator + round-trip test + shadow-verify are
source/test/`authoritative_generated_view`/`dual_write` work fully covered by the cutover PAUTH and the
ADR; no new requirement is needed to build them.

**New or revised requirement required before Phase 3 (the flip).** Phase 3 requires (a) the
`GOV-FILE-BRIDGE-AUTHORITY-001` amendment (formal-artifact-approval packet) repointing authority to the
TAFE store, and (b) a new derived `DCL` encoding the generated-view invariant + write-guard. Those are
captured through the governed approval path at Phase 3; the flip executes only after they land AND the
gate-2 AUQ is recorded. This proposal does NOT request that authority now.

## Proposed Change

Sequenced; each phase gated by the prior. Phases 1–2 are this proposal's implementable scope; Phases
3–4 are described for review completeness and return via a REVISED version post-gate-2.

**Phase 1 — Byte-faithful generator + round-trip golden test (this proposal; PAUTH
`authoritative_generated_view` + `test_addition`).**
- New module `groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py` exposing
  `render_index_from_flow_artifacts(flow_instances, flow_artifacts, *, header=...) -> str` (pure
  function): per `flow-bridge-<slug>` instance, emit a `Document: <slug>` block followed by the ordered
  version lines `<status_token>: <artifact_ref>` reconstructed from its `flow_artifacts`
  (`fa-bridge-<slug>-<NNN>`), newest-first, plus the canonical INDEX header. Document-block ordering is
  reproduced from ingest-captured ordering (the order INDEX presented at ingest); if ordering metadata
  is insufficient for byte-fidelity, the generator defines a deterministic canonical order and the
  round-trip test records the precise diff as the one-time, owner-visible reformat the flip would apply
  (semantics identical) — surfaced for the gate-2 decision, never applied silently.
- Round-trip golden test `test_tafe_index_generator.py`: ingest the live `bridge/INDEX.md` (Slice-C
  `ingest_bridge_index`, dry-run/in-memory) → `render_index_from_flow_artifacts` → assert byte-equality
  with the live INDEX; fixture-based variants cover terminal-archived trimming, multi-version threads,
  ADVISORY/DEFERRED tokens, and Document-block ordering. The generator is read-only and writes nothing.

**Phase 2 — Dual-authority shadow-verify CLI + test (this proposal; PAUTH `dual_write`).**
- Add `gt flow regen-verify` (`cli.py`): re-ingest the live INDEX into the shadow (or read current
  shadow), regenerate via the Phase-1 generator, and assert equality against the live `bridge/INDEX.md`;
  emit a JSON verdict (equal / diff) to `.gtkb-state/cutover-evidence/regen-verify/<run_id>/` (refuses
  to write canonical INDEX, mirroring `cutover-evidence`/`preview`). Test
  `test_tafe_index_generator_cli.py` covers equal + injected-diff cases.
- Operationally (no code): run `gt flow regen-verify` repeatedly under the live multi-harness swarm; the
  ADR's Phase-2 exit criterion is a sustained window of consecutive green regen-equality checks PLUS
  `gt flow cutover-evidence` GREEN. This proves the generator survives concurrent traffic before any
  authority change. Evidence accrues to the implementation report.

**Phase 3 — The flip (REVISED proposal; REQUIRES gate-2 AUQ + formal-artifact approvals; NOT this
scope).** (a) Swarm-quiesce the bridge writers; (b) final pre-cutover `gt flow ingest-bridge-index
--apply` so TAFE is the exact current truth; (c) migrate writers
(`scripts/gtkb_bridge_writer.insert_index_status`/`remove_document`, `bridge.index_mutation`,
`cli_bridge_index`, and the propose/revise/impl-report helpers) to write TAFE-first then regenerate
INDEX inside the existing serialized index write-lock, behind an authority-direction switch defaulting
to INDEX-canonical; (d) flip the switch (the single atomic `cutover` operation); (e) amend
`GOV-FILE-BRIDGE-AUTHORITY-001`; (f) record the new generated-view DCL; (g) harden
`.claude/hooks/bridge-index-write-serializer.py` so only the generator writes INDEX.

**Phase 4 — Post-flip hardening (later follow-on WIs; not this scope).** Optionally migrate hot readers
(dispatcher signature path) to query TAFE directly; consolidate hand-rolled INDEX parsers onto
`bridge.detector.parse_index`; retire dual-write scaffolding.

### Swarm-quiesce + final-re-ingest runbook (Phase 3 pre-steps; documented now for review)

1. Announce quiesce; pause/await the cross-harness trigger + single-harness dispatcher; confirm no
   in-flight bridge-helper writes (work-intent registry empty).
2. `gt flow ingest-bridge-index --apply` → TAFE shadow == exact live INDEX (fingerprint-gated, idempotent).
3. `gt flow cutover-evidence --json` → confirm `ok=True` (parity/contention/fidelity/completeness).
4. `gt flow regen-verify` → confirm byte-equality of regenerated vs live INDEX.
5. Flip the authority-direction switch; immediately regenerate INDEX and re-run `regen-verify` +
   `cutover-evidence`. On any red: execute the Rollback Plan.
6. Un-quiesce the swarm.

## Spec-Derived Verification Plan

Derived from the `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` Phase-1/2 contract (per
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

- `test_tafe_index_generator.py`:
  - Round-trip: ingest live INDEX → regenerate → byte-identical to live INDEX (the ADR Phase-1 exit
    criterion); if not byte-identical, the test asserts the diff is confined to ordering/whitespace and
    records it (the documented one-time reformat), failing on any *semantic* difference (added/dropped
    thread, changed status token, changed path).
  - Fixtures: multi-version thread reconstruction (`fa-bridge-<slug>-<NNN>` → ordered version lines);
    terminal-archived threads stay trimmed (consistent with `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`);
    ADVISORY/DEFERRED/WITHDRAWN tokens render correctly; Document-block ordering reproduced.
  - Read-only: AST/behavioral assertion that the generator performs no write to `bridge/`, no shadow
    write, no subprocess.
- `test_tafe_index_generator_cli.py`:
  - `gt flow regen-verify` returns equal-verdict on an in-sync fixture; diff-verdict (non-zero exit) on
    an injected divergence; refuses to write canonical `bridge/INDEX.md`.
- Integration: `gt flow regen-verify` over the live INDEX reproduces a byte-equal verdict at filing
  time (recorded in the implementation report as the Phase-1 round-trip evidence).
- Gates on changed Python: `ruff check` + `ruff format --check`.

## Risk / Rollback

- **Risk:** the generator is not byte-faithful (ordering/whitespace) → readers would drift at flip.
  **Mitigation:** Phase-1 golden round-trip test gates on byte-equality (semantic diff = hard fail);
  any benign reformat is surfaced for the gate-2 decision, never applied silently. Phases 1–2 change no
  authority, so a generator defect here cannot affect live bridge operation.
- **Risk:** write-then-regenerate under the swarm causes latency/contention (Phase 3).
  **Mitigation:** regeneration runs inside the existing serialized index write-lock; `cutover-evidence`
  `contention_zero` must stay true; this is Phase-3 scope and gate-2-gated.
- **Risk:** amending a P0 GOV invariant (Phase 3). **Mitigation:** own formal-artifact-approval packet +
  owner AUQ; LO bridge-repair-authority clause preserved verbatim; not in this proposal's scope.
- **Rollback (Phases 1–2):** purely additive — a new module + tests + a read-only CLI subcommand;
  reverting `tafe_index_generator.py`, the `cli.py` subcommand, and the two test files to HEAD restores
  prior behavior. No authority change, no INDEX mutation, no schema change (`kb_schema_change`
  PAUTH-forbidden).
- **Rollback (Phase 3, post-flip; documented now):** flip the authority-direction switch back to
  INDEX-canonical (writers resume direct INDEX writes; TAFE returns to read-derived shadow); revert the
  `GOV-FILE-BRIDGE-AUTHORITY-001` amendment to its prior version; relax the write-guard. Append-only
  `flow_instances`/`flow_artifacts` are never deleted; no data migration in either direction.

## Recommended Commit Type

`feat:` — Phases 1–2 add a new authoritative `flow_artifacts`-based INDEX generator and a
shadow-verify CLI surface (new capability), with their spec-derived tests.
