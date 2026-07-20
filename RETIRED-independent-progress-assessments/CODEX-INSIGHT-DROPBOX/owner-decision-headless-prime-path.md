author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e673b49a-79d9-485d-8b98-943def29837f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Owner Decision — Headless Prime Dispatch Path: Fix Codex (WI-5135), Not a New Non-GUI Prime Harness

## Context

Headless Prime Builder dispatch is OFF: Codex-A (the only active prime-builder
harness) was quiesced this session because its `exec` sandbox pops visible
`pwsh.exe` consoles per shell command (WI-5135); Cursor-E is suspended. Loyal
Opposition filed an advisory
(`INSIGHTS-2026-07-10-non-gui-prime-harness-advisory.md`) recommending adoption
of a non-GUI Prime harness (Alibaba Cloud Studio, or Ollama-Prime interim) and
recommending AGAINST chasing a Codex-shell window fix. The owner-grilling gate
questions were put to the owner via AskUserQuestion.

## Owner Decisions (AskUserQuestion, this session)

1. **Prime harness path — "Neither, keep interactive-Codex only."** The owner
   declined to adopt a non-GUI Prime harness (neither Alibaba nor Ollama-Prime).
   Headless Prime stays OFF; interactive Codex covers Prime work in the interim.
2. **Cloud Prime model acceptable — "Yes, acceptable for Prime work."** Recorded
   as an acceptable future option, not the path chosen now.
3. **Codex disposition — "Also fix WI-5135 in parallel."** The owner directs
   pursuing the Codex-shell no-window fix so Codex-A can become a window-safe
   headless Prime harness again. This is the chosen durable path, in preference
   to a new harness.
4. **Priority — "After current finalization backlog."** The WI-5135 fix is
   scheduled after the in-flight finalization-hardening threads (WI-5105 /
   WI-5112 / WI-5132) complete.

## Disposition (overrides the LO advisory's primary recommendation)

- The LO advisory recommended adopting a non-GUI Prime harness and NOT fixing
  Codex. The owner chose the **opposite**: fix Codex (WI-5135), do not adopt a
  new Prime harness. This owner decision governs.
- **WI-5135** is elevated from "captured defect" to **owner-directed fix**,
  scheduled **after** the finalization-hardening backlog. Scope: the Codex-shell
  no-window remediation (config/flag, no-window pwsh wrapper, or job-object
  containment) so Codex-A dispatch is window-safe and can be re-enabled.
- **WI-5072 / WI-5073** (Alibaba adoption) are NOT extended to the Prime role.
- **Codex-A stays quiesced** (`can_receive_dispatch=false`) until WI-5135 lands.
- **Ollama-D LO dispatch** (enabled this session) remains enabled; LO-only, not
  promoted to Prime.
- Cloud Prime remains an acceptable future fallback (decision 2) if the Codex
  fix proves infeasible.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
