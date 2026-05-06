NEW

# Claude Code SessionStart Hook Parity With Codex Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Claim

Claude Code's SessionStart hook silently drops the canonical startup payload
because `.claude/settings.json` invokes `scripts/session_self_initialization.py`
with the wrong subcommand flag, producing a JSON envelope that does not
match Claude Code's SessionStart hook contract. As a result, Prime Builder
sessions in the Claude harness have been bootstrapping cold — without the
governance disclosure, focus menu, freshness contract, or smart-poller
notification table that the canonical service is designed to deliver — while
Codex sessions, which use a wrapper dispatcher, receive the correct payload.

This proposal closes the gap with three changes:

1. Replace Claude's direct `python scripts/session_self_initialization.py
   --emit-report --fast-hook --harness-name claude` invocation with a Claude-
   side dispatcher analogous to `.codex/gtkb-hooks/session_start_dispatch.py`,
   wired through `.claude/settings.json`. The dispatcher will use the correct
   `--emit-startup-service-payload` flag, validate the freshness contract,
   re-emit the SessionStart envelope cleanly, and fall back to a degraded-
   banner context when the canonical service fails or times out.
2. Bump Claude's SessionStart hook timeout from 15 s to 60 s to match
   Codex and to remove a latent truncation cause under load.
3. Repair the `No module named 'scripts.check_harness_parity'` import
   defect inside `scripts/session_self_initialization.py` so the
   `Harness parity` field in the canonical startup payload populates
   correctly for both harnesses.

## Background And Investigation Evidence

Owner-directed investigation in S333. Live evidence captured in this
conversation:

- Manual run of the Claude SessionStart hook produced a flat JSON envelope:

  ```json
  {"additionalContext": "..."}
  ```

  The relevant emit path is at `scripts/session_self_initialization.py:5366`:

  ```python
  def _emit_hook_context(text: str) -> None:
      print(json.dumps({"additionalContext": text}, ensure_ascii=False))
  ```

  This shape is **not** the SessionStart hook contract Claude Code expects;
  the contract requires:

  ```json
  {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}
  ```

  emitted at `scripts/session_self_initialization.py:5608-5619` under the
  `--emit-startup-service-payload` branch.

- Manual run of the Codex SessionStart dispatcher
  (`.codex/gtkb-hooks/session_start_dispatch.py`) produced the correct
  wrapped envelope. The dispatcher invokes the canonical service with
  `--emit-startup-service-payload --fast-hook`, validates the freshness
  contract via `_valid_session_start_payload`, and re-emits a clean
  SessionStart payload via `_session_start_payload(...)`. On failure,
  it emits `_fallback_context(reason)` so Codex always receives some
  payload.

- The deterministic comparator
  `python scripts/check_harness_parity.py --all --markdown` reports
  `PASS: 50` — capability-registry parity is intact. The defect is at
  the protocol-envelope layer, which the comparator does not currently
  inspect.

- Both manual runs print:
  `Harness parity: unavailable (harness=..., role=..., no counts);
  error=No module named 'scripts.check_harness_parity'`. The script is
  importable directly but fails when the canonical service tries to
  import it as a sibling module — a separate latent defect.

- Codex writes `.codex/gtkb-hooks/last-session-start.json` and
  `last-session-start.err` for forensic auditing. Claude leaves no
  equivalent trace, which is why this defect has been silently
  shipping across multiple sessions.

- This S333 session itself is direct evidence: my Prime Builder startup
  composed its own disclosure rather than relaying the canonical payload
  verbatim, because the canonical payload never arrived in my context.
  Only the explanatory-style system reminder reached me.

## Specification Links

The following governing specifications constrain this proposal:

- `GOV-SESSION-SELF-INITIALIZATION-001` (governance, `verified`) — Fresh
  sessions must self-initialize with live role, governance, bridge,
  dashboard, priorities, and token context. The current Claude behavior
  violates this for Claude-harness sessions.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (protected_behavior,
  `verified`) — Sessions must not treat governance startup context as
  implicit. The current Claude defect forces sessions to either compose
  ad-hoc disclosures or skip governance disclosure entirely.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (design_constraint, `verified`)
  — Startup reports must include token-cost context and reduction
  options. The canonical service implements this; the Claude path
  loses it.
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` (specification) — Codex
  first-prompt discard gate may only arm from real SessionStart
  dispatch. Cited as parallel/precedent for the harness-specific
  startup-input contract; Claude needs equivalent fidelity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking per applicability
  matrix) — Bridge-mediated implementation work must honor the file
  bridge authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always
  blocking) — Implementation proposals must cite every relevant
  governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
  — Verification must be derived from linked specifications and
  executed against the implementation. The test plan below maps
  tests to each of the above specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking per the
  applicability matrix when proposals reference
  `.claude/rules/project-root-boundary.md` or
  `.claude/rules/file-bridge-protocol.md`) — All live GT-KB harness
  artifacts must remain within the canonical project root and the
  prescribed in-root locations. The new dispatcher and its diagnostic
  files will live entirely under `E:\GT-KB\.claude\hooks\`, satisfying
  this constraint.
- `.claude/rules/project-root-boundary.md` — All live GT-KB harness
  artifacts must remain under `E:\GT-KB`. The new dispatcher will
  live at `.claude/hooks/session_start_dispatch.py` and write
  diagnostics under `.claude/hooks/` to honor this rule.
- `.claude/rules/file-bridge-protocol.md` — File bridge protocol
  including the Owner Decisions / Input section gate.
- `.claude/rules/codex-review-gate.md` — Counterpart review gate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — Owner-relevant
  process changes captured here as durable artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — Development
  changes preserve traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — Lifecycle
  trigger states cited in the bridge thread.

## Prior Deliberations

Search performed via direct SQLite query on `groundtruth.db`
`deliberations` table and `specifications` table. No prior
deliberation specifically targets the Claude SessionStart envelope
defect; the closest related records are:

- `GOV-SESSION-SELF-INITIALIZATION-001` and
  `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (cited above as
  governing specs).
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` — addresses role
  authority ambiguity but not envelope shape.
- `DELIB-1417` (smart-poller-orient-verification-2026-04-29) —
  related smart-poller orientation work; not directly applicable.

No prior NO-GO has rejected this approach. The closest precedent is
the Codex dispatcher itself, which is the working model this
proposal mirrors for Claude.

## Proposed Changes

### Change 1 — Claude SessionStart Dispatcher

New file: `.claude/hooks/session_start_dispatch.py`. Functionally
mirrors `.codex/gtkb-hooks/session_start_dispatch.py` with these
differences:

- `HARNESS_NAME = "claude"`.
- Invokes `scripts/session_self_initialization.py
  --project-root <root> --emit-startup-service-payload --fast-hook
  --harness-name claude --harness-id <resolved>`.
- Writes diagnostics to `.claude/hooks/last-session-start.json` and
  `.claude/hooks/last-session-start.err` (in-root per
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`).
- Validates `_valid_session_start_payload` against the same freshness
  contract version (`gtkb-startup-freshness-v1`).
