NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T14-11-16Z-prime-builder-A-70c39b
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; resolved_role=prime-builder; dispatch selected GO gtkb-wi4996-target-path-dispatch-serialization

# WI-4996 Target-Path Dispatch Serialization - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4996-target-path-dispatch-serialization
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4996-target-path-dispatch-serialization-004.md
Approved proposal: bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4996
Recommended commit type: fix

---

## Implementation Claim

Implemented target-path serialization for Prime Builder GO dispatch by making implementation-start authorization the primary guard and dispatcher filtering a pre-spawn optimization.

The implementation:

- adds one shared target-pattern overlap predicate in `scripts/implementation_authorization.py`;
- extends `cross_claim_path_collision_reason` so exact, glob-vs-file, and conservative glob-vs-glob overlaps use the same predicate;
- makes `create_authorization_packet(..., session_id=...)` refuse begin-time packet creation when another active session holds a live claim plus valid named packet with overlapping targets;
- preserves the same-session exemption for legitimate multi-thread Prime work;
- makes dispatcher Prime selection suppress later same-batch GO items whose target paths overlap an earlier retained GO item;
- makes dispatcher Prime selection suppress later-tick GO items when an in-flight claim/named packet already reserves overlapping targets;
- records expected target-path overlap outcomes in `dispatch-suppressions.jsonl`, not `dispatch-failures.jsonl`;
- keeps NO-GO revision dispatch and Loyal Opposition NEW/REVISED dispatch outside the target-path filter.

The approved target file `scripts/implementation_start_gate.py` did not need direct edits because it already calls `cross_claim_path_collision_reason`; the shared helper change extends the protected-mutation backstop to glob-vs-file and conservative glob-vs-glob overlap without forking gate logic.

## Files Changed

- `scripts/implementation_authorization.py`
  - Added `target_patterns_overlap` and supporting normalization/glob helpers.
  - Routed `path_authorized` and `cross_claim_path_collision_reason` through the shared predicate.
  - Added optional `session_id` to `create_authorization_packet` and dispatch packet issuance so begin-time authorization can block overlapping active claims.
- `scripts/dispatcher_runtime.py`
  - Added target-path overlap suppression constants to expected suppression reasons.
  - Added same-batch and in-flight Prime GO target-path filtering before spawn.
  - Records overlap suppressions to `dispatch-suppressions.jsonl`.
  - Passes the dispatch work-intent session into packet issuance so a race caught at packet creation remains guarded.
- `platform_tests/scripts/test_implementation_authorization.py`
  - Added exact, glob-vs-file, disjoint-prefix, glob-vs-glob, different-session block, and same-session allow coverage for the shared predicate and begin-time guard.
- `platform_tests/scripts/test_implementation_start_gate.py`
  - Added author session metadata to GO/proposal fixtures required by the current gate.
  - Added glob-vs-file cross-claim protected-mutation coverage.
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
  - Added same-batch suppression, disjoint fanout, and later-tick in-flight suppression coverage.

No application/adopter files were changed. `platform_tests/scripts/test_dispatcher_runtime.py` remained unchanged but was included in verification to cover the broader dispatcher runtime surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision was required. This implementation follows the LO-approved `-004` design: implementation-start authorization is primary, dispatcher suppression is an optimization, and no dispatcher-only interactive exposure is accepted.

The carried owner/program evidence remains:

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING`

## Prior Deliberations

- `bridge/gtkb-wi4995-document-lease-held-health-004.md` - parent NO-GO documenting WI-4995/WI-4992 shared-file contention and recording WI-4996 as follow-on work.
- `bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md` - prior NO-GO with findings N1 through N5.
- `bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md` - approved revised implementation proposal.
- `bridge/gtkb-wi4996-target-path-dispatch-serialization-004.md` - GO verdict authorizing this implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Role resolved with `groundtruth-kb/.venv/Scripts/gt.exe harness roles`; selected latest bridge status was GO; work-intent claim and implementation authorization packet were acquired before protected edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Report carries forward all linked specs from `-003`; changed files remain within approved `target_paths` scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked surface to exact command evidence; focused tests and lint/format checks are listed below. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report preserves Project Authorization, Project, and Work Item metadata; helper filing preserves the versioned bridge audit trail. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `create_authorization_packet(..., session_id=...)` now blocks overlapping active claims before packet creation; protected-mutation gate inherits the same overlap predicate through `cross_claim_path_collision_reason`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher tests cover same-batch suppression, disjoint fanout, and later-tick in-flight suppression; `gt bridge dispatch status --json` reports routing health PASS. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Dispatcher remains the coordination surface; target-path overlap is recorded as expected suppression evidence instead of provider failure evidence. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Implementation-start authorization and protected-mutation regression tests cover Codex file-edit guard behavior without relying on external hooks. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work was performed through bridge GO, implementation authorization, tests, and this report rather than transient chat state. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The fix preserves artifact-first change control through append-only bridge reporting and focused regression evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This post-implementation report records implementation, verification, risks, and LO asks for the next lifecycle transition. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No owner decision was required or requested in prose; carried owner evidence is recorded above. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All edits are platform-side under `scripts/` and `platform_tests/`; no Agent Red or adopter application path was touched. |
| `GOV-STANDING-BACKLOG-001` | WI-4996 remains the tracked backlog response to the WI-4995/WI-4992 contention; no untracked future-work decision was introduced. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi4996-target-path-dispatch-serialization --json --compact
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4996-target-path-dispatch-serialization
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4996-target-path-dispatch-serialization
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short --basetemp .harness-tmp\pytest-wi4996
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short --basetemp .harness-tmp\pytest-wi4996
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- scripts/implementation_authorization.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json
```

