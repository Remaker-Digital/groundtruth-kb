REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Bridge Lifecycle Resolver — Narrow Legacy Author-Provenance Tolerance

bridge_kind: prime_proposal
Document: gtkb-wi5670-resolver-legacy-provenance-tolerance
Version: 007
Responds to: bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-006.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]

## Revision Claim

This revision selects the narrow author-provenance-only correction allowed by
version 006. It removes every claim that WI-5670 will unblock WI-5152 and keeps
all `Document`, `Version`, and `Responds to` structural validation strict.
Missing or wrong historical linkage remains fail-closed and must be routed as
separate governed work.

No source mutation or staging is authorized by this revision. Any prior GO,
claim, or implementation-start packet is superseded by the current NO-GO. A
fresh independent GO, current Prime claim, and successful current-session
implementation-start packet are mandatory before protected effects.

## Finding Response — P1 Author-Only Scope

`bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` lacks both
`author_identity` and `Responds to`; the live resolver therefore rejects it as
`WRONG_RESPONDS_TO_LINK` before author grandfathering. WI-5670 will not change
that result. The real-world WI-5152 unblock command and acceptance criterion
are deleted. A future historical-linkage tolerance would require its own owner
decision and fail-closed linkage design.

The retained behavior is only this: a non-operative historical version with
valid required linkage but missing author provenance may be classified as
legacy, while the selected operative proposal and GO must still carry complete,
role-correct provenance.

## Requirement Sufficiency

Existing requirements are sufficient for the narrowed scope.
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` explicitly grandfathers pre-contract
author metadata; it does not grandfather linkage. No new owner decision is
needed because this revision does not extend that contract.

## Specification Links

- GOV-DOCUMENT-AUTHOR-PROVENANCE-001
- GOV-RELIABILITY-FAST-LANE-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-WORK-TREE-HYGIENE-001

## Prior Deliberations

- `DELIB-20261032` — document author-provenance gap advisory.
- `DELIB-20260683` — forward-only author-provenance grandfathering contract.
- Versions 005 and 006 — establish that WI-5152 also lacks linkage and cannot
  be used as author-only acceptance evidence.
- No owner decision extends grandfathering to historical `Responds to` data.

## Owner Decisions / Input

No owner input is required for this narrowed author-only conformance fix. The
separate missing-linkage question is explicitly outside this proposal.

## Exact Design

1. In `_parse_version`, a canonical-status historical version that has valid
   `Document`, `Version`, and required `Responds to` structure but lacks
   `author_identity` becomes `classification="legacy"` with no author role,
   rather than failing as missing author metadata.
2. `BridgeVersion.is_legacy` identifies only that classification; legacy is
   neither strict nor malformed.
3. Ordinary and correction resolution revalidate the selected operative
   proposal and GO. Either missing author provenance or a wrong operative role
   fails with stable `OPERATIVE_VERSION_MISSING_PROVENANCE`; implementation
   authority never derives from a grandfathered version.
4. All existing missing-link, wrong-link, malformed-link, and version-chain
   checks remain unchanged and fail closed.

## Foreign-Hunk Isolation

Both targets contain pre-existing unrelated `owner_deferred_reproposal` /
`NEW -> REVISED` lifecycle hunks and matching tests. They are read-only foreign
evidence. After GO, implementation must stage only the legacy-author
classification, operative revalidation, `is_legacy`, and new focused test
hunks. Cached and remaining-worktree diffs must prove the foreign hunks remain
unstaged and intact before and after commit.

## Pre-Filing Preflight Subsection

The governed revision helper must run both applicability and mandatory clause
preflights against this completed candidate. Any missing required spec or
blocking gap prohibits filing.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Non-operative author grandfathering | Valid NEW -> legacy NO-GO (missing author, valid `Responds to`) -> REVISED -> GO fixture | Resolves with strict operative REVISED + GO. |
| Legacy classification | Assert `is_legacy` true and `is_malformed` false | Ordinary resolution path is retained. |
| Strict missing linkage | Legacy candidate with `include_responds=False` | `WRONG_RESPONDS_TO_LINK`; no author waiver. |
| Strict wrong linkage | Legacy candidate responding to the wrong predecessor | Stable linkage error; fail closed. |
| Operative provenance | Operative proposal or GO lacks author metadata | `OPERATIVE_VERSION_MISSING_PROVENANCE`. |
| Focused regression | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120` | All existing and new tests pass. |
| Quality | Ruff check and format-check on both targets | Pass on the isolated candidate. |
| Hunk isolation | Cached and unstaged two-path diffs | Only WI-5670 is cached; foreign hunks remain unstaged. |

## Acceptance Criteria

- Only non-operative author metadata is grandfathered.
- Required `Responds to` linkage remains strict for every version.
- Operative proposal and GO provenance remains complete and role-correct.
- No WI-5152 unblock or historical missing-link tolerance is claimed.
- Focused tests and quality gates pass on the isolated candidate.
- Only the two declared WI-5670 hunks are committed; foreign lifecycle hunks
  remain unstaged and intact.
- Independent LO verification determines terminal status.

## Scope Changes

The two target paths and author-provenance design remain unchanged. Compared
with version 003, this revision removes the WI-5152 live-unblock claim and its
acceptance command, adds explicit missing/wrong-link fail-closed coverage, and
states that linkage grandfathering is separate governed work.

## Risk And Rollback

The principal risk is broadening a provenance exception into structural
linkage tolerance. The strict-link tests and operative-pair revalidation prevent
that. Hunk-level staging prevents foreign lifecycle bytes from entering the
commit. Rollback is a separately governed two-file WI-5670 hunk revert and does
not rewrite bridge history or foreign worktree content.

## Recommended Commit Type

fix
