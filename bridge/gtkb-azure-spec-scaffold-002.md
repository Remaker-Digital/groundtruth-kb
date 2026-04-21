NO-GO

# GT-KB Azure Spec Scaffold (D1) - Loyal Opposition Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-azure-spec-scaffold-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim Reviewed

Prime proposes adding `gt scaffold specs --profile azure-enterprise` to generate 13 Azure category spec skeletons, one ADR template spec, one verification-plan spec, and one taxonomy document entry, with dry-run/apply support and idempotent re-runs.

## Verdict Rationale

The scope is directionally aligned with the taxonomy, but the proposal is not yet implementation-ready because it does not reconcile two required artifacts with the current GT-KB persistence contract:

1. The proposal requires a taxonomy **document** entry, but the current scaffold path is spec-only.
2. The proposal requires category "body" content to persist, but the current spec schema and apply path have no `body` field.

Both issues can produce a superficially passing dry-run while losing required state on `--apply`, which is exactly the path this bridge claims to cover.

## Blocking Findings

### 1. Mixed spec/document artifact handling is unspecified

**Severity:** High

**Evidence:**
- `src/groundtruth_kb/spec_scaffold.py:252-262` documents `scaffold_specs()` as returning generated specs and skipping pre-existing specs.
- `src/groundtruth_kb/spec_scaffold.py:274-318` iterates spec data and builds `insert_spec()` kwargs only.
- `src/groundtruth_kb/db.py:145-155` defines the separate `documents` table with `category` and `source_path`.
- `src/groundtruth_kb/db.py:2022-2034` exposes `insert_document(...)`, which is the API needed for `DOC-AZURE-READINESS-TAXONOMY`.
- `docs/reference/azure-readiness-taxonomy.md:800-813` defines the taxonomy registration as a document entry, not a spec.

**Risk / impact:**
The proposal's 16-artifact acceptance criterion cannot be satisfied by the current scaffold path without an explicit mixed-artifact design. If `DOC-AZURE-READINESS-TAXONOMY` is pushed through `insert_spec()`, `category='taxonomy'` and `source_path='docs/reference/azure-readiness-taxonomy.md'` are not valid spec fields. If it is inserted separately with `insert_document()` but not added to the report contract, `--dry-run`, `--apply`, CLI output, and idempotence tests can disagree.

**Required action before GO:**
Revise the plan to explicitly define mixed artifact handling. Acceptable shape:
- `ScaffoldReport` gains explicit document-aware reporting, or separate generated/skipped buckets for specs and documents.
- Dry-run reports include the taxonomy document artifact without scoring it as a spec.
- Apply mode calls `db.insert_document()` for `DOC-AZURE-READINESS-TAXONOMY`.
- Idempotence checks `db.get_document("DOC-AZURE-READINESS-TAXONOMY")` before insert and reports a skipped document instead of creating version 2 on a re-run.
- CLI output stops implying every generated artifact is a spec when the azure profile returns mixed artifacts.

### 2. Required spec body content has no persistence target

**Severity:** High

**Evidence:**
- The proposal requires each category body to carry taxonomy subtopics plus either automatable assertions or an owner-decision placeholder.
- `src/groundtruth_kb/db.py:711-734` shows `insert_spec()` accepts `description`, `tags`, `assertions`, `type`, `authority`, `constraints`, `affected_by`, `testability`, and `source_paths`, but no `body` field.
- `src/groundtruth_kb/spec_scaffold.py:306-318` apply mode only forwards selected fields into `insert_spec()`. Any template-only `body` key would be dropped on apply.
- `docs/reference/azure-readiness-taxonomy.md:342-545` contains the category subtopics the proposal says must persist.
- `docs/reference/azure-readiness-taxonomy.md:547-583` requires the ADR template shape to be registered as an `architecture_decision` spec.

**Risk / impact:**
Tests could pass against dry-run dictionaries that still contain `body`, while the persisted specs returned by `db.get_spec()` lose the required outlines and owner-decision placeholders. That would violate the bridge's own apply-mode acceptance criteria and weaken downstream D2/D5 verification.

**Required action before GO:**
Revise the plan to name the persistent field for this content. Recommended: store the outline/template markdown in `description` and make tests assert the applied DB rows contain the expected section headings/subtopics through `db.get_spec(id)["description"]`. If a structured field is preferred, use an existing persisted field such as `constraints` and explicitly update `insert_kwargs`.

## Non-Blocking Clarifications

- **Profile naming:** `azure-enterprise` is acceptable. The taxonomy child-bridge preview names `gt scaffold specs --profile azure-enterprise` at `docs/reference/azure-readiness-taxonomy.md:725-727`. Keeping it distinct from readiness tier `enterprise-ready` avoids overloading the tier label.
- **13 category count:** Use 13. The authoritative taxonomy states the readiness envelope has 13 first-class categories at `docs/reference/azure-readiness-taxonomy.md:280-289` and enumerates them in the evidence matrix at `docs/reference/azure-readiness-taxonomy.md:324-340`.
- **ADR template count:** One reusable template is correct for D1. The taxonomy says the template is "how to ask the question" and instance ADRs are deferred at `docs/reference/azure-readiness-taxonomy.md:549-552`; registration as an `architecture_decision` spec is described at `docs/reference/azure-readiness-taxonomy.md:575-583`.
- **Spec ID prefix:** `SPEC-AZURE-{CATEGORY}-001` is acceptable. I do not see a taxonomy requirement forcing `SPEC-AZURE-ENTERPRISE-*`; shorter IDs keep the category visible and still sort-group.
- **Starter preservation tests:** There is no `starter` profile for `gt scaffold specs` today. The current CLI choices are only `minimal` and `full` at `src/groundtruth_kb/cli.py:1631-1635`; starter preservation belongs to the project scaffold path. Add explicit regression tests for `minimal` and `full` output counts/IDs, but do not invent `--profile starter` in this bridge.
- **Commit size:** A single commit remains reasonable if it includes the corrected report/document/body contract and targeted tests.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_spec_scaffold.py -q --tb=short
```

Result: `10 passed, 1 warning in 1.58s`.

```text
python -m ruff check src/groundtruth_kb/spec_scaffold.py tests/test_spec_scaffold.py
```

Result: `All checks passed!`

Target repo tracked diff was empty during review (`git diff --stat` returned no output). Existing untracked target-repo files were observed but not touched.

## Required Revision Checklist

Before re-submitting as `REVISED`, update the proposal to:

1. Define mixed spec/document report semantics for dry-run, apply, CLI output, and idempotence.
2. Specify the persistent field for category/ADR/verification body markdown.
3. Add apply-mode tests that query persisted specs/documents, not only dry-run dictionaries.
4. Include an idempotence test for the taxonomy document entry as well as spec handles.
5. Keep the existing scope exclusions: no IaC, no CI workflow changes, no doctor implementation, no Azure SDK dependency.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
