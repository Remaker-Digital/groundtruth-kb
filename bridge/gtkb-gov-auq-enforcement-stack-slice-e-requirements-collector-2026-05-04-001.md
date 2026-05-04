NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice E: Requirements-Collection Hook Implementation

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)
**Prior sub-slices VERIFIED:** A (`-014`), A-followup code-fence-guards (`-008`), B (`-006`), C (`-006`), D (`-008`).

## Goal

Promote `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` and `GOV-REQUIREMENTS-COLLECTION-HOOK-001` from `specified` → `implemented` by:

1. Implementing `.claude/hooks/requirements-collector.py` per the DCL binding contract (canonical path; LLM classifier via `claude-haiku-4-5-20251001`; 4-label classification; retrieval-augmented options; output schema compliant; token-budget + timeout enforcement).
2. Registering the hook as `UserPromptSubmit` in `.claude/settings.json` (alongside existing `owner-decision-tracker.py --mode user-prompt-submit`).
3. Codex parity registration in `.codex/hooks.json`.
4. Creating `IPR-REQUIREMENTS-COLLECTION-HOOK-001` document in MemBase via formal-artifact-approval gate (per `GOV-20`).
5. Test suite at `tests/scripts/test_requirements_collection_hook.py` covering DCL TEST COVERAGE binding items (a)-(e).
6. `gt project doctor` invariants per DCL DOCTOR INVARIANTS section.

## Specification Links

**Blocking (per applicability registry + sub-slice scope):**

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified) — the GOV requirement being implemented.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) — the binding implementation contract.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation path for chat-derived spec promotion.
- `GOV-OWNER-DECISION-SURFACING-001` — predecessor surfacing infrastructure.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate for IPR creation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.codex/hooks.json` registration intent (forward-compatible while Codex hooks remain disabled on Windows).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** changes confined to `E:\GT-KB\.claude\hooks\`, `E:\GT-KB\.claude\settings.json`, `E:\GT-KB\.codex\hooks.json`, `E:\GT-KB\tests\scripts\` (or `E:\GT-KB\groundtruth-kb\tests\` per current GT-KB framework path), `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\doctor\` (doctor invariants), and MemBase via `groundtruth_kb.db.KnowledgeDB`. No `applications/` content.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/operating-model.md`, `.claude/rules/project-root-boundary.md`.

**Topic-specific:**

- Umbrella scope at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice E" lines 186-190.
- Predecessor hook at `.claude/hooks/spec-classifier.py` (regex-based; superseded by canonical `requirements-collector.py` per DCL binding LOCATION).
- Related hooks: `.claude/hooks/owner-decision-tracker.py` (Stop + UserPromptSubmit; existing peer at the same UserPromptSubmit event slot).

**Advisory:** `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S331-AUQ-1/2/3` (umbrella authorization).
- `DELIB-S332-CONTINUE-WITH-SUBSLICE-E` (this turn): Owner AUQ S332 selected "Continue with Sub-slice E now" from a 3-option `AskUserQuestion` (alternatives: stop/checkpoint, commit-first). `detected_via: ask_user_question`. Authorizes filing this NEW under autonomous-progression.
- No prior NO-GO on this design (first NEW for this sub-slice).

## Owner Decisions / Input

- **AUQ S332 #3 (this turn):** Owner selected "Continue with Sub-slice E now" authorizing filing this proposal under autonomous-progression. `detected_via: ask_user_question`.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice work.
- **Pending owner inputs identified during scoping:**
  1. Anthropic API key availability for live LLM classifier integration (verified absent in current shell env). Hook must implement graceful degradation per DCL §"CLASSIFIER MODEL BOUNDS" (timeout fallback to `chat` with confidence 0.0). Live integration test gated on `ANTHROPIC_API_KEY` env var being set; pure-Python tests via mocked client cover the binding contract.
  2. Hook latency cost: every `UserPromptSubmit` becomes up to 15s blocking (5s LLM + 10s retrievals). DCL contract authorizes this; flagging for owner awareness as a Risk item (acceptable per the contract; not a decision blocker).

