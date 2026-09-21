# Known Limitations

Use the installed CLI, current formal/work records and actual consumer evidence
to assess readiness. Historical release and audit reports remain observations
of their named revisions; they are not current repair instructions or authority.

## 1. Shared harness sources and bounded upgrade coverage

Harness instructions now come from authored root `AGENTS.md`, shared
`.agents/skills` and baseline rules/hooks/routing. Copied per-host rules, hooks
and skill bodies are obsolete. Use the current native checks and projector
rather than old daemon-count or manual settings-copy repair instructions.

Use native doctor/upgrade checks for the paths they declare and the sole
projector for the selected host profile. Unmanaged files and unrelated local
settings need explicit reconciliation; a clean managed-output check does not
cover them. Do not recreate copied hook/rule/skill trees. See [Harness
projection](reference/harness-projection.md).

Actual native instruction/skill loading, Codex hook trust, Antigravity root
selection and provider behavior require installed-host evidence. Missing native
observations remain unqualified, even when source and projector tests pass.

## 2. Search is a derived view

Native domain services remain authoritative. A search index can help retrieve
current material but does not carry owner choices, project authorization or
work state. An unavailable service does not permit a SQLite or archived-file
authority fallback. Use the current supported index regeneration route for
its declared scope and verify native-source readback.

## 3. Platform Baseline

The install baseline is **Windows + internet access**. Linux and macOS
workstations work in practice (the reference project CI runs on Ubuntu),
but the walkthrough in [Start Here](start-here.md) and the PowerShell
primer both assume Windows. A cross-platform walkthrough is tracked as a
future documentation pass.

## 4. Claude Design Integration

GroundTruth-KB supports **local manual handoff inspection only**. The
`gt design inspect <handoff>` command inspects a local Claude Design
handoff (`.zip` or directory), validates it against
`SPEC-CD-HANDOFF-FORMAT-001` and prints a metadata-only, redacted inspection
record; it stores nothing (raw design bytes are never inlined; see
[Claude Design Handoff Inspection](claude-design-intake.md)).

What is **not** supported today: live Claude Design API
([claude.ai/design](https://claude.ai/design)) integration; treating
Claude Design outputs (HTML prototypes, PPTX, Canva exports) as production
code; context-pack generation; visual verification; design dashboards; and
any review gate that treats a design-handoff as binding. Those remain
candidates for future ADRs + child bridges, not a v0.x capability.

## 5. Deployment Provisioning

GroundTruth-KB is a **local toolkit**. It does not provision cloud
infrastructure, create external accounts (Anthropic, OpenAI, Azure,
GitHub), install OS scheduled tasks, or deploy applications.
Project-specific deployment is the responsibility of the downstream
project, using the CI templates and setup prompts that
`gt project init` scaffolds.

## 6. CTO-Persona Walkthrough — Pending

The [Start Here](start-here.md) rewrite includes an owner-gated
qualitative gate: a cold-read walkthrough by a senior technologist who
has never seen GroundTruth-KB before. As of 2026-04-17, that walkthrough
is PENDING owner sign-off. Adopter feedback collected between this
release and the walkthrough will land in a docs-only follow-up.

---

## Reporting a New Limitation

If you hit a limitation that is not listed here, please open a GitHub
issue tagged `method-feedback`. We especially value reports that include:

- The command or workflow that surprised you.
- What you expected vs. what happened.
- Whether you worked around it, and if so, how.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
