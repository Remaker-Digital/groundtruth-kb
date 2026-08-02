REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop Prime Builder; transcript-defined PB role; owner-approved WI-5297 substantive v011 proposal only; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context


bridge_kind: prime_proposal
Document: gtkb-wi5297-inflight-max-item-capacity
Version: 011
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5297-inflight-max-item-capacity-010.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5297-MAX-ITEM-INFLIGHT-CAP-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5297
Test: TEST-11443

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation occurs in this proposal.

# WI-5297 REVISED Implementation Proposal — Enforce Per-Harness In-Flight Item Capacity

## Revision Disposition

Version 010 is a routing-only Loyal Opposition acceptance of version 009's
NO-ACTION carrier. It grants no implementation authority and directs any
continued repair through a linked tracked work-item
propose-to-GO-to-implement-to-VERIFIED cycle. This version begins that fresh
substantive cycle for still-open `WI-5297` after the project was reactivated
and the owner approved the work item as written in
`DELIB-20260801-WI5297-IMPLEMENTATION-APPROVAL`.

The defect remains present in current source: a target's configured
`dispatch_max_items` limits only the newly selected batch. Unresolved selected
documents already present in the recipient launch ledger do not consume the
next cycle's item capacity. A max-one harness can therefore receive a second
unresolved document before the first launch reaches processed terminal state.

This revision authorizes no source or test mutation. Implementation remains
blocked until an independent Loyal Opposition `GO`, an uncontested exact
work-intent claim, a schema-v3 implementation-start authorization packet, and
fresh target-ownership checks all pass. Dispatcher and TAFE activation,
configuration, lease policy, timers, credentials, provider selection, and
process termination are outside scope.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, `WI-5297`, and `TEST-11443`
already define the bounded capacity behavior and required regression evidence.
No specification amendment is needed before this source/test repair.

## Current-Code Evidence

- `scripts/dispatcher_runtime.py:5873` refreshes launch-ledger counts by
  unresolved launch records, not unresolved selected documents.
- `scripts/dispatcher_runtime.py:6380` performs pending-exit reconciliation
  before selection, providing the correct point after which active item usage
  can be derived.
- `scripts/dispatcher_runtime.py:6438-6439` computes the target signature from
  the raw effective target maximum and does not subtract prior in-flight item
  usage.
- `scripts/dispatcher_runtime.py:6966` again derives the raw target maximum in
  the dispatch loop, while the prior launch ledger is loaded only later at
  `scripts/dispatcher_runtime.py:7026-7028`.
- `platform_tests/scripts/test_dispatcher_runtime.py:7081-7177` already
  supplies launch-ledger fixtures and exact-once exit-reconciliation seams,
  and the ordered-fallback coverage around
  `platform_tests/scripts/test_dispatcher_runtime.py:7772-7924` supplies the
  ranked-target seam. No current test asserts cross-cycle item-capacity
  subtraction or a `dispatch_capacity_held` result.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — selection and launch capacity must remain deterministic across daemon cycles.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — configured caps and emitted effective-capacity evidence must agree.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — active harnesses receive genuine governed work without duplicate over-cap dispatch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected work requires an independently reviewed proposal, implementation report, and verification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — document and launch attribution remain bound to selected harness/session evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — operative requirements are linked before protected mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must re-derive and execute the mapped test evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact project, PAUTH, work item, test, and targets are declared.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the active PAUTH must remain valid at every mutation and finalization boundary.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — no protected edit may precede GO, claim, and implementation-start authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — defect, decision, implementation, test, and verdict stay durably linked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the governed artifact lifecycle remains the implementation carrier.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — a post-VERIFIED recurrence requires a fresh regression carrier.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the repair remains inside the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — deterministic source/test evidence enforces the same gates on this harness.
- `GOV-STANDING-BACKLOG-001` — WI-5297 remains visible until independently verified.

## Prior Deliberations

