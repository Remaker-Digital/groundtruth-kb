# Scaffold Upgrade Tier A — Pure ADDs + APPEND-GITIGNORE

Status: NEW
Author: prime-builder (harness B / Claude Code)
Filed: session continuing prior dashboard-driven scaffold-drift remediation
Branch: develop

## Summary

Apply the lowest-risk subset of `python -m groundtruth_kb.cli project upgrade --apply`:
the 12 `ADD` actions (template files missing locally) plus the 3 `APPEND-GITIGNORE`
actions (additive ignore-list entries). The 4 `MERGE-EVENT-HOOKS` actions, the 13
`SKIP` actions on customized files, and any actions covered by an in-flight
bridge `WARNING` are **out of scope** and reserved for separate Tier B / Tier C
proposals.

This proposal also resolves a glossary-vs-reality contradiction: the
`scanner-safe-writer.py` PreToolUse credential-scan hook is described in
`.claude/rules/canonical-terminology.md` as a live hook with a `Source:`
citation to `DELIB-0687`, but the file is missing from `.claude/hooks/` and the
hook is not registered in `.claude/settings.json`. Tier A installs the file;
Tier B will register it. Until both ship, the canonical credential-scan surface
described in the glossary is non-functional locally.

## Specification Links

Cross-cutting specs triggered by this proposal's content and target paths
(per `config/governance/spec-applicability.toml` self-check):

- **GOV-FILE-BRIDGE-AUTHORITY-001** (blocking) — bridge thread mediates the
  upgrade; bridge/INDEX.md remains canonical workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (blocking) — this
  proposal cites every relevant governing specification.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (blocking) — verification
  derives tests from each linked spec; see `## Test Plan` below.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (blocking, conservative cite) —
  upgrade target paths are all under `E:\GT-KB` and respect the project root
  boundary; no `applications/` paths are touched.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — file-system changes
  are durable artifacts; rationale and verification evidence are preserved.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — traceability links
  this work to scaffold templates, the upgrade planner, and the canonical
  glossary.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — `scanner-safe-writer`
  hook's lifecycle (verified → orphan → re-installed) requires explicit state
  tracking.

Additional load-bearing rules and specs:

- `.claude/rules/codex-review-gate.md` — implementation requires Loyal
  Opposition GO before any apply.
- `.claude/rules/file-bridge-protocol.md` — file-bridge protocol governs this
  proposal's lifecycle.
- `.claude/rules/bridge-essential.md` — bridge integrity is the top-priority
  task; this proposal does not weaken protocol invariants.
- `.claude/rules/operating-model.md` §3 — scaffold drift remediation is part
  of the platform-implemented surface; the proposal does not claim
  intended-but-partial capability as implemented.
- `.claude/rules/canonical-terminology.md` — glossary entry for
  `scanner-safe-writer` cites `DELIB-0687` and treats the hook as live; this
  proposal restores filesystem alignment with that glossary claim.
- **GOV-RELEASE-READINESS-GOVERNED-TESTING-001** — scaffold drift is one of
  the dashboard's release-gate-visible risks; closing the Tier A subset
  improves release-readiness evidence.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

The most directly relevant prior records are:

- **DELIB-0736** — Bridge thread `gtkb-hook-scanner-safe-writer`, 12 versions,
  VERIFIED. The hook was originally installed and verified through this
  thread.
- **DELIB-1198** — Same bridge thread reclassified as ORPHAN (informational
  outcome). This is the lifecycle event that produced the current
  glossary-vs-reality gap.
