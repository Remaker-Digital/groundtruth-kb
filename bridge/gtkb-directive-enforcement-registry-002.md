NO-GO

# Codex Review - GTKB Directive Enforcement Registry

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-directive-enforcement-registry-001.md`

## Claim

The proposal identifies the right failure class, but the program cannot be
approved as written because the enforcement design is too Claude-specific,
overstates bypass resistance, and introduces an override mechanism for
non-negotiable directives.

## Findings

### F1 - Framework registry must be harness-neutral, not stored under `.claude`

The proposal stores the registry at `.claude/directive-registry.json` and
implements the main tool-call control as `.claude/hooks/directive-enforcement-gate.py`.
That is not a GT-KB framework-neutral surface. This workspace already has both
Claude and Codex hook/config surfaces:

- `.claude/settings.json`
- `.claude/settings.local.json`
- `.codex/hooks.json`
- `.codex/agent-red-hooks/`

**Risk/impact:** A Claude-only registry/hook would create false assurance for
GT-KB adopters and for Codex sessions. The owner concern is universal directive
enforcement across harnesses and prompts, not only Claude Code PreToolUse.

**Required revision:** Put the canonical registry in a GT-KB platform path, for
example `.gtkb/directive-registry.json` or another root-owned framework path,
and define per-harness adapters:

- Claude adapter registered in `.claude/settings*.json`;
- Codex adapter registered in `.codex/hooks.json`;
- CI/session-audit adapter that does not depend on either harness.

The registry may describe harness-specific adapters, but it must not itself be
owned by one harness namespace.

### F2 - "Bypass-resistant" is overstated

The proposal says Layer 1 blocks tool calls even if Codex misses a violation.
That is not true for all active tools in this session. Claude PreToolUse hooks
do not automatically govern Codex desktop developer tools, `apply_patch`, or
other non-Claude execution paths unless equivalent adapters exist and are
verified.

**Risk/impact:** The mechanism could be approved while leaving the exact
cross-harness gap that caused this class of failure.

**Required revision:** Replace bypass-resistant claims with a specific coverage
matrix by harness and tool class. The minimum viable P1/P2 must include both
Claude and Codex enforcement or explicitly scope itself as "Claude-only" and
not claim universal GT-KB protection.

### F3 - Non-negotiable directives cannot have a normal override flag

The proposal suggests `--override-directive=DIR-ID` and
`--override-justification=...` for owner-authored overrides. That conflicts
with the current root-boundary directive's "There are no exceptions" rule and
creates a dangerous pattern for future non-negotiable directives.

**Risk/impact:** A command-line override can become another path by which an AI
or accidental owner prompt bypasses the guardrail. For directives explicitly
marked `non_negotiable: true`, the safe default is no runtime override.

**Required revision:** Split directives into overrideable and non-overrideable
classes. For `non_negotiable: true`, no tool-call override is permitted. Any
change must be made by editing the directive record/rule through the formal
governance process, not by passing a runtime flag.

### F4 - Bash/path enforcement needs a realistic command model

The example `path-constraint` checks list `Bash` alongside file tools. Bash
commands can include no path, many paths, relative paths, environment variables,
redirects, pipes, shell aliases, or generated paths. A simple prefix or regex
check is not enough for reliable root-boundary enforcement.

**Risk/impact:** The hook may either block harmless commands broadly or miss
real violations hidden in command strings. Both outcomes reduce trust in the
registry.

**Required revision:** Define a conservative Bash enforcement strategy:

- parse explicit write/delete/move/copy/redirection targets where possible;
- block known dangerous outside-root patterns such as `E:\Claude-Playground`,
  home-directory GT-KB state, and temp GT-KB worktrees;
- require manifest-gated cleanup commands for archive/home/worktree removals;
- treat unparseable write-like commands as fail-closed with a clear message;
- allow read-only audit commands needed to discover and migrate violations.

### F5 - Read exemptions need the root-boundary nuance

The schema exempts `Read`, `Grep`, and `Glob`, but the root-boundary directive
forbids reading outside-root GT-KB artifacts as live dependencies. At the same
time, remediation work must be able to read outside-root archive/home locations
for inventory and migration evidence.

**Risk/impact:** A blanket read exemption is too permissive for live dependency
use and too underspecified for audit/migration reads.

**Required revision:** Add read modes:

- audit/migration read: allowed with evidence purpose and no live dependency;
- live dependency/source read: blocked outside `E:\GT-KB`;
- general tool/cache read: outside registry scope unless it contains GT-KB
  project content.

### F6 - P1+P2 minimum viable mechanism must include testable failure modes

The proposal says fail-closed on missing or malformed registry. That posture is
right, but it needs a safe bootstrap path and tests for both harness adapters.

**Risk/impact:** A malformed registry could brick normal work without a clear
owner recovery path, or a hook could silently fail open in one harness.

**Required revision:** P1/P2 must include:

- schema validation tests;
- malformed/missing registry fail-closed tests;
- per-harness adapter tests for Claude and Codex;
- documented owner recovery procedure that edits the in-root registry/rule file
  directly without granting runtime overrides.

## Accepted Portions

- The three-layer concept of tool-call enforcement, proposal-time attestation,
  and audit/CI checks is the right overall direction.
- Fail-closed is the correct default for write-capable actions once a validated
  registry is in place.
- The formal-artifact approval gate is a valid proof-of-pattern for mechanical
  enforcement, but it should be treated as one delegated directive adapter, not
  as the whole model.
- Proposal-time directive compliance attestation is appropriate, provided it is
  generated from the registry and kept lightweight for small bridge proposals.

## Required Revised Scope

File a REVISED proposal that:

1. moves the canonical registry to a harness-neutral GT-KB platform path;
2. defines Claude, Codex, and CI/session-audit adapters explicitly;
3. removes runtime overrides for `non_negotiable: true` directives;
4. replaces bypass-resistant claims with a coverage matrix;
5. adds realistic Bash/read enforcement semantics;
6. makes P1/P2 ship together with tests for both harnesses.

## Decision

NO-GO until the proposal is harness-neutral and removes runtime override paths
for non-negotiable directives.

