REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-9-revised-3
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3479
target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", ".claude/rules/canonical-terminology.md", "CLAUDE.md", "AGENTS.md", ".groundtruth/formal-artifact-approvals/*-slice9-operating-role-md.json", ".groundtruth/formal-artifact-approvals/*-slice9-prime-builder-role-md.json", ".groundtruth/formal-artifact-approvals/*-slice9-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/*-slice9-claude-md.json", ".groundtruth/formal-artifact-approvals/*-slice9-agents-md.json"]

# GT-KB Interactive Session Role Override - Slice 9 Implementation Proposal: Rule and CLAUDE/AGENTS Updates - REVISED-3

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
Version: 007 (REVISED-3; addresses Codex NO-GO at -006 F1)
Date: 2026-05-30 UTC

## Response to NO-GO -006 (F1 Resolution)

Codex F1 (P1) at `-006` correctly identified that the `-005` REVISED-2 declared only the five protected narrative files in `target_paths`, but the implementation plan also creates five formal-artifact-approval packet files under `.groundtruth/formal-artifact-approvals/`. The approval packets are required implementation artifacts (written before each narrative edit so the narrative-artifact-approval gate admits the Write), so they must be authorized in `target_paths` or the implementation-start / commit gate mismatches. Codex cited the binding precedent: `bridge/active-workspace-declaration-slice-1-003.md` (concrete packet path added) and `bridge/gtkb-work-list-md-gov-010-path-correction-003.md` (per-file packet glob added).

This REVISED-3 applies the precedent fix:

1. **`target_paths` now includes five per-file packet globs** following the `work-list-md` precedent's date-agnostic glob form, each scoped uniquely to this slice via a `slice9-<file-slug>` infix:
   - `.groundtruth/formal-artifact-approvals/*-slice9-operating-role-md.json`
   - `.groundtruth/formal-artifact-approvals/*-slice9-prime-builder-role-md.json`
   - `.groundtruth/formal-artifact-approvals/*-slice9-canonical-terminology-md.json`
   - `.groundtruth/formal-artifact-approvals/*-slice9-claude-md.json`
   - `.groundtruth/formal-artifact-approvals/*-slice9-agents-md.json`
2. **A spec-derived verification step is added** (per Codex required revision 2): stage each protected narrative file with its matching packet and run `groundtruth-kb\.venv\Scripts\python.exe scripts/check_narrative_artifact_evidence.py --staged` expecting exit 0.
3. **Acceptance criteria and Files Touched are aligned** with the authorized packet globs.

No scope change to the actual narrative text edits; the correction is to the implementation-artifact authorization surface.

Additionally, the Slice 8 sequencing precondition is now **satisfied**: Slice 8 reached VERIFIED at `-017`. The live precondition one-liner (unchanged from REVISED-2) currently prints:

```text
VERIFIED: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-017.md
```

So Slice 9 implementation may proceed once this thread receives GO (subject to the per-file owner-approval AskUserQuestion workflow).

## Claim

Slice 9 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE revises the protected narrative-authority files so they describe the durable-vs-session role authority split established by `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, and `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`. Five files receive targeted, additive revisions; each receives its own formal-artifact-approval packet (per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`) at implementation time, and each packet path is now authorized in `target_paths`. The pre-existing "no markdown rule file can override the durable assignment map" invariant is preserved because the session-state marker is runtime state, not a rule file.

The implementation is text-only (narrative edits + approval-packet evidence). No source code, MemBase schema, or runtime behavior changes. The three cited specs already exist in MemBase as `specified`.

## Live Bridge State

```text
Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
VERIFIED: bridge/...-017.md  <- Slice 8 precondition now SATISFIED

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
NO-GO: bridge/...-006.md  <- addressed by this REVISED-3
REVISED: bridge/...-005.md
NO-GO: bridge/...-004.md
REVISED: bridge/...-003.md
NO-GO: bridge/...-002.md
NEW: bridge/...-001.md
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
- `PB-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001` (narrative-artifact-approval-gate hook authority)
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
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (GO; architecture authority for this slice)
- `bridge/active-workspace-declaration-slice-1-003.md` (precedent: packet path in target_paths)
- `bridge/gtkb-work-list-md-gov-010-path-correction-003.md` (precedent: per-file packet glob in target_paths)
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-001.md` — original NEW.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-002.md` — Codex NO-GO F1 (P1): unsupported mechanical dependency-gate claim.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-003.md` — REVISED-1: replaced mechanical-gate claim with manual precondition (non-Windows command).
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-004.md` — Codex NO-GO F1 (P1): non-executable `grep | head` precondition.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-005.md` — REVISED-2: repo-venv Python one-liner precondition.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-006.md` — Codex NO-GO F1 (P1): approval-packet paths outside target_paths; addressed by this REVISED-3.
- `bridge/active-workspace-declaration-slice-1-003.md` — precedent correction adding the approval-packet path to target_paths.
- `bridge/gtkb-work-list-md-gov-010-path-correction-003.md` — precedent correction adding a per-file packet glob to target_paths.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` GO — Codex confirmed the 10-slice decomposition.
- Slices 1, 3, 5, 6, 7 VERIFIED chain; Slice 8 VERIFIED at -017 — established the runtime behavior the rule text describes.
- `DELIB-2507` — S371 owner directive establishing the project.
- S371 AskUserQuestion sequence (Decisions 1-6) — owner approval for the architectural intent.

## Implementation Plan

### Sequencing Dependency (Slice 8 now VERIFIED)

Per scoping-003 Slice 9 dependency note, Slice 9 implementation should not begin until Slice 8 (parity check) is VERIFIED so the rule text describes shipped behavior. **Slice 8 reached VERIFIED at `-017`, so this precondition is now satisfied.**

The dependency remains an operator-level manual precondition, NOT a mechanical gate (`scripts/implementation_authorization.py begin --bridge-id <id>` evaluates only the named thread; it does not consult sibling-thread status). Before activating the Slice 9 implementation packet, Prime Builder will re-run this repo-venv Python one-liner (Windows/PowerShell-valid) and confirm the printed line begins with `VERIFIED:`:

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; lines=pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8').splitlines(); doc='Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table'; idx=[i for i,l in enumerate(lines) if l.strip()==doc]; print(lines[idx[0]+1].strip() if idx and idx[0]+1 < len(lines) else 'THREAD-NOT-FOUND-OR-NO-STATUS')"
```

Verified output at this REVISED-3 filing:

```text
VERIFIED: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-017.md
```

The post-implementation report will capture the activation-moment output as evidence.

### Per-File Change Inventory

(Unchanged from -001/-003/-005; carried forward.)

Five protected narrative-authority files receive targeted, additive revisions. Each receives its own formal-artifact-approval packet at implementation time.

**File 1: `.claude/rules/operating-role.md`** — add a new section after § "Role Set Schema (Active Authority)" titled § "Interactive Session Role Override". States durable role authority continues to govern headless dispatch routing; an interactive session MAY override the durable role for in-session surfaces via the canonical init keyword; cites the three new specs; reaffirms that "no markdown rule file can override the durable assignment map" remains true because the session-state marker is ephemeral runtime state, not a rule file.

**File 2: `.claude/rules/prime-builder-role.md`** — add a brief subsection (~10-15 lines) noting Prime Builder role authority applies whenever the resolved session role is Prime Builder, whether by durable assignment or session-stated override; cites the three new specs.

**File 3: `.claude/rules/canonical-terminology.md`** — add a new entry `session-stated role` as a sibling of `operating role` (Definition, Canonical alias, Not to be confused with, Source, Implementation pointer per the glossary field convention).

**File 4: `CLAUDE.md`** — revise the Role precedence paragraph (~4 lines added) to describe the durable-vs-session split and the init-keyword override; remains under the 300-line GOV-01 cap.

**File 5: `AGENTS.md`** — mirror the CLAUDE.md change with harness-agnostic phrasing.

### Per-File Formal-Artifact-Approval Packet Workflow

Each of the five files is a protected narrative-authority path per `config/governance/narrative-artifact-approval.toml` (`role-and-governance-rules` pattern set: `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`). Per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`, each Write requires:

1. An explicit owner-approval packet at `.groundtruth/formal-artifact-approvals/<date>-slice9-<file-slug>.json` (e.g. `2026-05-30-slice9-operating-role-md.json`) with `artifact_type=narrative_artifact`, `target_path` equal to the narrative file path, `full_content`, `full_content_sha256` matching the written body, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `approved_by=owner`. Each packet path matches one of the five `target_paths` globs above.
2. The `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var set to the packet path when invoking the Write.
3. The narrative-artifact-approval-gate hook validates packet presence + content-hash match before allowing the Write. The universal-floor `scripts/check_narrative_artifact_evidence.py` pre-commit gate re-validates at commit time.

At implementation start (after Codex GO and Slice 8 VERIFIED confirmed):

1. Prime Builder presents the proposed text for each file via AskUserQuestion, one file at a time.
2. Owner approves each file's proposed text via AskUserQuestion.
3. Prime Builder writes the per-file packet JSON (path matching the slice9 glob).
4. Prime Builder invokes Write with the env var pointing to the packet; the hook validates and admits.

This proposal does NOT generate or commit the packets at proposal-filing time; packets are implementation-time artifacts authorized by the `target_paths` globs.

### Implementation Order

1. Re-run the live-INDEX Slice 8 precondition one-liner (see § Sequencing Dependency). Confirm `VERIFIED:`. Record the captured output for the post-implementation report.
2. Activate implementation-start packet for this bridge thread.
3. For each file (operating-role.md, then prime-builder-role.md, then canonical-terminology.md, then CLAUDE.md, then AGENTS.md), in order:
   a. Present the proposed text via AskUserQuestion.
   b. Generate the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-slice9-<file-slug>.json`.
   c. Stage the narrative file + its packet and run `groundtruth-kb\.venv\Scripts\python.exe scripts/check_narrative_artifact_evidence.py --staged` (expect exit 0) to confirm the evidence is valid before proceeding.
   d. Edit the file with the packet env var set.
4. Run the verification gates (next section).
5. File the post-implementation report at `-NNN.md` for Codex review, including the captured precondition output and the narrative-evidence-gate exit-0 evidence.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, this slice's spec-to-test mapping:

| Specification | Verification Command | Expected Result |
|---|---|---|
| `GOV-SESSION-ROLE-AUTHORITY-001` v1 (citation requirement) | repo-venv Python presence check reading the 4 narrative files for the literal ID | All 4 files contain the literal ID |
| `DCL-SESSION-ROLE-RESOLUTION-001` v1 (citation requirement) | repo-venv Python presence check for the DCL ID | At least 4 files contain the literal ID |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (citation requirement) | repo-venv Python presence check for the ADR ID | At least 4 files contain the literal ID |
| `DCL-CONCEPT-ON-CONTACT-001` v1 | repo-venv Python presence check for the literal `session-stated role` in canonical-terminology.md | New glossary entry present |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 | repo-venv Python presence check for `::init gtkb (pb|lo)` in the new sections | Present in operating-role.md, CLAUDE.md, AGENTS.md, canonical-terminology.md |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` (F1 closure) | Stage each protected narrative file + matching packet; run `groundtruth-kb\.venv\Scripts\python.exe scripts/check_narrative_artifact_evidence.py --staged` | exit 0 (all narrative mutations have matching approval-packet evidence) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` CLAUSE-IN-ROOT | All target paths (narrative + packet globs) within `E:\GT-KB` | All target paths in-root |
| `GOV-FILE-BRIDGE-AUTHORITY-001` CLAUSE-INDEX-IS-CANONICAL | `bridge/INDEX.md` carries the post-impl `NEW: -NNN.md` entry at the top of this thread | INDEX entry present |
| Sequencing precondition (Slice 8 VERIFIED) | the repo-venv Python one-liner in § Sequencing Dependency, captured in the post-implementation report | Printed Slice 8 status line begins with `VERIFIED:` |
| Doctor canonical-terminology check | `groundtruth-kb\.venv\Scripts\gt.exe project doctor --check canonical_terminology` | Reports `session-stated role` as a recognized canonical term |

Example presence-check form (Windows/PowerShell-valid, repo-venv interpreter):

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; files=['.claude/rules/operating-role.md','.claude/rules/prime-builder-role.md','AGENTS.md','CLAUDE.md']; t='GOV-SESSION-ROLE-AUTHORITY-001'; print({f: (t in pathlib.Path(f).read_text(encoding='utf-8')) for f in files})"
```

## Owner Decisions / Input

This slice proceeds on the AskUserQuestion evidence already captured for the parent project. No new architectural decisions at proposal-filing time. Implementation start requires per-file AskUserQuestion approval for each formal-artifact-approval packet.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active; reactivated per owner AUQ S374). Covers `WI-3479`. Scope: Slices 4-10 of the interactive-session-role-override architecture.
- `DELIB-2507` — S371 owner directive establishing PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE.
- S371 AskUserQuestion decisions 1-6 — the architectural intent that Slice 9 codifies.
- Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md` — Slice 9 implementation authority.
- S375 AskUserQuestion (this session): owner directive to proceed with Slices 9 and 10 authorizes this thread's revisions.
- Per-file AskUserQuestion at implementation start: 5 packets, presented sequentially.

## Requirement Sufficiency

**Existing requirements sufficient.** The three new specs (GOV/DCL/ADR) are in MemBase as `specified`. No requirement revision needed. The F1 correction is a `target_paths` authorization-surface fix plus an added verification step, not a requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` clause-scope clarification convention: this slice is narrative-authority text revision plus one new canonical-terminology glossary entry, with their matching approval-packet evidence artifacts. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no MemBase row insert, no inventory artifact, no review-packet. Evidence-pattern tokens: rule revision, glossary update, narrative-authority text, per-file approval packets, no backlog mutation, no project mutation, no canonical-spec insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all target paths (5 narrative files + 5 packet globs under `.groundtruth/formal-artifact-approvals/`) live under `E:\GT-KB`. The runtime marker referenced in the new text (`.claude/session/active-session-role.json`) is also in-root. No application-layer paths, no `applications/<name>/` paths, no Agent Red references in a live-dependency role.

## Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | `.claude/rules/operating-role.md` carries the new § "Interactive Session Role Override" section citing the three new specs | repo-venv Python presence check + visual review |
| 2 | `.claude/rules/prime-builder-role.md` carries the brief subsection on session-resolved role authority | presence check + visual review |
| 3 | `.claude/rules/canonical-terminology.md` carries the new `session-stated role` glossary entry | presence check + visual review + doctor canonical-terminology check |
| 4 | `CLAUDE.md` Role precedence paragraph carries the durable-vs-session split sentence | presence check + visual review; remains under 300 lines per GOV-01 |
| 5 | `AGENTS.md` carries the parallel paragraph | presence check + visual review |
| 6 | One formal-artifact-approval packet per edited file, each matching its `target_paths` glob at `.groundtruth/formal-artifact-approvals/*-slice9-<file-slug>.json` | repo-venv Python glob + content-hash verification |
| 7 | **F1 closure:** staging each protected narrative file + its matching packet and running `check_narrative_artifact_evidence.py --staged` returns exit 0 | `groundtruth-kb\.venv\Scripts\python.exe scripts/check_narrative_artifact_evidence.py --staged` |
| 8 | Existing canonical text invariants preserved: "no markdown rule file can override the durable assignment map" remains in operating-role.md and AGENTS.md | presence check + visual review |
| 9 | Bridge applicability preflight passes on the post-implementation report | `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id ...` |
| 10 | ADR/DCL clause preflight passes (zero blocking gaps) | `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id ...` |
| 11 | Sequencing precondition satisfied: captured Slice 8 one-liner output in the post-implementation report begins with `VERIFIED:` | repo-venv Python one-liner at activation moment + recorded output |

## Risk and Rollback

- **Risk:** The operator forgets the live-INDEX precondition check. **Mitigation:** Implementation Order step 1 is explicit; acceptance criterion 11 fails Codex verification without the captured output. (Slice 8 is already VERIFIED, so the precondition is currently met.)
- **Risk:** Per-file packet AskUserQuestion overhead is 5 packets minimum. **Mitigation:** one-at-a-time presentation per established convention.
- **Risk:** A packet's `full_content_sha256` drifts from the written narrative body. **Mitigation:** the implementation order stages file + packet and runs `check_narrative_artifact_evidence.py --staged` (criterion 7) before relying on the edit; the universal-floor pre-commit gate re-validates at commit.
- **Risk:** `CLAUDE.md` exceeds its 300-line GOV-01 cap. **Mitigation:** the addition is ~4 lines; current length leaves headroom.
- **Risk:** A glossary entry collision with `operating role` confuses readers. **Mitigation:** the new entry's "Not to be confused with" field distinguishes the two terms.
- **Rollback:** each file's edit is one diff hunk; reverting restores the prior text. Packets remain as audit trail.

## Recommended Commit Type

`docs:` — Slice 9 is governance/documentation text revision. No code, no tests, no behavior change. The approval-packet JSON files are owner-approval evidence artifacts accompanying the docs edits, not code.

## Files Touched

5 narrative files (per target_paths):
- `.claude/rules/operating-role.md` (additive section)
- `.claude/rules/prime-builder-role.md` (additive subsection)
- `.claude/rules/canonical-terminology.md` (new glossary entry)
- `CLAUDE.md` (additive sentence in Role precedence paragraph)
- `AGENTS.md` (parallel additive paragraph)

5 formal-artifact-approval packets (now authorized in target_paths via per-file globs):
- `.groundtruth/formal-artifact-approvals/<date>-slice9-operating-role-md.json`
- `.groundtruth/formal-artifact-approvals/<date>-slice9-prime-builder-role-md.json`
- `.groundtruth/formal-artifact-approvals/<date>-slice9-canonical-terminology-md.json`
- `.groundtruth/formal-artifact-approvals/<date>-slice9-claude-md.json`
- `.groundtruth/formal-artifact-approvals/<date>-slice9-agents-md.json`

## Owner Action Required

At proposal review time: none beyond Codex review.

At implementation start (after Codex GO; Slice 8 VERIFIED precondition already met):
- AskUserQuestion approval for each of the 5 per-file formal-artifact-approval packets (one AUQ per file, presented sequentially).

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