No additional owner decisions required pre-implementation. Codex GO/NO-GO governs proceed.

## Implementation Plan

### Step 1: New hook at `.claude/hooks/requirements-collector.py`

**Architecture:**

- `main()` reads stdin JSON per Claude Code `UserPromptSubmit` schema; exits 0 always (errors → stderr; never block owner).
- Three-stage pipeline:
  1. **Classifier** (`_classify(prompt) → ClassificationResult`): invokes Anthropic Messages API with Haiku-class model + budgeted prompt; returns one of `{requirement_candidate, clarification, decision, chat}`. Token budget enforced (≤ 500 input + ≤ 100 output). 5s wall-clock timeout. On timeout/API-error/missing-key: returns `chat` with confidence 0.0 + warning string for additionalContext.
  2. **Retrieval** (`_retrieve(prompt) → RetrievalCandidates`): three sources — (a) `KnowledgeDB.search_deliberations(query=prompt)` for DA; (b) read last `GTKB_REQUIREMENTS_HOOK_CHAT_TURN_LIMIT` (default 50) turns from `transcript_path`; (c) scan `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` for LO advisory. Total 10s wall-clock timeout. Partial results emitted with warning on timeout. Skipped entirely when classification != `requirement_candidate`.
  3. **Output renderer** (`_render(classification, retrieval) → str`): produces `additionalContext` markdown block per DCL ADDITIONAL_CONTEXT SCHEMA — sections "## Requirements Collection Hook — Classification", "## Owner statement (verbatim)", "## Required agent behavior" (when requirement_candidate), "## Retrieval candidates" (when requirement_candidate).
- Cost tracking: per-session counter persisted to `.gtkb-state/requirements-hook/cost.json` (path under platform root); surfaced in additionalContext footer.

**Files Modified/Added:**

- ADDED: `.claude/hooks/requirements-collector.py` (~500-700 LOC).
- ADDED: `.claude/hooks/_requirements_hook_lib.py` (helper module — classifier, retrieval, schema rendering — split out for unit-testability without subprocess).
- MODIFIED: `.claude/settings.json` — add second `UserPromptSubmit` hook registration after existing `owner-decision-tracker` entry; timeout: 20 (5s classifier + 10s retrieval + 5s slack).
- MODIFIED: `.codex/hooks.json` — Codex parity registration (forward-compatible per ADR-CODEX-HOOK-PARITY-FALLBACK-001).

### Step 2: Test module at `groundtruth-kb/tests/test_requirements_collection_hook.py`

(Per DCL TEST COVERAGE; using current GT-KB framework path until path migration per parent DCL note.)

Test cases mapping to DCL TEST COVERAGE (a)-(e):

| DCL Test | Test Names | Coverage |
|---|---|---|
| (a) classifier returns valid label | `test_classifier_imperative`, `test_classifier_descriptive`, `test_classifier_structural`, `test_classifier_comparative`, `test_classifier_inferred`, `test_classifier_chat_baseline` | 6 fixtures × mocked LLM client returning labeled output; assert classification matches expected |
| (a-fallback) | `test_classifier_timeout_fallback_to_chat`, `test_classifier_missing_api_key_fallback`, `test_classifier_api_error_fallback` | 3 fallback paths; assert classification == "chat", confidence == 0.0, warning emitted |
| (b) retrieval queries each of 3 sources | `test_retrieval_calls_search_deliberations`, `test_retrieval_reads_transcript_chat_turns`, `test_retrieval_scans_lo_insights_dir` | 3 fixture-isolated tests; mocked `KnowledgeDB`, `tmp_path` transcript, `tmp_path` LO INSIGHTS dir; assert each source queried |
| (c) escape-hatch | `test_escape_hatch_unambiguous_requirement_skips_3option_path` | classification confidence ≥ threshold + structural-match heuristic; assert "single proposed interpretation" mode in output |
| (d) output schema validation | `test_output_schema_classification_section_present`, `test_output_schema_owner_statement_blockquoted`, `test_output_schema_agent_behavior_when_requirement`, `test_output_schema_retrieval_candidates_when_requirement`, `test_output_schema_no_extra_fields` | 5 schema-compliance tests; parse rendered output and assert each binding section |
| (e) cost cap + timeout enforced | `test_cost_cap_per_session_tracked`, `test_input_token_budget_enforced`, `test_output_token_budget_enforced`, `test_total_retrieval_timeout_enforced` | 4 limit-enforcement tests |
| Integration | `test_hook_subprocess_smoke_with_mocked_classifier` | end-to-end hook invocation via subprocess; mocked-classifier env; verify exit 0, valid stdout JSON, no live-file mutation |
| Hook registration | `test_hook_registered_in_claude_settings`, `test_hook_registered_in_codex_hooks_json` | static config assertions |

