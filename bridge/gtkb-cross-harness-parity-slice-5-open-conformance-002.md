GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-cross-harness-parity-slice-5-open-conformance
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-cross-harness-parity-slice-5-open-conformance-001.md
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4891
Recommended commit type: feat

## Separation Check

Proposal `-001` author session `0eb73a79-4ad6-40c0-88e9-16f797f0ef2e` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Slice 5 is the planned first conformance case: wire Claude
`::open`/`::close` topic-envelope routing via a new UserPromptSubmit adapter
calling the shared `groundtruth_kb.session.topic_router`, register both harness
surfaces under one capability id, and clear the Slice-3 discovery-diff finding
for `session_wrapup_trigger_dispatch`. Design correctly omits Codex wrap-trigger
branch on Claude (Stop-hook wrap already exists) and includes required
Cross-Harness Disposition for harness-surface targets.

## Evidence

- Preflights: applicability pass; clause gate 0 blocking gaps.
- Shared module + Codex adapter pattern confirmed
  (`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` uses `parse_topic_command`
  / `handle_topic_command`).
- Registry unification approach matches Slice-2 schema; discovery-diff integration
  test is the right acceptance gate for advisory §6 criterion 1.

## Residual Risks (non-blocking)

1. Verify startup-input gate reads the correct Claude lifecycle guard path and
   does not race SessionStart init-keyword relay.
2. Discovery-diff key naming: confirm post-registration finding clears for both
   `hook:session_wrapup_trigger_dispatch` and `hook.session-topic-envelope-routing`
   as claimed (stem/capability-id mapping).
3. Re-run Slice 2/3 parity regression suite; new hook must be git-tracked per
   `_check_registered_hooks_tracked` expectations.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §4 first conformance case.
- bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md (VERIFIED).
- bridge/gtkb-cross-harness-parity-slice-4-disposition-gate-004.md (VERIFIED).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
