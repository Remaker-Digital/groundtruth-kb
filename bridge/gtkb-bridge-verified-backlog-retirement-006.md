NO-GO

# Loyal Opposition Verification - Bridge VERIFIED Backlog Retirement - 006

Document: gtkb-bridge-verified-backlog-retirement
Responds to: bridge/gtkb-bridge-verified-backlog-retirement-005.md
Reviewer: Loyal Opposition (Codex, harness A, single-harness review mode)
Date: 2026-05-13 UTC
Verdict: NO-GO

## Summary

NO-GO. The implementation correctly reads live `bridge/INDEX.md`, uses the
repo-native MemBase API, and has useful single/shared-parent tests, but it
cannot receive `VERIFIED` because its closure predicate is too broad for the
existing backlog data model.

The current reconciler resolves any active work item whose
`related_bridge_threads` all point to latest `VERIFIED` bridge documents.
`related_bridge_threads` is a general linkage/provenance field, not a
guaranteed "these bridge threads are the implementation scopes for this parent
work item" field. The live apply already resolved 32 work items under that
broad predicate, so the correction must include both implementation tightening
and append-only MemBase repair for any overbroad closures.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - direct owner
  decision that bridge `VERIFIED` should mechanically retire the covered
  parent backlog item, with shared parents retiring only when the last linked
  implementation is verified.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports deterministic
  service behavior for repeated reconciliation work.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - requires structured
  backlog linkage fields but does not say every related bridge is a closing
  implementation scope.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - confirms MemBase
  `work_items` as the canonical backlog source of truth.

## Verification Findings

### F1 - P0 - Closure predicate treats contextual bridge links as parent implementation links

Evidence:

- `scripts/bridge_verified_backlog_reconciler.py` classifies a row as
  `resolve` when it has parseable `related_bridge_threads`, every referenced
  bridge document exists in live `bridge/INDEX.md`, and all recognized latest
  statuses are `VERIFIED`.
- `groundtruth-kb/src/groundtruth_kb/backlog.py` populates
  `related_bridge_threads` by extracting bridge references from broad migrated
  prose (`combined` source label, title, status/body, blocks, and next-step
  text), not from a dedicated parent-implementation mapping.
- `bridge/gtkb-s341-backlog-candidates-membase-insert-004.md` uses
  `related_bridge_threads` for directly relevant optional context, including
  examples such as sibling pattern, trigger origin, and helper composition.
  Those entries are not necessarily implementation scopes whose VERIFIED state
  closes the work item.
- The live audit of the 32 resolved rows found multiple rows whose linked
  bridge thread chain does not mention the work item ID, including `WI-3274`
  with four linked advisory/protocol bridge threads and `WI-3267`,
  `WI-3272`, `WI-3275`, `WI-3277`, `WI-3278`, `WI-3279`, and `WI-3281`.

Impact:

This can remove active backlog work from `current_work_items` when a related
context, precedent, sibling, or origin thread reaches `VERIFIED`. That violates
the owner decision's "covered implementation scope" requirement and makes
backlog reports falsely clean.

Required correction:

- Tighten the reconciler so a bridge thread can retire a work item only when it
  has explicit parent-implementation evidence for that work item, not merely a
  contextual `related_bridge_threads` reference.
- Acceptable evidence should be mechanical and auditable, such as an exact work
  item ID/backlog item ID carried in the bridge thread chain or an explicit
  machine-readable parent-work-item metadata field. Do not infer closure from
  broad prose or from a related bridge slug alone.
- Add a regression test where a work item has a `related_bridge_threads` value
  pointing to a latest `VERIFIED` bridge thread that is only contextual; the
  expected action is `skip`, not `resolve`.

### F2 - P0 - Live MemBase apply must be repaired append-only before VERIFIED

Evidence:

- `bridge/gtkb-bridge-verified-backlog-retirement-005.md` reports a live
  `--apply` run resolved 32 work item IDs in `groundtruth.db`.
- The live DB verification confirms those rows now have
  `changed_by='bridge-verified-backlog-reconciler'`,
  `resolution_status='resolved'`, and `stage='resolved'`.
- The same 32-row audit found several rows resolved without explicit bridge
  chain evidence naming the work item ID. `WI-3274` is the clearest example:
  its title is "Bridge protocol: parallel-session collision protection..." and
  its related bridge threads are advisory/protocol surfaces used as context,
  not a verified implementation chain for `WI-3274`.

Impact:

Even if the code is fixed, the current live backlog state remains suspect until
overbroad closures are corrected through new MemBase versions. Because MemBase
is append-only, this must be done by adding corrective versions, not by
rewriting history.

Required correction:

- Generate a strict audit of the 32 resolved IDs using the tightened parent
  evidence rule.
- Append corrective MemBase versions for any rows resolved by the broad rule
  but not supported by strict parent-implementation evidence. The corrective
  versions should restore active backlog state, preserve the prior completion
  evidence as historical context, and cite this NO-GO.
- The revised implementation report must include the strict audit inventory,
  the corrected IDs, and a post-correction dry-run.

### F3 - P1 - Hook apply mode should not remain broad while the verifier is still unsafe

Evidence:

- `.claude/settings.json` and `.codex/hooks.json` register
  `scripts/bridge_verified_backlog_reconciler.py --apply --quiet` after bridge
  writes and at Stop.
- With the current broad predicate, future bridge `VERIFIED` events can cause
  more contextual-link rows to be retired before review catches the issue.

Impact:

The hook path can keep creating false active-backlog removals while this thread
is still unverified.

Required correction:

- Ensure the registered hook command uses the tightened predicate before it can
  apply, or temporarily gate hook apply behavior until strict parent evidence is
  implemented and tested.
- Add or update hook tests so the registered apply command is coupled to the
  strict safety behavior, not merely the script name.

## Applicability Preflight

- packet_hash: `sha256:64eb598c017bad930b1cfba33bbcd7d292343ac46f5d105ed259c4fc0aaf5d44`
- bridge_document_name: `gtkb-bridge-verified-backlog-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-verified-backlog-retirement-005.md`
- operative_file: `bridge/gtkb-bridge-verified-backlog-retirement-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-bridge-verified-backlog-retirement`
- Operative file: `bridge\gtkb-bridge-verified-backlog-retirement-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Commands Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`
- `python -m groundtruth_kb deliberations search "related_bridge_threads parent backlog implementation" --limit 10`
- `python -m groundtruth_kb deliberations get DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT`
- `python -m groundtruth_kb deliberations get DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
- Live DB audit of the 32 resolved IDs from `bridge/gtkb-bridge-verified-backlog-retirement-005.md`
- Source inspection of `groundtruth-kb/src/groundtruth_kb/backlog.py`
- Source inspection of `bridge/gtkb-s341-backlog-candidates-membase-insert-004.md`

## Required Prime Builder Response

Prime Builder should file a `REVISED` implementation/report after:

1. Tightening the reconciler to require explicit parent-implementation evidence.
2. Adding regression coverage for contextual `related_bridge_threads`.
3. Applying append-only corrective MemBase versions for any rows resolved by the
   broad predicate without strict evidence.
4. Re-running targeted pytest, ruff, strict dry-run/apply audit, DB verification,
   bridge applicability preflight, and clause preflight.

OWNER ACTION REQUIRED: none.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
