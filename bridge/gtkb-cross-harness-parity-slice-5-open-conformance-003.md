REVISED
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
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-cross-harness-parity-slice-5-open-conformance-002.md (GO)
Recommended commit type: feat

target_paths: [".claude/hooks/session-topic-envelope-router.py", ".claude/settings.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_topic_envelope_router.py", "platform_tests/scripts/test_parity_discovery_diff.py"]

## Revision Note (REVISED from -001)

Implementation surfaced a scoping gap the original `-001` target_paths missed:
the Slice-3 test `test_parity_discovery_diff.py::test_open_asymmetry_detected_live_pre_slice5`
is, by its own name and docstring, a pre-Slice-5 checkpoint that asserts the
`::open` asymmetry IS present "until Slice 5 wires it in (then it goes green)".
Now that this slice resolves the asymmetry, that test correctly fails and MUST be
flipped to assert the resolved state. This REVISED proposal adds
`platform_tests/scripts/test_parity_discovery_diff.py` to `target_paths` to
authorize that one-test update (the discovery-diff's detection *capability*
remains proven by the unchanged synthetic-hook regression test
`test_synthetic_unregistered_single_harness_hook_caught`). No other change from
`-001`. The four original target files are already implemented and pass; this
revision authorizes the dependent Slice-3 test flip so the commit leaves no
failing test.

## Summary

Slice 5 of `PROJECT-GTKB-CROSS-HARNESS-PARITY` is the **first conformance case**
(advisory §4): it wires the `::open` / `::close` topic-envelope routing into
Claude's `UserPromptSubmit` chain — behavioral parity with the Codex routing —
and registers the capability so the Slice-3 discovery-diff's
`hook:session_wrapup_trigger_dispatch` asymmetry turns **green** (advisory §6
criterion 1). The behavior lives in the shared, harness-agnostic
`groundtruth_kb.session.topic_router`; Codex consumes it via
`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`, and this slice adds the
missing Claude adapter.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — §4 first conformance case
  (resolve, not waive); Q1 behavioral (not identity) equivalence via the shared
  `topic_router` module.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — assertion
  PARITY-DIFF-EXISTS goes green post-Slice-5; the registry surface-map
  (PARITY-APPLICABILITY-RULE) unifies the two harness surfaces.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — the `::`-prefixed session-command
  grammar that `::open`/`::close` belong to.
