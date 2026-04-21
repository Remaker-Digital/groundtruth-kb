GO

# GT-KB Azure ADR Template Activation (D2) - Proposal Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-azure-adr-template-activation-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target branch/commit inspected:** `main` at `c561da8` (`feat(azure): D1 - gtkb-azure-spec-scaffold`)

## Verdict

GO for single-commit implementation, subject to the binding conditions below.

The proposal is properly scoped as the D2 child bridge authorized by the verified Azure taxonomy and dependent on the verified D1 scaffold. It stays additive, preserves D1's `gt scaffold specs --profile azure-enterprise` surface, and provides the missing bridge between reusable ADR template shape and adopter-owned instance ADR answers.

## Prior Deliberations

No prior deliberations found for `azure adr template activation`, `adr scaffold`, or `adr harness`.

Searches were run from `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` using `groundtruth_kb.cli` through `click.testing.CliRunner`; each returned exit 0 and "No deliberations match ...".

The relevant prior bridge artifacts are:

- `bridge/gtkb-azure-enterprise-readiness-taxonomy-008.md` - VERIFIED taxonomy remediation; establishes the taxonomy and child-bridge sequence.
- `bridge/gtkb-azure-spec-scaffold-006.md` - VERIFIED D1 implementation at `c561da8`; confirms the ADR template spec and 13 Azure category specs are available.

## Rationale

The taxonomy explicitly defines the nine ADR template questions at `docs/reference/azure-readiness-taxonomy.md:560-568` and states that project instance ADRs are separate `architecture_decision` specs with IDs such as `ADR-AZURE-LANDING-ZONE-001` at `docs/reference/azure-readiness-taxonomy.md:586-587`.

The taxonomy child-bridge list authorizes `gtkb-azure-adr-template-activation` to activate the per-category ADR template and assertion harness at `docs/reference/azure-readiness-taxonomy.md:725-729`.

D1 is present and current. `git log -1 --oneline` in the target repo returned:

```text
c561da8 feat(azure): D1 — gtkb-azure-spec-scaffold
```

The D1 artifact registry exposes the exact 13 category spec IDs plus the ADR template ID at `src/groundtruth_kb/_azure_spec_templates.py:694-720`. D1's public scaffold currently produces 15 specs plus 1 taxonomy document for `azure-enterprise`, and preserves separate document buckets at `src/groundtruth_kb/spec_scaffold.py:93-98`.

The existing Click CLI already owns a `scaffold` group and `scaffold specs` command at `src/groundtruth_kb/cli.py:1625-1704`, so adding `gt scaffold adrs --profile azure-enterprise` as a sibling command is consistent with the local command structure and avoids changing D1's frozen `specs` behavior.

## Findings And Conditions

### F1 - GO: ID format accepted

Use `ADR-AZURE-{CATEGORY}-001`, as proposed.

Evidence: the taxonomy already uses `ADR-AZURE-LANDING-ZONE-001` as the example instance ADR ID at `docs/reference/azure-readiness-taxonomy.md:586-587`, and D1's category spec IDs are `SPEC-AZURE-{CATEGORY}-001` at `src/groundtruth_kb/_azure_spec_templates.py:694-707`.

Required action: implement the 13 ADR IDs exactly as listed in `bridge/gtkb-azure-adr-template-activation-001.md:25-37`, with tests asserting one-to-one pairing to `AZURE_CATEGORY_SPEC_IDS`.

### F2 - GO: placeholder token accepted

Use `<<ADOPTER-ANSWER-REQUIRED>>`, as proposed.

Risk controlled: the token is distinctive enough for deterministic harness checks and unlikely to collide with ordinary prose.

Required action: tests must prove every generated ADR skeleton contains the placeholder in the required owner-answer sections, and that replacing it with substantive text changes only that ADR's harness status from `unanswered` to `answered`.

### F3 - GO: separate scaffold subcommand accepted

Use a separate `gt scaffold adrs --profile azure-enterprise` command. Do not extend `gt scaffold specs`.

Evidence: D1's verified CLI is `gt scaffold specs --profile azure-enterprise`; the D1 verification condition required preserving existing minimal/full behavior and reporting artifact types separately. The current implementation performs spec idempotence by handle at `src/groundtruth_kb/spec_scaffold.py:311` and document idempotence separately at `src/groundtruth_kb/spec_scaffold.py:383-409`.

Required action: add ADR scaffolding in a separate module/command path. Regression tests must prove `scaffold_specs(minimal)`, `scaffold_specs(full)`, and `scaffold_specs(azure-enterprise)` outputs remain unchanged by D2.

### F4 - GO with condition: harness must verify section substance, not token absence alone

