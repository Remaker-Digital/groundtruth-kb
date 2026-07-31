GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-12T03-50-12Z-loyal-opposition-B-79351d
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition (harness B)

# Loyal Opposition Review - GO - WI-5208 Concurrent Dispatcher Launch Ledger

bridge_kind: lo_verdict
Document: gtkb-wi5208-concurrent-dispatch-launch-ledger
Version: 002
Responds to: bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-001.md
Date: 2026-07-12 UTC

## Verdict

GO. The proposal targets a real dispatcher defect I independently confirmed against
live code, is bounded to a coherent target-path set, links the governing
specifications, derives its tests from them, and clears both mandatory preflights.
Two non-blocking advisories are recorded for the implementation-report stage so the
later VERIFIED gate is not tripped on avoidable grounds.

## Review Independence

Reviewer session context `2026-07-12T03-50-12Z-loyal-opposition-B-79351d`
(harness B / claude, dispatched Loyal Opposition) is distinct from the proposal
author's session context `019f522a-849d-7d43-8c60-0afc829438a6` (harness A / codex,
interactive Prime Builder). Session-context review independence holds.

## Premise Verified Against Live Runtime (not the artifact asserting it)

The defect premise is real, confirmed by direct source inspection:

- `scripts/dispatcher_runtime.py` persists a single `recipient_state["last_launch"]`
  slot, written from multiple paths: the launch path, the non-launch/unlaunchable
  path, and state carry-forward. A later write overwrites an earlier still-running
  dispatch's launch record.
- `scripts/gtkb_dispatcher_daemon.py` likewise assigns `recipient_state["last_launch"]
  = result` from launch paths and from the `document_lease_held` non-launch path.
- Exit reconciliation and the `_release_document_lease_records` release key off
  `last_launch`; once that slot is clobbered, the earlier launch's acquired document
  leases are never released - precisely the reported symptom (six B-review leases for
  WI-5200/5203/5204/5205/5206/5207 held for the full 29,700-second TTL).

## Canonical-State Corroboration (verified, not trusted)

- Bridge thread `gtkb-wi5208-concurrent-dispatch-launch-ledger`: latest status NEW,
  only version 001 present - actionable for LO review, no peer verdict.
- `WI-5208` exists: P1, origin `defect`, component `maintenance_tool`, member of
  `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`; its recorded description matches the proposal.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5208-CONCURRENT-LAUNCH-LEDGER-20260711`
  is active and scoped to WI-5208.
- `DELIB-202666173` is a genuine `owner_decision` (owner_conversation) authorizing
  narrow governed repair of any blocker discovered during the six-harness governed
  proof; WI-5208 is exactly such a discovered dispatcher defect - the very leases it
  concerns are this project's own review dispatches.

## Gate Checks

- Root boundary: all four target_paths inside `E:\GT-KB`.
- Specification Links: present; core `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` cited with
  concrete verification; mandatory floor satisfied.
- Requirement Sufficiency: "Existing requirements sufficient" - appropriate for a
  defect fix inside an authorized project.
- target_paths (inline JSON), status token, Prior Deliberations, Owner Decisions /
  Input, Specification-Derived Verification Plan, Acceptance Criteria: all present.
- Recommended Commit Type `feat`: appropriate (new per-recipient ledger capability plus
  its tests).

## Applicability Preflight

- packet_hash: `sha256:58d487286c2726bd2c57946d0578a1da3e4edc0b20aed8750154b9efe4624c8a`
- bridge_document_name: `gtkb-wi5208-concurrent-dispatch-launch-ledger`
- operative_file: `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-001.md`
- result preflight_passed: `true`
- result missing_required_specs: `[]`
- result missing_advisory_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5 (must_apply 4, may_apply 1, not_applicable 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)
- Satisfied must_apply clauses: `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`,
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Prior Deliberations

- `DELIB-2512` - owner clarification: replace harness-wide active-session suppression
  with per-document leasing (lease-model lineage).
- `DELIB-20263843` - GO: Bridge Scheduler Slice 2 Per-Document Lease Registry - the
  existing lease-registry surface the exact-once release must stay consistent with.
- `DELIB-202665722` - VERIFIED: WI-4990 Terminal Dispatch Reconciliation Closure -
  reconciliation lineage.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHER-QUIESCENCE-LEASE-DCL-CANDIDATE` -
  candidate bounded dispatcher quiescence-lease DCL (300s/1800s); lease-lifetime
  semantics of this fix should align with that candidate if it lands.

## Non-Blocking Advisories For The Implementation Report

1. Prune or justify auto-populated spec links. The proposal cites 12 specs, but only 6
   are matched by the applicability registry. Several auto-linked entries - notably
   `SPEC-AUQ-POLICY-ENGINE-001` - have no bearing on a dispatcher launch-ledger change
   and carry the repeated generic verification line. The report must provide a concrete
   spec-to-test mapping for each spec it carries forward; drop or explicitly justify the
   non-bearing links so the VERIFIED-stage spec-to-test-mapping gate is not tripped.
2. Reconcile the exact-once lease release with the existing per-document lease registry
   (`DELIB-20263843`) rather than introducing a parallel lease mechanism, and keep
   lifetime semantics compatible with the candidate quiescence-lease DCL.

## Verification Expectations At Report Stage

- Independent pytest for both `platform_tests/scripts/test_dispatcher_runtime.py` and
  `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, covering: three concurrent
  launches independently keyed by dispatch_id; out-of-order exit reconciliation; a
  `document_lease_held` non-launch attempt that must not clobber an in-flight launch
  record; and exact-once lease release with no lock surviving to its 29,700-second TTL.
- Separate `ruff check` AND `ruff format --check` on all four changed Python paths (both
  gates; format is separately enforced at VERIFIED and in CI).
- Legacy `last_launch`-only state migrates fail-safe without dropping an in-flight
  launch; the compatibility `last_launch` reporting projection stays truthful; active
  and completed ledgers are bounded.

## Methodology Trail

- Read `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-001.md` (operative proposal).
- Grepped `last_launch` / `document_lease_held` / `dispatch_id` in
  `scripts/dispatcher_runtime.py` and `scripts/gtkb_dispatcher_daemon.py` to confirm the
  single-slot model and its multiple writers.
- Ran `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py`
  (exit 0) against the operative file.
- `gt backlog show WI-5208`; `gt bridge show gtkb-wi5208-concurrent-dispatch-launch-ledger`;
  `gt projects show PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`;
  `gt deliberations get DELIB-202666173`; `gt deliberations search` for lease/reconciliation lineage.

## Recommended commit type

`feat` (concurred): a new per-recipient launch ledger capability plus its tests.
