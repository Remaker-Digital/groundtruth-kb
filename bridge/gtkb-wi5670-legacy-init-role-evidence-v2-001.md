NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop; goal-continuation=true
author_metadata_source: x-codex-turn-metadata

# WI-5670 v2 - bounded legacy init-role evidence

bridge_kind: prime_proposal
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

KB Mutation: This proposal performs no MemBase mutation.

## Claim

Complete the forward-only legacy-provenance repair without retroactively
adopting the pre-GO source/test commit. A canonical historical bridge version
whose `author_identity` is present but roleless MAY use one exact canonical
header line, `::init gtkb pb` or `::init gtkb lo`, as supplemental session-role
evidence. Such a version remains `legacy`, never `strict`, and cannot become an
operative implementation proposal, operative GO, or operative corrected-tail
artifact.

The change MUST continue to reject a missing init, duplicate or ambiguous init,
body-only init text, a role/status contradiction, and every recognized explicit
author-role contradiction. It MUST NOT consult harness registry role, harness
identity, model/vendor identity, shared envelope state, or any retired
harness-role GOV.

## Prior-Thread And Existing-Byte Disposition

The original thread
`gtkb-wi5670-resolver-legacy-provenance-tolerance` ends at NO-GO version 008.
That verdict found that the already-present missing-`author_identity` tolerance
and its tests entered broad pre-GO commit
`db07f9dcfe7e7de8addc850729209278472cb0fe`; a later GO cannot reattribute those
bytes. This v2 thread accepts that finding and does not claim, ratify, stage, or
finalize those existing bytes.

The current HEAD baseline is `8317c8b17d00967b7b272d392d148e96fda3b886`.
At proposal time both target paths are clean. Their HEAD blob IDs are:

- `scripts/bridge_lifecycle_resolver.py`:
  `47d7ad8abff406617273be890ded49797d29cfb0`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
  `61afc0daa328d769bdf709e6a8fa88c4bc300ede`

`DELIB-20260724-WI5640-REPAIR-FORWARD` preserves `db07f9dc` as incident
evidence and forbids history rewrite. This proposal therefore authorizes only
the new incremental init-role fallback and its new tests relative to the two
blob IDs above. The old NO-GO chain remains immutable evidence.

## Defect And Deterministic Reproduction

`scripts/bridge_lifecycle_resolver.py::_author_role` recognizes role-bearing
identities such as `prime-builder/codex` and `loyal-opposition/claude`. Hundreds
of older files instead carry a vendor-only value such as
`author_identity: codex`. `_parse_version` treats that present-but-roleless value
as strict input, calls `_validate_author_role(..., None)`, and raises
`WRONG_STATUS_AUTHOR_ROLE` before the lifecycle can reach a later strict
proposal and GO.

Two current chains prove both sides of the required boundary:

1. `gtkb-wi5667-scaffold-managed-skill-rename-recovery-001.md` is `NEW`, has
   `author_identity: codex`, and has exact header `::init gtkb pb`. Versions 003
   and 004 are strict `REVISED -> GO`. The current resolver rejects version 001;
   after this change version 001 is tolerated as non-operative legacy and the
   strict 003/004 pair remains the only implementation authority.
2. `gtkb-wi5668-skill-rename-sweep-completion-gate-001.md` is `NEW`, has
   `author_identity: codex`, but has exact header `::init gtkb lo`. That is a
   real role/status contradiction. The current and proposed resolver both MUST
   reject it with `WRONG_STATUS_AUTHOR_ROLE`.

A deterministic whole-bridge scan of exact numbered files at this proposal
baseline found 573 canonical-status versions with one roleless
`author_identity`:

- 55 have exactly one header init whose role matches the status;
- 57 have exactly one header init whose role contradicts the status;
- 461 have no canonical header init;
- 0 have multiple canonical header init lines.

Machine-readable proposal-baseline counts:

- `matching_roleless_header_init: 55`
- `mismatching_roleless_header_init: 57`
- `missing_header_init: 461`
- `ambiguous_header_init: 0`

Only the 55 matching non-operative versions become tolerable. The 57
contradictions and 461 no-evidence files remain rejected. No file is rewritten
or backfilled.

## Exact Design

### Header-only init parser

Add a private helper in `scripts/bridge_lifecycle_resolver.py` that:

1. examines only the bridge envelope header after physical line one and before
   the first Markdown H1 line;
