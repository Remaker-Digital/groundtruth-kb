REVISED

# Revised Post-Rehearsal Report - GTKB Secrets Slice 3 Mirror Rehearsal

Author: Prime Builder (Codex, harness A)
Date: 2026-05-13
Bridge thread: `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan`
Prior report: `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-007.md`
NO-GO addressed: `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-008.md`

## Claim

Prime Builder revises the owner-approved mirror-only rehearsal report to add the
mandatory `## Owner Decisions / Input` section required for approval-dependent
bridge reports.

The underlying rehearsal evidence from `-007` is unchanged: Prime Builder
created a local backup bundle, cloned a fresh remote mirror, verified
`git-filter-repo`, performed the packet's target-path rewrite only inside that
mirror, and ran redacted all-refs verification before and after the mirror
rewrite.

No live remote mutation was performed. No force-push, tag rewrite, tag
deletion, branch deletion, GitHub settings mutation, credential lifecycle
operation, deployment, release, or Agent Red mutation was performed.

## Specification Links

- `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001`
- `SPEC-SEC-SCAN-REDACTION-001`
- `SPEC-SEC-SCANNER-CLI-001`
- `SPEC-SEC-CI-COVERAGE-001`
- `SPEC-DSI-COMMIT-GATE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

This report depends on a prior owner approval for mirror-only rehearsal. The
approval evidence available in this bridge thread is:

- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006.md`
  verified the Slice 3 approval packet for preparation only and stated that any
  mirror rehearsal, live history rewrite, force-push, tag operation, credential
  action, release, or deployment remained blocked until Mike gave explicit
  owner approval through a standalone `OWNER ACTION REQUIRED` flow.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-SECRETS-SLICE3-HISTORY-PURGE-APPROVAL-PACKET-2026-05-06-REV1.md`
  defined the approved decision shape. The relevant option was `Approve mirror
  rehearsal only`.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-007.md`
  records the consumed owner reply as: Mike replied `Approve mirror rehearsal`
  after the standalone `OWNER ACTION REQUIRED` block in that session.

Approved scope consumed by `-007`:

- create an in-root local backup bundle under `.gtkb-state/history-purge/`;
- clone a fresh GT-KB remote mirror under `.gtkb-state/history-purge/`;
- install or verify `git-filter-repo`;
- run redacted all-refs scans inside the fresh mirror before and after the
  mirror-only rewrite;
- run the target-path rewrite only inside the local bare mirror;
- report the resulting evidence through the bridge.

Explicit exclusions preserved by the owner-approved scope and by this revised
report:

- no live remote mutation;
- no force-push;
- no tag rewrite or tag deletion;
- no branch deletion;
- no GitHub settings or branch-protection mutation;
- no credential lifecycle action;
- no raw matched-value disclosure;
- no production deployment, release, tag publication, or PyPI publication;
- no Agent Red mutation.

This `-009` revision does not request or consume any new owner approval. It only
adds the missing mandatory owner-input section to the already-filed mirror-only
rehearsal report. Future live mutation remains blocked pending a new standalone
owner action and fresh bridge evidence.

## Prior Deliberations And Bridge State

- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` verifies Slice 1.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-004.md`
  verifies Slice 2 containment/enforcement.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006.md`
  verifies the Slice 3 approval packet for preparation only and explicitly
  blocks mirror rehearsal until standalone owner approval.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-008.md`
  found one governance-shape defect in `-007`: missing mandatory
  `## Owner Decisions / Input` section.

## Actions Performed

Created local rehearsal workspace:

- Backup root: `.gtkb-state/history-purge/20260512-152137/`
- Local all-refs backup bundle:
  `.gtkb-state/history-purge/20260512-152137/groundtruth-kb-pre-purge.bundle`
- Fresh remote mirror clone:
  `.gtkb-state/history-purge/20260512-152137/groundtruth-kb.mirror.git`

Verified tool availability:

- `python -m pip install --user git-filter-repo` reported `Requirement already satisfied`.
- `python -m git_filter_repo --version` returned `a40bce548d2c`.

Ran pre-rewrite redacted all-refs scan inside the fresh mirror:

- Report: `.gtkb-state/history-purge/20260512-152137/pre-rewrite-all-refs.json`
- Mode: `all-refs`
- Paths scanned: 6482
- Findings: 244
- Severity mix: `candidate-high: 244`
- Verified-provider findings: 0

Ran mirror-only rewrite:

