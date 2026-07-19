NEW

# WI-5467 Closure CLI Completion-Scanner Import Repair

bridge_kind: prime_proposal
Document: gtkb-wi5467-closure-cli-completion-scanner-import
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5467

target_paths: ["scripts/dispatch_blackbox_boundary_scanner.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py"]

implementation_scope: bounded_source_and_test_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the production-path import failure in the read-only black-box closure
command. The installed `gt` entry point loads
`scripts/dispatch_blackbox_boundary_scanner.py` by file path, but that scanner
uses a bare sibling import for `project_verified_completion_scanner`. The
installed entry point does not put `E:\GT-KB\scripts` on `sys.path`, so the
real command exits with `ModuleNotFoundError` before it can evaluate project
completion.

The implementation will resolve and load the existing sibling scanner
deterministically from the supplied in-root project root. It will add a
production-path CLI regression that invokes the real Click command without
monkeypatching `_load_dispatch_black_box_boundary_scanner`. No scanner
semantics, project-completion rules, dispatcher/TAFE state, MemBase rows,
claims, leases, or runtime behavior are changed.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the closure command remains a read-only dispatcher service surface.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the fix restores the governed CLI boundary without exposing or mutating dispatcher internals.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - existing closure semantics, live workers, and ordinary dispatcher behavior must remain unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, review, implementation report, and verification use the append-only numbered bridge chain.
- `GOV-WORK-TREE-HYGIENE-001` - implementation and finalization are limited to the two declared paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links its governing specifications and derives verification from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the PAUTH, project, work item, and exact target paths are machine-readable above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - positive VERIFIED requires executed production-path, scanner, lint, and formatting evidence.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation remains bounded by the WI-5467 PAUTH and exact start packet.
- `GOV-STANDING-BACKLOG-001` - WI-5467 remains open until independently VERIFIED and atomically finalized.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the reproduced defect is preserved as a work item, proposal, tests, report, and verdict chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation keeps deterministic evidence connected to the governed work item.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - source mutation starts only after GO and ends only after report, independent VERIFIED, and focused finalization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both implementation targets and all test fixtures remain inside the selected project root.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authority for bounded repair of newly reproduced bridge/TAFE/harness black-box defects; instantiated by the active WI-5467 PAUTH.
- `DELIB-20261498` - prior project-completion-scanner review establishes that scanner completion semantics are governed and must fail closed; this proposal changes only dependency loading.
- `bridge/gtkb-wi5276-black-box-closure-scanner-gate-003.md` and `bridge/gtkb-wi5276-black-box-closure-scanner-gate-004.md` - implementation report and VERIFIED verdict that introduced the closure command whose production import path is now defective.
- `WI-5467` / `TEST-11566` - live defect and linked regression-test anchor for the exact installed-entry-point failure.

## Owner Decisions / Input

