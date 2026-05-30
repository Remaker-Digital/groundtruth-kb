NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: bridge-auto-dispatch-2026-05-30T04-36-38Z
author_model: GPT-5
author_metadata_source: Codex bridge automation

# Loyal Opposition Review - Ruff Format Pre-File Gate REVISED-2

bridge_kind: proposal_verdict
Document: gtkb-ruff-format-pre-file-gate
Version: 004
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-30 UTC
Responds to: `bridge/gtkb-ruff-format-pre-file-gate-003.md`
Verdict: NO-GO

## Verdict

NO-GO.

The revised proposal closes the prior `-002` P1 findings on the active hook
surface and Ruff interpreter resolution. It now targets `.githooks/pre-commit`,
drops the inactive `.git/hooks` reinstall claim, and specifies a venv-first
Ruff resolver that fails closed when the project venv exists but Ruff is not
available. It also closes the prior advisory-spec citation gap: the
applicability preflight now reports no missing required or advisory specs.

One implementation-gate defect remains. The proposal authorizes and accepts the
generated Codex bridge skill adapter file, but not the generated metadata file
that `scripts/generate_codex_skill_adapters.py` updates as part of the same
operation. If Prime implements as written, either the implementation-start gate
blocks `.codex/skills/MANIFEST.json`, or the adapter changes without its
manifest metadata. A revision should include the generated metadata target(s)
and verification evidence before GO.

## Live Bridge State

Before writing this verdict, live `bridge/INDEX.md` listed:

```text
Document: gtkb-ruff-format-pre-file-gate
REVISED: bridge/gtkb-ruff-format-pre-file-gate-003.md
NO-GO: bridge/gtkb-ruff-format-pre-file-gate-002.md
NEW: bridge/gtkb-ruff-format-pre-file-gate-001.md
```

Latest status `REVISED` was Loyal Opposition-actionable. Full version chain
read: `-001`, `-002`, `-003`. The show-thread helper reported no drift.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:0d34a42d0185059ffb0a5bf509eda8c7f38c95c0655dd883119373142e9490e2`
- bridge_document_name: `gtkb-ruff-format-pre-file-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ruff-format-pre-file-gate-003.md`
- operative_file: `bridge/gtkb-ruff-format-pre-file-gate-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ruff-format-pre-file-gate`
- Operative file: `bridge\gtkb-ruff-format-pre-file-gate-003.md`
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

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner-approved
  standing reliability fast-lane: a standing project, standing authorization,
  and GOV spec for small reliability/defect fixes while preserving bridge
  review and safety gates.
- Deliberation searches for `WI-3473 ruff format pre-file guardrail checklist`
  and `S372 ruff format guardrail checklist` returned `[]`; no prior DA record
  rejects this specific revised approach.
- `bridge/gtkb-ruff-format-pre-file-gate-002.md` is the immediate NO-GO that
  this revision addresses.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` remains
  relevant precedent for avoiding inactive `.git/hooks` targeting. The
  citation-freshness preflight notes that thread is now withdrawn, but the
  cited version is intentionally historical review precedent.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md` is the
  historical formatter-gate NO-GO that motivated WI-3473; `-006` is the latest
  VERIFIED closure.

## Positive Confirmations

- Durable role resolution: Codex harness ID `A` is assigned
  `loyal-opposition`, so latest `NEW` and `REVISED` entries are actionable.
- The selected entry remained live and actionable when reviewed.
- `bridge/gtkb-ruff-format-pre-file-gate-003.md` includes `Project
  Authorization`, `Project`, and `Work Item` metadata.
- `WI-3473` exists in MemBase, is open, has `origin = defect`, and has active
  membership under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers work
  items by active project membership for eligible small reliability fixes. Its
  allowed mutation classes include `source`, `test_addition`, and
  `hook_upgrade`.
- The revised proposal includes a substantive `## Owner Decisions / Input`
  section and maps tests back to linked specifications.
- `git config --get core.hooksPath` returned `.githooks`, and the revised
  proposal targets `.githooks/pre-commit`.
- `python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-ruff-format-pre-file-gate`
  reported no recurring feedback-pattern findings.
- `python scripts/bridge_proposal_wi_id_collision_check.py --bridge-id gtkb-ruff-format-pre-file-gate`
  reported `has_collisions: false`.

## Findings

### F1 (P1) Generated adapter metadata is outside the authorized target path set

**Observation:** REVISED-2 plans to regenerate the Codex bridge skill adapter
but authorizes only `.codex/skills/bridge/SKILL.md`, not the generated adapter
manifest that the generator writes whenever adapter source hashes change.

**Evidence:**

- `bridge/gtkb-ruff-format-pre-file-gate-003.md:26` lists `target_paths` as
  `scripts/check_ruff_format.py`, `.githooks/pre-commit`,
  `.claude/skills/bridge/SKILL.md`, `.codex/skills/bridge/SKILL.md`, and
  `platform_tests/scripts/test_check_ruff_format.py`. It does not list
  `.codex/skills/MANIFEST.json`.
- `bridge/gtkb-ruff-format-pre-file-gate-003.md:117` instructs Prime to
  regenerate `.codex/skills/bridge/SKILL.md` via
  `python scripts/generate_codex_skill_adapters.py`.
- `scripts/generate_codex_skill_adapters.py:246-248` computes
  `.codex/skills/MANIFEST.json` and appends it to the changed-file set when the
  generated manifest content changes.
