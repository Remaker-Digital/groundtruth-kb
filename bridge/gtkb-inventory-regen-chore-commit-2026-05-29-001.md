NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-s369-inventory-regen-chore-commit
author_model: claude-opus-4
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Inventory Regen Chore Commit 2026-05-29: durable toolchain-volatile fix for the dev-environment inventory drift gate

bridge_kind: implementation_proposal
Document: gtkb-inventory-regen-chore-commit-2026-05-29
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Implements: WI-3449 (Durable fix: classify toolchain.*.version volatile in inventory drift gate + regen)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3449
target_paths: ["scripts/check_dev_environment_inventory_drift.py", "config/governance/protected-artifact-inventory-drift.toml", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py", ".groundtruth/inventory/dev-environment-inventory.json", ".groundtruth/inventory/dev-environment-inventory.md"]
Recommended commit type: fix:

## Summary

The pre-commit drift gate is hard-blocking ALL commits across every parallel session. The blocking reason is `normalized_inventory_drift` on `diff_keys: [repo_configured_surfaces, toolchain]`, and because that block fires unconditionally on baseline-vs-live difference (checker lines 208-215) with no review-evidence escape, even pathspec-limited commits are frozen. The staged index has accumulated to 461 paths.

Investigation (interrogative-default, owner premise corrected) determined the failure is a Python-interpreter split, not simple time-drift. The drift checker regenerates the "current" inventory in-process under whichever interpreter runs it; `_toolchain_inventory()` reads pytest/ruff/pip versions via the running interpreter. The pre-commit hook invokes `${PYTHON:-python}` with `$PYTHON` unset, so it resolves bare `python` to the system interpreter at `C:\Python314` (pytest 9.0.2, ruff 0.15.5). The committed baseline (commit `bd0f8bfa`, 2026-05-28) was generated under the canonical venv `groundtruth-kb/.venv` (pytest 9.0.3, ruff 0.15.12). Empirically, under the venv interpreter the committed baseline drifts on `repo_configured_surfaces` only (toolchain matches); under system python it additionally shows phantom `toolchain` drift. The only genuine drift is `repo_configured_surfaces.skills` (32 -> 34).

This proposal implements the owner-approved durable fix (AskUserQuestion this turn -> DELIB-2504): make `toolchain.*.version` volatile in the drift registry so toolchain version differences never block any interpreter, AND regenerate the two inventory artifacts under the venv to clear the genuine skills drift. The inventory artifact continues to RECORD every toolchain version; the gate simply stops BLOCKING on version fields. This is the explicit follow-on documented in the 2026-05-28 VERIFIED report (`bridge/gtkb-inventory-regen-chore-commit-2026-05-28-004.md`), which required an owner-authorized one-time `--no-verify` bypass precisely because this fix had not yet landed. No `--no-verify` is used here.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - this change proceeds through the file bridge; bridge/INDEX.md remains workflow authority.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are under E:\GT-KB; no out-of-root paths touched; the bridge file resides under E:\GT-KB\bridge.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing specification surfaces and concrete target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each governing surface to an executed verification step, including a new unit test for the wildcard volatile-path behavior.
- GOV-STANDING-BACKLOG-001 - WI-3449 was captured via the gate-clean backlog-add CLI and is an active member of PROJECT-GTKB-RELIABILITY-FIXES (membership row created this turn via gt projects add-item). This is not a bulk backlog operation; see the Clause Scope Clarification subsection.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the drift registry and inventory artifacts are durable governed records under change control.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability is preserved between DELIB-2504, WI-3449, this bridge thread, the commit, and the changed files.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3449 moves from candidate to lifecycle-tracked implementation scope through this thread.
- GOV-RELIABILITY-FAST-LANE-001 - this is a small reliability fix (one focused code change, one registry data row, one new test, two regenerated artifacts; no new public CLI/API surface); it reuses PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING via PROJECT-GTKB-RELIABILITY-FIXES membership.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is required. The change operationalizes the existing drift-gate design (the registry already defines volatile_inventory_paths as the extension point for non-blocking inventory fields) and the documented 2026-05-28 follow-on. The registry TOML and the checker script are governed through the normal bridge GO/VERIFIED cycle (per config/governance/narrative-artifact-approval.toml excluded_by_design: gate-driving config and governance-meta-code are not approval-packet-gated); no formal-artifact-approval or narrative-artifact-approval packet is required.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation. It implements a single reliability defect fix tracked by one work item (WI-3449) and produces an inventory artifact (the regenerated dev-environment inventory) plus this review packet. No bulk work_item state transitions, no backlog cleanup sweep, and no silent bypass of the deliberation/approval surface occur. The owner decision is captured at DELIB-2504 and the review packet is this bridge thread; the GOV-STANDING-BACKLOG-001 bulk-operations clause is therefore not applicable.

## Prior Deliberations

- DELIB-2504 (S369, this turn) - owner AskUserQuestion decision selecting "Volatile toolchain + regen" (durable) over venv-only-regen and system-python-regen. Direct authorization for this proposal's scope.
- bridge/gtkb-inventory-regen-chore-commit-2026-05-28-004.md (VERIFIED) - the 2026-05-28 cycle. Its Non-Blocking Notes and Open Items explicitly flagged the toolchain-volatile registry update as the long-term fix so future regeneration does not require a --no-verify bypass. This proposal lands that follow-on.
- bridge/gtkb-inventory-regen-chore-commit-2026-05-28-003.md - the 2026-05-28 post-implementation report documenting that material toolchain drift forced an owner-authorized one-time --no-verify bypass; root-cause analysis at its Step 5 matches this proposal's diagnosis.
- DELIB-2212 - compressed 2026-05-27 inventory-regen thread (latest VERIFIED); the two-file regeneration precedent. The 2026-05-29 thread extends that pattern with the durable gate fix.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the inventory regeneration is a deterministic service; this proposal removes a recurring manual-bypass tax on that service.
- memory/feedback_inspect_staged_index_before_commit.md (S355) and memory/feedback_verify_staged_blobs_not_just_file_counts.md (S368) - the parallel-session staging-contamination hazard; mitigated here by explicit pathspecs and a mandatory git diff --cached check before commit.

## Owner Decisions / Input

This proposal depends on the following owner decision:

- AskUserQuestion in S369 this turn ("The drift gate isn't failing on simple time-drift ... A regen's result depends on which interpreter runs it ... How should I remediate so a normal commit lands cleanly (no --no-verify), via the bridge?"): Owner selected "Volatile toolchain + regen" (the durable option) over "Venv regen only" and "System-python regen". This authorizes (a) making toolchain.*.version volatile in the drift registry, (b) the supporting wildcard extension to the checker, and (c) regenerating the two inventory artifacts under the venv. Archived as DELIB-2504 via the governed gt deliberations record path.

No additional owner decisions are deferred or required for this proposal.

## Implementation Plan

1. Extend `_delete_dotted_path` in `scripts/check_dev_environment_inventory_drift.py` to support a single `*` wildcard path segment. When a path component is `*`, the deletion recurses into every key at that level with the remaining path; non-wildcard components retain their current exact-match behavior. This is the minimal mechanism that lets `toolchain.*.version` cover all current and future tools without enumerating each.
2. Add `"toolchain.*.version"` to `volatile_inventory_paths` in `config/governance/protected-artifact-inventory-drift.toml` (preserving the existing generated_at + redaction entries).
3. Add a focused unit test to `platform_tests/scripts/test_check_dev_environment_inventory_drift.py` asserting that `normalize_inventory(payload, ["toolchain.*.version"])` deletes the version key from every tool sub-dict while preserving non-version fields, and that two payloads differing only in toolchain versions normalize equal.
4. Regenerate the two inventory artifacts UNDER THE CANONICAL VENV so the recorded toolchain reflects the managed environment and skills refreshes 32 -> 34:
   - `groundtruth-kb\.venv\Scripts\python.exe scripts\collect_dev_environment_inventory.py`
5. Run the full drift-checker test module under the venv and confirm all existing tests still pass plus the new wildcard test:
   - `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q`
6. Confirm the live drift check now passes under BOTH interpreters (durable-fix proof):
   - `groundtruth-kb\.venv\Scripts\python.exe scripts/check_dev_environment_inventory_drift.py --staged --allow-review-evidence` -> Material inventory drift: False
   - `python scripts/check_dev_environment_inventory_drift.py --staged --allow-review-evidence` (system interpreter) -> Material inventory drift: False
7. Stage exactly the five target files using explicit pathspecs (`git add -u` for the gitignored-but-tracked inventory files; explicit pathspecs for the rest). Do NOT use `git add .`, `git add -A`, or unscoped `git add -u`.
8. Pre-commit verification: `git diff --cached --name-only` and `git diff --cached --stat` show exactly the five target files; reconcile against the pre-commit hook's reported changed-path set.
9. Commit with a `fix(inventory)` conventional-commits message body citing WI-3449, DELIB-2504, and this bridge thread, passed via `git commit -F <file>` to avoid PowerShell redirection hazards. NO `--no-verify`.
10. Confirm: `git log -1 --stat` shows exactly the five files; `git status --short` no longer shows them modified; a follow-up trivial commit (or `git commit --dry-run` on an unrelated staged file) confirms a normal small commit now lands.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Expected Result |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal filed at bridge/gtkb-inventory-regen-chore-commit-2026-05-29-001.md; INDEX entry created. | PASS - bridge protocol observed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Resolve-Path on all five target files returns paths under E:\GT-KB. | PASS - all in-root. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | python scripts/bridge_applicability_preflight.py --bridge-id gtkb-inventory-regen-chore-commit-2026-05-29 reports preflight_passed true. | PASS - missing_required_specs []. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | New wildcard unit test + full drift-checker module run under the venv; live drift check under both interpreters. | PASS - new test green, all existing tests green, drift False on both interpreters. |
| GOV-STANDING-BACKLOG-001 | groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES shows WI-3449 as active member. | PASS - membership recorded. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Bridge audit trail + commit log preserve traceability between DELIB-2504, WI-3449, this thread, and the committed files. | PASS - traceability preserved. |
| GOV-RELIABILITY-FAST-LANE-001 | git diff --cached --stat final change set: one small code change, one registry row, one test, two regenerated artifacts; no new public CLI/API. | PASS - fast-lane envelope satisfied. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `_delete_dotted_path` wildcard support added; all existing drift-checker tests still pass; the new wildcard test passes.
- [ ] `toolchain.*.version` added to volatile_inventory_paths in the registry.
- [ ] Inventory regenerated under the venv; skills reflect 34; toolchain reflects venv versions.
- [ ] Live drift check reports Material inventory drift: False under BOTH the venv interpreter AND the system interpreter.
- [ ] `git add` stages exactly the five target files and nothing else; pre-commit `git diff --cached --name-only` shows exactly five lines.
- [ ] The commit is created with `fix(inventory)` type, cites WI-3449 + DELIB-2504 + this thread, and lands WITHOUT --no-verify (pre-commit gate passes naturally).
- [ ] Post-commit `git status --short` shows none of the five files modified; `git log -1 --stat` shows the change set is exactly the five files.
- [ ] A normal small commit (unrelated trivial change or dry-run) confirms commits are unblocked under the default interpreter.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report.

## Risk and Rollback

Risk is low-to-moderate. The code change touches a governance gate's normalization path, so a bug could affect existing volatile-path handling.

Risks and mitigations:
- Wildcard refactor regresses existing volatile handling (generated_at, redaction.*): mitigated by re-running the full existing test module (8 tests) plus the new test before commit; the refactor preserves exact-match behavior for non-wildcard components.
- Hook crashes during its own commit using the new code: mitigated by running the live drift check (Step 6) under both interpreters before staging; the hook imports the working-tree checker, so Step 6 exercises the exact code path the commit hook will run.
- Staging contamination from 461 parallel-session paths: mitigated by explicit pathspecs + mandatory git diff --cached --name-only / --stat reconciliation (per S355/S368 feedback).
- Recording wrong toolchain because regen runs under the wrong interpreter: mitigated by Step 4 mandating the canonical venv interpreter explicitly.
- Over-broadening volatility (a `*` matching unintended keys): mitigated by scoping the registry entry to exactly `toolchain.*.version`; non-version toolchain fields (status, classification, presence) and all other inventory keys continue to gate.

Rollback: `git reset --soft HEAD~1` reverts the commit while preserving working-tree state; the five files unstage for correction. If the registry change proves undesirable, removing the `toolchain.*.version` line restores prior gating behavior.

## Files Touched (target_paths recap)

- scripts/check_dev_environment_inventory_drift.py (wildcard support in _delete_dotted_path)
- config/governance/protected-artifact-inventory-drift.toml (add toolchain.*.version to volatile_inventory_paths)
- platform_tests/scripts/test_check_dev_environment_inventory_drift.py (new wildcard volatile-path test)
- .groundtruth/inventory/dev-environment-inventory.json (regenerate under venv)
- .groundtruth/inventory/dev-environment-inventory.md (regenerate under venv)

Bridge filing artifacts (this proposal, INDEX entry, post-impl report) are workflow infrastructure, not implementation scope.

## Loyal Opposition Asks

1. Confirm the `*` wildcard extension to `_delete_dotted_path` is the right mechanism for durable coverage, or NO-GO toward an explicit per-tool volatile list (registry-only, no code change) if you judge the minimal-footprint data-only change preferable to modifying gate code. Both achieve the owner-approved outcome; the wildcard is chosen for durability against future tool additions.
2. Confirm that making `toolchain.*.version` non-blocking (while still recording versions in the artifact) is the correct gate-behavior change and does not weaken a control the owner relies on. Note that non-version toolchain changes and all other inventory keys continue to gate.
3. Confirm the `fix(inventory)` commit type is appropriate (repairs a gate that freezes legitimate commits) versus `chore:` (the -27/-28 pure-regen precedent) given this cycle also changes gate behavior + code.
4. Confirm the reliability fast-lane attachment (WI-3449 under PROJECT-GTKB-RELIABILITY-FIXES via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) is appropriate for this scope, or recommend a different home.
5. Confirm there is no in-flight parallel-session inventory-regen or drift-gate thread this proposal would race with (I checked bridge/INDEX.md for inventory-regen and drift keywords and found no actionable entries; the -27/-28 threads are terminal).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
