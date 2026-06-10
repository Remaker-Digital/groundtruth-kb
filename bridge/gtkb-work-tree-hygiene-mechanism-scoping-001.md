NEW

# Implementation Proposal — Recurring Work-Tree Hygiene + Stash-Stray-Cleanup Mechanism (WI-4356)

bridge_kind: governance_advisory
Document: gtkb-work-tree-hygiene-mechanism-scoping
Version: 001
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ff01ba72-8bce-49fd-ab2f-9d2cff01ba72
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-4356
work_item_ids: [WI-4356]
target_paths: []
requires_verification: false
implementation_scope: governance_review_scoping
spec_ids: ["GOV-WORK-TREE-HYGIENE-001"]

Recommended commit type: docs(bridge)

---

## Claim

Define the recurring work-tree hygiene + stash-stray-cleanup mechanism owner-directed at 2026-06-04 in S-loop session ff01ba72. This proposal is the **scoping capstone** for a multi-slice implementation initiative; it ESTABLISHES the design contract but does NOT itself mutate source or governance. Each implementation slice files its own bridge thread under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING coverage.

## Owner Directive (Source)

Owner statement, 2026-06-04 UTC, S-loop ff01ba72:

> "We cannot expect agents to return and complete commits of their code after 12 hours have elapsed. Any work that is older than 12 hours must be triaged and committed by a different agent. We need to ensure that we are enforcing work-tree hygiene and have a regular method for cleaning up strays."

## Specification Links

Cross-cutting (blocking + advisory):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance umbrella; work-tree hygiene is an artifact-discipline contract.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance for reliability-class WIs.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets for new GOV/DCL insertion at impl time.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — fresh-read preference; hygiene checks should read live state, not cached snapshots.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the linkage mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Specification-Derived Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + PAUTH + WI metadata declared above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all work stays inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts produced (CLI, doctor check, governance spec).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring hygiene is exactly the class of deterministic service this principle endorses.

New specs drafted by this proposal (impl-time insertion):

- `GOV-WORK-TREE-HYGIENE-001` — governance contract defining stale criteria + triage rules + enforcement mechanism.

## Prior Deliberations

- 2026-06-04 S-loop ff01ba72 — owner directive (above); manual triage drop'd 9 abandoned stashes after confirming zero recoverable unique content.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing belongs in services, not sessions.
- `DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ` (this session) — example of owner-AUQ pattern for governance-state amendments.
- Prior session memory `project_2026_06_04_loop_session_5_drains_3_verified.md` — documents the cross-harness collaboration pattern this mechanism formalizes.

_The 9 dropped stashes are the originating evidence: 3 days to 2 weeks old, all from sessions that never returned, all content already recovered in HEAD via other commit paths. The drop was safe because of manual byte-identical-check; the proposed mechanism automates that check._

## Owner Decisions / Input

- 2026-06-04 UTC, S-loop ff01ba72: owner directed filing of this bridge proposal (verbatim above).
- 2026-06-04 UTC, S-loop ff01ba72: owner AUQ approved manual triage + batch-drop of 9 abandoned stashes (precedent for future automated stash disposition).
- No new owner-AUQ decisions required for THIS proposal filing (governance_review/scoping only). Implementation slices will collect their own AUQ + formal-artifact-approval packets at impl time.

## Requirement Sufficiency

Existing requirements sufficient as augmented by the owner directive above. The directive itself is the requirement: enforce work-tree hygiene + cleanup strays with recurring mechanism. Implementation slices may surface additional sub-requirements at proposal time.

## Proposed Scope

### Stale Detection Criteria

Define machine-checkable thresholds:

1. **Working-tree files** (modified, untracked, or deleted): stale if `(now - mtime) > 12h` AND the file's authoring session context_id (where extractable from file metadata, e.g., `author_session_context_id:` line in bridge/memory files) is NOT in the active-session registry.
2. **Git stashes**: stale if stash age > X days (proposed default: 3 days; configurable). Reason: aligns with owner's 12h working-tree rule extended to the longer-form stash mechanism (stashes are explicit-park gestures with longer expected residency).
3. **Active-session registry**: derived from `.gtkb-state/active-session-*.json` markers + `bridge-poller/dispatch-state.json`. Sessions absent from the registry for >24h are considered abandoned.

### Triage Decision Rules (Deterministic)

For each stale item:

1. **Working-tree file**:
   - If file is HEAD-byte-identical to current HEAD (mtime stale but content not actually different) → **silent no-op** (file is unchanged; mtime is misleading; touch-only artifact).
   - If file is modified and is in `ALLOWED_WRITE_PREFIXES` (bridge/, memory/, IPA/) with a recoverable author_session_context_id → **safe-commit candidate** (re-attribute commit via Co-Authored-By).
   - If file is modified and touches PROTECTED paths (scripts/, groundtruth-kb/src/, .claude/hooks/, etc.) → **stash-with-label** (require human review; never auto-commit protected mutations).
   - If file is untracked and >24h old with no recent author-session activity → **stash-or-discard candidate** (owner-AUQ).
