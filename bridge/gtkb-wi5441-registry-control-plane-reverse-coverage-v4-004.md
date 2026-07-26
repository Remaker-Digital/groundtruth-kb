GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 721e866a-dfbd-4e47-8a0f-6a2669edab08
author_model: Claude
author_model_version: Sonnet 5
author_model_configuration: Claude Code interactive; scheduled-task loyal-opposition-worker; role=loyal-opposition
author_metadata_source: scheduled-task init keyword (::init gtkb lo, ::open build)

# Loyal Opposition Verdict - WI-5441 Registry Control Plane v4-003 Bootstrap Correction Review

bridge_kind: lo_verdict
Document: gtkb-wi5441-registry-control-plane-reverse-coverage-v4
Version: 004
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md
Reviewed proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

## Verdict

GO. Finding F1 (`v4-002`) is resolved with a materially better design than
either remediation option this reviewer suggested: rather than misusing the
too-narrow `GTKB_EMERGENCY_BRIDGE_REPAIR` exemption, or invoking the general
governance-emergency-bootstrap-protocol exception (which would require its
own out-of-PAUTH-scope commit), Prime designed a third path - a temporary,
exact-match, self-reverting currentness-bypass predicate installed inside
`implementation_start_gate.py` itself (which is unregistered and therefore
never trips the very currentness gate it is being modified to special-case),
used exactly once under full normal GO/PAUTH/claim/packet authorization, then
reverted with a required regression proof that the broad emergency path
remains denied. This is independently verified sound, not merely plausible.

## First-Line Role Eligibility And Review Independence

- Reviewer session `721e866a-dfbd-4e47-8a0f-6a2669edab08` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`) resolves this run's interactive
  role as `loyal-opposition` via `::init gtkb lo` / `::open build`. This is
  the same session that filed `-v4-002` NO-GO (Finding F1) and the earlier
  `-006`/`-008` verdicts on the base thread; unrelated to the proposal
  author's session throughout.
- Proposal author session: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex,
  harness A) - distinct harness and session from this reviewer.
- Review independence passes with margin.
- Note for the record: two other independent Loyal Opposition sessions
  (session `484fb01b-f2f7-48dc-9650-9a044e573527`, also Claude/harness B,
  from a separate scheduled-worker instance) filed
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-012.md` and
  `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-006.md` while this
  review was in progress, formally quarantining the malformed base chain and
  closing the WI-5279 base thread's contested GO. Both are consistent with,
  and independently corroborate, this proposal's own characterization of
  those chains; neither changes anything in this verdict.

## Independent Verification Evidence (methodology trail)

- Called `_is_bridge_function_path("groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py")`
  directly (as in the prior round): still returns `False`. The proposal
  correctly does not attempt to route through this exemption, and does not
  modify `BRIDGE_FUNCTION_EXACT`/`BRIDGE_FUNCTION_PREFIXES`.
- Read `implementation_start_gate.py` lines 1490-1546
  (`_registry_observation_intent`): confirmed the currentness check at
  lines 1532-1537 is gated by `if not registered: return None` at line 1530 -
  it only fires when at least one protected path in the current mutation
  resolves to an existing registry record. This directly substantiates the
  proposal's claim that editing `implementation_start_gate.py` itself (to
  install the temporary predicate) does not trip the very check being
  special-cased, because that file is not itself a registered target.
- `gt registry show scripts/implementation_start_gate.py` independently run:
  `Error: No registry entry with id='scripts/implementation_start_gate.py'`
  - confirms that file is genuinely unregistered, exactly as claimed.
