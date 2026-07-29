NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; build review context with test verdict envelope

bridge_kind: lo_verdict
Document: gtkb-wi5714-registry-write-linearizability
Version: 004
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-003.md
Date: 2026-07-28 America/Los_Angeles

# Loyal Opposition Proposal Review — WI-5714 Registry Write Linearizability

## Verdict

NO-GO on one bounded specification-linkage omission. Revision 003 closes every
blocking design and verification finding from version 002 while remaining
inside the exact two-file owner authorization. It nevertheless makes dated
numeric and current-state claims in an audit/verification path without citing
or mapping `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, which expressly governs those
claims.

No owner decision is required. Add the missing governing link and fresh-read
verification mapping; the accepted generation-CAS design need not change.

## Review Independence

- Reviewed artifact author session: `019f9329-a174-7763-8f7e-29679f39e6bd`.
- Reviewer session: `019fac54-c55c-75c0-8332-d7fdaf03b20a`.
- Author metadata is present and readable, and the session contexts differ.
- The review-independence gate passes.

## Blocking Finding

### P1 — Current numeric/state evidence omits the governing freshness contract

**Claim.** Version 003 relies on numeric and mutable-state evidence but does not
cite `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` or map it to implementation-report and
terminal-verification reads.

**Evidence in the revision.** The operative proposal records:

- a dated two-process reproduction with two reported successes and one retained
  amendment;
- a dated focused baseline of `29 passed`;
- current work-item, project, PAUTH, target-cleanliness, bridge-state, and
  residual-work claims;
- future report and verification conclusions that depend on live canonical,
  packaged, projection, journal, PAUTH, claim, packet, and bridge state.

**Governing requirement.** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` applies to
reporting surfaces and any read path producing a numeric or state claim, state
queries about canonical sources, and audit/verification pass/fail paths. It
requires fresh canonical reads rather than cached snapshots or copied summaries.

**Why the mechanical preflight did not catch it.** Applicability and clause
preflights pass because the configured textual triggers do not infer this
semantic relevance from a proposal's dated measurements. They remain a
mechanical floor; the mandatory proposal linkage rule still requires every
relevant governing specification to be cited and mapped.

**Impact.** A later implementation report or terminal review could reuse the
proposal's earlier reproduction, test count, or governance-state summary as if
it were current and certify the implementation without rerunning the decisive
reads. That would violate both the freshness GOV and the specification-derived
verification contract.

**Required revision.** Add `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` to Specification
Links and add a discriminating verification row requiring fresh canonical reads
at implementation-report and terminal-verification time for:

1. the deterministic lost-update reproducer or its promoted regression test;
2. the complete focused pytest module and actual collected/pass count;
3. live WI-5714/project/PAUTH state and exact target cleanliness;
4. live TAFE plus status-bearing numbered-file bridge state;
5. claim and implementation-start packet liveness;
6. canonical/package/projection/journal generation parity after success and
   after retry exhaustion.

The report must record commands, timestamps or generation anchors, and results;
it must not treat this proposal's dated measurements as current closure evidence.

## Full-Chain Disposition

Versions 001 through 003 were read in full.

- Version 001 correctly diagnosed the lost-update race but had no measured red
  baseline, no deterministic interleaving, weak exact-new-behavior proof,
  generic verification mappings, and an overbroad completion claim.
- Version 002 accepted the diagnosis and generation-CAS mechanism but issued
  NO-GO on those evidence and scope defects.
- Version 003 supplies a measured red baseline, independent green baseline,
  child-local first-read barrier under Windows spawn, deterministic in-process
  interposition, exact conflict-subclass and no-side-effect assertions,
  coherent-read/parity evidence, requirement-specific mapping, a rejected-
  alternative analysis, explicit retry taxonomy, and an eight-attempt safety
  budget grounded in the owner decision.
- Version 003 narrows completion to `amend_artifact` and captures unbound
  `register_artifacts`/`bootstrap_legacy_registry` work as WI-5736 / TEST-11748.

All version-002 findings are accepted as closed and must carry forward. The
remaining blocker is only the missing freshness specification and evidence row.

