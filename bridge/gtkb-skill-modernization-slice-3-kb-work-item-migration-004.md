NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
reviewed_document: gtkb-skill-modernization-slice-3-kb-work-item-migration
reviewed_version: 003
verdict_version: 004
date: 2026-05-29 UTC

# Loyal Opposition Verdict - Skill Modernization Slice 3 kb-work-item Migration Revision

## Verdict

NO-GO.

The -003 revision fixes the prior GOV-13 orphan-test defect and corrects the bridge-kind token. The remaining blocking issue is adapter/registry parity: the proposal knowingly accepts a stale `source_sha256` in `config/agent-control/harness-capability-registry.toml` after changing the canonical `.claude/skills/kb-work-item/SKILL.md`. That is not a harmless deferred chore; the existing generator check, harness parity checker, and parity tests are designed to fail on that state. The proposal also still omits the registered Antigravity adapter path for the same canonical skill, despite the -002 re-review criterion requiring an explicit non-Codex adapter boundary.

## Prior Deliberations

- Deliberation searches for `kb-work-item migration add-work-item GOV-12 GOV-13 skill modernization` and `Skill Modernization Slice 3 kb-work-item` returned no additional rows.
- Direct review of cited records remains sufficient: `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repeated deterministic plumbing into services; `DELIB-S364-KB-WORK-ITEM-MIGRATION-SLICE-PAUTH` authorized this slice as a work-item + linked-test + phase chain.
- The prior bridge verdict `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-002.md` is the active rejected-alternative record for this revision.

## Applicability Preflight

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-skill-modernization-slice-3-kb-work-item-migration`
- exit: 0

```text
## Applicability Preflight

- packet_hash: `sha256:d956c757725b230e213a500856b2d61ac56f5b71251858e9d1c437f9b72a4ddd`
- bridge_document_name: `gtkb-skill-modernization-slice-3-kb-work-item-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md`
- operative_file: `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:application isolation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-skill-modernization-slice-3-kb-work-item-migration`
- exit: 0

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-skill-modernization-slice-3-kb-work-item-migration`
- Operative file: `bridge\gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - Registry source-hash drift is a planned parity regression

Severity: P1 governance drift

Observation: The revised proposal edits the canonical `.claude/skills/kb-work-item/SKILL.md`, regenerates `.codex/skills/kb-work-item/SKILL.md` and `.codex/skills/MANIFEST.json`, but explicitly excludes `config/agent-control/harness-capability-registry.toml`. It states that the registry's kb-work-item source hash will be left stale and shown as a pending delta in the post-implementation report.

Evidence:
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md:37-41` includes the canonical skill and generated Codex surfaces, then excludes the registry.
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md:92-95` states the canonical edit changes the source sha256 and leaves the registry source hash stale.
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md:121` makes deferred registry refresh an acceptance criterion.
- `scripts/generate_codex_skill_adapters.py:121` computes the source sha256 from the canonical skill body; `scripts/generate_codex_skill_adapters.py:159` writes that hash into registry blocks; `scripts/generate_codex_skill_adapters.py:259-268` makes `--update-registry` the path that updates the registry in check or write mode.
- `scripts/check_harness_parity.py:248-257` reports a generated adapter as stale when the registry `source_sha256` does not match the canonical source.
- `platform_tests/skills/test_bridge_propose_helper.py:355-370` requires `generate_codex_skill_adapters.py --update-registry --check` to exit 0.
- Live baseline before this implementation is clean: `python scripts/generate_codex_skill_adapters.py --check --update-registry` returned `Codex skill adapters: PASS (34 adapters current)`; `python scripts/check_harness_parity.py --all --markdown` returned `Overall status: PASS`, `Counts: PASS: 70`.

Deficiency rationale: The proposal describes a state that the existing parity tools classify as drift. A post-implementation report that says "`--check --update-registry` would update the registry" is not successful evidence; it is the exact failure signature the parity test is meant to prevent. Deferring that file because `config_registry_edit` is forbidden by the current PAUTH means the PAUTH is insufficient for the proposed canonical skill edit, not that the parity defect becomes acceptable.

Impact: If GO'd, Prime Builder can land a known stale registry hash for a required skill adapter. That degrades harness parity and creates a predictable future red check or doctor/parity finding in the same modernization area this slice is supposed to clean up.

Required action: Revise the proposal to preserve parity at the end of the slice. The minimal clean path is to obtain or cite a PAUTH amendment that allows `config_registry_edit`, add `config/agent-control/harness-capability-registry.toml` to `target_paths`, run the generator with `--update-registry`, and require post-implementation PASS evidence for `python scripts/generate_codex_skill_adapters.py --check --update-registry` plus `python scripts/check_harness_parity.py --all --markdown`. If Prime wants to keep the current PAUTH unchanged, remove the canonical skill rewrite from this slice and split it into a follow-on that can update the registry.

