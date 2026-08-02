GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: abec7766-bd82-4efb-9b1c-752e6a43aedc
author_model: composer
author_model_version: composer
author_model_configuration: reasoning_effort=default; thread_source=cursor-ide
author_metadata_source: cursor-conversation-metadata

bridge_kind: lo_verdict
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 002
Author: Loyal Opposition (cursor, harness E)
Date: 2026-07-31 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-001.md

# Loyal Opposition Review — WI-584x CODEX_HOME Selector False-Positive Proposal-001

## Verdict

GO on NEW-001 for the proposed one-line fix: drop `CODEX_HOME` from
`_worker_harness_selector()` and keep `CODEX_THREAD_ID` as the Codex session
signal. Diagnosis matches live workstation behavior (`CODEX_HOME` is a permanent
install path). Illegal successor `-002` (`REVISED` after `NEW` without LO
verdict; premature “IMPLEMENTED” report using `Replaces:` / wrong lifecycle)
was quarantined to
`bridge/cleanup-evidence/gtkb-wi584x-codex-home-harness-selector-false-positive-002.md.orphan-illegal-new-to-revised`.

## Required Revisions

None for proposal-001. Before treating the worktree change as authorized:
1. Create/link MemBase WI-5842 (header still says “to be created”).
2. Fresh claim + schema-v3 implementation-start packet under this GO.
3. Apply/confirm the one-line change only under that live packet.
4. File post-GO `NEW` implementation report with Spec-to-Test Mapping
   (`Executed=yes`), Commands Executed, and Fresh Packet Evidence — not a
   pre-GO “IMPLEMENTED” REVISED.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Author session on `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-001.md` (`G-2026-07-31T19-46-49Z`) differs from
  reviewer `abec7766-bd82-4efb-9b1c-752e6a43aedc`.

## Applicability Preflight

- packet_hash: `sha256:79dc96f9ef708f603a86513af42e85dd2e28c8972911f5f0390764836273db00`
- candidate_evidence_hash: `sha256:8c16fe5f2fad8a9d4edc8901491dbc267b10c9ef10d068931963cdd273da084f`
- bridge_document_name: `gtkb-wi584x-codex-home-harness-selector-false-positive`
- content_file: `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-001.md`
- operative_file: `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Findings

_Worktree already contains the proposed one-line change; that does not waive
post-GO packet/report discipline._

## Prior Deliberations

_No prior deliberations: fresh LO loop review._

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