- **DELIB-0687** — VERIFIED post-implementation verification of WI-3142
  Credential Scan Narrowing. Establishes the canonical credential pattern
  catalog (`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) used by both
  the hook template and the bridge-propose helper.

(The bridge-propose helper will additionally pre-populate glossary-seeded
candidates from `.claude/rules/canonical-terminology.md` and semantic-search
hits from the Deliberation Archive.)


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1255` — seed=search; bridge_thread; Bridge thread: gtkb-tier-a-current-main-integration (4 versions, ORPHAN)
- DA: `DELIB-0895` — seed=search; bridge_thread; Bridge thread: gtkb-tier-a-current-main-integration (4 versions, VERIFIED)
- DA: `DELIB-0813` — seed=search; bridge_thread; Bridge thread: gtkb-spec-pipeline-f6 (4 versions, ORPHAN)
- DA: `DELIB-1231` — seed=search; bridge_thread; Bridge thread: gtkb-project-boundary-and-upgrade-hardening (2 versions, ORPHAN)
- DA: `DELIB-1250` — seed=search; bridge_thread; Bridge thread: gtkb-spec-pipeline-f6 (4 versions, ORPHAN)

## Owner Decisions / Input

This proposal depends on owner approval per the AskUserQuestion-only
enforcement stack:

- **AUQ answer (this session, prior turn):** Owner replied "Continue Tier A"
  to the scoped tier-by-tier review presented after the option-13 startup
  selection. That reply authorizes Prime to draft this proposal and route
  it through the bridge for Loyal Opposition review.
- **Approval scope:** "Continue Tier A" authorizes (a) drafting and filing
  this proposal, (b) implementing if Codex GO is recorded, (c) executing the
  test plan in `## Test Plan`. It does NOT pre-authorize Tier B or Tier C,
  any `--force` apply, or any change outside the scoped action list in
  `## Scope`.
- **Outstanding owner decisions before VERIFIED:** none required. The Tier A
  subset is dispatchable (Axis 1 of the bridge automation model) — Codex
  review and Prime implementation can complete without further owner input.
  Per-artifact formal-approval packets are not required because none of the
  installed files are MemBase rows (GOV/SPEC/ADR/DCL/PB) or protected
  narrative artifacts.

## Scope

### IN SCOPE — 12 ADD actions

Files to be copied from `groundtruth-kb/templates/` into `E:\GT-KB`:

Hooks (7):
1. `.claude/hooks/intake-classifier.py`
2. `.claude/hooks/scanner-safe-writer.py`  *(closes the glossary-vs-reality gap; not registered in settings.json by this tier)*
3. `.claude/hooks/_delib_common.py`
4. `.claude/hooks/turn-marker.py`
5. `.claude/hooks/delib-preflight-gate.py`
6. `.claude/hooks/owner-decision-capture.py`
7. `.claude/hooks/gov09-capture.py`

Rules (4):
8. `.claude/rules/prime-builder.md` *(distinct from existing `prime-builder-role.md`)*
9. `.claude/rules/bridge-poller-canonical.md`
10. `.claude/rules/prime-bridge-collaboration-protocol.md`
11. `.claude/rules/report-depth.md` *(distinct from existing `report-depth-prime-builder-context.md`)*

Config (1):
12. `.claude/rules/canonical-terminology-policy.toml`

### IN SCOPE — 3 APPEND-GITIGNORE actions

Patterns appended to `.gitignore`:
13. `.claude/hooks/*.log` — Operational hook logs
14. `.groundtruth/` — KB working directory (chroma + cache)
15. `.claude/settings.local.json` — Adopter-owned local overlay

### OUT OF SCOPE (Tier B/C; deferred)

- 4 MERGE-EVENT-HOOKS (settings.json hook-list reordering) — Tier B.
- 13 SKIP actions on customized files — Tier C, per-file justification.
- 34 in-flight bridge WARNING entries — defer until each thread reaches VERIFIED.
- Registering `scanner-safe-writer.py` in `.claude/settings.json` PreToolUse
  array — Tier B (depends on the file landing first).

## Test Plan

### Pre-implementation tests (run before `--apply`)

1. **Specification linkage preflight** (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001):
   ```
   python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a-001
   ```
   Expected: `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`. Record `packet_hash` in the verdict file.

2. **Clause-test preflight** (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
   and adjacent ADR/DCL clauses):
   ```
   python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a-001
   ```
   Expected: exit 0, no blocking-severity must_apply clauses missing
   evidence.

3. **In-flight bridge gate confirmation** (GOV-FILE-BRIDGE-AUTHORITY-001):
   Re-run `plan_upgrade(Path('E:/GT-KB'))` immediately before apply; confirm
   the Tier A action set has not changed and that none of the 12 ADDs or 3
   APPEND-GITIGNOREs has acquired a WARNING (would indicate a new in-flight
   bridge intersects).

### Implementation step

4. Apply only the Tier A subset:
   ```
   python -m groundtruth_kb.cli project upgrade --apply --ignore-inflight-bridges
   ```
   Note: `--ignore-inflight-bridges` is required because 34 in-flight
   warnings would otherwise block apply. Tier A actions are independent of
   the warned threads (none of the 12 ADD targets or 3 gitignore patterns
   intersects an in-flight bridge file path).

   Per `cli.py:1556` the dry-run path skips execute_upgrade; apply proceeds
   to `execute_upgrade(...)` which runs in a payload branch with rollback
   receipt anchored on a real merge commit. See
   `docs/reference/upgrade-receipts.md`.

### Post-implementation tests (run after `--apply`)

5. **Plan re-verification** (GOV-RELEASE-READINESS-GOVERNED-TESTING-001):
   ```
   python -c "from pathlib import Path; from groundtruth_kb.project.upgrade import plan_upgrade; from collections import Counter; actions = plan_upgrade(Path('E:/GT-KB').resolve()); c = Counter(a.action.upper() for a in actions); print(c.most_common())"
   ```
   Expected: `ADD` count drops from 12 → 0; `APPEND-GITIGNORE` count drops
   from 3 → 0. `WARNING`, `INFORMATIONAL`, `SKIP`, `MERGE-EVENT-HOOKS` counts
   unchanged.

6. **Filesystem assertion** (canonical-terminology glossary alignment):
   ```
   python -c "from pathlib import Path; missing = [p for p in ['.claude/hooks/scanner-safe-writer.py', '.claude/hooks/intake-classifier.py', '.claude/hooks/_delib_common.py', '.claude/hooks/turn-marker.py', '.claude/hooks/delib-preflight-gate.py', '.claude/hooks/owner-decision-capture.py', '.claude/hooks/gov09-capture.py', '.claude/rules/prime-builder.md', '.claude/rules/bridge-poller-canonical.md', '.claude/rules/prime-bridge-collaboration-protocol.md', '.claude/rules/report-depth.md', '.claude/rules/canonical-terminology-policy.toml'] if not Path(p).exists()]; print('missing:', missing)"
   ```
   Expected: `missing: []`.

7. **Doctor regression** (GOV-RELEASE-READINESS-GOVERNED-TESTING-001):
   ```
   python -m groundtruth_kb.cli project doctor
   ```
   Expected: pass at the same baseline (harness=claude, role=prime-builder,
   PASS=21) or better. Specifically, `_check_cross_harness_trigger` and
   `_check_bridge_dispatch_liveness` must remain PASS.

8. **Hook regression** (bridge-essential.md, codex-review-gate.md):
   Trigger each currently-registered Claude Code hook event and confirm the
   pre-existing hooks still fire (`owner-decision-tracker.py` on Stop,
   `bridge-compliance-gate.py` on PreToolUse Write, `cross_harness_bridge_trigger.py`
   on PostToolUse and Stop). The 7 newly-added hooks are NOT registered by
   Tier A — verify they do not fire on any event.

9. **Gitignore semantics** (operational hygiene):
   ```
   git status --porcelain | grep -E '\.claude/hooks/.*\.log|\.groundtruth/|\.claude/settings\.local\.json' | head
   ```
   Expected: empty. Files matching the appended patterns must not appear in
   `git status`.

### Spec-to-test mapping (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)

| Spec | Verifying test step(s) |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 3 (in-flight gate); thread reaches VERIFIED through INDEX.md before any Tier B work |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (applicability preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping table |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | 6 (filesystem assertion confirms targets are under `E:\GT-KB`; no `applications/` paths) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 5 (plan re-verification) + 7 (doctor) |
| canonical-terminology.md glossary entry for `scanner-safe-writer` | 6 (filesystem assertion) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) | post-impl report preserves rationale + verification evidence |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) | post-impl report carries forward this proposal's spec links |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) | DELIB-0736 → DELIB-1198 → re-install lifecycle is documented in `## Prior Deliberations` |

