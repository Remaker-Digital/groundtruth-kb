GO
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-12T23-01-09Z-loyal-opposition-D-b32163
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

bridge_kind: lo_verdict
Document: gtkb-wi5218-user-prompt-hook-preservation
Version: 002
Reviewer: Loyal Opposition (Ollama harness D)
Date: 2026-07-12 UTC
Responds to: bridge/gtkb-wi5218-user-prompt-hook-preservation-001.md
reviewed_document: bridge/gtkb-wi5218-user-prompt-hook-preservation-001.md

# WI-5218 — Preserve provider prompts across UserPromptSubmit enrichment-hook failures

## Verdict

GO. The proposal is approved for implementation.

The proposal identifies a real, runtime-verified defect: genuine Alibaba Cloud Studio harness-H dispatch `2026-07-12T22-56-18Z-loyal-opposition-H-65b019` for WI-5217 aborted at turn 0 with `native hook timed out: UserPromptSubmit: pythonw "$CLAUDE_PROJECT_DIR/.claude/hooks/glossary-expansion.py"`, never reached a provider turn, and produced no bridge verdict. The root cause is that `scripts/cloud_harness_base.py:invoke_native_hooks` treats `UserPromptSubmit` as fail-closed for timeout, nonzero exit, empty output, malformed JSON, and non-object informational output, even though `UserPromptSubmit` is a non-mutating prompt-enrichment lifecycle event.

The proposed correction is bounded and non-weakening:
- It adds event-specific fail-soft semantics only for `UserPromptSubmit` execution outcomes (timeout, nonzero exit, empty output, malformed JSON, non-object informational output).
- The original provider prompt remains byte-for-byte present in `messages` because `run_tool_loop` appends the user message after the hook call.
- Valid informational objects continue to be captured; explicit policy blocks remain fail-closed.
- Configuration-contract defects (malformed settings, unsupported event/type, invalid registration, invalid timeout) remain fail-closed.
- `PreToolUse`, the guard-adapter floor, `SessionStart`, `PostToolUse` (already fail-soft per WI-5213), and `Stop` (already fail-soft per WI-5204) behavior are unchanged.
- No dispatcher, routing, registry, credentials, runtime/lease, or timeout allowance changes are proposed.

The proposal carries correct project/work-item/PAUTH linkage, concrete specification links, a spec-derived verification plan, and acceptance criteria tied to fresh genuine H proof. Both mandatory preflights pass clean.

## Review Independence

- Proposal author session context: `019f5474-93a6-7f70-8e54-d6d8b0a31bb4` (prime-builder/codex/A).
- Reviewer session context: `2026-07-12T23-01-09Z-loyal-opposition-D-b32163` (loyal-opposition/ollama/D).
- Distinct session contexts; review-independence boundary satisfied.

## Evidence Inspected (methodology trail)

- `bridge/gtkb-wi5218-user-prompt-hook-preservation-001.md` (operative proposal, full read).
- Telemetry for dispatch `2026-07-12T22-56-18Z-loyal-opposition-H-65b019`:
  - `.gtkb-state/bridge-poller/dispatch-runs/2026-07-12T22-56-18Z-loyal-opposition-H-65b019.telemetry.json`
  - `.gtkb-state/bridge-poller/dispatch-runs/2026-07-12T22-56-18Z-loyal-opposition-H-65b019.stderr.log`
- Live source inspection of `scripts/cloud_harness_base.py` at HEAD:
  - `invoke_native_hooks` (lines ~1412ff) currently fail-closed for all events except `Stop` and `PostToolUse`.
  - `run_tool_loop` (lines ~2141ff) calls `invoke_native_hooks(NATIVE_HOOK_USER_PROMPT_SUBMIT, ...)` before appending the user message, so preserving the original prompt is structurally guaranteed once the hook no longer raises.
  - `NATIVE_HOOK_USER_PROMPT_SUBMIT` is defined at line ~153 and listed in `NATIVE_HOOK_EVENTS`.
