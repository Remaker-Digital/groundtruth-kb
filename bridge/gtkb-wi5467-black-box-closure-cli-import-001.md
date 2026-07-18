NEW

# WI-5467 - Make the black-box closure CLI load its completion scanner

bridge_kind: prime_proposal
Document: gtkb-wi5467-black-box-closure-cli-import
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5.5 Codex
author_model_version: 5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5467

target_paths: ["scripts/dispatch_blackbox_boundary_scanner.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Commit `91e29767` added the read-only
`gt bridge dispatch black-box closure` command. Its real installed-console-entrypoint
path loads `scripts/dispatch_blackbox_boundary_scanner.py` by source-file
location, but `_member_completion_status()` then uses a bare sibling import for
`project_verified_completion_scanner`. The installed `gt` entry point does not
put the repository `scripts/` directory on `sys.path`, so the production
command crashes with `ModuleNotFoundError` before it can return a governed
closure result.

Load the existing repository-owned completion scanner by its exact in-root file
path and add a regression that invokes the real installed `gt` entry point.
The repair must preserve the scanner's read-only behavior, project-root
confinement, closure semantics, and nonzero `NOT READY` result. It must not
alter dispatcher, TAFE, harness, worker, lease, eligibility, routing, or
runtime state.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the canonical dispatcher CLI must
  execute through one deterministic in-root dependency path.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the repair preserves the existing CLI
  facade and read-only closure-scanner boundary.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - a loader failure must be fixed
  without disabling a harness or changing live routing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - source and test mutation remains gated by
  independent GO, exact claim, implementation-start authorization, report,
  independent verification, and focused finalization.
- `GOV-WORK-TREE-HYGIENE-001` - only the two currently clean target files may
  carry WI-5467 implementation bytes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  binds the exact defect and targets to concrete governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the PAUTH, project,
  work item, and target paths are explicit and mechanically checkable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must
  exercise the real installed entry point, not only a monkeypatched loader.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the active PAUTH permits only the
  bounded source/test repair after the remaining operation-time gates pass.
- `GOV-STANDING-BACKLOG-001` - WI-5467 and linked TEST-11566 preserve the
  reproduced defect and production-path acceptance condition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - reproduction, proposal, test,
  implementation report, verdict, and commit remain durable and linked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - executable console-entrypoint
  evidence, rather than an inferred import result, proves the repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - capture, review, implementation,
  verification, and closure remain distinct states.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes
  bounded carriers for newly reproduced fleet and bridge defects while
  preserving all later gates.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717` - active
  authorization limited to WI-5467 and the two declared target files.
- `bridge/gtkb-wi5276-black-box-closure-scanner-gate-003.md` - implementation
  report for the closure scanner whose production path exposed this defect.
- `bridge/gtkb-wi5276-black-box-closure-scanner-gate-004.md` - prior terminal
  verdict; WI-5467 is a fresh governed correction, not an edit to that chain.

## Owner Decisions / Input

No new owner decision is required. The active goal requires each newly found
bridge/TAFE/harness black-box defect to be captured as a hygiene work item with
a linked test and advanced through the normal workflow.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
bounded carrier, and the active PAUTH preserves independent GO, claim,
implementation-start, verification, and focused-commit gates.

## Requirement Sufficiency

Existing requirements sufficient. The linked dispatcher architecture,
nonimpairment, bridge authority, project authorization, and spec-derived test
requirements govern the exact repair. WI-5467 and TEST-11566 provide the
missing production-path acceptance condition.

## Proposed Implementation

1. Add a private completion-scanner loader in
   `scripts/dispatch_blackbox_boundary_scanner.py` that resolves
   `scripts/project_verified_completion_scanner.py` beneath the scanner's
   exact `PROJECT_ROOT`.
2. Load that file through `importlib.util.spec_from_file_location`, register
   the module before execution so its dataclasses resolve correctly, and fail
   with an explicit deterministic error if the in-root file cannot be loaded.
   Do not add a broad or persistent `sys.path` mutation.
3. Reuse the loaded module for `_member_completion_status()` without changing
   member-completion or boundary-finding semantics.
4. Add `test_black_box_closure_cli_loads_repository_completion_scanner` to the
   declared CLI test module. Invoke the actual venv/installed `gt` console
   entry point against an intentionally nonexistent project ID, assert a
   governed exit code 1 and parseable `project_not_found` JSON, and assert that
   neither stdout nor stderr contains `ModuleNotFoundError`.
5. Preserve the existing monkeypatched unit tests for JSON formatting, ready
   exit behavior, and out-of-root evidence rejection.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717; WI-5467; TEST-11566",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Load the repository-owned sibling completion scanner by its exact in-root source path from the already selected black-box closure scanner.",
  "before_behavior": "The installed gt entry point loads the black-box scanner by file, then a bare sibling import fails because the repository scripts directory is absent from sys.path.",
  "after_behavior": "The installed gt entry point deterministically loads the in-root completion scanner and returns the existing READY or NOT READY closure contract.",
  "self_descriptive_naming": "_load_project_completion_scanner, completion_scanner_path, and project_verified_completion_scanner identify the exact dependency and boundary.",
  "obsolete_guidance_disposition": "A bare sibling import is no longer treated as valid for a script loaded by file from an installed console entry point.",
  "history_preservation": "WI-5276 evidence remains unchanged; WI-5467 records the correction as a fresh work item, test, proposal, report, verdict, and focused commit.",
  "baseline": {
    "console_entrypoint": "groundtruth-kb/.venv/Scripts/gt.exe",
    "black_box_scanner": "scripts/dispatch_blackbox_boundary_scanner.py",
    "completion_scanner": "scripts/project_verified_completion_scanner.py",
    "failing_import": "project_verified_completion_scanner",
    "failure_class": "ModuleNotFoundError"
  },
  "expected_result": {
    "installed_entrypoint": "returns parseable closure JSON without ModuleNotFoundError",
    "missing_project": "returns exit 1 with project_not_found evidence",
    "dispatcher_state": "unchanged",
    "harness_state": "unchanged"
  },
  "rollback": {
    "instructions": "Revert only the two declared target files through a governed focused transaction.",
    "verification": "Rerun the focused CLI tests and confirm no dispatcher, TAFE, worker, lease, eligibility, routing, or runtime state changed."
  },
  "hard_invariants": [
    "Codex A remains Prime Builder only and never publishes a Loyal Opposition verdict.",
    "The completion scanner resolves only from E:\\GT-KB\\scripts\\project_verified_completion_scanner.py.",
    "No persistent sys.path mutation is introduced.",
    "The command remains read-only and keeps exit 1 for a NOT READY or nonexistent project.",
    "No harness, provider, worker, claim, lease, TAFE, dispatcher configuration, eligibility, routing, or runtime state is contacted or mutated by the implementation test.",
    "Only the two declared clean target files receive implementation bytes."
  ],
  "fail_closed_conditions": [
    "The expected completion-scanner source path is missing, unreadable, or outside E:\\GT-KB.",
    "Python cannot create or execute a module specification for the exact source file.",
    "The loaded module lacks member_completion_scan.",
    "The installed console-entrypoint output is not parseable closure JSON.",
    "Either clean target changes after implementation-start hashing."
  ],
  "essential_context_preservation": "Closure output retains project_id, member completion readiness, nonterminal work-item evidence, exclusion reasons, boundary finding counts, finding details, READY or NOT READY semantics, and the existing in-root evidence restriction."
}
```

## Spec-Derived Verification Plan

| Governing requirement | Focused verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Invoke the installed `gt bridge dispatch black-box closure` command for a nonexistent project and require parseable `project_not_found` JSON rather than an import exception. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete declared CLI test module and require all tests, including TEST-11566's named function, to pass. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare read-only dispatcher health/status before and after; require no worker, eligibility, routing, lease, TAFE, or runtime mutation. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Require the implementation diff and focused commit to contain only the two declared target files plus governed bridge evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify independent GO, exact claim, implementation-start packet, implementation report, independent verdict, and focused commit evidence. |

Planned commands:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\cli\test_bridge_dispatch_black_box_closure_cli.py -q --tb=short --timeout=300
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\dispatch_blackbox_boundary_scanner.py platform_tests\groundtruth_kb\cli\test_bridge_dispatch_black_box_closure_cli.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\dispatch_blackbox_boundary_scanner.py platform_tests\groundtruth_kb\cli\test_bridge_dispatch_black_box_closure_cli.py
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch black-box closure --project-id PROJECT-GTKB-WI5467-NOT-FOUND --json
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch health --json
```

Expected CLI exit code is 1 for the intentionally nonexistent project, with
valid JSON and `exclusion_reasons: ["project_not_found"]`.

## Risk / Rollback

The bounded risk is import-module registration or an incorrect source path.
Exact in-root path resolution, pre-execution registration, the installed-entrypoint
test, and the existing full CLI module tests cover that risk. Rollback is one
governed focused revert of the two declared files; no data, runtime, or
configuration migration is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5467-black-box-closure-cli-import`; no prior version is
deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix`: the diff restores the documented production behavior of an existing
read-only CLI command and adds its missing integration regression.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
