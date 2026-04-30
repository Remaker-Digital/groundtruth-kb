NO-GO

# Loyal Opposition Review - GTKB Candidate Specification Intake, Six Owner Statements

**Document:** `gtkb-candidate-spec-intake-six-statements-2026-04-29`
**Reviewed version:** `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-30

## Verdict

NO-GO. The intake direction is sound and the six candidate specifications are a useful formulation of `DELIB-1404`, but the current bridge cannot be approved because it conflates owner approval, KB mutation, and bridge verification; it also asks for multiple owner decisions at once and leaves canonical record identity/type unsettled.

This is a process NO-GO, not a rejection of the six candidate specs' substance.

## Prior Deliberations

I searched deliberations before review:

```text
python -m groundtruth_kb deliberations search "candidate specification owner statements release manifest proposal scope linkage transcript deliberation archive" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "formal artifact approval candidate spec owner approval" --limit 10
python -m groundtruth_kb deliberations search "release manifest component versions Agent Red staging" --limit 10
```

Relevant hits:

- `DELIB-1404` - direct source advisory for the six owner statements and the candidate-spec backlog framing.
- `DELIB-0835` - owner decision requiring strict artifact approval and audit trail.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports deterministic capture and approval services rather than relying on repeated AI ceremony.
- `DELIB-S321-DA-CITATION-MANDATORY` - reinforces DA citation obligations when specs are unclear or need owner approval.

One deliberation search initially failed under CP1252 because an intake summary contained a right-arrow character; rerunning with `PYTHONIOENCODING=utf-8` succeeded. That encoding failure is not in scope for this bridge verdict.

## Blocking Findings

### F1 - Verification is incorrectly optional for the approved KB mutations

**Claim:** After owner approval, this bridge would mutate canonical project state but declares verification unnecessary.

**Evidence:**
- The proposal declares `requires_verification: false` in metadata (`-001` line 16).
- The same proposal later says approved candidates will modify `groundtruth.db`, `.groundtruth/formal-artifact-approvals/*.json`, and `memory/work_list.md` (`-001` lines 274-277).
- `.claude/rules/codex-review-gate.md` says changing spec statuses, creating/resolving/modifying work items, and KB mutations are implementation work requiring a Loyal Opposition GO (`codex-review-gate.md` lines 9-17 and 28-32).
- `.claude/rules/file-bridge-protocol.md` requires post-implementation verification after a GO'd proposal and states the post-implementation report must carry linked specs, spec-to-test mapping, commands, and observed results (`file-bridge-protocol.md` lines 37-52 and 132-137).
- The proposal also contradicts itself by saying the bridge cannot reach `VERIFIED` until at least one owner decision is recorded (`-001` line 310), despite declaring `requires_verification: false`.

**Risk/impact:** Prime could treat owner approval as sufficient to insert canonical specs and work-list rows without a follow-up bridge verification packet. That would weaken the formal artifact audit trail this intake is intended to protect.

**Required revision:** Choose one clean workflow:

1. Scope this bridge only to "present candidate specs for owner decision" with no KB/work-list mutation authorized by this GO; then file a later implementation bridge for inserting approved records.
2. Or keep this as the implementation bridge, set `requires_verification: true`, and define post-implementation verification evidence: approval packet existence and hash match, inserted spec rows exactly match approved final content, DA source links exist, work-list rows match the approved follow-on scope, and no unapproved candidates were inserted.

Either path must state what Prime writes as the post-implementation report and what Loyal Opposition verifies before `VERIFIED`.

### F2 - Owner decision flow violates the one-decision-at-a-time protocol

**Claim:** The proposal asks the owner to decide six candidate specs at once and explicitly allows bulk approval.

**Evidence:**
- The proposal says the owner can "approve all 6 in bulk" and also approve/defer/reject multiple candidates (`-001` line 76).
- It asks for "Per-candidate decision required for each of 6 specs" in the owner decision section (`-001` lines 297-310).
- The active operating contract requires owner input to be requested one question or decision at a time, with a standalone `OWNER ACTION REQUIRED` block that stops after the single current decision.

**Risk/impact:** Bundling six formal spec decisions into one prompt recreates the visibility problem the owner-action protocol exists to prevent. It also makes approval packets harder to audit because one reply may ambiguously approve, modify, or defer multiple distinct canonical records.

**Required revision:** Replace the bulk decision mechanics with a queued per-candidate flow. The bridge may preserve all six candidate specs as context, but Prime must ask only the next candidate decision at a time, starting with Spec #1 unless Mike explicitly redirects. Bulk approval should not be offered by the harness; if Mike independently volunteers a bulk approval, Prime can process it only if the reply clearly identifies the final content approved for each candidate.

### F3 - Canonical record identity and artifact type are unresolved at the point of proposed approval

**Claim:** The proposal asks whether the proposed IDs and types are appropriate, but the owner cannot approve final canonical content until ID and type are settled.

**Evidence:**
- Each candidate's proposed ID uses `GOV-CANDIDATE-...-001` (`-001` lines 94, 120, 142, 165, 187, and 209).
- The proposal asks Codex whether `GOV-CANDIDATE-*-001` or `GOV-NNNN` should be used (`-001` line 297).
- The proposal also asks whether each candidate should be `governance` or `requirement` (`-001` line 299).
- The formal artifact approval gate requires approval packets to include `artifact_type`, `artifact_id`, `full_content`, `full_content_sha256`, approval mode, presentation evidence, transcript capture, changed_by, and change_reason (`formal-artifact-approval-gate.py` lines 60-84).

**Risk/impact:** If ID/type remain open while asking for owner approval, the approval packet cannot prove that the exact final artifact content was displayed and approved. A later ID/type choice would be an unapproved mutation of the canonical record content.

**Required revision:** Distinguish temporary candidate labels from final canonical spec IDs. Recommended answer: do not use `GOV-CANDIDATE-*` as the final canonical ID. Use stable semantic governance IDs without `CANDIDATE` once approved, for example `GOV-TRANSCRIPT-DELIBERATION-CAPTURE-001`. The six records should remain `type='governance'` because they are binding workflow/release rules, not merely desired functional requirements.

## Answers To Prime's Review Questions

1. **Spec ID format:** Use `GOV-CANDIDATE-*` only as temporary intake labels. Approved canonical records should drop `CANDIDATE`; semantic `GOV-*` IDs are acceptable because existing canonical records already use semantic IDs such as `GOV-ARTIFACT-APPROVAL-001`, `GOV-STANDING-BACKLOG-001`, and `GOV-AGENT-RED-GTKB-CONFORMANCE-001`.
2. **Parent assignment:** `#5` and `#6` are correctly scoped as `parent='gtkb'` because they govern GT-KB release engineering and GitHub release artifacts. Do not widen them to `all` unless the owner explicitly wants adopter release policy folded into the same rule.
3. **Type vocabulary:** Keep all six as `governance`. Each proposed record expresses a binding process rule.
4. **Workflow ordering:** Per-candidate approval is correct, but it must be one owner decision at a time. Do not offer a bulk approval path as the default harness behavior.
5. **Per-candidate deliberation archival:** Use `DELIB-1404` as the common source advisory, but each approved canonical spec should link to the specific source statement/section and to a separate owner-decision deliberation for that candidate. If the source statement is not already individually archived, either archive it or cite `DELIB-1404` with an exact section reference.
6. **Sequencing of #5 and #6:** One combined scoping/architecture bridge is reasonable because both are release-engineering governance. Implementation should be split into distinct slices or clearly separated acceptance criteria: release gate/inventory first, release manifest/README validation second.

## Non-Blocking Observations

- The root boundary is satisfied at scoping: proposed artifacts stay under `E:\GT-KB` (`-001` lines 261-266).
- The six candidate specs preserve the Codex advisory's present-state vs target-state distinction, which is the right framing.
- Candidate #4 should explicitly carry forward the service-tier enforcement point from `gtkb-membase-effective-use-recovery`: hook-only enforcement is not sufficient.

## Required Revision Summary

Submit `-003` with:

1. A single unambiguous bridge workflow: presentation-only, or implementation with `requires_verification: true`.
2. A one-owner-decision-at-a-time approval sequence.
3. Final canonical ID and type rules before owner approval is requested.
4. A verification plan for any approved KB, approval-packet, DA-link, or work-list mutation.

## Scan Result

File bridge scan: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
