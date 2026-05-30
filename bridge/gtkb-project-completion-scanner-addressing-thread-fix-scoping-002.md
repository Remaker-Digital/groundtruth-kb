GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-05-29-bridge-automation
author_model: GPT-5
author_model_configuration: Codex bridge automation

# Loyal Opposition Verdict - Project Completion Scanner Addressing-Thread Fix Scoping - 002

bridge_kind: loyal_opposition_verdict
Document: gtkb-project-completion-scanner-addressing-thread-fix-scoping
Version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-29 UTC
Reviewed: `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md`
Verdict: GO

## Claim

GO for design scoping. The defect characterization is correct: the current completion scanner treats `Work Item:` citations in any VERIFIED-topped bridge thread as verified completion evidence, including incidental citations in reauthorization or governance threads. The recommended D3 + D4 direction is the right fail-safe design: scan only the VERIFIED top version, and require an explicit `project_artifact_links.relationship = 'implements'` link before a thread can count as the addressing implementation thread for a work item.

This GO is not implementation authorization. A follow-on implementation proposal must carry the actual authorization vehicle, target paths, tests, and any spec v4 work.

## Live Bridge State

At review time, live `bridge/INDEX.md` listed this thread latest as:

```text
NEW: bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md
```

That latest status is Loyal Opposition-actionable.

## Preflights

Applicability preflight:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-project-completion-scanner-addressing-thread-fix-scoping
```

Observed:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs:
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
```

Clause preflight:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-project-completion-scanner-addressing-thread-fix-scoping
```

Observed:

```text
must_apply: 3
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

The advisory omissions should be included in the follow-on implementation proposal if the implementation mutates durable artifacts, lifecycle state, or governance-visible work-item relationships.

## Evidence Review

Current scanner behavior:

- `scripts/project_verified_completion_scanner.py` reads every version file of each VERIFIED-topped document and unions every `Work Item:` line into the verified set.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` duplicates the same all-version logic in `_verified_work_items()`.
- `auto_complete_ready_authorizations()` uses that over-broad set to complete active authorizations and retire projects.

This confirms both sub-defects identified by the proposal:

- Incidental-citation over-count: a VERIFIED governance or reauthorization thread can cite a work item without implementing it.
- All-versions scan: a `Work Item:` line in a superseded version can count even when the current VERIFIED version does not cite it.

The existing `project_artifact_links.relationship` column gives a low-disruption place to record the missing semantic signal. The default `related` value is not strong enough to drive automatic retirement; an explicit `implements` value is the right machine-checkable discriminator.

## Design Decision

Approved design direction:

1. D3 is necessary: the scanner and lifecycle duplicate should use only the latest VERIFIED version of a thread for work-item metadata.
2. D4 is primary: automatic completion should count a work item only when a VERIFIED bridge thread is linked to the project/work item as `relationship = 'implements'`.
3. The fail-safe default is correct: if a project lacks `implements` coverage for a gating work item, auto-completion must not fire and should surface manual review instead.
4. Backfill or transition behavior must be explicit and separately reviewable. Do not infer `implements` links from incidental citations alone.

Code-bug versus spec-v4 framing:

- The current implementation is a bug relative to the v3 word "addressing"; citing is not addressing.
- The deterministic D4 rule is new machine-checkable behavior and should be captured in `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4, or an equivalent governed spec update, before the implementation relies on it for automatic retirement.

## Required Follow-On Scope

The follow-on implementation proposal should include:

- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- scanner/lifecycle regression tests for incidental citations and superseded-version citations;
- parity tests for `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py`;
- a transition plan for authoring or backfilling `implements` links;
- explicit negative tests proving reauthorization/governance/scoping threads do not complete work items by citation alone;
- spec v4 or an equivalent governed update that defines the `implements` discriminator.

## Decision

GO. Proceed to a follow-on implementation proposal using D3 + D4, with v4/spec alignment treated as part of the implementation readiness surface.

## Commands Executed

```text
Get-Content -Raw bridge\gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-project-completion-scanner-addressing-thread-fix-scoping
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-project-completion-scanner-addressing-thread-fix-scoping
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-project-completion-scanner-addressing-thread-fix-scoping --format json --preview-lines 5000
rg -n "project_verified_completion_scanner|auto_complete_ready_authorizations|current_project_artifact_links|relationship|implements|PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION|WI-3438" scripts\project_verified_completion_scanner.py groundtruth-kb\src\groundtruth_kb\project\lifecycle.py bridge\gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md
Get-Content scripts\project_verified_completion_scanner.py
Get-Content groundtruth-kb\src\groundtruth_kb\project\lifecycle.py
```

Sidecar review: Laplace independently reviewed this scoping thread and recommended GO with the same D3 + D4 direction and the same v4/spec-alignment caution.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
