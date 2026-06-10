GO

# Loyal Opposition Review - Antigravity Onboarding WI-3347 Capability Adapters

bridge_kind: lo_verdict
Document: gtkb-antigravity-capability-adapters
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-antigravity-capability-adapters-001.md
Recommended commit type: feat:

## Verdict

GO. The implementation proposal at `bridge/gtkb-antigravity-capability-adapters-001.md` is approved for Prime Builder implementation within the stated `target_paths`.

The proposal satisfies the bridge gates for an implementation proposal:

- It includes project authorization metadata, `target_paths`, requirement sufficiency, specification links, owner-decision evidence, prior deliberation evidence, spec-derived verification mapping, acceptance criteria, and rollback notes.
- The live registry supports the claimed role-scoped set: 32 skill capabilities, 21 whose `required_for_roles` includes `loyal-opposition`, 11 Prime-only skills, and one shared hook that does not require an Antigravity skill adapter.
- `.agent/skills/<name>/SKILL.md` is the correct target for this slice. It is supported by the verified WI-3345 research document, the verified WI-3346 integration config, and the current Google Codelab documentation for Antigravity skills.
- The dedicated-generator design is acceptable for WI-3347 because the two genuine non-parity behaviors - LO-role filtering and BOM-aware frontmatter placement - are local to Antigravity. Consolidating Codex and Antigravity generators is a valid deterministic-services backlog candidate, not a blocker for this slice.
- Deferring `scripts/check_harness_parity.py` Antigravity awareness is acceptable for this slice. The current parity checker is explicitly limited to `claude` and `codex`, while the proposal's generator `--check` mode and test module provide slice-local drift protection for the new adapters.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-capability-adapters
```

Observed result:

- packet_hash: `sha256:43d4734842a56b83c56d68c2f6c9fdb7e5f3da701ab7a842109a0f2b661a2d0d`
- bridge_document_name: `gtkb-antigravity-capability-adapters`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-antigravity-capability-adapters-001.md`
- operative_file: `bridge/gtkb-antigravity-capability-adapters-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-capability-adapters
```

Observed result:

- Bridge id: `gtkb-antigravity-capability-adapters`
- Operative file: `bridge\gtkb-antigravity-capability-adapters-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Prior Deliberations

Deliberation Archive searches were run before review:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "Antigravity capability adapters WI-3347 role-scoped parity skills" --limit 8 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "DELIB-2079 Q8 role-scoped parity Antigravity skill capabilities loyal-opposition" --limit 8 --json
```

Observed result for both search queries: `[]`.

Direct retrieval confirmed the controlling deliberations:

- `DELIB-2079` records the owner-decided Antigravity Integration design. Q1 places Antigravity at harness identity `C` in the `loyal-opposition` role; Q8 selects role-scoped parity for capabilities whose registry `required_for_roles` includes `loyal-opposition` or both roles.
- `DELIB-2080` records the role-portability amendment and keeps the single-prime-builder invariant while allowing any active harness to hold either operating role.
- `DELIB-2081` is the current owner-decision lineage for the superseding project authorization row. The live authorization remains active for `PROJECT-ANTIGRAVITY-INTEGRATION` and includes `REQ-HARNESS-REGISTRY-001`.

No prior deliberation found during this review supersedes the WI-3347 proposal.

## Evidence Checks

### Live Bridge State

- Live `bridge/INDEX.md` was read before acting.
- Durable role resolution maps Codex harness `A` to `loyal-opposition`.
- The selected entry's live latest status remained `NEW: bridge/gtkb-antigravity-capability-adapters-001.md`.
- `show_thread_bridge.py` reported the `gtkb-antigravity-capability-adapters` thread found with no drift and a single `NEW` version.

### Registry And Role-Scoped Set

Read-only TOML parsing of `config/agent-control/harness-capability-registry.toml` returned:

- skill_count: 32
- lo_scoped_count: 21
- pb_only_count: 11
- hook_count: 1
- LO-scoped directories: `alternatives-investigation`, `arch-audit`, `bridge`, `check-deliberations`, `code-review-audit`, `lo-opportunity-radar`, `codex-report`, `decision-capture`, `harness-parity-review`, `kb-assert`, `kb-query`, `kb-session-wrap`, `kb-session-wrap-scan`, `kb-work-item`, `projects`, `proposal-review`, `release-candidate-gate`, `run-tests`, `send-review`, `structural-hygiene-review`, `verify`.
- Prime-only directories: `assertion-triage`, `bridge-propose`, `deploy`, `kb-adr`, `kb-batch`, `kb-promote`, `kb-spec`, `seed-tenant`, `spec-intake`, `gtkb-benchmarks`, `grill-me-for-clarification`.
- Shared hook: `hook.advisory-router-scan`.

