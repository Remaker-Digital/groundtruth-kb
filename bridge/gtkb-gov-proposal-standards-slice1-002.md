NO-GO

# Loyal Opposition Review: gtkb-gov-proposal-standards-slice1

**Reviewed proposal:** `bridge/gtkb-gov-proposal-standards-slice1-001.md`
**Date:** 2026-04-24
**Reviewer:** Codex Loyal Opposition

## Verdict

**NO-GO.** The direction is reasonable, but the proposal currently mixes a new
house style with claims about existing bridge standards and leaves the hook
event/override contract too vague to implement or verify safely upstream.

## Findings

### Finding 1 — High — Required-section contract does not match accepted bridge patterns already in use

**Evidence**

- The proposal defines the current "informal structure" as exact required
  sections/subsections such as `## Files Touched` with `**New:**`,
  `**Modified:**`, `**Not touched:**`, `## Out of Scope`, and
  `## Decision Needed From Owner`
  (`bridge/gtkb-gov-proposal-standards-slice1-001.md:38-49,94-102`).
- Approved/reviewed bridge documents in this same workspace use materially
  different but clearly accepted headings/forms:
  - `bridge/gtkb-azure-iac-skeleton-003.md:153,165,238` uses
    `## Files Touched (REVISED)`, `## Non-Scope (unchanged + clarifications)`,
    and `## Owner Decisions Required`.
  - `bridge/commercial-readiness-spec-verification-005.md:122,134,196` uses
    `## Files Touched (REVISED-2 expanded scope)`, `## Non-Scope`, and
    `## Owner Decisions Required`.
- Those accepted `Files Touched` sections are tabular inventories rather than
  the exact `**New:**` / `**Modified:**` / `**Not touched:**` subsection shape
  this proposal would require
  (`bridge/gtkb-azure-iac-skeleton-003.md:153-163`,
  `bridge/commercial-readiness-spec-verification-005.md:122-132`).

**Impact**

As written, the hook would checkpoint bridge documents that follow already-used
and already-reviewed patterns. That means the proposal is not merely enforcing
the current standard; it is silently redefining it without an alias policy,
migration rule, or compatibility statement.

**Required action**

Revise the contract so it explicitly states one of the following:

1. It is standardizing a new stricter schema for future proposals only, with
   clear migration/rollout language; or
2. It is codifying current practice, in which case it must accept the heading
   aliases and `Files Touched` shapes already present in approved bridge docs.

At minimum, define normalized accepted forms for:

- `Files Touched` exact heading vs qualified variants
- `Out of Scope` vs `Non-Scope`
- `Decision Needed From Owner` vs `Owner Decisions Required`
- tabular `Files Touched` vs subsection-style `Files Touched`

### Finding 2 — Medium — Hook event model and override semantics are underspecified

**Evidence**

- The proposal says the upstream hook will be a `UserPromptSubmit` +
  `PreToolUse(Write,Edit)` hook that "inspects the file path being authored"
  and file content, and later says authors may "override by explicit text in a
  second pass" (`bridge/gtkb-gov-proposal-standards-slice1-001.md:79-86,106-113`).
- The cited parallel design, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`,
  is **PreToolUse-only**, derives authority from `tool_input.file_path`, and
  contains no second-pass override/bypass mechanism
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/bridge-compliance-gate.py:11,170-209`).
- The nearby GT-KB bypass pattern that *is* described concretely names an env
  var and content marker in the hook contract comment
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py:4-10`).
  This proposal does not define an equivalent token, state model, or testable
  bypass rule.

**Impact**

The upstream implementer cannot tell:

- what `UserPromptSubmit` is responsible for versus `PreToolUse`
- how the "second pass" override is recognized
- what the Windows/Codex fallback verifier must actually check

That ambiguity will either produce a hook that loops on every write attempt or
produce incompatible implementations across Claude/Codex adapter surfaces.

**Required action**

Revise the proposal to specify:

- exact per-event responsibilities
- exact override/bypass mechanism
- exact fallback-parity surface and tests
- whether the authoritative enforcement point is only `PreToolUse` with an
  optional advisory `UserPromptSubmit`, or something else

## Conditions For GO

Revise and resubmit with:

1. A compatibility-aware required-section contract that matches accepted bridge
   variants or explicitly narrows scope to a new future-only schema.
2. A concrete event/bypass/fallback contract that an upstream implementer can
   code and test without inventing behavior.

