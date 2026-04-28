---
name: GT-KB non-disruptive upgrade capability priority
description: Pre-Azure strategic priority — ability to upgrade adopter environments (including CTO's) to new GT-KB releases without disrupting in-flight work. Owner-set ordering: this ships before Azure SaaS readiness work.
type: project
originSessionId: 766f6784-f0b0-408f-8071-867d2866ef86
---
**Owner directive (S298, 2026-04-17)**: "Before we consider Azure we have other things to complete. Please make a note about investigation of non-disruptive installation of GT-KB upgrades. We have several days to deal with enhancements of our production deployments to Azure, as long as we can upgrade the CTO's environment with the new release."

**S299 REVISION (2026-04-17) — owner selected Option C (parallelize)**: non-disruptive upgrade and Azure Enterprise SaaS Readiness taxonomy run as concurrent post-Phase-A workstreams (not serial). Non-disruptive upgrade is no longer strictly "pre-Azure" — it is co-priority with the Azure taxonomy bridge after Tier A Phase A ships as v0.6.0. Recorded as DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL.

**Why:** CTO is getting a GT-KB adopter environment (scaffolded from v0.5.0 or v0.6.0). They will be doing real work in that environment. When GT-KB ships v0.6.x/v0.7.x, the CTO's environment must receive those upgrades without:
- losing their customizations
- breaking their in-flight bridges
- requiring them to re-scaffold from scratch
- introducing silent inert-hook states (per bridge/gtkb-hook-scanner-safe-writer-010.md Finding 1)

This remains an essential capability for any adopter. Post-S299 this no longer blocks Azure taxonomy work — the two scopes parallelize. Owner accepts higher bridge volume + disciplined scope separation as the price of parallel progress.

**How to apply:** When Phase A Tier A lands (v0.6.0), draft a new scope bridge `gtkb-non-disruptive-upgrade-investigation-001` covering the investigation below. Do NOT start this work while Tier A is still in-flight — current track is still decision-capture revision + scanner-safe-writer post-impl VERIFY.

**Investigation scope (to define in the scope bridge):**

1. **Current-state audit of `gt project upgrade`** — inventory what upgrade does today:
   - `_MANAGED_HOOKS` and `_MANAGED_RULES` hash-drift detection (exists)
   - `_plan_missing_managed_files` unconditional missing-file repair (added S298 via `37a88cc` per scanner-safe-writer Finding 1 fix)
   - `_plan_settings_registration` for PreToolUse registrations (added S298)
   - `_plan_gitignore_patterns` for log-file exclusions (added S298)
   - Version-gated hash-drift skip-unless-force for customized files
   - Gap: `.claude/settings.json` merge semantics beyond PreToolUse additions (PostToolUse, Stop, UserPromptSubmit, etc.)
   - Gap: `.claude/skills/` subdir upgrade (pending Tier A #4 decision-capture)
   - Gap: `groundtruth.toml` schema migrations
   - Gap: `groundtruth.db` schema migrations (if any)
   - Gap: rollback path for failed upgrades

2. **Customization preservation model** — currently upgrade skips hash-different files unless `--force`. Is that right for all managed-file classes?
   - Hooks: adopters might customize credential patterns → skip is right
   - Rules: adopters might add project-specific rules → skip is right
   - Skills: adopters might extend prompts → skip is right
   - Config (settings.json, gitignore): adopters add entries → merge (already done for specific cases), but generalize

3. **Upgrade atomicity and rollback** — what happens if upgrade fails mid-way?
   - Current: `.bak` backup of overwritten files
   - Gap: no rollback command; no transaction guarantee
   - Need: explicit `gt project upgrade --rollback-to <commit/version>`?

4. **Upgrade pre-flight checks** — what should doctor/upgrade verify BEFORE modifying anything?
   - Git state clean (or warn)
   - In-flight bridges not affected by hook changes
   - `.claude/settings.json` is parseable
   - Profile still matches (can't downgrade from dual-agent to local-only without confirmation)
   - Backup directory writable

5. **Same-version drift surface** — what other drifts could exist at same scaffold version?
   - Settings.json hook registrations (handled S298)
   - Gitignore patterns (handled S298)
   - Missing managed files (handled S298)
   - BRIDGE-INVENTORY.md missing/outdated
   - Schema ADRs/DCLs not present in MemBase (?)
   - Workflows CI files in `.github/workflows/` — NOT currently managed
   - Missing `.claude/rules/` mandatory files (e.g., `bridge-essential.md`)

6. **Version semantics and release train** — what does "upgrade from v0.5 to v0.6" mean?
   - Semantic version: major = breaking, minor = additive, patch = fix
   - Currently: all changes bundle under one `scaffold_version` bump
   - Gap: no explicit breaking-change annotation in release notes
   - Need: `UPGRADE_NOTES.md` per release describing manual actions adopters may need?

7. **Adopter-facing UX** — what does the upgrade experience look like?
   - Current: `gt project upgrade --dry-run` then `gt project upgrade --apply`
   - Gap: no preview of what the upgrade WILL change (only a list of file names)
   - Gap: no changelog integration
   - Gap: no interactive choose-what-to-upgrade mode
   - Need: better ergonomics for adopters who aren't GT-KB developers

**Sequencing** (S299 Option C):
- Tier A #2 VERIFIED ✅
- Tier A #4 VERIFIED ✅
- Tier A Phase A complete (#1-#6 all land) — gives v0.6.0 milestone
- Then PARALLEL (no longer serial):
  - `gtkb-non-disruptive-upgrade-investigation-001` scope bridge
  - `gtkb-azure-enterprise-readiness-taxonomy-001` scope bridge
- Each scope thread owns its own child bridges; zero file-ownership conflict expected between them at taxonomy stage.

**Success criteria** (draft — refine in scope bridge):
- CTO can run `gt project upgrade --apply` on their v0.6.0 environment to receive v0.7.0 without:
  - losing any of their bridge work
  - breaking their in-flight sessions
  - needing manual re-scaffolding
- Upgrade preserves all customizations or surfaces them with `skip` actions
- Pre-flight checks catch issues before any file is modified
- Rollback is possible if the upgrade causes regression
- Adopter-facing dry-run output is readable (not just a list of paths)

**Relationship to Azure SaaS readiness** (S299 revision): Azure work is a PRODUCT-scale concern (how GT-KB-generated services get deployed). Non-disruptive upgrade is a TOOL-scale concern (how GT-KB itself gets updated in adopter environments). Original reasoning was "tool must work before product can be evaluated." Owner revised at S299: both scopes proceed in parallel after v0.6.0 because Azure positioning is strategic (cannot wait for tool-scale investigation to complete) and non-disruptive upgrade is adopter-experience (cannot wait for Azure taxonomy to complete). Coordination risk managed via disjoint scope threads + explicit file ownership.

**Current relevant state (S298):**
- Commit `37a88cc` adds `_plan_missing_managed_files` for same-version hook-file drift repair (already a partial down-payment on this priority)
- `pattern_description` declared non-contractual in scanner-safe-writer schema v1 (reduces stable-interface surface and easier to evolve)
- Both of these are incremental fixes within Tier A #2; a proper investigation bridge is the future work
