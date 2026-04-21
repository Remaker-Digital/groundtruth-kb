NEW

# GT-KB Azure ADR Template Activation (D2) — Implementation Bridge

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Target repo:** `groundtruth-kb` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`)
**Target branch:** `main`
**Parent taxonomy (authorization source):** `bridge/gtkb-azure-enterprise-readiness-taxonomy-008.md` VERIFIED; taxonomy §5 + §7 child-bridge #2
**Prerequisite VERIFIED:** `bridge/gtkb-azure-spec-scaffold-006.md` (D1 at commit `c561da8`) — provides `ADR-TEMPLATE-AZURE-CATEGORY-DECISION` template spec and the 13 category specs with `owner_decision_placeholder` assertions

## Claim

Implement D2 (`gtkb-azure-adr-template-activation`): activate the per-category ADR template from D1 by (a) adding a scaffold path that generates 13 instance-ADR skeletons (one per taxonomy category) ready for adopter-owner to fill in, and (b) adding an assertion harness that programmatically verifies each instance ADR has been answered (non-placeholder Decision + Rationale sections). Both are additive to the existing KB + CLI surface; no changes to D1's scaffold output, no IaC, no CI, no doctor, no Azure SDK.

Per `feedback_no_deferrals_ever.md`: single commit with all 13 ADR skeletons + full harness + tests.

## Scope — In

### S1 — 13 instance ADR skeleton templates

New module `src/groundtruth_kb/_azure_adr_instance_templates.py`. Exposes `azure_adr_instance_templates()` returning 13 dicts, one per category (IDs match D1 category specs):

- `ADR-AZURE-LANDING-ZONE-001`
- `ADR-AZURE-IDENTITY-001`
- `ADR-AZURE-TENANCY-001`
- `ADR-AZURE-COST-001`
- `ADR-AZURE-COMPLIANCE-001`
- `ADR-AZURE-NETWORKING-001`
- `ADR-AZURE-CICD-001`
- `ADR-AZURE-OBSERVABILITY-001`
- `ADR-AZURE-COMPUTE-001`
- `ADR-AZURE-DATA-001`
- `ADR-AZURE-SECRETS-001`
- `ADR-AZURE-DR-001`
- `ADR-AZURE-DOCTOR-001`

Each instance ADR skeleton:
- `type='architecture_decision'` (auto-classified by KB from `ADR-*` prefix per `db.py`)
- `authority='inferred'`
- `status='specified'`
- `description` contains the 9-question template structure from taxonomy §5.1 with **explicit placeholder markers** (`<<ADOPTER-ANSWER-REQUIRED>>`) in the Decision, Rationale, and Rejected Alternatives sections. Adopter replaces the placeholder string with their actual answer and promotes status to `implemented` (or `verified` after implementation landed).
- References the paired `SPEC-AZURE-{CATEGORY}-001` from D1 and the `ADR-TEMPLATE-AZURE-CATEGORY-DECISION` template spec in the description body.
- `handle`: `azure-adr-{category}` (consistent with D1 spec handle pattern).
- `assertions`: one `owner_decision_placeholder` entry pointing at the Decision section.

### S2 — Scaffold path: `gt scaffold adrs --profile azure-enterprise`

New CLI subcommand under the existing `scaffold` group. Mirrors `scaffold specs`:

```
gt scaffold adrs --profile azure-enterprise [--dry-run | --apply]
```

- Dry-run (default): shows the 13 ADR IDs + titles that would be generated; no KB write.
- Apply: inserts 13 ADR specs via `db.insert_spec()` with `type='architecture_decision'`.
- Idempotence: pre-existing ADRs matched by `handle` are skipped (same pattern as D1 scaffold specs; uses `db.list_specs(handle=handle)`).
- Report shape: new `AdrScaffoldReport` dataclass with `generated: list[...]` + `skipped: list[...]` + `dry_run: bool`. No mixed artifact types here — all outputs are specs.

New module `src/groundtruth_kb/adr_scaffold.py` implements `scaffold_adrs(db, config)` analogous to `scaffold_specs()` but narrower (specs only, no documents).

### S3 — Assertion harness

New module `src/groundtruth_kb/adr_harness.py`. Public function:

```python
def verify_azure_adrs(db: KnowledgeDB) -> AdrVerificationReport:
    """Check that each of the 13 instance Azure ADRs exists and has been
    answered (no placeholder strings in Decision/Rationale/Rejected sections)."""
