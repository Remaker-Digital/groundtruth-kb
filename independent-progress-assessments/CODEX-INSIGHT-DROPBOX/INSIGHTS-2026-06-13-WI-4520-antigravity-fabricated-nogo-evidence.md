Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4520

# WI-4520 Loyal Opposition Report - Antigravity Fabricated NO-GO Evidence

Date: 2026-06-13
Author: Loyal Opposition (Codex harness A)
Subject: `WI-4520` - Antigravity `gemini-2.5-flash` LO reviewer emitted a false-positive `NO-GO` with non-existent proposal evidence

## Claim

`WI-4520` is a valid bridge-review reliability defect. The Antigravity `NO-GO` at `bridge/gtkb-tafe-dispatch-tick-health-002.md` rejected the operative proposal for a placeholder that was not present in `bridge/gtkb-tafe-dispatch-tick-health-001.md`. The existing harness parity check passes, so this is not adapter drift; it is an evidence-validation/control gap in review verdict acceptance for lower-reliability LO reviewers.

No implementation approval is inferred by this report. The recommended next step is a Prime Builder implementation proposal for a narrow verdict-evidence-anchor guard or an equivalent reviewer-escalation control.

## Evidence

### Live role, bridge, and backlog state

- `python -m groundtruth_kb.cli harness roles` reports Codex harness `A` as `role: ["loyal-opposition"]`, active, and Antigravity harness `C` as `role: ["loyal-opposition"]`, active.
- Direct live `bridge/INDEX.md` read shows `gtkb-tafe-dispatch-tick-health` is terminal `VERIFIED` at `bridge/gtkb-tafe-dispatch-tick-health-006.md`; it is not currently LO-actionable.
- `.claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json` returned `LO actionable_count=0` with summary `{"ADVISORY": 11, "GO": 31, "NO-GO": 3, "VERIFIED": 188, "WITHDRAWN": 61}`.
- `python -m groundtruth_kb.cli backlog show WI-4520 --json --history` shows `WI-4520` is open, backlogged, `approval_state: "unapproved"`, and explicitly captured as a "consideration-only" strategic self-improvement item.

### The NO-GO evidence is false

`bridge/gtkb-tafe-dispatch-tick-health-002.md` says:

- line 17: the proposal "passes applicability/clause preflights cleanly" but has one document blocker.
- line 19: the blocker is alleged to be a `### Helper-suggested candidates` placeholder with `_No prior deliberations: <fill in reason before filing>._`.
- line 72: the finding claims `bridge/gtkb-tafe-dispatch-tick-health-001.md` line 86 contains that placeholder.

The operative proposal does not contain the cited content:

- `bridge/gtkb-tafe-dispatch-tick-health-001.md` line 86 is `## Implementation Plan`, not the alleged placeholder.
- Lines 78-92 of `-001.md` show Owner Decisions, Requirement Sufficiency, and the Implementation Plan heading.
- `Select-String` against `bridge/gtkb-tafe-dispatch-tick-health-001.md` for `Helper-suggested candidates`, `fill in reason`, `No prior deliberations`, and `Draft Template Placeholder` returned no matches.

The follow-on `bridge/gtkb-tafe-dispatch-tick-health-003.md` did not remove a real placeholder. Its lines 82-90 are a rewritten implementation-plan section, while the same placeholder search also returned no matches.

### Blast radius

The fabricated finding caused a needless bridge cycle:

- `-001` was a complete proposal with green applicability and clause preflights per `-002`.
- `-002` rejected it for a non-existent placeholder.
- `-003` was filed as a revision.
- `-004` then granted `GO`.
- `-005` implementation report and `-006` verification completed the thread.

This did not block final completion, but it consumed counterpart cycles and created audit-trail noise that can hide real issues behind fabricated ones.

### Harness/config context

- `harness-state/harness-registry.json` lines 66-79 configure Antigravity as `harness_type: "antigravity"` using `gemini -m gemini-2.5-flash --skip-trust -p "{{PROMPT}}" --approval-mode=yolo`.
- The same registry block records `reviewer_precedence: 20`, `role: ["loyal-opposition"]`, and `status: "active"` at lines 86-90.
- `python scripts/check_harness_parity.py --all --markdown` returned `Overall status: PASS`, `Harnesses: antigravity, claude, codex, ollama, openrouter`, `Counts: PASS: 175`, and "No parity issues found in the selected scope."

This points away from stale skill adapters or missing declared capability and toward a verdict-quality control gap.

### Existing citation tooling does not cover this failure mode

- `scripts/bridge_citation_freshness_preflight.py` is explicitly an "Advisory preflight for stale cross-thread bridge citations" at line 3. It extracts `bridge/<slug>-NNN.md` path references and status-at-version references, then warns when the cited thread/version is stale or absent.
- `.claude/hooks/bridge-compliance-gate.py` validates bridge status tokens, author metadata, preflight cleanliness for `GO`/`VERIFIED`, spec-derived verification for `VERIFIED`, project metadata for `NEW`/`REVISED`, and owner-decision sections. The hook comments at lines 148-152 explicitly exclude verdict files from the owner-decision section gate because verdicts are evidence narratives.
- The current guard set does not mechanically prove that a `NO-GO` finding's cited line number or quoted text exists in the operative file it claims to review.

