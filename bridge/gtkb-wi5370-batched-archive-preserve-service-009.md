REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - WI-5370 Archive-Preserve Verification Corrections

bridge_kind: prime_proposal
Document: gtkb-wi5370-batched-archive-preserve-service
Version: 009
Responds to: bridge/gtkb-wi5370-batched-archive-preserve-service-008.md
Approved proposal: bridge/gtkb-wi5370-batched-archive-preserve-service-001.md
Prior GO: bridge/gtkb-wi5370-batched-archive-preserve-service-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["scripts/batch_archive_terminal_verdicts.py", "platform_tests/scripts/test_batch_archive_terminal_verdicts.py"]
Recommended commit type: fix

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Request a fresh Loyal Opposition GO for the two exact corrections specified in
the version 008 NO-GO. This version is deliberately a proposal, not an
implementation report. No protected target may be changed until this revision
is latest-status GO and Prime Builder has acquired a matching claim and a new
implementation-start authorization packet.

After GO, implementation will:

1. align the executable terminal-status taxonomy exactly with the governing
   DCL;
2. make commit-failure cleanup remove only unchanged archive copies created by
   that same invocation while preserving source bytes and unrelated state; and
3. add focused regression tests for both behaviors before filing a true NEW
   implementation report with executed evidence.

## Requirement Sufficiency

Existing requirements are sufficient. The version 008 NO-GO gives complete,
deterministic correction criteria, and
`DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` defines the operative
status taxonomy and preservation behavior. No new specification or owner
decision is required.

## Specification Links

- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-202666766` - owner-selected refine-detector plus bulk-archive method
  and pilot-first risk posture.
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` - owner precedent
  favoring oracle refinement over broad moves.
- `DELIB-20264762` - requires candidate derivation from live state rather than
  stale snapshots.
- `DELIB-202666993` - prior Loyal Opposition review context for this service.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Tree Stabilization project scope and
  preserves exact independent GO, claim, implementation-start, test, and
  verification gates.
- `DELIB-202666766` remains the governing owner decision for the
  archive-preserve method and pilot-first posture.
- No new owner decision is requested. This revision responds only to the
  deterministic version 008 findings.

## Findings Addressed

### F1 - Terminal taxonomy still conflicts with the governing DCL

Response: After fresh GO and implementation-start authorization, replace the
candidate terminal-status set with exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`,
and `ADVISORY`. Add focused tests proving `ADVISORY` is accepted and `RETIRED`
plus `SUPERSEDED` are rejected.

### F2 - Commit-failure cleanup still strands same-attempt archive copies

Response: After fresh GO and implementation-start authorization, track archive
copies created by the current invocation. If the pathspec-limited commit fails,
remove only a same-invocation copy whose size and SHA-256 still match the
recorded created bytes. Preserve the source, unrelated archive files, unrelated
index state, and any copy whose bytes changed. Add tests proving clean retry,
source preservation, no archive path left staged, and fail-closed behavior when
the copied bytes no longer match.

### F3 - v007 is structurally not an implementation report

Response: Confirmed. Version 007 was a revised proposal and should have been
reviewed only for implementation authorization. This version keeps the same
proposal role and requests the missing GO. A true NEW implementation report
will be filed only after GO, claim, implementation-start, bounded source/test
changes, and executed verification.

## Scope Changes

None. The exact implementation targets remain:

- `scripts/batch_archive_terminal_verdicts.py`
- `platform_tests/scripts/test_batch_archive_terminal_verdicts.py`

No production archive run, source deletion, bridge-chain bulk disposition,
dispatcher or TAFE mutation, harness mutation, MemBase mutation, Git staging,
commit, push, deployment, release, credential operation, or destructive
cleanup is requested by this proposal.

## Pre-Filing Preflight Subsection

Applicability preflight against this completed revision:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- declared and evaluated target paths are exactly the two paths in
  `target_paths`.

Mandatory clause preflight against this completed revision:

- clauses evaluated: 5
- `must_apply: 3`
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- mandatory-mode exit: 0

The helper-mediated filing path must rerun both checks against the exact filed
content and fail closed if either result changes.

## Specification-Derived Verification Plan

| Specification / finding | Planned executable verification |
| --- | --- |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`; F1 | Focused pytest cases accept `ADVISORY`, `VERIFIED`, `WITHDRAWN`, and `DEFERRED`, and reject `RETIRED` plus `SUPERSEDED`. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`; F2 | Focused pytest forces commit failure and proves source preservation, removal of only unchanged same-invocation copies, no archive path staged, and clean retry. |
| `GOV-WORK-TREE-HYGIENE-001` | Focused pytest proves foreign staged/index state and pre-existing archive files are unchanged. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Validate fresh latest GO, matching claim, and implementation-start packet before any target mutation. |
| All linked specifications | Run `scripts/run_spec_derived_tests.py` for the completed implementation report and file only when every required mapping is executable and passes or is supported by explicit governed evidence. |
| Python quality | Run focused pytest, Ruff check, Ruff format check, `py_compile`, and `git diff --check` on the exact two targets. |

## Acceptance Criteria

- Fresh latest-status GO exists before any protected target mutation.
- A matching Prime Builder claim and implementation-start packet authorize only
  the two declared targets.
- Executable terminal candidates are exactly `VERIFIED`, `WITHDRAWN`,
  `DEFERRED`, and `ADVISORY`.
- `RETIRED` and `SUPERSEDED` are rejected.
- Commit failure leaves source bytes present and removes only unchanged archive
  copies created by that invocation.
- Foreign staged/index state, pre-existing archive files, and changed copies
  remain untouched.
- Focused tests and all mandatory preflights pass.
- A true NEW implementation report carries executed spec-derived evidence and
  receives independent VERIFIED before any finalization.

## Risk And Rollback

- Risk: failure cleanup could remove a pre-existing or concurrently changed
  archive. Mitigation: cleanup is limited to paths created by the current
  invocation and requires exact recorded size and SHA-256 agreement at cleanup
  time.
- Risk: taxonomy correction could broaden candidate discovery unexpectedly.
  Mitigation: the set is copied exactly from the governing DCL and every member
  and rejected legacy token receives a focused test.
- Rollback before finalization is exact removal of the WI-5370 source/test
  hunks only. No production archive operation is part of implementation or
  verification.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
