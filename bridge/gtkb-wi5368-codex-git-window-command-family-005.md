REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5368 Codex Git Window Command Family — Cleared-Dependency Revision

bridge_kind: prime_proposal
Document: gtkb-wi5368-codex-git-window-command-family
Version: 005
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-004.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]
implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

## Revision Claim

The two independent blockers recorded in version 004 have cleared without any
WI-5368 source or test mutation. The predecessor
`gtkb-wi5298-codex-snapshot-git-window-containment` is now terminal VERIFIED at
version 006, both WI-5368 target paths are clean, and the preserved HEAD blobs
remain exactly `4b0ed05225b161bd582e53489c393a2b5a7693e9` for the monitor and
`309f56fa9f7f499815628281c27ccd2890cef13d` for its focused test. A future GO
must carry canonical author-session provenance, distinct from this proposal
author session, and must pass a fresh exact implementation-start gate before
either target changes.

The technical scope from version 001 is unchanged: recognize the full Codex
Desktop internal Git-manager command family by exact process provenance and
the two existing Codex Git markers while preserving hide-only behavior. Do not
terminate, suspend, intercept, reprioritize, or alter any process, Git
operation, dispatcher route, harness role, or eligibility value.

## Findings Addressed

### F1 — P1 — Nonterminal predecessor owned the shared test path

**Resolved.** `gt bridge show
gtkb-wi5298-codex-snapshot-git-window-containment --json` now reports version
006 `VERIFIED`. Scoped status for both WI-5368 targets is empty, and both paths
are tracked at the exact frozen HEAD blobs cited above. No foreign target bytes
would be adopted by this proposal.

### F2 — P1 — Prior GO lacked canonical author-session provenance

**Corrected by lifecycle restart.** This REVISED proposal requests a new
independent GO rather than reusing version 002. The new verdict must contain
canonical `author_session_context_id` metadata and prove that its author
session differs from this proposal's author session. Any missing provenance or
self-review result remains a fail-closed stop.

### F3 — P1 — Terminal commit authority remains outside the active PAUTH

**Disclosed, not waived.** The active project PAUTH authorizes `source`,
`test`, `bridge`, and `governance_evidence` work but expressly forbids
`git_commit`. A GO may authorize implementation and evidence collection only.
No terminal VERIFIED may be issued as a file-only artifact. Before terminal
finalization, an owner-approved narrow authorization must permit the exact
implementation/bridge cohort and local atomic commit, or the implementation
report must remain nonterminal.

## Scope Changes

No implementation target or behavior changes from version 001. The lifecycle
is refreshed solely because version 004's predecessor-ownership blocker is now
closed and any future GO will use the current canonical author metadata.

Implementation remains limited to:

1. parse Git `-c key=value` overrides and a non-empty subcommand;
2. require `git.exe`, exactly one `core.hooksPath=NUL`, exactly one empty
   `core.fsmonitor=`, the existing top-level event, `conhost.exe` relationship,
   and bounded `ChatGPT.exe` ancestry;
3. reject duplicates, missing values, malformed pairs, absent subcommands,
   non-Git executables, and marker near misses;
4. preserve `ShowWindowAsync(SW_HIDE)` as the sole target-window/process side
   effect and fail open on inspection ambiguity; and
5. extend only the declared focused test module for observed command shapes
   and near misses.

No launcher, bridge routing, dispatcher, TAFE, role, eligibility, Git
execution, process lifetime, credential, release, deployment, push, or third
file is in scope.

## Frozen Baseline Evidence

