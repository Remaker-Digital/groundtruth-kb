NO-GO

# Loyal Opposition Review - GTKB Dashboard Industry Alignment Slice 2.2 (Metrics)

**Date:** 2026-04-24
**Document:** `gtkb-dashboard-industry-alignment-slice2b-metrics`
**Reviewed file:** `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md`
**Verdict:** NO-GO

## Prior Deliberations

No relevant prior deliberations found for `GTKB-DASHBOARD-002`, `coverage trend`, or `dashboard metrics` in the Deliberation Archive search against `groundtruth.db`. Generic matches on `security posture` were unrelated to this dashboard slice and did not carry a prior decision on this proposal.

## Claim

The proposed reuse of existing dashboard tables is the right direction, but the source-contract section is not yet grounded in the repo's actual current evidence. As written, the coverage design adds unnecessary CI churn on top of an already-existing merged artifact, and the chosen authoritative security source is not executable in the current repository/auth state.

## Findings

### Finding 1 (HIGH) - The coverage source contract is based on a stale CI premise and proposes an unnecessary new aggregation path

**Evidence**

- The proposal says current state only emits per-shard coverage and therefore needs a new `coverage-combine` job plus a new `coverage-combined` artifact before the fetch can work: `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md:32`, `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md:54-57`, and `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md:119-125`.
- The live workflow already has a merge section headed `# Merge coverage from all shards + generate report`: `.github/workflows/python-tests.yml:139-220`.
- That existing merge logic already writes `coverage-merged.json`: `.github/workflows/python-tests.yml:216-219`.
- The workflow already uploads the merged artifact today: `.github/workflows/python-tests.yml:412-419`.
- The local startup/dashboard integration model already treats `coverage-merged.json` as a configured artifact for the Python test integration: `scripts/session_self_initialization.py:1888-1901`.

**Risk / impact**

The proposal adds avoidable CI scope and renames the artifact contract without first proving the current merged artifact is insufficient. That creates unnecessary delivery risk in the Python test pipeline and obscures the simpler path: consume the existing merged coverage output already produced by the repo.

**Required action**

Revise the proposal to use the existing merged coverage artifact and current workflow shape unless there is a concrete, cited defect in that artifact. If a rename or new aggregation job is still required, state exactly why the current `coverage-merged.json` / `coverage-merged-*` path is inadequate.

### Finding 2 (HIGH) - The proposal's authoritative Dependabot-alert source is not currently available in this repository/auth posture

**Evidence**

- The proposal makes `gh api /repos/<owner>/<repo>/dependabot/alerts?...` the authoritative security source and says no owner auth provisioning is needed: `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md:59-63` and `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md:275-277`.
- Live verification on 2026-04-24 failed:
  - `gh api "/repos/Remaker-Digital/agent-red-customer-engagement/dependabot/alerts?state=open&per_page=1"` -> HTTP 403 with `"Dependabot alerts are disabled for this repository."`
  - the CLI also reported the current auth lacks the required scope and suggested `gh auth refresh -h github.com -s admin:repo_hook`.
- By contrast, the repo's existing GitHub Actions query path is available right now:
  - `gh run list --repo Remaker-Digital/agent-red-customer-engagement --workflow python-tests.yml --branch main --status success --limit 1 --json databaseId,headSha,displayTitle` -> exit 0 with a current successful run.

**Risk / impact**

The primary security ingest path cannot run under the current repo configuration and local auth state. That means the slice's security half would degrade to permanent unknown/no-data behavior, while the proposal currently frames the path as ready and owner-independent.

**Required action**

Revise the security-source contract to one of:

1. a source that is currently available in this repo/auth posture, or
2. an explicit prerequisite step that enables Dependabot alerts and secures the required API scope before this slice is implemented.

Do not treat the current Dependabot-alert API path as execution-ready until that prerequisite is addressed.

## Recommended Action

Keep the no-new-table direction, but revise the source contract before GO:

- coverage should start from the existing merged coverage artifact already emitted by `python-tests.yml`,
- security should use a currently executable source path or explicitly declare the prerequisite to enable the Dependabot alerts API.

## Decision Needed From Owner

None in this review. The blocking issue is proposal correctness against current repo state, not a new product/policy choice.
