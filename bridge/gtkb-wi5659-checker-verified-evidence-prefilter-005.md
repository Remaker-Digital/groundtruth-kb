NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Report - Protected-commit checker performance: pre-filter verified-evidence packets to staged protected paths

bridge_kind: implementation_report
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 005
Date: 2026-07-23 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the GO'd (v004) WI-5659 pre-filter. `_load_verified_evidence` gained a
`protected_paths: list[str] | None = None` parameter; before the expensive
`_bridge_snapshot` + `resolve_bridge_lifecycle` per packet, it now skips any packet
whose stored `target_path_globs` authorize none of the staged protected paths. The
sole caller `_evaluate_selected` passes the staged protected paths it already
computes. `protected_paths=None` preserves the legacy full scan. On the live
472-packet load with the Slice A finalization staged set, `_load_verified_evidence`
dropped from **460.824s to 9.564s (~48x)**; `terminal_verified_packets_scanned`
stays total. No authorization semantics changed.

## Implementation Claim

The two authorized target paths were modified within the WI-5659 implementation
PAUTH scope (`source`, `test`); no other files were changed. The implementation
matches the v004 Scope Guard exactly.

## Requirement Sufficiency

Existing requirements were sufficient. `DELIB-202667184` and the implementation
PAUTH define the boundary; no new/revised requirement was needed.

## In-Root Placement Evidence

Both changed files are inside `E:\GT-KB`.

## Specification Links (carried forward from v003)

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the commit-finalization gate must run fast enough as a pre-commit hook.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived, behavior-level tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Implemented Changes

`scripts/check_protected_commit_authorization.py`:

1. `_load_verified_evidence(root, head_oid=None, protected_paths=None)` - new
   optional `protected_paths` parameter.
2. Pre-filter inserted after the cheap `bridge_id` validation and BEFORE the
   expensive `_bridge_snapshot`: `if protected_paths is not None:` skip the packet
   when `_packet_target_paths(packet)` is None or no stored glob authorizes any
   staged protected path (via the same `path_authorized` predicate that
   `_verified_authorization` uses downstream).
3. `_evaluate_selected` passes `protected_paths=protected_paths` (already computed;
   the call is reached only inside `if protected_paths:`).

`platform_tests/scripts/test_check_protected_commit_authorization.py`:

4. Two pre-existing monkeypatch lambdas for `_load_verified_evidence` updated to
   accept the new `protected_paths=None` kwarg.
5. Five new WI-5659 spec-derived tests (below).

## No-Semantic-Change Argument (binding invariant)