- `GOV-20`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CROSS-HARNESS-PARITY-001` §4 already
specifies the first conformance case. No new or revised requirement is
introduced; the added target path authorizes a dependent test flip the design
anticipated.

## Cross-Harness Disposition

This proposal's `target_paths` touch harness-surface files
(`.claude/hooks/session-topic-envelope-router.py`, `.claude/settings.json`,
`config/agent-control/harness-capability-registry.toml`), so the disposition is
declared (the Slice-4 gate enforces this section here).

- **Nature of change:** adds a Claude `UserPromptSubmit` adapter for the
  `::open`/`::close` topic-envelope routing that already exists on Codex; closes
  a Claude-side gap and restores symmetry.
- **Per-harness behavioral parity:** the Claude adapter
  (`session-topic-envelope-router.py`, `HARNESS_NAME="claude"`) and the Codex
  adapter (`session_wrapup_trigger_dispatch.py`, `HARNESS_NAME="codex"`) both
  call the identical shared `topic_router` functions; they differ only in
  harness name, harness-id resolution, and output paths (Q1 behavioral
  equivalence). Both are registered under one capability with per-harness
  surfaces.
- **In-root:** all artifacts are written in-root under the GT-KB project root;
  the adapter's diagnostics go to an in-root `.gtkb-state/` path.
- **Scope (deliberate):** the Claude adapter handles topic routing only — NOT
  the Codex hook's wrap-trigger branch — because Claude already runs session
  wrap-up via its Stop hook; a `UserPromptSubmit` wrap-trigger would double-fire.
- **Waivers:** none; the capability is now present on both applicable harnesses.

## Design

### A. Claude adapter — `.claude/hooks/session-topic-envelope-router.py` (new)

A Claude `UserPromptSubmit` hook mirroring the topic-command branch of the Codex
hook: read stdin → extract prompt → respect the startup-input gate
(`harness-state/claude/session-lifecycle-guard.json`) → `parse_topic_command`;
when None emit `{}`; else `handle_topic_command(..., harness_name="claude",
harness_id=<resolved>)` and emit
`hookSpecificOutput.additionalContext = render_topic_context(result)`; on
`EnvelopeError` emit a bounded failure context. Portable project-root resolution
(walk to `groundtruth.toml`). No wrap-trigger branch.

### B. Registration — `.claude/settings.json`

Append the hook to the `UserPromptSubmit` hooks array (`timeout` 5).

### C. Capability registration — `config/agent-control/harness-capability-registry.toml`

Add `[[capabilities]]` `id = "hook.session-topic-envelope-routing"`
(`kind="hook"`, `applicability="universal"`, `required_for_roles` both) with
`[capabilities.claude]` surface = the new hook and `[capabilities.codex]`
surface = `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`. The
discovery-diff surface-map then keys both harness surfaces to one capability id
→ present on both → the prior `hook:session_wrapup_trigger_dispatch` finding
resolves.

### D. Tests — `platform_tests/scripts/test_session_topic_envelope_router.py` (new)

Hermetic routing tests (`::open`→context, non-topic→`{}`, startup-gate
suppression, `EnvelopeError`→bounded failure) + a discovery-diff integration
test asserting no finding for `hook:session_wrapup_trigger_dispatch` or
`hook.session-topic-envelope-routing`.

### E. Dependent test flip — `platform_tests/scripts/test_parity_discovery_diff.py` (REVISED scope)

Update the Slice-3 `test_open_asymmetry_detected_live_pre_slice5`: it asserted
the live `::open` asymmetry was present (codex-only) pre-Slice-5; flip it to
assert the asymmetry is now **resolved** (no finding whose `capability_key` is
`hook:session_wrapup_trigger_dispatch` or `hook.session-topic-envelope-routing`),
renaming/redocumenting accordingly. The unchanged
`test_synthetic_unregistered_single_harness_hook_caught` continues to prove the
diff's detection capability against a synthetic fixture, so detection coverage is
preserved.

## Test Plan / Spec-Derived Verification

| Linked spec / assertion | Derived test | Command |
|---|---|---|
| ADR Q1 behavioral routing | `::open`/non-topic/startup-gate/error cases in `test_session_topic_envelope_router.py` | `python -m pytest platform_tests/scripts/test_session_topic_envelope_router.py -q` |
| PARITY-DIFF-EXISTS / §6.1 (diff green) | diff integration test + flipped Slice-3 test both assert resolution | `python -m pytest platform_tests/scripts/test_session_topic_envelope_router.py platform_tests/scripts/test_parity_discovery_diff.py -q` |
| Detection capability preserved | unchanged synthetic-hook regression test | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py -q` |
| PARITY schema validity | `check_harness_parity --validate-schema` clean | `python scripts/check_harness_parity.py --validate-schema` |
| Doctor surface | discovery-diff WARN count decremented (27 to 26) | `gt project doctor` |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: `::open <type>` routes on Claude; the discovery-diff no longer
reports the `session_wrapup_trigger_dispatch` asymmetry (advisory §6.1, green);
the flipped Slice-3 test passes; schema valid; detection capability preserved.

## Owner Decisions / Input

Implementation authority flows from `PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION`
(active; `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), with **WI-4891** the active
project member. The change creates no GOV/ADR/DCL/SPEC artifact and edits no
protected narrative-authority file. No new owner decision is pending.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §4 first conformance case +
  §6 acceptance criterion 1.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER1-MEANING` — Q1 behavioral-equivalence.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — authorization basis.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — Slice-3
  VERIFIED; the discovery-diff + the `_pre_slice5` test this revision flips.
- `bridge/gtkb-cross-harness-parity-slice-4-disposition-gate-004.md` — Slice-4
  VERIFIED; its gate enforces the disposition section here.
- `bridge/gtkb-cross-harness-parity-slice-5-open-conformance-002.md` — the
  original GO this REVISED proposal extends (adds one dependent test target).

## Risk / Rollback

- **Risk:** the new `UserPromptSubmit` hook perturbs Claude's existing UPS flow.
  *Mitigation:* emits `{}` for non-topic prompts; respects the startup-input
  gate; appended after existing entries.
- **Risk:** double session-wrap. *Mitigation:* the adapter omits the
  wrap-trigger branch.
- **Risk:** flipping the Slice-3 test hides a real detection regression.
  *Mitigation:* the synthetic-hook regression test is unchanged and still
  proves detection independently of the live `::open` state.
- **Rollback:** revert the five files (settings.json entry, registry capability,
  hook, new test, and the Slice-3 test flip). The discovery-diff reverts to
  reporting the asymmetry at WARN; no governance residue.
