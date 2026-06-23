REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-22T19-120949Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Auto-builder Prime Builder automation

# Revised Defect-Fix Proposal - Combined changed_by attribution precedence

bridge_kind: prime_revision
Document: gtkb-gt-backlog-add-attribution-resolution
Version: 003
Date: 2026-06-22 UTC
Responds-To: bridge/gtkb-gt-backlog-add-attribution-resolution-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4367

target_paths: ["scripts/_kb_attribution.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py"]

## Claim

This revision resolves the Loyal Opposition NO-GO by combining the vendor-runtime proposal and the open-session-envelope proposal into one final precedence contract for `scripts/_kb_attribution.py`.

WI-4367 remains the vendor-runtime limb: when `gt backlog add` runs without an explicit harness name or `GTKB_HARNESS_NAME`, the resolver must not silently stamp the configured single active Prime Builder. It must first identify a positive runtime harness signal, validate that harness against the harness-state source of truth, and only then fall back to the durable single-Prime default.

The related WI-4632 limb is included in this same implementation contract because both fixes change `_resolve_harness_name()`. The implementation and verification must prove the final combined order, not two independent partial orders.

## Findings Addressed

`FINDING-P1-001` from `bridge/gtkb-gt-backlog-add-attribution-resolution-002.md` is addressed by this revision:

- Scope now includes both test modules that exercise the resolver order.
- The final combined resolver order is explicit below.
- The verification plan proves the final order as a whole, including precedence between session envelope and vendor-runtime sources.
- This proposal is paired with `bridge/gtkb-gt-backlog-add-changed-by-active-harness-003.md`, which carries the same combined contract for WI-4632.

## Combined Precedence Contract

The final `_resolve_harness_name()` order is:

1. Explicit `harness_name` argument.
2. `GTKB_HARNESS_NAME`.
3. A single unambiguous open session envelope harness name, skipped when `GTKB_BRIDGE_POLLER_RUN_ID` is set.
4. Runtime vendor-environment detection for the current process, validated against the harness-state source of truth.
5. Existing single active Prime Builder fallback.

Rationale:

- The explicit argument and `GTKB_HARNESS_NAME` are already the highest-confidence caller and dispatch sources, so their precedence is preserved.
- The open session envelope identifies the harness that owns the current interactive session. This resolves WI-4632 before durable-role fallback can substitute a different harness name.
- Runtime vendor-environment detection covers subprocesses that have no envelope-derived name in-process but still carry positive Codex or Claude runtime signals. This resolves WI-4367 before durable-role fallback can substitute the configured Prime Builder.
- The existing single active Prime Builder fallback remains available only when the higher-confidence sources are absent or ambiguous.
- Headless dispatch remains unchanged because dispatched workers already use `GTKB_HARNESS_NAME`; the envelope source is skipped under `GTKB_BRIDGE_POLLER_RUN_ID`.

The implementation must not introduce a new identity authority. Any harness name found from an envelope or vendor signal is only a candidate name and must still be validated through the existing harness identity and role resolution path. Unknown or roleless candidates must fail closed instead of returning `unknown` or a literal fallback.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `scripts/_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`

No application or adopter files are in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision returns the NO-GO proposal to the bridge for Loyal Opposition review before protected source mutation.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - `changed_by` must reflect the harness identity that performed the write, not a vendor default or configured Prime Builder substitute.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - envelope and vendor signals are candidate selectors only; final identity and role validation stays anchored in harness-state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - accurate `work_items.changed_by` provenance keeps the durable backlog artifact trail trustworthy.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries the governing specification links for the implementation scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each cited contract to a concrete test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, and Work Item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner decision is required because this is an internal attribution defect fix under standing authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the scope remains confined to GT-KB platform scripts and platform tests.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex attribution must not depend on hook environment propagation alone; resolver-side fallback is the mechanical safety net.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - provenance is an artifact-backed fact derived from the acting harness context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - work-item creation/update attribution is the lifecycle trigger protected by this fix.
- `GOV-STANDING-BACKLOG-001` - WI-4367 is a standing-backlog defect under PROJECT-GTKB-RELIABILITY-FIXES.

## Requirement Sufficiency

Existing requirements are sufficient. The harness-aware attribution contract already requires fail-closed, harness-aware `changed_by` resolution, and the session-role override contract already supports interactive role labels. The missing piece is not a new requirement; it is the final precedence order when both an interactive envelope and runtime vendor signals can exist. This revision states that order and requires tests that pin it.

No formal DA, GOV, SPEC, PB, ADR, or DCL mutation is required.

