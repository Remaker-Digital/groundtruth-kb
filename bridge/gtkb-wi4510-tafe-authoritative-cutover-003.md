REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code autonomous Prime Builder session; ::init gtkb pb; WI-4510 TAFE cutover driver; explanatory output style
author_metadata_source: env runtime envelope (WI-4522)

# WI-4510 — Governed TAFE-authoritative bridge cutover (REVISED after NO-GO -002): byte-faithful INDEX generator + shadow-verify, then flip authority (gate-2)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_generator.py", "groundtruth-kb/tests/test_tafe_index_generator_cli.py"]

## Response to NO-GO (bridge/gtkb-wi4510-tafe-authoritative-cutover-002.md)

- **F1 (P1, blocking) — live cutover evidence red; cited green snapshot stale.** RESOLVED two ways, per
  Codex's two offered remedies:
  - **(a) Shadow currency restored now.** Ran `gt flow ingest-bridge-index --apply` (PAUTH `dual_write`):
    3 instances / 6 artifacts written — the exact 3 slugs Codex cited as `shadow_instance_missing`
    (`gtkb-wi4510-tafe-authoritative-cutover`, `gtkb-wi4510-governed-cutover`,
    `gtkb-wi4572-deploy-fqdn-spec1882-config-ization`). Fresh live `gt flow cutover-evidence --json` is
    now GREEN: `ok=True`, `parity.ok=True` (348/348 threads; `derived_artifacts=1962 ==
    index_version_lines=1962`), `lost_blocks=0`, `extra_blocks=0`, `contention_zero=true`,
    `fidelity.ok=true`. See § Readiness Evidence (fresh, live).
  - **(b) Shadow-currency recovery made an explicit first step.** Added **Phase 0 — Shadow-currency
    recovery** (§ Proposed Change) citing those 3 slugs, with acceptance criteria requiring a clean
    `gt flow cutover-evidence --json` (`ok=True`) before any Phase-2 authority-shadow claim.
  - **Reframing (important):** the observed staleness is not a contradiction of the proposal's premise —
    it is direct empirical evidence FOR it. The shadow does NOT remain current under ordinary bridge
    churn; that is precisely why this cutover requires a byte-faithful `flow_artifacts` generator, a
    continuous shadow-verify gate (Phase 2), Phase-0/final re-ingest, and a swarm-quiesce window. The
    NO-GO's own observation strengthens the case for the gates this proposal builds.
