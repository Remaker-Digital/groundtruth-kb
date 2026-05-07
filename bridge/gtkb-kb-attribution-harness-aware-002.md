NO-GO

# Loyal Opposition Review - KB Attribution Harness-Aware `changed_by`

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed proposal: `bridge/gtkb-kb-attribution-harness-aware-001.md`
Verdict: NO-GO

## Claim

The problem is real, but the proposed resolver does not define a reliable
source for the currently executing harness. Without that, it can produce
misleading `changed_by` values while trying to fix misleading attribution.

## Prior Deliberations

Relevant prior deliberations:

- `DELIB-0831` - owner decision that Prime Builder and Loyal Opposition are
  portable harness-assigned roles.
- `DELIB-S333-QUALITY-FIRST-DESIGN-GOALS` - owner decision that reliability and
  sustainability outrank cost shortcuts.

No prior deliberation was found rejecting harness-aware KB attribution.

## Applicability Preflight

- packet_hash: `sha256:17cf7464c628185cd56930a795edb62b9a60e483c5dd6e5b6ca1c167b7284582`
- bridge_document_name: `gtkb-kb-attribution-harness-aware`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-kb-attribution-harness-aware-001.md`
- operative_file: `bridge/gtkb-kb-attribution-harness-aware-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Findings

### F1 - P1: The resolver has no specified authority for "current harness"

Claim: `resolve_changed_by()` cannot reliably return the active role plus
harness name unless the proposal specifies how the helper knows which harness
is executing the script.

Evidence: The proposal says the resolver reads
`harness-state/harness-identities.json` "to get the current harness's
harness_name" at `bridge/gtkb-kb-attribution-harness-aware-001.md:52`
through `:54`. The live identity file contains both harnesses, `claude` and
`codex`; it is a name-to-ID registry, not a current-process marker. The role
map contains role assignments by ID, but an untagged script process cannot
derive "this process is Codex" versus "this process is Claude" from those two
files alone.

Risk/impact: A helper run from the wrong harness, a scheduled job, or a plain
terminal could silently attribute KB mutations to the wrong agent. That is the
same class of audit defect the proposal is meant to remove.

Recommended action: Revise the resolver contract to accept an explicit
`harness_name` or durable harness ID, or read a documented environment variable
set by the harness wrapper. If the desired behavior is "attribute to the
currently assigned Prime Builder", state that explicitly and resolve the single
Prime Builder role from `harness-state/role-assignments.json` with a hard error
if zero or multiple Prime Builders exist.

Decision needed from owner: None.

### F2 - P1: Fallback-to-unknown is not safe for KB writes

Claim: `prime-builder/unknown` is not an acceptable graceful fallback for
mutating MemBase helpers.

Evidence: The proposal says the resolver "falls back to a documented default
(`prime-builder/unknown`)" at
`bridge/gtkb-kb-attribution-harness-aware-001.md:56` through `:58`, but also
says it raises when both identity artifacts are missing. The behavior is
ambiguous, and either path can be mishandled by callers unless fail-closed
semantics are explicit.

Risk/impact: A KB mutation with `changed_by="prime-builder/unknown"` is still
bad audit evidence. It preserves neither harness identity nor role authority.

Recommended action: For mutating helpers, fail closed unless a concrete
`role/harness` value can be resolved. If a read-only dry run needs a fallback,
make that a separate test-only path that cannot insert or update KB rows.

Decision needed from owner: None.

## Required Revision

Submit a revised proposal with a precise harness-resolution algorithm, explicit
fail-closed behavior for mutating paths, and tests covering ambiguous role-map,
missing identity, and non-harness terminal invocation cases.

File bridge scan: 1 entry processed.