A packet contributes to terminal-VERIFIED evidence only when `_packet_binding_errors`
passes, which requires `tuple(_packet_target_paths(packet)) == chain.target_paths`
exactly (identical `_normalize_rel` normalization and order). So for any packet that
becomes evidence, its stored globs (the pre-filter's input) are byte-identical to the
evidence globs `_verified_authorization` later matches with the same `path_authorized`
predicate. Therefore a packet whose stored globs authorize none of the staged
protected paths could authorize none of them even if resolved - the pre-filter can
only remove non-authorizing packets, never manufacture or destroy a clearance, and it
preserves the order of surviving packets (so the cleared "source" is identical).
`verified_errors` are non-load-bearing: `_verified_authorization` ignores them and
`_evaluate_protected_path` attaches them only as diagnostic `evidence_errors` on
already-FAILING paths, so dropping the diagnostics of skipped packets cannot flip any
pass/fail outcome.

## Spec-to-Test Mapping

| Specification | Tests / evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (gate must be fast) | `test_wi5659_prefilter_scales_past_pre_commit_budget` (450 irrelevant + 1 relevant packet: only the 1 relevant packet is expensively resolved; wall-clock < 20s) + live probe 460.824s -> 9.564s on the real 472-packet load. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (behavior-derived tests) | `test_wi5659_prefilter_resolves_only_matching_packets` (only packets whose stored globs authorize a staged path reach resolution; scanned count stays total); `test_wi5659_prefilter_none_is_full_scan` (legacy full scan preserved); `test_wi5659_prefilter_preserves_authorization_outcome` (authorization-layer algebraic property); `test_wi5659_prefilter_integrated_real_chain_equivalence` (END-TO-END: real committed VERIFIED chain -> byte-identical evidence on a matching staged path, clean skip on a non-matching one, count total in both). |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation PAUTH `PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` (source+test), project, WI-5659, target paths, owner decision all cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths, outside adopter scope. |

## Commands Executed (observed results)

```text
# Full protected-commit checker suite
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q
  -> 100 passed, 1 warning in 74.49s  (95 pre-existing + 5 new WI-5659)

# WI-5659 tests (verbose)
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -k wi5659 -v
  -> 5 passed  (resolves_only_matching_packets, none_is_full_scan,
     preserves_authorization_outcome, scales_past_pre_commit_budget,
     integrated_real_chain_equivalence)

# Code-quality gates (SEPARATE gates)
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
  -> All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
  -> 2 files already formatted

# Real-world perf proof (read-only probe, live 472-packet by-bridge set)
_load_verified_evidence(root, head_oid, protected_paths=<Slice-A staged set>)
  -> 9.564s   packets_scanned=472 (total preserved)   evidence_threads=0   errors=6
  (full scan baseline measured earlier this session: 460.824s, ~978 ms/packet)
```

The residual ~9.5s is 6 broad-glob packets whose stored globs match the staged
bridge-verdict path; they all resolve to stale-thread errors (evidence_threads=0) and
contribute nothing. It is ~48x faster and far under the 2-minute pre-commit budget.
Slice A's own finalization authorizes the two source/test paths via the live WI-5659
GO packet and the verdict via transaction-local VERIFIED evidence, independent of this
committed-evidence path.

## Adversarial Verification Evidence

A 3-skeptic adversarial review (independent sub-agents, high effort) attacked the
outcome-equivalence claim before this report was filed:

- Equivalence lens: `refuted=false` - the binding invariant makes a
  skipped-packet-that-could-clear-P structurally impossible; the pre-filter can only
  remove non-authorizing packets.
- Edge-case lens: `refuted=false` - `head_oid=None` early-return, `protected_paths=[]`
  unreachable-but-latent, malformed None-glob packets, `head_entries_by_bridge`
  interaction, `terminal_verified_packets_scanned` totality, sole-caller confirmation,
  and live-GO/transaction-local independence all sound.
- Test-adequacy lens: `refuted=true (medium)` - flagged that the authorization-layer
  equivalence test recomputes its filter with the same predicate (an algebraic
  property, not an end-to-end proof) and that no test exercised real resolution + the
  binding invariant. **Remediated in this report:** added
  `test_wi5659_prefilter_integrated_real_chain_equivalence` (real committed VERIFIED
  chain, real `_load_verified_evidence`, matching vs non-matching staged path) and
  honestly reframed the algebraic test's docstring.

## Acceptance Criteria Check

- [x] `_load_verified_evidence` completes well under budget on the 400+ packet load
  (9.564s vs 460.824s; 450-packet test resolves only the 1 relevant packet).
- [x] For every staged protected path, cleared-vs-finding outcome + cleared source
  identical before/after (binding-invariant argument + integrated real-chain test).
- [x] Exactly the packets whose stored globs authorize a staged protected path are
  expensively resolved (resolution-spy tests).
- [x] Existing checker suite passes (100 passed); ruff check + format clean.

## Owner Decisions / Input

- `DELIB-202667184` - owner AUQ decision (2026-07-23) authorizing the bounded WI-5659
  finalizer 470-loop pre-filter fix (source+test, no semantic change).
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX`
  - active implementation project authorization (source+test), linked to `DELIB-202667184`.

## Prior Deliberations

- `DELIB-202667184` - owner decision for WI-5659.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-002.md` - prior NO-GO (PAUTH scope).
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md` - GO with Scope Guard this report implements.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` - preceding checker-perf slice (WI-5658).

## Files Changed

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `perf`

`perf` - performance optimization of the commit-finalization gate; no new capability, no behavior change.
