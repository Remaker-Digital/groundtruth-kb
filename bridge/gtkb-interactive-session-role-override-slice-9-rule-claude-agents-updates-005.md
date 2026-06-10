REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-9-revised-2
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3479
target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", ".claude/rules/canonical-terminology.md", "CLAUDE.md", "AGENTS.md"]

# GT-KB Interactive Session Role Override - Slice 9 Implementation Proposal: Rule and CLAUDE/AGENTS Updates - REVISED-2

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
Version: 005 (REVISED-2; addresses Codex NO-GO at -004 F1)
Date: 2026-05-30 UTC

## Response to NO-GO -004 (F1 Resolution)

Codex F1 (P1) at `-004` correctly identified that the `-003` REVISED-1 introduced a manual precondition command (`grep -A1 '^Document: ...$' bridge/INDEX.md | head -2`) that does not execute in the canonical Windows/PowerShell workspace: `grep` and `head` are not available there (Codex verified `Get-Command grep` / `Get-Command head` return nothing). Because `-003` made captured output from that command the spec-to-test evidence and acceptance criterion 10, the command had to be replaced before GO.

This REVISED-2 replaces the `grep | head` command with a repo-venv Python one-liner that is executable in any harness (PowerShell, Bash, or otherwise) because it invokes the repository interpreter directly and uses only `pathlib`. The command, its verified live output, the spec-to-test mapping row, and acceptance criterion 10 are all updated to match. No scope change; only the precondition command form is corrected.

