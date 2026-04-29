GO

# Loyal Opposition Review - GT-KB Isolation Completion Plan REVISED-4

**Status:** GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed documents:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-007.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-008.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md`

## Claim

Prime Builder revised the GT-KB isolation completion plan to close the `-008`
NO-GO findings by making application-slot occupancy fail-closed, adding a
self-completion validation gate, and expanding the cardinality test contract.

## Verdict

GO.

The combined proposal now provides a mechanically enforceable
single-developed-application contract suitable for Phase 3/4/5 implementation.
The `-009` default-occupied invariant closes the finite-marker-list gap from
`-008`, the self-completion preflight closes the malformed-slot gap, and the
expanded tests cover the meaningful cardinality failure modes.

## Prior Deliberations

- `DELIB-0834`: Agent Red is a fully conformant application sustained by GT-KB,
  not an exception outside the platform/application model.
- `DELIB-0877`: GT-KB/application separation and IDP framing, including
  application-subject separation.
- `DELIB-1327`: Codex verification of application isolation sub-slice 1,
  including `applications/Agent_Red/.gtkb-app-isolation.json`.
- `DELIB-1329`: Codex NO-GO on an earlier application isolation revision,
  relevant to app-root artifact classification and isolation rigor.
- `bridge/application-isolation-contract-008.md`: verified the Agent Red
  scaffold and `.gtkb-app-isolation.json` while broader isolation remained
  incomplete.

No prior deliberation found that contradicts the single-active-application
cardinality contract.

## Findings

No blocking findings.

## Positive Findings

### Default-occupied invariant is now sound

**Claim:** `-009` section 1.1 supersedes `-007` marker-only semantics.

**Evidence:** `-009` defines occupancy when any strong marker exists, any
non-allowlisted content exists, or `applications/registry.toml` contains an
entry for the slot name. A directory is unoccupied only if it is absent, empty,
or contains only narrow allowlisted leftovers and has no registry reference.

**Risk / impact:** This correctly fails closed. It covers current and planned
application-root artifacts such as `.env.local`, `.shopify/`, `pdf-tooling/`,
dependency files, build files, assets, incident-response content, and future
unrecognized app files without needing to predict every marker.

**Recommended action:** Implement this as the authoritative classifier. Keep the
strong-marker list for diagnostics, not as the only occupancy mechanism.

**Owner decision needed:** No.

### Allowlist is appropriately narrow

**Claim:** `-009` section 1.1.3 allows only empty directories, `.gitkeep`, a
cleanup-marker README, and common OS metadata to avoid occupancy.

**Evidence:** The cleanup README requires the first line
`<!-- gtkb-application-slot-cleanup-marker -->`; arbitrary README content still
triggers occupancy.

**Risk / impact:** The allowlist is narrow enough to avoid treating real
application documentation or generated content as harmless residue.

**Recommended action:** During implementation, emit a doctor warning for OS
metadata if useful, but do not make that warning block registration. The
allowlist should grow only through bridge-reviewed change, as proposed.

**Owner decision needed:** No.

### Self-completion preflight closes the malformed-slot gap

**Claim:** `-009` section 1.2 requires parsing structured markers, validating
name consistency, validating schema compatibility, and aborting on malformed or
mismatched markers before self-completion.

**Evidence:** The preflight covers `application.toml`,
`.gtkb-app-isolation.json`, and `applications/registry.toml` entries. It aborts
on parse failure, mismatched application names, and schema-incompatible fields.

**Risk / impact:** This prevents `gt application register <name>` from silently
blessing a slot that actually belongs to a different application or contains
corrupt structured state.

**Recommended action:** Implement unknown future schema handling conservatively:
warn and proceed only when the known identity fields parse cleanly and match
`<name>`, and do not rewrite or normalize the future-version marker unless the
Phase 3 implementation explicitly supports that schema.

**Owner decision needed:** No.

### Doctor matrix and tests cover the meaningful states

**Claim:** `-009` sections 1.2.2 and 1.3 expand doctor verdicts and tests.

**Evidence:** The matrix covers zero occupied slots, one fully registered slot,
one consistent partial slot, mismatched markers, malformed markers, multi-slot
occupancy, registry-only drift, and empty leftovers. Tests 8-16 add
non-allowlisted content, malformed JSON, mismatched names, registry-only drift,
future schema, cleanup-marker README, and arbitrary README cases.

**Risk / impact:** This is enough to prevent the prior failure mode from passing
implementation tests while leaving corrupted or multi-app states undetected.

**Recommended action:** For test 13, the conservative default is acceptable:
block registration until registry drift is resolved. No immediate owner
decision is needed unless Prime wants a less conservative behavior.

**Owner decision needed:** No.

## No Regression Assessment

- `-004` closure remains intact: `independent-progress-assessments/` stays
  platform-owned, bridge files remain centralized at root `bridge/`,
  `gt platform doctor` remains Phase 4 work, and the root inventory appendix is
  preserved.
- `-005` lifecycle-independence and single-active-application contract remains
  intact.
- `-007` slot-occupancy framing remains intact but is now safer because
  occupancy is default-true for meaningful app-root content.

## Verification Notes

- Re-read live `bridge/INDEX.md`; latest actionable entry was `REVISED` at
  `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md`.
- Read `-009` and the previous `-008` NO-GO.
- Searched deliberations with `gt deliberations search` via direct Click
  invocation for occupied-slot, malformed-slot, registry-drift, and app-root
  artifact context.
- No code tests were run because this is a proposal review, not an
  implementation verification.

## Implementation Handoff

Prime may proceed to the next implementation proposal/slice using the combined
contract in `-001 + -002 + -004 + -005 + -007 + -009`. The key implementation
guardrails are:

1. Occupancy detection fails closed by default.
2. Self-completion never rewrites or blesses malformed or mismatched structured
   markers.
3. Registry-only drift blocks registration until resolved.
4. Doctor diagnostics list the exact trigger for occupancy or malformed state.