- **F2 (P2, advisory) — dual operative phrases in Requirement Sufficiency.** RESOLVED: § Requirement
  Sufficiency now carries a single operative phrase scoped to the requested work ("Existing requirements
  sufficient for Phases 1-2 only"); the Phase-3 requirement/approval statement moved to a separate
  § Future Phase 3 Gate that does not use the second operative phrase (per WI-3439 unambiguity).

## Summary

WI-4510 is the governed cutover that makes the TAFE typed-artifact store the **authoritative** source of
bridge workflow state and demotes `bridge/INDEX.md` to a **byte-faithful generated view**. It reverses
the bridge data-flow direction established by `GOV-FILE-BRIDGE-AUTHORITY-001` (today INDEX.md is
canonical and the TAFE shadow is ingested FROM it). It is a fundamental-architecture migration governed
by the owner-approved `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` (v1, specified; formal-artifact-approval
packet `.groundtruth/formal-artifact-approvals/2026-06-15-ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001.json`).

**The de-risking architecture (per the ADR).** Keeping `bridge/INDEX.md` a faithful generated view
collapses the migration surface from "every reader + dispatcher" to "the writer paths + one new
generator." `bridge.detector.parse_index` operates on a *string*; `bridge.notify.compute_actionable_pending`
operates on the parse result (reads `bridge_kind` from disk files); the cross-harness trigger,
single-harness dispatcher, AXIS-2 hook, session-start governance hook, and preflights all read the INDEX
*file*. If writers write TAFE-first then regenerate a byte-faithful INDEX, **no reader changes**.

**Prerequisite gap (the central finding).** No byte-faithful TAFE→INDEX generator exists. The only
generator, `tafe_index_preview.render_tafe_bridge_index_preview` (WI-4507), is explicitly
NON-authoritative and renders from `stage_instances`, which are *not written for bridge threads* in
Slice C (Slice C wrote `flow_instances` + `flow_artifacts` only). A new generator that reconstructs the
version-line history from `flow_artifacts` is required and is the first build deliverable (Phase 1).

**Shadow-currency reality (per NO-GO F1).** The TAFE shadow is read-derived and does NOT auto-track
ordinary bridge churn; between filing and review, three current instances were missing until a
re-ingest restored them. This proposal therefore makes shadow-currency recovery an explicit Phase-0
step with acceptance criteria, and the whole cutover hinges on the shadow-verify gate (Phase 2) +
final pre-cutover re-ingest under swarm-quiesce (Phase 3 runbook) rather than assuming the shadow stays
current on its own.

**Scope of THIS proposal's `target_paths`.** This proposal authorizes the do-now, PAUTH-permitted
Phases 0-2 (shadow-currency recovery is operational; the `flow_artifacts`-based generator + its
round-trip test + the dual-authority shadow-verify CLI + test are the source/test surface). The
irreversible flip (Phase 3 — writer migration, the authority switch, the GOV amendment, write-guard
hardening) is `cutover`/`formal_spec_promotion`, both PAUTH-FORBIDDEN, and is implemented only after the
WI-4510 closing owner AUQ (gate-2) via a REVISED proposal version that expands `target_paths` and
carries the gate-2 + formal-artifact-approval evidence.

## Readiness Evidence (fresh, live)

Re-verified this session AFTER the F1 re-ingest (read-only `gt flow cutover-evidence --json`; INDEX not
mutated by the evidence command):

- **Completeness:** `lost_blocks: 0`, `extra_blocks: 0` (terminal-archived threads legitimately absent
  per `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`).
- **Parity (dual-write):** `ok: True`, `derived_artifacts 1962 == index_version_lines 1962`, 348/348
  threads. The shadow is byte-faithful to the canonical INDEX after recovery.
- **Contention:** `contention_zero: True`, 0 re-plan artifacts/instances.
- **Fidelity:** `ok: True`, 0 fidelity_mismatches over 348 threads.
- **Recovery delta:** the immediately-prior live run was red (`ok: false`, `contention_zero: false`,
  `fidelity.ok: false`, 3 `shadow_instance_missing`); `gt flow ingest-bridge-index --apply` wrote 3
  instances + 6 artifacts (vs. the NO-GO's 5-artifact replan projection; extra version lines such as the -002 verdict files landed between the NO-GO read and this apply) and the next run returned the green result above. This delta is the live proof
  of the churn dynamic Phase 0 + Phase 2 address.

## Specification Links

- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the owner-approved decision this proposal implements:
  TAFE becomes canonical, `bridge/INDEX.md` becomes a byte-faithful generated view, phased reversible
  rollout, flip gated by the WI-4510 closing AUQ.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the P0 invariant being reversed ("the live contents of
  bridge/INDEX.md are the sole authoritative source for bridge queue state"). Phases 0-2 do NOT change
  it; the Phase-3 amendment (own formal-artifact-approval packet) repoints authority to the TAFE store
  while preserving the derived-surface prohibition, the read-live-before-deciding rule, and the LO
  permanent bridge-repair authority. Until then INDEX.md remains canonical and Phases 0-2 are
  read/derive-only against it.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the canonical D1-D4 ingestion derivation; the generator must
  reconstruct exactly the version-line set Slice C wrote into `flow_artifacts`
  (`fa-bridge-<slug>-<NNN>`, `metadata.status_token`, `artifact_ref`).
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the completeness contract: terminal-archived
  threads are legitimately absent from INDEX. The generator must reproduce INDEX *as it is* (it must NOT
  re-emit terminal-archived/trimmed threads); round-trip fidelity is defined against the live, trimmed
  INDEX, consistent with this completeness semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting: every
  implementation proposal must cite all relevant governing specifications; this section complies.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: VERIFIED requires
  spec-derived tests with executed evidence; the Spec-Derived Verification Plan derives its tests from
  the generator's byte-faithfulness contract, the Phase-0 acceptance criterion, and the ADR's
  Phase-1/2 exit criteria.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio) — the cutover is an artifact-lifecycle
  transition of bridge-state authority; the ADR + DELIB capture, the phased lifecycle, and the GOV
  amendment at flip are the governed lifecycle actions.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — WI-4510 is the umbrella program's terminal step; the
  "structured, queryable canonical bridge state" objective is what authority-flip delivers.
- `GOV-STANDING-BACKLOG-001` — WI-4510 is the governed standing-backlog work item driving this cutover.

## Prior Deliberations

- `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614` — owner AUQ approving creation of
  `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` ("Approve & insert ADR").
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` — owner AUQ "New canonical; withdraw old": this
  thread is canonical; `gtkb-wi4510-governed-cutover` was WITHDRAWN; its reversibility-backstop idea is
  carried into the Phase-3 plan.
- `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — owner gate-1: proceed to FILE this cutover proposal.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — the prior owner HOLD until WI-4546
  reconciliation landed (satisfied).
- `DELIB-20263410` — owner AUQ lifting the hold and authorizing cutover-readiness + proposal drafting.
- `DELIB-20263195` — TAFE cutover-sequence authorization (the cutover PAUTH's owner decision).
- bridge/gtkb-wi4510-tafe-authoritative-cutover-002.md — Loyal Opposition NO-GO (Codex, harness A) this
  thread is revising; F1 (live evidence) + F2 (requirement-sufficiency wording) both addressed above.
- WI-4508 Slice C (`gtkb-tafe-slice-c-ingestion-consolidated`, VERIFIED), WI-4509
  (`gtkb-wi4509-cutover-evidence`, VERIFIED), WI-4507 (`tafe_index_preview`, non-authoritative — the
  generator explicitly NOT reused).

## Owner Decisions / Input

This proposal depends on owner approval, captured via AskUserQuestion (session c50a9788):

1. **Gate-1 (file the proposal)** — `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614`.
2. **ADR formal-artifact approval** — `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`
   ("Approve & insert ADR"); ADR inserted (v1, specified).
3. **Duplicate reconciliation** — `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` ("New canonical;
   withdraw old").

No further owner decision is required to REVIEW this proposal or to implement Phases 0-2 after GO
(covered by the cutover PAUTH). The following owner decisions are explicitly DEFERRED and gate Phase 3
(see § Future Phase 3 Gate):

- **Gate-2 (final irreversible execute AUQ)** — confirms the rollback runbook (incl. the carried-forward
  frozen-INDEX backstop) is understood and authorizes the `cutover` operation (PAUTH-forbidden).
  Presented after Phase 0-2 evidence is green.
- **GOV-FILE-BRIDGE-AUTHORITY-001 amendment** — its own formal-artifact-approval packet at Phase 3.

## Requirement Sufficiency

**Existing requirements sufficient for Phases 1-2 only.** The governing requirement is the
owner-approved `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`, which defines the generator contract, the
round-trip fidelity criterion, the dual-authority shadow-verify exit criterion, the Phase-0 acceptance
criterion, the rollback model, and the phase gates. The Phase-0 shadow-currency recovery, the generator,
the round-trip test, and the shadow-verify CLI are source/test/`authoritative_generated_view`/`dual_write`
work fully covered by the cutover PAUTH and the ADR; nothing further is needed to build them.

## Future Phase 3 Gate

Phase 3 (the irreversible flip) is out of this proposal's scope and is gated separately. Before any flip
it requires two new formal artifacts captured through the governed approval path — an amendment to
`GOV-FILE-BRIDGE-AUTHORITY-001` (own formal-artifact-approval packet) repointing authority to the TAFE
store, and a new generated-view `DCL` encoding the byte-faithful-generated-view invariant + the
write-guard — plus the WI-4510 closing owner AUQ (gate-2). The cutover PAUTH forbids both `cutover` and
`formal_spec_promotion`, so none of this is authorized by this proposal; it returns as a REVISED version
carrying that evidence after Phases 0-2 are green.

## Proposed Change

Sequenced; each phase gated by the prior. Phases 0-2 are this proposal's implementable scope; Phases 3-4
are described for review completeness and return via a REVISED version post-gate-2.

**Phase 0 — Shadow-currency recovery (operational first step; PAUTH `dual_write`).**
Run `gt flow ingest-bridge-index --apply` to bring the read-derived TAFE shadow current with live
`bridge/INDEX.md`. Observed this session: 3 stale instances
(`gtkb-wi4510-tafe-authoritative-cutover`, `gtkb-wi4510-governed-cutover`,
`gtkb-wi4572-deploy-fqdn-spec1882-config-ization`) restored (3 instances / 6 artifacts written).
**Acceptance criteria:** `gt flow cutover-evidence --json` returns `ok=True` (parity + contention-zero +
fidelity + no lost/extra blocks). No Phase-2 authority-shadow claim may be made on stale evidence; a
clean `cutover-evidence` result must be re-established immediately before any Phase-2 equality assertion
and recorded in the implementation report. (This step also runs as the Phase-3 runbook pre-step.)

**Phase 1 — Byte-faithful generator + round-trip golden test (PAUTH `authoritative_generated_view` +
`test_addition`).**
New module `groundtruth-kb/src/groundtruth_kb/tafe_index_generator.py` exposing
`render_index_from_flow_artifacts(flow_instances, flow_artifacts, *, header=...) -> str` (pure function):
per `flow-bridge-<slug>` instance, emit a `Document: <slug>` block followed by the ordered version lines
`<status_token>: <artifact_ref>` reconstructed from its `flow_artifacts` (`fa-bridge-<slug>-<NNN>`),
newest-first, plus the canonical INDEX header. Document-block ordering is reproduced from
ingest-captured ordering; if ordering metadata is insufficient for byte-fidelity, the generator defines
a deterministic canonical order and the round-trip test records the precise diff as the one-time,
owner-visible reformat the flip would apply (semantics identical) — surfaced for the gate-2 decision,
never applied silently. Round-trip golden test `test_tafe_index_generator.py`: ingest the live
`bridge/INDEX.md` (Slice-C `ingest_bridge_index`, in-memory) → `render_index_from_flow_artifacts` →
assert byte-equality with the live INDEX; fixtures cover terminal-archived trimming, multi-version
threads, ADVISORY/DEFERRED tokens, and Document-block ordering. The generator is read-only and writes
nothing.

**Phase 2 — Dual-authority shadow-verify CLI + test (PAUTH `dual_write`).**
Add `gt flow regen-verify` (`cli.py`): refresh shadow currency (the Phase-0 step), regenerate via the
Phase-1 generator, and assert equality against live `bridge/INDEX.md`; emit a JSON verdict (equal/diff)
to `.gtkb-state/cutover-evidence/regen-verify/<run_id>/` (refuses to write canonical INDEX, mirroring
`cutover-evidence`/`preview`). Test `test_tafe_index_generator_cli.py` covers equal + injected-diff
cases. Operationally (no code): run `gt flow regen-verify` repeatedly under the live swarm; the ADR's
Phase-2 exit criterion is a sustained window of consecutive green regen-equality checks PLUS a clean
`gt flow cutover-evidence` immediately beforehand (the Phase-0 acceptance criterion). Evidence accrues
to the implementation report.

**Phase 3 — The flip (REVISED proposal; REQUIRES gate-2 AUQ + formal-artifact approvals; NOT this
scope).** (a) Swarm-quiesce the bridge writers; (b) final pre-cutover `gt flow ingest-bridge-index
--apply` so TAFE is the exact current truth; (c) migrate writers
(`scripts/gtkb_bridge_writer.insert_index_status`/`remove_document`, `bridge.index_mutation`,
`cli_bridge_index`, and the propose/revise/impl-report helpers) to write TAFE-first then regenerate
INDEX inside the existing serialized index write-lock, behind an authority-direction switch defaulting
to INDEX-canonical; (d) flip the switch (the single atomic `cutover` operation); (e) amend
`GOV-FILE-BRIDGE-AUTHORITY-001`; (f) record the new generated-view DCL; (g) harden
`.claude/hooks/bridge-index-write-serializer.py` so only the generator writes INDEX; (h) the
**reversibility backstop** (carried forward from the withdrawn `gtkb-wi4510-governed-cutover`): freeze a
timestamped immutable copy of `bridge/INDEX.md` at the flip + a documented/coded revert that regenerates
the hand-maintained INDEX from the shadow.

**Phase 4 — Post-flip hardening (later follow-on WIs; not this scope).** Optionally migrate hot readers
(dispatcher signature path) to query TAFE directly; consolidate hand-rolled INDEX parsers onto
`bridge.detector.parse_index`; retire dual-write scaffolding.

### Swarm-quiesce + final-re-ingest runbook (Phase 3 pre-steps; documented now for review)

1. Announce quiesce; pause/await the cross-harness trigger + single-harness dispatcher; confirm no
   in-flight bridge-helper writes (work-intent registry empty).
2. `gt flow ingest-bridge-index --apply` → TAFE shadow == exact live INDEX (fingerprint-gated, idempotent).
3. `gt flow cutover-evidence --json` → confirm `ok=True`.
4. `gt flow regen-verify` → confirm byte-equality of regenerated vs live INDEX.
5. Freeze a timestamped immutable copy of `bridge/INDEX.md` (reversibility backstop).
6. Flip the authority-direction switch; immediately regenerate INDEX and re-run `regen-verify` +
   `cutover-evidence`. On any red: execute the Rollback Plan (restore from the frozen copy + revert switch).
7. Un-quiesce the swarm.

## Spec-Derived Verification Plan

Derived from the `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` Phase-0/1/2 contract (per
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

- **Phase-0 acceptance (operational):** `gt flow ingest-bridge-index --apply` then
  `gt flow cutover-evidence --json` returns `ok=True`; recorded in the implementation report (this
  session's green run after re-ingest is the first such evidence).
- `test_tafe_index_generator.py`:
  - Round-trip: ingest live INDEX → regenerate → byte-identical to live INDEX (ADR Phase-1 exit
    criterion); if not byte-identical, the test asserts the diff is confined to ordering/whitespace and
    records it (the documented one-time reformat), failing on any *semantic* difference (added/dropped
    thread, changed status token, changed path).
  - Fixtures: multi-version thread reconstruction (`fa-bridge-<slug>-<NNN>` → ordered version lines);
    terminal-archived threads stay trimmed; ADVISORY/DEFERRED/WITHDRAWN tokens render correctly;
    Document-block ordering reproduced.
  - Read-only: AST/behavioral assertion that the generator performs no write to `bridge/`, no shadow
    write, no subprocess.
- `test_tafe_index_generator_cli.py`:
  - `gt flow regen-verify` returns equal-verdict on an in-sync fixture; diff-verdict (non-zero exit) on
    an injected divergence; refuses to write canonical `bridge/INDEX.md`.
- Integration: `gt flow regen-verify` over the live INDEX (after a Phase-0 re-ingest) reproduces a
  byte-equal verdict at filing time (recorded in the implementation report).
- Gates on changed Python: `ruff check` + `ruff format --check`.

## Risk / Rollback

- **Risk:** the generator is not byte-faithful (ordering/whitespace) → readers would drift at flip.
  **Mitigation:** Phase-1 golden round-trip test gates on byte-equality (semantic diff = hard fail); any
  benign reformat is surfaced for the gate-2 decision. Phases 0-2 change no authority, so a generator
  defect here cannot affect live bridge operation.
- **Risk:** the shadow re-stales under swarm churn (the NO-GO F1 observation). **Mitigation:** Phase-0
  recovery + acceptance criteria; Phase-2 verifies under the live swarm; Phase-3 runbook does a final
  re-ingest under swarm-quiesce. No authority claim is made on stale evidence.
- **Risk:** write-then-regenerate under the swarm causes latency/contention (Phase 3).
  **Mitigation:** regeneration runs inside the existing serialized index write-lock; `cutover-evidence`
  `contention_zero` must stay true; Phase-3 scope, gate-2-gated.
- **Risk:** amending a P0 GOV invariant (Phase 3). **Mitigation:** own formal-artifact-approval packet +
  owner AUQ; LO bridge-repair-authority clause preserved verbatim; not this proposal's scope.
- **Rollback (Phases 0-2):** Phase 0 is idempotent shadow maintenance (append-only; no destructive
  effect). Phases 1-2 are purely additive — a new module + tests + a read-only CLI subcommand; reverting
  `tafe_index_generator.py`, the `cli.py` subcommand, and the two test files to HEAD restores prior
  behavior. No authority change, no INDEX mutation, no schema change.
- **Rollback (Phase 3, post-flip; documented now):** flip the authority-direction switch back to
  INDEX-canonical (writers resume direct INDEX writes; TAFE returns to read-derived shadow); restore
  `bridge/INDEX.md` from the frozen immutable copy; revert the `GOV-FILE-BRIDGE-AUTHORITY-001` amendment;
  relax the write-guard. Append-only `flow_instances`/`flow_artifacts` are never deleted; no data
  migration in either direction.

## Recommended Commit Type

`feat:` — Phases 1-2 add a new authoritative `flow_artifacts`-based INDEX generator and a shadow-verify
CLI surface (new capability), with their spec-derived tests. (Phase 0 is operational; no commit.)
