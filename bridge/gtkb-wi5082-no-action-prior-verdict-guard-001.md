NEW

# gtkb-wi5082-no-action-prior-verdict-guard — Mechanical guard: NO-ACTION bridge writes require a prior in-thread LO verdict (Slice 2a)

bridge_kind: prime_proposal
Document: gtkb-wi5082-no-action-prior-verdict-guard
Version: 001
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-07-08 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 15b8ff86-9015-457d-b838-3ef6e4be3c73
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5082

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py", ".claude/skills/advisory-disposition/SKILL.md", ".codex/skills/advisory-disposition/SKILL.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is Slice 2a of the owner-directed NO-ACTION correction drive
(`DELIB-20260708-NO-ACTION-CORRECTION-DRIVE-APPROACH`). It mechanically prevents
the advisory-disposition NO-ACTION misuse that Slice 1 documented.

`DCL-NO-ACTION-STATUS-SEMANTICS-001` states a machine-checkable well-formedness
invariant: a NO-ACTION entry is well-formed only when a prior Loyal Opposition
GO or NO-GO verdict exists in the same numbered bridge thread for Prime Builder
to reject. Advisory threads have no prior verdict, so writing NO-ACTION to close
an advisory is always ill-formed (it flips a Prime-actionable ADVISORY into an
LO-actionable NO-ACTION with no verdict to correct -- the five WI-5034/5035/5036/
5037/5039 threads).

Per owner AUQ (`DELIB-20260708-NO-ACTION-SLICE2-MECHANICAL-GUARD`) the fix is a
mechanical guard, not skill-prose alone: the bridge-compliance-gate blocks a
`NO-ACTION` write to `bridge/<slug>-NNN.md` when no prior version in the thread
carries a GO or NO-GO status. A new `_deny_reason_for_content` first-line branch
(`first_line == "NO-ACTION"`) enumerates the thread's prior versions via the
existing `_versioned_bridge_file_groups` / `_status_from_versioned_bridge_file`
helpers and blocks when none is GO/NO-GO. The advisory-disposition skill No-op
path is amended to prescribe the correct terminal path (WITHDRAWN, or keep
ADVISORY with a recorded disposition note) and to forbid NO-ACTION, citing the
DCL. Slice 2b (separate proposal) will remediate the five existing misused
threads.

The gate's stale body-status-token block message (which omits NO-ACTION) is
corrected in the same edit for consistency; the token was already accepted by
`BRIDGE_STATUS_TOKENS`, so this is message-text only.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — governing requirement; the guard enforces its well-formedness invariant.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge status-discipline authority; the gate is the mechanical enforcement surface for bridge status rules.
- `GOV-RELIABILITY-FAST-LANE-001` — small, single-concern defect-class reliability fix under the standing fast-lane authorization.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — cross-cutting requirements should be mechanically enforced; this is the write-time enforcement layer for the NO-ACTION constraint.
- `ADR-CROSS-HARNESS-PARITY-001` — the gate and skill are harness surfaces; behavioral parity is required (see Cross-Harness Disposition).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires the Cross-Harness Disposition section because harness-surface files are targeted.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH / Project / Work Item metadata carried above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root platform files; no adopter/application file touched.

## Prior Deliberations

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — owner decision defining NO-ACTION semantics and the well-formedness invariant this guard enforces.
- `DELIB-20260708-NO-ACTION-CORRECTION-DRIVE-APPROACH` — owner decision to run the full sequenced program; this is Slice 2a.
- `DELIB-20260708-NO-ACTION-SLICE2-MECHANICAL-GUARD` — owner AUQ choosing the mechanical-guard approach over skill-prose-only.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — the governing constraint (Slice 1).
- Source LO advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-08-22-31-no-action-semantics-misuse.md`.

## Owner Decisions / Input

- `DELIB-20260708-NO-ACTION-SLICE2-MECHANICAL-GUARD` — AskUserQuestion (this session): mechanical-guard approach selected.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` and `DELIB-20260708-NO-ACTION-CORRECTION-DRIVE-APPROACH` authorize the drive.
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5082 by project membership.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-NO-ACTION-STATUS-SEMANTICS-001` supplies the well-formedness invariant the guard enforces; the owner AUQ selected the mechanical approach. No new or revised requirement is needed before implementation.

## Cross-Harness Disposition

Applicable harness-observable surfaces:
- Claude: `.claude/hooks/bridge-compliance-gate.py` gains the NO-ACTION-prior-verdict guard; `.claude/skills/advisory-disposition/SKILL.md` No-op path amended.
- Codex: the byte-identical `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (which the Codex `--audit-only` bridge-compose path runs) receives the same guard edit; `.codex/skills/advisory-disposition/SKILL.md` adapter receives the same prose.

Parity declaration: behavioral parity is required and intended. The `.claude` hook and its template are kept byte-identical (verified IDENTICAL pre-change); both receive the same guard so a NO-ACTION write lacking a prior in-thread LO verdict is blocked identically on the Claude PreToolUse surface and the Codex audit-only surface. The advisory-disposition skill prose is identical across the `.claude` source and the generated `.codex` adapter. No owner-approved typed waiver is requested.

Non-applicable harnesses: Antigravity, Cursor, Ollama, and OpenRouter have no advisory-disposition skill adapter surface (WI-4840 created only the `.claude` source and the `.codex` adapter); any future adapter would require its own parity disposition.

## Specification-Derived Verification (Spec-to-Test Mapping)

Spec-to-test mapping. Verification is a new pytest regression suite plus the existing gate suite.

| Specification | Test / command | Expected result |
| --- | --- | --- |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | New `platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py`: (a) NO-ACTION write to a thread whose priors are ADVISORY-only is BLOCKED; (b) NO-ACTION write to a thread containing a prior GO or NO-GO is ALLOWED; (c) a thread with no priors is BLOCKED. Run with `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py -q`. | pytest PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / regression | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q` (no regression from the message-text edit). | pytest PASS. |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical after the edit (diff). | Identical. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` AND `ruff format --check` on the new test plus the two edited gate files. | Clean. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection: all five target paths in-root. | In-root only. |

Command evidence (captured in the implementation report):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed .py>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed .py>
diff .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py
```

## Risk / Rollback

Risk: a too-broad guard could block a legitimate NO-ACTION write. Mitigation: the guard fires ONLY on `first_line == "NO-ACTION"` and blocks ONLY when no prior thread version is GO/NO-GO; well-formed NO-ACTION (Prime rejecting a real verdict) always has a prior GO/NO-GO and is allowed. Existing NO-ACTION files already on disk are not re-written, so the guard has no retroactive effect (consistent with the body-status-token grandfathering model). The guard is Write-only (the `Edit` tool is out of scope, matching the body-status-token rule).

Rollback: single-commit revert of the two gate edits, the new test, and the two skill edits. No KB or bridge-state mutation.

## Recommended Commit Type

fix — repairs a defect class (advisory-to-NO-ACTION misuse) by adding a write-time guard to an existing governance hook plus corrective skill guidance; no new user-facing capability or module.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
