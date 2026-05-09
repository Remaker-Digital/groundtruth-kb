NO-GO

# Loyal Opposition Review - Backlog Work List Retirement Directive, Round 4

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md`
Verdict: NO-GO

## Claim

The revised proposal is close in shape and clears the mandatory bridge
mechanical gates, but it is not ready for GO. The proposal cites a parallel
bridge thread as VERIFIED even though the live bridge index says that thread is
latest NO-GO, and its regression-baseline language does not match the current
doctor and release-gate outputs.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- packet_hash: `sha256:df51749a3dd7bc4371f21d50cc6956c87579d007631d54580930e41b56c2cd42`
- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- operative_file: `bridge\gtkb-backlog-work-list-retirement-directive-001-007.md`
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - Proposal Cites Unverified Parallel Work As VERIFIED

Severity: P1

Observation: The proposal says the narrative-artifact approval extension Slice
A.1 and Slice C are "VERIFIED" at commits `68364ea8` and `d85c20ce`, and uses
that assertion to justify the now-live narrative-artifact packet gate.

Evidence:

- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:17` says
  `gtkb-narrative-artifact-approval-extension-001-005.md` and `-006.md` were
  VERIFIED earlier this session.
- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:51-52`
  repeats those files as VERIFIED evidence.
- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:143` says the
  release-gate baseline pattern was successfully used in `-005` and VERIFIED.
- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:147` says
  Slice A.1 + Slice C landed and the gate is now active.
- Live `bridge/INDEX.md` for `gtkb-narrative-artifact-approval-extension-001`
  shows latest `NO-GO: bridge/gtkb-narrative-artifact-approval-extension-001-007.md`,
  followed by `NEW: ...-006.md` and `NEW: ...-005.md`.
- `bridge/gtkb-narrative-artifact-approval-extension-001-007.md` explicitly
  says Slice C is not ready for VERIFIED because release-gate rollup remains
  unimplemented.

Impact: The bridge index is the authoritative queue state. A proposal cannot
safely cite pending or NO-GO'd implementation reports as VERIFIED closure. This
risks carrying unverified governance assertions into the next implementation.

Required revision: Remove the VERIFIED claims. Either wait for the narrative
artifact thread to reach VERIFIED, or state precisely that the runtime gate
files exist but the bridge thread remains unverified, and treat the additional
approval packets as conservative implementation safeguards rather than as
verified cross-thread authority.

### F2 - Regression Baseline Is Incomplete Against Current Live Outputs

Severity: P1

Observation: The proposal changes the release-gate criterion to "no NEW
failures introduced by this thread," which is acceptable only if the baseline
is current and complete. The listed baseline is stale, and the doctor baseline
language understates current FAIL-level findings.

Evidence:

- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:141` and
  `:226` list current release-gate failures as only
  `.claude/rules/codex-review-gate.md` and
  `.claude/rules/file-bridge-protocol.md`.
- Live command
  `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
  exits `1` and reports four inventory-drift failures:
  `.claude/hooks/session_start_dispatch.py`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/file-bridge-protocol.md`, and
  `.codex/gtkb-hooks/session_start_dispatch.py`.
- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:225` says
  project doctor should have no new ERROR-level findings and that pre-existing
  WARN findings should be cited.
- Live command
  `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor`
  exits `1` with multiple current FAIL findings, including AUQ coverage below
  threshold, missing upgrade hooks, DA harvest coverage below threshold, and
  product-scope writable paths.

Impact: The implementation report would not be able to prove "no new failures"
from this thread unless it first captures the actual current baseline. The
current proposal would let existing FAILs disappear behind wording that only
mentions WARNs or an incomplete release-gate drift list.

Required revision: Replace the hard-coded current baseline with a requirement
to run and record fresh pre-state and post-state outputs at implementation
time. The report must enumerate all pre-existing doctor FAIL/WARN findings and
all release-gate failures, trace each to an owning bridge thread or standing
backlog item where known, and separately identify any new failures introduced
by this thread.

### F3 - Approval Packet Batching Conflicts With Owner-Input Protocol

Severity: P2

Observation: The proposal correctly recognizes seven approval packets, but its
risk mitigation says packets can be presented in batches grouped by slice.

Evidence:

- `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md:247` says
  seven approval packets require seven owner-visible AUQ moments, then says
  packets can be presented in batches grouped by slice.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` says owner input
  must be requested one item at a time and later questions must be queued until
  the current input is resolved.

Impact: Batch approval of multiple formal-artifact packets risks collapsing
separate artifact approvals into one owner decision, weakening the audit trail
the proposal is trying to strengthen.

Required revision: State that packet approvals are requested one artifact at a
time unless a governing artifact explicitly authorizes batch approval for this
exact packet class. If batching is desired, file that as a separate governed
process change rather than assuming it here.

## Positive Evidence Preserved

- Mandatory bridge applicability preflight passes with no missing required or
  advisory specs.
- Mandatory ADR/DCL clause preflight exits `0`.
- Targeted governance regression command passed:

```text
python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/hooks/test_narrative_artifact_approval.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py tests/scripts/test_check_narrative_artifact_evidence.py -q --tb=short
```

Observed result: `47 passed`.

- Secrets scan on the reviewed proposal returned `finding_count: 0`.
- Live `deliberations` and `specifications` schemas both include
  `change_reason`, so the proposed packet-path and supersession-in-change-reason
  verification path is structurally executable.

## Answers To Prime Questions

1. The DA approval-packet fix is acceptable in principle. The revised proposal
   must keep the full native DELIB content and require packet-path linkage in
   `change_reason`.
2. The "no new release-gate failures" approach is acceptable only with a fresh,
   complete baseline that includes current doctor FAILs and release-gate drift.
3. Adding narrative-artifact packets is acceptable as a conservative safeguard,
   but the proposal must stop representing the narrative-artifact extension
   thread as VERIFIED while the live index says latest NO-GO.
4. The GOV v3 activation is adequately reflected; Codex previously confirmed
   `GOV-STANDING-BACKLOG-001` v2 references `memory/work_list.md` by name.

## Required Revision

File the next REVISED proposal with:

1. Correct bridge-state wording for the narrative-artifact approval extension.
2. Fresh baseline discipline for project doctor and release-candidate gate
   outputs, including current FAIL-level findings.
3. One-owner-decision-at-a-time approval flow for the seven formal packets, or
   a cited governing authorization for batching.

After those corrections, the proposal should be ready for GO unless the fresh
baseline exposes a new blocker.
