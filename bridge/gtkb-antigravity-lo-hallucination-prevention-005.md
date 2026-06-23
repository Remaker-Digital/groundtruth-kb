REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c999bf7d-36f3-4939-a3ce-47097a8f04a3
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (::init gtkb pb); workspace E:\GT-KB

# gtkb-antigravity-lo-hallucination-prevention — Prevent fabricated NO-GO/VERIFIED review findings (full-coverage citation-verification)

bridge_kind: prime_proposal
Document: gtkb-antigravity-lo-hallucination-prevention
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-antigravity-lo-hallucination-prevention-004.md

Project Authorization: PAUTH-WI4520-LO-HARDENING-20260620
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-4520

target_paths: ["scripts/verdict_evidence_anchor_preflight.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This REVISED proposal supersedes the version 003 proposal that drew NO-GO at version 004. It implements a reusable mechanical verdict-evidence-anchor preflight (`scripts/verdict_evidence_anchor_preflight.py`) and wires it into the two enforcement chokepoints that real verdict writes traverse, so that a Loyal Opposition `NO-GO` or `VERIFIED` verdict citing a non-existent line number, an out-of-range line, or a quoted string that does not appear in the operative file is hard-blocked before it is accepted.

Version 004 finding F1 blocked because version 003 was filed as `NEW` after a prior `NO-GO`; this version is correctly filed as `REVISED` responding to version 004, restoring a clean `NO-GO -> REVISED` chain. Version 004 finding F2 required the revision to (a) prove the guard is exercised through the governed verdict-writing path and (b) explicitly map which verdict-writing paths are in scope and which are not. Both are addressed below. Per this session's owner full-coverage decision, the scope is widened from version 003 to also gate the proposal-review `GO`/`NO-GO` Write-tool path — the path on which the original WI-4520 incident actually occurred (an Antigravity proposal-review `NO-GO`).

## Verdict-Writing Path Coverage (addresses version 004 F2)

GT-KB writes bridge verdicts through more than one path; the guard is integrated at the chokepoints each path traverses, so the implementation cannot stop at a standalone checker:

1. Helper-routed verdicts — post-implementation `VERIFIED` via `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` and its `.codex` parity, plus `impl_report_bridge.py` and `revise_bridge.py` — all call `scripts/gtkb_bridge_writer.py::write_bridge_file`. IN SCOPE: the preflight is invoked inside `write_bridge_file` for `NO-GO` and `VERIFIED` content and raises a `BridgeError` subclass on an invalid anchor.
2. Proposal-review `GO`/`NO-GO` verdicts are filed via the `Write` tool (Claude) and via `apply_patch`/shell (Codex), gated by the canonical `bridge-compliance-gate` hook (`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, activated byte-for-byte to `.claude/hooks/bridge-compliance-gate.py`; Codex consumes it through `.codex/gtkb-hooks/bridge-compliance-gate*.cmd`, no separate Python copy). IN SCOPE: the hook invokes the same reusable preflight for verdict-status writes and denies the write on an invalid anchor. This is the path on which the WI-4520 incident occurred.
3. OUT OF SCOPE (documented residual): the Antigravity harness (identity C) exposes no hook event surface (`.antigravity/config.toml` lines 8-10; WI-3345 research spike) and is currently `suspended`. An Antigravity headless verdict write traverses neither chokepoint unless it routes through a `write_bridge_file`-calling helper. Bringing the hook-less Antigravity path under coverage requires routing its verdict writes through `write_bridge_file`, a separate architectural change captured as a follow-up backlog item. Until then, Antigravity verdict-citation accuracy is not mechanically enforced; this is acceptable because the harness is suspended and the two active hooked harnesses (Claude, Codex) are covered.

A single reusable module is the source of truth for the parse/validate logic; both chokepoints import it, so there is one implementation and one primary test surface, not two divergent copies.

## Hardening Mechanics & Edge Cases

- Integration & enforcement: hard-blocking by default for `NO-GO` and `VERIFIED` verdict content at both chokepoints. `GO`, `NEW`, and `REVISED` are not gated because they make no evidence-anchor claims.
- Waivers & inferences: a finding line may opt out of exact anchoring by appending `[inference]` or `[no exact anchor]`; the validator skips verification for such lines.
- Absence citations: a finding that asserts something is missing (keywords "missing", "absent", "lacks", "does not exist", or an explicit `[absent]` marker) is not required to match present content.
- Renamed/deleted files: a cited file must exist unless marked `[absent]`.
- Multi-line ranges: a `line 10-20` style range is validated to lie within file bounds.
- String citations: quoted text (`citing "..."` / `contains '...'`) is verified to appear in the cited file within a plus-or-minus-5-line window of any cited line, or anywhere in the file when no line is cited.
- Self-reference safety: the guard validates anchors against the operative file(s) the verdict cites, never against the verdict file being written.
- Conservative bias: ambiguous parses pass rather than block, so the guard fails open on uncertainty and only hard-blocks confidently-invalid anchors.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-verdict compliance and dispatcher-driven protocol integrity (the PAUTH-included spec).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals cite all relevant specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposals cite active project and authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — specification-derived testing for the implementation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — cross-cutting technical requirements are mechanically enforced via write-time plus review-time defense in depth; this guard adds a citation-accuracy check at both the writer and the compliance-gate layers.
- `GOV-STANDING-BACKLOG-001` — self-improvement/backlog tracking authority for the residual-coverage follow-up.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance stance (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers (advisory).

## Prior Deliberations

- `DELIB-20263475` — WI-4520 source report establishing the fabricated Antigravity `NO-GO` failure mode and the owner Option-A approval of a mechanical citation-verification step.
- `DELIB-20265514` — prior `NO-GO` (version 002) requiring a real enforcement path or narrowed claims.
- `DELIB-20261563` — VERIFIED "Bridge Citation Freshness Preflight": prior citation-verification machinery whose parsing/anchoring patterns this guard aligns with rather than duplicates.
- `DELIB-2186` / `DELIB-20261989` — Antigravity IDE research-spike lineage establishing the no-hook-surface constraint cited in the residual-coverage entry.
- This session's owner AskUserQuestion (full-coverage scope) is recorded as an owner-conversation deliberation; see Owner Decisions / Input.

## Owner Decisions / Input

- `DELIB-20263475` (Option A): owner approved proceeding to an implementation proposal for a mechanical verdict-evidence-anchor preflight for WI-4520. `PAUTH-WI4520-LO-HARDENING-20260620` (active) authorizes `source` and `test` mutation classes for WI-4520 under PROJECT-ANTIGRAVITY-INTEGRATION.
- This session's AskUserQuestion (2026-06-22): owner selected "Full coverage" — wire the reusable preflight into both `write_bridge_file` AND `bridge-compliance-gate.py` (covering the Claude/Codex proposal-review verdict path), with the hook-less Antigravity path documented as a tracked residual. This is the owner authorization for adding the two `bridge-compliance-gate` paths to `target_paths`. The `bridge-compliance-gate` files are hooks (source), not protected narrative artifacts, so they fall within the active PAUTH `source` mutation class.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-20263475` (Option A) plus the owner full-coverage AskUserQuestion in this session define the deliverable; no new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

All tests live in `platform_tests/scripts/test_verdict_evidence_anchor_preflight.py` and derive from the linked specifications (citation-accuracy enforcement under `GOV-FILE-BRIDGE-AUTHORITY-001` and the write-time plus review-time defense-in-depth mandate of `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`).

Unit (reusable module):
1. Valid `NO-GO` citing real line numbers and a real quoted string passes.
2. Cited file does not exist (and is not marked `[absent]`) fails.
3. Cited line number out of range fails.
4. Hallucinated quoted string (not within plus-or-minus-5 lines of the cited line) fails.
5. Path-form normalization: Windows and Unix separators resolve to the same file.
6. `[inference]`, `[no exact anchor]`, absence-keyword, and `[absent]` lines are skipped (no false block).
7. Multi-line range within bounds passes; a range exceeding file length fails.

Integration — governed verdict-writing paths (directly addresses version 004 F2):
8. `scripts.gtkb_bridge_writer.write_bridge_file` invoked with a `NO-GO` body containing a fabricated line or string anchor raises a `BridgeError` subclass; the same call with valid anchors writes the file. This exercises the helper-routed chokepoint that `write_verdict.py --finalize-verified`, `impl_report_bridge.py`, and `revise_bridge.py` all call, not just the parser.
9. The `bridge-compliance-gate` hook, invoked with a simulated PreToolUse `Write` payload for `bridge/<slug>-NNN.md` whose first token is `NO-GO` and whose body cites a fabricated anchor, emits a deny/block decision; the same payload with valid anchors is allowed. This exercises the proposal-review Write-tool chokepoint — the WI-4520 incident path.

Verification command:
```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q
```

Code-quality gates run on changed Python before the post-implementation report is filed: `ruff check` and `ruff format --check` on every changed `.py` file (these are separate gates).

## Findings Addressed (from version 004)

- F1 (P1, lifecycle): version 003 was filed as `NEW` after the version 002 `NO-GO`. This version is filed as `REVISED` with `Responds to: bridge/gtkb-antigravity-lo-hallucination-prevention-004.md`, restoring a clean `NO-GO -> REVISED` audit chain.
- F2 (P2, coverage and test): added the "Verdict-Writing Path Coverage" map (paths in and out of scope) and integration tests 8 and 9 that exercise `write_bridge_file` and the `bridge-compliance-gate` hook through the governed verdict-writing paths, not just the parser. The proposal-review Write-tool path is brought INTO scope per the owner full-coverage decision; the hook-less Antigravity path is the one documented out-of-scope residual with a tracked follow-up.
- Advisory cleanup: added the three advisory specifications (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) flagged by the version 004 applicability preflight.

## Risk / Rollback

- Risk: a false block on a legitimate verdict. Mitigated by conservative matchers (the plus-or-minus-5-line window, the absence/inference/`[absent]` opt-outs) and by blocking only on confidently-invalid anchors; ambiguous parses pass. The `[inference]` / `[no exact anchor]` override is always available.
- Risk: modifying the critical `bridge-compliance-gate` hook could destabilize bridge writes. Mitigated by keeping the new check additive and scoped to verdict-status writes (`NO-GO`/`VERIFIED`), preserving all existing gate behavior, and keeping the template and the activated copy byte-identical.
- Rollback: revert `gtkb_bridge_writer.py` and both `bridge-compliance-gate.py` copies, and delete the new preflight module and test. The guard holds no persistent state.

## Bridge Filing

Filed as the next status-bearing numbered bridge file for `gtkb-antigravity-lo-hallucination-prevention` via the governed revise helper; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
