---
name: lo-opportunity-radar
description: Bias Loyal Opposition review toward finding token-savings opportunities and deterministic-service / automation candidates alongside defects. Use during Loyal Opposition review, evaluation, advisory, bridge-verdict, or wrap-up work, or when asked to scan for automation or efficiency opportunities.
allowed-tools: Read, Grep, Glob, Bash
---

# /lo-opportunity-radar

Apply a structured "opportunity radar" pass to Loyal Opposition review work.
Standard review finds defects in the artifact under inspection; this skill
additionally makes every applicable review ask whether the work it touched
reveals a recurring manual pattern, a token-cost smell, or a deterministic
service the project should own.

This skill implements `SPEC-LO-OPPORTUNITY-RADAR-001`. It operationalizes the
strategic self-improvement directive and the deterministic-services principle
(`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`): repetitive work performed by an
AI is a defect, and noticing it is part of the review, not an afterthought.

## When to invoke

Use this skill during Loyal Opposition work that reviews, evaluates, or wraps
up substantive activity: implementation-proposal review, post-implementation
verification, advisory authoring, bridge verdicts, and session wrap-up. It is a
posture overlay on existing review skills (`code-review-audit`,
`proposal-review`), not a replacement for them.

Skip it for trivial acknowledgements and routine protocol chatter.

## The radar passes

Run these five short passes over the work in front of you. Keep each finding to
a few lines — the radar surfaces cues, it does not write essays.

### 1. Defect pass

Identify concrete errors, unsafe assumptions, contradictions, missing tests,
and governance drift. This is ordinary review; it stays first so the radar
never trades correctness for efficiency.

### 2. Token-savings pass

Look for cost the work pays with no information dividend: large repeated reads
of the same file, oversized hook payloads, noisy generated summaries, repeated
context relays, and over-broad searches that should be narrowed or cached.

### 3. Deterministic-service pass

Look for repeated manual sequences with stable inputs, objective outputs, and
idempotent behavior — the signature of work that belongs in a service rather
than a session. The AI's substantive contribution being a small fraction of
the total work is the tell.

### 4. Surface-eligibility pass

For each candidate from passes 2 and 3, classify where it belongs:
hook, benchmark, doctor check, `gt` CLI command, standalone script, or
skill-only guidance. State the residual human judgement that cannot be
made deterministic.

### 5. Routing pass

If a finding is material, record it as a Loyal Opposition advisory in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. The existing
advisory-router (`scripts/advisory_backlog_router.py`, registered as a Stop
hook) converts written advisories into MemBase work items idempotently. Do not
mutate the backlog directly from this skill — detection is read-only; backlog
promotion happens downstream through the advisory and the router.

## Output discipline

A radar pass produces compact cues, not a report. For each material finding
note: the observed pattern, the candidate deterministic replacement, the
recommended surface, and the residual human judgement. One advisory may carry
several findings. When nothing material is found, say so in one line and move
on — a silent radar and a noisy radar are both failures.

## Scope

This skill is the first slice of `SPEC-LO-OPPORTUNITY-RADAR-001`: a review
posture delivered as guidance. The deterministic radar scanner, a `gt check`
CLI surface, and dedicated radar hook surfaces are deferred and out of scope
until a future owner decision authorizes them.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
