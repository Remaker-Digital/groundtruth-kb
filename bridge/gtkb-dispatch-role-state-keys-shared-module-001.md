NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Pull dispatch role-state keys + agent-recipient mapping into one shared module

bridge_kind: prime_proposal
Document: gtkb-dispatch-role-state-keys-shared-module
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4315

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The canonical bridge-dispatch role-state constants are duplicated across dispatch-related source instead of living in one shared module. `scripts/cross_harness_bridge_trigger.py:394` declares `ROLE_STATE_KEYS = ("prime-builder", "loyal-opposition")`, while `groundtruth-kb/src/groundtruth_kb/project/doctor.py:3661` independently declares the agent-name-to-role dispatch mapping `_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime-builder", "codex": "loyal-opposition"}` and re-uses the same canonical role tokens as standalone literals elsewhere in the module (`frozenset({"prime-builder", "loyal-opposition"})` at `doctor.py:4465` and `:4671`). Because the values are duplicated rather than imported, the dispatch trigger, the doctor checks, and the dispatch-liveness test can drift apart silently. This is a hygiene defect: a single canonical fact (which role labels exist, and how agent names map to them) is encoded in multiple places with no shared source of truth.

## Requirement Sufficiency

Existing requirements sufficient. This is a no-behavior-change refactor that consolidates duplicated string-literal constants into one module and re-exports them so all call sites resolve to the same object. No new or revised requirement/specification is introduced; the governing specs (`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`) already establish that durable artifacts and canonical facts should have a single authoritative source. The fix preserves every observable behavior (dispatch routing, doctor verdicts) and is verified by re-using the existing parity test plus a focused single-ownership test.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: the new module `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` (created under the existing in-root `groundtruth_kb.bridge` package), `scripts/cross_harness_bridge_trigger.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, and `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`. No path resolves outside `E:\GT-KB`, and no application/adopter surface is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the constants being consolidated (`ROLE_STATE_KEYS`, `BRIDGE_AGENT_TO_RECIPIENT`) define the role labels and agent->role mapping the dispatch trigger and doctor liveness checks use to route bridge work; a single canonical source protects the bridge-dispatch authority from silent key drift.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - a canonical fact (which roles exist, how agents map to them) should have one durable, authoritative home rather than being re-encoded as scattered literals; this refactor makes the dispatch role-state an explicit shared artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from a cited spec clause, including the single-ownership/re-export-identity assertion (mandatory spec-to-test mapping).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory project linkage).
- `SPEC-AUQ-POLICY-ENGINE-001` - not directly implicated: this refactor introduces no owner-decision policy surface and no AUQ routing change; the role labels it consolidates are the same tokens AUQ-keyed routing already consumes, so consolidation preserves (does not alter) any policy-engine dependence on those labels.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the new module and all edits are confined to the GT-KB platform (`groundtruth-kb/src/groundtruth_kb/bridge/`, `scripts/`, platform tests); no application/adopter placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4315 is a standing-backlog work item (P3, origin hygiene) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - tangential: the agent->role mapping includes `codex -> loyal-opposition`, but this refactor does not change Codex hook parity behavior or the dispatch substrate; it only relocates the literal so doctor/trigger/test agree on the same Codex role label.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the dispatch role-state becomes a first-class, importable artifact with one owner, rather than a value inferred independently at each call site.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the duplicated dispatch constants triggers consolidation into a controlled shared surface, aligning with the specify/centralize-on-contact lifecycle trigger for previously-uncontrolled duplicated facts.

## Prior Deliberations

- `DELIB-20264042` - Loyal Opposition Review - Doctor `_check_bridge_dispatch_liveness` recipient-key fix (GO). Directly relevant: this is the WI-4307 fix that corrected stale `_BRIDGE_AGENT_TO_RECIPIENT` keys after they drifted from the trigger's canonical labels — the exact drift class this consolidation prevents structurally.
- `DELIB-20264041` - Loyal Opposition Verification - Doctor `_check_bridge_dispatch_liveness` recipient-key fix. The verification companion of the WI-4307 incident; confirms the parity test (`test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels`, TP8) that this proposal extends with a single-ownership assertion.
- `DELIB-1515` - Loyal Opposition Review - Canonical Init-Keyword Syntax. Relevant context: established `prime-builder`/`loyal-opposition` (and the `pb`/`lo` keyword pair) as the canonical role tokens that the consolidated `ROLE_STATE_KEYS` must reflect.
- `DELIB-20263880` - Loyal Opposition Review - Canonical Init-Keyword Syntax. Same canonical-role-token lineage; reinforces that the shared module's tuple must remain the two durable role labels with no legacy aliases.

## Owner Decisions / Input

- `DELIB-20265457` - owner decision (AUQ, 2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-4315 is an in-scope open work item of that batch, so authoring this NEW proposal is owner-authorized.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the project-scoped authorization envelope for the non-fast-lane batch; it covers WI-4315 through active project membership (origin=hygiene refactor confined to platform source + a platform test), satisfying the implementation-authorization evidence for the bounded scope below. No additional owner approval is required for this proposal beyond the batch authorization.

## Proposed Scope

Minimal, no-behavior-change consolidation:

1. Create `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` as the single owner of the dispatch role-state constants:
   - `ROLE_STATE_KEYS: tuple[str, str] = ("prime-builder", "loyal-opposition")` — the canonical durable role-label tuple.
   - `BRIDGE_AGENT_TO_RECIPIENT: dict[str, str] = {"claude": "prime-builder", "codex": "loyal-opposition"}` — the agent-name -> role-label dispatch mapping.
   - Keep the module dependency-free (string literals + simple types only) so both `scripts/` and `groundtruth_kb/project/` can import it without import cycles.
2. In `scripts/cross_harness_bridge_trigger.py`, replace the local literal at `:394` with a re-export: `from groundtruth_kb.bridge.role_state import ROLE_STATE_KEYS`. Preserve the module-level name `ROLE_STATE_KEYS` so the existing test access `cross_harness_bridge_trigger.ROLE_STATE_KEYS` (TP8) and the internal use at `:455` continue to resolve unchanged. (The trigger already inserts `scripts/`-relative paths and resolves `groundtruth_kb`; if it does not currently import `groundtruth_kb`, add the minimal import-path guard consistent with the module's existing pattern.)
3. In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, import the mapping from the shared module and bind the existing private name to it so no other call site changes: `from groundtruth_kb.bridge.role_state import BRIDGE_AGENT_TO_RECIPIENT as _BRIDGE_AGENT_TO_RECIPIENT` (replacing the literal at `:3661`). The standalone canonical-role frozensets at `doctor.py:4465` and `:4671` are constructed from the same tokens; rebuild them from `ROLE_STATE_KEYS` where doing so is a pure substitution that does not alter membership (the `:4671` set additionally includes the READ-only legacy `acting-prime-builder` token, which is preserved by union with `ROLE_STATE_KEYS`, not removed).
4. In `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`, keep the existing parity test (TP8) and add a single-ownership/re-export-identity test asserting that the trigger's `ROLE_STATE_KEYS` and the doctor's `_BRIDGE_AGENT_TO_RECIPIENT` resolve to the shared-module objects (identity, not just equality), and that no duplicate string-literal definition of the role tuple or agent-recipient mapping remains in the dispatch trigger or doctor source (grep-style source assertion over the two source files).

Out of scope: changing dispatch routing behavior, the freshness thresholds, the doctor check severities, or the legacy-key migration (`LEGACY_TO_NEW_STATE_KEY`) — those remain untouched. This is a structural consolidation only.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (canonical role labels / agent->role mapping must be consistent across dispatch surfaces) | `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` (existing TP8, retained) | `set(cross_harness_bridge_trigger.ROLE_STATE_KEYS) == set(_BRIDGE_AGENT_TO_RECIPIENT.values())`, and `"prime"`/`"codex"` legacy labels are absent. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (one authoritative owner of the canonical fact) | `test_role_state_constants_have_single_shared_owner` (new) | `cross_harness_bridge_trigger.ROLE_STATE_KEYS is groundtruth_kb.bridge.role_state.ROLE_STATE_KEYS` and `doctor._BRIDGE_AGENT_TO_RECIPIENT is groundtruth_kb.bridge.role_state.BRIDGE_AGENT_TO_RECIPIENT` (identity, not just equality). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (no residual duplicated literals after centralization) | `test_no_duplicate_role_state_literals_in_dispatch_sources` (new) | Reading `scripts/cross_harness_bridge_trigger.py` and `groundtruth-kb/src/groundtruth_kb/project/doctor.py` source, the standalone literal definitions `("prime-builder", "loyal-opposition")` and `{"claude": "prime-builder", "codex": "loyal-opposition"}` appear zero times (each surface imports from the shared module instead). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (behavior preserved by the refactor) | full `test_doctor_bridge_dispatch_liveness.py` suite (regression) | All pre-existing dispatch-liveness checks (claude/codex OK/WARN/ALARM/absent/unparseable) still pass unchanged, proving the consolidation is behavior-neutral. |

Execution commands:
- `python -m pytest groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/role_state.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/role_state.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`

## Acceptance Criteria

1. `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` exists and is the sole definition site of both `ROLE_STATE_KEYS` and `BRIDGE_AGENT_TO_RECIPIENT`.
2. `scripts/cross_harness_bridge_trigger.py` and `groundtruth-kb/src/groundtruth_kb/project/doctor.py` import these constants from the shared module; grep finds zero standalone string-literal definitions of the role-label tuple `("prime-builder", "loyal-opposition")` or the agent-recipient mapping `{"claude": "prime-builder", "codex": "loyal-opposition"}` in dispatch-related source.
3. The legacy READ-only `acting-prime-builder` token at `doctor.py:4671` is preserved (consolidation must not drop it).
4. The existing parity test (TP8) plus the new single-ownership and no-duplicate-literal tests pass; the full `test_doctor_bridge_dispatch_liveness.py` suite passes (no behavior regression).
5. `ruff check` and `ruff format --check` are clean on all four changed files.

## Risks / Rollback

- Risk: introducing an import cycle (`groundtruth_kb.project.doctor` <-> `groundtruth_kb.bridge.role_state`, or the `scripts/` trigger importing `groundtruth_kb`). Mitigation: the new module is dependency-free (constants only) and lives under the existing `groundtruth_kb.bridge` package that is already imported elsewhere; verified by the test suite importing all three surfaces together.
- Risk: the `scripts/` trigger may not currently resolve `groundtruth_kb` on its import path in every invocation context. Mitigation: reuse the module's existing import-path/sys.path pattern; the TP8 test already imports both `cross_harness_bridge_trigger` and `groundtruth_kb.project.doctor` from the same process, demonstrating the path is resolvable in the test harness; any runtime guard added is minimal and matches existing convention.
- Risk: accidentally narrowing the `:4671` frozenset by rebuilding it from `ROLE_STATE_KEYS` and forgetting `acting-prime-builder`. Mitigation: acceptance criterion 3 + an explicit membership assertion in the regression-covered path.
- Rollback: revert the four files; the new module is additive and the edits are pure import substitutions, so reverting restores the exact prior literals with no migration or state change.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` (new shared module)
- `scripts/cross_harness_bridge_trigger.py` (re-export from shared module)
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (import from shared module)
- `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py` (single-ownership / re-export-identity test)

## Recommended Commit Type

`refactor`

Per `.claude/rules/file-bridge-protocol.md` § "Conventional Commits Type Discipline", the type must match the diff stat. This change is a behavior-neutral consolidation of duplicated constants into one module with import re-exports — `refactor:` ("restructuring without behavior change") is the accurate type. It is not `fix:` (no broken runtime behavior is being repaired; the WI is origin=hygiene, and the prior WI-4307 key-drift defect was already fixed by `DELIB-20264042`), nor `feat:` (no new capability surface is added).
