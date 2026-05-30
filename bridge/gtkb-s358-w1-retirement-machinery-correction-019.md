GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-27-lo-startup
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Loyal Opposition Review - W1 Retirement-Machinery Authorization Envelope Correction

bridge_kind: loyal_opposition_review
Document: gtkb-s358-w1-retirement-machinery-correction
Version: 019
Author: Loyal Opposition (Codex harness A)
Date: 2026-05-27 UTC
Reviewed proposal: bridge/gtkb-s358-w1-retirement-machinery-correction-018.md
Verdict: GO

## Claim

The `-018` revision resolves the `-017` NO-GO blocker and is ready for Prime Builder implementation. The revision is correctly scoped as an authorization-envelope correction: it names the exact GOV v3 approval-packet path, names the exact provenance-deliberation approval-packet path, keeps `groundtruth.db` in scope, and does not propose reinserting or rewriting the already-persisted GOV v3 row or provenance deliberation.

This GO authorizes only the corrected-envelope continuation described in `-018`: regenerate the implementation-start packet from this GO, verify `path_authorized()` / validation for the three named targets, and re-file the W1 implementation report with reviewer-reproducible authorization evidence.

## Evidence

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-s358-w1-retirement-machinery-correction --format json --preview-lines 300`: live thread read; latest indexed operative file was `bridge/gtkb-s358-w1-retirement-machinery-correction-018.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction`: passed with `preflight_passed: true`, no missing required specs, and no missing advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction`: passed with 0 blocking gaps.
- `python -m groundtruth_kb deliberations get DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION --json`: confirmed the S358 owner-decision authorization for W1, including the retirement-machinery correction, GOV v3, provenance deliberation, and LO Opportunity Radar retirement.
- `python -m groundtruth_kb deliberations get DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE --json`: confirmed the provenance deliberation exists with `spec_id=GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, `work_item_id=WI-3365`, and the expected content hash.
- `Get-ChildItem` confirmed both exact approval-packet files exist:
  - `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`

## Prior Finding Closure

`-017` blocked verification because the actual GOV v3 approval-packet filename did not match the prior GO-derived glob. `-018` closes that defect by naming the exact deterministic filename:

```text
.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json
```

It also names the provenance packet exactly:

```text
.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json
```

and preserves `groundtruth.db` in the target list. This is the correct bridge-layer remedy for the authorization-envelope mismatch.

## Conditions For Post-Implementation Report

The next implementation report must include:

- Fresh implementation-start packet hash generated from this `-019` GO.
- Reviewer-reproducible authorization evidence for:
  - `groundtruth.db`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`
- Explicit statement that the GOV v3 row and provenance deliberation were not reinserted.
- Carry-forward evidence for the W1 behavioral implementation and the positive confirmations already established by `-017`, unless Prime Builder discovers a new independent defect.

## Risk / Impact

Risk is low because the correction is bridge-envelope metadata only. The main remaining risk is another path spelling mismatch; exact paths in `-018` materially reduce that risk.

## Owner Decision Needed

None.

File bridge scan contribution: 1 entry processed.
