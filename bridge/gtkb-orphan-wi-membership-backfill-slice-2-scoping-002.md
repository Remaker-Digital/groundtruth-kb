GO

bridge_kind: implementation_review
Document: gtkb-orphan-wi-membership-backfill-slice-2-scoping
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md
Recommended commit type: feat

# Loyal Opposition Review - Orphan-WI Membership Backfill Slice 2 Scoping

## Verdict

GO. The scoping-only proposal is sound and faithful to the Slice 1 deferred
contract: consume the verified orphan-WI discovery report, refresh discovery
before mutation, resolve each orphan through owner AUQ or approval-packet
evidence, and perform actual state changes only through deterministic GT-KB
services. No source, test, or MemBase mutation is authorized by this scoping GO;
the follow-on implementation proposal must carry concrete `target_paths`,
implementation-start authorization, `groundtruth.db` mutation scope where
applicable, and executable spec-derived tests.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:868dd35ff55f5fb4d0539deeaab015dc8632cdf1b9beab3e222059bdb71c1884`
- bridge_document_name: `gtkb-orphan-wi-membership-backfill-slice-2-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md`
- operative_file: `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-orphan-wi-membership-backfill-slice-2-scoping`
- Operative file: `bridge\gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Evidence Checked

- Live `bridge/INDEX.md` listed the latest thread status as `NEW` for
  `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md` before
  this verdict.
- Full version chain read: the thread currently has a single proposal version,
  `-001`.
- Predecessor thread `gtkb-orphan-wi-membership-discovery-slice-1` is terminal
  `VERIFIED` at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md`.
- `gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json` shows active project
  membership for `WI-3450` under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` shows
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` active. This is sufficient for
  the present scoping review because the proposal mutates no state.
- `gt backlog show WI-3450 --json` shows `WI-3450` open/backlogged, with
  related bridge/spec evidence linking it to Slice 1 and the orphan-WI
  membership remediation scope.
- The verified discovery scanner was re-run in stdout-only mode:
  `scripts/discover_orphan_wi_memberships.py --run-id codex-scope-check-2026-05-29T1752Z --json`
  reported `orphan_count 27`, `total_open 239`, and all 27 currently classified
  as `unrecoverable`. This supports the proposal's "re-run discovery first"
  requirement and confirms the live problem class still exists.

## Findings

None blocking.

## Implementation Constraints For The Follow-On

- The follow-on implementation proposal must not rely on this scoping GO as
  direct permission to mutate MemBase. It must declare `groundtruth.db` and any
  state/report paths in `target_paths` when membership rows, retire/exclude
  records, or approval-packet-backed state changes are in scope.
- If the implementation performs membership backfill or retire/exclude changes,
  the authorization surface must explicitly cover that mutation class. The
  standing reliability PAUTH's `source`, `test_addition`, and `hook_upgrade`
  classes are not, by themselves, a data-migration envelope.
- Owner decisions for unrecoverable or low-confidence orphans must remain
  AUQ-gated, with approval-packet evidence for retire/exclude decisions as the
  proposal describes.
- The implementation proposal must provide the promised spec-derived test map:
  dry-run plan generation, high-confidence candidate mapping, owner-decision
  gating before retire mutation, and idempotency for already-membered work
  items.

## Commands Executed

```text
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-orphan-wi-membership-backfill-slice-2-scoping --format json --preview-lines 2000
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-membership-backfill-slice-2-scoping
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-membership-backfill-slice-2-scoping
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-orphan-wi-membership-discovery-slice-1 --format json --preview-lines 500
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m groundtruth_kb backlog show WI-3450 --json
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/discover_orphan_wi_memberships.py --run-id codex-scope-check-2026-05-29T1752Z --json
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
