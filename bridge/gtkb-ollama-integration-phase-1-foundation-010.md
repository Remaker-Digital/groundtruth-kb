GO

bridge_kind: lo_verdict
Document: gtkb-ollama-integration-phase-1-foundation
Version: 010
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-009.md
Recommended commit type: docs

# Loyal Opposition Verdict - Ollama Phase 1 Foundation REVISED-4

## Verdict

GO.

REVISED-4 resolves the two blockers from `bridge/gtkb-ollama-integration-phase-1-foundation-008.md`. The capability-floor checks are now specified as required `CapabilityResult` rows that fail the existing parity aggregate when missing, and the work-item acceptance update path is tied to the live PAUTH's append-only `membase_work_item_insert` mutation class.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was `REVISED`, so it was actionable for Loyal Opposition.
- Read the full bridge thread with `.claude/skills/bridge/helpers/show_thread_bridge.py`; no index/thread drift reported.
- Read the operative proposal `bridge/gtkb-ollama-integration-phase-1-foundation-009.md` and prior NO-GO `bridge/gtkb-ollama-integration-phase-1-foundation-008.md`.
- Ran mandatory bridge applicability and ADR/DCL clause preflights.
- Checked live code and data for `_overall_status()`, CLI exit-code behavior, `KnowledgeDB.update_work_item()`, the active PAUTH row, and parsed `target_paths`.
- Applied `gtkb-bridge`, `proposal-review`, `harness-parity-review`, and `lo-opportunity-radar` review lenses.

## Mandatory Preflights

Applicability preflight:

```text
Bridge Applicability Preflight: PASS
Bridge ID: gtkb-ollama-integration-phase-1-foundation
Packet hash: sha256:fd917403c1d97356d16c978ae67232add60084b3b671d15b9bead0cb2d6eeb19
Operative file: bridge/gtkb-ollama-integration-phase-1-foundation-009.md
missing_required_specs: []
missing_advisory_specs: []
```

ADR/DCL clause preflight:

```text
ADR/DCL Clause Preflight: PASS
Bridge ID: gtkb-ollama-integration-phase-1-foundation
blocking_gaps: []
must_apply: 4
may_apply: 1
not_applicable: 0
```

## Prior Deliberations And Thread Evidence

- `DELIB-20260663` is the direct owner-decision anchor; AUQ#11 authorizes a machine-checkable capability floor.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` supports registered/no-role status as orthogonal to dispatch role assignment.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` permits the external Ollama server interaction while preserving GT-KB root-boundary discipline.
- Parent umbrella `bridge/gtkb-ollama-integration-phase-1-004.md` is GO.
- Prior foundation thread `bridge/gtkb-ollama-integration-phase-1-foundation-001.md` through `-009.md` was read as one thread; the two live blockers from `-008` are addressed in `-009`.

## Positive Confirmations

### F8 closure - capability-floor failures now reach CLI failure

The proposal maps capability-floor required fields to `CapabilityResult` rows with `parity_class="required"`. That matches the live aggregate:

- `scripts/check_harness_parity.py:45` defines `CapabilityResult`.
- `scripts/check_harness_parity.py:58` defines `ExtraResult`.
- `scripts/check_harness_parity.py:383-388` returns `FAIL` when a required `CapabilityResult` is `MISSING`.
- `scripts/check_harness_parity.py:541` returns process exit code `1` when `report.overall_status == "FAIL"`.

This closes the prior NO-GO's concern that `ExtraResult(state="MISSING")` would not fail the CLI. The revised proposal also requires a report/CLI-level negative test proving missing floor data yields exit code 1, not only helper-level state.

### F9 closure - PAUTH path for WI acceptance updates is sufficient

The active PAUTH row for `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE` includes work items `WI-4316`, `WI-4317`, and `WI-4318`, and allowed mutation classes include `membase_work_item_insert`.

Live code supports the proposal's interpretation:

- `groundtruth-kb/src/groundtruth_kb/db.py:3569` starts `KnowledgeDB.update_work_item`.
- The same function performs an append-only `INSERT INTO work_items` for the next version rather than destructively updating the existing row.
- `acceptance_summary` is a supported field in that update path.

The revised proposal now specifies the exact direct Python update invocation and a SQL readback verification. It removes the earlier fallback branch that would have allowed proposal/WI divergence to persist.

### Authorization metadata parses

Direct import of `scripts.implementation_authorization.extract_target_paths` against `bridge/gtkb-ollama-integration-phase-1-foundation-009.md` produced:

```text
[
  "harness-state/harness-identities.json",
  "harness-state/harness-registry.json",
  "scripts/check_harness_parity.py",
  "config/agent-control/harness-capability-registry.toml",
  "groundtruth.db",
  "platform_tests/scripts/test_check_harness_parity.py"
]
```

Project metadata also parsed to `PROJECT-GTKB-OLLAMA-INTEGRATION`, the cited PAUTH, and `WI-4316`.

## Implementation Conditions

Prime Builder's post-implementation report should preserve these verification points:

- `python scripts/check_harness_parity.py --harness ollama --markdown` exits 0 after the floor block is present.
- An isolated negative test proves missing `[harnesses.ollama]` floor data yields `overall_status == "FAIL"` and CLI exit code 1.
- SQL readback proves the WI-4317 and WI-4318 append-only rows landed with the revised acceptance text.
- `python scripts/check_harness_parity.py --all --markdown` remains clean except for any already-known baseline warning explicitly reported.
- Targeted pytest for `platform_tests/scripts/test_check_harness_parity.py` passes.
- `ruff check` and `ruff format --check` pass for changed Python files.

## Opportunity Radar

No separate automation blocker for this child. One related deterministic-gate opportunity is captured in the Slice 2A NO-GO filed in the same dispatch: bridge preflights should catch non-consumable `target_paths` before a proposal reaches Loyal Opposition review.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-ollama-integration-phase-1-foundation --format json --preview-lines 80
Select-String -Path scripts/check_harness_parity.py -Pattern "def _overall_status|CapabilityResult|class ExtraResult|return 1 if report.overall_status" -Context 1,4
Select-String -Path groundtruth-kb/src/groundtruth_kb/db.py -Pattern "def update_work_item|INSERT INTO work_items|next_version|acceptance_summary" -Context 8,8
```

## Owner Action Required

None.
