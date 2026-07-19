NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; sandbox=none
author_metadata_source: trusted Codex turn metadata

# Implementation Proposal - Add artifact-head envelope to the WI-5425 nonimpairment fixture

bridge_kind: prime_proposal
Document: gtkb-wi5561-nonimpairment-fixture-envelope-hunk
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5561

target_paths: ["platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py", "bridge/hunks/gtkb-wi5561-nonimpairment-fixture-envelope-hunks.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore four WI-5425 focused assertions by adding only the mandatory artifact-head envelope to their synthetic NEW proposal, with hunk-only ownership that preserves the foreign same-file WI-5425 implementation.

Work item description: Current platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py retains the exact foreign WI-5425 membership-isolation hunk at SHA-256 2CDF298965965B5867E1D76CB3CBFAE6B5A317DE6343013EACA8C44D8993A517, but later ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001 enforcement makes four focused assertions stop at the missing line-2 ::init and line-3 ::open envelope. Add only the canonical NEW responder/activity envelope to the synthetic _proposal fixture, preserve both production hook files byte-for-byte, and use a declared hunk patch so this child finalizes first without absorbing WI-5425. Then WI-5425 must rerun 14/14 and finalize its own remaining hunk separately.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5561` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`, `bridge/hunks/gtkb-wi5561-nonimpairment-fixture-envelope-hunks.patch`.

## Specification Links

- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - auto-linked governing or work-item specification.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666063` - Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)
- `DELIB-202666320` - Loyal Opposition Verdict - NO-GO (finalization-scoped) - WI-5113 Suppress Git console windows in VERIFIED finalization
- `DELIB-202666163` - GT-KB Loyal Opposition Verdict - gtkb-wi5205-no-action-consumer-parity - 005 (VERIFIED)
- `DELIB-202666555` - Loyal Opposition Proposal Review - GO - WI-5346 Restore WI-5254 PAUTH Amendment Preflight
- `DELIB-20260712-WI5205-FULL-GENERATED-ADAPTER-INCLUSION` - Owner decision: include full regenerated bridge adapters in WI-5205

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5561`.

## Proposed Scope

- Add exactly line 2 `::init gtkb lo` and line 3 `::open build` after the synthetic proposal's line-1 `NEW` token in `_proposal`; make no other test-code change.
- Treat the existing membership-isolation diff in the same file as foreign WI-5425 pre-start content at SHA-256 2CDF298965965B5867E1D76CB3CBFAE6B5A317DE6343013EACA8C44D8993A517.
- Create the declared patch artifact containing only the WI-5561 envelope-line addition relative to committed HEAD; it must exclude every WI-5425 line.
- Preserve `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` byte-for-byte at their shared SHA-256 6D8B98695A7854C87645B67FB58B4309FA9D5F0718F52886095923108A06D714.
- After independent VERIFIED and separate exact mechanical authority, finalize the WI-5561 hunk before WI-5425; the resulting worktree must retain only the foreign WI-5425 hunk in the shared test file.
- Do not mutate dispatcher/TAFE configuration, harness routing or eligibility, process lifetimes, credentials, groundtruth.db, Agent Red, or unrelated dirt.

## Cross-Harness Disposition

- **Codex A**: Prime Builder authors the governed fixture-only repair lifecycle; runtime behavior is unchanged.
- **Cursor E**: No runtime behavior change.
- **Claude Code B**: No runtime behavior change.
- **Antigravity C**: No runtime behavior change.
- **Ollama D**: No runtime behavior change.
- **OpenRouter F**: No runtime behavior change.
- **Alibaba H**: No runtime behavior change.
- **TAFE and dispatcher**: No configuration, routing, eligibility, role, cap, lease, or process-lifetime mutation.

## Pre-Start Ownership Evidence

- Current Git baseline at filing: `0bb45100ac922552aa4ec1c3879bc775e3e915a0`.
- Shared test-file pre-start SHA-256: `2CDF298965965B5867E1D76CB3CBFAE6B5A317DE6343013EACA8C44D8993A517`.
- The pre-start diff is foreign WI-5425 content and must not appear in the WI-5561 hunk patch.
- Active and template production hook SHA-256: `6D8B98695A7854C87645B67FB58B4309FA9D5F0718F52886095923108A06D714`.
- Current focused result: 10 passed and 4 envelope-preemption failures; Ruff lint/format and Git whitespace checks pass.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "after_behavior": "The synthetic NEW fixture carries the canonical responder/activity envelope and all 14 focused assertions reach their intended gates.",
  "applicability": "applicable",
  "baseline": {
    "focused_failed": 4,
    "focused_passed": 10,
    "foreign_same_file_owners": 1,
    "production_hook_files_changed": 0
  },
  "before_behavior": "Four nonimpairment fixture assertions stop at the artifact-head envelope gate before testing their intended behavior.",
  "canonical_authority": "ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001, DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001, WI-5561, and PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE.",
  "essential_context_preservation": "The proposal records the same-file ownership split, exact pre-start and production hashes, mandatory line order, hunk-only sequencing, and post-finalization WI-5425 preservation check.",
  "expected_result": {
    "focused_failed": 0,
    "focused_passed": 14,
    "foreign_hunks_absorbed": 0,
    "production_hook_files_changed": 0
  },
  "fail_closed_conditions": [
    "missing independent GO or matching claim/start",
    "pre-start file or production-hook hash drift",
    "focused test, Ruff, whitespace, or patch-application failure",
    "hunk patch contains any WI-5425 or unrelated line",
    "missing independent VERIFIED or exact mechanical authority"
  ],
  "hard_invariants": [
    "only the two canonical fixture-envelope lines enter the WI-5561 patch",
    "both production hook hashes remain unchanged",
    "the foreign WI-5425 hunk remains uncommitted by WI-5561",
    "no dispatcher, TAFE, harness, database, credential, or Agent Red mutation"
  ],
  "history_preservation": "WI-5425 and WI-5524 histories remain unchanged; the declared patch mechanically separates WI-5561 from the foreign same-file hunk.",
  "obsolete_guidance_disposition": "No production guidance is changed; the stale envelope-less synthetic fixture shape is replaced only in the governed test hunk.",
  "primary_route": "governed NEW proposal, independent GO, exact claim/start, two-line fixture edit plus declared hunk patch, independent VERIFIED, and separate exact hunk finalization",
  "provenance": "WI-5425 owns the foreign membership-isolation hunk; WI-5524 owns its already reported fixture batch; WI-5561 owns only this omitted fixture envelope.",
  "rollback": {
    "instructions": "Fail before finalization or reverse only the two fixture-envelope lines; never alter or discard the foreign WI-5425 hunk.",
    "test": "Recompute hashes, rerun 14 focused tests, and apply/check the declared patch against the recorded committed preimage."
  },
  "schema_version": 1,
  "self_descriptive_naming": "WI-5561, its slug, test title, target file, and hunk-patch filename all name the nonimpairment fixture-envelope repair."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` | Assert the synthetic NEW artifact has the canonical responder and activity envelope and the focused module passes 14/14. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require independent GO, matching claim/start, implementation report, and independent VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest, Ruff check, Ruff format --check, py_compile, git diff --check, and patch-application checks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` | Assert NEW remains line 1, ::init gtkb lo is line 2, and ::open build is line 3. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Rehash both production hooks, prove no production-byte change, and rerun the active/template focused module. |
| `GOV-WORK-TREE-HYGIENE-001` | Validate the declared hunk patch against HEAD and prove it excludes every WI-5425 line and unrelated path. |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` | Prove the exact hunk transaction preserves the foreign same-file change. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Embed exact hashes, commands, observed results, and patch identity in the implementation report. |

## Acceptance Criteria

- The focused nonimpairment module passes 14/14 for active and template hooks.
- The two production hook files remain byte-identical to the recorded SHA-256.
- The hunk patch applies cleanly to the declared committed preimage and changes only the two canonical fixture-envelope lines.
- Independent Loyal Opposition verifies the exact hunk boundary and confirms that the foreign WI-5425 membership-isolation hunk is excluded.
- Exact finalization commits only WI-5561 artifacts and leaves the shared test file dirty solely for WI-5425.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`
- `bridge/hunks/gtkb-wi5561-nonimpairment-fixture-envelope-hunks.patch`

## Recommended Commit Type

`feat`
