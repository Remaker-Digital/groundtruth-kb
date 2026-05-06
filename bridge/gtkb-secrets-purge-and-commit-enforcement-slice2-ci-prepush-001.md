NEW

# Implementation Proposal - GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT Slice 2

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: P0 security hardening proposal
Risk tier: High for security posture; medium implementation blast radius. No credential lifecycle operation, production deployment, remote repository mutation, or destructive history rewrite is in scope.
Backlog item: `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`
Requested verdict: `GO` for Slice 2 only.

## Purpose

Slice 1 closed the immediate current-file and local staged-commit gap by adding the tracked redacted scanner, `gt secrets scan`, redacting the current verified-provider finding, wiring `.githooks/pre-commit`, and adding release-gate presence checks.

Slice 2 extends that containment to the remaining non-destructive enforcement surfaces:

1. Broad CI secret-scan coverage independent of the existing path-filtered Security Scan workflow.
2. Tracked pre-push range scanning through `.githooks/pre-push`.
3. Completed `gt secrets scan --all-refs` redacted inventory mode for fetched local history, without rewriting history.
4. Candidate-high triage rules for legacy Agent Red FQDN/fixture-shaped findings, still with redacted-only output.
5. Release-candidate gate checks proving the CI workflow and pre-push hook are present and callable.

This slice does not rotate credentials, query live provider APIs, change GitHub settings, push commits/tags, or rewrite Git history.

## Specification Links

Security and deterministic scanner specs:

- `SPEC-SEC-SCAN-PROVIDER-COVERAGE-001` - Slice 2 reuses the Slice 1 provider catalog and broadens where it runs.
- `SPEC-SEC-SCAN-REDACTION-001` - every CI, hook, history, JSON, artifact, bridge, and release-gate output remains raw-value-free.
- `SPEC-SEC-HOOK-PORTABILITY-001` - both pre-commit and pre-push hooks must be tracked under `.githooks/`, with `core.hooksPath = .githooks`.
- `SPEC-SEC-CI-COVERAGE-001` - CI secret-scan coverage must be broad and independent of adjacent SAST/dependency path filters.
- `SPEC-SEC-SCANNER-CLI-001` - `gt secrets scan` must support `--staged`, `--range`, `--paths`, and `--all-refs` redacted modes with deterministic exit codes.
- `SPEC-SEC-ALLOWLIST-001` - candidate triage must not become a broad production-path allowlist.
- `SPEC-DSI-COMMIT-GATE-001` - release-candidate gate and local hooks must fail closed on configured verified-provider findings.
- `SPEC-DSI-TRACE-REF-FORMAT-001` - remains adjacent to commit-message policy; not directly changed in Slice 2.

Bridge, root-boundary, and lifecycle specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and registered in `bridge/INDEX.md`.
- `.claude/rules/file-bridge-protocol.md` - proposal, review, implementation, and post-implementation verification lifecycle.
- `.claude/rules/codex-review-gate.md` - no implementation before Loyal Opposition `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant governing specs before requesting `GO`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map tests to the linked specs.
- `.claude/rules/project-root-boundary.md` - all GT-KB artifacts remain inside `E:\GT-KB`; Agent Red files are not treated as live GT-KB artifacts.
- `.claude/rules/deliberation-protocol.md` - prior deliberation and owner-decision evidence must be searched and cited.
- `.claude/rules/canonical-terminology.md` - distinguishes GT-KB platform, adopter applications, and Agent Red as a separate project.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application placement boundaries must be preserved.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - the P0 security work item remains durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Slice 2 preserves durable proposal, evidence, test mapping, and deferral artifacts.

Owner direction and prior bridge evidence:

- `memory/work_list.md` row 0 and top P0 security override - owner-elevated `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`.
- `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-family-batch.json` - owner approval for the SPEC-SEC family.
- `.groundtruth/formal-artifact-approvals/2026-05-04-spec-sec-*.json` - per-spec approval packets.
- `.groundtruth/formal-artifact-approvals/2026-05-04-spec-dsi-commit-gate-001.json` and `.groundtruth/formal-artifact-approvals/2026-05-04-spec-dsi-trace-ref-format-001.json`.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-001.md` - Slice 1 proposal.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-002.md` - Slice 1 `GO`; explicitly defers pre-push, range, all-refs, and broad CI to Slice 2.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-003.md` - Slice 1 post-implementation report; records 0 verified-provider current tracked findings and 239 candidate-high findings for Slice 2 triage.

## Owner Decisions / Input

Existing owner input is sufficient to file this proposal and implement Slice 2 after `GO`:

- S333 approved the SPEC-SEC family and related DSI specs.
- The 2026-05-05 owner directive elevated this workstream to P0 until current-file purge, generated-artifact redaction, and inspection-before-commit enforcement are in place.
- Slice 1 GO explicitly said pre-push range scanning, broad CI coverage, and history scanning may remain Slice 2 deferrals.

This proposal does not require new owner input because it is non-destructive and redacted-only.

Actions that still require a separate owner decision and are out of scope:

