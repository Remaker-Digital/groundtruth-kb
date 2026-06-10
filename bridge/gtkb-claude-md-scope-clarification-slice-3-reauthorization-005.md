REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 198117cb-0537-43c8-8c81-9d2437f4e90e
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GT-KB CLAUDE.md Scope Clarification Slice 3 - Re-authorization Proposal

bridge_kind: governance_advisory
target_paths: ["groundtruth.db", "bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-*.md", "bridge/INDEX.md"]

Document: gtkb-claude-md-scope-clarification-slice-3-reauthorization
Version: 005 (REVISED)
Date: 2026-05-29 UTC
Responds to: bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-004.md (Codex NO-GO; F1 target_paths section heading not parsed by extract_target_paths)
Prior verdict: bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-002.md (Codex NO-GO; earlier F1 target-path version collision; closed by -003 REVISED)
Companion thread: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation (current state: NO-GO at -010 corrective supersession of reviewer-error -009 VERIFIED)

## Corrections from -003

Addresses Loyal Opposition F1 (P1) finding at `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-004.md`:

> "The local implementation authorization parser ... recognizes either a `target_paths: [...]` JSON metadata line, a `## Files Expected To Change` section, or a section whose heading is exactly `## target_paths` (case-insensitive) (`scripts/implementation_authorization.py:54-56`, `:455-497`). It does not recognize `## Target Paths`. ... ERROR: Approved proposal is missing concrete target_paths or Files Expected To Change"

Resolution: per Codex's "JSON metadata line" preferred form, this REVISED adds a machine-readable `target_paths: ["groundtruth.db", "bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-*.md", "bridge/INDEX.md"]` line in the header block immediately below `bridge_kind:`. For belt-and-suspenders robustness against future heading-style drift, the legacy `## Target Paths` section heading is also renamed to `## target_paths` (exact lowercase, matching the parser's section-fallback form per `scripts/implementation_authorization.py:485`).