```powershell
python -m git_filter_repo --force `
  --path docs/owner-messages-all.json `
  --path docs/owner-messages-batch3a.json `
  --path docs/_temp_batch3_messages.txt `
  --path docs/system-specification-extraction.json `
  --path scripts/deploy/production-gateway-generated.yaml `
  --invert-paths
```

`git-filter-repo` completed successfully in the mirror and removed the mirror's
`origin` remote as expected. No push command was run.

Ran post-rewrite redacted all-refs scan inside the rewritten mirror:

- Report: `.gtkb-state/history-purge/20260512-152137/post-rewrite-all-refs.json`
- Mode: `all-refs`
- Paths scanned: 6482
- Findings: 244
- Severity mix: `candidate-high: 244`
- Verified-provider findings: 0
- Mirror ref count after rewrite: 42
- Mirror remote after rewrite: none

## Target Path Check

The packet's five target paths had zero scanner findings in the fresh remote
mirror before rewrite and zero scanner findings after rewrite:

| Target path | Pre-rewrite findings | Post-rewrite findings |
|---|---:|---:|
| `docs/owner-messages-all.json` | 0 | 0 |
| `docs/owner-messages-batch3a.json` | 0 | 0 |
| `docs/_temp_batch3_messages.txt` | 0 | 0 |
| `docs/system-specification-extraction.json` | 0 | 0 |
| `scripts/deploy/production-gateway-generated.yaml` | 0 | 0 |

After rewrite, `git log --all -- <target paths>` in the mirror returned no
entries for the target paths.

## Interpretation

The May 6 approval packet was correct for the local all-refs evidence available
at the time, but the current fresh remote mirror does not reproduce the
verified-provider exposure that was visible in local all-refs. The verified
provider-class findings refreshed on 2026-05-12 remain reachable from local
refs, not from the fresh remote mirror.

Therefore, this rehearsal does not support proceeding to live remote history
mutation on current evidence. The next work should be either:

- local-ref cleanup planning for local-only refs that still carry
  verified-provider findings, or
- candidate-high triage and scanner calibration for the 244 candidate-high
  findings still present in the fresh remote mirror.

## Specification-Derived Verification

No pytest suite was applicable to this owner-approved mirror rehearsal because
the acceptance evidence is produced by the scanner CLI, the mirror rewrite tool,
and the bridge preflight scripts. Verification command evidence:

| Spec / rule | Command evidence | Observed result |
|---|---|---|
| `SPEC-SEC-SCANNER-CLI-001` | `python -m groundtruth_kb secrets scan --help` | CLI supports `--tracked`, `--all-refs`, `--redacted`, `--json`, `--report-json`, and `--fail-on`; `--repo-root` remains absent. |
| `SPEC-SEC-SCAN-REDACTION-001` | `python -m groundtruth_kb secrets scan --all-refs --redacted --report-json <report> --fail-on=` | Pre/post mirror reports were redacted JSON reports; no raw matched values are included in this report. |
| `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001` | Pre-rewrite mirror scan from inside `.gtkb-state/history-purge/20260512-152137/groundtruth-kb.mirror.git` | 244 findings, all `candidate-high`; 0 `verified-provider`. |
| `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001` | Post-rewrite mirror scan from inside `.gtkb-state/history-purge/20260512-152137/groundtruth-kb.mirror.git` | 244 findings, all `candidate-high`; 0 `verified-provider`. |
| `SPEC-DSI-COMMIT-GATE-001` / non-destructive boundary | `python -m git_filter_repo --force ... --invert-paths` executed only inside the local bare mirror | Rewritten mirror had no remote configured afterward; no push or live mutation command was run. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` | PASS; no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` | PASS; blocking gaps: 0. |
| `SPEC-SEC-SCAN-REDACTION-001` | `python -m groundtruth_kb secrets scan --paths bridge\gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-009.md --redacted --fail-on=verified-provider` | PASS; 0 findings in this revised report file. |

## Safety Result

No raw matched values were printed or recorded in this report. The scanner
reports use redacted findings only.

No live remote mutation was performed. No force-push, tag rewrite, tag
deletion, branch deletion, GitHub settings mutation, credential lifecycle
operation, deployment, release, or Agent Red mutation was performed.

## Recommended Commit Type

`docs:` - this revision is a bridge-governance report correction only. It adds
the required owner-input audit section and does not change source code,
configuration, MemBase records, or runtime behavior.

## Requested Loyal Opposition Review

Verify the revised owner-approved mirror-only rehearsal report. If verified,
treat live GT-KB remote history rewrite as not currently justified by the fresh
mirror evidence. Any future live mutation remains blocked pending a new
standalone owner action and fresh bridge evidence.
