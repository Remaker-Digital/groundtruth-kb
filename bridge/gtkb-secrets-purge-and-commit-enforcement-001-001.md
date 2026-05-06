NEW

# Implementation Proposal - GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT Slice 1

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-06
**Type:** P0 security incident containment proposal
**Risk tier:** High for security posture; medium for implementation blast radius. No production deployment, credential lifecycle operation, remote GitHub history rewrite, or secret-value disclosure is in scope.
**Backlog item:** `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`
**Requested verdict:** `GO` for Slice 1 only.

---

## Purpose

This proposal begins the P0 owner-elevated security workstream created after a tracked GT-KB artifact exposed provider credentials. The immediate goal is to close the current-file and local-commit gap before returning to isolation or CI cleanup work.

Slice 1 is intentionally narrow:

1. Inventory current tracked text artifacts for secret-shaped material without printing raw values.
2. Purge or redact currently tracked secret-bearing artifacts.
3. Harden scanner output and generated artifact paths so findings are redacted by construction.
4. Wire mandatory local inspection-before-commit enforcement through the tracked `.githooks/pre-commit` path.

CI-wide coverage, pre-push range scanning, GitHub security posture checks, and any destructive history rewrite are separate slices and require later bridge work. A history rewrite plan must be owner-approved before any rewrite is attempted.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| P0 override makes this the controlling workstream | `memory/work_list.md` lines 16, 45, and row 0 | Owner-elevated priority outranks the release-path isolation sequence until containment gates are implemented and verified |
| Required next step is this bridge proposal | `memory/work_list.md` row 0 | Row says to file `bridge/gtkb-secrets-purge-and-commit-enforcement-001-001.md` before implementation |
| Approved security specs exist | `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-family-batch.json` and per-spec packets | S333 approved the SPEC-SEC family by AskUserQuestion and anchored the scanner/commit-gate work |
| Existing canonical credential catalog exists | `groundtruth-kb/src/groundtruth_kb/governance/credential_patterns.py` | Provides an approved pattern inventory; Slice 1 should reuse it instead of inventing a separate regex set |
| Existing Claude Write/Edit scanner exists | `.claude/hooks/credential-scan.py` and `tests/hooks/test_credential_scan.py` | Useful local precedent, but it is not a git staged-content gate and excludes several artifact classes |
| Existing stronger guardrail hook exists but is not active through `.githooks/pre-commit` | `scripts/guardrails/pre-commit` calls `scripts/guardrails/check_hardcoded_env.py`; `.githooks/pre-commit` currently only runs PowerShell syntax validation | The active tracked hook path does not currently run the credential scan before commit |
| No tracked pre-push hook exists | `.githooks/pre-push` is absent | Pre-push range scanning belongs to Slice 2, not Slice 1 |
| Existing Security Scan is path-scoped | `.github/workflows/security-scan.yml` | Semgrep secrets exists, but the workflow path filters do not satisfy broad artifact coverage from `SPEC-SEC-CI-COVERAGE-001` |
| Local scanner/redaction work is currently ignored by git | `.gitignore` line 24 ignores `secrets/`; `git check-ignore -v groundtruth-kb/src/groundtruth_kb/secrets/redaction.py tests/secrets/test_redaction.py` reports both ignored by that rule | Existing local `groundtruth-kb/src/groundtruth_kb/secrets/` and `tests/secrets/` files cannot become committed enforcement until the ignore policy is corrected or paths are moved |

## Specification Links

Security incident and scanner specifications:

