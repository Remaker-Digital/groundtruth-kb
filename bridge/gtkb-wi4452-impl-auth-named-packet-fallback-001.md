NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi4452-impl-auth-named-packet-fallback
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4452
Related Work Item: WI-4443
target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py"]

# WI-4452 Implementation Authorization Named-Packet Fallback Proposal

## Claim

Fix the implementation-start authorization global-pointer race by allowing the gate to use the by-bridge named packet cache when `current.json` is absent or points at the wrong bridge, but only when exactly one currently valid named packet authorizes every protected target in the attempted mutation.

This resolves WI-4452 and the duplicate/sibling defect WI-4443 without changing the bridge GO requirement, target-path enforcement, expiry checks, post-GO review freeze, or project-authorization drift checks.

## Defect / Reproduction

`scripts/implementation_authorization.py begin --bridge-id <X>` writes both:

- `.gtkb-state/implementation-authorizations/current.json`
- `.gtkb-state/implementation-authorizations/by-bridge/<X>.json`

The named by-bridge packet survives concurrent work, but `validate_targets()` currently calls `load_packet()`, which reads only the single global `current.json` pointer. If another active Prime session runs `begin --bridge-id <Y>`, `current.json` is overwritten with bridge Y. A still-authorized bridge X mutation then blocks even though `by-bridge/<X>.json` remains valid.

Existing regression `test_gate_unchanged_reads_current_json_only` intentionally locks that old behavior, so the implementation must update the test contract as part of the fix.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the gate must still require live bridge GO authorization before protected implementation mutations.
- `GOV-RELIABILITY-FAST-LANE-001` - this is a small reliability fix for the implementation-start gate under the standing fast-lane PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares concrete target paths, work-item linkage, and governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is regression-driven and mapped to the gate contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the fix must not create a bypass; it may only select among already-issued, still-valid GO packets.
- `GOV-STANDING-BACKLOG-001` - WI-4452 and WI-4443 are durable backlog records being closed through bridge-reviewed implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the old test contract is being intentionally superseded by a bridge-reviewed defect fix rather than silently rewritten.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - VERIFIED bridge evidence should retire both linked backlog defects if the implementation passes review.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner-approved reliability fast-lane authorization for small defect/reliability fixes in `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20261667` - session-captured evidence that concurrent `begin --bridge-id` calls clobber the active `current.json` pointer and block authorized work.
- `WI-4452` - primary P0 backlog defect: concurrent `begin --bridge-id X` clobbers another active session's current packet.
- `WI-4443` - sibling P0 backlog defect: `load_packet()` validates only the single global `current.json`, so by-bridge packets cannot coexist without repeated activation.

No contrary prior deliberation was found in the current local evidence review. The existing current-json-only regression is treated as the obsolete contract being replaced by this proposal.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped reliability fix.

The implementation is a stricter use of already-approved authorization packets, not a new authorization model: every packet considered by fallback must pass the same live bridge, expiry, GO-file, post-GO chain, target-path, and project-authorization validation already used by `load_packet()` and `load_named_packet()`.

## Proposed Scope

1. Add an authorization resolver in `scripts/implementation_authorization.py` that:
   - normalizes the protected target paths once;
   - first accepts `current.json` when it is valid and authorizes all protected targets;
   - otherwise scans `by-bridge/*.json` through `load_named_packet()` and collects currently valid packets that authorize all protected targets;
   - returns the single matching named packet when exactly one valid named packet matches;
   - fails closed when zero or multiple valid named packets match.
2. Update `validate_targets()` to use that resolver while preserving its existing return shape (`packet`, `targets`) for callers.
3. Update gate-facing messaging in `scripts/implementation_start_gate.py` only if needed to mention named-packet fallback or ambiguity clearly.
4. Replace the old current-json-only gate regression with coverage for unique named-packet fallback.
5. Add an ambiguity regression proving the gate blocks if more than one valid named packet authorizes the same protected target.
6. Add or update direct authorization tests proving concurrent bridge A / bridge B begins no longer clobber each other when their target paths are distinct.

No bridge writer, hook registration, dispatch routing, MemBase schema, or project-authorization semantics are in scope.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification command |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused gate tests prove protected mutations still require a valid GO packet; named fallback uses `load_named_packet()` validation and fails closed on ambiguity. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff review confirms the change is limited to the gate/authorization reliability surface and tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation report carries forward this proposal, work-item IDs, target paths, and spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py::<new_named_fallback_tests> platform_tests/scripts/test_implementation_authorization.py::<new_concurrent_packet_test> -q --tb=short` |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Regression tests prove fallback does not authorize absent, expired, post-GO-review, or ambiguous named packets. |
| `GOV-STANDING-BACKLOG-001` | Post-VERIFIED reconciliation links this thread to WI-4452 and WI-4443. |

Minimum command set for the implementation report:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
```

## Acceptance Criteria

- Two concurrent GO bridge packets with disjoint `target_paths` can both authorize their own protected mutations after the second `begin` overwrites `current.json`.
- A valid named packet alone can authorize a protected mutation only when it is the unique valid named packet covering all protected targets.
- If multiple valid named packets cover the same protected target, the gate blocks with an ambiguity reason and tells the operator to activate or re-issue the intended packet.
- Existing missing-packet, out-of-scope target, expired packet, post-GO review freeze, and project-authorization drift protections remain intact.
- WI-4452 and WI-4443 can be linked to the final VERIFIED bridge thread for mechanical backlog retirement.

## Risks / Rollback

Residual risk is that named-packet fallback could accidentally broaden authorization if it selected stale or overlapping packets. The implementation counters this by using `load_named_packet()` for every candidate and failing closed unless exactly one valid packet authorizes the full protected target set.

Rollback is a normal revert of the code/test changes in the listed target paths. Bridge files remain append-only.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`fix`
