NEW

# gtkb-bridge-reconciler-engine-wi4704 — Bridge Reconciler Engine: umbrella auto-closure + parent-evidence relaxation (WI-4704)

bridge_kind: prime_proposal
Document: gtkb-bridge-reconciler-engine-wi4704
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-20 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 34407a42-8900-4908-a72a-3ed27a0df984
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-ENGINE-WI4704
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4704

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4704 extends `scripts/bridge_verified_backlog_reconciler.py` so it can auto-resolve two work-item classes a 2026-06-20 session-start dry-run could not (95 candidates examined, 0 resolved — every one skipped `linked_bridge_not_verified` or `missing_parent_evidence`). Owner authorized this session to drive WI-4704 (`DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION`, AskUserQuestion 2026-06-20) under `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-ENGINE-WI4704`.

This proposal is deliberately conservative because the reconciler's no-false-positive contract is load-bearing: the strict parent-evidence requirement exists precisely because an earlier related-thread closure predicate was found overbroad (`DELIB-20263864`, `-006` NO-GO; repaired per the reconciler's `REPAIR_CHANGE_REASON`). The two changes below add resolution paths without re-opening that defect.

**Change 1 — Umbrella auto-closure (backlog resolution only; no bridge VERIFIED minting).** A work item linked to a thread `T` whose latest status is `GO` becomes resolvable when: (a) `T` has at least one child thread (a thread whose slug is `T-<suffix>`), (b) **all** of `T`'s child threads are latest `VERIFIED`, and (c) at least one child thread carries the work item's parent evidence (the WI id via the existing `bridge_thread_has_parent_evidence` check). Resolution uses a distinct reason `umbrella_children_all_verified` and completion evidence citing the umbrella + verified children. The reconciler does **not** mint a `VERIFIED` verdict on the umbrella bridge file: `VERIFIED` is a Loyal Opposition verdict, and a reconciler minting it would violate verdict authority. This is a deliberate, governance-aware deviation from WI-4704's literal "file VERIFIED on an umbrella" wording — the same backlog outcome (the parent WI resolves) is achieved without a non-LO verdict. Child detection reuses existing slug/child helpers (`groundtruth_kb.bridge.routing` / `bridge.audit`) where available rather than inventing a parallel matcher.

