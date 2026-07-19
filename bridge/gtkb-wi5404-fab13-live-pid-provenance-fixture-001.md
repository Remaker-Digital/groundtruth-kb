NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Repair FAB-13 live dispatch retention fixture provenance

bridge_kind: prime_proposal
Document: gtkb-wi5404-fab13-live-pid-provenance-fixture
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5404

target_paths: ["platform_tests/scripts/test_fab13_retention_policy.py", "bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair only the stale FAB-13 live-PID fixture by adding the production-required process create-time provenance sidecar, while preserving the concurrent WI-5396 exact-root hunks through a canonical hash-declared hunk patch and deferring Git finalization to separate authority.

Work item description: platform_tests/scripts/test_fab13_retention_policy.py::test_dispatch_runs_prune_preserves_live_pid_artifacts writes live.pid and live.stdout.log for os.getpid() but omits the matching live.create_time_epoch sidecar now required by scripts/dispatcher_runtime.py::_run_artifact_live. The deterministic test therefore deletes both artifacts and fails, while the production requirement to match PID create-time correctly protects against PID reuse. Repair the fixture to record exact process provenance through the production-compatible helper or an equivalent exact timestamp; do not weaken production liveness or provenance checks. Preserve the concurrent WI-5396 exact-root additions in the same test file.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5404` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_fab13_retention_policy.py`, `bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch`.

## Specification Links

- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666190` - Verdict Rationale
- `DELIB-202666128` - gtkb-wi5181-report-metrics-enrichment — Loyal Opposition Verdict (VERIFIED)
- `DELIB-202666188` - WI-5220 - Dispatcher test fixture parity VERIFIED finalization
- `DELIB-20263252` - Verdict
- `DELIB-20266135` - Owner decision: draft and file the WI-4818 storm-watchdog Cursor-coverage fix

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5404`.

## Proposed Scope

- After independent GO and exact claim/start, modify only test_dispatch_runs_prune_preserves_live_pid_artifacts so the fixture writes the current process create-time sidecar required by the production retention contract; do not change production code or weaken PID provenance.
- Preserve the current WI-5396 exact-root hunks in platform_tests/scripts/test_fab13_retention_policy.py byte-for-byte as foreign work and create bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch containing only the WI-5404 fixture delta against HEAD.
- Require the implementation report to declare the canonical patch path, SHA-256, byte size, preimage/postimage evidence, and hunk-patch finalization shape; any local commit remains deferred to separate exact mechanical authority.
- Do not mutate dispatcher or TAFE configuration/runtime, harness routing/eligibility/roles, production source, credentials, deployment, release, Git history, or unrelated worktree paths.

## Cross-Harness Disposition

- **Codex A**: No runtime behavior change; Prime Builder files and, only after GO/start, implements the bounded test fixture hunk.
- **Claude Code B**: No runtime behavior or target-path change.
- **Antigravity C**: No runtime behavior or target-path change.
- **Cursor E**: No runtime behavior or target-path change.
- **Ollama D**: No runtime behavior or target-path change.
- **OpenRouter F**: No runtime behavior or target-path change.
- **Alibaba H**: No runtime behavior or target-path change.
- **TAFE and dispatcher**: No configuration, runtime, routing, eligibility, role, cap, or process-lifetime mutation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5404; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "platform_tests/scripts/test_fab13_retention_policy.py::test_dispatch_runs_prune_preserves_live_pid_artifacts writes live.pid and live.stdout.log for os.getpid() but omits the matching live.create_time_epoch sidecar now required by scripts/dispatcher_runtime.py::_run_artifact_live. The deterministic test therefore deletes both artifacts and fails, while the production requirement to match PID create-time correctly protects against PID reuse. Repair the fixture to record exact process provenance through the production-compatible helper or an equivalent exact timestamp; do not weaken production liveness or provenance checks. Preserve the concurrent WI-5396 exact-root additions in the same test file.",
  "after_behavior": "Repair only the stale FAB-13 live-PID fixture by adding the production-required process create-time provenance sidecar, while preserving the concurrent WI-5396 exact-root hunks through a canonical hash-declared hunk patch and deferring Git finalization to separate authority.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5404",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE",
    "target_paths": [
      "platform_tests/scripts/test_fab13_retention_policy.py",
      "bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch"
    ],
    "linked_specifications": [
      "DCL-SMART-POLLER-AUTO-TRIGGER-001",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "DCL-DISPATCH-ENVELOPE-RULES-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "GOV-DOCUMENT-AUTHOR-PROVENANCE-001"
    ]
  },
  "expected_result": {
    "summary": "Repair only the stale FAB-13 live-PID fixture by adding the production-required process create-time provenance sidecar, while preserving the concurrent WI-5396 exact-root hunks through a canonical hash-declared hunk patch and deferring Git finalization to separate authority.",
    "scope": [
      "After independent GO and exact claim/start, modify only test_dispatch_runs_prune_preserves_live_pid_artifacts so the fixture writes the current process create-time sidecar required by the production retention contract; do not change production code or weaken PID provenance.",
      "Preserve the current WI-5396 exact-root hunks in platform_tests/scripts/test_fab13_retention_policy.py byte-for-byte as foreign work and create bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch containing only the WI-5404 fixture delta against HEAD.",
      "Require the implementation report to declare the canonical patch path, SHA-256, byte size, preimage/postimage evidence, and hunk-patch finalization shape; any local commit remains deferred to separate exact mechanical authority.",
      "Do not mutate dispatcher or TAFE configuration/runtime, harness routing/eligibility/roles, production source, credentials, deployment, release, Git history, or unrelated worktree paths."
    ],
    "acceptance_criteria": [
      "The full platform_tests/scripts/test_fab13_retention_policy.py module passes 8 of 8 with the current WI-5396 additions present, and the live PID, stdout log, and matching create-time sidecar are retained only under exact process provenance.",
      "The canonical hunk patch applies cleanly to a disposable HEAD index, touches only platform_tests/scripts/test_fab13_retention_policy.py, contains only the WI-5404 fixture delta, and excludes every WI-5396 exact-root hunk.",
      "Ruff check, Ruff format --check, git diff --check, candidate/live applicability preflight, mandatory clause preflight, and independent verification all pass before any finalization.",
      "Target hash drift, missing independent authority, a noncanonical evidence dependency, or any dispatcher/TAFE/harness/foreign-path mutation fails closed."
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
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Run the full FAB-13 retention module and prove the strict live-artifact retention contract retains only PID artifacts carrying matching process create-time provenance. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Require the implementation report and independent verdict to map every cited mandatory requirement to executable evidence and results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Inspect the test-only diff and assert scripts/dispatcher_runtime.py and all dispatcher/TAFE configuration and runtime state remain unchanged. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Verify the fixture emits live.pid, live.stdout.log, and live.create_time_epoch using the current process identity and that mismatched or absent provenance remains fail-closed. |
| `GOV-WORK-TREE-HYGIENE-001` | Validate the declared canonical hunk patch against a disposable HEAD index and prove it excludes all foreign WI-5396 hunks and unrelated paths. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the full target module plus exact diff/hash checks and confirm no harness, dispatcher, routing, eligibility, role, or process-lifetime behavior changes. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Validate trusted author metadata for every new status-bearing bridge artifact. |

## Acceptance Criteria

- The full platform_tests/scripts/test_fab13_retention_policy.py module passes 8 of 8 with the current WI-5396 additions present, and the live PID, stdout log, and matching create-time sidecar are retained only under exact process provenance.
- The canonical hunk patch applies cleanly to a disposable HEAD index, touches only platform_tests/scripts/test_fab13_retention_policy.py, contains only the WI-5404 fixture delta, and excludes every WI-5396 exact-root hunk.
- Ruff check, Ruff format --check, git diff --check, candidate/live applicability preflight, mandatory clause preflight, and independent verification all pass before any finalization.
- Target hash drift, missing independent authority, a noncanonical evidence dependency, or any dispatcher/TAFE/harness/foreign-path mutation fails closed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_fab13_retention_policy.py`
- `bridge/hunks/gtkb-wi5404-live-pid-provenance-fixture.patch`

## Recommended Commit Type

`feat`
