NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e150e9ce-4657-4130-9e10-af48d3e79a44
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4843 self-review verdict gate parity on the Codex apply_patch path

Document: gtkb-wi4843-self-review-verdict-gate-apply-patch-parity
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4843
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4843-SELF-REVIEW-APPLY-PATCH-PARITY

target_paths: [".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", "platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py"]

## Summary

WI-4829 added a write-time self-review gate for bridge verdicts: the Claude hook
`.claude/hooks/bridge-compliance-gate.py` (`_verdict_self_review_deny`, wired at
the Write-handling path) blocks a GO/NO-GO/VERIFIED verdict whose
`author_session_context_id` equals the `author_session_context_id` of the
artifact it reviews, via the shared comparator
`scripts/bridge_review_independence.py` (`verdict_self_review_reason`).

That gate covers the Claude Write/Edit surface. The Codex apply_patch surface has
its own bridge-compliance adapter,
`.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`, which does NOT
invoke the self-review comparator. So a self-review verdict written through Codex
apply_patch bypasses the WI-4829 gate — a harness-parity hole in a load-bearing
review-independence control. This WI closes it by wiring the same shared
comparator into the apply_patch adapter.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge authority and review-independence
  discipline; self-review verdicts must be blocked regardless of write surface.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Codex hook parity authority; the
  apply_patch adapter is the Codex interception boundary that must reach parity
  with the Claude bridge-compliance gate for this control.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  hook/test files in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4843 is the canonical backlog record for this
  work; no bulk backlog operation is performed.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the control is
  enforced mechanically on both write surfaces by spec-derived tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4843 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop; basis for the
  covering PAUTH.
- WI-4829 (resolved) — the self-review write-time gate this WI extends; built the
  shared comparator `scripts/bridge_review_independence.verdict_self_review_reason`
  and wired it into `.claude/hooks/bridge-compliance-gate.py`.
- WI-4830 (duplicate of WI-4829) — defense-in-depth self-review detection framing.
- The PAUTH PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-SELF-REVIEW-WRITE-TIME-GATE-2026-06-25
  is scoped to WI-4829 only, hence WI-4843 needs its own authorization.
- No prior deliberation rejects extending the gate to the apply_patch surface.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 and the WI-4829
self-review contract already require self-review verdicts to be blocked; this WI
brings the Codex apply_patch surface to parity with the existing Claude
enforcement. No new or revised requirement is needed; no formal spec/governance
mutation is in scope.

## Design

Single behavioral change plus tests, confined to the two authorized files:

1. `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`: when the
   apply_patch target is a versioned bridge verdict file whose first non-blank
   line is a GO/NO-GO/VERIFIED status token, invoke
   `scripts.bridge_review_independence.verdict_self_review_reason(content,
   bridge_id, project_root)` and DENY the apply_patch when it returns a reason,
   emitting the same governance message shape as the Claude hook's
   `_verdict_self_review_deny`. The bridge_id is resolved from the target file
   name the same way the existing adapter resolves it.

2. Mirror the Claude hook's defensive posture: the comparator import and
   evaluation are wrapped so that an unavailable module or an unexpected
   comparator error never breaks a legitimate apply_patch write (fail-open on
   comparator error; fail-closed only on a positive self-review reason). This
   matches the WI-4829 contract that the control must not break legitimate
   bridge writes.

No change to the shared comparator (`scripts/bridge_review_independence.py`) or
the Claude hook is required or in scope; this is purely the Codex-surface parity
wiring plus tests.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (self-review verdict via apply_patch is blocked) | test_apply_patch_self_review_verdict_blocked | platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 (independent-context verdict via apply_patch is allowed) | test_apply_patch_independent_verdict_allowed | platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (non-verdict bridge write is unaffected by the verdict self-review check) | test_apply_patch_non_verdict_write_unaffected | platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (comparator unavailable fails open, does not break a legitimate write) | test_apply_patch_self_review_comparator_unavailable_fails_open | platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py -q --tb=short
python -m ruff check .codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py
python -m ruff format --check .codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py
```

## Risk / Rollback

- Risk: an over-eager block prevents a legitimate apply_patch verdict.
  Mitigation: the comparator only returns a reason on a positive
  author-session-context match; fail-open on comparator error; the test plan
  pins the independent-context allow path and the comparator-unavailable path.
- Risk: bridge_id resolution differs from the Claude hook. Mitigation: reuse the
  adapter's existing bridge_id resolution; the test plan exercises a real
  verdict file name.
- Rollback: the change is confined to the adapter and its test; reverting the two
  files restores prior behavior. No schema, governed-record, or narrative change
  is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4843-self-review-verdict-gate-apply-patch-parity-001.md`) under
the canonical append-only numbered-file chain; revisions and verdicts are added
as new numbered files so the numbered file chain remains the canonical audit
trail per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), which minted the covering
  PAUTH PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4843-SELF-REVIEW-APPLY-PATCH-PARITY
  (allowed mutation classes: source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001). No further owner decision is required to review
  this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
