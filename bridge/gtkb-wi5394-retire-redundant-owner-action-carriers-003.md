REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5394-retire-redundant-owner-action-carriers
Version: 003
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5394-retire-redundant-owner-action-carriers-002.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5394

target_paths: ["harness-state/codex/owner-action-canonical-authority-recovery-2026-07-09.md", "harness-state/codex/owner-action-manual-claude-lo-path-2026-07-09.md", "harness-state/codex/owner-action-startup-relay-repair-2026-07-09.md"]

implementation_scope: exact three-path redundant runtime-carrier retirement
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: none

# WI-5394 Revised Proposal — Exact Three-File Retirement

## Revision Claim

This revision resolves the sole finding in version 002. The owner has now
granted explicit per-path destructive authority in
`DELIB-20260801-WI5394-EXACT-THREE-FILE-DELETION-APPROVAL` for exactly the
three declared paths and rejected the non-destructive archival alternative.

The proposal otherwise preserves version 001's scope, fail-closed checks, and
independent review requirements. No file has been deleted. This `REVISED`
filing authorizes no implementation by itself; Prime Builder must still receive
a fresh independent `GO`, acquire the exact implementation claim, and pass the
schema-v3 implementation-start gate before any deletion.

## Finding Response

### F1 — Explicit owner per-path deletion authority

Resolved. The owner replied, “Approve WI-5394 exact three-file deletion as
written.” The decision-capture workflow recorded that answer as
`DELIB-20260801-WI5394-EXACT-THREE-FILE-DELETION-APPROVAL` (rowid 13478,
version 1, `outcome=owner_decision`, `work_item_id=WI-5394`). The record names
each path and preserves these boundaries:

- no wildcard or directory deletion;
- no move, rename, or ignore-rule substitute;
- no deletion of any fourth path;
- fresh `GO`, exact claim, implementation-start, and independent verification
  remain mandatory;
- no dispatcher, TAFE, session-envelope, durable harness-registry, database,
  credential, Git, deployment, release, or unrelated mutation.

## Requirement Sufficiency

