# Owner Decision Capture — Dispatcher Black-Box Hardening: Full Phasing (2026-07-17)

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb); captured via the LO-sanctioned CODEX-INSIGHT-DROPBOX path because the shared envelope projection resolved to loyal-opposition under a split-brain condition

Program: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
WIs: WI-5269, WI-5270, WI-5271
Prior decisions: DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE, -PHASED-HARDENING, -ACTIVITY-ENVELOPE-AUTHORITY, -ORDINARY-WORKER-DEFINITION, -DISPATCHER-WORKER-CONTEXT-PACKET, -SAFE-PACKET-CONTENT, -CAPABILITY-TOKEN-ENFORCEMENT, BRIDGE-FILES-PROTECTED-WORKER-SURFACE
Audit input: DELIB-202666770

## Owner decisions (2026-07-17)

### 1. Worker-boundary directive (standing)

Workers must not reference the bridge/TAFE/dispatcher configuration or internals
except when explicitly directed within an ops activity envelope. (Reasserts and
escalates the 2026-07-15 black-box program.)

### 2. Method selection: FULL PHASING (AUQ "Reconcile")

The owner selected **full phasing** — build the safe facade first, then gate —
over "non-destructive hardening now" and "emergency supersede." Sequence:

1. Land spec-foundation VERIFIED + `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`,
   `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`,
   `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` canonically (currently unbuilt).
2. Implement WI-5270 (worker-context packet) + WI-5271 (mediated bridge views).
3. Rewrite Layer-1 rules + canonical skills to consume the facade; re-project
   adapters (parity-gated).
4. Add audit + soft-deny.
5. Turn on the WI-5269 hard gate (deny worker internals-reference outside ops) per
   protected surface, only after safe-facade parity.

This honors the prior `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING`, which
required safe-facade-first and explicitly rejected immediate hard removal. Rationale
surfaced during reconciliation: the safe-facade WIs (5269/5270/5271) are all
open/backlogged and WI-5271 is blocked on the unbuilt DCLs/ADR, so removing raw
access now would break the review/verification/implementation workflows the phasing
decision protects.

### 3. Session tightening (2026-07-17, current interactive session)

The owner further directed that this session must **not alter or inspect the
dispatcher configuration** — an absolute boundary with no ops exception for the
active session. Recorded as the operative constraint under which the audit
(DELIB-202666770) and this capture were produced.

## Status note

The safe-facade prerequisites remain unbuilt; the program's next executable step is
the spec-foundation + the three formal artifacts named above. PB implementation of
those is currently blocked by an unrelated session-envelope split-brain (concurrent
interactive sessions on harness B), which is owner-managed.