This exactly matches the proposal's 21-adapter scope and its exclusion of the 11 Prime-only skills plus the shared hook.

### Antigravity Skill Target

Evidence supports `.agent/skills/`:

- `.gtkb-state/antigravity-research/wi-3345-findings.md` records RQ2 as determined-with-evidence: workspace skills use `.agent/skills/<skill-name>/SKILL.md`, with YAML frontmatter and a mandatory `description`.
- `bridge/gtkb-antigravity-ide-research-spike-004.md` VERIFIED the WI-3345 research spike and treated RQ2 as sufficient evidence for downstream skill parity.
- `.antigravity/config.toml` records `skills_dir = ".agent/skills"` for later onboarding slices.
- `bridge/gtkb-antigravity-integration-directory-004.md` VERIFIED the WI-3346 integration directory carrying that config.
- Current Google Codelab documentation, "Authoring Google Antigravity Skills", describes Antigravity skills as directory packages with `SKILL.md`, workspace scope under `<workspace-root>/.agent/skills/`, YAML frontmatter, optional `name`, and mandatory `description`: https://codelabs.developers.google.com/getting-started-with-antigravity-skills

The stale MemBase work-item description that says `.antigravity/skills/` is a known stale pre-research description, and the proposal surfaces it rather than hiding it. Implementing `.agent/skills/` is the correct path for WI-3347.

### In-Root And Tracking

- `Test-Path .agent` returned no existing `.agent` directory before this implementation.
- `git check-ignore -v .agent/skills/example/SKILL.md` returned no ignore match, so `.agent/skills` artifacts are not excluded by repository ignore rules.
- All proposed target paths are under `E:\GT-KB`.
- No `applications/` path is in scope.

### Generator Design And Existing Parity Tooling

- `scripts/generate_codex_skill_adapters.py` already provides reusable helper behavior for canonical-body hashing, generated-block stripping, adapter rendering, registry block writing, manifest generation, and check mode.
- `platform_tests/scripts/test_generate_codex_skill_adapters.py` provides a local test pattern for adapter generation, check mode, current-state drift pass, and registry updates.
- `scripts/check_harness_parity.py` currently declares `KNOWN_HARNESSES = ("claude", "codex")` and uses the Codex adapter marker. Running `python scripts/check_harness_parity.py --all --markdown` reported PASS for Claude/Codex only; it does not yet claim Antigravity coverage.

Deferring `check_harness_parity.py` Antigravity awareness is acceptable because the proposal does not rely on that tool for WI-3347 drift protection. The proposed generator's own `--check` mode and test module cover this slice, while the parity-tool extension remains appropriate follow-on work.

## Findings

No blocking findings.

### P3-NON-BLOCKING - Rollback prose contains one stale sentence about existing-file edits

Observation: The proposal correctly lists `config/agent-control/harness-capability-registry.toml` as an existing file to be modified, and its rollback text correctly says the registry `[capabilities.antigravity]` blocks are removable with a corrective edit. The final rollback sentence then says, "No existing file is modified," which is false for the registry edit.

Deficiency rationale: This does not create implementation ambiguity because the `target_paths`, "Files Expected To Change", and rollback block all otherwise identify the registry mutation. It is still a small narrative inconsistency that should not be repeated in the post-implementation report.

Recommended action: In the implementation report, state plainly that the registry is an existing file modified by adding/removing `[capabilities.antigravity]` blocks. Do not repeat the "No existing file is modified" sentence.

Disposition: Non-blocking. The rollback procedure is substantively adequate.

## Implementation Conditions For Prime Builder

- Keep implementation inside the approved `target_paths`.
- The implementation report must enumerate the 21 generated `.agent/skills/<name>/SKILL.md` adapters and confirm no adapters exist for the 11 Prime-only skills or the shared hook.
- The implementation report must include executed evidence for `python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py`, `python scripts/generate_antigravity_skill_adapters.py --check`, TOML parsing of the registry with 21 Antigravity blocks, and directory inspection of `.agent/skills/`.
- The implementation report must confirm `scripts/generate_codex_skill_adapters.py` remains unmodified.
- If Prime files the deterministic-services consolidation backlog item, cite this GO verdict and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`; do not bundle the consolidation into WI-3347.

## Opportunity Radar

No new advisory filed. The material deterministic-services opportunity - consolidating Codex and Antigravity skill-adapter generators behind a harness-general core - is already surfaced inside the proposal and is better routed as a follow-on backlog item after WI-3347 lands.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
