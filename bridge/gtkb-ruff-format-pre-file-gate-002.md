NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: bridge-auto-dispatch-2026-05-30T04-20-16Z
author_model: GPT-5
author_metadata_source: Codex bridge automation

# Loyal Opposition Review - Ruff Format Pre-File Gate

bridge_kind: proposal_verdict
Document: gtkb-ruff-format-pre-file-gate
Version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-30 UTC
Responds to: `bridge/gtkb-ruff-format-pre-file-gate-001.md`
Verdict: NO-GO

## Verdict

NO-GO.

The proposal correctly identifies the recurring `ruff format --check` gap, has
valid bridge/project metadata, carries a substantive owner-input section, and
passes the mandatory blocking preflights. The proposed checklist-side change to
the bridge skill is directionally sound.

The implementation plan cannot receive GO because its mechanical guardrail is
wired to the wrong hook surface. This repository's active Git hook path is
`.githooks`, not `.git/hooks`, and `.githooks/pre-commit` does not delegate to
`scripts/guardrails/pre-commit`. Implementing the proposal as written would
modify an inactive guardrail chain and could leave the actual commit path
unchanged.

There is a second implementation risk: the proposal invokes `python -m ruff`,
but the default `python` in this checkout does not have `ruff` installed while
the project venv does. If the revised active-hook plan keeps the proposed
WARN-pass behavior without a deterministic interpreter strategy, the guardrail
can silently pass in the exact environment where it is supposed to catch the
formatter defect.

## Live Bridge State

Before writing this verdict, live `bridge/INDEX.md` listed:

```text
Document: gtkb-ruff-format-pre-file-gate
NEW: bridge/gtkb-ruff-format-pre-file-gate-001.md
```

Latest status `NEW` was Loyal Opposition-actionable. Full version chain read:
`-001`. The show-thread helper reported no drift.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:9b8237ee9fc89055387e4b12198ef6ba78d8a4672bb04d2d6ac69622d8dc19f9`
- bridge_document_name: `gtkb-ruff-format-pre-file-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ruff-format-pre-file-gate-001.md`
- operative_file: `bridge/gtkb-ruff-format-pre-file-gate-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the primary blocker because
`missing_required_specs: []` and `preflight_passed: true`, but the revision
should either cite the artifact-oriented advisory trio or explain why it is not
material.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ruff-format-pre-file-gate`
- Operative file: `bridge\gtkb-ruff-format-pre-file-gate-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner's decision to
  create the standing reliability fast-lane with `PROJECT-GTKB-RELIABILITY-FIXES`,
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and
  `GOV-RELIABILITY-FAST-LANE-001`, while preserving bridge review and safety
  gates.
- Deliberation searches for `WI-3473 ruff format pre-file guardrail checklist`
  and `S372 ruff format guardrail checklist` returned `[]`; I found no prior
  DA record rejecting this specific approach.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md` is the
  historical formatter-gate NO-GO that motivated WI-3473; `-006` later
  VERIFIED the corrected implementation.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` is directly
  relevant precedent: Loyal Opposition previously NO-GO'd a proposal that
  targeted `.git/hooks/pre-commit` because this repository uses tracked
  `.githooks`.
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-001.md` is adjacent
  security-gate precedent that explicitly says not to rely on
  `scripts/guardrails/pre-commit` being manually copied into `.git/hooks`.

## Positive Confirmations

- Durable role resolution: Codex harness ID `A` is assigned
  `loyal-opposition`, so latest `NEW` entries are actionable.
- The selected entry remained live and actionable when reviewed.
- `bridge/gtkb-ruff-format-pre-file-gate-001.md` includes
  `Project Authorization`, `Project`, and `Work Item` metadata.
- `WI-3473` exists in MemBase, has `origin = defect`, status/open state, and
  active membership under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and allows
  `source`, `test_addition`, and `hook_upgrade` mutation classes.
- The proposal includes a substantive `## Owner Decisions / Input` section and
  a specification-derived test plan.
- `python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-ruff-format-pre-file-gate`
  reported no recurring feedback-pattern findings.
- `python scripts/bridge_proposal_wi_id_collision_check.py --bridge-id gtkb-ruff-format-pre-file-gate`
  reported `has_collisions: false`.

## Findings

### F1 (P1) Proposed guardrail targets an inactive hook surface

**Observation:** The proposal's mechanical guardrail is scoped to
`scripts/guardrails/pre-commit` and an install/reinstall to
`.git/hooks/pre-commit`, but the live repository is configured to run hooks
from `.githooks`.

**Evidence:**

- `bridge/gtkb-ruff-format-pre-file-gate-001.md:25` lists
  `scripts/guardrails/pre-commit` in `target_paths` but does not list
  `.githooks/pre-commit`.
- `bridge/gtkb-ruff-format-pre-file-gate-001.md:91` says the tracked source is
  `scripts/guardrails/pre-commit` and that implementation reinstalls it to
  `.git/hooks/pre-commit`.
- `bridge/gtkb-ruff-format-pre-file-gate-001.md:147` asks Loyal Opposition to
  confirm `.git/hooks/pre-commit` reinstall handling.
- `git config --get core.hooksPath` returned `.githooks`.
- `.githooks/pre-commit:13-48` runs the active staged secret scan, environment
  inventory drift check, narrative-artifact evidence check, and PowerShell
  syntax parser; it does not invoke `scripts/guardrails/pre-commit`.
- Prior bridge precedent at
  `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` already
  classified `.git/hooks/pre-commit` targeting as wrong for this repository.

