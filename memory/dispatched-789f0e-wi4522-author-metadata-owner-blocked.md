# Dispatched worker 789f0e — WI-4522 author-metadata NO-GO stand-down (owner-blocked)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T07-50-18Z-prime-builder-B-789f0e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code headless bridge auto-dispatch worker; Prime Builder; explanatory output style; model claude-opus-4-8[1m]

Dispatch `2026-06-14T07-50-18Z-prime-builder-B-789f0e`, cap=2, selected NO-GO
`gtkb-wi4522-author-metadata-per-harness-resolution-002`. Live INDEX confirmed
latest=NO-GO@-002 (Prime-actionable). **Stood down: zero bridge/MemBase/source
mutations.** Class: `dispatched-worker-blocked-on-owner-decision` (NOT the usual
`addresses-report-evidence-defect` — Codex's "no owner decision needed"
assessment is itself wrong here).

## Why Codex's NO-GO@-002 is correct (independently confirmed)

`REQUIRED_AUTHOR_METADATA_FIELDS` (`scripts/bridge_author_metadata.py:20-27`) = 6
fields. Two are **durable** (`author_identity`, `author_harness_id`); four are
**runtime session facts** (`author_session_context_id`, `author_model`,
`author_model_version`, `author_model_configuration`). The proposed
`_resolve_metadata_from_harness_identity` reads `harness-state/harness-identities.json`
(name->id) + `harness-state/harness-registry.json` (id->role/status) — **neither
carries the 4 runtime fields.** `validate_author_metadata` (`:186-196`) raises if
any of the 6 is absent. So in the exact headless/no-env case the fix targets,
identity-resolution alone can't validate; keeping `current.json` as fallback
leaves the stale-shared-file bug reachable.

## New evidence I added (not in -002)

`cross_harness_bridge_trigger._spawn_harness` (`:2408-2454`): worker env =
`dict(os.environ)` + `GTKB_PROJECT_ROOT`, `GTKB_BRIDGE_POLLER_RUN_ID`,
`GTKB_INHERITED_SESSION_ID`, impl-auth vars, `GTKB_BRIDGE_DISPATCH_KEYWORD`.
**Sets NONE of `GTKB_AUTHOR_*` / `GTKB_MODEL*` / `GTKB_SESSION_ID`.** Confirms the
4 runtime fields have NO per-harness source in headless dispatch once
`current.json` is removed. (Contrast `_kb_attribution.resolve_changed_by`:
registry-only works there because it resolves a single LABEL `<role>/<name>`, not
6 audit fields — the proposal's "mirror the priority-3 pattern" analogy breaks on
the 4 runtime fields.)

## Why this is OWNER-blocked (disagrees with Codex "Decision Needed: None")

No completion exists within the proposal's authorized scope
(`scripts/bridge_author_metadata.py` + 1 test; PAUTH allows `source`+`test_addition`
only). Every working fix must source the 4 runtime fields from a NEW surface:

1. **Launcher-threaded**: dispatcher sets author/model env on worker from a NEW
   per-harness registry field -> touches `cross_harness_bridge_trigger.py` +
   registry schema/data. (Out of target_paths.)
2. **Per-session isolated packet** keyed by session/dispatch id -> this IS the
   **cycle-12 owner-REJECTED "key cache by session/harness id"**. Cannot silently
   adopt.
3. **Hybrid** (Codex option 3): registry for 2 durable fields + runtime envelope
   for 4 session fields — still needs the dispatcher to populate the envelope =
   option 1's scope.

The cycle-12 owner decision ("Per-harness resolution at filing time", session
02535fad) was made on the premise the identity registry could supply the
metadata — Codex falsified that. Interrogative-default + AUQ-only require
surfacing the corrected understanding as a fresh owner decision. Even a narrowed
fix (resolve only `author_identity`+`author_harness_id` per-call from registry,
leave model fields to current.json) is PARTIAL — model/version/configuration
would still stamp from the stale baseline -> Codex re-NO-GO. Confirmed: no
in-scope, owner-input-free completion.

## Owner AUQ to run (interactive Prime — pre-framed)

"WI-4522's chosen 'per-harness resolution at filing time' can't supply the 4
runtime author fields (session id, model, version, configuration) — the harness
registries don't carry them, and headless dispatch sets no author/model env. How
should the filing harness obtain a complete correct author record?"

- **A. Launcher-threaded** (recommended): dispatcher writes author/model env on
  each spawned worker; per-harness default model metadata added to the registry;
  `bridge_author_metadata` resolves identity from registry + model/session from
  env. Scope: +`cross_harness_bridge_trigger.py`, +registry field. Honors
  "per-harness at filing time."
- **B. Session-scoped packet**: SessionStart hook writes an isolated
  `.gtkb-state/.../by-session/<id>.json`; load reads current session's record.
  (NOTE: close to the cycle-12-rejected keyed-cache — confirm the owner now
  accepts it.)
- **C. Defer** WI-4522; keep current.json with a documented concurrency caveat.

## Thread state left as-is

Latest=NO-GO@-002 (Prime-actionable). Did NOT file REVISED (would flip to
Codex-actionable -> documented dispatch-churn anti-pattern; and no complete
design to GO). Next interactive Prime: run the AUQ above, then file REVISED with
the chosen fork's full scope. **Substrate-hygiene candidate (already tracked in
memory):** auto-park NO-GO threads that are owner-decision-blocked so they stop
re-dispatching to headless Prime workers.

~40K tokens. 2026-06-14 ~07:50-08:00Z, claude-opus-4-8[1m], harness B.
