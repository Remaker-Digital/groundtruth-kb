REVISED

bridge_kind: implementation_report
Document: gtkb-fab-20-hygiene-investigation-skill
Version: 007
Author: prime-builder (Claude Opus 4.7, harness B) - interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-20-hygiene-investigation-skill-006.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4432
Project Authorization: PAUTH-FAB20-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 244ad9d8-1982-4987-9181-662ef9b47074
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".claude/skills/gtkb-hygiene-investigation/**", ".codex/skills/gtkb-hygiene-investigation/**", "scripts/hygiene/**", "config/governance/hygiene-baseline-registry.toml", "config/agent-control/harness-capability-registry.toml", "platform_tests/**", "bridge/gtkb-fab-20-hygiene-investigation-skill-*.md", "bridge/INDEX.md"]

# FAB-20 - Post-Implementation Report (REVISED-007: addresses NO-GO@-006)

WI-4432 (FAB-20) of PROJECT-FABLE-INVESTIGATION. Charter:
`bridge/gtkb-fable-investigation-advisory-001.md` Q5 repeatability architecture.
GO at `bridge/gtkb-fab-20-hygiene-investigation-skill-004.md`.
Prior post-implementation report at
`bridge/gtkb-fab-20-hygiene-investigation-skill-005.md`; NO-GO at
`bridge/gtkb-fab-20-hygiene-investigation-skill-006.md`. This REVISED report
addresses both numbered findings from the NO-GO and the third Required
Revisions item; the bulk of the implementation report carries forward verbatim
from `-005` with the three corrections inlined where they belong.

## Revision Scope

Addresses every item from NO-GO@-006:

- **P1 fix (frontmatter overclaim).** The canonical
  `.claude/skills/gtkb-hygiene-investigation/SKILL.md` description previously
  said the skill "diffs against the HYG-001..068 baseline registry". That was
  an active-capability claim, inconsistent with the GO'd hard constraint that
  delta mode is deferred. The description now reads:
  ``... uses the frozen HYG-001..068 baseline registry for lookup and
  reporting; baseline diff/delta mode is deferred to a follow-on bridge.``
  The Codex adapter at `.codex/skills/gtkb-hygiene-investigation/SKILL.md` has
  been regenerated, the manifest refreshed, and the registry source_sha256
  updated. A regression test enforces the corrected wording (see Spec-to-Test
  Mapping below).
- **P2 fix (missing carried-forward spec).** This REVISED report explicitly
  carries forward `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` from the GO'd `-003`
  proposal and maps it to the implementation surface that exposes lifecycle
  states (`candidate`, `deferred`, `verified`, `retired`). The applicability
  preflight is now expected to return `missing_advisory_specs: []`.
- **P3 fix (explicit interpreter).** The Verification section below records
  the deterministic interpreter path that produces reproducible results in any
  shell (including the Codex dispatch shell, which does not have `pytest` or
  `ruff` on bare `python`): ``groundtruth-kb\.venv\Scripts\python.exe``.

No source/code behavior change beyond the SKILL.md description string and the
new regression test; the baseline registry, report generator, and capability
registration are unchanged.

## Summary

- **Orchestration skill (in scope).** `.claude/skills/gtkb-hygiene-investigation/SKILL.md`
  packages the structured findings schema, the 4-round probe workflow
  (parallel focus-area probes -> gap probe -> completeness critic ->
  adversarial skeptic), loop-until-dry with explicit decay disclosure, and an
  explicit Deferred-follow-on section excluding delta mode and any FAB-19
  evidence-pack consumer. Description string corrected per P1.
- **Codex adapter + registry.** `.codex/skills/gtkb-hygiene-investigation/SKILL.md`
  generated via `scripts/generate_codex_skill_adapters.py --update-registry`;
  capability registry entry under `config/agent-control/harness-capability-registry.toml`
  is current; `scripts/generate_codex_skill_adapters.py --check` returns PASS
  (37 adapters current).
- **Baseline registry loader (in scope).** `scripts/hygiene/hygiene_baseline.py`
  defines the shared `HygieneFinding` dataclass and `load_baseline()` returning
  a frozen `BaselineRegistry`. Pure module: no subprocess, no MemBase write, no
  filesystem traversal beyond the single registry read.
- **Chunked report generator (in scope).** `scripts/hygiene/hygiene_report.py`
  provides `generate_report_chunks()` (size-bounded chunks suitable for a
  single context window) and `finding_to_work_item()` (`gt backlog add`-routable
  form). Bulk MemBase mutation explicitly excluded. No FAB-19 evidence-pack
  consumer.
- **Baseline registry (in scope).** `config/governance/hygiene-baseline-registry.toml`
  seeds the canonical frozen HYG-001..068 corpus from the v1 report and the v2
  advisory merge.
- **Delta mode (DEFERRED).** Implemented nowhere; documented in the skill body
  and the description's qualified clause as out of slice scope.

## Specification Links

