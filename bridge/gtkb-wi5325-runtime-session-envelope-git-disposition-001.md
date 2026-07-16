NEW

# WI-5325 - Lossless Git disposition for runtime session-envelope histories

bridge_kind: prime_proposal
Document: gtkb-wi5325-runtime-session-envelope-git-disposition
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning configuration

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5325

target_paths: [".gitignore", "platform_tests/scripts/test_session_envelope_git_disposition.py", "harness-state/alibaba-cloud-studio/session-envelope.json", "harness-state/antigravity/session-envelope.json", "harness-state/claude/session-envelope.json", "harness-state/codex/session-envelope.json", "harness-state/cursor/session-envelope.json", "harness-state/ollama/session-envelope.json", "harness-state/openrouter/session-envelope.json"]

implementation_scope: repository_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Define a lossless Git ownership policy for per-harness session-envelope runtime
state. The inventory found more than 600 untracked live/per-session/archive
documents, while seven mutable `harness-state/*/session-envelope.json` files are
foreign staged additions absent from `HEAD`. These files are required in-root
runtime and audit inputs, but continuously versioning every session mutation is
incompatible with a stable worktree and no governing requirement says Git is
their authority.

Add narrow `.gitignore` rules for the live, per-session, and archive envelope
families; add a regression test that proves canonical runtime readers still see
the files while Git ignores only those families; and remove exactly the seven
named staged legacy live projections from the index without deleting or
rewriting their working-tree bytes. No existing archive or session document is
deleted, moved, normalized, closed, or edited. This complements WI-5314 (stop
false non-spawn creation) and WI-5281 (close terminal worker envelopes) without
absorbing either implementation.

## Intended Implementation

1. Record, before any index mutation, the working-tree SHA-256 and current
   index mode/blob for each of the seven named staged additions. Confirm every
   path is absent from `HEAD` and no active work-intent claim owns it.
2. Add exact `.gitignore` patterns for:
   - `harness-state/*/session-envelope.json`
   - `harness-state/*/session-envelopes/`
   - `harness-state/*/session-envelope-archive/`
3. Add `test_session_envelope_git_disposition.py` to run `git check-ignore
   --no-index` for representative paths, prove `harness-state/harness-registry.json`
   is not ignored, and verify canonical session-envelope code continues to use
   the in-root runtime paths.
4. After GO and implementation-start authority, remove only the seven declared
   staged additions from the index with an exact path list. Verify their files
   still exist and retain the recorded SHA-256 values. Do not reset, restore,
   clean, or stage any other path.
5. Report the `.gitignore` hunk, new test blob, before/after index entries, and
   before/after file hashes for independent verification. Any final commit must
   contain only independently VERIFIED repository-metadata/test bytes.

## Pre-start Ownership Boundary

`.gitignore` already contains unrelated unstaged WI-5299 work; only the new
session-envelope hunk belongs to WI-5325. All seven live files are staged
additions but absent from `HEAD`; their bytes are foreign runtime state. The
new test path is absent. Whole-file staging of `.gitignore`, broad index reset,
and capture of any session JSON content are prohibited.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - repository metadata, tests, and exact index mutation require independent GO, claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal maps runtime durability, provenance, hygiene, and non-impairment requirements to evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5325, PROJECT-GTKB-TREE-STABILIZATION, and the bounded PAUTH are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must inspect both Git behavior and byte preservation.
- `GOV-STANDING-BACKLOG-001` - the ownership omission is recorded as WI-5325 and its transaction defect as WI-5326.
- `GOV-WORK-TREE-HYGIENE-001` - generated runtime state receives an explicit durable disposition instead of broad commit or deletion.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - authoritative live state stays in-root, archives remain append-only, and readers remain unchanged.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - session-document author evidence remains available at the same local paths for governed validation.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the change reduces Git noise without reducing runtime evidence, harness capacity, or dispatcher behavior.

## Prior Deliberations

- `DELIB-202666332` - assigns the clean-worktree goal and permits exact local finalization only for independently VERIFIED isolated scopes.
- `DELIB-2238` - establishes the session-envelope lifecycle context carried into the durability DCL.
- `DELIB-20260637` - records the per-harness envelope payload and lifecycle decisions cited by the durability DCL.

## Owner Decisions / Input

`DELIB-202666332` authorizes the exact independently reviewed work required to
inventory ownership and clear the worktree, including exact local finalization.
The authorization expressly forbids broad capture and destructive cleanup.
This proposal preserves that boundary by keeping every runtime file on disk and
limiting index mutation to seven named additions absent from `HEAD`.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ENVELOPE-DURABILITY-001`
requires in-root live state and append-only local archives but does not require
Git tracking. `GOV-WORK-TREE-HYGIENE-001` requires an explicit generated-state
disposition, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` requires the documents to
remain readable. Ignoring the runtime families while preserving every byte
satisfies all three without a new or revised requirement.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, proposal/project linkage DCLs, and
  `GOV-STANDING-BACKLOG-001`: mandatory applicability and clause preflights pass;
  WI-5325 and WI-5326 remain queryable through `gt backlog show`.