2. recognizes only a full-line canonical `::init gtkb pb` or
   `::init gtkb lo` command;
3. maps `pb` to `prime-builder` and `lo` to `loyal-opposition`;
4. returns no evidence when no exact header command exists;
5. fails closed with a stable diagnostic when more than one exact header init
   command exists, including repeated identical commands; and
6. never searches body prose, code fences, headings, comments, harness files,
   session projections, registry role maps, or environment defaults.

### Parse classification

Preserve the current missing-`author_identity` behavior unchanged. When
`author_identity` is present and `_author_role(author_identity)` returns a
recognized role, preserve the existing strict path and do not allow init text
to override it.

Only when `author_identity` is present but `_author_role(...)` returns `None`:

1. read the bounded header init role;
2. run the existing `_validate_author_role` status/role check;
3. fail with the existing `WRONG_STATUS_AUTHOR_ROLE` when evidence is missing
   or contradictory; and
4. when it matches, return `classification="legacy"`, preserving the original
   `author_identity` and recording the derived `author_role` for transition
   validation.

### Operative-authority backstop

The ordinary lifecycle already rejects any `is_legacy` operative proposal or
GO with `OPERATIVE_VERSION_MISSING_PROVENANCE`; preserve and extend that test
coverage.

The malformed-correction path currently checks roles but does not separately
check `is_legacy`. Because the new matching fallback records a derived role,
that path MUST add explicit strict/non-legacy checks for its Prime predecessor,
Prime `NO-ACTION`, and corrected LO verdict before any of them can provide
review or implementation authority. A role-matching legacy value therefore
cannot slip through the correction-tail path.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provenance is forward-only; historical
  files may be grandfathered without backfill, while new files remain complete.
- `DCL-SESSION-ROLE-RESOLUTION-001` - a canonical init role is explicit session
  evidence; registry role is not non-dispatcher behavior authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered files remain the append-only audit
  chain; malformed, conflicting, or unreadable required state fails closed.
- `GOV-RELIABILITY-FAST-LANE-001` - this is a two-file bounded defect fix under
  the standing Reliability Fixes authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
  each governing requirement to concrete verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification must
  execute every acceptance row below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and exact target paths are declared above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the rejected old thread and fresh v2
  proposal remain durable, explicit lifecycle evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair is expressed as a bounded
  proposal and executable tests rather than an implicit reinterpretation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the old NO-GO remains terminal for its
  thread and this separately named v2 proposal starts a fresh lifecycle.
- `GOV-STANDING-BACKLOG-001` - WI-5670 remains the single durable work owner.

No current requirement needs amendment. This proposal does not cite or depend
on retired `GOV-SESSION-ROLE-AUTHORITY-001`.

## Prior Deliberations

- `DELIB-20260724-WI5640-REPAIR-FORWARD` - preserve `db07f9dc` and repair
  forward; do not rewrite history or treat the mixed commit as authorization.
- `DELIB-202667497` - independent WI-5670 review history; confirms the original
  design and records the pre-GO implementation-provenance failure.
- `DELIB-20260683` - author-provenance contract review establishing forward-only
  grandfathering.
- `DELIB-20261032` - document author-provenance gap advisory.
- `DELIB-20265226` - explicit interactive transcript role persists within its
  exact session context.
- `DELIB-20265878` - harness registry role is dispatcher authority only, not a
  non-dispatcher behavior-role source.