Carried forward verbatim from the GO'd `-003` proposal:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the skill packages the proven
  investigation method as a durable, reusable artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented governance
  framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle trigger categories
  (`candidate`, `deferred`, `verified`, `retired`); the skill names
  `deferred` explicitly for the delta-mode follow-on, and the structured
  findings schema includes `owner_touchpoint_required` to enable lifecycle
  transitions through owner-AUQ rather than silent state change.
  **This is the spec the prior `-005` report failed to carry forward (P2).**
- `SPEC-DSI-DOCTOR-CHECK-001` - report generator emits a deterministic,
  schema-keyed findings record.
- `GOV-08` - GT-KB is the source of truth; findings route to the backlog
  (`work_items`), not markdown.
- `GOV-STANDING-BACKLOG-001` - WI-4432 governs the slice; the skill's output
  feeds the standing backlog as candidates (capture is not implementation
  approval). The skill performs no bulk backlog mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every changed surface is in-root
  under `E:\GT-KB\`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this REVISED report is filed under `bridge/`
  with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant specs
  cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and
  verification commands below; results reproducible with the explicit
  interpreter recorded in this report.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` - chartering advisory.
- `DELIB-FABLE-GRILL-20260610-Q5` - owner repeatability architecture (layered
  deterministic core + orchestration skill + delta mode).
- `DELIB-FAB20-REMEDIATION-20260610` - cluster determination (build per Q5).
- `bridge/gtkb-fab-20-hygiene-investigation-skill-002.md` - prior NO-GO on
  sequencing (delta mode coupled to unavailable FAB-19 contract).
- `bridge/gtkb-fab-20-hygiene-investigation-skill-003.md` - GO'd REVISED
  proposal narrowing to dependency-free first slice.
- `bridge/gtkb-fab-20-hygiene-investigation-skill-004.md` - LO GO verdict with
  the hard constraint "Do not implement delta mode, an evidence-pack differ,
  or any FAB-19 output consumer in this slice".
- `bridge/gtkb-fab-20-hygiene-investigation-skill-005.md` - prior
  post-implementation report (NEW) that overclaimed in frontmatter and omitted
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `bridge/gtkb-fab-20-hygiene-investigation-skill-006.md` - LO NO-GO verdict
  enumerating the P1/P2/P3 corrections this REVISED report addresses.
- `DELIB-FAB19-REMEDIATION-20260610` - deterministic-core cluster whose
  evidence pack the deferred delta-mode follow-on will consume.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - service/skill split
  rationale.

DA semantic search for ``FAB-20 frontmatter delta deferred lifecycle triggers``
returned no additional deliberations beyond the citations above.

## Owner Decisions / Input

None. The NO-GO@-006 verdict explicitly recorded
``Owner Action Required: None``; Codex characterized the issues as
Prime-Builder-addressable within the approved FAB-20 scope. This REVISED
report makes the textual and traceability corrections in scope of
PAUTH-FAB20-20260610 (WI-4432) and the impl-start authorization packet
``sha256:dd509a1b5593a4cc0311c01aedc3d2918d4b46f5e54f3872024eb5b3c8621c5f``
minted against the NO-GO@-006 head.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: this REVISED revision
performs **no bulk backlog operation**. The orchestration skill plus the
chunked report generator emit a structured findings **inventory artifact**
(the v1-style report rendered from the schema-keyed corpus, chunked under a
configurable per-chunk character budget). Each finding's individual mapping to
a `work_items`-routable form is performed by the pure function
`finding_to_work_item()`, but the routing itself - calling `gt backlog add`
for any specific finding - is an explicit, per-finding, owner-gated step under
`GOV-STANDING-BACKLOG-001` (capture is not implementation approval). No bulk
routing run is authorized by this report, and no MemBase write is performed
by the skill or its helpers. Any future bulk routing would be its own
owner-AUQ-approved bridge thread carrying its own inventory artifact + review
packet, and that thread - not this one - would be the place a Phase/Path-
deferred decision marker for the bulk operation would land. The test
`test_report_module_performs_no_bulk_mutation_or_fab19_consumer` enforces this
invariant by AST-inspecting the generator module for forbidden mutation
imports/calls.

## Requirement Sufficiency

Existing requirements sufficient. The disposition is fixed by
`DELIB-FABLE-GRILL-20260610-Q5` and `DELIB-FAB20-REMEDIATION-20260610`; the
governing specifications listed above already constrain the implementation. No
new requirement is needed; this REVISED report applies in-scope corrections to
the existing implementation.

## Spec-to-Test Mapping

