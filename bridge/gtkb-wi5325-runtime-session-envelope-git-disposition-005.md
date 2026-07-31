REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; approval_policy=never

# Revised Proposal - Lossless Git disposition for runtime session-envelope histories

bridge_kind: prime_proposal
Document: gtkb-wi5325-runtime-session-envelope-git-disposition
Version: 005
Responds to: bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-004.md
Date: 2026-07-17 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5325
target_paths: [".gitignore", "platform_tests/scripts/test_session_envelope_git_disposition.py"]
implementation_scope: repository_metadata,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore

## Revision Claim

Revise WI-5325 around the current repository facts. The seven per-harness
`harness-state/*/session-envelope.json` carriers are untracked runtime files,
not staged additions. The revised implementation therefore mutates only
repository metadata and test coverage: add narrow `.gitignore` coverage for the
runtime session-envelope families and add a focused regression test proving the
ignore policy does not hide durable harness identity or registry files.

This revision removes every `git rm --cached`, index-entry, staged-addition,
runtime-byte-baseline, and active-writer quiescence claim from the approved
transaction. It does not mutate, hash-stabilize, move, delete, close, rewrite,
stage, or commit any live session-envelope JSON or archive file.

## Current-State Facts Checked Before Revision

- `git status --short --untracked-files=all` reports the seven current
  `harness-state/*/session-envelope.json` carriers as `??`, with no staged
  index entries.
- `git diff -- .gitignore` is empty in the current working tree.
- WI-5299's `.gitignore` predecessor is latest `VERIFIED` at
  `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md`, and
  MemBase records WI-5299 as resolved.
- The dispatcher still has active/writer-capable runtime surfaces, so this
  revision makes no live-byte stability assertion for the runtime envelope
  files.

## Requirement Sufficiency

Existing requirements remain sufficient. `DCL-SESSION-ENVELOPE-DURABILITY-001`
requires in-root live state and append-only local archive availability, not Git
tracking of mutable runtime files. `GOV-WORK-TREE-HYGIENE-001` requires an
explicit generated-state disposition. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
requires the documents to remain readable. Narrow ignore rules plus negative
tests for durable controls satisfy these requirements without a new owner
decision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is a Prime-authored numbered bridge proposal and remains implementation-start gated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing requirements are listed explicitly and mapped to verification below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, Work Item, and target paths are machine-readable in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps the ignore policy to executable regression tests.
- `GOV-STANDING-BACKLOG-001` - WI-5325 is the durable work item for the runtime-envelope Git disposition.
- `GOV-WORK-TREE-HYGIENE-001` - runtime-generated envelope histories receive an explicit non-capturing Git disposition.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - live and archived session-envelope files remain in-root and readable.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provenance-bearing session documents are not deleted or rewritten.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the change reduces Git noise without reducing runtime evidence, harness capacity, or dispatcher behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and representative paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the generated-state policy and rejected alternatives are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation, regression, report, and verification remain one lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision keeps the work in explicit proposal, report, and verification states.

## Prior Deliberations

