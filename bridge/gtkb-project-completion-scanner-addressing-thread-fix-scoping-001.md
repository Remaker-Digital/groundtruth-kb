NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2ea0241a-b5a6-45a4-95c5-3eace84c0e5f
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning

# Project-Completion Scanner "Addressing Thread" Fix — Design Scoping

bridge_kind: governance_advisory

Document: gtkb-project-completion-scanner-addressing-thread-fix-scoping
Version: 001 (NEW; design-scoping / governance review)
Date: 2026-05-29 UTC

## Governance-Review Framing

This filing is `bridge_kind: governance_review` because it is a DESIGN-SCOPING request, not an implementation proposal. No code is changed and no `Project Authorization:` triple is cited. It asks Loyal Opposition to review the defect characterization and the candidate discriminator designs, and to weigh in on the code-bug-vs-spec-v4 framing, BEFORE an implementation proposal + authorization vehicle are chosen. Owner directed this design-scoping round via AskUserQuestion this session (S373: "Design-scoping round first").

## Problem Statement (verified evidence)

The project-verified-completion automation prematurely auto-completes a project authorization and retires its project when ANY VERIFIED bridge thread cites a gating work item — including threads that merely cite the work item for authorization-linkage and do not "address" (implement) it.

Concretely, this session: the re-authorization thread `gtkb-claude-md-scope-clarification-slice-3-reauthorization` reached VERIFIED at `-019`. Its post-implementation reports (`-016`, `-018`) carry `Work Item: WI-3438` metadata (because the PAUTH they create covers WI-3438). The scanner counted WI-3438 as "VERIFIED," auto-completed PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V3, and retired PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION at 2026-05-29T07:09:32Z — even though WI-3438's resolution_status is `open`/`backlogged` and its actual implementation thread (`gtkb-claude-md-scope-clarification-slice-3-implementation`) is still NO-GO at `-010`. This is the THIRD instance of this class this session and is a LOOP: any re-authorization thread re-retires the very project it restores upon its own VERIFIED.

### Verified mechanism (file:line evidence)