**Change 2 — Parent-evidence relaxation (narrow, deliberate-declaration path).** The `missing_parent_evidence` skip fires when a VERIFIED linked thread does not carry the WI id in its files. The relaxation accepts, as sufficient parent evidence, a VERIFIED thread that declares the work item through the **canonical `^Work Item: WI-XXXX$` metadata line** (already parsed by `_WORK_ITEM_METADATA_RE` / `build_work_item_bridge_links`). It explicitly does **not** accept bare `related_bridge_threads` membership or prose mentions as evidence — that is the exact overbroad predicate `DELIB-20263864` rejected. The implementation first enumerates the live `missing_parent_evidence` cases (read-only dry-run) and applies the relaxation only to those provably backed by a canonical metadata declaration; the regression test encodes the no-false-positive guard.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — the reconciler resolves MemBase `work_items`; backlog is the governed authority whose terminal-state correctness this change improves.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — resolution derives from latest bridge status read from the status-bearing numbered file chain (no-index canonical state); umbrella/child detection reads the same surface.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — classification reads fresh bridge files + MemBase, not cached reports.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — work proceeds under `PAUTH-...-ENGINE-WI4704`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the new resolution paths preserve the reconciler's `--apply` gating and no-bulk-false-positive contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — keeps backlog/bridge artifacts consistent (the project's purpose).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — treats the project as a network of durable artifacts; the reconciler closes the loop between VERIFIED bridge artifacts and backlog artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — VERIFIED bridge completion is the lifecycle trigger that should retire the parent backlog item (`DELIB-S345`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps each change to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — carries Project / Work Item / Project Authorization metadata.

## Prior Deliberations

- `DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION` — owner authorization for this work; this proposal implements it.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — the reconciler's basis (bridge VERIFIED retires the parent backlog item); WI-4704 extends its reach to umbrella + relaxed-evidence classes.
- `DELIB-20263864` — Bridge VERIFIED Backlog Retirement `-006` NO-GO that identified an **overbroad `related_bridge_threads` closure predicate**; Change 2 is scoped specifically to NOT reintroduce it.
- `DELIB-20263863` — `-002` GO for the retirement engine (the safe baseline).
- `DELIB-20263860` — `-010` VERIFIED retirement (the current safe state this change builds on).
- `DELIB-20262508` — Terminal Backlog Evidence Review Packet (evidence-discipline context).
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — project authorization for PROJECT-GTKB-BRIDGE-RECONCILIATION.

## Owner Decisions / Input

- `DELIB-2026-06-20-WI4704-ENGINE-IMPLEMENTATION-AUTHORIZATION` — owner AskUserQuestion (2026-06-20) selected "Authorize & I drive it" for WI-4704, authorizing this session to drive the engine change and the bounded `PAUTH-...-ENGINE-WI4704`. The decision explicitly preserves the no-false-positive contract and all bridge/review/verification gates.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — owner authorization of the project.

## Requirement Sufficiency

Existing requirements sufficient. Governing requirements: WI-4704's acceptance summary ("Reconciler auto-resolves the stuck-at-GO-umbrella and missing-parent-evidence WI classes; a regression test covers the 95-candidate class; no false-positive resolutions") + the authorization DELIB + `PAUTH-...-ENGINE-WI4704` (linked to GOV-STANDING-BACKLOG-001 + GOV-FILE-BRIDGE-AUTHORITY-001). No new requirement is needed; the acceptance summary's "no false-positive resolutions" clause is the binding safety constraint Change 2 is designed around.

## Spec-Derived Verification Plan

| Linked specification(s) | Verification (test / command + expected result) |
| --- | --- |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | New cases in `test_bridge_verified_backlog_reconciler.py`: an umbrella thread at GO with all children VERIFIED + child parent-evidence → WI classified `resolve` (`umbrella_children_all_verified`); a VERIFIED thread declaring the WI via the canonical `Work Item:` metadata line → WI classified `resolve`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` (no-false-positive contract), `DELIB-20263864` | Negative cases: umbrella at GO with ≥1 non-VERIFIED child → `skip` (still `linked_bridge_not_verified`); a WI linked only via bare `related_bridge_threads` / prose mention to a VERIFIED thread that does NOT declare it via metadata → `skip` (still `missing_parent_evidence`); confirms the overbroad predicate is not reintroduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests drive `classify_work_item` over fixture bridge dirs (no live mutation); a read-only `--dry-run --json` smoke against live state shows the previously-skipped classes now appear under `would_resolve_ids` with the new reasons and `errors: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Full `pytest` of the reconciler test module passes (existing + new cases); `ruff check` and `ruff format --check` pass on the changed files; applicability + clause preflights green. |

Commands (repo venv interpreter):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_verified_backlog_reconciler.py --dry-run --json
```

## Risk / Rollback

Primary risk is a **false-positive resolution** (resolving a WI whose work is not truly complete). Mitigations: Change 1 requires ALL children VERIFIED plus child-level parent-evidence and never mints a bridge verdict; Change 2 accepts only canonical `Work Item:` metadata declarations, explicitly excluding the bare-`related_bridge_threads`/prose predicate that `DELIB-20263864` rejected; the regression test encodes both positive and negative (no-false-positive) cases; and the reconciler remains read-only unless `--apply` is passed, with the existing `--repair-overbroad` reopen path intact as a backstop. Rollback: single-commit revert restores the prior reconciler + test. No data/KB rollback (`kb_mutation_in_scope: false`); the change alters classification logic, not stored state, and resolution only occurs on an explicit, separately-run `--apply`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-bridge-reconciler-engine-wi4704`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` — adds two new resolution paths (a new capability) to the reconciler engine plus regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
