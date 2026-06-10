NO-GO

# Loyal Opposition Review - Codex Skill-Loading Failure Cleanup Slice 1

bridge_kind: lo_verdict
Document: gtkb-codex-skill-loading-failure-cleanup-slice-1
Version: 002
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-14 UTC
Responds to: bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md
Verdict: NO-GO

## Decision

NO-GO.

The problem statement is valid: live inspection finds Codex skill adapters whose first line is not YAML frontmatter, while both `scripts/generate_codex_skill_adapters.py --update-registry --check` and `scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` report PASS. The proposal still needs revision because it lacks parser-supported target-path metadata and its repair scope targets generated adapter outputs without including the generator/canonical-source path that creates the malformed files.

## Review Scope

- Durable role resolution: `harness-state/harness-identities.json` maps Codex to harness ID `A`; `harness-state/role-assignments.json` assigns `A` to `loyal-opposition`.
- Live bridge state before review: `bridge/INDEX.md` listed latest status `NEW: bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`, actionable for Loyal Opposition.
- Full thread read: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`.
- Harness-parity guidance loaded via `.codex/skills/harness-parity-review/SKILL.md`.

## Prior Deliberations

Deliberation searches were run for:

```text
codex skills yaml frontmatter adapter harness parity skill load
harness parity generated Codex adapters skill load YAML
```

Relevant results:

- `DELIB-1565` - bridge-skill unified verification found generated skill-surface semantics matter and that parity checks can miss behavior defects.
- `DELIB-1646` and `DELIB-1645` - harness parity baseline NO-GO and later GO; relevant because generated Codex adapters are recognized as the parity surface.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - owner approval of the Codex harness parity specification bundle.
- `DELIB-1473` - Loyal Opposition hygiene-assessment skill advisory; relevant generated-adapter and parity-check context.

No searched deliberation authorizes direct hand-editing of generated Codex adapters as the durable repair path.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:91fec7e65dc2fbb167df351b8aeba09f00ca6b8420c31f7273d2ab56f39f76f0`
- bridge_document_name: `gtkb-codex-skill-loading-failure-cleanup-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
- operative_file: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-codex-skill-loading-failure-cleanup-slice-1`
- Operative file: `bridge\gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

### F1 - Proposal lacks implementation-start-compatible target-path metadata

Severity: P1 governance/authorization blocker.

Observation: The proposal has a prose `## target_paths` section at `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md:56-61`, but it does not include a top-level JSON `target_paths: [...]` line and does not include a `## Files Expected To Change` section.

Evidence: The live implementation-start parser only extracts the top-level `target_paths: [...]` metadata form or backticked paths under `## Files Expected To Change`:

```text
scripts/implementation_authorization.py:28:TARGET_PATHS_RE = re.compile(
scripts/implementation_authorization.py:29:    r"(?:\*\*)?target_paths(?:\*\*)?\s*:(?:\*\*)?\s*(\[[^\n]+\])",
scripts/implementation_authorization.py:228:def extract_target_paths(markdown: str) -> list[str]:
scripts/implementation_authorization.py:240:    body = section_body(markdown, "Files Expected To Change")
scripts/implementation_authorization.py:248:        raise AuthorizationError("Approved proposal is missing concrete target_paths or Files Expected To Change")
```

Deficiency rationale: This proposal requests protected file mutations in `.codex/skills/*/SKILL.md`, script files, doctor code, and tests. After GO, `python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1` would not be able to derive a concrete scope from the approved proposal.

Impact: Prime Builder would be blocked at implementation start, or would need to revise after GO only to make the approval packet machine-readable. A GO must authorize an executable bounded scope, not a prose scope the hook cannot enforce.

Required action: Revise with parser-supported target metadata, for example:

```text
target_paths: [".codex/skills/*/SKILL.md", ".claude/skills/*/SKILL.md", "scripts/generate_codex_skill_adapters.py", "scripts/check_harness_parity.py", "scripts/check_codex_hook_parity.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_codex_skill_load_smoke.py"]
```

Narrow the list during revision if Prime decides some paths are not needed. The final proposal must include every file class it expects implementation to touch.

### F2 - Repair scope targets generated adapter outputs but omits the generator and canonical-source path

Severity: P1 implementation-quality blocker.

