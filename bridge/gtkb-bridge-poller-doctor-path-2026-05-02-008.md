VERIFIED

# Loyal Opposition Verification - Smart-Poller Doctor-Path Fix REVISED-1

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-007.md`
Verdict: VERIFIED

## Claim

The revised post-implementation report resolves the prior procedural NO-GO and
the implementation satisfies the approved `-003` proposal. The doctor
bridge-poller path now reads the smart-poller dispatch-state surface, the
spec-counted tests exercise the public `run_doctor(..., "dual-agent")`
surface, and the promised GOV-20 IPR/CVR document rows exist in the KB with
owner-approval evidence recorded.

## Evidence

- Live bridge state was actionable for Loyal Opposition: `bridge/INDEX.md`
  listed `REVISED:
  bridge/gtkb-bridge-poller-doctor-path-2026-05-02-007.md` as the latest status
  for this document when reviewed.
- The prior NO-GO at `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-006.md`
  was limited to the IPR/CVR acceptance-criterion state. The revised report
  changes those items from pending to inserted and cites the KB row IDs plus
  owner approval via AskUserQuestion.
- Direct KB verification using `KnowledgeDB().get_document(...)` returned:
  - `IPR-BRIDGE-POLLER-DOCTOR-PATH-001`: `version=1`,
    `category=implementation_proposal`, `status=specified`,
    `changed_by=prime-builder/claude`, `changed_at=2026-05-02T06:39:32+00:00`.
  - `CVR-BRIDGE-POLLER-DOCTOR-PATH-001`: `version=1`,
    `category=constraint_verification`, `status=verified`,
    `changed_by=prime-builder/claude`, `changed_at=2026-05-02T06:39:32+00:00`.
- `.claude/hooks/formal-artifact-approval-gate.py` defines
  `VALID_ARTIFACT_TYPES` as `deliberation`, `governance`, `requirement`,
  `protected_behavior`, `architecture_decision`, and `design_constraint`.
  Document-class IPR/CVR rows are not accepted by that hook's packet validator,
  so direct KB insertion with explicit owner approval is the applicable
  document-row path for this GOV-20 advisory-pilot slice.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` now defines
  `_BRIDGE_DISPATCH_STATE_PATH =
  Path(".gtkb-state/bridge-poller/dispatch-state.json")` and maps
  `_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}`.
- `groundtruth-kb/tests/test_doctor_bridge_poller.py` contains the public
  `run_doctor(..., "dual-agent")` coverage for TP1-TP7, including fresh,
  warning, stale/fail, missing-state, BOM tolerance, pending-count visibility,
  and claude/codex recipient distinction.
- `.claude/rules/bridge-essential.md` has the narrow Operational Mode
  reconciliation: the smart poller is canonical while healthy, retired OS
  pollers remain disabled, `bridge/INDEX.md` remains canonical workflow state,
  and VERIFIED is terminal.

## Verification Performed

```powershell
python -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py -q --tb=short
```

Observed result: `47 passed, 1 warning in 8.42s`.

```powershell
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py
```

Observed result: `All checks passed!`.

```powershell
uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent
```

Observed result: overall doctor remained `FAIL` only because of the
pre-existing/out-of-scope workspace findings already excluded by the approved
proposal. The relevant smart-poller checks passed:

```text
[OK]  claude bridge poller: OK
[OK]  codex bridge poller: OK
[OK]  smart-poller active
```

## Risk / Impact

The original risk was that the bridge audit trail would close while the
accepted GOV-20 IPR/CVR evidence was still pending. That risk is resolved: the
two rows are present in the KB and cite owner approval in their change reasons.
The remaining doctor failures are not regressions from this slice and were
explicitly out of scope in the approved proposal.

## Non-Blocking Notes

- The phrase "via formal-artifact-approval gate" in the proposal/report is
  imprecise for document-class IPR/CVR rows. The current hook gate does not
  accept a `document` artifact type, so the verified closure is direct
  `KnowledgeDB.insert_document()` with explicit owner approval recorded in the
  row and bridge audit trail.
- The live doctor command currently reports `ruff not found` inside the `uv`
  doctor environment even though `python -m ruff check ...` passed in the
  active environment. This is a tooling-environment warning, not a blocker for
  the scoped doctor-path fix.

## Decision Needed From Owner

None.

