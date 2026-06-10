REVISED

# GT-KB / Application Boundary — Mechanism Audit (REVISED-1)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-APP-BOUNDARY-MECHANISM-AUDIT
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Responds to:** NO-GO at `bridge/gtkb-app-boundary-mechanism-audit-002.md`

bridge_kind: prime_proposal
work_item_ids: [GTKB-APP-BOUNDARY-MECHANISM-AUDIT]
spec_ids: [SPEC-INTAKE-0ecc94, SPEC-INTAKE-c67594, SPEC-INTAKE-e09e4b]
target_project: groundtruth-kb
target_paths: ["(audit only; no file changes in this bridge)"]
implementation_scope: governance
requires_review: true
requires_verification: true

---

## Cross-NO-GO Discipline

| -002 Finding | Required action | This revision |
|---|---|---|
| **F1 (HIGH)** — customization-gap verdict misstated live upgrade behavior. The live `_plan_managed_file_drift()` at `upgrade.py:181-211` plans `skip` with reason "File differs from template (customized?) — use --force to overwrite"; it does not overwrite by default. Draft's "edits clobbered on upgrade" framing was too strong. | Distinguish default-skip behavior from absence of a first-class customization/extension contract. Adjust sequencing rationale. | **Fully reframed.** §3 now opens with explicit description of the default-skip behavior, then reframes the real gap as (a) no first-class extension contract, (b) adopter customization is tolerated but undeclared, (c) no safety under `--force`, (d) no automatic-convergence path for selective upstream tracking, (e) no structural way for upstream hooks/skills to invite customization. §5 sequencing rationale updated to match: Track A's value is about making customization explicit and supported, not about preventing a clobber that doesn't happen by default. |
| **F2 (MEDIUM)** — `release-candidate-gate` misclassified as definitely cross-cutting despite Agent Red-specific SKILL.md metadata (`project: agent-red-customer-experience`) and script content (`scripts/release_candidate_gate.py:2-6,53-79` Agent Red-specific paths). | Reclassify as KEEP LOCAL or split. | **Reclassified to "KEEP LOCAL or split"** in §4.2. Relocation totals in §4.6 revised: skills relocate drops from ~16 to ~15; total relocate drops from ~62 to ~61. |
| **F3 (MEDIUM)** — row count narrative said "51 records" while the component breakdown (19+10+6+15+4) sums to 54. Live parse confirms 54. Separately, Track A3 proposed new divergence-policy values without evaluating the existing `error` and `force-merge-on-upgrade` already in `DivergencePolicyEnum` at `managed_registry.py:69-72,98-102`. | Fix count; evaluate existing divergence-policy values before proposing schema growth. | **Fixed.** §2 now says "54 records" consistently. §2.1 type table lists all three implemented divergence-policy values (`warn`, `error`, `force-merge-on-upgrade`) with semantics. §5.2 Track A3 rewritten to evaluate the existing values first; proposes schema growth only if the evaluation surfaces a genuinely new need. |
| **F4 (LOW)** — Files Touched listed `memory/work_list.md` as Modified despite audit-only framing. | Remove or reframe as recommended follow-up. | **Reframed.** §6 now shows `memory/work_list.md` update as an explicit follow-up recommendation in §5.5, not as a change this bridge makes. §6 "Modified" section lists only "(none)". |

---

## Prior Deliberations

- `SPEC-INTAKE-0ecc94`, `SPEC-INTAKE-c67594`, `SPEC-INTAKE-e09e4b` — the three owner boundary specs (governance / requirement / architecture_decision).
- `DELIB-INTAKE-cfec8779`, `-fc507eaf`, `-aa34d25b` — owner confirmations 2026-04-24.
- `bridge/gtkb-membase-effective-use-umbrella-014.md` VERIFIED — precedent for upstream routing.
- `bridge/gtkb-gov-proposal-standards-slice1-024.md` VERIFIED — precedent for managed hook family.
- `bridge/gtkb-artifact-ownership-matrix-003.md` — origin of the 5-value ownership enum + ownership-glob sibling registry.
- Evidence sources this revision re-checked: `upgrade.py:181-211` (default-skip behavior), `managed_registry.py:69-72,98-102` (three-value `DivergencePolicyEnum`), `managed-artifacts.toml` (live tomllib parse confirms 54 rows), `.claude/skills/release-candidate-gate/SKILL.md:2-12` + `scripts/release_candidate_gate.py:2-6,53-79` (Agent Red-specific).

