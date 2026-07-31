REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

# WI-5460/WI-5465 Revised Proposal - Exact shared-file sequencing

bridge_kind: prime_proposal
Document: gtkb-wi5460-wi5465-canonical-spec-existence-gates
Version: 005
Responds to: bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-004.md
Carries forward proposal: bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-003.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5460
Work Item: WI-5465
included_work_item_ids: ["WI-5460", "WI-5465"]

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_implementation_authorization_spec_existence.py"]

implementation_scope: source | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

---

## Revision Claim

Version 004's two blocking sequencing findings are accepted. No source or
test byte has changed under WI-5460/WI-5465.

The canonical specification-existence design, four target paths, active
PAUTH, specification links, requirement-sufficiency conclusion, and
specification-derived verification plan remain those in version 003.
This revision changes only the implementation-readiness contract so it names
every current owner of the two dirty applicability-preflight files and
requires a clean committed baseline after their focused finalization.

Implementation may not begin until all of these conditions hold:

1. `gtkb-wi5403-declared-applicability-target-scope` is independently
   VERIFIED and its declared-target hunks are hunk-finalized without adopting
   WI-5387 or WI-5408 bytes.
2. WI-5502 repairs and focused-finalizes the untracked WI-5387 bridge chain
   and its operative-version source/test hunks. MemBase `stage=resolved` or
   the existing malformed terminal verdict alone does not satisfy this gate.
3. `gtkb-wi5408-pauth-amendment-owner-evidence-applicability` completes
   implementation, independent VERIFIED, and focused finalization from a
   clean post-WI5403/WI5502 baseline.
4. All four WI-5460/WI-5465 targets are clean in Git and have no active
   foreign claim, implementation-start packet, non-terminal peer report, or
   uncommitted terminal peer ownership.

This is strict sequence, not scope absorption. WI-5460/WI-5465 does not
repair, remove, rewrite, stage, finalize, or claim any WI-5387, WI-5403,
WI-5408, or WI-5502 byte or artifact.

## Findings Addressed

### Finding 1 - WI-5387 is terminal in MemBase but not finalized in Git

Accepted. The clearing condition is corrected from narrative "terminal
disposition" to governed repair and focused finalization through WI-5502.

Canonical evidence:

- `bridge/gtkb-wi5387-applicability-corrected-go-operative-004.md` is the
  existing terminal verdict whose metadata/finalization defect requires
  repair.
- MemBase WI-5502 is the dedicated remediation work item.
- Neither record makes the two shared files clean by itself; exact Git
  cleanliness and commit provenance are required after finalization.

### Finding 2 - WI-5408 is an open owner of the same source/test surface

Accepted. WI-5408 is now explicit and must complete before this proposal.

Canonical evidence:

- `bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-005.md`
  is the current GO for its source/test correction.
- Its GO requires a clean baseline and therefore follows focused WI-5403 and
  WI-5502 finalization.
- WI-5460/WI-5465 begins only after WI-5408 reaches independent VERIFIED and
  focused finalization.

### Additional current owner - WI-5403

The live shared-file inventory also includes
`bridge/gtkb-wi5403-declared-applicability-target-scope-005.md`, a revised
implementation report that explicitly separates its hunks from WI-5387 and
WI-5408. This revision brings that owner into the same sequence so no
currently known shared-file work is omitted.

## Exact Sequencing

The required order is:

`WI-5403 focused finalization -> WI-5502/WI-5387 repair and focused
finalization -> WI-5408 implementation/VERIFIED/focused finalization ->
WI-5460/WI-5465 implementation`

Each transition fails closed on:

- dirty or untracked predecessor paths;
- absent terminal commit provenance;
- an active foreign claim or implementation packet;
- hash drift from the predecessor's terminal evidence;
- whole-file staging that would absorb another owner's hunks; or
- any target outside this proposal's four-path PAUTH.

No owner sequencing choice remains unresolved: this order preserves the
existing approved WI-5408 clean-baseline condition and gives each earlier
owner a non-overlapping terminal path before this later proposal starts.

## Requirement Sufficiency

Existing requirements sufficient.

The underlying defect remains missing canonical-specification existence
enforcement at proposal applicability and implementation start. This
sequencing correction introduces no new product or governance requirement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded carrier while preserving every downstream gate.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` supplies the mechanically
  reviewable proposal structure carried forward from version 003.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` limits this revision
  to canonical MemBase, Deliberation Archive, and numbered bridge authority.
- The numbered WI-5387, WI-5403, and WI-5408 bridge chains plus MemBase
  WI-5502 are the canonical shared-ownership records for this correction.

## Owner Decisions / Input

No new owner decision is required.