- `DELIB-202666332` - owner requires clean-tree completion through exact ownership inventory and independently VERIFIED local finalization, while forbidding broad capture and destructive cleanup.
- `DELIB-2238` - establishes session-envelope convention context and the medium-commitment lifecycle framing.
- `DELIB-20260637` - records the envelope meta-model and dispatch/session/topic containment that makes session-envelope runtime state an in-root operational artifact.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md` - independently VERIFIED `.gitignore` predecessor now clears the foreign-work conflict cited in version 004.
- `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-004.md` - the current NO-GO whose F1/F2/F3 findings this revision addresses.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666332` already authorizes exact
clean-worktree finalization only after independent verification and forbids
broad capture, destructive cleanup, Git push, deployment, release, credential
actions, history rewrite, dispatcher/TAFE/harness mutation, and harness
eligibility changes. This revision requests none of those operations.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5325 revision after bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-004.md at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001, DCL-SESSION-ENVELOPE-DURABILITY-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Repository-metadata ignore disposition plus focused git check-ignore regression coverage",
  "before_behavior": "Runtime session-envelope carriers and per-session/archive histories remain visible as untracked Git dirt even though they are live in-root runtime state rather than source or governed evidence carriers",
  "after_behavior": "Runtime session-envelope families are ignored by Git while durable harness registry, identity, bridge, and source surfaces remain visible and governed",
  "self_descriptive_naming": "session-envelope.json, session-envelopes, session-envelope-archive, and test_session_envelope_git_disposition name the runtime families and verification intent",
  "obsolete_guidance_disposition": "The stale staged-index-removal premise is rejected; no runtime envelope file becomes obsolete or is deleted",
  "history_preservation": "All existing live and archived runtime envelope bytes remain on disk under the same in-root paths; bridge and MemBase history remain append-only",
  "baseline": {
    "runtime_carriers": "seven current harness-state/*/session-envelope.json paths are untracked",
    "gitignore": "current working tree has no .gitignore diff after WI-5299 VERIFIED",
    "active_writers": "runtime writers may still update envelope bytes, so byte-stability is not asserted"
  },
  "expected_result": {
    "git_visibility": "representative runtime envelope paths are ignored",
    "durable_controls": "harness registry and identity files remain non-ignored",
    "runtime_bytes": "no runtime session-envelope file is in target_paths or implementation diff"
  },
  "rollback": {
    "instructions": "remove only the WI-5325 .gitignore hunk and focused test file through a governed successor",
    "verification": "rerun the focused ignore regression and confirm no runtime envelope file changed"
  },
  "hard_invariants": [
    "no runtime envelope deletion, move, close, rewrite, staging, or commit",
    "no dispatcher, TAFE, harness, lease, eligibility, routing, credential, release, deploy, push, history rewrite, or destructive cleanup mutation",
    "no broad Git status capture or whole-tree staging",
    "durable harness registry and identity files remain visible to Git"
  ],
  "fail_closed_conditions": [
    "foreign .gitignore diff at implementation start",
    "implementation-start packet missing or outside two target paths",
    "runtime JSON path appears in target_paths or implementation diff",
    "focused ignore regression fails",
    "ignore rule hides harness registry or identity controls",
    "GO, claim, start, or independent verification is absent"
  ],
  "essential_context_preservation": "The proposal keeps runtime envelope durability, provenance readability, clean-tree ownership, and non-impairment boundaries explicit while rejecting the obsolete staged-index premise."
}
```

## Findings Addressed

### F1 - Invalid index-removal scope

Accepted. The revised target set excludes every runtime JSON carrier. No
`git rm --cached`, index-entry removal, staged-addition rollback, or
before/after index proof is requested. The implementation changes only
`.gitignore` and a new focused test file after independent GO, claim, and
implementation-start authorization.

### F2 - Volatile baseline bytes

Accepted. The revised plan makes no byte-hash baseline promise for any active
runtime writer path. The implementation must not open runtime envelope files for
modification, must not quiesce or restart the dispatcher, and must not assert
that live runtime bytes were stable. Losslessness is proven by scope and by the
absence of runtime-file mutation in the implementation report, not by freezing
writer-owned files during active dispatch.

### F3 - Foreign `.gitignore` work

Resolved by current state. WI-5299 is latest `VERIFIED`, and the current
working tree has no `.gitignore` diff before this revision. The eventual
WI-5325 implementation must still apply a hunk-only `.gitignore` edit against
the then-current base and must fail closed if a new foreign `.gitignore` diff
appears before implementation start.

## Intended Implementation

1. Confirm latest bridge status is `GO`, acquire the matching implementation
   claim, and create a current implementation-start packet before touching
   `.gitignore` or the test file.
2. Re-check that `.gitignore` has no unrelated working-tree diff. If it does,
   stop and refile or wait for the owner/peer scope to clear.
3. Add only narrow runtime-session-envelope ignore patterns, rooted to the
   existing harness-state layout:
   - `harness-state/*/session-envelope.json`
   - `harness-state/*/session-envelopes/`
   - `harness-state/*/session-envelope-archive/`
4. Add `platform_tests/scripts/test_session_envelope_git_disposition.py` with
   focused checks that representative live, per-session, and archive envelope
   paths are ignored while durable controls such as
   `harness-state/harness-registry.json`,
   `harness-state/harness-identities.json`, and non-envelope harness files are
   not ignored.
5. Run the focused test and the two separate code-quality gates for the changed
   test file if Python test code is added.
6. File a post-implementation report carrying forward the exact target paths,
   the `.gitignore` hunk, the test evidence, and evidence that no runtime
   session-envelope files were modified by the implementation.

## Explicit Non-Scope

- No dispatcher, TAFE, harness, live worker, lease, eligibility, routing,
  current session-envelope JSON, per-session envelope history, archive history,
  database, credential, deployment, release, external-system, Git push, Git
  history rewrite, destructive cleanup, broad staging, or broad capture
  mutation.
- No claim that ignored runtime files cease to exist. The policy is visibility
  and ownership disposition, not deletion.
- No quiescence window is requested. Any future operation requiring stable
  runtime bytes belongs in a separate governed quiescence/handoff work item.

## Spec-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-WORK-TREE-HYGIENE-001` | `git check-ignore --no-index` evidence and focused pytest prove runtime envelope families are ignored while durable controls remain visible. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001` | Tests and source inspection prove the policy does not relocate, delete, or rewrite session-envelope runtime paths. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | The implementation report must show runtime provenance files are outside `target_paths` and untouched by the diff. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Regression tests prove harness registry/identity files remain non-ignored; dispatcher/harness eligibility is not mutated. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and linkage DCLs | Applicability and clause preflights pass before filing and before any `VERIFIED` outcome. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The post-implementation report must include commands, observed results, and this spec-to-test mapping carried forward. |

## Acceptance Criteria

- Latest LO review of this revision is `GO` before implementation.
- Implementation-start authorization names exactly `.gitignore` and
  `platform_tests/scripts/test_session_envelope_git_disposition.py`.
- `.gitignore` receives only the WI-5325 runtime-envelope hunk.
- The new focused test passes and proves the ignore policy is narrow.
- No runtime session-envelope file appears in the implementation diff.
- The implementation report does not claim stable live runtime byte hashes or
  index-removal evidence.
- Loyal Opposition can independently verify the change without quiescing,
  restarting, deleting, staging, or committing runtime JSON state.

## Risk And Rollback

Primary risk is overbroad ignore coverage hiding durable harness controls. The
focused test guards that by checking representative negative paths. Rollback is
to remove the WI-5325 `.gitignore` hunk and the focused test file; no runtime
bytes are touched, so rollback does not need to reconstruct session-envelope
state.

## Pre-Filing Self-Check Evidence

The completed content was prepared after the required Prime drafting claim.

- Applicability preflight command:
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5325-runtime-session-envelope-git-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5325-runtime-session-envelope-git-disposition-005.md --json`
- Applicability result: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`. The filing helper repeats this preflight against the final content and emits the operative packet hash.
- Clause preflight command:
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5325-runtime-session-envelope-git-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5325-runtime-session-envelope-git-disposition-005.md`
- Clause result: mandatory mode, exit 0, clauses evaluated 5, must_apply 4, evidence gaps in must_apply clauses 0, blocking gaps 0.