- `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001` - shared scanner must detect the provider credential classes identified by S333.
- `SPEC-SEC-SCAN-REDACTION-001` - scanner output paths must never contain raw secret values.
- `SPEC-SEC-HOOK-PORTABILITY-001` - pre-commit and pre-push hooks must be tracked under `.githooks/`, with `core.hooksPath = .githooks`.
- `SPEC-SEC-CI-COVERAGE-001` - CI secret-scan coverage must be broad and independent of adjacent SAST/dependency workflow path filters.
- `SPEC-SEC-SCANNER-CLI-001` - `gt secrets scan` must support `--staged`, `--range`, `--paths`, and `--all-refs` redacted modes with deterministic exit codes.
- `SPEC-SEC-ALLOWLIST-001` - fixture allowlists must be exact value plus exact test path; provider-shaped fixture values must not be committed as contiguous text.
- `SPEC-DSI-COMMIT-GATE-001` - later commit-time spec-derived enforcement must integrate cleanly with the sibling secret-scanning gate and keep raw secret values redacted.
- `SPEC-DSI-TRACE-REF-FORMAT-001` - relevant to future commit-message trace refs, not required for Slice 1 secret scan blocking.

Existing governance and operating constraints:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is the live authority for this proposal and the proposal file must be inserted there with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite relevant specifications before `GO`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must map linked specifications to executed verification before `VERIFIED`.
- `.claude/rules/file-bridge-protocol.md` - proposal, review, implementation report, and verification lifecycle.
- `.claude/rules/codex-review-gate.md` - no implementation before Loyal Opposition `GO`.
- `.claude/rules/project-root-boundary.md` - all active GT-KB files must remain inside `E:\GT-KB`; GT-KB applications under `E:\GT-KB\applications\`.
- `.claude/rules/deliberation-protocol.md` - search and cite prior deliberation/advisory context.
- `.claude/rules/canonical-terminology.md` - distinguishes GT-KB platform from adopter/application scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application placement and platform/application isolation must be respected; Agent Red is not treated as a live GT-KB platform artifact unless Mike explicitly declares application work.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - standing backlog/work list is durable cross-session work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable incident evidence, proposals, test mappings, and follow-up plans must be preserved.

Owner direction and approval evidence:

- `memory/work_list.md` row 0 - owner-elevated P0 work item and required outcomes.
- `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-family-batch.json` - owner approved all seven SPEC-SEC drafts via AskUserQuestion in S333.
- `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-*.json` - per-spec approval packets.

The proposed tests derive from these linked specifications as follows: provider coverage drives pattern fixture tests; redaction drives output tests; hook portability drives `.githooks` and `core.hooksPath` tests; scanner CLI drives staged/path scan tests and exit codes; allowlist drives exact test-path allowlist tests; backlog and bridge specs drive index/file checks and post-implementation spec-to-test mapping.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "secret scan redaction commit gate credential exposure history rewrite" --limit 10
python -m groundtruth_kb deliberations search "SPEC-SEC-SCAN-REDACTION-001 gtkb-sec-redaction-commit-gate" --limit 10
```

Relevant records and adjacent evidence:

| Record or artifact | Relevance |
|---|---|
| `DELIB-0738` | Compressed bridge thread for `gtkb-credential-patterns-canonical`; supports reusing the canonical pattern catalog |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Supports deterministic scanner/CLI enforcement instead of prompt-only discipline |
| `SPEC-SEC-*` approval packets | Formal owner-approved specification family for scanner/commit-gate implementation |
| `.claude/session/spec-events-seen.jsonl` entry for `SPEC-SEC-SCAN-REDACTION-001` | Confirms the spec event surfaced locally |
| `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-003.md` | Adjacent CI/security scan enforcement, but it does not replace this incident containment workstream |

No search result found owner approval for a destructive GitHub history rewrite. History purge remains out of scope for Slice 1 and requires a separate owner-approved plan.

## Owner Decisions / Input

Existing owner input is sufficient to file this proposal and implement Slice 1 after `GO`:

- S333 AskUserQuestion approved the seven SPEC-SEC specifications as drafted, recorded in `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-family-batch.json`.
- The 2026-05-05 owner directive in `memory/work_list.md` elevates `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` to P0 and names this bridge proposal as the next step.

No new owner decision is needed for Slice 1 because it does not rotate credentials, deploy, rewrite GitHub history, or delete non-generated project content. Any history rewrite, credential lifecycle action, or production/GitHub settings mutation must stop for a separate one-decision owner approval.

## Proposed Slice 1 Scope

### A. Secret exposure inventory without raw-value output

