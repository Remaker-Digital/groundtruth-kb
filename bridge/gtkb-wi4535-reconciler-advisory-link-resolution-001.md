NEW

# gtkb-wi4535-reconciler-advisory-link-resolution - Reconciler Advisory-Link Resolution

bridge_kind: prime_proposal
Document: gtkb-wi4535-reconciler-advisory-link-resolution
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4535-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4535

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4535 fixes a remaining conservative-overblock in `scripts/bridge_verified_backlog_reconciler.py`: a work item can have one or more verified implementation bridge threads and also carry a broad linkage to a terminal or advisory coordination thread. Today, `classify_work_item` treats every recognized non-`VERIFIED` link as `linked_bridge_not_verified` unless it is a satisfied GO umbrella whose children are all verified. That is appropriate for implementation threads, but it incorrectly keeps otherwise-complete work items open when the extra link is an `ADVISORY`, `WITHDRAWN`, or explicitly advisory/planning-only GO thread.

The implementation will add a narrow non-implementation-link classifier. A work item may resolve when it has at least one verified implementation thread with the existing parent-evidence/canonical-metadata safeguards, and every remaining recognized non-verified link is provably non-blocking: latest `ADVISORY`; latest `WITHDRAWN`; or a latest `GO` whose thread chain is explicitly advisory/planning-only through bridge metadata or verdict text. Implementation-like `NEW`, `REVISED`, `GO`, `NO-GO`, `DEFERRED`, missing, and unknown links continue to block. This builds on WI-4704's no-false-positive reconciler engine without weakening the rejected broad `related_bridge_threads` predicate.

No live backlog mutation is in scope for this proposal. The reconciler remains dry-run by default; any later `--apply` run remains a separate operator action after the source/test change is verified.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the classifier derives current bridge status from the status-bearing numbered bridge file chain and must not infer terminal bridge state from stale queue artifacts.
- `GOV-STANDING-BACKLOG-001` - the reconciler resolves MemBase `work_items`, so backlog terminal-state correctness and false-positive avoidance govern the change.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - live classification must read fresh bridge files and current MemBase rows rather than cached scan summaries.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4535-BATCH-A2-20260705`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization lets Prime proceed through the bridge protocol; it does not bypass LO review, `GO`, implementation-start, or verification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the proposed resolution predicate preserves a narrow, auditable authorization envelope for backlog mutation behavior.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable Project Authorization / Project / Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs and maps each to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from the linked specs and WI acceptance behavior.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the bridge/reconciler behavior is used across harnesses and must not encode harness-local assumptions.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - resolving a backlog item through bridge evidence must preserve relevant spec closure rather than treating advisory links as implementation completion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the backlog and bridge audit artifacts aligned when advisory/planning artifacts are linked for traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - treats advisory, proposal, verification, and backlog records as related durable artifacts while preserving their different lifecycle meanings.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge lifecycle states are artifact triggers; ADVISORY and WITHDRAWN do not mean unimplemented work remains.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the target paths are GT-KB platform files under the project root, not external adopter-repository surfaces.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch A2 continuation and active PAUTH for WI-4535.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - basis for the bridge-verified backlog reconciler: VERIFIED implementation evidence can retire parent backlog items.
- `DELIB-20263864` - prior NO-GO identified an overbroad `related_bridge_threads` closure predicate; this proposal keeps the no-false-positive safety floor and does not allow bare related-link membership to satisfy implementation completion.
- `DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION` and `bridge/gtkb-bridge-reconciler-engine-wi4704-001.md` / `-005.md` - recent reconciler engine work added satisfied-GO-umbrella and canonical metadata relaxation paths while explicitly disclosing zero live resolutions under the conservative predicate.
- `bridge/gtkb-fable-investigation-advisory-001.md` - exemplar `ADVISORY` governance-advisory thread broadly linked to FAB implementation work items; it is traceability context, not incomplete implementation.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-003.md` / `-004.md` - exemplar advisory/planning-only GO thread; the GO verdict explicitly limits approval to advisory and planning direction.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-29-08-15-reconciler-linked-bridge-not-verified.md` - LO audit context for the `linked_bridge_not_verified` class.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner directed continuation through the high-priority backlog queue and authorized Batch A2 work through governed PAUTH records, including WI-4535. No additional owner decision is required because this proposal does not expand scope beyond the recorded PAUTH and does not request live backlog mutation.

## Requirement Sufficiency

Existing requirements sufficient. WI-4535 states the required behavior: resolve a work item when at least one linked implementation thread is `VERIFIED` and no linked implementation thread is still in-progress or `NO-GO`; treat `ADVISORY` any status, `WITHDRAWN`, and advisory-kind GO threads as non-blocking. The active PAUTH and linked governance specs are sufficient to implement and verify that behavior without creating a new requirement.

## Spec-Derived Verification Plan

| Linked specification(s) | Verification (test / command + expected result) |
| --- | --- |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` | Add positive reconciler tests where a WI has a verified implementation thread plus an `ADVISORY` thread, a `WITHDRAWN` thread, or an explicit advisory/planning-only GO thread; each resolves with a distinct non-implementation-link reason/evidence and keeps the existing parent-evidence/canonical metadata floor for the verified implementation link. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `DELIB-20263864`, `GOV-FILE-BRIDGE-AUTHORITY-001` | Add negative tests where no verified implementation thread exists, where the extra link is implementation-like `GO` / `NO-GO` / `NEW` / `REVISED` / `DEFERRED`, and where a verified thread lacks parent/canonical evidence; each remains `skip` and does not reintroduce bare `related_bridge_threads` closure. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests build fixture bridge directories from versioned files and run `classify_work_item` / `reconcile` through the same source-of-truth readers used by live operation; no cache or harness-specific queue artifact is consulted. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Before source edits, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4535-reconciler-advisory-link-resolution`; expected packet is active, latest `GO`, target paths limited to the two listed files. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, artifact-oriented specs | Focused verification commands pass and are reported in the implementation report: `python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short`, `python -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`, `python -m ruff format --check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`, and a read-only `python scripts/bridge_verified_backlog_reconciler.py --dry-run --json` smoke with `errors: []`. |

## Risk / Rollback

Primary risk is false-positive backlog resolution when a traceability/advisory link is mistaken for completed implementation. Mitigations: require at least one verified implementation thread with existing parent-evidence/canonical metadata safeguards; classify only latest `ADVISORY`, latest `WITHDRAWN`, and explicit advisory/planning-only GO as non-blocking; keep implementation-like non-verified links blocking; add negative tests for all blocking statuses; and leave live mutation behind the existing explicit `--apply` flag. Rollback is a single commit revert of the reconciler/test changes. No live MemBase or bridge state mutation is part of this implementation.

## Pre-Filing Self-Review

Candidate content was checked before filing with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4535-reconciler-advisory-link-resolution --content-file .gtkb-state/propose-drafts/gtkb-wi4535-reconciler-advisory-link-resolution-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4535-reconciler-advisory-link-resolution --content-file .gtkb-state/propose-drafts/gtkb-wi4535-reconciler-advisory-link-resolution-001.md
```

Observed result before filing:

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:d265cb018f126f4a5c69a00f1daa51c735c3248dba958eb4031ffec62c15db1f`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0`.
- Placeholder sweep: no placeholder markers remained.
- Phantom-spec sweep: all 15 cited spec IDs exist in MemBase.
- `target_paths` parse check: `["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4535-reconciler-advisory-link-resolution`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - repairs an over-conservative reconciler classification defect and adds regression coverage without adding a new user-facing command surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
