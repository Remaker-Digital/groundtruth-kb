NEW

# WI-4884 Daemon Resilience ADR/DCL Formalization

bridge_kind: prime_proposal
Document: gtkb-wi4884-daemon-resilience-formalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-28 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4884

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-28-ADR-DISPATCHER-ARCHITECTURE-001-resilience-addendum-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001-content.md", ".groundtruth/formal-artifact-approvals/2026-06-28-ADR-DISPATCHER-ARCHITECTURE-001-resilience-addendum.json", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001.json", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001.json", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001.json", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001.json", ".groundtruth/formal-artifact-approvals/2026-06-28-DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001.json", "groundtruth.db", "platform_tests/groundtruth_kb/cli/test_spec_record.py", "platform_tests/groundtruth_kb/cli/test_spec_update.py", "platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Process WI-4884, Phase 0 of the dispatcher-daemon resilience program, by formalizing the owner scope-lock in MemBase governance artifacts before the later resilience implementation phases proceed. The work updates `ADR-DISPATCHER-ARCHITECTURE-001` with a resilience addendum and creates five DCLs covering the daemon single-instance invariant, the GTKB-DispatcherDaemon supervision contract, per-mode recovery SLAs, alert-and-degrade escalation, and harness/dispatch isolation.

This proposal is intentionally governance-only. It does not flip topology, start or stop daemons, edit dispatcher source, change dispatcher rules configuration, or implement load/chaos tests. Later topology and reliability-test items in the same project depend on these formal constraints but remain out of scope here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` governs the append-only bridge handoff: Prime Builder files `NEW`; Loyal Opposition decides `GO` or `NO-GO`; implementation starts only after GO and a matching work-intent claim.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires this implementation proposal to cite the governing specs rather than treating the backlog item as free-form work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` requires the Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata present above.
- `GOV-ARTIFACT-APPROVAL-001` requires owner-presented formal artifact approval before ADR/DCL rows are treated as canonical project truth.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires verification evidence derived from the linked specs and from the new artifact constraints before a VERIFIED verdict can close the item.
- `GOV-STANDING-BACKLOG-001` makes MemBase `work_items` the durable authority for selecting WI-4884 from PROJECT-GTKB-DISPATCHER-RELIABILITY.
- `ADR-DISPATCHER-ARCHITECTURE-001` is the architecture-of-record being amended in place with the resilience addendum.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` is the current dispatcher service requirement that the resilience addendum and DCL family must preserve.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` justify preserving the owner scope-lock as durable formal artifacts rather than leaving it only as backlog prose.

## Proposed Formal Artifact Set

The implementation will prepare native-format content and formal approval packets for:

- ADR-DISPATCHER-ARCHITECTURE-001 resilience addendum (update existing architecture decision)
- DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001
- DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001
- DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001
- DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001
- DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001

The five DCL IDs above are proposed new records, not existing authority at proposal time. They are derived from WI-4884 and DELIB-20266276, with the isolation DCL also grounded in DELIB-20265888.

## Prior Deliberations

- `DELIB-20266276` - owner scope-lock for the Daemon Resilience and Full-Harness Activation program. This is the direct WI-4884 source: D0-D6 define topology, load target, full auto-recovery, scheduled task supervision, alert-and-degrade escalation, mock load/chaos tests, and PB routing.
- `DELIB-20265888` - owner harness/dispatch isolation invariant. This is the source for the proposed isolation DCL and for preserving harnesses as dispatch consumers rather than dispatch control-plane actors.
- `DELIB-20266272` - PHASE-Y full daemon go-live decision. This provides the motivating operational context for strengthening daemon resilience before wider topology activation.
- `DELIB-20266084` - dispatcher daemon foundation authorization. This established the persistent daemon foundation and independent heartbeat direction that WI-4884 formalization extends.
- `ADR-DISPATCHER-ARCHITECTURE-001` - current dispatcher architecture row, recorded from the 2026-06-25 storm lesson and owner target-architecture decisions.

## Owner Decisions / Input

Existing owner decisions are sufficient to file this proposal and to prepare the draft formal artifact content: WI-4884 cites DELIB-20266276 as the source scope-lock, and the project authorization includes WI-4884.

Actual canonical ADR/DCL recording remains gated by `GOV-ARTIFACT-APPROVAL-001`. The implementation must generate owner-presented formal approval packets and must not run non-dry-run `gt spec update` or `gt spec record` for these artifacts until the approval evidence exists.

## Requirement Sufficiency

Existing requirements are sufficient for this Phase 0 lane. The owner already selected the six resilience decisions in DELIB-20266276, and ADR-DISPATCHER-ARCHITECTURE-001 plus SPEC-CENTRALIZED-DISPATCH-SERVICE-001 establish the architectural surface being amended.

No new requirement clarification is requested before Loyal Opposition review. If review finds the proposed DCL vocabulary too broad or too narrow, the proper response is NO-GO with a concrete scope correction against the five proposed DCLs above.

## Implementation Plan

1. Draft the ADR resilience addendum and the five DCL native-format content files under `.groundtruth/formal-artifact-approvals/`.
2. Run `gt spec update --dry-run --json` for the ADR addendum and `gt spec record --dry-run --json` for each DCL to validate required metadata, owner-presented fields, types, tags, constraints, and source paths.
3. Generate formal approval packets with `gt generate-approval-packet --kind formal` for the six artifacts.
4. After formal approval evidence exists, run the non-dry-run `gt spec update` / `gt spec record` commands against `groundtruth.db`.
5. Verify the recorded rows with `gt spec show`, targeted governance tests, and bridge preflights before filing the implementation report.

## Spec-Derived Verification Plan

Proposal preflight before filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4884-daemon-resilience-formalization-001.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4884-daemon-resilience-formalization-001.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4884-daemon-resilience-formalization-001.md
```

Implementation verification after GO:

```text
gt spec show ADR-DISPATCHER-ARCHITECTURE-001 --json
gt spec show DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001 --json
gt spec show DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001 --json
gt spec show DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001 --json
gt spec show DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001 --json
gt spec show DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001 --json
python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/groundtruth_kb/cli/test_spec_update.py platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py -q --tb=short
```

Expected results: bridge preflights pass; dry-run spec commands accept all six formal artifacts before mutation; after formal approval and recording, `gt spec show` returns the ADR update and five DCL rows; targeted governance tests pass.

## Risk / Rollback

Primary risk is silently over-formalizing operational behavior before implementation phases prove the details. This proposal limits that risk by keeping the DCLs at invariant/contract/SLA level and leaving topology activation, source changes, and chaos tests to later WIs.

Rollback is single-lane: if GO is rejected, no protected mutation occurs. If implementation proceeds and a formal packet or spec row is wrong, retire or supersede the affected MemBase row through the governed `gt spec update` path with a new approval packet; do not edit `groundtruth.db` directly.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4884-daemon-resilience-formalization`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

docs - formal governance artifact content and approval packets, with MemBase ADR/DCL rows as the canonical backing store after approval.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
