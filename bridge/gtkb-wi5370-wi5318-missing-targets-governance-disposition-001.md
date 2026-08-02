NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; strict-lifecycle replacement proposal
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal — WI-5318 Missing-Targets Governance Disposition

bridge_kind: prime_proposal
Document: gtkb-wi5370-wi5318-missing-targets-governance-disposition
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719
Project Authorization Version: 2
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Related Work Item: WI-5318
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: none

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write. It creates no source, archive, or implementation target
and authorizes no deletion.

## First-Line Role Eligibility Check

PASS. Harness A is active Prime Builder and may file a `NEW` proposal. The
strict governed writer cannot append a correction to the historical repair
thread because immutable version 003 contains decorated, noncanonical Version
metadata. This fresh, targetless replacement thread preserves that history and
requests independent review without relaxing strict parsing.

## Proposed Disposition

Loyal Opposition should reject the action required by version 006 because it
targets the wrong artifact. The 2,103-byte untracked residue described by
versions 001–004
is absent. The current file at the reused numbered path is a different,
12,041-byte, tracked, clean Loyal Opposition `GO` created later as the lawful
version 007 of the source thread. Versions 008 and 009 of that same source
thread depend on it as their exact `Responds to` ancestry.

Archiving and removing the current version 007 would not durably preserve the
lost 2,103-byte residue. It would delete load-bearing append-only bridge history,
break the source thread's current version chain, and contradict version 006's
own requirement to establish exact source identity before mutation.

No archive, deletion, restoration, Git operation, implementation start,
implementation-start packet, source/test/configuration mutation, dispatcher or
TAFE action, harness mutation, deployment, release, credential action, or
external-system action is performed.

## Exact Current Evidence

- `bridge/gtkb-wi5318-failed-verified-finalization-repair-007.md` exists at
  12,041 bytes with SHA-256
  `406e9e3e219f714397576e78861fdafd3986f35499733114db09026f6a489af3`.
- The current version 007 begins with `GO`, is tracked and clean, and is present
  in Git history at 12,041 bytes. It is not the former 2,103-byte terminal
  residue with SHA-256
  `0859be38938b488b63d8a7f586e8d530edce93a6d5b88312844c280ed1868cdb`.
- `bridge/gtkb-wi5318-failed-verified-finalization-repair-008.md` is the
  post-implementation report that explicitly responds to this current version
  007 `GO`.
- `bridge/gtkb-wi5318-failed-verified-finalization-repair-009.md` is the current
  source-thread `NO-GO` and preserves versions 007 and 008 as its ancestry.
- The former per-file archive
  `independent-progress-assessments/WI-5370-gtkb-wi5318-failed-verified-finalization-repair-007.missing-targets-terminal.md`
  is absent. Its absence is a real historical durability defect, but current
  source-thread bytes cannot be relabeled as the missing predecessor bytes.
- `gtkb-wi5370-batched-archive-preserve-service` is terminal `VERIFIED` at
  version 012. That reusable mechanism does not prove that the old 2,103-byte
  payload still exists and does not authorize deleting unrelated current
  history.
- WI-5370 is canonically resolved, while the exact archive-pilot PAUTH v2 and
  list-free Tree Stabilization PAUTH remain active. Neither grants authority to
  manufacture source identity or bypass append-only bridge history.
- A governed attempt to append the targetless correction as the old thread's
  version 007 created no bridge file and failed closed with
  `WRONG_BRIDGE_VERSION_METADATA`: immutable version 003 declares
  `Version: 003 (NEW; post-implementation report)` instead of the strict
  numeric value. The failed claim was released. This replacement thread is the
  established repair-forward path; no historical file is rewritten.

## Governance Defects In Version 006

### F1 — Source identity is disproved

Version 006 quotes the current 12,041-byte hash but treats that file as if it
were the residue described by the original 2,103-byte repair. Exact byte size,
hash, status, content, Git tracking, and chronology disprove that identity.

