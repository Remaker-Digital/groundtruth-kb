DEFERRED

bridge_kind: operational_state_change
Document: gtkb-harness-benchmark-scoring-pipeline
Version: 002
Responds-To: bridge/gtkb-harness-benchmark-scoring-pipeline-001.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 806e5944-602e-41ac-b030-cdd18fd50242
author_model: claude-opus-4-7
author_model_version: Claude Opus 4.7
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Hybrid scoring pipeline (WI-4583) — DEFERRED (owner-directed parking pending manifest amendment)

## Status

DEFERRED. This is owner-directed bridge parking state per
`.claude/rules/file-bridge-protocol.md` § "DEFERRED Status". It is not a Prime
Builder revision and not a Loyal Opposition verdict. The prior `-001` NEW entry
is preserved unchanged (append-only); this entry parks the thread as
non-actionable until the resume condition below is met.

## Owner Decisions / Input

- AskUserQuestion answer 2026-06-18, this session (transcript
  `806e5944-602e-41ac-b030-cdd18fd50242`): owner selected
  **"Pause 4 NEW slices, file manifest amendment first (Recommended)"** after
  being presented with the bridge-quality retrospective × benchmark synthesis
  verdict.
- AskUserQuestion answer 2026-06-18, this session (execution sequencing):
  owner selected **"File 4 DEFERRED entries now; defer amendment proposal to
  next turn (Recommended)"** authorizing immediate parking of WI-4583.
- Source synthesis evidence: bridge-quality retrospective
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/BRIDGE-QUALITY-RETROSPECTIVE-2026-06-18.md`.
- Enhancement E1 (separately captured for incorporation at REVISED):
  retrospective §11 (corrected) shows cloud-routed reviewers (Qwen3/Kimi/
  DeepSeek via harness D/F) issued NO-GO on 0–17% of verdicts vs Codex's
  ~87% on parallel workload — a reviewer-rigor signal the scorer should
  capture as a deterministic NO-GO-rate-on-seeded-defect-corpus baseline
  metric.

## Deferral Reason

The scoring slice was filed against the VERIFIED Slice-1 manifest contract
at `scripts/benchmarks/harness_quality_manifest.py`. Two `-001` design
surfaces will be invalidated by the forthcoming manifest amendment:

1. The `-001` Proposed Change keys the deterministic scorer to the
   manifest's per-family `deterministic_evidence` tokens. After R1 adds
   `author_model_configuration` to `REQUIRED_EVIDENCE_FIELDS`, the scorer's
   loader/adapter must consume the 22-field schema rather than 21.
2. The `-001` design has the scorer record a `failure_class` only via the
   evidence record from the runner. After R2 defines `FAILURE_CLASSES`, the
   scorer should also score against the closed vocabulary (e.g., penalize
   recall on a fixture whose expected `failure_class` is `claim-accuracy`
   but whose evidence carries a different value), turning `failure_class`
   into a scored dimension rather than only a passthrough field.

Additionally, retrospective §11 shows the scorer should track reviewer-rigor
as a deterministic dimension (NO-GO rate against seeded defects), which
should be in scope at REVISED rather than retrofitted post-VERIFIED.

The proposed slice mutation was NOT started: no scoring module, no tests,
and no scored output were created under `-001`. Deferral therefore carries
no implementation loss.

## Clear / Resume Condition

This thread becomes actionable again when the forthcoming bridge thread
`bridge/gtkb-harness-benchmark-manifest-amendment-*` reaches VERIFIED with
both R1 (`author_model_configuration` added to `REQUIRED_EVIDENCE_FIELDS`)
and R2 (`FAILURE_CLASSES` enumerated tuple defined) landed in
`scripts/benchmarks/harness_quality_manifest.py`.

On that VERIFIED event:

- Prime Builder reads the amended manifest's `REQUIRED_EVIDENCE_FIELDS`
  and `FAILURE_CLASSES`.
- Prime Builder files `bridge/gtkb-harness-benchmark-scoring-pipeline-003.md`
  as REVISED, updating the deterministic scorer to consume the 22-field
  schema, score against the enumerated `failure_class` vocabulary, and add
  enhancement E1 (reviewer-rigor calibration dimension —
  NO-GO-rate-on-seeded-defect-corpus as a deterministic metric grading the
  LO benchmark mode).
- Standard NEW → GO → implementation cycle resumes from the REVISED.

While this DEFERRED entry is the latest version, the thread is excluded
from Loyal Opposition's actionable queue and from headless dispatch.

## Related Threads

- `bridge/gtkb-harness-benchmark-fixture-corpus-002.md` (sibling DEFERRED,
  WI-4580).
- `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md` (sibling
  DEFERRED, WI-4581).
- `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` (sibling
  DEFERRED, WI-4584).
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md`
  (VERIFIED Slice-1 manifest/rubric being amended).
- `bridge/harness-testing-quality-benchmarking-umbrella-005.md` (VERIFIED
  umbrella sequencing).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
