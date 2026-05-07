# GOV-20 Implementation Plan: Architecture Decision Governance

**Spec:** GOV-20 — Architecture Decision Governance (ADR/DCL/IPR/CVR lifecycle)
**Author:** Prime Builder (S218)
**Status:** Draft — pending Loyal Opposition review
**Date:** 2026-03-25

---

## Overview

This plan implements the four-artifact, three-gate system defined in GOV-20. Phase 1 uses existing KB tables with no schema migration. Phase 2 adds schema columns and hook enforcement. Phase 3 adds automation.

---

## Phase 1: Foundation (No Schema Migration)

### 1.1 — Store ADR-* as KB Specifications

**What:** ADRs stored in the `specifications` table with `type = 'architecture_decision'`.

**How:** Use existing `db.insert_spec()` with:
- `id`: `ADR-{N}` (monotonically increasing, start at ADR-001)
- `type`: `'architecture_decision'` (new type value — insert_spec accepts arbitrary type strings)
- `title`: Short decision summary (imperative form)
- `description`: Structured markdown with mandatory sections:
  ```
  ## Context
  [Problem being solved, forces at play]

  ## Decision
  [What was decided]

  ## Alternatives Considered
  [What was rejected and why]

  ## Consequences
  [What follows — positive and negative]

  ## Failed Approaches
  [Prior attempts that failed, with failure reasons]

  ## Derived Constraints
  DCL: DCL-001, DCL-002
  ```
- `status`: `proposed` → `accepted` → `superseded` | `rejected`
- `tags`: comma-separated, always includes `adr` plus domain tags
- `assertions`: Machine-verifiable checks for the decision (e.g., "implemented: No asyncio.Lock() at module level in src/multi_tenant/**")
- `scope`: Domain area (e.g., `encryption`, `async-lifecycle`, `tenant-isolation`)
- `section`: `architecture-decisions`

**Acceptance criteria:**
- ADR-001 through ADR-005 seeded from known decisions (see §1.5)
- `db.insert_spec(type='architecture_decision')` works without error
- KB web UI displays ADRs when filtered by type

**Files touched:** None (existing API supports arbitrary type values)

### 1.2 — Store DCL-* as KB Specifications

**What:** Design Constraint Checklists stored in `specifications` table with `type = 'design_constraint'`.

**How:** Use `db.insert_spec()` with:
- `id`: `DCL-{N}` (monotonically increasing, start at DCL-001)
- `type`: `'design_constraint'`
- `title`: Constraint in imperative form (e.g., "asyncio primitives must not be created at module level")
- `description`: Structured markdown:
  ```
  ## Source ADR
  ADR: ADR-001

  ## Scope
  src/multi_tenant/**

  ## Check Type
  grep | ast | test | hook | manual

  ## Check Definition
  [For grep: pattern to search. For test: TEST-ID. For manual: review question]

  ## Severity
  blocking | warning
  ```
- `status`: `active` | `retired`
- `assertions`: The check itself as a machine-verifiable assertion (e.g., "implemented: grep -r 'asyncio.Lock()' src/multi_tenant/ finds zero module-level instances")
- `tags`: Always includes `dcl` plus the ADR ID

**Acceptance criteria:**
- DCL-001 through DCL-010 derived from seeded ADRs (see §1.5)
- Each DCL has at least one machine-checkable assertion
- DCLs with `check_type=grep` have executable grep patterns

**Files touched:** None

### 1.3 — Store IPR-* as KB Documents

**What:** Implementation Proposal Reviews stored in `documents` table with `category = 'implementation_proposal'`.

**How:** Use `db.insert_document()` with:
- `id`: `IPR-{N}` (monotonically increasing)
- `category`: `'implementation_proposal'`
- `title`: `"IPR for WI-{N}: {WI title}"`
- `content`: Structured markdown:
  ```
  ## Work Item
  WI: WI-1635

  ## Applicable ADRs
  ADR: ADR-001, ADR-003

  ## Applicable DCLs
  DCL: DCL-001, DCL-005, DCL-007

  ## Compliance Plan
  ### DCL-001: asyncio primitives must not be created at module level
  - Compliance: Will use lazy initialization via factory function
  - Evidence: _get_dek_lock() pattern from base.py

  ### DCL-005: All tenant data access through repository hooks
  - Compliance: Using _pre_write/_post_read in BaseRepository
  - Evidence: No direct Cosmos container.* calls

  ### DCL-007: No cross-partition queries without explicit flag
  - Compliance: N/A — this WI does not add queries

  ## Status
  accepted
  ```
