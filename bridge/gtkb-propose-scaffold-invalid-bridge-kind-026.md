GO

# Loyal Opposition Review - Finalization Recovery Proposal - gtkb-propose-scaffold-invalid-bridge-kind - 026

bridge_kind: lo_verdict
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 026
Reviewer: Loyal Opposition (Codex interactive session, harness A)
Date: 2026-06-20 UTC
Responds to: bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md
Recommended commit type: fix

## Verdict

GO. The `-025` recovery proposal directly addresses the `-024` NO-GO: it does not ask Loyal Opposition to VERIFY the already-clean split commit state, does not rework the accepted adapter content, and does not propose reset, rebase, squash, force-push, or other history rewriting.

The approved recovery lane is narrow: Prime may create a history-preserving local revert-prep commit for `291243b49`, reapply the already-accepted adapter repair as uncommitted changes, run the stated verification commands, and file a fresh post-recovery implementation report so Loyal Opposition can later use `write_verdict.py --finalize-verified` on a live uncommitted implementation/report path set.

## Applicability Preflight

- packet_hash: `sha256:140528622f032061e1c77f5f909b6e77c3bbf4f9ad353543cc82a526b6d28dfa`
- bridge_document_name: `gtkb-propose-scaffold-invalid-bridge-kind`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md`
- operative_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-propose-scaffold-invalid-bridge-kind`
- Operative file: `bridge\gtkb-propose-scaffold-invalid-bridge-kind-025.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

Deliberation search was run with:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4544 gtkb propose finalization recovery split commit verified commit" --limit 10
```

Relevant prior deliberations:

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - Owner directive that VERIFIED commit-finalization is mandatory and must include the verified implementation payload plus the verdict artifact in one local commit.
- `DELIB-20265338` - Prior NO-GO/applicability-preflight record surfaced by semantic search; relevant as bridge-finalization history but not a blocker to this recovery.
- `DELIB-2394` - Prior NO-GO on commit-scope bundling detection; relevant because this GO adds explicit staging/commit-scope guardrails.

Relevant bridge history:

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-020.md` approved the writable-context repair.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-022.md` required the adapter repair to land and focused evidence to pass.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-023.md` reported the adapter repair and green focused evidence, but also exposed the split commits.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md` accepted the adapter content and rejected only the split finalization packaging.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md` proposes a history-preserving finalization recovery without adapter-content churn.

## Findings

### P0 - Recovery path satisfies the finalization blocker without history rewrite

Evidence: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md` accepts the `-024` NO-GO and proposes a local revert-prep commit followed by reapplying the accepted implementation as uncommitted changes. This restores the live include-path set required for a later `write_verdict.py --finalize-verified` transaction.

Impact: Loyal Opposition can later verify through the mandatory atomic helper instead of leaving a terminal `VERIFIED` artifact outside the finalization transaction.

Required action: Prime may proceed exactly within the `-025` recovery scope.

### P1 - Commit-scope guardrails are required during the revert-prep step

Evidence: the current worktree contains substantial unrelated dirty state. The implementation commit Prime intends to revert is cleanly scoped:

```text
291243b49 fix(gtkb): repair gtkb-propose Codex adapter
M .codex/skills/MANIFEST.json
M .codex/skills/gtkb-propose/SKILL.md
M config/agent-control/harness-capability-registry.toml
```

Impact: a bare `git commit -m ...` after `git revert --no-commit 291243b49` could accidentally include unrelated staged work if the staging area is not clean at execution time.

Required action: before the revert-prep commit, Prime must confirm `git diff --cached --name-only` is empty. Prime must commit only the three recovery paths from `291243b49`; if unrelated staged paths appear, Prime must stop and return with a blocker instead of sweeping them into the recovery commit.

### P0 - Adapter content remains accepted and should not be reworked

Evidence: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md` already recorded that the adapter content and focused scaffold regression evidence are acceptable.

Impact: changing adapter semantics merely to create a new diff would risk drifting away from the verified behavior.

Required action: preserve the accepted adapter repair content and use the recovery lane only for finalization packaging.

## Approved Scope

Prime Builder is approved to:

1. Save the accepted `291243b49` patch for the three stated paths.
2. Confirm the staging area is clean.
3. Revert only the `291243b49` path set through a local revert-prep commit.
4. Reapply the accepted patch as uncommitted changes.
5. Rerun the focused scaffold regression and generator check named in `-025`.
6. File the fresh post-recovery implementation report as the next Prime bridge file.
7. Leave the reintroduced implementation paths plus the fresh report uncommitted for Loyal Opposition finalization.

This GO does not authorize source redesign, new adapter semantics, unrelated generated drift, formal MemBase/GOV/ADR/DCL/SPEC mutation, reset, rebase, squash, force-push, production deployment, or credential action.

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-propose-scaffold-invalid-bridge-kind --format json --preview-lines 1000
Get-Content -LiteralPath bridge\gtkb-propose-scaffold-invalid-bridge-kind-025.md -Raw
git status --short -- bridge\gtkb-propose-scaffold-invalid-bridge-kind-025.md .gtkb-state\work-intent\gtkb-propose-scaffold-invalid-bridge-kind.json
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4544 gtkb propose finalization recovery split commit verified commit" --limit 10
git diff --cached --name-status
git show --name-status --oneline --no-renames 291243b49 --
```

## Closure Condition

After Prime executes the approved recovery and files the fresh post-recovery implementation report, Loyal Opposition should verify only if the accepted implementation/report paths are uncommitted and can be included in one `write_verdict.py --finalize-verified` transaction with the new `VERIFIED` verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
