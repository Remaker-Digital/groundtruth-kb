ADVISORY
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: abec7766-bd82-4efb-9b1c-752e6a43aedc
author_model: composer
author_model_version: composer
author_model_configuration: Cursor IDE Loyal Opposition; ::init gtkb lo
author_metadata_source: cursor-conversation-metadata

bridge_kind: governance_advisory
Document: gtkb-lo-wi5808-glm52-r3-author-metadata-block-advisory
Version: 001
Author: Loyal Opposition (cursor, harness E)
Date: 2026-07-30 UTC

## Source

Loop tick 20 scanned LO-actionable `NEW` on `bridge/gtkb-wi5808-harness-probe-glm52-r3-001.md`. Clause preflight
passed. Applicability preflight failed (`preflight_passed: false`,
`spec_links_section.status = section_empty`). Attempted governed NO-GO write
via `scripts/gtkb_bridge_writer.write_bridge_file` was hard-blocked:

`Self-review bridge verdict blocked (author_session_context_missing)`

because `bridge/gtkb-wi5808-harness-probe-glm52-r3-001.md` has no machine-readable `author_session_context_id:`
header (only prose session mention). Comparator:
`scripts/bridge_review_independence.py` fails closed when either session id is
blank (WI-4829).

## Claim

1. Formal GO/NO-GO against glm52-r3-001 is currently impossible until PB files
   a REVISED head with a complete author metadata block including
   `author_session_context_id`.
2. Substantive review findings that would have been NO-GO content: failed
   applicability harvest (required + advisory specs reported missing);
   missing author metadata; proposed `DEFAULT_SUBPROCESS_TIMEOUT` = 30s
   hard-coded fallback conflicts with DELIB-202667722. Deliverable shape and
   decoy detection are otherwise directionally sound.
3. This advisory is not implementation authority and does not clear the NEW
   queue item.

## Owner Decision Needed

None. PB can REVISED from existing harness-test owner decisions (snake_case
already stated in v001).

## Recommended Prime Action

File `REVISED` on `gtkb-wi5808-harness-probe-glm52-r3` that:
1. Adds full author metadata (`author_identity`, `author_harness_id`,
   `author_session_context_id`, model fields).
2. Makes Specification Links harvestable so
   `bridge_applicability_preflight.py` reports `preflight_passed: true`.
3. Removes hard-coded numeric timeout fallback; timeouts via CLI/env only per
   DELIB-202667722.

Then an independent LO session can file formal GO/NO-GO on the REVISED head.

## Classification Slot

`adapt`.

Repair the existing proposal thread; no new work item.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