---

## 1. Purpose (unchanged)

Deliver an audit — not an implementation — answering three questions posed after the owner's 2026-04-24 statement of principle:

1. **Mechanism assessment** — does the current `gt project upgrade` + `managed-artifacts.toml` + `scaffold-ownership.toml` infrastructure satisfy `SPEC-INTAKE-c67594`'s customization requirement?
2. **Relocation inventory** — which Agent Red-local artifacts would need to move upstream under `SPEC-INTAKE-0ecc94`?
3. **Forward path** — propose either "mechanism is sufficient, here is the migration plan" or "mechanism has gaps X / Y / Z, here is what the customization layer needs."

Audit is read-only against `groundtruth-kb` and Agent Red develop at commit `2b9ac81a`.

---

## 2. Mechanism Summary (as-built, 2026-04-24) — CORRECTED

### 2.1 What exists

**Registry layer** (two TOML files, both in `groundtruth-kb/templates/`):

- `managed-artifacts.toml` — **54 records** covering hooks (19), rules (10), skills (6 = 3 skills × 2 files each), settings-hook-registrations (15), gitignore-patterns (4). Rich lifecycle axes (`initial_profiles` / `managed_profiles` / `doctor_required_profiles`) and ownership metadata (`ownership` / `upgrade_policy` / `adopter_divergence_policy`).
- `scaffold-ownership.toml` — ownership-glob records keyed by `path_glob`, covering adopter-owned classes of files (bridge/, memory/, groundtruth.toml; groundtruth.db as `legacy-exception`).

**Code layer** (`groundtruth-kb/src/groundtruth_kb/project/`):

- `managed_registry.py` (784 lines) — loader + validator. Exposes `FileArtifact` / `SettingsHookRegistration` / `GitignorePattern` / `OwnershipGlobArtifact` / `OwnershipMeta` dataclasses.
- `upgrade.py` (958 lines) — `plan_upgrade()` + `execute_upgrade()` with drift detection, structured-merge of settings hook events, gitignore-pattern append-only merge, git-branch rollback.
- `doctor.py`, `preflight.py`, `rollback.py` — companion entry points.

**Type system (implemented values):**

| Ownership (5) | Upgrade policy (5) | Divergence policy (3) |
|---|---|---|
| `gt-kb-managed` — upstream owns content | `overwrite` — replace adopter version with template | `warn` — log warning on drift |
| `gt-kb-scaffolded` — upstream creates at init, adopter edits afterward | `structured-merge` — merge at field granularity (JSON / TOML) | `error` — non-zero exit on drift |
| `shared-structured` — upstream defines protocol, adopter owns content | `adopter-opt-in` — no action unless adopter opts in | `force-merge-on-upgrade` — auto-resolve in favor of upstream |
| `adopter-owned` — adopter owns entirely | `preserve` — never touch after initial scaffold | |
| `legacy-exception` — grandfathered | `transient` — ephemeral | |

### 2.2 What is actually used today (live row counts)

| Field | Value | Count | % |
|---|---|---|---|
| `ownership` | `gt-kb-managed` | 54 / 54 | 100% |
| `upgrade_policy` | `overwrite` | 35 / 54 | 65% |
| `upgrade_policy` | `structured-merge` | 19 / 54 | 35% |
| `upgrade_policy` | `adopter-opt-in` / `preserve` / `transient` | 0 / 54 | 0% |
| `adopter_divergence_policy` | `warn` | 54 / 54 | 100% |
| `adopter_divergence_policy` | `error` / `force-merge-on-upgrade` | 0 / 54 | 0% |

`scaffold-ownership.toml` uses `preserve` for adopter data files (bridge/, memory/, `groundtruth.toml`) — but that is "don't touch adopter data," not "let adopter customize managed content."

### 2.3 Live upgrade behavior for drifted managed files (ADDED in REVISED-1)

`_plan_managed_file_drift()` at `upgrade.py:181-211`:

- For every managed file row in the selected profile, compare template hash to project-local hash.
- If hashes differ (i.e., the file was customized), plan an **`action="skip"`** with `reason="File differs from template (customized?) — use --force to overwrite"`.
- Overwrite only happens when the operator passes `--force` to `execute_upgrade()`.

**Consequence:** an adopter's edits to a managed hook / rule / skill **survive the default upgrade path.** The warning logged with `adopter_divergence_policy = "warn"` is informational; no file replacement occurs unless `--force` is explicitly given.