- `GOV-WORK-TREE-HYGIENE-001`: representative live, per-session, and archive
  paths are ignored; the 600-plus current runtime paths disappear from ordinary
  `git status` without deletion.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` and
  `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`: every pre-existing file still exists at
  its original path with identical SHA-256; focused session-envelope reader and
  provenance tests pass.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: canonical harness registry,
  identities, capability registry, and non-envelope harness-state files are not
  ignored; bridge dispatch health is unchanged.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: independent Loyal
  Opposition reruns the focused tests and verifies exact index/file evidence.

Expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_git_disposition.py groundtruth-kb/tests/test_session_envelope.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_session_envelope_git_disposition.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_session_envelope_git_disposition.py
git check-ignore --no-index -v harness-state/codex/session-envelope.json harness-state/codex/session-envelopes/example.json harness-state/codex/session-envelope-archive/example.json
git check-ignore --no-index harness-state/harness-registry.json
git diff --cached --name-only -- harness-state/alibaba-cloud-studio/session-envelope.json harness-state/antigravity/session-envelope.json harness-state/claude/session-envelope.json harness-state/codex/session-envelope.json harness-state/cursor/session-envelope.json harness-state/ollama/session-envelope.json harness-state/openrouter/session-envelope.json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json
```

The registry `git check-ignore` command is expected to return non-zero; the
three representative runtime-envelope paths are expected to return zero. The
cached diff for the seven exact runtime files is expected to be empty after the
authorized index-only removal.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666332",
  "canonical_authority": "DCL-SESSION-ENVELOPE-DURABILITY-001 and GOV-WORK-TREE-HYGIENE-001",
  "primary_route": "canonical session-envelope APIs read and write harness-state runtime paths; Git observes the repository through .gitignore",
  "before_behavior": "Valid session activity continuously creates hundreds of untracked files and seven foreign staged live projections.",
  "after_behavior": "The same runtime files remain readable and append-only where required but no longer appear as repository changes.",
  "self_descriptive_naming": "session-envelope.json, session-envelopes, and session-envelope-archive map directly to three explicit ignore rules.",
  "obsolete_guidance_disposition": "No guidance is removed; the accidental implication that mutable runtime records are commit candidates is replaced by exact Git policy.",
  "history_preservation": "All live and archived files remain byte-identical at their original in-root paths; only Git tracking metadata changes.",
  "baseline": {
    "tracked_in_head": 0,
    "foreign_staged_live_files": 7,
    "untracked_runtime_history_files": "more than 600"
  },
  "expected_result": {
    "runtime_files_deleted": 0,
    "foreign_staged_live_files": 0,
    "ordinary_git_status_runtime_envelope_entries": 0
  },
  "rollback": {
    "instructions": "Restore only the recorded .gitignore hunk and test blob; if pre-commit index rollback is required, restore the seven exact recorded mode/blob entries without touching working-tree files.",
    "test": "Re-run file SHA-256 comparison, focused tests, and exact git status path checks."
  },
  "hard_invariants": [
    "No session-envelope file deletion, move, close, normalization, or content edit",
    "Append-only archives stay available at the same paths",
    "harness-registry.json and harness-identities.json remain Git-visible",
    "No broad stage, reset, clean, stash, or whole-file .gitignore capture",
    "No harness eligibility, routing, role, worker, or dispatcher mutation"
  ],
  "fail_closed_conditions": [
    "missing GO, claim, or implementation-start authority",
    "any named runtime path exists in HEAD",
    "working-tree hash differs after index mutation",
    "active claim owns a named path",
    "ignore pattern covers non-envelope harness authority"
  ],
  "essential_context_preservation": "Session role/provenance validators continue reading the same in-root files; Git ignore changes no runtime lookup or dispatcher behavior."
}
```

## Risk / Rollback

The primary risks are hiding canonical registry state, deleting append-only
evidence, disturbing another session's staged work, or committing unrelated
`.gitignore` bytes. Exact path patterns, negative ignore assertions, before/after
hashes, collision checks, and hunk-only finalization address those risks. Before
commit, rollback restores the seven exact recorded index entries and removes
only the WI-5325 hunk/test; after commit, rollback is an exact revert of the
WI-5325 commit and must not delete local runtime files.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5325-runtime-session-envelope-git-disposition`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - assign a deterministic lossless Git disposition to mutable runtime
session-envelope state and remove recurring false worktree dirt.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
