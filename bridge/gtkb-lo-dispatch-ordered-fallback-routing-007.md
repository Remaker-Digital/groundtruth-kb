REVISED

bridge_kind: implementation_report_revision
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 007
Responds-To: bridge/gtkb-lo-dispatch-ordered-fallback-routing-006.md
Original-Implementation-Report: bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md
Prior-Revision: bridge/gtkb-lo-dispatch-ordered-fallback-routing-005.md
GO-Verdict: bridge/gtkb-lo-dispatch-ordered-fallback-routing-002.md
Recommended commit type: feat:

Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4484
Project Authorization: PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

---

# Revised Implementation Report - Ordered Fallback Routing

## Revision Claim

This revision addresses both traceability blockers in
`bridge/gtkb-lo-dispatch-ordered-fallback-routing-006.md`.

The ordered-fallback behavior is unchanged. The correction is artifact
finalization: the two WI-4484 target files are now staged as the exact durable
candidate tested below, with no remaining unstaged diff on those paths. The
previous hunk-level future-finalization plan is withdrawn; no future hunk
reconstruction is required to commit the WI-4484 target files as they were
tested.

## Implementation Claim

Standard Loyal Opposition dispatch ranks active LO dispatch candidates by
numeric `reviewer_precedence`, attempts the lowest-precedence ready candidate
first, records skipped unavailable candidates, and falls through
deterministically to the next ready candidate. Prime Builder dispatch keeps the
prior singleton-target safety behavior: multiple active Prime Builder targets
still produce a configuration failure instead of silent selection.

This does not claim full cheapest-backend operational availability. WI-4477
still governs Ollama server readiness and autostart.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner input is required.

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` is the owner-decision basis for cost-optimized automatic dispatch and the precedence posture.
- `PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484` authorizes the bounded WI-4484 implementation scope.

## Prior Deliberations And Bridge Context

- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` - approved proposal.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-002.md` - Loyal Opposition GO.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md` - first implementation report.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-004.md` - NO-GO requiring same-file overlap disclosure.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-005.md` - first revision.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-006.md` - NO-GO requiring exact artifact state.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner basis.
- `bridge/gtkb-fab-13-retention-policy-umbrella-009.md` - separate staged handoff for co-resident retention changes in `scripts/cross_harness_bridge_trigger.py`.
- `bridge/gtkb-fab-14-gate-fp-feedback-loop-011.md` - separate staged handoff for the FAB-14 implementation-authorization and gate false-positive repairs.

## Findings Addressed

### F1 - The revised report still requires future hunk-level finalization

Corrected. The future hunk-level finalization requirement no longer exists.

Current target-path status:

```text
M  platform_tests/scripts/test_cross_harness_bridge_trigger.py
M  scripts/cross_harness_bridge_trigger.py
```

Current unstaged diff for target paths:

```text
<no output>
```

The exact staged contents of both target files are now the durable candidate.
This revision asks LO to verify WI-4484 behavior against those staged files.

Same-file disclosure remains important: `scripts/cross_harness_bridge_trigger.py`
contains co-resident staged changes from other bridge threads, especially
FAB-13 retention work. Those changes are no longer an unstaged future plan and
are separately handed off in their own bridge thread. WI-4484's acceptance
claim remains the ordered-fallback behavior and Prime Builder safety boundary,
but the artifact state itself is exact and staged.

### F2 - Out-of-scope staged/unstaged files still contaminate the verification surface

Corrected. The prior out-of-scope files are no longer staged/unstaged (`MM` or
`AM`) and are no longer part of the ordered-fallback verification command set.
They are staged-only under the separate FAB-14 handoff:

```text
A  platform_tests/scripts/test_fab14_requirement_sufficiency.py
M  scripts/implementation_authorization.py
```

The rerun verification below uses only WI-4484's two target files:

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

No FAB-14 test or implementation-authorization file is included in the WI-4484
verification commands.

## Final Target-State Evidence

```powershell
git status --short -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py scripts/implementation_authorization.py platform_tests/scripts/test_fab14_requirement_sufficiency.py
```

Observed result:

```text
M  platform_tests/scripts/test_cross_harness_bridge_trigger.py
A  platform_tests/scripts/test_fab14_requirement_sufficiency.py
M  scripts/cross_harness_bridge_trigger.py
M  scripts/implementation_authorization.py
```

```powershell
git diff --name-only -- scripts/implementation_authorization.py platform_tests/scripts/test_fab14_requirement_sufficiency.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

Observed result: no output.

## Pre-Filing Preflight Subsection

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-lo-dispatch-ordered-fallback-routing --content-file .gtkb-state\bridge-revisions\drafts\gtkb-lo-dispatch-ordered-fallback-routing-007.md
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:f5228781b5fd4ea5fe0b187c4be89c40f4e7e788828f9a8e733cf395533aba53
missing_required_specs: []
missing_advisory_specs: []
warnings.missing_parent_dirs: []
```

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-lo-dispatch-ordered-fallback-routing --content-file .gtkb-state\bridge-revisions\drafts\gtkb-lo-dispatch-ordered-fallback-routing-007.md
```

Observed result:

```text
must_apply: 3
may_apply: 2
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Requirement-Derived Verification

| Spec / requirement | Evidence |
|---|---|
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Full focused trigger suite passes against the staged target files. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | Focused `ordered_fallback or prime_builder_multi_active` tests prove LO fallback behavior and Prime Builder multi-active safety. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests exercise precedence read from registry-style candidate records rather than a shadow routing authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pytest, ruff lint, and ruff format checks were rerun after target files were staged-only. |

Commands rerun after staging:

```powershell
Remove-Item Env:GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-ordered-fallback-revised-a
```

Observed result: `72 passed in 3.89s`.

```powershell
Remove-Item Env:GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "ordered_fallback or prime_builder_multi_active" --basetemp=.gtkb-state\pytest-tmp-ordered-fallback-revised-b
```

Observed result: `4 passed, 68 deselected in 1.56s`.

```powershell
python -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
```

Observed result: `All checks passed!`.

```powershell
python -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
```

Observed result: `2 files already formatted`.

## Acceptance Criteria Status

- PASS: multiple active Loyal Opposition backends no longer cause a multi-active target-resolution failure in the standard LO dispatch path.
- PASS: numeric `reviewer_precedence` determines candidate order.
- PASS: unavailable preferred candidates are skipped with recorded evidence.
- PASS: all-unavailable LO candidates record an explicit no-ready-target result.
- PASS: Prime Builder multi-active dispatch remains a configuration failure.
- PASS: target files are staged-only, with no remaining future hunk-level reconstruction.
- PASS: targeted pytest and ruff verification passed.

## Bridge Protocol Compliance

This revision will be filed as
`bridge/gtkb-lo-dispatch-ordered-fallback-routing-007.md` with a matching
`REVISED` line inserted at the top of this document's `bridge/INDEX.md` entry.
Prior versions remain on disk and in the INDEX.

## Residual Risk And Follow-Up

- WI-4477 remains necessary before the lowest-cost Ollama reviewer can be treated as reliably available.
- Co-resident staged changes in `scripts/cross_harness_bridge_trigger.py` are disclosed and separately handed off; LO can verify WI-4484 behavior against the exact staged file.

## Recommended Commit Type

`feat:` - adds deterministic cost-optimized fallback routing behavior to the
existing Loyal Opposition dispatcher.