- `DELIB-20260801-WI5297-IMPLEMENTATION-APPROVAL` — owner approval of WI-5297 as written; explicitly authorizes this fresh substantive proposal cycle while preserving all downstream gates.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — original bounded fleet-proof defect-repair authority carried by the active PAUTH.
- `DELIB-20260702-DISPATCH-LAYERED-CAPS-OVERFLOW` — prior owner decision establishing layered capacity controls and overflow behavior.
- `DELIB-202666236` — predecessor WI-5233 terminal decision; its per-batch repair does not close the cross-cycle in-flight gap.
- `DELIB-202667749` — project reactivation evidence for `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION` version 6.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` — VERIFIED launch-ledger predecessor that supplies the authoritative per-recipient history.
- `bridge/gtkb-wi5297-inflight-max-item-capacity-008.md` through `bridge/gtkb-wi5297-inflight-max-item-capacity-010.md` — correction chain that closed the stale carrier and required a fresh tracked proposal cycle.

## Owner Decisions / Input

The owner approved `WI-5297` as written. The durable evidence is
`DELIB-20260801-WI5297-IMPLEMENTATION-APPROVAL`. No further owner decision is
required to review this proposal. That decision does not waive independent GO,
target ownership, implementation-start, test, report, or verification gates.

## Proposed Implementation

1. After ordinary pending-exit and per-document terminal reconciliation,
   derive active in-flight item usage for the selected recipient from every
   unresolved launch-ledger record.
2. Count unresolved documents, not processes. Prefer per-document outcome
   fields when present. For legacy records without those fields, count the
   normalized unique `selected_documents` entries; a malformed record must
   fail bounded and conservatively rather than create extra capacity.
3. Derive `available_items = max(0, configured_target_max_items -
   active_inflight_items)` and use that value consistently for selected-item
   slicing and signature construction.
4. When available capacity is zero, acquire no new document lease and spawn no
   worker. Record stable non-failure `dispatch_capacity_held` evidence including
   configured, active, and available item counts.
5. Continue ordered target evaluation after a capacity-held target so another
   eligible target with capacity can receive the pending item.
6. A normally processed terminal exit releases capacity on the next ordinary
   cycle. Do not terminate a worker, rewrite an existing launch record, or
   release an existing lease merely to manufacture capacity.
7. Preserve oldest-first ordering, document-lease authority, work-intent
   claims, launch-failure reconciliation, provider backoff, stale-run handling,
   circuit breakers, role selection, reviewer independence, harness allowance,
   and current dispatch configuration.

## Live Ownership And Sequencing

Fresh scoped Git checks show both targets clean. Exact current `target_paths`
scanning nevertheless finds two nonterminal, unclaimed `NEW` proposal lanes:

- `bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md` names both targets.
- `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strict-recovery-001.md` names the shared test target.

Those lanes do not block proposal review, but they do block implementation
start unless they first become terminal or a fresh mechanical overlap check
proves exact hunk non-overlap accepted by the governing start packet. WI-5297
must not overwrite, absorb, or finalize their work. If either lane acquires a
claim or dirties a shared target, WI-5297 waits and rebaselines.

## Verification Plan

| Requirement | Spec-derived verification | Expected result |
| --- | --- | --- |
| Max-one cross-cycle capacity | Seed one unresolved selected document for a max-one recipient, present a distinct actionable document, and run a later cycle | no second lease or spawn; result `dispatch_capacity_held`; configured=1, active=1, available=0 |
| Per-document rather than per-process accounting | Seed one unresolved multi-document launch under a larger cap | active count equals unresolved selected documents, not one process |
| Partial max-two capacity | Seed one unresolved document under cap two | exactly one additional document may be selected |
| Per-document completion | Mark one document in a multi-document launch terminal while another remains unresolved | only the unresolved document consumes capacity |
| Terminal release and idempotence | Process the prior exit twice, then run the next cycle | capacity releases once; exactly one new dispatch becomes eligible |
| Legacy compatibility | Seed a legacy launch with `selected_documents` and no per-document outcomes | normalized unresolved documents consume bounded capacity without crashing |
| Ranked failover | Make the first ranked target capacity-held and a later target available | first records hold evidence; later target receives the item |
| No destructive runtime side effects | Spy on lease acquisition/release, process termination, and spawn helpers | capacity-held branch acquires/releases/kills/spawns none |
| Existing dispatcher contracts | Run the complete dispatcher runtime test module plus Ruff check and format check | all tests and style checks pass without routing, lease, backoff, allowance, or reconciliation regression |

Planned commands:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
```

## Acceptance Criteria

1. A recipient capped at one item with one unresolved selected document cannot
   receive or lease a second document on a later cycle.
2. Capacity accounting is per unresolved selected document across all active
   launch-ledger entries, including current per-document and bounded legacy
   representations.
3. Partial completion releases only completed-document capacity; processed
   terminal exit reconciliation is idempotent.
4. A full first-ranked target does not prevent a later eligible target with
   available capacity from receiving work.
5. Capacity-held evidence is stable and contains configured, active, and
   available counts without being classified as a provider or worker failure.
6. The hold branch acquires no new lease, spawns no worker, kills no process,
   and mutates no existing launch record or dispatcher/TAFE configuration.
7. Focused and full runtime tests plus Ruff check and format check pass.
8. The final candidate contains only WI-5297 hunks in the two authorized paths
   and does not overlap live peer work.
9. A post-implementation report receives independent `VERIFIED` before any
   finalization or focused commit.

## Scope Boundaries

In scope: the smallest source change needed to subtract unresolved
per-document launch-ledger usage from configured item capacity, plus focused
regressions in the existing dispatcher runtime test module.

Out of scope: dispatcher or TAFE activation/reconfiguration; timer or timeout
changes; worker termination; lease-policy changes; provider, model, role,
allowance, eligibility, or ranking changes; credentials; external-system
mutation; destructive cleanup; Git history rewrite; push; deployment; release;
KB mutation; and unrelated formatting or refactoring.

## Pre-Filing Preflight Subsection

Before live filing, the completed v011 candidate must pass:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5297-inflight-max-item-capacity --content-file .tmp/bridge-revisions/gtkb-wi5297-inflight-max-item-capacity-011.candidate.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5297-inflight-max-item-capacity --content-file .tmp/bridge-revisions/gtkb-wi5297-inflight-max-item-capacity-011.candidate.md
```

The filing helper must also perform credential scanning, author-envelope
normalization, bridge-compliance audit, exact claim enforcement, append-only
version writing, and publication through the governed bridge writer.

## Risk And Rollback

The primary risk is conservative under-dispatch when a legacy launch record is
malformed or remains unresolved. That is safer than duplicate live work and is
observable through explicit counts. The implementation must derive usage only
after normal reconciliation and must not alter existing live work to free
capacity. Rollback is a focused revert of the eventual two-path source/test
commit; append-only owner decision, bridge, test, report, and verdict evidence
remains historical.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