## Prior Deliberations

- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction behind `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` - prior Codex-as-Prime attribution defect in the same provenance family.
- `DELIB-20263483` - WI-4522 author identity environment alias defect.
- `DELIB-20263700` - Backlog Add CLI Slice 1 review establishing resolver-owned attribution.
- `DELIB-2026-06-14-WI4483-WI4514-CLOSE-RESOLVED-REGISTRY-CORRECTION` - prior harness role-state correction context.
- `DELIB-20264748` - prior verified backlog batch insert context.
- `DELIB-20264491` - prior work-item provenance and membership context.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this defect fix through PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` authorized the reliability-fixes proposal batch that included WI-4367.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` provides the durable fast-lane rationale.

No additional owner decision is required. This revision adds no new public surface, no destructive action, no deployment, and no new formal requirement.

## Proposed Scope

1. In `scripts/_kb_attribution.py`, add or reuse a read-only helper that returns the harness name from a single unambiguous open `harness-state/*/session-envelope.json`. The helper returns `None` for zero open envelopes, multiple open envelopes, parse failures, or headless dispatch.
2. In `scripts/_kb_attribution.py`, add or reuse a read-only helper that identifies Codex or Claude from runtime vendor environment signals and returns only a candidate harness name.
3. Update `_resolve_harness_name()` to use the combined order stated above.
4. Preserve `resolve_changed_by()` fail-closed validation so candidate names from envelope or vendor detection still require a known harness identity and durable role.
5. Add regression coverage across `platform_tests/scripts/test_kb_attribution.py` and `platform_tests/scripts/test_kb_attribution_session_role.py`.

Out of scope:

- Any `gt backlog add` public CLI change.
- Any new `--changed-by` option or literal attribution bypass.
- Any change to bridge dispatch wrappers beyond preserving existing `GTKB_HARNESS_NAME` behavior.
- Any governance-record mutation.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` | explicit argument precedence | Explicit `harness_name` wins over `GTKB_HARNESS_NAME`, an open envelope, and vendor signals. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | environment precedence | `GTKB_HARNESS_NAME` wins over an open envelope and vendor signals. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | envelope precedence | A single open envelope wins over a conflicting vendor signal and the durable Prime fallback. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Codex vendor detection | With no explicit argument, no env var, and no envelope, a Codex runtime signal resolves to the Codex harness rather than the durable Prime fallback. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Claude vendor detection | With no explicit argument, no env var, and no envelope, a Claude runtime signal resolves to the Claude harness. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | candidate validation | An envelope or vendor-detected harness name missing from the harness-state source of truth fails closed. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | ambiguity safety | Multiple open envelopes return no envelope source and defer to vendor detection or durable fallback. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | fallback preservation | With no explicit argument, no env var, no envelope, and no vendor signal, the existing single active Prime Builder fallback still resolves. |
| session-role headless invariant | headless skip | With `GTKB_BRIDGE_POLLER_RUN_ID` set, the envelope source is skipped and dispatch attribution remains driven by explicit env or durable fallback. |

Execution commands:

- `python -m pytest platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short`
- `python -m ruff check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`
- `python -m ruff format --check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`

## Acceptance Criteria

1. The final resolver order is exactly: explicit argument, `GTKB_HARNESS_NAME`, single open envelope, vendor-runtime detection, durable single-Prime fallback.
2. The WI-4367 reproduction resolves a Codex runtime signal to Codex instead of the configured Prime Builder fallback.
3. The WI-4632 reproduction resolves a single open Claude session envelope to Claude instead of the durable Prime fallback.
4. Candidate harness names from envelope and vendor detection are still validated through harness-state and fail closed when unknown or roleless.
5. Headless dispatch behavior is unchanged.
6. The focused pytest and ruff commands listed above pass.

## Risks / Rollback

- Risk: stale or concurrent session envelopes could misidentify the interactive harness. Mitigation: use the envelope source only when exactly one open envelope exists, and skip it under headless dispatch.
- Risk: stale vendor environment variables could be present in an ad-hoc shell. Mitigation: vendor detection is lower precedence than explicit argument, `GTKB_HARNESS_NAME`, and an unambiguous envelope, and candidate names still require harness-state validation.
- Risk: callers with no runtime context still need the old fallback. Mitigation: the durable single-Prime fallback is preserved as the last source.
- Rollback: revert the helper additions, the `_resolve_harness_name()` ordering change, and the added tests. No schema or data migration is involved.

## Files Expected To Change

- `scripts/_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`

## Recommended Commit Type

`fix`
