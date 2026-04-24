NEW

# GT-KB Mass Adoption Readiness Phase A Proposal

target_paths: ["memory/work_list.md", "memory/release-readiness.md", "docs/gtkb-dashboard/session-startup-report.md", "docs/gtkb-dashboard/dashboard-data.json", "docs/gtkb-dashboard/index.html", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/", "scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_groundtruth_governance_adoption.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_standing_backlog_harvest.py", "scripts/release_candidate_gate.py"]

## Status

NEW - Loyal Opposition review requested before implementation.

## Requested Verdict

GO to execute the narrow Phase A readiness inventory and first commit-scope
isolation work, or NO-GO with required revisions.

This proposal does not request approval to commit, push, merge, deploy, mutate
formal artifacts, rotate credentials, purge git history, or apply GT-KB
scaffold changes.

## Claim

Prime Builder should start `GTKB-MASS-001` with a current-state evidence refresh
and first-scope isolation pass before any commit, push, merge, or mass-adoption
claim.

The source plan from 2026-04-20 is still directionally correct, but some of its
numeric evidence is stale. Phase A should reconcile the plan with the current
dashboard/startup evidence, classify the dirty worktree, and produce a concise
implementation handoff that identifies the first safe commit/review scope.

## Prior Deliberations

Deliberation search was run before this proposal.

Relevant records:

- `DELIB-0758`: VERIFIED `gtkb-mass-adoption-readiness` developer-preview MVP
  bridge thread. It explicitly did not prove mass-adoption readiness.
- `DELIB-0757`: VERIFIED GT-KB adoption-gap closure thread, relevant to
  managed adoption and scaffold drift.
- `DELIB-0785`: VERIFIED GT-KB release-readiness thread, relevant to release
  discipline and evidence gates.
- `DELIB-0633`: GroundTruth-KB strategic assessment; still relevant because it
  cautions against overstating adoption readiness.
- `DELIB-0835`: strict artifact approval and audit-trail rule for formal
  artifacts and Deliberation Archive changes.

## Governing Evidence

- `memory/work_list.md` records `GTKB-MASS-001` as TOP after `GTKB-GOV-012`
  is proposed/reviewed or explicitly paused.
- `bridge/gtkb-proposal-verification-gates-002.md` now gives GO for
  `GTKB-GOV-012`, with binding conditions for the portable proposal and
  verification gate implementation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20.md`
  defines the ordered mass-adoption readiness program.
- Current startup evidence in `docs/gtkb-dashboard/session-startup-report.md`
  says:
  - release blockers: 0
  - active backlog items: 3
  - open MemBase work items: 29
  - drift changed paths: 8
  - testing/tool rollup: 0 failing, 6 manual, 16 ready/passing
  - GT-KB package: 0.6.1, dry-run upgrade plan available
- Current `git status --short` shows a broad dirty tree with governance,
  dashboard, bridge, release-gate, commercial integration, and test changes.
  That makes immediate commit/push unsafe without scope classification.

## Problem

The mass-adoption plan cannot be executed safely as a single undifferentiated
work item. The working tree contains unrelated or differently governed changes,
and the 2026-04-20 plan evidence no longer matches the current startup report.

If Prime Builder jumps directly to commit/push/merge readiness, it risks:

1. mixing bridge proposals, dashboard lifecycle work, commercial integration
   work, and GT-KB adoption drift into one review package;
2. preserving stale release-blocker/tool-integration counts;
3. claiming GT-KB mass-adoption readiness based on developer-preview or
   dashboard evidence alone;
4. losing the distinction between Agent Red dogfooding readiness, private beta,
   and public adoption readiness.

## Scope In

Phase A should perform only:

1. Current evidence refresh:
   - read startup report/dashboard data;
   - read release-readiness memory;
   - read standing backlog;
   - read bridge latest statuses;
   - run lightweight current-state commands where safe.
2. Dirty path inventory:
   - classify changed paths into:
     - bridge/proposal artifacts;
     - startup/dashboard lifecycle;
     - GT-KB scaffold/adoption;
     - release-gate/governance checks;
     - commercial integration durability;
     - unrelated or owner-held work;
     - unknown/manual-review-needed.
3. First commit/review scope recommendation:
   - identify the smallest coherent package that could be committed or pushed
     after review;
   - list files that must be excluded from that first package;
   - list required checks for that package.
4. Acceptance-gate refresh:
   - compare the 2026-04-20 plan counts with current dashboard/startup counts;
   - identify any stale evidence that must be updated or superseded.
5. Additive report:
   - write a new report under
     `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`;
   - include claim, evidence, risk/impact, recommended action, and owner
     decisions needed.

## Scope Out

1. No commit.
2. No push.
3. No merge.
4. No production/staging deployment.
5. No credential lifecycle work.
6. No git-history purge.
7. No `gt project upgrade --apply`.
8. No formal DA, GOV, SPEC, PB, ADR, or DCL mutation.
9. No commercial-readiness NO-GO revisions, because the bridge index pause note
   says those tracks remain paused until the owner explicitly unpauses them.
10. No implementation of `GTKB-GOV-012` or `GTKB-CORE-001` under this proposal;
    those have separate bridge threads.

## Proposed Implementation Plan

### Step 1 - Capture Current Baseline

Run/read:

```powershell
git status --short
git branch --show-current
git rev-parse --short HEAD
Get-Content -Raw docs/gtkb-dashboard/session-startup-report.md
Get-Content -Raw docs/gtkb-dashboard/dashboard-data.json
Get-Content -Raw memory/work_list.md
Get-Content -Raw memory/release-readiness.md
Get-Content -Raw bridge/INDEX.md
```

If dashboard JSON is too large, parse only the fields needed for release
blockers, active backlog items, drift paths, tool integrations, and action
center entries.

### Step 2 - Classify Dirty Paths

Produce a table with columns:

- path;
- status;
- category;
- apparent workstream;
- first-scope inclusion recommendation;
- required verification;
- owner decision needed.

Do not stage or revert anything.

### Step 3 - Refresh Readiness Claims

Compare:

- 2026-04-20 plan evidence: 7 blockers, 8 failing integrations, 3 unknown
  integrations, 11 changed paths, 21 scaffold actions;
- current startup evidence: 0 blockers, 0 failing integrations, 2 unknown
  integrations, 8 changed paths, GT-KB 0.6.1 dry-run available.

Classify each difference as:

- resolved with evidence;
- stale dashboard/report value;
- current but renamed/reclassified;
- unknown and needs command verification;
- owner decision needed.

### Step 4 - Recommend First Review Package

The expected default recommendation is likely one of:

1. bridge/proposal artifacts only;
2. startup/dashboard lifecycle artifacts;
3. GT-KB scaffold/adoption current-main integration;
4. release-gate/governance test updates.

The report must justify the recommendation by blast radius and verification
cost, not by convenience.

### Step 5 - Record Additive Report

Create a report named with a timestamp, for example:

```text
independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-PHASE-A-YYYY-MM-DD-HH-mm.md
```

Required report sections:

- Claim;
- Evidence;
- Dirty Path Classification;
- Stale Evidence Reconciliation;
- First Commit/Review Scope Recommendation;
- Required Verification;
- Owner Decisions Needed;
- Explicit Non-Claims.

## Verification Plan

Phase A should verify the report and not the whole readiness program.

Run:

```powershell
git diff --check -- bridge/INDEX.md bridge/gtkb-mass-adoption-readiness-phase-a-001.md
python -m pytest tests/scripts/test_standing_backlog_harvest.py -q --tb=short
```

Run only if the report recommends startup/dashboard lifecycle as the first
review package:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short
python scripts/release_candidate_gate.py --skip-frontend
```

Do not claim clean-adopter readiness, complete release readiness, or mass
adoption readiness from Phase A alone.

## Acceptance Criteria

Loyal Opposition should be able to verify that Phase A produced:

1. a current dirty-path classification;
2. a reconciliation of stale 2026-04-20 plan counts against current evidence;
3. a recommended first commit/review package with excluded files listed;
4. required verification commands for that package;
5. clear owner-decision blocks for any commit/push/merge, credential, history,
   commercial durability, or adoption-target decision;
6. no unapproved formal artifact mutation;
7. no staging/production deployment or git history mutation.

## Review Questions

1. Is Phase A narrow enough to execute without owner approval beyond the
   standing backlog and this bridge proposal?
2. Should the first report be allowed to recommend a bridge/proposal-only
   commit package if that is the lowest-risk path?
3. Should stale dashboard/readiness counts be corrected in place during Phase A,
   or should Phase A only report the discrepancy and leave corrections for a
   second proposal?
4. Are the proposed dirty-path categories sufficient for Loyal Opposition to
   verify scope isolation?

## Decision Needed From Owner

None at proposal time.

Implementation is blocked on Loyal Opposition `GO`. Later owner decisions will
be required before commit/push/merge, credential lifecycle actions, git-history
purge, production/staging deployment, or formal artifact mutation.
