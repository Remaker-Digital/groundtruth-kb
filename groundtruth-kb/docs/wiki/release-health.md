# Release Health

This page is the wiki-ready source for GT-KB release-health evidence. It is
published from `groundtruth-kb/docs/wiki/release-health.md` into the
`Remaker-Digital/groundtruth-kb` GitHub Wiki as `Release-Health.md`.

The wiki copy is a publication target only. The in-root markdown file remains
the GT-KB source artifact.

## Release-Health Gates

GT-KB release readiness is not a single green counter. The dashboard release
health view combines these evidence classes:

| Evidence | Source | Release meaning |
| --- | --- | --- |
| Dirty worktree paths | `git status --short --branch` | Changed paths must be classified before release commit or push. |
| Bridge actionability | TAFE/dispatcher state plus numbered `bridge/*.md` files | Latest `GO`, `NO-GO`, `NEW`, or `REVISED` work means the bridge is still active. |
| Dispatcher daemon health | `gt bridge dispatch health/status/daemon status --json` | WARN or FAIL states block a clean release-health claim. |
| CI and workflow runs | GitHub Actions for `Remaker-Digital/groundtruth-kb` on `main` | Recent failures, unavailable live state, and absent workflows are distinct states. |
| README/wiki drift | `scripts/update_wiki_pages.py compare` | Published wiki pages must match in-root source docs before release signoff. |
| Governed release gate | `scripts/release_candidate_gate.py` | A release candidate needs governed local evidence or an explicit owner-approved deferral. |

Azure Container Apps reconciliation is not part of the default GT-KB release
gate. It is an optional adopter diagnostic and only runs when
`GTKB_DASHBOARD_AZURE_RECONCILE=1` is set for the dashboard refresh process.

## Dashboard Semantics

The dashboard must not report `release_blockers = 0` solely because a cached
readiness note says no blockers. Live git, bridge, dispatcher, workflow, and
wiki comparison findings are release-health blockers when they indicate
unclassified or unresolved release-scope work.

`current_metrics.release_blockers` therefore reflects the larger of:

- the release-readiness model's explicit blocker count;
- explicit blocker messages; and
- live release-health findings gathered during dashboard refresh.

## GitHub Workflow State

GitHub workflow health is classified rather than collapsed into one unknown
state:

| State | Meaning |
| --- | --- |
| `passing` | A recent completed run for the relevant workflow and branch succeeded. |
| `failing` | A recent completed run failed, timed out, was cancelled, or requires action. |
| `running` | A run is in progress. |
| `no_recent_run` | The workflow exists locally, but no recent run was returned. |
| `not_wired` | The workflow or required local configuration is absent. |
| `manual` | The gate is intentionally local/manual and no workflow run is expected. |
| `live_state_unavailable` | `gh` is unavailable, unauthenticated, rate-limited, or otherwise unable to query. |

The GT-KB release branch is `main` unless a future release proposal explicitly
selects another branch.

## README and Wiki Comparison

Use the in-root wiki comparison tool:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki
```

To refresh the local wiki checkout from in-root source pages:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py update --wiki-dir .tmp/groundtruth-kb.wiki
```

The updater does not push. Any wiki publish step is a separate external Git
operation and must use the in-root source pages as the content source.

Live git, dispatcher, and GitHub workflow probes are opt-in during dashboard
refresh:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root E:\GT-KB --probe-live
```

Use live probes for release signoff only after confirming the host-local
dispatcher and GitHub CLI probes are healthy.

## Release Signoff Rule

A clean release-health claim requires all of the following:

- dashboard release-health findings are zero or explicitly dispositioned;
- the worktree is clean except for intentionally staged release artifacts;
- bridge state has no unresolved release-scope Prime or Loyal Opposition work;
- dispatcher daemon/control-surface health is not WARN or FAIL;
- required `main` workflow evidence is passing or explicitly deferred; and
- README and wiki source comparisons are current.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
