REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-w1-target-path-envelope-revision
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Implementation Proposal Revision - W1 Retirement-Machinery Authorization Envelope Correction

bridge_kind: prime_proposal
Document: gtkb-s358-w1-retirement-machinery-correction
Version: 018
Author: Prime Builder (Codex, harness A)
Date: 2026-05-19 UTC
Session: Codex desktop Prime Builder bridge continuation

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3365

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json", ".groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json"]

## Revision Claim

Version 018 supersedes the `-017` NO-GO by correcting the W1 target-path authorization envelope. The only remaining `-017` blocker was an audit-envelope mismatch: the implemented W1 source, tests, hooks, MemBase records, and approval-packet hashes already checked out, but the GO-derived target path glob `.groundtruth/formal-artifact-approvals/*-gov-project-verified-completion-retirement-001.json` did not authorize the actual GOV v3 approval-packet filename `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`.

This revision names both actual approval-packet paths exactly, keeps `groundtruth.db`, and carries forward the W1 implementation target paths from the earlier approved scope. No source, test, hook, config, approval-packet, or MemBase mutation is proposed here. After Loyal Opposition GO on this corrected revision, Prime Builder will regenerate the implementation-start packet, verify `path_authorized()` for `groundtruth.db`, the exact GOV v3 packet path, and the exact provenance-deliberation packet path, then re-file a post-implementation report. The already-persisted GOV v3 row and provenance deliberation must not be reinserted.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - the primary governing specification for the W1 behavior already implemented and verified by prior review evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the specification directly implicated by the `-017` authorization-envelope finding; every protected write surface must be within the GO-derived implementation envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - project-start owner approval and linked-spec discipline remain unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this correction is filed through the live bridge chain and awaits a fresh Loyal Opposition GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries a relevance-closed specification link set and corrected concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the re-filed report after GO will carry reviewer-reproducible authorization checks plus the previously executed W1 spec-derived tests.
- `GOV-ARTIFACT-APPROVAL-001` - the GOV v3 and provenance-deliberation formal artifacts are backed by owner-approved packets, and this revision ensures those packet paths are in the implementation envelope.
- `PB-ARTIFACT-APPROVAL-001` - protected artifact approval discipline applies to the GOV v3 and provenance deliberation already inserted.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - formal-artifact approval packet discipline governs the two artifact packet paths now named exactly.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the revision includes Project Authorization, Project, and Work Item headers.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every target path is inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this revision preserves the audit trail rather than rewriting prior artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - W1 traceability remains connected across the work item, bridge chain, implementation report, MemBase records, and approval packets.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the W1 lifecycle artifacts remain append-only; this revision corrects the authorization metadata path.
- `SPEC-AUQ-POLICY-ENGINE-001` - W1's removal of the project-completion owner-AUQ gate remains governed by the prior accepted implementation evidence and does not change here.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` authorizes the S358 combined governance-correction project and the W1 retirement-machinery correction scope.
- `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` is the earlier keep-open decision for PROJECT-GTKB-LO-OPPORTUNITY-RADAR; W1 superseded it under the S358 owner directive already cited in prior versions.
- `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` is the provenance deliberation created by W1 and already confirmed present by the `-017` review.

No prior deliberation changes the `-017` target-path finding. The correction is mechanical: the implementation envelope must name the deterministic filenames that actually exist.

## Owner Decisions / Input

- 2026-05-17, S357/S358: the owner directed and authorized the combined S358 governance-correction project, including W1, in `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`.
- 2026-05-18, S358: the owner approved `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 as drafted after full native-format presentation. The approval packet is `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`.
- 2026-05-18, S358: the owner approved `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` as drafted after full native-format presentation. The approval packet is `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`.
- The `-017` NO-GO explicitly states `Owner Action Required: None` for the recommended revised-proposal and re-GO path. This revision follows that path and does not request a waiver.

## Finding Response

### F1 - P1 - The actual GOV v3 approval packet is outside W1's GO-derived target paths

Response: Corrected. Version 018 replaces the prior lower-case, no-version GOV approval-packet glob with the exact deterministic filename `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`. It also names the existing provenance-deliberation packet exactly as `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json` and keeps `groundtruth.db` in scope. A fresh GO on this revision will allow `implementation_authorization.py begin` to mint a packet whose target path list mechanically covers all three reviewer-requested authorization checks.

## Scope Changes

The scope change is limited to proposal/report audit metadata:

- Replace `.groundtruth/formal-artifact-approvals/*-gov-project-verified-completion-retirement-001.json` with `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`.
- Replace `.groundtruth/formal-artifact-approvals/*-delib-s358-s350-manufactured-variant-provenance.json` with `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`.
- Preserve the already implemented W1 source/test/config/MemBase scope without rewriting or reinserting it.

The next post-GO report will include fresh `path_authorized()` output for:

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`
- `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`

## Requirement Sufficiency

Existing requirements are sufficient. The W1 behavior, project retirement, GOV v3 historical-record correction, and provenance deliberation were already covered by the earlier W1 bridge chain. Version 018 changes no behavioral requirement and performs no new protected artifact mutation. It corrects the bridge authorization envelope so the existing protected packet filenames are covered by a fresh GO-derived implementation-start packet.

## Pre-Filing Preflight Subsection

Before live filing, `revise_bridge.py file` runs the candidate-content preflights:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction --content-file <candidate>`

The revision is filed only if both preflights exit successfully.

## Verification Plan

After Loyal Opposition GO on version 018:

| Specification | Verification Evidence To Include In Re-Filed Report | Expected Result |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Regenerated packet hash plus `implementation_authorization.py validate --target groundtruth.db --target .groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json --target .groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json` | `authorized: true` for all three targets |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Carry forward the previously executed W1 pytest evidence from `-016` / `-017` and rerun if the environment permits without protected-mutation conflicts | W1 behavioral implementation remains passing |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Read the two exact approval-packet JSON files and compare their hashes to the existing MemBase records | Hashes match the already-persisted records |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` shows `GO` for version 019 before packet regeneration and `NEW` for the post-implementation report after filing | Bridge lifecycle remains append-only |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-filed report carries this mapping and the executed authorization/hash evidence | Verification evidence is reviewer-reproducible |

## Acceptance Criteria

- Loyal Opposition GO is issued on this corrected target-path revision.
- A fresh implementation-start packet is regenerated from that GO.
- `path_authorized()` or `implementation_authorization.py validate` returns true for `groundtruth.db`, the exact GOV v3 approval packet, and the exact provenance-deliberation approval packet.
- The re-filed post-implementation report does not reinsert the GOV v3 row or the provenance deliberation.
- The report carries forward the positive W1 confirmations from `-017` and adds the new exact-path authorization evidence.

## Risk And Rollback

Risk is low because this revision does not mutate source, tests, hooks, config, approval packets, or MemBase rows. The main risk is another path spelling mismatch; using exact paths rather than wildcard globs mitigates it. Rollback is bridge-only: if Loyal Opposition finds another defect, Prime Builder files the next REVISED bridge entry while preserving the append-only chain.

## Recommended Commit Type

`docs` for the revision itself because it changes only bridge proposal/report metadata. The W1 implementation change set remains `fix` as recorded in prior reports.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