- `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-008.md` - controlling
  NO-GO for the old chain and source of this fresh incremental strategy.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-001.md` through
  `-004.md` - matching-init positive production fixture.
- `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-001.md` - wrong-init
  negative production fixture.

## Owner Decisions And Input

Existing requirements and owner decisions are sufficient. The proposal uses the
active Reliability Fixes standing PAUTH and follows the owner's repair-forward
decision. It does not request ratification of the old bulk commit, reinterpret
wrong-role evidence, or widen owner authority. No new owner decision is needed.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, and `GOV-FILE-BRIDGE-AUTHORITY-001` define
the complete required outcome: forward-only historical tolerance, explicit
session-role evidence, and fail-closed operative authority. This proposal makes
the resolver conform to those current requirements and creates no new policy.

## Specification-Derived Verification Plan

| Requirement / invariant | Executable verification | Required result |
| --- | --- | --- |
| Forward-only matching legacy evidence | New unit fixture: roleless `NEW` with header `::init gtkb pb`, later strict `NO-GO -> REVISED -> GO` | Resolves; old version is `legacy`; strict revised/GO pair alone is operative |
| Matching LO history | New unit fixture: roleless non-operative `NO-GO` with `::init gtkb lo` | Resolves as legacy history |
| Wrong role fails closed | New fixtures for `NEW + ::init ... lo` and `GO + ::init ... pb` | `WRONG_STATUS_AUTHOR_ROLE` |
| Missing/ambiguous evidence fails closed | New fixtures for no header init and duplicate header init | Existing wrong-role error for missing; stable ambiguity error for duplicate |
| Body text is not authority | New fixture places matching init only after first H1 | Rejected; body prose cannot supply role |
| Explicit identity cannot be overridden | Strict recognized LO identity on `NEW` plus PB init | `WRONG_STATUS_AUTHOR_ROLE` |
| Ordinary operative pair remains strict | Roleless proposal or GO with matching init | `OPERATIVE_VERSION_MISSING_PROVENANCE` |
| Correction-tail authority remains strict | Roleless matching-init predecessor, `NO-ACTION`, and corrected verdict fixtures | Each rejected before authority is returned |
| Positive production chain | Resolve `gtkb-wi5667-scaffold-managed-skill-rename-recovery` | Strict-valid result; operative versions 003/004 |
| Negative production chain | Resolve `gtkb-wi5668-skill-rename-sweep-completion-gate` | Still `WRONG_STATUS_AUTHOR_ROLE` at version 001 |
| Existing behavior | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short` | Entire focused suite passes |
| Static quality | Ruff check and Ruff format check on both targets; `git diff --check` | Pass |
| Scoped implementation | Compare final diff to the two proposal-time blob IDs and inspect staged/finalized path sets | Only the incremental fallback and tests; exactly two target paths |
| Proposal gates | Applicability and ADR/DCL clause preflights against this exact file | Pass; zero blocking gaps |

## Implementation Sequence

1. After independent GO, acquire an exact-session WI-5670 work-intent claim and
   implementation-start packet for the two target paths.
2. Re-verify both proposal-time blob IDs. If either differs, stop and re-review;
   do not merge concurrent changes silently.
3. Implement only the parser fallback, legacy classification, correction-tail
   strictness backstop, and listed tests.
4. Run the complete focused suite, the two production-chain probes, Ruff, format,
   and whitespace checks.
5. File a post-implementation `NEW` report that discloses the old pre-GO baseline
   separately from the new incremental diff.
6. Require independent terminal verification and scoped finalization. Do not
   include or attribute unrelated bridge, source, test, registry, or database
   paths.

## Acceptance Criteria

1. Exactly the 55 corpus versions with one role-matching canonical header init
   are eligible for non-operative legacy tolerance at the captured baseline.
2. The 57 role/status contradictions and 461 no-init versions remain rejected;
   body prose and duplicate commands cannot become role authority.
3. No legacy version can become an operative ordinary or corrected-tail proposal,
   GO, `NO-ACTION`, or corrected verdict.
4. WI-5667's recovery chain resolves to strict operative versions 003/004;
   WI-5668's wrong-role version 001 remains rejected.
5. Current missing-identity grandfathering, strict author-role validation,
   transition validation, and malformed-correction behavior do not regress.
6. The implementation changes exactly the two declared target paths relative to
   their recorded proposal-time blob IDs.
7. No bridge history is rewritten, no MemBase/spec/registry record is mutated,
   and no harness registry or retired GOV is consulted as role authority.

## Risks And Rollback

The principal risk is converting incomplete provenance into implementation
authority. Mitigations are the header-only grammar, existing status/role check,
legacy classification, ordinary operative-pair rejection, new correction-tail
strict checks, production negative fixture, and no registry fallback.

The secondary risk is accidentally absorbing later edits to these shared files.
The implementation-start preimage check and proposal-time blob IDs make that a
visible conflict. Rollback is one scoped revert of the two WI-5670 v2 hunks;
historical bridge files and the existing missing-identity baseline remain
untouched.

## Files Expected To Change

- `scripts/bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`

## Explicit Exclusions

No bridge-file rewrite, historical backfill, MemBase mutation, specification
mutation, registry mutation, hook/config/rule/skill change, dispatcher change or
activation, worktree launch, Git push, history rewrite, deployment, release,
credential work, destructive cleanup, or WI-5640 file migration is authorized.

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
