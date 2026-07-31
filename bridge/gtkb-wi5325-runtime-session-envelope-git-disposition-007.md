NEW

# WI-5325 Runtime Session Envelope Git Disposition - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5325-runtime-session-envelope-git-disposition
Version: 007
Responds to GO: bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-006.md
Approved proposal: bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-005.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5325
target_paths: [".gitignore", "platform_tests/scripts/test_session_envelope_git_disposition.py"]
Recommended commit type: chore

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; approval_policy=never

## Implementation Claim

Implemented the approved WI-5325 runtime session-envelope Git disposition by
adding narrow `.gitignore` coverage for live, per-session, and archived
per-harness session-envelope runtime paths:

- `harness-state/*/session-envelope.json`
- `harness-state/*/session-envelopes/`
- `harness-state/*/session-envelope-archive/`

Added focused regression coverage in
`platform_tests/scripts/test_session_envelope_git_disposition.py` proving those
runtime envelope families are ignored while durable harness controls remain
visible to Git.

The implementation changed only the two approved target paths. It did not
delete, move, rewrite, stage, hash-stabilize, or commit any live
`harness-state/*/session-envelope.json` carrier, per-session envelope history,
or session-envelope archive bytes. It did not mutate dispatcher, TAFE, harness,
lease, eligibility, routing, credential, release, deployment, Git history, or
database state.

## Implementation-Start Evidence