---

## 3. Customization Gap Assessment (REVISED — addresses -002 F1)

### 3.1 What the default upgrade actually does (REVISED)

The prior draft overstated the problem. Clarifying:

- **Default `gt project upgrade`:** drifted managed files → `skip` action → adopter edits preserved → upgrade continues with no content replacement for that file.
- **`gt project upgrade --force`:** drifted managed files → overwrite → adopter edits lost.
- Settings hook registrations, gitignore patterns → `structured-merge` regardless of `--force`.

So an adopter who never passes `--force` keeps their edits indefinitely. The question is whether that is good enough.

### 3.2 What IS customizable today (mostly via tolerance, not design)

| Customization need | Current path | Works? |
|---|---|---|
| Edit managed hook / rule / skill content, retain edits across upgrades | Default `skip`-on-drift preserves the edit file-by-file | ✅ **Tolerates but does not declare.** Adopter edit survives but there is no registry row recording "this is an adopter customization point." |
| Add adopter-specific hook registration to `.claude/settings.json` | Structured-merge on managed entries; adopter entries not in registry are untouched | ✅ Works by design. |
| Add adopter-specific gitignore patterns | Same structured-merge pattern | ✅ Works by design. |
| Override settings values (`.claude/settings.local.json`) | Gitignored local overlay loaded after `settings.json` | ✅ Works. Settings-only. |
| Maintain adopter bridge / memory / groundtruth.toml content | `scaffold-ownership.toml` classifies as `preserve` / `shared-structured` | ✅ Works by design. |
| Add adopter-specific new files (hooks / skills / rules not in registry) | Registry unaware → never touched | ✅ Works by omission. |

### 3.3 What is genuinely absent (REVISED — the real gaps)

With default-skip behavior understood, the gap list is narrower and more specific:

| Gap | Evidence |
|---|---|
| **No declared extension/customization contract** | `managed-artifacts.toml` has zero `adopter-opt-in` rows; no rule exposes "here is the adopter extension point inside this hook." Customization relies on file-level drift, which is invisible to upstream authors. |
| **No safety under `--force`** | An operator who runs `gt project upgrade --force` (e.g., to converge everything to upstream) loses every customization silently. There is no per-file opt-out short of omitting the force flag. |
| **No structured customization API in hooks/skills** | Hook files are monolithic Python; they do not consume adopter-supplied modules or config. A hook that wanted to honor "adopter prefers these additional regex patterns" has no declared way to accept them. |
| **No automatic convergence for unchanged files** | Default-skip is all-or-nothing per file. An adopter who edits one line cannot say "track upstream for everything except this line" — they either skip the whole file or accept full overwrite with `--force`. |
| **`adopter-opt-in` policy exists but is never exercised** | 0 of 54 rows use it. The upgrade planner already supports it (`upgrade.py:44,112-123`), but no template is offered for "upstream provides this optional capability; adopter opts in by creating a trigger file." |
| **`adopter-divergence-policy="error"` and `="force-merge-on-upgrade"` exist but are never used** | Same — enum values are implemented and validated; no row exercises them. |
| **No auditable declaration of "this adopter intends to track upstream exactly"** | An adopter who wants strict upstream conformance has no opt-in row saying so; `--force` is operator-level, not declared policy. |

### 3.4 Verdict on `SPEC-INTAKE-c67594` (REVISED)

**Partially satisfied, but the gap is narrower than -001 claimed.**

Injection criteria (deterministic / auditable / idempotent): **met.** Customization criteria: **partially met by tolerance, not by design.** The phrase "without forking" is achieved by default-skip; the phrase "without losing the ability to pull future upstream updates" is true as long as `--force` is never invoked, but there is no declared-customization path that survives `--force`, no structural way for upstream to expose extension points, and the existing `adopter-opt-in` / `error` / `force-merge-on-upgrade` values in the type system are not exercised.

---

## 4. Relocation Inventory (REVISED — addresses -002 F2 + F3)

Under `SPEC-INTAKE-0ecc94`, the following Agent Red-local files are relocation candidates. Classifications in this revision are evidence-based; each "definitely cross-cutting" entry cites content that is not Agent Red-specific.

### 4.1 Hooks (Agent Red-local without upstream equivalent)

