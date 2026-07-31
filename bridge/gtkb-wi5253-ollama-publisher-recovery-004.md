NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed fleet stabilization; reasoning high

# Implementation Report - WI-5253 Ollama D Publisher Failure Recovery

bridge_kind: implementation_report
Document: gtkb-wi5253-ollama-publisher-recovery
Version: 004
Date: 2026-07-15 UTC
Responds to GO: bridge/gtkb-wi5253-ollama-publisher-recovery-003.md
Approved proposal: bridge/gtkb-wi5253-ollama-publisher-recovery-002.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5253-OLLAMA-PUBLISHER-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5253
target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]
Recommended commit type: fix:

## Implementation Claim

Prime Builder implemented the GO-approved D/Ollama publisher-recovery repair. Failed
`PublishBridgeVerdict` results now retain a whitespace-normalized,
credential-redacted diagnostic capped at 500 characters. The next publisher-only
correction includes that concrete reason, and exhaustion reports both the exact
attempt count and last bounded failure rather than a generic no-progress message.

If Ollama emits a non-publisher call while the recovery payload exposes only
`PublishBridgeVerdict`, the call is rejected before `dispatch_tool_call`, counted
against the same bounded recovery allowance, and followed by another publisher-only
correction while budget remains. Successful completion still requires a nonblank
governed `verdict_path`; successful publication clears the retained failure state.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - D must complete governed LO work or produce actionable failure evidence.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - governs D's guarded tool loop and fail-closed publisher path.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - recovered publication must preserve dispatcher session and model provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the governed publisher may append LO verdicts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires mapped deterministic verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, work item, and exact target paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires exact scope enforcement at implementation start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace GO, claim, or implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the observed D failure as a durable governed correction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the dispatch failure, WI, test, PAUTH, bridge chain, implementation, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the observed fleet failure to advance through the governed lifecycle.

## Owner Decisions / Input

- `DELIB-202666204` authorizes the WI-5253 governed proposal and implementation lifecycle.
- `DELIB-202666173` directs correction of proof-blocking defects found during the six-harness fleet program.
- The owner reported Ollama D at 31.2% remaining budget with a hard cap and a four-day reset. This is advisory routing data only; it did not alter implementation scope or governance.
- D remains `can_receive_dispatch=false` pending independent VERIFIED and a fresh governed post-fix D proof.

## Prior Deliberations

- `DELIB-202666204` - WI-5253 implementation authorization.
- `DELIB-202666173` - fleet proof and defect-correction directive.
- `DELIB-202666171` - governed provider verdict-publication context.
- `DELIB-20264376` - prior Ollama dispatch-failure hardening context.
- `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md` - GO-approved parent semantic recovery design, not reimplemented here.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-005.md` - VERIFIED fail-closed completion predecessor.
- `bridge/gtkb-wi5253-ollama-publisher-recovery-002.md` - approved revised proposal.
- `bridge/gtkb-wi5253-ollama-publisher-recovery-003.md` - distinct-session Loyal Opposition GO.

## Implementation Details

1. Added a 500-character publisher-diagnostic bound with whitespace normalization.
2. Applied the canonical GT-KB DB credential-pattern catalog before any retained failure reaches a provider prompt or terminal error.
3. Preserved the concrete governed publisher result when `verdict_path` is missing or publication raises.
4. Rejected non-publisher recovery tool calls before dispatch and counted each malformed turn against the publisher-recovery limit.
5. Continued to expose only `PublishBridgeVerdict` after recovery begins.
6. Reported exhaustion as `exhausted after <N> attempts; last failure: <bounded diagnostic>`.
7. Reset retained failure state only after a nonblank governed `verdict_path`.

## Files Changed

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

No shared cloud-provider loop, dispatcher, routing, eligibility, runtime JSON,
lease, lock, credential, deployment, release, push, or unrelated worktree path
was changed.

## Specification-Derived Verification

| Governing surface | Executed evidence |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001` | The 77-test focused Ollama suite proves successful recovery, bounded repeated publisher failure, bounded non-publisher schema violations, fail-closed completion, and existing tool-loop behavior. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Existing metadata tests remain green, including dispatcher session-id resolution and `author_harness_id: D` propagation through the governed publisher. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_bridge_review_bounds_nonpublisher_recovery_without_dispatch` proves rejected `Read` calls never reach `dispatch_tool_call`; publisher success still delegates to the canonical governed writer and requires a nonblank `verdict_path`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Two new tests and strengthened missing-path/repeated-failure assertions execute against the implementation; all 77 focused tests pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Claim row 31231 was acquired at `2026-07-15T14:50:11Z`; implementation-start packet finalized at `2026-07-15T14:50:16Z`; PAUTH evaluator returned `allowed` for exactly one source and one test path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5253 and its linked test, PAUTH, revised proposal, GO, implementation, report, and pending independent verdict preserve the live D failure lifecycle. |

## Commands Run And Observed Results

- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short --basetemp .pytest-A-wi5253-baseline` - pre-implementation baseline: 75 passed.
- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short --basetemp .pytest-A-wi5253-final` - final focused suite: 77 passed.
- `python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py` - all checks passed.
- `python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py` - 2 files already formatted.
- `git diff --check -- scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py` - passed.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery --json` - passed; no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery` - passed; zero must-apply evidence gaps and zero blocking gaps.

## Acceptance Criteria Status

- [x] Publisher exhaustion includes the exact bounded attempt count and the last concrete publisher error.
- [x] Retained publisher diagnostics use canonical credential redaction, whitespace normalization, and a 500-character cap.
- [x] A non-publisher call during publisher-only recovery is never executed and receives only bounded corrective opportunities.
- [x] Recovery payloads expose only `PublishBridgeVerdict` and include the prior bounded failure reason.
- [x] Completion is never accepted until the publisher returns a nonblank `verdict_path`.
- [x] Successful recovery clears retained failure state and preserves trusted author/session metadata.
- [x] Existing completion, publisher, guard, timeout, and allowance tests remain green.
- [x] Changes remain limited to the two declared paths and do not duplicate WI-5216 or WI-5245 scope.

## Risk And Rollback

The credential-pattern catalog is loaded dynamically to retain the Ollama shim's
fail-closed startup behavior. If it is unavailable, the harness emits a generic,
bounded diagnostic instead of exposing unredacted provider output. The remaining
provider risk is whether D follows the publisher-only schema in a genuine run;
the adapter-side rejection and attempt limit remain authoritative when it does
not.

Rollback reverts only the two focused source/test paths. WI-5253, its linked
test, PAUTH, proposal, GO, implementation report, and subsequent verification
remain append-only evidence.

## Recommended Commit Type

`fix`

## Loyal Opposition Asks

1. Verify the implementation against every linked specification and the exact command evidence.
2. Confirm that non-publisher recovery calls never reach dispatch, diagnostics are credential-safe and bounded, and successful completion still requires a nonblank governed `verdict_path`.
3. Return `VERIFIED` with atomic focused commit finalization if the implementation satisfies the GO; otherwise return `NO-GO` with concrete findings.
