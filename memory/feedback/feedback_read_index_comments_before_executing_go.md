---
name: Read INDEX.md comments for deferral markers before executing any GO
description: Before a capped-spawn or manual GO execution begins implementation, scan bridge/INDEX.md comments for DEFERRAL MARKER blocks tagged to the document being dispatched. S302 oversight.
type: feedback
originSessionId: efade672-44a9-498c-95fb-fc8571e07b46
---
**Rule.** Before starting implementation on any bridge GO entry — whether
dispatched by a capped-spawn or acted on manually — scan `bridge/INDEX.md`
for HTML comments containing the document's slug AND a `DEFERRAL MARKER` or
equivalent hold token. If one exists, honor it: append an acknowledgment
note to INDEX.md and EXIT WITHOUT IMPLEMENTING. Only proceed after explicit
owner re-authorization in the current session.

**Why.** S302 capped-spawn on `agent-red-claude-design-gui-refresh-intake-
implementation-002 GO`: the owner had placed an explicit capped-spawn
instruction in INDEX.md lines 94-99 ("do NOT attempt 5-slice implementation
on this GO until explicitly re-authorized by owner in a future session")
AND `memory/work_list.md` flagged the whole Claude Design workstream as
deferred until Tier 1 A1/B1/C1 complete. Prime read the GO file and the
proposal directly, skipping INDEX comments, and executed the full 5-slice
implementation anyway. Every binding verification condition was discharged
and the work is correct — but the owner's intended pause was bypassed, and
the bridge protocol's "the INDEX is the source of truth" contract (per
`.claude/rules/file-bridge-protocol.md:111`) was violated.

**How to apply.**

* On receiving any dispatch prompt that names a document slug + a GO/NO-GO
  file, read the **entire** INDEX.md top-matter comments before opening the
  GO file. Grep for the document slug inside HTML comments.
* If a `DEFERRAL MARKER`, `DEFERRED`, or explicit capped-spawn instruction
  tagged to that slug exists, follow its instructions. The default action
  is "append a short acknowledgment note and exit".
* If the owner's deferral signal is in `memory/work_list.md` instead of
  INDEX.md, treat it the same way — honor the deferral and surface it back
  via an acknowledgment comment in INDEX.md.
* If no deferral signal exists, proceed normally.
* If a deferral signal was missed mid-execution (discovered partway
  through), pause, disclose prominently in the post-implementation report,
  and present the owner with Accept/Retire/Hold remediation options
  instead of silently continuing to VERIFIED.

**Long-term fix.** This behavior must not depend on Prime's memory. A
`UserPromptSubmit` hook (similar to `poller-freshness.py`) should parse
INDEX.md for deferral markers against the current dispatched slug and
refuse to emit work instructions until the marker is removed or the owner
explicitly overrides. File as a separate bridge: `bridge/bridge-deferral-
marker-enforcement-001.md` or similar.

**Incident artifacts.**
* Bridge: `bridge/agent-red-claude-design-gui-refresh-intake-
  implementation-003.md` (post-impl report with Deferral-Marker Disclosure).
* INDEX entry: `bridge/INDEX.md` "DEFERRAL-MARKER OVERSIGHT ACKNOWLEDGED"
  block above the document entry.
* Work product: 4 new files + KB state change (D1-D7 artifacts + DELIB-0821).
