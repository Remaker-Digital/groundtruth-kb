NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-9-new
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3479
target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", ".claude/rules/canonical-terminology.md", "CLAUDE.md", "AGENTS.md"]

# GT-KB Interactive Session Role Override - Slice 9 Implementation Proposal: Rule and CLAUDE/AGENTS Updates

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
Version: 001
Date: 2026-05-30 UTC

## Claim

Slice 9 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE revises the protected narrative-authority files so they describe the durable-vs-session role authority split established by `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, and `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`. Five files receive targeted, additive revisions; each receives its own formal-artifact-approval packet (per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`) at implementation time. The pre-existing "no markdown rule file can override the durable assignment map" invariant is preserved because the session-state marker is runtime state, not a rule file.

The implementation is text-only. No source code, MemBase schema, or runtime behavior changes. The three cited specs already exist in MemBase as `specified` (verified at filing time via `KnowledgeDB.get_spec_history`).

## Live Bridge State

```text
Document: gtkb-interactive-session-role-override-scoping
GO: bridge/gtkb-interactive-session-role-override-scoping-004.md  ← architecture authority

Document: gtkb-interactive-session-role-override-slice-7-doctor-marker-checks
VERIFIED: bridge/...-006.md  ← Slice 7 shipped

Document: gtkb-interactive-session-role-override-slice-6-attribution-role-awareness
VERIFIED: bridge/...-004.md  ← Slice 6 shipped

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
NO-GO: bridge/...-015.md  ← Slice 8 in v5 NO-GO; this slice has an implementation-sequencing dependency

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
NEW: bridge/...-001.md  ← this proposal
```

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` v1 (specified in MemBase)
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 (specified in MemBase)
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (specified in MemBase)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1
- `DCL-CONCEPT-ON-CONTACT-001` v1 (specified in MemBase; authority for the new glossary entry)
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` v1 (specified in MemBase; canonical-terminology placement authority)
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-ACTING-PRIME-BUILDER-001`
- `GOV-ARTIFACT-APPROVAL-001` (formal-artifact-approval packet authority)
- `DCL-ARTIFACT-APPROVAL-HOOK-001` (narrative-artifact-approval-gate hook authority)
- `PB-ARTIFACT-APPROVAL-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `bridge/gtkb-interactive-session-role-override-scoping-003.md`
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (GO; architecture authority for this slice)
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-scoping-003.md` Slice 9 specification (lines 353-361 in the GO'd scoping) — concrete acceptance criterion enumerates the cited specs and the new glossary entry.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` GO — Codex confirmed the 10-slice decomposition and gave non-blocking acknowledgement that Slice 9 = rule/docs update.
- Slices 1, 3, 5, 6, 7 VERIFIED chain — established the runtime behavior that the rule text now describes.
- `DELIB-2507` — S371 owner directive establishing the project.
- S371 AskUserQuestion sequence (Decisions 1-6) — owner approval for the architectural intent that the rule text now codifies.
- `DCL-CONCEPT-ON-CONTACT-001` — authority for adding the `session-stated role` glossary entry on first canonical contact.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and `ADR-DA-READ-SURFACE-PLACEMENT-001` — placement authority for the new glossary entry.
- `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "interactive session role override slice 9 rule claude agents" --limit 8` returned no Deliberation Archive matches; this is novel text under an existing thread family.

## Implementation Plan

### Sequencing Dependency

Per scoping-003 Slice 9 dependency note: "Slices 1-8 land first so the rule changes describe shipping behavior, not pre-shipped behavior." At filing time, Slices 1, 3, 5, 6, 7 are VERIFIED; Slice 8 (parity check) is at NO-GO `-015` with one remaining v5 finding (same-line semicolon bypass of `_main_call_order_error`).

This proposal MAY pass Codex review before Slice 8 reaches VERIFIED. Implementation of Slice 9 will NOT begin until Slice 8 reaches VERIFIED, because the rule text references the parity-check enforcement that Slice 8 establishes. Prime Builder will hold this slice at GO state until Slice 8 lands. The Slice 9 implementation start packet activation will check the live Slice 8 thread state and refuse activation if Slice 8 is not VERIFIED.

If the owner directs Slice 9 implementation to begin earlier (e.g., describing the architectural intent without citing the live parity-check), the proposal-side rule text can be edited via REVISED-1 to drop the implementation-state references; this is an AskUserQuestion point at implementation start, not a proposal-review concern.

### Per-File Change Inventory

Five protected narrative-authority files receive targeted, additive revisions. Each receives its own formal-artifact-approval packet at implementation time.

#### File 1: `.claude/rules/operating-role.md`

**Current state:** Defines `harness-state/role-assignments.json` as the single source-of-truth durable role map. States: "no markdown rule file can override the durable role assignment map at `harness-state/role-assignments.json` (the single source of truth)."

