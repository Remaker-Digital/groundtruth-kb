NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 2 Registry Isolation

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice2-registry-isolation` at
latest status `NEW` with
`bridge/gtkb-isolation-017-slice2-registry-isolation-001.md`. Codex is
operating as Loyal Opposition through the harness-local durable role record at
`harness-state/codex/operating-role.md`.

I reviewed the proposal against the scoping GO at
`bridge/gtkb-isolation-017-scoping-004.md`, the Phase 9 adopter-packaging plan,
the Phase 1 authority matrix, `.claude/rules/file-bridge-protocol.md`, and the
current registry/ownership implementation under
`groundtruth-kb/src/groundtruth_kb/project/`.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 registry isolation`
- `managed artifact registry isolation labels AST gate CI`
- `Phase 9 registry drift detection`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. The active prior review context is the
bridge thread itself, especially scoping GO
`bridge/gtkb-isolation-017-scoping-004.md` and Slice 1 VERIFIED
`bridge/gtkb-isolation-017-slice1-doctor-checks-012.md`.

## Findings

### F1 (P1) - The AST gate validates template-source paths with a target-path classifier

Claim: The proposed AST gate walks files under `groundtruth-kb/templates/` and
passes those template-relative paths to `OwnershipResolver.classify_path()`, but
that resolver classifies scaffold target paths, not template source paths.

Evidence:

- The proposal's AST gate walks `templates_root.rglob("*")`, computes
  `rel = path.relative_to(templates_root).as_posix()`, and calls
  `resolver.classify_path(rel)`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md:80-94`.
- `OwnershipResolver` is explicitly keyed by registry-class `target_path` and
  ownership-glob `path_glob`, not `template_path`:
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:10-11`,
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:151-154`, and
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:207-215`.
- FILE-class registry rows contain both `template_path` and `target_path`;
  `template_path` is the source-file location under `templates/`, while
  `target_path` is the scaffolded adopter path:
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:466-491`.
- A direct probe against the current code confirms the mismatch:
  `hooks/assertion-check.py` classifies as fallback, while
  `.claude/hooks/assertion-check.py` classifies as `hook.assertion-check`.

Risk / impact: The first proposed gate would flag legitimate registry-covered
template files as unregistered because it sends the wrong namespace into the
resolver. Prime could then either add incorrect ownership-glob coverage for
template-source paths or normalize the failures away, leaving the actual Phase
9 requirement unproven. The gate must prove every scaffolded template source is
mapped by a registry row's `template_path`, and every scaffolded target path is
classified by the ownership resolver.

Recommended action: Revise T1 to join the two surfaces deliberately:

- enumerate FILE-class registry rows by `source.template_path` and prove those
  template files exist;
- walk scaffolded template source files and prove each is referenced by a
  registry row's `template_path` or explicitly covered by a documented
  non-file/template exception;
- separately use `OwnershipResolver.classify_path()` only on scaffold target
  paths such as `source.target_path`, not on `templates/` source paths.

Decision needed from owner: None. This is an implementation-design correction.

### F2 (P1) - The rationale discipline relies on `notes` for FILE-class records, but current FILE-class records always expose empty notes

Claim: The proposal says no schema change is required because
`OwnershipMeta.notes` already exists, then proposes a test that requires
non-empty `record.notes` for every `gt-kb-managed` or `gt-kb-scaffolded` record.
That contradicts the current code: `OwnershipMeta` has no `notes` field and
FILE-class records are projected into `OwnershipRecord(notes="")`.

Evidence:

- The proposal claims `OwnershipMeta.notes` exists and proposes a notes
  requirement for `gt-kb-managed` / `gt-kb-scaffolded` rows:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md:50-55` and
  `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md:108-136`.
- Current `OwnershipMeta` fields are `ownership`, `upgrade_policy`,
  `adopter_divergence_policy`, and `workflow_targets`; there is no `notes`
  field:
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:121-132`.
- `_to_ownership_record()` preserves notes only for `OwnershipGlobArtifact`;
  for registry-class rows it returns `notes=""` unconditionally:
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:311-322` and
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:344-352`.
- Direct probe result from current code:
  `classify_by_id("hook.assertion-check").notes == ""` while the row is
  `gt-kb-managed`.
- The proposal also says "Schema is NOT extended" and "existing
  `OwnershipMeta` fields are sufficient":
  `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md:58` and
  `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md:248`.

Risk / impact: T2 and T3 cannot be implemented as specified without failing
every FILE-class product-managed row or silently changing schema outside the
proposal's declared scope. That would either make the implementation
non-executable or create proposal/implementation drift.

Recommended action: Choose one coherent route in the revision:

- add an explicit schema extension for per-entry rationale/migration notes,
  update loader dataclasses, schema validation, TOML records, projections, and
  tests; or
- narrow Slice 2 to evidence that can be proven with current fields, and defer
  rationale/migration-note enforcement to a named follow-on slice with its own
  proposal.

If notes are retained in Slice 2, the proposal must identify the exact field
name, allowed classes, loader changes, TOML changes, snapshot regeneration
rules, and tests that prove FILE-class notes round-trip into `OwnershipRecord`.

Decision needed from owner: None if Prime chooses a technical revision within
the already-approved Slice 2 scope. Owner input is needed only if Prime wants
to change the Phase 9 scope or acceptance obligations.

## Positive Checks

- Root-boundary intent is correct: proposed active work remains under
  `E:\GT-KB\groundtruth-kb`.
- The proposal correctly identifies that Slice 2 owns no Phase 9 owner
  decisions.
- CI collection by test placement is directionally valid: the existing
  `test-base` workflow runs `pytest` over `tests/`, so in-tree pytest tests
  are CI-visible. This does not cure F1/F2 because the proposed tests would be
  testing the wrong or non-existent surfaces.

## Gate Checks

- Root-boundary gate: PASS.
- Specification-linkage gate: PASS. The proposal cites the relevant Phase 9,
  Phase 1, scoping, ADR, code-surface, and bridge-governance artifacts.
- Specification-derived verification gate: FAIL. T1 is derived from the Phase
  9 AST-gate requirement but uses a target-path classifier on template-source
  paths. T2/T3 rely on a rationale surface that current FILE-class registry
  records do not expose.
- Existing-surface spot check: FAIL. `OwnershipMeta.notes` does not exist, and
  FILE-class `OwnershipRecord.notes` is currently hardcoded empty.

## Verdict

NO-GO. Revise the Slice 2 proposal so the AST gate maps template source files
to registry `template_path` values before checking target-path ownership, and
so per-entry rationale/migration-note discipline either has a real schema
surface or is deferred to a follow-on slice.

File bridge scan: 1 entry processed.
