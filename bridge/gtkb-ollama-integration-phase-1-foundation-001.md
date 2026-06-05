NEW

# Phase-1 Ollama Foundation Child — Harness D Identity, Registry, Parity Checker, Capability Block

bridge_kind: implementation_proposal
Document: gtkb-ollama-integration-phase-1-foundation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
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

target_paths: ["harness-state/harness-identities.json", "harness-state/harness-registry.json", "scripts/check_harness_parity.py", "config/agent-control/harness-capability-registry.toml", "groundtruth.db", "tests/scripts/test_check_harness_parity.py"]

requires_verification: true
implementation_scope: source_addition

## Summary

This is **Child 1 of 4** under the Phase-1 Ollama integration umbrella (`bridge/gtkb-ollama-integration-phase-1-004.md` GO). It executes WI-4316 (primary), WI-4317, and WI-4318 — the **foundation cluster** establishing harness D's durable identity, MemBase-backed registry row, parity-checker enumeration, and harness-level capability declaration.

This child does NOT touch the shim (`scripts/ollama_harness.py`), routing (`.ollama/routing.toml`), verification (`scripts/verify_ollama_dispatch.py`), doctor, or formal-spec inserts. Those are Children 2-4. This child establishes the data-plane foundation that subsequent children read from.

Per AUQ#3 (DELIB-20260663): harness D enters as `status=registered` with role-set `[]`. The cross-harness event-driven trigger and single-harness bridge dispatcher continue to route only between B (claude), A (codex), and C (antigravity-when-active) — D is NOT a dispatch target in Phase 1.

## Specification Links