- `status`: `'active'`
- `tags`: `['ipr', 'WI-1635']`

**Acceptance criteria:**
- IPR can be created and retrieved via `db.insert_document()` / `db.get_document()`
- Content parses to extract WI, ADR, and DCL references (regex: `^(WI|ADR|DCL): (.+)$`)

**Files touched:** None

### 1.4 — Store CVR-* as KB Documents

**What:** Constraint Verification Records stored in `documents` table with `category = 'constraint_verification'`.

**How:** Use `db.insert_document()` with:
- `id`: `CVR-{N}`
- `category`: `'constraint_verification'`
- `title`: `"CVR for WI-{N}: {WI title}"`
- `content`: Structured markdown:
  ```
  ## Work Item
  WI: WI-1635

  ## IPR Reference
  IPR: IPR-001

  ## Constraint Results
  | DCL | Result | Evidence |
  |-----|--------|----------|
  | DCL-001 | PASS | grep finds 0 module-level asyncio.Lock() — verified in base.py |
  | DCL-005 | PASS | All writes go through _pre_write — TEST-10935 passes |
  | DCL-007 | N/A | No new queries added |

  ## Overall Status
  pass
  ```

**Acceptance criteria:**
- CVR can be created and retrieved
- Content includes pass/fail per DCL with evidence

**Files touched:** None

### 1.5 — Seed Initial ADRs and DCLs

**What:** Create ADR-001 through ADR-005 from known architectural decisions, then derive DCL-001 through DCL-010.

**Seed ADRs (from existing codebase decisions):**

| ADR | Decision | Source |
|-----|----------|--------|
| ADR-001 | Async lifecycle: all async primitives created within active event loop | S218 asyncio.Lock bug, base.py |
| ADR-002 | Tenant data isolation: all tenant data access through BaseRepository hooks (_pre_write/_post_read) | SPEC-1843, zero-knowledge architecture |
| ADR-003 | Encryption at rest: envelope encryption with per-tenant DEK, operator-blind | SPEC-1843/1844, ZERO-KNOWLEDGE-ARCHITECTURE-PLAN.md |
| ADR-004 | No hardcoded environment values: all FQDNs, keys, credentials from env vars | SPEC-0058, S211 enforcement |
| ADR-005 | Outside-in testing: tests exercise observable surfaces, not internal functions | GOV-19, S213 |

**Seed DCLs (derived from ADRs):**

