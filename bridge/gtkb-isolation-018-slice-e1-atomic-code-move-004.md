NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-1

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

The revised proposal fixes the out-of-root scratch paths, records a concrete import-resolution strategy, and now passes the current applicability and clause preflights on the live operative file. It is still not ready for GO because the replacement clean/scoped-worktree guard remains too broad for a 1,400+ file move: it classifies entire platform-sensitive directories such as `tests/` and `config/` as in scope, even though this slice only moves a manifest-selected test subset and `config/stripe_product_ids.json`.

## Prior Deliberations

Deliberation Archive checks were run before review using `python -m groundtruth_kb deliberations search ...` and exact `get` lookups.

Search queries:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red src tests admin widget`
- `Agent Red nested applications migration pending waiver code cluster E.1`
- `18.E code cluster E.3 platform test disposition manifest pythonpath`
- exact lookups for `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`, `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`, and `DELIB-S334-OQ-E3-OPTION-A`

Relevant results:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` remains the owner-decision authority for nesting Agent Red under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` remains the active migration-window waiver and requires sub-slices to keep scope discipline.
- `DELIB-S334-OQ-E3-OPTION-A` selects file-level platform-test disposition and dual pytest discovery as needed.
- Search also surfaced `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` as relevant context for keeping GT-KB platform lint/test surfaces scoped separately from Agent Red movement.

No prior deliberation found in this review rejects the approved 18.E direction. The blocker below is an execution-safety issue in the revised implementation plan.

## Findings

### FINDING-P1-001 - The scoped-worktree guard still permits unrelated platform paths

Observation:
The revised proposal adds a clean-or-scoped-worktree precondition, but the allowed-prefix list is directory-wide for several surfaces:

```text
allowed_prefixes = ('src/','tests/','admin/','widget/','branding/','config/','pyproject.toml','applications/Agent_Red/.gtkb-app-isolation.json','.github/workflows/','Dockerfile','docker-compose.yml','.dockerignore','.tmp/e1-')
```

This is broader than the proposal's actual move/write set. For example, `config/agent-control/*` and `config/governance/*` are GT-KB platform configuration, not Agent Red Stripe config, and `tests/hooks/`, `tests/scripts/`, and `tests/skills/` are explicitly classified as platform tests by the revised drift probe.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md:167` allows any path beginning with `tests/` or `config/`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md:195` narrows the actual config move to `config/stripe_product_ids.json`.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md:151` says platform configs in `config/agent-control/` and `config/governance/` stay at the GT-KB root.
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json:25-58` classifies multiple `tests/scripts/*` files as `STAYS_PLATFORM_scripts`; lines 9-22 do the same for `tests/hooks/*`, and lines 61-66 for `tests/skills/*`.
- Current review-time `git status --short` includes examples of platform changes under these broad prefixes: `M config/agent-control/system-interface-map.toml` and untracked `tests/scripts/test_session_init_keyword_matching.py`. The current precondition would not reject those paths based on prefix alone.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md:414` keeps GT-KB platform-cluster paths out of scope.
- `.claude/rules/codex-review-gate.md:57-65` requires the clause preflight and requires NO-GO when the proposal still has an implementation blocker.

Impact:
This leaves the same risk class as the prior NO-GO's rollback finding: unrelated platform work can be treated as "scoped" because it happens to live under a broad directory that the move touches. With a bulk `git mv` and a single commit, that can bundle unrelated platform changes into the Agent Red move, hide platform modifications inside the rename noise, or discard/revert them during the path-scoped recovery step.

Required revision:
Replace the prefix-only guard with an exact planned write-set check:

- Allow `config/stripe_product_ids.json` only, not `config/`.
- For `tests/`, derive the allowed paths from `manifest-v3` MIGRATES buckets, and explicitly reject STAYS_PLATFORM paths such as `tests/hooks/`, `tests/scripts/`, and `tests/skills/` unless a specific file is intentionally touched and justified.
- For `.github/workflows/` and Docker files, either enumerate the exact files discovered by the grep probes or state that every workflow/Docker file is intentionally in scope for path-string edits.
- Make the rollback list and the clean/scoped-worktree guard use the same generated write-set, so a path cannot be accepted by the precondition while excluded from rollback/accounting.

## Applicability Preflight

- packet_hash: `sha256:e46031631faac47da518f89987dc05ce8f369d498b1dd485e65559c5b8ad43dc`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate when evidence is absent and no owner waiver is cited. Current operative file passes this mechanical gate; the NO-GO is based on the human review finding above.

## Prime Builder Implementation Context

The next revision should be small. Preserve the current direction and mechanical preflight cleanliness, but replace the broad prefix guard with a generated exact write-set. The exact write-set should be produced before any `git mv`, persisted under `.tmp/e1-drift/`, used by the clean/scoped-worktree precondition, and reused by rollback/accounting. Once that is narrowed, this proposal appears close to GO.

No owner decision is needed. This is a Prime Builder revision task.

## Result

NO-GO. Revise and re-file as `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-005.md`.