- Emits the validated `hookSpecificOutput.additionalContext` via
  `_session_start_payload(...)`.
- On any failure (timeout, non-zero exit, freshness contract failure),
  emits `_fallback_context(reason)` so Claude always receives some
  payload.

Modify `.claude/settings.json` SessionStart hook from:

```
"command": "python \"$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py\" --emit-report --fast-hook --harness-name claude",
"timeout": 15
```

to:

```
"command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/session_start_dispatch.py\"",
"timeout": 60
```

Same change applied to the existing Stop hook? — **No.** The Stop
hook uses `--emit-wrapup` which is a separate code path; this
proposal is scoped to SessionStart only. Stop-hook envelope shape
will be inspected in a follow-on review and will be filed as a
separate bridge thread if needed.

### Change 2 — Timeout Increase

`.claude/settings.json` SessionStart `timeout: 15` → `timeout: 60`.
Matches Codex SessionStart timeout. Justification: the canonical
service's freshness payload includes Grafana dashboard reachability
checks and KB summary queries that can spike under cold-cache
conditions. Codex already runs at 60s without complaint; aligning
prevents Claude-side truncation.

### Change 3 — Harness Parity Import Repair

Investigate and fix `No module named 'scripts.check_harness_parity'`
at the call site inside `scripts/session_self_initialization.py` that
populates the `Harness parity` startup-payload field. Likely fixes
include adjusting `sys.path`, switching to a `runpy` invocation, or
shelling out to the script as a subprocess (mirroring how the same
script is invoked at the CLI). The chosen fix will be the smallest
change that makes the field populate without introducing a new
import-cycle risk.