| File | Verdict | Evidence |
|---|---|---|
| `.claude/hooks/formal-artifact-approval-gate.py` | **RELOCATE** | Governance PreToolUse gate; referenced by cross-repo ADR `ADR-ARTIFACT-FORMALIZATION-GATE-001` and MemBase record `GOV-ARTIFACT-APPROVAL-001`. |
| `.claude/hooks/poller-freshness.py` | **RELOCATE** | Bridge visibility companion to upstream `rule.bridge-essential`; cross-cutting for any dual-agent adopter. |
| `.claude/hooks/workstream-focus.py` | **RELOCATE (complex)** | Work-subject / role / topology management. Cross-cutting but ~1,166 lines; interlocked with `session_self_initialization.py`. Requires coordinated move. |

Agent Red hooks already in upstream (`templates/hooks/`): `assertion-check.py`, `credential-scan.py`, `destructive-gate.py`, `scheduler.py`, `spec-classifier.py` — correctly managed; Agent Red receives via scaffold / upgrade.

### 4.2 Skills — 22 Agent Red vs 3 upstream

**Definitely cross-cutting → RELOCATE** (evidence: SKILL.md frontmatter `project:` field is not Agent Red-specific; helpers operate on generic KB / governance surfaces):

- KB tooling: `kb-adr`, `kb-assert`, `kb-batch`, `kb-promote`, `kb-query`, `kb-session-wrap`, `kb-spec`, `kb-work-item` — 8 skills. All operate on the generic `KnowledgeDB` API.
- Governance process: `arch-audit`, `check-deliberations`, `codex-report`, `proposal-review`, `send-review` — 5 skills.
- Cross-cutting investigation / review: `alternatives-investigation`, `code-review-audit` — 2 skills.

Subtotal: **15 skills → RELOCATE.**

**KEEP LOCAL** (evidence: Agent Red-specific SKILL.md frontmatter or helpers):

- `release-candidate-gate` — SKILL.md `project: agent-red-customer-experience` and description "Agent Red release-candidate gate"; commands invoke local `scripts/release_candidate_gate.py` which opens with "Non-deploying release-candidate gate for Agent Red" and checks Agent Red-specific paths like `scripts/deploy/production-gateway-generated.yaml`. **Reclassified in REVISED-1** (was incorrectly in "Definitely cross-cutting" in -001). A cross-cutting "release-candidate-gate" skill could be extracted as a follow-on; the current skill stays local until that split is scoped and approved.
- `deploy` — Agent Red deployment specifics; app-specific content probable (needs content check during Track B).
- `seed-tenant` — Agent Red tenant seeding; app-specific.
- `run-tests` — Agent Red test runner wrapper; likely app-specific, possibly splittable.

Subtotal: **4 skills → KEEP LOCAL (or split with justification during Track B).**

### 4.3 Rules (Agent Red-local without upstream equivalent)

Agent Red unique:
- `acting-prime-builder.md` — **RELOCATE** (cross-cutting role governance).
- `codex-review-gate.md` — **RELOCATE** (cross-cutting dual-agent governance).
- `operating-role.md` — **RELOCATE** (cross-cutting; adopter keeps a scaffolded file pointing at upstream contract).
- `prime-builder-role.md` — **MERGE / REPLACE** with upstream `prime-builder.md`.
- `report-depth-prime-builder-context.md` — **MERGE / REPLACE** with upstream `report-depth.md`.

Subtotal: **3 relocate + 2 merge-into-existing-upstream.**

### 4.4 Cross-cutting scripts in `scripts/`

| Area | Files | Verdict |
|---|---|---|
| Dashboard infrastructure | `scripts/gtkb_dashboard/*.py` (~6 files) | **RELOCATE** — dashboard is a GT-KB IDP tool. Sub-slice DASHBOARD-002 work currently writes here; timing flagged in §7.4. |
| Bridge writer | `scripts/gtkb_bridge_writer.py` | **RELOCATE** — cross-cutting. |
| Session lifecycle | `scripts/session_self_initialization.py` (~6k lines) | **RELOCATE (complex)** — see §7.3. |
| Release gate & parity scripts | `scripts/release_candidate_gate.py`, `scripts/check_*_parity.py`, `scripts/check_scoped_service_boundary.py`, etc. | **Per-file split likely needed.** The `release_candidate_gate.py` is Agent Red-specific (per §4.2); parity scripts are mixed. Audit during Track B. |
| Agent Red business | `scripts/build_agent_containers.py`, `scripts/build_orchestrator.py`, `scripts/_self_provision.py`, `scripts/seed_tenant*`, etc. | **KEEP LOCAL** — deployment and application-specific. |

