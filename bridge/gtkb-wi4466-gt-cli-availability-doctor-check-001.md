NEW

bridge_kind: prime_proposal
Document: gtkb-wi4466-gt-cli-availability-doctor-check
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a460ee9e-4606-4e64-bd03-cd7eae14bdef
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (resolved via ::init gtkb pb, harness B); explanatory output style; autonomous project-completion loop; model claude-opus-4-8[1m]
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22
Project: PROJECT-GTKB-COMMAND-SURFACE
Work Item: WI-4466
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py", "platform_tests/scripts/test_check_gt_cli_availability.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4466: Deterministic gt CLI availability doctor check (PATH or canonical venv fallback)

## Summary

WI-4466 (P2, `command-surface`, origin=defect): during FAB-16 bridge work, a Codex/PowerShell session could not invoke `gt` because the shim was not on PATH, forcing fallbacks to direct SQLite reads and the Python CLI entrypoint to retrieve backlog/project-authorization facts. This raises the chance of agents getting lost, using inconsistent command paths, or bypassing the intended operator surface. (This exact friction recurred at the start of the authoring session for this very proposal.)

Per the WI-4466 acceptance summary, the fix is a **deterministic `gt` invocation path** — either `gt` is on PATH, or startup/tooling exposes and verifies the canonical venv fallback — plus a **doctor or regression check that catches missing CLI availability** before bridge/project work depends on it.

WI-4530 (GO at `DELIB-20263239`) already delivered the pure launcher-shim *generator* (`scripts/install_gt_path_shim.py`) and explicitly deferred "wiring this generator into the install / bootstrap path" and the verification follow-on to a later slice "with its own authorization." This proposal implements that deferred **verification** follow-on as a registered doctor check: it makes `gt` availability machine-checkable and surfaces the canonical venv fallback, without taking on the risky PATH-placement install concern (still deferred).

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4466 is the backlog authority for this fix (P2 `command-surface` defect). Single-WI scope (one new registered-check module + one platform test); the `CLAUSE-VISIBILITY-BULK-OPS` clause is triggered by the citation but is `not_applicable` here (no inventory artifact, no bulk status mutation).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` (active; includes WI-4466; allows `source` + `test_addition`; forbids formal-artifact mutation without packet, deploy, force-push, credential lifecycle, broad bulk status mutation).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + **`.claude/rules/project-root-boundary.md`** — both `target_paths` are in-root under the GT-KB project root. The check resolves the canonical venv fallback at the in-root relative path `groundtruth-kb/.venv/Scripts/gt.exe` (Windows) / `groundtruth-kb/.venv/bin/gt` (POSIX). The check reads only; it writes nothing, in-root or out-of-root. The narrow External Harness Executable Resolution Exception is not needed here because the check inspects the in-root venv launcher, not an out-of-root harness executable.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge (always-applicable bridge-governance trigger). Adds no aggregate-queue artifact and mutates no bridge workflow state beyond this thread.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked above.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the Verification Plan below maps each acceptance criterion (PATH pass, venv-fallback warning, genuinely-missing fail, registry auto-discovery, fallback-path consistency with the WI-4530 generator) to an executed test.
- **ADR-REGISTRY-DISCOVERY-001** — the new check is added through the dynamic doctor-check registry (`groundtruth_kb.project.checks.register_check`), the idiomatic extension point; it requires no edit to `doctor.run_checks`.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — a durable, tracked check that converts a per-session-rediscovered failure mode into a machine-checkable invariant.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4466 acceptance summary), WI-4530's GO (`DELIB-20263239`) explicitly deferred this verification follow-on, the bounded PAUTH authorizes the `source` + `test_addition` work, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / the project-root-boundary rule defines the in-root constraint this slice respects (read-only, in-root paths). No new or revised formal specification is required.

## Prior Deliberations

A live semantic deliberation search was run during authoring (`deliberations search "gt CLI shim PATH availability PowerShell Codex venv fallback command surface"`, limit 8).

- **`DELIB-20263239` — WI-4530 gt CLI PATH shim generator (GO, 2026-06-14).** The direct parent. WI-4530 built the pure launcher generator and deferred (a) install/PATH placement and (b) the verification follow-on to a later authorized slice. This proposal implements the verification follow-on (the doctor check) and deliberately leaves the PATH-placement install concern deferred. The check resolves the same venv launcher path the WI-4530 generator emits, and a test cross-checks that consistency.
- **`DELIB-20263464` — WI-4395 uv cache command-surface disposition (LO advisory, 2026-06-13).** Sibling command-surface determinism work in the same project; cited for shared framing (canonical, tracked command surfaces over per-session rediscovery).
- **`DELIB-20261489` — GT-KB Discoverability CLI Slice 2 (GO).** Related `gt`-surface work; cited to confirm this proposal does not duplicate or conflict with discoverability-CLI scope (this is availability verification, not new command surface).
- **`DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` — owner directive (2026-06-22).** Owner directed Prime Builder to complete WI-4395 + WI-4466 and retire PROJECT-GTKB-COMMAND-SURFACE; authorizes this slice.

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622`** — owner directive (interactive session a460ee9e, 2026-06-22) to drive PROJECT-GTKB-COMMAND-SURFACE to VERIFIED/retired by completing its open work items. This authorizes the bounded `source` + `test_addition` work recorded in `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22`.

