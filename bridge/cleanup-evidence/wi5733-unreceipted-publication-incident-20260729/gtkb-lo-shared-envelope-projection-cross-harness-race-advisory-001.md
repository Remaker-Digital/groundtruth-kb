ADVISORY
::init gtkb lo
::open build
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: ed636a98-0d21-47be-a41a-f494da6e996c
author_model: Composer
author_model_version: composer
author_model_configuration: Cursor interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: loyal_opposition_advisory
Document: gtkb-lo-shared-envelope-projection-cross-harness-race-advisory
Version: 001
Date: 2026-07-29 UTC
Author: Loyal Opposition (Cursor E)

# Loyal Opposition Advisory — Shared session envelope projection is cross-harness racy

## Classification

**Severity P1.** Concurrent harnesses stomp `.claude/session/envelope.json`, so
CLI attribution (`resolve_changed_by` / worker-role provenance) can read another
harness's session and fail closed or, worse, attribute work incorrectly after a
manual restore.

This advisory is **not** implementation approval.

## Source

Observed in Cursor LO session `ed636a98-0d21-47be-a41a-f494da6e996c` while
auto-processing the LO bridge queue and attempting `gt backlog add-work-item`
to capture CLI defects (owner direction: file WIs for defective procedures
instead of continuing workarounds).

## Claim

`python -m groundtruth_kb session envelope open --harness-name cursor ...`
returned Cursor session `ed636a98-...`, and
`harness-state/cursor/session-envelopes/ed636a98-....json` remained correct, but
the shared projection `.claude/session/envelope.json` was overwritten by a
concurrent Claude session to harness B / `prime-builder` /
`B-2026-07-29T22-06-54Z`. Subsequent `gt backlog add-work-item` failed with:

`resolve_changed_by: Worker role provenance session id does not match the current session.`

Manual restore of the Cursor envelope into the shared projection unblocked WI
creation. That restore is a defective workaround, not a durable fix.

## Evidence

- Cursor open stdout: `ed636a98-0d21-47be-a41a-f494da6e996c`
- Immediate projection read showed Claude PB envelope (`harness_id=B`,
  `role_resolved=prime-builder`, `init_keyword=::init gtkb pb`)
- Authoritative Cursor envelope file remained present under
  `harness-state/cursor/session-envelopes/`
- After copying the Cursor envelope back to `.claude/session/envelope.json`,
  `gt backlog add-work-item` succeeded

## Related backlog (created this session)

| WI | Title |
| --- | --- |
| `WI-5747` / `TEST-11752` | Isolate shared `.claude/session/envelope.json` projection across concurrent harnesses |
| `WI-5744` / `TEST-11749` | Add `gt bridge file-verdict` governed CLI for GO/NO-GO/ADVISORY publication |
| `WI-5745` / `TEST-11750` | Fix `write_verdict.py` Windows cp1252 stdout UnicodeEncodeError |
| `WI-5746` / `TEST-11751` | Retire stale `.cursor/skills/bridge` scan_bridge path from LO startup docs |

Related prior advisory (file-verdict gap, not the envelope race):
`bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md`.

## Recommended next artifact path

1. Prime Builder disposition of `WI-5747` as the primary fix (harness-scoped
   provenance resolution; stop using a single shared projection as cross-harness
   authority).
2. Keep `WI-5744`–`WI-5746` as companion tooling repairs so LO auto-process no
   longer depends on raw Write, Unicode-fragile stdout seeding, or missing
   helper paths.
3. Do not activate the deliberately disabled TAFE dispatcher as part of this
   repair.

## Owner Action Required

None blocking. Owner may prioritize `WI-5747` (P1) if concurrent multi-harness
sessions remain the normal operating mode.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
