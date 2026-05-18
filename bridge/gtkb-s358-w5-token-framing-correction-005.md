NEW

# Implementation Report - W5 Token-Framing-Distortion Correction (GTKB-GOVERNANCE-CORRECTION-S358-W5)

bridge_kind: implementation_report
Document: gtkb-s358-w5-token-framing-correction
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3370

target_paths: ["CLAUDE.md", ".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md", ".groundtruth/formal-artifact-approvals/*-claude-md.json", ".groundtruth/formal-artifact-approvals/*-claude-rules-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/*-claude-rules-canonical-terminology-md.json"]

## Summary

This is the post-implementation report for the W5 token-framing-distortion correction. It implements the proposal at `bridge/gtkb-s358-w5-token-framing-correction-003.md` (REVISED), which received Codex GO at `-004`.

IP-1, IP-2, and IP-3 are all landed. Six distorted poller-history passages across the three auto-loaded reasoning-shaping rule files now state the retired-poller defect as its mechanism - blind, activity-independent polling - rather than as token volume. Every incident fact is retained: the roughly tenfold spawn increase, the fixed three-minute interval, the 173 Claude and 92 Codex spawn counts, and the per-spawn token figure. No do-not-re-enable mandate, no manual-scan fallback text, and no cross-harness-trigger operating-mode text was removed or weakened.

Each of the three protected-file corrections carries an owner-approved narrative-artifact-approval packet, and the staged narrative-artifact evidence check passes with the three protected files cleared. The implementation-start authorization packet for this work is `sha256:1e5a071d740623348fbede0647e0f1155c7a28e46c7010738e4ce4a4e8875d10`, derived from the live `GO` at `-004`.

## In-Root Placement Evidence

All target paths are in-root under the GT-KB project root: `CLAUDE.md` at the root, two rule files under the rules directory, and three approval-packet globs under the formal-artifact-approvals directory. This report file resides under the bridge directory. No target path is outside the GT-KB project root, and no application path was touched.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this report is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries the complete, relevance-closed Specification Links section forward from the GO'd proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-test mapping with executed verification evidence and the exact commands run.
- GOV-ARTIFACT-APPROVAL-001 - the three target files are protected narrative artifacts; each correction is gated by a narrative-artifact-approval packet presented to and approved by the owner before the Write.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to this narrative-artifact correction.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the narrative-artifact-approval gate hook and the universal pre-commit evidence floor enforce the packet requirement on the protected-file Writes.
- config/governance/narrative-artifact-approval.toml - the registry that constrains protected-path matching, the approval-packet directory and filename pattern, and the packet schema for the three narrative-artifact corrections.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME, WI-3370, the proposal, the approval packets, and this report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the deliberation, work item, proposal, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3370 moves through open, in-progress, and verified lifecycle states.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root; no application path was touched.

## Prior Deliberations

A Deliberation Archive body-search was performed for the token-framing topic during proposal authoring. Relevant records:

- DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME - the owner-decision deliberation (S358, owner_conversation) that authorizes this correction and states the canonical waste-not-volume framing. This implementation realizes it.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this correction aligns the rule files to: token cost as a recurring tax that pays no marginal information dividend; repetitive AI work is the defect.
- DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION and DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION - the smart-poller clarification deliberations; they record the OLD-poller halt as implementation-specific and the spawn-to-notify objective. They are append-only design-reasoning records and are not rewritten by this work.

No prior deliberation rejected or already addressed this framing correction.

## Owner Decisions / Input

- 2026-05-18, S358: the owner clarified that the GT-KB token concern is waste - pointless repetition, blind or activity-independent work, or work a deterministic implementation should do - not raw token volume, and directed removing the lingering distortion from the artifacts. Captured as DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME, owner-approved as drafted via AskUserQuestion.
- 2026-05-18, S358: the owner chose, via AskUserQuestion, to fold this correction into PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 as a fifth workstream and authorized the one-time extension of the project authorization to cover WI-3370.
- The three per-file narrative-artifact-approval packets were created and owner-approved before the protected-file Writes. They are at `.groundtruth/formal-artifact-approvals/2026-05-18-claude-md.json`, `.groundtruth/formal-artifact-approvals/2026-05-18-claude-rules-bridge-essential-md.json`, and `.groundtruth/formal-artifact-approvals/2026-05-18-claude-rules-canonical-terminology-md.json`. Each carries `presented_to_user: true`, `transcript_captured: true`, `approval_mode: approve`, and a `full_content_sha256` confirmed by the staged narrative-artifact evidence check to match the staged blob.