**Proposed change:** Add a new section after § "Role Set Schema (Active Authority)" titled § "Interactive Session Role Override". The new section:

1. States that durable role authority continues to govern headless dispatch routing (the cross-harness event-driven trigger consults durable role).
2. States that an interactive session MAY override the durable role for in-session surfaces (SessionStart disclosure, AXIS 2 Claude-native surface, workstream-focus menu, MemBase attribution, AUQ routing) by including the canonical init keyword `::init gtkb (pb|lo)` on an owner prompt.
3. Cites `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` as the authority chain.
4. Reaffirms that the pre-existing "no markdown rule file can override the durable assignment map" statement remains true: the session-state marker is ephemeral runtime state (`.claude/session/active-session-role.json`), not a rule file. Rule files do not record which role is active; the marker does, only for the session.

**Preserved invariants:** the durable map is still the single source of truth for durable role; rule files are still behavior contracts; the persistent identity record is still authoritative for harness identification.

#### File 2: `.claude/rules/prime-builder-role.md`

**Current state:** Behavior contract for Prime Builder. References "no markdown rule file can override the durable role assignment map".

**Proposed change:** Add a brief subsection after the existing "Role Assignment Rules"-equivalent text noting that:

1. Prime Builder role authority applies whenever the resolved session role (per `DCL-SESSION-ROLE-RESOLUTION-001`) is Prime Builder, whether by durable assignment or by session-stated override.
2. When the session role differs from the durable role (interactive override active), Prime Builder's permissions and restrictions follow the session role, not the durable role.
3. Cites the three new specs.

This subsection is small (target ~10-15 lines) to keep the file's role-contract focus intact.

#### File 3: `.claude/rules/canonical-terminology.md`

**Current state:** Canonical terminology glossary with existing entries for `operating role`, `session lane`, `session focus`, `work subject`.

**Proposed change:** Add a new entry `session-stated role` as a sibling of `operating role`. The entry follows the established glossary field convention (Definition, Canonical alias, Not to be confused with, Source, Implementation pointer):

- Definition: An ephemeral, session-scoped role declared by the owner via the canonical init keyword `::init gtkb (pb|lo)` on an interactive owner prompt. Overrides the durable operating role for SessionStart disclosure rendering, AXIS 2 Claude-native surface filtering, workstream-focus menu shape, MemBase attribution, and AUQ-keyed routing for the duration of the session. Persists in `.claude/session/active-session-role.json` and is invalidated by the next SessionStart.
- Canonical alias: interactive session role; session-scoped role.
- Not to be confused with: `operating role` (durable, persists across sessions); `session lane` (non-authority work classification); `session focus` (owner-facing startup focus selection); `work subject` (active subject area; orthogonal axis).
- Source: `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`; `DELIB-2507` (S371 originating owner directive); `DCL-CONCEPT-ON-CONTACT-001` (authority for first-contact addition).
- Implementation pointer: `.claude/session/active-session-role.json` is the runtime marker; written by `scripts/workstream_focus.py` on init-keyword match; invalidated by both `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` at SessionStart.

#### File 4: `CLAUDE.md`

**Current state:** The "Role precedence" paragraph (currently near the top of CLAUDE.md, citing the durable harness identity and role assignment chain).

**Proposed change:** Revise the Role precedence paragraph to add one sentence after the existing "active role is resolved at session start from `harness-state/harness-identities.json` ... and `harness-state/role-assignments.json` (the single source-of-truth durable role map)" text:

> "Interactive sessions MAY override the durable role for in-session surfaces (SessionStart disclosure, AXIS 2 Claude-native surface, focus menu, MemBase attribution, AUQ routing) by typing the canonical init keyword `::init gtkb (pb|lo)` on an owner prompt; the override is held in the ephemeral `.claude/session/active-session-role.json` marker for the rest of the session lifetime and is invalidated by the next SessionStart. Headless dispatch routing remains keyed to the durable role per `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`."

CLAUDE.md remains under its 300-line GOV-01 cap; the addition is roughly 4 lines.

#### File 5: `AGENTS.md`

**Current state:** Loyal Opposition operating contract; "Durable Operating Role Assignment" section currently states the same "No markdown rule file can override this durable assignment map" invariant.

**Proposed change:** Mirror the CLAUDE.md change in AGENTS.md: add the parallel paragraph after the existing durable-role text. AGENTS.md is the Codex-side mirror, so the text is harness-agnostic ("interactive sessions" rather than "Claude sessions"). Citations are identical.

### Per-File Formal-Artifact-Approval Packet Workflow

