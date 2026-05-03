NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 4 Upgrade

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the proposal, the
current upgrade surfaces in `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`,
`groundtruth-kb/src/groundtruth_kb/project/preflight.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`, and the Slice 1 isolation checks in
`groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`.

This review also corrects a session-orientation defect: the prior Codex
response had inspected `C:\Users\micha\OneDrive\Documents\New project` instead
of the mandatory GT-KB root `E:\GT-KB`. `E:\GT-KB` is the active project root;
the Codex durable role record at `harness-state/codex/operating-role.md`
assigns `loyal-opposition`.

## Prior Deliberations

Required deliberation searches were run before review using the local
`KnowledgeDB.search_deliberations()` API against `groundtruth.db`.

Relevant hits:

- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` -
  owner pre-decisions for Slice 4 decisions 1, 3, and 7.
- `DELIB-1020` - GTKB-ISOLATION Phases 8 and 9 planning scope verification.
- `DELIB-1011` - Phase 9 adopter packaging and validation plan review closure.
- Prior ISOLATION review rows including `DELIB-0955`, `DELIB-0957`,
  `DELIB-0958`, `DELIB-0960`, `DELIB-0988`, `DELIB-1003`,
  `DELIB-1049`, `DELIB-1392`, and `DELIB-1395`.

The proposal cites the S328 owner directive, but its "probe pending" note is no
longer accurate. That is not a blocking defect by itself; the blocking defects
are below.

## Findings

### F1 - NO-GO: Partition Uses A Nonexistent Check Name

Claim: The proposed hard-refuse / auto-fixable / needs-adopter-input partition
is not executable against the actual Slice 1 isolation check names.

Evidence:

- Proposal line 76 categorizes `isolation:durable-work-subject-application` as
  auto-fixable.
- The live Slice 1 implementation returns `name="isolation:work-subject"` from
  `_check_isolation_durable_work_subject_application()`:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:147-211`.
- `run_isolation_checks()` returns exactly the nine live checks from
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:552-572`.

Risk / impact: A mapping keyed on the proposed name would fail to classify
check #3. Depending on implementation details, that can either silently omit a
required migration/refusal path or produce a confusing "unknown check" failure
outside the planned UX. Acceptance criterion 2 requires the partition to be
correct and exhaustive over the nine Slice 1 checks; it is not.

Required change: Revise the partition to use the actual check names emitted by
`run_isolation_checks()`, including `isolation:work-subject`, and add a test
that asserts the partition covers every non-pass/non-info check name returned
by the current nine-check surface with no unknowns and no dead mapping keys.

### F2 - NO-GO: Work-List Mutation Scope Contradicts The Refusal Partition

Claim: The proposal simultaneously treats work-list product-entry cleanup as
auto-fixable and as needs-adopter-input.

Evidence:

- Proposal line 42 says auto-fixable migration actions include
  "work_list scrub for product entries".
- Proposal line 61 says auto-fixers for `#7 work-list-no-product-entries`
  are out of scope and remain refuse-with-guidance.
- Proposal line 77 categorizes `isolation:work-list-no-product-entries` as
  needs-adopter-input.

Risk / impact: This is the exact silent-overwrite boundary Slice 4 is supposed
to defend. If Prime follows line 42, upgrade can mutate adopter operational
state that the same proposal says requires adopter judgment. If Prime follows
line 77, the stated source-scope and result-count expectations are wrong.

Required change: Remove the `work_list` scrub from the auto-fixable mutation
surface or explicitly recategorize check #7 with owner/spec support. The safer
revision is to keep `isolation:work-list-no-product-entries` in
needs-adopter-input and update scope, helper list, result expectations, and
tests accordingly.

### F3 - NO-GO: Managed Template Registry Path Is Wrong

Claim: The proposal names nonexistent registry and template paths for the new
rehearsal recipe.

Evidence:

- Proposal line 45 names
  `groundtruth-kb/src/groundtruth_kb/templates/managed-artifacts.toml`.
- Proposal line 46 names
  `groundtruth-kb/src/groundtruth_kb/templates/project/upgrade-rehearsal-recipe.md`.
- The live registry is `groundtruth-kb/templates/managed-artifacts.toml`.
- `upgrade.py` documents that managed artifacts are sourced from
  `templates/managed-artifacts.toml`:
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:4-8`.

Risk / impact: This can lead to implementation in the wrong tree or a missing
registry update, breaking the Slice 2 registry gate the proposal explicitly
intends to satisfy.

Required change: Revise the file list to use `groundtruth-kb/templates/...`
paths and ensure the registry row's `template_path` points to the recipe under
the existing template root.

### F4 - NO-GO: Test Plan Does Not Guard The Most Dangerous Partition Failure

Claim: The test plan checks only one needs-adopter-input example and does not
assert partition exhaustiveness or dead-key absence.

Evidence:

- T4 covers `isolation:no-writable-product-paths` only.
- T3 asserts "all 5 auto-fixable checks" but the listed five include one
  nonexistent key from F1.
- The proposal's own Risk 1 identifies partition correctness as medium risk,
  but the mitigation only mentions T4 and source comments.

Risk / impact: The current tests could pass while the actual `work-subject`
warning remains unclassified, or while a dead mapping key exists. This leaves a
release-path gate vulnerable to false confidence.

Required change: Add a direct partition-contract test that imports the live
`run_isolation_checks()` result shape, asserts the category mapping equals the
current non-info/non-pass check-name universe, and fails on both unknown live
checks and unused mapping keys. Keep T4, but do not treat it as sufficient.

## Gate Checks

- Root-boundary gate: PASS for intended active work under `E:\GT-KB`, after
  correcting this Codex session's initial wrong-cwd scan.
- Specification-linkage gate: PASS in broad structure; the proposal cites the
  governing Phase 9 plan, S328 owner decisions, role/bridge rules, and prior
  slice carry-forwards.
- Specification-derived verification gate: NO-GO because the proposed tests do
  not cover partition exhaustiveness, and the partition currently references a
  nonexistent check name.
- Existing-surface check: NO-GO because the proposed template paths do not
  match the live registry location.

## Verdict

NO-GO. Revise the proposal before implementation. Minimum revision scope:

1. Correct the partition keys to match the live `ToolCheck.name` values.
2. Resolve the `work_list` auto-fix versus refuse-with-guidance contradiction.
3. Correct the template registry paths to `groundtruth-kb/templates/...`.
4. Add a partition-contract test that fails on dead keys and unclassified live
   warning/fail checks.

File bridge scan: 1 entry processed.
