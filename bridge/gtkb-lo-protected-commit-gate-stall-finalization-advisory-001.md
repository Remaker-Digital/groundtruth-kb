ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory — protected-commit gate can strand VERIFIED finalization

bridge_kind: governance_advisory
Document: gtkb-lo-protected-commit-gate-stall-finalization-advisory
Version: 001
Author: Loyal Opposition (Codex A)
Date: 2026-07-29 UTC

## Source

Two governed VERIFIED finalizers reached `git commit` and then stalled in the
pre-commit hook on 2026-07-29, after publishing their terminal bridge files but
before moving `HEAD`:

- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-014.md`
- `bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-004.md`

In each case the hook reached `python scripts/check_protected_commit_authorization.py --staged` after the secret, inventory, narrative-evidence, and Ruff-format gates passed. The protected checker remained active without a result or progress output. Direct reproduction against WI-5670's exact disposable-index cohort showed the same stall.

`scripts/check_protected_commit_authorization.py:2350-2357` runs the staged path through `_index_snapshot` and `_evaluate_selected`; the full snapshot/path traversal and bridge/registry evaluation have no enclosing wall-clock bound. Its Git subprocess timeout (`:285-311`) therefore does not bound the complete checker.

## Claim

The pre-commit protected-authorization gate has an unbounded full-check path
that can leave an atomically published terminal `VERIFIED` uncommitted. This
is distinct diagnostic evidence for the broader interruption/recovery issue in
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Owner Decision Needed

None for advisory capture. A future implementation proposal must select and
document its timeout/recovery semantics before it changes the security gate.

## Recommended Prime Action

File a scoped bridge proposal that:

1. Places a fail-closed wall-clock bound around the full
   `check_protected_commit_authorization.py --staged` evaluation, not only Git
   subprocesses.
2. Emits phase/progress evidence sufficient to distinguish a slow snapshot from
   a stalled gate.
3. Makes VERIFIED finalization preflight the full commit gate before publishing
   a terminal bridge capability, or provides a governed resume path when that
   preflight cannot complete.
4. Adds regression coverage with a deliberately delayed snapshot/evaluation so
   timeout, cleanup, and no-stranded-publication behavior are deterministic.

## Prior Deliberations And Related Evidence

- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001` — broader published-but-uncommitted terminal recovery defect; this advisory identifies the protected-commit gate as the observed stall point.
- `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — owner selected exact recovery for the two transactions affected in this run; it does not approve a gate implementation change.
- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-014.md` and `bridge/gtkb-wi5588-advisory-consumers-bridge-only-discovery-004.md` — reproduced finalizer interruption evidence.

## Classification Slot

`adapt`.

The remedy is a GT-KB-native reliability change to an existing mandatory gate.

## Non-Approval Semantics

This advisory authorizes no security-gate bypass, source/configuration change,
staging, commit, push, release, dispatcher operation, or deployment. It records
future work only.
