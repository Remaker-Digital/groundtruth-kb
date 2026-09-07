---
name: gtkb-sweep-commit
description: Clear a dirty GroundTruth-KB worktree the governed way — take an ownership inventory of the changed paths, then finalize each independently verified scope through the per-work-item Git lifecycle. Use when the owner says to "sweep commit", "commit everything", "commit all changes", consolidate verified bridge work, or perform the regular GT-KB worktree cleanup. Handles GT-KB governance hooks, inventory drift, narrative-artifact approval evidence, credential scans, and verification. Does not push unless the owner explicitly asks.
metadata:
  project: groundtruth-kb
  category: operation and hygiene
  activity-envelope: ops
---
<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Activity Envelope Requirement

This is an **activity-envelope-only** skill. Use it only after the current worker has opened the respective activity-envelope(s) (e.g., 'ops', 'deliberation', or 'build') specified earlier in this document. If a request for this skill arrives outside `::open <activity-envelope>`, do not act on this skill request and inform the user that this skill is only availablewithin the specified activity envelope.


# GT-KB Sweep Commit

## Overview

Bring a dirty GT-KB worktree back to clean by finalizing each owned, independently
verified scope on its own. Ownership is established first; commits follow per work
item. Unowned and unverified paths are left in place for their owners.

## Authority

Owner decision `DELIB-202666332` ("Authorize exact VERIFIED finalization to reach a
clean worktree") governs this procedure. It authorizes local commits for
independently VERIFIED scopes whose exact implementation, report, verdict paths, or
reviewed hunks are mechanically isolated, and it requires each finalization to use
the governed path and to preserve unrelated staged and unstaged content.

`python -m groundtruth_kb.git_lifecycle` is the authorized execution boundary for
Git effects. Its operations bind to one work item and realize only that work item's
scope, which is what keeps each commit attributable and each unrelated change
untouched.

## Operating Rules

- Treat `E:\GT-KB` as the project root and do not pull live GT-KB artifacts from
  outside that root.
- Establish which work item owns a path before finalizing that path.
- Finalize one work item at a time, and only when its scope is independently
  verified.
- Leave unowned, unverified, or concurrently held paths exactly as found.
- Preserve unrelated staged and unstaged content across every operation.
- Do not push unless the owner explicitly asks for a push.
- Stop instead of finalizing if a real credential or secret finding appears in the
  content under review.

## Workflow

1. Inspect live state.

   ```powershell
   git status --short
   $paths = @(git ls-files --modified --deleted --others --exclude-standard)
   $paths.Count
   ```

   If there are no paths, report the clean worktree and stop.

2. Take an ownership inventory. For each cluster of changed paths, identify the
   owning work item and whether that scope is independently verified.

   ```powershell
   gt backlog list --contains <topic> --json
   gt bridge show <slug>
   ```

   A scope is finalizable when a work item owns it and that work item's bridge
   thread carries independent verification. Record clusters with no identified
   owner and report them; they are left in place.

3. For each finalizable work item, bind the scope through the governed lifecycle.

   ```powershell
   $python = "groundtruth-kb\.venv\Scripts\python.exe"
   & $python -m groundtruth_kb.git_lifecycle create --work-item-id <WI-NNNN> --title "<title>" --project-branch <branch>
   & $python -m groundtruth_kb.git_lifecycle attach --work-item-id <WI-NNNN>
   & $python -m groundtruth_kb.git_lifecycle validate --work-item-id <WI-NNNN>
   ```

   `validate` confirms branch existence, ancestry, and binding hash before any
   effect is realized.

4. Run required verification for that work item's scope.

   ```powershell
   & $python -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider
   & $python -m py_compile @py
   & $python -m ruff check @py
   & $python -m ruff format --check @py
   & $python -m pytest @tests -q --tb=short
   & $python scripts\check_dev_environment_inventory_drift.py --staged --allow-review-evidence
   & $python scripts\check_narrative_artifact_evidence.py --staged
   ```

   Build `$py` and `$tests` from that work item's bound scope. Broaden pytest when
   the scope touches shared infrastructure, hooks, governance validators, or test
   discovery logic.

5. Fix expected gate failures within the bound scope.

   - Ruff format drift: run `& $python -m ruff format <paths>`.
   - Inventory drift: run `& $python scripts\collect_dev_environment_inventory.py`,
     then rerun the inventory drift check.
   - Narrative-artifact evidence: generate a packet, then rerun the check:

     ```powershell
     groundtruth-kb\.venv\Scripts\gt.exe generate-approval-packet `
       --kind narrative `
       --target <protected-narrative-path> `
       --artifact-id <short-kebab-id> `
       --action update `
       --source-ref "<bridge/verdict/source evidence or owner request>" `
       --explicit-change-request "<owner-visible request>" `
       --change-reason "<why this narrative file changed>" `
       --approval-mode auto `
       --changed-by "<harness-role-id>"
     & $python scripts\check_narrative_artifact_evidence.py --staged
     ```

   - Secret scan finding: stop. Report the finding path and wait for owner
     direction; credential lifecycle is owner-managed.

6. Realize the bound scope.

   ```powershell
   & $python -m groundtruth_kb.git_lifecycle preserve --work-item-id <WI-NNNN> --message "<type(scope): message (WI-NNNN)>"
   ```

   `preserve` realizes only the bound work-item scope, so unrelated content is
   carried forward untouched. Cite every work item the message retires in the form
   `(WI-NNNN)`. If a governance hook fails, read the hook output, fix the specific
   evidence or formatting issue within the bound scope, and retry.

7. Repeat steps 3 through 6 for the next finalizable work item, then report final
   state.

   ```powershell
   git status --short
   git log -1 --format="%H%n%s"
   ```

   Final response should include each commit hash produced, the verification
   summary per scope, the paths deliberately left in place with the reason, the
   remaining clean/dirty status, and whether a push was performed.

<!--
GTKB-GOOSE-SKILL-ADAPTER-BEGIN
Generated by: scripts/harness_projection/project_harness.py
Generated at: content-addressed a46a9568a625
Canonical source: .harness-baseline-configuration/skills/gtkb-sweep-commit/SKILL.md
Canonical source sha256: a46a9568a625a76cdeb6f119f5f4e39253059ae76a3362ce9f3a398b4e71b375
GTKB-GOOSE-SKILL-ADAPTER-END
-->
