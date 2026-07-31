NEW

# Repair Proposal - Restore MEMORY.md as a bounded operational index

bridge_kind: prime_proposal
Document: gtkb-wi5289-memory-index-retention-compaction
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5289

target_paths: ["memory/MEMORY.md", "memory/archive/MEMORY-session-details-20260628-20260715.md"]

implementation_scope: documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore `memory/MEMORY.md` to its verified three-tier-memory role as a compact
operational index. The current working file is 98,421 bytes and fails both the
25,000-byte release ceiling and the stricter 12,000-byte Slice 8 index guard.
Its Recent Sessions section has regrown into a content store containing dozens
of full session narratives and visible encoding drift.

The implementation will preserve the exact current Recent Sessions content in
one additive dated archive, then replace that section with bounded one-line
hooks and a direct archive pointer. The compact index will state the 12,000-byte
limit and exact verification commands so a future wrap cannot treat a full
narrative as valid index content. No MemBase, Deliberation Archive, bridge,
source, test, harness, dispatcher, TAFE, credential, or external-system state
will be changed.

## Baseline And Concurrent-Content Ownership

- HEAD at proposal preparation:
  `2974839d62374e8e23cd585d6e3c254716a907ec`.
- HEAD `memory/MEMORY.md` blob:
  `5eccc4700c9c900f126704e9600e78c8f2112532`, 25,234 bytes.
- Staged index blob:
  `74e8a2bcccc96fff6d1820e29e1940c3ad3d239e`, 95,718 bytes.
- Authoritative working-copy blob at proposal preparation:
  `c0001d4fcd189cd243e37442f6a72212b0ea6e2b`, 98,421 bytes.
- The file is `MM`: staged session entries and two later unstaged entries are
  foreign concurrent content. This proposal claims preservation and
  compaction of those bytes, not authorship of their substantive narratives.
- The additive archive target does not exist at proposal preparation.
- Implementation must acquire the matching work-intent claim and
  implementation-start packet, snapshot the then-live working bytes, and abort
  if `memory/MEMORY.md` changes between snapshot and replacement.
- No Git index operation or commit is included. Any later finalization requires
  separate exact mechanical authority and must prove that no concurrent bytes
  were dropped.

## Specification Links

- `ADR-0001` - MemBase is durable factual memory, the Deliberation Archive is
  durable reasoning, and MEMORY.md is only the compact operational-notepad
  tier.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The index may hold bounded pointers
  but cannot become a stale substitute for fresh authoritative reads.
- `GOV-STANDING-BACKLOG-001` - Work-item authority remains in MemBase rather
  than repeated session prose in MEMORY.md.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Both the active index and its
  dated archive remain inside the mandatory GT-KB project-root boundary.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Compaction must preserve every
  current session narrative additively while restoring startup usability.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Source hashes, archive
  hashes, byte ceilings, line limits, and exact tests make the migration
  independently evaluable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Implementation requires independent GO,
  matching claim, and implementation-start authority before file mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  binds the migration and preservation proof to governing contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work
  item, and target paths are explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED
  must rerun both memory guards and inspect the byte-preservation evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Durable facts remain in governed
  artifacts; the notepad index carries only navigational hooks.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The archive, source hashes, work
  item, report, and verdict form the durable migration evidence graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Session narratives transition from
  active index content to archived history without being deleted.

## Prior Deliberations

- `DELIB-20265460` - The owner authorized Slice 8 to rewrite MEMORY.md as an
  index and retire session ephemera; this repair restores that verified state
  after regression.
- `DELIB-20260672` - The owner selected an index-only MEMORY cadence rather
  than allowing operational memory to remain a content store.
- `DELIB-202666274` - The owner authorized all required modernization blocker
  repairs while preserving bridge review, implementation-start, and mechanical
  operation gates.

## Owner Decisions / Input

No additional product decision is required. The three-tier memory architecture,
Slice 8 owner decision, verified 12,000-byte guard, and project-level
modernization authorization already determine the outcome. This proposal
chooses additive archival over deletion to preserve the concurrent worktree
content. It does not authorize staging, commit, push, deployment, release,
credentials, dispatcher, TAFE, harness, routing, role, or external-system
mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The verified architecture and tests already define the authority boundary and
the stricter byte ceiling. The defect is a content-retention regression, not a
missing product requirement. The working-copy narratives are non-authoritative
but are preserved additively because the owner requires the concurrent
worktree to remain authoritative during modernization.

## Proposed Scope

1. After GO/claim/start, capture the live `memory/MEMORY.md` bytes and record
   the complete-file SHA-256 plus the exact byte range and SHA-256 of the
   `## Recent Sessions` block.
2. Create
   `memory/archive/MEMORY-session-details-20260628-20260715.md` with an ASCII
   provenance header followed by the complete unabridged Recent Sessions block
   from the captured working copy.
3. Rewrite only the Recent Sessions block in `memory/MEMORY.md`; preserve the
   bootstrap, quick-reference, and protected-file sections while normalizing
   the visible title/header encoding to valid UTF-8 or ASCII.
4. Retain no more than five newest session hooks, each on one physical line and
   no more than 240 characters, plus a direct relative link to the archive and
   fresh-read routes for backlog, bridge, and deliberations.
5. Add an index-local instruction that full session narratives belong in the
   dated archive or governed session evidence, that the index must remain at or
   below 12,000 bytes, and that both memory tests must run after every edit.
6. Verify the archive body hash equals the captured block hash and that every
   removed session identifier remains searchable in the archive.
