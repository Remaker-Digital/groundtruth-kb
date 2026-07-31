NO-ACTION
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Codex desktop session; role override `::init gtkb pb`; WI-5033 dispatcher/bridge auto-build goal

# Prime Advisory Disposition - WI-5036 Stale Lease Reaping

bridge_kind: operational_state_change
Document: gtkb-wi5036-stale-lease-reaping-advisory
Version: 002
Responds-To: bridge/gtkb-wi5036-stale-lease-reaping-advisory-001.md
Date: 2026-07-07 UTC
Disposition: NO-ACTION on this advisory thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-bearing advisory dispositions use the numbered bridge file chain.
- `GOV-STANDING-BACKLOG-001` - advisory work must be routed to existing backlog/work-item state or a governed follow-on artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory findings are preserved as durable artifacts without being treated as implementation approval.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source advisory, destination artifact, and disposition rationale remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - duplicate, adopted, retired, owner-gated, or deferred advisory states need explicit lifecycle disposition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - any future implementation proposal must carry concrete specification links rather than relying on this advisory disposition.

## Source Advisory

- bridge/gtkb-wi5036-stale-lease-reaping-advisory-001.md
- Work Item: WI-5036

## Disposition

The advisory describes plausible dispatcher hygiene work, but current MemBase state marks WI-5036 as `owner-gated/unapproved`: no related implementation bridge thread and no active project authorization were surfaced for this item. Prime Builder therefore must not create an implementation proposal or perform protected edits from the advisory alone.

## Evidence Checked

- `python -m groundtruth_kb.cli backlog show WI-5036 --json` reports `resolution_status: open`, `stage: backlogged`, and status detail: owner-gated/unapproved; requires owner authorization, deferral, retirement, or re-scope before proposal filing.
- The advisory remains preserved at `bridge/gtkb-wi5036-stale-lease-reaping-advisory-001.md` as source evidence.

## Rejected Alternatives

- Bridge proposal: rejected until owner authorization or project authorization exists.
- Implementation: rejected because an advisory is not implementation approval.
- No-op as duplicate: rejected; this remains a valid backlog candidate, just not implementation-authorized.

## Result

No further Prime Builder action is due on this advisory thread in this auto-build run. Resume from WI-5036 only after owner authorization, deferral, retirement, or re-scope is captured.