- credential rotation, validation, upload, or provider API use;
- GitHub history rewrite, force-push, tag rewrite, branch deletion, or remote repository mutation;
- GitHub settings, branch protection, required checks, environments, secrets, or deployment changes;
- production deployment or PyPI publish;
- treating de facto Agent Red repository evidence as canonical release authorization.

## Current Evidence Snapshot

- `.githooks/pre-commit` exists and runs `python -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider`.
- `.githooks/pre-push` is absent.
- `.githooks/setup-hooks.sh` only activates `pre-commit` in its current help text.
- `gt secrets scan --range` exists and scans changed head-side blobs.
- `gt secrets scan --all-refs` is present as a CLI option but intentionally raises a Slice 2 deferral error.
- `.github/workflows/security-scan.yml` is path-filtered to root Agent Red paths and adjacent workflow files; it is not broad GT-KB artifact coverage.
- Slice 1 inventory reported 0 verified-provider current tracked findings and 239 candidate-high findings requiring triage/hardening.

## Proposed Scope

### A. Broad CI secret-scan workflow

Add a dedicated workflow, preferably `.github/workflows/gtkb-secrets-scan.yml`, that:

- runs on `pull_request`, `push` to release-relevant branches, and `workflow_dispatch`;
- is not constrained by the existing Agent Red product path filters in `.github/workflows/security-scan.yml`;
- installs or resolves the in-root GT-KB package without using external live dependencies;
- runs `python -m groundtruth_kb secrets scan --tracked --redacted --report-json .quality/gtkb-secrets.json --fail-on verified-provider`;
- uploads only the redacted JSON report;
- fails on verified-provider findings and reports candidate-high findings as redacted metadata only.

### B. Portable pre-push hook

Add tracked `.githooks/pre-push` and update `.githooks/setup-hooks.sh` so developers activate both hooks.

Expected behavior:

- Parse Git pre-push stdin tuples: `<local-ref> <local-sha> <remote-ref> <remote-sha>`.
- For ordinary branch updates, run `python -m groundtruth_kb secrets scan --range <remote-sha>..<local-sha> --redacted --fail-on verified-provider`.
- For deleted refs, skip.
- For all-zero new-remote refs, choose a safe deterministic fallback: use a merge-base with the configured upstream/default branch when available; otherwise fail closed with a redacted guidance message instructing a manual `--tracked` or reviewed history scan.
- Never print raw matched values.
- Do not push, fetch, rewrite, or mutate remotes.

### C. `--all-refs` redacted inventory

Implement `gt secrets scan --all-refs` as a read-only local/fetched-history inventory mode:

- enumerate local refs with `git for-each-ref` or equivalent;
- scan reachable text blobs while deduplicating by blob/object id where practical;
- skip known binary/cache/vendor paths using the shared scanner policy;
- emit provider class, ref/path/line, fingerprint, severity/tier, and object metadata sufficient for triage;
- never print raw matched values;
- default to report-only unless `--fail-on` is supplied;
- explicitly state that this is not a history rewrite and does not inspect remote refs that have not been fetched locally.

If full all-ref scanning is too expensive in one slice, implement a bounded first version that scans local branch and tag tips plus changed blobs per ref, and file any deep-pack exhaustive scan as Slice 3. The implementation report must be explicit about coverage.

### D. Candidate-high triage and fixture hardening

Use the Slice 1 redacted inventory to classify the 239 candidate-high findings into durable categories:

- likely fixture/example value assembled as contiguous provider-shaped text;
- legacy Agent Red FQDN or non-secret endpoint reference;
- generated artifact requiring redaction;
- production-path value requiring manual owner/security review in a later slice.

Slice 2 may update tests/fixtures/docs to assemble provider-shaped examples at runtime rather than committing contiguous secret-shaped text, but it must not delete durable audit evidence solely to make the scanner quiet.

No production-path allowlist is allowed. Any production-path candidate that is not clearly a non-secret endpoint remains a redacted finding for a later owner-reviewed disposition.

### E. Release-candidate gate hardening

Extend `scripts/release_candidate_gate.py` and focused tests so the gate verifies:

- `.githooks/pre-commit` exists and invokes staged scan;
- `.githooks/pre-push` exists and invokes range scan;
- `core.hooksPath` is `.githooks`;
- `gt secrets scan --help` advertises `--staged`, `--range`, `--paths`, `--tracked`, and `--all-refs`;
- the dedicated CI secret-scan workflow exists and invokes the shared scanner in redacted mode.

## Out Of Scope

- Credential lifecycle operations.
- Any remote repository mutation, including force-push or history rewrite.
- GitHub settings, secrets, required-checks, or branch-protection changes.
- Production deployment, PyPI publication, or release tagging.
- Agent Red repository migration.
- Treating candidate-high findings as verified secrets without evidence.
- Broad production-path allowlists.

## Acceptance Criteria

Slice 2 is complete when all of the following are true:

1. A dedicated broad GT-KB secret-scan CI workflow exists, is redacted-only, and fails on verified-provider findings.
2. `.githooks/pre-push` is tracked, executable where possible, and runs redacted `--range` scans for ordinary branch updates.
3. `.githooks/setup-hooks.sh` documents and activates both `pre-commit` and `pre-push`.
4. `gt secrets scan --all-refs` no longer raises the Slice 2 deferral error and produces redacted history inventory output.
5. Candidate-high findings from Slice 1 are triaged into documented redacted categories; any path changes preserve audit meaning.
6. Release-candidate gate tests fail if the pre-push hook, broad workflow, or `--all-refs` CLI surface is missing.
7. Focused tests prove no raw fixture value appears in stdout, JSON, reports, hook output, or bridge reports.
8. The implementation report carries forward this proposal's Specification Links, includes the applicability preflight, and maps every acceptance criterion to executed verification or an explicitly named follow-on deferral.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| T-bridge-index | `GOV-FILE-BRIDGE-AUTHORITY-001`; `.claude/rules/file-bridge-protocol.md` | `bridge/INDEX.md` latest entry is `NEW` for this proposal and the named file exists |
| T-preflight | Mandatory Applicability Preflight Gate | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush` reports no missing required or advisory specs |
| T-ci-workflow | `SPEC-SEC-CI-COVERAGE-001` | Focused test parses `.github/workflows/gtkb-secrets-scan.yml` and asserts broad triggers plus redacted shared-scanner invocation |
| T-prepush-hook | `SPEC-SEC-HOOK-PORTABILITY-001`; `SPEC-SEC-SCANNER-CLI-001` | Focused test verifies `.githooks/pre-push` invokes `secrets scan --range --redacted` and handles all-zero refs deterministically |
| T-setup-hooks | `SPEC-SEC-HOOK-PORTABILITY-001` | Focused test verifies setup script mentions/activates both hooks and `core.hooksPath = .githooks` remains the active invariant |
| T-all-refs | `SPEC-SEC-SCANNER-CLI-001`; `SPEC-SEC-SCAN-REDACTION-001` | Unit or integration test exercises `--all-refs` in a temporary git repo with runtime-assembled fixture values and verifies redacted-only JSON |
| T-range-redaction | `SPEC-SEC-SCAN-REDACTION-001` | Range scan over a synthetic commit emits provider/fingerprint metadata only, never raw value |
| T-candidate-triage | `SPEC-SEC-ALLOWLIST-001` | Tests prove production-path allowlists are still rejected and fixture examples use runtime assembly or exact tests-only allowlists |
| T-release-gate | `SPEC-DSI-COMMIT-GATE-001`; `SPEC-SEC-CI-COVERAGE-001` | `tests/scripts/test_release_candidate_gate.py` covers missing pre-push hook, missing CI workflow, and missing `--all-refs` support |
| T-no-raw-report | `SPEC-SEC-SCAN-REDACTION-001` | Post-implementation report and generated inventory contain only redacted metadata |

Suggested command set:

```powershell
python -m pytest tests/secrets tests/scripts/test_release_candidate_gate.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_credential_patterns.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/secrets groundtruth-kb/src/groundtruth_kb/cli.py tests/secrets tests/scripts/test_release_candidate_gate.py scripts/release_candidate_gate.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/secrets groundtruth-kb/src/groundtruth_kb/cli.py tests/secrets tests/scripts/test_release_candidate_gate.py scripts/release_candidate_gate.py
python scripts/release_candidate_gate.py --skip-python --skip-frontend
python -m groundtruth_kb secrets scan --paths <touched-paths> --json --fail-on=
git diff --check -- <touched-paths>
```

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| CI workflow uploads raw values | Creates a new exposure channel | Shared scanner returns redacted findings only; test workflow command and JSON output shape |
| Pre-push hook blocks legitimate new branches | Developer friction | Deterministic fallback; fail closed only when a safe base cannot be determined, with explicit manual-scan guidance |
| `--all-refs` is expensive on a large repo | Slow local/CI runs | Make it an explicit command, not default pre-push; dedupe blobs; allow Slice 3 follow-on for exhaustive deep-pack mode if required |
| Candidate-high triage hides real secrets as endpoints | Residual risk | No production-path broad allowlist; suspicious values remain redacted findings for later owner/security review |
| Workflow fights ongoing Agent Red migration | Release-plan confusion | Name workflow GT-KB-specific, cite root-boundary rules, and do not alter Agent Red repository state |
| Dirty worktree mixes unrelated work | Commit packaging risk | Implementation report lists touched paths and uses scoped tests/diffs; no unrelated reverts |

## Rollback

Rollback is local Git-only: revert the Slice 2 commit. No remote or external system is mutated. If a hook is too disruptive, temporarily bypassing hooks remains a local Git operation, but the project release gate should continue to fail until the issue is corrected or a bridge-approved waiver exists.

## Prime Builder Recommendation

Proceed with Slice 2 after Loyal Opposition `GO`.

Do not start any GitHub history rewrite or credential lifecycle work in this slice. If `--all-refs` finds old verified-provider history, file a separate owner-action history-purge plan with blast radius, backup, branch/tag impact, collaborator coordination, and exact approval language before any rewrite.

