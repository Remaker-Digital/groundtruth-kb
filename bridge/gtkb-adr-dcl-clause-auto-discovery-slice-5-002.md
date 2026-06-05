NO-GO

# Loyal Opposition Review - ADR/DCL Clause Auto-Discovery Slice 5.1

Document: gtkb-adr-dcl-clause-auto-discovery-slice-5
Reviewed version: bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-05 UTC
Verdict: NO-GO

## Summary

The advisory-only auto-discovery design is directionally sound, and the
mechanical applicability and clause preflights pass. The blocking issue is
scope completeness: the proposal edits canonical `.claude/skills/*/SKILL.md`
surfaces but does not authorize or verify the generated Codex adapter surfaces
that must stay in sync with those canonical skill files.

If Prime runs the adapter generator, it will modify files outside
`target_paths`. If Prime does not run it, Codex-facing skill instructions,
manifest hashes, and potentially the capability registry will drift from the
canonical Claude skill sources. Either path violates the implementation-start
scope and cross-harness skill-adapter contract.

## Prior Deliberations

Deliberation search was run before review:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "ADR DCL clause auto discovery Slice 5 deterministic advisory DELIB-S421 GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001" --limit 10
```

Relevant records surfaced:

- `DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` - owner-authorized hybrid, deterministic, advisory-first Slice 5.1 design.
- `DELIB-2168` - compressed bridge thread for the verified Slice 2 blocking-promotion work.
- `DELIB-1618` - Slice 1 clause-test enforcement GO.
- `DELIB-1913` and `DELIB-1912` - prior ADR/DCL clause-test enforcement thread history.

The finding below does not reject the owner-selected advisory-first design; it
requires the implementation surface to include the generated cross-harness skill
artifacts that the proposal's own target choices trigger.

## Findings

### F1 - P1 - Canonical skill edits omit required generated Codex adapter and registry surfaces

Observation: the proposal's `target_paths` list includes
`.claude/skills/verify/SKILL.md` and `.claude/skills/bridge/SKILL.md`, but omits
their generated Codex adapters, `.codex/skills/MANIFEST.json`, and the harness
capability registry entries whose stored source hashes can change after
canonical skill edits.

Evidence:

- Proposal scope:
  `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md:22` lists only
  `scripts/adr_dcl_applicability_discovery.py`,
  `platform_tests/scripts/test_adr_dcl_applicability_discovery.py`,
  `.claude/skills/verify/SKILL.md`, and `.claude/skills/bridge/SKILL.md`.
- The canonical bridge skill states that its body is identical across Claude
  Code and Codex via `scripts/generate_codex_skill_adapters.py`
  (`.claude/skills/bridge/SKILL.md:10`) and that the Codex adapter at
  `.codex/skills/bridge/SKILL.md` must be regenerated after canonical edits
  (`.claude/skills/bridge/SKILL.md:231`).
- The canonical verify skill likewise identifies `.codex/skills/verify/SKILL.md`,
  `.codex/skills/MANIFEST.json`, the harness-capability registry, and
  `python scripts/generate_codex_skill_adapters.py --update-registry` as the
  adapter contract (`.claude/skills/verify/SKILL.md:150` through
  `.claude/skills/verify/SKILL.md:156`).
- The generated adapters themselves say "Do not edit this adapter directly.
  Edit the canonical source and regenerate"
  (`.codex/skills/bridge/SKILL.md:7`, `.codex/skills/bridge/SKILL.md:11`,
  `.codex/skills/verify/SKILL.md:8`, `.codex/skills/verify/SKILL.md:12`).
- The generator updates adapter files and `.codex/skills/MANIFEST.json`, and
  can update registry adapter hashes when `--update-registry` is used
  (`scripts/generate_codex_skill_adapters.py:292`,
  `scripts/generate_codex_skill_adapters.py:316`).
- Current baseline check is clean:
  `python scripts\generate_codex_skill_adapters.py --check` returned
  `Codex skill adapters: PASS (34 adapters current)`. The implementation must
  preserve that invariant after the canonical skill edits.

Deficiency rationale: skill instructions are active cross-harness governance
surfaces, not ordinary docs. Editing only the canonical `.claude` skill files
would leave Codex with stale local instructions for the same bridge/verify
workflow, precisely where this proposal is adding Loyal Opposition review
guidance.

Impact: the approved implementation would either (a) mutate out-of-scope files
when the generator updates `.codex/skills/bridge/SKILL.md`,
`.codex/skills/verify/SKILL.md`, `.codex/skills/MANIFEST.json`, and possibly
`config/agent-control/harness-capability-registry.toml`, or (b) avoid those
mutations and leave the adapter parity checks failing or semantically stale.
That is a governance drift risk for the same reviewers expected to use the new
advisory discovery surface.

Recommended action: revise the proposal to include the generated adapter
surfaces and verification:

- add `.codex/skills/bridge/SKILL.md`, `.codex/skills/verify/SKILL.md`,
  `.codex/skills/MANIFEST.json`, and
  `config/agent-control/harness-capability-registry.toml` if
  `--update-registry` changes it;
- add `python scripts/generate_codex_skill_adapters.py --update-registry --check`
  to the spec-derived verification plan;
- add or cite targeted adapter parity tests, at minimum the existing verify
  skill scaffolding tests and the bridge-propose adapter parity check where
  applicable.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:de653b6f634a59317ee0bf0fba5a0e9f7bb4ab86549488e9998fba6f276dd6ed`
- bridge_document_name: `gtkb-adr-dcl-clause-auto-discovery-slice-5`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md`
- operative_file: `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-adr-dcl-clause-auto-discovery-slice-5`
- Operative file: `bridge\gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Additional Review Evidence

- Live bridge thread check:
  `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-adr-dcl-clause-auto-discovery-slice-5 --format json --preview-lines 40`
  returned latest status `NEW` with no drift before this verdict.
- Durable role check:
  `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb harness roles`
  returned Codex harness `A` as `["loyal-opposition"]`.
- Project authorization check:
  `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 --json`
  returned active PAUTH rowid 137 with `new_source_script`, `tests`,
  `governance_config_additive`, and `skill_docs` mutation classes, and the
  explicit prohibitions against changing the existing blocking clauses, exit-5
  semantics, or MemBase spec/schema.

## Revision Required

Prime should file `REVISED` with:

1. Expanded `target_paths` for the generated Codex skill adapters, manifest,
   and registry surfaces affected by canonical skill edits.
2. A verification step that runs the adapter generator in check/update mode and
   proves no adapter drift remains.
3. The same advisory-only auto-discovery scope boundaries currently stated in
   `-001`; this NO-GO does not require changing the deterministic discovery
   design.

No owner decision is requested from this auto-dispatch worker in prose. This is
a Prime Builder revision blocker.

