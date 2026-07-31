REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - Cursor E Dispatcher Telemetry Provenance

bridge_kind: prime_proposal
Document: gtkb-wi5369-cursor-dispatch-telemetry-provenance
Version: 003
Responds to: bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-002.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5369
Related Work Items: WI-5400, WI-5427

target_paths: ["platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py"]

implementation_scope: focused test only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision accepts the version 002 NO-GO and preserves the accepted
test-only design. It makes the production-baseline dependency explicit and
operation-time enforceable:

1. `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md` is now the
   canonical terminal `VERIFIED` entry for WI-5400.
2. `bridge/gtkb-wi5427-daemon-generation-handoff-005.md` remains `REVISED`.
   WI-5369 implementation must not start until that thread reaches independent
   terminal `VERIFIED`.
3. Immediately before any WI-5369 claim or implementation-start packet, the
   implementer must prove that the new test target is absent or clean and that
   the three exercised production paths are clean relative to committed HEAD:
   `scripts/dispatcher_runtime.py`, `scripts/ensure_dispatcher_daemon.py`, and
   `scripts/gtkb_dispatcher_daemon.py`.
4. Any failed precondition is a fail-closed no-op. It permits no test write and
   must be returned through this bridge thread with current canonical evidence.

The only implementation target remains the new test module. No production
source, dispatcher configuration, dispatcher runtime state, TAFE state,
eligibility, routing, lease, or worker mutation is proposed.

## Summary

Add one isolated production-path integration test proving that the existing
role-neutral dispatch telemetry reconciliation records Cursor E worker, model,
status, and error provenance for successful and failed completion. The
canonical WI-5369 MemBase record supplies the captured defect statement;
this proposal does not cite or depend on runtime logs, scratch material,
retired evidence directories, or copied telemetry projections.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5369; TEST-11485; PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717; bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-002.md",
  "canonical_authority": "SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py exercising the committed production reconciliation API after the WI-5427 dependency clears",
  "before_behavior": "Generic telemetry coverage exists, but no isolated committed-baseline regression proves Cursor E provenance for both successful and failed completion.",
  "after_behavior": "The focused test proves Cursor E dispatch identity, harness identity, provider, model, completion status, exit code, and failure diagnostic provenance through the existing role-neutral production path.",
  "self_descriptive_naming": "The test module and cases name Cursor dispatch telemetry provenance and success or failure behavior directly.",
  "obsolete_guidance_disposition": "No guidance is replaced. The revision supersedes version 001's incomplete baseline assumption with an explicit terminal-and-clean pre-start gate.",
  "history_preservation": "The numbered bridge chain and existing production/test history remain unchanged; the implementation may add one new test file only.",
  "baseline": {
    "wi5400": "terminal VERIFIED at bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md",
    "wi5427": "nonterminal REVISED at bridge/gtkb-wi5427-daemon-generation-handoff-005.md",
    "new_test_target": "absent before implementation",
    "production_source": "must be clean at operation time"
  },
  "expected_result": {
    "success_case": "Cursor E provenance is persisted with completed status and no fabricated failure.",
    "failure_case": "Cursor E provenance is persisted with failed status, nonzero exit code, and the actual bounded diagnostic.",
    "production_source": "unchanged"
  },
  "rollback": "Remove only the new governed test file after an independently approved revert; no production source or historical bridge artifact is deleted.",
  "hard_invariants": [
    "No production source mutation.",
    "No implementation begins before WI-5427 is terminal VERIFIED and the exercised production paths are clean relative to HEAD.",
    "No dispatcher configuration, TAFE, runtime, harness registry, eligibility, lease, worker, credential, Git staging, push, deployment, or release mutation.",
    "Existing A, B, C, D, F, and H telemetry behavior remains governed by the same role-neutral implementation."
  ],
  "fail_closed_conditions": [
    "WI-5427 is not terminal VERIFIED.",
    "The new test target already exists or carries foreign changes.",
    "Any exercised production path is dirty relative to committed HEAD.",
    "The test cannot exercise the real production reconciliation API.",
    "Cursor E identity, model, success status, failure status, exit code, or diagnostic is absent or synthetic."
  ],
  "essential_context_preservation": "The test retains dispatch identity, harness identity, provider and model provenance, terminal status, exit code, diagnostic, session linkage, and the existing generic telemetry contract."
}
```

## Finding Response

### P1 - Parallel-session isolation precondition

Accepted. WI-5400 has since reached canonical terminal `VERIFIED`, while
WI-5427 remains nonterminal and owns the dirty daemon/supervisor production
paths. This revision hard-sequences implementation behind WI-5427 terminal
`VERIFIED` and requires exact clean-source evidence before claim acquisition,
not merely before the test command runs. A worker encountering a dirty path
must stop without creating or editing the test target.

### P3 - Stale backlog text and commit type

Accepted. The proposal now states its current bridge state directly and uses
recommended commit type `test`. The MemBase status-detail refresh is deferred
until this revision is filed so the canonical backlog statement can cite the
actual version 003 path rather than predict it.

## Requirement Sufficiency

Existing requirements are sufficient. The version 002 review accepted the
underlying engineering design and specification set. This revision changes
sequencing and evidence requirements only; it adds no production behavior or
new authority.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - defines the role-neutral
  telemetry contract exercised by the focused test.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs the dispatcher completion
  reconciliation path and its trusted provenance.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` -
  require trusted role/session provenance rather than verdict-prose parsing.
