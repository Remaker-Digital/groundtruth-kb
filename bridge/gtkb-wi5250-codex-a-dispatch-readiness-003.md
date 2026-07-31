REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge drain

# Revised Defect-Fix Proposal - WI-5250 Codex A Dispatch Readiness Probe Classification

bridge_kind: prime_proposal
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 003
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-002.md
Supersedes proposal: bridge/gtkb-wi5250-codex-a-dispatch-readiness-001.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250

target_paths: ["scripts/verify_codex_dispatch.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Revision Claim

Prime Builder accepts the version 002 finding and aligns this proposal with canonical WI-5250 version 3. The current defect is a Python-child ACL probe readability divergence, not evidence that the Codex sandbox group, current-user allow ACE, or local ACL repair is missing.

The bounded repair will make verifier/runtime diagnostics distinguish probe execution or nested-read failure from an authoritative ACL result. It will never translate an unavailable or incomplete probe into false `sandbox_group.present=false` or false missing-allow conclusions.

## Current Reproduction

- `python scripts/verify_codex_dispatch.py --json` exits 1 with `errors_count=213`, `risky_deny_count=0`, sandbox group absent, both allow flags false, and `live_headless_reason=codex_no_window_verification_expired`.
- Direct Windows PowerShell `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` reads the same root ACL with `errors_count=0`, reports `CodexSandboxUsers` present with its allow ACE, reports the current-user allow ACE, and exits 1 only because two foreign-SID risky Deny ACEs are genuinely present.
- Direct `Get-Acl` and `icacls` also read the root ACL successfully.
- Controlled ordinary and `CREATE_NO_WINDOW` Python child launches both reproduce the 213 nested-read errors.

Therefore the safe implementation boundary is probe classification and propagation. The PowerShell repair script remains read-only diagnostic context and is removed from implementation targets.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and the current WI-5250 record already require truthful readiness evidence. This revision corrects an implementation diagnosis; it does not add an ACL policy or dispatch capability.

## In-Root Placement Evidence

All four mutation targets are under `E:\GT-KB\scripts\` or `E:\GT-KB\platform_tests\`. Read-only comparison may inspect `E:\GT-KB\scripts\repair_codex_dotdir_acl.ps1` and the local `.codex` ACL, but neither is a mutation target. No out-of-root file or live external dependency is introduced.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - readiness classification must be truthful and deterministic.
- `GOV-SESSION-ROLE-AUTHORITY-001` - A remains Prime Builder only; no LO authority is created.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires a fresh independent GO, claim, start packet, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries the complete governing set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the direct-versus-child divergence and false-absence regression map to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, and exact paths are present.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - source/test mutation remains operation-time gated.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not authorize ACL, runtime, or dispatcher mutation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the verifier must accurately model Codex's Windows child-process boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - evidence, WI, tests, proposal, implementation, and verdict stay linked.
- `GOV-STANDING-BACKLOG-001` - A readiness remains visible until current governed proof exists.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and evidence remain in the GT-KB root.

## Prior Deliberations

- `DELIB-202666203` authorizes the governed WI-5250 proposal and implementation flow.
- `DELIB-202666106` records prior Codex no-window readiness verification.
- `DELIB-202665843` records headless dispatch window hardening context.
- `DELIB-202665726` records headless-ineligible dispatch suppression verification.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-002.md` identifies the stale ACL/no-window framing corrected here.

## Owner Decisions / Input

No new owner input is required. This revision narrows the implementation to the evidence and exclusions already durable in WI-5250 version 3.

## Findings Addressed

### F1 - Proposal diagnosis was stale against WI-5250 version 3

Accepted and corrected. The proposal no longer treats child-probe false absence as evidence for ACL apply or local-group repair. It removes `scripts/repair_codex_dotdir_acl.ps1` from target paths and forbids no-window smoke refresh, direct Codex invocation, dispatcher state edits, and eligibility/config mutation.

## Proposed Implementation

1. Give the ACL probe a structured execution/readability state separate from parsed ACL findings.
2. Preserve authoritative booleans only when the probe completed with complete, parseable evidence. On timeout, child-process failure, malformed JSON, or nested unreadability, report `probe_available=false` (or the established equivalent), preserve the bounded error summary, and leave identity/allow conclusions unknown rather than false.
3. Keep genuine risky Deny ACE findings distinct from probe transport errors.
4. Propagate the classification through `verify_codex_dispatch.py` and the dispatcher readiness result so `codex_dispatch_not_ready` includes an actionable bounded reason without asserting absent identities.
5. Preserve expired no-window proof as a separate readiness blocker. Do not refresh it, launch Codex, or mint readiness evidence in this implementation.
6. Preserve A as PB-only and leave dispatcher selection, runtime JSON, leases, registry, eligibility, roles, routing, and allowances unchanged.

## Explicit Exclusions

- No ACL apply, owner/group/ACE mutation, or local-group repair.
- No mutation of `scripts/repair_codex_dotdir_acl.ps1`; it is diagnostic context only.
- No no-window smoke refresh or proof issuance.
- No direct Codex invocation or harness contact.
- No dispatcher config, runtime JSON, lease, lock, eligibility, role, route, model, allowance, or credential mutation.
- No deployment, release, Git push/history rewrite, destructive cleanup, or unrelated worktree mutation.

## Specification-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Probe failure is not false absence | Hermetic verifier tests inject timeout, subprocess failure, malformed JSON, and nested unreadability; identity and allow fields remain unknown/not-authoritative and diagnostics identify probe unavailability. |
| Direct-versus-child divergence | Fixture direct output contains present group/user allows and two risky denies while child output contains read errors; verifier reports divergence without recommending ACL apply. |
| Genuine ACL findings remain distinct | Complete fixture output with risky Deny ACEs remains a deterministic readiness failure with `probe_available=true`. |
| Expired no-window proof remains separate | Existing stale-proof tests continue to report expiry independently of ACL probe state and no refresh function is called. |
| Dispatcher propagation | Focused dispatcher tests assert stable `codex_dispatch_not_ready` classification and bounded reason fields for probe unavailable versus ACL deny. |
| Role and side effects | Tests prove A remains PB-only and no runtime/config/lease/proof mutation path is invoked. |
| Static quality | Ruff lint/format checks and `git diff --check` pass on the four declared paths. |
| Governance | Applicability and mandatory clause preflights pass on this exact revision before filing and again before the report. |

Minimum focused commands:

- `python -m pytest platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short`
- selected `platform_tests/scripts/test_dispatcher_runtime.py` Codex-readiness tests
- `python -m ruff check scripts/verify_codex_dispatch.py scripts/dispatcher_runtime.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py`
- `python -m ruff format --check scripts/verify_codex_dispatch.py scripts/dispatcher_runtime.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py`

## Acceptance Criteria

- Python-child probe failure cannot produce authoritative false group/user absence.
- Complete ACL evidence still distinguishes valid allows from risky deny ACEs.
- Expired no-window proof remains an independent, explicit blocker and is not refreshed here.
- Dispatcher diagnostics explain probe unavailable versus complete ACL denial without ambiguity.
- A remains PB-only and no ACL/runtime/dispatch state mutation occurs.
- All changes remain within the four PAUTH-covered source/test paths.
- Any future governed A dispatch proof is a separate dispatcher-controlled lifecycle step after this repair is independently VERIFIED.

## Pre-Filing Preflight Subsection

The governed revision helper must run applicability and mandatory clause preflights against this exact pending content. Filing is allowed only with no missing required specifications, no semantic blocking errors, and zero mandatory clause gaps.

## Risk And Rollback

The main risk is making a real ACL denial look like mere probe unavailability. Tests therefore require complete output with risky Deny ACEs to remain a hard readiness failure while only incomplete transport/readability evidence becomes unknown. Rollback is a focused revert of the four eventual source/test changes; bridge and WI evidence remains append-only.

## Recommended Commit Type

`fix`
