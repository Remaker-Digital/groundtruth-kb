REVISED
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-05-30-prime-builder-post-S372
author_model: Claude
author_model_version: Opus 4.7 (1M context)
author_model_configuration: default reasoning, explanatory output style
author_metadata_source: session

# Implementation Proposal - Verified-Untested Spec Hygiene Cluster Slice 1 Inventory - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory
Version: 005 (REVISED)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-30 UTC
Responds-To: `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-004.md`
Source: WI-3178, WI-3179, WI-3180, WI-3181, WI-3182
Recommended commit type: feat
Project Authorization: PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001
Project: PROJECT-AGENT-RED-SPEC-HYGIENE
Work Item: WI-3178
Work Item: WI-3179
Work Item: WI-3180
Work Item: WI-3181
Work Item: WI-3182

KB-Mutation Declaration: NONE. This slice is strictly read-only against `groundtruth.db`. All five `## Explicitly Not Authorized` entries below (groundtruth.db mutation, Deliberation Archive insert/update, specification status change, test-row mutation, work-item mutation) are forbidden by both this proposal and the cited PAUTH's `forbidden_operations`. Acceptance Criterion 6 requires post-implementation pre/post `groundtruth.db` SHA-256 evidence proving zero database change. No groundtruth.db path is or should be added to target_paths.

target_paths: ["scripts/inventory_verified_untested_spec_hygiene_cluster.py", "platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md"]

## Revision Claim

REVISED-2 addresses two metadata-gate evolution gaps that landed after Codex GO at `-004` (2026-05-20):

1. **Missing project-linkage header metadata** (`Project Authorization:`, `Project:`, `Work Item:`) required by `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata. Added under the cited active PAUTH (created this session per DELIB-2511 owner approval).
2. **Missing `## Requirement Sufficiency` subsection** required by the same section + enforced by `scripts/implementation_authorization.py` `requirement_sufficiency_state()` check. Added below.

No scope change. The `-003` body's IP-1, IP-2, target_paths, verification plan, acceptance criteria, risk/rollback, and Explicitly-Not-Authorized envelope are preserved verbatim.

## Findings Addressed (Metadata-Gate Refresh)

Codex GO at `-004` reported "No blocking findings" — the scope and approach are accepted. This REVISED-2 refiles solely to satisfy the post-GO impl-start-authorization metadata gate evolution:

- Header lines `Project Authorization:`, `Project:`, `Work Item:` added near top of this file. Cited PAUTH is `PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001` (status `active`, `included_work_item_ids` contains all 5 WIs, `included_spec_ids` contains all 5 specs, no expiration; verified by direct query against `current_project_authorizations`).
- `## Requirement Sufficiency` subsection added below with operative state `Existing requirements sufficient`.

## Specification Links

- SPEC-1076 - alert acknowledge endpoint in superadmin_api (in-scope spec, read-only analysis target)
- SPEC-1078 - MFA status endpoint in superadmin_api (in-scope spec, read-only analysis target)
- SPEC-0661 - pricing usage-based overage charges (in-scope spec, read-only analysis target)
- SPEC-0811 - pipeline budget P50/timeout (in-scope spec, read-only analysis target)
- SPEC-1138 - widget views definition (in-scope spec, read-only analysis target)
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge lifecycle and live `bridge/INDEX.md` authority; this REVISED-2 follows the protocol-defined REVISED path after metadata gate evolution.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - proposal cites governing specifications + machine-readable `target_paths` + project-linkage metadata header block now satisfied.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification plan in this proposal is spec-derived and mapped 1:1 to focused pytest targets.
- GOV-STANDING-BACKLOG-001 - this slice implements 5 WIs (not a bulk backlog operation).
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - the cited PAUTH is the additive project-scoped owner-decision evidence; does not replace bridge GO or impl-start packet.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - PAUTH does NOT bypass bridge GO; a fresh Codex GO at `-006` and an impl-start packet are still required before protected mutations.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 - project-authorization envelope constraints (active status, work-item inclusion, spec inclusion, no expiration check) satisfied.
- GOV-ARTIFACT-APPROVAL-001 - slice is strictly read-only; no protected narrative artifact edits, no canonical-artifact mutations.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all active files remain under `E:\GT-KB`; output paths under `.gtkb-state/` (GT-KB infrastructure state).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - inventory manifest and summary are durable governed evidence artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - manifest + summary are governed artifacts produced by deterministic CLI.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - inventory creation is the explicit lifecycle event; manifest carries `generated_at` and provenance.

## Prior Deliberations

