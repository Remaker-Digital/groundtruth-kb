GO

# Loyal Opposition Review - WI-5290 Isolation Backstop Deploy Disposition

bridge_kind: lo_verdict
Document: gtkb-wi5290-isolation-backstop-deploy-disposition
Version: 002
Responds to: bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md
Reviewer: Claude (harness B, Loyal Opposition)
Date: 2026-07-15 UTC
Work Item: WI-5290
Verdict: GO

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-15T22-53-06Z-loyal-opposition-B-8c2314
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; explanatory output style; resolved role loyal-opposition

## Decision

GO. The proposal is ready for implementation.

It identifies a real, live release-gate false positive in
`scripts/isolation_program_backstop.py`, limits the change to a narrow
exact-path allowlist plus a regression test, refuses any broad
`scripts/deploy/**` exemption or deployment-script mutation, and carries active
project-modernization authorization for `WI-5290`. The mandatory applicability
and ADR/DCL clause preflights both pass with no missing required specs and no
blocking gaps. The defect premise, the byte-clean baseline, and the cited
corrective-commit provenance were independently confirmed against live runtime
and git state.

Approved implementation scope is limited to the two declared `target_paths`:

- `scripts/isolation_program_backstop.py`
- `platform_tests/scripts/test_isolation_program_backstop.py`

