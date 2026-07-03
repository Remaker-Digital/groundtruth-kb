NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T16-51-05Z-prime-builder-A-979413
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; reasoning_effort=xhigh

# GT-KB Bridge Implementation Report - gtkb-artifact-essentiality-emergency-guardrails-reproposal - 003

bridge_kind: implementation_report
Document: gtkb-artifact-essentiality-emergency-guardrails-reproposal
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-002.md
Approved proposal: bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-001.md
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-97538B
Related Work Item: WI-AUTO-SPEC-INTAKE-99A602

## Implementation Claim

Implemented the approved emergency registry-first cleanup essentiality guardrails.

- Registered `.env.local` as the active owner-managed local runtime artifact `owner-local-env` in `config/registry/sot-artifacts.toml`, with path-only authority and notes explicitly stating that GT-KB does not serialize or manage credential values.
- Removed Git tracking as an inventory/string-scan inclusion filter. Registry-declared concrete paths, globs, and directories now decide inventory scope; Git tracked/ignored/untracked state no longer excludes a registered artifact from inventory expansion.
- Added registry-aware stray classification. Dirty workspace paths matching active registry records are classified as `registered_artifact` with candidate action `preserve_registered_artifact` before stale tracked/untracked heuristics apply.
- Added a collector path for exact owner-managed `gitignored_runtime` artifacts, so an ignored `.env.local` can be surfaced as preserved even when `git status --untracked-files=all` hides it.
- Avoided content hashing for registry-preserved workspace entries so `.env.local` can be preserved without reading or hashing credential values in the stray scanner.
- Added focused unit and CLI regressions for gitignored registered artifacts in inventory/string-scan and strays surfaces.
- Synced the SoT artifact registry projection into `groundtruth.db`. The sync inserted `owner-local-env` and also updated two pre-existing TOML/projection divergences in the same registry file (`bridge-dispatch-state`, `harness-bridge-substrate`) because registry sync projects the current TOML as a whole.

This implementation did not print, copy, normalize, rotate, validate, mutate, or disclose `.env.local` credential values.

## Specification Links

- `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality; Git state cannot exclude registered artifacts.
- `SPEC-INTAKE-99a602` - cleanup must fail closed while no reliable GT-KB backup exists.
- `GOV-ENV-LOCAL-AUTHORITY-001` - `.env.local` is owner-managed local credential/config state; this proposal preserves path authority without exposing values.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation report must cite fresh registry, projection, and test reads.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - no protected implementation starts until this replacement receives GO and a matching work-intent claim.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner emergency input that crosses into a requirement/plan is preserved as governed bridge state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact correction is routed through bridge/spec/test evidence rather than scratch memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - cleanup-risk findings trigger durable artifact lifecycle handling.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal carries concrete project authorization, project, work item, target paths, and spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting proposal includes PAUTH/project/WI metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report maps each blocking spec to executed verification evidence.

## Owner Decisions / Input

No new owner decision was required by this implementation report.

Carried-forward owner/governance evidence:

- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner emergency decision authorizing immediate registry-first cleanup essentiality remediation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` - active bounded implementation authorization for config/source/test guardrails and registry projection sync.

## Prior Deliberations

- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner emergency authorization.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality.
- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - no reliable GT-KB backup before destructive cleanup.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-001.md` - original proposal.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-002.md` - original GO verdict, later superseded because it lacked mandatory Requirement Sufficiency metadata.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-001.md` - replacement proposal.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-002.md` - Loyal Opposition GO verdict authorizing this implementation.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED read-only stray CLI.
- `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-044.md` - unresolved broader cleanup governance thread remains separate.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-INTAKE-97538b` | `test_scan_inventory_strings_includes_gitignored_registered_artifact`, `test_inventory_refresh_counts_gitignored_registered_artifact`, `test_registered_artifact_is_preserved_before_untracked_stale_heuristic`, and `test_hygiene_strays_preserves_gitignored_registered_local_artifact` prove registered artifacts are included/preserved even when Git would exclude or hide them. |
| `SPEC-INTAKE-99a602` | Strays tests continue to assert candidate-only dry-run behavior and no destructive cleanup runs. Registered artifacts return `preserve_registered_artifact`, not owner-review deletion/cleanup candidates. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | `registry show owner-local-env --json` shows `.env.local` path authority, owner-only role, and `gitignored_runtime` backup policy without credential values. Stray collector sets `content_hash=None` for registry-preserved entries. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Fresh registry commands were run after implementation: `registry sync`, `registry validate --json`, `registry list --json`, and `admin inventory refresh --json`. Post-sync registry parity is `in_sync: true`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation began only after live latest `GO`, implementation authorization, and work-intent claim. Authorization packet hash: `sha256:b273131b21717cd00df40ae90f5c4f35e544a54c529390095756ed99f62e207d`; work-intent rowid: `29691`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Owner emergency artifact-essentiality input is preserved in the replacement bridge chain and in the SoT registry row/projection. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The remediation is represented as durable source/config/test/database changes plus this bridge report rather than scratch memory. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Cleanup-risk artifact lifecycle handling is encoded by `owner-local-env` and by strays `registered_artifact` preservation classification. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's specification links and maps them to command evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report preserves PAUTH/project/work-item metadata from the approved proposal and GO. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This section maps each linked spec/governing surface to executed tests or fresh command evidence. |

## Commands Run

Initial role/tooling checks:

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
```

Observed result: failed because `groundtruth-kb/.venv/Scripts/gt.exe` is not present in this venv. Direct reads of `harness-state/harness-identities.json` / `harness-state/harness-registry.json` confirmed Codex harness ID `A` and durable role `prime-builder`. Subsequent package-importing commands used `groundtruth-kb/.venv/Scripts/python.exe`, not ambient `python` or bare `gt`.

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-artifact-essentiality-emergency-guardrails-reproposal --format json
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-artifact-essentiality-emergency-guardrails-reproposal
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-artifact-essentiality-emergency-guardrails-reproposal
```

Observed result: selected thread live latest status was `GO`; implementation authorization succeeded; work-intent claim acquired for session `2026-07-03T16-51-05Z-prime-builder-A-979413`.

Code quality:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/hygiene/strays.py scripts/hygiene/stray_detector.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/hygiene/strays.py scripts/hygiene/stray_detector.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py
```

Observed result: `All checks passed!`; `7 files already formatted`.

Focused tests:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short --basetemp .pytest-basetemp-artifact-essentiality-inventory -o cache_dir=.pytest-cache-artifact-essentiality-inventory
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short --basetemp .pytest-basetemp-artifact-essentiality-strays -o cache_dir=.pytest-cache-artifact-essentiality-strays
```

Observed result: inventory/string-scan suite `10 passed, 1 warning`; strays suite `35 passed, 1 warning`. The warning in both runs is the existing pytest config warning for unknown `asyncio_mode`.

The same pytest targets initially failed before test setup because the host default temp root `C:\Users\micha\AppData\Local\Temp\pytest-of-micha` was not readable by the session. Rerunning with root-local ignored basetemp/cache directories produced the passing results above.

Registry projection:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry validate --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry show owner-local-env --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry sync --json --changed-by prime-builder/codex --change-reason "gtkb-artifact-essentiality-emergency-guardrails-reproposal registry projection sync"
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry validate --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry list --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli admin inventory refresh --json
```

Observed result:

- Pre-sync validation: `in_sync: false`, `toml_count: 25`, `projection_count: 24`, `missing_in_projection: ["owner-local-env"]`, plus pre-existing field divergences for `bridge-dispatch-state` and `harness-bridge-substrate`.
- `registry show owner-local-env --json`: `storage_path: ".env.local"`, `backup_policy: "gitignored_runtime"`, `owner_role: "owner_only"`; no credential values.
- Sync: inserted `owner-local-env`; updated `bridge-dispatch-state` and `harness-bridge-substrate`; all other rows unchanged.
- Post-sync validation: `in_sync: true`, `toml_count: 25`, `projection_count: 25`, no missing rows or field divergences.
- Inventory refresh: `artifact_count: 25`, `scanned_file_count: 9946`, `mutated: false`; one archive missing artifact remains `bridge-index` / `bridge/INDEX.md`.

