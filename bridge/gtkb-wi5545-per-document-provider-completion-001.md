NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed WI-5545 proposal

# Implementation Proposal - Require provider harness completion for every assigned bridge document

bridge_kind: prime_proposal
Document: gtkb-wi5545-per-document-provider-completion
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5545

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Require each cloud-provider and Ollama worker to complete every dispatcher-assigned bridge document through the canonical governed publisher before accepting provider completion. The proposal preserves the fixed A/D/F topology and sequences source implementation after current exact-target owners WI-5495 and WI-5471 are terminal.

Work item description: The current Ollama and shared cloud-provider Loyal Opposition loops track governed completion with one global bridge_verdict_published boolean even though the canonical active topology permits D and F to receive two bridge documents per dispatch. After one assigned slug publishes successfully, the loop can accept final assistant text while another assigned NEW, REVISED, or NO-ACTION document remains unadvanced. WI-5207 correctly detects and reoffers that partial batch after worker exit, but does not make the provider adapter finish its assigned batch. Add trusted assigned-slug context and per-document publication state to each provider loop; accept only role-correct governed verdict publication for assigned slugs; reject wrong, duplicate, or unassigned slugs; continue until every assigned document is terminally advanced or a bounded actionable failure occurs. Preserve current dispatch_max_items, roles, eligibility, routing, TAFE, leases, allowances, and live-worker behavior. Require fresh substantive dispatcher-produced two-document proof after independent verification.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5545` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-202666237` - Summary
- `DELIB-20265391` - Verdict
- `DELIB-202666250` - Loyal Opposition Verification Verdict - WI-5245 Alibaba H Publisher Recovery

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718` - active project authorization covering `WI-5545`.

## Proposed Scope

- Load the trusted assigned-document set only through groundtruth_kb.bridge_dispatch_worker_context.build_worker_context_packet(self_only=True); provider adapters must not read dispatcher runtime files.
- Track governed verdict publication separately for every assigned slug, reject unassigned and duplicate slugs before publisher execution, and continue until every assigned latest NEW, REVISED, or NO-ACTION document has advanced.
- Preserve all current provider/model/session/operation allowances, dispatcher roles, eligibility, max-items, routing, TAFE state, leases, live workers, and canonical publisher/finalizer gates.
- Do not begin protected implementation until WI-5495, WI-5471, and every exact-target owner are terminal and a fresh matching claim plus implementation-start packet authorize the reconciled target bytes.

## Cross-Harness Disposition

- **A / Codex**: PB-only lane is unchanged and receives no provider-adapter behavior change.
- **D / Ollama**: Direct LO repair target; preserve max-items 2 and require genuine two-document proof.
- **F / OpenRouter**: Direct LO repair target through the shared cloud adapter; preserve max-items 2 and require genuine two-document proof.
- **B, C, E, H**: No role, eligibility, route, cap, provider, or runtime change.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused two-document D and F integration tests prove per-assigned-document completion and preserve current provider loop behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent GO, exact-target clearance, matching claim, implementation-start authorization, and canonical publication remain mandatory. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent verification executes focused and affected harness suites plus lint, format, compilation, and exact-diff checks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Fresh dispatcher-produced substantive D and F batches prove every assigned document advances through the canonical publisher. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Both provider adapter families receive equivalent assigned-document invariants while provider-specific transport behavior remains unchanged. |

## Acceptance Criteria

- A two-document D fixture and a two-document F fixture cannot complete after only one governed publication.
- Wrong, duplicate, and unassigned slugs fail closed before canonical publisher execution; one valid verdict advances only its matching assigned document.
- Final provider text is accepted only after all assigned documents have advanced; bounded failure remains actionable and never counts as completion.
- Fresh substantive dispatcher-produced two-document proof succeeds after independent VERIFIED and focused finalization without changing current topology or allowances.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
