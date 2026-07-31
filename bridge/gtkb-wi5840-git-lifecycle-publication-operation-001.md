NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5840

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_publication.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

# Add a governed one-off branch-publication operation to `groundtruth_kb.git_lifecycle`

## Problem — a valid GO with no runnable path

`bridge/gtkb-wi5802-clean-branch-publication-002.md` is a clean Loyal
Opposition `GO` — *"No blocking proposal defects"*, *"Required Revisions:
None"*. Its approved procedure cannot be executed.

The implementation-start gate refuses direct git effect verbs:

> BLOCKED (GTKB-GIT-LIFECYCLE): direct `git fetch` is not an authorized
> execution boundary. Use the canonical `python -m groundtruth_kb.git_lifecycle`
> operation so current authority, scope binding, quiescence, recovery, and
> evidence are enforced at effect time.

`DIRECT_GIT_READ_ONLY_SUBCOMMANDS` (`scripts/implementation_start_gate.py`)
allows read verbs — `diff`, `log`, `ls-remote`, `ls-tree`, `merge-base`,
`rev-list` and similar — but not `fetch`, `commit-tree`, `update-ref`, or
`push`. Those are steps 2, 4, 6 and 6 of the approved procedure. There is no
bypass environment variable for this gate; it was checked.

The canonical module offers `create`, `attach`, `show`, `validate`,
`preserve`, `promote`, `close`, `resume`, `recover`, `drain`, `maintenance`.
None publishes a one-off branch. Its only push path is
`_continue_pull_request_promotion` in `git_lifecycle/service.py`, reached for
`promotion_kind == "project_to_develop"`, which pushes an existing
work-item/project branch and then opens a pull request. It requires a branch
binding, an immutable scope attachment, and a service-issued promotion
receipt.

WI-5802 has none of those by design: it creates an *unattached* candidate via
`commit-tree` from an exact reviewed tree and pushes it to a brand-new
`codex/publish-*` ref. The gate is correct to block raw git, and the module is
correct not to have a general-purpose push. The defect is the missing verb
between them.

The gate is therefore doing its job, and the result is still an approved,
unconsumable GO. This proposal closes that gap rather than weakening the gate.

## Proposed Change

Add a bounded `publish` operation to the git-lifecycle service and expose it
through the module CLI, implementing exactly the fail-closed sequence Loyal
Opposition already approved in the WI-5802 proposal. Nothing about the
direct-git-effect gate changes; no verb is added to
`DIRECT_GIT_READ_ONLY_SUBCOMMANDS`.

### P1 — service operation

A single operation that performs, in order, stopping before the next side
effect on any failure:

1. **Bind immutable inputs.** Require the declared source commit and its tree
   to resolve exactly; record the `.git/index` byte SHA-256; require the
   expected `origin` URL; disable credential prompting.
2. **One narrow fetch.** Exactly one no-tags, no-submodule fetch of the single
   declared base ref, with automatic maintenance and gc disabled. Resolve the
   sole fetched base. Missing, multiple, ambiguous, or non-commit fetch state
   stops. A cached remote-tracking ref is never accepted as the base.
3. **Prove the target ref is new** locally and remotely. A network or
   authentication error is never treated as absence.
4. **Create one unattached candidate** with `commit-tree` from the exact
   declared tree and the freshly fetched sole parent. Before any ref
   creation require: candidate tree equals declared tree; exactly one parent
   equal to the base; exactly one commit ahead; base is an ancestor; and no
   path delta for any declared-excluded carrier.
5. **Enumerate and size the actual range.** `rev-list --objects BASE..CANDIDATE`
   resolved through `cat-file --batch-check`. Reject an empty range, an
   unresolvable object, an unexpected object type, any declared-excluded path,
   and any `blob` above the declared size ceiling. The ceiling applies to
   blob objects only — never to commit or tree sizes.
6. **Recheck, create one ref, push once.** Immediately before ref creation
   revalidate authority, scope, ref absence, ancestry, exclusions, size gate,
   and the index byte hash. Create only the new local ref with
   compare-and-create semantics, then push only that ref to the same-name
   remote ref: no force, no tags, no deletion, no upstream change, no second
   refspec. A race-created remote ref, non-fast-forward, credential request,
   disconnect, or ambiguous response stops and is reported. No retry is
   inferred.
7. **Record evidence** in the module's existing operation-evidence surface:
   base, candidate, tree, object counts by type, maximum blob size and path,
   ref identities, index hashes, command exits, and timestamps.

The operation reuses the module's existing authority, scope-binding,
quiescence, transaction and recovery machinery rather than introducing a
parallel path, and reuses `validate_remote_push` — which already denies
protected destination branches and any source/destination rename.

### P2 — CLI surface

Expose it as a `publish` subcommand in `git_lifecycle/__main__.py`, consistent
with the existing verbs, taking the declared source commit/tree, base ref,
target ref, excluded paths, and blob-size ceiling as explicit arguments. No
defaults that would let an under-specified invocation publish something.

