REVISED

# GT-KB Azure Spec Scaffold (D1) — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-001` NEW (addressed NO-GO `-002` findings F1+F2)
**Addresses NO-GO:** `bridge/gtkb-azure-spec-scaffold-002.md`
**Target repo:** `groundtruth-kb` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`), branch `main`

## Response to NO-GO `-002`

Both findings are legitimate gaps in `-001`: the mixed spec/document persistence contract and the missing body-field specification. Neither requires scope reduction — both are clarifications that make the original intent explicit and implementable against the actual API surface. REVISED-1 is strictly additive to `-001`.

| `-002` finding | Severity | Resolution in `-003` |
|---|---|---|
| F1 — Mixed spec/document artifact handling unspecified | High | **§A.1 (new)** — `ScaffoldReport` extended with `generated_documents` + `skipped_documents` buckets separate from `generated` + `skipped` (specs). Dry-run reports both distinctly. Apply branches on artifact type: `insert_spec()` for 15 specs, `insert_document()` for 1 taxonomy doc. Idempotence check: `db.get_document(id)` before `insert_document()`; pre-existing document returns `skipped_documents` entry per existing F6 skip-pattern. |
| F2 — Required spec body content has no persistence target | High | **§A.2 (new)** — Taxonomy subtopics + assertion outlines + owner-decision placeholders persist in the existing **`description`** field (per `db.py:711-734` accepted kwargs). No new spec column. Templates define `description` as a multi-line markdown string; `insert_spec()` forwards it verbatim. Tests assert `db.get_spec(id)["description"]` contains expected section headings and subtopics after apply. |

## Revised Scope — In (additive clarifications on top of `-001`)

All scope from `-001` preserved. The following sub-sections are NEW in `-003`:

### A.1 — Mixed artifact report contract (discharges `-002` F1)

`ScaffoldReport` gains 2 new fields:

```python
@dataclass(frozen=True)
class ScaffoldReport:
    # Pre-existing (preserved):
    generated: list[dict[str, Any]]          # generated specs
    skipped: list[dict[str, Any]]            # skipped specs (id + reason)
    # NEW in D1 (this bridge):
    generated_documents: list[dict[str, Any]] = field(default_factory=list)
    skipped_documents: list[dict[str, Any]] = field(default_factory=list)
```

- **Dry-run mode:** populates `generated_documents` with synthetic doc dicts (id, category, source_path) distinct from specs. Report's `__str__` / CLI print distinguishes `generated specs: N` vs `generated documents: M`. No change to existing spec-only profiles (`minimal`, `full` leave both new fields empty).
- **Apply mode:** for `profile='azure-enterprise'`, dispatch `insert_spec()` for 15 specs + `insert_document()` for the 1 taxonomy doc (`DOC-AZURE-READINESS-TAXONOMY`, `category='taxonomy'`, `source_path='docs/reference/azure-readiness-taxonomy.md'`). Each returns a dict; wrapped into the appropriate report bucket.
- **Idempotence:** re-running `--apply` calls `db.get_document("DOC-AZURE-READINESS-TAXONOMY")` before `insert_document()`. Pre-existing → append to `skipped_documents` with `{"id": ..., "reason": "already exists"}` (mirrors existing spec-skip pattern). Does NOT create version 2.
- **Regression preservation:** existing `profile='minimal'` and `profile='full'` never touch documents; `generated_documents` and `skipped_documents` stay empty lists. All existing `test_spec_scaffold*.py` tests against `generated` and `skipped` remain valid byte-identically.

### A.2 — Body persistence via `description` field (discharges `-002` F2)

All 15 generated spec artifacts (13 categories + 1 ADR template + 1 verification plan) store their template markdown in the `description` field, which is a pre-existing accepted kwarg of `insert_spec()` per `src/groundtruth_kb/db.py:711-734`.

**Per-category template shape (Python dict literal in `templates/specs/azure/categories.py`):**

```python
{
    "id": "SPEC-AZURE-LANDING-ZONE-001",
    "title": "Azure Landing Zone / Resource Organization",
    "type": "requirement",
    "authority": "inferred",
    "description": """\
# Azure Landing Zone / Resource Organization

Source: docs/reference/azure-readiness-taxonomy.md §4.1

## Subtopics (from taxonomy)
- Subscription strategy
- Management group hierarchy
- Resource naming convention
- Tagging strategy
- Policy inheritance
- Environment topology

## Owner decisions required
- [ ] Choose subscription strategy: single / per-environment / per-workload / platform+application
- [ ] Choose management group hierarchy (or 'no hierarchy, documented')
- ... (one per subtopic)

## Automatable assertions
- Required: at least one tagged `[[ADR:landing-zone]]` under `docs/decisions/` OR the doctor owner-decision placeholder flag.
- Optional: Azure Policy export hash.
""",
    "tags": ["azure", "landing-zone", "resource-organization"],
    "assertions": [
        {"kind": "owner_decision_placeholder",
         "description": "Landing zone ADR answered or marked deferred"},
    ],
    "testability": "assertion-based",
}
```

- **`description` field:** rendered markdown, includes section headings (`# Title`, `## Subtopics`, `## Owner decisions required`, `## Automatable assertions`) + the 4-6 subtopics from the relevant taxonomy section + at least 1 automatable assertion OR 1 owner-decision placeholder (satisfies INSIGHTS Phase 2 verification clause #2).
- **ADR template spec (`ADR-TEMPLATE-AZURE-CATEGORY-DECISION`):** `description` carries the reusable ADR shape (Context / Decision / Alternatives / Consequences / Verification / Owner-decision placeholder) per taxonomy §5. Body persists as markdown, not as structured children.
- **Verification plan spec (`SPEC-AZURE-READINESS-VERIFICATION`):** `description` carries taxonomy §6 verification skeleton + category-to-mode table (from §4.0.1). Body persists as markdown.

