NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 0eb73a79-4ad6-40c0-88e9-16f797f0ef2e
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4891

Document: gtkb-cross-harness-parity-slice-5-open-conformance
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-cross-harness-parity-slice-5-open-conformance-004.md (GO on REVISED -003)
Recommended commit type: feat

target_paths: [".claude/hooks/session-topic-envelope-router.py", ".claude/settings.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_topic_envelope_router.py", "platform_tests/scripts/test_parity_discovery_diff.py"]

## Post-Implementation Report

Implementation of Slice 5 (`WI-4891`, first conformance case) per the GO at
`-004` (REVISED `-003`). All five `target_paths` implemented within scope. The
discovery-diff `::open` asymmetry is **resolved** (the program's end-to-end
proof: detect → prevent → conform).

## What Was Built

1. **`.claude/hooks/session-topic-envelope-router.py`** (new) — Claude
   `UserPromptSubmit` adapter for `::open`/`::close` topic-envelope routing.
   Calls the shared `groundtruth_kb.session.topic_router`
   (`parse_topic_command`/`handle_topic_command`/`render_topic_context`) with
   `HARNESS_NAME="claude"`; respects the startup-input gate; emits `{}` for
   non-topic prompts; bounded `EnvelopeError` failure context. Topic routing
   only (no wrap-trigger branch — Claude wraps via its Stop hook). Portable
   project-root resolution.
2. **`.claude/settings.json`** — appended the hook to the `UserPromptSubmit`
   array; file remains valid JSON.
3. **`config/agent-control/harness-capability-registry.toml`** — added
   `[[capabilities]]` `id = "hook.session-topic-envelope-routing"`
   (`applicability="universal"`) unifying `[capabilities.claude]` (the new hook)
   and `[capabilities.codex]` (`session_wrapup_trigger_dispatch.py`).
4. **`platform_tests/scripts/test_session_topic_envelope_router.py`** (new) — 5
   tests: routing (`::open`→context), non-topic→`{}`, startup-gate suppression,
   `EnvelopeError`→bounded failure, and the discovery-diff green integration test.
5. **`platform_tests/scripts/test_parity_discovery_diff.py`** (REVISED scope) —
   flipped the Slice-3 `test_open_asymmetry_detected_live_pre_slice5` (now
   `test_open_asymmetry_resolved_post_slice5`) to assert the asymmetry is
   resolved; the unchanged synthetic-hook regression test preserves detection
   coverage.

## Specification Links (carried forward)

- `ADR-CROSS-HARNESS-PARITY-001` (§4 first conformance case; Q1 behavioral
  equivalence via the shared module).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (PARITY-DIFF-EXISTS now green;
  PARITY-APPLICABILITY-RULE surface-map unification).
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`; `GOV-20`;
  `GOV-FILE-BRIDGE-AUTHORITY-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

## Requirement Sufficiency

Existing requirements sufficient. The slice implements the already-specified §4
first conformance case; no new or revised requirement was introduced.

## Cross-Harness Disposition

This report's `target_paths` touch harness-surface files
(`.claude/hooks/session-topic-envelope-router.py`, `.claude/settings.json`,
`config/agent-control/harness-capability-registry.toml`), so the disposition is
declared (the Slice-4 gate enforces this section).

- **Nature of change:** adds the missing Claude adapter for the `::open`/`::close`
  routing that already exists on Codex; restores symmetry. Applicability
  **universal**.
- **Per-harness behavioral parity:** the Claude adapter and the Codex adapter
  both call the identical shared `topic_router` functions, differing only in
  `HARNESS_NAME`, harness-id resolution, and output paths (Q1). Both are
  registered under one capability with per-harness surfaces; the discovery-diff
  now keys them together → present on both.
- **In-root:** all artifacts in-root; adapter diagnostics go to
  `.gtkb-state/session-topic-router/claude/`.
- **Scope (deliberate):** topic routing only; wrap-trigger handling stays on
  Claude's Stop hook to avoid double-firing.
- **Waivers:** none.

## Spec-to-Test Mapping + Verification Evidence

| Linked spec / assertion | Derived test(s) | Result |
|---|---|---|
| ADR Q1 behavioral routing | `test_non_topic_prompt_emits_no_context`, `test_topic_open_emits_additional_context`, `test_startup_gate_suppresses_routing`, `test_envelope_error_emits_bounded_failure` | PASS |
| PARITY-DIFF-EXISTS / §6.1 (diff green) | `test_discovery_diff_no_longer_reports_open_asymmetry` + flipped `test_open_asymmetry_resolved_post_slice5` | PASS |
| Detection capability preserved | unchanged `test_synthetic_unregistered_single_harness_hook_caught` | PASS |
| Behavior preservation | `test_check_harness_parity.py` + `test_cross_harness_parity_schema.py` | PASS |

Commands run and observed results:

- `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_session_topic_envelope_router.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_cross_harness_parity_schema.py -q`
  → **43 passed**.
- `python scripts/parity_discovery_diff.py` → **Unwaived asymmetries: 26**
  (was 27); no `session_wrapup_trigger_dispatch` or
  `session-topic-envelope-routing` finding remains — the `::open` asymmetry is
  **resolved** (advisory §6.1, green).
- `python scripts/check_harness_parity.py --validate-schema` → **parity schema OK**.
- `ruff check <changed>` → **All checks passed**;
  `ruff format --check <changed>` → **3 files already formatted**.
- `.claude/settings.json` validated as well-formed JSON after the edit.

## Acceptance Criteria (advisory §6 criterion 1)

- ✅ The discovery-diff detected the `::open` asymmetry pre-Slice-5 (Slice 3) and
  goes **green** after this slice — the first conformance case is closed.
- ✅ `::open <type>` routes on Claude via the shared `topic_router` (additionalContext emitted).
- ✅ Detection capability preserved (synthetic-hook regression unchanged).

## Owner Decisions / Input

Implementation authority flows from `PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION`
(active; `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), with **WI-4891** the active
project member. The change creates no GOV/ADR/DCL/SPEC artifact and edits no
protected narrative-authority file (the hook, settings.json, and the capability
registry are platform code/config), so no formal-artifact approval packet is
required. No new owner decision is pending.

Note (non-blocking context): the settings.json registration was briefly blocked
by a concurrent, since-expired path reservation from the unrelated abandoned
`gtkb-wi4889-auto-finalization-sweep`; the conflict cleared on packet expiry and
no force-through occurred.

## Prior Deliberations

- `bridge/gtkb-cross-harness-parity-slice-5-open-conformance-004.md` — the GO on
  REVISED `-003` this report responds to (Cursor LO, harness E; separation
  check passed).
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §4 first conformance case +
  §6 acceptance criterion 1.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER1-MEANING` — Q1 behavioral-equivalence.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — Slice-3
  VERIFIED; the discovery-diff + the `_pre_slice5` test flipped here.
- `bridge/gtkb-cross-harness-parity-slice-4-disposition-gate-004.md` — Slice-4
  VERIFIED; its gate enforces the disposition section here.

## Recommended Commit Type

`feat:` — net-new Claude topic-envelope routing capability (new hook + settings
registration + registry capability + tests + the dependent Slice-3 test flip).
