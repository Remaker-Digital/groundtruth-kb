ADVISORY
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: db8acfd1-59c4-4849-ae05-dd5a57691aa4
author_model: composer
author_model_version: composer
author_model_configuration: Cursor IDE interactive Loyal Opposition; transcript-resolved ::init gtkb lo
author_metadata_source: current session envelope

bridge_kind: governance_advisory
Document: gtkb-advisory-lo-verdict-build-activity-suffices
Version: 001
Author: Loyal Opposition (cursor, harness E)
Date: 2026-08-01 UTC
Mode: advisory proposal
Severity: medium
Priority: P2

# Advisory — LO bridge verdicts must accept ::open build

## Source

Owner-directed correction in Cursor LO session
`db8acfd1-59c4-4849-ae05-dd5a57691aa4` on 2026-08-01, after a peer LO session
claimed "NO-GO requires `::open test`" when filing a corrected verdict for
`gtkb-wi5694-terminal-evidence-packet-validator`.

Authoritative surfaces already contradict that claim:

- `config/agent-control/activity-envelope-sharding.toml` — `build` loads
  `codex-review-operating-contract.md` and `codex-loyal-opposition-runbook.md`;
  `test` adds checklists/templates only.
- `config/agent-control/activity-disposition-profiles.toml` —
  `[activities.build]` includes `verify` and terminology `GO` / `NO-GO` /
  `VERIFIED`.
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` — GO/NO-GO/VERIFIED
  with review skills on `::open build|test`; no test-only precondition.
- Hook sweep: no PreToolUse activity gate blocks LO verdict writes on build.

Concrete write-path failure that produced the false process claim:

- `scripts/gtkb_bridge_writer.py` `default_bridge_envelope_activity()` returns
  `"test"` for status in `{GO, NO-GO, VERIFIED}` or
  `LO_ENVELOPE_BRIDGE_KINDS`, then
  `normalize_bridge_envelope_head` raises
  `BridgeEnvelopeError: ... got 'build', expected 'test'`.
- Amplifier: `groundtruth_kb.session.handoff._activity_keyword_for_role` returns
  `::open test` for loyal-opposition.

Misleading doc surfaces (substantial review / verification flavor without a
positive "build suffices" rule): knowledge-base index, session-bootstrap, LO
runbook, and test disposition profile language about VERIFIED requiring
executed tests.

Linked MemBase capture already filed from this session:

- `WI-5903` — Align LO bridge-verdict envelope default: `::open build` suffices
  for GO/NO-GO/VERIFIED
- `TEST-11820` (PHASE-001) — assert LO GO/NO-GO/VERIFIED writes accept
  `::open build`
- Source specs: `SPEC-INTAKE-46594e`, `DCL-ACTIVITY-DISPOSITION-PROFILE-001`

## Claim

`::open build` is sufficient for all bridge-related Loyal Opposition work,
including filing `GO` / `NO-GO` / `VERIFIED`. `::open test` is optional heavier
context, not a verdict precondition. The writer default and a few doc surfaces
falsely couple LO bridge verdicts to `test`, contradicting authoritative
activity maps and owner intent.

## Owner Decision Needed

No additional owner decision is needed to file this ADVISORY or `WI-5903`.
The owner already directed the corrective Advisory work item on 2026-08-01.

Future implementation still requires normal disposition: Prime Builder advisory
intake, bounded proposal against exact targets
(`scripts/gtkb_bridge_writer.py`, handoff keyword, doc positive-rule lines),
Loyal Opposition GO, implementation-start, and verification of `TEST-11820`.

## Recommended Prime Action

1. Route this ADVISORY through governed advisory disposition; adopt `WI-5903`
   rather than duplicating work items.
2. File a bounded implementation proposal to:
   - change `default_bridge_envelope_activity` so LO bridge verdicts default to
     `build` (still accept explicit `::open test`);
   - align `_activity_keyword_for_role` for loyal-opposition with that rule;
   - state the positive rule in sharding/docs that build alone suffices for
     bridge LO verdicts; keep test as checklist/template load only.
3. Satisfy `TEST-11820`:
   `write_bridge_file` / `normalize_bridge_envelope_head` accept
   GO/NO-GO/VERIFIED with `::open build` without activity-mismatch errors.

## Classification Slot

Owner-directed governance advisory. Classification recommendation: `adopt`
into `WI-5903` / `TEST-11820` under `SPEC-INTAKE-46594e`. Not implementation
approval. No protected mutation, PAUTH, claim, Git, dispatcher, or TAFE change
is authorized by this ADVISORY.

## Prior Deliberations

_No prior deliberations: owner-directed corrective advisory from 2026-08-01 LO
session evidence; semantic search did not surface a governing DELIB that
requires test-activity for LO bridge verdicts._

## Specification Links

- `SPEC-INTAKE-46594e`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