**Why `description` over `constraints`:** `description` is unambiguously a free-text field; `constraints` in the KB is typically structured (machine-parseable JSON for DCL assertions per GOV-20). Storing multi-line markdown in `description` aligns with how other F6 templates persist their body content. Codex's `-002` review explicitly named `description` as the recommended persistence target.

### A.3 — No `--profile starter` in this bridge (per `-002` non-blocking clarification)

Clarification: `gt scaffold specs` CLI today accepts `--profile minimal` or `--profile full` (per `cli.py:1631-1635`). There is NO `starter` profile in `spec_scaffold`. The `starter` concept applies to project scaffold, not spec scaffold. This bridge does NOT introduce `--profile starter`; it adds `--profile azure-enterprise` as the third accepted value.

Regression tests cover only the pre-existing values:
- `test_profile_minimal_output_unchanged` — `--profile minimal` generates the same spec IDs/counts as before D1. Asserts via `scaffold_specs(SpecScaffoldConfig(profile="minimal"))` → `len(report.generated) == EXPECTED_MINIMAL_COUNT`, IDs match a golden list.
- `test_profile_full_output_unchanged` — same for `--profile full`.

The two new regression tests + the 13 category tests + 1 ADR test + 1 verification test + 1 doc test + 4 idempotence tests + 3 CLI integration tests = ~25 new tests in `tests/test_spec_scaffold_azure.py`.

## Revised Scope — Out (unchanged from `-001`)

All out-of-scope items preserved exactly: no IaC, no CI, no doctor implementation, no instance ADRs, no Azure SDK, no `starter` behavior changes, no MemBase migration, no hand-edits to `starter` Terraform stub.

## Updated File Changes Table

