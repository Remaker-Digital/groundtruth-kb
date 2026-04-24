NEW

# GT-KB / Application Boundary — Mechanism Audit

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-APP-BOUNDARY-MECHANISM-AUDIT
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Type:** Audit + forward-path proposal. Not an implementation bridge.

bridge_kind: proposal
work_item_ids: [GTKB-APP-BOUNDARY-MECHANISM-AUDIT]
spec_ids: [SPEC-INTAKE-0ecc94, SPEC-INTAKE-c67594, SPEC-INTAKE-e09e4b]
target_project: groundtruth-kb
target_paths: ["(audit only; no file changes in this bridge)"]
implementation_scope: governance
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `SPEC-INTAKE-0ecc94` (governance, specified) — GT-KB is the default locus for all new artifacts.
- `SPEC-INTAKE-c67594` (requirement, specified) — GT-KB-to-application injection mechanism with customization support. Spec text explicitly requests this assessment: "their ability to satisfy the customization requirement in full is not yet verified and must be assessed."
- `SPEC-INTAKE-e09e4b` (architecture_decision, specified) — Application definition: deployable + GT-KB leverage configuration only.
- Deliberations `INTAKE-cfec8779`, `INTAKE-fc507eaf`, `INTAKE-aa34d25b` (confirmed 2026-04-24) — the owner decisions behind the three specs above.
- `bridge/gtkb-membase-effective-use-umbrella-014.md` VERIFIED — precedent for upstream routing of cross-cutting capabilities.
- `bridge/gtkb-gov-proposal-standards-slice1-024.md` VERIFIED — precedent for `templates/hooks/**` + `gt project upgrade` ingestion path.
- `bridge/gtkb-artifact-ownership-matrix-003.md` (referenced in `scaffold-ownership.toml`) — introduced the 5-value ownership enum and the sibling ownership-map file.
- No prior deliberations found for `app boundary audit`, `customization gap`, or `relocation inventory`.

---

## 1. Purpose

This bridge delivers an audit, not an implementation. It answers three questions posed after the owner's 2026-04-24 statement of principle:

1. **Mechanism assessment** — does the current `gt project upgrade` + `managed-artifacts.toml` + `scaffold-ownership.toml` infrastructure satisfy `SPEC-INTAKE-c67594`'s customization requirement?
2. **Relocation inventory** — which Agent Red-local artifacts would need to move upstream under `SPEC-INTAKE-0ecc94`?
3. **Forward path** — propose either "mechanism is sufficient, here is the migration plan" or "mechanism has gaps X / Y / Z, here is what the customization layer needs."

