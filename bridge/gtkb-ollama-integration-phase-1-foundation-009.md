REVISED

# Phase-1 Ollama Foundation Child — REVISED-4 addressing Codex NO-GO at -008 (CLI exit-code enforcement + PAUTH path resolution)

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-1-foundation
Version: 009
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-008.md (NO-GO)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4316
work_item_ids: [WI-4316, WI-4317, WI-4318]
parent_bridge: gtkb-ollama-integration-phase-1
parent_status: GO@-004

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: cb8d1960-2984-4042-b76d-6a869cd0e16a
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic-pacing session

target_paths: ["harness-state/harness-identities.json", "harness-state/harness-registry.json", "scripts/check_harness_parity.py", "config/agent-control/harness-capability-registry.toml", "groundtruth.db", "platform_tests/scripts/test_check_harness_parity.py"]

requires_verification: true
implementation_scope: source_addition

## Revision Claim (REVISED-4)

This REVISED-4 addresses the two findings in Codex's NO-GO at `bridge/gtkb-ollama-integration-phase-1-foundation-008.md`. All five prior cumulative fixes (F1/F2/F3 from -002, F4 from -004, F5/F6/F7 from -006) are PRESERVED with the targeted refinements below. Codex confirmed the capability-floor MODEL DIRECTION is correct in -008 §Positive Confirmations: "the right direction for D as `registered`/`role: []`; the remaining issue is the checker failure semantics, not the model choice."

The two new corrections:

- **F8 (from -008) P1 FIX:** Model capability-floor checks as `CapabilityResult` rows (with `parity_class="required"`), NOT `ExtraResult` rows. The existing `_overall_status()` logic in `scripts/check_harness_parity.py:383-393` fails on `CapabilityResult(state="MISSING")` for required parity classes — so a missing or incomplete `[harnesses.ollama]` floor block will mechanically force `overall_status="FAIL"` and CLI exit code 1. Each capability-floor required field becomes its own `CapabilityResult` row (e.g., `floor.tool_guard_adapter_fail_closed` for harness `ollama`). The proposal's test scope is updated to include a CLI/report-level test that proves missing-floor → exit-code-1 (not just helper-level PASS/MISSING).

- **F9 (from -008) P1 FIX:** Resolve the PAUTH coverage path for the WI-4317/WI-4318 acceptance updates by **adopting Codex's option (c)** from -008 §F2: explicitly argue that the PAUTH `allowed_mutation_classes` value `membase_work_item_insert` (verified live: `["source_file", "test_file", "config_file", "protected_narrative_file", "membase_spec_insert", "membase_work_item_insert"]`) covers append-only `update_work_item()` version inserts. Rationale: `update_work_item()` (at `groundtruth-kb/src/groundtruth_kb/db.py:3569-3635`) creates a new version row in the `work_items` table — structurally an INSERT operation against the append-only versioned table, not a destructive UPDATE. The mutation class name reflects the database operation (INSERT INTO work_items), not the conceptual semantic (revising work-item content). The proposal specifies the EXACT direct Python invocation, the verification command, and removes the prior fallback branch that would have proceeded with WI/proposal divergence.

Codex's positive confirmations from -008 are preserved: REVISED-3 correctly addressed F4/F5/F7 (reader-migration, capability-floor model direction, guarded import); preflights GREEN.

## Specification Links