7. Leave every non-target path and the Git index unchanged.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5289, DELIB-20265460, DELIB-20260672, and DELIB-202666274",
  "canonical_authority": "ADR-0001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short",
  "before_behavior": "MEMORY.md is a 98,421-byte content store; startup loads are truncated and both enforced ceilings fail.",
  "after_behavior": "MEMORY.md is a sub-12,000-byte navigational index and every displaced session narrative remains in one hash-anchored in-root archive.",
  "self_descriptive_naming": "The archive filename states its content and date range; index hooks name the session and durable evidence route.",
  "obsolete_guidance_disposition": "Full narrative wrap entries are explicitly classified as archive content, not active-index content; no authoritative record is retired.",
  "history_preservation": "The complete then-live Recent Sessions block is copied without abridgment and verified by hash before the index replacement is accepted.",
  "baseline": {
    "head": "2974839d62374e8e23cd585d6e3c254716a907ec",
    "head_memory_blob": "5eccc4700c9c900f126704e9600e78c8f2112532",
    "index_memory_blob": "74e8a2bcccc96fff6d1820e29e1940c3ad3d239e",
    "working_memory_blob": "c0001d4fcd189cd243e37442f6a72212b0ea6e2b",
    "working_bytes": 98421,
    "canonical_ceiling_bytes": 12000
  },
  "expected_result": {
    "memory_bytes_max": 12000,
    "archive_body_hash_matches_snapshot": true,
    "lost_session_identifiers": 0,
    "non_target_changes": 0,
    "git_index_operations": 0
  },
  "essential_context_preservation": "Session identifiers, dates, substantive narratives, evidence paths, and next-action details remain recoverable from the dated archive while active authority continues to come from fresh MemBase, bridge, and Deliberation Archive reads.",
  "hard_invariants": [
    "no session narrative deletion",
    "no MemBase or Deliberation Archive mutation",
    "no bridge, TAFE, dispatcher, or harness mutation",
    "no Git index, commit, push, deploy, or release operation",
    "no edit outside the two declared memory paths",
    "frozen modernization acceptance scope unchanged"
  ],
  "fail_closed_conditions": [
    "MEMORY.md changes after snapshot and before replacement",
    "archive body hash differs from the captured Recent Sessions block",
    "any displaced session identifier is absent from the archive",
    "MEMORY.md exceeds 12000 bytes",
    "either memory guard fails",
    "any non-target path changes"
  ],
  "rollback": "Restore the captured working-copy bytes from the pre-migration snapshot and remove only the new dated archive after verifying the restored SHA-256."
}
```

## Spec-Derived Verification Plan

| Specification | Verification and expected result |
|---|---|
| `ADR-0001` | Inspect MEMORY.md to prove it contains only bootstrap/reference text and bounded hooks; inspect the archive for full narratives. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Confirm the compact index names fresh `gt backlog`, bridge CLI, and deliberation routes rather than copied current-state claims. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm both declared targets resolve beneath `E:\GT-KB\memory` and no external memory dependency is introduced. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare the captured Recent Sessions SHA-256 with the archive body SHA-256 and prove zero missing session identifiers. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Record before/after byte counts, hashes, line lengths, archive path, and exact command outputs. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and ADR/DCL clause preflights pass with zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns both memory tests and the preservation audit before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify valid GO, matching claim, and implementation-start packet before either path is written. |

Exact implementation verification commands:

```text
python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short
python -c "from pathlib import Path; p=Path('memory/MEMORY.md'); assert p.stat().st_size <= 12000; assert max(map(len, p.read_text(encoding='utf-8').splitlines())) <= 240"
git status --short -- memory/MEMORY.md memory/archive/MEMORY-session-details-20260628-20260715.md
```

The implementation report must additionally provide a deterministic
preservation audit containing:

- captured full-file SHA-256;
- captured Recent Sessions block SHA-256;
- archive body SHA-256;
- before/after byte counts;
- total displaced session identifiers and missing count;
- proof that the Git index was not mutated.

## Acceptance Criteria

1. `memory/MEMORY.md` is valid UTF-8, no more than 12,000 bytes, and every
   physical line is no more than 240 characters.
2. Both existing memory test files pass in full.
3. The archive contains the exact unabridged captured Recent Sessions block and
   its body hash equals the captured block hash.
4. Every session identifier removed from the active index remains searchable
   in the archive; missing count is zero.
5. The index retains no more than five one-line recent-session hooks and states
   the archive route, 12,000-byte ceiling, and post-edit verification commands.
6. No authoritative DB, source, test, bridge, TAFE, dispatcher, harness,
   credential, external system, Git index, commit, push, deploy, or release
   mutation.
7. Independent LO reviews the preservation evidence and returns VERIFIED before
   the repair is considered complete.

## Risk / Rollback

The material risk is losing concurrent staged or unstaged session narratives
during compaction. The implementation therefore snapshots the live file,
copies the entire target block before replacement, verifies the archive body by
hash, and aborts on any intervening source change. Rollback restores the exact
captured file bytes and removes only the new archive after hash verification.

## Bridge Filing

This proposal is filed as the first append-only numbered bridge file,
`bridge/gtkb-wi5289-memory-index-retention-compaction-001.md`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge
files remain the governed workflow surfaces.

## Recommended Commit Type

`chore` - the change restores a non-authoritative operational index and
archives historical session detail without changing product behavior. Any
eventual commit remains separately mechanically authorized.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
