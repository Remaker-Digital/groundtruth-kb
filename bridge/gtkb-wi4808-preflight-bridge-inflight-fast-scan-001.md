NEW

# WI-4808 - Preflight Bridge In-Flight Fast Scan

bridge_kind: prime_proposal
Document: gtkb-wi4808-preflight-bridge-inflight-fast-scan
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:34:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI4808-BATCH-B-20260705
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4808

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/preflight.py", "groundtruth-kb/tests/test_preflight_checks.py", "platform_tests/scripts/test_dashboard_subject_selector.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4808 captures a performance defect in `groundtruth_kb.project.preflight._check_bridge_inflight`: it currently reads every versioned Markdown file under `bridge/` to discover the latest status for each bridge thread. With thousands of bridge files, dashboard/startup-adjacent tests that call the real upgrade preflight can exceed the global timeout on slower machines. The backlog row came from the WI-3433 Loyal Opposition NO-GO F2 observation and is now owner-authorized by the Batch B PAUTH.

This proposal authorizes a narrow source/test optimization: preserve the same externally visible warnings for latest non-terminal bridge threads while avoiding a full-content read of every bridge file. Candidate implementation directions include grouping versioned files by slug from filenames, considering only the highest numbered file per slug, and reading only those latest candidates; or replacing the ad hoc scan with an existing bridge-thread/status helper if it is faster and preserves the preflight contract. The implementation must not change upgrade apply behavior or suppress legitimate in-flight warnings.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4808 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4808 Batch B scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge-control and backlog specifications before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the performance and behavior requirements to concrete tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the touched `groundtruth-kb/project` preflight code must continue honoring the GT-KB root/application boundary and must not treat adopter application paths as directly integrated GT-KB artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4808 remains the MemBase backlog authority and must be resolved only with evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the performance concern is preserved as a bounded artifact-backed change rather than a silent timeout workaround.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, PAUTH, bridge proposal, tests, implementation report, and final backlog disposition must remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4808 moves from backlog candidate to bridge proposal, implementation report, verification, and terminal backlog resolution through explicit lifecycle states.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch B continuation and the active PAUTH covering WI-4808.
- WI-3433 Loyal Opposition NO-GO F2 - surfaced the real timeout risk in the dashboard writer path and recommended the follow-on performance optimization captured as WI-4808.
- `INTAKE-f8bc08a3` - dispatcher/bridge CLI as primary mutating UI for GT-KB artifact operations; relevant because the optimization must not bypass bridge authority.
- `INTAKE-e584f460` - all live agent mutations are bridge-first by default; relevant to preserving bridge-governed implementation flow.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI4808-BATCH-B-20260705`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The operative requirements are the WI-4808 backlog row, the cited PAUTH, and the existing preflight behavior contract documented in `groundtruth-kb/src/groundtruth_kb/project/preflight.py`: report one warning per bridge document whose latest version has a non-terminal status, remain silent for terminal/parked states, and keep all checks read-only.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Preserve `_check_bridge_inflight` behavior | Extend or update `groundtruth-kb/tests/test_preflight_checks.py` so the optimized scan still reports latest `NEW`, `REVISED`, `GO`, and `ADVISORY` threads and suppresses terminal or parked latest states. |
| Avoid O(n) full-content reads across all historical bridge files | Add a regression/performance-shape test that creates many obsolete versions and proves the implementation reads only latest-version candidates or otherwise avoids content reads for older versions. |
| Preserve dashboard writer contract | Update or retain `platform_tests/scripts/test_dashboard_subject_selector.py` evidence so the prior timeout workaround can be removed or justified after the optimized scan lands. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4808-preflight-bridge-inflight-fast-scan`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest groundtruth-kb/tests/test_preflight_checks.py -q --tb=short
python -m pytest platform_tests/scripts/test_dashboard_subject_selector.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4808-preflight-bridge-inflight-fast-scan --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4808-preflight-bridge-inflight-fast-scan
```

## Risk / Rollback

Risk is concentrated in false negatives: an overly aggressive fast path could miss an active bridge thread and let adopter upgrade checks look green while GT-KB work is in flight. Keep the implementation conservative, add tests for latest-version precedence and malformed/unreadable files, and roll back as one commit if warning behavior regresses.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4808-preflight-bridge-inflight-fast-scan`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - the expected implementation corrects a preflight performance defect while preserving existing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
