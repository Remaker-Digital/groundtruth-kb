NEW

# WI-4802 Reconciler Duplicate Disposition

bridge_kind: prime_proposal
Document: gtkb-wi4802-reconciler-duplicate-disposition
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4802-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4802

target_paths: ["groundtruth.db"]

implementation_scope: governance_evidence/kb_disposition
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4802 is now a duplicate/stale implementation request. Its backlog text asks for `scripts/bridge_verified_backlog_reconciler.py` to stop blocking otherwise complete work items when their verified implementation bridge is co-linked to terminal-but-non-implementation `WITHDRAWN` or `ADVISORY` sibling threads. The later WI-4535 bridge chain implemented and VERIFIED that exact behavior, including positive tests for `ADVISORY`, `WITHDRAWN`, and explicit advisory/planning-only `GO` links plus negative tests for implementation-like non-terminal statuses.

This proposal requests no source or test changes. It requests a single governed MemBase disposition after LO review: resolve WI-4802 as superseded/implemented-by the VERIFIED WI-4535 chain, with completion evidence citing `bridge/gtkb-wi4535-reconciler-advisory-link-resolution-004.md`. The implementation command after GO is limited to `gt backlog resolve WI-4802` with explicit status detail and related bridge evidence. Broad bulk status mutation remains out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the disposition depends on the live numbered bridge chain for WI-4535, not cached summaries.
- `GOV-STANDING-BACKLOG-001` - WI-4802 is a MemBase backlog item and must reach terminal state through governed evidence.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - terminal work-item status feeds project completion/retirement; stale duplicate WIs should not keep projects artificially active.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation must read current WI-4535 bridge/backlog evidence and current WI-4802 state before mutating.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A2 PAUTH scopes the WI-4802 governed disposition work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH and owner queue continuation do not bypass this bridge review.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the mutation envelope is one explicit work item, not a bulk backlog sweep.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH/project/work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - relevant governance specs are cited and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must show source evidence and command results for the disposition.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - WI-4802 can close only because the verified WI-4535 evidence is relevance-complete for WI-4802's stated defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - backlog status, bridge evidence, and completion rationale remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the disposition preserves the relationship between the duplicated WI and the verified implementation chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a VERIFIED implementation thread is the lifecycle trigger for this duplicate disposition.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing through all 43 high-priority items to governed disposition, including retiring/superseding items when live evidence shows they are stale, duplicated, or already terminal under newer work.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - formal-artifact-approval packet for that owner decision; this is not a broad bulk mutation approval and is narrowed here to one WI.
- `bridge/gtkb-wi4535-reconciler-advisory-link-resolution-001.md` - proposal for the reconciler advisory-link resolution fix.
- `bridge/gtkb-wi4535-reconciler-advisory-link-resolution-003.md` - implementation report confirming source/test changes for `ADVISORY`, `WITHDRAWN`, and advisory-kind `GO` links.
- `bridge/gtkb-wi4535-reconciler-advisory-link-resolution-004.md` - Loyal Opposition VERIFIED verdict for that implementation.
- `WI-4802` backlog text - original defect statement naming `WITHDRAWN` and `ADVISORY` sibling threads as blocking otherwise complete work item resolution.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved governed disposition of the high-priority queue and explicitly allowed retirement/supersession when live evidence shows an item is stale, duplicated, or terminal under newer work.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - formal-artifact-approval packet validating the captured owner decision.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4802-BATCH-A2-20260705` - active project authorization for WI-4802 disposition work.

No new owner decision is required. This proposal selects the already-authorized duplicate/superseded disposition path and remains subject to LO GO before any MemBase mutation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4802 states the required behavior, and WI-4535's verified bridge chain satisfies it. The owner continuation decision and Batch A2 PAUTH authorize governed disposition; no new requirement or spec mutation is needed.

## Proposed Implementation

After LO GO and implementation-start authorization, run a single-work-item backlog resolution:

```text
groundtruth-kb/.venv/Scripts/gt.exe backlog resolve WI-4802 --related-bridge-threads "[\"gtkb-wi4535-reconciler-advisory-link-resolution\"]" --status-detail "Resolved as duplicate/superseded by VERIFIED WI-4535 reconciler advisory-link resolution; see bridge/gtkb-wi4535-reconciler-advisory-link-resolution-004.md." --owner-approved --change-reason "Resolve WI-4802 under Batch A2 governed disposition; VERIFIED WI-4535 implemented the same ADVISORY/WITHDRAWN sibling-thread reconciler behavior." --json
```

No source, test, bridge-history rewrite, project retirement, credential, deployment, destructive cleanup, or broad backlog mutation is in scope.

## Spec-Derived Verification Plan

This is the spec-to-test mapping for a no-source/no-test backlog disposition. No Python source changes are proposed, so `pytest`, `ruff check`, and `ruff format --check` are not applicable to an implementation diff. The implementation report must still include command evidence and observed results for each live read, dry-run, apply, and post-apply read below.

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Disposition reads live WI-4535 bridge status and live WI-4802 backlog state before mutation. | `show_thread_bridge.py gtkb-wi4535-reconciler-advisory-link-resolution --format json` shows latest `VERIFIED`; `gt backlog show WI-4802 --json` shows open before apply. |
| `DCL-SPEC-RELEVANCE-CLOSURE-001` | WI-4535 evidence fully covers WI-4802's defect scope. | Implementation report cites the WI-4535 proposal/report/verdict lines covering `ADVISORY` and `WITHDRAWN` sibling threads. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Exactly one work item is mutated; no bulk update. | `gt backlog resolve WI-4802 --dry-run --json` before apply and final `gt backlog show WI-4802 --json` after apply. |
| `GOV-STANDING-BACKLOG-001` and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | WI-4802 reaches terminal `resolved/resolved` with durable completion evidence. | Final `gt backlog show WI-4802 --json` reports `stage=resolved`, `resolution_status=resolved`, and status detail references WI-4535 VERIFIED evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries exact command evidence. | Report includes the live read, dry-run, apply, and post-apply read commands with observed results. |

Minimum verification commands after GO:

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4535-reconciler-advisory-link-resolution --format json --preview-lines 40
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4802 --json
groundtruth-kb/.venv/Scripts/gt.exe backlog resolve WI-4802 --related-bridge-threads "[\"gtkb-wi4535-reconciler-advisory-link-resolution\"]" --status-detail "Resolved as duplicate/superseded by VERIFIED WI-4535 reconciler advisory-link resolution; see bridge/gtkb-wi4535-reconciler-advisory-link-resolution-004.md." --owner-approved --change-reason "Resolve WI-4802 under Batch A2 governed disposition; VERIFIED WI-4535 implemented the same ADVISORY/WITHDRAWN sibling-thread reconciler behavior." --dry-run --json
groundtruth-kb/.venv/Scripts/gt.exe backlog resolve WI-4802 --related-bridge-threads "[\"gtkb-wi4535-reconciler-advisory-link-resolution\"]" --status-detail "Resolved as duplicate/superseded by VERIFIED WI-4535 reconciler advisory-link resolution; see bridge/gtkb-wi4535-reconciler-advisory-link-resolution-004.md." --owner-approved --change-reason "Resolve WI-4802 under Batch A2 governed disposition; VERIFIED WI-4535 implemented the same ADVISORY/WITHDRAWN sibling-thread reconciler behavior." --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4802 --json
```

## Risk / Rollback

Risk is low but real: an incorrect duplicate disposition would prematurely hide a live backlog item. Mitigation is explicit relevance evidence from the VERIFIED WI-4535 bridge chain and a single-WI dry-run before apply. Rollback would append a new `gt backlog update WI-4802 --stage backlogged --resolution-status open` version with a corrective change reason through a follow-up governed bridge if LO or later evidence finds the disposition wrong.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4802-reconciler-duplicate-disposition`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore:` because the eventual change is governed backlog metadata disposition only, with no source/test behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
