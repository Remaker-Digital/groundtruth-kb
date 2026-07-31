REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5368-codex-git-window-command-family
Version: 015
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-014.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]
implementation_scope: exact_postimage_recovery_and_atomic_finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5368 PAUTH-v3 Exact-Postimage Recovery And Finalization Proposal

## Revision Claim

This revision accepts the v014 NO-GO and resolves its sole authority blocker
through an owner-approved whole-project amendment. Active Harness Parity PAUTH
version 3, MemBase row 943, removes only `git_commit` from the prior forbidden
operations. The owner decision is captured as `DELIB-202667709`. No per-work-
item exception is requested or controlling.

The already completed, unstaged two-file postimages are preserved exactly. This
revision authorizes no new source or test mutation. It requests independent
review of a recovery sequence that binds those exact bytes to PAUTH v3, a fresh
GO, a fresh work-intent claim, and a new schema-v3 implementation-start packet
before a corrected implementation report is published. The v012 GO, its
expired start packet, and the v013 scratch report remain historical evidence
only and must not be reused as current authority.

## Findings Addressed

### V014-F1 - Whole-project commit authority was absent

Resolved. The owner approved Harness Parity PAUTH v3 and the canonical project
authorization writer appended active version 3 at row 943. Version 3 preserves
the project scope, allowed mutation classes, included specifications, list-free
active-member inheritance, and all normal bridge/start/verification gates. It
removes only `git_commit` from `forbidden_operations`.

### V014-F2 - A fresh LO response and fresh claim/start are mandatory

Accepted without relaxation. V015 is a proposal, not an implementation report.
No claim is currently held and no valid WI-5368 implementation-start packet
exists. A new independent GO must respond to this exact v015 content before a
`go_implementation` claim or schema-v3 start packet is acquired.

### V014-F3 - Completed bytes must be preserved without an authority bypass

Satisfied by freezing both the clean HEAD preimages and current unstaged
postimages below. No protected-file write, staging action, commit, report
publication, dispatcher/TAFE action, push, release, deployment, or external
mutation has occurred after v014. Any cohort drift requires another append-only
revision rather than an in-place repair or broad reset.

## Exact Frozen Recovery Cohort

Both targets are worktree-modified and unstaged. The index entries remain the
clean HEAD blobs.

| Target | Clean HEAD / index blob | Clean raw SHA-256 | Current postimage blob | Current raw SHA-256 | Numstat |
| --- | --- | --- | --- | --- | --- |
| `scripts/ops/codex_snapshot_window_hider.py` | `4b0ed05225b161bd582e53489c393a2b5a7693e9` | `a8f6169e51cb1e40796a764a6a6596f183541139a29dd0d44aff84a29b1a677c` | `cc1923054d9bb82c6cb6314093af7595385836d5` | `88bffc35e4ab9a9a18b243cc35993c086276c3add8ccb22326b87ffea0a18bc1` | `+42/-14` |
| `platform_tests/scripts/test_codex_snapshot_window_hider.py` | `309f56fa9f7f499815628281c27ccd2890cef13d` | `83ca43cf6cb140b08bb4def269c18ac6641193b618b1be21cba24d0b4223cda6` | `8b5ac667b48519d96e3c716dd83f78acae931c8b` | `bb93f56aa55689002c470080094c0213313f5f16359895f2e1d79800caf7a20a` | `+151/-8` |

The binary Git diff is 11,279 bytes with SHA-256
`972ecddda39ef764c7d438607541ef1ee3a5b44f7c40bb245dc3e93c46360936`.
Any preimage, postimage, diff digest, index state, target path, HEAD, claim,
project membership, project authorization, or bridge-frontier drift is a hard
stop requiring an append-only REVISED response.

## Project-Only Authorization

