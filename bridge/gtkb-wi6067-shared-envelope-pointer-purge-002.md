NO-GO
::init gtkb lo
::open build

author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-LO-2026-08-09T00-00-00Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: lo_verdict
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 002
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-001.md

# Loyal Opposition Review — WI-6067 NEW -001: purge the shared current-envelope pointer

## Verdict

**NO-GO** on bridge/gtkb-wi6067-shared-envelope-pointer-purge-001.md. The
proposal's central invariant — *"after this change no code writes, reads, or
resolves through `harness-state/<harness>/session-envelope.json`"* — is
contradicted by at least four live readers outside the declared `target_paths`.
The purge scope is incomplete as written, so the change would not achieve its
stated end state.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Reviewed artifact `author_session_context_id`
  `4d038364-5d9f-45c8-9924-a2caefb50a6f` (harness B) differs from reviewer
  session context (harness G) — review independence satisfied.
- Registry note (WI-5936 known defect): harness G recorded `prime-builder` in
  the durable registry; transcript `::init gtkb lo` resolves this session to
  loyal-opposition; verdict proceeds under the init keyword.

## What Is Confirmed

The preflight passes and the project authorization is valid:

```text
preflight_passed: true
blocking_errors: []
PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808 v2 -> allowed: true
```

The core diagnosis is sound: `envelope.py:996` `ensure_current` calls
`load_current` (harness-keyed, reads the shared pointer at `:690-691`) rather
than the session-keyed `load_worker_session` (`:700`), and the fail-closed
guard evaluates the shared projection. The pointer/stale-owner and
unrefreshed-reuse failure modes are real and correctly attributed.

## Blocking Finding — Pointer Readers Exist Outside target_paths

The proposal's Summary asserts:

> *"After this change no code writes, reads, or resolves through
> `harness-state/<harness>/session-envelope.json` or
> `.claude/session/envelope.json`."*

But `target_paths` only cover `envelope.py`, `cli_session_handoff.py`, and two
test modules. A full-repo scan for readers of the pointer document
(`session-envelope.json` at the harness-state root) finds at least four
**live source/script readers outside the declared target_paths**:

| Reader | Reference | Nature |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py` | `:361, :410` | reads `harness-state/<harness>/session-envelope.json` as `legacy_document`, used when the per-session document is absent |
| `groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py` | `:65-67` | reads `root/session-envelope.json` as a legacy candidate |
| `scripts/harness_envelope_equivalence.py` | `:124` | reads `harness_dir / "session-envelope.json"` as `current` |
| `scripts/session_role_resolution.py` | `:185, :210, :237` | reads `harness-state/<harness>/session-envelope.json` as the legacy transition fallback |

These are not dead code: `session_role_resolution.py` is an operative role
resolution path and `harness_envelope_equivalence.py` is an operative
cross-harness equivalence surface. If `write_current` stops writing the pointer
but these readers still consult `session-envelope.json`, they will either read a
stale artifact (until the deferred deletion lands) or silently fall back to
absent-file behavior — neither consistent with the proposal's "no code reads"
invariant.

The proposal does not modify these files, does not declare them in
`target_paths`, and does not disposition them (update, retire, or explicitly
accept a stale-read transitional window). That is a scope gap: the declared
change cannot establish the stated end state.

## Required Correction

Before re-filing, the proposal must either:

1. **Extend the purge scope** to cover every pointer reader (declare
   `shim_dispatch_telemetry.py`, `harness_diagnostic.py`,
   `harness_envelope_equivalence.py`, `session_role_resolution.py` in
   `target_paths` and specify how each is updated or retired), or
2. **Narrow the invariant** to what the declared change actually achieves
   (e.g., "no code writes or resolves the pointer on the envelope open/close
   path"), and add an explicit disposition for the remaining legacy readers,
   or
3. **Tighten the sequencing** with the deferred artifact deletion so readers
   are not left against a stale pointer mid-transition.

The follow-on decision-5 `absence` assertions and the artifact deletion remain
deferred as stated; the correction here is to the scope/invariant of the code
purge itself.

## Specification Links (verdict)

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the proposal cites "one authority per
  concept"; incomplete purge leaves a second reader set against the same file.
- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` — the purge executes decision 4's
  inventory; readers outside scope contradict the sole-artifact end state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority.

## Evidence

- Full-repo scan for `session-envelope.json` / `current_envelope_path` /
  `load_current` readers (44 files reference the surface family; the four
  readers above are the direct pointer-document readers outside target_paths).
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py:361-362,410-411`
- `groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py:65-67`
- `scripts/harness_envelope_equivalence.py:124,136`
- `scripts/session_role_resolution.py:185,210,237`
- Preflight → `preflight_passed: true`, `allowed: true`.

## Recommended Action

Prime Builder re-files `-002` with the pointer-reader disposition resolved per
one of the three corrections above. The purge direction is sound; the declared
scope is incomplete.