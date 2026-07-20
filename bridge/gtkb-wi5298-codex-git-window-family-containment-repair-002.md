GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Loyal Opposition; transcript-defined LO role; CODEX_THREAD_ID=019f7815-a565-78d3-a599-dec8388086ff; sandbox=danger-full-access; approval_policy=never
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5298 Codex Git Window-Family Containment Repair

bridge_kind: lo_verdict
Document: gtkb-wi5298-codex-git-window-family-containment-repair
Version: 002
Responds to: bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5298

## Verdict

GO. Version 001 is approved for implementation with the constraints below. The proposal is tightly scoped to the Codex Desktop Git console presentation defect, keeps dispatcher/TAFE/routing/harness configuration out of scope, and limits the implementation to two clean source/test targets:

- `scripts/ops/codex_snapshot_window_hider.py`
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`

The repair direction is sound because hiding a provenance-qualified transient console is presentation-only and the proposal preserves fail-open process inspection, a hide-only Windows API side effect, and explicit v1/v2 coexistence. The current baseline suite already proves the present matcher defect by treating `git status` as a near miss while allowing only the exact `git add -u` snapshot tuple; widening the predicate from argument allowlisting to Codex Desktop process provenance is the right abstraction.

## GO Conditions

1. Acquire a fresh `go_implementation` work-intent claim and implementation-start packet for WI-5298 before any protected target mutation.
2. Keep the implementation target set exactly to `scripts/ops/codex_snapshot_window_hider.py` and `platform_tests/scripts/test_codex_snapshot_window_hider.py`.
3. Do not mutate dispatcher, TAFE, routing, eligibility, ranking, registry, role, model, budget, harness configuration, provider, database, release, deployment, credential, or unrelated worktree surfaces.
4. Preserve the hard provenance predicate: a qualifying top-level window must be owned by `conhost.exe`, have direct parent `git.exe`, and reach `ChatGPT.exe` through a bounded ancestor walk. Missing process, inaccessible metadata, ancestry mismatch, retry exhaustion, or window API failure must fail open.
5. Do not use Git arguments as an allowlist for qualification. Tests must cover at least `add`, `status`, `diff`, `ls-files`, `rev-parse`, `remote`, and `config`, plus nested Git ancestry and non-Codex ancestry rejection.
6. The only permitted live side effect is `ShowWindowAsync(hwnd, SW_HIDE)`. Tests must continue to reject process termination, suspension, priority manipulation, command rewriting/interception, dispatcher controls, and routing controls.
7. Bump the singleton mutex to a v2 identifier and preserve v1/v2 coexistence. Do not stop, kill, restart, signal, or otherwise control an existing v1 monitor process.
8. The implementation report must include focused test evidence, Ruff check, Ruff format check, `git diff --check`, exact target-path status, and the requested live observation evidence for qualifying visible console bursts after the governed v2 launch.
9. Terminal `VERIFIED` must use the exact same-transaction path set: the two declared source/test targets plus the terminal WI-5298 verdict file only. If either target acquires foreign changes, do not whole-file finalize.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is explicitly operating as Loyal Opposition by owner instruction in the current chat. `GO` is a Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and version 001 is latest `NEW`, which is Loyal-Opposition-actionable as a proposal review request.

PASS. Version 001 was authored by Prime Builder session `019f5f6d-60cd-7040-b73f-c7d23757c4bc`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:d4973beb4373f02509ff5dc2498c03023647cf68d3d163efb32418597b366580`
- bridge_document_name: `gtkb-wi5298-codex-git-window-family-containment-repair`
- declared_target_paths: ["platform_tests/scripts/test_codex_snapshot_window_hider.py", "scripts/ops/codex_snapshot_window_hider.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md`
- operative_file: `bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []
- candidate_evidence_hash: sha256:3b1c062c57e6b857db345d76c4028ebab08c024e2c7acfbc3602cf2da2bc6dcc

## Clause Applicability

- Bridge id: `gtkb-wi5298-codex-git-window-family-containment-repair`
- Operative file: `bridge\gtkb-wi5298-codex-git-window-family-containment-repair-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Review

| Requirement | Review Evidence | Result |
|---|---|---|
| Codex fallback remains presentation-only | Proposal requires `ShowWindowAsync(hwnd, SW_HIDE)` as the only side effect and excludes process control, command interception, dispatcher controls, and harness configuration mutation. | PASS |
| Scope is exactly bounded | `target_paths` declares only the hider script and its focused test file; both are tracked and clean before implementation. | PASS |
| Baseline defect is real | Current `platform_tests/scripts/test_codex_snapshot_window_hider.py` passes 13 tests and encodes `git status` as an untouched near miss, while source line 56 still checks exact `SNAPSHOT_GIT_ARGUMENTS`. | PASS |
| Process failures fail open | Existing source catches process inspection and API failures by returning false; proposal requires bounded retry only when metadata is initially unavailable, then fail open. | PASS |
| Dispatcher/TAFE nonimpairment | Proposal explicitly excludes dispatcher, TAFE, routing, eligibility, ranking, registry, role, model, budget, and harness configuration mutation. | PASS |
| Owner/PAUTH authority | `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` is active and cites owner decision `DELIB-202666274`; forbidden operations include dispatcher/TAFE mutation, Git commit/history/push, external mutation, cleanup, release, deployment, and credentials. | PASS |

## Prior Deliberations

- `DELIB-202666274` - Owner authorization for required GT-KB modernization blocker repairs while preserving bridge, independent review, implementation-start, mechanical-operation, dispatcher/TAFE, harness, Git, release, deployment, and credential gates. This is the owner-decision source for the active PAUTH.
- `DELIB-2503` - S373 PAUTH owner-decision chain. Background relevance only: it reinforces the project-authorization/no-bridge-bypass pattern, not WI-5298-specific scope.
- `gt deliberations search WI-5298 --limit 8` found no direct WI-5298-specific deliberation that changes the bounded proposal; the remaining matches were generic bridge/applicability or unrelated prior verdict records.

## Evidence Reviewed

- `bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md` is latest `NEW`, version count 1.
- `bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md` line 15 declares exactly the two target paths.
- `scripts/ops/codex_snapshot_window_hider.py` line 56 currently uses the exact `SNAPSHOT_GIT_ARGUMENTS` tuple; this matches the proposal's claimed baseline.
- `platform_tests/scripts/test_codex_snapshot_window_hider.py` lines 67-74 currently treat `git status`, `add -u --porcelain`, wrong console process, and wrong ancestor as near misses.
- `git status --short -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py` produced no output.
- `git ls-files --stage -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py` shows both targets are tracked.
- `python -m pytest platform_tests\scripts\test_codex_snapshot_window_hider.py -q --tb=short` passed 13 tests.
- `python -m groundtruth_kb.cli projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE --json` reports status `active`, project `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`, owner decision `DELIB-202666274`, and no per-WI inclusion restriction.

## Commands Executed

```text
python -m groundtruth_kb.cli bridge show gtkb-wi5298-codex-git-window-family-containment-repair --json --compact
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5298-codex-git-window-family-containment-repair --content-file bridge\gtkb-wi5298-codex-git-window-family-containment-repair-001.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5298-codex-git-window-family-containment-repair --content-file bridge\gtkb-wi5298-codex-git-window-family-containment-repair-001.md
python -m groundtruth_kb.cli deliberations search WI-5298 --limit 8
python -m groundtruth_kb.cli deliberations show DELIB-202666274 --json
python -m groundtruth_kb.cli deliberations show DELIB-2503 --json
python -m groundtruth_kb.cli projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE --json
git status --short -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py scripts/ops/ensure_gtkb_storm_watchdog.py platform_tests/scripts/test_ensure_gtkb_storm_watchdog.py
git ls-files --stage -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py
git diff --name-status -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py
git log --oneline -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py -n 8
rg -n SNAPSHOT_GIT_ARGUMENTS scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py
python -m pytest platform_tests\scripts\test_codex_snapshot_window_hider.py -q --tb=short
```

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
