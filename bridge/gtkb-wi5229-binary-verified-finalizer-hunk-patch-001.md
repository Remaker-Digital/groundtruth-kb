NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; owner-authorized WI-5229 binary VERIFIED finalizer repair proposal; A is PB-only
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Binary-aware VERIFIED Finalizer Hunk Patch Support

bridge_kind: prime_proposal
Document: gtkb-wi5229-binary-verified-finalizer-hunk-patch
Version: 001
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5229

target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source+test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the WI-5139-blocking VERIFIED finalizer gap by allowing explicitly reviewed binary patches for tracked include paths such as `groundtruth.db`, while preserving hunk-scoped atomicity, include-set coverage, reviewer-visible evidence, and unrelated-work exclusion.

This proposal does not restore or replace the live `groundtruth.db`. It only repairs the governed publication/finalization tooling so the already-reviewed WI-5139 restoration can later be finalized through the normal LO VERIFIED path without absorbing unrelated concurrent database state.

## Claim

Prime Builder proposes a bounded source/test implementation slice for `WI-5229`. The implementation will teach the provider-side `PublishBridgeVerdict` preflight and the canonical VERIFIED finalizer helper parity copies to accept reviewed binary-capable patch files for modified tracked include paths.

The repair remains fail-closed:

- modified tracked include paths still require explicit reviewed patch coverage;
- patch-touched paths must remain inside the VERIFIED include set;
- the disposable-index commit path remains authoritative;
- unrelated staged or worktree changes remain excluded;
- finalization still writes only the numbered VERIFIED verdict plus reviewed include paths;
- no direct bridge verdict file write bypass is introduced.

## Requirement Sufficiency

Existing governance requirements are sufficient. `WI-5229` captures the incident-specific finalizer defect and `DELIB-202666199` authorizes the bounded work item, PAUTH, and proposal path. The active implementation PAUTH cited above includes source, test, bridge, metadata, and governance-evidence mutation classes and excludes dispatcher mutation, destructive cleanup, credential lifecycle, production deployment, git history rewrite, external-system mutation, and git push.

A separate filing-only PAUTH, `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5229-IMPLEMENTATION-PROPOSAL-FILING`, was created by the generic filing service while checking proposal feasibility. It is not cited by this proposal and does not authorize implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `scripts/gtkb_bridge_writer.py`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

No `applications/Agent_Red/` path is targeted.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge artifacts and governed writer/finalizer paths remain the only status authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal must cite every relevant governing specification and map tests to those specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include executable tests derived from the linked requirements before VERIFIED.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provider and helper-authored bridge documents must retain real author/session provenance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes PAUTH, project, work item, and target path metadata.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/Claude/Cursor verify-helper copies must remain behaviorally equivalent for governed verification flows.
- `ADR-CROSS-HARNESS-PARITY-001` - equivalent verification-helper behavior must be projected across applicable harness surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity-sensitive helper changes require explicit cross-harness disposition and tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target-path and non-scope statements must preserve GT-KB root/application boundary discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, work items, bridge proposal, tests, and verification evidence must remain durable artifact surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must preserve traceability among artifacts, tests, reports, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - blocked, active, reviewed, and verified lifecycle states must stay explicit in bridge and MemBase artifacts.

## Prior Deliberations

