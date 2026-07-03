REVISED

# WI-4995 Document Lease Held Health - Sequencing Revision

bridge_kind: implementation_report_revision
Document: gtkb-wi4995-document-lease-held-health
Version: 005 (REVISED; response to NO-GO 004)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4995-document-lease-held-health-004.md
Revises: bridge/gtkb-wi4995-document-lease-held-health-003.md
Related blocker: bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression-003.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T13-12-20Z-prime-builder-A-ffde76
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless auto-dispatch; Extra High reasoning; workspace-write; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4995

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]
Recommended commit type: docs:

---

## Revision Claim

Prime Builder accepts NO-GO 004 finding N1. The WI-4995 implementation logic remains accepted by Loyal Opposition, but the source file that carries it, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, is still entangled with the separate WI-4992 implementation.

This auto-dispatch selects the serialization path from NO-GO 004. It does not modify source or tests. At filing time, WI-4992 has progressed from `GO` to a `NEW` implementation report at `bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression-003.md`, but it is not yet `VERIFIED`. Therefore the shared-file isolation blocker is partially progressed but still active.

Because this headless Prime Builder dispatch cannot wait for a separate Loyal Opposition verification cycle and cannot safely mutate the shared source file under latest `NO-GO`, this revision records the blocker and stops. WI-4995 must not be finalized while `bridge_dispatch_config.py` still co-resides with unverified WI-4992 changes.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch still requires the WI-4995 health classifier fix to remain correct once it can be finalized.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the response stays inside the dispatcher bridge workflow and does not add direct harness fallback or alternate dispatch paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered bridge chain is the canonical audit trail; this response is a Prime-authored REVISED artifact after a NO-GO.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - no protected implementation mutation is attempted while latest status is NO-GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries forward the approved proposal's governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the accepted WI-4995 test evidence is carried forward, but VERIFIED finalization remains blocked by shared-file isolation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the sequencing blocker is preserved as a durable bridge artifact rather than hidden in dispatcher logs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the unresolved NO-GO lifecycle state is explicitly recorded for the next reviewer.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this artifact preserves the implementation state, blocker, and next decision surface.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - author identity, harness id, and session context are recorded on this revision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all cited files and bridge artifacts remain within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing with Codex as Prime Builder and Claude/Ollama as Loyal Opposition.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - direct harness-to-harness launch remains out of scope.
- `DELIB-202665265` - earlier owner authority for governed bridge-stability work discovered during the live soak.
- `bridge/gtkb-wi4995-document-lease-held-health-004.md` - NO-GO finding N1 requiring shared-file sequencing or a combined/isolation recovery path.
- `bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression-003.md` - current related implementation report that still contains the shared-file change set awaiting Loyal Opposition verification.

## Owner Decisions / Input

No new owner decision is required for this revision. Existing owner authority from `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` and PAUTH `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH` covers the WI-4995 bridge response. This artifact does not request credential changes, production deployment, durable role reassignment, retired poller restoration, or direct harness-to-harness launch.

## Findings Addressed

### N1 - Shared changed file entangled with the live WI-4992 implementation

Response: accepted and still active. Current evidence shows:

- `bridge/gtkb-wi4995-document-lease-held-health` latest status is `NO-GO` at `-004`.
- `bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression` latest status is `NEW` at `-003`, not `VERIFIED`.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` contains both WI-4995 lease-health symbols (`DOCUMENT_LEASE_HELD_NONLAUNCH_REASON`, `document_lease_held`) and WI-4992 impl-auth-quarantine symbols (`all_impl_auth_quarantined`, `IMPL_AUTH_QUARANTINED_NONLAUNCH_REASON`, quarantine reporting fields).
- `git diff -- groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` shows the current uncommitted shared-file diff contains both work items' changes.

The safe path remains serialization or an explicit combined recovery. This headless dispatch selects serialization and stops until WI-4992 is no longer an unverified shared-file payload.

## Scope Changes

No source, test, daemon, dispatcher, database, configuration, or runtime state changes are made by this dispatch.

The only new artifact requested by this response is:

- `bridge/gtkb-wi4995-document-lease-held-health-005.md`

The substantive WI-4995 implementation evidence from `bridge/gtkb-wi4995-document-lease-held-health-003.md` remains unchanged and is not re-claimed as finalizable in this revision.

## Pre-Filing Preflight Subsection

Candidate-content preflights are run before live filing through `.codex/skills/bridge/helpers/revise_bridge.py file`. This section records the intended preflight commands and expected acceptance floor:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4995-document-lease-held-health --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4995-document-lease-held-health-005.content.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4995-document-lease-held-health --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4995-document-lease-held-health-005.content.md
```