## Design

New module `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py` — registered via `@register_check("gt_cli_availability")` (ADR-REGISTRY-DISCOVERY-001), auto-discovered by `get_registered_checks()`; no edit to `doctor.run_checks`. Pure-Python, stdlib only, read-only.

`check_gt_cli_availability(target: Path) -> ToolCheck` resolves a deterministic three-state verdict:

1. **`gt` on PATH** (`shutil.which("gt")` truthy) -> `status="pass"`, message names the resolved path. This is the optimal state.
2. **`gt` not on PATH but the canonical venv launcher exists** at `target/groundtruth-kb/.venv/Scripts/gt.exe` (Windows) or `target/groundtruth-kb/.venv/bin/gt` (POSIX) -> `status="warning"`. The CLI IS deterministically available via the documented fallback; the warning records that it is not yet on PATH and points to `scripts/install_gt_path_shim.py` (the WI-4530 generator) and the `python -m groundtruth_kb` entrypoint.
3. **Neither on PATH nor a venv launcher present** -> `status="fail"`. This is the "missing CLI availability" condition the acceptance summary requires the check to catch, with guidance to create the venv / generate a launcher.

The venv-launcher relative path is computed identically to `scripts/install_gt_path_shim.resolve_venv_gt_exe`, keeping WI-4466 and WI-4530 from drifting; a test asserts that equivalence.

**Explicitly out of scope** (kept minimal and consistent with the WI-4530 deferral): placing a launcher on a user-PATH directory, mutating PATH, running an install/bootstrap step, or launching a subprocess. The check is read-only verification; PATH placement remains the deferred install slice's responsibility.

## Verification Plan (Specification-Derived)

| Acceptance criterion (WI-4466) | Test (in `platform_tests/scripts/test_check_gt_cli_availability.py`) | Method |
|---|---|---|
| `gt` on PATH yields a deterministic pass | `test_gt_on_path_passes` | monkeypatch `shutil.which` -> a fake path; assert `status == "pass"` and the path appears in the message |
| Not on PATH but canonical venv fallback present yields a functional-but-suboptimal warning | `test_venv_fallback_warns` | monkeypatch `which` -> None; create the platform-appropriate venv launcher file under a tmp `target`; assert `status == "warning"` and message names the fallback + `python -m groundtruth_kb` |
| Genuinely missing CLI is caught as a failure | `test_unavailable_fails` | monkeypatch `which` -> None; tmp `target` with no venv; assert `status == "fail"` |
| Check is auto-discovered by the registry | `test_check_is_registered` | assert `"gt_cli_availability" in get_registered_checks()` |
| Fallback path stays consistent with the WI-4530 generator | `test_fallback_path_matches_shim_generator` | import `scripts/install_gt_path_shim.resolve_venv_gt_exe`; assert the check's resolved fallback path equals it for the current `sys.platform` |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_check_gt_cli_availability.py -q --tb=short`.

## Risk / Rollback

- **Risk: low.** Net-new read-only registered check + its tests. No PATH mutation, no subprocess launch, no install step, no out-of-root access, no KB mutation. The check only reads `shutil.which` and tests for a file's existence under the in-root venv.
- **Severity calibration:** the check is `required=False` and emits `warning` (not `fail`) whenever the venv fallback is present, so a normal fresh checkout (venv present, `gt` not yet on PATH) does not turn `gt project doctor` red; only a genuinely unusable command surface (no PATH `gt` and no venv) fails.
- **Rollback:** delete the two new files. The registry auto-discovery means removal needs no `doctor.py` edit. No migration, no schema, no config edit, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (a registered doctor check + its regression suite), not a repair of existing in-repo code. Per the Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