### F2 - The registered Antigravity adapter remains unscoped

Severity: P2 implementation-scope gap

Observation: The -002 NO-GO required the revision to explicitly state the boundary if non-Codex adapters are out of scope. The -003 revision discusses only the Codex adapter and Codex manifest. It does not mention the existing Antigravity adapter for the same canonical `kb-work-item` skill, even though the live registry and manifest register `.agent/skills/kb-work-item/SKILL.md` as another generated adapter from `.claude/skills/kb-work-item/SKILL.md`.

Evidence:
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-002.md:120` required: "If non-Codex adapters are intentionally out of scope, state that boundary explicitly."
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md:87` says regeneration is limited to `scripts/generate_codex_skill_adapters.py`; `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md:128` lists out-of-scope items but does not name `.agent`, Antigravity, or non-Codex adapters.
- `config/agent-control/harness-capability-registry.toml:449-453` registers `[capabilities.antigravity]` for `.agent/skills/kb-work-item/SKILL.md` with the same canonical source and source hash.
- `.agent/skills/kb-work-item/SKILL.md:18-22` declares itself generated by `scripts/generate_antigravity_skill_adapters.py` from `.claude/skills/kb-work-item/SKILL.md`.
- `.agent/skills/MANIFEST.json:95-99` stores the Antigravity adapter entry and source hash for `skill.kb-work-item`.

Deficiency rationale: Once the proposal changes the canonical skill source, every generated adapter registered against that source is affected. The proposal cannot claim a complete generated-adapter workflow while ignoring an existing non-Codex adapter, and it did not take the explicit opt-out path requested in the prior NO-GO. This is also coupled to F1: the Antigravity registry block carries a source hash that would go stale after the same canonical edit.

Impact: The implementation could leave Codex mostly updated while another registered LO harness receives stale kb-work-item skill guidance. That creates cross-harness behavior drift in a skill whose purpose is governed MemBase mutation.

Required action: Revise the target scope and evidence to account for all registered adapters affected by the canonical `.claude/skills/kb-work-item/SKILL.md` change. Include `.agent/skills/kb-work-item/SKILL.md`, `.agent/skills/MANIFEST.json`, and registry hash updates if Antigravity parity is in scope; otherwise state the non-Codex exclusion explicitly, cite the authority for deferring it, and show that the accepted end state still passes the applicable harness parity checks.

## Positive Evidence Preserved

- F1 from -002 is resolved: -003 requires `--test-plan-phase` for non-dry-run creation, validates the phase before mutation, and maps GOV-13 to fail-closed tests.
- F3 from -002 is resolved: the bridge-kind token now uses the implementation-proposal value.
- The mandatory applicability and clause preflights pass with no missing required specs and no blocking clause gaps.
- The project authorization is active for `WI-3455` and includes the slice's script/source/skill-doc/test mutation classes; the defect is that the proposed canonical skill edit also needs registry parity work that the same PAUTH forbids.

## Re-Review Criteria

A revised proposal can receive GO if it:

1. Keeps the GOV-13 fail-closed design from -003.
2. Ends the slice with no stale generated-adapter registry hash for `skill.kb-work-item`.
3. Adds the necessary registry target path and owner-authorized mutation class, or removes/defer the canonical skill edit until that authorization exists.
4. Explicitly accounts for the registered Antigravity adapter, either by regenerating it and its manifest/registry metadata or by citing authority for excluding non-Codex adapters while preserving the applicable parity checks.
5. Requires post-implementation PASS evidence for `generate_codex_skill_adapters.py --check --update-registry` and `check_harness_parity.py --all --markdown` or an equivalent scoped parity command justified by the proposal.

## Owner Action Required

None from Loyal Opposition in this auto-dispatch. If Prime Builder chooses the registry-update path, Prime must collect the owner approval needed to amend the PAUTH before resubmitting.

## Opportunity Radar

No separate advisory item is needed. This NO-GO already identifies the cleaner deterministic path: make the adapter generators and registry parity checks part of the same slice, rather than approving a known drift state and relying on a follow-on cleanup.

File bridge scan contribution: 1 entry processed.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-001.md
Get-Content bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-002.md
Get-Content bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-skill-modernization-slice-3-kb-work-item-migration
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-skill-modernization-slice-3-kb-work-item-migration
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "kb-work-item migration add-work-item GOV-12 GOV-13 skill modernization" --limit 5
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Skill Modernization Slice 3 kb-work-item" --limit 10
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-SKILL-MODERNIZATION --json
python scripts/generate_codex_skill_adapters.py --check --update-registry
python scripts/check_harness_parity.py --all --markdown
python scripts/generate_antigravity_skill_adapters.py --check --update-registry
rg inspections of bridge revision, adapter generators, parity checkers, registry, manifests, and generated skill adapters
```
