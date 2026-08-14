NEW
::init gtkb lo
::open build

# Embed the Standing Directive: Every Tool Use Is a Test

bridge_kind: prime_proposal
Document: gtkb-wi6221-tool-use-is-a-test-directive
Version: 001
Author: Prime Builder (harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 2da3617e-95da-4957-bd9e-c277c7c6d051
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword

Work Item: WI-6221
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814

target_paths: [".harness-baseline-configuration/rules/governance-principles.md", ".goose/rules/governance-principles.md", ".goose/.projection-manifest.json"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-6221 (P1, GET HEALTHY PHASE 2) requires the owner's standing directive —
every skill, helper, or CLI use is a TEST of an unproven implementation — to
live in the baseline every harness inherits, not in session transcripts and
handoffs. This session alone produced eleven live tool-defect findings under
that directive (WI-6233..6237, WI-6263, WI-6264, WI-6266, WI-6267, plus the
blocked-ADVISORY and sweep findings); the directive demonstrably pays for
itself, and it currently reaches new sessions only by owner repetition.

## Scope

One new section in the baseline rule
`.harness-baseline-configuration/rules/governance-principles.md` (the
always-loaded principles surface created by the A1 split), stating:

1. Every tool, skill, helper, or CLI invocation is a test of that tool:
   inspect the output, evaluate utility, never assume correctness,
   completeness or optimality.
2. A found defect, gap, mislabel, or overlooked case is captured AT THE
   POINT OF DISCOVERY as an ADVISORY (which may become a hygiene or
   enhancement work item) — not batched to session end, and not silently
   absorbed.
3. Capture at point of discovery is not implementation approval; the
   captured item follows normal owner prioritization and the bridge
   protocol.
4. When a defect blocks the current task: document it, work around it
   through a lawful path if one exists, and file the after-action record for
   independent review.

Then re-project the Goose surface so the projection carries the directive
(`.goose/rules/governance-principles.md` plus the ownership manifest).
Other harness projections inherit it at their Phase D cutovers.

The directive text is harness-neutral (zero harness tokens; census
unaffected; the census ratchet at cap 210 stays green). This proposal
performs no MemBase mutation: it edits one baseline rule file and
re-projects one harness surface.

## Specification Links

- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — the baseline is the delivery
  surface every harness inherits (obligations 2, 3); this change is baseline
  content, so it reaches every projection mechanically.
- `GOV-STANDING-BACKLOG-001` v5 — clause 2's capture route is the MemBase
  backlog; the section binds discovery-time capture to it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifacts over transient
  conversation; the directive converts transcript-borne owner instruction
  into a governed artifact.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — clause 4's after-action route.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — governs this
  section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — governs the
  verification plan below.

## Requirement Sufficiency

Existing requirements sufficient: WI-6221 records the owner directive
(2026-08-13, repeated 2026-08-14) as its source; the change embeds an
already-given owner instruction, creating no new requirement surface.

## Spec-Derived Verification Plan

1. The baseline file contains the four-clause section (grep assertion on the
   section heading and the point-of-discovery clause).
2. `python scripts/harness_projection/project_harness.py --harness goose`
   then `--check` reports 0 drift, and the projected
   `.goose/rules/governance-principles.md` carries the section beneath the
   non-canonical stamp.
3. `python -m pytest platform_tests/scripts/test_harness_projection.py -q`
   stays 6 passed (census unchanged: the section is token-free).

## Owner Decisions / Input

- Owner standing directive, 2026-08-13 (transcript, twice) and 2026-08-14
  (restated with the ADVISORY capture vehicle): "when you are using a skill
  or a helper or a CLI, you are testing an unproven implementation…
  capture that as an ADVISORY which may become a hygiene or enhancement
  work item." WI-6221 was created by the owner to embed exactly this.
- No further owner decision is required: the wording above restates the
  directive; the baseline rule file is not a protected narrative artifact
  under the formal-approval registry (it is baseline operating content
  landed by the A1 split).

## Prior Deliberations

- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the running defect inventory the
  directive produced.
- `DELIB-20260814-PB-TOOL-TEST-FINDINGS-ADVISORY-BLOCKED` — the
  advisory-blocked capture carrying findings under this directive.
- `DELIB-20260814-CODEX-HARNESS-ROLE-INFORMATION-DELIVERY-FAILURE` — owner
  confirmation that transcript-borne direction fails to reach other
  harnesses; the baseline is the delivery mechanism.
- `bridge/gtkb-baseline-correction-and-goose-projector-slice-1-*` — the
  projection framework this change rides.

## Risk / Rollback

Additive text in one baseline rule plus a re-projection; no code, no
behavior change, no census movement. Rollback is deleting the section and
re-projecting.

## Recommended Commit Type

`docs` — governance/rule-only content change plus its mechanical
projection.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