- `.codex/skills/MANIFEST.json:25-29` stores the bridge adapter path, canonical
  source path, and source SHA for `.claude/skills/bridge/SKILL.md`; changing
  the canonical bridge skill changes the manifest content.
- `config/agent-control/harness-capability-registry.toml:86-89` also stores
  the Codex adapter surface and source SHA for the bridge skill. The generator
  updates registry hashes only when invoked with `--update-registry`
  (`scripts/generate_codex_skill_adapters.py:259,267-268`).

**Deficiency rationale:** Bridge implementation authorization depends on
complete `target_paths` metadata. The proposed implementation cannot both run
the declared generator and stay within the declared write scope unless the
generated metadata file is included. If Prime omits the manifest update, Codex
skill adapter metadata drifts from the canonical skill source. If Prime includes
the manifest update, the implementation touches a path not authorized by this
proposal.

**Impact:** The implementation can fail at the implementation-start gate or
create stale generated-skill metadata. Either outcome undermines the stated
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` parity acceptance criterion.

**Required action:** Revise the proposal to include
`.codex/skills/MANIFEST.json` in `target_paths`, acceptance criteria, and
verification evidence. Also choose one of these registry treatments:

1. Invoke `python scripts/generate_codex_skill_adapters.py --update-registry`
   and include `config/agent-control/harness-capability-registry.toml` in
   `target_paths`; or
2. Explicitly keep the registry out of scope, do not use `--update-registry`,
   and add post-implementation evidence explaining why the registry's stored
   source SHA is intentionally unchanged or not expected to drift.

## Required Revision

1. Refile as `REVISED` with `.codex/skills/MANIFEST.json` added anywhere the
   generated Codex adapter work is scoped: `target_paths`, spec-to-test mapping,
   acceptance criteria, and post-implementation evidence requirements.
2. Decide whether the harness capability registry should be regenerated with
   `--update-registry`. If yes, add `config/agent-control/harness-capability-registry.toml`
   to `target_paths`; if no, state that decision explicitly and verify no
   unintended registry drift.
3. Preserve the corrected active-hook design: `.githooks/pre-commit`,
   `scripts/check_ruff_format.py`, venv-first Ruff resolution, fail when the
   project venv exists but Ruff is unresolvable, and the active-hook dry-run
   demonstration.

## Commands Executed

```text
Get-Content -Raw .codex/skills/bridge/SKILL.md
Get-Content -Raw .codex/skills/verify/SKILL.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw harness-state/harness-identities.json
Get-Content -Raw harness-state/role-assignments.json
Get-Content -Raw bridge/gtkb-ruff-format-pre-file-gate-001.md
Get-Content -Raw bridge/gtkb-ruff-format-pre-file-gate-002.md
Get-Content -Raw bridge/gtkb-ruff-format-pre-file-gate-003.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/codex-review-gate.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw .claude/rules/loyal-opposition.md
Get-Content -Raw .claude/rules/report-depth-prime-builder-context.md
Get-Content -Raw .claude/rules/project-root-boundary.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-ruff-format-pre-file-gate --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-ruff-format-pre-file-gate
python scripts/bridge_proposal_wi_id_collision_check.py --bridge-id gtkb-ruff-format-pre-file-gate
git config --get core.hooksPath
Get-Content -Raw .githooks/pre-commit
python -m groundtruth_kb --help
python -m ruff --version
groundtruth-kb\.venv\Scripts\python.exe -m ruff --version
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3473 ruff format pre-file guardrail checklist" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "S372 ruff format guardrail checklist" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-3473 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
rg -n "narrative|NARRATIVE|skills/bridge|\.claude/skills|\.codex/skills" config/governance .claude/rules bridge/gtkb-ruff-format-pre-file-gate-003.md
rg -n "MANIFEST|update-registry|write|bridge/SKILL|codex/skills" scripts/generate_codex_skill_adapters.py
Select-String -Path scripts/generate_codex_skill_adapters.py -Pattern "manifest_path|MANIFEST_NAME|_write_if_changed|--update-registry|update_registry"
Select-String -Path .codex/skills/MANIFEST.json -Pattern "bridge/SKILL.md|source_sha256"
Select-String -Path config/agent-control/harness-capability-registry.toml -Pattern "canonical_name = ""gtkb-bridge""|canonical_source = ""\.claude/skills/bridge/SKILL.md""|surface = ""\.codex/skills/bridge/SKILL.md""|adapter_source = ""\.claude/skills/bridge/SKILL.md"""
git status --short
```

Notes:

- `python -m groundtruth_kb --help` failed under system Python
  (`No module named groundtruth_kb`), matching the existing hook's dependency
  on the configured `PYTHON` environment or project venv for current hook
  commands.
- `python -m ruff --version` failed under system Python
  (`No module named ruff`); the project venv reported `ruff 0.15.12`. This
  supports the revised proposal's venv-first Ruff resolution requirement.
- `bridge_citation_freshness_preflight.py` reported stale historical bridge
  citations. I did not treat those as blockers because the revised proposal
  uses them as historical precedent and motivation rather than as latest state.
- The repository worktree is heavily dirty from other sessions; this verdict
  touched only `bridge/gtkb-ruff-format-pre-file-gate-004.md` and
  `bridge/INDEX.md`.

## Owner Action Required

None. This auto-dispatched harness cannot ask the owner interactively, and no
owner decision is required for Prime to add the generated metadata path(s) and
refile.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
