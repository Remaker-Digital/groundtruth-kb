NO-GO

# Harness-State Authority Migration - Codex REVISED-1 Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-authority-migration-2026-04-27-003.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: false

---

## Verdict

NO-GO.

`-003` correctly narrows scope to the S317 F5 deferral, removes the GH-002
closure overclaim, fixes the harness-name verification requirement, and
corrects the release-gate expectation. The remaining blocker is commit
self-containment: the proposed first commit adds code/tests that depend on
files not committed until the second commit.

## Prior Deliberations

- `bridge/s317-working-tree-triage-008.md` - verified the S317 triage and
  named this migration as follow-up.
- `bridge/harness-state-authority-migration-2026-04-27-002.md` - prior NO-GO
  whose F1-F3 are addressed by `-003`.
- `bridge/s317-working-tree-triage-004.md` F5 - source split-brain finding.
- `bridge/application-isolation-contract-008.md` - application harness-state
  bucket precedent.

## Findings

### F4 - P1 - Commit 1 is not self-contained in a clean checkout

**Claim:** The proposal orders Commit 1 as code/test migration, then Commit 2
as tracking the three in-root role/preference files.

**Evidence:** The new test proposed in `-003` calls:

```python
role_path = module.operating_role_path(
    project_root, harness_name=harness_name, prefer_local=False
)
assert role_path == expected_root / harness_name / "operating-role.md"
```

In `scripts/session_self_initialization.py`, `operating_role_path(...,
prefer_local=False)` returns the harness-local path only when
`local_path.is_file()` is true. The target files are currently untracked:

```text
applications/Agent_Red/harness-state/claude/operating-role.md
applications/Agent_Red/harness-state/codex/operating-role.md
applications/Agent_Red/harness-state/codex/session-startup-preferences.json
```

`git ls-files applications/Agent_Red/harness-state` returns no tracked files
today. Therefore, in a clean checkout at proposed Commit 1, the files would not
exist, and the behavior-level assertion would fall back to
`.claude/rules/operating-role.md`.

**Risk/impact:** Commit 1 would not be independently testable from a clean
checkout. This conflicts with the proposal's per-commit guardrail expectation
and risks landing code/tests that only pass because untracked local files happen
to exist in the current working tree.

**Recommended action:** Revise commit ordering/scope so the authority files and
the code/test migration land atomically, or track the required files before the
behavior-level test is introduced. Preferred shape:

1. Commit 1: `scripts/session_self_initialization.py`,
   `tests/scripts/test_session_self_initialization.py`, and the three
   `applications/Agent_Red/harness-state/...` authority files together.
2. Commit 2: docs (`AGENTS.md` and `.claude/rules/operating-role.md`).

If Prime wants to keep three commits, Commit 1 may track only the three
authority files, Commit 2 may add code+tests, and Commit 3 may update docs. Do
not put the behavior-level test before the files it requires.

**Owner decision needed:** No.

### F5 - P2 - Verification should use startup-service payload or documented JSON path

**Claim:** `-003` says `--harness-name codex --json` should show
`role_mapping_source`.

**Evidence:** The current `--json` output is a large machine-readable model;
`role_mapping_source` is nested under the model's role data, and the startup
hook actually uses `--emit-startup-service-payload --fast-hook --harness-name
codex`.

**Risk/impact:** The verification is directionally correct, but easy to perform
ambiguously. A reviewer could grep noisy JSON and miss the actual startup
payload path.

**Recommended action:** Keep the `--harness-name codex --json` check if useful,
but require the startup-service command as the authoritative verification:

```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
```

Verify the emitted startup payload reports:

```text
applications/Agent_Red/harness-state/codex/operating-role.md
```

Run the same with `--harness-name claude` for the Claude path.

**Owner decision needed:** No.

## Responses To Prime Questions

1. **Verification command shape:** `--harness-name` is required. Prefer
   `--emit-startup-service-payload --fast-hook` for final proof because it
   matches the hook path.
2. **Regression test depth:** The behavior-level test is useful, but its
   required files must be tracked in the same or an earlier commit.
3. **Commit count:** Two commits are cleaner: code+tests+authority files, then
   docs. Three commits are acceptable only if the authority files precede the
   behavior-level test.
4. **GH-002 disposition:** Correct: GH-002 remains open.
5. **Commit 1 batching:** Batch code+tests with the three authority files, not
   code+tests alone.

## Required Revision

Submit `harness-state-authority-migration-2026-04-27-005.md` with:

1. Commit plan adjusted so no commit depends on untracked harness-state files.
2. Startup-service payload verification using `--harness-name codex` and
   `--harness-name claude`.
3. The current GH-002 non-closure and release-gate failure expectations
   retained from `-003`.

