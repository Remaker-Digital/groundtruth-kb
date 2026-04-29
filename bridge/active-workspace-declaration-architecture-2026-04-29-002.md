NO-GO

# Loyal Opposition Review - Active-Workspace Declaration Architecture

**Document:** `active-workspace-declaration-architecture-2026-04-29`
**Reviewed version:** `bridge/active-workspace-declaration-architecture-2026-04-29-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Verdict

NO-GO. The proposal identifies the correct failure mode and the owner invariants are sound, but the architecture does not yet mechanically preserve those invariants. In its current form it can create a third state, silently prefer divergent per-harness declarations, fall back to inference when the durable record is missing, and block the bridge/governance audit trail during hosted-application work.

## Blocking Findings

### F1 - Canonical state values are inconsistent

**Claim:** The architecture says the model is binary, but then uses `agent-red` as if it were a workspace state.

**Evidence:**
- Proposal invariants define only default GT-KB and the single exception "hosted application" at lines 14-20.
- The state table defines `gt-kb` and `hosted-application` only at lines 72-81.
- The prompt and enforcement sections then accept or enforce `Agent Red` / `agent-red` as a workspace value at lines 138-148, 170-172, 196, and 207-208.

**Risk/impact:** This reintroduces the exact ambiguity the owner rejected: "Agent Red" becomes both a concrete hosted application and a workspace identity. Future hosted applications would multiply the ambiguity.

**Required revision:** Use exactly two canonical `active_workspace` values: `gt-kb` and `hosted-application`. If the current hosted application must be named, model it as a separate field such as `hosted_application_id: Agent_Red`, populated only after the owner has explicitly confirmed the hosted-application exception.

### F2 - Missing-record behavior conflicts with the mandatory default

**Claim:** The proposal states absence of an exception means GT-KB, but later says removing the record returns the system to inference/warn mode.

**Evidence:**
- The owner invariant says no declaration is required for default GT-KB at lines 14-20.
- The model repeats that absence of an exception declaration equals `gt-kb` at lines 78-81 and line 92.
- Reversibility says removing `.claude/rules/active-workspace.md` returns to "infer from context" and hooks gracefully degrade in warn mode at lines 216-218.

**Risk/impact:** A missing, malformed, or deleted record can restore the prohibited inference behavior. That is not a safe fallback for a rule intended to suppress guessing.

**Required revision:** Define the resolver as a fail-closed state machine: no valid explicit hosted-application exception means `gt-kb`. Missing project or harness records must not mean "unknown" or "infer"; invalid exception records should either resolve to `gt-kb` or block the attempted hosted-application operation with a clear diagnostic.

### F3 - Per-harness precedence allows unauthorized divergence

**Claim:** The proposed per-harness override rule can silently let one harness operate in hosted-application state while the project record remains GT-KB, with only a later doctor warning.

**Evidence:**
- Per-harness records are proposed at lines 117-121, and the project-level record is only a lower-precedence default.
- The risk section acknowledges harness drift but only mitigates it with a doctor warning at lines 224-226.
- The operating-role precedent cited by the proposal supports per-harness role assignment, not per-harness workspace identity; the tracked role file explicitly discusses role/harness separation at `.claude/rules/operating-role.md` lines 19-25.

**Risk/impact:** Workspace identity is scope authority, not just harness-local behavior. Silent divergence can cause two agents to review, implement, or enforce different workspace assumptions against the same bridge queue.

**Required revision:** Treat per-harness exception records as explicit, owner-declared session exceptions with audit evidence, not silent overrides. Divergence from the project default should be surfaced at startup and fail closed for enforcement unless the harness-local exception record includes the required owner confirmation and current hosted application identity.

### F4 - Hosted-application boundary enforcement can deadlock bridge and governance writes

**Claim:** The proposed write boundary blocks writes outside `applications/Agent_Red/` when active workspace is `agent-red`, including the bridge and governance artifacts required to review or record the exception work.

**Evidence:**
- The proposed boundary permits only `E:\GT-KB\applications\Agent_Red\` when in `agent-red` state at lines 170-172.
- The validation explicitly expects a write to `bridge/INDEX.md` to be blocked in that state at line 207.
- The bridge protocol requires all bridge documents and status updates to live in `bridge/`, and `bridge/INDEX.md` is the authoritative queue.
- The project-root boundary rule separately requires bridge, harness, dashboard, and governance work to remain under `E:\GT-KB` at `.claude/rules/project-root-boundary.md` lines 18-31.

**Risk/impact:** Once hosted-application state is active, an agent may be unable to file bridge proposals, NO-GO/GO responses, verification reports, or workspace-governance audit records. That breaks the required audit trail.

**Required revision:** Separate "work subject boundary" from "control-plane/audit artifact boundary." Hosted-application work may restrict application source writes, but must still allow the minimum GT-KB control-plane artifacts needed for bridge, durable declarations, harness state, and governance audit. Define this allowlist precisely and test it.

### F5 - Enforcement coverage is Claude-centric and misses Codex/shell write paths

**Claim:** The proposal presents hook enforcement as mechanical, but the cited implementation layers are Claude Code `Write`/`Edit` hooks and bridge helpers. They do not cover Codex `apply_patch`, shell writes, direct scripts, or other non-Claude write paths.

**Evidence:**
- The proposed enforcement targets `Write`/`Edit` hooks at lines 158-172.
- Current `.claude/settings.json` registers Claude Code hooks only; the SessionStart command is hard-coded with `--harness-name claude`, and PreToolUse hooks are Claude settings.
- Existing `bridge-compliance-gate.py` gates `Write`/`Edit`, not shell-level mutation or Codex patching.

**Risk/impact:** The architecture may pass Claude hook tests while Codex or scripts can still create mismatched bridge files or write outside the declared workspace. That gives a false sense of mechanical enforcement across the AI coding harnesses named in the owner problem.

**Required revision:** Either scope the first implementation explicitly to Claude Code and document Codex as protocol-only, or add repo-native enforcement that Codex and scripts can execute before mutation. At minimum, add tests for direct helper calls, shell/script writes, and Codex review behavior so the unsupported paths are visible.

### F6 - Prompt handling does not fully encode the interrogation contract

**Claim:** The proposed prompt recognizer can update the workspace on broad or ambiguous prompts without forcing the required owner confirmation that "we are working on the hosted application."

**Evidence:**
- The owner directive in the proposal says any off-default signal must stop and interrogate until the owner explicitly states hosted-application work at lines 10-18.
- The recognizer accepts `set workspace to Agent Red`, `set workspace to agent-red`, and the generic `change workspace to <value>` at lines 138-148.

**Risk/impact:** Broad prompt matching can turn a mention of Agent Red, a path, or a non-canonical value into an active exception. That violates the no-inference/interrogation contract.

**Required revision:** Make `gt-kb` the only non-interactive transition. Any off-default prompt that is not the exact canonical hosted-application confirmation should produce a single owner-question checkpoint and must not update the durable record until the confirmation is received.

## Additional Required Revision

The proposal needs a complete spec-to-test mapping before approval. Lines 47-48 only say tests will derive from the DCLs, and the implementation table lists broad validations at lines 188-198. The revised proposal should map each linked or newly filed DCL/ADR to concrete tests, including:

- missing record resolves to `gt-kb`;
- malformed or stale exception record behavior;
- per-harness/project divergence behavior;
- canonical value rejection for `agent-red` as an `active_workspace`;
- hosted-application confirmation checkpoint behavior;
- bridge/control-plane allowlist behavior during hosted-application work;
- Codex or non-Claude write-path limitations;
- bridge proposal `Active Workspace:` parsing and mismatch behavior.

## GO Conditions

A revised proposal can receive GO when it:

1. Uses only `gt-kb` and `hosted-application` as canonical workspace states.
2. Defines deterministic default behavior where absence of a valid exception mechanically resolves to `gt-kb`, with no inference fallback.
3. Defines per-harness records as audited owner-declared exceptions, not silent divergent authorities.
4. Preserves bridge/governance/control-plane audit writes while enforcing hosted-application source boundaries.
5. Explicitly scopes or implements enforcement across Claude, Codex, shell/script, and helper-write paths.
6. Implements the interrogation contract as a blocking confirmation flow for any off-default signal.
7. Provides a concrete spec-to-test mapping for each linked DCL/ADR/rule and each edge case above.

## Decision Needed From Owner

None for this review. Prime Builder can revise within the owner-stated invariants already quoted in the proposal.
