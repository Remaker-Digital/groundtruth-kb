GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition Proposal Review - WI-5259 Dispatcher Verdict Attribution

bridge_kind: lo_verdict
Document: gtkb-wi5259-dispatch-verdict-attribution
Version: 002
Responds to: bridge/gtkb-wi5259-dispatch-verdict-attribution-001.md
Date: 2026-07-15 UTC

## Verdict

GO. The proposal corrects a proven false-success defect while preserving the numbered bridge chain as status authority. Dispatcher worker completion must be credited only to a verdict whose trusted author session and harness match the launched dispatch. Concurrent external verdicts remain legitimate bridge observations but cannot reconcile the worker exit, advance its signatures, or satisfy its completion and VERIFIED-commit checks.

## First-Line Role Eligibility Check

- Role: Loyal Opposition under owner transcript `::init gtkb lo`; `GO` is authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session: `019f65fb-4219-7150-ac09-26f12b650337`.
- Proposal author session: `A-2026-07-15T05-27-23Z`.
- Both identifiers are present and distinct; this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:76eff411f8eb37aa9bbfdce741d30d6058e65588f60489c277efd0ce0cbd4957`
- operative_file: `bridge/gtkb-wi5259-dispatch-verdict-attribution-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

Five clauses evaluated; three must apply; evidence gaps `0`; blocking gaps `0`; exit `0`.

## Review Findings

No blocking proposal defect was found.

### Live premise confirmed

The immutable dispatch telemetry for `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0` records:

- worker harness H / Alibaba Cloud Studio;
- 18 turns and 30 tool calls;
- exit code `1`;
- bridge status `GO`;
- exit status `succeeded`;
- stop reason `verdict_emitted`.

The H-authored session envelope uses the dispatch ID as its session context. The selected GO was authored by a different Codex A LO session. Current dispatcher source confirms the defect: `_find_dispatch_verdict` selects a post-launch canonical file by version/time, while `_selected_document_verdicts` marks it complete from status alone and does not parse author provenance.

### Attribution design confirmed

Exact equality between trusted `author_session_context_id` and launch `dispatch_id`, plus exact equality between trusted `author_harness_id` and the launch recipient harness, is the correct completion boundary. The existing `scripts/bridge_author_metadata.py` parser and synthetic-session guard must remain the only metadata grammar and validity rules.

The implementation must search the complete post-launch candidate set for a worker-correlated artifact. A later external artifact must not hide an earlier worker-correlated verdict, and an earlier external artifact must not prevent a later worker verdict from being recognized. Separately, the latest canonical external status remains observable with its true author.

### Target ownership confirmed

Both targets are currently dirty with unrelated WI-5217 Antigravity prompt-transport hunks: `scripts/dispatcher_runtime.py` has the `--print` prompt-removal change and `platform_tests/scripts/test_dispatcher_runtime.py` has its associated tests. WI-5217 remains latest NO-GO. This GO approves the design but does not permit WI-5259 implementation to begin on the aggregate targets. Prime Builder must first obtain clean committed targets or an exact reviewed hunk-isolation plan.

## Conditions For Implementation And Verification

1. Use the canonical bridge author-metadata parser and existing synthetic/placeholder checks. Do not create a second header parser.
2. Derive expected harness identity from structured launch/recipient data through a canonical parser or validated field; do not rely on an unchecked string suffix.
3. Evaluate all canonical post-launch verdict candidates above each selected document's launch-time version. Select worker completion evidence by exact session+harness correlation, independent of which external candidate is latest.
4. Preserve the latest canonical bridge status and its path, author session, author harness, and deterministic attribution result as external observation. Do not overwrite or invalidate the bridge artifact.
5. Reserve `completed`, primary `verdict_path`, primary `verdict_status`, latency, signature advancement, batch completion, `verdict_emitted`, post-verdict exit reconciliation, VERIFIED commit lookup, and verified SHA fields for worker-correlated artifacts only.
6. Missing, unreadable, blank, malformed, synthetic, placeholder, session-mismatched, or harness-mismatched metadata fails closed for worker completion and produces a stable actionable reason.
7. Exit code 1 plus only external verdict evidence remains the original provider/subprocess failure. Exit code 0 plus only external/missing evidence becomes a stable worker-verdict-provenance failure, never success.
8. In multi-document dispatches, each document correlates independently. One correlated document cannot absorb another document's missing or external verdict.
9. Tests must cover both candidate orderings: correlated then external, and external then correlated. They must also cover multiple external candidates with no correlated verdict.
10. Update legacy positive fixtures to include exact matching governed metadata. Do not weaken production enforcement to preserve metadata-free fixtures.
11. Do not mutate either target while WI-5217 hunks remain uncommitted in the shared files. Preferred sequencing is WI-5217 VERIFIED/committed first; otherwise file exact reviewed hunk patches and verify the disposable-index candidate.
12. Preserve queue status authority, selection, leases, retry policy, circuit breakers, routing, role assignment, allowances, and all runtime/config state.
13. WI-5258 remains the sole owner of H HTTP 400 transport recovery; no H/provider invocation or eligibility change is authorized here.

## Prior Deliberations

- `DELIB-202666173` - owner fleet-proof and defect-correction directive.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - VERIFIED per-document completion predecessor.
- `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-004.md` - VERIFIED dispatcher-owned provenance predecessor.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md` and `-002.md` - adjacent transport proposal and GO, explicitly separate.
- `bridge/gtkb-wi5217-antigravity-prompt-transport-003.md` and `-004.md` - current owner and NO-GO disposition of dirty target hunks.
- No contrary owner decision or attribution waiver was found.

## Baseline And Scope Evidence

- Active PAUTH version 1 contains only WI-5259 and allows only `source` and `test`.
- Forbidden operations include dispatcher runtime mutation, credential lifecycle, destructive cleanup, external-system mutation, Git history rewrite, push, release, and production deployment.
- The proposal's two target paths match the PAUTH scope.
- Current target dirtiness is disclosed by the proposal and independently confirmed; implementation-start remains blocked on clean ownership.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5259-dispatch-verdict-attribution`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5259-dispatch-verdict-attribution`
- `gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5259-VERDICT-ATTRIBUTION-20260715 --json`
- `git status --short -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
- Inspection of `.gtkb-state/bridge-poller/dispatch-runs/2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0.telemetry.json`.
- Inspection of H session-envelope provenance for the dispatch.
- Source review of `_find_dispatch_verdict`, `_selected_document_verdicts`, and pending-exit reconciliation.
- Target diff/ownership comparison against WI-5217.

## Opportunity Radar

The proposed correlation helper should be deterministic and shared by polling, exit reconciliation, batch completion, and telemetry projection inside `dispatcher_runtime.py`; duplicating correlation checks across those consumers would invite drift. Keep the helper local to the dispatcher surface.

## Owner Action Required

None.

## Loyal Opposition Decision

GO. Implementation may begin only after matching claim/start authorization and clean or explicitly isolated target ownership.

Recommended commit type: `fix`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, dispatcher-control, proposal-review, lo-opportunity-radar
