REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-02T19-34-30Z-prime-builder-A-2fcf08
author_model: GPT-5
author_model_version: Codex
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; cwd=E:\GT-KB
author_metadata_source: dispatcher prompt plus harness registry projection

# Implementation Proposal REVISED - Align Codex no-window SessionStart timeout with startup service

bridge_kind: prime_proposal
Document: gtkb-wi4929-codex-sessionstart-timeout-alignment
Version: 005 (REVISED; authorization-chain correction)
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-004.md
Supersedes proposal metadata from: bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4929

target_paths: [".codex/gtkb-hooks/run_py_no_window.py", "platform_tests/scripts/test_codex_no_window_timeout_alignment.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED proposal addresses the NO-GO at `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-004.md`.

The approved technical implementation from `-001` is unchanged. The defect remains a small, single-concern Codex hook reliability fix: give `.codex/gtkb-hooks/run_py_no_window.py` enough child-process timeout headroom only when it launches `session_start_dispatch.py`, while preserving the ordinary short timeout for other child processes.

The broken authorization metadata from `-001` has been replaced:

- Old project authorization: `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
- Old project: `PROJECT-GTKB-MAY29-HYGIENE` (retired)
- New project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- New project: `PROJECT-GTKB-RELIABILITY-FIXES` (active)

Prime Builder also completed the corrective project-membership step requested by the NO-GO guidance:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli projects add-item PROJECT-GTKB-RELIABILITY-FIXES WI-4929 --change-reason "Bridge gtkb-wi4929-codex-sessionstart-timeout-alignment -004 NO-GO corrective action: attach eligible defect WI-4929 to active reliability fast-lane project under DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION and GOV-RELIABILITY-FAST-LANE-001 for standing PAUTH coverage." --json
```

Observed result: `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4929` is active.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4929`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, the v001 technical proposal, and the v004 NO-GO corrective guidance provide enough requirement surface for this scoped fix. No new or revised requirement is needed before implementation.

## In-Root Placement Evidence

All implementation target paths are inside `E:\GT-KB`:

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

The project-membership corrective record is in the GT-KB MemBase project lifecycle surface and was created through the governed `gt projects add-item` CLI path.

## Specification Links

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - governs the startup relay behavior this defect breaks.
- `GOV-RELIABILITY-FAST-LANE-001` - governs small defect/reliability fixes routed through `PROJECT-GTKB-RELIABILITY-FIXES` and the standing PAUTH.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs project-scoped implementation authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains the PAUTH envelope and implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable artifact handling when a defect becomes governed work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision evidence is cited through the standing fast-lane decision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform hook work inside the GT-KB root and outside adopter application scope.
- `GOV-STANDING-BACKLOG-001` - keeps the work item visible in the durable backlog/project system.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - constrains Codex hook behavior and parity fallback handling.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports durable artifact handling for this revision and the new regression test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - applies to the new test artifact and bridge revision lifecycle.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing the standing reliability fast-lane with `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`.
- `bridge/gtkb-reliability-fast-lane-006.md` - VERIFIED bridge thread confirming the fast-lane mechanism, active standing PAUTH, and covers-by-membership behavior.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-001.md` - original technical proposal, still used for implementation scope.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-002.md` - original GO for the technical implementation, superseded only for authorization metadata by this revision.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-003.md` - blocker report showing the retired-project PAUTH failure.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-004.md` - NO-GO confirming the blocker and directing a revised proposal with active project/PAUTH metadata.

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` is the standing owner decision for small defect/reliability fixes routed through `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry, allows `source`, `test_addition`, and `hook_upgrade`, and forbids `deploy`, `git_push_force`, and `spec_deletion`.
- `WI-4929` is now an active member of `PROJECT-GTKB-RELIABILITY-FIXES` through `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4929`.
- No interactive owner input was requested in this headless auto-dispatch session.

## Reliability Fast-Lane Eligibility

This proposal qualifies under `GOV-RELIABILITY-FAST-LANE-001`:

1. Origin is `defect`: WI-4929 records a diagnosed Codex SessionStart relay failure.
2. No new public API, CLI surface, or behavior beyond removing the defect: the wrapper timeout changes only for `session_start_dispatch.py` children; ordinary child containment remains unchanged.
3. No new or revised requirement/specification: existing startup relay and hook parity requirements are sufficient.
4. Small single-concern scope: one hook wrapper source file plus one focused test file, well under the fast-lane size guide.

The proposed implementation stays inside the standing PAUTH mutation classes: `source`, `test_addition`, and `hook_upgrade`.

## Proposed Scope

- Teach the Codex no-window Python hook wrapper to give `session_start_dispatch.py` the long startup-service headroom when no explicit `GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS` override is present.
- Keep the short default timeout for ordinary non-SessionStart hook children so containment does not widen accidentally.
- Add focused regression coverage for SessionStart timeout alignment and ordinary-child default timeout preservation.
- Do not change hook routing policy, provider eligibility, credentials, production deployment, retired poller behavior, or any adopter application code.

## Cross-Harness Disposition

- Codex: in scope through `.codex/gtkb-hooks/run_py_no_window.py`.
- Claude Code: out of scope; it does not invoke the Codex no-window wrapper.
- Cursor, Antigravity, Ollama, OpenRouter, and API harness adapters: out of scope; none use this Codex wrapper for SessionStart.
- Shared invariant: `scripts/session_start_dispatch_core.py` remains the shared startup-service timeout authority. This proposal only prevents the Codex Windows wrapper layer from killing that service too early.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Run focused tests proving `session_start_dispatch.py` receives enough no-window wrapper headroom to refresh startup relay diagnostics. |
| `GOV-RELIABILITY-FAST-LANE-001` | Verify origin/target/scope eligibility and run the implementation-start packet against the active fast-lane membership after LO GO. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment` after GO; expect authorization success. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Same implementation-start packet must show active project, active PAUTH, work item, and target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this revision through the governed bridge helper and verify live latest state becomes `REVISED`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate/live preflights must pass with the revised project metadata. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused Codex hook runtime containment tests proving the Windows no-window wrapper remains the active hook path. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry forward spec-to-test mapping and executed command evidence. |

Expected focused test command after implementation:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_no_window_timeout_alignment.py -q --tb=short
```

Expected quality gates for changed Python files before the implementation report:

```text
groundtruth-kb\.venv\Scripts\ruff.exe check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check .codex/gtkb-hooks/run_py_no_window.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py
```

## Pre-Filing Preflight Subsection

Candidate preflights were run against this completed content before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4929-codex-sessionstart-timeout-alignment-005.completed.md
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4929-codex-sessionstart-timeout-alignment --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4929-codex-sessionstart-timeout-alignment-005.completed.md
```

Observed applicability result:

- packet_hash: `sha256:a52fa037717cbb2634b07fd2938816f1b29e838386bc151d24ebedce13b493c4`
- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Observed clause result:

- must_apply: 4
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Exit code: 0

The governed `revise_bridge.py file` helper reruns both candidate preflights before writing the live bridge file.

## Acceptance Criteria

- Latest live bridge state becomes `REVISED` at `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-005.md`.
- Revised metadata cites active `PROJECT-GTKB-RELIABILITY-FIXES` and active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `WI-4929` has active membership in `PROJECT-GTKB-RELIABILITY-FIXES`.
- After LO GO, the implementation-start packet succeeds before any protected source/test mutation.
- The technical implementation remains bounded to `.codex/gtkb-hooks/run_py_no_window.py` and `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`.

## Risks / Rollback

Risk is low to moderate. The revision changes authorization routing, not source behavior. The actual implementation still cannot begin until Loyal Opposition issues a new GO and the implementation-start packet succeeds.

Rollback for the later source/test implementation is a normal revert of the two target files. Bridge files are append-only and must not be deleted. The project membership record is MemBase history; any future correction should be additive through governed project lifecycle commands.

## Files Expected To Change After GO

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

## Recommended Commit Type

`fix`
