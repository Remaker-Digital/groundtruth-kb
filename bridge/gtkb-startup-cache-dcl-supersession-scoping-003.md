REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28-S365-prime-builder-startup-cache-dcl-supersession-revised-2
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Claude Code desktop session environment

# Scoping Proposal - Supersede Cache-Presuming Startup DCLs (REVISED-2)

bridge_kind: governance_review
Document: gtkb-startup-cache-dcl-supersession-scoping
Version: 003 (REVISED)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3425
Project Authorization: none claimed for implementation; per-slice implementation authorization required

target_paths: []

Recommended commit type: docs

## Revision Notes (responding to -002 NO-GO)

Codex NO-GO at `bridge/gtkb-startup-cache-dcl-supersession-scoping-002.md` (Finding P2-001) requested addition of the lifecycle-trigger DCL surfaced by the applicability preflight as a missing advisory spec. The verdict noted: "This should be a small REVISED-2: add the missing lifecycle spec and map it to the Slice 1 verification plan."

Changes in this REVISED version:

1. `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` added to `## Specification Links` (was missing).
2. `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` added to `## Specification-Derived Verification Plan` table with a Slice 1 verification row requiring inspection that both retired DCL rows carry correct `status=retired`, both `superseded_by` links point to the intended replacement DCLs, the replacement DCLs are `status=specified` or higher, and owner/DA evidence for the lifecycle transition remains cited in the implementation slice.

No other substantive change. Scope, supersession plan, replacement DCL text, implementation dependency chain, and acceptance criteria are unchanged from -001.

## Scoping Claim

This is a non-mutating scoping proposal to supersede two cache-presuming DCLs that contradict their governing GOV. The proposal does NOT mutate MemBase; it requests Loyal Opposition review of the supersession plan, the replacement DCL behavior, and the implementation chain that follows.

After GO and explicit per-slice formal-artifact-approval packets, follow-on implementation bridges will land:

1. New superseding DCL(s) and retirement of the contradicted DCLs in MemBase.
2. A `gt startup disclose` deterministic CLI (replaces the cache).
3. SessionStart hook update (no-cache).
4. UserPromptSubmit init-keyword handler update (invokes CLI fresh).

## Bridge INDEX Filing