- `DCL-DISPATCH-ENVELOPE-RULES-001` and
  `GOV-HARNESS-ONBOARDING-CONTRACT-001` - require Cursor E to use the same
  governed dispatch envelope and telemetry contract as the active fleet.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires no production behavior
  change and preserved fleet-neutral regressions.
- `GOV-WORK-TREE-HYGIENE-001` - requires the terminal-and-clean production
  baseline and isolation of the one new test path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the append-only proposal, verdict,
  report, and verification chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - keep the active PAUTH
  necessary but insufficient and preserve GO, claim, start, report, and
  verification gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - require the exact
  project, work-item, PAUTH, target, and specification linkage carried here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the eventual
  implementation report and independent verdict to map all carried
  requirements to executed evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the defect, revision,
  implementation evidence, and terminal disposition as governed artifacts.
- `GOV-STANDING-BACKLOG-001` - keeps the discovered gap and its current
  sequencing visible in MemBase.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps every target and evidence
  surface inside `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` and `SPEC-AUQ-POLICY-ENGINE-001` -
  preserve the governed Codex write path and existing owner-decision policy.

## Prior Deliberations

- `DELIB-202666260` - approved the role-neutral B/C telemetry predecessor whose
  committed behavior this test exercises for Cursor E.
- `DELIB-202666374`, `DELIB-202666410`, `DELIB-202666551`, and
  `DELIB-202666230` - carried forward from version 001 as the accepted
  fail-closed dispatch and telemetry lineage.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes the
  bounded WI-5369 carrier and governed proposal while preserving every later
  exact gate.
- `bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-002.md` - controlling
  NO-GO requiring explicit production-baseline sequencing.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md` - terminal
  `VERIFIED` evidence for the first predecessor identified by version 002.
- `bridge/gtkb-wi5427-daemon-generation-handoff-005.md` - current `REVISED`
  evidence for the remaining production-baseline predecessor.

The mandatory Deliberation Archive search for WI-5369 telemetry provenance and
the two sequencing predecessors found no more directly controlling owner
decision than the records above.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded
  PAUTH carriers and governed proposals for discovered fleet defects while
  explicitly preserving GO, claim, start, verification, and non-bypass gates.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717` is
  active, includes only WI-5369, allows bridge/metadata/test/governance
  evidence, and authorizes no production source or dispatcher/TAFE mutation.

No new owner decision is required for this test-only revision.

## Proposed Scope

1. Wait until WI-5427 reaches terminal `VERIFIED`.
2. Before acquiring a WI-5369 claim, require clean scoped status for
   `scripts/dispatcher_runtime.py`, `scripts/ensure_dispatcher_daemon.py`,
   `scripts/gtkb_dispatcher_daemon.py`, and the absent-or-clean new test path.
3. After independent GO, acquire the exact WI-5369 claim and schema-v3
   implementation-start packet for only
   `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`.
4. Add success and failure integration coverage through the committed
   production reconciliation entry point. Assert dispatch id, harness id E,
   provider, actual model, terminal status, exit code, diagnostic, and session
   linkage without bypassing the production API boundary.