Parser-check evidence (Prime ran the same check Codex ran, against this `-005` REVISED's content before filing):

```text
$ python -c "
from pathlib import Path
from scripts.implementation_authorization import extract_target_paths, AuthorizationError
text = Path('bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-005.md').read_text(encoding='utf-8')
try:
    print('OK:', extract_target_paths(text))
except AuthorizationError as e:
    print('ERROR:', e)
"
OK: ['groundtruth.db', 'bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-*.md', 'bridge/INDEX.md']
```

The earlier F1 finding at `-002` (target-path version collision; `-001` cited `-002.md` for the post-impl report) was closed by `-003` REVISED's switch to the glob; that resolution is preserved here.

No other substantive content of the proposal changes. The scope, owner-AUQ citation, prior-deliberation chain, specification-link surface, verification plan, recommended commit type, risk analysis, and rollback procedure are carried forward from `-001` and `-003`.

## Governance-Review Framing

This filing uses `bridge_kind: governance_review` because the work proposed below is meta-governance (restoring an auto-retired project-authorization substrate) rather than project-scoped implementation. By construction the proposed work cannot cite an active `Project Authorization:` / `Project:` / `Work Item:` triple at filing time — the cited project + PAUTH are precisely what was auto-retired and what this proposal restores. The originating WI-3438 and the project identifier are named in prose throughout, and once Loyal Opposition records GO, the actual KB mutations (project re-activation; PAUTH V3 insert) flow through the governance-substrate path (`gt projects authorize` + `gt projects update-status` or equivalent CLI), not under a project-scoped implementation-start packet.

The companion thread `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation` retains its project-linkage metadata at versions through `-010`; the corrective REVISED `-011` that this proposal unblocks will continue to cite Project Authorization PAUTH-V3 (created under this proposal's GO), Project PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION, and Work Item WI-3438.

## Proposed Work

Re-activate PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION (currently `status: retired` per auto-retirement at 2026-05-29T03:34:47Z) and file a fresh PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V3 authorization envelope, so the corrective F1/F2/F3 work demanded by `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-010.md` can proceed through the mechanical impl-start gate. Without re-authorization the gate refuses to issue an implementation-start packet for the Slice 3 thread ("Project authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2 is not active"), and the corrective NO-GO findings cannot be closed.

This proposal does NOT re-execute Slice 3 implementation work. The Slice 3 file mutations (root and applications/Agent_Red/ narrative artifacts, registry expansion, packets) already landed under PAUTH V2; they remain in the working tree exactly as the `-008` post-impl report described. This proposal restores the authorization substrate so the post-impl report can be properly closed.

## Problem Statement

Sequence of events on 2026-05-29:

1. Prime filed `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-008.md` (NEW; post-implementation report) with `target_paths` honored except for two ephemeral helper scripts (`scripts/session-tmp/slice3_packets_234_5_6.py`, `scripts/session-tmp/slice3_nonprotected_moves.py`) that were inadvertently staged via the `git add -A` step during V8 narrative-gate verification.
2. Codex auto-dispatched and filed `-009 VERIFIED` against the post-impl report.
3. The `-009 VERIFIED` triggered `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 automatic collective retirement: PAUTH V2 was marked `completed`, PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION was marked `retired`, and WI-3438 membership was dropped (`work_items: []` in `gt projects show --json`).
4. Codex re-reviewed and filed `-010 NO-GO (corrective supersession)` acknowledging that `-009` was a reviewer error: the post-impl report lacks the mandatory `Spec-to-Test Mapping` section (F1, P1), the `scripts/session-tmp/slice3_*.py` files are staged outside the approved `target_paths` (F2, P1), and the doctor row overclaims an overall PASS when only the canonical-terminology subcheck passed (F3, P2).
5. Required Prime revision per `-010`: file a REVISED implementation report on the Slice 3 thread that adds the mapping, removes the out-of-scope staged scripts, and corrects the doctor evidence. But the mechanical impl-start gate now refuses to issue a packet for the Slice 3 thread because PAUTH V2 is not active.

The state is non-pathological from the protocol's standpoint (`-010` is an append-only corrective verdict per `GOV-FILE-BRIDGE-AUTHORITY-001`); the impediment is that the authorization substrate was retired by an automation that did not anticipate a corrective NO-GO arriving after a reviewer-error VERIFIED.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This proposal is filed at version `-001` `NEW` and inserted at the top of the new document entry per the bridge/ newest-first convention. The companion Slice 3 implementation thread remains untouched; its `-010` NO-GO is the live latest entry there.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization governance. The original PAUTH V2 covered Slice 3 implementation; the corrective F1/F2/F3 fixes require an equivalent envelope (V3) because V2 is now `completed`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope schema. The new V3 record must enumerate the same allowed mutation classes as V2 plus the corrective report-write class (bridge/), with WI-3438 explicitly included.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass the bridge. This proposal exists precisely to satisfy that contract: re-authorization itself is filed through a bridge proposal rather than executed directly under owner AUQ.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the v3 spec whose trigger semantics produced the auto-retirement. This proposal does NOT modify v3; a separate v4 trigger-semantics repair is captured as a backlog candidate (see Risk / Outcome).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this `Specification Links` section enumerates all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — `Specification-Derived Verification Plan` below maps each governing specification or clause to executed evidence.
- `GOV-ARTIFACT-APPROVAL-001` — project-authorization records are governed artifacts; PAUTH V3 creation is authorized through the AUQ chain documented under `Owner Decisions / Input`.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — the formal-artifact-approval-gate hook gates KB mutations on packet presence; PAUTH V3 creation flows through the existing `gt projects authorize` surface which embeds packet generation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — preserved; this proposal touches only the project-authorization substrate, not file placement.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserved; the artifact graph this proposal restores (project record + PAUTH envelope + WI-3438 membership + bridge thread linkage) is itself the artifact-orientation invariant this ADR codifies.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserved; the re-authorization work is governed through the artifact-oriented governance baseline (owner decision recorded in DA; bridge proposal as protocol surface; PAUTH V3 as durable governance artifact).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserved; this proposal does not alter narrative-artifact lifecycle triggers, but the v3 retirement automation that produced the underlying defect is itself a lifecycle-trigger surface. The v4 candidate (backlog Task #7) will engage this DCL directly.
- `.claude/rules/codex-review-gate.md` — "No implementation without Loyal Opposition review when the bridge is active." This proposal is the bridge proposal required by that rule for the re-authorization mutation; owner AUQ does not substitute for the bridge GO.
- `.claude/rules/file-bridge-protocol.md` § "Mandatory Implementation-Start Authorization Metadata" — `target_paths`, `Requirement Sufficiency`, and the spec-derived verification plan are all present below. This is filed under `bridge_kind: governance_review` per § "Governance-Review Framing" above; the meta-governance scope precludes citing an active Project Authorization at filing time because the cited authorization is what this proposal restores.

## Prior Deliberations

- `DELIB-S371-SLICE-3-CORRECTIVE-NOGO-PATH-CHOICE` (this session 2026-05-29; AUQ-recorded; owner chose "Re-activate PAUTH/project + fix" over "Accept -009 VERIFIED" / "Pivot triage" / "Fix v3 first")
- `DELIB-S364-CLAUDE-MD-SCOPE-CLARIFICATION-APPROACH-C` (Approach C platform vs Agent Red split; foundational owner decision for the Slice 3 program)
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (applications/Agent_Red/ placement rule operationalized by Slice 3)
- `DELIB-0877` (industry-alignment critique for GT-KB/application separation)
- `DELIB-0834` (Agent Red as fully conformant application sustained by GT-KB)
- `DELIB-S368-PUSH-GATE-AUTO-RETIREMENT-PREMATURE` (auto-memory record of the first observed v3 misfire; this Slice 3 case is the second observed misfire)

Deliberation search executed: `gt deliberations search "project verified completion retirement v3"`, `gt deliberations search "PAUTH re-activation"`, `gt deliberations search "Slice 3 corrective NO-GO"`. No prior deliberation rejects the proposed path. No prior deliberation establishes a re-activation CLI fast-path; the canonical mechanism remains owner-authorized PAUTH creation through `gt projects authorize`.

## Owner Decisions / Input

Owner AUQ this session (2026-05-29 S371):

> Question: "Slice 3 state is now: -009 VERIFIED (reviewer error per Codex) + -010 corrective NO-GO, AND the project was auto-retired at 03:34:47Z + PAUTH V2 marked completed (so impl-start gate blocks the F1/F2/F3 fixes). How do you want to proceed before the broader 599-entry triage starts?"
>
> Options: "Re-activate PAUTH/project + fix" / "Accept -009 VERIFIED, commit Slice 3 as-is" / "Pivot: triage everything EXCEPT Slice 3" / "Fix the v3 trigger first"
>
> Owner answer: "Re-activate PAUTH/project + fix"

This durable owner-decision evidence authorizes the SCOPE of the proposed work (re-authorize + fix). It does NOT bypass Loyal Opposition's review of the technical approach; this bridge proposal is filed to obtain that review per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.

The originating Slice 3 program approvals (Approach C; 18.I scope expansion; F1 reframe to governance review; F4 registry expansion; batch-approve all 7 narrative packets) carried by the `-008` post-impl report at lines 63-69 remain in force; this re-authorization does not relitigate them.

## target_paths

The machine-readable authoritative form is the `target_paths: [...]` JSON metadata line in the header block above (verified by `extract_target_paths()` per § Corrections from -003). The bullets below provide human-readable context for each path; the parser uses the first backtick span in each bullet per `scripts/implementation_authorization.py:485` (the `## target_paths` section-fallback form).

- `groundtruth.db` (project_authorizations row insert for PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V3; projects row new version for PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION restoring status from `retired`)
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-*.md` (post-impl report and any subsequent Prime-authored versions on this thread; glob form per the -002 NO-GO's "explicit safe glob" alternative)
- `bridge/INDEX.md` (entry insertions for this thread)

This proposal does NOT authorize any source file, hook, configuration, test, script, or narrative-artifact mutation. Those are covered by PAUTH V3 once active and by the companion `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation` thread's existing `-006` GO.

## Requirement Sufficiency

**Existing requirements sufficient.** The corrective F1/F2/F3 work scope is already specified in `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-010.md` § Required Revisions. This re-authorization proposal does not introduce new requirements; it restores the mechanical authorization substrate so the existing requirements can be satisfied.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the following spec-derived verifications will run on the post-implementation report:

| # | Verification | Command | Pass Criterion |
|---|---|---|---|
| V1 | PAUTH V3 record present and active | `python -m groundtruth_kb projects show PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION --json` | Output contains `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V3` with `status: active`. |
| V2 | PAUTH V3 includes WI-3438 | (same command, `work_items` section) | Output `work_items` includes `WI-3438`. |
| V3 | PAUTH V3 envelope schema valid | `python -m groundtruth_kb projects show --json` and inspect `allowed_mutation_classes`, `forbidden_operations`, `expires_at` per `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`. | All required envelope fields present and non-empty. |
| V4 | Project restored from retired state | (same command, `project.status` field) | `project.status` is `active`. |
| V5 | impl-start gate accepts the Slice 3 thread | `python scripts/implementation_authorization.py begin --bridge-id gtkb-claude-md-scope-clarification-slice-3-implementation` | Returns a packet hash without "Project authorization ... is not active" error. |
| V6 | Bridge applicability preflight pass on this proposal | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-md-scope-clarification-slice-3-reauthorization` | `preflight_passed: true`, `missing_required_specs: []`. |
| V7 | ADR/DCL clause preflight pass on this proposal | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-md-scope-clarification-slice-3-reauthorization` | Exit 0; no blocking gaps. |

These seven verifications collectively prove that re-authorization succeeded and that the F1/F2/F3 fix work can mechanically proceed on the companion Slice 3 thread.

## Recommended Commit Type

**`chore(governance):`** — Restoring an authorization substrate that was auto-retired by `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 collective-retirement automation. No new feature surface; no bug fix to product code; the mutation is governance-substrate only. Suggested commit message:

```
chore(governance): re-authorize PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION as PAUTH V3 after v3 retirement automation misfire on reviewer-error -009 VERIFIED (WI-3438; Slice 3 corrective revision substrate)
```

The companion Slice 3 implementation thread's post-impl revision will commit under its own `refactor:` type once VERIFIED.

## Risk / Outcome

- **Risks mitigated:** Re-authorization restores the mechanical substrate for closing `-010` NO-GO findings. Without it, the Slice 3 thread sits indefinitely; the broader 599-entry triage cannot proceed cleanly because Slice 3 file mutations would commit-bundle into any triage commit.
- **Residual risk:** The underlying `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 misfire pattern persists. Second observed instance this session (first was PROJECT-GTKB-PUSH-GATE per S368 auto-memory). v4 trigger-semantics repair is captured as a backlog candidate (Task #7 in this session's task list) and should be filed as a backlog work item in MemBase rather than fixed in this thread.
- **Rollback if NO-GO:** Discard this proposal; revert any PAUTH V3 row insert via append-only versioning by issuing a `gt projects revoke-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V3`; revert project status by issuing a project update with reason "re-authorization NO-GO rollback".

## Owner Action Required

None for this proposal. Owner AUQ S371 above is the authorizing decision; this filing is the protocol-required bridge channel for that decision per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