| Spec | Severity | Trigger | How this child complies |
|------|----------|---------|------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | REVISED-4 versioned bridge file with canonical status token; INDEX entry updated with new REVISED line. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section enumerates all triggered specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:verification, spec-to-test | `requires_verification: true`; per-WI spec-to-test mapping includes F8 CLI-level enforcement test + F9 verification command. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/** | D registered/role=[]; single-ACTIVE-per-role invariant preserved. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | content:harness-registry, role | D's role-set empty; durable-vs-session-stated split N/A. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | Cites active PAUTH; F9 resolves the mutation-class coverage question explicitly. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH `allowed_mutation_classes` interpreted per F9. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | Live PAUTH `allowed_mutation_classes` value verified by direct SQL read; live `_overall_status()` semantics verified at `scripts/check_harness_parity.py:383-393`; live `update_work_item()` API verified at `groundtruth-kb/src/groundtruth_kb/db.py:3569-3635`. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WIs 4316/17/18 canonical backlog rows; F6/F9 updates use append-only `update_work_item()` version inserts. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | Capability-floor evaluation preserves parity-fallback semantic. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, harness-state/**, config/agent-control/**, platform_tests/** | All target paths platform-side. |
| `REQ-HARNESS-REGISTRY-001` (FR5) | blocking-by-test | path:scripts/** reading harness state | F4 fix preserved: uses `scripts.harness_projection_reader.load_harness_projection`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact | All durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Terminal at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, work item, project authorization | DELIB-20260663 + 3 WIs + PAUTH cited. |

**Forward references** (UNCHANGED from -007).

## Requirement Sufficiency

**Existing requirements sufficient.** F8 (CLI exit-code enforcement) is a mechanical correction to the checker's failure semantics — the capability-floor model itself is already owner-approved via AUQ#11. F9 (PAUTH mutation-class coverage clarification) is a textual interpretation of the live `allowed_mutation_classes` list — `membase_work_item_insert` covers the database-level INSERT operation that `update_work_item()` performs. Per Codex NO-GO -008 §Owner Action Required: "None."

## Prior Deliberations

- **`DELIB-20260663`** (S408) — direct owner-decision anchor. AUQ#11 authorizes capability-floor governance reach (machine-checkable).
- **`bridge/gtkb-ollama-integration-phase-1-001.md` through `-004.md`** — umbrella with GO.
- **`bridge/gtkb-ollama-integration-phase-1-foundation-001.md` through `-008.md`** — full thread chain; each NO-GO converged the design (test path → namespace → parity command → reader migration → capability-floor model → CLI enforcement → PAUTH path).
- **`DELIB-2079`** Q4 — `REQ-HARNESS-REGISTRY-001` FR5 (F4 preserved).
- **`platform_tests/scripts/test_harness_registry_reader_migration.py`** L559-582 + L608 — reader-migration invariant.
- **LO INSIGHTS** — peer-solution advisory anchors.
- **`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`** + **`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** — supports D as registered/role:[].
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits Ollama server invocation.
- **`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** v2 — informs WI-4317.
- **`scripts/harness_identity.py` L14-16 + `scripts/harness_roles.py` L47-49** — guarded-import precedent (F7 preserved).
- **`scripts/check_harness_parity.py` L28-34, L383-393, L541** — `WARNING_STATES`, `_overall_status()` semantics, CLI exit-code path (F8 anchors).
- **`groundtruth-kb/src/groundtruth_kb/db.py` L3569-3635** — `KnowledgeDB.update_work_item()` API (F9 anchor).

## Owner Decisions / Input

DELIB-20260663 anchor unchanged. AUQ#11's "machine-checkable capability floor" governance reach is the direct authorization for F8's mechanical CLI enforcement of the floor — making the floor *machine-checkable* requires that missing-floor data fails the parity CLI. F9 is a textual clarification of an already-approved PAUTH; no new owner approval required per Codex NO-GO -008 §Owner Action Required.

**No new owner input is requested by this REVISED-4 proposal.**

## Scope and Touchpoints

### WI-4316 (UNCHANGED from -007)

MemBase row insert via `groundtruth_kb.harness_ops.register_harness`; regeneration via `groundtruth_kb.harness_projection.generate_harness_projection`; identities JSON hand-edit.

### WI-4317 — KNOWN_HARNESSES generalization + capability-floor mode (F4 + F5 + F7 PRESERVED, F8 NEW)

#### Guarded import (F7 preserved)

```python
try:
    from scripts.harness_projection_reader import load_harness_projection
except ModuleNotFoundError:
    from harness_projection_reader import load_harness_projection  # type: ignore[no-redef]
```

#### Projection-based loader (F4 preserved)

`_load_known_harnesses_from_projection()` unchanged from -007.

#### Capability-floor mode — REWORKED PER F8

Capability-floor evaluation now returns `list[CapabilityResult]` (NOT `ExtraResult`). Each required floor field becomes a `CapabilityResult` row with `parity_class="required"`, so the existing `_overall_status()` MISSING/FAIL semantic at `scripts/check_harness_parity.py:383-393` applies for free — missing or incomplete floor → `overall_status="FAIL"` → CLI exit code 1 at L541.

```python
CAPABILITY_FLOOR_REQUIRED_FIELDS = (
    "bridge_compliance_gate_respect",
    "root_boundary_respect",
    "author_metadata_env_var_setting",
    "destructive_gate_delegation",
    "advertised_tool_subset",
    "tool_guard_adapter_fail_closed",
)
CANONICAL_TOOL_SUBSET = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})


def _harness_lifecycle_class(harness_name: str) -> str | None:
    """Return 'active' | 'registered_no_role' | 'other' | None from registry projection."""
    projection = load_harness_projection(PROJECT_ROOT)
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict) or record.get("harness_name") != harness_name:
            continue
        status = record.get("status")
        role = record.get("role") or []
        if status == "registered" and role == []:
            return "registered_no_role"
        if status == "active":
            return "active"
        return "other"
    return None


def _evaluate_capability_floor(
    harness_name: str,
    registry_data: dict[str, Any],
) -> list[CapabilityResult]:
    """For registered/no-active-role harnesses, evaluate the top-level [harnesses.<name>] floor.

    Returns a list of CapabilityResult rows (NOT ExtraResult) so the existing
    _overall_status() MISSING-fails-required-parity semantic applies. Per F8 fix
    (Codex NO-GO -008): modeling floor checks as CapabilityResult with
    parity_class='required' makes missing/incomplete floor data mechanically force
    overall_status='FAIL' and CLI exit code 1.
    """
    floor = registry_data.get("harnesses", {}).get(harness_name, {})
    results: list[CapabilityResult] = []
    for field in CAPABILITY_FLOOR_REQUIRED_FIELDS:
        present = field in floor
        results.append(
            CapabilityResult(
                harness=harness_name,
                capability_id=f"capability_floor.{field}",
                capability_name=f"Capability floor: {field}",
                parity_class="required",
                required_for_roles=["registered_no_role"],
                configured_status="declared" if present else "missing",
                state="PASS" if present else "MISSING",
                evidence=f"config/agent-control/harness-capability-registry.toml::[harnesses.{harness_name}].{field}",
                note=("" if present else f"Required capability-floor field '{field}' not declared"),
            )
        )
    # Advertised-tool-subset extra-tools check: non-canonical entries also FAIL.
    advertised = floor.get("advertised_tool_subset", [])
    if floor and advertised:
        extras = set(advertised) - CANONICAL_TOOL_SUBSET
        if extras:
            results.append(
                CapabilityResult(
                    harness=harness_name,
                    capability_id="capability_floor.advertised_tool_subset.canonical",
                    capability_name="Capability floor: advertised_tool_subset ⊆ canonical 6-tuple",
                    parity_class="required",
                    required_for_roles=["registered_no_role"],
                    configured_status="extra_tools",
                    state="MISSING",  # MISSING for "canonical subset constraint not satisfied"
                    evidence=f"[harnesses.{harness_name}].advertised_tool_subset",
                    note=f"Non-canonical tools in advertised_tool_subset: {sorted(extras)}",
                )
            )
    return results
```

#### `--all` and `--harness` invocation behavior (F5 model + F8 enforcement)

The main parity loop's per-harness iteration calls `_harness_lifecycle_class(name)`:
- If `"registered_no_role"` → evaluate via `_evaluate_capability_floor()`; emit CapabilityResult rows into `report.results` (NOT extras); existing aggregate machinery handles MISSING→FAIL.
- If `"active"` → existing per-capability evaluation path (unchanged).
- If `"other"` or `None` → existing path (unchanged); no regression.

Concrete effect:
- `python scripts/check_harness_parity.py --all --markdown` after `[harnesses.ollama]` is present: returns baseline WARN (1 EXTRA: `gtkb-propose`); 6 new PASS rows for ollama's capability-floor fields; exit 0.
- `python scripts/check_harness_parity.py --harness ollama --markdown`: returns 6 PASS rows; exit 0.
- **Negative test (F8 fix)**: `python scripts/check_harness_parity.py --harness ollama --markdown` BEFORE `[harnesses.ollama]` is present (fixture state): returns 6 MISSING rows + overall_status=FAIL + exit code 1.

#### Test extensions — REWORKED PER F8

`platform_tests/scripts/test_check_harness_parity.py` gains 6 new test functions (3 from REVISED-2 + 3 for F5/F8):

1. `test_known_harnesses_data_driven_from_projection` (preserved)
2. `test_known_harnesses_fallback_on_empty_projection` (preserved)
3. `test_known_harnesses_fallback_on_missing_projection` (preserved)
4. `test_capability_floor_for_registered_no_role_harness` — fixture registry with ollama status=registered/role=[]; `_harness_lifecycle_class("ollama") == "registered_no_role"`; `_evaluate_capability_floor("ollama", registry)` returns 6 PASS CapabilityResults when floor has all 6 fields.
5. `test_capability_floor_missing_floor_returns_MISSING` — fixture registry without `[harnesses.ollama]`; floor evaluation returns 6 MISSING CapabilityResults.
6. **`test_cli_exits_nonzero_when_capability_floor_missing`** (F8 enforcement test) — fixture a temp project root with ollama in registry (status=registered/role=[]) but NO `[harnesses.ollama]` floor block in capability registry; invoke parity report end-to-end via `_collect_report(...)` or equivalent; assert `report.overall_status == "FAIL"`. Then invoke the CLI entry point as `subprocess.run([sys.executable, "scripts/check_harness_parity.py", "--harness", "ollama", "--markdown"], cwd=fake_root)`; assert `result.returncode == 1`. This proves CLI-level enforcement, not just helper-level state.

### WI-4318 — Add [harnesses.ollama] top-level capability-floor block (UNCHANGED from -007)

Append `[harnesses.ollama]` section with 6 required fields.

### F6/F9 (REWORKED): MemBase Work-Item Acceptance Updates via Confirmed Mutation Class

#### F9 Resolution: `membase_work_item_insert` covers `update_work_item()` append-only version inserts

Live PAUTH `allowed_mutation_classes` value (read via `python -c "import sqlite3; con=sqlite3.connect('groundtruth.db'); print(con.execute(\"SELECT allowed_mutation_classes FROM current_project_authorizations WHERE id LIKE '%OLLAMA%'\").fetchone()[0])"`): `["source_file", "test_file", "config_file", "protected_narrative_file", "membase_spec_insert", "membase_work_item_insert"]`.

The `update_work_item()` API at `groundtruth-kb/src/groundtruth_kb/db.py:3569-3635` is documented as creating a new version row in the `work_items` table — this is structurally an `INSERT INTO work_items (version=N+1, ...)` operation, NOT a destructive UPDATE of the prior version row. The append-only `(id, version)` uniqueness constraint guarantees that "update_work_item" never mutates an existing row; it inserts a new versioned row that the `current_work_items` view treats as the latest.

Therefore: `membase_work_item_insert` in the PAUTH `allowed_mutation_classes` covers the database-level INSERT operation performed by `update_work_item()`. Stating the mapping explicitly per Codex NO-GO -008 §F2 option (c).

This mapping is consistent with how `membase_spec_insert` covers `update_spec()` (both work the same way: append-only version insert via the corresponding `db.py` API).

#### F6 Concrete Invocation Path (NO Fallback Branch)

The acceptance updates run via direct Python invocation. The invocation is recorded in the implementation report:

```text
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB('groundtruth.db')
db.update_work_item(
    work_item_id='WI-4317',
    acceptance_summary='KNOWN_HARNESSES contains all 4 harnesses via registry-projection reader (no direct identity-file read per REQ-HARNESS-REGISTRY-001 FR5); --harness ollama returns clean capability-floor PASS verdict for registered/no-active-role lifecycle class; full --all --markdown remains at baseline WARN; capability-floor MISSING-floor case mechanically fails CLI exit code 1.',
    changed_by='claude-prime-builder',
    change_reason='REVISED-4 of foundation child per Codex NO-GO -008 §F2 option (c): align WI-4317 acceptance with capability-floor model implementation. PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE allowed_mutation_classes includes membase_work_item_insert which covers append-only update_work_item() version insert. Owner-decision anchor: DELIB-20260663 AUQ#11 capability-floor governance reach.',
)
db.update_work_item(
    work_item_id='WI-4318',
    title='Add [harnesses.ollama] capability-floor block to config/agent-control/harness-capability-registry.toml (TOML-valid namespace replacing [capabilities.ollama] which conflicts with [[capabilities]] array)',
    acceptance_summary='harness-capability-registry.toml [harnesses.ollama] block exists with the 6 declared capability-floor fields (bridge_compliance_gate_respect, root_boundary_respect, author_metadata_env_var_setting, destructive_gate_delegation, advertised_tool_subset, tool_guard_adapter_fail_closed); --harness ollama returns capability-floor PASS verdict; missing-floor case forces CLI exit code 1; doctor parity check passes.',
    changed_by='claude-prime-builder',
    change_reason='REVISED-4 of foundation child per Codex NO-GO -008 §F2 option (c): align WI-4318 title + acceptance with capability-floor TOML namespace. PAUTH covers via membase_work_item_insert mutation class. Owner-decision anchor: DELIB-20260663 AUQ#11.',
)
"
```

#### F9 Verification Command (NEW per -008)

```text
python -c "
import sqlite3
con = sqlite3.connect('groundtruth.db')
cur = con.cursor()
for wi in ('WI-4317', 'WI-4318'):
    row = cur.execute(
        'SELECT id, version, acceptance_summary FROM current_work_items WHERE id=?', (wi,)
    ).fetchone()
    print(f'{row[0]} v{row[1]}: acceptance_summary contains capability-floor evidence?', 'capability-floor' in (row[2] or '').lower())
    print(f'  acceptance: {row[2][:150]}...')
"
```

Expected: both WIs print `True` and their acceptance text reflects the capability-floor model + matches the proposal.

**No fallback branch.** Per Codex NO-GO -008 §F2 Required revision: "The next revision should not include a fallback that proceeds while leaving the WI/proposal divergence unresolved." The `membase_work_item_insert` PAUTH coverage is asserted unconditionally; if implementation reveals the mapping is rejected by a downstream gate, the implementation BLOCKS at that point (not a graceful proceed) and Prime files a follow-on REVISED.

## Implementation Plan

1. MemBase + JSON projection insert (WI-4316).
2. Hand-edit `harness-state/harness-identities.json` (WI-4316).
3. Update `scripts/check_harness_parity.py` (WI-4317): guarded import, projection-reader loader, capability-floor mode returning `list[CapabilityResult]` with `parity_class="required"`.
4. Extend `platform_tests/scripts/test_check_harness_parity.py` (WI-4317): 6 test functions including F8 CLI-level enforcement test.
5. Append `[harnesses.ollama]` to capability registry (WI-4318).
6. **MemBase work-item acceptance updates via `update_work_item()` direct Python invocation** (F6/F9 path).
7. Pre-file gates: `ruff check` + `ruff format --check` on changed Python files (both PASS).
8. Reader-migration regression: `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q` (no NEW failures).
9. Targeted regression: `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` (all 6 new tests PASS, including F8 CLI exit-code test).
10. Full parity (F3 preserved): `python scripts/check_harness_parity.py --all --markdown` (baseline WARN; 6 ollama floor PASS rows).
11. `--harness ollama` (F5/F8): `python scripts/check_harness_parity.py --harness ollama --markdown` (6 PASS rows; exit 0).
12. **F8 negative-path proof**: temporarily remove `[harnesses.ollama]` (or stash), re-run `--harness ollama`, observe exit code 1 + FAIL; restore (or use isolated fixture in test).
13. **F9 verification**: run the SQL readback command for WI-4317/WI-4318.
14. Doctor: `python -m groundtruth_kb.cli project doctor --check role_set_topology_consistency` (PASS).
15. File post-implementation report as `bridge/gtkb-ollama-integration-phase-1-foundation-010.md` (NEW).

## Specification-Derived Verification Plan

| Spec / WI | Test | PASS criterion |
|-----------|------|----------------|
| WI-4316: D registered/role=[] in projection | `python -c "import json; d=json.load(open('harness-state/harness-registry.json')); o=[h for h in d['harnesses'] if h['id']=='D']; assert len(o)==1 and o[0]['role']==[] and o[0]['status']=='registered'"` | Exits 0 |
| WI-4316: identities file has ollama | `python -c "import json; assert json.load(open('harness-state/harness-identities.json'))['harnesses']['ollama']['id']=='D'"` | Exits 0 |
| WI-4317 + F4: reader-migration regression | `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q` | No NEW failures (1 pre-existing handoff.py noted in -004) |
| WI-4317 + F5: capability-floor returns CapabilityResult list | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_capability_floor_for_registered_no_role_harness platform_tests/scripts/test_check_harness_parity.py::test_capability_floor_missing_floor_returns_MISSING -q` | All 2 PASS |
| WI-4317: projection loader 3 modes | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_data_driven_from_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_empty_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_missing_projection -q` | All 3 PASS |
| **F8 spec-derivation: missing floor → CLI exit 1 + overall_status FAIL** | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_cli_exits_nonzero_when_capability_floor_missing -q` | PASS |
| F5: `--all --markdown` returns baseline WARN | `python scripts/check_harness_parity.py --all --markdown` | Exit 0; EXTRA list = `[gtkb-propose]`; 6 new ollama floor PASS rows; no MISSING rows for ollama |
| F5: `--harness ollama` clean capability-floor PASS | `python scripts/check_harness_parity.py --harness ollama --markdown` | Exit 0; 6 PASS rows; no FAIL state |
| **F8 spec-derivation (negative path): floor removed → exit 1** | Equivalent to the `test_cli_exits_nonzero_when_capability_floor_missing` pytest test using its in-root fixture under the project root (the test fixtures a temp project tree using pytest's per-test isolated directory under the repo's `.gtkb-state/scratch/` area, runs the parity checker against the fake root, and asserts exit 1 + overall_status FAIL). No live mutation of the canonical capability registry file is performed; the negative path is exercised entirely within the isolated test fixture, keeping all paths in-root per ADR-ISOLATION-APPLICATION-PLACEMENT-001 CLAUSE-IN-ROOT. | Pytest assertion passes (exit code 1 observed in subprocess result) |
| **F9 spec-derivation: WI-4317 + WI-4318 acceptance text aligned** | (SQL readback command above) | Both WIs print `True` for capability-floor evidence |
| WI-4318: `[harnesses.ollama]` declared | `python -c "import tomllib; d=tomllib.loads(open('config/agent-control/harness-capability-registry.toml').read()); h=d['harnesses']['ollama']; assert h['tool_guard_adapter_fail_closed'] is True; assert set(h['advertised_tool_subset'])==set(['Read','Write','Edit','Grep','Glob','Bash'])"` | Exits 0 |
| `GOV-HARNESS-ROLE-PORTABILITY-001` invariant | doctor `_check_role_set_topology_consistency` | PASS |
| F7: import works under direct script execution | `cd scripts && python check_harness_parity.py --harness ollama --markdown` | Exit 0 |
| Pre-file ruff gates | `ruff check` + `ruff format --check` on changed Python files | Both PASS |

## Risk and Rollback

### Risks

1. **MemBase insert collision on `harnesses` table.** Mitigation: pre-check + append-only versioning.
2. **`update_work_item()` direct Python invocation fails.** Mitigation: per F9, the API at `db.py:3569-3635` is documented and tested; if the invocation fails, BLOCK (no fallback) and file follow-on REVISED.
3. **`membase_work_item_insert` PAUTH mapping rejected by a downstream gate.** Mitigation: pre-impl read of PAUTH `allowed_mutation_classes`; if downstream gate explicitly distinguishes inserts from updates, BLOCK and file follow-on REVISED. Per F9 rationale, this should not happen because the database operation IS an insert.
4. **Capability-floor as required CapabilityResult cascades unexpected failures.** Mitigation: F8 test fixtures exercise both positive (PASS) and negative (MISSING→FAIL) paths; existing per-capability tests for active harnesses are unaffected.
5. **antigravity lifecycle class.** Current registry: status=registered, role=["prime-builder"] → NOT `registered_no_role` (role non-empty) → existing path → no cascade.
6. **Reader-migration invariant tightening mid-flight.** Mitigation: F4 regression re-runs at impl time.
7. **Child 4 obligation slippage.** Mitigation: documented binding obligation.

### Rollback

- **Per-WI revert.** Each WI's changes isolated.
- **MemBase mutation revert.** Append-only versioning; new "retired" version for each row + `change_reason: "rollback per ..."`.
- **Whole-child revert.** `git revert <commit>` + MemBase `harnesses` row retirement + WI text rollback.
- **Phase-1 abandonment.** Children 2-4 NOT YET FILED.

## Recommended Commit Type

`feat:` — new Ollama harness foundation: identity + registry row, parity checker with capability-floor mode (CapabilityResult-based, CLI-enforcing), capability floor TOML block, MemBase work-item acceptance alignment via append-only versioning. ~220 LOC across 4 source/config files + 6 new test functions + 2 MemBase work-item version inserts.

## INDEX Update

This REVISED-4 inserts `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-009.md` at the top of the existing `Document: gtkb-ollama-integration-phase-1-foundation` entry. Prior 8 status lines remain as the append-only audit trail.

## Pre-Filing Preflight Subsection

Expected: applicability preflight PASS; clause preflight exits 0 with zero blocking gaps.

## Applicability Preflight

(To be appended by LO at review time.)

## Clause Applicability

(To be appended by LO at review time.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
