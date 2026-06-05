REVISED

# Phase-1 Ollama Foundation Child — REVISED-3 addressing Codex NO-GO at -006 (capability-floor model + WI acceptance alignment + import guard)

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-1-foundation
Version: 007
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-006.md (NO-GO)
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

## Revision Claim (REVISED-3)

This REVISED-3 addresses the three findings in Codex's NO-GO at `bridge/gtkb-ollama-integration-phase-1-foundation-006.md`. All four prior cumulative fixes (F1/F2/F3 from -002 and F4 from -004) are PRESERVED unchanged. The three new corrections:

- **F5 (from -006) P1 FIX:** Adopt the **capability-floor model** for registered/no-active-role harnesses (Codex offered this as option 2 in -006 §F1 Required revision). Extend `scripts/check_harness_parity.py` to detect harnesses with `status="registered"` AND `role=[]` from the live registry projection, and evaluate them ONLY against the top-level `[harnesses.<name>]` capability-floor block — NOT against per-row `[capabilities.<harness>]` sub-table membership. This is consistent with AUQ#11's owner-approved "procedural + machine-checkable + capability floor" semantic and with the umbrella's GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer-3 design. Effect: `--all --markdown` continues to return baseline WARN (1 EXTRA: `gtkb-propose`); `--harness ollama` returns a capability-floor PASS verdict.

- **F6 (from -006) P1 FIX:** Update the live MemBase acceptance criteria for WI-4317 and WI-4318 via append-only versioning so the proposal and the canonical work items agree. Specifically: WI-4317 acceptance gains "capability-floor evaluation for registered harnesses"; WI-4318 title and acceptance change `[capabilities.ollama]` → `[harnesses.ollama]` (the 6-field semantic is preserved; the TOML namespace is corrected). MemBase mutation is authorized by the active PAUTH (WIs 4317/4318 are in its `included_work_item_ids` list) and by AUQ#11 (governance-depth approval covering capability-floor schema). Change reason cites this REVISED-3 + DELIB-20260663 owner-decision anchor.

- **F7 (from -006) P2 FIX:** Use the guarded import pattern observed in `scripts/harness_identity.py:14-16` + `scripts/harness_roles.py:47-49` for the projection-reader import in `scripts/check_harness_parity.py`. The pattern is `try: from scripts.harness_projection_reader import ... ; except ModuleNotFoundError: from harness_projection_reader import ...  # type: ignore[no-redef]`. This makes direct `python scripts/check_harness_parity.py` execution work regardless of whether the repo root is on sys.path.

Codex's positive confirmations from -006 are preserved: REVISED-2 fixed the reader-migration issue (F4) cleanly; the `tests/scripts` path defect remains fixed (F1); the `harnesses.ollama` semantic is carried consistently through the proposal; both preflights GREEN.

## Specification Links