No new owner decision is required. The owner-directed active black-box goal and
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` already authorize
the bounded proposal carrier
`PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717`. Every normal
GO, claim, implementation-start, independent verification, and focused-commit
gate remains mandatory.

## Requirement Sufficiency

Existing requirements sufficient.

The PAUTH-linked dispatcher architecture, nonimpairment, project-authorization,
bridge-linkage, and spec-derived-verification requirements fully define this
two-file import repair. No new or revised formal requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; WI-5467; TEST-11566; PAUTH-DISPATCHER-BLACK-BOX-WI5467-CLOSURE-CLI-IMPORT-20260717",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, and ADR-DISPATCHER-ARCHITECTURE-001",
  "primary_route": "The existing gt bridge dispatch black-box closure command remains the only operator route; this change repairs its in-root dependency loading.",
  "before_behavior": "The installed gt entry point loads the boundary scanner but exits with ModuleNotFoundError before project completion can be evaluated.",
  "after_behavior": "The same command deterministically loads the existing completion scanner from the selected in-root project and returns its normal READY or NOT READY result.",
  "self_descriptive_naming": "The bridge slug, WI-5467 title, two target paths, loader symbols, and production-path test all identify the closure CLI completion-scanner import responsibility.",
  "obsolete_guidance_disposition": "No command, scanner, or project-completion rule is replaced. The ambient bare sibling-import assumption is retired only inside the boundary scanner.",
  "history_preservation": "The bridge chain, WI and test records, scanner output, and focused commit remain append-only evidence; no historical bridge or MemBase record is rewritten.",
  "baseline": {
    "command": "gt bridge dispatch black-box closure --project-id PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING --json",
    "observed_failure": "ModuleNotFoundError: No module named project_verified_completion_scanner",
    "source_commit": "91e29767 introduced the verified closure scanner gate"
  },
  "expected_result": {
    "production_path": "The real installed command reaches member_completion_scan without an import traceback.",
    "nonterminal_behavior": "The command may still exit nonzero while project members remain nonterminal, with deterministic JSON instead of an exception.",
    "test_scope": "Both focused scanner and CLI modules pass."
  },
  "rollback": {
    "instructions": "Revert the exact two-file focused commit.",
    "verification": "Rerun the pre-fix production command and both focused test modules; no database or runtime rollback is involved."
  },
  "hard_invariants": [
    "No dispatcher, TAFE, harness, claim, lease, runtime-state, database, credential, deployment, release, or external-system mutation.",
    "No change to project-completion classification or boundary-finding semantics.",
    "No ambient or out-of-root module may satisfy the dependency."
  ],
  "fail_closed_conditions": [
    "The selected project root is outside the governed root.",
    "The sibling completion-scanner file is missing, ambiguous, or unloadable.",
    "The real production-path regression still requires a monkeypatched scanner loader."
  ],
  "essential_context_preservation": "Preserve project-root confinement, existing member_completion_scan output, READY/NOT READY exit behavior, boundary evidence scanning, and every current CLI option."
}
```

## Spec-Derived Verification Plan

| Specification | Planned command or evidence | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Add a test in `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py` that creates an isolated in-root project fixture with the real boundary scanner and a stub sibling completion scanner, then invokes the real `gt bridge dispatch black-box closure` Click path without monkeypatching the scanner loader. | Command reaches the completion scanner and emits deterministic JSON instead of raising `ModuleNotFoundError`. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `python -m pytest platform_tests/scripts/test_dispatch_blackbox_boundary_scanner.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py -q --tb=short` | All scanner and CLI behavior tests pass; existing fail-closed exit semantics remain unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `gt bridge show gtkb-wi5467-closure-cli-completion-scanner-import --json --compact` at report and verdict time. | Numbered chain progresses NEW -> GO -> NEW implementation report -> independently finalized VERIFIED. |
| `GOV-WORK-TREE-HYGIENE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only HEAD -- <two target paths>` and isolated fixture path assertions. | Only the two approved in-root paths change. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Applicability preflight, clause preflight, exact claim, and implementation-start packet validation. | No missing specs or clause gaps; packet covers exactly the two target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute both focused pytest modules plus `python -m ruff check` and `python -m ruff format --check` for both targets. | All commands exit 0 and are reproduced by the independent verifier. |
| `GOV-STANDING-BACKLOG-001`; artifact-oriented GOV/ADR/DCL | Inspect WI-5467, TEST-11566, report, verdict, and focused commit evidence. | Work item stays nonterminal before VERIFIED and closes only after exact terminal evidence. |

The implementation report must also reproduce the real installed command
against `E:\GT-KB` after the fix. A nonzero result is acceptable while project
members remain nonterminal, but no import traceback is acceptable.

## Risk / Rollback

The main risk is loading the right module under tests while accidentally
changing process-global import resolution or masking a missing in-root
dependency. The implementation must resolve the completion scanner from the
selected project root, fail deterministically when that file is absent, and
avoid accepting an out-of-root or ambient module.

Rollback is a normal revert of the exact two-file focused commit. No database,
dispatcher/TAFE runtime, claim/lease, configuration, credential, deployment,
release, or external-system rollback is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5467-closure-cli-completion-scanner-import`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - restores an existing closure command's production dependency path.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