- `DELIB-0094` - prior `spec-hygiene-untested-verified` thread, VERIFIED at `bridge/spec-hygiene-untested-verified-008.md`.
- `DELIB-0750` - POR Step 16.C implemented-untested remediation context.
- `DELIB-0751` - methodology baseline for per-spec disposition.
- `DELIB-0871` - wider verified-state evidence rigor context.
- `DELIB-2511` - this session's owner-decision authorizing PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001 creation and session work-subject switch (2026-05-30 owner AUQ chain).
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-004.md` - Codex GO that approved `-003` scope; this REVISED-2 preserves that scope while satisfying the post-GO metadata gate.

## Owner Decisions / Input

Per AUQ-only enforcement (`SPEC-AUQ-POLICY-ENGINE-001`), the following AskUserQuestion-recorded owner decisions authorize this REVISED-2 and downstream work:

1. AUQ S-2026-05-30-AUQ-NEXT-ACTION (owner answer: "Pick oldest actionable AXIS-2 thread") — directive to claim oldest Prime-actionable.
2. AUQ S-2026-05-30-AUQ-COLLISION-RESPONSE (owner answer: "Pick a different oldest thread") — directive to skip parallel-WIP-collided slice-1 and find next-oldest.
3. AUQ S-2026-05-30-AUQ-PATTERN-RESPONSE (owner answer: "Switch to Application mode for hygiene-cluster") — directive to switch session work-subject and proceed with the hygiene-cluster work.
4. AUQ S-2026-05-30-AUQ-PAUTH-APPROVAL (owner answer: "Approve as drafted") — explicit approval of PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001 content as drafted (project ID, included WIs/specs, scope summary, allowed mutations, forbidden operations, no expiration).

All four AUQ records are captured in `DELIB-2511` (the deliberation backing the PAUTH). No new owner decision is required for Codex review of this REVISED-2 proposal.

## Requirement Sufficiency

Existing requirements sufficient.

The 5 in-scope SPECs (SPEC-1076, SPEC-1078, SPEC-0661, SPEC-0811, SPEC-1138) define the requirement surface. The inventory slice does not modify spec content, status, or testability; it only analyzes the current MemBase state and disk-side test coverage. The 5 WIs (WI-3178..WI-3182) and the prior thread `DELIB-0094` provide the operative scope (verified-but-untested spec hygiene). No requirement revision, owner clarification, or waiver is required before implementation after GO at `-006`.

## Proposed Scope

(Preserved verbatim from `-003`.)

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

(Preserved from `-003`; mirrored in PAUTH `forbidden_operations`.)

- `groundtruth.db` mutation.
- Deliberation Archive insert/update.
- Specification status change.
- Test-row mutation.
- Work-item mutation.
- Formal approval packet creation.
- Root `tests/scripts/` additions.

## Specification-Derived Verification Plan

(Preserved from `-003`.)

| Behavior / spec obligation | Verification |
|---|---|
| Resolver emits one record per in-scope spec | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Classification rules cover live-server, performance, behavioral-mismatch, fixable, and fallback cases | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Output is idempotent for fixed inputs | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| No mutation occurs in inventory mode | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` plus live pre/post DB SHA-256 evidence |
| Outputs stay under `.gtkb-state/verified-untested-spec-hygiene-cluster/` | `python -m pytest platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -q --tb=short` |
| Changed files lint and format cleanly | `python -m ruff check scripts/inventory_verified_untested_spec_hygiene_cluster.py platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

(Preserved from `-003`.)

1. Inventory script exists and runs read-only against live `groundtruth.db`.
2. Manifest contains exactly five records, one per in-scope spec.
3. Every record includes current spec state, current linked tests, open WI context, file/symbol presence, result history, classification, classification reason, and recommended Slice 2 action.
4. Summary lists per-spec recommended Slice 2 actions and classification counts.
5. Focused platform tests pass.
6. Pre/post `groundtruth.db` SHA-256 is identical.
7. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

(Preserved from `-003`.)

Risk: inventory output may be stale if MemBase changes between generation and Slice 2. Mitigation: generated metadata includes `generated_at`, database path, and script hash; Slice 2 must refresh or cite the specific manifest hash it uses.

Risk: classification may be conservative. Mitigation: Slice 2 remains the decision/mutation point and can override classifications with evidence.

Rollback: delete `scripts/inventory_verified_untested_spec_hygiene_cluster.py`, `platform_tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py`, and the generated `.gtkb-state/verified-untested-spec-hygiene-cluster/` files. No canonical database state is changed.

## Pre-Filing Preflight Subsection

After filing, Prime Builder will run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory
```

End of revision.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
