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
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Recommended commit type: feat

target_paths: [".claude/hooks/session-topic-envelope-router.py", ".claude/settings.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_session_topic_envelope_router.py"]

## Summary

Slice 5 of `PROJECT-GTKB-CROSS-HARNESS-PARITY` is the **first conformance case**
(advisory §4): it wires the `::open` / `::close` topic-envelope routing into
Claude's `UserPromptSubmit` chain — behavioral parity with the Codex routing —
and registers the capability so the Slice-3 discovery-diff's
`hook:session_wrapup_trigger_dispatch` asymmetry turns **green** (advisory §6
criterion 1). It is the end-to-end proof of the whole invariant: a real
Claude-vs-Codex behavioral gap, detected by the discovery-diff, resolved (not
waived).

The behavior already lives in the shared, harness-agnostic platform module
`groundtruth_kb.session.topic_router` (`parse_topic_command`,
`handle_topic_command`, `render_topic_context`). Codex consumes it through
`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`; Claude currently has no
adapter, so `::open <type>` / `::close [<type>]` are unhandled on Claude even
though the SessionStart payload advertises `::open <activity>`. This slice adds
the missing Claude adapter.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — the bidirectional behavioral-parity
  invariant; this slice is the §4 first conformance case (resolve, not waive),
  with Q1 behavioral (not identity) equivalence: both harnesses call the same
  shared `topic_router` module via harness-appropriate adapters.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — the discovery-diff
  (assertion PARITY-DIFF-EXISTS) detects the asymmetry pre-Slice-5 and goes
  green post-Slice-5; the registry waiver/surface map (PARITY-WAIVER-SCHEMA /
  PARITY-APPLICABILITY-RULE) is exercised by registering the unifying capability.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — the `::`-prefixed canonical
  session-command grammar that `::open`/`::close` belong to.
- `GOV-20`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

The proposed tests derive from the linked specs: the routing tests map to the
Q1 behavioral-equivalence requirement; the discovery-diff integration test maps
to PARITY-DIFF-EXISTS (the asymmetry must be gone after registration).

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CROSS-HARNESS-PARITY-001` §4 already
specifies the first conformance case (wire `::open`/`::close` into Claude
UserPromptSubmit + register the capability). No new or revised requirement is
introduced.

## Cross-Harness Disposition

This proposal's `target_paths` touch harness-surface files
(`.claude/hooks/session-topic-envelope-router.py`, `.claude/settings.json`,
`config/agent-control/harness-capability-registry.toml`), so the disposition is
declared (and the Slice-4 gate now enforces this section here).

- **Nature of change:** adds a Claude UserPromptSubmit adapter for the
  `::open`/`::close` topic-envelope routing that already exists on Codex. The
  change is **directional by intent** (it closes a Claude-side gap) but
  **restores symmetry**: after it, both harnesses expose the same
  topic-envelope-routing capability.
- **Per-harness behavioral parity:** the Claude adapter
  (`.claude/hooks/session-topic-envelope-router.py`, `HARNESS_NAME="claude"`) and
  the Codex adapter (`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`,
  `HARNESS_NAME="codex"`) both call the identical shared `topic_router` functions;
  they differ only in harness name, harness-id resolution, and output paths
  (Q1 behavioral-not-identity equivalence). Both are registered under one
  capability with per-harness surfaces.
- **In-root:** all artifacts (the new hook, the settings.json edit, the registry
  edit, the new test, this bridge file) are written in-root under the GT-KB
  project root; the hook's diagnostic output goes to an in-root harness-state
  path.
- **Scope (deliberate):** the Claude adapter handles the `::open`/`::close`
  topic-envelope routing only — NOT the wrap-trigger-phrase branch of the Codex
  hook — because Claude already runs session wrap-up via its Stop hook
  (`session_self_initialization --emit-wrapup`); adding a UserPromptSubmit
  wrap-trigger would double-fire. Wrap-trigger parity is a separate concern, not
  this conformance case.
- **Waivers:** none; the capability is now present on both applicable harnesses.

## Design

### A. Claude adapter — `.claude/hooks/session-topic-envelope-router.py` (new)

A Claude `UserPromptSubmit` hook mirroring the topic-command branch of the Codex
`session_wrapup_trigger_dispatch.py` (lines ~158-179), Claude-native:

1. Read stdin, extract the prompt (reuse the Codex hook's prompt-extraction
   shape: JSON payload or raw text).
2. Respect the startup-input gate (read
   `harness-state/claude/session-lifecycle-guard.json`; emit `{}` when
   `discard_next_user_prompt` / `startup_response_pending` is set) so the hook
   never interferes with the SessionStart init-keyword relay.
3. `command = parse_topic_command(prompt)`; when None, emit `{}` (no context)
   and exit 0 — non-topic prompts pass through untouched.
4. When a command is present: `result = handle_topic_command(PROJECT_ROOT,
   command, harness_name="claude", harness_id=<resolved claude id>)`; emit
   `hookSpecificOutput.additionalContext = render_topic_context(result)`. On
   `EnvelopeError`, emit a bounded failure context (mirroring the Codex hook).
5. Write a diagnostic `last-topic-envelope-command.json` to an in-root Claude
   state dir.

Resolves the Claude harness id via `scripts.harness_identity.resolved_harness_id`
(same as the Codex hook). No wrap-trigger branch (see disposition scope note).

### B. Registration — `.claude/settings.json`

Add the new hook to the `UserPromptSubmit` hooks array (one entry, `timeout` 5,
consistent with the other UPS hooks). Position is non-load-bearing; appended
after the existing entries.

### C. Capability registration — `config/agent-control/harness-capability-registry.toml`

Add a `[[capabilities]]` entry that **unifies** the two harness surfaces under
one capability so the discovery-diff's surface-map upgrade keys both to the same
id:

```
id = "hook.session-topic-envelope-routing"
kind = "hook"
canonical_name = "session-topic-envelope-routing"
canonical_purpose = "UserPromptSubmit routing of ::open/::close topic-envelope commands."
canonical_source = ".claude/hooks/session-topic-envelope-router.py"
required_for_roles = ["prime-builder", "loyal-opposition"]
parity_class = "shared"
applicability = "universal"
[capabilities.claude] surface = ".claude/hooks/session-topic-envelope-router.py"; status = "native"
[capabilities.codex]  surface = ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py"; status = "native"
```

Bump `last_updated`. After this, the discovery-diff maps codex's
`session_wrapup_trigger_dispatch` stem and claude's `session-topic-envelope-router`
stem to the same capability id → present on both applicable harnesses → no
finding (the prior `hook:session_wrapup_trigger_dispatch` unregistered asymmetry
disappears).

### D. Tests — `platform_tests/scripts/test_session_topic_envelope_router.py` (new)

- **Behavioral routing (Q1):** load the Claude hook module; a `::open <type>`
  prompt yields a `hookSpecificOutput.additionalContext` payload (topic context
  rendered); a non-topic prompt yields `{}`; the startup-input gate suppresses
  output. (Use a tmp project / monkeypatched topic_router where needed to stay
  hermetic, or a live-or-skip idiom for the envelope runtime.)
- **Discovery-diff green (PARITY-DIFF-EXISTS / acceptance §6.1):**
  `parity_discovery_diff.run_discovery_diff(PROJECT_ROOT)` returns no finding
  whose `capability_key` is `hook:session_wrapup_trigger_dispatch` OR
  `hook.session-topic-envelope-routing` (the asymmetry is resolved). A
  pre-registration synthetic fixture still shows it (guards against silent
  no-op).
- **Schema validity:** `check_harness_parity.validate_parity_schema` stays clean
  with the new capability + surfaces.
- **Registration drift:** the hook is referenced in `.claude/settings.json` and
  exists on disk (mirrors `_check_registered_hooks_tracked` expectations).

## Test Plan / Spec-Derived Verification

| Linked spec / assertion | Derived test | Command |
|---|---|---|
| ADR Q1 behavioral routing | `::open`/non-topic/startup-gate cases in `test_session_topic_envelope_router.py` | `python -m pytest platform_tests/scripts/test_session_topic_envelope_router.py -q` |
| PARITY-DIFF-EXISTS / §6.1 (diff green) | discovery-diff no longer reports the session_wrapup_trigger_dispatch asymmetry | `python -m pytest platform_tests/scripts/test_session_topic_envelope_router.py -q` |
| PARITY schema validity | `check_harness_parity --validate-schema` clean | `python scripts/check_harness_parity.py --validate-schema` |
| Behavior preservation | existing discovery-diff + parity-matrix tests | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_check_harness_parity.py -q` |
| Doctor surface | `gt project doctor` parity discovery-diff check drops the resolved asymmetry | `gt project doctor` (WARN count decremented) |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: `::open <type>` routes on Claude (additionalContext emitted); the
discovery-diff no longer reports the `session_wrapup_trigger_dispatch` asymmetry
(advisory §6.1 — green only after this slice); schema stays valid; existing
parity tests remain green.