Rough estimate: **~40 of ~100+ scripts are cross-cutting.** Per-file audit needed.

### 4.5 Settings / governance surfaces (unchanged)

- `.claude/settings.json` — already structured-merge via upstream.
- `.claude/rules/` — see §4.3.
- `CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE_ARCHIVE.md` — adopter-owned; stay local.

### 4.6 Scale summary (CORRECTED)

| Class | Relocate | Keep local | Merge / Replace |
|---|---|---|---|
| Hooks | 3 | 0 | 0 |
| Skills | 15 | 4 | 0 |
| Rules | 3 | 0 | 2 |
| Scripts | ~40 | ~60 | 0 |
| **Total** | **~61** | **~64** | **2** |

---

## 5. Forward-Path Recommendation (REVISED)

### 5.1 Assessment summary (REVISED)

| Q | Answer |
|---|---|
| 1. Mechanism sufficient for customization? | **No — but the gap is narrower than -001 claimed.** Default upgrade preserves adopter edits by skipping drifted files. What is absent: declared-customization contract, structural extension points in hooks/skills, safety under `--force`, and exercise of the existing `adopter-opt-in` / `error` / `force-merge-on-upgrade` type-system values. |
| 2. Relocation inventory size? | **~61 files** (was ~62 in -001; -1 from reclassifying `release-candidate-gate`). |
| 3. Proposal? | Umbrella WI with two tracks — see §5.2. Track A sequencing rationale updated per -002 F1. |

### 5.2 Proposed next-layer structure

**Umbrella: `GTKB-APP-BOUNDARY-ENFORCEMENT`**

**Track A — Declared customization contract (serves `SPEC-INTAKE-c67594`):**

- **A1. Design extension-point pattern for managed hooks/skills/rules.** Candidate shape: an `<artifact>.local` sibling file loaded by the managed artifact when present. Alternatives (single `application-overlay.toml`, a `groundtruth.toml` overrides section) surfaced for Codex evaluation.
- **A2. Add the first `adopter-opt-in` and `preserve` rows** to `managed-artifacts.toml` for artifacts that are appropriate for customization. Exercise the existing enum values instead of inventing new ones.
- **A3. Evaluate existing divergence-policy values** (`warn`, `error`, `force-merge-on-upgrade`) against the needs identified in §3.3. **Propose new values only if the evaluation surfaces a genuinely new need not covered by those three.** The prior draft's proposed `block` / `preserve-with-warning` values are withdrawn pending this evaluation.
- **A4. Document the customization contract** in a new `templates/rules/app-boundary.md` so every adopter and hook author knows the pattern.
- **A5. Harden `--force` behavior**: decide whether declared customization points should survive `--force` or whether `--force` is specifically the escape hatch that blows them away. Either decision is defensible but must be documented.

**Track B — Relocate Agent Red-local cross-cutting code (serves `SPEC-INTAKE-0ecc94`):**

- **B1.** Hooks batch — 3 files.
- **B2.** Rules consolidation — 5 → 3 relocate + 2 merge.
- **B3.** KB skills batch — 8 files.
- **B4.** Governance skills batch — 7 files (5 governance-process + 2 cross-cutting investigation).
- **B5.** Scripts / dashboard / session-lifecycle — ~40 files, multiple sub-bridges.

### 5.3 Sequencing (REVISED — addresses -002 F1)

**Track A lands before Track B's later batches, because…**

Prior draft justified this with "otherwise relocations arrive as `overwrite` and lock in the gap" — that framing was based on the overstated clobber claim. Corrected rationale:

- Track A produces the pattern that defines how an adopter **declares** a customization point on a managed artifact. Without that pattern, Track B relocations land as `gt-kb-managed` + `overwrite` + no extension contract — identical to every current managed row. That is the status-quo shape.
- Agent Red's current customizations on the three Track B1 hooks (if any exist locally) would survive default upgrade under current behavior. They would remain undeclared, invisible to upstream authors, unsafe under `--force`, and without a structural upstream extension point.
- Track A therefore does not **prevent loss** (default-skip already prevents that). Track A **establishes declared intent** and **gives upstream authors a contract** to code against when writing the relocated artifacts.
- B1 (hooks) and B2 (rules) are small enough to ship in parallel with Track A design if the owner prefers visible progress; B3/B4/B5 materially benefit from A landing first.

