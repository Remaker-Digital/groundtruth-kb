GO

# AUQ Headless Hook Launch Hygiene Exact Target Amendment — Review Verdict

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 5dd183df-8ea9-47b5-8f68-0558279a42db
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; resolved role loyal-opposition

bridge_kind: lo_verdict
Document: gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md (NEW)

Project Authorization: PAUTH-PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE-WI-4959
Project: PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE
Work Item: WI-4959
Recommended commit type: fix

---

## Verdict Summary

**GO.** This is a `scope-amendment-only` proposal (`requires_verification: false`)
that narrows the original WI-4959 GO's directory-level `target_paths` entry
`.codex/gtkb-hooks` into 16 machine-checkable exact paths, so
`impl_start_target_paths_preflight.py` (which matches target paths exactly, not
as recursive directory prefixes) stops reporting `out_of_scope_drift` when Prime
Builder edits the individual `.cmd` adapters. Every requested target path is a
strict subset of what the original `-002` GO already authorized; the amendment
adds no new product scope. Authorization, spec linkage, both mandatory
preflights, root-boundary, scope faithfulness, and premise truth all check out
against canonical state.

## Review Independence

- Amendment proposal (`-001`) author session context: `019f23f0-b16e-7481-8a18-9622ab564d50` (Codex, harness A).
- Review session context: `5dd183df-8ea9-47b5-8f68-0558279a42db` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied. The prior original-thread GO (`gtkb-auq-headless-hook-launch-hygiene-002`) was authored by a *different* Claude-B session (`d118c716-...`), which does not affect independence for this amendment thread authored by Codex A.

## Applicability Preflight

- packet_hash: `sha256:3a6d677e7fc1bec64619ccee3eb69d31d44077d9971b2a40ba622b35963d2247`
- bridge_document_name: `gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Note: the amendment cites the 3 artifact-oriented advisory specs (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001) that the original `-002` GO had flagged as `missing_advisory_specs` — an improvement over the original.

## Clause Applicability (Slice 2; mandatory gate)

- Operative file: `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md`
- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0; exit 0 (pass).
- must_apply clauses satisfied: ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING.

## Canonical Evidence Reviewed

| Claim in `-001` | Canonical source inspected | Result |
| --- | --- | --- |
| Original thread is `GO` and authorized `.codex/gtkb-hooks` | `bridge/gtkb-auq-headless-hook-launch-hygiene-001.md` line 20 (`target_paths` includes `.codex/gtkb-hooks` and `platform_tests/scripts/test_codex_hook_runtime_containment.py`); `-002.md` line 1 = `GO` | CONFIRMED — amendment's 16 targets are a strict subset of the original GO's authorized set |
| The 16 `.cmd` adapters invoke bare console-attached `python` | `grep '\bpython\b' .codex/gtkb-hooks/*.cmd` | CONFIRMED — all 15 `.cmd` files in `target_paths` invoke bare `python`; the 16th target is the regression test |
| `impl_start_target_paths_preflight.py` treats directory entry as exact | Proposal's Pre-Implementation Target Gate Evidence (`verdict: out_of_scope_drift` for the 3 `.cmd` files; `test_codex_hook_runtime_containment.py` in scope) | ACCEPTED — consistent with exact-match gate semantics; the test path was already in original scope |
| PAUTH / project / WI active | `gt projects show PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE` | CONFIRMED — project `[active]`, WI-4959 `open`, PAUTH-...-WI-4959 `active` |
| Cited anchor deliberation is genuine | `gt deliberations show DELIB-20266297` | CONFIRMED — WI-4896 dispatcher console-window suppression owner directive (2026-06-27); establishes the console-window-hygiene lineage |

## Prior Deliberations

Independent deliberation search per `.claude/rules/deliberation-protocol.md`:
- Semantic/keyword search for "AUQ headless hook launch hygiene", "implementation start target path exact directory recursive gate drift", and "dispatch OPS wave console window suppression headless" returned no matches — expected, as the cited `DELIB-20260702-*` records are same-day (2026-07-02) and not yet in the semantic index.
- Direct lookup confirmed `DELIB-20266297` (WI-4896 dispatcher console-window suppression, 2026-06-27) is genuine and on-point.
- No prior *rejected* approach or conflicting decision surfaced. The proposal's 5 cited deliberations are consistent with the WI-4959 Wave-1 lineage.

## Findings

### [P4] Recurring directory-vs-exact-path target-gate friction (backlog candidate, not a blocker)

- **Claim:** The `impl_start_target_paths_preflight.py` exact-match semantics have now forced two separate scope-amendment bridge threads in one session (this thread + `gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment`), each solely to convert a directory-level `target_paths` intent into exact file lists after a GO.
- **Evidence:** Both `-exact-target-amendment` threads filed 2026-07-02 by Codex A; both cite `out_of_scope_drift` on directory entries.
- **Risk/impact:** Low per-instance, but the pattern is recurring friction and a token/latency tax — proposals naturally think in directories while the gate requires exact files, so a directory entry silently authorizes nothing recursively.
- **Recommended action:** Capture as a strategic-self-improvement backlog item — either (a) teach proposal authoring to expand directory intents to exact files pre-GO, or (b) an owner-governed decision on whether the gate should support explicit recursive-directory authorization semantics. This is a governance/tooling improvement, not a change requested of this amendment.
- **Owner decision needed:** No (backlog capture only).

### [P4] Amendment thread not yet artifact-linked to the project record

- **Claim:** `gt projects show PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE` lists `bridge_thread:gtkb-auq-headless-hook-launch-hygiene` (the original) as the implementation-proposal artifact link, but not the amendment thread.
- **Risk/impact:** Cosmetic traceability gap; the amendment carries correct Project/PAUTH/WI metadata inline, so authorization is intact.
- **Recommended action:** Optionally add the amendment thread as an artifact link during WI-4959 implementation-report filing. Non-blocking.
- **Owner decision needed:** No.

## Prime Builder Implementation Context

- **Objective:** With this GO, the 16 exact target paths are approved implementation targets for WI-4959.
- **Next step (per proposal Acceptance Criteria):** Re-run `python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-auq-headless-hook-launch-hygiene --candidate-paths <the exact adapter list> --json` before any protected mutation. If it still reports drift after this amendment, pause again per the proposal's own acceptance criterion rather than mutating protected hook files.
- **Scope guardrail:** Permit only launcher hygiene (replace bare `python` with a hidden/no-window launcher preserving stdout/stderr for hook diagnostics) plus the focused static regression `platform_tests/scripts/test_codex_hook_runtime_containment.py`. No dispatcher topology, no OPS/lane-scoring behavior.
- **Verification obligation carried forward:** The eventual WI-4959 implementation report (under the original thread's verification obligations) must map each changed adapter to focused-test/regression evidence, run ruff on changed Python, provide Windows smoke or justified equivalent, and document the Claude/Cursor cross-harness parity disposition.

## Verdict

**GO** — approved for implementation within the exact `target_paths` enumerated in `-001`. The amendment is a faithful narrowing of the original WI-4959 GO's authorized scope; no re-verification of the amendment itself is required (`requires_verification: false`). The two P4 findings are advisory and do not gate this GO.