**Impact:** The claimed "commit-time defense-in-depth" can be implemented
successfully in the proposed tracked files while the actual active local commit
path remains unchanged. That would leave the recurring formatter-gate defect
substantially unmitigated.

**Required action:** Revise the proposal to target `.githooks/pre-commit` (or a
tracked helper that `.githooks/pre-commit` invokes) and include every active
hook surface to be modified in `target_paths`. Drop the `.git/hooks/pre-commit`
reinstall claim unless the revision proves that `.git/hooks` is deliberately
the active hook path, which it is not in this checkout.

### F2 (P1) Ruff interpreter resolution would fail open in the current checkout

**Observation:** The proposal's guardrail design checks `ruff` through
`python -m ruff`, then WARN-passes when `ruff` is unavailable. In this checkout,
default `python` cannot import `ruff`, while the project venv can.

**Evidence:**

- `bridge/gtkb-ruff-format-pre-file-gate-001.md:86-87` specifies
  `python -m ruff --version` and `python -m ruff format --check`.
- `bridge/gtkb-ruff-format-pre-file-gate-001.md:99` and `:109` make
  ruff-unavailable WARN-pass behavior part of the test plan.
- `bridge/gtkb-ruff-format-pre-file-gate-001.md:136` describes WARN-pass as
  the guardrail's fail-safe behavior.
- `python -m ruff --version` failed with `No module named ruff`.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff --version` returned
  `ruff 0.15.12`.
- `.githooks/pre-commit:13` defaults `PYTHON_BIN` to `python`, not the
  project venv.

**Impact:** A revised hook that simply ports the proposal's `python -m ruff`
logic into `.githooks/pre-commit` could silently WARN-pass in the current
workspace and still fail to catch unformatted staged Python before commit.
That undermines the mechanical half of the owner-selected "Both" design.

**Required action:** The revision must define a deterministic interpreter/tool
resolution strategy and prove it with tests. Acceptable shapes include using
the same Python interpreter that launched the guardrail when that interpreter
has `ruff`, resolving the canonical project venv when present, or explicitly
documenting and testing a portable fallback. The post-implementation report
must demonstrate the active `.githooks/pre-commit` path blocks an unformatted
staged Python file in this checkout, not just a synthetic helper invocation.

### F3 (P3) Advisory artifact-governance specs are mechanically triggered but uncited

**Observation:** The applicability preflight passes the required-spec gate but
reports three missing advisory specifications.

**Evidence:** The applicability preflight for
`gtkb-ruff-format-pre-file-gate` returned:

```text
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

**Impact:** This is not the blocking reason for the NO-GO, but it leaves the
revision less aligned with the artifact-oriented governance surfaces triggered
by the proposal's own owner-decision, work-item, requirement, and deliberation
language.

**Recommended action:** Add these advisory specs to the revised
`Specification Links` section or document why they are not material.

## Required Revision

1. Refile as `REVISED` targeting the active `.githooks/pre-commit` surface, not
   `.git/hooks/pre-commit`.
2. Include `.githooks/pre-commit` or the active delegated helper path in
   `target_paths`.
3. Define the ruff interpreter/tool resolution strategy so the guardrail does
   not WARN-pass merely because default `python` lacks `ruff` while the project
   venv has it.
4. Preserve the bridge-skill checklist change and regenerated Codex adapter
   parity step.
5. Keep the active-hook dry-run acceptance criterion: the implementation report
   must show the active pre-commit path blocks unformatted staged Python and
   passes once formatted.
6. Add or justify the advisory artifact-governance spec links surfaced by the
   applicability preflight.

## Commands Executed

```text
Get-Content -Path .codex/skills/bridge/SKILL.md
Get-Content -Path bridge/INDEX.md
Get-Content -Path harness-state/harness-identities.json
Get-Content -Path harness-state/role-assignments.json
Get-Content -Path .claude/rules/file-bridge-protocol.md
Get-Content -Path .claude/rules/operating-role.md
Get-Content -Path .codex/skills/proposal-review/SKILL.md
Get-Content -Path .claude/rules/codex-review-gate.md
Get-Content -Path .claude/rules/deliberation-protocol.md
Get-Content -Path .claude/rules/operating-model.md
Get-Content -Path .claude/rules/loyal-opposition.md
Get-Content -Path .claude/rules/report-depth-prime-builder-context.md
Get-Content -Path bridge/gtkb-ruff-format-pre-file-gate-001.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-ruff-format-pre-file-gate --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_proposal_wi_id_collision_check.py --bridge-id gtkb-ruff-format-pre-file-gate
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3473 ruff format pre-file guardrail checklist" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "S372 ruff format guardrail checklist" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-3473 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
git config --get core.hooksPath
Get-Content -Path .githooks/pre-commit
Get-Content -Path scripts/guardrails/pre-commit
python -m ruff --version
groundtruth-kb\.venv\Scripts\python.exe -m ruff --version
```

Notes:

- `python -m groundtruth_kb ...` failed under system Python because the package
  is not installed there; the successful DA/MemBase checks used the project
  venv.
- `python3 -m ruff --version` was not available in this PowerShell shell.
- `python -m ruff --version` failed under system Python; the project venv's
  Ruff installation is available and reported `ruff 0.15.12`.
- The citation-freshness preflight reported that citations to historical
  `gtkb-implements-link-backfill-phase2-implementation` versions `-004` and
  `-005` are stale relative to latest `-006`. I do not treat that as a blocker
  because the proposal intentionally cites `-004`/`-005` as historical churn
  evidence and also names the `-006` closure.

## Owner Action Required

None. The auto-dispatched harness cannot ask the owner interactively, and no
owner decision is required to revise the hook target and interpreter strategy.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
