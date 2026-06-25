NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d40d99d8-b006-4dd8-8e9d-bce8371a1e4b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; mode=auto

# Add a SessionStart `[Shell]` hint line — gt-via-PowerShell + venv PYTHONPATH (WI-4831)

bridge_kind: prime_proposal
target_paths: ["groundtruth-kb/templates/hooks/session-start-governance.py", "platform_tests/hooks/test_session_start_governance_shell_hint.py"]

Project Authorization: PAUTH-WI-4831-STARTUP-SHELL-HINT-001
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4831

Document: gtkb-wi4831-startup-shell-hint-line
Snapshot: 2026-06-25T~18:05Z

## Summary

Append a concise `[Shell]` line to the SessionStart governance hook's emitted
`additionalContext`, so fresh agents stop rediscovering — each session — how to invoke
`gt` and project Python on this Windows host. Single tracked source edit plus one new test.

The runtime hook `.claude/hooks/session-start-governance.py` is an 18-line `runpy` shim
that delegates to the canonical template
`groundtruth-kb/templates/hooks/session-start-governance.py`, so editing the **template**
alone changes runtime behavior — no re-activation step, no shim edit.

## Problem (owner-directed, evidence-based)

On this host, agents that reach for `gt` via the Claude **Bash tool** hit
`gt: command not found`: `gt.cmd` lives in `~/.local/bin` (a uv-tool install) which is on
the **Windows PATH** (PowerShell resolves it) but not the Bash tool's Git-Bash PATH. A
second, related gotcha: the project venv cannot import `groundtruth_kb` directly — it needs
`PYTHONPATH=groundtruth-kb/src`. Both are **deterministic** (identical every fresh session)
and recur at high cadence (50+ sessions in ~3 days via `list_sessions`).

Measured cost this session (representative): ~3–6 wasted tool round-trips before landing on
PowerShell `gt` (~10–20K tokens, ~1–3 min). The existing soft hint ("Shell: PowerShell
(primary)") did not prevent it; a directive, specific line is expected to outperform.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governing spec. Fresh sessions self-initialize
  with startup context AND must "suggest options for reducing token consumption during
  session startup." This `[Shell]` hint is a startup token-reduction measure: it removes
  the per-session rediscovery dance. The hook is a SessionStart self-init surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governs this
  proposal/review/verification cycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every
  relevant governing spec before requesting GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives a test
  from the linked requirement (assert the `[Shell]` line is emitted).
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the change is to a
  governance hook; the added behavior is covered by a mechanical test (write-time
  enforcement layer parity).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — durable artifact (the hook) is the
  capture point; the owner decision + spec linkage are preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — owner directive triggers a tracked
  implementation artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented stance.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` (startup self-init
+ its explicit startup-token-reduction clause) governs this additive startup-context line;
no new or revised requirement is needed before implementation.

## Prior Deliberations

- `DELIB-20266110` (this session, owner_decision) — owner AUQ chose to implement the doc
  line now (over eliminate-via-Bash-PATH, measure-first, or backlog-only).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI work / rediscovered
  conventions are a defect; eliminate recurring friction. This hint operationalizes that
  for session startup (the change is filed under PROJECT-GTKB-DETERMINISTIC-SERVICES-001).
- _No prior deliberations on the specific gt-on-PATH/shell topic: a `gt deliberations
  search` returned only semantically distant hits (novel topic)._

## Owner Decisions / Input

- **AUQ-S20260625-startup-shell-line-next-step** → owner answer: **"Implement the doc line
  now."** Captured as `DELIB-20266110`. The prior AUQ established the focus (quantify +
  add a line); this AUQ chose the doc-line implementation path over the alternatives.
- Scope confirmed Claude-harness scoped (the measured friction is the Claude Bash-tool
  PATH); Codex/AGENTS.md parity is a deliberately separate consideration.

## Change Detail (post-GO execution)

1. In `groundtruth-kb/templates/hooks/session-start-governance.py`, add a module-level
   `SHELL_HINT` constant and append it to `msg` in `main()` (both the pending and the
   clear branches), e.g.:
   `"[Shell] Run gt and project Python via PowerShell — the Claude Bash tool's PATH lacks gt (it's a uv-tool .cmd on the Windows PATH). For project Python: PYTHONPATH=groundtruth-kb/src .venv/Scripts/python.exe."`
   The `--self-test` branch may also include it.
2. Add `platform_tests/hooks/test_session_start_governance_shell_hint.py`: invoke the hook
   as a subprocess with a minimal JSON payload and assert the emitted `additionalContext`
   contains `[Shell]`, `PowerShell`, and `PYTHONPATH`.
3. Run the hook `--self-test` + the new pytest; report results.

Additive only: no existing startup behavior is removed or altered beyond the appended line.

## Verification plan (spec-derived)

- **GOV-SESSION-SELF-INITIALIZATION-001 / DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001**:
  the new test asserts the SessionStart `additionalContext` includes the `[Shell]` line
  with both `PowerShell` and `PYTHONPATH` tokens — directly verifying the requirement that
  startup context now carries the shell-invocation hint.
- Command: `python -m pytest platform_tests/hooks/test_session_start_governance_shell_hint.py -q`.
- Regression: existing governance-line text (bridge-pending / clear branches) remains
  present; the added line is appended, not replacing.

## Rollback

`git revert` the single implementation commit removes the appended line and the test.
Fully reversible; no data or state migration.

## Bridge Protocol Compliance

This proposal is filed as the next numbered, append-only bridge file
(`bridge/gtkb-wi4831-startup-shell-hint-line-001.md`). Prior bridge versions are never
deleted or rewritten; the numbered/versioned bridge file chain remains the canonical audit
trail per `GOV-FILE-BRIDGE-AUTHORITY-001`, with TAFE-backed dispatcher state as the
workflow authority.

## Risk

Low. Additive startup-context line in one governance hook + one new test. No source logic
change beyond the appended string; no KB, config, or runtime-state changes. Claude-harness
scoped.
