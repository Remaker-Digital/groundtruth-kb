NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: GPT-5 Codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop; PowerShell; network enabled; approval policy never

# NEW: Emergency registry-first cleanup essentiality guardrails

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-97538B
Related Work Item: WI-AUTO-SPEC-INTAKE-99A602

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "scripts/hygiene/stray_detector.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "groundtruth.db"]
implementation_scope: emergency_guardrail
recommended_commit_type: fix

## Owner Decisions / Input

- Owner decision captured as `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY`: implement immediately that the GT-KB tracked artifact list is the canonical authority for cleanup essentiality, and that Git tracked/ignored/untracked state must not decide whether a file is essential.
- Owner emergency input in this session: `.env.local` was deleted during cleanup, an older backup was manually restored, recent backups are unreliable because of directory-size bloat, and this remediation must be done now rather than deferred.
- Bounded authorization created from that decision: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` permits config/source/test registry guardrails and registry projection sync only; it forbids credential lifecycle, deployment, force-push, destructive bulk cleanup, broad file deletion, and secret-value disclosure.

## Problem Statement

We failed to protect an essential local artifact during cleanup because the cleanup/inventory stack did not enforce the owner's intended authority model. The GT-KB tracked artifact list exists, but `.env.local` is not registered there, and at least one inventory-backed scan still filters registry-declared files through `git ls-files`. That makes Git tracking/ignore state an accidental essentiality gate.

The closed hygiene work did not solve this invariant. `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` verified a read-only, candidate-actions-only stray CLI and explicitly deferred destructive cleanup. `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-044.md` remains `REVISED` and owner-blocked on missing exact-content formal artifact approval for `GOV-WORK-TREE-HYGIENE-001`.

## Evidence

- `config/registry/sot-artifacts.toml` has no `.env.local`, environment, credential, or OpenRouter local artifact entry. A pattern scan for `env|credential|secret|OPENROUTER|local` only found unrelated text at line 119.
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py` builds `_git_tracked_paths()` with `git ls-files` at lines 71-80, filters `_expand_artifact_files()` through `_is_tracked()` at line 113, and wires this into `_artifact_inventory()` at lines 121-125.
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py` collects workspace entries from `git status --porcelain=v1 -z --untracked-files=all` at lines 108-110 and derives `tracked = status != "??"` at line 126. The current CLI report is read-only and candidate-action-only at lines 253-260.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` line 28 verifies the CLI as read-only and line 146 explicitly defers destructive cleanup.
- `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-044.md` lines 38-40 state the thread remains blocked; lines 91-102 show the approval packet and `GOV-WORK-TREE-HYGIENE-001` are absent; line 173 says future non-interactive redispatch cannot resolve it.
- `python -m groundtruth_kb.cli registry validate --json` currently reports `in_sync: false` with existing field divergences for `bridge-dispatch-state` and `harness-bridge-substrate`.

## Proposed Implementation

1. Register `.env.local` as an active owner-managed local artifact in `config/registry/sot-artifacts.toml`, with preservation semantics that make path presence/essentiality visible without ever serializing credential values.
2. Remove Git tracking as an inclusion filter from registry-backed inventory/string scans. The registry must decide which artifact paths are in scope; Git may remain diagnostic metadata, but it must not exclude registered artifacts.
3. Teach stray/cleanup classification to preserve registered artifacts before applying tracked/untracked/stale heuristics. Registered artifacts must not be emitted as deletion candidates solely because they are ignored, untracked, large, or old.
4. Add focused regression coverage proving a gitignored, registry-declared local artifact is included/preserved and that Git status is not used as essentiality authority.
5. Run the registry projection sync so `groundtruth.db` matches `config/registry/sot-artifacts.toml`, then verify `registry validate` and the focused tests.

## Explicit Non-Goals

- Do not print, copy, normalize, rotate, validate, or otherwise mutate credential values.
- Do not perform destructive cleanup or broad file deletion in this work item.
- Do not resolve the entire historical work-tree hygiene governance thread beyond this emergency guardrail.
- Do not treat Git ignored/untracked/tracked status as artifact essentiality authority.

## Specification Links

| Spec | Applicability | Verification |
| --- | --- | --- |
| `SPEC-INTAKE-97538b` | Blocking | Tests must prove the tracked artifact list is canonical for cleanup essentiality and Git state cannot exclude registered artifacts. |
| `SPEC-INTAKE-99a602` | Blocking | Tests and implementation must fail closed for destructive cleanup assumptions while no reliable backup exists. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Blocking | Proposal carries concrete project authorization, project, work item, target paths, and spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Blocking | Implementation report must map each blocking spec to executed verification evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Blocking | No protected implementation starts until this proposal receives `GO` and a matching work-intent claim. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Blocking | Implementation report must cite fresh registry, projection, and test reads. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Advisory | `.env.local` is owner-managed local credential/config state; this proposal preserves path authority without exposing values. |

## Specification-Derived Verification

- `python -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short`
- `python -m groundtruth_kb.cli registry list --json` and inspect that `.env.local` appears as an active registered artifact without secret value material.
- `python -m groundtruth_kb.cli registry validate --json` must report `in_sync: true` after projection sync, or the implementation report must explain any unrelated pre-existing divergence left open.
- Manual credential-safety check: no test output, report, or bridge artifact contains credential values from `.env.local`.

## Prior Deliberations

- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner emergency decision authorizing immediate registry-first cleanup essentiality remediation.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` - tracked artifact list is canonical for cleanup essentiality.
- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - no reliable GT-KB backup before destructive cleanup.
- `DELIB-20260809` - approved the five-slice WI-4356 work-tree hygiene plan.
- `DELIB-20260867` - owner AUQ approval for WI-4356 implementation authorization.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED read-only stray CLI; destructive cleanup deferred.
- `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-044.md` - latest blocker record for the unresolved cleanup governance spec.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-ARTIFACT-ESSENTIALITY-PROJECTION-20260701` - bounded emergency project authorization including registry projection sync.

## Risk And Rollback

Risk is low to moderate: the change narrows cleanup behavior and broadens inventory inclusion to registered artifacts. Rollback is to revert the source/config/test changes and rerun registry projection sync, but rollback would restore the known failure mode that allowed essential gitignored local state to be treated as disposable.
