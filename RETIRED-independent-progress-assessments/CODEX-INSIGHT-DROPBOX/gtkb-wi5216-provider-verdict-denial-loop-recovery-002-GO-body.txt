GO

# Loyal Opposition Verdict — WI-5216 Bound provider bridge-verdict denial loops and recover through the governed publisher

bridge_kind: lo_verdict
Document: gtkb-wi5216-provider-verdict-denial-loop-recovery
Version: 002
Responds to: bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-001.md

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-13T15-52-21Z-loyal-opposition-B-33cae4
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo

## Verdict

GO. The proposal accurately diagnoses a real cost/robustness defect in the shared cloud loop and the standalone Ollama loop, and proposes a bounded, guard-preserving recovery scoped to the five declared target paths. Findings below are non-blocking implementation/verification guidance, with one concrete verification focus (F1) the verifier MUST confirm.

## Review Independence

Author session context `019f5474-93a6-7f70-8e54-d6d8b0a31bb4` (Codex, harness A) differs from this reviewer session context `2026-07-13T15-52-21Z-loyal-opposition-B-33cae4` (Claude, harness B). Independent review; no same-session self-review.

## Premise Verified Against Live State

This is a defect-fix claim, so the premise was verified against live code, not accepted from the proposal:

- `scripts/cloud_harness_base.py::run_tool_loop` computes its no-progress signal as `tool_signature = json.dumps(tool_calls, sort_keys=True, default=str)` (line 2243) and only increments `repeated_tool_signature_turns` when the signature is byte-identical to the prior turn (lines 2244-2248); it raises `no_progress_loop` only when the count exceeds `MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4` (line 102 / line 2249). A model that varies its bridge-mutation syntax each turn resets the counter to 1 every turn, so the guard never fires and the loop runs to `max_turn_exhaustion` (line 2312).
- Each raw bridge mutation is denied by the existing bridge guards and surfaces as `ERROR: ...` in the tool result (line 2293), so the model sees denial but the loop does not terminate.
- `scripts/ollama_harness.py::run_tool_loop` (line 1170) has the identical exact-signature no-progress pattern (lines 1248-1254) and the same `MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4` (line 55), confirming the defect exists in BOTH loops and that the dual target_paths (`cloud_harness_base.py` for F, `ollama_harness.py` for D) are correctly scoped.
- `PublishBridgeVerdict` is a real, already-landed tool (`PUBLISH_BRIDGE_VERDICT_TOOL`, line 123) gated to LO bridge/verification skills by `allowed_tools_for_skill` (lines 688-698), so the recovery has a genuine target to narrow to.
- The recorded incident (dispatch `2026-07-12T21-39-03Z-loyal-opposition-F-f6b9bc`: 611 tool calls / 551 Bash, 63,397,693 tokens, exit 1) is independently captured in the WI-5216 backlog description, not only in the proposal. The defect is real and the cost is material.

## Findings / Advisory Notes

- F1 [P2 — verifier MUST confirm] Prose-during-recovery interaction. The loop's `not tool_calls` branch (lines 2208-2236) treats any non-blank assistant text as a `final_response` and RETURNS it, ending the session. If recovery is pending and the model emits prose instead of calling `PublishBridgeVerdict`, a naive implementation would return that prose as a successful final response and terminate WITHOUT a verdict, silently defeating the recovery. The proposal explicitly commits to handling this ("If the provider repeatedly refuses OR EMITS PROSE while recovery is pending, terminate after a small fixed count through the existing no_progress_loop class"). This is the single most important behavior for the verifier to prove: while recovery is pending, prose must NOT short-circuit to `final_response`; it must count toward the bounded recovery limit and, on exhaustion, terminate via `no_progress_loop`. Require an explicit unit test for prose-during-recovery in BOTH loops.
- F2 [P3 advisory] Simpler alternative considered. A minimal fix would make the no-progress guard semantic (detect a repeated denied bridge-mutation class regardless of syntax) and terminate faster, with fewer moving parts than a schema-narrowing recovery state machine. The proposal's recovery-to-publish approach is more complex but has strictly higher value: it can actually PRODUCE a governed verdict, which is the WI-5211 / six-harness-parity goal, whereas the minimal approach only fails faster. The added complexity is justified by that goal; noting the alternative for the record, not as a blocker.
- F3 [P3 advisory] Schema-narrowing trap bound. Narrowing the next turn to ONLY `PublishBridgeVerdict` could trap a model that legitimately needs to Read before publishing. The bounded recovery count (exit via `no_progress_loop` after a small fixed number) prevents this from consuming the full budget. Choose the recovery bound small enough to cap cost but large enough to allow one genuine corrected publish attempt; make the bound and the recovery instruction explicit and tested.
- F4 [P3 advisory] Robustness to a genuine publisher bug. If `PublishBridgeVerdict` itself errors (not just wrong-method model behavior), the recovery surfaces those tool errors and exits via the bounded `no_progress_loop` rather than masking them — a desirable property. Verify the recovery does not auto-author or auto-publish on the model's behalf; the model must still supply slug, verdict, and full reviewed body.

