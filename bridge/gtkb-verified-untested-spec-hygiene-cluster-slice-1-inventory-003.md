REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Verified-Untested Spec Hygiene Cluster Slice 1 Inventory - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-002.md`

Source: WI-3178, WI-3179, WI-3180, WI-3181, WI-3182
Recommended commit type: feat
target_paths: ["scripts/inventory_verified_untested_spec_hygiene_cluster.py", "platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md"]

## Revision Claim

This revision makes Slice 1 strictly read-only against MemBase. It removes the optional `--apply` mode, removes the optional Deliberation Archive write, removes all DA-row acceptance/verification text, and preserves the database hash invariant.

The deliverable is only a deterministic inventory script, focused platform tests, and generated `.gtkb-state` inventory outputs.

## Specification Links

- SPEC-1076
- SPEC-1078
- SPEC-0661
- SPEC-0811
- SPEC-1138
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-APPROVAL-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- `DELIB-0094` - prior `spec-hygiene-untested-verified` thread, VERIFIED at `bridge/spec-hygiene-untested-verified-008.md`.
- `DELIB-0750` - POR Step 16.C implemented-untested remediation context.
- `DELIB-0751` - methodology baseline for per-spec disposition.
- `DELIB-0871` - wider verified-state evidence rigor context.

## Owner Decisions / Input

No new owner decision is required. This slice is inventory-only and performs no spec, test, work-item, Deliberation Archive, or formal-artifact mutation.

## Findings Addressed

### F1 - P1 - Optional DA write contradicts the no-MemBase-mutation scope and target paths

Response: Removed `--apply`, removed optional DA row creation, removed optional DA deliverable, and removed optional DA verification. The script must not mutate `groundtruth.db`. The post-implementation report must include pre/post `groundtruth.db` SHA-256 evidence showing no database change.

### F2 - P3 - Recommended commit type does not match the proposed diff shape

Response: Changed recommended commit type to `feat`, because this slice adds a reusable inventory script plus tests.

## Proposed Scope

### IP-1: Read-only inventory script

Add `scripts/inventory_verified_untested_spec_hygiene_cluster.py`.

Required behavior:

1. Read the five in-scope specs from MemBase: `SPEC-1076`, `SPEC-1078`, `SPEC-0661`, `SPEC-0811`, and `SPEC-1138`.
2. Read current linked tests and open WIs for each spec.
3. Probe test files on disk with static parsing only; do not execute live or performance tests.
4. Classify each spec into a closed inventory bucket:
   - `fixable_test_present`
   - `live_server_required_test`
   - `performance_oracle_required_test`
   - `behavioral_mismatch`
   - `unresolvable_in_scope`
5. Write `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json`.
6. Write `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md`.
7. Never write to `groundtruth.db`.

### IP-2: Focused platform tests

Add `platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py`.

Tests must use a temporary database/fixture and temporary output directory. They must not touch live `groundtruth.db`.

## Explicitly Not Authorized

- `groundtruth.db` mutation.
- Deliberation Archive insert/update.
- Specification status change.
- Test-row mutation.
- Work-item mutation.
- Formal approval packet creation.
- Root `tests/scripts/` additions.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Resolver emits one record per in-scope spec | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Classification rules cover live-server, performance, behavioral-mismatch, fixable, and fallback cases | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Output is idempotent for fixed inputs | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| No mutation occurs in inventory mode | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` plus live pre/post DB SHA-256 evidence |
| Outputs stay under `.gtkb-state/verified-untested-spec-hygiene-cluster/` | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Changed files lint and format cleanly | `python -m ruff check scripts/inventory_verified_untested_spec_hygiene_cluster.py platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. Inventory script exists and runs read-only against live `groundtruth.db`.
2. Manifest contains exactly five records, one per in-scope spec.
3. Every record includes current spec state, current linked tests, open WI context, file/symbol presence, result history, classification, classification reason, and recommended Slice 2 action.
4. Summary lists per-spec recommended Slice 2 actions and classification counts.
5. Focused platform tests pass.
6. Pre/post `groundtruth.db` SHA-256 is identical.
7. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

Risk: inventory output may be stale if MemBase changes between generation and Slice 2. Mitigation: generated metadata includes `generated_at`, database path, and script hash; Slice 2 must refresh or cite the specific manifest hash it uses.

Risk: classification may be conservative. Mitigation: Slice 2 remains the decision/mutation point and can override classifications with evidence.

Rollback: delete `scripts/inventory_verified_untested_spec_hygiene_cluster.py`, `platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py`, and the generated `.gtkb-state/verified-untested-spec-hygiene-cluster/` files. No canonical database state is changed.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory --content-file .gtkb-state\bridge-revisions\drafts\gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory --content-file .gtkb-state\bridge-revisions\drafts\gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-003.md`

End of revision.