## Acceptance Criteria

- [ ] All 12 ADD targets exist on disk after apply (test step 6 reports `missing: []`).
- [ ] All 3 APPEND-GITIGNORE patterns appear in `.gitignore`.
- [ ] `plan_upgrade()` re-run reports 0 ADDs and 0 APPEND-GITIGNOREs (test step 5).
- [ ] `gt project doctor` baseline PASS=21 holds or improves (test step 7).
- [ ] No pre-existing hook regression (test step 8).
- [ ] No untracked files match the appended ignore patterns (test step 9).
- [ ] `scanner-safe-writer.py` filesystem presence aligns with the glossary
      entry's claim of liveness — even though Tier A does not yet register
      the hook in `settings.json`. The glossary entry will be supplemented
      in the Tier B post-impl report to record the new lifecycle stage
      (per DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001).

## Risk + Rollback

### Risks

- **R1 (Low): Newly-added hook files are present but unregistered, causing
  later confusion.**
  Mitigation: Tier A explicitly does NOT touch `.claude/settings.json` — only
  the 4 separate MERGE-EVENT-HOOKS rows do, and those are deferred to Tier B.
  Test step 8 confirms only pre-existing hooks fire.

- **R2 (Low): `prime-builder.md` and `report-depth.md` ADD targets land
  alongside existing `prime-builder-role.md` and
  `report-depth-prime-builder-context.md`, creating governance-rule sprawl.**
  Mitigation: file paths are distinct so neither overwrites the other. Both
  can coexist as inert files; rule consolidation is a separate
  `.claude/rules/` review out of scope here. Flag for follow-up backlog
  entry if Codex review concurs.

