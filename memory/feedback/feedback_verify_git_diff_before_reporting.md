---
name: Verify git diff before reporting multi-file commits
description: When a commit claims to touch N files, verify via `git diff --name-status HEAD~1 HEAD | wc -l` before writing the post-impl report. Edit-tool "success" is not equivalent to "committed to git."
type: feedback
originSessionId: S302
---

**Rule:** Before reporting a multi-file commit in a post-implementation bridge, **verify the actual committed file scope** via:

```bash
git diff --name-status HEAD~1 HEAD
```

Count the lines. Compare to the expected number of files. If mismatch, investigate before claiming the report accurately describes the commit.

**Do:**
- Always run `git diff --name-status HEAD~1 HEAD` after any multi-file commit, before writing the post-impl discharge table.
- Paste the output into the post-impl report so the reviewer can verify the claim independently.
- If the count differs from the expected file list, stop and fix before claiming VERIFIED-ready status.

**Do NOT:**
- Trust the "File has been updated successfully" response from the Edit tool as evidence the change persisted to the working tree at commit time.
- Trust `git add` output alone — it reports adding an existing file even if the file's content is unchanged from HEAD.
- Write a post-impl report that names files the commit didn't actually touch.

**Why:** S302 C3 incident. I edited `docs/reference/upgrade-receipts.md` via the Edit tool, which reported success. I then ran `git add <5 files>` including that doc. The commit (`ebd0f04`) landed with only 4 files; the docs file's content on disk was reverted (likely by a subsequent `ruff format` run I did on the source files, or by some tool-level write race). My `-007` post-impl report claimed the docs file was modified and quoted the new section's line count. Codex's verification ran `git diff --name-status HEAD~1 HEAD` and `rg -n "gt project rollback" docs/reference/upgrade-receipts.md` — caught the missing docs immediately and filed NO-GO `-008`. I then filed a follow-up commit `87d174d` to add the missing section, and filed REVISED post-impl `-009` acknowledging the gap.

The root cause of the defect was trusting the Edit tool's success response as equivalent to git-level state. Codex's git-level verification is the correct discipline. Any time I stage + commit a file, I need to verify the committed content, not just the most recent tool call.

**How to apply:**

1. After any `git commit` that claims to touch multiple files, run `git diff --name-status HEAD~1 HEAD` immediately.
2. Compare the output's line count to the expected file count. If they differ, investigate.
3. For each file expected to be modified, spot-check with `git show HEAD -- <path>` or `git show HEAD:<path> | grep <expected-content>` to confirm the change landed.
4. Include the `git diff --name-status HEAD~1 HEAD` output verbatim in the post-impl report's evidence section. This lets Codex verify without re-running.
5. If a follow-up commit is needed to close a gap, acknowledge the two-commit scope explicitly in the REVISED report; don't pretend it was always one commit.

**Related memories:**
- `feedback_postimpl_report_hygiene.md` — already says "use class-qualified pytest node IDs; distinguish commit-local delta from range delta". This feedback extends that: add git-diff verification to the discipline.
- `feedback_no_deferrals_ever.md` — follow-up commits for defects are acceptable; scope-splitting to defer required work is not.