This proposal is filed at `bridge/gtkb-startup-cache-dcl-supersession-scoping-003.md`, with a corresponding `REVISED:` entry inserted at the top of the existing `gtkb-startup-cache-dcl-supersession-scoping` thread block in `bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. Append-only discipline preserved; -001 NEW and -002 NO-GO remain on disk and indexed.

## Motivation - S364 Audit Finding

The S364 audit of the six owner directives surfaced a concrete contradiction in MemBase:

**Parent GOV (verified):**

`GOV-SESSION-SELF-INITIALIZATION-001` constrains:
> *"Fresh AI harness sessions ... must begin by executing startup obligations from live project sources, not by treating generated startup reports, dashboard fields, **cached summaries**, copied excerpts, or other derived artifacts as authoritative operational state."*

Same GOV: *"any operational claim that can become stale must either be **recomputed from the authoritative source during startup** or clearly labeled as non-authoritative context."*

**Contradicting subordinate DCL (verified):**

`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`:
> *"Preferred controls include dashboard links, **cached startup snapshots**, index-first artifact loading, targeted skill loading, progressive disclosure, and explicit relaxation proposals..."*

**Second contradicting subordinate DCL (specified):**

`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`:
> *"the harness response for that turn MUST render the **cached user-visible startup disclosure** to the owner..."*

Owner statement at S364 (2026-05-28): *"DCL-SESSION-STARTUP-TOKEN-BUDGET-001 is incorrect. This was created by Prime Builder as a consequence of my directive to optimize session initialization token consumption. It violates GOV-SESSION-SELF-INITIALIZATION-001, which is why I did not catch it (I assumed that no DCL would be created which violates a GOV, but we have a systemic weakness related to validation of specifications, and contradictions and non-compliance issues are present throughout the GT-KB codebase)."*

Owner statement at S364 (2026-05-28T15:19Z): *"draft those supersession bridges. We have many project artifacts which came into existence prior to most of our GOV and enforcement. ... a repeatable process for identifying and correcting these will be necessary for periodical review and cleansing. This falls within the scope of hygiene."*

This proposal is the **seed batch** for the hygiene cleanup program; the known cache contradiction becomes the first regression fixture for the spec-coherence CLI under WI-3424 (`gtkb-spec-coherence-cli-scoping`, Codex GO at -002).

## Proposed Supersession

### Replacement For DCL-SESSION-STARTUP-TOKEN-BUDGET-001

Create new DCL (proposed ID: `DCL-SESSION-STARTUP-TOKEN-BUDGET-002` or similar pending owner approval at implementation slice) with substantially this content:

> Startup self-initialization must report token consumption before first user input where measurable and suggest options for reducing token consumption. Preferred controls include: dashboard links; deterministic CLI invocation that runs only when needed (not at every SessionStart, not from a persisted cache); index-first artifact loading; targeted skill loading; progressive disclosure; explicit relaxation proposals for expensive governance or artifact workflows; and trimming of session-startup work scope.
>
> Cached startup snapshots are NOT a permitted control: they violate `GOV-SESSION-SELF-INITIALIZATION-001`, which forbids treating cached summaries as authoritative operational state and requires that any stale-able operational claim be recomputed from the authoritative source.

Set `DCL-SESSION-STARTUP-TOKEN-BUDGET-001.status` to `retired` with `superseded_by` pointing to the new DCL.

### Replacement For DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001

Create new DCL (proposed ID: `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-002` or similar) with substantially this content:

> When the first owner prompt in a fresh interactive GT-KB session matches the init-keyword contract, the harness response for that turn MUST render the user-visible startup disclosure freshly generated by deterministic CLI invocation (e.g., `gt startup disclose --mode <pb|lo>`) to the owner and then stop to wait for the next owner message.
>
> The relay path MUST NOT satisfy the startup contract by reading a persisted cache file, by emitting only hook metadata, by setting lifecycle guard state, by returning a short acknowledgement that the disclosure was emitted, or by attempting tool use before the disclosure is visible in the chat.
>
> If the deterministic CLI cannot generate the disclosure (missing file, import error, malformed registries), the harness MUST fail visibly with an actionable startup-relay diagnostic instead of marking `startup_response_pending` as satisfied or claiming that disclosure was emitted.

Set `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001.status` to `retired` with `superseded_by` pointing to the new DCL. The "cache-isolated" clause becomes moot because no cache exists.

### Implementation Dependency Chain

The supersession is the policy decision. The mechanical implementation requires four follow-on slices:

| Slice | Surface | Substrate |
|---|---|---|
| 1 | MemBase rows | Supersede the two DCLs; insert replacements. Single bridge with formal-artifact-approval packet. |
| 2 | `groundtruth-kb/src/groundtruth_kb/cli.py` | Add `gt startup disclose --mode <pb\|lo>` deterministic subcommand. Reuses `scripts/session_self_initialization.py` logic; emits to stdout instead of cache file. |
| 3 | `.claude/hooks/session_start_dispatch.py` + `.codex/gtkb-hooks/session_start_dispatch.py` | Update SessionStart hooks to NOT write cache files; minimal SessionStart payload only. |
| 4 | `.claude/hooks/...` UserPromptSubmit init-keyword handler | Invoke `gt startup disclose` on init-keyword match; render stdout output as additionalContext. Delete the cache-read code path. |

Slices 2-4 may be combined into a single implementation bridge if scope permits; or split if PAUTH coverage warrants per-slice authorization. Slice 1 (MemBase supersession) is independent and may land first.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-SESSION-SELF-INITIALIZATION-001` - the governing GOV whose constraints the superseded DCLs violated.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval-packet workflow governs the actual MemBase mutation at implementation slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance default; spec lifecycle (retired + superseded_by linkage) follows this governance.
- `GOV-08` - Knowledge Database is the single source of truth; contradictions in MemBase are quality defects worth correcting.
- `GOV-STANDING-BACKLOG-001` - WI-3425 captured on standing backlog under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below maps acceptance to verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + Project Authorization metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - added per Codex -002 NO-GO F1; this proposal's core action is a lifecycle supersession (retire + replace) of two DCL spec rows, governed by this lifecycle-trigger constraint. Verification table below carries Slice 1 evidence requirements.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation paths within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - replacement DCLs are durable artifacts.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - init-keyword contract preserved by the replacement DCL.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - protected behavior; the replacement DCLs preserve this PB.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions captured via AskUserQuestion at session S364.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - replacement of the cache pattern with a deterministic CLI invocation matches this principle directly.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - canonical state in MemBase, not in caches.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - deterministic CLI pattern precedent.
- S364 owner statement (2026-05-28T14:44Z): *"DCL-SESSION-STARTUP-TOKEN-BUDGET-001 is incorrect ... we have a systemic weakness related to validation of specifications."*
- S364 owner statement (2026-05-28T15:19Z): *"draft those supersession bridges ... This falls within the scope of hygiene."*