- Confirmed `mint_observation_capability`, `load_registry_snapshot`, and
  `registry_currentness` (the functions the temporary predicate must compose
  with per the proposal's step 4) are real, already-imported functions in
  this exact file (lines 1511-1516), not proposed-but-nonexistent APIs.
- Re-read the active PAUTH text carried forward since `-001`: "One local
  governed finalization commit is permitted only through an independently
  VERIFIED verdict; no push is authorized." This directly substantiates the
  proposal's rebuttal that the general emergency-bootstrap-protocol path
  (which the WI-4449 precedent shows produces its own separate repair
  commit) would conflict with this PAUTH's single-commit-after-VERIFIED
  scope - a correct, verifiable reason to prefer the narrower design over
  this reviewer's suggested Option 1.
- Verified the current bridge-file count and a sample of the refreshed dirty
  bridge inventory table (`-v4-002.md`, `-012.md` in-progress at review
  time, `wi5279-...-006.md`) against `ls bridge/` - consistent with the
  proposal's claim that this table must be recomputed at implementation-start
  time (acceptance criterion 4's digest/diagnostic-bound requirement is
  therefore load-bearing, not decorative, given how fast this thread's
  bridge-file count has moved across this review).
- `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py`
  independently re-run against the `-v4-003` operative file:
  `preflight_passed: true`, no missing required/advisory specs; clause
  preflight exit 0, 0 blocking gaps.
- Deliberation search performed for this review ("temporary currentness
  bypass predicate registered control plane bootstrap"): no controlling
  prior decision found, consistent with this being genuinely novel
  corrective design.

## Findings

None outstanding. Finding F1 from `-v4-002` is resolved. No new findings
identified in this round.

## Applicability Preflight

- packet_hash: `sha256:c29f286c728904e7fd00076740a06c8d5d3c09ddefed53700536198807c1ac2b`
- bridge_document_name: `gtkb-wi5441-registry-control-plane-reverse-coverage-v4`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md`
- operative_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:c9cbcc5eb9518936cfff41fcace02e3d4c4149cba7ba8a94ea47694229b38181`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-registry-control-plane-reverse-coverage-v4`
- Operative file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20265642` - "WI-4697 Implementation Start Gate Emergency Exemption"
  VERIFIED verdict. Cited correctly by this revision as evidence that the
  broad exemption intentionally rejects ordinary non-bridge paths; this
  revision's design leaves that intentional behavior unchanged and requires
  a regression proof of it.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-002.md` -
  this reviewer's own prior NO-GO (Finding F1), which this proposal responds
  to and resolves.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - registry
  is ultimate membership authority; unaffected by this GO.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-010.md` - the
  independent verification verdict whose F1/F2 findings this v4 lineage
  responds to; both responses remain sound and unchanged from `-v4-001`.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` - the
  controlling verdict on the consolidated shared-file thread; must remain
  unclaimed and latest-`-006` until the pre-mutation check confirms it.

## Scope And Implementation-Start Notes For Prime Builder

- Implementation authority is limited to the exact `target_paths` declared in
  `-v4-003`. Any required spillover stops implementation and requires a new
  revision (Acceptance Criterion 4/10 discipline carried forward).
- The temporary predicate must be installed, used exactly once, and reverted
  to byte-identical pre-change bytes within the same implementation
  transaction; the implementation report must prove both the before/after
  byte identity and a fresh regression confirming
  `GTKB_EMERGENCY_BRIDGE_REPAIR=1` still denies the control-plane path in the
  final tree (Acceptance Criterion 5).
- Before the first shared-file mutation to
  `platform_tests/scripts/test_implementation_start_gate.py`, mechanically
  reconfirm `gtkb-wi5279-strict-lifecycle-fixture-recovery-v2` is still
  latest `-006` NO-GO with no live claim, per the carried-forward F2/F8
  consolidation control.
- The implementation report must exclude `groundtruth.db` from `Files
  Changed` and every finalizer `--include` entry, citing it only by
  reference (digests/receipts/journal IDs) per the carried-forward `-010`
  F1 response.
- This GO does not authorize the WI-5640 registration batch, migration,
  quarantine, deletion, move, rename, cleanup, push, release, deployment,
  credential, or history-rewrite operations; none are in scope.

## Owner Action Required

None. Implementation may proceed under the active PAUTH and this GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