WI-5368 is an active member of
`PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY`. The active list-free
whole-project authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE`,
version 3, row 943, owner decision `DELIB-202667709`. Work-item
`approval_state` compatibility metadata neither grants nor revokes authority.

PAUTH v3 continues to forbid `credential_lifecycle`, `destructive_cleanup`,
`dispatcher_mutation`, `external_system_mutation`, `git_history_rewrite`,
`git_push`, `production_deployment`, and `release`. Raw staging, manual bridge
writes, manual commit, push, deployment, release, dispatcher/TAFE mutation,
harness mutation, role mutation, and direct external-system mutation remain
outside this proposal. Only the governed exact atomic finalizer may stage and
commit the independently reviewed cohort after operation-time validation.

Project authorization does not replace the independent GO, claim,
implementation-start, applicability, clause, specification-derived testing,
independent verification, or terminal finalization gates.

## Requirement Sufficiency

**Existing requirements are sufficient.** The active nonimpairment,
harness-parity, project-authorization, bridge-authority, source-of-truth
freshness, worktree-hygiene, and spec-derived-verification requirements fully
determine this exact-postimage recovery. No new or revised requirement is
needed before the fresh review.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667709` records the owner's exact Harness Parity PAUTH v3
  approval and supports project authorization version 3 at row 943.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establishes that
  implementation approval belongs to the project and active member work items
  inherit it; orphan work items cannot implement.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` retires per-work-item
  approval as controlling authority.
- `DELIB-202666274` is the prior whole-project Harness Parity authority. PAUTH
  v3 changes only the local-commit prohibition; it does not widen technical
  scope or waive any lifecycle gate.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` requires nonimpairing background
  window containment.

## Owner Decisions / Input

