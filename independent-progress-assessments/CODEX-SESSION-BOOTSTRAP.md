# Session Bootstrap - GroundTruth-KB

Purpose: one short startup file that makes session behavior deterministic after
restart.

## What To Expect On Restart

These changes take effect automatically when the active AI harness starts in
this workspace and reads `AGENTS.md`:

- The assigned operating role must be loaded before role-specific permissions or
  restrictions are applied.
- Fresh-session startup discovers the assigned operating role from
  `.claude/rules/operating-role.md`.
- Prime Builder work follows Prime Builder governance; Loyal Opposition review
  follows Loyal Opposition governance.
- Prime Builder / Loyal Opposition coordination uses the file bridge in
  `bridge/`.
- Both Prime Builder and Loyal Opposition startup procedures load
  `.claude/rules/canonical-terminology.md` so the live glossary is available
  before ordinary role work.
- The GT-KB root boundary is mandatory: all active GT-KB artifacts must remain
  within `E:\GT-KB`; all GT-KB application files must remain within
  `E:\GT-KB\applications\`; Agent Red files must remain within
  `E:\GT-KB\applications\Agent_Red\`. There are no exceptions.
- The file bridge is always available through `bridge/INDEX.md` and must be
  checked at startup in both Prime Builder and Loyal Opposition roles.
- The live contents of `bridge/INDEX.md` are the sole authoritative source for
  bridge queue state. Startup reports, dashboard fields, cached scan counts,
  copied excerpts, summaries, and other derived artifacts are context only and
  must not determine current bridge state.
- Loyal Opposition has permanent owner authority to diagnose and repair correct
  bridge function and bridge use, including downstream bridge-dependent
  artifacts required to sustain bridge function and full utilization.
- When Prime Builder starts a fresh session, any latest `GO` or `NO-GO` bridge
  entry is included in the continuation scope for the prior session; those
  entries may be Loyal Opposition responses created in a separate previous
  session.
- The poller is separate from the bridge. The retired OS poller remains
  disabled, but the verified smart poller should be used when it is available
  and functioning. When smart-poller automation is unavailable, use manual scans
  or activate monitoring only when Prime Builder and Loyal Opposition are
  running in separate harnesses or asynchronous monitoring is otherwise needed.
- Prime Builder startup presents the GT-KB numbered session-focus choices to the
  owner. Loyal Opposition startup does not present those choices.
- The owner's first message in a fresh session is only a session-start stimulus,
  not informational input. Do not interpret it as a focus choice, task prompt,
  approval, answer, or owner decision; present startup first, then wait for the
  next owner message before choosing or mapping session work.
- Loyal Opposition fresh sessions start prepared to review and verify Prime
  Builder work; their first task is to verify that the bridge is functioning.
- If the bridge is not functioning, Loyal Opposition diagnoses and repairs it
  first, with owner pre-approval to make required file and configuration
  changes.
- Proposal review, code review, and alternatives investigation are the primary
  work modes when the active role is Loyal Opposition.
- The review contract, checklists, and templates are part of the expected
  startup context when the active role is Loyal Opposition.

These changes now activate automatically when `.claude/rules/operating-role.md`
declares Loyal Opposition mode:

- non-mutating review-mode hook behavior

Optional local environment overrides remain available:

- force read-only behavior:
  - `LOYAL_OPPOSITION_READONLY=1`
  - `CODEX_REVIEW_MODE=1`
- temporarily allow builder-style hook behavior during an explicitly approved implementation session:
  - `LOYAL_OPPOSITION_READONLY=0`
  - `CODEX_REVIEW_MODE=0`

## Recommended Review-Session Startup

**Phase A - File bridge verification (first priority):**
1. Read `bridge/INDEX.md`.
2. Treat the live read as authoritative; do not use cached or generated bridge
   scan values to determine current state.
3. Verify the bridge is functioning before ordinary Prime Builder or Loyal
   Opposition work.
4. If the bridge is not functioning, diagnose and repair bridge files,
   configuration, or automation as needed; this repair authority is
   owner-pre-approved for bridge restoration.
5. In Loyal Opposition mode, identify document entries whose latest status is
   `NEW` or `REVISED`.
6. In Prime Builder mode, identify latest `GO` or `NO-GO` entries and include
   them in "Continue Last Session" scope.
7. In Loyal Opposition mode, process latest `NEW` or `REVISED` entries from
   oldest to newest using `.claude/rules/file-bridge-protocol.md`.
8. In Prime Builder mode, do not process latest `NEW`, `REVISED`, or
   `VERIFIED` entries as actionable queue work. Prime Builder bridge handling is
   limited to latest `GO` or `NO-GO` entries.
9. Report scan count: "File bridge scan: N entries processed."

**Phase B — Local bootstrap (after bridge obligations are clear):**
8. Start the assigned AI harness in this workspace:
   `E:\GT-KB`
9. Review-mode hooks should auto-activate from `.claude/rules/operating-role.md`.
   Only set an environment flag if you need to force or override the detected mode.
10. Confirm the assigned AI harness loads:
   - `AGENTS.md`
   - `.claude/rules/operating-role.md`
   - the currently assigned role file
   - `.claude/rules/canonical-terminology.md`
   - `independent-progress-assessments/CODEX-STANDING-PRIORITIES.md`
   - `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
   - `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md`
   - `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md`
   - `independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md`
11. For substantial work, use:
   - `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`
   - `independent-progress-assessments/TEMPLATE-CODE-REVIEW.md`
   - `independent-progress-assessments/TEMPLATE-DECISION-MEMO.md`

## Quick Restart Prompt

Use this at the start of a new session if needed:

```text
Start in the GroundTruth-KB role recorded by `.claude/rules/operating-role.md`.
Load AGENTS.md, the currently assigned role file,
.claude/rules/canonical-terminology.md,
independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md,
independent-progress-assessments/CODEX-STANDING-PRIORITIES.md,
independent-progress-assessments/CODEX-WAY-OF-WORKING.md,
independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md,
independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md, and
independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md. Apply only the
permissions and restrictions for the assigned operating role. Use
bridge/INDEX.md as the file bridge. Prime Builder acts only on latest `GO` or
`NO-GO` entries; Loyal Opposition processes latest `NEW` or `REVISED` entries.
```

## Read-Only Review Mode Behavior

When Loyal Opposition review mode is active, the local hook behavior should:

- skip scheduler mutation
- skip assertion-run pruning
- read session handoff without consuming it

## Boundary

- The `.claude/` skills and hook changes are local-only because `.claude/` is git-ignored in this repo.
- The tracked baseline for intended setup lives in `config/agent-control/`.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

