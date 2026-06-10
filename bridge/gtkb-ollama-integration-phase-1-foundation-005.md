REVISED

# Phase-1 Ollama Foundation Child — REVISED-2 addressing Codex NO-GO at -004 (WI-4317 reader-migration compliance)

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-1-foundation
Version: 005
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-004.md (NO-GO)
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

## Revision Claim (REVISED-2)

This REVISED-2 addresses the single P1 finding in Codex's NO-GO at `bridge/gtkb-ollama-integration-phase-1-foundation-004.md`. All three prior corrections from REVISED-1 (-003) are PRESERVED unchanged:

- **F1 (from -002):** test path remains `platform_tests/scripts/test_check_harness_parity.py` (canonical pytest-discovered location).
- **F2 (from -002):** TOML namespace remains `[harnesses.ollama]` with the binding Child-4 obligation to rewrite GOV/DCL draft assertions from `capabilities.ollama.*` to `harnesses.ollama.*` before formal-artifact-approval-packet creation.
- **F3 (from -002):** `python scripts/check_harness_parity.py --all --markdown` remains in required verification with documented baseline (WARN; 1 EXTRA: `gtkb-propose`).

The single new correction:

- **F4 (from -004) P1 FIX:** WI-4317's KNOWN_HARNESSES loader is reworked to read from `harness-state/harness-registry.json` via `scripts.harness_projection_reader.load_harness_projection`, NOT from the legacy `harness-state/harness-identities.json` directly. This satisfies the active reader-migration invariant enforced by `platform_tests/scripts/test_harness_registry_reader_migration.py` (which blocks any `scripts/` reader executing `harness-identities.json` `.read_text()`-style direct access). The 3 proposed tests are updated to fixture `harness-registry.json` instead of `harness-identities.json`. The data source change does NOT alter the WI-4317 semantic outcome — KNOWN_HARNESSES still ends up as `("antigravity", "claude", "codex", "ollama")` post-Child-1 because all four are entries in `harness-registry.json`.

Codex's positive confirmations from -004 are preserved:

- live INDEX read; WI 4316/17/18 exist and belong to PROJECT-GTKB-OLLAMA-INTEGRATION; PAUTH active and covers Phase-1 WIs; -003 fixes are correct in scope; both preflights GREEN with no missing required specs or blocking clause gaps; baseline parity-checker output is WARN with 1 EXTRA (`gtkb-propose`).

## Specification Links

