WITHDRAWN

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-directed append-only bridge retirement
author_metadata_source: explicit current-session owner decision

# WI-5657 Old-Chain Retirement

bridge_kind: operational_state_change
Document: gtkb-wi5657-protected-commit-superseded-verified
Version: 005
Date: 2026-07-28 UTC
Responds to: bridge/gtkb-wi5657-protected-commit-superseded-verified-004.md

## Withdrawal Rationale

The owner directed: "Continue v2 and retire the old chain."
`DELIB-202667520` records that exact instruction after the historical-chain
facts were corrected. This thread is strict-resolver-valid but ends at `NO-GO`
version 004. It is retired rather than revised because the clean
`gtkb-wi5657-terminal-finalization-recovery-v2` thread carries the current
singleton authorization, exact-session metadata, and bounded terminal-recovery
plan.

This `WITHDRAWN` version is an append-only lifecycle disposition. It does not
rewrite, delete, reinterpret, or verify versions 001 through 004, and it does
not authorize implementation work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202667520` - owner directs the clean v2 recovery to continue and this
  strict-valid old chain to be retired append-only.
- `DELIB-202667519` - prior authorization for the bounded WI-5657 terminal
  recovery; retained as provenance and not stretched to supply this corrected
  disposition.

## Effect

`WITHDRAWN` is terminal and non-actionable. The complete old chain remains
preserved as audit evidence. All further WI-5657 terminal-recovery work proceeds
only through `gtkb-wi5657-terminal-finalization-recovery-v2` after independent
Loyal Opposition review.

## Prohibited Effects

No source, test, configuration, registry, specification, direct database,
dispatcher, push, deployment, release, history-rewrite, or destructive-cleanup
operation is performed or authorized by this withdrawal.