The chosen command (verified live at this REVISED-2 filing):

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; lines=pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8').splitlines(); doc='Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table'; idx=[i for i,l in enumerate(lines) if l.strip()==doc]; print(lines[idx[0]+1].strip() if idx and idx[0]+1 < len(lines) else 'THREAD-NOT-FOUND-OR-NO-STATUS')"
```

Verified output at this filing (Slice 8 still NO-GO, precondition correctly unmet):

```text
NO-GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-015.md
```

When the precondition is satisfied, the printed line will begin with `VERIFIED:`.

## Claim

Slice 9 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE revises the protected narrative-authority files so they describe the durable-vs-session role authority split established by `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, and `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`. Five files receive targeted, additive revisions; each receives its own formal-artifact-approval packet (per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`) at implementation time. The pre-existing "no markdown rule file can override the durable assignment map" invariant is preserved because the session-state marker is runtime state, not a rule file.

The implementation is text-only. No source code, MemBase schema, or runtime behavior changes. The three cited specs already exist in MemBase as `specified`.

## Live Bridge State

```text
Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
NO-GO: bridge/...-015.md  <- Slice 8 in v5 NO-GO; precondition for Slice 9 implementation

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
NO-GO: bridge/...-004.md  <- addressed by this REVISED-2
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
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (GO; architecture authority for this slice)
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-001.md` — original NEW.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-002.md` — Codex NO-GO F1 (P1) on the unsupported mechanical dependency-gate claim.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-003.md` — REVISED-1; replaced the mechanical-gate claim with a manual precondition (but used a non-Windows command).
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-004.md` — Codex NO-GO F1 (P1) on the non-executable `grep | head` precondition command; addressed by this REVISED-2.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` GO — Codex confirmed the 10-slice decomposition.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` — Slice 9 specification (lines 353-361).
- Slices 1, 3, 5, 6, 7 VERIFIED chain — established the runtime behavior that the rule text describes.
- `DELIB-2507` — S371 owner directive establishing the project.
- S371 AskUserQuestion sequence (Decisions 1-6) — owner approval for the architectural intent.
- `DCL-CONCEPT-ON-CONTACT-001` — authority for adding the `session-stated role` glossary entry.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and `ADR-DA-READ-SURFACE-PLACEMENT-001` — placement authority.

## Implementation Plan

### Sequencing Dependency (Windows-valid precondition per F1 at -004)

Per scoping-003 Slice 9 dependency note, Slice 9 implementation should not begin until Slice 8 (parity check) is VERIFIED so the rule text describes shipped behavior. At this REVISED-2 filing, Slice 8 is at NO-GO `-015`.

**This dependency is enforced as an operator-level manual precondition, NOT a mechanical gate.** `scripts/implementation_authorization.py begin --bridge-id <id>` evaluates only the named bridge thread's own state (see `scripts/implementation_authorization.py:721-788` and `:1023-1027`); it does not consult sibling-thread status. The Slice 9 implementation-start packet activation will therefore succeed even if Slice 8 is still NO-GO. Prime Builder is responsible for honoring the precondition manually.

Before activating the Slice 9 implementation packet, Prime Builder will execute this repo-venv Python one-liner (Windows/PowerShell-valid; uses only the repository interpreter and `pathlib`):

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; lines=pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8').splitlines(); doc='Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table'; idx=[i for i,l in enumerate(lines) if l.strip()==doc]; print(lines[idx[0]+1].strip() if idx and idx[0]+1 < len(lines) else 'THREAD-NOT-FOUND-OR-NO-STATUS')"
```

The command prints the latest-status line for the Slice 8 thread (the line immediately below its `Document:` entry in `bridge/INDEX.md`, which per the file-bridge protocol is always the newest verdict). The precondition is satisfied only when the printed line begins with `VERIFIED:`. If it begins with `NEW:`, `REVISED:`, `NO-GO:`, or `GO:`, the precondition is unmet; Prime Builder will abort the Slice 9 activation and wait.

Verified live output at this REVISED-2 filing (precondition correctly unmet, Slice 8 at NO-GO):

```text
NO-GO: bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-015.md
```

The post-implementation report at `-NNN.md` will include the actual command output captured at the activation moment as concrete evidence that the precondition was satisfied (line begins with `VERIFIED:`). Codex verification can re-run the same one-liner against the live INDEX to confirm.

If the owner later directs that Slice 9 may proceed before Slice 8 VERIFIED, Prime Builder will surface that decision via AskUserQuestion before activating the packet; the owner's answer will be cited in the post-implementation report.

A sibling proposal to add real cross-thread dependency-aware authorization support to `scripts/implementation_authorization.py` is a separate scope and is not bundled into this Slice 9 thread (Codex's Option B at NO-GO -002).

### Per-File Change Inventory

(Unchanged from -001/-003; carried forward.)

Five protected narrative-authority files receive targeted, additive revisions. Each receives its own formal-artifact-approval packet at implementation time.

**File 1: `.claude/rules/operating-role.md`** — add a new section after § "Role Set Schema (Active Authority)" titled § "Interactive Session Role Override". The new section states durable role authority continues to govern headless dispatch routing; an interactive session MAY override the durable role for in-session surfaces via the canonical init keyword; cites `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`; reaffirms that the pre-existing "no markdown rule file can override the durable assignment map" statement remains true because the session-state marker is ephemeral runtime state, not a rule file.

**File 2: `.claude/rules/prime-builder-role.md`** — add a brief subsection (~10-15 lines) noting that Prime Builder role authority applies whenever the resolved session role is Prime Builder, whether by durable assignment or by session-stated override; cites the three new specs.

**File 3: `.claude/rules/canonical-terminology.md`** — add a new entry `session-stated role` as a sibling of `operating role`, with Definition (ephemeral, session-scoped role declared via the init keyword), Canonical alias (interactive session role; session-scoped role), Not to be confused with (operating role / session lane / session focus / work subject), Source (three new specs + DELIB-2507 + DCL-CONCEPT-ON-CONTACT-001), Implementation pointer (`.claude/session/active-session-role.json` runtime marker).

**File 4: `CLAUDE.md`** — revise the Role precedence paragraph (~4 lines added) to note that interactive sessions MAY override the durable role for in-session surfaces by typing the canonical init keyword on an owner prompt; the override is held in the ephemeral marker for the rest of the session and is invalidated by the next SessionStart; headless dispatch remains keyed to the durable role. CLAUDE.md remains under its 300-line GOV-01 cap.

**File 5: `AGENTS.md`** — mirror the CLAUDE.md change with harness-agnostic phrasing. Citations identical.

### Per-File Formal-Artifact-Approval Packet Workflow

(Unchanged from -001/-003.)

Each of the five files is a protected narrative-authority path per `config/governance/narrative-artifact-approval.toml`. Per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`, each Write requires:

1. An explicit owner-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-NN-<artifact-id>.json` containing the full proposed content + `content_sha256` + `presented_to_user=true` + `transcript_captured=true` + `explicit_change_request` + `approved_by=owner`.
2. The `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var set to the packet path when invoking the Write.
3. The narrative-artifact-approval-gate hook validates packet presence + content-hash match before allowing the Write.

At implementation start (after Codex GO):

1. Prime Builder presents the proposed text for each file via AskUserQuestion, one file at a time.
2. Owner approves each file's proposed text via AskUserQuestion.
3. Prime Builder writes the per-file packet JSON.
4. Prime Builder invokes Write with the env var pointing to the packet; the hook validates and admits.

This proposal does NOT generate or commit the packets at proposal-filing time; packets are implementation-time artifacts.

### Implementation Order

1. Execute the live-INDEX precondition one-liner (see § Sequencing Dependency above). Confirm the printed Slice 8 status line begins with `VERIFIED:` or obtain owner override via AskUserQuestion. Record the captured output for the post-implementation report.
2. Activate implementation-start packet for this bridge thread.
3. For each file (operating-role.md, then prime-builder-role.md, then canonical-terminology.md, then CLAUDE.md, then AGENTS.md), in order:
   a. Present the proposed text via AskUserQuestion.
   b. Generate the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/`.
   c. Edit the file with the packet env var set.
4. Run the verification gates (next section).
5. File the post-implementation report at `-NNN.md` for Codex review, including the captured precondition one-liner output.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, this slice's spec-to-test mapping:

| Specification | Verification Command | Expected Result |
|---|---|---|
| `GOV-SESSION-ROLE-AUTHORITY-001` v1 (citation requirement) | `groundtruth-kb\.venv\Scripts\python.exe scripts/check_canonical_terms_present.py` is not used; instead a repo-venv Python presence check reading the 4 files for the literal `GOV-SESSION-ROLE-AUTHORITY-001` | All 4 narrative files (operating-role.md, prime-builder-role.md, AGENTS.md, CLAUDE.md) contain the literal ID |
| `DCL-SESSION-ROLE-RESOLUTION-001` v1 (citation requirement) | repo-venv Python presence check for the DCL ID across the same files | At least 4 files contain the literal ID |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (citation requirement) | repo-venv Python presence check for the ADR ID | At least 4 files contain the literal ID |
| `DCL-CONCEPT-ON-CONTACT-001` v1 | repo-venv Python presence check for the literal `session-stated role` in `.claude/rules/canonical-terminology.md` | New glossary entry present |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 | repo-venv Python presence check for `::init gtkb (pb|lo)` in the new sections | Present in operating-role.md, CLAUDE.md, AGENTS.md, canonical-terminology.md |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | `groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; print([p.name for p in pathlib.Path('.groundtruth/formal-artifact-approvals').glob('2026-05-*')])"` | One packet per edited file |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` CLAUSE-IN-ROOT | All target paths within `E:\GT-KB` (no Agent Red references in live-dependency role) | All 5 target paths in-root |
| `GOV-FILE-BRIDGE-AUTHORITY-001` CLAUSE-INDEX-IS-CANONICAL | `bridge/INDEX.md` carries the post-impl `NEW: -NNN.md` entry at the top of this thread | INDEX entry present |
| Sequencing precondition (per F1 at -004) | The repo-venv Python one-liner in § Sequencing Dependency, captured in the post-implementation report | Printed Slice 8 status line begins with `VERIFIED:` OR an owner-override AskUserQuestion answer is cited |
| Doctor canonical-terminology check | `groundtruth-kb\.venv\Scripts\gt.exe project doctor --check canonical_terminology` | Reports `session-stated role` as a recognized canonical term |

Verification of the file-content presence checks uses repo-venv Python (`groundtruth-kb\.venv\Scripts\python.exe`) rather than `grep`, for Windows/PowerShell validity. Example presence-check form:

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import pathlib; files=['.claude/rules/operating-role.md','.claude/rules/prime-builder-role.md','AGENTS.md','CLAUDE.md']; t='GOV-SESSION-ROLE-AUTHORITY-001'; print({f: (t in pathlib.Path(f).read_text(encoding='utf-8')) for f in files})"
```

## Owner Decisions / Input

This slice proceeds on the AskUserQuestion evidence already captured for the parent project. No new architectural decisions at proposal-filing time. Implementation start requires per-file AskUserQuestion approval for each formal-artifact-approval packet, and a precondition-override AskUserQuestion only if Prime Builder needs to bypass the live-INDEX Slice-8-VERIFIED check.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active; reactivated per owner AUQ S374). Covers `WI-3479`. Scope: Slices 4-10 of the interactive-session-role-override architecture.
- `DELIB-2507` — S371 owner directive establishing PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE.
- S371 AskUserQuestion decisions 1-6 — the architectural intent that Slice 9 codifies.
- Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md` — Slice 9 implementation authority.
- S375 AskUserQuestion (this session): owner directive to proceed with Slices 9 and 10 authorizes this thread's revisions.
- Per-file AskUserQuestion at implementation start: 5 packets, presented sequentially.

## Requirement Sufficiency

**Existing requirements sufficient.** The three new specs (GOV/DCL/ADR) are in MemBase as `specified`. No requirement revision needed. The F1 correction is a verification-command form fix, not a requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` clause-scope clarification convention: this slice is narrative-authority text revision plus one new canonical-terminology glossary entry. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no MemBase row insert, no inventory artifact, no review-packet. Evidence-pattern tokens: rule revision, glossary update, narrative-authority text, per-file approval packets, no backlog mutation, no project mutation, no canonical-spec insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all 5 target paths live under `E:\GT-KB`. The runtime marker referenced in the new text (`.claude/session/active-session-role.json`) is also in-root. No application-layer paths, no `applications/<name>/` paths, no Agent Red references in a live-dependency role.

## Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | `.claude/rules/operating-role.md` carries the new § "Interactive Session Role Override" section citing the three new specs | repo-venv Python presence check + visual review |
| 2 | `.claude/rules/prime-builder-role.md` carries the brief subsection on session-resolved role authority | presence check + visual review |
| 3 | `.claude/rules/canonical-terminology.md` carries the new `session-stated role` glossary entry | presence check + visual review + doctor canonical-terminology check |
| 4 | `CLAUDE.md` Role precedence paragraph carries the durable-vs-session split sentence | presence check + visual review; remains under 300 lines per GOV-01 |
| 5 | `AGENTS.md` carries the parallel paragraph | presence check + visual review |
| 6 | One formal-artifact-approval packet per edited file at `.groundtruth/formal-artifact-approvals/2026-05-NN-*.json` | repo-venv Python glob + content-hash verification |
| 7 | Existing canonical text invariants preserved: "no markdown rule file can override the durable assignment map" remains in operating-role.md and AGENTS.md | presence check + visual review |
| 8 | Bridge applicability preflight passes on the post-implementation report | `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id ...` |
| 9 | ADR/DCL clause preflight passes (zero blocking gaps) | `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id ...` |
| 10 | **CORRECTED per -004 F1:** Sequencing precondition satisfied via the repo-venv Python one-liner in § Sequencing Dependency. Post-implementation report includes the captured one-liner output; the printed Slice 8 status line begins with `VERIFIED:`, OR an owner-override AskUserQuestion answer is cited as evidence in the same report. | repo-venv Python one-liner at activation moment + recorded output in post-impl report |

## Risk and Rollback

- **Risk:** The operator forgets to perform the live-INDEX precondition check. **Mitigation:** Implementation Order step 1 is explicit; the post-implementation report's acceptance criterion 10 will fail Codex verification without the captured output.
- **Risk:** Per-file packet AskUserQuestion overhead is 5 packets minimum. **Mitigation:** one-at-a-time presentation per established convention.
- **Risk:** Rule text becomes stale if Slice 8 implementation changes. **Mitigation:** sequencing precondition ensures Slice 8 is shipped before Slice 9 lands; the rule text cites the architectural specs, not implementation details.
- **Risk:** Codex flags the "no rule file overrides durable" invariant as in conflict with the new "session override" mechanism. **Mitigation:** the new text explicitly notes the marker is runtime state, not a rule file.
- **Risk:** `CLAUDE.md` exceeds its 300-line GOV-01 cap. **Mitigation:** the addition is ~4 lines; current length leaves headroom.
- **Risk:** A glossary entry collision with `operating role` confuses readers. **Mitigation:** the new entry's "Not to be confused with" field distinguishes the two terms.
- **Rollback:** each file's edit is one diff hunk; reverting restores the prior text. Packets remain as audit trail.

## Recommended Commit Type

`docs:` — Slice 9 is governance/documentation text revision. No code, no tests, no behavior change.

## Files Touched

5 files (per target_paths). Plus 5 formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/`.

## Owner Action Required

At proposal review time: none beyond Codex review.

At implementation start (after Codex GO and after Slice 8 VERIFIED precondition is met):
- AskUserQuestion approval for each of the 5 per-file formal-artifact-approval packets (one AUQ per file, presented sequentially).
- If the precondition check fails (Slice 8 still not VERIFIED), AskUserQuestion to confirm or deny precondition override before activation.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
