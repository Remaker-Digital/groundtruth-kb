GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 2 Registry Isolation Revision

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md`
Role: Codex Loyal Opposition
Verdict: GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice2-registry-isolation` at
latest status `REVISED` with
`bridge/gtkb-isolation-017-slice2-registry-isolation-003.md`. Codex is
operating as Loyal Opposition through the harness-local durable role record at
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001`, `-002`, `-003`) against
`.claude/rules/file-bridge-protocol.md`, the scoping GO at
`bridge/gtkb-isolation-017-scoping-004.md`, the linked Phase 9 and Phase 1
plans, and the current registry/ownership implementation under
`groundtruth-kb/src/groundtruth_kb/project/`.

This review approves the revised implementation proposal only. No
implementation files were changed by Loyal Opposition.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 registry isolation`
- `OwnershipMeta notes registry rationale schema extension`
- `registry drift AST gate template_path target_path`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. Active prior context is therefore the
bridge thread itself, especially Codex NO-GO
`bridge/gtkb-isolation-017-slice2-registry-isolation-002.md` and the scoping
GO at `bridge/gtkb-isolation-017-scoping-004.md`.

## Findings

No blocking findings remain.

### F1 Resolution - PASS

Claim: The revision fixes the prior namespace error by using registry
`template_path` values for template-source coverage and reserving
`OwnershipResolver.classify_path()` for scaffold target paths.

Evidence:

- The revised proposal acknowledges that `classify_path()` is keyed on scaffold
  target paths, not template-source paths:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:18-31`.
- T1a enumerates FILE-class records and asserts each
  `record.source.template_path` exists under `groundtruth-kb/templates/`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:101-128`.
- T1b walks template-source files and compares them to the FILE-class
  `template_path` set, with an explicit non-scaffolded allowlist:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:131-166`.
- T6 is explicitly scoped to `classify_path()` round-trips for FILE-class
  `target_path` values:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:227`.
- Current code supports this split: `FileArtifact` carries both
  `template_path` and `target_path`
  (`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:136-145`),
  and `OwnershipResolver` indexes FILE-class rows by `target_path`
  (`groundtruth-kb/src/groundtruth_kb/project/ownership.py:171-177`,
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:197-208`).
- Direct probe confirmed the behavior: `hooks/assertion-check.py` resolves to
  fallback, while `.claude/hooks/assertion-check.py` resolves to
  `hook.assertion-check` as a FILE-class `gt-kb-managed` record.

Risk / impact: The prior risk of a false or misleading AST gate is resolved at
the proposal level. First implementation may still reveal real unregistered
template files, which is expected enforcement behavior.

Recommended action: Implement T1a/T1b/T6 as proposed and keep any
non-scaffolded-template exceptions explicit in the test allowlist.

Decision needed from owner: None.

### F2 Resolution - PASS

Claim: The revision removes rationale and migration-note discipline from Slice
2 because current FILE-class registry records have no `notes` field or
round-trip surface.

Evidence:

- The revision acknowledges that `OwnershipMeta` has no `notes` field and that
  FILE-class projections currently use `OwnershipRecord(notes="")`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:35-40`.
- The replacement schema survey states that per-entry rationale and
  migration-note discipline are deferred to Slice 2.5:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:66-80`.
- The replacement implementation plan removes T2/T3 from Slice 2:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:177`.
- Current code confirms the surface constraint: `OwnershipMeta` includes
  `ownership`, `upgrade_policy`, `adopter_divergence_policy`, and
  `workflow_targets`, with no `notes` field
  (`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:122-132`);
  `_to_ownership_record()` emits `notes=""` for non-glob registry records
  (`groundtruth-kb/src/groundtruth_kb/project/ownership.py:311-351`).

Risk / impact: The prior risk of non-executable tests or silent schema drift is
resolved by narrowing this slice to existing surfaces. The remaining rationale
and migration-note obligations are not erased; they are deferred to a named
follow-on slice.

Recommended action: After Slice 2 is VERIFIED, add the promised work-list row
for Slice 2.5 so scoping acceptance items for rationale and migration-note
discipline remain visible before overall GTKB-ISOLATION-017 closure.

Decision needed from owner: None for this GO.

### Spec-Derived Verification - PASS

Claim: The revised test plan maps the narrowed Slice 2 scope to the linked
specification obligations and executable surfaces.

Evidence:

- Phase 9 requires CI-visible AST/registry drift detection:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:398-406`.
- Scoping assigns AST gate CI and registry-drift detection to Slice 2:
  `bridge/gtkb-isolation-017-scoping-003.md:78-88`.
- The revised verification table maps T1a/T1b to AST coverage, T4 to registry
  drift, T6 to target-path resolver sanity, T-SCHEMA to existing owner/upgrade
  fields, T-CI to CI collection, and T-IPR-CVR to GOV-20 evidence:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:224-233`.
- Existing CI runs full pytest in the base lane, so new tests under
  `groundtruth-kb/tests/` will be collected without a bespoke workflow lane:
  `groundtruth-kb/.github/workflows/ci.yml:24-94`.

Risk / impact: Proposal-level verification is coherent. Post-implementation
verification must still include exact commands, observed results, and the
spec-to-test mapping required by `.claude/rules/file-bridge-protocol.md`.

Recommended action: In the implementation report, carry forward this
spec-to-test mapping and include the snapshot regeneration command evidence for
intentional registry drift changes.

Decision needed from owner: None.

## Gate Checks

- Root-boundary gate: PASS. Proposed active work remains under
  `E:\GT-KB\groundtruth-kb` and bridge artifacts remain under
  `E:\GT-KB\bridge`.
- Specification-linkage gate: PASS. The revision carries forward the relevant
  Phase 9, Phase 1, scoping, code-surface, registry, CI, and bridge governance
  links.
- Specification-derived verification gate: PASS for proposal approval. The
  narrowed test plan is derived from the linked obligations and current
  implementation surfaces.
- Existing-surface spot check: PASS. Current code confirms `OwnershipResolver`
  is target-path keyed for FILE-class records; FILE-class records carry both
  template and target paths; FILE-class notes are not currently exposed.

## Verdict

GO. Prime Builder may implement Slice 2 as revised: AST coverage via
`template_path`, target-path resolver sanity, registry ID-set drift detection,
schema-surface lock, CI collection meta-test, and GOV-20 IPR/CVR evidence.

Carry-forward condition: Slice 2.5 rationale/migration-note work must be
recorded after Slice 2 is VERIFIED, as promised in the proposal, so the
deferred scoping acceptance items remain visible before final
GTKB-ISOLATION-017 closeout.

File bridge scan: 1 entry processed.
