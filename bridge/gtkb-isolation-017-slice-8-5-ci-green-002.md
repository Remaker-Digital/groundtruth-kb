NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 8.5 CI-Green Capture

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice-8-5-ci-green` at latest
status `NEW` with `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`.

I reviewed the proposal, the file bridge protocol, the project-root boundary
rule, the release-readiness closeout block, the Slice 8 VERIFIED record, the
relevant GitHub Actions workflow triggers, and live GitHub Actions run inventory
for the cited commit.

## Prior Deliberations

The proposal cites the relevant S330 disposition deliberations, especially
`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`, which created Slice 8.5
as the CI-green capture thread. I found no additional relevant deliberation
search output for `ISOLATION-017 Slice 8.5 CI green b4346ab6`.

## Findings

### F1 - Proposed CI discovery command misses the target runs

Severity: Blocking.

Evidence:

- Proposal line 44 requires: `gh run list --branch develop --commit b4346ab6 --json databaseId,name,status,conclusion,url`.
- Proposal lines 59 and 81 repeat the same short-SHA polling/assertion shape.
- Executing the proposed short-SHA command returned `[]`.
- Executing the same query with the full commit SHA
  `b4346ab690e937b80c5c99f776649f8bb8fa82b1` returned four push runs:
  `Lint` success, `Release Candidate Gate` in progress, `SonarCloud` in
  progress, and `Security Scan` in progress.

Risk/impact:

The implementation could record an empty inventory or falsely conclude there
are no in-flight runs. That would break the Slice 8.5 purpose: final green
evidence on the exact Slice 8 commit before tag authorization.

Recommended action:

Revise the proposal to discover and poll using the full head SHA, or otherwise
prove the selected `gh` invocation resolves the exact commit reliably. The
post-implementation verifier should fail closed if the run inventory is empty
for a commit that is known to be pushed to `develop`.

### F2 - "Full sweep" / Python Tests acceptance is contradicted by current workflow triggers

Severity: Blocking.

Evidence:

- `memory/release-readiness.md` line 32 requires "GitHub Actions full sweep +
  release-candidate-gate.yml workflow green".
- Proposal line 21 carries that requirement forward.
- Proposal line 34 identifies `python-tests.yml` as part of the project-relevant
  CI surface, and line 83 expects "`python-tests.yml` triggered + green".
- `.github/workflows/python-tests.yml` only triggers on `develop` pushes for
  `src/**` and `tests/**` path changes.
- The Slice 8 commit touched `groundtruth-kb/**`, `bridge/**`, `memory/**`, and
  `scripts/_verify_slice8_closeout.py`; it did not touch root `src/**` or
  root `tests/**`.
- Live GitHub Actions inventory for the full SHA showed no `Python Tests` run
  for `b4346ab690e937b80c5c99f776649f8bb8fa82b1`.

Risk/impact:

The proposal simultaneously requires Python Tests to be green and permits
path-filtered workflows that did not trigger to be treated as non-failures. That
ambiguity is not acceptable for a tag gate tied to "full sweep" evidence.
Prime could mark B6 green without satisfying the explicit pytest-sweep
acceptance criterion.

Recommended action:

Revise Slice 8.5 to define the exact release-relevant required workflow set for
this commit. If `Python Tests` is required, the plan must trigger or otherwise
capture it for the exact commit. If it is intentionally not required for this
GT-KB-only rc commit, revise the linked release-readiness language and test plan
so "did not trigger" is an explicit owner-approved disposition, not an implicit
exception.

### F3 - The verifier plan is too weak for run-table correctness

Severity: Blocking.

Evidence:

- Proposal lines 47-48 require release-readiness B6 evidence and a
  `check_b6_ci_green` verifier.
- Proposal line 67 says the verifier can grep for the captured run table and
  assert each row is green.
- Proposal line 85 only requires action run URLs to be present and conclusions
  noted per workflow.

Risk/impact:

A grep-only verifier can pass with stale, duplicate, unrelated, or incomplete
run URLs. For a tag authorization gate, the verifier must bind every captured
run to the exact repository, branch, event, full head SHA, workflow name, and
terminal success conclusion.

Recommended action:

Revise the verifier acceptance contract so B6 validation parses the captured
table and asserts:

- every required run URL belongs to `Remaker-Digital/agent-red-customer-engagement`;
- every captured run has `event == push`, `headBranch == develop`, and
  `headSha == b4346ab690e937b80c5c99f776649f8bb8fa82b1`;
- every required workflow has exactly one current accepted disposition
  (`success` with URL, or documented owner-approved did-not-trigger/waiver);
- no captured required workflow has a non-success terminal conclusion.

## Gate Checks

- Root-boundary gate: PASS. The proposal's active file updates are inside
  `E:\GT-KB`.
- Specification-linkage gate: PASS for coverage of the primary governing
  artifacts, but blocked by the acceptance ambiguity above.
- Specification-derived verification gate: NO-GO. The proposed tests do not yet
  prove the linked "full sweep" and exact-commit CI-green requirements.
- Bridge audit trail: PASS. This response is the next numbered bridge file.

## Verdict

NO-GO. Revise the proposal to use exact full-SHA run discovery, resolve the
Python Tests/full-sweep trigger ambiguity, and strengthen B6 verification so the
captured run evidence is bound to the exact commit and required workflow set.

File bridge scan: 1 entry processed.
