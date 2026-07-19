NEW

# WI-5394 - Retire redundant harness-local owner-action carriers

bridge_kind: prime_proposal
Document: gtkb-wi5394-retire-redundant-owner-action-carriers
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5394

target_paths: ["harness-state/codex/owner-action-canonical-authority-recovery-2026-07-09.md", "harness-state/codex/owner-action-manual-claude-lo-path-2026-07-09.md", "harness-state/codex/owner-action-startup-relay-repair-2026-07-09.md"]

implementation_scope: exact redundant runtime-carrier retirement
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Retire exactly three untracked Codex harness-local owner-action markdown copies
after independently proving their decisions already exist in the durable
Deliberation Archive as `DELIB-202665933`, `DELIB-202665934`, and
`DELIB-202665935`. The local files are non-authoritative scratch carriers; one
also retains stale dispatcher-disabled guidance that must not compete with
current policy.

This is a destructive cleanup and implementation must fail closed until the
owner grants exact per-path deletion authority in addition to project PAUTH and
independent GO. No wildcard, directory deletion, move, ignore rule, source
change, database mutation, harness process change, or Git operation is in
scope. Independent verification must compare substantive content and prove no
active consumer references any local path before deletion.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable owner decisions belong in
  governed artifacts, not competing harness-local copies.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - each local carrier is linked to its
  durable decision and explicit retirement evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - superseded local candidates require
  explicit retirement rather than silent disappearance.
- `GOV-WORK-TREE-HYGIENE-001` - exact redundant artifacts receive ownership and
  byte-bounded disposition rather than broad cleanup.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - retirement must not change
  runtime role, dispatch, startup, or authority behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED remain
  mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing
  requirements are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  and exact paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each
  local file to durable decision and consumer-absence evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5394 durably owns this discovered residue.

## Prior Deliberations

- `DELIB-202665933` - durable canonical-authority recovery decision promoted
  from the first local carrier.
- `DELIB-202665934` - durable temporary manual Loyal Opposition decision
  promoted from the second local carrier.
- `DELIB-202665935` - durable startup-relay repair authorization promoted from
  the third local carrier.
- Owner directive, 2026-07-16 - clear all worktree dirt with exact ownership;
  correct flawed or competing audit surfaces without blocking other work.

## Owner Decisions / Input

The project is authorized, but destructive cleanup remains a mechanical
exception. Implementation requires a later exact owner authorization naming
all three paths. This proposal does not itself grant deletion authority and
performs no mutation.

## Requirement Sufficiency

Existing requirements are sufficient. The canonical destination and the
non-authority of harness-local scratch records are already defined; only exact
retirement evidence is missing.

## Proposed Scope

1. Hash and read each exact local file without modifying it.
2. Query the three durable DELIB records and compare substantive decision,
   provenance, and limits.
3. Search active startup, source, configuration, and test surfaces for exact
   path references; fail closed on any consumer.
4. After independent GO and exact owner deletion authority, remove only the
   three declared files.
5. Verify all DELIB records remain queryable and no other path changed.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Compare each local record with its named DELIB record. | Every substantive decision, provenance statement, and limit is durably represented before local retirement. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-WORK-TREE-HYGIENE-001` | Record exact pre-delete hashes and post-delete path status. | Exactly three declared paths disappear; no wildcard or neighboring path is affected. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Search active consumers before deletion and rerun startup/health smoke checks after deletion. | No active consumer references the files and runtime behavior is unchanged. |
| Mechanical authority | Inspect owner authorization and exact path set before any deletion. | Authority names all three targets and no broader destructive operation. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5394; DELIB-202665933; DELIB-202665934; DELIB-202665935","canonical_authority":"GOV-ARTIFACT-ORIENTED-GOVERNANCE-001; GOV-WORK-TREE-HYGIENE-001","primary_route":"durable Deliberation Archive records plus exact local-carrier retirement","before_behavior":"Three untracked harness-local copies duplicate durable decisions and one carries stale operational guidance.","after_behavior":"The durable DELIB records remain authoritative and queryable; the exact redundant local copies no longer create dirt or competing guidance.","self_descriptive_naming":"WI-5394 and the three explicit target names identify redundant owner-action carrier retirement.","obsolete_guidance_disposition":"Stale local operational wording is retired only after its durable historical decision remains preserved.","history_preservation":"Pre-delete hashes, DELIB mappings, proposal, report, verdict, and exact owner authorization preserve the complete retirement trail.","baseline":{"local_files":3,"durable_records":["DELIB-202665933","DELIB-202665934","DELIB-202665935"]},"expected_result":{"local_files":0,"durable_records_queryable":3,"other_paths_changed":0},"rollback":{"instructions":"If retirement is later reversed, restore only independently recorded bytes through a governed successor; do not reconstruct from memory.","verification":"hash comparison and DELIB re-query"},"hard_invariants":["exact three-path scope","durable decisions remain","no directory or wildcard deletion","no startup, role, routing, eligibility, dispatcher, database, or Git mutation"],"fail_closed_conditions":["missing DELIB mapping","substantive content mismatch","active consumer reference","missing exact owner deletion authority","missing GO, claim, start, or independent VERIFIED"],"essential_context_preservation":"Retain owner decision content, provenance, limits, durable IDs, byte hashes, and the distinction between historical decision evidence and current operational authority."}
```

## Acceptance Criteria

1. All three durable DELIB records contain the corresponding decisions.
2. No active consumer references any local target.
3. Exact owner destructive authority names all three files.
4. Only the three declared files are deleted and all durable records remain.
5. Independent VERIFIED follows the deletion evidence.

## Risk / Rollback

The risk is deleting unique authority or a live dependency. Exact DELIB mapping,
consumer scans, per-path owner authority, and independent verification fail
closed against that risk. Rollback uses only recorded bytes through a governed
successor; no broad restore or reconstructed content is acceptable.

## Bridge Filing

File through the governed Codex non-bypass helper. The numbered bridge file
chain is append-only. Deterministic TAFE routing remains external; this filing
does not contact or configure any harness.

## Recommended Commit Type

No commit is expected for deleting files absent from HEAD; retain the governed
retirement evidence in the normal bridge lifecycle.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
