NEW

# gtkb-wi4752-verified-reconciler-live-status-guard - prevent stale VERIFIED reconciler closure

bridge_kind: prime_proposal
Document: gtkb-wi4752-verified-reconciler-live-status-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-23T09:14:55Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, Prime Builder resolved role

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4752

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4752 covers a stale-closure defect in `scripts/bridge_verified_backlog_reconciler.py`: live WI-4723 was marked resolved by the bridge VERIFIED backlog reconciler even though the relevant bridge thread later had a non-terminal latest state at `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-019.md`.

This proposal adds a narrow source/test guard so the reconciler cannot write a resolved work-item version from stale VERIFIED-derived classification when the linked bridge thread is no longer latest `VERIFIED`. The intended implementation keeps the existing dry-run inventory behavior and strict parent-evidence rules, but revalidates latest bridge status immediately before `--apply` performs a MemBase resolution write. If any recognized parent link has drifted to `NEW`, `REVISED`, `GO`, `NO-GO`, `ADVISORY`, `DEFERRED`, `WITHDRAWN`, or missing/non-VERIFIED state, the row is skipped and reported as not resolved.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the reconciler must treat dispatcher/TAFE state plus status-bearing numbered bridge files as live bridge authority; the proposal and any implementation must preserve append-only bridge files and latest-status semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal cites the governing requirements and maps them to concrete regression tests before any source mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the required `Project Authorization`, `Project`, and `Work Item` metadata lines for the bounded May29 Hygiene authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the linked bridge/backlog/reconciler requirements, not only a source diff inspection.
- `GOV-STANDING-BACKLOG-001` - the reconciler mutates `work_items` lifecycle state in MemBase, so it must not resolve a standing-backlog work item unless the durable evidence still satisfies the closure rule at mutation time.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this proposal relies on the active project-scoped PAUTH named above and remains limited to source plus test additions in the declared target paths.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - project and work-item lifecycle closure is driven by VERIFIED bridge evidence; stale VERIFIED evidence must not remain authoritative after a later non-terminal bridge version exists.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal preserves the artifact graph between WI-4752, bridge evidence, MemBase work-item lifecycle state, regression tests, and the implementation report/verdict trail.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect is a lifecycle-trigger error: a work item reached `resolved` from stale bridge evidence while the related bridge thread was later non-terminal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this change keeps concrete project state and closure criteria visible in governed artifacts instead of accepting stale generated closure state as truth.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - the reconciler's core closure authority: a parent backlog/work item can be retired from VERIFIED bridge evidence. This proposal preserves that authority but adds a live-status guard before mutation.
- `DELIB-20263860` - Loyal Opposition verification for Bridge VERIFIED Backlog Retirement, confirming prior work on this reconciler family. This proposal is a follow-up guard, not a replacement for the verified retirement mechanism.
- `DELIB-20263863` - Loyal Opposition review for Bridge VERIFIED Backlog Retirement, establishing the review lineage for strict bridge-backed backlog retirement behavior.
- `DELIB-WI4723-OWNER-PROCEED-20260621` - owner directive to proceed with WI-4723, the live incident family cited by WI-4752.
- `DELIB-20265754`, `DELIB-20265756`, `DELIB-20265758`, and `DELIB-20265762` - WI-4723 verification/NO-GO deliberations showing the thread continued through later review states; these are the concrete stale-closure regression context.

## Owner Decisions / Input

The owner already authorized this bounded implementation through `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`, owner decision `DELIB-20265586`. No additional owner decision is required because the proposal does not mutate formal artifacts, does not add work items, does not change the project authorization scope, and limits implementation to source plus test changes.

## Requirement Sufficiency

Existing requirements sufficient - WI-4752 states the required behavior directly: the reconciler must validate latest live bridge state before resolving work items and avoid using stale VERIFIED-derived closure when later non-terminal bridge files exist. The linked bridge, backlog, project-retirement, and verification specifications above are sufficient to implement and verify this guard.

## Spec-Derived Verification Plan

| Linked specification / requirement | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; WI-4752 live-status requirement | Add a focused regression in `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` where initial classification sees a VERIFIED linked bridge, a later non-terminal version is introduced before the apply-time MemBase write, and the reconciler skips resolution after re-reading latest bridge state. |
| `GOV-STANDING-BACKLOG-001`; `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Assert the work item remains `open`/`backlogged` and `resolved_ids` stays empty when the latest bridge state is non-terminal. Also preserve existing positive tests where all parent links remain latest VERIFIED. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused reconciler test module through the repo venv and report observed results in the post-implementation report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run the mandatory bridge applicability and ADR/DCL clause preflights before filing the proposal and again in LO review; ensure implementation-start accepts only the two declared target paths after GO. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve the proposal/report/verdict artifact trail, cite WI-4752 and prior deliberations, and verify that the lifecycle transition only occurs when latest bridge evidence still supports it. |

Expected commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4752-verified-reconciler-live-status-guard
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4752-verified-reconciler-live-status-guard
```

## Pre-Filing Preflight Evidence

Candidate-body checks before filing:

- Placeholder-marker scan against `.gtkb-state/propose-drafts/gtkb-wi4752-verified-reconciler-live-status-guard-001.md` - PASS; no remaining scaffold placeholders.
- `target_paths` inline JSON parse via PowerShell `ConvertFrom-Json` - PASS; parsed paths are `scripts/bridge_verified_backlog_reconciler.py` and `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4752-verified-reconciler-live-status-guard-001.md --json` - PASS after advisory-spec citation update; `missing_required_specs: []`, `missing_advisory_specs: []`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4752-verified-reconciler-live-status-guard-001.md` - PASS; blocking gaps 0.

## Risk / Rollback

Risk is narrow but lifecycle-sensitive: an overly strict guard could leave eligible work items open after a legitimate VERIFIED closure. The implementation should preserve existing strict-parent-evidence and umbrella-child positive tests, and only skip resolution when the just-in-time latest bridge status check disagrees with the earlier resolve classification. Rollback is a single-source/test revert of the two target paths plus withdrawal or supersession of this bridge thread if LO finds the approach unsound before implementation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4752-verified-reconciler-live-status-guard`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the proposed change repairs incorrect work-item lifecycle resolution without adding a new user-facing capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