The proposal's direction is accepted, but the implementation must not classify an ADR as `answered` merely because the placeholder token is absent.

Evidence: the taxonomy requires nine questions/sections at `docs/reference/azure-readiness-taxonomy.md:560-568`. The proposal says the harness verifies non-placeholder Decision and Rationale sections at `bridge/gtkb-azure-adr-template-activation-001.md:15` and later includes Rejected Alternatives in the placeholder-bearing sections at `bridge/gtkb-azure-adr-template-activation-001.md:41-43`.

Required action: `verify_azure_adrs()` must require the relevant sections to exist and contain non-empty, non-placeholder content. Minimum required section gates for `answered` are:

- `Decision`
- `Rationale`
- `Rejected alternatives`

Recommended stronger gate: verify all nine D2 template headings are present, while only Decision/Rationale/Rejected alternatives need non-placeholder owner content for this D2 acceptance.

Tests must include malformed cases where a placeholder is deleted but the required section is empty or missing; those cases must remain `unanswered`.

### F5 - GO: JSON output and exit semantics accepted

Implement `gt check adrs --profile azure-enterprise` with human-readable output by default plus a `--json` flag.

Required action:

- exit 0 only when all 13 ADRs are `answered`;
- exit non-zero when any are `missing` or `unanswered`;
- JSON output must include per-ADR statuses plus summary counts: `answered_count`, `missing_count`, `unanswered_count`, and `total`.

Status promotion is not required for an ADR to count as answered. The proposal's description-based check is accepted because it supports owner iteration before `status='implemented'`. The report may include the current spec status for context, but must not gate on `status != 'specified'`.

### F6 - GO: scope boundary is correct

The out-of-scope list is accepted.

Required action: the D2 implementation must not touch IaC templates, CI workflows, doctor implementation, Azure SDK dependencies, or Agent Red product files. Agent Red writes remain limited to bridge coordination files. Target-repo docs may be updated only for the small D2 taxonomy addendum proposed at `bridge/gtkb-azure-adr-template-activation-001.md:103`.

### F7 - GO: idempotence and persisted-row tests are mandatory

Required action:

- `scaffold_adrs(..., dry_run=True)` must not write to the DB.
- `scaffold_adrs(..., dry_run=False)` must insert exactly 13 ADR specs.
- re-apply must skip all 13 by handle and must not create version 2 rows.
- apply-mode tests must query persisted rows through `db.get_spec(id)["description"]`, matching the D1 verification pattern.

Evidence: `KnowledgeDB.insert_spec()` auto-detects `ADR-*` IDs as `architecture_decision` when type is left as default at `src/groundtruth_kb/db.py:674-683`, and also accepts explicit `type='architecture_decision'` at `src/groundtruth_kb/db.py:711-748`. The proposal may pass the type explicitly.

## Required Verification Before Post-Implementation Report

Run and report these commands from `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_adr_scaffold_azure.py tests/test_adr_harness_azure.py -q --tb=short
python -m pytest tests/test_spec_scaffold_azure.py tests/test_spec_scaffold.py -q --tb=short
python -m mypy --strict src/groundtruth_kb/adr_scaffold.py src/groundtruth_kb/adr_harness.py src/groundtruth_kb/_azure_adr_instance_templates.py
python -m ruff check src/groundtruth_kb/adr_scaffold.py src/groundtruth_kb/adr_harness.py src/groundtruth_kb/_azure_adr_instance_templates.py src/groundtruth_kb/cli.py tests/test_adr_scaffold_azure.py tests/test_adr_harness_azure.py
python -m ruff format --check src/groundtruth_kb/adr_scaffold.py src/groundtruth_kb/adr_harness.py src/groundtruth_kb/_azure_adr_instance_templates.py src/groundtruth_kb/cli.py tests/test_adr_scaffold_azure.py tests/test_adr_harness_azure.py
python -m pytest -q --tb=short
```

I ran the D1 regression subset during this proposal review:

```text
python -m pytest tests/test_spec_scaffold_azure.py tests/test_spec_scaffold.py -q --tb=short
```

Result:

```text
37 passed, 1 warning in 3.19s
```

## Review Ask Answers

1. Instance-ADR ID format: accept `ADR-AZURE-{CATEGORY}-001`.
2. Placeholder token: accept `<<ADOPTER-ANSWER-REQUIRED>>`.
3. Scaffold command shape: accept separate `gt scaffold adrs`.
4. Harness output: require text default plus `--json`.
5. Exit semantics: accept 0 only when all 13 are answered; non-zero for missing or unanswered.
6. Status promotion gate: do not require `status != 'specified'` for D2's answered check.

## Decision Needed From Owner

None. Prime may implement D2 under the conditions above.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
