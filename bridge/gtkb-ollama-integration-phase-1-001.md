NEW

# Phase-1 Ollama Harness Integration — Governance Umbrella + Spec Drafts

bridge_kind: governance_review
Document: gtkb-ollama-integration-phase-1
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ea180cec-1e77-4700-beed-cde3905bd344
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths: []

requires_verification: false
implementation_scope: governance_only

## Why governance_review and not implementation_proposal

The bridge-compliance-gate (`.claude/hooks/bridge-compliance-gate.py` L744–751) extracts ONE `Work Item:` per implementation proposal via `re.search` — first-match semantics. Phase 1 covers 10 WIs (WI-4316 … WI-4325) across foundation, shim+routing, verification, and governance clusters. Filing as a single implementation proposal would require collapsing 10 WIs into one cited Work Item, which fails the live MemBase WI-project membership check.

The structurally correct shape is: **one governance umbrella** (this proposal) carrying the architecture decision, 5 spec drafts, and 2 protected-file diffs for Codex to GO on, followed by **four child implementation bridges** (one per WI cluster) that execute the source-code work post-umbrella-GO. The umbrella's deliverable is the design-and-governance contract; the children carry per-cluster implementation discipline including individual Work Item bindings.

## Summary

This proposal lands the Phase 1 governance scaffold of PROJECT-GTKB-OLLAMA-INTEGRATION — onboard Ollama as the fourth GT-KB coding harness, identity `D`, registered with an empty role-set and `status=registered` so the dispatch substrate stays unchanged. Scope is set by 12 owner-AUQ decisions (DELIB-20260663) responding to two Loyal Opposition INSIGHTS reports (decision memo recommending Option A + parity gap analysis).

**This umbrella seeks GO on:**
1. The architecture decision: Option A (Python shim, no framework) per AUQ#1.
2. Five new spec drafts (inline below) — `ADR-OLLAMA-HARNESS-ADOPTION-001` + 3 DCLs + `GOV-HARNESS-ONBOARDING-CONTRACT-001`.
3. Two protected-file diffs (inline below) — glossary additions in `.claude/rules/canonical-terminology.md` + §3 update in `.claude/rules/operating-model.md`.
4. The PAUTH already minted: `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE` (v1, rowid 117) — Codex review confirms the envelope is well-scoped.

**This umbrella does NOT directly modify source code.** The 10 implementation WIs (WI-4316 … WI-4325) execute via four child bridges filed AFTER umbrella GO:
- `gtkb-ollama-integration-phase-1-foundation-001` — WI-4316 (identity/registry) + WI-4317 (parity checker) + WI-4318 (capability registry)
- `gtkb-ollama-integration-phase-1-shim-001` — WI-4319 (shim) + WI-4320 (routing.toml) + WI-4321 (author metadata)
- `gtkb-ollama-integration-phase-1-verification-001` — WI-4322 (E2E verify) + WI-4323 (doctor check)
- `gtkb-ollama-integration-phase-1-governance-impl-001` — WI-4324 (5 spec inserts via approval packets) + WI-4325 (2 protected-file edits via narrative approval packets)

Each child proposal cites a single Work Item (or a tightly-coupled WI bundle representable as one impl scope), satisfies the impl-proposal gate, and carries its own preflights.

**Owner-Grilling-Gate (per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`):** Satisfied by the 12-AUQ pass archived as DELIB-20260663 (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`).

**Explicit Phase 1 boundary:** EXCLUDED from Phase 1 — multi-model routing, `.ollama/skills/` adapter generation, dispatch-substrate wiring (cross-harness trigger + single-harness dispatcher route only between B/A/C — D is NOT a dispatch target), role promotion (D stays `registered`), additional models beyond Qwen 2.5 Coder 14B. These are Phase-2+ candidates.

## Specification Links