| Spec / requirement | Derived test |
|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_skill_documents_structured_findings_schema`, `test_skill_documents_four_round_workflow` - skill body packages the proven method as a durable artifact with the structured schema and 4-round workflow. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (**newly mapped, P2**) | `test_skill_defers_delta_mode` (body anchors ``Deferred follow-on`` lifecycle state explicitly) **and** `test_frontmatter_does_not_overclaim_while_body_defers_delta_mode` (regression: frontmatter description must not announce active behavior for a lifecycle-state-deferred capability while the body still defers it). The structured findings schema field `owner_touchpoint_required` is the surface through which lifecycle transitions are explicit owner-AUQ events rather than silent state change. |
| `SPEC-DSI-DOCTOR-CHECK-001` | `test_chunks_respect_size_bound_and_cover_all_findings`, `test_empty_corpus_returns_single_chunk`, `test_baseline_renders_through_generator`, `test_render_finding_emits_present_fields` - deterministic, schema-keyed report rendering. |
| `GOV-08` + `GOV-STANDING-BACKLOG-001` | `test_finding_to_work_item_is_backlog_routable`, `test_finding_to_work_item_defaults_component_without_cluster`, `test_report_module_performs_no_bulk_mutation_or_fab19_consumer`, `test_loads_sixty_eight_findings`, `test_ids_are_contiguous_hyg_001_to_068` - findings emitted in `work_items`-routable form; no bulk mutation; no FAB-19 consumer; 68 contiguous canonical IDs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed paths under `E:\GT-KB\` (target_paths above); enforced by the impl-start gate which rejected any out-of-root write. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED file at `bridge/gtkb-fab-20-hygiene-investigation-skill-007.md` with a matching `REVISED` line at the top of the same entry in `bridge/INDEX.md`; append-only - no prior version removed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The Specification Links section above carries the full set forward including the previously-omitted `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The Verification section below records the explicit deterministic interpreter (`groundtruth-kb\.venv\Scripts\python.exe`), the exact pytest / ruff / generator commands, and the observed results. **P3 fix.** |
| `test_skill_uses_canonical_role_registry_not_retired_mirror` covers a separate hygiene invariant: the skill must reach role state through `harness_projection.read_roles`, not the retired `role-assignments.json` mirror. |

## Verification

All commands run from the repo root with the deterministic interpreter
``groundtruth-kb\.venv\Scripts\python.exe`` (the platform venv that carries
`pytest`, `ruff`, and the editable `groundtruth_kb` install). The system
`python.exe` does not carry these modules and is **not** the right
interpreter for FAB-20 verification, including for Codex headless dispatch.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_hygiene_investigation.py -q --tb=short
# 28 passed in 0.29s

groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# 3 files already formatted

groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check
# Codex skill adapters: PASS (37 adapters current)

groundtruth-kb\.venv\Scripts\python.exe scripts\hygiene\hygiene_report.py --baseline --count-only
# 3
```

The test count moves from 27 (at `-005`) to **28** with the addition of
`test_frontmatter_does_not_overclaim_while_body_defers_delta_mode`. The new
test parses the YAML frontmatter `description:` value, splits it into clauses,
and fails when any clause contains an active-capability token
(``diffs against``, ``delta mode``, ``evidence pack``, ``the differ``) without
a ``deferred``/``follow-on``/``future`` qualifier - while the body still has a
``Deferred follow-on`` section. The test would have failed on the `-005` -era
description and passes against the corrected description.

## Acceptance Criteria

1. Skill description does not advertise active diff/delta/evidence-pack
   behavior - **MET** (P1 fix; new clause requires `deferred` qualifier).
2. Codex adapter regenerated and parity green - **MET** (`--check` returns
   PASS for all 37 adapters).
3. Regression test added that fails on the prior overclaim wording - **MET**
   (`test_frontmatter_does_not_overclaim_while_body_defers_delta_mode`).
4. Implementation report carries forward `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
   and maps it to test surfaces - **MET** (P2 fix; Specification Links and
   Spec-to-Test Mapping above).
5. Verification commands record the deterministic interpreter - **MET** (P3
   fix; Verification section above).
6. No delta-mode surface implemented in this slice - **MET** (verified by the
   pre-existing `test_skill_defers_delta_mode` and
   `test_report_module_performs_no_bulk_mutation_or_fab19_consumer`).

## Files Changed Relative to -005

- `.claude/skills/gtkb-hygiene-investigation/SKILL.md` - one-line description
  edit replacing "diffs against the HYG-001..068 baseline registry" with
  "uses the frozen HYG-001..068 baseline registry for lookup and reporting;
  baseline diff/delta mode is deferred to a follow-on bridge".
- `.codex/skills/gtkb-hygiene-investigation/SKILL.md` - regenerated adapter
  (description string propagated; marker + sha256 refreshed).
- `.codex/skills/MANIFEST.json` - regenerated (refreshed `source_sha256`).
- `config/agent-control/harness-capability-registry.toml` - `source_sha256` for
  this skill refreshed via `--update-registry`.
- `platform_tests/scripts/test_gtkb_hygiene_investigation.py` - added
  `test_frontmatter_does_not_overclaim_while_body_defers_delta_mode`.
- `bridge/gtkb-fab-20-hygiene-investigation-skill-007.md` - this REVISED report.
- `bridge/INDEX.md` - new top entry `REVISED:` for this thread.

No source/behavior change in the baseline registry, report generator, or test
suite beyond the new regression test.

## Recommended Commit Type

`fix:` - this REVISED revision fixes a frontmatter overclaim (capability
description out of sync with implemented behavior) and a traceability gap
(missing carried-forward spec + spec-to-test mapping). No net-new capability
surface; the only added Python is the regression test guarding the fix.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