## Positive Evidence

- The lost-update defect is real: live `amend_artifact` reads one coherent
  snapshot, builds a full desired generation, then applies without binding the
  snapshot generation.
- The existing transaction layer already computes coherent generation identity
  and rejects a supplied stale digest before journal or declaration/projection
  mutation, making the proposed mechanism feasible and bounded.
- The deterministic spawn design installs its wrapper inside each child, waits
  only on the first read, and lets fresh-snapshot retries bypass the barrier.
- Exact exception classification, retry-only-conflict taxonomy, amend-specific
  idempotency ordering, no-partial-write exhaustion, and the whole-operation-lock
  alternative are adequately addressed.
- `WI-5714` is open at P0 in the cited project.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729`
  is active, unexpired, unsuperseded, scoped only to WI-5714, permits only
  source/test mutation, and names exactly the two declared targets.
- Both target files are clean.
- The focused baseline was independently rerun: `29 passed in 12.20s`.
- `WI-5736` exists for the out-of-scope residual writers.
- Both mandatory preflights pass.

## Applicability Preflight

- packet_hash: `sha256:3a49f2c9472f29be96aa56c35ef9d08401c50acba782d0a277b1c126fa988dce`
- candidate_evidence_hash: `sha256:44c0d0e1bea64dfd0ba5b84f96f4e7de9a78bb7c29cd9db1d8ba3db2bb47b527`
- bridge_document_name: `gtkb-wi5714-registry-write-linearizability`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5714-registry-write-linearizability-003.md`
- operative_file: `bridge/gtkb-wi5714-registry-write-linearizability-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5714-registry-write-linearizability`
- Operative file: `bridge/gtkb-wi5714-registry-write-linearizability-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory gate exit: `0`

The mechanical gates are a floor. The blocking finding above comes from manual
review of the proposal's verification claims against a relevant live GOV.

## Specification-Derived Review

| Requirement | Review evidence | Disposition |
|---|---|---|
| `GOV-PLATFORM-SOT-REGISTRY-001` | accepted deltas retained in the final authoritative snapshot | PASS |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` / `GIT-REQ-A11` | forced spawn wave, deterministic interposition, coherent committed read | PASS |
| Registry parity and mutation authorization DCLs | exact conflict before mutation; parity/journal assertions | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | omitted from links and verification mapping despite dated/live audit claims | NO-GO |
| Project and operation-time authorization | active exact-singleton two-path PAUTH; later claim/start required | PASS |
| Bridge/spec/test linkage | fresh mechanical packets and otherwise discriminating table | PASS except freshness omission |
| Root boundary, lifecycle, traceability, and hygiene | in-root two-path scope; append-only chain; residual WI/test | PASS |

## Prior Deliberations

Required archive search and direct retrieval confirmed:

- `DELIB-202667517` is the owner decision requiring highly parallel Prime
  Builder operation and preservation of accepted shared-control-plane writes.
- `DELIB-202667522` is the exact owner authorization for the two-file WI-5714
  repair, typed conflict, fresh-snapshot retry, eight-attempt bound, and
  deterministic Windows-spawn coverage.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` traces to owner decision `DELIB-2521` and
  its bounded later amendments; no decision waives fresh reads for this audit or
  verification path.

No new owner decision is required.

## Review Methodology

- Read versions 001 through 003 in full and traced every version-002 finding to
  its version-003 disposition.
- Inspected the live error taxonomy, `amend_artifact`, transaction digest guard,
  idempotency ordering, and focused tests.
- Retrieved both owner decisions, the freshness GOV, work item, residual work,
  and exact active PAUTH; searched the Deliberation Archive for registry
  concurrency decisions.
- Ran both mandatory preflights against version 003.
- Independently ran the focused baseline: `29 passed in 12.20s`.
- Verified both target files are clean.
- Used a parallel read-only reviewer to challenge specification completeness and
  then independently confirmed the omitted GOV's applicability.

## Skills Applied

- `gtkb-bridge`
- `gtkb-proposal-review`
- `gtkb-query`

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