| Spec | Severity | Trigger | How this umbrella complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as a NEW versioned bridge file with canonical status token; INDEX entry inserted after Write. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section exists with comprehensive citation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | governance_review with `requires_verification: false` — no post-impl verification gate; child impl bridges carry their own spec-derived verification. See §Specification-Derived Verification Plan for the per-child mapping. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/groundtruth_kb/project/** | The verification child bridge will modify `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (in-tree, root-bounded) per WI-4323. All other Phase-1 paths are platform-side. This umbrella scopes that future work; the child bridge re-cites + carries impl evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Every Phase-1 surface is an artifact: identity record, registry row, shim script, routing config, ADR/DCL/GOV rows. Linked deliberation DELIB-20260663 records 12 owner decisions. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | This umbrella ends at GO (governance_review, terminal at GO). Child impl bridges complete at VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:owner decision, specification, ADR, DCL, work item | 12 owner decisions, 10 WIs, 1 new ADR, 3 new DCLs, 1 new GOV — fully artifact-routed. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | Five formal-artifact-approval packets enumerated in the governance-impl child bridge's target_paths; generated after umbrella GO + owner explicit approval per packet. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | blocking | adopt classification of LO advisory | DELIB-20260663 archives the 12-AUQ pass; all 4 gate elements satisfied (see §Prior Deliberations). |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | advisory | adopt/adapt advisory | Per Slice 1+2 advisory-only state; this proposal's Owner Decisions / Input section enumerates AUQ evidence. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/** | Harness D gets durable identity but role-set `[]` (no role assignment); preserves single-ACTIVE-per-role invariant per S378 orthogonality. Executed by foundation child bridge. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | content:harness-registry, role | D's role-set is empty so the durable-vs-session-stated split is N/A; D cannot be a session-stated role target since no role tokens authorize it. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | path:project authorization, content:PAUTH | Cites PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE (status=active, version=1, rowid=117). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cited fields: owner-decision DELIB-20260663, 5 framing specs, 10 WIs, 6 allowed mutations, 5 forbidden operations. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 approved framing specs (LO advisory gate, file-bridge authority, role portability, project-impl-auth, artifact approval). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | advisory | content:cited paths | All cited paths verified via grep against current commit; no cached-snapshot reasoning. |
| `DCL-CONCEPT-ON-CONTACT-001` | blocking | content:new concepts | Three new load-bearing concepts (`ollama`, `routing.toml`, `task-to-model routing`) added to `.claude/rules/canonical-terminology.md` in the governance-impl child. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | 10 Phase-1 WIs already inserted as canonical backlog rows; project membership recorded; PAUTH includes work-item-id list. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | path:scripts/check_harness_parity.py | Foundation child bridge extends KNOWN_HARNESSES; parity-fallback semantic preserved. |

## Requirement Sufficiency

**Existing requirements sufficient.** This proposal does not require new requirement capture; the 12 AUQ owner decisions resolve all material requirement-disambiguation questions. The 5 new specs drafted below are architecture/design/governance artifacts derived from the AUQ decisions, not new requirements.

## Prior Deliberations

- **`DELIB-20260663`** (this turn, S408, `owner_conversation`, `outcome=owner_decision`) — The 12-AUQ grilling pass archived as a deliberation. Records the full Q+A pairs, final scope determination, and Owner-Grilling-Gate satisfaction evidence. THIS PROPOSAL'S DIRECT OWNER-DECISION ANCHOR.
- **LO INSIGHTS report** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md` — peer-solution decision memo recommending Option A; classified `adopt` per `.claude/rules/peer-solution-advisory-loop.md`.
- **LO INSIGHTS report** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md` — LO parity gap analysis enumerating 7 file touchpoints; closed open routing-storage question via AUQ#2.
- **`DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`** — establishes the isolation/lifecycle-independence principle that motivates D-as-registered (no auto-dispatch); applies to Phase 1's "do not wire dispatch substrate" boundary.
- **`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** — confirms role and status are orthogonal axes. D = role-set `[]` + status `registered` is a clean orthogonal cell.
- **`DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`** — permits cross-harness invocation of external harness executables; applies to ollama server at `localhost:11434`.
- **`ADR-CODEX-HOOK-PARITY-FALLBACK-001`** v2 — harness hook-parity verification pattern; foundation child preserves the semantic.
- **`bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-004.md`** VERIFIED — earlier-session role-state-key drift fix; this proposal's doctor extension must avoid reintroducing.

_No prior deliberations: rejected — multiple prior decisions cited above._

## Owner Decisions / Input

The following 12 AskUserQuestion answers, archived as `DELIB-20260663` (`source_type=owner_conversation`, `outcome=owner_decision`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`), authorize the work proposed below.

### Batch 1 — Architecture, Routing, Role, MVP scope

- **AUQ#1 — Architecture:** Option A (Python shim, no framework). _Authorizes:_ `scripts/ollama_harness.py` as a standalone Python script with direct Ollama HTTP/SDK calls; rejects LangChain/LangGraph framework dependencies.
- **AUQ#2 — Routing store:** Static `.ollama/routing.toml`. _Authorizes:_ creating `.ollama/routing.toml` as the routing source-of-truth; rejects MemBase-backed routing for Phase 1.
- **AUQ#3 — Role for D:** `registered`, no active role. _Authorizes:_ `harness-registry.json` row with `role: []` and `status: "registered"`; forbids active-role assignment for D in Phase 1.
- **AUQ#4 — MVP scope:** Identity + registry + shim + ONE model + E2E test. _Authorizes:_ the 10 Phase-1 WIs in scope; defers multi-model routing, skill adapters, dispatch wiring to Phase 2+.

### Batch 2 — Model, Tool subset, Gov depth, PAUTH

- **AUQ#5 — MVP model:** Qwen 2.5 Coder 14B (Q4_K_M). _Authorizes:_ `qwen2.5-coder:14b-instruct-q4_K_M` as the single registered model.
- **AUQ#6 — Tool subset:** Full parity (Read, Write, Edit, Grep, Glob, Bash). _Authorizes:_ shim exposes full GT-KB tool surface; triggers bridge-compliance-gate + scanner-safe-writer + destructive-gate + author-metadata respect in the shim.
- **AUQ#7 — Governance depth:** Heavy (ADR + 3 DCLs + new GOV). _Authorizes:_ 5 new spec inserts with formal-artifact-approval packets.
- **AUQ#8 — PAUTH path:** Issue one project PAUTH covering Phase-1 WIs. _Authorizes:_ PAUTH minted this turn (v1, rowid 117), cited by this proposal.

### Batch 3 — E2E, Doctor, GOV reach, Sub-project

- **AUQ#9 — E2E scope:** Both — round-trip + bridge filing + ruff/pytest sanity. _Authorizes:_ `scripts/verify_ollama_dispatch.py` with 3-phase test.
- **AUQ#10 — Doctor scope:** Reachability + models + registry consistency. _Authorizes:_ doctor `_check_ollama_harness` with 3 sub-checks across 4 stores.
- **AUQ#11 — GOV reach:** Procedural + machine-checkable + capability floor. _Authorizes:_ GOV-HARNESS-ONBOARDING-CONTRACT-001 with assertions + capability minimums.
- **AUQ#12 — Sub-project:** Flat. _Authorizes:_ PROJECT-GTKB-OLLAMA-INTEGRATION as flat project with 10 direct WI memberships.

## Phase 1 WI Roster + Child Bridge Mapping

| WI | Title (short) | Child Bridge | File touchpoints (in child) |
|----|---------------|--------------|------------------------------|
| WI-4316 | Reserve harness ID D (identities + registry) | foundation | `harness-state/harness-identities.json`, `harness-state/harness-registry.json` |
| WI-4317 | Generalize KNOWN_HARNESSES in parity checker | foundation | `scripts/check_harness_parity.py` |
| WI-4318 | `[capabilities.ollama]` block | foundation | `config/agent-control/harness-capability-registry.toml` |
| WI-4319 | `scripts/ollama_harness.py` | shim | `scripts/ollama_harness.py` (new) + `tests/scripts/test_ollama_harness.py` (new) |
| WI-4320 | `.ollama/routing.toml` | shim | `.ollama/routing.toml` (new) |
| WI-4321 | Author-metadata env-var injection | shim | `scripts/ollama_harness.py` (logic block) + unit tests |
| WI-4322 | `scripts/verify_ollama_dispatch.py` E2E | verification | `scripts/verify_ollama_dispatch.py` (new) |
| WI-4323 | Doctor `_check_ollama_harness` | verification | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` + `tests/groundtruth_kb/test_doctor_ollama.py` (new) |
| WI-4324 | Insert 5 specs via formal-artifact-approval packets | governance-impl | `.groundtruth/formal-artifact-approvals/2026-06-04-{5 spec ids}.json` |
| WI-4325 | Update canonical-terminology.md + operating-model.md §3 | governance-impl | `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md` + narrative approval packets |

## Proposed Specification Drafts

### ADR-OLLAMA-HARNESS-ADOPTION-001

**Type:** `architecture_decision`. **Status:** `specified` (at insert); promotes to `implemented` after the four impl child bridges complete at VERIFIED.

**Title:** Adopt Ollama as the fourth GT-KB coding harness via a Python tool-calling shim and static TOML routing.

**Decision:** GroundTruth-KB adopts Ollama as harness identity `D` using a lightweight Python shim (`scripts/ollama_harness.py`) that wraps Ollama's HTTP `api/chat` tool-calling endpoint, with task-to-model routing managed by a static `.ollama/routing.toml` file.

**Context:** Two LO INSIGHTS reports classified `adopt`. Ollama is a model-hosting server; its native CLI does not handle the tool-execution loop. GT-KB requires harness-side tool dispatch to be compatible with bridge-compliance-gate.py, scanner-safe-writer.py, destructive-gate, and author-metadata env-var injection.

**Rejected alternatives:**
- **Option B — LangChain/LangGraph framework.** Massive dep bloat, context overhead. Rejected per AUQ#1.
- **Option C — CLI pass-through with command parsing.** Unreliable tool calling, safety hazard. Rejected per AUQ#1.

**Consequences:**
- **Positive:** Zero framework bloat; direct tool-API alignment; granular env-var injection control; reversible (shim is a standalone script).
- **Negative:** ~150-300 lines of Python tool-loop code to maintain; per-model tool-calling quality varies.
- **Risk mitigation:** Smaller models reserved for read-only checks; complex tasks routed to Qwen 2.5 Coder 14B+.

**Assertions:**
- `scripts/ollama_harness.py` exists and imports no `langchain*`, `langgraph*`, `crewai*`, `autogen*` symbols.
- `.ollama/routing.toml` exists and parses via `tomllib.load`.
- `harness-state/harness-registry.json` contains an entry with `id: "D"`.

---

### DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:** `ADR-OLLAMA-HARNESS-ADOPTION-001`.

**Title:** `.ollama/routing.toml` schema constraint.

**Constraint:** Every `.ollama/routing.toml` MUST conform to:

```
schema_version = 1   # integer, required
[models.<key>]       # at least one models table required
model_id = "<provider:model-tag>"
context_window = <int>
tool_calling_supported = <bool>
allowed_tools = [<tool>, ...]  # subset of ("Read","Write","Edit","Grep","Glob","Bash")
[routing]
default_model = "<models-key>"
[routing.skills]                 # optional in Phase 1
```

**Severity:** blocking. Non-conformant routing.toml MUST fail dispatch-time schema check and doctor advertised-models sub-check.

**Enforcement:** `scripts/ollama_harness.py::_load_routing_config()`; doctor `_check_ollama_harness` re-validates.

**Assertions:**
- Grep: `.ollama/routing.toml` contains `schema_version = 1`.
- Grep: `.ollama/routing.toml` contains `[routing]` and `default_model = `.
- Grep: `.ollama/routing.toml` contains at least one `[models.` table.
- Code-check: `scripts/ollama_harness.py` defines `_load_routing_config` and raises `ValueError` on schema violations.

---

### DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:** `ADR-OLLAMA-HARNESS-ADOPTION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`.

**Title:** Ollama harness MUST inject author-metadata env vars before any Write tool dispatch.

**Constraint:** Inside `scripts/ollama_harness.py`, before invoking any Write tool dispatch on the local model's behalf, the shim MUST set `GTKB_AUTHOR_MODEL=<routed model id>` and `GTKB_AUTHOR_MODEL_VERSION=<model tag suffix>` in the subprocess environment. These env vars are parsed by `scripts/bridge_author_metadata.py` L34 to populate Author/Model lines in any bridge file the local model writes.

**Severity:** blocking. A bridge file without correct author-metadata env vars will fail bridge-compliance-gate.

**Enforcement:** `_dispatch_write_tool` calls `_set_author_metadata()` first; raises `RuntimeError` if values missing.

**Assertions:**
- Code-check: `scripts/ollama_harness.py` defines `_set_author_metadata` and `_dispatch_write_tool`.
- Grep: `scripts/ollama_harness.py` contains `GTKB_AUTHOR_MODEL` and `GTKB_AUTHOR_MODEL_VERSION`.

---

### DCL-OLLAMA-TOOL-PARITY-GATE-001

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:** `ADR-OLLAMA-HARNESS-ADOPTION-001`.

**Title:** Ollama harness exposes canonical full-parity GT-KB tool surface; destructive-gate authority delegated to existing hook.

**Constraint:** `scripts/ollama_harness.py` MUST expose exactly `("Read", "Write", "Edit", "Grep", "Glob", "Bash")`. Routing-config `allowed_tools` MUST be a subset; non-canonical names rejected at load time. Destructive-action gate MUST apply unchanged; shim MUST NOT implement its own destructive-allowlist.

**Severity:** blocking. Non-canonical exposure widens attack surface; shim-side bypass undermines safety control.

**Enforcement:** `CANONICAL_TOOLS = frozenset({...})`; routing validation rejects non-canonical; Bash routes through existing destructive-gate.

**Assertions:**
- Code-check: `scripts/ollama_harness.py` defines `CANONICAL_TOOLS` with the canonical 6-tool set.
- Code-check: `scripts/ollama_harness.py` does NOT define its own destructive-allowlist.
- Grep: `config/agent-control/harness-capability-registry.toml::[capabilities.ollama].advertised_tool_subset` matches canonical.

---

### GOV-HARNESS-ONBOARDING-CONTRACT-001

**Type:** `governance`. **Status:** `specified`.

**Title:** Harness Onboarding Contract — required artifacts, machine-checkable assertions, and capability floor for any new GT-KB coding harness.

**Contract:** Any new AI coding harness (E, F, ...) MUST satisfy three layers:

#### Layer 1 — Required Artifacts (procedural)

1. Entry in `harness-state/harness-identities.json` with unique installation-stable `id`.
2. Row in `harness-state/harness-registry.json` with canonical `role` field (JSON list: `[]`, `["prime-builder"]`, `["loyal-opposition"]`, or both) and `status` field (`active`, `registered`, `suspended`).
3. Entry in `scripts/check_harness_parity.py::KNOWN_HARNESSES`.
4. `[capabilities.<harness>]` block in `config/agent-control/harness-capability-registry.toml`.
5. Glossary entry in `.claude/rules/canonical-terminology.md` per `DCL-CONCEPT-ON-CONTACT-001`.
6. Entry in `.claude/rules/operating-model.md::§3` (implemented or intended).
7. An ADR (e.g., `ADR-<HARNESS>-HARNESS-ADOPTION-NNN`).
8. Doctor `_check_<harness>_harness` function in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

#### Layer 2 — Machine-Checkable Assertions

For each `<harness>` in `harness-identities.json`: (1) registry row with matching `id`, (2) KNOWN_HARNESSES entry, (3) capability block in registry TOML, (4) glossary entry (case-insensitive), (5) doctor check function.

#### Layer 3 — Capability Floor

Each `[capabilities.<harness>]` MUST declare:

1. `bridge_compliance_gate_respect = true`
2. `root_boundary_respect = true`
3. `author_metadata_env_var_setting = true`
4. `destructive_gate_delegation = true`
5. `advertised_tool_subset` subset of `("Read","Write","Edit","Grep","Glob","Bash")`

**Severity:** Layer 1 procedural-only; Layer 2 blocking; Layer 3 blocking.

**Related:** `ADR-OLLAMA-HARNESS-ADOPTION-001` (first concrete adoption), `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

## Proposed Protected-File Edits

### `.claude/rules/canonical-terminology.md` — add 3 glossary entries

```
### ollama
**Definition:** The fourth GT-KB coding harness (identity `D`), adopted in Phase 1 of `PROJECT-GTKB-OLLAMA-INTEGRATION`. Locally hosts open-weight models via the Ollama platform CLI/server at `http://localhost:11434`. Integrated through `scripts/ollama_harness.py` and `.ollama/routing.toml`. Phase-1 state: `registered` with empty role-set.
**Canonical alias:** ollama harness.
**Not to be confused with:** the upstream Ollama platform CLI; Ollama Python SDK.
**Source:** `ADR-OLLAMA-HARNESS-ADOPTION-001`; `DELIB-20260663`; bridge/gtkb-ollama-integration-phase-1-001.md.
**Implementation pointer:** scripts/ollama_harness.py; .ollama/routing.toml; harness-state/harness-identities.json::ollama; doctor `_check_ollama_harness`.

### routing.toml
**Definition:** Static TOML routing config at `.ollama/routing.toml`. Maps Ollama-served local models to dispatch contexts. Schema per `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`.
**Not to be confused with:** Ollama server's own model cache; bridge dispatch state.
**Source:** `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`; AUQ#2.
**Implementation pointer:** .ollama/routing.toml; scripts/ollama_harness.py::_load_routing_config.

### task-to-model routing
**Definition:** GT-KB pattern binding skill contexts to models within a single harness's model pool. Implemented via `.ollama/routing.toml::[routing.skills.<skill>]` overriding default_model.
**Not to be confused with:** cross-harness dispatch (cross_harness_bridge_trigger); destructive-action routing.
**Source:** `ADR-OLLAMA-HARNESS-ADOPTION-001`; AUQ#2.
**Implementation pointer:** .ollama/routing.toml::[routing]; scripts/ollama_harness.py::_resolve_model_for_context.
```

### `.claude/rules/operating-model.md` §3 — add to implemented-but-partial

```
- Ollama harness (identity D, registered/no-active-role) per `ADR-OLLAMA-HARNESS-ADOPTION-001`; single-model Phase-1 (Qwen 2.5 Coder 14B); full-parity tool surface; static .ollama/routing.toml routing; doctor `_check_ollama_harness`.
```

Add to intended-but-partial:

```
- Ollama harness Phase 2+ — multi-model routing, .ollama/skills/ adapter generation, dispatch-substrate wiring, role promotion. Tracked under PROJECT-GTKB-OLLAMA-INTEGRATION Phase 2+.
```

## Child Bridges Filed After Umbrella GO

### Child 1 — `gtkb-ollama-integration-phase-1-foundation-001`

- **bridge_kind:** `implementation_proposal` | **Primary WI:** WI-4316 | **Bundled:** WI-4317, WI-4318
- **target_paths:** `harness-state/harness-identities.json`, `harness-state/harness-registry.json`, `scripts/check_harness_parity.py`, `config/agent-control/harness-capability-registry.toml`
- **Verification:** `gt harness list` shows D; doctor `_check_role_set_topology_consistency` PASS
- **Commit type:** `feat:`

### Child 2 — `gtkb-ollama-integration-phase-1-shim-001`

- **bridge_kind:** `implementation_proposal` | **Primary WI:** WI-4319 | **Bundled:** WI-4320, WI-4321
- **target_paths:** `scripts/ollama_harness.py`, `.ollama/routing.toml`, `tests/scripts/test_ollama_harness.py`
- **Verification:** Unit tests PASS; `ruff check` + `ruff format --check` PASS
- **Commit type:** `feat:`

### Child 3 — `gtkb-ollama-integration-phase-1-verification-001`

- **bridge_kind:** `implementation_proposal` | **Primary WI:** WI-4322 | **Bundled:** WI-4323
- **target_paths:** `scripts/verify_ollama_dispatch.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `tests/groundtruth_kb/test_doctor_ollama.py`
- **Verification:** E2E 3-phase test PASSes when ollama server up
- **Commit type:** `feat:`

### Child 4 — `gtkb-ollama-integration-phase-1-governance-impl-001`

- **bridge_kind:** `implementation_proposal` | **Primary WI:** WI-4324 | **Bundled:** WI-4325
- **target_paths:** 5 formal-artifact-approval packets + 2 narrative-artifact-approval packets + `.claude/rules/canonical-terminology.md` + `.claude/rules/operating-model.md`
- **Verification:** All 5 specs exist; canonical-terminology doctor PASS; Layer-2 assertions PASS for ollama
- **Commit type:** `feat:`

**Recommended Child Ordering:** foundation → shim → verification → governance-impl.

## Specification-Derived Verification Plan (for this Umbrella)

This umbrella's deliverable is the design + governance contract; it does NOT carry executable verification. Children carry their own spec-derived verification.

| Source | Verification | PASS criterion |
|--------|--------------|---------------|
| ADR + 3 DCLs + 1 GOV drafts | Codex review for internal consistency, contract clarity | Codex GO with no NO-GO findings |
| Protected-file diffs | Codex review of glossary + §3 edits | Codex GO with no NO-GO findings |
| PAUTH | PAUTH envelope review | Codex confirms scope appropriate |
| Per-cluster impl | Each child's §Spec-Derived Verification Plan | Cross-reference |

## Risk / Rollback

### Risks (umbrella-scope)

1. **Codex NO-GO on spec drafts.** Most likely on GOV-HARNESS-ONBOARDING-CONTRACT-001 (largest surface). _Mitigation:_ revise; refile REVISED -003.
2. **Codex NO-GO on glossary diffs.** Possible if placement wrong. _Mitigation:_ revise diff blocks.
3. **PAUTH scope too broad.** Codex could request narrower scope. _Mitigation:_ revoke v1 + reissue v2.

### Risks (cascade to children)

4. **Child preflight missing-specs.** Each child cites the 5 new specs; before governance-impl lands, preflight reports missing. _Mitigation:_ children cite specs as `(to be inserted in this Phase 1)`; preflight relaxes for same-project in-flight specs.
5. **Inter-child dependencies.** Foundation must land before shim; shim before verification. _Mitigation:_ documented ordering.

### Rollback

If umbrella NO-GO'd: empty target_paths means nothing to revert; file REVISED -003.

If a child later NO-GO'd: per-child revert; re-file REVISED child.

If Phase 1 wrong-direction strategic choice: revert all four children; revert operating-model §3; retire ADR with `supersedes_reason`; revoke PAUTH.

## Applicability Preflight

(To be appended after `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1`.)

## Clause Applicability

(To be appended after `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1`.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