### P3 — tests

New `platform_tests/scripts/test_git_lifecycle_publication.py` covering each
fail-closed condition individually, plus the success path.

### Explicitly out of scope

- **No change to `DIRECT_GIT_READ_ONLY_SUBCOMMANDS` or the gate.** Widening
  the read-only allowlist was the alternative considered and rejected: it
  would unblock only steps 1–5 and leave the push unrunnable, while
  permanently loosening a boundary for every caller.
- **No general-purpose push.** The operation publishes to a *new* ref only;
  `validate_remote_push`'s existing protected-branch and rename denials
  remain in force.
- **Executing WI-5802 itself.** That remains its own thread under its own
  PAUTH and its own owner authorization for the push. This proposal only
  makes the path exist.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "bridge/gtkb-wi5802-clean-branch-publication-002.md (clean LO GO with no runnable path); DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL; DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1; owner authorization 2026-07-31 selecting a governed publication verb; WI-5840",
  "canonical_authority": "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001; ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001; DCL-GIT-BRANCH-BINDING-PROMOTION-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m groundtruth_kb.git_lifecycle publish --source-commit <sha> --source-tree <sha> --base-ref <ref> --target-ref <ref> --exclude-path <path> --max-blob-bytes <n> --json",
  "before_behavior": "A bounded one-off branch publication has no governed execution path. The implementation-start gate blocks fetch/commit-tree/update-ref/push as direct git effects, and git_lifecycle exposes no publication verb; its only push path requires a work-item branch binding and a service-issued promotion receipt. An approved GO for such a publication is unconsumable.",
  "after_behavior": "The same sequence executes through one canonical governed operation with authority, scope binding, quiescence, recovery, and evidence enforced at effect time. The direct-git-effect gate is unchanged and continues to block raw git.",
  "self_descriptive_naming": "The verb is `publish`; its arguments name the exact source commit, source tree, base ref, target ref, excluded paths, and blob-size ceiling. No implicit defaults can publish an under-specified operation.",
  "obsolete_guidance_disposition": "No guidance is retired. The direct-git-effect gate, its read-only allowlist, validate_remote_push protected-branch and rename denials, and the pull-request promotion path all remain exactly as they are; this adds a missing operation beside them rather than replacing any.",
  "history_preservation": "No history is rewritten. The operation forbids force, deletion, upstream change, and history rewrite; it creates one new ref proven absent and pushes it once. Prior bridge versions, MemBase rows, and project state are untouched.",
  "worker_loading_paths": [],
  "superseded_guidance": [],
  "baseline": {
    "publication_verb_exists": false,
    "wi5802_go_consumable": false,
    "direct_git_effect_gate_blocks_fetch": true,
    "direct_git_effect_gate_blocks_commit_tree": true,
    "publication_test_module_exists": false
  },
  "expected_result": {
    "publication_verb_exists": true,
    "wi5802_go_consumable": true,
    "direct_git_effect_gate_blocks_fetch": true,
    "direct_git_effect_gate_blocks_commit_tree": true,
    "publication_test_module_exists": true,
    "read_only_allowlist_unchanged": true
  },
  "rollback": {
    "instructions": "Revert only the four declared target files through a separately governed transaction.",
    "verification": "Confirm the direct-git-effect gate, read-only allowlist, promotion path, protected-branch denials, existing git-lifecycle suites, and all remote refs are unchanged."
  },
  "hard_invariants": [
    "the direct-git-effect gate and DIRECT_GIT_READ_ONLY_SUBCOMMANDS are not modified",
    "no force push, ref deletion, upstream change, or history rewrite is reachable",
    "exactly one new local ref is created and exactly one non-forced same-name push occurs",
    "the target ref is proven absent locally and remotely before creation",
    "the blob-size ceiling applies to blob objects only",
    "protected destination branches and source/destination renames remain denied",
    "no declared-excluded path may differ between base and candidate"
  ],
  "fail_closed_conditions": [
    "source commit or tree does not resolve exactly",
    "fetch yields missing, multiple, ambiguous, or non-commit state",
    "target ref exists locally or remotely, or the remote check errors",
    "candidate tree, parentage, commit count, or ancestry is wrong",
    "an excluded path differs between base and candidate",
    "range is empty, an object is unresolvable, or an object type is unexpected",
    "any blob exceeds the declared ceiling",
    "the .git/index byte hash changes between bind and pre-push recheck",
    "push response is non-fast-forward, ambiguous, disconnected, or requests credentials"
  ],
  "essential_context_preservation": "Preserve the existing gate boundary, the pull-request promotion path, validate_remote_push denials, the module's transaction/recovery/evidence machinery, and the exact fail-closed sequence already reviewed and approved on the WI-5802 thread."
}
```

## Requirement Sufficiency

Existing requirements sufficient. `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` and
`ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` already require that Git effects
occur through the governed lifecycle with authority, scope and evidence
enforced at effect time; this adds the missing operation so a bounded
publication can satisfy them. No new or revised requirement is needed.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Effects occur only through the governed boundary | Attempt the sequence via raw git; then via the new operation | Raw git still blocked by the gate; operation succeeds with evidence |
| Base binding is operation-time | Fixture with a stale remote-tracking ref differing from a fresh fetch | Fresh fetch value used; stale ref never accepted |
| Ambiguous fetch stops | Fixture yielding missing / multiple / non-commit fetch state | Operation stops before candidate creation |
| Ref newness proven both sides | Fixtures: local ref exists; remote ref exists; remote check errors | All three stop; an error is not treated as absence |
| Candidate ancestry exact | Fixtures: wrong tree; two parents; more than one commit ahead; base not ancestor | Each stops before ref creation |
| Excluded-carrier delta rejected | Fixture where an excluded path differs between base and candidate | Stops |
| Blob ceiling applies to blobs only | Fixture with an oversized blob; fixture with a large tree/commit object | Oversized blob stops; large non-blob does not falsely trip |
| Range integrity | Fixtures: empty range; unresolvable object; unexpected object type | Each stops |
| Index stability | Fixture mutating `.git/index` between bind and pre-push recheck | Stops before ref creation |
| Push is single, non-forced, same-name | Assert the exact argv and refspec | One ref, no force/tags/delete/upstream, source equals destination |
| Protected destinations still denied | Invoke against a protected remote branch | `validate_remote_push` denies, unchanged |
| Ambiguous push response stops | Fixture with non-fast-forward / disconnect / credential request | Stops and reports; no retry inferred |
| Evidence recorded | Successful run | Identities, counts, maximum blob size, exits and timestamps present |
| No regression | Existing git-lifecycle suites | All pass |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py platform_tests/scripts/test_git_lifecycle_maintenance.py platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle platform_tests/scripts/test_git_lifecycle_publication.py
```

