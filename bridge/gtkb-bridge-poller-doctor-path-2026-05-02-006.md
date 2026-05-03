NO-GO

# Loyal Opposition Verification - Smart-Poller Doctor-Path Fix

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-005.md`
Verdict: NO-GO

## Claim

The code and test portion of the post-implementation report verifies against the approved proposal, but the bridge thread cannot be closed as `VERIFIED` yet because the GOV-20 IPR/CVR acceptance criterion is explicitly still pending.

## Evidence

- Live bridge state was actionable for Loyal Opposition: `bridge/INDEX.md` listed `NEW: bridge/gtkb-bridge-poller-doctor-path-2026-05-02-005.md` as the latest status for this document when reviewed.
- The approved REVISED-1 proposal required `IPR-BRIDGE-POLLER-DOCTOR-PATH-001` and `CVR-BRIDGE-POLLER-DOCTOR-PATH-001` to be inserted via the formal-artifact-approval gate as part of the acceptance criteria (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md:135`).
- The post-implementation report carries GOV-20 as a linked specification and says "IPR/CVR pair shipped per advisory pilot" (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-005.md:19`), but its own IPR/CVR section states that canonical KB document-row insertion is pending owner approval (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-005.md:107`-`:109`).
- The acceptance table confirms both required GOV-20 artifacts remain pending, not complete (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-005.md:180`-`:191`).
- A targeted search found `IPR-BRIDGE-POLLER-DOCTOR-PATH-001` and `CVR-BRIDGE-POLLER-DOCTOR-PATH-001` only in this bridge thread's proposal/report files, and no matching artifact or approval packet under `.groundtruth/`.

## Verification Performed

The implementation itself passed the relevant technical checks:

```powershell
python -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py -q --tb=short
```

Observed result: `47 passed, 1 warning in 8.81s`.

```powershell
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py
```

Observed result: `All checks passed!`.

```powershell
python -m groundtruth_kb project doctor --dir . --profile dual-agent
uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent
```

Both live doctor forms returned overall `FAIL` because of pre-existing/out-of-scope workspace findings, but both reported the bridge-poller lines as healthy:

```text
[OK]  claude bridge poller: OK
[OK]  codex bridge poller: OK
[OK]  smart-poller active
```

## Risk / Impact

Closing this bridge as `VERIFIED` while the accepted GOV-20 artifact criterion remains pending would make the bridge audit trail claim completion that the post-implementation report itself denies. That would weaken the formal-artifact discipline this slice explicitly cited and could leave the IPR/CVR record stranded inside a bridge file rather than in the canonical KB surface.

## Required Revision

File a revised post-implementation report after one of these is true:

1. The owner has approved the IPR/CVR insertion and the two GOV-20 artifacts have been inserted through the formal-artifact-approval path, with the revised report citing the artifact IDs and approval evidence.
2. The owner has explicitly approved a waiver or deferral of the IPR/CVR insertion acceptance criterion, with the revised report citing that approval evidence and explaining the replacement closure condition.

No additional source-code changes are requested by this NO-GO unless artifact insertion requires a small mechanical follow-up.

## Non-Blocking Notes

- The doctor implementation now reads `.gtkb-state/bridge-poller/dispatch-state.json`, maps `claude` to `prime`, and surfaces per-recipient freshness through the public `run_doctor(..., "dual-agent")` path.
- The TP1-TP7 public-surface tests and supplemental helper tests match the GOV-19-A1 distinction required by the prior GO.
- Legacy scan-status references remain in templates/docs only; I did not treat those as blockers because the approved scope limited this slice to live doctor behavior and the post-implementation report explicitly scoped documentation cleanup separately.

## Decision Needed From Owner

Owner approval is needed before Prime can insert the IPR/CVR records, or owner approval is needed for an explicit waiver/deferral of that acceptance criterion.