### 5.4 What this bridge does NOT do

Audit only. Nothing moves files, edits `managed-artifacts.toml`, writes new templates, or changes upgrade behavior.

### 5.5 Recommended follow-up (not performed by this bridge — addresses -002 F4)

Once this audit is VERIFIED, update `memory/work_list.md` to add `GTKB-APP-BOUNDARY-ENFORCEMENT` as a top-level entry with Tracks A and B and the three `SPEC-INTAKE-*` refs. This is a separate update, not a change this bridge makes.

---

## 6. Files Touched (CORRECTED — addresses -002 F4)

**New:** (none — audit only)

**Modified:** (none — this bridge file is the only artifact produced)

**Not touched:**
- All upstream `groundtruth-kb/**` files.
- All Agent Red `src/`, `scripts/`, `.claude/` content.
- `managed-artifacts.toml` / `scaffold-ownership.toml`.
- `memory/work_list.md` — follow-up update recommended in §5.5 but not performed here.

---

## 7. Open Questions for Loyal Opposition Review (refreshed)

1. **Customization pattern shape** (Track A1). Sibling `<artifact>.local` file vs single `application-overlay.toml` vs `groundtruth.toml` section. Codex to accept or direct.
2. **Batch ordering (Track B).** -001 used size; dependency ordering (rules → hooks → skills) is an alternative. Codex to confirm.
3. **`session_self_initialization.py` relocation scope.** ~6k lines deeply interwoven. Clean relocate may require structural refactor first. Codex to accept multi-stage or request prerequisite split.
4. **Dashboard relocation timing.** `scripts/gtkb_dashboard/` is under live DASHBOARD-002 work. Suggest Track B's dashboard batch waits until DASHBOARD-002's sub-slices VERIFIED. Codex to accept.
5. **Split-file judgment calls.** Some files (e.g., `release-candidate-gate`, parity scripts) wrap cross-cutting logic in Agent Red-specific orchestration. Track B's per-file verdicts will require splits. Codex to accept per-file decisions during Track B, or request a taxonomy upfront.
6. **Interim `adopter-owned` classification** for files that will stay Agent Red-local pending Track B. Reasonable to mark them in `scaffold-ownership.toml` now (since `adopter-owned` is an existing enum value), or wait for Track A to define the pattern first? Codex to decide.
7. **`--force` semantics under declared customization** (Track A5). Should `gt project upgrade --force` honor declared adopter-opt-in / preserve rows (i.e., still skip them), or is `--force` the explicit escape hatch that ignores declarations? Either is defensible. Codex to weigh in.

---

## 8. Verification Matrix (audit-only)

| Risk | Test requirement |
|------|-----------------|
| Inventory counts drift after audit | On VERIFIED, the follow-up `memory/work_list.md` entry carries the §4.6 counts. |
| Assessment framing misrepresents the mechanism | Codex review verifies the 5 × 5 × 3 type system table against `managed_registry.py:OWNERSHIP_ENUM` / `UPGRADE_POLICY_ENUM` / `DIVERGENCE_POLICY_ENUM` (manual). |
| Relocation list includes an app-specific file as cross-cutting | Codex samples any 3 of the relocation candidates; each must be independently justified as non-Agent-Red-specific via SKILL.md frontmatter or file content. |
| Customization gap restated too weakly / too strongly | Codex confirms §3.3 gap list matches observable behavior; verifies no "cannot X" claim is invalidated by the default-skip mechanism. |
| `release-candidate-gate` not re-audited | Codex re-checks that the skill is marked KEEP LOCAL in §4.2 (was cross-cutting in -001). |
| Row count inconsistent | Codex verifies "54 records" appears consistently in §2; no residual "51 records" anywhere. |

---

## 9. Decision Needed From Owner

Three non-blocking decisions carried forward from -001:

1. **Two-track structure** (A customization, B relocation) under one umbrella WI? Or prefer separate WIs?
2. **Track A before Track B's larger batches** (B3/B4/B5)? Or ship all of B in parallel with A?
3. **Audit depth confirmation**: is §4 sufficient, or do you want per-file relocation verdicts for the ~40 scripts before the first implementation bridge?

**Owner input received 2026-04-24 during this session: "Proceed: Track A before Track B."** That resolves decision (2) as Track A first. Decisions (1) and (3) remain open at Codex's discretion unless owner provides further direction.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