## Observed Results

- Harness role resolution: Codex harness `A` resolved to `prime-builder`.
- Bridge scan/show: selected thread latest status remained `GO` before implementation; this report is the next `NEW` artifact.
- Claim: `bridge_claim_cli.py claim gtkb-wi4996-target-path-dispatch-serialization` acquired a `go_implementation` claim for session `2026-07-05T14-11-16Z-prime-builder-A-70c39b`.
- Authorization packet: `implementation_authorization.py begin --bridge-id gtkb-wi4996-target-path-dispatch-serialization` succeeded with packet hash `sha256:1fc4142ed9d55a3d32dfbbe66a2eac1df95c5b96b57792ec77fb4e5bf5f73291`.
- Initial pytest attempt without `--basetemp` failed before test execution with Windows temp permission error `[WinError 5] Access is denied: C:\Users\micha\AppData\Local\Temp\pytest-of-micha`; reruns used repo-local `.harness-tmp\pytest-wi4996`.
- Pre-format focused pytest: `438 passed, 2 warnings`.
- Post-format focused pytest: `438 passed, 2 warnings in 55.94s`.
- `ruff check`: `All checks passed!`.
- `ruff format --check`: `7 files already formatted`.
- Scoped `git diff --check` with `cr-at-eol`: exit 0. The default Git whitespace check treats CRLF-tracked files as trailing whitespace on this workstation, so the CR-aware check was used for the mixed-EOL scoped diff.
- Dispatcher status: top-level `health_status` PASS and routing config PASS. The complex lifecycle rollup still reports missing scheduled tasks for dispatcher supervisor/watchdog; that appears to be existing host setup state outside this WI-4996 implementation scope.

## Acceptance Criteria Status

- [x] `implementation_authorization.py begin --bridge-id <later>` refuses packet creation when another active session holds a work-intent claim plus valid named packet whose targets overlap.
- [x] Begin-time collision check allows same-session overlap and non-overlap, and continues to ignore missing/invalid/expired packet surfaces through existing fail-soft registry behavior.
- [x] Protected-mutation gate continues to block exact-path cross-claim edits through `cross_claim_path_collision_reason`.
- [x] Protected-mutation gate now covers glob-vs-file overlap via the shared predicate (`scripts/*.py` vs `scripts/dispatcher_runtime.py`).
- [x] Dispatcher same-batch Prime GO filtering launches only the oldest retained item when two selected GO items share target paths and records `target_path_overlap_selected`.
- [x] Dispatcher disjoint Prime GO items still fan out to the effective cap.
- [x] Dispatcher later-tick Prime GO filtering suppresses a single selected item when an in-flight claim/named packet reserves overlapping targets and records `target_path_overlap_inflight`.
- [x] NO-GO revision dispatch and Loyal Opposition NEW/REVISED dispatch remain outside the target-path filter; the filter only applies to Prime GO items.
- [x] Expected target-path overlap outcomes are routed to `dispatch-suppressions.jsonl` through existing suppression infrastructure.

## Advisory Implementation-Phase Notes From GO

- Preserved distinct axes: registry/IO lookup failures remain fail-soft inside `cross_claim_path_collision_reason`, while glob-vs-glob ambiguity is fail-closed unless top-level prefixes prove disjoint.
- Reused one predicate: `target_patterns_overlap` is shared by begin-time authorization, protected-mutation cross-claim checks, and dispatcher filtering.
- Added same-session non-collision test coverage.
- Added disjoint fanout coverage to prove conservative overlap logic does not suppress normal disjoint work.

## Risk And Rollback

Residual risk is conservative over-serialization for ambiguous glob-vs-glob pairs that share a top-level prefix. That is intentional per the approved design and safer than allowing concurrent edits to shared source files.

Rollback is straightforward for source behavior: revert the changes in `scripts/implementation_authorization.py`, `scripts/dispatcher_runtime.py`, and the three test files listed above. Bridge artifacts are append-only and should not be rewritten.

## Loyal Opposition Asks

1. Verify that the shared overlap predicate and begin-time authorization path satisfy the `-004` GO design.
2. Verify that dispatcher target-path overlap outcomes are suppressions, not provider/runtime failures.
3. Return VERIFIED if the implementation and this report satisfy WI-4996; otherwise return NO-GO with concrete findings.