The existing PAUTH continues to authorize only WI-5460/WI-5465 and the four
declared source/test paths after independent GO, exact claim, and schema-v3
implementation start. It grants no authority over the predecessor threads.
The build-envelope case-specific mutation gate therefore remains unsatisfied
until this revised proposal receives a fresh independent GO after the
predecessor sequence is complete.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5460; WI-5465; WI-5502; bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-004.md",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; DCL-PROJECT-DEPENDENCY-ORDERING-001; GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "Finalize each shared-file owner in exact order, require a clean committed four-target baseline, then start the canonical-specification existence correction.",
  "before_behavior": "The proposal named only WI-5387 terminal disposition and could mistake resolved MemBase state for committed byte ownership while omitting WI-5403 and WI-5408.",
  "after_behavior": "WI-5403, WI-5502/WI-5387, and WI-5408 each complete focused finalization before WI-5460/WI-5465 may claim or mutate the shared files.",
  "self_descriptive_naming": "predecessor_finalization_sequence, clean_shared_target_baseline, and foreign_owner_clearance describe the implementation gate.",
  "obsolete_guidance_disposition": "Version 003's terminal-WI5387-only disclaimer is replaced by exact commit-based clearance for all known owners.",
  "history_preservation": "Every predecessor bridge chain, MemBase record, focused commit, and dirty-byte ownership remains intact and separately attributable.",
  "baseline": {
    "dirty_targets": [
      "scripts/bridge_applicability_preflight.py",
      "platform_tests/scripts/test_bridge_applicability_preflight.py"
    ],
    "known_owners": [
      "WI-5387 via WI-5502",
      "WI-5403",
      "WI-5408"
    ]
  },
  "expected_result": "All four WI-5460/WI-5465 targets are clean and predecessor-finalized before claim/start, then only the canonical-specification existence feature is added.",
  "rollback": {
    "instructions": "Revert only the eventual focused WI-5460/WI-5465 commit after separate governance.",
    "verification": "Predecessor commits and bridge histories remain unchanged and no shared-file owner is reset."
  },
  "hard_invariants": [
    "No predecessor byte or bridge artifact is adopted, removed, rewritten, staged, or finalized by WI-5460/WI-5465.",
    "No whole-file staging over shared dirty targets.",
    "No implementation before clean Git state and terminal focused provenance for WI-5403, WI-5502/WI-5387, and WI-5408.",
    "No dispatcher configuration/runtime, TAFE, harness, credential, external, deployment, release, or push action.",
    "Only the four declared targets may change after fresh GO, claim, and schema-v3 start."
  ],
  "fail_closed_conditions": [
    "Any predecessor thread is non-terminal or unfinalized.",
    "Any declared target is dirty, untracked, foreign-claimed, or hash-ambiguous.",
    "Commit provenance does not isolate each predecessor's hunks.",
    "A new shared-file owner appears before implementation start.",
    "Focused tests, static checks, applicability preflight, or clause preflight fails."
  ],
  "essential_context_preservation": "The implementation report must record predecessor terminal paths and commits, clean-baseline hashes, claim/start evidence, exact WI-5460/WI-5465 hunks, test results, and post-report ownership state."
}
```

## Specification-Derived Verification Plan

Version 003's complete functional matrix is carried forward. Before any
functional test, the implementation-start evidence must additionally prove:

| Sequencing invariant | Verification | Required result |
|---|---|---|
| WI-5403 focused finalization | Read its terminal numbered verdict and focused commit provenance | Only declared-target hunks landed; WI-5387/WI-5408 bytes remained separate. |
| WI-5502/WI-5387 repair | Read MemBase WI-5502 plus repaired terminal bridge and focused commit provenance | The malformed/untracked WI-5387 chain is repaired and operative-version hunks are committed. |
| WI-5408 completion | Read its terminal numbered verdict and focused commit provenance | PAUTH-amendment validation is independently VERIFIED and committed from a clean baseline. |
| Clean WI-5460/WI-5465 start | `git status --short -- <four target paths>` plus claim/start validation | No dirty/untracked target, foreign claim, or non-terminal peer owner remains. |
| Functional behavior | Run both focused pytest modules, Ruff check/format, `py_compile`, `git diff --check`, applicability preflight, and mandatory clause preflight | Canonical specification existence fails closed at both layers with no regression or blocking gate. |

## Pre-Filing Preflight Subsection

Both mandatory preflights were run against this completed revision:

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5460-wi5465-canonical-spec-existence-gates-005.md`
  - PASS: `preflight_passed: true`; all four declared targets resolved; no
    missing required or advisory specifications; no blocking errors.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5460-wi5465-canonical-spec-existence-gates-005.md`
  - PASS: five clauses evaluated; three `must_apply`; zero evidence gaps and
    zero blocking gaps.

## Risk And Rollback

The principal risk is misattributing shared working-tree bytes. Exact
predecessor order, focused finalization, and a clean four-target start are
mandatory. Any ambiguity blocks work rather than broadening ownership.

Rollback remains a separately governed focused revert of only the eventual
WI-5460/WI-5465 commit. It must not reset shared files or disturb any
predecessor commit, bridge chain, or MemBase record.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