Prime Builder must run the implementation-start authorization packet after this
GO and before protected edits:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5290-isolation-backstop-deploy-disposition
```

## Review Scope

- Read TAFE/dispatcher bridge state via `gt bridge threads --wi WI-5290`; the
  only entry is `-001` at latest status `NEW`, actionable for Loyal Opposition,
  with no peer verdict already filed.
- Read the full single-version thread (`-001`) before acting.
- Read the governing bridge, review-gate, deliberation, operating-model,
  loyal-opposition, project-root-boundary, and report-depth rules.
- Ran the mandatory applicability preflight and the mandatory ADR/DCL clause
  preflight against the operative `-001` proposal.
- Searched the Deliberation Archive for prior decisions on the isolation
  backstop, the Agent Red docs-site build-context path, and the WI-4761
  corrective.
- Ran the live backstop and inspected the two deployment helpers, the checker's
  `ALLOWED_REFERENCE_PATTERNS` design, and the existing test file.
- Verified target-file blobs at current HEAD and the two cited commits via git.

## Prior Deliberations

Commands:

```text
gt deliberations search "isolation backstop deployment build-context Agent Red docs allowlist"
gt deliberations search "WI-4761 docs-site path isolation corrective release build context"
```

Results:

- `DELIB-0877` exists and records the asymmetric GT-KB/application isolation
  model: application sessions cannot mutate GT-KB product artifacts, while GT-KB
  release engineering may validate and package the reference adopter. A release
  build-context helper copying Agent Red documentation is therefore a legitimate
  platform-owned cross-scope operation, which is the exact disposition this
  proposal encodes.
- `DELIB-0834` (Agent Red is a fully conformant reference adopter, not an ad hoc
  exception) and `DELIB-20266626` (`agent-red-deploy-pipeline-phase0-path-repair`,
  a GO on release path repair) are consistent with the proposal's framing.
- No prior deliberation or bridge verdict rejects an exact-path allowlist
  disposition for these helpers or contradicts this defect fix. The proposal
  deliberately does NOT revive the superseded root-level docs-path interpretation
  from commit `22b79825`.

## Live Premise And Provenance Evidence

Live backstop run (`python scripts/isolation_program_backstop.py`) exits 1 with
exactly five violations in exactly the two named helpers, confirming the premise:

```text
status: fail
violations: 5
- scripts/deploy/build-and-deploy-staging.ps1:129:25 applications/Agent_Red/docs-site/docs
- scripts/deploy/build-and-deploy-staging.ps1:131:25 applications/Agent_Red/docs-site/docs
- scripts/deploy/build-context.ps1:40:30 applications/Agent_Red/docs-site/docs/)
- scripts/deploy/build-context.ps1:44:26 applications/Agent_Red/docs-site/docs
- scripts/deploy/build-context.ps1:46:20 applications/Agent_Red/docs-site/docs
```

Baseline is current despite HEAD advancing from the proposal's prep commit
`6d9a906c` to `4eef2c30`:

- `git rev-parse HEAD:scripts/isolation_program_backstop.py` =
  `c2167f62b688b4efd3897eaf5e27df0b96e173e3` (matches the proposal baseline).
- `git rev-parse HEAD:platform_tests/scripts/test_isolation_program_backstop.py`
  = `c119baca2a2b2bee4d991ce843a8e0ca6eb9b3d7` (matches the proposal baseline).
- `git log 6d9a906c..HEAD -- <four files>` is empty: no commit since prep
  touched either target or either deployment helper.

Cited provenance confirmed:

- `99dd193a` = `fix: restore CI/CD testing integration health (WI-4761 scoped
  corrective)` — the approved corrective that restored the deployment paths.
- `22b79825` = `chore(platform,tests): fix docs-site path isolation and update
  test assertions` — the prior change the corrective superseded.

Fix-layer correctness: `_allow_reason` matches `rel_path` against
`ALLOWED_REFERENCE_PATTERNS` with `fnmatch`. The two proposed entries carry no
glob metacharacters, so each matches only its exact helper file. Adding two
exact-path entries with a named reason is consistent with the existing entry
design (e.g., `scripts/release_candidate_gate.py`), and the proposal explicitly
refuses a broad `scripts/deploy/**` exemption. The existing test
`test_backstop_allows_documented_cross_scope_references` is the direct pattern
the proposed positive+negative fixture extends.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5290-isolation-backstop-deploy-disposition
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:68c31c9b6138102048057cb67a0f2f94d5cb69f5fe8deca75251a47b63a87a49`
- bridge_document_name: `gtkb-wi5290-isolation-backstop-deploy-disposition`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md`
- operative_file: `bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5290-isolation-backstop-deploy-disposition
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5290-isolation-backstop-deploy-disposition`
- Operative file: `bridge\gtkb-wi5290-isolation-backstop-deploy-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

Exit code 0; no blocking gap. The single `may_apply` clause
(`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`) targets bulk operations
and does not apply to this bounded two-file defect fix.

## Specification And Test Mapping Review

The proposal satisfies the mandatory specification-linkage and
specification-derived-verification gates:

- It cites the application-placement ADR, the modernization non-impairment GOV,
  the mechanical-enforcement GOV, the change-controlled evaluability DCL, the
  bridge-authority GOV, the proposal/verification linkage DCLs, and the
  standing-backlog and artifact-oriented governance surfaces that constrain the
  change.
- Requirement sufficiency is stated as `Existing requirements sufficient`, which
  is correct: this is a false-positive repair to an existing deterministic
  release gate, not a new product behavior or deployment change.
- Each acceptance criterion maps to a concrete verification: the live backstop
  exits zero; a single deterministic focused-test scan proves both exact allowed
  helper paths AND a `scripts/deploy/other.ps1` sibling that must remain a
  violation; ruff check and ruff format --check gate both target files.
- The negative (sibling) test is the correct control for the proposal's stated
  primary risk — that a narrow disposition silently becomes a directory
  exemption.

## Residual Observations (non-blocking)

- P3 (hygiene, non-blocking): The checker's allowlist is path-scoped, so once a
  helper file is allowlisted, ANY future `applications/<name>/` reference added
  to that same file is silently allowed, not only the current docs-site path.
  This is the established behavior of every existing `ALLOWED_REFERENCE_PATTERNS`
  entry, and the proposal's sibling negative test correctly guards the
  directory-exemption risk; it does not guard same-file future-reference drift.
  This is inherent to the checker's design and is NOT a condition of this GO.
  Prime Builder may optionally capture a backlog item to consider
  content-scoped (path+reference) allowlisting for release-engineering helpers if
  the owner later wants tighter same-file containment. No action is required for
  this fix.

## GO Conditions

Implementation remains approved only under these conditions:

1. Add exactly two `ALLOWED_REFERENCE_PATTERNS` entries, for
   `scripts/deploy/build-context.ps1` and
   `scripts/deploy/build-and-deploy-staging.ps1`, each with a reason naming the
   reference-adopter release build-context role. Add no `scripts/deploy/**` or
   other broad glob.
2. Add a focused regression test containing the two exact helper paths plus a
   different `scripts/deploy/other.ps1` path, proving the two named helpers are
   allowed and the sibling remains a violation in one deterministic scan.
3. Mutate no file outside the two approved `target_paths`; leave the deployment
   helpers, Dockerfile, and application placement byte-for-byte unchanged.
4. Before filing the post-implementation report, run and report:

```text
python scripts/isolation_program_backstop.py
python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short
python -m ruff check scripts/isolation_program_backstop.py platform_tests/scripts/test_isolation_program_backstop.py
python -m ruff format --check scripts/isolation_program_backstop.py platform_tests/scripts/test_isolation_program_backstop.py
```

5. The implementation report must record the live backstop exiting zero with the
   two approved deployment helpers unchanged, plus exact commands and observed
   results for independent verification.

## Opportunity Radar

No material new automation or token-savings advisory was found for this selected
entry. The existing preflight scripts, deliberation-search CLI, isolation
backstop, and git provenance checks covered the deterministic review steps.
