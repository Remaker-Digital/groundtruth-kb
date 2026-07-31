NEW

# Defect-Fix Proposal - Align Codex interactive GO claims with the canonical open session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5256-codex-interactive-session-successor
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: 2026-07-15 runtime
author_model_configuration: Codex desktop interactive Prime Builder; active fleet-goal reconciliation; approval_policy=never; workspace=E:\GT-KB


Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5256-CODEX-SESSION-SUCCESSOR-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5256
Test: TEST-11411

target_paths: ["scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", "scripts/_kb_attribution.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_implementation_start_gate.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Repair the interactive Codex bridge-session identity handoff after a governed
session wrap. The bridge work-intent claim, canonical MemBase attribution, and
implementation-start ownership checks must select the one current open Codex
worker-session document when the persistent `CODEX_THREAD_ID` names its closed
predecessor. Explicit session IDs and dispatcher-composed run IDs retain their
current precedence. Closed, missing, concurrent, ambiguous, or role-conflicting
documents remain non-authoritative and fail closed.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-SESSION-ROLE-AUTHORITY-001` and
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` require document-authoritative
interactive role continuity; `GOV-FILE-BRIDGE-AUTHORITY-001`, the operation-time
authorization constraints, WI-5256, TEST-11411, and the active bounded PAUTH
define the change and verification boundary. No new owner requirement is
needed before independent Loyal Opposition review.

## Defect / Reproduction

On 2026-07-15 the Codex worker-session document
`harness-state/codex/session-envelopes/019f5f66-9582-7f03-a3f1-3c75e6bd9d0a.json`
was correctly closed by manual wrap at `05:23:21Z`. A successor session opened
at `05:28:32Z` as `A-2026-07-15T05-27-23Z` and is the sole current open Codex
envelope with Prime Builder provenance. The desktop process still exports the
persistent thread ID `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.

The canonical command
`python scripts/bridge_claim_cli.py claim gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift`
therefore selected the closed predecessor and failed before mutation with:

```text
ERROR: go_implementation claim requires a prime-builder harness; session
'019f5f66-9582-7f03-a3f1-3c75e6bd9d0a' resolves to worker session document
rejected: Worker role provenance requires an open session envelope.
```

The canonical backlog writer reproduced the same mismatch through
`scripts._kb_attribution.resolve_changed_by`. Supplying the exact current open
session ID as the documented explicit override made attribution succeed, which
isolates the defect to default interactive session selection rather than role,
project, work-item, or database state. A later explicit WI-5236 claim reached
the separate, already tracked WI-5240 PAUTH-vocabulary denial, confirming that
the session-provenance gate itself passed with the successor ID.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_session_id.py`, `scripts/bridge_claim_cli.py`, `scripts/_kb_attribution.py`, `scripts/implementation_authorization.py`, `platform_tests/scripts/test_gtkb_session_id.py`, `platform_tests/scripts/test_bridge_claim_cli.py`, `platform_tests/scripts/test_kb_attribution.py`, `platform_tests/scripts/test_implementation_start_gate.py`.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - role and claim authority must come from the exact validated open worker-session document.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge implementation remains gated by role-correct proposal, GO, claim, start, report, and verification states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the observed failure is preserved as WI-5256, TEST-11411, PAUTH, and this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all applicable behavioral and cross-cutting requirements are linked before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification requires executed successor and fail-closed regression evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the exact PAUTH, project, work item, test, and target set are machine-readable.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic evidence, not an avoidable owner question, resolves ordinary session selection.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and evidence remain in the GT-KB platform root.
- `GOV-STANDING-BACKLOG-001` - the newly observed defect remains visible until independently verified and committed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must self-enforce the claim/start gates even where native hooks are unavailable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair preserves traceability among session evidence, work item, test, proposal, report, and verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - candidate, authorized, GO, implemented, and verified states remain explicit.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - a resumed interactive role remains bound to its valid successor envelope without adopting another session.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - claim and implementation-start evaluate the selected live session and current PAUTH at operation time.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the resolver cannot turn a missing or closed document into implementation authority or bypass an independent GO.

## Prior Deliberations

- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` - Concurrent Codex task clobbers document-authoritative session envelope
- `DELIB-20263296` - GO - WI-4534 Role-Eligibility Guard on go_implementation Claims
- `DELIB-202666143` - Loyal Opposition Verdict — WI-5189 Document-Authoritative GO-Implementation Claim Eligibility
- `DELIB-20266137` - Owner authorization: drive 7 dispatcher-reliability WIs (Fixes-then-Phases); yield WI-4818 to concurrent session
- `DELIB-20263247` - WI-4522 Revised Proposal Review Verdict

## Owner Decisions / Input

- `DELIB-20260714-FLEET-GOAL-RESUME-CARRIER-REPAIR` - owner resumed the fleet goal and authorized governed work-item, test, PAUTH, bridge, implementation, verification, and commit carriers for defects found during the program.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5256-CODEX-SESSION-SUCCESSOR-20260715` - active source/test-only authorization for this exact eight-path slice.

## Proposed Scope

1. Add one shared, opt-in document-aware resolver in
   `scripts/gtkb_session_id.py`; preserve the existing pure environment
   resolver and its hook-safe behavior.
2. Preserve explicit `--session-id` and `GTKB_BRIDGE_POLLER_RUN_ID` precedence
   exactly. Headless dispatch identities must never be redirected to an
   interactive envelope.
3. For an ordinary interactive Codex candidate, keep the candidate when its
   exact worker-session document is open. When that exact document is closed,
   select a successor only when the per-harness current projection identifies
   the sole open worker-session document, the successor opened after the
   predecessor closed, and harness/role/subject/init evidence is consistent.
4. Return no successor on missing evidence, multiple open documents,
   contradictory timestamps, harness mismatch, role mismatch, or malformed
   JSON. Downstream document-authoritative role validation remains mandatory.
5. Integrate the shared selection into `bridge_claim_cli.py`,
   `_kb_attribution.py`, and `implementation_authorization.py` so claim holder,
   changed-by attribution, and implementation-start ownership use one session
   ID. Do not change bridge author-session metadata semantics in this slice.
6. Add focused regression coverage for the observed closed-predecessor/open-
   successor case and all fail-closed boundaries. Do not edit dispatcher
   runtime state, bridge state, lease files, eligibility, roles, models,
   credentials, or unrelated dirty files.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Resolver and claim tests prove one validated open successor is selected while closed, missing, ambiguous, and role-conflicting documents are denied. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and filed applicability/clause preflights pass; the exact PAUTH, project, work item, test, and eight targets remain linked. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start tests prove the resolved successor must own the live GO claim and no explicit or dispatcher identity is rewritten. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `TEST-11411` is implemented and the four focused test modules plus Ruff check/format execute after GO and implementation-start. |
| `SPEC-AUQ-POLICY-ENGINE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The deterministic CLI path works without an AUQ, remains inside the GT-KB root, and does not depend on unavailable native Codex hooks. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5256, TEST-11411, PAUTH, proposal, report, verdict, and focused commit preserve the complete defect lifecycle. |

Planned commands:

```text
python -m pytest platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/gtkb_session_id.py scripts/bridge_claim_cli.py scripts/_kb_attribution.py scripts/implementation_authorization.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/gtkb_session_id.py scripts/bridge_claim_cli.py scripts/_kb_attribution.py scripts/implementation_authorization.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_implementation_start_gate.py
```

## Acceptance Criteria

- `TEST-11411` passes for a closed `CODEX_THREAD_ID` document followed by one
  compatible current open Codex successor.
- The no-override WI-5236 claim reaches project-authorization evaluation rather
  than failing on the closed predecessor.
- Canonical backlog attribution resolves `prime-builder/codex` from the same
  selected open successor.
- Implementation-start ownership resolves the same session ID held by the
  work-intent claim.
- Explicit session IDs and `GTKB_BRIDGE_POLLER_RUN_ID` remain unchanged.
- Missing, malformed, closed-only, multiple-open, timestamp-conflicting,
  harness-conflicting, and role-conflicting cases fail closed.
- The full focused test command and Ruff check/format pass.
- No dispatcher/TAFE runtime, bridge state, lease, eligibility, registry,
  credential, deployment, release, push, or unrelated worktree mutation occurs.

## Risks / Rollback

The primary risk is accidentally mapping one interactive thread to another
concurrent Codex session. The implementation must therefore require a sole
compatible open successor and retain downstream document-authoritative role
validation; ambiguity is a denial, not a best-effort guess. A second risk is
weakening dispatch identity precedence, addressed by explicit tests that the
dispatcher run ID is never redirected.

Rollback is a focused revert of the four source and four test files. The
append-only WI/test/PAUTH/bridge evidence remains as audit history. Rollback
does not delete or rewrite worker-session documents.

## Files Expected To Change

- `scripts/gtkb_session_id.py`
- `scripts/bridge_claim_cli.py`
- `scripts/_kb_attribution.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_gtkb_session_id.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
