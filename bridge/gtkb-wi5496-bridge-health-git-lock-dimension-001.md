NEW
::init gtkb lo
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: d067ca16-171b-4b2e-89f5-642340e605a6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code-interactive-prime-builder-via-init-gtkb-pb

# Implementation Proposal - Add stale git-lock detection dimension to bridge dispatch health

bridge_kind: prime_proposal
Document: gtkb-wi5496-bridge-health-git-lock-dimension
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5496

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Owner-directed fix for an observability gap surfaced by the WI-5153 finalization incident: a stale .git/index.lock silently blocked every index-mutating git operation (including VERIFIED-verdict finalize commits) for 3+ hours with gt bridge dispatch health reporting clean the entire time, because the health rollup has no dimension inspecting .git/ for lock files. Add a third, read-only health dimension (git_lock_health) alongside the existing complex_lifecycle and routing_config dimensions, following their exact contract: detect .git/index.lock, age-threshold it into PASS/WARN/FAIL, and surface a finding with recovery guidance. Detection only; no auto-delete. Fast-lane reliability/observability defect; source plus test only.

Work item description: A stale `.git/index.lock` (created 2026-07-17T12:19:07-07:00) silently blocked every index-mutating git operation in the repo, including VERIFIED bridge-verdict finalization commits, for over three hours before it was discovered by manual investigation into one stuck verdict (WI-5153). `gt bridge dispatch health` reported PASS/WARN throughout that entire window with no mention of the lock; the dispatcher daemon kept ticking and dispatching workers whose eventual finalize-commit step was doomed to fail against the same lock, and the actionable-queue backlog kept growing invisibly. The health-monitoring tool the project actually runs (bridge dispatch health, checked every dispatcher-status read this session) has no dimension that inspects `.git/` for stale lock files, so this failure mode is currently undetectable except by a human or agent manually noticing a specific stuck operation and diagnosing it from scratch.

Fix: add a new health dimension (e.g. `git_lock_health`) to `collect_bridge_dispatch_health` in `bridge_dispatch_config.py`, alongside the existing `complex_lifecycle` and `routing_config` dimensions. The dimension scans `.git/index.lock` (and, if scoped in, other well-known git lock paths such as `.git/HEAD.lock` and `.git/refs/heads/*.lock`) for existence and age; a lock present past a generous staleness threshold (well above any legitimate git operation duration for this repo) reports WARN, escalating to FAIL past a longer threshold, with a finding message identifying the lock path, its age, and the standard git recovery guidance (confirm no live git process holds it, then remove). Detection only, matching the existing dimensions' read-only contract and the Loyal Opposition file-safety boundary that already prohibits automated deletion; this does not add auto-repair.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5496` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`.

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
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260704-WITHDRAW-GTKB-WI4821-DISPATCH-CAN-RECEIVE-DISPATCH-DRIFT-RECONCILE-GO` - Withdraw stale GO for WI-4821 dispatch drift reconcile
- `DELIB-20265486` - Loyal Opposition verification - WI-4682 finalization blocked by git index lock
- `DELIB-20265324` - Loyal Opposition GO: Requirement-Sufficiency operative-precedence fix
- `DELIB-20265437` - Verdict
- `DELIB-20265632` - Loyal Opposition NO-GO Verification Verdict: gtkb-gt-bridge-verify-embedded-evidence-cli

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5496`.

## Proposed Scope

- Add a new pure function _git_lock_health_dimension(project_root) to bridge_dispatch_config.py, following the exact {name, health_status, findings} contract of the existing _complex_lifecycle_health_dimension and _routing_config_health_dimension functions. It checks .git/index.lock for existence and age (mtime), reporting PASS when absent or fresh, WARN past a generous staleness threshold, and FAIL past a longer threshold, with a finding string naming the lock path, its age, and standard git-lock recovery guidance.
- Wire the new dimension into collect_bridge_dispatch_health alongside complex_lifecycle and routing_config: add it to the dimensions dict, fold its health_status into the _max_health_status aggregate, and include its findings in the flattened findings list, matching the existing two-dimension pattern exactly.
- Detection only, no auto-repair: the dimension only reads filesystem metadata (stat) and never deletes or modifies the lock file, preserving the same read-only contract as the other two dimensions and the Loyal Opposition file-safety boundary that already governs deletion of git-internal state.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest platform_tests/scripts/test_bridge_dispatch_config.py; report pass/fail counts in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-RELIABILITY-FAST-LANE-001` | New unit tests in test_bridge_dispatch_config.py cover PASS/WARN/FAIL states for the new dimension using fabricated lock-file fixtures under tmp_path. |

## Acceptance Criteria

- gt bridge dispatch health includes a git_lock_health (or equivalently named) dimension in its dimensions output alongside complex_lifecycle and routing_config.
- A unit test creates a fake stale .git/index.lock (old mtime) under a tmp_path project root and asserts the new dimension reports WARN or FAIL with a finding naming the lock and its age.
- A unit test confirms the dimension reports PASS when no lock file is present, and when a lock file exists but is younger than the staleness threshold.
- The aggregate health_status returned by collect_bridge_dispatch_health correctly escalates when the new dimension reports WARN/FAIL, matching the existing _max_health_status aggregation behavior.
- ruff check and ruff format --check pass on both changed files.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`feat`