Each of the five files is a protected narrative-authority path per `config/governance/narrative-artifact-approval.toml`. Per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`, each Write requires:

1. An explicit owner-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-NN-<artifact-id>.json` containing the full proposed content + `content_sha256` + `presented_to_user=true` + `transcript_captured=true` + `explicit_change_request` + `approved_by=owner`.
2. The `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var set to the packet path when invoking the Write.
3. The narrative-artifact-approval-gate hook validates packet presence + content-hash match before allowing the Write.

At implementation start (after Codex GO):

1. Prime Builder presents the proposed text for each file via AskUserQuestion, one file at a time (per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel and `memory/feedback_present_decisions_one_by_one.md`).
2. Owner approves each file's proposed text via AskUserQuestion.
3. Prime Builder writes the per-file packet JSON.
4. Prime Builder invokes Write with the env var pointing to the packet; the hook validates and admits.

This proposal does NOT generate or commit the packets at proposal-filing time; packets are implementation-time artifacts.

### Implementation Order

1. Wait for Slice 8 VERIFIED.
2. Activate implementation-start packet for this bridge thread.
3. For each file (operating-role.md → prime-builder-role.md → canonical-terminology.md → CLAUDE.md → AGENTS.md), in order:
   a. Present the proposed text via AskUserQuestion.
   b. Generate the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/`.
   c. Edit the file with the packet env var set.
4. Run the verification gates (next section).
5. File the post-implementation report at `-NNN.md` for Codex review.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, this slice's spec-to-test mapping:

| Specification | Verification Command | Expected Result |
|---|---|---|
| `GOV-SESSION-ROLE-AUTHORITY-001` v1 (citation requirement per scoping-003 Slice 9 acceptance) | `grep -l "GOV-SESSION-ROLE-AUTHORITY-001" .claude/rules/operating-role.md .claude/rules/prime-builder-role.md AGENTS.md CLAUDE.md` | All 4 files match (the canonical-terminology entry also cites it, but it is verified by the term-presence check below) |
| `DCL-SESSION-ROLE-RESOLUTION-001` v1 (citation requirement) | Same grep with the DCL ID | At least 4 files match |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (citation requirement) | Same grep with the ADR ID | At least 4 files match |
| `DCL-CONCEPT-ON-CONTACT-001` v1 | `grep -A2 "session-stated role" .claude/rules/canonical-terminology.md` | New glossary entry present with the required field convention |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 | grep for `::init gtkb (pb|lo)` in the new sections of each file | Present in operating-role.md, CLAUDE.md, AGENTS.md, canonical-terminology.md |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | List of created packets at `.groundtruth/formal-artifact-approvals/2026-05-NN-*.json` | One packet per edited file |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` CLAUSE-IN-ROOT | All target paths within `E:\GT-KB` (no Agent Red references in live-dependency role) | All 5 target paths in-root |
| `GOV-FILE-BRIDGE-AUTHORITY-001` CLAUSE-INDEX-IS-CANONICAL | `bridge/INDEX.md` carries the post-impl `NEW: -NNN.md` entry at the top of this thread | INDEX entry present |
| Doctor canonical-terminology check | `gt project doctor --check canonical_terminology` | Reports `session-stated role` as a recognized canonical term; no missing-term errors |

The verification commands are simple (grep + ls + doctor); they do not require new test modules. Slice 10 separately adds the regression and integration tests for the runtime behavior; Slice 9 verification is text-presence verification only.

## Owner Decisions / Input

This slice proceeds on the AskUserQuestion evidence already captured for the parent project. No new architectural decisions are required at proposal-filing time. Implementation start requires per-file AskUserQuestion approval for each formal-artifact-approval packet (enumerated in § Per-File Formal-Artifact-Approval Packet Workflow above).

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active; reactivated per owner AUQ S374). Covers `WI-3479`. Scope summary: "Slices 4-10 of the interactive-session-role-override architecture per bridge/gtkb-interactive-session-role-override-scoping-004.md".
- `DELIB-2507` — the S371 owner directive establishing PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE.
- S371 AskUserQuestion decisions 1-6 (override scope, undeclared default, role persistence, declaration UX, landing path, disclosure transparency) — the architectural intent that Slice 9 codifies in narrative-authority text.
- Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md` — Slice 9 implementation authority.
- S375 AskUserQuestion (this session): owner directive to proceed with Slices 9 and 10 authorizes the filing of this proposal and its sibling Slice 10 proposal in parallel. This proposal declares `WI-3479` (Slice 9 scope only); Slice 10 carries its own work-item declaration in its own bridge thread.
- Per-file AskUserQuestion at implementation start: owner approval of the proposed text for each of the 5 protected files, captured one at a time per `memory/feedback_present_decisions_one_by_one.md`.

## Requirement Sufficiency

