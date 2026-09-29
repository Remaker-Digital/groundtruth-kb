# Product overview

**Status:** Current first-pass overview
**Reviewed:** 2026-09-26

GroundTruth KB helps an owner and independent AI-agent contexts progress
software work from current requirements to tested, reviewed, committed results.
It is designed for work where generated code is not enough: requirements,
evidence, review independence, exact work product, and final Git state must stay
connected.

## What GTKB provides

- A native service for canonical specifications, tests, projects, work items,
  memberships, session bindings, and coordination state.
- The `gt` CLI for supported reads and mutations.
- GTKB Home as the primary interactive interface.
- Project-scoped authorization and one parent project per work item.
- Executable-test linkage for new implementation work.
- An agent-authored proposal, review, implementation report, and verification
  lifecycle.
- Per-bridge-item claims that coordinate the next artifact without assigning an
  agent durable ownership of a work-item thread.
- Project-level finalization: independently verified work items complete
  together in one project commit.

## What GTKB does not provide

- It is not a chat archive or a durable store of bridge-message content.
- It does not make deliberation notes authoritative.
- It does not use PAUTH or DECISION records.
- It does not infer owner choices from prior messages or cached state.
- It does not make generated harness projections authoritative.
- It does not turn a health check, generated dashboard, or passing local test
  into release qualification by itself.
- It does not yet provide a unified end-user installer for the complete Windows
  host.

## Main components

| Component | Purpose |
| --- | --- |
| Native PostgreSQL domain service | Canonical current records and supported mutation APIs |
| `gt` CLI | Scriptable product command surface |
| GTKB Home | Primary interactive user interface on the local workstation |
| Harness baseline and projectors | Authored shared agent configuration and derived harness-specific projections |
| Bridge coordination | Ephemeral delivery of the next agent-authored lifecycle artifact |
| Git repositories | Durable authored work product and activation history |

Continue with [Core concepts](Core-Concepts), or review
[System requirements](System-Requirements) before installation.