## Clause Scope Clarification (Not a Bulk Operation)

This work is not a bulk standing-backlog operation. It is a three-file framing correction tracked by exactly one work item, WI-3370, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item inventory, bulk transition, or backlog cleanup was performed. The report references the phrase "work item" and the word "backlog" only to identify WI-3370 and to describe the poller history; it performs no bulk operation. Each artifact correction is an individual formal-artifact change carrying its own narrative-artifact-approval packet.

## Bridge INDEX Update Evidence

A `NEW` entry for `gtkb-s358-w5-token-framing-correction` pointing at this `-005` report file is inserted at the top of that document's version list in the bridge index, above the `GO: -004`, `REVISED: -003`, `NO-GO: -002`, and `NEW: -001` lines. No prior bridge file and no prior index entry is deleted or rewritten; `-001` through `-004` remain on disk and in the index as the append-only audit trail.

## Implementation Detail

The corrections were applied verbatim per the GO'd proposal's IP-1, IP-2, and IP-3 scope. The full diff is reproducible with:

`git diff -- CLAUDE.md .claude/rules/bridge-essential.md .claude/rules/canonical-terminology.md`

Diff stat:

```text
 .claude/rules/bridge-essential.md      | 26 +++++++++++++++-----------
 .claude/rules/canonical-terminology.md |  7 ++++---
 CLAUDE.md                              |  8 ++++----
 3 files changed, 23 insertions(+), 18 deletions(-)
```

### IP-1 - CLAUDE.md Bridge-Polling-Halted rationale

Before:

> Rationale: the OS Claude poller activation around 2026-04-23 drove a ~10x session token-cost regression (~12.5M tokens/day from background spawns alone). Manual scans recover the cost; the bridge protocol itself is unaffected.

After:

> Rationale: the OS Claude poller (activated ~2026-04-23) fired on a fixed interval regardless of bridge activity - a ~10x spawn jump (~12.5M tokens/day) mostly doing work without information, not token volume. The bridge protocol itself is unaffected.

CLAUDE.md is line-neutral: four lines removed, four added (`8 ++++----`). The file remains 301 lines, unchanged from before this correction.

### IP-2 - bridge-essential.md poller-lesson framing (three spots)

Spot 1, Operational Mode lead-in. Before: "former token-heavy implementation". After: "former blind-polling implementation".

Spot 2, Operational Mode rationale. Before:

> The 2026-04-25 OS-poller halt was made after the former OS Claude poller (activated ~2026-04-23) drove a ~10x session token-cost regression: 173 Claude capped-spawns/day at peak, plus 92 Codex spawns/day, each costing ~50k tokens.

After:

> The 2026-04-25 OS-poller halt was made after the former OS Claude poller (activated ~2026-04-23) was found to fire on a fixed interval regardless of bridge activity: 173 Claude capped-spawns/day at peak plus 92 Codex spawns/day, the great majority doing work without information. The defect was blind repetition, not the ~50k tokens each spawn consumed.

Spot 3, the S308 Incident History entry - the core fix. Before:

> Former OS Claude poller activation drove a ~10x token-cost regression (~12.5M tokens/day from background spawns alone). [...] Lesson: token cost is a first-class operational metric; automation that scales faster than the work it serves becomes a regression even when it works correctly.

After:

> Former OS Claude poller activation produced ~12.5M tokens/day of background spawns (a ~10x jump), most doing work without information because the poller fired on a fixed interval regardless of bridge activity. [...] Lesson: blind, activity-independent automation - work repeated whether or not there is anything to do - is the defect; automation must be activity-driven and deterministic. The waste was work without information, not token volume.

### IP-3 - canonical-terminology.md poller entries (two spots)

Spot 1, the cross-harness-event-driven-trigger glossary entry. Before: retired `OS poller` described as a "token-heavy scheduled-task class". After: "blind-polling scheduled-task class".

Spot 2, the "OS poller" glossary entry. Before:

> All members of this class were halted 2026-04-25 per owner directive after a 10x session token-cost regression and must not be re-enabled as a substitute for the smart poller.

After:

> All members of this class were halted 2026-04-25 per owner directive because they polled blindly - waking the harnesses on a fixed interval regardless of bridge activity - and must not be re-enabled as a substitute for the smart poller.

## Spec-to-Test Mapping with Executed Evidence