- `DELIB-202666199` - owner authorized the incident-specific binary VERIFIED finalizer repair PAUTH/proposal and explicitly prohibited live DB replacement, commit alteration, staging, commit, push, deployment, credential changes, and source/test edits before bridge GO plus implementation-start.
- `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-003.md` - WI-5139 implementation report for the additive fleet MemBase carrier restoration.
- `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-blocker-verified-finalization.md` - independent D review found WI-5139 substantively ready for VERIFIED but blocked by the binary hunk-patch finalization gate.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-006.md` - existing hunk-scoped VERIFIED finalization path that introduced disposable-index and `--hunk-patch` behavior for text hunks.
- `bridge/gtkb-wi5224-provider-verdict-completion-contract-004.md` - current provider completion-contract implementation report; related to provider verdict publication but intentionally not sufficient to repair binary patch finalization.
- `WI-5125` - broader pure-state VERIFIED finalization model gap; related background, but not a substitute for this incident-specific binary patch parser/coverage fix.

## Owner Decisions / Input

- `DELIB-202666199` - owner authorization for this exact PAUTH/proposal path.
- No further owner decision is required before LO review.

## Cross-Harness Disposition

- Claude Code / `.claude/skills/verify/helpers/write_verdict.py`: in scope as the canonical verify-helper copy.
- Codex / `.codex/skills/verify/helpers/write_verdict.py`: in scope as a required behavior-parity copy for Codex verification helper use.
- Cursor / `.cursor/skills/verify/helpers/write_verdict.py`: in scope as a required behavior-parity copy because the current repo still carries the Cursor verify-helper projection.
- Antigravity, OpenRouter, Ollama, Alibaba, Goose: no direct helper-copy target is present under their harness surfaces for this file; their provider publication path calls `scripts/gtkb_bridge_writer.py` and the canonical finalizer, so they inherit behavior through the shared writer/finalizer contract.

No typed waiver is requested. The implementation report must prove the helper copies remain equivalent for the new binary-patch behavior and existing text-hunk behavior.

## Proposed Scope

- Update `scripts/gtkb_bridge_writer.py` so the provider-side VERIFIED preflight can recognize binary-capable reviewed patch files as coverage for modified tracked include paths without weakening uncovered-path denial.
- Update `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, and `.cursor/skills/verify/helpers/write_verdict.py` in parity so the canonical finalizer can read, validate, and apply binary-capable reviewed patch files while preserving the disposable index and include-set gates.
- Add focused tests in `platform_tests/scripts/test_lo_verified_commit_atomicity.py` for tracked binary include finalization, missing-patch denial, unrelated staged/worktree preservation, and existing text hunk behavior.
- Add focused tests in `platform_tests/scripts/test_gtkb_bridge_writer.py` for provider-side hunk coverage detection and denial semantics.

## Explicit Non-Scope

- Do not modify, replace, or byte-restore live `groundtruth.db`.
- Do not alter commit `08cbc0172ad77d6b4395f34498e5cb0abbe7465f`.
- Do not stage, commit, push, release, deploy, or change credentials.
- Do not change dispatcher routing, harness roles, provider credentials, or active lease/runtime state.
- Do not add a by-reference waiver or a direct finalization bypass.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused tests prove VERIFIED publication still uses the numbered bridge/finalizer path and binary patch support does not permit uncovered modified tracked include paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run proposal applicability preflight before filing and carry linked specifications into the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` and report spec-to-test mapping in the implementation report. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing provider/bridge writer tests remain green; no shortcut direct bridge verdict writer is introduced. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability and bridge-compliance preflights must pass with PAUTH, Project, Work Item, and inline JSON target paths present. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Assert the `.claude`, `.codex`, and `.cursor` helper copies expose equivalent binary patch parsing/application behavior. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Compare behavior across the `.claude`, `.codex`, and `.cursor` helper copies and keep provider harness behavior centralized through `scripts/gtkb_bridge_writer.py`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm changed paths remain inside `E:\GT-KB` and do not target adopter/application subtrees. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm the owner decision, work item, PAUTH, bridge proposal, tests, and implementation report remain durable linked artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm WI-5139 remains blocked pending VERIFIED finalizer repair, WI-5229 moves through bridge review/implementation/report states, and no terminal VERIFIED is claimed without LO finalization. |

Additional checks:

- `python -m ruff check scripts/gtkb_bridge_writer.py .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py`
- `python -m ruff format --check scripts/gtkb_bridge_writer.py .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py`

## Acceptance Criteria

- A reviewed binary patch for a tracked include path can be supplied to `PublishBridgeVerdict` / `finalize_verified_commit` and commit exactly the included work plus the VERIFIED verdict from a disposable index.
- A modified tracked binary include path without explicit reviewed patch coverage is denied before verdict publication/finalization mutation.
- Existing text hunk-patch finalization behavior remains green.
- Unrelated staged and worktree changes remain excluded from the final commit.
- Helper parity copies remain behaviorally aligned.

## Risks / Rollback

Risk is moderate because this touches the governed VERIFIED commit-finalization path. The main regression risks are accidentally weakening the reviewed-hunk coverage gate, accidentally staging whole binary files without explicit reviewed patch evidence, or breaking existing text hunk-patch finalization.

Rollback is a source/test revert of the WI-5229 implementation if LO review or verification finds a defect. Bridge files, work item/test records, deliberation records, and PAUTH rows are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`fix(governance):`
