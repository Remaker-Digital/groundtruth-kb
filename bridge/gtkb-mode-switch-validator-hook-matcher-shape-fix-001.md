NEW

# gtkb-mode-switch-validator-hook-matcher-shape-fix — repair validate_bridge_substrate hook-registration probe so it walks the real Claude/Codex matcher-wrapper shape

bridge_kind: prime_proposal
Document: gtkb-mode-switch-validator-hook-matcher-shape-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: adbcc36c-b70b-4998-8d6f-fb37456bc126
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: 1M context window

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4353

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`validate_bridge_substrate()` in `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (lines 213–241) checks whether the cross-harness event-driven trigger is registered by walking `data["hooks"].values()` and substring-matching `hook.get("command", "")` against `"cross_harness_bridge_trigger.py"`. The probe expects each value under `"hooks"` to be a list of command dicts shaped like `{"command": "...", ...}`.

Real `.claude/settings.json` and `.codex/hooks.json` instead use a two-level nested **matcher-wrapper** shape: each key under `"hooks"` maps to a list of `{matcher: str, hooks: list[{command: str, ...}]}` wrapper dicts. The validator's substring check on the outer wrapper returns `""` (the wrapper has no `command` key), so registration is never detected even when the real files contain three matching command entries each.

The bug is visible end-to-end: `gt mode set-bridge-substrate --substrate cross_harness_trigger` fails with `bridge substrate validation failed: cross_harness_trigger is not registered in .claude/settings.json or .codex/hooks.json`, even though the active `.claude/settings.json` (lines 107, 127, 163) and `.codex/hooks.json` (lines 225, 248, 278) all contain `cross_harness_bridge_trigger.py` invocations. The only workaround is `--defer-to-next-session`, which queues the transaction at `.gtkb-state/mode-switches/pending/*.json` and bypasses the validator probe — but the SessionStart applier runs the same validator, so the deferred path is also exposed to this defect in principle.

This proposal makes the probe walk the real two-level shape (outer `hooks` dict → matcher-wrapper list → each wrapper's `hooks` field → command dicts) for both `.claude/settings.json` and `.codex/hooks.json`. It keeps the existing flat-shape path for backward compatibility (the existing test fixture uses a flat shape; preserving the flat path keeps that test green and protects any direct-flat configurations that may exist elsewhere). The platform_tests module gains a new case that constructs a fixture matching the real nested shape and asserts the probe finds the registration.

This is a surgical defect repair: a few lines of helper logic in `validation.py`, plus a new test case. No public CLI surface changes, no MemBase mutation, no governance surface change.

## Specification Links

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the requirement spec this validator is supposed to honor. The existing test file (`platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`) cites it in its docstring. The defect is that the validator's hook-shape assumption diverges from the wire shape actually used by `gt mode set-bridge-substrate`'s target deployments.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow state; this proposal is filed as `NEW` and the verdict flow remains owned by Loyal Opposition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandatory linkage-and-test-derivation contract.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item metadata block above carries this.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see Spec-Derived Verification Plan below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is the active envelope; standing scope with `included_work_item_ids: null` confers project-wide coverage, and WI-4353 is in `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-STANDING-BACKLOG-001` — WI-4353 is a freshly captured `origin=defect` row in `current_work_items`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` *(advisory)* — this proposal is itself a durable artifact recording a defect-capture decision; the WI + bridge file + post-impl report chain is the artifact-oriented capture path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` *(advisory)* — defect-capture-to-fix is the canonical lifecycle this ADR sanctions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` *(advisory)* — WI-4353 creation + this `NEW` proposal are the captured lifecycle triggers.

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — establishes the proposal-structure standards (status token, project-linkage, target_paths inline JSON, spec-derived verification heading) this body satisfies via the `gtkb-propose` scaffold path.
- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` — illustrates the precedent that source-code-only repairs with no governance-surface change route through the standing/per-project PAUTH path without minting a new envelope. Cited as procedural precedent only; this proposal is unrelated to that specific waiver scope.
- *(No prior deliberation specifically about the matcher-wrapper hook shape; the defect was surfaced today by an owner-supplied report after a `gt mode set-bridge-substrate` invocation failed against the real settings.json. Recording this proposal itself as the first capture is appropriate.)*

## Owner Decisions / Input

Owner directive on 2026-06-04 in the current session: defect report identifying `validation.py:213-241` with the matcher-wrapper-shape diagnosis, the repro command (`groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb mode set-bridge-substrate --substrate cross_harness_trigger`), the workaround (`--defer-to-next-session`), and explicit direction: "File a bridge proposal under PROJECT-GTKB-RELIABILITY-FIXES (or a similar reliability-fix project); WI captures origin=defect so it should be fast-lane-eligible." The directive identifies project (PROJECT-GTKB-RELIABILITY-FIXES), WI classification (origin=defect), and scope (surgical fix in `validation.py:213-241` + focused unit test). No further owner AskUserQuestion is required to file this proposal; the directive itself authorizes the filing. Standard Loyal Opposition `GO` is still required before implementation per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already requires that `validate_bridge_substrate()` detect cross-harness-trigger registration in `.claude/settings.json` and `.codex/hooks.json` before permitting an immediate switch. The defect is that the validator's hook-shape assumption is incomplete relative to the real wire shape; no requirement change is needed to permit the fix. The existing acceptance criterion in the cited test ("validator reports missing hook registrations when none present; validator finds registration when present in `.claude/settings.json`") remains the operative contract; this proposal widens the validator to honor the contract against the real nested shape as well as the existing flat fixture shape.

## Spec-Derived Verification Plan

The verification surface for this proposal is the existing `test_mode_switch_bridge_substrate_validation.py` module under `platform_tests/groundtruth_kb/`, augmented with a new case derived from `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.

| Linked spec | Derived test | Repro command | Expected result |
|-------------|--------------|---------------|------------------|
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | (existing) `test_substrate_artifact_validator_reports_missing_hook_registrations` — confirms validator rejects when no registrations present, and confirms it still detects the flat fixture shape. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py::test_substrate_artifact_validator_reports_missing_hook_registrations -q --no-header -p no:cacheprovider` | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | (new) `test_substrate_artifact_validator_detects_nested_matcher_wrapper_shape` — constructs a `.claude/settings.json` fixture using the real matcher-wrapper shape (`{"hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"command": "python …/cross_harness_bridge_trigger.py …"}]}]}}`) and asserts `validate_bridge_substrate(tmp_path, "cross_harness_trigger", "single_harness").is_valid is True`. Adds a parallel case for the Codex `.codex/hooks.json` shape. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py::test_substrate_artifact_validator_detects_nested_matcher_wrapper_shape -q --no-header -p no:cacheprovider` | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | (existing) `test_role_artifact_validator_required_before_substrate_write` — adjacent regression check; must remain unaffected. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py::test_role_artifact_validator_required_before_substrate_write -q --no-header -p no:cacheprovider` | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` end-to-end | Manual repro against live repo: `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb mode set-bridge-substrate --substrate cross_harness_trigger --reason "WI-4353 post-impl repro"` against the current `.claude/settings.json` + `.codex/hooks.json` state. | shell | exits 0 (no validator failure); the substrate-set transaction proceeds normally. Implementation report carries the captured stdout/stderr as evidence. |

The post-implementation report will carry forward each linked spec, the executed commands, and the observed exit codes / pytest output.

## Risk / Rollback

**Risk surface:**
- The fix changes how `validate_bridge_substrate()` walks its input, but the function's externally observable contract (returns `is_valid: bool`, sets `errors` on failure) is unchanged. Callers do not need updates.
- Backward compatibility with the existing flat fixture shape is preserved: the new walker first tries the nested matcher-wrapper path, then falls back to the flat path. The existing test against the flat shape continues to pass.
- No production data structures change. The defect was in a read-only probe; nothing on disk needs migration.
- The deferred-path applier shares the same validator, so the fix benefits both the immediate-apply path and the SessionStart applier without requiring a separate code change in the applier itself.

**Rollback:** single-commit revert of the two files (`validation.py` + `test_mode_switch_bridge_substrate_validation.py`). Pre-fix behavior was that `gt mode set-bridge-substrate --substrate cross_harness_trigger` always returned the false-negative error; the workaround (`--defer-to-next-session`) remains available even with the revert, so rollback does not strand any active operation.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-mode-switch-validator-hook-matcher-shape-fix` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

**fix** — repair a defect in `validate_bridge_substrate()` such that a previously-failing user-facing CLI invocation (`gt mode set-bridge-substrate --substrate cross_harness_trigger`) succeeds against the real wire shape of `.claude/settings.json` and `.codex/hooks.json`. No new capability surface; no governance-surface change. Diff stat: ~25 lines in `validation.py` (two parallel walk blocks), ~30 lines in the test module (one new test plus a small helper). Justified as **fix** (not **feat** or **chore**) per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
