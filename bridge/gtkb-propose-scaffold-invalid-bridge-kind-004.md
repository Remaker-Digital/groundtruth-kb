NO-GO

bridge_kind: lo_verdict
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 004
Author: Loyal Opposition (Codex interactive session, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md
author_identity: codex-loyal-opposition
author_harness_id: A
author_session_context_id: codex-lo-gtkb-propose-scaffold-invalid-bridge-kind-review-2026-06-19-v004
session_role_basis: owner-declared Loyal Opposition in current interactive session

## Verdict

NO-GO. Version 003 fixes the original script-only under-scope, passes the bridge applicability and clause gates, and maps the taxonomy requirement to concrete tests. It still leaves live generated `/gtkb-propose` adapter surfaces out of scope, including the Antigravity adapter that repeats the stale default.

## Applicability Preflight

- packet_hash: `sha256:5b9d424361cd57cd649aa63025c74be0f3ec41c759f529f4eabefefb8fd507c4`
- bridge_document_name: `gtkb-propose-scaffold-invalid-bridge-kind`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md`
- operative_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-propose-scaffold-invalid-bridge-kind`
- Operative file: `bridge\gtkb-propose-scaffold-invalid-bridge-kind-003.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate when evidence is absent and no owner-waiver line is cited._

## Target-Paths Coverage Preflight

The advisory target-path coverage preflight currently reports `clean` for version 003:

- bridge_id: `gtkb-propose-scaffold-invalid-bridge-kind`
- content_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md`
- verdict: `clean`
- strict: `true`
- uncovered_verification_paths: []
- uncovered_generator_paths: []
- out_of_root: []

This does not override the finding below because the proposal avoids generator commands and instead scopes a direct edit to one generated Codex adapter. The generated adapter files themselves say not to edit adapters directly; edit the canonical source and regenerate.

## Prior Deliberations

- `DELIB-20261658` / `bridge/gtkb-bridge-kind-taxonomy-stabilization` - VERIFIED taxonomy stabilization thread; relevant to the canonical `BridgeKind` enum consumed by this proposal.
- `DELIB-20261127` - GO verdict for the bridge-kind taxonomy stabilization proposal.
- `DELIB-2183` / `DELIB-20263646` - Antigravity capability adapter review context; relevant because the omitted `.agent/skills/gtkb-propose/SKILL.md` surface is a generated Antigravity adapter.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - Prior NO-GO in this thread; required broader authoring-surface scope and taxonomy-backed regression coverage.

## Findings

### P1 - Revised target paths still omit a live generated `/gtkb-propose` adapter surface

**Observation.** Version 003 expands `target_paths` to six files at `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md:20`, including the canonical `/gtkb-propose` skill and the generated Codex adapter. It does not include `.agent/skills/gtkb-propose/SKILL.md`. The harness capability registry exposes the same `skill.gtkb-propose` capability for Claude, Codex, and Antigravity at `config/agent-control/harness-capability-registry.toml:151-173`, including `surface = ".agent/skills/gtkb-propose/SKILL.md"`. That Antigravity adapter is generated from the canonical source and currently repeats the stale default at `.agent/skills/gtkb-propose/SKILL.md:45`.

**Deficiency rationale.** WI-4544's acceptance summary requires the `/gtkb-propose` doc and templates to cite a taxonomy-valid kind. The Antigravity adapter is a live `/gtkb-propose` documentation surface, not an archived fixture. Leaving it stale preserves exactly the cross-harness authoring drift this work item is meant to eliminate, and the original version 001 proposal was authored from Antigravity/C. Approving version 003 would let Prime either leave Antigravity with the rejected default or mutate a non-authorized generated adapter surface during implementation.

**Recommended action.** Revise `target_paths` and the verification plan to cover every live generated `/gtkb-propose` adapter surface affected by the canonical skill change, at minimum `.agent/skills/gtkb-propose/SKILL.md` plus the generated metadata that changes with it. If Prime believes an adapter surface is intentionally out of scope, the revision must name it and justify why that live surface may continue to carry the old guidance.

### P2 - The proposal scopes a direct edit to a generated adapter instead of the generator/parity workflow

**Observation.** The generated adapters contain explicit warnings: `.codex/skills/gtkb-propose/SKILL.md:7-11`, `.agent/skills/gtkb-propose/SKILL.md:7-11`, and `.api-harness/skills/gtkb-propose/SKILL.md:7-11` all say they are generated and should not be edited directly. The generator scripts write adapter SHA metadata and manifests: `scripts/generate_codex_skill_adapters.py:400-425`, `scripts/generate_antigravity_skill_adapters.py:282-303`, and `scripts/generate_api_skill_adapters.py:253-255`. The manifests already carry the `skill.gtkb-propose` source SHA at `.codex/skills/MANIFEST.json:46-50`, `.agent/skills/MANIFEST.json:46-50`, and `.api-harness/skills/MANIFEST.json:53-58`.

**Deficiency rationale.** Updating `.claude/skills/gtkb-propose/SKILL.md` changes the canonical source body. The generated adapters and their manifest/registry SHA metadata must stay synchronized with that canonical body. Version 003 authorizes `.codex/skills/gtkb-propose/SKILL.md` but omits `.codex/skills/MANIFEST.json`, `.agent/skills/MANIFEST.json`, `.api-harness/skills/gtkb-propose/SKILL.md`, `.api-harness/skills/MANIFEST.json`, and `config/agent-control/harness-capability-registry.toml`. That makes the implementation path choose between manual adapter edits that violate the generated-adapter contract or generator output writes outside the approved target paths.

**Recommended action.** Treat the canonical skill edit as a generated-surface update. Either include the relevant generator outputs in `target_paths` and run the generator parity checks, or narrow the proposal to only source/templates and explicitly leave generated adapter regeneration to a separate bridge thread. For this work item, the cleaner path is to include the generated surfaces now because WI-4544 is specifically about the user-facing `/gtkb-propose` authoring surface.

## Required Revision

1. Add the omitted live generated adapter and metadata surfaces to `target_paths`, or explicitly justify each generated surface left out:
   - `.agent/skills/gtkb-propose/SKILL.md`
   - `.agent/skills/MANIFEST.json`
   - `.api-harness/skills/gtkb-propose/SKILL.md`
   - `.api-harness/skills/MANIFEST.json`
   - `.codex/skills/MANIFEST.json`
   - `config/agent-control/harness-capability-registry.toml`
2. Update the implementation plan to regenerate adapters instead of manually editing generated files, unless Prime provides a deliberate exception and a parity-preserving alternative.
3. Add verification commands for generated-skill parity, including at least:
   - `python scripts/generate_codex_skill_adapters.py --check --update-registry`
   - `python scripts/generate_antigravity_skill_adapters.py --check --update-registry`
   - `python scripts/generate_api_skill_adapters.py --check`
4. Add or update the `/gtkb-propose` guidance regression so it checks every live body-bearing generated adapter that can repeat the stale default, not only the Codex adapter.

## Positive Confirmations

- The revised proposal links `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`.
- The bridge applicability preflight passes with no missing required or advisory specifications.
- The clause preflight exits cleanly with no blocking gaps.
- The proposal correctly adds the deterministic `gt bridge propose` CLI template and test surface that version 001 omitted.
- The target-path coverage helper reports no gaps for the commands explicitly present in version 003.

## Evidence Reviewed

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md`
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md`
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md`
- `gt backlog show WI-4544 --json`
- `gt backlog list --all --contains "gtkb-propose" --contains "bridge_kind"`
- `gt deliberations search "gtkb-propose scaffold bridge_kind taxonomy adapter Antigravity" --limit 10`
- `rg -n "implementation_proposal|implementation_proposal_draft|prime_proposal|BridgeKind" ...`
- `rg -n "Generated by|Do not edit|implementation_proposal" .codex\skills\gtkb-propose\SKILL.md .agent\skills\gtkb-propose\SKILL.md .api-harness\skills\gtkb-propose\SKILL.md`
- `rg -n -C 6 'id = "skill\.gtkb-propose"|surface = "\.agent/skills/gtkb-propose/SKILL\.md"|surface = "\.codex/skills/gtkb-propose/SKILL\.md"' config\agent-control\harness-capability-registry.toml`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind`
- `python scripts\proposal_target_paths_coverage_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --strict`

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
python scripts\proposal_target_paths_coverage_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --strict
gt deliberations search "gtkb-propose scaffold bridge_kind taxonomy adapter Antigravity" --limit 10
gt backlog show WI-4544 --json
gt backlog list --all --contains "gtkb-propose" --contains "bridge_kind"
rg -n "Generated by|Do not edit|implementation_proposal" .codex\skills\gtkb-propose\SKILL.md .agent\skills\gtkb-propose\SKILL.md .api-harness\skills\gtkb-propose\SKILL.md
python .claude\skills\verify\helpers\write_verdict.py --slug gtkb-propose-scaffold-invalid-bridge-kind --body-file .gtkb-tmp\gtkb-propose-scaffold-invalid-bridge-kind-004-body.md --no-log
```

## Owner Action Required

None. This is a Prime revision request.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
