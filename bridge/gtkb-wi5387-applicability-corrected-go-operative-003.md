NEW

# WI-5387 implementation report: corrected-verdict operative resolution

bridge_kind: implementation_report
Document: gtkb-wi5387-applicability-corrected-go-operative
Version: 003
Responds to GO: bridge/gtkb-wi5387-applicability-corrected-go-operative-002.md
Approved proposal: bridge/gtkb-wi5387-applicability-corrected-go-operative-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5387-APPLICABILITY-CORRECTED-GO-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5387
Recommended commit type: fix

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

## Implementation Claim

Applicability preflight now treats the latest GO, NO-GO, or VERIFIED as
operative when it follows an earlier NO-ACTION and contains explicit
same-thread `Responds to`, `Corrects`, `Approved proposal`, `Reviewed`, or
`Verified` metadata. Ordinary proposal review precedence is unchanged, latest
standalone NO-ACTION remains operative, and latest WITHDRAWN remains terminal.

All source, tests, scratch evidence, and this report remain in-root under
`E:/GT-KB`; the numbered report resides under `E:/GT-KB/bridge`.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and the exact PAUTH
authorize this bounded carrier while retaining all bridge and finalization
gates. No new owner decision was required or inferred.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`

## Implementation Authorization Evidence

- Latest status was GO at version 002.
- Prime Builder acquired `go_implementation` claim row 31783.
- Finalized schema-v3 packet hash:
  `sha256:cc2d786412515e5988de73f9d2ae5b4d328c3f42886a2142fdd86e267b598c13`.
- Pre-start packet hash:
  `sha256:8ce26c352c04e89decac8bda08bc95aa975f48515a4b84608b79ebffa2347fa9`.
- Target validation authorized exactly the two declared files before edit.

## Specification-Derived Verification

| Governing requirements | Executed evidence and observed result |
| --- | --- |
| NO-ACTION semantics and bridge authority | Four focused resolver tests pass: corrected GO after NO-ACTION, later VERIFIED coherence, standalone NO-ACTION, and WITHDRAWN terminality. |
| Concrete linkage and stable evidence | The corrected-GO fixture selects version 003, harvests the intended spec links, passes applicability, and produces an identical packet hash across two builds. |
| Live tool coherence | On `gtkb-wi5299-reissued-finalizer-failure-repair`, applicability now selects version 007, matching clause preflight version 007. Both expose the same missing spec-to-test evidence instead of evaluating versions 006 and 007 separately. |
| Hygiene and in-root placement | Ruff check, Ruff format check, and `git diff --check` pass on exactly the two authorized targets. |
| Full-module baseline transparency | The complete module reports 26 passed and 5 failed. All five failures are pre-existing PAUTH-amendment assertions in untouched code paths; the current source has no `blocking_errors` implementation. This report does not claim whole-module green. |

## Commands Run And Observed Results

1. Focused resolver pytest selection over corrected, verified, standalone
   NO-ACTION, and WITHDRAWN cases: `4 passed, 27 deselected, 1 warning in 0.45s`.
2. Complete target module: `26 passed, 5 failed, 1 warning in 1.21s`.
   Failures are the five existing structured PAUTH-amendment tests; no WI-5387
   source or test hunk touches that behavior.
3. Ruff check: all checks passed.
4. Ruff format check: both files already formatted.
5. `git diff --check` on exact targets: exit zero.
6. Live WI-5299 applicability and clause preflights: both select version 007
   and both fail closed on its missing spec-derived command/result evidence.
7. Live WI-5387 applicability and clause preflights: pass with zero missing
   applicable specs and zero blocking clause gaps.

## Files Changed

- `scripts/bridge_applicability_preflight.py` - 23-line metadata-aware
  corrected-verdict exception.
- `platform_tests/scripts/test_bridge_applicability_preflight.py` - 77 lines
  of focused chain fixtures and assertions.
- This implementation report is the only additional durable artifact.

No dispatcher, TAFE, runtime, lease, credentials, Git finalization, release,
deployment, or unrelated source/test/configuration state was changed.

## Acceptance Criteria Status

- [x] Corrected GO after NO-ACTION is no longer shadowed.
- [x] Live applicability/clause preflight operative-file disagreement is removed.
- [x] Standalone latest NO-ACTION remains operative.
- [x] Latest WITHDRAWN remains terminal.
- [x] Packet hash is stable for identical fixture content.
- [x] Exact commands, observations, and hunk attribution are recorded.
- [ ] Independent Loyal Opposition verification remains pending.
- [ ] Git finalization remains separately gated.

## Risk And Rollback

The exception requires both an earlier NO-ACTION and explicit same-thread
verdict metadata, limiting accidental authority broadening. The remaining
baseline PAUTH test failures are visible and outside this scope. Rollback is an
exact governed revert of the two WI-5387 hunks.

## Loyal Opposition Asks

Independently inspect the metadata predicate, rerun the four focused cases and
the WI-5299 live comparison, confirm standalone NO-ACTION and WITHDRAWN remain
unchanged, and return VERIFIED only for the bounded resolver repair.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
