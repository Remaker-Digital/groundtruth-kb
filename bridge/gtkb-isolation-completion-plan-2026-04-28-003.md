NO-GO

# Loyal Opposition Review - GT-KB Isolation Completion Plan

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed documents:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`

## Claim

The combined `-001` plan plus `-002` owner-decision addendum is the proposed
canonical contract for completing GT-KB platform / Agent Red application
separation before execution begins.

## Verdict

NO-GO for execution as written.

The target platform/application model is directionally correct and the owner
decisions in `-002` are mostly actionable. However, the proposal still
misclassifies active GT-KB Loyal Opposition artifacts as Agent Red bootstrap
content, leaves the bridge relocation model inconsistent with the active bridge
protocol, and schedules `gt platform doctor` before the command exists in the
phase plan. Those are coherence-control defects in exactly the area this plan is
meant to stabilize.

## Prior Deliberations

No exact prior deliberation found for `gtkb-isolation-completion-plan-2026-04-28`.
Relevant adjacent deliberations found:

- `DELIB-1327` / `bridge/application-isolation-contract-008.md`: Agent Red app-root
  scaffold was VERIFIED, but broader isolation remained incomplete and deletion
  readiness stayed blocked.
- `DELIB-1328` / `bridge/application-isolation-contract-006.md`: GO for the
  revised Agent Red application isolation contract.
- `DELIB-1329` and `DELIB-1330`: prior NO-GO reviews on the application isolation
  contract.
- `DELIB-1098`, `DELIB-1043`, `DELIB-1041`: adjacent GTKB isolation wave/slice
  deliberations.

## Findings

### P1 - Active Codex / Loyal Opposition artifacts are classified as Agent Red bootstrap content

**Evidence:** `-001` line 259 includes `independent-progress-assessments/` in the
stale-dir deletion category, and line 261 says active `CODEX-*` documents move
to `applications/Agent_Red/codex-bootstrap/`. Current startup artifacts identify
these files as GroundTruth-KB / Loyal Opposition operating context:
`independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md`,
`CODEX-STANDING-PRIORITIES.md`, `CODEX-WAY-OF-WORKING.md`,
`CODEX-REVIEW-OPERATING-CONTRACT.md`, and `CODEX-LOYAL-OPPOSITION-RUNBOOK.md`.
They are loaded for GT-KB role startup and bridge review, not Agent Red app
runtime.

**Risk / impact:** Moving the active review operating contract into
`applications/Agent_Red/codex-bootstrap/` would make GT-KB's reviewer bootstrap
look application-owned. That directly conflicts with the 2026-04-28 scope
correction that GT-KB is the default active project and Agent Red is only an
adopter/demo unless explicitly selected.

**Recommended action:** Revise Section 1.3 and Section 2.3. Keep current
`independent-progress-assessments/CODEX-*`, `LOYAL-OPPOSITION-LOG.md`, and
active insight/report templates as GT-KB platform review artifacts unless a
specific file is proven Agent-Red-only. If Agent Red needs per-app Codex
bootstrap, generate a new app-local bootstrap from template rather than moving
the active GT-KB review corpus.

**Owner decision needed:** No. This follows the existing role/root-boundary
contract and the current GT-KB framing correction.

### P1 - Per-application bridge-file relocation conflicts with the active bridge protocol

**Evidence:** `-001` line 277 assigns application-specific session state to
`applications/<app>/bridge/`, and line 539 says root `bridge/INDEX.md` entries
may point to platform-root or per-app bridge files. The active protocol in
`.claude/rules/file-bridge-protocol.md` defines `bridge/` at project root as the
bridge directory, says all proposal/review/verification documents live there,
and gives the canonical file-line shape as `STATUS: bridge/{name}-{NNN}.md`.

**Risk / impact:** Moving hundreds of bridge files into
`applications/Agent_Red/bridge/` without first changing the protocol, poller,
startup scanner, INDEX parser, and writer rules can strand active or historical
threads. This is a coordination-layer migration, not a content move. If it is
handled as ordinary application-file cleanup, Prime and Loyal Opposition can
disagree about queue state.

**Recommended action:** Add an explicit bridge-routing sub-design before Phase 2
file moves. It must define whether `bridge/INDEX.md` may reference non-root
paths, how next-version files are written for per-app entries, how existing
INDEX lines are migrated, and which tests prove Prime/Codex scanners continue
to process only the live authoritative INDEX. Until that sub-design is GO/VERIFIED,
keep all active bridge files under root `bridge/`.

**Owner decision needed:** No, unless Mike wants to choose between "central
bridge files with app metadata" and "per-app bridge files with upgraded protocol."

### P1 - Phase 1 depends on `gt platform doctor`, but platform commands are scheduled for Phase 4

**Evidence:** `-001` line 928 makes Phase 1 run `gt platform doctor`. `-001`
lines 945-951 schedule `gt platform init` and `gt platform configure-host` for
Phase 4. A code search found current doctor support under
`groundtruth-kb/src/groundtruth_kb/project/doctor.py` and `gt project doctor`;
no `gt platform doctor` command exists in the current checkout.

**Risk / impact:** Phase 1 cannot be mechanically verified as written. If Prime
implements an ad hoc doctor inside Phase 1 without saying so, the phase plan
understates scope and creates another hidden dependency. If Prime skips it, the
plan's first stabilization phase loses its main drift-detection mechanism.

**Recommended action:** Either pull a minimal `gt platform doctor --pre-restructure`
implementation into Phase 1 as an explicit deliverable with tests, or change
Phase 1 to use existing checks only and defer `gt platform doctor` to Phase 4.
Do not leave it as an implicit future command.

**Owner decision needed:** No if Prime chooses the smallest verifiable path.

### P2 - Inventory sampling found unclassified or underclassified root artifacts

**Evidence:** A random root-file sample returned:
`pyproject.toml`, `docs.html`, `prechat-form-phone-screenshot.png`,
`generate-pdf.bat`, `README.md`, `groundtruth.db.pre-backfill-20260412-135740`,
`CNAME`, `requirements.txt`, and `_split_superadmin.py` among others. The plan
classifies several of these (`pyproject.toml`, `README.md`, `docs.html`,
`CNAME`, `_split_superadmin.py`), but does not classify `requirements.txt`,
`requirements-local.txt`, `requirements-test.txt`, `prechat-form-phone-screenshot.png`,
`generate-pdf.bat`, or the large DB backup/WAL-style artifacts. Current
`requirements*.txt` files are Agent Red dependencies and still reference the old
GitHub `groundtruth-kb` install pattern; the screenshot and PDF/batch artifacts
appear Agent-Red-specific or stale but are not dispositioned.

**Risk / impact:** Phase 2 will hit avoidable stop-and-decide moments during
file moves. Worse, unclassified dependency files can leave Agent Red's package
install path or GT-KB's framework install path pulling the wrong requirements.

**Recommended action:** Add an explicit inventory appendix for root-level files
and generated/database artifacts, including `requirements*.txt`, `*.bat`,
standalone screenshots/images, DB backups/WAL/SHM/corrupt snapshots, root logs,
and PDF generation artifacts. Assign each one: platform, Agent Red, delete,
archive, or owner-gated.

**Owner decision needed:** Only for destructive deletion of backups or artifacts
whose historical value is uncertain.

## Positive Findings

- The Section 2 platform/application model satisfies the owner's core model:
  `E:\GT-KB` is the platform and `applications/<app>` is the application slot.
- The `-002` always-on dashboard decision is compatible with the "do not
  auto-install cloud SDKs" stance. Dashboard service is local GT-KB
  infrastructure; Azure/GitHub/Docker/Shopify tooling remains external and
  manually authenticated.
- The tag-in-place migration is a reasonable direction. Current DB tables
  inspected (`specifications`, `work_items`, `tests`, `current_deliberations`,
  `deliberations`) do not have `application_id`, so the proposal correctly
  treats this as a schema migration rather than an existing feature.
- Deferring Phase 2 file moves to the next session is correct pacing. The file
  moves are too large and too risky to combine with proposal review and Phase 1
  cleanup in one session.

## Required Revision Before GO

1. Correct the disposition of `independent-progress-assessments/` and active
   Codex/Loyal Opposition documents so they remain GT-KB platform artifacts.
2. Add a bridge-routing migration design or keep bridge files centralized until
   the protocol and tooling are upgraded.
3. Resolve the `gt platform doctor` phase dependency.
4. Add a root-file/generated-artifact inventory appendix covering the sampled
   omissions and the relevant dependency files.

## Verification Performed

- Read full bridge entry from live `bridge/INDEX.md`: latest actionable entry was
  `NEW: bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`.
- Read `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` and `-002.md`.
- Read `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/project-root-boundary.md`.
- Queried `groundtruth.db` for relevant deliberations and DB column state.
- Sampled 10 root files with `Get-ChildItem -File | Get-Random -Count 10`.
- Searched the current codebase for `gt platform doctor` / platform doctor
  support.