Add or adapt a shared scanner entrypoint that can scan tracked/current text content and report only redacted findings:

- provider class,
- file path,
- line number,
- fingerprint,
- severity/tier.

The inventory command must not print raw matched values to stdout, JSON, logs, CI artifacts, bridge files, or reports.

### B. Current tracked artifact purge/redaction

Use the scanner to identify tracked files requiring purge or redaction, then apply the smallest safe changes:

- redact generated docs/JSON/bridge payloads that are meant to remain as audit evidence,
- delete only generated secret-bearing artifacts that are unsafe to keep and are already covered by existing deletion policy,
- preserve audit meaning with redacted placeholders and fingerprints where appropriate.

The implementation report must list paths and redacted finding identifiers only. It must not include raw values.

### C. Trackable scanner/redaction implementation

Resolve the local ignored-path problem before relying on scanner code:

- either move current local `groundtruth-kb/src/groundtruth_kb/secrets/` and `tests/secrets/` work into tracked, non-ignored package/test paths, or
- narrow `.gitignore` so GT-KB source/test packages named `secrets` can be tracked while runtime secret directories remain ignored.

The selected approach must preserve the intent of `.gitignore` line 24: runtime secret material remains ignored.

### D. Mandatory local pre-commit gate

Update tracked `.githooks/pre-commit` so the active portable hook path runs the secret scan on staged blobs before allowing a commit.

Expected behavior:

- no staged files: pass,
- staged clean files: pass,
- staged secret finding at or above the configured fail threshold: block with redacted output,
- staged fixture values: pass only when allowed under exact tests-only allowlist rules,
- hook continues to run existing PowerShell syntax validation.

Do not rely on `scripts/guardrails/pre-commit` being manually copied into `.git/hooks`.

### E. Release-gate hook-integration smoke

Add a focused release-candidate gate check that proves the portable secret gate is present and callable. The full broad CI workflow from `SPEC-SEC-CI-COVERAGE-001` belongs to Slice 2.

## Out of Scope

- No credential rotation, revocation, validation, or upload.
- No production, staging, GitHub settings, or repository-security posture mutation.
- No `git filter-repo`, force push, branch deletion, tag rewrite, or destructive history rewrite.
- No pre-push range gate in Slice 1.
- No broad CI `secrets-scan.yml` job in Slice 1.
- No Agent Red repository mutation.
- No formal artifact mutation outside this bridge lifecycle and already-approved SPEC-SEC usage.

## Acceptance Criteria

Slice 1 is complete when all of the following are true:

1. A shared scanner/redaction implementation is tracked by git and is not hidden by the root `secrets/` ignore rule.
2. The scanner can scan staged blobs and explicit paths without exposing raw matched values in stdout or JSON.
3. Provider-pattern coverage is derived from the existing canonical catalog or an explicitly documented successor catalog, not a new unsourced regex set.
4. Current tracked secret-bearing artifacts identified by the scanner are redacted or purged in the working tree without printing raw values.
5. `.githooks/pre-commit` invokes the staged secret scan and blocks above-threshold findings.
6. `git config --get core.hooksPath` returns `.githooks` locally, and a doctor/test covers the invariant.
7. Allowlist behavior is exact value plus exact test path; production paths cannot be allowlisted.
8. Focused tests cover redaction, staged scan failure, staged scan pass, allowlist rejection, hook portability, and release-gate presence.
9. The post-implementation report carries forward this proposal's Specification Links and maps each acceptance criterion to an executed test or explicit out-of-scope deferral.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| `T-bridge-index` | `.claude/rules/file-bridge-protocol.md`; `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` latest entry is `NEW` for this proposal and the named file exists |
| `T-preflight` | Mandatory Applicability Preflight Gate | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-secrets-purge-and-commit-enforcement-001` reports no missing required specs |
| `T-redaction-stdout` | `SPEC-SEC-SCAN-REDACTION-001` | Scanner stdout contains path/provider/fingerprint but not the raw fixture value |
| `T-redaction-json` | `SPEC-SEC-SCAN-REDACTION-001`; `SPEC-SEC-SCANNER-CLI-001` | `--json` or report JSON contains redacted finding fields only |
| `T-provider-coverage` | `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001` | Synthetic runtime-assembled fixtures produce one finding per required provider class |
| `T-staged-scan-fail` | `SPEC-SEC-SCANNER-CLI-001`; `SPEC-SEC-HOOK-PORTABILITY-001` | A temporary staged fixture with an above-threshold finding causes the staged scan/pre-commit path to exit non-zero |
| `T-staged-scan-pass` | `SPEC-SEC-SCANNER-CLI-001` | Clean staged content exits zero |
| `T-allowlist-exact` | `SPEC-SEC-ALLOWLIST-001` | Exact test-path allowlist passes; path/value near-miss and production-path allowlists fail |
| `T-hook-portability` | `SPEC-SEC-HOOK-PORTABILITY-001` | `.githooks/pre-commit` exists, `.githooks/pre-push` remains out of Slice 1 or is explicitly absent, and `core.hooksPath` is `.githooks` |
| `T-release-gate-presence` | `SPEC-SEC-HOOK-PORTABILITY-001`; `SPEC-SEC-CI-COVERAGE-001` partial Slice 1 | `scripts/release_candidate_gate.py` or a focused test proves the local secret gate is present and callable; broad CI coverage is deferred to Slice 2 |
| `T-no-raw-report` | `SPEC-SEC-SCAN-REDACTION-001` | The implementation report and any generated inventory file contain no raw matched values |

Suggested focused command set for the implementation report:

```powershell
python -m pytest tests/hooks/test_credential_scan.py tests/scripts/test_release_candidate_gate.py -q --tb=short
python -m pytest <new secret scanner tests> -q --tb=short
python scripts/release_candidate_gate.py --skip-frontend --require-python 3.12
git diff --check -- <touched paths>
```

The exact new test file paths may change during implementation, but the report must map them back to the test IDs above.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Scanner output leaks raw values | The gate becomes a second exposure path | Redaction is acceptance criterion 1 for every output mode; tests use runtime-assembled fixtures |
| `.gitignore` change accidentally tracks runtime secret directories | New exposure risk | Use a narrow negation or move code paths instead of broadly unignoring `secrets/`; test/inspect ignored files before staging |
| Pre-commit hook blocks legitimate generated docs | Developer friction | Use exact test-only allowlist and redacted placeholders; do not allow production-path bypasses |
| Current-file purge breaks audit trail | Loss of governance evidence | Prefer redaction over deletion for governance/audit artifacts; delete only generated unsafe artifacts with replacement evidence |
| History still contains old secret material | Residual repository risk | Slice 1 states this explicitly and produces a later owner-approved history-purge plan; no rewrite happens here |
| Existing dirty worktree makes commit packaging risky | Could mix unrelated changes | Implementation must stage only intended files and report unrelated dirty paths as pre-existing |

## Rollback

If the Slice 1 implementation causes false blocking or breaks local commits, rollback by reverting the Slice 1 commit. No remote rewrite or external system mutation is part of Slice 1, so rollback is local Git state only.

## Review Questions

1. Is Slice 1 narrow enough to approve before CI/pre-push/history-purge work?
2. Should the ignored local `groundtruth-kb/src/groundtruth_kb/secrets/` work be moved, or should `.gitignore` be narrowed to allow source/test packages named `secrets`?
3. Does the local commit gate need to call the packaged `gt secrets scan` CLI in Slice 1, or is a direct shared-engine invocation acceptable until the full CLI surface lands?
4. Are bridge files scanned for current-file inventory in Slice 1 even though bridge proposals remain audit artifacts? Prime recommendation: yes, scan and redact findings, while preserving bridge lifecycle history.

## Prime Builder Recommendation

Proceed with Slice 1 after Loyal Opposition `GO`.

Do not begin CI/pre-push enforcement or any GitHub history rewrite until separate bridge proposals are filed and approved. In particular, any history purge plan must include owner-visible options, blast-radius analysis, branch/tag impact, contributor coordination, backup strategy, and explicit owner approval before execution.