2. **Git stash**:
   - If 100% of stash files are HEAD-byte-identical OR represent NO-OP applies (e.g., file-deletion of already-absent file) → **auto-drop** (today's precedent: 7 of 9 stashes fell into this category).
   - If stash has 1+ files unique to the stash (not in HEAD) → **owner-AUQ for inspect/recover/drop**.
   - If stash >2 weeks old AND all content auto-regenerates (runtime cache) → **auto-drop**.

### Implementation Surfaces (Multi-Slice Plan)

This is a scoping capstone; each surface lands in its own bridge thread:

- **Slice A** — Detection helper (`scripts/hygiene/stray_detector.py`): read-only enumeration of stale items per criteria above. Produces structured JSON output. Reuses existing helpers (`extract_target_paths`, `normalize_relative_path`, etc.) where applicable.
- **Slice B** — Triage CLI (`gt hygiene strays`): consumes detector output; for each stale item, applies the deterministic triage rules; emits actions (drop / commit / stash-with-label / owner-AUQ-required) but does NOT execute mutations by default (dry-run-first per `kb-batch` precedent).
- **Slice C** — Doctor integration (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`): new check `_check_work_tree_strays` that runs the detector in summary mode and surfaces stray count + age distribution.
- **Slice D** — Governance spec insertion (`GOV-WORK-TREE-HYGIENE-001`): MemBase insert with body + machine-checkable assertions referencing the detector/CLI. Requires formal-artifact-approval packet at this slice.
- **Slice E** — Optional enforcement automation: scheduled-task or hook integration (PostToolUse on git commands? Stop-hook? scheduled cron?). Owner-AUQ-required decision at the slice's proposal time.

Each slice files its own bridge proposal citing this scoping capstone as a Prior Deliberation. Each slice carries its own target_paths and verification plan.

### Out of Scope (Explicit)

- Backfill of pre-existing stale state: out of scope here; the 9 stashes drop'd this session are the manual-precedent backfill.
- Automatic mutation execution by default: out of scope; the CLI emits actions but executes only on explicit owner-confirmed run (e.g., `gt hygiene strays --apply` after dry-run).
- Cross-repository scanning: this mechanism is scoped to `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification-Derived Verification Plan

| Linked Spec | Expected Impl-Time Verification |
|---|---|
| `GOV-WORK-TREE-HYGIENE-001` (new) | MemBase readback after Slice D shows version 1, type=governance, status=specified, expected assertions referencing detector + CLI + doctor check. |
| `GOV-ARTIFACT-APPROVAL-001` | Slice D's MemBase insert is gated on a generated approval packet validated via `scripts/validate_formal_artifact_packet.py`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Detector reads live working-tree state (`git status`, `git stash list`) + live `.gtkb-state/active-session-*.json` markers each run; no cached snapshots. |
| `GOV-RELIABILITY-FAST-LANE-001` | Each slice's diff stat ≤ ~500 lines net + bounded scope; all slices reliability-fast-lane-eligible (origin=hygiene). |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This Specification Links section + applicability preflight on this proposal AND each slice. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each slice carries its own spec-to-test mapping table. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Slice A detector + Slice B CLI demonstrate the deterministic service replacing manual per-session triage. |

## Risk / Rollback

- **Risk: low for this proposal** (governance_review/scoping only; no mutation). Implementation slices each have their own risk profile.
- **Risk: medium for Slice E** (enforcement automation). Mitigation: owner-AUQ-required decision at Slice E proposal time; default is "report-only" with manual owner-confirmed apply.
- **Rollback for impl slices:** revert per-slice commits; the governance spec can be marked superseded via formal-artifact path.
- **Forward-compatibility:** the detector's structured JSON output is the durable contract; UI surfaces (doctor check, CLI report) consume that contract.

## Bridge-Index Canonical-State Acknowledgment

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this proposal is filed via the canonical `bridge/INDEX.md` workflow and its acceptance/rejection state is determined exclusively by INDEX status lines. The proposed hygiene mechanism EXPLICITLY READS `bridge/INDEX.md` as the canonical bridge-state source-of-truth (no cached snapshots, no DA queries as substitute) when classifying stale working-tree files as "bridge-recoverable" vs "lost-work" candidates. The proposed `gt hygiene strays` CLI's bridge-related triage paths MUST consult live `bridge/INDEX.md` per `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`. No alternative bridge-state authority is introduced or implied by this proposal or any of its 5 slices.

## Artifact-Lifecycle-Triggers Acknowledgment

Per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: this proposal is a CANDIDATE governance-review scoping capstone (origin=hygiene per WI-4356 classification). The lifecycle trigger chain is: owner directive (2026-06-04) → captured deliberation (above) → backlog candidate WI-4356 created via `gt backlog add` → this scoping proposal (current artifact) → owner-AUQ-gated impl slices → VERIFIED governance spec `GOV-WORK-TREE-HYGIENE-001`. Each downstream slice's bridge thread carries its own lifecycle evidence. No artifact transitions to "verified" status without the bridge-protocol verification chain completing for the relevant slice.

## Acceptance Criteria for This (Scoping) Slice

GO from Loyal Opposition on this proposal means:

1. The scope (detection criteria, triage rules, slice plan) is acceptable as the implementation contract.
2. The 5-slice decomposition is the right grain for incremental delivery.
3. The new `GOV-WORK-TREE-HYGIENE-001` spec name + intent are acceptable as the governance target.

NO-GO triggers a REVISED with adjusted scope. Implementation only begins after this scoping proposal reaches GO.

## Recommended Commit Type

`docs(bridge)` — this proposal mutates no source/spec/config; it's a governance_review scoping artifact + INDEX entry only.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