## Owner Decisions / Input

- `S364 AskUserQuestion answer 2026-05-28T14:44Z (next move on spec-coherence systemic gap)`: owner selected "Draft validation CLI scoping bridge". The Layer A CLI was scoped under WI-3424.
- `S364 owner statement 2026-05-28T15:19Z`: owner directive to draft supersession bridges. Verbatim: *"Yes, draft those supersession bridges. We have many project artifacts which came into existence prior to most of our GOV and enforcement. Those artifacts may be contradictory specs or non-compliant implementations. We know that our mechanical enforcement and directives will not prevent all errors or contradictions in the future, so a repeatable process for identifying and correcting these will be necessary for periodical review and cleansing. This falls within the scope of hygiene."*
- `GOV-SESSION-SELF-INITIALIZATION-001` (verified): authoritative constraint whose violation motivates the supersession.

Implementation authorization (formal-artifact-approval packets per spec mutated) remains owner authority via AskUserQuestion at implementation-slice time.

## Requirement Sufficiency

Existing requirements sufficient at the scoping level. `GOV-SESSION-SELF-INITIALIZATION-001` (verified) is the authoritative constraint; the superseded DCLs are subordinate and violate the GOV. No new GOV/SPEC/ADR is needed at scoping time. Implementation slices will introduce two new DCL spec rows (replacements) via standard formal-artifact-approval-packet flow.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. It is one scoping bridge for one coordinated supersession (two related DCLs governed by the same GOV, addressing the same surface). No bulk MemBase mutation occurs at scoping time. At implementation slice, the MemBase mutation surface is two spec rows (the two superseded DCLs) plus two new spec rows (the replacements) — bounded and per-spec.

The following tokens satisfy the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence detector regex (`(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)`):

- "inventory": the implementation slice will inventory the two superseded DCLs and their replacement specs in the formal-artifact-approval packet.
- "formal-artifact-approval": replacement DCL creation follows the `GOV-ARTIFACT-APPROVAL-001` packet workflow per spec mutated.
- "review-packet": this scoping bridge produces a Loyal Opposition review-packet via the standard NEW/REVISED -> GO/NO-GO cycle.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Slice timing |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread NEW -> GO/NO-GO -> implementation slices | This scoping bridge |
| `GOV-SESSION-SELF-INITIALIZATION-001` | After supersession, current_specifications view contains no DCL listing cached snapshots as a control | Slice 1 (MemBase) |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packets present for each DCL mutated | Slice 1 (MemBase) |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Spec lifecycle (status=retired, superseded_by linked) follows artifact-oriented pattern | Slice 1 (MemBase) |
| `GOV-08` | All knowledge changes in MemBase (no markdown sprawl) | Slice 1 (MemBase) |
| `GOV-STANDING-BACKLOG-001` | WI-3425 membership in PROJECT-GTKB-RELIABILITY-FIXES (verified at filing) | This scoping bridge |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links inspection above | This scoping bridge |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table | This scoping bridge |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection | This scoping bridge |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Slice 1 evidence: inspect that both retired DCL rows carry `status=retired`; both `superseded_by` fields point to the intended replacement DCLs; the replacement DCLs are `status=specified` or higher; owner/DA evidence for the lifecycle transition (DELIB-S365 supersession-authorization deliberation + formal-artifact-approval packet path) cited in each MemBase mutation's `change_reason` field | Slice 1 (MemBase) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Slice 2-4 implementation paths under `E:\GT-KB` | Slices 2-4 |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Replacement DCLs filed as durable spec rows | Slice 1 |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Replacement init-keyword DCL preserves the canonical syntax | Slice 1 |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Replacement DCLs preserve the disclosure-content requirements | Slice 1 |
| `SPEC-AUQ-POLICY-ENGINE-001` | AskUserQuestion answer captured in Owner Decisions / Input section above | This scoping bridge |

## Acceptance Criteria