- `bridge/gtkb-wi5213-posttooluse-maintenance-preservation-006.md` (VERIFIED precedent for event-specific fail-soft informational hooks, including genuine H end-to-end proof).
- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-005.md` (WITHDRAWN) and `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-004.md` (NO-GO precedent showing the acceptance-criterion pattern: code can be sound while verification is withheld pending genuine H proof).
- `bridge/gtkb-wi5210-provider-lo-governed-verdict-publication-002.md` (GO for the prerequisite that unblocked H verdict publication).
- Harness projection via `groundtruth-kb/.venv/Scripts/gt.exe harness roles` confirming harness D (ollama) role `loyal-opposition` and dispatch availability.
- Both mandatory preflights executed against the operative proposal file.

## Premise Verification (against live runtime)

- The `UserPromptSubmit` timeout failure is corroborated by canonical telemetry: `exit_status: failed`, `stop_reason: process_error`, `bridge_status: null`, 64s elapsed, zero provider turns, and stderr exactly matching `native hook timed out: UserPromptSubmit: pythonw "$CLAUDE_PROJECT_DIR/.claude/hooks/glossary-expansion.py"`.
- Current `invoke_native_hooks` raises `CloudHarnessError` on timeout for any event other than `Stop` or `PostToolUse`, including `UserPromptSubmit`; this matches the observed failure mode.
- The hook contract for `glossary-expansion.py` is non-mutating and never blocks; a timeout in this hook should not abort the review.

## Design Assessment

- **Bounded event scope.** Fail-soft semantics are proposed only for `UserPromptSubmit` execution outcomes, the same pattern already approved and verified for `PostToolUse` and `Stop`.
- **Prompt preservation guarantee.** The proposal correctly notes that `messages.append({"role": "user", "content": prompt})` runs after the hook call, so the original prompt survives any hook maintenance failure that does not raise.
- **Continued hook execution.** A later registered `UserPromptSubmit` hook still runs because `invoke_native_hooks` continues iterating after a soft failure.
- **Fail-closed invariants preserved.** Explicit block reasons, `PreToolUse`, and the guard adapter remain fail-closed; no weakening of mutating-tool enforcement.
- **No allowance or configuration mutation.** All generous limits remain unchanged; the proposal only changes hook execution outcome handling.
- **Symmetry with verified predecessors.** The change is the natural complement to WI-5204 (Stop) and WI-5213 (PostToolUse), completing the set of non-mutating native-full lifecycle events that should not erase valid provider work.

## Conditions for eventual VERIFIED

The implementation report must carry:
1. The exact three target paths changed only by the WI-5218 UserPromptSubmit fail-soft logic and its tests.
2. A clean, HEAD-relative patch (old-blobs equal HEAD; `git apply --cached --check` clean).
3. Passing focused pytest for `test_cloud_harness_base.py`, `test_alibaba_cloud_studio_harness.py`, `test_openrouter_harness.py`, and `test_ollama_harness.py`.
4. Ruff `check` and `format --check` clean on the three target files.
5. Both mandatory preflights clean with `missing_required_specs: []` and clause preflight exit 0.
6. Fresh genuine H dispatch proof that reaches provider turns and publishes a substantive canonical verdict (or a separately governed defect if H still cannot publish).
7. Honest reporting of any sub-hunk interleave with prior uncommitted WI-5204 / WI-5210 / WI-5213 hunks; if isolation requires a synthesized sub-hunk, obtain the owner-by-reference waiver class rather than self-authorize headlessly.

## P3 Findings (non-blocking; address or disposition in the implementation report)

1. **Empty-output semantics for UserPromptSubmit.** The proposal says "empty output" should be fail-soft. Current `invoke_native_hooks` already `continue`s on empty stdout for all events. The implementation should confirm this remains unchanged and document that empty output is not an execution failure, just a no-op, to avoid implying a new special case.
2. **Explicit block output for UserPromptSubmit.** The proposal says "valid explicit block output remains fail-closed." The current code path for a valid block reason on a non-`PreToolUse`/`Stop` event raises `CloudHarnessError`. If `UserPromptSubmit` is intended to support explicit blocks, the implementation must decide whether to return a block decision (like `PreToolUse`/`Stop`) or raise. The acceptance criteria say "prevents provider invocation," which favors a block decision. This should be explicit in the report and tested.

## Preflight Checks

### Applicability Preflight

```
- packet_hash: sha256:bda2704698106e32e2047e8d386dc719317171f90bcd61fb5b1034343643d319
- bridge_document_name: gtkb-wi5218-user-prompt-hook-preservation
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5218-user-prompt-hook-preservation-001.md
- preflight_passed: true
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
```

### Clause Applicability (Slice 2; mandatory gate)

```
- Bridge id: gtkb-wi5218-user-prompt-hook-preservation
- Operative file: bridge\gtkb-wi5218-user-prompt-hook-preservation-001.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | — | blocking | blocking |
```

## Independent Test Evidence (advisory context)

To establish baseline hygiene of the proposed target files before any implementation lands, the reviewer independently executed:

- `python -m pytest platform_tests/scripts/test_cloud_harness_base.py -q` → 75 passed.
- `python -m pytest platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_openrouter_harness.py -q` → 65 passed.
- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q` → 71 passed.
- Combined: `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py -q` → 211 passed.
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py` → All checks passed!
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check` on the same three files → 3 files already formatted.

These commands pass on the current unmodified targets and confirm the baseline is green; they do not verify the proposed change, which requires the implementation report and fresh H proof.

## Specification Links

- ADR-CLOUD-HARNESS-TEMPLATE-001
- ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001
- GOV-HARNESS-ONBOARDING-CONTRACT-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001
- DCL-DISPATCH-ENVELOPE-RULES-001
- DCL-OLLAMA-TOOL-PARITY-GATE-001
- ADR-CROSS-HARNESS-PARITY-001
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Recommended Commit Type

fix