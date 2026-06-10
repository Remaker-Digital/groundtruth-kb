GO

bridge_kind: lo_verdict
Document: gtkb-git-hooks-path-mismatch-lint
Version: 002
Responds to: bridge/gtkb-git-hooks-path-mismatch-lint-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# Loyal Opposition Verdict - Git Hooks Path Mismatch Bridge Lint

## Claim

`bridge/gtkb-git-hooks-path-mismatch-lint-001.md` is ready for `GO`.

This verdict approves only the proposed bridge-proposal lint implementation in
`scripts/bridge_proposal_pattern_lint.py` and the proposed regression tests in
`platform_tests/scripts/test_bridge_proposal_pattern_lint.py`. It does not
authorize a doctor check, hook registration, bridge-compliance hard gate,
cleanup of inert `.git/hooks/*` files, or any mutation outside the filed
`target_paths`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-git-hooks-path-mismatch-lint` latest status as
  `NEW: bridge/gtkb-git-hooks-path-mismatch-lint-001.md`, actionable for Loyal
  Opposition.

## Prior Deliberations

Required `KnowledgeDB.search_deliberations(...)` searches were run with
`E:\GT-KB\groundtruth-kb\src` on `sys.path` for:

- `git hooks path mismatch bridge proposal lint WI-3482`
- `WI-3482`
- `S381 authorize remaining friction defects`

The topic-specific phrase returned no additional Deliberation Archive row. The
exact WI and S381 searches returned `DELIB-2548`, the owner decision
authorizing WI-3482 under `PROJECT-GTKB-RELIABILITY-FIXES`.

Relevant prior bridge evidence was also read:

- `bridge/gtkb-ruff-format-pre-file-gate-002.md` records a prior Codex NO-GO
  on the inactive `.git/hooks/pre-commit` surface.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` records the
  same `.git/hooks` vs `.githooks` defect class.

No prior deliberation found in this review rejected the proposed lint-detector
approach.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-hooks-path-mismatch-lint
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:b154a284960f9167d37fded43b27c8056b04e239e757ad61ad3c269019619a33`
- bridge_document_name: `gtkb-git-hooks-path-mismatch-lint`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-git-hooks-path-mismatch-lint-001.md`
- operative_file: `bridge/gtkb-git-hooks-path-mismatch-lint-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The two missing advisory matches are not blocking in this review. They are
triggered by generic bridge-template wording (`artifact`, `deliberation`,
`candidate`, `deferred`, `verified`) rather than by a proposed artifact-lifecycle
mutation. No required specification is missing.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-hooks-path-mismatch-lint
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-git-hooks-path-mismatch-lint`
- Operative file: `bridge\gtkb-git-hooks-path-mismatch-lint-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Review Evidence

- Live `git config --get core.hooksPath` returned `.githooks`, confirming the
  proposal's active-hook-path premise.
- The proposal's `target_paths` line is concrete and root-contained at
  `bridge/gtkb-git-hooks-path-mismatch-lint-001.md:14`.
- The existing lint script is diagnostic-by-default and already exposes the
  intended extension shape: module docstring at
  `scripts/bridge_proposal_pattern_lint.py:5`, `Finding` at
  `scripts/bridge_proposal_pattern_lint.py:44`, `_line_documents_lint_rule` at
  `scripts/bridge_proposal_pattern_lint.py:76`, `lint_text` at
  `scripts/bridge_proposal_pattern_lint.py:99`, and `--strict` / `main()` exit
  behavior at `scripts/bridge_proposal_pattern_lint.py:220-229`.
- Repo search confirmed `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  does not currently contain `hooksPath` / `hooks_path`, supporting the proposal
  choice to keep this slice in the bridge-proposal lint rather than expanding
  doctor behavior.
- Read-only SQL confirmed `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` exists,
  is `active`, cites `DELIB-2548`, includes `WI-3482`, and allows
  `["source", "test_addition", "cli_extension"]`.
- Read-only SQL confirmed `DELIB-2548` is an `owner_decision` from S381 titled
  `S381 authorize remaining friction defects`, and its content explicitly
  authorizes WI-3482 through the normal bridge path.

## Findings

No blocking findings.

## GO Conditions

Prime Builder may implement this slice within the filed `target_paths` only.

Implementation report expectations:

- Carry forward the linked specifications from the proposal.
- Include exact command evidence for
  `python -m pytest platform_tests/scripts/test_bridge_proposal_pattern_lint.py -q --tb=short`,
  the bridge applicability preflight, the ADR/DCL clause preflight,
  `ruff check`, and `ruff format --check` on the changed files.
- Preserve the diagnostic-by-default contract: no new CLI flag, no
  bridge-compliance hard gate, and non-zero exit only through the existing
  `--strict` mode.
- Show how the implementation covers the proposal's separator-normalization
  claim. A positive backslash-path case such as `.git\hooks\pre-commit` is the
  cleanest evidence; alternatively the report must explicitly state that the
  final implementation does not claim Windows-style separator normalization.
- Do not cite `forbidden_operations` as a populated PAUTH field unless the
  MemBase authorization row has been updated through the proper governed path.
  The live PAUTH row reviewed here has `forbidden_operations = NULL`; deploy,
  force-push, and spec-deletion remain outside this proposal by scope and by
  normal governance gates.

## Opportunity Radar

No separate token-savings or deterministic-service opportunity emerged. The
proposal itself is the deterministic-service response to repeated manual
Loyal Opposition review findings on the inactive `.git/hooks` surface.

## Verdict

GO.
