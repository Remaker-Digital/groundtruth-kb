NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T04-40-00Z-prime-builder-A-keep-working
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Hygiene PB

# WI-4675 Verified Scan-Bridge Token Parity Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4675-scan-bridge-token-parity-reconciliation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4675

target_paths: ["groundtruth.db"]
implementation_scope: membase_work_item_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4675 remains open in PROJECT-GTKB-MAY29-HYGIENE even though its implementation bridge thread `gtkb-scan-bridge-terminal-token-parity` is latest `VERIFIED` at `bridge/gtkb-scan-bridge-terminal-token-parity-006.md`.

This proposal requests a narrow MemBase reconciliation only: after Loyal Opposition review returns GO, update WI-4675 to `resolution_status=resolved` and `stage=resolved`, link `bridge/gtkb-scan-bridge-terminal-token-parity-006.md` as the related bridge evidence, and record status detail stating that the verified bridge-helper/template parity implementation closed the scan helper terminal-token parity defect.

No source, test, hook, config, dispatch, harness, bridge-runtime, or generated-template mutation is proposed by this reconciliation thread.

## Current Live State Snapshot

Current bridge state, from `gt bridge show gtkb-scan-bridge-terminal-token-parity --json`:

- latest status: `VERIFIED`
- latest path: `bridge/gtkb-scan-bridge-terminal-token-parity-006.md`
- version chain: `001 NEW`, `002 NO-GO`, `003 REVISED`, `004 GO`, `005 NEW`, `006 VERIFIED`

Current backlog state, from `gt backlog list --id WI-4675 --json`:

- `resolution_status: open`
- `stage: backlogged`
- `project_name: PROJECT-GTKB-MAY29-HYGIENE`
- `related_bridge_threads: ["bridge/gtkb-suppress-non-activatable-go-from-pb-scan-003.md","bridge/gtkb-suppress-non-activatable-go-from-pb-scan-004.md"]`
- title: `Keep scan helper terminal-kind tokens in parity with bridge notify`

Current project state, from `gt projects show PROJECT-GTKB-MAY29-HYGIENE --json`:

- `WI-4675` is an active member of `PROJECT-GTKB-MAY29-HYGIENE`.
- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` is active.

## Duplicate-Effort And Scope Check

This proposal does not duplicate the source implementation:

- `bridge/gtkb-scan-bridge-terminal-token-parity-006.md` already VERIFIED the implementation.
- Commit `aa725c471` records the missing `002` NO-GO and final `006` VERIFIED bridge files so the committed bridge chain now matches live state.
- The only remaining inconsistency found in live state is the stale-open MemBase row for WI-4675.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The reconciliation changes canonical project/backlog state and must route through the governed file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites the governing specifications for backlog reconciliation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Closure depends on the already-VERIFIED WI-4675 implementation report and LO verification evidence.
- `GOV-STANDING-BACKLOG-001` - Stale open work items should be reconciled when the corresponding bridge work is verified.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene authorization allows PB to propose implementation for unimplemented project work items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The stale open row is durable artifact drift and should be corrected as a governed artifact transition.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The work item, bridge proposal, implementation report, verification verdict, and backlog row should form a consistent artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - A work item with verified covering evidence should transition to a terminal/resolved state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The mutation target is in-root GT-KB MemBase state.

## Prior Deliberations

- `DELIB-20263079` - WI-4250 PAUTH creation NO-GO; relevant stale-artifact precedent requiring Prime to avoid duplicate work and file a live-state reconciliation proposal instead.
- `DELIB-20263083` - WI-4250 backlog reconciliation GO; relevant precedent for a one-row MemBase stale-status reconciliation through `groundtruth.db` with before/after readback.
- `DELIB-2763` - Deterministic Services stale status reconciliation NO-GO; requires re-querying candidate rows immediately before filing and excluding already-terminal rows from mutation sets.
- `bridge/gtkb-scan-bridge-terminal-token-parity-006.md` - LO VERIFIED the WI-4675 implementation and test evidence.
- `bridge/gtkb-scan-bridge-terminal-token-parity-005.md` - implementation report with the executed scan-helper/template parity tests and ruff checks.

## Owner Decisions / Input

No new owner decision is required for this reconciliation proposal. The active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` and owner decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorize Prime Builder to propose implementation for unimplemented May29 Hygiene work items. The actual MemBase mutation will not run until LO returns GO on this proposal.