Existing requirements sufficient. The durable decisions, owner deletion
approval, worktree-hygiene rules, non-authority contract, and bridge gates fully
define the bounded retirement. No new or revised requirement is required before
implementation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5394; DELIB-20260801-WI5394-EXACT-THREE-FILE-DELETION-APPROVAL; bridge/gtkb-wi5394-retire-redundant-owner-action-carriers-002.md",
  "canonical_authority": "The three corresponding Deliberation Archive records remain the durable authoritative records; the named harness-state markdown files are redundant, non-authoritative carriers.",
  "primary_route": "REVISED proposal, independent Loyal Opposition GO, exact work-intent claim, schema-v3 implementation-start, operation-time consumer and hash checks, deletion of only the three named files, implementation report, and independent verification.",
  "before_behavior": "Three redundant harness-local owner-action markdown carriers duplicate durable Deliberation Archive content and can be mistaken for live authority.",
  "after_behavior": "The Deliberation Archive remains the sole durable authority for the three decisions, while the redundant harness-local copies are absent and all active consumers remain intact.",
  "self_descriptive_naming": "The work item and bridge slug identify retirement of redundant owner-action carriers, and every authorized target is listed by its exact path.",
  "obsolete_guidance_disposition": "Only the three owner-approved redundant carriers are removed; numbered bridge history and Deliberation Archive records remain append-only and unchanged.",
  "history_preservation": "The corresponding Deliberation Archive records, this bridge chain, and the recorded pre-delete hashes preserve the decisions and audit trail.",
  "baseline": "All three named files are present with the recorded SHA-256 hashes, each maps substantively to its corresponding Deliberation Archive record, and the active-consumer scan is empty.",
  "expected_result": "Exactly the three named files are absent; their Deliberation Archive records remain readable; no active source, test, configuration, hook, dispatcher, TAFE, credential, release, deployment, Git-history, or unrelated workspace state changes.",
  "rollback": "Restore only an accidentally deleted named file from its recorded preimage when authorized; do not recreate a redundant carrier after successful verified deletion unless a new governed decision requires it.",
  "hard_invariants": "No wildcard or directory deletion; no fourth target; no operation before fresh GO, matching claim, and schema-v3 implementation-start; no deletion if hashes, contents, archive mappings, or consumer scan differ.",
  "fail_closed_conditions": "Missing or stale GO, foreign or expired claim, missing implementation-start, target-set mismatch, preimage hash mismatch, archive-record mismatch, active consumer reference, or any requested scope expansion blocks deletion before effect.",
  "essential_context_preservation": "Preserve the exact owner approval, all three Deliberation Archive records, v001/v002/v003 bridge evidence, preimage hashes, and the distinction between redundant harness-state copies and governed authority."
}
```

## Current Preimage Evidence

Fresh read-only evidence on 2026-08-01:

| Exact path | Bytes | SHA-256 | Durable record | Content result |
| --- | ---: | --- | --- | --- |
| `harness-state/codex/owner-action-canonical-authority-recovery-2026-07-09.md` | 1477 | `E697AE87C2F37EBCE6F6207FB6ACBAD117E6E2642762ECBD1778FD6E9FB4BBCF` | `DELIB-202665933` | Equal after LF normalization and trailing-whitespace removal. |
| `harness-state/codex/owner-action-manual-claude-lo-path-2026-07-09.md` | 1498 | `B353386B468061E5851DFB4C2F7633DFD543334684774168AAA06B7DFECFE858` | `DELIB-202665934` | Equal after LF normalization and trailing-whitespace removal. |
| `harness-state/codex/owner-action-startup-relay-repair-2026-07-09.md` | 736 | `ADDD6168E4DBD4ED469E528DD018EE8DCDE0F9A03AF5AE94E830963C51DEEAFB` | `DELIB-202665935` | Exact text and content hash match. |

The first two byte hashes differ from their Deliberation Archive content hashes
only because the stored records contain terminal-newline normalization; their
LF-normalized, right-trimmed substantive content is equal. The third is exactly
equal. Each durable record remains version 1, queryable, and linked to the same
owner decision carried by its local file.

A focused exact-string scan across active `.claude` rules/hooks (excluding
alternate `.claude/worktrees`), `.codex`, `config`, `scripts`,
`groundtruth-kb`, and `platform_tests` returned no reference to any exact path.
Historical bridge text and transcript inventories may mention the filenames;
those are audit evidence, not startup/runtime consumers.

All preimage hashes, content comparisons, and active-consumer scans must be
repeated inside the implementation claim/start window immediately before
deletion. Any drift, missing durable record, substantive mismatch, or active
consumer reference stops the operation without deleting anything.

## Exact Authorized Operation

1. Confirm latest bridge state is this proposal's independent `GO`, the exact
   claim belongs to this session, and schema-v3 implementation-start covers all
   three paths.
2. Re-read all three exact paths without following wildcards or computed
   directory targets; require their current SHA-256 values to equal the table.
3. Re-query `DELIB-202665933`, `DELIB-202665934`, and `DELIB-202665935` through
   the canonical Deliberation Archive reader; require every record to remain
   queryable and substantively equal to its local carrier after the stated
   normalization.
4. Repeat the exact-path consumer scan across active startup, rule, hook,
   configuration, source, and test surfaces; fail closed on any active
   dependency.
5. Resolve and verify the three absolute targets remain exact descendants of
   `E:/GT-KB/harness-state/codex` and equal the declared target set.
6. Delete the three files by explicit literal path in one bounded operation.
   Do not enumerate a directory, use a wildcard, or compute additional targets.
7. Require all three exact paths absent, all three durable records still
   queryable, and `git status --short` on the declared paths empty because the
   retired files were untracked.
8. Run bounded startup/health read-only checks and file an implementation report
   with the pre/post evidence for independent verification.

## Explicit Exclusions

- No wildcard, recursive operation, directory deletion, move, rename, archive,
  ignore rule, or fourth path.
- No change to session envelopes, active-workspace state, session lifecycle
  state, durable harness identities/registry, dispatcher/TAFE configuration or
  runtime, leases, locks, workers, routing, eligibility, roles, or models.
- No MemBase, specification, work-item, test-record, deliberation, project,
  authorization, source, test, configuration, credential, Git, deployment,
  release, or external-system mutation.
- All implementation and evidence remain in-root under `E:/GT-KB`; no live
  artifact or dependency is created or required outside the project root.

This proposal performs no KB or MemBase mutation, does not create or update any
specification, work item, test record, deliberation, project, authorization, or
other `groundtruth.db` row, and therefore does not include `groundtruth.db` in
`target_paths`.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260801-WI5394-EXACT-THREE-FILE-DELETION-APPROVAL` — current
  explicit owner approval for deletion of exactly the three named paths.