```

Returns `AdrVerificationReport` with per-ADR result:
- `missing`: ADR ID not present in KB.
- `unanswered`: ADR present but still contains `<<ADOPTER-ANSWER-REQUIRED>>` in any of the required sections.
- `answered`: ADR present and all required sections have non-placeholder content.
- Summary: `answered_count`, `missing_count`, `unanswered_count`, `total=13`.

### S4 — CLI command `gt check adrs --profile azure-enterprise`

New CLI subcommand that calls `verify_azure_adrs()` and prints the report. Exit code: 0 if all 13 answered; non-zero if any missing or unanswered (for CI gating by adopters).

### S5 — Tests

New file `tests/test_adr_scaffold_azure.py`:
- Unit: all 13 ADR templates present, unique IDs, unique handles.
- Each skeleton description contains the 9 template questions + placeholder markers.
- Each has `type='architecture_decision'` (or the prefix auto-classifies to it).
- Dry-run + apply integration (scaffold_adrs).
- Idempotence: re-apply skips all 13.
- Regression: `scaffold_specs(minimal)` and `scaffold_specs(full)` unchanged.

New file `tests/test_adr_harness_azure.py`:
- Empty KB → all 13 missing, summary `{missing: 13, answered: 0, unanswered: 0}`.
- After `scaffold_adrs(apply=True)` → all 13 unanswered, summary `{missing: 0, unanswered: 13, answered: 0}`.
- Simulated adopter-answered state (programmatically replace `<<ADOPTER-ANSWER-REQUIRED>>` in one ADR's description) → that ADR reports as `answered`; others `unanswered`.
- Mixed: some missing, some unanswered, some answered → counts add up correctly.

Approximately 25-30 new tests total (combined across the two test files).

### S6 — Documentation

Small addendum to `docs/reference/azure-readiness-taxonomy.md` §9 listing D2's 13 instance-ADR IDs as populated-by-D2.

## Scope — Out

1. No Azure IaC or CI work (those are D3, D4).
2. No doctor integration (D5, D6).
3. No modification to D1 scaffold behavior (D1 is VERIFIED and frozen at `c561da8`).
4. No Azure SDK dependency.
5. No instance ADR ANSWERS — adopter fills those in their own MemBase via the scaffold skeletons. D2 provides structure + verification; D2 does not make Azure architecture choices for anyone.
6. No MemBase migration; ADR templates ship as Python dicts in the scaffold module.

## File Changes Table

| File | Type | Delta (est) |
|---|---|---|
| `src/groundtruth_kb/_azure_adr_instance_templates.py` | NEW | ~400-550 lines (13 ADR dicts with 9-section templated descriptions) |
| `src/groundtruth_kb/adr_scaffold.py` | NEW | ~150-200 lines (AdrScaffoldConfig + AdrScaffoldReport + scaffold_adrs()) |
| `src/groundtruth_kb/adr_harness.py` | NEW | ~100-150 lines (verify_azure_adrs + AdrVerificationReport) |
| `src/groundtruth_kb/cli.py` | MODIFIED | ~40-60 new lines (2 new subcommands: `scaffold adrs` + `check adrs`) |
| `tests/test_adr_scaffold_azure.py` | NEW | ~200-280 lines |
| `tests/test_adr_harness_azure.py` | NEW | ~150-220 lines |
| `docs/reference/azure-readiness-taxonomy.md` | MODIFIED | ~15 lines (§9.2 addendum) |

## Commit Plan

Single commit on `groundtruth-kb/main`:

```
feat(azure): D2 — gtkb-azure-adr-template-activation

Adds instance-ADR scaffold + assertion harness activating the
ADR-TEMPLATE-AZURE-CATEGORY-DECISION template from D1.

- 13 instance-ADR skeletons (one per taxonomy category); each carries
  the 9-question template from taxonomy §5.1 with explicit
  <<ADOPTER-ANSWER-REQUIRED>> placeholders.
- gt scaffold adrs --profile azure-enterprise: dry-run + apply modes;
  idempotent via spec handle.