5. Run the new test, the existing shim telemetry suite, focused runtime
   reconciliation tests, Ruff check/format, and scoped Git hygiene checks.
6. File a post-implementation report carrying the exact pre-start baseline,
   commands, results, and spec-to-test mapping. Independent LO retains
   terminal verification authority.

## Out Of Scope

- Any edit to production source, including the three exercised production
  paths.
- Dispatcher or TAFE configuration or runtime mutation.
- Harness registry, identity, role, eligibility, routing, worker, lease,
  credential, external-system, Git staging/commit/push/history, deployment, or
  release mutation.
- Runtime telemetry files, scratch paths, retired evidence directories, or
  copied projections as bridge evidence.
- Any attempt to implement while WI-5427 remains nonterminal or an exercised
  production path is dirty.

## Cross-Harness Disposition

- A, B, C, D, F, and H: no production behavior change; existing
  fleet-neutral telemetry regressions remain required.
- E: direct success and failure coverage is added through the same committed
  role-neutral reconciliation path.

## Specification-Derived Verification Plan

| Governing requirement | Executed evidence required in implementation report | Expected result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001`; version 002 NO-GO | Exact scoped status before claim for the new test and three exercised production paths; canonical WI-5427 latest-file read | WI-5427 is terminal VERIFIED; new target is absent or clean; production paths are clean relative to HEAD. |
| Active PAUTH; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Exact `go_implementation` claim and schema-v3 start packet after the baseline check | Packet target set contains only the new test path; no production source authority is granted. |
| `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | New Cursor E success/failure integration tests plus existing shim telemetry and focused reconciliation suites | Trusted Cursor E identity/model/status/error provenance is persisted through the production path. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`; `DCL-DISPATCH-ENVELOPE-RULES-001` | Test assertions for matching trusted session evidence and fail-closed missing/conflicting provenance | No verdict-prose inference or synthetic provenance is accepted. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Fleet-neutral existing tests and proof the production source hashes remain unchanged | Cursor E gains coverage without a Cursor-specific production branch or regression to A/B/C/D/F/H. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate/live applicability and clause preflights plus append-only report filing | No missing required/advisory specs or blocking clause gaps; report is the next numbered file. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report carries this mapping and exact command outputs; independent verdict reruns or independently validates them | Every carried requirement has executed evidence before VERIFIED. |
| Root and artifact governance family | Scoped path resolution, bridge chain, MemBase WI, and DA citations | All evidence is in-root and canonical; no scratch or retired evidence dependency exists. |

## Acceptance Criteria

- WI-5427 is terminal `VERIFIED` before claim acquisition.
- The new test target is absent or clean, and all three exercised production
  paths are clean relative to committed HEAD immediately before claim
  acquisition.
- The exact start packet authorizes only
  `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`.
- The new test exercises the real committed production reconciliation entry
  point for Cursor E success and failure.
- The focused test, existing shim telemetry suite, and focused runtime
  reconciliation tests pass.
- Ruff check and format check pass for the new test.
- Production source hashes remain unchanged.
- No dispatcher, TAFE, runtime, harness, eligibility, worker, lease,
  credential, Git, external-system, deployment, or release state changes.

## Risk And Rollback

The principal risk is testing moving production bytes and mistaking a
working-tree candidate for verified behavior. The terminal-and-clean
precondition now fails closed before claim acquisition, and the implementation
packet cannot authorize production source.

Rollback is a separately governed removal of only the new test file. Bridge,
MemBase, and Deliberation Archive history remains append-only and is never
deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`

## Recommended Commit Type

`test`

## Pre-Filing Preflight Subsection

Candidate checks against this exact completed draft produced:

- Applicability packet hash:
  `sha256:acb67512575bfcce73c699071cf0a6cdf24cd78e7243d22ce8665313cf31cc88`.
- `preflight_passed: true`.
- `missing_required_specs: []`.
- `missing_advisory_specs: []`.
- `blocking_errors: []`.
- Mandatory clause preflight: 5 clauses evaluated, 4 `must_apply`, 1
  `may_apply`, zero evidence gaps in `must_apply`, zero blocking gaps, exit 0.

The related-work collision checker is also run against the completed draft.
The filed version is rechecked through the same applicability, clause, and
relationship-classification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