**Existing requirements sufficient.** The three new specs (GOV/DCL/ADR) are in MemBase as `specified` and define the architectural intent that Slice 9 codifies. No requirement revision is needed. The S371 AskUserQuestion evidence is the durable owner approval for the underlying intent; the per-file packets at implementation time are the per-file implementation gate, not new requirements.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` clause-scope clarification convention: this slice is narrative-authority text revision plus one new canonical-terminology glossary entry. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no MemBase row insert (the cited specs already exist), no inventory artifact, and no review-packet. Evidence-pattern tokens: rule revision, glossary update, narrative-authority text, per-file approval packets, no backlog mutation, no project mutation, no canonical-spec insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all 5 target paths live under `E:\GT-KB`. The runtime marker referenced in the new text (`.claude/session/active-session-role.json`) is also in-root. No application-layer paths, no `applications/<name>/` paths, no Agent Red references in a live-dependency role. The text proposes preserving the existing root-boundary statements in each file.

## Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | `.claude/rules/operating-role.md` carries the new § "Interactive Session Role Override" section citing the three new specs | grep + visual review |
| 2 | `.claude/rules/prime-builder-role.md` carries the brief subsection on session-resolved role authority | grep + visual review |
| 3 | `.claude/rules/canonical-terminology.md` carries the new `session-stated role` glossary entry with the required field convention | grep + visual review + doctor canonical-terminology check |
| 4 | `CLAUDE.md` Role precedence paragraph carries the durable-vs-session split sentence, citing the new GOV and DCL | grep + visual review; CLAUDE.md remains under 300 lines per GOV-01 |
| 5 | `AGENTS.md` carries the parallel paragraph | grep + visual review |
| 6 | One formal-artifact-approval packet per edited file at `.groundtruth/formal-artifact-approvals/2026-05-NN-*.json` | ls + content-hash verification |
| 7 | Existing canonical text invariants preserved: "no markdown rule file can override the durable assignment map" remains in operating-role.md and AGENTS.md; rule files remain behavior contracts | grep + visual review |
| 8 | Bridge applicability preflight passes on the post-implementation report | `python scripts/bridge_applicability_preflight.py --bridge-id ...` |
| 9 | ADR/DCL clause preflight passes (zero blocking gaps) | `python scripts/adr_dcl_clause_preflight.py --bridge-id ...` |
| 10 | Slice 8 is VERIFIED before Slice 9 implementation begins | check `bridge/INDEX.md` for `VERIFIED:` line on the Slice 8 thread top |

## Risk and Rollback

- **Risk:** Per-file packet AskUserQuestion overhead is 5 packets minimum. **Mitigation:** packets are presented one at a time per `memory/feedback_present_decisions_one_by_one.md`; each is small and self-contained (a single file edit).
- **Risk:** Rule text becomes stale if Slice 8 implementation changes. **Mitigation:** sequencing dependency on Slice 8 VERIFIED ensures the rule text describes shipped behavior; the rule text describes the architectural contract (cited specs), not implementation details that might drift.
- **Risk:** Codex flags the "no rule file overrides durable" invariant as in conflict with the new "session override" mechanism. **Mitigation:** the new text explicitly notes the marker is runtime state, not a rule file; this preserves the original invariant exactly (rule files don't override; the runtime marker is a different mechanism).
- **Risk:** `CLAUDE.md` exceeds its 300-line GOV-01 cap. **Mitigation:** the addition is ~4 lines; the file's current length leaves headroom. If headroom is insufficient, the implementation will compact one or more existing low-value sections.
- **Risk:** A glossary entry collision with `operating role` confuses readers. **Mitigation:** the new entry's "Not to be confused with" field explicitly distinguishes the two terms; placement is adjacent to `operating role` in the glossary so the contrast is immediate.
- **Rollback:** each file's edit is one diff hunk; reverting the addition restores the prior text exactly. The packets remain as audit trail.

## Recommended Commit Type

`docs:` — Slice 9 is governance/documentation text revision. No code, no tests, no behavior change. The Conventional Commits `docs:` type is correct per `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline ("for governance/rule/runbook-only edits").

## Files Touched

5 files (per target_paths):
- `.claude/rules/operating-role.md` (additive section)
- `.claude/rules/prime-builder-role.md` (additive subsection)
- `.claude/rules/canonical-terminology.md` (new glossary entry)
- `CLAUDE.md` (additive sentence in Role precedence paragraph)
- `AGENTS.md` (parallel additive paragraph)

Plus 5 formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/`. The packets are not under `target_paths` because they are owner-approval evidence artifacts, not project source; they are written before each file Edit as required by the gate hook.

## Owner Action Required

At proposal review time: none beyond Codex review.

At implementation start (after Codex GO):
- AskUserQuestion approval for each of the 5 per-file formal-artifact-approval packets (one AUQ per file, presented sequentially).

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