- Work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-wi5325-runtime-session-envelope-git-disposition --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 7200`
- Claim result: `claim_kind: go_implementation`; `project_id: PROJECT-GTKB-TREE-STABILIZATION`; `implementation_deadline: 2026-07-17T05:00:11Z`; claim acquired at `2026-07-17T04:30:11Z`.
- Implementation-start command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5325-runtime-session-envelope-git-disposition --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 120`
- Implementation-start result: latest status `GO`, GO file `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-006.md`, proposal file `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-005.md`, packet hash `sha256:2e3ff7e7eb50c80ae7754b6c8c02eaecc24354285b68561be0001bde2d4ebc2b`, pre-start packet hash `sha256:684ec219c8b1d96caced9397f6ddbae06524d7585fe4980b11ab7a6d7722b298`.
- Authorized target path globs: `.gitignore`, `platform_tests/scripts/test_session_envelope_git_disposition.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations And Bridge Evidence

- `DELIB-202666332` - owner requires clean-tree completion through exact ownership inventory and independently VERIFIED local finalization, while forbidding broad capture and destructive cleanup.
- `DELIB-2238` - establishes session-envelope convention context and the medium-commitment lifecycle framing.
- `DELIB-20260637` - records the envelope meta-model and dispatch/session/topic containment that makes session-envelope runtime state an in-root operational artifact.
- `bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-004.md` - independently VERIFIED `.gitignore` predecessor clearing the foreign-work conflict raised in WI-5325 version 004.
- `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-005.md` - approved revised proposal.
- `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-006.md` - Loyal Opposition GO.

## Files Changed

- `.gitignore`
- `platform_tests/scripts/test_session_envelope_git_disposition.py`

The observed worktree still contains unrelated foreign harness-state projection
and owner-action-note dirt outside the approved WI-5325 target set, including
`harness-state/harness-registry.json` and untracked `harness-state/codex/owner-action-*.md`
paths. Those files are not part of this implementation report and were not
included in the WI-5325 target paths or implementation diff.

## Gitignore Hunk

```diff
 # Root-level harness-state replaces applications/Agent_Red/harness-state/.
 # Durable operating-role.md and session-startup-preferences.json ARE tracked;
 # the per-harness session-lifecycle-guard.json is runtime-mutable.
 harness-state/*/session-lifecycle-guard.json
+# WI-5325: live and archived per-harness session-envelope runtime state remains
+# in-root and readable, but is not a git-tracked source or governance artifact.
+harness-state/*/session-envelope.json
+harness-state/*/session-envelopes/
+harness-state/*/session-envelope-archive/
```

## Test Coverage Added

`platform_tests/scripts/test_session_envelope_git_disposition.py` adds:

- `test_runtime_session_envelope_paths_are_gitignored`, which checks representative live, per-session, and archive session-envelope paths with `git check-ignore --no-index -v`.
- `test_durable_harness_controls_remain_visible_to_git`, which checks `harness-state/harness-registry.json`, `harness-state/harness-identities.json`, `harness-state/codex/operating-role.md`, `harness-state/codex/session-startup-preferences.json`, and a similarly named non-envelope file remain visible with `git check-ignore --no-index -q`.

## Specification-Derived Verification

| Specification | Executed evidence and result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status for WI-5325 was `GO` at `bridge/gtkb-wi5325-runtime-session-envelope-git-disposition-006.md`; work-intent claim and implementation-start packet authorized exactly `.gitignore` and `platform_tests/scripts/test_session_envelope_git_disposition.py`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This implementation report carries forward all governing specs from the approved proposal and GO. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header names the active PAUTH, `PROJECT-GTKB-TREE-STABILIZATION`, `WI-5325`, and exact target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked requirement family to executed command evidence before requesting independent `VERIFIED`. |
| `GOV-STANDING-BACKLOG-001` | WI-5325 remains the durable work item for this generated-state disposition pending Loyal Opposition verification. |
| `GOV-WORK-TREE-HYGIENE-001` | Focused pytest passed 2 tests; `git check-ignore --no-index -v` reports the three runtime envelope patterns as ignored. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001` | Runtime envelope files remain in-root and readable; no runtime envelope path appears in the implementation diff. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | No provenance-bearing runtime envelope JSON or archive file was deleted, rewritten, moved, staged, or committed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Negative checks prove durable harness registry, identity, operating-role, and startup-preference files remain visible to Git. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed paths and all representative check paths are under `E:\GT-KB`; no external or Agent Red repository target is involved. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work item, proposal, GO, implementation-start packet, test, and report preserve the generated-state disposition as durable artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation and verification evidence are tied to the approved bridge lifecycle rather than informal cleanup. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This `NEW` implementation report advances the GO implementation to independent Loyal Opposition verification without prematurely resolving WI-5325. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_session_envelope_git_disposition.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_session_envelope_git_disposition.py`
- `python -m ruff format --check platform_tests/scripts/test_session_envelope_git_disposition.py`
- `git diff --check -- .gitignore platform_tests/scripts/test_session_envelope_git_disposition.py`
- `git check-ignore --no-index -v harness-state/codex/session-envelope.json harness-state/claude/session-envelopes/session-example.json harness-state/openrouter/session-envelope-archive/2026-07-17T04-00-00Z-session-envelope.json`
- Per-path visibility loop using `git check-ignore --no-index -q -- <path>` for `harness-state/harness-registry.json`, `harness-state/harness-identities.json`, `harness-state/codex/operating-role.md`, `harness-state/codex/session-startup-preferences.json`, and `harness-state/codex/session-envelope-notes.json`.
- `git diff --name-only -- harness-state/*/session-envelope.json harness-state/*/session-envelopes harness-state/*/session-envelope-archive`
- `git status --short --ignored --untracked-files=all -- harness-state/codex/session-envelope.json harness-state/claude/session-envelope.json harness-state/openrouter/session-envelope.json`

## Observed Results

- Pytest: `2 passed`.
- Ruff check: `All checks passed!`
- Ruff format: `1 file already formatted`.
- Diff check: exit 0.
- Runtime ignore evidence:
  - `.gitignore:519:harness-state/*/session-envelope.json` matched `harness-state/codex/session-envelope.json`.
  - `.gitignore:520:harness-state/*/session-envelopes/` matched `harness-state/claude/session-envelopes/session-example.json`.
  - `.gitignore:521:harness-state/*/session-envelope-archive/` matched `harness-state/openrouter/session-envelope-archive/2026-07-17T04-00-00Z-session-envelope.json`.
- Durable harness control visibility loop returned:
  - `visible: harness-state/harness-registry.json`
  - `visible: harness-state/harness-identities.json`
  - `visible: harness-state/codex/operating-role.md`
  - `visible: harness-state/codex/session-startup-preferences.json`
  - `visible: harness-state/codex/session-envelope-notes.json`
- Runtime envelope diff command produced no output.
- Representative ignored live runtime files now appear as ignored (`!!`) under `git status --ignored`, not as visible untracked source candidates.

## Acceptance Criteria Status

- PASS: Latest LO review was `GO` before implementation.
- PASS: Implementation-start authorization named exactly `.gitignore` and `platform_tests/scripts/test_session_envelope_git_disposition.py`.
- PASS: `.gitignore` received only the WI-5325 runtime-envelope hunk.
- PASS: The new focused test passes and proves the ignore policy is narrow.
- PASS: No runtime session-envelope file appears in the implementation diff.
- PASS: This report does not claim stable live runtime byte hashes or index-removal evidence.
- PASS: Verification can be performed without quiescing, restarting, deleting, staging, or committing runtime JSON state.

## Risk And Rollback

Residual risk is overbroad ignore coverage hiding durable harness controls. The
new negative regression test guards that by checking the registry, identity,
operating-role, startup-preference, and similarly named non-envelope files.

Rollback is a governed successor that removes only the WI-5325 `.gitignore`
hunk and the focused test file. No runtime session-envelope bytes require
reconstruction because none were modified.

## Loyal Opposition Asks

1. Independently verify the two-file implementation and command evidence.
2. Return `VERIFIED` only if the narrow ignore behavior, durable-control
   visibility, no-runtime-mutation boundary, and foreign-work exclusion are
   satisfied.