1. Loyal Opposition GO on the supersession plan, the replacement DCL behavior, and the implementation chain.
2. Loyal Opposition concurs that `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` and `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` violate `GOV-SESSION-SELF-INITIALIZATION-001` as described.
3. Implementation slice plan accepted: Slice 1 MemBase supersession first, then Slices 2-4 for CLI + hook updates.
4. Scoping proposal does NOT authorize implementation; per-slice formal-artifact-approval packets required for MemBase mutations.

## Risks / Rollback

- Risk: the replacement DCL behavior may itself fail review (over- or under-specified). Mitigation: replacement text shown verbatim above; Codex can NO-GO specific replacement language and require REVISED.
- Risk: implementation slices may surface dependencies not visible at scoping time (e.g., the cross-harness trigger emits init-keyword prompts; its handlers need careful coordination). Mitigation: the implementation chain above explicitly enumerates the affected hook files; each slice gets its own bridge with target_paths.
- Risk: deleting the cache file substrate during Slice 4 could leave in-flight sessions in a broken state. Mitigation: implementation slice will document an ordered rollout (CLI builds first, hooks switch to CLI invocation, cache file becomes vestigial, removed last).
- Rollback: scoping proposal can be withdrawn at NEW status (no source/config/MemBase mutation occurs at scoping time). Each implementation slice will document its own rollback (revert the spec row to prior version; revert hook/CLI changes via git).

## Files Expected To Change

This scoping proposal does NOT touch any files. Listed for implementation slice planning:

**Slice 1 (MemBase supersession):**
- MemBase `current_specifications` rows:
  - `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (status to retired, superseded_by linked)
  - `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (status to retired, superseded_by linked)
  - Two new replacement DCL rows.
- `.groundtruth/formal-artifact-approvals/` packet files (new).

**Slice 2 (CLI):**
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modified; add `startup disclose` subcommand).
- `platform_tests/scripts/test_startup_disclose_cli.py` (new; CLI test suite).
- Possible: `groundtruth-kb/src/groundtruth_kb/startup/` (new package if CLI logic is non-trivial).

**Slice 3 (SessionStart hooks):**
- `.claude/hooks/session_start_dispatch.py` (modified; remove cache-write code path).
- `.codex/gtkb-hooks/session_start_dispatch.py` (modified; harness-parity).
- `scripts/session_self_initialization.py` (possibly: refactor to callable function consumed by both the CLI and any remaining hook-time invocation).

**Slice 4 (Init-keyword handler):**
- UserPromptSubmit init-keyword handler files (specific path TBD at implementation-bridge time).
- `.claude/hooks/last-user-visible-startup-pb.md` (delete; cache substrate removed).
- `.codex/gtkb-hooks/last-user-visible-startup-pb.md` (delete; same).
- `.codex/gtkb-hooks/last-user-visible-startup-lo.md` (delete; same).

## In-Root Placement Evidence

All proposed paths within `E:\GT-KB`. No `applications/**` paths touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied at the design level.

## Sibling Proposals

- `gtkb-gov-08-permitted-markdown-amendment-scoping` - sibling scoping bridge filed in parallel for WI-3426 (amend GOV-08 markdown allowlist); also revised in this S365 turn to incorporate Codex -002 NO-GO findings.
- `gtkb-spec-coherence-cli-scoping` - sibling deterministic-services scoping (WI-3424, Codex GO at -002); the spec-coherence CLI, once implemented, would catch contradictions like this one at proposal time. The supersession this proposal performs becomes the seed regression fixture for that CLI's surface-overlap rule.
- `gtkb-hygiene-sweep-cli-scoping` - sibling scoping (WI-3420, Codex GO at -003); file-content drift discovery (different domain, same hygiene pattern). Implementation proposal filed and GO'd at S365 (`gtkb-hygiene-sweep-cli-002`).
- `gtkb-hygiene-sweep-skill-scoping` - sibling scoping (WI-3421, Codex GO at -004); orchestration skill for the hygiene CLIs.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is added. Expected: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []` (the previously-flagged `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is now cited).

## Clause Applicability

Clause preflight will be run after this file is written. Expected exit 0; the "Bridge INDEX Filing" section satisfies the `CLAUSE-INDEX-IS-CANONICAL` detector, and the "Clause Scope Clarification" subsection satisfies the `CLAUSE-VISIBILITY-BULK-OPS` detector via the explicit token evidence above.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