Diff hygiene:

```text
git diff --check -- config/registry/sot-artifacts.toml groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/hygiene/strays.py scripts/hygiene/stray_detector.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py
```

Observed result: clean exit; no whitespace errors.

## Observed Results

- Live bridge status for `gtkb-artifact-essentiality-emergency-guardrails-reproposal` remained latest `GO` before implementation.
- Implementation authorization and work-intent claim were acquired before protected source/config/test/database edits.
- `.env.local` exists, is gitignored by `.gitignore:18`, and is not tracked by `git ls-files .env.local`.
- Inventory/string-scan no longer calls `git ls-files` or filters expanded registry files through tracked-path membership.
- Stray detection preserves registry-matched workspace entries before stale tracked/untracked classification and reports `workspace_registered_artifact`.
- The package-side stray collector loads active SoT registry records, annotates dirty paths with registry matches, synthesizes exact owner-managed gitignored runtime artifacts hidden by Git status, and avoids content hashing for registry-preserved entries.
- Registry projection is in sync after `registry sync`.
- No command output, report text, or bridge artifact contains `.env.local` credential values.

## Files Changed

Implementation files for this GO:

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `scripts/hygiene/stray_detector.py`
- `groundtruth-kb/tests/test_inventory_string_scan.py`
- `platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py`
- `platform_tests/scripts/test_hygiene_strays_cli.py`
- `platform_tests/scripts/test_work_tree_stray_detector.py`
- `groundtruth.db`

Scope note: the worktree contains many unrelated dirty and untracked files from other active work. This implementation report claims only the files listed above for this GO. Within `config/registry/sot-artifacts.toml`, some bridge-dispatch/substrate edits were pre-existing when this session began; the new row added by this implementation is `owner-local-env`, and the authorized projection sync updated `groundtruth.db` for the full current registry TOML.

## Recommended Commit Type

- Recommended commit type: `fix`
- Diff-stat justification: behavioral guardrail fix with source/config/test/database changes.

## Acceptance Criteria Status

- [x] The replacement proposal received a fresh independent GO at `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-002.md`.
- [x] Implementation started only from the replacement GO plus implementation authorization and a matching work-intent claim.
- [x] `.env.local` path authority is represented in the registry and projection without disclosing or mutating credential values.
- [x] Inventory/string-scan includes gitignored registry-declared local artifacts instead of filtering them through Git tracked state.
- [x] Stray/cleanup classification preserves registered artifacts before stale tracked/untracked heuristics.
- [x] Focused registry, inventory, and stray-classification tests pass.
- [x] Registry projection sync completed and post-sync validation reports parity.

## Risk And Rollback

Residual risk: removing the Git tracked-file filter increases inventory refresh/string-scan scope for registry-declared directories and globs. The observed live refresh scanned 9946 files. That is intentional under the approved requirement that registry authority, not Git state, controls artifact essentiality, but future performance tuning may need path-specific exclusions or more precise registry rows if scans become too broad.

Rollback path: revert the listed source/config/test changes, run `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry sync --json --changed-by prime-builder/codex --change-reason "<rollback reason>"` to restore the registry projection, and rerun the focused pytest and registry validation commands. Do not delete or mutate `.env.local` credential values as part of rollback.

## Loyal Opposition Asks

1. Verify only the implementation files listed above for this GO; ignore unrelated dirty worktree files unless they create direct verification risk.
2. Confirm the registry-first invariant: a registered `.env.local` is included/preserved despite being gitignored and untracked.
3. Confirm the implementation report carries sufficient spec-to-test mapping for `SPEC-INTAKE-97538b`, `SPEC-INTAKE-99a602`, `GOV-ENV-LOCAL-AUTHORITY-001`, and the bridge/governance DCLs.
