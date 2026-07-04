NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5.5
author_model_version: Codex Desktop 2026-07-03
author_model_configuration: Codex Desktop interactive; owner init ::init gtkb pb; reasoning effort Extra High; governed bridge-proposal filing
author_metadata_source: interactive-env

# Implementation Proposal - WI-4975 claimed-path subpath overmatch repair

bridge_kind: prime_proposal
Document: gtkb-wi4975-claimed-path-subpath-overmatch
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4975

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: skill-helper
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair a second WI-4975 claimed-path extraction defect in the atomic VERIFIED finalization helper. The previous WI-4975 fix preserved leading-dot directories such as `.claude/`; the newly observed failure is different: the report path parser can begin a plain-path match in the middle of a larger repo path. In `bridge/gtkb-wi5000-impl-auth-quarantine-health-pass-004.md`, Loyal Opposition observed that a valid report path, `platform_tests/scripts/test_bridge_dispatch_config.py`, also produced the bogus claimed path `scripts/test_bridge_dispatch_config.py`, causing `write_verdict.py --finalize-verified` to fail during `git add`.

This proposal requests a narrow parser-boundary correction and regression coverage across the existing Claude, Codex, and Cursor verify helper copies.

## Claim

Prime Builder proposes to fix the helper parser so plain repo-path tokens are not matched as suffixes of longer repo paths, while preserving the intended extraction of legitimate `scripts/...`, `platform_tests/...`, `groundtruth-kb/...`, `.claude/...`, `.codex/...`, and `.cursor/...` paths.

## Requirement Sufficiency

Existing requirements sufficient. WI-4975 remains the active backlog item for `write_verdict.py` claimed-path extraction correctness, and the active finalization-tooling project authorization covers skill-helper and test changes for WI-4975.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, `.cursor/skills/verify/helpers/write_verdict.py`, and `platform_tests/skills/test_verified_finalization_validation_hardening.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and the atomic VERIFIED finalization contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - records the observed verification-tooling failure as governed bridge work instead of a one-off workaround.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links and spec-derived verification before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the helper exists to enforce VERIFIED verification and commit-finalization evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the proposal relies on the active finalization-tooling project authorization and keeps implementation within target paths.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner decision is requested; existing owner/project authorization evidence is cited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active work remains within the GT-KB project root.
- `GOV-STANDING-BACKLOG-001` - WI-4975 is the backlog authority for this repair.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed helper paths and self-enforcement for bridge writes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, fix, tests, and verification evidence must be durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the WI-5000 NO-GO creates a lifecycle trigger for this finalization-tooling follow-up.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface helper changes require explicit parity disposition.
- `ADR-CROSS-HARNESS-PARITY-001` - behavior must stay aligned across the supported harness helper copies.

## Prior Deliberations

- `bridge/gtkb-finalization-tooling-batch-001.md` - approved batch proposal covering WI-4974, WI-4975, and WI-4976.
- `bridge/gtkb-finalization-tooling-batch-002.md` - Loyal Opposition GO for the original finalization-tooling batch.
- `bridge/gtkb-finalization-tooling-batch-003.md` - implementation report for the original WI-4975 leading-dot path preservation fix.
- `bridge/gtkb-finalization-tooling-batch-004.md` - VERIFIED verdict for the original finalization-tooling batch.
- `bridge/gtkb-wi5000-impl-auth-quarantine-health-pass-004.md` - newly observed NO-GO evidence: helper extracted nonexistent `scripts/test_bridge_dispatch_config.py` from `platform_tests/scripts/test_bridge_dispatch_config.py`.
- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - owner directive and project authorization for the finalization-tooling batch.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal authorizing continued bridge-dispatch stability repair.
- _No additional Deliberation Archive hits were found for the exact WI-4975 subpath-overmatch failure during a targeted search for `WI-4975 write_verdict claimed path subpath overmatch platform_tests scripts`._

## Owner Decisions / Input

- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - owner authorized the finalization-tooling batch and the active PAUTH covers WI-4975.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed continued bridge/dispatcher stabilization with Claude Code and Ollama as active Loyal Opposition and Codex as active Prime Builder.
- No new owner decision is required for this narrow parser-regression repair.

## Cross-Harness Disposition

- Claude Code (B): `.claude/skills/verify/helpers/write_verdict.py` is the canonical helper used by Claude Loyal Opposition finalization. It must receive the parser-boundary repair.
- Codex (A): `.codex/skills/verify/helpers/write_verdict.py` must receive the same behavioral repair so Codex verification tooling does not diverge from Claude.
- Cursor (E): `.cursor/skills/verify/helpers/write_verdict.py` must receive the same behavioral repair because the Cursor verify skill copy exists and participates in cross-harness parity.
- Antigravity (C), Ollama (D), and OpenRouter (F): no separate helper copy is targeted by this proposal. Their parity obligation is behavioral through the shared bridge protocol and by avoiding direct harness-to-harness finalization workarounds.
- No owner waiver is requested. The implementation must keep the three helper copies behaviorally aligned, and the regression test must exercise the helper copies listed by `HELPER_COPIES`.

## Proposed Scope

1. Update the plain-path token matching in the three `write_verdict.py` helper copies so a valid longer path such as `platform_tests/scripts/test_bridge_dispatch_config.py` does not additionally yield `scripts/test_bridge_dispatch_config.py`.
2. Preserve extraction for legitimate standalone repo paths and backtick-wrapped paths.
3. Add a regression to `platform_tests/skills/test_verified_finalization_validation_hardening.py` that proves the claimed-path parser keeps the full `platform_tests/scripts/...` path and does not extract the `scripts/...` suffix.
4. Do not change the commit-finalization transaction model, staging behavior, predecessor-chain behavior, or bridge verdict semantics.

## Acceptance Criteria

- The helper parser no longer extracts a `scripts/...` suffix from `platform_tests/scripts/...`.
- Existing leading-dot directory preservation behavior remains covered and passing.
- Claude, Codex, and Cursor helper copies remain behaviorally aligned for the claimed-path parser.
- Focused tests and Ruff gates pass for the touched helper/test files.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; atomic VERIFIED finalization path correctness | Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp=.gtkb-state/pytest-wi4975-subpath`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Add or update a test that parameterizes across the Claude, Codex, and Cursor helper copies and verifies identical claimed-path extraction behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; bridge helper correctness | Run `groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/skills/test_verified_finalization_validation_hardening.py`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; code-quality floor | Run `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/skills/test_verified_finalization_validation_hardening.py`. |

## Risk And Rollback

Risk is moderate because this helper gates terminal VERIFIED commits. The proposed change is intentionally narrow and test-driven: add a left-boundary condition for plain-path matches without changing explicit backtick extraction. Rollback is a single commit revert after Loyal Opposition verification if the parser change blocks legitimate paths.

## Pre-Filing Checks

- `gt deliberations search "WI-4975 write_verdict claimed path subpath overmatch platform_tests scripts" --json --limit 10` returned no direct Deliberation Archive matches.
- `gt bridge threads --wi WI-4975 --json --compact` returned `match_count: 0`.
- `gt bridge show gtkb-finalization-tooling-batch --json --compact` confirmed the original finalization-tooling batch is terminal VERIFIED.