| Specification | Behavior verified | Verification procedure | Result |
|---|---|---|---|
| DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME | No poller-retirement passage in the three target files presents token volume as the lesson; each names the blind, activity-independent mechanism | Repo-wide grep over `*.md` for `token-cost regression`, `first-class operational metric`, `token-heavy`; plus full diff inspection over the three files | PASS - grep returns zero hits in the three target files; the only remaining hits are in append-only `bridge/` thread files, `memory/` operational-notepad scratch, and `independent-progress-assessments/` Loyal Opposition reports, all explicitly scoped out by the proposal's Out-of-scope and MemBase Scope sections |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | The corrected text is consistent with the deterministic-services framing - waste is repetition that yields no marginal information | Inspection of the corrected passages against the deterministic-services principle | PASS - each corrected Lesson names "work repeated whether or not there is anything to do" and "work without information" as the defect |
| GOV-ARTIFACT-APPROVAL-001 | Each protected-file correction carries a narrative-artifact-approval packet with `presented_to_user: true` and a matching content hash | Inspection of the three packets at `.groundtruth/formal-artifact-approvals/2026-05-18-*.json` | PASS - three packets present, each `artifact_type: narrative_artifact`, `action: update`, `presented_to_user: true`, `transcript_captured: true`, with `full_content_sha256` populated |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Each protected narrative-file change clears the universal pre-commit narrative-artifact evidence floor only when its matching approval packet is staged | `python scripts/check_narrative_artifact_evidence.py --staged` with the three rule files staged | PASS - output: `PASS narrative-artifact evidence (3 cleared)` |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The do-not-re-enable mandates, the manual-scan fallback, and the cross-harness-trigger operating mode are unchanged | Full diff inspection over the three files | PASS - the diff touches only framing and lesson sentences; no do-not-re-enable line, no manual-scan fallback line, and no cross-harness-trigger operating-mode line is in the changed set |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | This section | PASS |

Commands executed during verification:

```text
git diff --stat -- CLAUDE.md .claude/rules/bridge-essential.md .claude/rules/canonical-terminology.md
git diff -- CLAUDE.md .claude/rules/bridge-essential.md .claude/rules/canonical-terminology.md
python scripts/check_narrative_artifact_evidence.py --staged
```

The narrative-artifact evidence check was run with the three rule files staged; it reported `PASS narrative-artifact evidence (3 cleared)`, confirming the staged blob of each protected file hashes to the `full_content_sha256` recorded in its approval packet (no line-ending or BOM drift).

## Acceptance Criteria Check

- IP-1 through IP-3 landed: the poller-retirement passages in all three files name the blind, activity-independent mechanism and no longer present token volume as the lesson or as an operational metric. **MET.**
- The incident facts (the roughly tenfold spawn increase, the blind three-minute interval, the 173/92 spawn counts, the per-spawn token figure) are retained. **MET** - each fact still appears in the corrected text.
- No do-not-re-enable mandate, no manual-scan fallback text, and no cross-harness-trigger operating-mode text is removed or weakened. **MET** - confirmed by diff inspection.
- Each protected-file Write carries an owner-approved narrative-artifact-approval packet under the formal-artifact-approvals directory, matching the schema in config/governance/narrative-artifact-approval.toml. **MET** - three packets present and schema-valid.
- `python scripts/check_narrative_artifact_evidence.py --staged` reports PASS with the three protected narrative files cleared. **MET** - `PASS narrative-artifact evidence (3 cleared)`.
- Both bridge preflights pass on this post-implementation report. **MET** - see the Applicability Preflight and Clause Applicability sections below.

## Files Changed

- Staged for commit: `CLAUDE.md`, `.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md` (3 files; `git diff --stat`: 23 insertions, 18 deletions).
- Approval evidence (gitignored under `.groundtruth/`, local evidence, not committed): three narrative-artifact-approval packets under `.groundtruth/formal-artifact-approvals/`. The narrative-artifact evidence check reads these from the filesystem, so they correctly remain uncommitted.
- This report file and the bridge index entry.

## Recommended Commit Type

`docs` - the change corrects governance and rule narrative text in three documentation-class files. No code, test, or capability surface changed. This matches the GO'd proposal's recommended type.

## Risks / Rollback

The proposal's three identified risks did not materialize:

- A correction inadvertently weakening a do-not-re-enable mandate: did not occur; the diff touches only framing and lesson sentences.
- Corrected wording drifting from the DELIB-S358 framing: did not occur; each correction matches the waste-not-volume framing and was owner-approved per packet.
- Approval-packet `full_content_sha256` not matching the staged blob: did not occur; the staged narrative-artifact evidence check passed.

Rollback remains a clean revert of the three files; each is an independent, self-contained text correction with no schema, code, or migration dependency.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
