NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-06-06Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Fix 5 WI-5651 skill-rename live breaks in bridge finalization and dispatch code

bridge_kind: prime_proposal
Document: gtkb-wi5661-terminal-verdict-recovery
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661

target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "scripts/per_thread_finalization_repair.py", "scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover WI-5661 after an untracked false VERIFIED verdict: quarantine dirty work, repair all six original live breaks from a clean authorized baseline, and require committed finalization evidence.

Work item description: WI-5651 skill rename (bridge->gtkb-bridge, verify->gtkb-verify, bridge-propose->gtkb-bridge-propose under .claude/skills/) left 5 stale path constants in live load-bearing code that are actively broken or degraded (verified via workflow w0yjqag3h 2026-07-24): (1) scripts/gtkb_bridge_writer.py:630 provider VERIFIED finalizer path fails closed, breaking Ollama/OpenRouter/Alibaba verdict finalization; (2) .claude/hooks/bridge-axis-2-surface.py:119 plus tracked mirror config/hooks/gtkb-bridge-axis-2-surface.py:119 cause axis-2 Claude-native bridge surfacing FileNotFoundError every turn; (3) scripts/per_thread_finalization_repair.py:24 stale sys.path breaks the module on import; (4) scripts/harness_parity_phase2.py:448-454 stale surfaces dict yields false needs_adapter parity reports; (5) scripts/verify_antigravity_dispatch.py:42-43 stale verdict-evidence anchor paths. Fix each bare skill-dir segment to the gtkb- prefixed name (fallback-tuple resolver where it is a live import). Tier-0 fast-lane slice of the WI-5651 reference-sweep project; remaining tiers become the follow-on project.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5661` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `.claude/hooks/bridge-axis-2-surface.py`, `config/hooks/gtkb-bridge-axis-2-surface.py`, `scripts/per_thread_finalization_repair.py`, `scripts/harness_parity_phase2.py`, `scripts/verify_antigravity_dispatch.py`.

## Specification Links

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

## Prior Deliberations

- `DELIB-20265732` - Loyal Opposition Verification Verdict: WI-4691 Verified Finalization Repair
- `DELIB-202665679` - Loyal Opposition Verdict -- NO-GO (implementation blocked, cross-harness parity violated)
- `DELIB-202665675` - Loyal Opposition Verdict -- GO (proposal approved with conditions)
- `DELIB-202666416` - Loyal Opposition VERIFIED Verdict - WI-5236 Starvation Fixture Oldest-First (Implementation Report)
- `DELIB-202666934` - Loyal Opposition Corrected Verdict - NO-GO - WI-5269 Activity-Envelope Authority Validators (Predecessor/Dirty-Target Hold Confirmed)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724` - active project authorization covering `WI-5661`.

## Proposed Scope

- Quarantine the untracked terminal verdict and all dirty claimed implementation files; do not stage, attribute, or finalize them.
- Re-establish a clean, authorized six-finding implementation slice from current committed baseline, with each mirror/source pair repaired together.
- Require a governed commit and complete commit-finalization evidence before any independent LO VERIFIED verdict.

## Cross-Harness Disposition

- **Claude**: Repair the tracked hook and its config source-of-record as a coupled pair.
- **Other harnesses**: No harness-specific hook mutation; validate the shared scripts and adapters through the mapped tests.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5661; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5651 skill rename (bridge->gtkb-bridge, verify->gtkb-verify, bridge-propose->gtkb-bridge-propose under .claude/skills/) left 5 stale path constants in live load-bearing code that are actively broken or degraded (verified via workflow w0yjqag3h 2026-07-24): (1) scripts/gtkb_bridge_writer.py:630 provider VERIFIED finalizer path fails closed, breaking Ollama/OpenRouter/Alibaba verdict finalization; (2) .claude/hooks/bridge-axis-2-surface.py:119 plus tracked mirror config/hooks/gtkb-bridge-axis-2-surface.py:119 cause axis-2 Claude-native bridge surfacing FileNotFoundError every turn; (3) scripts/per_thread_finalization_repair.py:24 stale sys.path breaks the module on import; (4) scripts/harness_parity_phase2.py:448-454 stale surfaces dict yields false needs_adapter parity reports; (5) scripts/verify_antigravity_dispatch.py:42-43 stale verdict-evidence anchor paths. Fix each bare skill-dir segment to the gtkb- prefixed name (fallback-tuple resolver where it is a live import). Tier-0 fast-lane slice of the WI-5651 reference-sweep project; remaining tiers become the follow-on project.",
  "after_behavior": "Recover WI-5661 after an untracked false VERIFIED verdict: quarantine dirty work, repair all six original live breaks from a clean authorized baseline, and require committed finalization evidence.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5661",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      ".claude/hooks/bridge-axis-2-surface.py",
      "config/hooks/gtkb-bridge-axis-2-surface.py",
      "scripts/per_thread_finalization_repair.py",
      "scripts/harness_parity_phase2.py",
      "scripts/verify_antigravity_dispatch.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "Recover WI-5661 after an untracked false VERIFIED verdict: quarantine dirty work, repair all six original live breaks from a clean authorized baseline, and require committed finalization evidence.",
    "scope": [
      "Quarantine the untracked terminal verdict and all dirty claimed implementation files; do not stage, attribute, or finalize them.",
      "Re-establish a clean, authorized six-finding implementation slice from current committed baseline, with each mirror/source pair repaired together.",
      "Require a governed commit and complete commit-finalization evidence before any independent LO VERIFIED verdict."
    ],
    "acceptance_criteria": [
      "All six original stale skill-reference findings have concrete source and test evidence; no finding is deferred without a separately linked governed work item.",
      "The hook and its config source-of-record resolve the same canonical managed helper path.",
      "The implementation diff contains no unrelated bridge responder-routing change.",
      "The closure evidence names an immutable commit containing only the governed recovery slice and passes its mapped tests."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- All six original stale skill-reference findings have concrete source and test evidence; no finding is deferred without a separately linked governed work item.
- The hook and its config source-of-record resolve the same canonical managed helper path.
- The implementation diff contains no unrelated bridge responder-routing change.
- The closure evidence names an immutable commit containing only the governed recovery slice and passes its mapped tests.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `.claude/hooks/bridge-axis-2-surface.py`
- `config/hooks/gtkb-bridge-axis-2-surface.py`
- `scripts/per_thread_finalization_repair.py`
- `scripts/harness_parity_phase2.py`
- `scripts/verify_antigravity_dispatch.py`

## Recommended Commit Type

`feat`
