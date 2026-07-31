WITHDRAWN

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-directed append-only bridge retirement
author_metadata_source: explicit current-session owner decision

# WI-5458 Malformed Old-Chain Retirement

bridge_kind: operational_state_change
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-008.md

## Withdrawal Rationale

The owner directed: "Continue v2 and retire the old chain."
`DELIB-20260729-WI5458-V2-OLD-CHAIN-RETIREMENT` records that exact
instruction and its WI-5458 scope. The clean
`gtkb-wi5458-proposal-pauth-precedence-v2` thread is now the sole executable
continuation.

The original thread cannot be repaired in place. Version 007 contains
`Version: 007 (NEW; post-implementation report)` instead of exact metadata
`Version: 007`. The strict lifecycle resolver therefore raises
`WRONG_BRIDGE_VERSION_METADATA` before any correction-tail logic. This
withdrawal terminates routing authority; it does not cure, validate,
reinterpret, or authorize the malformed historical prefix.

## First-Line Role Eligibility Check

`scripts/bridge_lifecycle_resolver.py` classifies `WITHDRAWN` as a
Prime-or-owner-authored terminal status. The active session is Prime Builder,
harness A, session context `019f863a-acd3-7320-80c0-1831f0936cc0`.

## Specification Links

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Specification-Derived Verification

This is a lifecycle disposition, not an implementation report, so it claims no
source behavior and requires no source-test execution. Its deterministic
verification is limited to the affected governance state:

- `gt bridge show gtkb-wi5458-proposal-pauth-precedence --json --compact`
  must report version 009 with latest status `WITHDRAWN` after publication.
- `gt bridge show gtkb-wi5458-proposal-pauth-precedence-v2 --json --compact`
  must continue to report v2 version 001 `NEW`.
- The strict lifecycle resolver must continue to report
  `WRONG_BRIDGE_VERSION_METADATA` at old version 007; withdrawal must not be
  misrepresented as curing that prefix.
- `git status --short` over old versions 001 through 008 must remain empty,
  proving those audit artifacts were not rewritten.
- The three v2 implementation target paths must remain clean and unchanged.

## Owner Decisions / Input

- `DELIB-20260729-WI5458-V2-OLD-CHAIN-RETIREMENT` - owner directs the
  strict-valid v2 recovery to continue and the malformed old chain to be
  retired append-only.

## Effect

`WITHDRAWN` is terminal and non-actionable for file-based bridge routing.
Versions 001 through 008 remain byte-for-byte audit evidence. WI-5458 version
16 canonically links only
`bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md` and records this old
thread as retired and superseded. All further WI-5458 work proceeds only
through v2 after independent Loyal Opposition review.

## Prohibited Effects

This withdrawal grants no source, test, configuration, registry,
specification, PAUTH, project, dispatcher, TAFE, harness, Git, credential,
external-system, cleanup, deployment, or release authority. It does not mark
WI-5458 resolved and does not waive v2 GO, claim, implementation-start, or
independent verification requirements.
