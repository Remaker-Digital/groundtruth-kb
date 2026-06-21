NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Storm watchdog detects only codex-family processes; cost-optimized routing now prefers Ollama(D)/OpenRouter(F) whose runaway spawns it would miss

bridge_kind: prime_proposal
Document: gtkb-storm-watchdog-detect-noncodex-process-families
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4631

target_paths: ["scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_harness_storm_watchdog.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The emergency dispatch-storm watchdog `harness_storm_watchdog.ps1` detects and trips on `codex`-family headless processes ONLY: it counts `Get-Process -Name codex` against `CODEX_THRESHOLD = 15` and kills the family `{codex, node_repl-under-OpenAI\Codex, codex-command-runner*, codex-windows-sandbox*}`. Per the canonical harness registry (`harness-state/harness-registry.json` `invocation_surfaces`), the cost-optimized Loyal Opposition dispatch targets Ollama (`D`, `dispatch_cost = 20`) and OpenRouter (`F`, `dispatch_cost = 20`) are launched as `groundtruth-kb/.venv/Scripts/python.exe scripts/ollama_harness.py` and `... scripts/openrouter_harness.py` respectively - i.e. `python.exe` processes, not `codex`-family processes. Because `config/dispatcher/rules.toml` now ranks LO dispatch by `cost` first (`bridge-loyal-opposition-cheap-fast-default`: `prefer = ["cost", "availability", ...]`), D and F are the preferred LO targets. A runaway dispatch storm originating from D or F therefore produces a population of `scripts/ollama_harness.py` / `scripts/openrouter_harness.py` `python.exe` processes that the watchdog never counts and never throttles. Such a storm is caught only by the backend-agnostic global concurrency cap added in WI-4472 (default 8 live headless processes), leaving the watchdog - the owner-mandated emergency fallback (`DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612`: "event-driven with watchdog fallback") - blind to the very backends the routing layer now prefers.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is required. This is a defect: the watchdog's detection set drifted out of alignment with the canonical harness registry after cost-optimized routing made Ollama(D)/OpenRouter(F) the preferred low-cost LO targets. The fix realigns the watchdog's detection surface with the registry-declared `invocation_surfaces` for those backends and lands the watchdog on a tracked, reviewable, testable surface. Governing authority already exists: the file-bridge authority model (`GOV-FILE-BRIDGE-AUTHORITY-001`), the tracked-surface bias for load-bearing automation (`.claude/rules/codex-way-of-working.md` § Tracked Surface Bias, `DELIB` 2026-04-29 decision-ledger entry), and the standing-backlog authority (`GOV-STANDING-BACKLOG-001`) under which WI-4631 is tracked.

## Bridge Protocol Compliance

This proposal is filed as the next numbered, versioned bridge file in its thread (`bridge/gtkb-storm-watchdog-detect-noncodex-process-families-001.md`) under the append-only numbered-file-chain discipline of `GOV-FILE-BRIDGE-AUTHORITY-001`: no prior bridge version is deleted or rewritten, and the file's first non-blank line carries the canonical `NEW` status token. Loyal Opposition verdicts and any post-implementation report continue the same numbered chain (`-002`, `-003`, ...) without mutating earlier versions.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/ops/harness_storm_watchdog.ps1`, `platform_tests/scripts/test_harness_storm_watchdog.py`.

Current vs. target placement (load-bearing design point): the watchdog currently lives at the git-ignored runtime-ops path `.gtkb-state/ops/harness_storm_watchdog.ps1` (deployed there as an emergency under the 2026-06-12 owner AUQ; `.gtkb-state/` is ignored by `.gitignore` line 523). A git-ignored file cannot be staged into the VERIFIED commit-finalization commit required by `.claude/rules/file-bridge-protocol.md` § "Mandatory VERIFIED Commit-Finalization Gate", and the repo has no PowerShell/Pester test convention. To deliver a tracked, reviewable, committable, and testable fix, the widened watchdog is landed at the already-tracked ops directory `scripts/ops/` (which today tracks `install_ollama_autostart_task.ps1`). This folds in the promotion that the WI cross-references as "Related: WI-4474 (promote watchdog from untracked .gtkb-state/ops to tracked scripts/ops/)" - the promotion is the enabling vehicle for the WI-4631 fix, not separate scope. Both target paths are therefore net-new tracked files: the promoted+widened source and its new content-assertion pytest. The current `.gtkb-state/ops/harness_storm_watchdog.ps1` is the source whose behavior this proposal preserves-and-widens; it is left in place as the runtime copy until the scheduled task is repointed (see Proposed Scope step 4).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority model governs this implementation+verification cycle; the fix is delivered through the file-bridge protocol and its VERIFIED commit-finalization gate, which is precisely why the fix must land on a tracked (stageable) path rather than the git-ignored runtime copy.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the watchdog is promoted from a transient git-ignored runtime artifact into a durable tracked artifact with a regression test, preserving the emergency-control behavior as a governed artifact rather than ungoverned ops state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification for the change (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below derives each test from a cited spec clause and gives executable commands, satisfying the mandatory VERIFIED-conditional testing contract.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the mandatory Project Authorization / Project / Work Item linkage lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21 / PROJECT-GTKB-RELIABILITY-FIXES / WI-4631).
- `SPEC-AUQ-POLICY-ENGINE-001` - not implicated: this fix changes only headless process-detection logic and a regression test; it adds no owner-decision channel, no AUQ surface, and no policy-engine routing, so the AUQ policy engine is out of scope for this change. Cited for completeness of the seeded link set.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform ops (`scripts/ops/`) and platform tests (`platform_tests/scripts/`); no adopter/application surface (`applications/`) is touched, so no platform/application isolation boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4631 is a standing-backlog work item (origin=improvement, P3) under PROJECT-GTKB-RELIABILITY-FIXES; this proposal advances it under the standing-backlog work authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - tangentially relevant: the watchdog is the host-side emergency fallback for dispatch-storm control. This proposal does not alter Codex hook parity; it is cited because the watchdog sits in the same fallback-mechanism family. No hook-parity behavior changes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix keeps the watchdog's emergency-control behavior artifact-backed (tracked source + regression test + bridge audit trail) rather than inferred from ungoverned runtime ops state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the watchdog (currently an ungoverned runtime artifact) triggers its promotion into a tracked, lifecycle-managed artifact with a verified test surface, per the lifecycle-trigger discipline.

## Prior Deliberations

- `DELIB-20262481` - Loyal Opposition Independent Proposal Review: Cross-Harness Dispatch Concurrency Cap - establishes the WI-4472 backend-agnostic global cap (default 8) that the WI identifies as the ONLY current control catching D/F storms; this proposal restores watchdog coverage as the complementary fast emergency control.
- `DELIB-20265232` - Loyal Opposition Review - gtkb-bridge-auto-dispatch-storm NEW - the dispatch-storm incident thread (the storm class this watchdog exists to contain).
- `DELIB-20265231` - Loyal Opposition Review - gtkb-bridge-auto-dispatch-storm VERIFIED - terminal verification of the dispatch-storm remediation thread; context for why a fast emergency watchdog remains required alongside the cap.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612` - "Activation model: event-driven with watchdog fallback" - the owner decision that designates the watchdog as the emergency fallback mechanism; a fallback blind to the preferred low-cost backends does not fulfil that role.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (2026-06-21); WI-4631 is in scope of this batch authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the bounded project authorization envelope covering the 2026-06-21 non-fast-lane PROJECT-GTKB-RELIABILITY-FIXES batch; WI-4631 (origin=improvement, P3) is an included member, so implementation of this proposal is authorized through active project membership once Loyal Opposition records GO.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch and directing NEW proposals for the open work items in that project; this proposal is filed under that authorization. No additional per-item owner decision is required for this defect-class fix.

## Proposed Scope

Minimal, single-concern change. Preserve all existing watchdog behavior (heartbeat, log-rotate, never-kill-`claude`, kill-switch assertion) and add backend-agnostic detection for the registry-declared non-codex LO backends, landed on a tracked surface.

1. Land `scripts/ops/harness_storm_watchdog.ps1` as the tracked, widened watchdog (content promoted verbatim from the current `.gtkb-state/ops/harness_storm_watchdog.ps1`, then widened):
   - Add a Python-backend detection set alongside the codex-family set. Match `python.exe`/`python` processes whose command line invokes `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` (the registry `invocation_surfaces[*].headless.argv` for harnesses D and F). Use `Get-CimInstance Win32_Process` to read `CommandLine` (the `Get-Process` object does not expose the command line), filtered to the GT-KB venv interpreter path / the two harness script names so ordinary developer `python.exe` processes are never matched.
   - Generalize the threshold check: trip when the codex count exceeds `CODEX_THRESHOLD` (unchanged) OR when the non-codex headless-harness count exceeds a new `NONCODEX_THRESHOLD` (default 15, matching the codex sensitivity). Keep `claude` excluded from all kill sets (conservative-by-design invariant preserved).
   - On trip, assert the existing `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch (unchanged) and kill the union of matched codex-family and matched non-codex-harness processes. Preserve the `node_repl` image-path guard and add the symmetric command-line guard for the python-backend set so only GT-KB harness `python.exe` processes are killed.
   - Update the heartbeat/log lines to record `noncodex=<n>` and `noncodexThreshold=<n>` alongside the existing `codex`/`family` counters so the intervention audit trail reflects both detection paths.
   - Preserve the existing log-rotate guard and `$ErrorActionPreference = 'SilentlyContinue'` posture.
2. Add `platform_tests/scripts/test_harness_storm_watchdog.py` - a Python content-assertion regression suite over the tracked `.ps1` (the repo's established pattern for asserting non-Python source content; cf. `platform_tests/scripts/test_work_tree_stray_detector.py` AST/source assertions). The suite reads the tracked script text and asserts the detection set, threshold logic, and safety invariants (see Verification Plan). This is a static-content contract test, not a live process-kill test (killing real processes in CI is unsafe and out of scope).
3. Cross-check the widened detection set against `harness-state/harness-registry.json` so the test fails if a future low-cost LO backend is added to the registry with a `python.exe`-style `invocation_surfaces` argv that the watchdog does not yet match (drift guard for the exact failure class this WI documents).
4. Repoint the scheduled-task launcher to the tracked path: update the `GTKB-HarnessStormWatchdog` task (and the `run_harness_storm_watchdog_hidden.vbs` runtime wrapper under `.gtkb-state/ops/`, which is itself git-ignored runtime state) to execute `scripts/ops/harness_storm_watchdog.ps1`. The VBS/task repoint is a runtime-ops operation (git-ignored launcher pointing at the tracked script); the tracked deliverable is the `.ps1` and its test. Document the repoint command in the implementation report.

Out of scope (would require a new requirement, explicitly deferred): the WI's optional alternative of "model/display that the watchdog is intentionally codex-only and rely solely on the WI-4472 cap for other backends." Adopting that posture would be a behavior/contract decision, not a defect fix, and is not pursued here.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (fix delivered on a stageable tracked surface) | `test_watchdog_lands_on_tracked_path` | `scripts/ops/harness_storm_watchdog.ps1` exists and is git-tracked (not git-ignored), so it can be staged into the VERIFIED commit-finalization commit. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (detection widened to non-codex backends) | `test_watchdog_detects_ollama_and_openrouter_backends` | The script text references both `ollama_harness.py` and `openrouter_harness.py` in its process-detection logic. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (non-codex trip path exists) | `test_watchdog_has_noncodex_threshold_trip` | The script defines a non-codex threshold and trips the kill-switch when the non-codex headless-harness count exceeds it (not only on the codex count). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (registry-aligned detection; drift guard) | `test_watchdog_covers_registry_lowcost_backends` | For every harness in `harness-state/harness-registry.json` whose `invocation_surfaces[*].headless.argv` invokes a `*_harness.py` python script (currently D=ollama, F=openrouter), the watchdog script text matches that harness's script name. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (conservative-by-design invariant preserved) | `test_watchdog_never_kills_claude` | The script never adds `claude` to a kill set and the python-backend kill path is guarded to GT-KB harness processes only (venv interpreter / `*_harness.py` command line). |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (existing safety behavior preserved) | `test_watchdog_preserves_heartbeat_and_logrotate` | The script retains the heartbeat write, the `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch assertion, and the 1MB log-rotate guard. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_harness_storm_watchdog.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_harness_storm_watchdog.py`
- `python -m ruff format --check platform_tests/scripts/test_harness_storm_watchdog.py`

Note: `ruff` lints/formats Python only. The tracked `.ps1` is exercised by the content-assertion suite above; no PowerShell linter is configured in-repo, so the `.ps1` is verified by the pytest content contract rather than by `ruff`.

## Acceptance Criteria

1. `scripts/ops/harness_storm_watchdog.ps1` exists, is git-tracked, and preserves every prior watchdog behavior (heartbeat, kill-switch assertion, `claude` exclusion, `node_repl` image-path guard, log-rotate).
2. The watchdog detects runaway `python.exe` processes running `scripts/ollama_harness.py` (Ollama/D) and `scripts/openrouter_harness.py` (OpenRouter/F), guarded so ordinary developer `python.exe` processes are never matched, and trips the kill-switch + kill path when their count exceeds the non-codex threshold.
3. `platform_tests/scripts/test_harness_storm_watchdog.py` passes; its registry drift-guard test would fail if a future low-cost `*_harness.py` LO backend were added to the registry without corresponding watchdog coverage.
4. `ruff check` and `ruff format --check` are clean on the new Python test file.
5. The scheduled-task launcher targets the tracked `scripts/ops/harness_storm_watchdog.ps1` (repoint documented in the implementation report).

## Risks / Rollback

- Risk: over-broad `python.exe` matching could kill an unrelated developer python process during a storm. Mitigation: the python-backend kill path is guarded to the GT-KB venv interpreter path and/or the two `*_harness.py` script names read from the command line; the test asserts the guard is present.
- Risk: `Get-CimInstance Win32_Process` command-line reads can be slower than `Get-Process`. Mitigation: the watchdog runs ~once per minute and the CIM query is filtered; the marginal cost is negligible relative to the emergency it guards. The codex-family detection path remains `Get-Process`-based and unchanged.
- Risk: repointing the scheduled task could momentarily leave no active watchdog. Mitigation: the existing git-ignored `.gtkb-state/ops/harness_storm_watchdog.ps1` runtime copy is left in place until the task is confirmed repointed; the repoint is a single `Register-ScheduledTask`/`Set-ScheduledTask` step documented in the report.
- Risk: drift-guard test coupling to the registry could fail on unrelated registry edits. Mitigation: the test scopes itself to harnesses whose `invocation_surfaces` argv invokes a `*_harness.py` python script, so non-python backends (codex/claude/gemini) do not trigger it.
- Rollback: delete `scripts/ops/harness_storm_watchdog.ps1` and its test and re-point the task at the prior `.gtkb-state/ops/` copy. The change is additive (net-new tracked files + a task repoint) and fully reversible with no migration and no MemBase mutation.

## Files Expected To Change

- `scripts/ops/harness_storm_watchdog.ps1`
- `platform_tests/scripts/test_harness_storm_watchdog.py`

## Recommended Commit Type

`fix`
