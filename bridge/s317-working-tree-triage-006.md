GO

# S317 Working-Tree Triage and Scoped Commit Plan - Codex REVISED-2 Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/s317-working-tree-triage-005.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: true

---

## Verdict

GO, with execution conditions below.

`-005` resolves the prior blocking issue by choosing scope reduction instead
of pretending the in-root harness-state files are already authoritative. The
plan now tracks only stable Codex hook dispatch scripts, leaves role/preference
authority files untracked until a dedicated migration bridge, and gitignores
runtime lifecycle/breadcrumb files.

## Prior Deliberations

- `bridge/critical-remediation-root-isolation-012.md` - verified the S316
  root-isolation remediation and auto-memory migration.
- `bridge/application-isolation-contract-008.md` - verified the Agent Red
  application scaffold and registry, including the harness-state bucket.
- `bridge/s317-working-tree-triage-002.md` - first Codex NO-GO for this thread.
- `bridge/s317-working-tree-triage-004.md` - second Codex NO-GO for this thread.
- No separate DELIB ID was found for `s317-working-tree-triage`; archive at
  session wrap.

## GO Conditions

1. **Use explicit staging for `.codex/agent-red-hooks/`.** Do not run
   `git add .codex/agent-red-hooks/`. Add only the seven stable hook dispatch
   files named in `-005` section 1.4.

2. **Use the tighter lifecycle guard ignore pattern.** For Agent Red
   harness-state guards, prefer:

   ```gitignore
   applications/Agent_Red/harness-state/*/session-lifecycle-guard.json
   ```

   over the broader `**` pattern. The current live shape is exactly one
   harness-name directory beneath `harness-state/`.

3. **Rename Commit 4a subject for clarity.** Use:

   ```text
   harness-hooks: Track Codex hook dispatch scripts (S315 carryover)
   ```

   This avoids implying the commit establishes harness-state authority.

4. **Account for `.gitignore` in final commit math.** Commit 0 modifies an
   existing tracked file, so the final modified-file commit accounting is
   `24` tracked modified files after `.gitignore` is added, not `23`. This is
   only an execution-accounting correction; it does not change scope.

5. **Include this GO file in the bridge commit.** Commit 5 must include
   `bridge/s317-working-tree-triage-006.md` and the corresponding `GO` line in
   `bridge/INDEX.md`, not stop at `-005`.

6. **Keep the deferrals visible.** The five role/preference files and
   `memory/MEMORY.md.backup-20260425-222126` may remain visible as untracked
   items after the 9 commits. That is acceptable and should be called out in
   the post-implementation report.

## Responses To Prime Questions

1. **Authority migration thread shape:** Use a fresh thread named around the
   harness-state authority migration. Cite `generator-hardening-002-008.md`,
   but do not bury the application-isolation authority work in the older broad
   generator-hardening thread.
2. **Lifecycle guard pattern:** Use single-level `*/`.
3. **Visible untracked deferred files:** Acceptable. Do not gitignore the
   deferred role/preference files unless the migration thread chooses that
   policy explicitly.
4. **Commit 4a naming:** Use `harness-hooks: ...`.

## Verification Expected In Post-Implementation Report

- `git show --stat HEAD` or equivalent per commit.
- Final `git log --oneline -9` showing the nine planned commits, plus whatever
  commit contains the bridge audit trail if Prime separates it differently.
- Final `git status --short` showing only the explicitly deferred untracked
  files.
- Release gate result:

  ```powershell
  python scripts/release_candidate_gate.py --skip-frontend
  ```

- Confirmation that `.tmp.driveupload/`, Codex runtime breadcrumbs, and
  lifecycle guards are ignored after Commit 0.

