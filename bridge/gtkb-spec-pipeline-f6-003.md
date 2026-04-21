# F6: Project Scaffold Generator — REVISED

**Feature:** F6 — Project Scaffold Generator
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f6-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. F1/F3 dependencies unresolved | Phased: Phase A generates specs with existing schema only. Phase B populates F1 fields after F1 GO. F3 validation added in Phase B. |
| 2. `ProjectProfile` naming conflict | Renamed to `SpecScaffoldConfig` to avoid collision with existing `groundtruth_kb.project.profiles.ProjectProfile`. |
| 3. Existing scaffold integration undefined | F6 integrates INTO the existing `scaffold_project()` flow as an optional step. Called after project init, before first session. Also available standalone via `gt scaffold specs`. |
| 4. Generated spec authority unresolved | Decision: generated specs use `authority='inferred'` (AI-generated template, not yet owner-confirmed). Owner confirms specs individually or in batch, which promotes to `authority='stated'`. This prevents over-authorizing generic templates. |

---

## Integration With Existing Scaffold

Current GT-KB scaffold flow (scaffold.py:41):
1. `scaffold_project(options)` creates project directory, KB database, hooks, rules, templates

F6 adds an optional step after scaffold:
2. `scaffold_specs(config, kdb)` generates seed specs into the newly created KB

This is NOT a separate scaffold path. It extends the existing one:

```python
# In scaffold.py, after existing project init:
def scaffold_project(options: ScaffoldOptions) -> Path:
    # ... existing project creation ...
    
    # Optional: generate seed specs if spec scaffold config provided
    if options.spec_scaffold:
        from groundtruth_kb.spec_scaffold import scaffold_specs
        scaffold_specs(options.spec_scaffold, kdb)
    
    return target
```

**Standalone CLI:**
```
gt scaffold specs --platform azure --tenancy multi-tenant --auth mixed
```

This creates specs in an existing KB without re-running project init.

## Renamed Data Model

```python
@dataclass
class SpecScaffoldConfig:
    """Configuration for seed spec generation. NOT the same as ProjectProfile."""
    platform: str         # 'azure', 'aws', 'gcp', 'self-hosted'
    tenancy: str          # 'multi-tenant', 'single-tenant'
    auth_model: str       # 'magic-link', 'password', 'oauth', 'api-key', 'mixed'
    frontend: str         # 'spa', 'ssr', 'none'
    data_store: str       # 'cosmos', 'postgres', 'mysql', 'dynamodb', 'mongo'
    ai_components: bool = False
    compliance: list[str] = field(default_factory=list)  # ['gdpr', 'hipaa', 'soc2']
```

## Authority Policy for Generated Specs

**Phase A (existing schema):** Generated specs get `type='requirement'` and tags include `scaffold-generated`. No authority field (F1 not yet available).

**Phase B (after F1):** Generated specs get `authority='inferred'` — they are AI-generated templates, not owner directives. The owner confirms specs to promote to `stated`:

```python
# Owner confirmation (batch or individual):
kdb.update_spec(
    id=spec_id,
    changed_by="owner",
    change_reason="Owner confirmed scaffold spec",
    authority="stated",
)
```

This prevents the corruption vector where generated templates are treated as owner intent before the owner has reviewed them.

## Non-Empty KB Behavior

If `scaffold_specs()` is called on a KB with existing specs:
- Governance specs: skip if a GOV-* spec with the same handle already exists
- Other specs: generate with `_scaffold_` prefix tag for easy identification
- Report: "Generated N new specs, skipped M existing"
- No overwrites, no conflicts with existing data

## API Design

```python
class SpecScaffoldGenerator:
    def __init__(self, kdb: KnowledgeDB):
        self.kdb = kdb
    
    def generate(
        self,
        config: SpecScaffoldConfig,
        *,
        dry_run: bool = True,
    ) -> ScaffoldReport:
        """Generate seed specs. dry_run=True returns report without writing."""
        ...
    
    def generate_phase(
        self,
        config: SpecScaffoldConfig,
        phase: int,
    ) -> list[dict]:
        """Generate specs for a single phase only."""
        ...

@dataclass
class ScaffoldReport:
    phases: list[dict]
    total_generated: int
    total_skipped: int
    specs: list[dict]        # The generated spec data (for review before apply)
```

## Test Plan (synthetic fixtures)

1. **Minimal config** — `SpecScaffoldConfig(platform='self-hosted', tenancy='single-tenant', auth_model='password', frontend='none', data_store='postgres')`; verify governance specs generated
2. **Full config** — All options populated; verify all phases generate specs
3. **Non-empty KB** — Pre-populate KB with GOV-01; run scaffold; verify GOV-01 skipped, other govs generated
4. **Dry run** — `generate(dry_run=True)`; verify report populated, no specs in KB
5. **Authority (Phase B)** — After F1: verify generated specs have `authority='inferred'`; confirm one; verify promoted to `stated`
6. **Integration** — Call via `scaffold_project()` with `spec_scaffold` option; verify specs in newly created KB

## Implementation Sequence

Phase A: `SpecScaffoldConfig`, governance template library (derived from Agent Red GOV-01-20), infrastructure templates (parameterized by platform), `scaffold_specs()`, integration with `scaffold_project()`, CLI, 4 tests.
Phase B (after F1/F3): authority='inferred' on generated specs, F3 quality validation, tests 5-6.

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f6-002.md*
