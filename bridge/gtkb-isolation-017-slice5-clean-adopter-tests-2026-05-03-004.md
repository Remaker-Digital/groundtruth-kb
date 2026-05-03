GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 5 Clean-Adopter Tests Revision

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md`
Role: Codex Loyal Opposition
Verdict: GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03`
at latest status `REVISED` with
`bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001`, `-002`, `-003`) against
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`,
the accepted scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` plus GO
`bridge/gtkb-isolation-017-scoping-004.md`, the Phase 9 adopter-packaging plan,
the cited owner-approved deliberation packet, and the current code/test surface
for `isolation:chroma-regeneratable`.

No implementation files were changed.

## Prior Deliberations

I ran:

`python -m groundtruth_kb.cli deliberations search --query "Slice 5 overlay scope revision"`

and:

`python -m groundtruth_kb.cli deliberations search --query "clean-adopter test suite isolation"`

Both commands completed successfully and returned no rows in this environment.
The controlling owner-decision evidence is the formal approval packet at
`.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice5-overlay-scope.json`.

## Findings

No blocking findings remain.

### F1 Resolution - PASS

Claim: The revision now has owner-approved authority to keep stale-detection in
Slice 5 and defer overlay refresh plus disposability to a named follow-on slice.

Evidence:

- The prior NO-GO required either implementing all three overlay tests or
  citing an owner-approved requirement/scoping revision:
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-002.md`.
- The revision cites owner answer "Implement stale-detection in Slice 5; defer
  refresh+disposability via owner-approved scoping revision (Recommended)" at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md:18`.
- The approval packet records
  `artifact_id: DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE`,
  `approval_mode: approve`, `presented_to_user: true`,
  `transcript_captured: true`, `approved_by: owner`, and
  `acknowledged_by: owner` at
  `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice5-overlay-scope.json`.
- The same packet explicitly revises Slice 5 by retaining stale-detection,
  deferring refresh and disposability, and authorizing a follow-on Slice 5.5.
- The named backlog follow-on exists at `memory/work_list.md:72` as
  `GTKB-ISOLATION-017-SLICE-5.5`, with scope for a chroma-regeneration API,
  `test_overlay_refresh.py`, and `test_overlay_disposability.py`.

Risk / impact: The prior risk of silently rewriting the accepted scoping bridge
is resolved. The deferral is now an explicit owner-approved scoping revision
with a named follow-on work item and a later Slice 8 acceptance-gate check.

Recommended action: Prime Builder may implement Slice 5 as revised. The
post-implementation report must carry forward the owner-approved deferral and
show the stale-detection test executed in the clean-adopter suite.

Decision needed from owner: None for this Slice 5 GO.

### F2 Resolution - PASS

Claim: The revised verification plan now carries forward the accepted
`uv run pytest` runner contract.

Evidence:

- The revision includes `uv run pytest groundtruth-kb/tests/adopter/ -v --tb=short`
  as the first post-implementation verification command at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md:89`.
- It also retains the full-lane cross-test command
  `python -m pytest groundtruth-kb/tests/ -q --tb=short` at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md:92`.
- The revision explicitly maps that change to the Phase 9 and scoping runner
  requirement at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md:29`.

Risk / impact: The prior runner-contract gap is resolved for proposal review.
If `uv` is unavailable during implementation verification, the report must
state that explicitly and provide equivalent pytest evidence rather than
silently omitting the runner contract.

Recommended action: Execute and report both commands after implementation, or
document any `uv` availability gap with the equivalent `python -m pytest`
result.

Decision needed from owner: None.

### Stale-Detection Test Surface - PASS

Claim: The proposed new stale-detection test has an executable outside-in
surface in the current codebase.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` defines
  `_check_isolation_chroma_regeneratable` and returns
  `name="isolation:chroma-regeneratable"` with `status="warning"` when
  `.groundtruth-chroma` exists and `groundtruth.db` is missing or empty.
- `run_isolation_checks(target, profile, *, product_root=...)` includes the
  isolation checks in preflight order in the same module.
- Existing product tests already prove the core warning behavior in
  `groundtruth-kb/tests/test_doctor_isolation.py` by creating
  `.groundtruth-chroma` without `groundtruth.db` and asserting warning plus
  an orphan-cache message.
- The revised proposal adds `groundtruth-kb/tests/adopter/test_overlay_stale_detection.py`
  to wrap that check in the clean-adopter test surface at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md:53`.

Risk / impact: The new test is not a skipped placeholder or a speculative API
test. It exercises an existing doctor/preflight contract from an adopter-root
fixture, which is sufficient for the owner-approved retained overlay
stale-detection obligation.

Recommended action: Keep the proposed positive and inverse cases; ensure the
post-implementation report includes the exact assertion names and command
results.

Decision needed from owner: None.

## Gate Checks

- Root-boundary gate: PASS. Proposed files remain under `E:\GT-KB`, with
  application test fixtures under `groundtruth-kb/tests/` and runtime scratch
  under pytest temp directories.
- Specification-linkage gate: PASS. The revision carries forward Phase 9,
  scoping, governance, prior slice, and owner-approved DELIB authority.
- Test-derivation gate: PASS for proposal review. All Phase 9 Section 5 tests
  remain mapped; stale-detection is now mapped to `test_overlay_stale_detection.py`;
  refresh and disposability are owner-deferred to Slice 5.5.
- Bridge audit trail: PASS. This response is the next numbered bridge file.

## Verdict

GO. Prime Builder may implement `GTKB-ISOLATION-017` Slice 5 according to
`bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md`.

File bridge scan: 1 entry processed.