Observation: The proposal authorizes `.codex/skills/*/SKILL.md` repair/removal at `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md:58` and says to repair YAML mechanically or remove stale/duplicate skills at lines 65-69. It does not include `scripts/generate_codex_skill_adapters.py`, `scripts/check_harness_parity.py`, or `.claude/skills/*/SKILL.md` in the implementation scope.

Evidence from live files:

- Current load-shape inspection found three Codex skill adapters whose first line is not YAML frontmatter: `.codex/skills/alternatives-investigation/SKILL.md`, `.codex/skills/code-review-audit/SKILL.md`, and `.codex/skills/proposal-review/SKILL.md`.
- `.codex/skills/proposal-review/SKILL.md:1-9` shows the generated adapter block precedes the frontmatter, so the file starts with `<!-- GTKB-CODEX-SKILL-ADAPTER` and the `---` frontmatter appears later.
- The generated adapter block itself says: "Do not edit this adapter directly. Edit the canonical source and regenerate." See `scripts/generate_codex_skill_adapters.py:68-78` for the emitted marker text.
- The generator inserts the marker after frontmatter only when `lines[0].strip() == "---"`; otherwise it prepends the generated block before the source text at `scripts/generate_codex_skill_adapters.py:103-111`.
- The live parity checker adapter path validates metadata/hash parity, then returns PASS at `scripts/check_harness_parity.py:238-271`; it does not validate that the rendered adapter starts with YAML frontmatter.
- `python scripts/generate_codex_skill_adapters.py --update-registry --check` returned `Codex skill adapters: PASS (29 adapters current)`.
- `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` returned `overall_status: PASS`, `PASS: 20`.

Deficiency rationale: Directly hand-fixing generated `.codex` files treats the symptom as the durable source. The observed failure mode can be recreated by the adapter generator itself when a canonical source has a frontmatter shape the generator does not normalize. If implementation edits only `.codex/skills/*/SKILL.md`, a later generator run can reintroduce malformed adapters while parity still reports PASS.

Impact: The cleanup would not be stable. Codex worker startup noise can recur, and the parity surface would continue to overclaim health because "adapter matches canonical source" is not the same as "adapter is loadable by Codex."

Required action: Revise the implementation plan so the durable repair path is one of:

- normalize/fix canonical `.claude/skills/*/SKILL.md` frontmatter and regenerate adapters;
- update `scripts/generate_codex_skill_adapters.py` so rendered adapters always preserve YAML frontmatter at byte/line 1 even with BOM or leading marker anomalies;
- update `scripts/check_harness_parity.py` and/or the doctor path to fail when a Codex skill adapter is hash-current but not loadable.

The revised verification plan should include at least:

```text
python scripts/generate_codex_skill_adapters.py --update-registry --check
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
python -m pytest platform_tests/scripts/test_codex_skill_load_smoke.py -q --tb=short
```

It should also include a deterministic first-line/frontmatter smoke over `.codex/skills/*/SKILL.md`, either through the new doctor check or a focused script/test assertion.

## Positive Confirmations

- The proposal cites the required cross-cutting specifications; applicability preflight passes with `missing_required_specs: []`.
- The clause preflight reports no blocking gaps.
- The stated problem is reproducible: malformed-frontmatter adapter files exist while current generator and parity checks report PASS.
- The owner directive is clear that skill-loading failures should become visible failures rather than hidden startup noise.

## Commands Executed

- `Get-Content -Raw bridge/INDEX.md`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-codex-skill-loading-failure-cleanup-slice-1 --format json`
- `Get-Content -Raw bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1`
- `python -m groundtruth_kb deliberations search --limit 8 "codex skills yaml frontmatter adapter harness parity skill load"`
- `python -m groundtruth_kb deliberations search --limit 8 "harness parity generated Codex adapters skill load YAML"`
- `Get-ChildItem .codex/skills -Recurse -Filter SKILL.md | first-line frontmatter inspection`
- `Get-ChildItem .claude/skills -Recurse -Filter SKILL.md | first-line frontmatter inspection`
- `python scripts/generate_codex_skill_adapters.py --update-registry --check`
- `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json`
- Targeted reads of `scripts/generate_codex_skill_adapters.py`, `scripts/check_harness_parity.py`, `scripts/implementation_authorization.py`, and `.codex/skills/proposal-review/SKILL.md`.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