The audit is read-only against the current `groundtruth-kb` and Agent Red checkouts as of commit `0ed4acdb` (Agent Red develop) and the `groundtruth-kb` worktree at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`.

---

## 2. Mechanism Summary (as-built, 2026-04-24)

### 2.1 What exists

**Registry layer (two TOML files, both in `groundtruth-kb/templates/`):**

- `managed-artifacts.toml` — 51 records covering hooks (19), rules (10), skills (6 = 3 skills × 2 files each), settings-hook-registrations (15), gitignore-patterns (4). Rich lifecycle axes (`initial_profiles` / `managed_profiles` / `doctor_required_profiles`) and ownership metadata (`ownership` / `upgrade_policy` / `adopter_divergence_policy`).
- `scaffold-ownership.toml` — ownership-glob records keyed by `path_glob`, covering adopter-owned classes of files (bridge/, memory/, groundtruth.toml, groundtruth.db as a legacy-exception).

**Code layer (`groundtruth-kb/src/groundtruth_kb/project/`):**

- `managed_registry.py` (784 lines) — loader with full validator for both TOML files. Exposes `FileArtifact` / `SettingsHookRegistration` / `GitignorePattern` / `OwnershipGlobArtifact` / `OwnershipMeta` dataclasses.
- `upgrade.py` (958 lines) — `plan_upgrade()` + `execute_upgrade()` with file-hash drift detection, structured-merge of settings hook events, gitignore-pattern append-only merge, and git-branch-based rollback.
- `doctor.py`, `preflight.py`, `rollback.py` — companion entry points (not audited in detail for this report).

**Type system (5 × 5 × divergence-policy grid):**

| Ownership type | Meaning |
|---|---|
| `gt-kb-managed` | Upstream owns content; adopter is a consumer. |
| `gt-kb-scaffolded` | Upstream creates at init; adopter edits freely afterward. |
| `shared-structured` | Upstream defines protocol; adopter owns per-file content. |
| `adopter-owned` | Adopter owns entirely; upstream never touches. |
| `legacy-exception` | Grandfathered case; typically `preserve`. |

| Upgrade policy | Action on upgrade |
|---|---|
| `overwrite` | Replace adopter version with template. |
| `structured-merge` | Merge at structured-field granularity (JSON / TOML). |
| `adopter-opt-in` | No action unless adopter opts in. |
| `preserve` | Never touch after initial scaffold. |
| `transient` | Ephemeral; no persistence. |

| Divergence policy | Semantics |
|---|---|
| `warn` | Log a warning when drift is detected. |
| *(other values not observed in live registry rows.)* |

### 2.2 What is actually used today

Quantified from `managed-artifacts.toml` row counts:

| Field | Value | Count | % |
|---|---|---|---|
| `ownership` | `gt-kb-managed` | 54 / 54 | 100% |
| `upgrade_policy` | `overwrite` | 35 / 54 | 65% |
| `upgrade_policy` | `structured-merge` | 19 / 54 | 35% |
| `upgrade_policy` | `adopter-opt-in` | 0 / 54 | 0% |
| `upgrade_policy` | `preserve` | 0 / 54 | 0% |
| `adopter_divergence_policy` | `warn` | 54 / 54 | 100% |

`scaffold-ownership.toml` uses `preserve` for adopter files (bridge/, memory/, `groundtruth.toml`), so that policy IS exercised — but only for **"don't touch adopter data,"** not for **"let adopter customize managed content."**

---

## 3. Customization Gap Assessment (addresses `SPEC-INTAKE-c67594`)

The framework has the vocabulary for customization. The current usage does not exercise it for any managed artifact.

### 3.1 What an adopter can customize today

| Customization need | Available path | Working? |
|---|---|---|
| Add adopter-specific hook registration to `.claude/settings.json` | `structured-merge` on settings.json + adopter adds entries that upstream does not manage | ✅ Works. Upstream only merges managed entries; adopter additions survive. |
| Add adopter-specific gitignore patterns | Same `structured-merge` pattern on `.gitignore` | ✅ Works. |
| Override settings values (`.claude/settings.local.json`) | Gitignored local overlay loaded by Claude Code after `settings.json` | ✅ Works. Covers settings, not hook content. |
| Maintain adopter bridge files, memory files, groundtruth.toml | `scaffold-ownership.toml` classifies these as `preserve` / `shared-structured` | ✅ Works. Upstream never overwrites. |
| Add adopter-specific rules, skills, or hooks as NEW files | No registry row → upstream unaware → never touched | ✅ Works by omission, not by design. |

### 3.2 What an adopter cannot customize today (the gaps)

| Customization need | Reason it fails today |
|---|---|
| **Modify content of a managed hook** (e.g., custom error message, adjusted regex) | Every managed hook has `upgrade_policy = "overwrite"`. Next `gt project upgrade` clobbers the change. `adopter_divergence_policy = "warn"` produces a warning but the overwrite still happens. |
| **Modify content of a managed rule** (add project-specific guidance to prime-builder.md) | Same — `overwrite`. |
| **Modify content of a managed skill** (override SKILL.md prompt for adopter's domain) | Same — `overwrite`. |
| **Disable a specific managed hook while keeping the rest of its profile** | No mechanism. Only profile selection (`local-only` / `dual-agent` / `dual-agent-webapp`) can disable a hook, and it's all-or-nothing per hook per profile. |
| **Extend a managed hook with adopter-specific post-hook logic** | No extension-point pattern. Hooks call into internal functions, not into adopter-supplied plugins. |
| **Adopt an upstream capability opt-in rather than by default** | `adopter-opt-in` policy exists in the enum but is not used in any live row. No activation mechanism surfaces it to adopters. |
| **Block upstream overwrite on a specific file while still tracking upstream updates** | `adopter_divergence_policy = "warn"` is the only observed value; no `"block"` or `"preserve-with-warning"` is in use. |

### 3.3 Verdict on `SPEC-INTAKE-c67594`

**Partially satisfied.** The injection mechanism works (files get copied, gitignored, merged correctly; deterministic + auditable + idempotent — `SPEC-INTAKE-c67594` criteria met). The customization support is structurally absent for managed hook / rule / skill content:

- Adopter can customize **registrations and non-managed additions**.
- Adopter **cannot customize content of managed artifacts** without forking upstream or losing upstream updates.

This matches the spec text that said assessment was pending. The gap is not a bug — it is an unused capability in the framework, compounded by the absence of any design pattern that says "here is how upstream hooks invite customization."

---

## 4. Relocation Inventory (addresses `SPEC-INTAKE-0ecc94`)

Under the principle that all non-application-specific artifacts belong upstream, the following Agent Red-local files are candidates for relocation to `groundtruth-kb/templates/` (or `groundtruth-kb/src/` for library code).

### 4.1 Hooks (Agent Red-local without upstream equivalent)

| File | Verdict | Notes |
|---|---|---|
| `.claude/hooks/formal-artifact-approval-gate.py` | **RELOCATE** | Governance PreToolUse gate; not Agent Red business logic. Already referenced by cross-repo ADRs (`ADR-ARTIFACT-FORMALIZATION-GATE-001`). Memory records this as `DELIB-0835`-era work with Codex parity intent. |
| `.claude/hooks/poller-freshness.py` | **RELOCATE** | Bridge visibility hook. Cross-cutting for any dual-agent adopter. Agent Red's "bridge-essential" rule is already upstream; this hook is the mechanical companion. |
| `.claude/hooks/workstream-focus.py` | **RELOCATE (complex)** | Work-subject / role / topology management. Cross-cutting but ~1,166 lines and interlocked with `session_self_initialization.py`. Relocation requires coordinated move. |

Agent Red hooks already also in upstream (verified present in `templates/hooks/`): `assertion-check.py`, `credential-scan.py`, `destructive-gate.py`, `scheduler.py`, `spec-classifier.py` — these are already correctly upstream-managed; Agent Red gets them via scaffold/upgrade.

### 4.2 Skills (Agent Red-local without upstream equivalent)

19 skills Agent Red-local vs. 3 upstream (`bridge-propose`, `decision-capture`, `spec-intake`).

**Definitely cross-cutting → RELOCATE:**
- `kb-adr`, `kb-assert`, `kb-batch`, `kb-promote`, `kb-query`, `kb-session-wrap`, `kb-spec`, `kb-work-item` — all direct KB-tooling skills. Cross-cutting by definition.
- `arch-audit`, `check-deliberations`, `codex-report`, `proposal-review`, `send-review` — governance-process skills.
- `release-candidate-gate` — process skill (the Agent Red version wraps an Agent Red-specific script; see §4.4).
- `alternatives-investigation`, `code-review-audit` — governance skills.

**Probably app-specific → KEEP LOCAL or split:**
- `deploy` — likely Agent Red deployment specifics; app-specific content probable.
- `seed-tenant` — Agent Red tenant seeding; app-specific.
- `run-tests` — Agent Red test runner wrapper; likely app-specific but could be split into a cross-cutting `/run-tests` skill + Agent Red-specific configuration.

**Verdict:** ~16 of 19 skills relocate. Requires per-skill audit to confirm no Agent Red-specific content is embedded in the SKILL.md or helpers.

### 4.3 Rules (Agent Red-local without upstream equivalent)

Agent Red unique rules:
- `acting-prime-builder.md` — acting-Prime role contract. **RELOCATE** (cross-cutting role governance).
- `codex-review-gate.md` — no-implementation-without-GO gate. **RELOCATE** (cross-cutting dual-agent governance).
- `operating-role.md` — durable role record. **RELOCATE** (cross-cutting; the Agent Red copy would become a scaffolded adopter-edited file pointing at the upstream contract).
- `prime-builder-role.md` — overlaps with upstream `prime-builder.md`. **MERGE / REPLACE** with upstream.
- `report-depth-prime-builder-context.md` — overlaps with upstream `report-depth.md`. **MERGE / REPLACE** with upstream.

Verdict: 5 Agent Red rule files → 3 relocations, 2 consolidations into existing upstream rules.

### 4.4 Cross-cutting scripts in `scripts/` (not in the registry today)

| Area | Files | Verdict |
|---|---|---|
| Dashboard infrastructure | `scripts/gtkb_dashboard/*.py` (6+ files: `refresh_dashboard_db.py`, `refresh_service.py`, `generate_grafana_dashboard.py`, `control_plane_registry.py`, etc.) | **RELOCATE** all — dashboard is a GT-KB IDP tool, not Agent Red business code. Slice 1 and Slice 2 of DASHBOARD-002 targeted these paths as local; under the new principle they should be upstream. |
| Bridge writer | `scripts/gtkb_bridge_writer.py` | **RELOCATE** — bridge protocol helper used by multiple skills. |
| Session lifecycle | `scripts/session_self_initialization.py` (~6k lines) | **RELOCATE (complex)** — session startup / wrap-up / dashboard model. Large, interlocked with workstream_focus.py. Significant move. |
| Release gate | `scripts/release_candidate_gate.py`, `scripts/check_*_parity.py`, `scripts/check_scoped_service_boundary.py`, etc. | **RELOCATE** many — governance-gate scripts are cross-cutting. |
| Agent Red business | `scripts/build_agent_containers.py`, `scripts/build_orchestrator.py`, `scripts/_self_provision.py`, `scripts/seed_tenant*`, etc. | **KEEP LOCAL** — deployment and application-specific tooling. |

Rough estimate: ~40 of ~100+ scripts are cross-cutting. Per-file audit needed before any move.

### 4.5 Settings / governance surfaces

- `.claude/settings.json` — already structured-merge via upstream. Agent Red additions need audit for whether they belong upstream.
- `.claude/rules/` — see §4.3.
- `CLAUDE.md` — adopter-owned by design (contains adopter-specific instructions); stays local.
- `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE_ARCHIVE.md` — adopter-owned; stay local.

### 4.6 Scale summary

| Class | Relocate | Keep local | Merge/Replace |
|---|---|---|---|
| Hooks | 3 | 0 | 0 |
| Skills | ~16 | ~3 | 0 |
| Rules | 3 | 0 | 2 |
| Scripts | ~40 | ~60 | 0 |
| **Total** | **~62 files** | **~63 files** | **2** |

---

## 5. Forward-Path Recommendation

### 5.1 Assessment summary

Returning to the three audit questions:

| Q | Answer |
|---|---|
| 1. Mechanism sufficient for customization? | **No.** Injection half works; customization half is structurally absent for managed content. |
| 2. Relocation inventory size? | ~62 files across hooks, skills, rules, scripts. Non-trivial. |
| 3. Proposal? | Two interlocked tracks, outlined below. |

### 5.2 Proposed next-layer structure

I recommend an umbrella WI `GTKB-APP-BOUNDARY-ENFORCEMENT` with two tracks:

**Track A — Close the customization gap (serves `SPEC-INTAKE-c67594`):**

- **A1. Design adopter-opt-in pattern** for managed hooks/skills/rules. Probable shape: a `<artifact>.local` file alongside the managed file that upstream loads if present. Hooks would be written to look for `<hook>.local.py` as an adopter extension point; rules would be supplemented by `<rule>.local.md` appended at render; skills would consult an optional `<skill>/helpers/<tool>.local.py` adopter module.
- **A2. Add `preserve` + `adopter-opt-in` rows** to `managed-artifacts.toml` for a first wave of artifacts that are appropriate for customization.
- **A3. Strengthen `adopter_divergence_policy`** with additional values (`block`, `preserve-with-warning`) and clear semantics for each.
- **A4. Document the customization contract** in a new `templates/rules/app-boundary.md` so every adopter and every hook author knows the pattern.

**Track B — Relocate Agent Red-local cross-cutting code (serves `SPEC-INTAKE-0ecc94`):**

- **B1. Per-file categorization pass** using §4 as the starting inventory. Each file labeled: *relocate-as-is*, *relocate-with-split*, *merge-into-existing*, *keep-local*.
- **B2. Batch 1 — Hooks** (smallest, highest leverage): 3 files. Ship as one upstream bridge; Agent Red receives via `gt project upgrade`.
- **B3. Batch 2 — Rules consolidation** (5 → 3 + 2 merges). One upstream bridge.
- **B4. Batch 3 — KB skills** (8 files: kb-*). One upstream bridge; well-bounded.
- **B5. Batch 4 — Governance skills** (8 files: arch-audit, etc.). One upstream bridge.
- **B6. Batch 5 — Scripts, dashboard, session lifecycle** (~40+ files, largest). Multiple upstream bridges, sequenced over several sessions.

### 5.3 Sequencing

Track A should land **before** Track B's larger batches. Reasons:

- Without Track A, every relocated artifact arrives as `gt-kb-managed` + `overwrite` — the relocation would lock in the customization gap.
- Track A is smaller (design + framework work, no content migration).
- Track B's first two batches (hooks, rules) are small enough to ship under the current framework without waiting for A, if the owner prefers visible progress. But the downstream batches (KB skills, governance skills, scripts) benefit materially from A being in place.

### 5.4 What this bridge does NOT do

This is an audit. Nothing in this bridge moves files, edits `managed-artifacts.toml`, writes new templates, or changes upgrade behavior. The only artifact this bridge produces is itself (plus the 3 spec references that already exist).

---

## 6. Files Touched

**New:** (none — audit only)

**Modified:**
- `memory/work_list.md` — add `GTKB-APP-BOUNDARY-ENFORCEMENT` as a top-level backlog entry with two tracks (A customization, B relocation) and the three `SPEC-INTAKE-*` spec refs.

**Not touched:**
- All upstream `groundtruth-kb/**` files.
- All Agent Red `src/`, `scripts/`, `.claude/` content.
- Managed-artifacts.toml.
- Any Python or markdown outside this bridge file.

---

## 7. Open Questions for Loyal Opposition Review

1. **Customization pattern shape (Track A1).** I sketched a `<artifact>.local` alongside-file pattern. Alternatives: a single `application-overlay.toml` declaring overrides, or a `groundtruth.toml` section adopters edit. Codex to accept the sketch or propose an alternative.
2. **Batch ordering (Track B).** I ordered by size (small first). Alternative: by dependency (rules first because hooks reference rules; then hooks; then skills that use both). Codex to confirm or reorder.
3. **`session_self_initialization.py` relocation scope.** This script is ~6k lines and deeply interwoven with Agent Red's current state. A clean relocate may require structural refactor first. Codex to accept as a multi-stage item or request a prerequisite split.
4. **Dashboard relocation timing.** `scripts/gtkb_dashboard/` is currently the subject of live work (DASHBOARD-002 Slice 2.1/2.2). Relocating mid-flight is risky. I suggest Track B's dashboard batch waits until DASHBOARD-002's subslices are VERIFIED. Codex to accept.
5. **"App-specific" vs "cross-cutting" judgment calls.** Some files (e.g., `release-candidate-gate`) have Agent Red-specific wrappers around cross-cutting logic. The migration may require splitting each such file. Codex to accept per-file split decisions during Track B, or request a taxonomy now.
6. **Retroactive `adopter-owned` classification for already-local files.** If Track A lands before Track B finishes, the still-local files could be reclassified as `adopter-owned` in `scaffold-ownership.toml` as an interim step. Codex to accept or reject this half-step.

---

## 8. Verification Matrix (audit-only)

| Risk | Test requirement |
|------|-----------------|
| Inventory counts drift after audit | On VERIFIED, the `memory/work_list.md` entry carries the counts from §4.6 and a reviewable sha of this bridge file. |
| Assessment framing misrepresents the mechanism | Codex review verifies the 5 × 5 type system enumeration matches `managed_registry.py:OWNERSHIP_ENUM` + `UPGRADE_POLICY_ENUM` (manual cross-check during review). |
| Relocation list incorrectly classifies an app-specific file as cross-cutting | Codex review samples any 5 of the relocation candidates; each must be independently justified as cross-cutting. |
| Customization gap overstated | Codex review verifies each "cannot customize" row in §3.2 by attempting the customization against the current framework (manual during review). |

---

## 9. Decision Needed From Owner

Three non-blocking decisions to surface, for scheduling:

1. **Accept the two-track structure** (A customization, B relocation) under one umbrella WI? Or prefer separate WIs?
2. **Accept Track A before Track B** sequencing? Or ship B1+B2 in parallel with Track A design?
3. **Audit scope confirmation**: do you want me to deepen this audit (e.g., per-file relocation verdicts for scripts, concrete file counts by module) before an implementation bridge lands, or is the summary in §4 sufficient to proceed?

None block this audit's VERIFIED verdict.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