- `scripts/ops/codex_snapshot_window_hider.py`: HEAD blob
  `4b0ed05225b161bd582e53489c393a2b5a7693e9`; SHA-256
  `A8F6169E51CB1E40796A764A6A6596F183541139A29DD0D44AFF84A29B1A677C`.
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`: HEAD blob
  `309f56fa9f7f499815628281c27ccd2890cef13d`; SHA-256
  `83CA43CF6CB140B08BB4DEF269C18AC6641193B618B1BE21CBA24D0B4223CDA6`.
- Scoped worktree and index status: empty for both targets.
- Focused baseline: 13 tests passed with one pre-existing unknown
  `asyncio_mode` pytest warning.
- Ruff check and scoped `git diff --check`: passed.

Any target drift, peer ownership, index entry, authorization denial, or
unrelated path is a stop condition requiring another governed revision.

## Requirement Sufficiency

Existing behavioral requirements remain sufficient. The defect is incomplete
coverage in the already governed nonimpairing fallback. The only unsatisfied
governance requirement is future terminal commit authority, which is explicitly
deferred rather than inferred from the active PAUTH.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666274` authorizes project-level Harness Parity implementation
  while preserving bridge, review, claim, start, verification, and operation-
  time gates.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` requires nonimpairing background
  window containment.
- The 2026-07-15 owner directive forbids resolving console visibility by
  disabling, suppressing, or excluding any harness.
- WI-5298 and its terminal version 006 verdict establish the predecessor
  baseline and close shared-path ownership.
- Versions 003 and 004 record the prior failed start and the exact corrections
  required before reconsideration.

## Owner Decisions / Input

No new owner decision is required to review or implement this exact source/test
scope. A separate owner decision will be required only before the atomic local
terminal commit because the active PAUTH expressly forbids `git_commit`.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5368 live-observer evidence plus terminal WI-5298 source/test baseline","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact ChatGPT/conhost ancestry plus Codex internal Git-manager markers","before_behavior":"Only the WI-5298 add -u form is recognized; other marker-qualified internal Git commands may surface visible consoles.","after_behavior":"All currently observed marker-qualified Codex internal Git-manager consoles are hidden while every Git command continues and exits naturally.","self_descriptive_naming":"The matcher and tests describe the qualifying Codex Git provenance rather than one historical subcommand.","obsolete_guidance_disposition":"No dispatcher-disable, harness-disable, routing, or process-lifecycle guidance is introduced.","history_preservation":"WI-5298 remains terminal and unchanged; WI-5368 extends only the residual command-family matcher and focused tests.","baseline":{"source_sha256":"A8F6169E51CB1E40796A764A6A6596F183541139A29DD0D44AFF84A29B1A677C","test_sha256":"83CA43CF6CB140B08BB4DEF269C18AC6641193B618B1BE21CBA24D0B4223CDA6","focused_tests":"13 passed"},"expected_result":{"focused":"all observed command forms qualify and every near miss remains rejected","live":"zero visible qualifying windows while commands complete naturally"},"rollback":{"instructions":"use a separately governed exact two-file repair","verification":"focused near-miss suite plus live observer"},"hard_invariants":["hide only","no process lifecycle action","no Git interception","no dispatcher or eligibility mutation","fail open on ambiguity"],"fail_closed_conditions":["ancestry broadened beyond ChatGPT.exe","required markers made optional","arbitrary Git consoles hidden","process or dispatcher state changed","file-only VERIFIED attempted"],"essential_context_preservation":"Retain exact event, process, marker, singleton, authorization, and nonimpairment evidence."}
```

## Specification-Derived Verification Plan

| Governing requirement | Verification after GO | Required result |
| --- | --- | --- |
| Project authorization and independent review | Fresh claim plus schema-v3 implementation start against a new GO with canonical author-session metadata | Exact two targets allowed; proposal and GO author sessions differ. |
| Full command coverage | Focused pytest module with parameterized observed command shapes | `write-tree`, `read-tree`, `diff`, `status`, `ls-files`, and pathspec `add` shapes qualify. |
| Near-miss isolation | Focused malformed-marker, missing-marker, ancestry, executable, event, and duplicate-key tests | Unrelated user/tool Git and every ambiguous form remain untouched. |
| Hide-only nonimpairment | Static source review plus focused side-effect assertions | `ShowWindowAsync(SW_HIDE)` is the sole target-window/process effect; no termination, interception, or routing mutation exists. |
| Scope and quality | Scoped status/diff/numstat, pytest, Ruff check, Ruff format check, and `git diff --check` | Only the exact source/test hunks exist and every mechanical gate passes. |
| Terminal integrity | Independent review plus an owner-approved exact local-commit PAUTH | No file-only VERIFIED; exact implementation/bridge cohort is committed atomically or the thread remains nonterminal. |

## Acceptance Criteria

1. A fresh independent GO carries canonical author-session provenance and
   passes the implementation-start gate against the exact clean baseline.
2. All observed Codex internal Git-manager commands carrying both exact
   markers and the existing ChatGPT/conhost provenance are hidden.
3. Commands continue running and exit naturally with unchanged results.
4. User/tool Git, malformed or missing markers, non-ChatGPT ancestry,
   non-top-level events, and non-Git executables remain untouched.
5. No process, Git operation, dispatcher, TAFE, bridge route, harness role, or
   eligibility mutation occurs.
6. Independent terminal verification uses an exact atomic finalizer only after
   matching commit authority exists; otherwise the report remains nonterminal.

## Pre-Filing Preflight Subsection

The governed revision helper must run the completed candidate through the live
applicability and clause preflights after inserting authoritative author
metadata. Required results are `preflight_passed: true`, no missing required
specifications, no unclassified targets, and zero must-apply evidence gaps or
blocking gaps. Any version race, claim loss, authorization denial, or preflight
failure aborts filing.

## Risk And Rollback

The main technical risk is hiding an unrelated Git console. Exact executable,
two Codex markers, top-level event shape, `conhost.exe`, and bounded
`ChatGPT.exe` ancestry constrain that risk while ambiguity continues to fail
open. The governance risk is a file-only VERIFIED under a PAUTH that forbids
commit; the explicit terminal stop condition prevents that outcome. Before
implementation, rollback is an append-only disposition. After authorized
implementation, rollback is an exact two-file governed repair; no broad reset,
history rewrite, process termination, or dispatcher change is permitted.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
