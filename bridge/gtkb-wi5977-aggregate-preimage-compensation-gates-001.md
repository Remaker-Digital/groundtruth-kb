ADVISORY
::init gtkb lo
::open deliberation
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-06T20-01-18Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-wi5977-aggregate-preimage-compensation-gates
Version: 001
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-07 UTC
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5977
Priority: P1 (root cause of the VERIFIED-finalization gridlock)

# Advisory Proposal — Narrow the whole-aggregate compensation gates in compensate_bridge_publication (WI-5977)

## Claim

`compensate_bridge_publication` gates on a whole-aggregate (15,532-file)
preimage digest that any concurrent bridge write invalidates, causing the
`BRIDGE_PUBLICATION_REPAIR_REQUIRED` stranding that has blocked several
VERIFIED finalizations (WI-5867, W0/WI-5839, and the queued post-implementation
reports). WI-5977 is the root cause; it should be prioritized and formalized
into a governed implementation proposal.

## Evidence (verified live 2026-08-07)

All four gates are whole-aggregate equality comparisons in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
(`compensate_bridge_publication`, defined at line 4115):

| Gate | Line | Failure |
|---|---|---|
| G1 | 4207 | `predicted != row.aggregate_preimage_digest` → `aggregate preimage cannot be restored exactly` (57 stuck rows) |
| G2 | 4221 | state=minted: `latest.content_digest != row.aggregate_preimage_digest` → `minted … no longer has its aggregate preimage` (5 rows) |
| G3 | 4234 | `latest.revision_id != row.revision_id` → `another bridge aggregate revision followed the publication` (2 rows) |
| G4 | 4254 | after `target.unlink()` inside `BEGIN IMMEDIATE`: `observed != row.aggregate_preimage_digest` → `bridge aggregate changed during compensation` (TOCTOU) |

G4 is a genuine TOCTOU: it runs inside the `BEGIN IMMEDIATE` opened at ~4249
but re-globs the filesystem via `artifact_content_state` at ~4252. No SQLite
transaction serializes filesystem writes by other OS processes, so a peer
harness writing any bridge file between 4249 and 4252 fails the check while the
DB lock is held. Locking/retry cannot fix this; only changing the invariant can.

## Safety Argument for the Fix

The ONLY filesystem mutation in the entire compensation path is `target.unlink()`
(~4251); compensation then writes only a DB revision. It cannot add, remove, or
alter any other aggregate entry. Therefore the whole-aggregate equality gates
defend against a failure mode the code is structurally incapable of producing,
while reliably blocking the normal multi-writer case. Narrowing all four gates to
the target slot loses no real protection.

## Recommended Fix

1. Narrow G1-G3 to the target slot: verify the target reached its intended state
   (absent after rollback; present-with-expected-digest after finalize).
2. Treat unrelated concurrent entries as benign (they are owned by their own
   publications).
3. Remove/replace the G4 filesystem TOCTOU re-glob inside `BEGIN IMMEDIATE`;
   verify the target slot only, inside the lock.
4. Retain the whole-aggregate digest as an audit observation, not a gate.
5. Add focused tests: multi-writer compensation under concurrent bridge writes;
   target-absent rollback; target-present-with-digest finalize; unrelated
   concurrent entry tolerated.

## Impact If Unaddressed

Every VERIFIED finalization that must compensate a capability remains at risk of
stranding under any concurrent bridge write. Current stranded/queued threads
(wi5509, w0-skill-rename-path-repair, and the WI-5825-class recovery backlog)
remain blocked or fragile.

## Recommended Action

Formalize WI-5977 into a governed `prime_proposal` (targeting
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` + focused
tests) for independent GO, then implement. This is the root cause of the
finalization gridlock and should be prioritized ahead of further VERIFIED
finalizations.

## Decision Needed From Owner

None required to file this advisory; owner prioritization is requested: confirm
WI-5977 be elevated for implementation ahead of the queued finalizations.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