## Test Plan And Spec-To-Test Mapping

| Linked specification | Test or verification |
|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | Regression test: invoke `.claude/hooks/session_start_dispatch.py`, parse stdout as JSON, assert `hookSpecificOutput.hookEventName == "SessionStart"`, assert `additionalContext` contains `"Programmatic Startup Payload"`. |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Same test asserts the additionalContext contains the role-mapping disclosure block (`"Role being assumed:"`) and the focus-menu marker (`"Choose This Session's Focus"` for Prime, or the Loyal Opposition startup-action block for LO). |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Same test asserts the additionalContext contains `"Token measurement status:"` and `"reducing startup token consumption"` mentions. |
| `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` | Parity test: assert the Claude dispatcher emits `hookSpecificOutput` envelope identical in shape to the Codex dispatcher's output (`set(hookSpecificOutput.keys()) == {"hookEventName", "additionalContext"}` minimum). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Static test: assert `.claude/hooks/session_start_dispatch.py` exists and resolves under `E:\GT-KB`; assert diagnostics paths `last-session-start.json` and `last-session-start.err` resolve under `E:\GT-KB\.claude\hooks\`. |
| Hook timeout alignment | Static test: parse `.claude/settings.json` and `.codex/hooks.json`, assert SessionStart timeouts are equal. |
| Harness parity import repair | Manual evidence + targeted test: invoke the canonical service with `--emit-report --fast-hook --harness-name claude` and assert the resulting markdown does **not** contain the substring `"error=No module named 'scripts.check_harness_parity'"`. |
| Fallback safety | Targeted test: invoke the dispatcher with a deliberately broken `STARTUP_SERVICE` path (env override or temp rename), assert the dispatcher still emits a valid `hookSpecificOutput` envelope containing `_fallback_context()`'s degraded-banner marker. |

Test home: `tests/scripts/test_claude_session_start_dispatcher.py`.
Existing parity infrastructure (`scripts/check_harness_parity.py` +
`tests/scripts/test_check_harness_parity.py`) will not be modified
in this proposal; an enrichment to the comparator (envelope-shape
check) is captured as accepted future work in §"Accepted Future Work"
below rather than scope creep here.

## Acceptance Criteria

1. Fresh Claude Code session opens; assistant's first context contains
   the canonical "Programmatic Startup Payload" header.
2. `.claude/hooks/last-session-start.json` exists after session start
   and parses as valid SessionStart envelope JSON.
3. `python scripts/session_self_initialization.py --emit-report --fast-hook
   --harness-name claude` no longer prints
   `error=No module named 'scripts.check_harness_parity'`; the
   `Harness parity` field shows real counts.
4. `.claude/settings.json` SessionStart timeout equals
   `.codex/hooks.json` SessionStart timeout.
5. New tests in `tests/scripts/test_claude_session_start_dispatcher.py`
   pass under the GT-KB platform pytest lane.
6. `python scripts/check_harness_parity.py --all --markdown` continues
   to report `PASS`.

## Risk And Rollback

- **Risk: dispatcher introduces new failure surface.** Mitigated by
  the fail-soft pattern Codex already uses — any unhandled exception
  emits `_fallback_context(...)` rather than crashing the hook.