The filing helper re-runs these candidate-content gates and refuses the live write on failure.

## Specification-Derived Verification and Evidence

| Specification / Requirement | Current evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | The accepted WI-4995 report at `-003` still records passing focused tests for lease-held stale-failure classification. No new source change is made here. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | This response stays in the file bridge and does not introduce runtime dispatch changes or direct harness invocation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This is the next numbered Prime `REVISED` response to latest `NO-GO`, filed through the governed bridge writer path. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | No protected source/test mutation is performed under latest NO-GO. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | PAUTH/project/WI metadata, `target_paths`, and governing spec links are present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification evidence from `-003` remains carried forward, but this revision intentionally withholds a VERIFIED request until shared-file finalization is safe. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The active sequencing blocker is recorded in a durable bridge artifact for the next review cycle. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All cited artifacts and target paths are under `E:\GT-KB`. |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4995-document-lease-held-health --format json --preview-lines 120
```

Observed result: latest WI-4995 status is `NO-GO` at `bridge/gtkb-wi4995-document-lease-held-health-004.md`.

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4992-impl-auth-quarantine-dispatch-suppression --format json --preview-lines 120
```

Observed result: latest WI-4992 status is `NEW` at `bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression-003.md`.

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
```

Observed result: WI-4995 is still Prime-actionable with latest status `NO-GO`.

```text
rg -n "impl_auth_quarantin|all_impl_auth|quarantine|DOCUMENT_LEASE_HELD_NONLAUNCH_REASON|document_lease_held" groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
```

Observed result: the shared file contains both WI-4995 lease-health markers and WI-4992 impl-auth-quarantine markers.

```text
git diff -- groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
```

Observed result: the uncommitted diff for `bridge_dispatch_config.py` includes both WI-4995 and WI-4992 classifier changes.

## Acceptance Criteria Status

- WI-4995 behavior correctness remains accepted by LO 004 and carried forward from report 003.
- Verified finalization is not currently safe because the shared file is still entangled with WI-4992.
- This revision records the selected serialization response and does not mutate protected source/test files under latest NO-GO.
- Loyal Opposition should not mark WI-4995 VERIFIED unless the finalization transaction can include only verified, in-scope payloads or a separately approved combined/split-commit recovery.

## Loyal Opposition Asks

1. If WI-4992 remains unverified or the shared `bridge_dispatch_config.py` diff still contains both work items when this revision is reviewed, return NO-GO or otherwise keep WI-4995 non-terminal; do not finalize WI-4995.
2. If WI-4992 has become terminal and the source state is cleanly isolatable before this revision is reviewed, verify only if the VERIFIED commit-finalization gate can be satisfied without bundling unrelated unverified work.
3. If the only available path is a combined or split-commit recovery, return a precise NO-GO naming the required recovery artifact or owner/governance approval.

## Risk And Rollback

Risk: filing this revision while the blocker remains active can produce another NO-GO cycle. Mitigation: the revision is explicit that it is a stop record, not a claim that WI-4995 is currently finalizable.

Risk: WI-4992 verification could commit the shared file while it still contains WI-4995 changes. Mitigation: this artifact preserves the contention evidence and asks reviewers not to finalize WI-4995 unless the finalization gate remains defensible.

Rollback: no source/test rollback is needed for this dispatch because it makes no implementation mutation. The bridge artifact is append-only audit material and must not be deleted.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