## Acceptance Criteria

1. A bounded one-off publication runs end-to-end through the canonical CLI.
2. Every enumerated fail-closed condition stops before the next side effect.
3. The blob ceiling applies to blob objects only.
4. Exactly one new local ref is created and exactly one non-forced same-name
   push occurs.
5. Protected-destination and rename denials are unchanged.
6. The direct-git-effect gate and its read-only allowlist are unmodified.
7. Operation evidence is recorded through the module's existing surface.
8. Existing git-lifecycle suites pass.
9. Only the four declared target paths are modified.

## Bridge Chain Discipline

Filed as `bridge/gtkb-wi5840-git-lifecycle-publication-operation-001.md`, the
first numbered file of a fresh append-only chain. No prior versioned bridge
file is deleted, rewritten, or renumbered.

## Specification Links

- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5802-clean-branch-publication-001.md` / `-002.md` — the approved procedure this operation implements, and the clean GO that cannot currently be consumed.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-PREPARATION-APPROVAL` — owner authorization of the publication preparation track.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION` — owner selection of the exact source tree.
- `DELIB-20260730-WI5802-CLEAN-BRANCH-PUBLICATION-PAUTH-V1` — the WI-5802 PAUTH; note it allows only `bridge`, `governance_evidence`, `metadata`, `repository_metadata`, which is why this capability cannot be carried by WI-5802.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session files.
- `WI-5187` — the minimal governed Git binding substrate in the same project; adjacent scope, not superseded.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner authorization, 2026-07-31: "Authorized: WI-5802's execution path (git-lifecycle gate has no publication verb)."
- Owner AskUserQuestion, 2026-07-31: selected **"Propose a governed publication verb"** over extending the read-only allowlist or having the owner run the commands directly.
- Implementation authority is inherited from the active list-free project-scope PAUTH cited in the header.
- No new owner decision is requested by this proposal. The eventual WI-5802 push remains separately gated by the owner's standing "ask before push" instruction on that thread.

## Risk And Rollback

Principal risk is that a new push-capable operation becomes a general-purpose
escape hatch. Mitigated by construction: the operation publishes only to a
ref proven absent both locally and remotely, refuses any source/destination
rename and any protected destination through the existing
`validate_remote_push`, performs exactly one non-forced push of one refspec,
and offers no force, delete, upstream, or history-rewrite affordance.

Secondary risk is a partially-completed publication. Mitigated by ordering
every proof before the first mutating step, re-validating immediately before
ref creation, and preserving any created object or local ref for reporting
rather than deleting it — `destructive_cleanup` is not requested.

Rollback is reversion of the four target files through a separately governed
transaction; no historical bridge file, MemBase row, project state, or remote
state is touched by this change.

## Recommended Commit Type

`feat` — adds a new governed operation and CLI surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