- **Risk: timeout increase masks a real performance regression.**
  Mitigated by the dispatcher's stderr capture and audit-file write,
  which makes slow startups visible for retrospective analysis.
- **Risk: import repair changes the canonical service's behavior for
  Codex too.** Acceptable — the `Harness parity` field is the same
  field Codex consumes; both harnesses benefit equally.
- **Rollback:** revert `.claude/settings.json` SessionStart command
  to the prior `--emit-report` invocation and restore `timeout: 15`.
  Delete `.claude/hooks/session_start_dispatch.py`. Restore the
  `Harness parity` call site to its prior form. All three changes are
  isolated and individually revertable.

## Accepted Future Work (Out Of Scope For This Proposal)

- Enrich `scripts/check_harness_parity.py` to verify SessionStart
  hook envelope shape end-to-end (run the configured hook command,
  assert `hookSpecificOutput.hookEventName == "SessionStart"`). File
  as separate bridge after this proposal verifies.
- Audit Claude's Stop and UserPromptSubmit hooks for the same
  envelope-shape defect class. File as separate bridge.
- Consider promoting the Claude dispatcher pattern into a shared
  `scripts/harness_session_start_dispatcher.py` library used by both
  `.claude/hooks/` and `.codex/gtkb-hooks/`. File as separate bridge.

## Owner Decisions / Input

- Owner directive in S333 (this conversation): "Start by investigating
  #1 first, then file a bridge proposal targeting fixes 1–3." This is
  the explicit owner-approved scope for this proposal. The
  investigation result was reported in the same conversation with
  evidence (flat-vs-wrapped JSON envelope at
  `scripts/session_self_initialization.py:5366` vs `5608`).
- Owner directive in S333: "Yes please" (in response to the offer
  to run the deterministic comparator), authorizing
  `python scripts/check_harness_parity.py --all --markdown`. Result
  recorded above (PASS: 50).
- No additional owner approval is requested by this proposal beyond
  the standard Loyal Opposition `GO`/`NO-GO` review. No formal
  artifact mutation is requested. No destructive action is requested.
  No production / external surface is touched.
- If Loyal Opposition NO-GOs, Prime Builder will revise per findings
  without re-soliciting owner approval, since the scope itself was
  owner-directed.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing
Preflight Subsection":

1. Read `config/governance/spec-applicability.toml` — done. Triggered
   rules identified: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
   (blocking; triggered by `applies_when_paths_match` matching
   references to `.claude/rules/project-root-boundary.md` and
   `.claude/rules/file-bridge-protocol.md`),
   `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking),
   `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
   (mention of "implementation proposal" in this file),
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (mention of
   "verification" / "spec-to-test"), `GOV-ARTIFACT-ORIENTED-
   GOVERNANCE-001` (advisory, mentions "specification",
   "requirement"), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory,
   mentions "artifact", "traceability"), `DCL-ARTIFACT-LIFECYCLE-
   TRIGGERS-001` (advisory, mentions "deferred", "verified"). All
   cited in §"Specification Links". Initial draft was hard-blocked
   by `bridge-compliance-gate.py` for omitting
   `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; this revision adds it.

2. KB-search for cross-cutting governance specs governing the
   artifact type — done. Identified
   `GOV-SESSION-SELF-INITIALIZATION-001`,
   `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
   `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`,
   `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001`. All cited.

3. Bridge proposal triggers the always-blocking cross-cutting
   bridge-governance set — cited:
   `.claude/rules/file-bridge-protocol.md`,
   `.claude/rules/codex-review-gate.md`.

4. Run `python scripts/bridge_applicability_preflight.py --bridge-id
   gtkb-claude-session-start-parity` — to be run after this file is
   saved and the INDEX entry added. Expected:
   `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`. If the preflight reports any missing
   specs, this file will be revised before re-saving.

5. Preflight `packet_hash`: `sha256:e2a87501c7d2878622665c580fda09e55355672a1a922e793405cb17f39c8d08`
   (recorded 2026-05-06 S333 after INDEX entry filed; output:
   `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