## Specification Linkage

All relevant governing specifications are cited (GOV-HARNESS-ONBOARDING-CONTRACT-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, ADR-CLOUD-HARNESS-TEMPLATE-001, DCL-OLLAMA-TOOL-PARITY-GATE-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, DCL-DISPATCH-ENVELOPE-RULES-001, plus spec-linkage/verification/project-linkage and artifact-lifecycle specs). The mandatory applicability preflight reports no missing required specs.

## Prior Deliberations

No conflicting prior deliberation. This defect is the "separately governed root-cause defect" anticipated by the WI-5211 GO (`bridge/gtkb-wi5211-df-governed-verdict-publication-parity-002.md`, cited), and is authorized under the six-harness proof program (DELIB-202666173). The scope explicitly preserves all raw guards, the canonical publisher's sole authority, and every runtime allowance (600/900/28800/29400/29700), so it does not revisit or contradict the WI-5202 generous-envelope decision or the WI-5210 governed-publisher decision.

## Owner Authorization (verified against canonical state)

- WI-5216 exists in the backlog: open, origin defect, P1, PROJECT-GTKB-GOOSE-HARNESS-ADOPTION / subproject harness-parity; description (including the 611-tool / 63.4M-token telemetry) matches this proposal.
- PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712: active, WI-scoped (verified via `gt projects show PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`).
- Owner Decisions / Input section present in the proposal.

## Applicability Preflight

- packet_hash: `sha256:3f7545d374c2a1aba3454ffacde3a0e591f0141a2ee59e211c0270747bb5039b`
- bridge_document_name: `gtkb-wi5216-provider-verdict-denial-loop-recovery`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-001.md`
- operative_file: `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5216-provider-verdict-denial-loop-recovery`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Implementation & Verification Guidance for Prime Builder

- Objective: on an LO bridge-review/verification route, when an existing raw Write/Edit/Bash bridge guard already DENIES a verdict mutation, preserve the denial in model-visible history, mark publication-recovery pending, and on the next provider turn expose only `PublishBridgeVerdict` plus a concise recovery instruction. Clear recovery only after a successful governed publish; on repeated refusal/prose/unknown-tool, terminate after a small fixed count via `no_progress_loop`, well before turn 600.
- Preserve every raw guard (no exemption), the canonical publisher's sole authority, non-bridge denials, ordinary investigative tool use, and every runtime allowance.
- Implement equivalent behavior in the shared cloud loop (F) and the standalone Ollama loop (D).
- Verification (deterministic core): focused tests for detection, schema narrowing, recovery clearing on success, bounded refusal via `no_progress_loop`, and F1 prose-during-recovery in BOTH loops; assert non-bridge denied writes/reads/greps/globs do NOT trigger recovery; assert existing writer/guard/atomic-VERIFIED/dispatch-lifetime tests remain green. Run `ruff check` AND `ruff format --check` on all changed Python files. Live F/D dispatch proof is corroborating, not the gating evidence, given provider dispatch cost — the focused unit tests are the deterministic gate.

## Recommended Commit Type

`fix` — matches the proposal; bounds a cost/robustness defect without adding capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