## Owner Decisions / Input

Implementation authority flows from `PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION`
(active; `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), with **WI-4891** the active
project member. The change creates no GOV/ADR/DCL/SPEC artifact and edits no
protected narrative-authority file (the new hook, settings.json, and the
capability registry are platform code/config), so no formal-artifact approval
packet is required. No new owner decision is pending.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §4 first conformance case +
  §5 step 5 + §6 acceptance criterion 1 (diff goes green after this slice).
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER1-MEANING` — Q1 behavioral-equivalence
  basis for the harness-appropriate-adapter approach.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — the owner authorization basis.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — Slice-3
  VERIFIED; the discovery-diff that flagged `hook:session_wrapup_trigger_dispatch`.
- `bridge/gtkb-cross-harness-parity-slice-4-disposition-gate-004.md` — Slice-4
  VERIFIED; its gate enforces the `## Cross-Harness Disposition` section this
  proposal carries.

## Risk / Rollback

- **Risk:** the new UserPromptSubmit hook could perturb Claude's existing UPS
  flow (init-keyword relay, classifiers). *Mitigation:* the hook emits `{}` for
  any non-topic prompt and respects the startup-input gate; it is appended after
  existing entries and shares no state with them.
- **Risk:** double session-wrap. *Mitigation:* the adapter deliberately omits the
  wrap-trigger branch; Claude wrap stays on the Stop hook.
- **Risk:** the registry edit could break the schema or the discovery-diff.
  *Mitigation:* `validate_parity_schema` + the discovery-diff integration test +
  the existing Slice-2/3 suites are re-run.
- **Risk:** envelope runtime (`open_topic`/`close_topic`) behaves differently
  under `harness_name="claude"` (e.g. missing claude harness-state dirs).
  *Mitigation:* the hook catches `EnvelopeError` and emits a bounded failure
  context rather than crashing the prompt; tests cover the error path.
- **Rollback:** revert the four files (remove the settings.json entry, the
  registry capability, the hook, and the test). The discovery-diff reverts to
  reporting the asymmetry at WARN (the pre-Slice-5 state); no governance residue.