| DCL | Constraint | ADR | Check Type | Scope |
|-----|-----------|-----|------------|-------|
| DCL-001 | No asyncio.Lock/Event/Semaphore at module level | ADR-001 | grep | src/** |
| DCL-002 | No global mutable state in async code paths | ADR-001 | manual | src/** |
| DCL-003 | All document writes go through BaseRepository._pre_write | ADR-002 | grep | src/multi_tenant/repositories/** |
| DCL-004 | No direct container.upsert_item/create_item outside BaseRepository | ADR-002 | grep | src/** |
| DCL-005 | All _encryption_fields declared on every repository | ADR-003 | test | tests/**/test_flow_encryption.py |
| DCL-006 | No plaintext write paths bypass envelope encryption | ADR-003 | test | tests/**/test_flow_encryption.py |
| DCL-007 | No hardcoded FQDNs in source files | ADR-004 | grep | src/**,tests/**,scripts/** |
| DCL-008 | No API keys or credentials in source files | ADR-004 | hook | .claude/hooks/credential-scan.py |
| DCL-009 | Tests verify behavior/state transitions, not just field existence | ADR-005 | manual | tests/** |
| DCL-010 | E2E tests exercise API endpoints, not Python functions | ADR-005 | manual | tests/e2e/** |

**Implementation:** Python script `scripts/seed_gov20.py` that calls `db.insert_spec()` for each ADR and DCL.

**Files touched:** `scripts/seed_gov20.py` (new, temporary)

### 1.6 — Update kb-work-item Skill

**What:** Extend the WI creation skill to require ADR/DCL linkage.

**How:** Add Step 2.5 between current Steps 2 and 3 in `.claude/skills/kb-work-item/SKILL.md`:

```
## Step 2.5: Architecture Review (GOV-20 -- MANDATORY)

Before creating the WI, identify applicable architecture decisions and constraints:

1. Query KB for ADRs with matching scope:
   db.list_specs(type='architecture_decision') — filter by scope/tags overlap with WI component
2. Query KB for DCLs derived from matched ADRs:
   db.list_specs(type='design_constraint') — filter by scope matching WI's file targets
3. Record linkage in WI description using structured format:
   ADR: ADR-001, ADR-003; DCL: DCL-001, DCL-005

If no ADRs/DCLs match, state explicitly: "No applicable ADRs/DCLs identified."
If the WI touches a new architectural area with no ADR, create the ADR first.
```

**Files touched:** `.claude/skills/kb-work-item/SKILL.md`

### 1.7 — Create kb-ipr Skill

**What:** New skill for creating Implementation Proposal Reviews.

**How:** `.claude/skills/kb-ipr/SKILL.md` with steps:
1. Accept WI ID as argument
2. Look up WI to get ADR/DCL references from description
3. Query each cited DCL for check_type and check_definition
4. Generate compliance plan template
5. Insert IPR document via `db.insert_document()`
6. Report IPR ID

**Files touched:** `.claude/skills/kb-ipr/SKILL.md` (new)

### 1.8 — Create kb-cvr Skill

**What:** New skill for creating Constraint Verification Records.

**How:** `.claude/skills/kb-cvr/SKILL.md` with steps:
1. Accept WI ID as argument
2. Look up IPR for this WI
3. For each DCL in the IPR, run the check:
   - grep: execute grep pattern against scope
   - test: run the linked test
   - hook: verify hook is active
   - manual: prompt Claude to answer the review question
4. Compile results table
5. Insert CVR document via `db.insert_document()`
6. Report CVR ID and overall pass/fail

**Files touched:** `.claude/skills/kb-cvr/SKILL.md` (new)

### 1.9 — Add Gate 1 to assertion-check.py

**What:** SessionStart hook reports WI readiness (IPR linkage).

**How:** Add `_check_wi_architecture_readiness(db)` function to `.claude/hooks/assertion-check.py`:

```python
def _check_wi_architecture_readiness(db) -> list[str]:
    """Check in-progress WIs for GOV-20 IPR linkage."""
    open_wis = [wi for wi in db.get_open_work_items()
                if wi.get("resolution_status") == "in_progress"]
    if not open_wis:
        return []

    missing_ipr = []
    for wi in open_wis:
        desc = wi.get("description", "")
        has_adr = "ADR:" in desc or "ADR-" in desc
        has_dcl = "DCL:" in desc or "DCL-" in desc
        # Check for IPR document
        iprs = [d for d in db.list_documents()
                if d.get("category") == "implementation_proposal"
                and f"WI: {wi['id']}" in (d.get("content") or "")]
        if not has_adr or not has_dcl or not iprs:
            missing_ipr.append(wi)

    if missing_ipr:
        lines = [f"GOV-20 READINESS WARNING: {len(missing_ipr)} in-progress WIs missing architecture review:"]
        for wi in missing_ipr:
            lines.append(f"  [{wi['id']}] {wi['title']} — create IPR before implementation")
        return lines
    return [f"GOV-20: {len(open_wis)} in-progress WIs all have accepted IPRs"]
```

Wire into `main()` alongside existing `_check_untested_work_items()`.

**Files touched:** `.claude/hooks/assertion-check.py`

### 1.10 — Update CLAUDE.md

**What:** Add GOV-20 to governance index and workflow.

**Changes:**
1. Add row to Governance Index table:
   `| 20 | Architecture decisions | ADR/DCL/IPR/CVR lifecycle; no implementation without accepted IPR |`
2. Add step 4a to workflow:
   `4a. Architecture review → create/cite ADRs, derive DCLs, create and accept IPR`
3. Add brief description under workflow section explaining the ADR/DCL/IPR/CVR chain

**Files touched:** `CLAUDE.md`

---

## Phase 2: Schema Evolution + Hook Enforcement

### 2.1 — Add columns to work_items table

Add `adr_ids TEXT` and `dcl_ids TEXT` columns to `work_items`. Update `insert_work_item()` to accept these as parameters.

**Files touched:** `tools/knowledge-db/db.py`, migration script

### 2.2 — PreToolUse hook for Gate 2 (pre-merge)

New hook `.claude/hooks/architecture-gate.py` that:
- On `Bash` tool use containing `git commit`:
  - Reads staged files via `git diff --cached --name-only`
  - For each staged file, checks if any active DCL's scope matches
  - If matched DCLs exist, verifies the active WI's IPR cites those DCLs
  - Blocks commit if uncited constraints are touched

**Files touched:** `.claude/hooks/architecture-gate.py` (new), `.claude/settings.json`

### 2.3 — Release pipeline Gate 3

Add CVR completeness check to `scripts/release_pipeline.py`:
- Query all WIs resolved since last release
- For each, verify a CVR document exists with status = pass
- Fail release if any WI lacks passing CVR

**Files touched:** `scripts/release_pipeline.py`

### 2.4 — Dedicated assertion check for IPR/CVR completeness

Add to `tools/knowledge-db/assertions.py`:
- Assert: every resolved WI (since GOV-20 adoption) has a CVR with status = pass
- Assert: every in-progress WI has an accepted IPR

**Files touched:** `tools/knowledge-db/assertions.py`

---

## Phase 3: Automation

### 3.1 — Auto-suggest ADRs/DCLs on WI creation

When `kb-work-item` skill runs, auto-query ADRs/DCLs by matching WI component against DCL scope patterns. Present suggested linkage to Claude for confirmation.

### 3.2 — Auto-generate IPR template

When `kb-ipr` skill runs, pre-populate the compliance plan by listing each matched DCL with its check_definition, so Claude only needs to fill in the compliance approach.

### 3.3 — CI validator

GitHub Actions workflow step that runs a Python script checking Gate 2 and Gate 3 conditions on every PR.

---

## Dependency Order

```
1.1 (ADR storage) ──┐
1.2 (DCL storage) ──┤
                    ├── 1.5 (Seed ADRs/DCLs)
1.3 (IPR storage) ──┤
1.4 (CVR storage) ──┘
                         │
              ┌──────────┴──────────┐
              │                     │
         1.6 (Update WI skill)  1.7 (IPR skill)
              │                     │
              └──────────┬──────────┘
                         │
                    1.8 (CVR skill)
                         │
                    1.9 (Gate 1 hook)
                         │
                    1.10 (CLAUDE.md)
                         │
              ┌──────────┼──────────┐
              │          │          │
         2.1 (Schema) 2.2 (Gate 2) 2.3 (Gate 3)
              │          │          │
              └──────────┴──────────┘
                         │
                    2.4 (Assertions)
                         │
              ┌──────────┼──────────┐
              │          │          │
         3.1 (Suggest) 3.2 (Template) 3.3 (CI)
```

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Overhead on every WI slows development | Phase 1 is self-enforcement only — no blocking hooks. Gate hooks come in Phase 2 after workflow is proven. |
| Retroactive IPR/CVR burden | Grandfathered: existing WIs exempt. Only new WIs after adoption. |
| ADR/DCL scope mismatch (too broad or narrow) | Start with 5 ADRs / 10 DCLs and iterate. DCL scope uses glob patterns that can be refined. |
| Claude forgets to create IPR | Gate 1 in assertion-check.py warns at session start. Phase 2 hook blocks implementation. |
| Schema migration risk | Phase 1 avoids migration entirely. Phase 2 migration is additive (new columns, no existing data affected). |

## Success Criteria

Phase 1 is complete when:
1. 5 ADRs and 10 DCLs exist in KB
2. kb-work-item skill requires ADR/DCL linkage
3. kb-ipr and kb-cvr skills exist and work
4. assertion-check.py reports WI readiness at session start
5. CLAUDE.md reflects GOV-20
6. Next WI created uses the full ADR→DCL→IPR→CVR workflow

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