| Spec | Severity | Trigger | How this child complies |
|------|----------|---------|------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | REVISED-3 versioned bridge file with canonical status token; INDEX entry updated with new REVISED line. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section enumerates all triggered specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:verification, spec-to-test | `requires_verification: true`; per-WI spec-to-test mapping updated for capability-floor mode + MemBase WI updates. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/** | D gets durable identity but role-set `[]`; single-ACTIVE-per-role invariant unaffected. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | content:harness-registry, role | D's role-set is empty; durable-vs-session-stated split N/A. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | Cites active PAUTH covering WIs 4316/17/18. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH `allowed_mutation_classes` is verified to include MemBase work-item updates (see §F6 below). |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs from the umbrella. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | Guarded-import pattern observed at `scripts/harness_identity.py:14-16` and `scripts/harness_roles.py:47-49` (verified at HEAD). |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WIs 4316/17/18 canonical backlog rows under PROJECT-GTKB-OLLAMA-INTEGRATION; F6 updates acceptance text via append-only versioning per the standing-backlog contract. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | WI-4317 generalizes KNOWN_HARNESSES AND adds capability-floor evaluation mode; parity-fallback semantic preserved; full `--all --markdown` continues to return baseline WARN. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, harness-state/**, config/agent-control/**, platform_tests/** | All target paths platform-side; no `applications/` touchpoints. |
| `REQ-HARNESS-REGISTRY-001` (FR5) | blocking-by-test | path:scripts/** reading harness state | F4 fix preserved: uses `scripts.harness_projection_reader.load_harness_projection` (stdlib-only hot-path reader). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact | harness identity, registry row, parity-checker capability-floor mode, capability block, WI acceptance updates — all durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Terminal at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, work item, project authorization | DELIB-20260663 + 3 WIs + PAUTH cited. |

**Forward references (specs drafted in umbrella; Child 4 lands them):**

| Spec draft | This child's relation |
|------------|----------------------|
| `ADR-OLLAMA-HARNESS-ADOPTION-001` | This child realizes the identity/registry portion. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-1 items 1-4 | All satisfied: identities (1), registry row (2), KNOWN_HARNESSES via projection (3), capability-floor block (4). |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-3 capability floor | Declares all 6 required fields in `[harnesses.ollama]`. **Child 4 obligation:** update GOV/DCL draft text from `capabilities.ollama.*` to `harnesses.ollama.*` before formal-artifact-approval packets. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Declares `advertised_tool_subset` from canonical 6-tuple in `[harnesses.ollama]`. |

## Requirement Sufficiency

**Existing requirements sufficient.** F5 (capability-floor mode) is authorized by AUQ#11 (procedural + machine-checkable + capability floor governance reach). F6 (MemBase WI acceptance updates) is mechanical alignment of canonical work-item text with the implementation reality this child delivers — covered by PAUTH `allowed_mutation_classes` for work-item updates. F7 (guarded import) is a Python-level compliance correction.

Per Codex NO-GO -006: "No owner input is required from this auto-dispatch worker."

## Prior Deliberations

- **`DELIB-20260663`** (S408, `owner_conversation`, `outcome=owner_decision`) — Direct owner-decision anchor. AUQ#11 (procedural + machine-checkable + capability floor) authorizes F5.
- **`bridge/gtkb-ollama-integration-phase-1-001.md` through `-004.md`** — Umbrella with GO authorizing child filings.
- **`bridge/gtkb-ollama-integration-phase-1-foundation-001.md` through `-006.md`** — operative predecessors corrected by this REVISED-3. NO-GOs at -002, -004, -006 each addressed one finding cluster cleanly; this REVISED-3 addresses the third.
- **`DELIB-2079`** Q4 — establishes `REQ-HARNESS-REGISTRY-001` FR5; F4 preserves compliance.
- **`platform_tests/scripts/test_harness_registry_reader_migration.py`** L559-582 + L608 — reader-migration invariant codification.
- **LO INSIGHTS** `INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md` + `INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md` — peer-solution advisory anchors.
- **`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`** + **`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** — supports D as `registered`/`role: []`. The capability-floor model is the direct expression of role/status orthogonality at the checker level.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits Ollama server invocation.
- **`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** v2 — informs WI-4317 capability-floor extension.
- **`scripts/harness_identity.py` L14-16 + `scripts/harness_roles.py` L47-49** — guarded-import precedent for F7.

## Owner Decisions / Input

DELIB-20260663 (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`; packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json` with sha256 `d7581bb32a858b113a59e8aedcb2224cb4f81c4211fd0375b22128c602564be2`).

Directly authoritative for this child:

- **AUQ#3:** D registered, no active role. → WI-4316 implementation.
- **AUQ#4:** MVP scope (identity + registry + shim + 1 model + E2E). → Foundation cluster.
- **AUQ#8:** Single project PAUTH covering Phase-1 WIs. → This child cites the PAUTH; F6 MemBase WI updates use PAUTH-authorized `allowed_mutation_classes`.
- **AUQ#11:** Procedural + machine-checkable + **capability floor** governance reach. → **Directly authorizes F5's capability-floor evaluation mode in the checker.** This is owner-approved schema-level design.

**No new owner input is requested by this REVISED-3 proposal.** Per Codex NO-GO -006 §Required Revision Scope and §Owner Action Required: this is mechanical compliance correction.

## Scope and Touchpoints

### WI-4316 — Reserve harness ID D + insert registry row (UNCHANGED across -003/-005/-007)

Files: `harness-state/harness-identities.json` (hand-edit), `harness-state/harness-registry.json` (regenerated from MemBase), `groundtruth.db` (insert `harnesses` row via `groundtruth_kb.harness_ops.register_harness` L298, regenerate via `groundtruth_kb.harness_projection.generate_harness_projection` L144).

Fields per AUQ#3: id=D, harness_name=ollama, harness_type=ollama, role=[], status=registered, event_driven_hooks=false, invocation_surfaces={}, capabilities_ref=null, reviewer_precedence=null, version=1.

### WI-4317 — Generalize KNOWN_HARNESSES + add capability-floor evaluation mode (F4 + F5 REVISED)

**Files:** `scripts/check_harness_parity.py` (loader + capability-floor mode), `platform_tests/scripts/test_check_harness_parity.py` (extend with tests).

#### Loader change (F4 preserved + F7 guarded import)

```python
# Guarded import — direct script execution may not have repo root on sys.path.
# Pattern from scripts/harness_identity.py:14-16 + scripts/harness_roles.py:47-49.
try:
    from scripts.harness_projection_reader import load_harness_projection
except ModuleNotFoundError:
    from harness_projection_reader import load_harness_projection  # type: ignore[no-redef]


_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")


def _load_known_harnesses_from_projection() -> tuple[str, ...]:
    """Derive KNOWN_HARNESSES from registry projection per REQ-HARNESS-REGISTRY-001 FR5."""
    projection = load_harness_projection(PROJECT_ROOT)
    names = tuple(
        sorted(
            str(record.get("harness_name"))
            for record in projection.get("harnesses", [])
            if isinstance(record, dict) and record.get("harness_name")
        )
    )
    return names if names else _FALLBACK_KNOWN_HARNESSES


KNOWN_HARNESSES = _load_known_harnesses_from_projection()
```

#### Capability-floor mode (F5 new)

A `_harness_lifecycle_class(harness_name)` helper inspects the registry projection and returns one of `"active"` (status=active), `"registered_no_role"` (status=registered AND role==[]), or `"other"` (suspended, active-with-empty-role, etc.). The classification is used to gate per-capability evaluation.

```python
CAPABILITY_FLOOR_REQUIRED_FIELDS = (
    "bridge_compliance_gate_respect",
    "root_boundary_respect",
    "author_metadata_env_var_setting",
    "destructive_gate_delegation",
    "advertised_tool_subset",
    "tool_guard_adapter_fail_closed",
)


def _harness_lifecycle_class(harness_name: str) -> str | None:
    """Return 'active' | 'registered_no_role' | 'other' | None from the registry projection."""
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


def _evaluate_capability_floor(harness_name: str, registry_data: dict[str, Any]) -> ExtraResult:
    """For registered/no-active-role harnesses, evaluate the top-level [harnesses.<name>] floor.

    Returns ExtraResult with state PASS / MISSING / EXTRA reflecting the floor declaration
    against CAPABILITY_FLOOR_REQUIRED_FIELDS and the canonical tools subset constraint.
    """
    floor = registry_data.get("harnesses", {}).get(harness_name, {})
    if not floor:
        return ExtraResult(
            kind="capability_floor",
            name=harness_name,
            state="MISSING",
            evidence=f"config/agent-control/harness-capability-registry.toml::[harnesses.{harness_name}]",
            note=f"No [harnesses.{harness_name}] capability-floor block in registry",
        )
    missing = [f for f in CAPABILITY_FLOOR_REQUIRED_FIELDS if f not in floor]
    if missing:
        return ExtraResult(
            kind="capability_floor",
            name=harness_name,
            state="MISSING",
            evidence=f"[harnesses.{harness_name}]",
            note=f"Missing capability-floor fields: {missing}",
        )
    advertised = floor.get("advertised_tool_subset", [])
    canonical_set = {"Read", "Write", "Edit", "Grep", "Glob", "Bash"}
    if not set(advertised).issubset(canonical_set):
        return ExtraResult(
            kind="capability_floor",
            name=harness_name,
            state="EXTRA",
            evidence=f"[harnesses.{harness_name}].advertised_tool_subset",
            note=f"Non-canonical tools in advertised_tool_subset: {set(advertised) - canonical_set}",
        )
    return ExtraResult(
        kind="capability_floor",
        name=harness_name,
        state="PASS",
        evidence=f"[harnesses.{harness_name}] (6 required fields present, advertised_tool_subset ⊆ canonical)",
        note="Capability floor satisfied",
    )
```

#### `--all` and `--harness` invocation behavior change (F5)

The main parity loop's per-harness iteration splits selected harnesses into `active_harnesses` (evaluated via existing per-capability logic) and `registered_floor_harnesses` (evaluated via `_evaluate_capability_floor`). Floor results appear in the report's `extras` list alongside undeclared-skill warnings; they DO NOT generate per-capability MISSING/STALE entries.

Concrete effect:
- `python scripts/check_harness_parity.py --all --markdown` continues to return baseline WARN (1 EXTRA: `gtkb-propose` undeclared); the new capability-floor entry for ollama is `state=PASS` (no new findings added).
- `python scripts/check_harness_parity.py --harness ollama` returns clean output: capability-floor PASS verdict, no per-capability MISSING.

#### Test extensions (F4 + F5 + F7)

`platform_tests/scripts/test_check_harness_parity.py` gains 5 new test functions (3 from REVISED-2 + 2 for F5):

1. `test_known_harnesses_data_driven_from_projection` — verifies ollama + claude + codex + antigravity all present.
2. `test_known_harnesses_fallback_on_empty_projection` — empty `harnesses` array falls back to baseline.
3. `test_known_harnesses_fallback_on_missing_projection` — missing file falls back.
4. **`test_capability_floor_for_registered_no_role_harness`** (NEW for F5) — fixture a registry with ollama status=registered, role=[]; assert `_harness_lifecycle_class("ollama") == "registered_no_role"`; assert `_evaluate_capability_floor("ollama", registry)` returns PASS when floor has all 6 fields.
5. **`test_capability_floor_missing_floor_returns_MISSING`** (NEW for F5) — fixture a registry without `[harnesses.ollama]`; assert floor evaluation returns MISSING.

### WI-4318 — Add [harnesses.ollama] top-level capability-floor block (UNCHANGED from -005)

**File:** `config/agent-control/harness-capability-registry.toml`. Append `[harnesses.ollama]` section with the 6 required fields. TOML-valid; does not conflict with `[[capabilities]]` array.

### F6: MemBase Work-Item Acceptance Updates (NEW for REVISED-3)

The current WI acceptance text in MemBase contradicts the proposal. F6 reconciles via append-only versioning under PAUTH authorization:

#### WI-4317 acceptance update

Current (pre-update): "KNOWN_HARNESSES contains all 4 harnesses; --harness ollama returns clean output; no unknown-harness false-positives."

New (post-update): "KNOWN_HARNESSES contains all 4 harnesses via registry-projection reader (no direct identity-file read per REQ-HARNESS-REGISTRY-001 FR5); --harness ollama returns clean capability-floor PASS verdict (registered/no-active-role harness lifecycle class); no unknown-harness false-positives; full --all --markdown remains at baseline WARN."

Rationale: the original acceptance was written before the capability-floor model was specified by Codex's NO-GO -006. The new acceptance is consistent with what the implementation actually delivers per AUQ#11 (capability-floor governance reach).

#### WI-4318 title + acceptance update

Current title: "Add [capabilities.ollama] block to config/agent-control/harness-capability-registry.toml"

New title: "Add [harnesses.ollama] capability-floor block to config/agent-control/harness-capability-registry.toml (TOML-valid namespace replacing [capabilities.ollama] which conflicts with [[capabilities]] array)"

Current acceptance: "harness-capability-registry.toml [capabilities.ollama] block exists with the 6 declared fields; doctor parity check passes."

New acceptance: "harness-capability-registry.toml [harnesses.ollama] block exists with the 6 declared capability-floor fields (bridge_compliance_gate_respect, root_boundary_respect, author_metadata_env_var_setting, destructive_gate_delegation, advertised_tool_subset, tool_guard_adapter_fail_closed); --harness ollama returns capability-floor PASS verdict; doctor parity check passes."

Rationale: TOML structural constraint (`[capabilities.ollama]` cannot coexist with `[[capabilities]]` array of tables at top level — confirmed by Codex's TOML parse experiment in NO-GO -002 §F2). The 6-field semantic from the original acceptance is preserved; only the section name is corrected.

#### MemBase update mechanics

Both updates use `groundtruth_kb` `update_work_item` (or equivalent append-only-versioning API) to insert a new version row for WI-4317 and WI-4318 with the updated text. `changed_by`: `claude-prime-builder`. `change_reason`: "REVISED-3 of foundation child per Codex NO-GO -006 §F2: align WI acceptance text with capability-floor model implementation; authorized by DELIB-20260663 AUQ#11 and PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE." PAUTH covers via `allowed_mutation_classes` (work-item updates are within standard project-implementation scope).

If PAUTH `allowed_mutation_classes` does NOT explicitly include work-item updates: this is a discoverable defect; report it and either (a) skip F6 with a documented Codex-visible note that WI acceptances need a separate owner-approved update bridge, or (b) request explicit owner approval via AskUserQuestion. Pre-impl check: verify PAUTH covers work-item updates BEFORE attempting MemBase mutation. If not covered, fall back to filing a follow-on WI to update PAUTH or to documenting the residual WI/proposal divergence.

## Implementation Plan

1. **Pre-impl check (NEW):** Read PAUTH `allowed_mutation_classes` and `included_work_item_ids`; verify WI-4317 + WI-4318 updates are authorized. If not, surface as a discoverable defect and either pause for owner approval (AskUserQuestion) or proceed with WI-4317/WI-4318 implementation only (no acceptance updates), documenting the residual divergence in the impl report.
2. MemBase + JSON projection insert (WI-4316).
3. Hand-edit `harness-state/harness-identities.json` (WI-4316).
4. Update `scripts/check_harness_parity.py` (WI-4317): guarded import, projection-reader-based KNOWN_HARNESSES loader, capability-floor mode (`_harness_lifecycle_class` + `_evaluate_capability_floor` + per-class iteration split in main loop).
5. Extend `platform_tests/scripts/test_check_harness_parity.py` (WI-4317): 5 test functions per above.
6. Append `[harnesses.ollama]` to `config/agent-control/harness-capability-registry.toml` (WI-4318).
7. MemBase work-item updates (F6, WI-4317 + WI-4318 acceptance text) — IF pre-impl check (step 1) PASSed.
8. Pre-file gates: `ruff check` + `ruff format --check` on changed Python files (both PASS).
9. Reader-migration regression: `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q` (no NEW failures vs baseline).
10. Targeted regression: `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` (all 5 new tests PASS).
11. Full parity (F3 preserved): `python scripts/check_harness_parity.py --all --markdown` (baseline WARN; capability-floor PASS for ollama).
12. `--harness ollama` (F5): `python scripts/check_harness_parity.py --harness ollama` (clean capability-floor PASS verdict).
13. Doctor: `python -m groundtruth_kb.cli project doctor --check role_set_topology_consistency` (PASS).
14. File post-implementation report as `bridge/gtkb-ollama-integration-phase-1-foundation-008.md` (NEW status).

## Specification-Derived Verification Plan

| Spec / WI | Test | PASS criterion |
|-----------|------|----------------|
| WI-4316: D registered/role=[] in projection | `python -c "import json; d=json.load(open('harness-state/harness-registry.json')); o=[h for h in d['harnesses'] if h['id']=='D']; assert len(o)==1 and o[0]['role']==[] and o[0]['status']=='registered'"` | Exits 0 |
| WI-4316: identities file has ollama entry | `python -c "import json; d=json.load(open('harness-state/harness-identities.json')); assert d['harnesses']['ollama']['id']=='D'"` | Exits 0 |
| WI-4317 + F4: KNOWN_HARNESSES sources from projection-reader | `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q` | No NEW failures vs baseline (1 pre-existing handoff.py failure documented in -004) |
| WI-4317 + F5: capability-floor mode evaluates registered harnesses | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_capability_floor_for_registered_no_role_harness platform_tests/scripts/test_check_harness_parity.py::test_capability_floor_missing_floor_returns_MISSING -q` | All 2 PASS |
| WI-4317: projection-based loader works in 3 modes | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_data_driven_from_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_empty_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_missing_projection -q` | All 3 PASS |
| **F5 spec-derivation: `--all --markdown` remains at baseline WARN (capability-floor mode keeps ollama out of per-capability scan)** | `python scripts/check_harness_parity.py --all --markdown` | Exit code matches baseline; EXTRA list = `[gtkb-propose]` (no ollama-driven cascade) |
| **F5 spec-derivation: `--harness ollama` returns capability-floor PASS verdict** | `python scripts/check_harness_parity.py --harness ollama --markdown` | Exit 0; output contains capability-floor result for ollama with state=PASS |
| **F6 spec-derivation: WI-4317 + WI-4318 acceptance text aligned with capability-floor model** | `python -c "import sqlite3; con=sqlite3.connect('groundtruth.db'); c=con.cursor(); rows=c.execute(\"SELECT id, acceptance_summary FROM current_work_items WHERE id IN ('WI-4317','WI-4318')\").fetchall(); assert all('capability-floor' in (r[1] or '').lower() for r in rows)"` | Exits 0 |
| WI-4318: `[harnesses.ollama]` capability-floor declared | `python -c "import tomllib; d=tomllib.loads(open('config/agent-control/harness-capability-registry.toml').read()); h=d['harnesses']['ollama']; assert h['tool_guard_adapter_fail_closed'] is True; assert h['advertised_tool_subset']==['Read','Write','Edit','Grep','Glob','Bash']"` | Exits 0 |
| `GOV-HARNESS-ROLE-PORTABILITY-001` invariant | doctor `_check_role_set_topology_consistency` | PASS |
| **F7 spec-derivation: import works under direct script execution** | `cd scripts && python check_harness_parity.py --harness ollama --markdown` (simulates direct execution with scripts/ as sys.path[0]) | Exit 0 (no ModuleNotFoundError) |
| Pre-file ruff gates | `ruff check` + `ruff format --check` on changed Python files | Both PASS |

## Risk and Rollback

### Risks

1. **MemBase insert collision on `harnesses` table.** Mitigation: pre-check, append-only versioning.
2. **PAUTH `allowed_mutation_classes` may not cover WI updates.** Mitigation: pre-impl check (step 1); fall back to filing follow-on WI or AUQ owner approval.
3. **Capability-floor mode breaks for active harnesses.** Mitigation: 5 test functions including lifecycle-class detection; existing parity-check semantic preserved for active harnesses.
4. **`_harness_lifecycle_class` import-time projection read fails.** Mitigation: projection reader's fail-safe behavior returns empty doc; classification returns None; per-class iteration falls back to legacy per-capability path (no harness skipped).
5. **F6 WI text updates not propagated to consumers.** Mitigation: `current_work_items` view reflects latest version; backlog CLIs read this view.
6. **antigravity in KNOWN_HARNESSES (active, no-role) → capability-floor evaluation cascade.** Lifecycle class for antigravity per registry: status=registered (per harness-registry.json L79) + role=["prime-builder"]. So antigravity is NOT registered/no-active-role → falls into existing per-capability path → no cascade.
7. **Reader-migration invariant tightening mid-flight.** Mitigation: F4 verification re-runs the regression at impl time.
8. **Child 4 obligation slippage.** Mitigation: documented binding obligation; Child 4 reviewer MUST verify before GO.

### Rollback

- **Per-WI revert.** Each WI's changes are isolated.
- **MemBase WI text revert.** Append-only versioning; new "retired" version with old text + `change_reason: "rollback per ..."`.
- **Whole-child revert.** `git revert <commit>` + MemBase `harnesses` row retirement + WI text rollback.
- **Phase-1 abandonment.** Children 2-4 NOT YET FILED; reverting removes foundation but leaves umbrella + PAUTH intact.

## Recommended Commit Type

`feat:` — new Ollama harness foundation infrastructure: identity + registry row, parity checker generalization with capability-floor evaluation mode for registered/no-active-role harnesses, capability floor declaration, MemBase work-item acceptance alignment. ~200 LOC across 4 source/config files + 5 new test functions + 2 MemBase work-item version inserts.

## INDEX Update

This REVISED-3 proposal inserts a new line at the top of the existing `Document: gtkb-ollama-integration-phase-1-foundation` entry in `bridge/INDEX.md`: `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-007.md` (per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`). Prior 6 status lines remain in place as the append-only audit trail.

## Pre-Filing Preflight Subsection

Expected:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

Expected result: applicability preflight PASS with `missing_required_specs: []`; clause preflight exits 0 with zero blocking gaps.

## Applicability Preflight

(To be appended by LO at review time.)

## Clause Applicability

(To be appended by LO at review time.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