- `DELIB-202665933` — durable canonical-authority recovery decision promoted
  from the first local carrier.
- `DELIB-202665934` — durable manual Loyal Opposition routing decision promoted
  from the second local carrier; its old dispatcher-disabled wording is
  historical rather than current runtime authority.
- `DELIB-202665935` — durable startup-relay repair authorization promoted from
  the third local carrier.
- `bridge/gtkb-wi5394-retire-redundant-owner-action-carriers-001.md` — original
  bounded proposal.
- `bridge/gtkb-wi5394-retire-redundant-owner-action-carriers-002.md` — exact
  `NO-GO` requiring per-path owner deletion authority.

## Owner Decisions / Input

The owner approved the destructive choice exactly as presented and rejected
the non-destructive archival alternative. The authoritative evidence is
`DELIB-20260801-WI5394-EXACT-THREE-FILE-DELETION-APPROVAL`.

That decision authorizes only the three named deletions after the remaining
bridge and implementation-start gates. It does not waive fresh preimage,
durable-record, consumer-absence, in-root, nonimpairment, or independent
verification checks.

## Specification-Derived Verification

| Requirement | Executed evidence required in implementation report |
| --- | --- |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Re-query all three DELIB records and prove normalized substantive equality before deletion and continued queryability afterward. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-WORK-TREE-HYGIENE-001` | Record exact current preimage hashes and prove exactly three declared paths become absent with no neighboring change. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Exact active-consumer scan passes before deletion; bounded startup/health checks pass afterward; dispatcher/TAFE and harness authority state remain unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; project authorization specifications | Fresh independent `GO`, exact claim, and schema-v3 implementation-start all precede deletion. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Read-only role evidence confirms this session remains Prime Builder and authors no LO status. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolved literal targets and all evidence remain inside `E:/GT-KB`. |
| Owner destructive authority | Exact DELIB readback names the same three paths and no broader operation. |

No `pytest` or Ruff execution is required for deletion of three untracked
Markdown carriers because no executable source or test changes. The
implementation report must instead execute and report the exact deterministic
hash, normalized-content, consumer-scan, literal-path, durable-readback,
startup/health, and path-isolation checks above.

## Acceptance Criteria

- Fresh owner approval evidence names exactly all three paths.
- All three current preimages match the proposal table at operation time.
- Each local carrier remains substantively represented by its durable record.
- No active startup/runtime consumer references an exact target.
- Exactly the three declared paths are deleted; no fourth path changes.
- All three durable records remain queryable.
- Dispatcher/TAFE and harness authority/runtime state remain unchanged.
- An independent Loyal Opposition session verifies the implementation evidence.

## Risk and Rollback

The material risk is deletion of unique authority or a live runtime dependency.
Exact preimage binding, normalized durable-record equality, active-consumer
scans, literal target resolution, owner per-path approval, and fresh independent
review make the operation fail closed.

Because the three targets are untracked, Git cannot restore them. If immediate
post-delete checks fail, do not reconstruct content from memory or ad hoc chat.
File a blocker and use a separately governed successor that restores only the
recorded exact preimage bytes from the implementation evidence. The durable
Deliberation Archive records remain authoritative throughout.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