The exact owner reply `Approve Harness Parity PAUTH v3` is captured as
`DELIB-202667709` and materialized as active project authorization version 3,
row 943. No further owner decision is requested for this exact recovery.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5368 v011/v012 reviewed design, exact preserved v015 postimage cohort, and fresh 42-test evidence","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact ChatGPT/conhost ancestry plus exact singleton Codex internal Git-manager markers","before_behavior":"Only the historical add -u form is recognized, so other marker-qualified internal Git commands may surface visible consoles.","after_behavior":"Observed marker-qualified Codex internal Git-manager consoles are hidden while every Git command continues and exits naturally.","self_descriptive_naming":"The matcher and tests describe qualifying Codex Git provenance rather than one historical subcommand.","obsolete_guidance_disposition":"The broader argument-independent sibling design remains explicitly superseded and is not adopted.","history_preservation":"The append-only v011-v015 chain, retired sibling artifacts, clean preimages, and frozen postimages remain intact.","baseline":{"source_blob":"4b0ed05225b161bd582e53489c393a2b5a7693e9","test_blob":"309f56fa9f7f499815628281c27ccd2890cef13d","source_postimage_blob":"cc1923054d9bb82c6cb6314093af7595385836d5","test_postimage_blob":"8b5ac667b48519d96e3c716dd83f78acae931c8b"},"expected_result":{"focused":"all 42 marker-family and near-miss tests pass","live":"qualifying consoles are hidden while commands complete naturally"},"rollback":{"instructions":"use a separately governed exact two-file repair","verification":"focused near-miss suite plus exact postimage and live-observation checks"},"hard_invariants":["hide only","no process-lifecycle action","no Git interception","no dispatcher or TAFE mutation","fail open on ambiguity"],"fail_closed_conditions":["required markers made optional","nested Git ancestry accepted","arbitrary Git consoles hidden","process or dispatcher state changed","target or authority drift detected"],"essential_context_preservation":"Retain exact event, process, marker, singleton, project-authorization, bridge-frontier, and nonimpairment evidence."}
```

## Recovery And Atomic Finalization Sequence

1. Loyal Opposition independently reviews v015 and files a fresh GO.
2. Prime Builder confirms the v015/v016 frontier, exact postimage cohort,
   active project membership, PAUTH v3, claim availability, and clean target
   index state.
3. Prime Builder acquires a fresh `go_implementation` claim and finalizes a
   schema-v3 implementation-start packet bound to v015, the new GO, PAUTH v3,
   and the exact two postimages. No source/test edit is performed.
4. Prime Builder reruns the focused tests, Ruff checks, diff checks, exact hash
   checks, and current-authority checks, then rebuilds the v013 scratch report
   as a new implementation report with only current claim/start/PAUTH evidence.
5. Loyal Opposition independently reviews the report. Terminal acceptance must
   use the governed atomic finalizer to bind the exact source, test, report,
   verdict, and commit. The finalizer may stage only that reviewed cohort after
   its own operation-time checks.

No old claim, start packet, report metadata, GO, or scratch artifact is current
authority for steps 3 through 5.

## Specification-Derived Verification Plan

| Governing requirement | Evidence before report publication | Required result |
| --- | --- | --- |
| Project-only authorization and current authority | Project membership, PAUTH v3 row 943, fresh independent GO, fresh claim, schema-v3 start packet | Exact v015/v016 cohort is allowed at operation time; no WI-local approval is consulted. |
| Frozen postimage integrity | HEAD/index blobs, current Git blobs, raw SHA-256 values, binary-diff digest, numstat, and scoped status | Every recorded identity matches and neither target is staged before the governed finalizer. |
| Marker-qualified command coverage | `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short` | All 42 focused tests pass, including observed command families and rejection cases. |
| Near-miss isolation and hide-only nonimpairment | Focused malformed/provenance tests plus static source assertions | Missing, duplicate, malformed, unrelated, nested-Git, and ambiguous forms remain untouched; `ShowWindowAsync(SW_HIDE)` remains the sole target-window/process effect. |
| Code quality and scope | Ruff check, Ruff format check, `git diff --check`, exact two-target diff | All checks pass and no third path enters the implementation cohort. |
| Terminal integrity | Independent report verdict and exact atomic finalizer | Only the reviewed cohort is committed; no foreign staged bytes, manual commit, push, dispatcher/TAFE mutation, release, or deployment occurs. |

Fresh read-only evidence before v015 filing: 42 of 42 focused tests passed; Ruff
check passed; Ruff format check passed; `git diff --check` passed; both recorded
postimage Git blobs matched; and both files remained unstaged.

## Acceptance Criteria

1. A new independent GO approves this exact v015 recovery and finalization
   sequence under active project PAUTH v3.
2. Before any implementation report, a fresh `go_implementation` claim and
   schema-v3 start packet bind the exact v015/v016 frontier, PAUTH v3, active
   project membership, and two preserved postimages.
3. No source or test edit occurs during recovery. Any byte, index, HEAD,
   authority, frontier, claim, or target-cohort drift stops the attempt and is
   disclosed through another append-only revision.
4. The rebuilt implementation report carries only current PAUTH v3,
   claim/start, exact-hash, test, and scope evidence; it does not reuse the
   expired v012 packet or v013 scratch metadata as authority.
5. Independent review verifies the marker-qualified behavior, near-miss
   isolation, hide-only nonimpairment, exact target cohort, and complete
   specification-derived testing.
6. Terminal publication and local commit are one governed atomic operation over
   only the reviewed source, test, implementation report, and verdict cohort.
   Git push, release, deployment, history rewrite, dispatcher/TAFE mutation,
   credential action, destructive cleanup, and external mutation remain
   prohibited.

## Pre-Filing Preflight Subsection

The completed v015 candidate must pass the live applicability and mandatory
ADR/DCL clause preflights with authoritative PB metadata, no missing required
or advisory specifications, no unclassified target, and no blocking clause
gap. The governed writer must confirm that v014 is still the latest consumed
thread status and publish a receipt bound to the exact v015 bytes. Any failure
aborts publication without a manual write.

## Risk And Rollback

The primary technical risk is that preserved dirty bytes drift before a fresh
start or review. Exact hashes and fail-closed cohort checks contain that risk.
The primary concurrency risk is foreign staged work entering an atomic
finalizer; the finalizer must refuse any noncohort index entry rather than
commingling it. The functional residual risk remains a future Codex command
shape lacking both required markers; fail-open behavior leaves that console
visible rather than hiding an unrelated process.

Rollback before finalization is preservation plus another append-only bridge
revision. After an authorized commit, rollback is a separately governed exact
two-file repair. No broad reset, checkout, revert, process termination,
history rewrite, dispatcher/TAFE mutation, manual bridge write, push, release,
or deployment is authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