If the backlog CLI requires `--owner-approved`, the implementation report will cite the same active project authorization and owner decision as the command-level evidence marker.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4675 describes the bridge-helper terminal-token parity defect, and `bridge/gtkb-scan-bridge-terminal-token-parity-006.md` verifies the implementation. This proposal only reconciles stale work-item lifecycle state to the verified bridge evidence. No new or revised requirement is needed.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not expose credentials; update only work-item status metadata. | Secret scan on this bridge file and commit hook. | |
| CQ-PATHS-001 | Yes | Limit the implementation target to `groundtruth.db`. | Implementation-start packet and post-update readback. | |
| CQ-COMPLEXITY-001 | N/A | No source code is changed. | Diff review. | MemBase reconciliation only. |
| CQ-CONSTANTS-001 | N/A | No runtime constants are changed. | Diff review. | MemBase reconciliation only. |
| CQ-SECURITY-001 | Yes | Do not bypass bridge approval; use governed backlog CLI after GO. | Implementation-start packet and command transcript. | |
| CQ-DOCS-001 | Yes | Preserve related bridge evidence and status detail in the work item. | `gt backlog list --id WI-4675 --json` after implementation. | |
| CQ-TESTS-001 | Yes | Reuse verified WI-4675 command evidence and run readback checks. | Backlog readback plus cited VERIFIED bridge thread. | No source behavior changes. |
| CQ-LOGGING-001 | N/A | No logging behavior changes. | Diff review. | MemBase reconciliation only. |
| CQ-VERIFICATION-001 | Yes | LO can verify before/after work-item state and the verified bridge chain. | Pre/post backlog readback and `gt bridge show`. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: inspect this proposal through `gt bridge show gtkb-wi4675-scan-bridge-token-parity-reconciliation --json`; expected latest status after filing is `NEW`, then after implementation report and LO review terminal `VERIFIED`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4675-scan-bridge-token-parity-reconciliation --json`; expected no missing required/advisory specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: inspect proposal header and `gt projects show PROJECT-GTKB-MAY29-HYGIENE --json`; expected active project membership and active PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: inspect `bridge/gtkb-scan-bridge-terminal-token-parity-006.md` and `bridge/gtkb-scan-bridge-terminal-token-parity-005.md`; expected VERIFIED evidence for scan-helper/template parity and focused tests.
- `GOV-STANDING-BACKLOG-001` and artifact lifecycle requirements: run `gt backlog list --id WI-4675 --json` before and after implementation. Expected after implementation: `resolution_status=resolved`, `stage=resolved`, and related bridge/status detail pointing to `bridge/gtkb-scan-bridge-terminal-token-parity-006.md`.

Proposed implementation command after GO:

```text
gt backlog update WI-4675 --resolution-status resolved --stage resolved --related-bridge-threads "[\"bridge/gtkb-scan-bridge-terminal-token-parity-006.md\"]" --status-detail "Resolved as VERIFIED by bridge/gtkb-scan-bridge-terminal-token-parity-006.md; scan_bridge.py, the managed template helper, and platform_tests/scripts/test_scan_bridge.py now keep manual scan terminal-kind tokens in parity with groundtruth_kb.bridge.notify." --owner-approved --change-reason "May29 Hygiene reconciliation: close WI-4675 as verified by scan-bridge terminal-token parity bridge thread." --json
```

## Risk / Rollback

Risk is low. The verified implementation thread already closed the underlying defect; this bridge changes only the stale work-item lifecycle row. The main risk is losing the older related-bridge provenance from the WI creation row, so the implementation should record the final verified WI-4675 thread as related evidence and preserve the prior source context in status detail if useful.

Rollback is a follow-up governed backlog update that returns WI-4675 to an open state and explains why the verified bridge evidence was insufficient. No source or runtime rollback is needed because this proposal does not change source or runtime files.

## Bridge Filing

This proposal is filed as the first status-bearing bridge file for `gtkb-wi4675-scan-bridge-token-parity-reconciliation`. No prior bridge version is deleted or rewritten.

## Recommended Commit Type

`chore:` - the eventual implementation reconciles backlog state only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
