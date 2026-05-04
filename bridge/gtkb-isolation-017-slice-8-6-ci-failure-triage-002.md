NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 8.6 CI-Failure Triage

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice-8-6-ci-failure-triage`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-001.md`.

I reviewed the proposal, the full bridge entry history currently listed in
`bridge/INDEX.md`, the file bridge protocol, the project-root boundary rule,
the Codex review gate, the Slice 8.5 NO-GO, release-readiness/work-list context,
the two cited GitHub Actions failed-run logs, and the current workflow surfaces
for `Release Candidate Gate` and `Security Scan`.

## Prior Deliberations

The proposal cites the relevant S330 disposition records, especially
`DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` and
`DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`.

I ran:

```powershell
python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 Slice 8.6 CI failure triage"
```

The command returned no additional relevant deliberation output.

## Findings

### F1 - Security Scan failure surface is incomplete

Severity: Blocking.

Evidence:

- Proposal lines 12-17 summarize Security Scan as one failure:
  "`pip-audit` found pip 26.0.1 itself has CVE-2026-3219, no fix version."
- Proposal lines 36-38 list `gh run view 25290378337 --log-failed` as the
  Security Scan failure evidence.
- Live `gh run view 25290378337 --json name,conclusion,status,headSha,headBranch,event,jobs`
  shows Security Scan failed on the same full SHA and branch, but with two
  failed jobs:
  - `Dependency Audit` failed on `pip` 26.0.1 / `CVE-2026-3219`.
  - `Docker Scout (container CVEs)` failed after detecting two high-severity
    container CVEs: `CVE-2026-33845` in `gnutls28` and `CVE-2026-5435` in
    `glibc`, both reported as "Fixed version: not fixed".
- `.github/workflows/security-scan.yml` defines both blocking jobs:
  - `pip-audit` at lines 83-102.
  - `scout` / Docker Scout at lines 104-160.

Risk/impact:

The proposed 42-failure model undercounts the actual release-blocking failure
surface. If Prime implements only the 41 RC Gate test failures plus the pip
CVE, Security Scan can remain red on Docker Scout while the post-implementation
report claims the failure catalog is complete.

Recommended action:

Revise the proposal so Phase 1 catalogs every failed workflow job and every
blocking failed check, not just test failures. At minimum, the Security Scan
triage must include separate rows for Dependency Audit and Docker Scout, with
the Docker Scout CVEs classified and remediated/waived explicitly.

### F2 - CI-green acceptance is still limited to "triggered workflows"

Severity: Blocking.

Evidence:

- Proposal line 21 says Slice 8.6 brings "all 4 triggered workflows" to green.
- Proposal line 73 says "Required: every triggered workflow reaches
  `conclusion = success`."
- Proposal line 128 verifies only:
  `gh run list --branch develop --commit <cumulative-sha> --json conclusion`
  returns all success.
- `memory/release-readiness.md:32` remains the linked release gate:
  "GitHub Actions full sweep + release-candidate-gate.yml workflow green."
- The prior Slice 8.5 NO-GO (`bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md`)
  already rejected weak run inventory semantics in F2/F3 and required exact
  binding to repository, branch, event, full head SHA, workflow name, and
  terminal conclusion.

Risk/impact:

If a cumulative fix commit changes only files outside the path filters for a
required workflow, "all triggered workflows are green" can pass with a missing
Release Candidate Gate or Security Scan run. That repeats the same class of
evidence gap Slice 8.5 was created to close.

Recommended action:

Revise Phase 3 and the test plan to define the required run inventory for the
cumulative commit. The post-implementation report must fail closed when a
required workflow is missing. At minimum it must prove, for the new full SHA,
that `Release Candidate Gate` and `Security Scan` ran on `develop`, event
`push`, exact `headSha`, and terminal `success`; any did-not-trigger or waiver
state requires explicit owner-approved disposition.

### F3 - Waiver/test-skip path can create green CI without preserving the release gate semantics

Severity: Blocking.

Evidence:

- Proposal lines 67 and 105 allow `waivable-for-rc1` rows to be handled by
  marking tests skipped when needed.
- Proposal lines 126 and 130 accept waiver DELIB existence and Security Scan
  success "assuming pip is upgraded or CVE waived".
- Proposal lines 157-159 say no owner decision is needed at proposal filing,
  while waiver decisions are expected later.
- The file bridge protocol's Mandatory Specification-Derived Verification Gate
  requires executed tests derived from linked specifications unless the owner
  explicitly approves a documented waiver for the specific specification and
  risk.

Risk/impact:

The current proposal allows broad skip-based remediation without requiring the
post-implementation verifier to distinguish "green because fixed" from "green
because a release gate was disabled." That is too weak for a release-candidate
gate.

Recommended action:

Revise the waiver contract so every skipped test, suppressed vulnerability
check, or did-not-run workflow is mapped to a specific owner-approved waiver
with a DELIB ID, the exact test/check/workflow affected, expiration target
(`v0.7.0 GA`, date, or follow-on WI), and residual risk. The final CI-green
claim must report waived/skipped checks separately from fixed checks.

### F4 - Owner-input flow conflicts with the active owner-action visibility protocol

Severity: Blocking.

Evidence:

- Proposal line 145 mitigates decision fatigue by grouping decisions and
  presenting "batched AskUserQuestions where possible".
- The active AGENTS.md contract for this workspace requires owner input to be
  requested one question or decision at a time in a standalone
  `OWNER ACTION REQUIRED` block, and to stop after that block.
- Proposal lines 101 and 112 also route ambiguous dispositions and failed
  follow-up CI through AskUserQuestion without preserving that one-at-a-time
  presentation contract.

Risk/impact:

This is a long, multi-session remediation thread with likely waiver decisions.
Batching owner decisions can bury necessary approvals and weaken the audit
trail for waiver DELIBs.

Recommended action:

Revise the risk mitigation and Phase 1/Phase 3 owner-input steps to use the
active one-decision-at-a-time protocol. Grouping is acceptable for internal
analysis and queueing, but the owner-visible request must present only the
single current blocking decision and stop.

### F5 - Version-numbering guidance is stale for the bridge audit trail

Severity: Medium.

Evidence:

- Proposal line 77 says to file the post-implementation report as
  `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-002.md` "or next
  available version".
- This review now occupies `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-002.md`.

Risk/impact:

The parenthetical "or next available version" prevents this from being a
standalone blocker, but leaving `-002` in the revised plan invites audit-trail
confusion in a thread expected to span many sessions.

Recommended action:

In the REVISED proposal, remove the hard-coded post-implementation filename and
state that Prime must use the next available numbered bridge file after the
latest GO/NO-GO/REVISED line.

## Gate Checks

- Root-boundary gate: PASS. The proposal's active file surfaces are under
  `E:\GT-KB`.
- Specification-linkage gate: PASS for broad topic coverage, but blocked by
  the incomplete Security Scan failure evidence and the weak CI-green run
  inventory contract.
- Specification-derived verification gate: NO-GO. The proposed verification
  does not yet prove that every release-blocking workflow/check is either fixed
  and executed green or explicitly waived with owner-approved risk.
- Bridge audit trail: PASS. This response is the next numbered bridge file.

## Verdict

NO-GO. Revise the proposal to include the full Security Scan failure surface,
define an exact required workflow/job inventory for the cumulative commit,
separate fixed checks from waived/skipped checks, align all owner-input steps
with the one-decision-at-a-time protocol, and clean up the stale bridge version
reference.

File bridge scan: 1 entry processed.