| Spec | Severity | Trigger | How this child complies |
|------|----------|---------|------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | REVISED-2 versioned bridge file with canonical status token; INDEX entry updated with new REVISED line. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section enumerates all triggered specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:verification, spec-to-test | `requires_verification: true`; per-WI spec-to-test mapping in §Specification-Derived Verification Plan, updated for projection-reader sourcing. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/** | D gets durable identity but role-set `[]`; preserves single-ACTIVE-per-role invariant per S378 orthogonality. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | content:harness-registry, role | D's role-set is empty so the durable-vs-session-stated split is N/A. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | Cites `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE` (status=active, v1). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH covers WI-4316/4317/4318 per Phase-1 inclusion list. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs from the umbrella. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | All target paths re-verified at HEAD; `scripts/harness_projection_reader.py` confirmed present with `load_harness_projection`, `harness_by_id`, `id_for_name` exports. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WI-4316/4317/4318 already canonical backlog rows under PROJECT-GTKB-OLLAMA-INTEGRATION. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | WI-4317 generalizes KNOWN_HARNESSES via the registry-projection reader; parity-fallback semantic preserved; full `--all --markdown` command in verification per F3. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, harness-state/**, config/agent-control/**, platform_tests/** | All target paths are platform-side under `E:\GT-KB`; none touch `applications/`. |
| `REQ-HARNESS-REGISTRY-001` (FR5) | blocking-by-test | path:scripts/** reading harness state | This REVISED-2 explicitly uses `scripts.harness_projection_reader.load_harness_projection` (the FR5 stdlib-only hot-path reader), NOT a direct `harness-identities.json` read. Satisfies the reader-migration invariant. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | harness identity, registry row, parity-checker enumeration, capability block — all durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Terminal at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, work item, project authorization | DELIB-20260663 + 3 WIs + PAUTH cited. |

**Forward references (specs drafted in umbrella; Child 4 lands them):**

| Spec draft | This child's relation |
|------------|----------------------|
| `ADR-OLLAMA-HARNESS-ADOPTION-001` | This child realizes the identity/registry portion of the ADR's decision. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-1 items 1-4 | This child satisfies items 1 (identities), 2 (registry row), 3 (KNOWN_HARNESSES via projection-reader), 4 (capabilities block). **Child 4 obligation per F2 fix:** the Layer-3 capability floor draft text MUST be updated from `capabilities.ollama.*` to `harnesses.ollama.*` before formal-artifact-approval-packet creation. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-3 capability floor | This child declares all 5 required fields in `[harnesses.ollama]` (TOML-valid namespace). |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Declares `advertised_tool_subset` from the canonical 6-tuple. **Child 4 obligation per F2 fix:** assertion text MUST be updated to `harnesses.ollama.advertised_tool_subset matches canonical` before formal-artifact-approval-packet creation. |

## Requirement Sufficiency

**Existing requirements sufficient.** The 12 AUQ owner decisions archived as DELIB-20260663 cover all material requirement-disambiguation questions. The F4 fix is a mechanical compliance correction to the active reader-migration invariant (`REQ-HARNESS-REGISTRY-001` FR5); no new owner input required per Codex NO-GO -004 "No owner decision is required; this is a mechanical compliance correction."

## Prior Deliberations

- **`DELIB-20260663`** (S408, `owner_conversation`, `outcome=owner_decision`) — Direct owner-decision anchor for Phase-1 Ollama project. Approval packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json`.
- **`bridge/gtkb-ollama-integration-phase-1-001.md`** through **`-004.md`** (umbrella GO) — Parent umbrella authorizes child filings.
- **`bridge/gtkb-ollama-integration-phase-1-foundation-001.md` (NEW), `-002.md` (NO-GO), `-003.md` (REVISED-1), `-004.md` (NO-GO)** — operative predecessors corrected by this REVISED-2.
- **`DELIB-2079`** Q4 — establishes `REQ-HARNESS-REGISTRY-001` FR5 (SessionStart hot-path projection must be DB-independent; stdlib-only readers). The projection-reader migration invariant derives from this.
- **`platform_tests/scripts/test_harness_registry_reader_migration.py`** L559-582 + L608 — codifies the no-direct-read invariant via a planted-detector fixture. F4 fix conforms.
- **LO INSIGHTS** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md` + `INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md` — peer-solution decision memo + parity gap analysis.
- **`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`** — supports D as `registered` (no auto-dispatch).
- **`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** — confirms D = role-set `[]` + status `registered`.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits Ollama server invocation at `localhost:11434`; Phase 1 only registers identity.
- **`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** v2 — informs WI-4317 generalization.
- **`platform_tests/governance/test_platform_tests_rename.py`** L134-141 — codifies the bare-`tests` testpath retirement that motivated F1.

## Owner Decisions / Input

The following AskUserQuestion answers, archived as **DELIB-20260663** (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`; packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json` with sha256 `d7581bb32a858b113a59e8aedcb2224cb4f81c4211fd0375b22128c602564be2`), authorize the work in this child.

Directly authoritative for this child:

- **AUQ#3 — Role for harness D:** `registered`, no active role. **Implemented by this child via WI-4316.**
- **AUQ#4 — MVP scope:** Identity + registry + shim + ONE model + E2E test. **Implemented by this child (foundation cluster).**
- **AUQ#8 — PAUTH path:** Issue one project PAUTH covering Phase-1 WIs. **This child cites the active PAUTH as its impl authorization envelope.**
- **AUQ#11 — GOV reach:** Procedural + machine-checkable + capability floor. **Implemented via `[harnesses.ollama]` top-level block declared by WI-4318.**

**No new owner input is requested by this REVISED-2 proposal.** Per Codex NO-GO -004 §Required Revision Scope: "No owner decision is required; this is a mechanical compliance correction."

## Scope and Touchpoints

### WI-4316 — Reserve harness ID D + insert registry row (UNCHANGED from -003)

**Files:**
- `harness-state/harness-identities.json` — add `"ollama"` key mapping to `{"id": "D", "assigned_at": "2026-06-05T...Z", "assigned_by": "owner-directed-initial-identity-via-DELIB-20260663"}`. Bump `updated_at`. Hand-edit per the file's stated purpose ("Maps host-local harness installation names to durable unique IDs … by explicit owner-requested identity change") — DELIB-20260663 + AUQ#3 satisfies the owner-directed requirement.
- `harness-state/harness-registry.json` — insert ollama harness record per existing schema. Fields:
  - `id`: "D"
  - `harness_name`: "ollama"
  - `harness_type`: "ollama"
  - `role`: `[]` (empty role-set per AUQ#3)
  - `status`: "registered"
  - `event_driven_hooks`: false
  - `invocation_surfaces`: `{}` (no dispatch invocation in Phase 1)
  - `capabilities_ref`: null
  - `reviewer_precedence`: null
  - `version`: 1

  **Authoritative source:** the MemBase `harnesses` table is the SoT per `REQ-HARNESS-REGISTRY-001 FR5`; `harness-registry.json` is its hot-path projection. The row insert goes through MemBase first (via `groundtruth_kb.harness_ops.register_harness` at L298), then `groundtruth_kb.harness_projection.generate_harness_projection` at L144 regenerates the JSON file. Atomic from the consumer's perspective.

  **MemBase insert authorization:** the `harnesses` table is a runtime registry, not a formal artifact. PAUTH membership of WI-4316 + bridge GO suffices.

### WI-4317 — Generalize KNOWN_HARNESSES via registry-projection reader (F4 REVISED)

**Files:**
- `scripts/check_harness_parity.py` line 18: replace `KNOWN_HARNESSES = ("claude", "codex")` with a data-driven loader from `harness-state/harness-registry.json` **via `scripts.harness_projection_reader.load_harness_projection`**, with a fallback constant for empty/missing-projection states.
- `platform_tests/scripts/test_check_harness_parity.py` (existing 8048-byte file): **EXTEND** with 3 new test functions that **fixture `harness-state/harness-registry.json`** (NOT `harness-identities.json`).

**F4 fix per Codex NO-GO -004:** The previous REVISED-1 loader would have read `harness-state/harness-identities.json` directly via `Path.read_text()`. That conflicts with the active reader-migration invariant enforced by `platform_tests/scripts/test_harness_registry_reader_migration.py` L559-582 + planted-detector fixture at L608: every migrated production reader under `scripts/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, and `groundtruth-kb/src/groundtruth_kb/` MUST resolve harness identity/role from `harness-state/harness-registry.json` through the projection reader, NOT from the legacy identity JSON file.

Concrete `scripts/check_harness_parity.py` change shape (F4-compliant):

```python
from scripts.harness_projection_reader import load_harness_projection


_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")  # used only if projection is empty/missing


def _load_known_harnesses_from_projection() -> tuple[str, ...]:
    """Derive KNOWN_HARNESSES from the registry projection per REQ-HARNESS-REGISTRY-001 FR5.

    Uses scripts.harness_projection_reader (stdlib-only, fail-safe) to satisfy
    the active reader-migration invariant; direct reads of harness-identities.json
    are forbidden under the planted-detector fixture in
    platform_tests/scripts/test_harness_registry_reader_migration.py.
    """
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

Concrete `platform_tests/scripts/test_check_harness_parity.py` extension shape (3 new functions appended; fixtures use `harness-registry.json`):

```python
def test_known_harnesses_data_driven_from_projection(tmp_path: Path) -> None:
    """KNOWN_HARNESSES reads from harness-state/harness-registry.json projection."""
    # Live projection at HEAD includes ollama after WI-4316
    module = _load_module()
    assert "ollama" in module.KNOWN_HARNESSES
    assert "claude" in module.KNOWN_HARNESSES
    assert "codex" in module.KNOWN_HARNESSES
    assert "antigravity" in module.KNOWN_HARNESSES


def test_known_harnesses_fallback_on_empty_projection(monkeypatch, tmp_path: Path) -> None:
    """When the projection has no harnesses entry, falls back to baseline tuple."""
    fake_root = tmp_path
    (fake_root / "harness-state").mkdir()
    (fake_root / "harness-state" / "harness-registry.json").write_text(
        '{"harnesses": [], "schema_version": 1}', encoding="utf-8"
    )
    monkeypatch.setattr("check_harness_parity.PROJECT_ROOT", fake_root)
    module = _load_module()
    result = module._load_known_harnesses_from_projection()
    assert result == ("claude", "codex")


def test_known_harnesses_fallback_on_missing_projection(monkeypatch, tmp_path: Path) -> None:
    """When the projection file is missing entirely, falls back via the safe-default reader."""
    fake_root = tmp_path
    (fake_root / "harness-state").mkdir()  # parent exists, file absent
    monkeypatch.setattr("check_harness_parity.PROJECT_ROOT", fake_root)
    module = _load_module()
    result = module._load_known_harnesses_from_projection()
    assert result == ("claude", "codex")
```

Note: malformed-JSON is handled inside `load_harness_projection` itself (it returns a normalized empty document on parse failure per the docstring at `scripts/harness_projection_reader.py:1-19`); so the third test covers missing-file via the same fail-safe path.

### WI-4318 — Add [harnesses.ollama] top-level block to harness-capability-registry.toml (UNCHANGED from -003)

**File:** `config/agent-control/harness-capability-registry.toml`.

**Namespace choice (F2):** `[harnesses.ollama]` — TOML-valid; the umbrella-approved capability-floor semantic is unchanged.

**Cross-Child dependency (binding on Child 4):** GOV-HARNESS-ONBOARDING-CONTRACT-001 + DCL-OLLAMA-TOOL-PARITY-GATE-001 draft assertions MUST be rewritten from `capabilities.ollama.*` to `harnesses.ollama.*` BEFORE Child-4 formal-artifact-approval packet creation.

Concrete addition (appended at end of file):

```toml
[harnesses.ollama]
# Harness-level capability floor declaration per GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 3
# (spec inserted by Child 4; draft assertions updated from capabilities.ollama.* to
# harnesses.ollama.* per Cross-Child dependency in foundation-005.md). Declared here so
# Child 2/3 verification can read it before the spec lands. Phase-1 values:
bridge_compliance_gate_respect = true
root_boundary_respect = true
author_metadata_env_var_setting = true
destructive_gate_delegation = true
advertised_tool_subset = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
tool_guard_adapter_fail_closed = true  # per umbrella -003 revision
phase_1_only = true  # remove when role promotion lands in Phase 2+
```

## Implementation Plan

Ordered steps post-GO:

1. **MemBase + JSON projection insert (WI-4316).** Insert ollama row into MemBase `harnesses` table via `groundtruth_kb.harness_ops.register_harness`. Regenerate `harness-state/harness-registry.json` via `groundtruth_kb.harness_projection.generate_harness_projection`. Verify via direct read of the regenerated projection (D row present, status=registered, role=[]).
2. **Hand-edit `harness-state/harness-identities.json` (WI-4316).** Add `"ollama"` entry; update `updated_at`.
3. **Update `scripts/check_harness_parity.py` (WI-4317, F4-compliant).** Replace `KNOWN_HARNESSES = ("claude", "codex")` with `_load_known_harnesses_from_projection()`-derived value; add fallback constant; import `load_harness_projection` from `scripts.harness_projection_reader`.
4. **Extend `platform_tests/scripts/test_check_harness_parity.py` (WI-4317).** Append the 3 test functions shown above (data-driven from projection, fallback on empty projection, fallback on missing projection).
5. **Update `config/agent-control/harness-capability-registry.toml` (WI-4318).** Append `[harnesses.ollama]` section per shape above.
6. **Run pre-file gates per file-bridge-protocol.md:** `ruff check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py` + `ruff format --check` on the same files (both MUST PASS).
7. **Run reader-migration regression (F4 verification):** `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q --tb=short` — must show no new failures introduced by the change. Baseline: 1 pre-existing failure (`groundtruth-kb/src/groundtruth_kb/session/handoff.py:209` direct read; documented in Codex NO-GO -004 as not caused by this proposal).
8. **Run targeted regression:** `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` (must PASS, including the 3 new tests).
9. **Run full harness parity check (F3):** `python scripts/check_harness_parity.py --all --markdown`. Document output in report. Expected baseline: WARN with `1 EXTRA: gtkb-propose undeclared`. Any new findings beyond that baseline indicate cascade from this change and MUST be analyzed.
10. **Run doctor:** `python -m groundtruth_kb.cli project doctor --check role_set_topology_consistency` (must PASS).
11. **File post-implementation report** as `bridge/gtkb-ollama-integration-phase-1-foundation-006.md` (NEW status) with spec-to-test mapping, full parity-checker output, reader-migration regression output, and baseline-comparison narrative.

## Specification-Derived Verification Plan

| Spec / WI | Test | PASS criterion |
|-----------|------|----------------|
| WI-4316 spec-derivation: harness D registered with role-set `[]` | `python -c "import json; d=json.load(open('harness-state/harness-registry.json')); ollama=[h for h in d['harnesses'] if h['id']=='D']; assert len(ollama)==1; assert ollama[0]['role']==[]; assert ollama[0]['status']=='registered'"` | Exits 0 |
| WI-4316 spec-derivation: identities file has ollama entry | `python -c "import json; d=json.load(open('harness-state/harness-identities.json')); assert d['harnesses']['ollama']['id']=='D'"` | Exits 0 |
| WI-4317 spec-derivation: KNOWN_HARNESSES contains ollama via projection | `python -c "from scripts.check_harness_parity import KNOWN_HARNESSES; assert 'ollama' in KNOWN_HARNESSES"` | Exits 0 |
| **F4 spec-derivation: KNOWN_HARNESSES sources from projection-reader (NO direct identity-file read)** | `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q --tb=short` | No NEW failures vs baseline (1 pre-existing handoff.py failure documented in -004); planted-detector confirms `scripts/check_harness_parity.py` is NOT a new offender |
| WI-4317 spec-derivation: projection-based loader works in 3 modes | `python -m pytest platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_data_driven_from_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_empty_projection platform_tests/scripts/test_check_harness_parity.py::test_known_harnesses_fallback_on_missing_projection -q` | All 3 PASS |
| **F3 verification: full parity checker output captured + baseline comparison** | `python scripts/check_harness_parity.py --all --markdown` | Exit code matches baseline (WARN); EXTRA list matches baseline (`gtkb-propose`) unless additional findings introduced by KNOWN_HARNESSES expansion are analyzed and accepted in the report |
| WI-4318 spec-derivation: capability-floor declared for ollama | `python -c "import tomllib; d=tomllib.loads(open('config/agent-control/harness-capability-registry.toml').read()); assert d['harnesses']['ollama']['tool_guard_adapter_fail_closed'] is True; assert d['harnesses']['ollama']['advertised_tool_subset']==['Read','Write','Edit','Grep','Glob','Bash']"` | Exits 0 |
| `GOV-HARNESS-ROLE-PORTABILITY-001` invariant: single-ACTIVE-per-role unaffected | doctor `_check_role_set_topology_consistency` | PASS (D registered/[] is orthogonal) |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` invariant: parity-fallback semantic preserved | Existing parity-related tests in `platform_tests/scripts/` | PASS (no regression in existing parity test surface) |
| Pre-file ruff gates per file-bridge-protocol.md "Pre-File Code-Quality Gates" | `ruff check` + `ruff format --check` on the two changed Python files | Both PASS separately |

## Risk and Rollback

### Risks

1. **MemBase insert collision.** If a row with `id=D` already exists in `harnesses` table from prior speculative attempts: insert fails. _Mitigation:_ pre-check + use append-only versioning.
2. **harness-registry.json regeneration disrupts other rows.** _Mitigation:_ `harness_projection` is idempotent.
3. **Projection-reader import-time failure.** If `scripts.harness_projection_reader` is not importable at `check_harness_parity.py` load time, KNOWN_HARNESSES falls back to baseline tuple (2-element). _Mitigation:_ fallback constant + reader's own fail-safe behavior on missing/malformed projection.
4. **antigravity-added-to-KNOWN_HARNESSES cascades unexpected parity-check findings beyond the documented `gtkb-propose` baseline.** _Mitigation:_ F3 fix requires full `--all --markdown` command with explicit baseline comparison; new findings analyzed in implementation report.
5. **Child 4 obligation slippage.** Child 4 must update GOV/DCL draft text from `capabilities.ollama.*` to `harnesses.ollama.*`. _Mitigation:_ documented binding obligation in §Specification Links → "Forward references"; Child 4 reviewer (Codex) MUST verify before GO.
6. **Reader-migration invariant tightening mid-flight.** If `test_harness_registry_reader_migration.py` is updated to forbid additional patterns during Child 1 implementation, the loader might need adjustment. _Mitigation:_ verification step 7 above re-runs the regression at implementation time.

### Rollback

- **Per-WI revert.** Each WI's changes are isolated to its own file(s).
- **Whole-child revert.** `git revert <commit>` reverts all file changes; harness-registry.json is regenerated from MemBase (so MemBase row must also be removed via append-only "retired" version).
- **Phase-1 abandonment.** Children 2-4 NOT YET FILED post this child. Reverting removes the foundation but leaves the umbrella + PAUTH intact for future revival.

## Recommended Commit Type

`feat:` — new Ollama harness foundation infrastructure (identity, registry, parity-checker generalization via registry-projection reader, capability floor declaration). ~120 LOC across 4 source/config files + 3 new test functions in existing `platform_tests/scripts/test_check_harness_parity.py`.

## INDEX Update

This REVISED-2 proposal inserts a new line at the top of the existing `Document: gtkb-ollama-integration-phase-1-foundation` entry in `bridge/INDEX.md`: `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-005.md` (per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`). Prior NEW@-001, NO-GO@-002, REVISED-1@-003, NO-GO@-004 lines remain in place beneath it as the append-only audit trail. No deletion or rewrite of historical INDEX content occurs.

## Pre-Filing Preflight Subsection

The preflights below will be run after this REVISED-2 proposal is filed and the INDEX entry added. Expected:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

Expected result: applicability preflight PASS with `missing_required_specs: []`; clause preflight exits 0 with zero blocking gaps.

## Applicability Preflight

(To be appended by LO at review time after running `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation`.)

## Clause Applicability

(To be appended by LO at review time after running `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation`.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
