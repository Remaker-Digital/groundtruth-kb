# Release Health

This is the in-repository source for the published release-health wiki page.
The dashboard provides observations about the selected host and application.
A completed refresh or a green aggregate does not establish release acceptance.

## Current observations

| Evidence | Source | Meaning |
| --- | --- | --- |
| Worktree changes | `git status --short --branch` | Classify changed release-scope paths before committing; unrelated work remains separate. |
| Native service | Configured authority status | Unavailable or unready authority is reported explicitly. |
| Native bridge coordination | `gt bridge state-report --json` | Reports exact active claims and eligible/blocked role queues. Queue observation does not dispatch work or establish release readiness. |
| Workflow runs | The selected repository's configured workflow integration | A passing run, a failing run, an in-progress run and unavailable live state are different observations. |
| Published documentation | `scripts/update_wiki_pages.py compare` | Compares the local wiki checkout with repository source pages. |
| Candidate qualification | `scripts/release_candidate_gate.py` and the applicable test results | Required checks must pass on the candidate being released. |

Live probes are opt-in:

```powershell
gt --config E:\GT-KB\groundtruth.toml dashboard refresh --runtime-root E:\GT-KB\.groundtruth\dashboard-health --json --probe-live
```

The native probes read service readiness and bridge state from the selected
configuration. Missing or malformed bridge results are reported as unavailable
or malformed. Active claims and blocked actions remain visible. Local bridge
files and an old readiness note do not replace those observations.

The dashboard combines explicit blocker counts/messages with current
release-health findings. Its runtime database and rendered views are derived
outputs, not canonical authority. Application deployment and infrastructure
values depend on the application's connector; demonstration data is not a
measurement of a live deployment.

## Workflow state

| State | Meaning |
| --- | --- |
| `passing` | The relevant completed run succeeded. |
| `failing` | The run failed, timed out, was cancelled or requires action. |
| `running` | The run is in progress. |
| `no_recent_run` | A configured workflow has no recent result. |
| `not_wired` | Required workflow or local configuration is absent. |
| `manual` | The selected check runs locally and no workflow run is expected. |
| `live_state_unavailable` | The integration cannot obtain current results. |

Evaluate the repository and revision selected for the release. A historical
run on another revision does not qualify current bytes.

## Compare published documentation

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py update --wiki-dir .tmp/groundtruth-kb.wiki
```

The updater changes the local wiki checkout and does not push. Publication is
a separate external Git operation using the repository pages as its source.

## Release assessment

Use the applicable project requirements, exact qualification results,
independent review and native commit checks to assess a release. Investigate
reported blockers and distinguish missing evidence from a passing result.
The dashboard's observations help locate that work; they do not waive it,
approve a commit or authorize an installation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
