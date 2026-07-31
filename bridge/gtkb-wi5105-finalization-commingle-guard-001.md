NEW

# WI-5105: Preserve Per-Thread Finalization Isolation

bridge_kind: prime_proposal
Document: gtkb-wi5105-finalization-commingle-guard
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5105-COMMINGLE-GUARD-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5105

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4471 blocks two different live work-intent claims from reserving the same
target. It does not protect the next phase: a first thread may release its
claim after reporting implementation while its shared target remains dirty and
awaits VERIFIED. A second GO thread can then start on that dirty file, making a
whole-file VERIFIED finalization misattribute both threads' hunks.

Add a deterministic, fail-closed-on-positive-evidence guard at implementation
authorization and protected-mutation time. It will inspect the live versioned
bridge chains, named authorization packets, and `git status` for the concrete
target. It must block only when a non-terminal peer thread has an
implementation report that claims the same dirty concrete path. Existing
active-claim collision behavior remains in force; clean targets, terminal peer
threads, non-overlapping paths, and same-thread work remain allowed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the guard reads the live bridge chain and
  preserves its per-thread audit and finalization authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization is
  bounded and must not permit unsafe work outside the approved scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the new guard strengthens,
  rather than bypasses, GO, target-path, implementation-report, and LO gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - peer identity and
  target-path scope come from the required proposal metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites concrete governing requirements for the source and test changes.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each governing behavior
  is covered by focused executed regression tests before verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - claims, authorization packets,
  reports, and terminal state must remain attributable durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the guard distinguishes live
  non-terminal work from terminally verified work before blocking a start.

## Prior Deliberations

- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - owner authorization for the
  bounded reliability guard and its governed bridge path.
- WI-4471 implementation report, version 003 - added active-claim path
  collision protection; this proposal addresses its released-claim,
  dirty-worktree residual gap.
- WI-4841 Loyal Opposition NO-GO, version 020 - a current demonstration of why
  shared registry and manifest hunks cannot be whole-file finalized safely.

## Owner Decisions / Input

`DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` authorizes this bounded proposal
and post-GO implementation. It expressly preserves independent LO review,
implementation-start authorization, and the prohibition on committing
unrelated dirty files.

## Requirement Sufficiency

Existing requirements sufficient. The live-bridge authority, bounded project
authorization, no-bypass, mandatory linkage, and spec-derived verification
requirements define the needed behavior; no new or revised requirement is
needed for this narrowly scoped concurrency guard.

## Spec-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short --basetemp .harness-tmp/wi5105` | A dirty path claimed by a non-terminal peer report blocks both authorization start and protected mutation; the diagnostic names the peer thread and path. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Same focused suite | The guard is evaluated in addition to, not instead of, the existing project/GO/claim checks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Same focused suite with proposal target metadata fixtures | The peer match derives from parser-readable bridge target paths and a concrete reported path. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Same focused suite plus `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py` | All focused tests and static checks pass. |

## Risk / Rollback

The main risk is a false-positive block that slows a legitimate independent
edit. The guard therefore requires all three facts: a non-terminal peer report,
a claimed overlapping concrete path, and a currently dirty target. It does not
infer ownership from a dirty path alone. Rollback is one scoped revert of the
guard and its tests; no bridge history, runtime state, or unrelated worktree
changes are altered.

## Bridge Filing

Filing creates the next append-only numbered bridge file for this document;
no prior version is deleted or rewritten. The governed writer publishes the
file and its dispatcher/TAFE state. The numbered file chain remains the live
workflow state under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the change closes a demonstrated concurrency and finalization defect in
existing implementation authorization behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