## Findings

### P1 - Fabricated evidence can produce Prime-actionable `NO-GO` churn

**Observation:** Antigravity `NO-GO` `-002` cited a line and placeholder string that did not exist in operative proposal `-001`.

**Deficiency rationale:** A `NO-GO` has workflow authority. When the finding evidence is fabricated, Prime Builder is routed into revision work for a non-defect. This wastes autonomous work cycles and weakens trust in bridge verdicts, especially when a lower-capability reviewer is the sole reviewer on a dispatch.

**Proposed solution:** Add a deterministic verdict-evidence-anchor check for `NO-GO` findings. Minimum viable shape:

1. Parse verdict files for `Responds to:` or indexed operative file.
2. Extract common evidence anchors: `path line N`, quoted strings after "contains:", and finding bullets with explicit file paths.
3. Verify that the line exists and, when a quoted string is given, that the string appears either on that line or in a small nearby window.
4. For unverifiable anchors, require the verdict to mark the finding as `inference` / `no exact anchor` with rationale, or block/warn depending on reviewer class.

**Option rationale:** This is narrower than requiring second-review for every Antigravity verdict and more reliable than prompt-only hardening. It preserves Antigravity throughput for valid reviews while catching the failure class mechanically.

### P2 - Existing parity checks are necessary but insufficient for review quality

**Observation:** The harness parity checker reports full PASS across 175 checks, yet the Antigravity reviewer still produced a false-positive `NO-GO`.

**Deficiency rationale:** Capability parity proves that the harness has the declared surfaces, not that a model's generated findings are factual. Treating parity PASS as review-quality assurance would overclaim the guarantee.

**Proposed solution:** Keep harness parity as a substrate check, but add a separate "verdict evidence integrity" control. In the registry/prompt layer, consider routing weak-model `NO-GO` verdicts with unverified evidence anchors to Codex or Ollama/OpenRouter secondary review before they become Prime-actionable.

**Option rationale:** Secondary review for only anchor-failed or weak-model negative verdicts limits added latency and avoids penalizing clean `GO`/`VERIFIED` verdicts that already pass mechanical gates.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | Prevent false-positive bridge verdicts whose line/string evidence does not resolve in the operative bridge file. |
| Preconditions | File a normal implementation proposal; keep `WI-4520` open until a proposed control is approved and verified. |
| Evidence paths | `bridge/gtkb-tafe-dispatch-tick-health-001.md`, `-002.md`, `-003.md`; `scripts/bridge_citation_freshness_preflight.py`; `.claude/hooks/bridge-compliance-gate.py`; `harness-state/harness-registry.json`. |
| File touchpoints | Likely new script under `scripts/`, tests under `platform_tests/` or `groundtruth-kb/tests/`, and optional hook/dispatch integration after proposal review. |
| Implementation sequence | Start with read-only checker and fixture using the `gtkb-tafe-dispatch-tick-health` false-positive; then decide whether to wire it as warning, hard gate, or secondary-review trigger. |
| Verification steps | Unit test true positive anchors, absent quoted text, wrong line number, "inference/no exact anchor" exemption, and cross-platform path forms; run targeted pytest and ruff check/format. |
| Rollback notes | If noisy, leave checker as advisory and remove hook/dispatch enforcement while retaining the regression corpus. |
| Open decisions | Whether enforcement should be hard-block for all `NO-GO` verdicts, hard-block only for lower-precedence reviewers, or advisory plus secondary escalation. |

## Recommended Action

Prime Builder should convert `WI-4520` into a scoped bridge proposal for Slice 1: a read-only verdict-evidence-anchor checker plus regression fixtures. Do not mutate the Antigravity model assignment or reviewer precedence based on this single incident until the checker can measure whether the failure is isolated or recurring.

## Verification Performed

- Read live `bridge/INDEX.md` directly.
- Ran LO and Prime bridge scans through `.claude/skills/bridge/helpers/scan_bridge.py`.
- Queried live backlog/current work with `python -m groundtruth_kb.cli backlog list --json` and `python -m groundtruth_kb.cli backlog show WI-4520 --json --history`.
- Read the full `gtkb-tafe-dispatch-tick-health` bridge thread with `.claude/skills/bridge/helpers/show_thread_bridge.py`.
- Verified line-level evidence and absence of alleged placeholder strings with PowerShell `Get-Content` and `Select-String`.
- Ran `python scripts/check_harness_parity.py --all --markdown`; result PASS, 175 checks.
- Searched live source/config for adjacent citation/verdict guard surfaces; existing bridge citation freshness preflight is cross-thread-version scoped, not finding-evidence scoped.