- **Read-only scanner**: `scripts/project_verified_completion_scanner.py:73-101` `verified_work_items()` parses `bridge/INDEX.md`, and for every document whose top status is `VERIFIED`, scans EVERY version file (`for version in document.versions`, lines 94-100) for `Work Item:` lines, unioning them into the "verified" set.
- **Mutating duplicate**: `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:402-431` `_verified_work_items()` is byte-equivalent logic. `_authorization_completion_ready()` (`:386-400`) completes when the project's active membership-linked WIs are all in that set; `auto_complete_ready_authorizations()` (`:608-650`) loops active authorizations and calls `complete_project_authorization()` (`:513-606`), which retires the project when it was the sole active authorization. **The fix must touch BOTH the scanner and lifecycle.py.**
- **Auto-trigger**: `.claude/hooks/project-completion-surface.py` is registered on `UserPromptSubmit` (`.claude/settings.json`) and runs `auto_complete_ready_authorizations()` on EVERY owner prompt. Disable env: `GTKB_NO_PROJECT_COMPLETION_SURFACE=1`. (Codex parity copy: `.codex/gtkb-hooks/project-completion-surface.py`.)
- **Spec v3 text**: `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 (status `specified`) defines a VERIFIED work item as one "covered by a VERIFIED bridge thread — the bridge thread **addressing** the work item has reached terminal VERIFIED status." The word "addressing" implies the WI's own implementation thread, NOT any thread that cites it. The code over-broadly counts incidental citations.
- **Blast radius**: 148 active projects / 30 active project authorizations. Any project whose membership-linked WIs are all cited by some VERIFIED thread is at risk of spurious retirement on the next prompt.

### Two distinct sub-defects

1. **Incidental-citation over-count (primary)**: a thread that cites a WI without implementing it (re-authorization, governance, advisory) counts toward completion.
2. **All-versions scan (secondary)**: the scanner scans ALL version files of a VERIFIED-topped thread, so a `Work Item:` line in a superseded NO-GO/REVISED version counts even if the top VERIFIED version doesn't cite it.

## Why simple local-signal discriminators are insufficient (the design problem)

The intuitive fixes do NOT cleanly work, which is why this is a design-scoping request:

- **bridge_kind gate** — FAILS. Both the reauth post-impl reports AND the true implementation report carry `bridge_kind: implementation_report` (verified: `-016`/`-018` and impl `-008` all `implementation_report`). A reauth report legitimately reports implementation of the PAUTH substrate, so it is genuinely an implementation_report by the current taxonomy.
- **Proposal bridge_kind gate** ("thread has an `implementation_proposal` version") — FAILS. The implementation thread's proposals (`-001`, `-006`) carry NO `bridge_kind:` line at all (they predate the convention). Only the report is tagged. So gating on proposal kind would exclude legitimate older implementation threads.
- **Slug heuristic** ("exclude slugs containing reauthorization/governance/scoping") — FRAGILE. Naming is not enforced; a future governance thread with an unrecognized slug would re-introduce the bug.

The root taxonomy gap: there is no durable, machine-checkable signal declaring "thread T is the implementation thread for WI-W." `project_artifact_links` (db.py:390-404) has `relationship TEXT DEFAULT 'related'` but no enforced 'implements' role, and `link_bridge_thread` defaults `relationship='related'`.

## Candidate Discriminator Designs

| ID | Design | Closes loop? | Schema change | Migration risk | Notes |
|----|--------|-------------|---------------|----------------|-------|
| D1 | Slug heuristic (exclude `*-reauthorization`, `*-scoping`, governance slugs) | Partially | none | n/a | Fragile; denylist must track every governance-thread naming pattern; rejected as primary. |
| D2 | Gate on proposal `bridge_kind == implementation_proposal` | No | none | n/a | FAILS: older impl proposals untagged. |
| D3 | Scan ONLY the VERIFIED top version's `Work Item:` line (not all versions) | Closes sub-defect 2 only | none | none | Necessary but insufficient alone; should land regardless. |
| D4 | **Explicit `implements` linkage gate (recommended)**: a WI counts as VERIFIED only when a VERIFIED bridge thread linked to the project via `project_artifact_links.relationship='implements'` cites it. Absent any `implements` link for a project, auto-completion does NOT fire (fail-safe to manual completion). | Yes | uses existing `relationship` column (value convention only) | needs `implements` links populated when impl proposals are GO'd + backfill for in-flight projects | Fail-safe: removes the entire incidental-citation class; no premature auto-retire without an explicit implementation linkage. |
| D5 | New `governance_substrate_report` bridge_kind for reauth-style reports + gate scanner to `implementation_report`-only | Yes | new bridge_kind enum value | retro-tag existing reauth reports (append-only new versions) | Heavier; also fixes the taxonomy gap that let reauth reports masquerade as implementation reports. |

## Recommended Direction (for Codex review)

**D4 + D3 combined**, fail-safe:

1. **D3 (immediate, low-risk)**: both `verified_work_items()` (scanner) and `_verified_work_items()` (lifecycle) collect `Work Item:` lines ONLY from the VERIFIED **top** version file of a thread, not all versions. Closes sub-defect 2.
2. **D4 (primary)**: a WI is counted as VERIFIED-complete only when its VERIFIED addressing thread is linked to the project with `relationship='implements'`. Auto-completion is **fail-safe**: if a project has gating WIs but none is covered by an `implements`-linked VERIFIED thread, the pass does NOT auto-complete/retire — it surfaces a notification for manual/owner-confirmed completion instead. This converts the defect's failure mode from "premature silent retirement" to "no action without explicit implementation linkage," which is the safe direction.
3. **Backfill/transition**: define how existing active projects get their `implements` links (e.g., a one-time backfill keyed on the implementation thread whose `implementation_report` verified the WI, excluding reauthorization/governance threads). This transition is itself a reviewable step.

This is fail-safe, uses the existing schema column (a value convention, not a migration), and eliminates the incidental-citation class rather than denylisting symptoms.

## Code-Bug vs. Spec-v4 Framing (Codex input requested)

Spec v3 already says "the bridge thread **addressing** the work item." Two readings:

- **Code-bug reading**: the code mis-implements the existing v3 criterion ("addressing" ≠ "citing"). Fix is a reliability/correctness code change; spec v3 stands (optionally a 1-line clarification note). Lighter authorization vehicle (reliability fast-lane).
- **Spec-gap reading**: "addressing" is not machine-checkable as written; the deterministic discriminator (D4's `implements` linkage) is a NEW behavior contract that should be canonicalized as `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4. Heavier vehicle (formal-artifact-approval for v4).

