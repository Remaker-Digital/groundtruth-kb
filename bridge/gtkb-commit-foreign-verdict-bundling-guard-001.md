NEW

# gtkb-commit-foreign-verdict-bundling-guard — Block a foreign-session-staged bridge verdict from being swept into an unrelated commit

bridge_kind: prime_proposal
Document: gtkb-commit-foreign-verdict-bundling-guard
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 6e9eb87a-50f6-492f-b3fe-b230cb088350
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (::init gtkb pb); MAY29-HYGIENE retirement drive

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4763

target_paths: ["scripts/check_commit_pathspec_safety.py", "scripts/check_commit_scope_bundling.py", "platform_tests/scripts/test_commit_foreign_verdict_bundling_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

On 2026-06-23 UTC, while a Loyal Opposition session staged a NO-GO verdict
(`bridge/gtkb-disable-active-session-dispatch-suppression-008.md`), a concurrent
external commit (`e22bbb6b8`, "lock bridge substrate predicate behavior") landed
and swept that freshly-staged foreign verdict into a commit alongside unrelated
substrate/source changes. The prior commit-scope work — the WI-4464 commit
pathspec-safety detector (`scripts/check_commit_pathspec_safety.py`) and the
commit-scope bundling detector (`scripts/check_commit_scope_bundling.py`) — is
resolved, so this is a post-resolution regression: neither detector flags the
specific case of a **staged bridge verdict authored by a different session** being
folded into an unrelated commit.

This proposal extends the existing commit-scope-safety detection so a commit that
includes a staged bridge verdict file (`bridge/<slug>-NNN.md` whose first token is
`GO`/`NO-GO`/`VERIFIED`) authored by a session other than the committing session is
either **blocked** or the foreign verdict is **excluded**, unless the committer
explicitly names it via an owned pathspec. Verdict ownership is derived from the
verdict file's `author_session_context_id` metadata compared against the committing
session; a foreign or missing author-session id on a staged verdict that is not in
the explicit commit pathspec is the fail-closed trigger. This complements the
already-landed explicit-pathspec finalize path (WI-4743) by guarding the *other*
commit surfaces (sweep-commit and ad-hoc commits) that do not finalize verdicts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge files are an append-only audit trail;
  a foreign verdict swept into an unrelated commit corrupts the per-thread audit
  chain and the commit-scope discipline this spec requires. The guard protects
  that invariant.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the fix adds a regression
  that reproduces the concurrent-commit sweep and asserts block/exclude; it is the
  spec-to-test mapping for this clause.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all
  relevant governing specs; satisfied by the applicability preflight.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/work-item
  linkage metadata is present in the header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is authorized by
  the cited PAUTH covering WI-4763.
- `GOV-STANDING-BACKLOG-001` — WI-4763 is an active MAY29-HYGIENE backlog member.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserves bridge verdicts as
  trustworthy durable artifacts attributable to their authoring session.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — commit-scope integrity keeps
  the bridge thread a trustworthy artifact network.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — a verdict commit is a lifecycle
  transition; the guard keeps the transition attributable and scoped.

## Prior Deliberations

- `DELIB-20263280` — Loyal Opposition GO verdict for the WI-4464 Commit
  Pathspec-Safety Detector (`scripts/check_commit_pathspec_safety.py`). This
  proposal extends that detector's pathspec-ownership model to recognize foreign
  staged bridge verdicts; it does not revisit or revert WI-4464.
- `DELIB-20260866` — Loyal Opposition Verification of Commit-Scope Bundling
  Detection Slice 1 (`scripts/check_commit_scope_bundling.py`, currently WARN-only
  for multi-scope narrative artifacts). The foreign-verdict case is a distinct
  trigger this proposal adds; the existing multi-scope warning behavior is
  preserved.
- Deliberation search query `"concurrent commit bundles foreign staged bridge
  verdict pathspec ownership commit scope contamination"` (2026-06-24) surfaced the
  two prior decisions above and no decision specific to the foreign-session-verdict
  regression; no previously rejected approach is being revisited.

## Owner Decisions / Input

Authorized by owner AskUserQuestion on 2026-06-24 (option "Authorize all 6"),
captured as `DELIB-20265880`, which created
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24` covering the six
out-of-snapshot member work items (including WI-4763) for bounded implementation
(allowed mutation classes: source, test_addition, hook_upgrade, cli_extension,
scaffold_update). No further owner decision is required to proceed through the
bridge protocol; this section records the standing authorization evidence.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is specified by
`GOV-FILE-BRIDGE-AUTHORITY-001` (bridge audit-trail and scoped-commit discipline)
and the WI-4763 acceptance criterion (a regression must reproduce a concurrent
commit after a foreign session stages a verdict and prove the commit tooling blocks
or excludes the foreign staged verdict unless explicitly included by an owned
pathspec). No new or revised requirement is needed.

## Spec-Derived Verification Plan

New regression test `platform_tests/scripts/test_commit_foreign_verdict_bundling_guard.py`
constructs a fixture repo, stages a bridge verdict whose `author_session_context_id`
differs from the committing session, simulates an unrelated commit that does not
name the verdict in its pathspec, and asserts the detector flags/blocks (or
excludes) the foreign verdict; a companion case asserts that a verdict explicitly
named in an owned pathspec is allowed (no false-positive on the legitimate
finalize path).

| Specification | Test / Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (foreign verdict swept) | `test_blocks_foreign_session_staged_verdict_outside_pathspec` | detector fail-closed (non-zero / block finding) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (owned pathspec allowed) | `test_allows_owned_verdict_in_explicit_pathspec` | pass (no false-positive) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (own-session verdict allowed) | `test_allows_same_session_authored_verdict` | pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full test module run | all assertions pass |

Execution command (repo venv for reproducibility):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_commit_foreign_verdict_bundling_guard.py -q --no-header
```

Pre-file code-quality gates on changed Python (both, separate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>
```

## Risk / Rollback

- **Risk: false-positive on legitimate verdict finalization.** The
  `finalize_verified_commit` path legitimately stages + commits a verdict via an
  explicit owned pathspec; the guard must allow that (same-session author + named
  pathspec). Mitigated by the owned-pathspec and same-session allow tests.
- **Risk: author-session metadata absent on older verdicts.** Some historical
  verdicts predate `author_session_context_id`; the guard must not retroactively
  block commits of already-tracked historical verdicts. Mitigated by scoping the
  check to *freshly-staged* (newly added/modified) verdict files, not
  already-committed ones.
- **Risk: detector escalation breaks existing WARN-only behavior.** The
  scope-bundling detector is WARN-only today; the foreign-verdict trigger is added
  as a distinct finding so existing multi-scope warning semantics are unchanged.
- **Rollback:** single-commit revert of the detector + test restores prior behavior;
  the change is additive detection with no data migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-commit-foreign-verdict-bundling-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a post-resolution commit-scope regression (foreign verdict sweep)
by extending existing detectors; no new capability surface beyond the added guard
and its regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
