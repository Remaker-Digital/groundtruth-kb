NEW
::init gtkb lo
::open build

# WI-5325 Session-Envelope Git Disposition

bridge_kind: prime_proposal
Document: gtkb-wi5325-session-envelope-git-disposition
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-18T17:40:12Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5325

target_paths: [".gitignore", "platform_tests/scripts/test_session_envelope_git_disposition.py"]

implementation_scope: repository_metadata | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add exact Git ignore rules for per-harness live session-envelope carriers,
per-session envelope directories, and append-only runtime archive directories,
plus a focused regression test that proves those paths are ignored while
durable harness controls remain visible to Git.

This is a non-destructive disposition. All runtime files remain in-root and
readable by their canonical services. No file is deleted, moved, truncated, or
rewritten. Current `HEAD` tracks no live carrier or per-session envelope file;
87 older archive records remain tracked historical evidence and are not
untracked or changed by this slice. The worktree currently contains 1,555
ignored runtime-envelope files whose bytes remain untouched.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - requires deterministic report-first handling
  of runtime evidence and prohibits deleting or broad-committing another
  session's state.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - requires per-harness live state and
  append-only archive availability; Git disposition must not impair either.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the clean-tree repair
  to preserve startup, wrap, audit, and harness operation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves independent review, exact
  claim/start, implementation reporting, VERIFIED, and append-only bridge
  history.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds the exact
  ignore hunk and regression test to the governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this two-file
  scope to WI-5325 and its dedicated project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executable
  proof that runtime paths are ignored and durable control paths are not.
- `GOV-STANDING-BACKLOG-001` - recognizes WI-5325 as the durable P0 ownership
  record for recurring session-envelope worktree dirt.

## Prior Deliberations

- `DELIB-202666332` - authorizes the bounded Tree Stabilization filing and
  implementation path for WI-5325 while preserving all runtime bytes and
  forbidding broad capture or destructive cleanup.
- `DELIB-202666274` - supplies project-level Tree Stabilization authority and
  the clean-worktree completion objective without waiving exact ownership,
  independent review, or finalization gates.

## Owner Decisions / Input

No new owner decision is required. The dedicated active PAUTH
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715`
is bound to `DELIB-202666332`. Independent GO, matching claim/start,
spec-derived testing, independent VERIFIED, and an exact two-file finalizer
remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001` defines
non-destructive runtime-state disposition, and
`DCL-SESSION-ENVELOPE-DURABILITY-001` defines the live and archive availability
contract. WI-5325 narrows those requirements to exact Git ignore behavior.

## Spec-Derived Verification Plan

1. `GOV-WORK-TREE-HYGIENE-001`,
   `DCL-SESSION-ENVELOPE-DURABILITY-001`, and
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_git_disposition.py -q --tb=short
   ```

   Expected: 2 tests pass. The three runtime-envelope path families are
   ignored, while durable harness registry, identity, role, preferences, and
   similarly named non-runtime controls remain visible.

2. Byte-preserving inventory:

   ```text
   git ls-files --others --ignored --exclude-standard -- harness-state/*/session-envelope.json harness-state/*/session-envelopes/** harness-state/*/session-envelope-archive/**
   ```

   Expected: runtime files remain present and discoverable as ignored files;
   the implementation deletes or rewrites none of them.

3. Historical preservation:

   ```text
   git ls-files -- harness-state/*/session-envelope-archive/**
   ```

   Expected: all 87 historical archive records already tracked by the parent
   commit remain tracked and unchanged.

4. Live-state tracking boundary:

   ```text
   git ls-files -- harness-state/*/session-envelope.json harness-state/*/session-envelopes/**
   ```

   Expected: zero tracked live or per-session runtime files.

5. Quality:

   ```text
   groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_session_envelope_git_disposition.py
   groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_session_envelope_git_disposition.py
   ```

   Expected: both commands pass.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5325; DELIB-202666332; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5325-RUNTIME-ENVELOPE-GIT-DISPOSITION-20260715",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001 and DCL-SESSION-ENVELOPE-DURABILITY-001",
  "primary_route": "governed bridge GO, matching claim/start, independent VERIFIED, and exact .gitignore/test finalization",
  "before_behavior": "Valid runtime session-envelope histories recur as worktree dirt even though they are service state rather than tracked source or governance artifacts.",
  "after_behavior": "Live carriers, per-session envelopes, and new runtime archives remain in-root and service-readable while Git ignores them; durable harness controls and historical tracked archives remain visible.",
  "self_descriptive_naming": "The ignore comment and focused test name the WI-5325 session-envelope Git disposition directly.",
  "obsolete_guidance_disposition": "No active guidance is retired and no existing tracked archive is reclassified or removed.",
  "history_preservation": "All 1,555 current ignored runtime files and all 87 tracked historical archives remain byte-for-byte present; bridge and Git history remain append-only.",
  "baseline": {
    "ignored_runtime_envelope_files": 1555,
    "tracked_live_or_session_files": 0,
    "tracked_historical_archive_files": 87
  },
  "expected_result": {
    "focused_tests": "2 passed",
    "tracked_live_or_session_files": 0,
    "tracked_historical_archive_files": 87,
    "runtime_bytes_deleted": 0
  },
  "rollback": {
    "instructions": "Under separate exact authority, revert only the .gitignore hunk and focused test commit; do not remove or alter any runtime or historical envelope file.",
    "verification": "Rerun the focused tests and repeat the tracked/ignored inventory commands."
  },
  "hard_invariants": [
    "No session-envelope byte is deleted, moved, truncated, rewritten, staged, or committed by implementation.",
    "Historical archive records already tracked by the parent commit remain tracked and unchanged.",
    "Durable harness identity, registry, role, and preference controls remain visible to Git.",
    "No harness is stopped, disabled, de-eligibilized, rerouted, or otherwise impaired.",
    "No dispatcher, TAFE, credential, deployment, release, or external-system state is mutated."
  ],
  "fail_closed_conditions": [
    "The active PAUTH, independent GO, claim, or implementation-start evidence is missing or stale.",
    "The .gitignore hunk or focused test path changes under concurrent ownership.",
    "Any durable control path becomes ignored or any historical tracked archive becomes untracked or modified.",
    "Any runtime byte would need deletion or any unrelated path would need staging for finalization.",
    "Focused tests, quality checks, or inventory checks fail."
  ],
  "essential_context_preservation": "The repair preserves in-root runtime availability, append-only historical evidence, durable harness controls, exact two-file ownership, independent review, and the zero-dirt objective."
}
```

## Risk / Rollback

An overbroad ignore pattern could hide durable harness configuration or cause a
future operator to mistake historical evidence for disposable runtime state.
The exact path-family patterns and negative regression cases therefore form the
implementation boundary. No wildcard broader than the three named
session-envelope runtime families is allowed.

Rollback is a separately authorized revert of only the five-line `.gitignore`
hunk and the focused test file. Runtime and historical envelope bytes are never
part of the commit or rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5325-session-envelope-git-disposition`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the change corrects recurring worktree classification for valid runtime
state while adding an executable nonimpairment guard.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
