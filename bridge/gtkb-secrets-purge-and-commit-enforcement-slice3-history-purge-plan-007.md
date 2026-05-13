NEW

# Post-Rehearsal Report - GTKB Secrets Slice 3 Mirror Rehearsal

Author: Prime Builder (Codex, harness A)
Date: 2026-05-12
Bridge thread: `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan`
Prior verification: `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006.md`
Owner approval consumed: Mike replied `Approve mirror rehearsal` after the standalone `OWNER ACTION REQUIRED` block in this session.

## Claim

Prime Builder performed the owner-approved mirror-only rehearsal for GT-KB
history-purge planning. The rehearsal created a local backup bundle, cloned a
fresh remote mirror, installed/verified `git-filter-repo`, performed the
packet's target-path rewrite only inside that mirror, and ran redacted all-refs
verification before and after the mirror rewrite.

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

## Prior Deliberations And Bridge State

- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` verifies Slice 1.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-004.md` verifies Slice 2 containment/enforcement.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006.md` verifies the Slice 3 approval packet for preparation only and explicitly blocks mirror rehearsal until standalone owner approval.
- Owner approval for mirror rehearsal only was supplied in this session after the standalone owner-action block.

## Actions Performed

Created local rehearsal workspace:

- Backup root: `.gtkb-state/history-purge/20260512-152137/`
- Local all-refs backup bundle: `.gtkb-state/history-purge/20260512-152137/groundtruth-kb-pre-purge.bundle`
- Fresh remote mirror clone: `.gtkb-state/history-purge/20260512-152137/groundtruth-kb.mirror.git`

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
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` | Initially identified this missing section; the report was revised to include this spec-derived verification mapping. |
| `SPEC-SEC-SCAN-REDACTION-001` | `python -m groundtruth_kb secrets scan --paths bridge\gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-007.md --redacted --fail-on=verified-provider` | PASS; 0 findings in this report file. |

## Safety Result

No raw matched values were printed or recorded in this report. The scanner
reports use redacted findings only.

No live remote mutation was performed. No force-push, tag rewrite, tag
deletion, branch deletion, GitHub settings mutation, credential lifecycle
operation, deployment, release, or Agent Red mutation was performed.

## Requested Loyal Opposition Review

Verify the owner-approved mirror-only rehearsal. If verified, treat live GT-KB
remote history rewrite as not currently justified by the fresh mirror evidence.
Any future live mutation remains blocked pending a new standalone owner action
and fresh bridge evidence.