- **R3 (Low): `--ignore-inflight-bridges` flag bypasses the warning that
  34 GO threads are in-flight.**
  Mitigation: Tier A targets are deliberately disjoint from any in-flight
  bridge file path. The flag suppresses an *informational* gate, not a
  *correctness* gate. Test step 3 re-confirms the action set immediately
  before apply.

- **R4 (Negligible): The `--apply` path runs in a payload branch with
  rollback receipt; if merge fails, no working-tree mutation persists.**
  No mitigation needed beyond standard `execute_upgrade` semantics.

### Rollback

If post-implementation tests fail or owner withdraws approval before VERIFIED:

1. `git revert <merge-commit-sha>` — the upgrade payload merge commit is
   atomic and reversible.
2. Confirm `plan_upgrade()` returns to 12 ADDs + 3 APPEND-GITIGNOREs (the
   state captured in this proposal).
3. File a `REVISED` version of this proposal documenting what failed and
   the revised approach.

## Recommended Commit Type

`feat:` — net-new infrastructure (7 hook files + 4 rule files + 1 config file
+ 3 ignore patterns). Per the Conventional Commits Type Discipline rule
(file-bridge-protocol.md), `chore:` would mis-categorize this since the
diff stat is +12 files net new, not maintenance-only. The Tier B and Tier C
follow-on commits will use `feat:` (settings.json hook registration) and
case-by-case typing (config/rule customization) respectively.

## Applicability Preflight

To be filled in by Codex (Loyal Opposition) at GO time per
`.claude/rules/file-bridge-protocol.md` Mandatory Applicability Preflight
Gate. Prime self-check (per the catch-22 case in
`file-bridge-protocol.md` Mandatory Pre-Filing Preflight Subsection): the
applicability rules above were grepped manually against
`config/governance/spec-applicability.toml` `applies_when_*` patterns; all
four blocking-severity rules and three advisory rules are cited in
`## Specification Links`. Final preflight will run after this proposal is
filed and the INDEX entry exists.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