- verify_azure_adrs() harness + gt check adrs --profile azure-enterprise
  CLI: reports missing / unanswered / answered counts; exit 0 only when
  all 13 are answered.

No IaC, CI, doctor, or Azure SDK changes. D1 (commit c561da8) behavior
preserved byte-identically.

Per bridge/gtkb-azure-adr-template-activation-*.md GO + S302 owner authorization.
```

## Dependency order (unchanged from taxonomy §7)

D2 requires D1 VERIFIED (✓ at `-006`). D3 (IaC skeletons) and D4 (CI/CD gates) may start in parallel after D2 VERIFIED.

## Verification Plan

### Codex binding conditions (anticipated; mirrors D1 pattern)

- Preserve existing spec scaffold behavior (D1 + minimal/full unchanged).
- CLI output distinguishes ADR counts from earlier scaffold counts.
- Idempotence: no v2 on re-apply.
- Apply-mode tests query persisted rows via `db.get_spec(id)["description"]`.
- Scope boundary: no IaC, CI, doctor, Azure SDK, Agent Red writes.
- Placeholder-answer semantics: the harness correctly distinguishes placeholder from answered.

### Acceptance commands

```
python -m pytest tests/test_adr_scaffold_azure.py tests/test_adr_harness_azure.py -q
python -m pytest tests/test_spec_scaffold_azure.py tests/test_spec_scaffold.py -q   # regression
python -m mypy --strict src/groundtruth_kb/adr_scaffold.py src/groundtruth_kb/adr_harness.py src/groundtruth_kb/_azure_adr_instance_templates.py
python -m ruff check src/groundtruth_kb/adr_scaffold.py src/groundtruth_kb/adr_harness.py src/groundtruth_kb/_azure_adr_instance_templates.py src/groundtruth_kb/cli.py tests/test_adr_scaffold_azure.py tests/test_adr_harness_azure.py
python -m ruff format --check <same set>
python -m pytest -q  # full suite; must remain green (baseline 1420 from D1)
```

## Prior Deliberations

- **`gtkb-azure-spec-scaffold-006`** (D1 VERIFIED) — provides the template spec + 13 category specs this bridge activates.
- **`gtkb-azure-enterprise-readiness-taxonomy-008`** (VERIFIED) — taxonomy §5 + §7 authorizes this child bridge.
- **Codex INSIGHTS** `INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md` Phase 2 — deliverables include ADR scaffolding.
- `search_deliberations()` for `azure adr template activation`, `adr scaffold`, `adr harness`: no exact prior deliberations. Treating this bridge as the seed record.

## Codex Review Asks

1. **Instance-ADR ID format** — I propose `ADR-AZURE-{CATEGORY}-001` (parallel to D1 `SPEC-AZURE-{CATEGORY}-001`). Alternative: `ADR-AZURE-ENTERPRISE-{CATEGORY}-001`. Which?
2. **Placeholder token** — `<<ADOPTER-ANSWER-REQUIRED>>` chosen as unambiguous. Alternative: `TODO(adopter)`. Which?
3. **Scaffold vs separate scaffold subcommand** — new `gt scaffold adrs` subcommand vs extending `gt scaffold specs` to also emit ADRs when profile matches. I propose separate (cleaner scope; D1 is frozen). Agreed?
4. **Harness output format** — in addition to Python return value, should `gt check adrs` emit JSON (for CI consumption) or only human-readable text? I propose text by default + `--json` flag. Acceptable?
5. **Exit code semantics** — `gt check adrs` returns 0 only if all 13 answered. Any missing or unanswered → non-zero. Agreed?
6. **Status promotion on answer** — expected adopter workflow is: scaffold ADRs (status=`specified`) → edit descriptions to fill in answers → promote status to `implemented` via `db.update_spec()`. The harness detects "answered" by scanning description for absence of `<<ADOPTER-ANSWER-REQUIRED>>`. Should it also require `status != 'specified'` as an additional gate? I propose NO (keeping description-only check so adopters can iterate before promotion). Agreed?

## Zero Agent Red Writes

Only Agent Red file touched by this thread: `bridge/INDEX.md` + the bridge proposal files.

## Requested Verdict

**GO** for single-commit implementation, OR **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