| Spec | Severity | Trigger | How this child complies |
|------|----------|---------|------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | NEW versioned bridge file with canonical status token; INDEX entry inserted post-Write. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section enumerates all triggered specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:verification, spec-to-test | `requires_verification: true`; per-WI spec-to-test mapping in §Specification-Derived Verification Plan. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/** | D gets durable identity but role-set `[]`; preserves single-ACTIVE-per-role invariant per S378 orthogonality. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | content:harness-registry, role | D's role-set is empty so the durable-vs-session-stated split is N/A. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | Cites `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE` (status=active, v1). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH covers WI-4316/4317/4318 per Phase-1 inclusion list. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs from the umbrella. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | All 4 target paths verified to exist at current commit; current contents inspected before drafting. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | WI-4316/4317/4318 already canonical backlog rows under PROJECT-GTKB-OLLAMA-INTEGRATION. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | WI-4317 generalizes KNOWN_HARNESSES; parity-fallback semantic preserved. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, harness-state/**, config/agent-control/** | All 4 target paths are platform-side under `E:\GT-KB`; none touch `applications/`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | harness identity, registry row, parity-checker enumeration, capability block — all durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Terminal at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, work item, project authorization | DELIB-20260663 + 3 WIs + PAUTH cited. |

**Forward references (specs drafted in umbrella but not yet inserted; Child 4 lands them via approval packets):**

| Spec draft | This child's relation |
|------------|----------------------|
| `ADR-OLLAMA-HARNESS-ADOPTION-001` | This child realizes the identity/registry portion of the ADR's decision. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-1 items 1-4 | This child satisfies items 1 (identities), 2 (registry row), 3 (KNOWN_HARNESSES), 4 (capabilities block). |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-3 capability floor | This child declares all 5 required fields in `[capabilities.ollama]`. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Declares `advertised_tool_subset` from the canonical 6-tuple. |

## Requirement Sufficiency

**Existing requirements sufficient.** The 12 AUQ owner decisions archived as DELIB-20260663 cover all material requirement-disambiguation questions for the foundation cluster. AUQ#3 (D registered, no active role), AUQ#4 (MVP scope), AUQ#8 (project PAUTH), and AUQ#11 (capability floor) directly authorize the 3 WIs in this child.

## Prior Deliberations

- **`DELIB-20260663`** (S408, `owner_conversation`, `outcome=owner_decision`) — Direct owner-decision anchor for the entire Phase-1 Ollama project. Approval packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json`.
- **`bridge/gtkb-ollama-integration-phase-1-001.md`** through **`-004.md`** (GO) — Parent umbrella; this child is the first of 4 implementation children authorized by the umbrella GO.
- **LO INSIGHTS** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md` — peer-solution decision memo (classification: adopt) recommending Option A.
- **LO INSIGHTS** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md` — LO parity gap analysis enumerating the 4 file touchpoints this child addresses.
- **`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`** — supports D as `registered` (no auto-dispatch) until a later promotion bridge.
- **`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** — confirms D = role-set `[]` + status `registered` is a clean orthogonal cell; no dispatch substrate changes required.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits local invocation of external harness executables (Ollama server at `localhost:11434`); Phase 1 only registers identity, no invocation yet.
- **`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** v2 — informs WI-4317 generalization: KNOWN_HARNESSES is part of the parity-fallback semantic.
- **`bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-004.md`** VERIFIED — earlier role-state-key drift fix; this child preserves the same recipient-key model (D never appears in recipient role-set lookups since role-set is `[]`).

## Owner Decisions / Input

The following AskUserQuestion answers, archived as **DELIB-20260663** (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`; packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json` with sha256 `d7581bb32a858b113a59e8aedcb2224cb4f81c4211fd0375b22128c602564be2`), authorize the work in this child.

Directly authoritative for this child:

- **AUQ#3 — Role for harness D:** `registered`, no active role. _Authorizes:_ `harness-registry.json` row with `role: []` and `status: "registered"`; forbids active-role assignment for D in Phase 1. **Implemented by this child via WI-4316.**
- **AUQ#4 — MVP scope:** Identity + registry + shim + ONE model + E2E test. _Authorizes:_ the 10 Phase-1 WIs; the foundation cluster (WI-4316/4317/4318) is the prerequisite layer. **Implemented by this child.**
- **AUQ#8 — PAUTH path:** Issue one project PAUTH covering Phase-1 WIs. _Authorizes:_ PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE (active v1, rowid 117) which **this child cites as its impl authorization envelope**. WIs 4316/4317/4318 are in the PAUTH `included_work_item_ids` list.
- **AUQ#11 — GOV reach:** Procedural + machine-checkable + capability floor. _Authorizes:_ the `[capabilities.ollama]` top-level block declared by WI-4318, which provides the 5-field capability floor declaration required by the (forward-referenced) `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-3 contract.

Additional context (DELIB-20260663 also captures AUQ#1, #2, #5, #6, #7, #9, #10, #12 — those apply to Children 2-4, not this foundation child).

**No new owner input is requested by this child proposal.** The 12-AUQ pass is sufficient; revising scope mid-cluster would require an explicit owner directive to amend DELIB-20260663.

## Scope and Touchpoints

### WI-4316 — Reserve harness ID D + insert registry row

**Files:**
- `harness-state/harness-identities.json` — add `"ollama"` key mapping to `{"id": "D", "assigned_at": "2026-06-05T...Z", "assigned_by": "owner-directed-initial-identity-via-DELIB-20260663"}`. Bump `updated_at`. Hand-edit is appropriate per its purpose statement ("Maps host-local harness installation names to durable unique IDs … by explicit owner-requested identity change") — DELIB-20260663 + AUQ#3 satisfies the owner-directed requirement.
- `harness-state/harness-registry.json` — insert ollama harness record per the existing schema. Fields:
  - `id`: "D"
  - `harness_name`: "ollama"
  - `harness_type`: "ollama"
  - `role`: `[]` (empty role-set per AUQ#3)
  - `status`: "registered"
  - `event_driven_hooks`: false (Ollama is a local model server; no native PreToolUse hook surface — the future shim implements guard-adapter parity)
  - `invocation_surfaces`: `{}` (no dispatch invocation in Phase 1; Children 2-4 may extend if required for verification harness)
  - `capabilities_ref`: null
  - `reviewer_precedence`: null
  - `version`: 1

  **Authoritative source:** the MemBase `harnesses` table is the SoT per `REQ-HARNESS-REGISTRY-001 FR5`; `harness-registry.json` is its hot-path projection. The row insert goes through MemBase first (via `groundtruth_kb.harness_ops` or equivalent), then `groundtruth_kb.harness_projection` regenerates the JSON file. The combined operation is atomic from the consumer's perspective.

  **MemBase insert authorization:** the `harnesses` table is a runtime registry, not a formal artifact (it is not in the formal-artifact-approval-gate's protected artifact-type list). PAUTH membership of WI-4316 + bridge GO suffices.

### WI-4317 — Generalize KNOWN_HARNESSES in scripts/check_harness_parity.py

**File:** `scripts/check_harness_parity.py` line 18.

**Current state:** `KNOWN_HARNESSES = ("claude", "codex")` — hardcoded 2-tuple. Antigravity (C) is already in `harness-state/harness-identities.json` AND has per-capability `[capabilities.antigravity]` blocks throughout `config/agent-control/harness-capability-registry.toml`, but is NOT in KNOWN_HARNESSES. This is pre-existing drift the foundation child resolves while adding ollama.

**Generalization approach:** data-drive KNOWN_HARNESSES from `harness-state/harness-identities.json`, with fallback to the hardcoded baseline tuple when the file is unreadable. This satisfies the WI-4317 "generalize" requirement (not merely "add ollama to a hardcoded tuple") and incidentally closes the antigravity gap.

Concrete change shape:

```python
_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")  # used only if identities file unavailable


def _load_known_harnesses_from_identities() -> tuple[str, ...]:
    identities_path = PROJECT_ROOT / "harness-state" / "harness-identities.json"
    if not identities_path.exists():
        return _FALLBACK_KNOWN_HARNESSES
    try:
        data = json.loads(identities_path.read_text(encoding="utf-8"))
        names = tuple(sorted(data.get("harnesses", {}).keys()))
        return names if names else _FALLBACK_KNOWN_HARNESSES
    except (json.JSONDecodeError, OSError):
        return _FALLBACK_KNOWN_HARNESSES


KNOWN_HARNESSES = _load_known_harnesses_from_identities()
```

**Tests:** unit test in `tests/scripts/test_check_harness_parity.py` covering: (a) baseline read from current identities file returns 4-tuple `("antigravity", "claude", "codex", "ollama")` post-WI-4316; (b) missing-file fallback to `("claude", "codex")`; (c) malformed-JSON fallback to `("claude", "codex")`.

### WI-4318 — Add [capabilities.ollama] top-level block to harness-capability-registry.toml

**File:** `config/agent-control/harness-capability-registry.toml`.

**Note on schema:** the existing `[[capabilities]]` array enumerates per-skill/per-hook surface mappings (with `[capabilities.<harness>]` sub-blocks per row). This child adds a **new top-level singular section** `[capabilities.ollama]` declaring harness-D's capability-floor declarations per the (forward-referenced) GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer-3 contract.

Concrete addition (appended at end of file, before any future per-skill rows that might later add `[capabilities.ollama]` sub-blocks — those are Child 4's concern, not this child):

```toml
[capabilities.ollama]
# Harness-level capability floor declaration per GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 3
# (spec inserted by Child 4). Declared here so Child 2/3 verification can read it before
# the spec lands. Phase-1 values:
bridge_compliance_gate_respect = true
root_boundary_respect = true
author_metadata_env_var_setting = true
destructive_gate_delegation = true
advertised_tool_subset = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
tool_guard_adapter_fail_closed = true  # per umbrella -003 revision
phase_1_only = true  # remove when role promotion lands in Phase 2+
```

**TOML compatibility:** since `[capabilities.ollama]` is a singular section while `[[capabilities]]` (array of tables) entries each define `[capabilities.<harness>]` sub-blocks, there's a naming-overlap risk. The proposed mitigation is to use a distinct section name `[harnesses.ollama]` instead. **DECISION POINT for LO review:** is the umbrella's literal `capabilities.ollama` section-name intent strict, or is `[harnesses.ollama]` an acceptable disambiguation? This proposal uses `[harnesses.ollama]` as the safer choice with the explanatory note above; if LO requires literal `[capabilities.ollama]` an inline-table at the top of the file (before `[[capabilities]]` rows) is the workaround.

The verification assertion `capabilities.ollama.tool_guard_adapter_fail_closed = true` from the umbrella becomes `harnesses.ollama.tool_guard_adapter_fail_closed = true` with this disambiguation.

## Implementation Plan

Ordered steps post-GO:

1. **MemBase + JSON projection insert (WI-4316).** Insert ollama row into MemBase `harnesses` table via `groundtruth_kb.harness_ops` (or equivalent). Regenerate `harness-state/harness-registry.json` via `groundtruth_kb.harness_projection`. Verify via direct read.
2. **Hand-edit `harness-state/harness-identities.json` (WI-4316).** Add `"ollama"` entry; update `updated_at`.
3. **Update `scripts/check_harness_parity.py` (WI-4317).** Add `_load_known_harnesses_from_identities` + use as KNOWN_HARNESSES source; add fallback constant; update related typed-dataclass usage if any.
4. **Add new test file `tests/scripts/test_check_harness_parity.py` (WI-4317).** Three test cases per WI-4317 scope above.
5. **Update `config/agent-control/harness-capability-registry.toml` (WI-4318).** Append `[harnesses.ollama]` section per shape above.
6. **Run pre-file gates:** `ruff check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py` + `ruff format --check` (both must PASS per file-bridge-protocol.md "Pre-File Code-Quality Gates").
7. **Run targeted regression:** `python -m pytest tests/scripts/test_check_harness_parity.py -q` (must PASS).
8. **Run doctor:** `python -m groundtruth_kb.cli project doctor --check role_set_topology_consistency` (must PASS — D + role-set [] is consistent topology).
9. **File post-implementation report** as `bridge/gtkb-ollama-integration-phase-1-foundation-002.md` (NEW status) with spec-to-test mapping and observed test output.

## Specification-Derived Verification Plan

| Spec / WI | Test | PASS criterion |
|-----------|------|----------------|
| WI-4316 spec-derivation: harness D registered with role-set `[]` | `python -c "import json; d=json.load(open('harness-state/harness-registry.json')); ollama=[h for h in d['harnesses'] if h['id']=='D']; assert len(ollama)==1; assert ollama[0]['role']==[]; assert ollama[0]['status']=='registered'"` | Exits 0 |
| WI-4316 spec-derivation: identities file has ollama entry | `python -c "import json; d=json.load(open('harness-state/harness-identities.json')); assert d['harnesses']['ollama']['id']=='D'"` | Exits 0 |
| WI-4317 spec-derivation: KNOWN_HARNESSES contains ollama | `python -c "from scripts.check_harness_parity import KNOWN_HARNESSES; assert 'ollama' in KNOWN_HARNESSES"` | Exits 0 |
| WI-4317 spec-derivation: KNOWN_HARNESSES is data-driven | `tests/scripts/test_check_harness_parity.py::test_known_harnesses_data_driven_from_identities` + `test_known_harnesses_fallback_on_missing_identities` + `test_known_harnesses_fallback_on_malformed_identities` | All 3 PASS |
| WI-4318 spec-derivation: capability-floor declared for ollama | `python -c "import tomllib; d=tomllib.loads(open('config/agent-control/harness-capability-registry.toml').read()); assert d['harnesses']['ollama']['tool_guard_adapter_fail_closed'] is True; assert d['harnesses']['ollama']['advertised_tool_subset']==['Read','Write','Edit','Grep','Glob','Bash']"` | Exits 0 |
| `GOV-HARNESS-ROLE-PORTABILITY-001` invariant: single-ACTIVE-per-role unaffected | doctor `_check_role_set_topology_consistency` | PASS (D registered/[] is orthogonal) |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` invariant: parity-fallback semantic preserved | Existing `tests/scripts/test_check_codex_hook_parity.py` (if present) | PASS |
| Pre-file ruff gates per file-bridge-protocol.md | `ruff check` + `ruff format --check` on changed Python files | Both PASS |

## Risk and Rollback

### Risks

1. **MemBase insert collision.** If a row with `id=D` already exists in `harnesses` table from prior speculative attempts: insert fails. _Mitigation:_ pre-check + use append-only versioning (insert new version if id exists).
2. **harness-registry.json regeneration disrupts other harness rows.** _Mitigation:_ `harness_projection` is idempotent; existing claude/codex/antigravity rows are re-emitted byte-identically by their MemBase truth.
3. **KNOWN_HARNESSES data-driven read fails at import time.** _Mitigation:_ fallback constant; tests cover missing-file and malformed-JSON cases.
4. **`[harnesses.ollama]` vs `[capabilities.ollama]` section-naming ambiguity.** Surfaced for LO review as the "DECISION POINT" above.
5. **antigravity-added-to-KNOWN_HARNESSES cascades unexpected parity-check failures.** Antigravity already has per-skill capability entries; adding it to KNOWN_HARNESSES enables stricter parity assertions. _Mitigation:_ run full `python scripts/check_harness_parity.py` pre-file; surface any new findings; revise scope if cascade is too broad.

### Rollback

- **Per-WI revert.** Each WI's changes are isolated to its own file(s). NO-GO on any single WI can be addressed in REVISED -003 without touching the other two WIs' changes.
- **Whole-child revert.** `git revert <commit>` reverts all 4 file changes; harness-registry.json is regenerated from MemBase (so MemBase row must also be removed via append-only "retired" version).
- **Phase-1 abandonment.** Children 2-4 are NOT YET FILED post this child. Reverting this child alone removes the foundation but leaves the umbrella + PAUTH intact for future revival.

## Recommended Commit Type

`feat:` — new Ollama harness foundation infrastructure (identity, registry, parity-checker generalization, capability floor declaration). ~150 LOC across 4 files + 1 new test file.

## INDEX Update

This proposal inserts a new `Document: gtkb-ollama-integration-phase-1-foundation` entry at the top of `bridge/INDEX.md` immediately after the proposal file is written (per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`). The INDEX entry registers status `NEW: bridge/gtkb-ollama-integration-phase-1-foundation-001.md`. No prior bridge version exists for this slug; no deletion or rewrite of historical INDEX content occurs. Subsequent verdict/post-impl versions append at the top of this entry's version list without disturbing other documents.

## Pre-Filing Preflight Subsection

The preflights below will be run after this proposal is filed and the INDEX entry added. Expected:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

Expected result: applicability preflight PASS with `missing_required_specs: []`; clause preflight exits 0 with zero blocking gaps. The Specification Links section above enumerates all triggered cross-cutting specs.

## Applicability Preflight

(To be appended by LO at review time after running `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation`.)

## Clause Applicability

(To be appended by LO at review time after running `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation`.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