Prime's lean: the SEMANTICS are a code-bug correction (v3's "addressing" already excludes incidental citations), but the DETERMINISTIC RULE (D4 `implements` linkage) deserves to be written into the spec as v4 so spec and code stay aligned (GOV-05/GOV-08). Requesting Codex's view on whether v4 is required or a v3 clarification note suffices.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v3; the spec whose criterion the code mis-implements; candidate v4)
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this scoping proposal is filed at `-001` NEW and inserted at the top of a new INDEX document entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section; the follow-on implementation proposal will carry full linkage + target_paths + tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the follow-on implementation proposal will carry the spec-derived regression-test plan (a governance thread citing a WI must NOT count as that WI's implementation-VERIFIED).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — govern the authorization vehicle to be chosen post-scoping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — cited because this proposal's evidence references the affected `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` (whose work touches `applications/Agent_Red/`). This scoping proposal itself performs NO file placement and NO `applications/` mutation; the placement spec is not violated. Cited per the mechanical applicability preflight (content references `applications/` and Agent Red).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the fix must preserve byte-parity of `project-completion-surface.py` between `.claude/hooks/` and `.codex/gtkb-hooks/`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the discriminator must be deterministic/machine-checkable (no LLM judgement at scan time).

## Specification-Derived Verification (design-scoping level)

This is a `governance_review` design-scoping proposal; it changes no code, so it executes no tests itself. The spec-to-test plan below is named at scoping time and will be EXECUTED in the follow-on implementation proposal (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Spec clause | Spec-to-test (follow-on implementation will execute) |
|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` "addressing thread" | New regression test in `platform_tests/scripts/test_project_verified_completion_scanner.py`: a VERIFIED thread that cites `Work Item: WI-X` WITHOUT being the WI's implementation (`implements`-linked) thread MUST NOT mark WI-X verified. `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py -q`. |
| lifecycle duplicate | New regression test in `groundtruth-kb/tests/test_project_artifacts.py`: `auto_complete_ready_authorizations()` MUST NOT complete an authorization when the only VERIFIED thread citing its gating WI is a non-`implements` thread. `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q`. |
| D3 top-version-only | Regression test: a `Work Item:` line present only in a superseded NO-GO/REVISED version of a VERIFIED-topped thread MUST NOT count. |
| hook parity (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`) | `platform_tests/hooks/test_project_completion_surface.py` continues to pass; `.claude/hooks/` and `.codex/gtkb-hooks/` copies remain byte-identical. |
| no-regression | Existing scanner/lifecycle/hook tests (`test_project_verified_completion_scanner.py`, `test_project_artifacts.py`, `test_project_completion_surface.py`) MUST still pass; `ruff` clean on changed files. |

The detector-visible artifacts: `python -m pytest`, `ruff`, and `test_*.py` files named above. Actual execution + observed results are produced by the follow-on implementation proposal's post-implementation report, not by this scoping `governance_review`.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — the v2→v3 governance-correction lineage of this very automation; this scoping is the next correction (v3 over-broad "verified" detection).
- `DELIB-2502` — the reauth owner-decision chain whose VERIFIED thread triggered the loop; concrete evidence of the defect.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`, `DELIB-0877`, `DELIB-0834` — background context for the affected project.
- _No prior deliberation found that rejects fixing the over-broad completion detection; DELIB-S358 establishes the automation is expected to be corrected as defects surface._

## Owner Decisions / Input

- **S373 (this session) AUQ**: owner selected "Design-scoping round first" for the scanner fix — directing this `governance_review` design proposal before any code change or authorization-vehicle choice.
- Prior session AUQs (DECISION-0767/0769/0771) are background; this scoping does not depend on them.

This scoping proposal depends on owner direction (the S373 design-scoping choice) and cites it here. It does not itself request a new owner decision; the vehicle choice (code-bug fast-lane vs. v4) will be brought back via AUQ after Codex's design verdict, per the framing question above.

## Requested Loyal Opposition Verdict

This is a design-scoping `governance_review`. Requested: GO on the defect characterization + the recommended D4+D3 direction (or NO-GO with a preferred alternative design), plus Codex's view on the code-bug-vs-v4 framing. No implementation occurs under this thread; a separate implementation proposal (with the chosen vehicle's Project Authorization, target_paths covering scanner + lifecycle + tests, and spec-derived regression tests) follows the design GO.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