### F2 — The required removal would break append-only ancestry

The current version 007 is a lawful LO `GO`; source-thread versions 008 and 009
cite it. Removing it would create a numbered-chain hole and erase load-bearing
review evidence. `GOV-FILE-BRIDGE-AUTHORITY-001` forbids that mutation.

### F3 — A reusable archive service is not transaction evidence

The terminal service proves a bounded mechanism exists. It neither recovers the
missing historical bytes nor supplies a capability, claim, exact tracked archive
target, or operation-time authority for this now-different source file.

## Loyal Opposition Review Requested

Review this strict-valid replacement proposal and issue a verdict that:

1. rejects any archive/remove action against the current tracked version 007;
2. preserves source-thread versions 007–009 unchanged;
3. records that the original 2,103-byte durability gap cannot be repaired by
   substituting later bytes;
4. requires any future recovery proposal to identify an authentic surviving
   copy of the original payload, or to preserve an explicit evidence-loss
   finding without fabricating byte recovery; and
5. does not treat any resulting `NO-ACTION` as implementation, closure, deferral,
   withdrawal, terminal verification, or authorization to mutate either thread.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Prior Deliberations

- `DELIB-202666766` directs tracked in-root archive preservation and does not
  authorize substituting unrelated later bytes for a missing payload.
- `DELIB-202667001` records that a gitignored archive does not durably preserve
  the original bytes.
- `DELIB-202667150` requires live-state and finalization-ready proof rather than
  archive presence alone.
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` rejects broad or
  identity-ambiguous file movement in favor of exact per-item disposition.

## Owner Decisions / Input

No new owner decision is required. Existing owner direction requires
append-only evidence, exact source identity, tracked archive preservation, and
bounded per-thread repair. This proposal applies those decisions and requests
no implementation or destructive action. The owner-directed TAFE/dispatcher
repair hold remains unchanged.

## Specification-Derived Verification

| Requirement | Executed evidence | Observed result |
| --- | --- | --- |
| Exact source freshness and provenance | File length/hash, first-line status, scoped Git status, index, and history for source version 007 | Current file is a tracked clean 12,041-byte GO, not the 2,103-byte residue. |
| Append-only bridge authority | Full source-thread versions 007–009 and current child versions 001–006 | Versions 008 and 009 depend on current version 007; deletion would break ancestry. |
| Archive durability | Exact-path search for the historical per-file archive and authentic original-hash copies | Historical per-file archive is absent; no authentic current payload was established. |
| Project authorization non-bypass | Current WI/PAUTH readback and targetless proposal scope | No PAUTH is treated as authority to delete or manufacture identity. |
| NO-ACTION semantics | The source `NO-GO`, targetless replacement scope, and requested independent verdict | Any resulting `NO-ACTION` rejects the defective LO verdict and grants no implementation authority. |
| Timer/concurrency standing directive | Evidence scan for a timer or contention failure in this review | None observed; no timer WI or concurrency Advisory is created here. |
| Mandatory bridge gates | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi5318-missing-targets-governance-disposition --content-file <candidate> --json`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi5318-missing-targets-governance-disposition --content-file <candidate>` | Applicability passed with no missing required/advisory specs or blocking errors; clause preflight passed with zero evidence gaps and zero blocking gaps. |

## Pre-Filing Preflight

- Candidate applicability preflight: exit `0`; no missing required/advisory
  specifications and no blocking errors.
- Mandatory ADR/DCL clause preflight: exit `0`; zero evidence gaps and zero
  blocking gaps.
- The governed writer repeats compliance and role/claim checks against final
  content before creating the numbered file.

## Non-Impairment And Rollback

This is a targetless replacement proposal. It preserves both bridge chains, every current
source byte, the staged/index state, MemBase, and all infrastructure state.
Rollback is unnecessary because no implementation state changes. The numbered
proposal remains append-only review evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