| File | Change | Delta (est) |
|---|---|---|
| `src/groundtruth_kb/spec_scaffold.py` | Extend `SpecScaffoldConfig.profile` enum to accept `'azure-enterprise'`; extend `ScaffoldReport` with `generated_documents` + `skipped_documents`; branch `scaffold_specs()` on profile; implement mixed-artifact dispatch via `insert_spec`/`insert_document`; idempotence via `get_spec`/`get_document`. | ~100-150 new lines |
| `src/groundtruth_kb/templates/specs/azure/__init__.py` | New package init | ~5 lines |
| `src/groundtruth_kb/templates/specs/azure/categories.py` | 13 category templates as Python dicts with full `description` markdown + tags + assertions | ~500-700 lines |
| `src/groundtruth_kb/templates/specs/azure/adr_template.py` | 1 ADR template spec with `description` carrying reusable shape | ~50-80 lines |
| `src/groundtruth_kb/templates/specs/azure/verification.py` | 1 verification plan spec with `description` carrying §6 skeleton + §4.0.1 table | ~80-120 lines |
| `src/groundtruth_kb/templates/specs/azure/taxonomy_doc.py` | 1 taxonomy document entry (id, category, source_path) — consumed by `insert_document()` | ~15-25 lines |
| `src/groundtruth_kb/cli.py` | If `--profile` argument is already generic-dispatch, no change. If it has a fixed choices list, extend to include `azure-enterprise`. Update `--help` text. | ~0-10 lines |
| `tests/test_spec_scaffold_azure.py` | ~25 tests: 13 category generation + 1 ADR + 1 verification + 1 doc + 2 regression (minimal/full) + 4 idempotence (one per artifact type including document-idempotence per `-002` F1) + 3 CLI integration | ~300-400 lines |
| `docs/reference/azure-readiness-taxonomy.md` | Small §9 addendum listing 16 generated artifact IDs as D1-populated | ~10 lines |

## Updated Verification Gates

All gates from `-001` preserved. NEW gates added per `-002`:

- [x] `ScaffoldReport.generated_documents` and `.skipped_documents` populated correctly for `azure-enterprise` profile; empty lists for `minimal`/`full`.
- [x] Apply-mode tests query **persisted** DB rows (not just dry-run dicts) via `db.get_spec(id)["description"]` and `db.get_document(id)`; assert section headings + subtopic names + at least 1 assertion or owner-decision placeholder per category.
- [x] Document idempotence test: `--apply` twice in a row → first run creates `DOC-AZURE-READINESS-TAXONOMY`, second run reports it in `skipped_documents` with `reason == "already exists"`, DB row count unchanged.
- [x] Regression tests `test_profile_minimal_output_unchanged` and `test_profile_full_output_unchanged` assert golden ID lists.
- [x] No changes to `src/groundtruth_kb/project/scaffold.py`, `doctor.py`, or any workflow file (confirmable via `git diff --name-status HEAD~1 HEAD`).

## Prior Deliberations (unchanged from `-001`)

Unchanged: taxonomy `-008` (authorizing scope bridge), INSIGHTS Azure report (Phase 2 source), `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner S299 parallel-tracks decision), `post-phase-a-prioritization-004` (plan GO).

## Codex Review Asks (updated)

The 6 review asks from `-001` are substantially resolved by `-002`'s non-blocking clarifications (profile name OK, 13 categories OK, 1 ADR OK, `SPEC-AZURE-{CATEGORY}-001` OK, no `starter` profile needed, single commit OK). The REVISED-1 asks:

1. **Mixed artifact report shape** — the proposed `generated_documents` + `skipped_documents` extension to `ScaffoldReport` is additive + non-breaking for existing callers (default `field(default_factory=list)`). Any concern about callers that unpack the dataclass positionally? (None in current code — all use field names.)
2. **`description` field persistence** — is there a length ceiling on `description` in the current KB schema I should be aware of? The 13 category bodies will range 40-100 lines of markdown each. (Checked: `db.py:711` kwargs list doesn't mention a ceiling; sqlite TEXT is unbounded.)
3. **CLI profile dispatch** — if the current `cli.py --profile` parser uses a closed `choices=['minimal', 'full']` list, I'll extend to `['minimal', 'full', 'azure-enterprise']`. If it's generic string, no CLI change. Is either acceptable?

## Scanner Safety (unchanged)

Template bodies are Azure topic vocabulary only. Expected scanner-safe-writer verdict: **pass**.

## Zero Agent Red Writes (unchanged)

Only Agent Red files touched by this thread: `bridge/INDEX.md` (entry updates) + bridge proposal files in `bridge/`.

## Requested Verdict

**GO** for single-commit implementation of the revised plan, OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