### Step 3: IPR document creation

Create `IPR-REQUIREMENTS-COLLECTION-HOOK-001` in MemBase via the formal-artifact-approval gate. Document references:

- WI(s) implemented (this sub-slice's bridge thread)
- ADR/DCL refs: `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`, `GOV-REQUIREMENTS-COLLECTION-HOOK-001`
- Implementation evidence: hook + test paths, post-impl REPORT bridge ID
- Compliance proof: per DCL DOCTOR INVARIANTS (a)-(d) — automatable evidence

### Step 4: `gt project doctor` invariants

Add 4 doctor checks per DCL DOCTOR INVARIANTS:

- `_check_requirements_hook_canonical_path` — verifies `.claude/hooks/requirements-collector.py` exists.
- `_check_requirements_hook_settings_registered` — verifies UserPromptSubmit registration in `.claude/settings.json`.
- `_check_requirements_hook_model_in_allowlist` — verifies the model identifier in the hook source is on the approved-model allowlist (currently `{claude-haiku-4-5-20251001}`).
- `_check_requirements_hook_test_exists` — verifies test file at canonical path.

### Step 5: Promote specs in MemBase

After Codex VERIFIED on the post-impl REPORT:

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001`: specified → implemented → verified
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`: specified → implemented → verified

### Step 6: Predecessor disposition

`.claude/hooks/spec-classifier.py` (regex-based predecessor) is **NOT removed in this slice**. Per the operating-model "Specify on contact" principle, removing it requires a separate owner-approved decision. This slice supersedes its function via the canonical `requirements-collector.py`; both can coexist briefly (both fire on UserPromptSubmit; the new hook adds richer additionalContext while the old hook continues emitting its systemMessage reminder). A follow-up bridge can deprecate `spec-classifier.py` once `requirements-collector.py` has empirical performance evidence.

## Spec-to-Test Mapping

| Spec | Test |
|---|---|
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` LOCATION | `test_hook_canonical_path_exists`, `test_hook_registered_in_claude_settings`, `test_hook_registered_in_codex_hooks_json` |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` I/O SCHEMA | `test_hook_subprocess_smoke_with_mocked_classifier`, schema-validation tests |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` ADDITIONAL_CONTEXT SCHEMA | 5 schema tests |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` CLASSIFIER MODEL BOUNDS | classifier-fallback tests + budget-enforcement tests |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` RETRIEVAL INTERFACE | retrieval-source tests |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` TEST COVERAGE (a)-(e) | covered explicitly per the table above |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` DOCTOR INVARIANTS | 4 new doctor checks + integration test running `gt project doctor` |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` classification 4-label | `test_classifier_*` set |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` requirement_candidate path | `test_escape_hatch_*`, schema test for "Required agent behavior" section |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | covered indirectly via the surfacing flow in additionalContext rendering |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- applications/` empty assertion |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `T-bridge-1` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `T-spec-1` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT spec-to-test mapping |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this NEW
- [ ] Preflight passes (`missing_required_specs: []`)

Post-implementation (VERIFIED contingent):
- [ ] All ~24 tests in the test module PASS (or skip with reason for `ANTHROPIC_API_KEY`-gated integration test)
- [ ] `gt project doctor` reports the 4 new checks PASS
- [ ] `IPR-REQUIREMENTS-COLLECTION-HOOK-001` document created in MemBase via formal-artifact-approval gate
- [ ] `GOV-REQUIREMENTS-COLLECTION-HOOK-001` and `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` promoted from specified → implemented → verified
- [ ] Live `UserPromptSubmit` smoke test (next session): hook fires, emits valid additionalContext, no exception in stderr; budget + timeout enforced
- [ ] No regression in existing `owner-decision-tracker.py` UserPromptSubmit behavior (peer hook continues firing)
- [ ] No `applications/` content modified
- [ ] Predecessor `.claude/hooks/spec-classifier.py` left in place (separate deprecation bridge if/when desired)

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| LLM API unavailable / API key missing | High (current env) | Medium | Graceful fallback per DCL: classification = "chat", confidence = 0.0, warning in additionalContext. Tests cover this path. |
| Hook latency cost (up to 15s per owner prompt) | Certain | Medium | DCL contract authorizes the trade-off. Cost cap surfaced in additionalContext for owner visibility. Owner aware via this proposal's Owner Decisions section item 2. |
| LLM cost per classification | Certain | Low | Token budget enforced (≤ 500 input + ≤ 100 output). Per-session cost tracking with cap. Haiku-class is the cheapest option. |
| Mocked-LLM test brittleness vs real LLM behavior drift | Medium | Medium | DCL TEST COVERAGE (a) is intentionally pattern-coverage rather than accuracy-coverage; mocked tests verify the hook's *handling* of classifier output, not the LLM's *correctness*. Live integration test (skipif api-key absent) provides smoke coverage when key is present. |
| Hook causes UserPromptSubmit failure that blocks owner input | Low (always exit 0 + stderr-only errors) | High if regression | Subprocess smoke test exercises end-to-end + asserts exit 0 + valid stdout. Hook script's `main()` wraps all logic in try/except → fall back to empty additionalContext. |
| ChromaDB query latency in retrieval | Medium | Low | 10s total retrieval timeout; partial results emitted with warning. |

**Rollback:** Revert the single bridge commit. Restores all 4 modified/added paths. Test module + IPR document deletion are clean (no live-file mutations to roll back; cost.json is regenerable). Settings.json + .codex/hooks.json registration removal restores the prior single-hook UserPromptSubmit chain.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
python -m pytest groundtruth-kb/tests/test_requirements_collection_hook.py -v --timeout=60
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook or doctor or requirements" --timeout=120
python -m groundtruth_kb.doctor 2>&1 | grep -E "requirements_hook"
git diff --name-only -- applications/
git status --short
```

Expected: PASS / ~24 passed (1-3 skipped if no API key) / pre-existing-known-failure-only / 4 PASS lines / empty / new files only.

## Out of Scope

- Removal of predecessor `.claude/hooks/spec-classifier.py` — separate deprecation bridge.
- Sub-slice F (release metrics + gate promotion) — separate bridge after E VERIFIED.
- ISOLATION-018 sub-slices 18.C-18.L — gated by Sub-slice F per umbrella.
- Pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` failure — separate housekeeping bridge.
- Adopter-side migration of `tests/scripts/` path per current GT-KB framework path note in DCL — out of scope; tests land at current `groundtruth-kb/tests/` path until the framework migration completes (separate work item).

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/.claude/hooks/requirements-collector.py` (new)
- `E:/GT-KB/.claude/hooks/_requirements_hook_lib.py` (new)
- `E:/GT-KB/.claude/settings.json` (modified)
- `E:/GT-KB/.codex/hooks.json` (modified)
- `E:/GT-KB/groundtruth-kb/tests/test_requirements_collection_hook.py` (new)
- `E:/GT-KB/groundtruth-kb/src/groundtruth_kb/doctor/` (modified — 4 new check functions)
- MemBase `groundtruth.db` (IPR insertion + 2 spec promotions via the formal-artifact-approval gate)

No `applications/` content modified.
