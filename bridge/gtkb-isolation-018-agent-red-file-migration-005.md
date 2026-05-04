REVISED

# Implementation Proposal — GTKB-ISOLATION-018: Agent Red File Migration (REVISED-2)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Scoping & strategy proposal (umbrella for sub-slices)
**Predecessor program:** GTKB-ISOLATION-017 (Slices 1–8.6, all VERIFIED or terminally-blocked)
**Successor sub-slices:** 18.A through 18.L (12 sub-slices)
**Revision basis (cycle 1):** Addressed Codex NO-GO at `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` — F1 (missing required cross-cutting spec citations), F2 (waiver bootstrap problem), F3 (acceptance-criteria internal inconsistency).
**Revision basis (cycle 2, this revision):** Addresses Codex NO-GO at `bridge/gtkb-isolation-018-agent-red-file-migration-004.md` — F1 (sub-slice 18.B numbering inconsistency: simultaneously labeled active PDF-cluster move and a vacated historical slot). Per Codex's preferred resolution, 18.B is the active PDF-cluster move; all `vacated` language has been removed from this revision.

---

## Codex Findings Addressed

### Cycle 2 (NO-GO at -004, addressed in -005)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — Sub-slice `18.B` is both active and vacated | Choose one consistent numbering convention; preferred option = make `18.B` active and delete all `vacated` statements | This revision deletes ALL `vacated` language. 18.B is the active PDF-cluster move per the sub-slice table. The header, ordering rationale, sub-slice plan introduction, acceptance criteria, and post-table notes have been edited to reflect a single consistent convention: 12 active sub-slices labeled 18.A through 18.L; the original waiver-DELIB work is filed as a precursor thread (`bridge/gtkb-isolation-018-pending-migration-waiver-006.md`, VERIFIED), not as a sub-slice. |

---

## Cycle 1 Findings (NO-GO at -002, addressed in -003)


| Finding | Recommendation | Disposition in this revision |
|---------|----------------|------------------------------|
| **F1** — Missing required specs (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) + advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) | "Revise the proposal to cite and satisfy" the 3 required + advisory specs | All 3 required + 3 advisory specs added to the Specification Links section below; preflight expected to report `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` |
| **F2** — Waiver bootstrap: proposal claimed an active waiver before its DELIB existed | "Revise the sequencing so the pending-migration waiver is created before any proposal or implementation relies on it" | The waiver DELIB (`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`) is now created via a *precursor bridge thread*: `bridge/gtkb-isolation-018-pending-migration-waiver-001.md`. This umbrella's INDEX entry will not be updated to reference `-003` until the precursor thread reaches VERIFIED and the DELIB is in MemBase. The original sub-slice slot 18.B (which had been the waiver) is vacated; sub-slices renumber accordingly (original 18.C–18.M → new 18.B–18.L). |
| **F3** — Acceptance criteria included "OQ-1 decided" but the OQ table deferred OQ-1 to sub-slice 18.K | "Decide OQ-1 before 18.A is accepted" OR "Revise 18.A acceptance criteria to say OQ-1 may be deferred until 18.K, and make 18.K explicitly blocked on that owner decision" | Both: a recommended *default* is stated (Option X — `git filter-repo`); the OQ table is updated to say "Default applies unless owner overrides at start of sub-slice 18.J [the new 18.K]"; 18.A acceptance criteria are revised to say "OQ-1 default accepted (Option X) OR explicit owner override recorded — either path satisfies the criterion." Sub-slice 18.J [the new 18.K] is explicitly blocked on owner confirmation/override of OQ-1 in its own bridge thread. |

---

## Background

The Slice 8.6 incident (S330, 2026-05-04) demonstrated that Agent Red files at GT-KB root are an active topology violation against the project-root-boundary rules. The owner-led S330 audit retroactively captured the binding rule as `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` and spawned `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` + `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`. Per the GOV's WAIVER POLICY, the current state — Agent Red files at GT-KB root pending migration — is a *known* violation tracked by *this* bridge thread and authorized by the precursor pending-migration waiver DELIB created via `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md`.

ISOLATION-017 (the predecessor program) established the isolation harness scaffolding inside `applications/Agent_Red/` — `.claude/`, `.codex/`, `.vscode/`, `.gtkb-app-isolation.json`, and `incident-response/` already exist (per `applications/Agent_Red/.gtkb-app-isolation.json` registry; sub-slice 1 GO at `bridge/application-isolation-contract-006.md`). What remains is the *physical migration* of Agent Red app code, infrastructure, CI workflows, docs, branding, legal, and identity files into that scaffolded location, plus repo-target separation so each project has its own canonical remote.

This proposal does not perform the migration. It scopes the migration, enumerates Agent Red files at GT-KB root, defines the sub-slice plan, and specifies the test plan + acceptance criteria. The actual file moves are delegated to sub-slice bridge threads, each individually subject to Codex GO/NO-GO and Codex VERIFIED.

---

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority and permanent bridge repair authority. Applies because this proposal lives under `bridge/` and must honor `bridge/INDEX.md` as canonical workflow state. Compliance: this thread is filed as a versioned `bridge/<descriptive-name>-NNN.md` file; once the precursor waiver thread reaches VERIFIED, the INDEX entry for this umbrella will be revised from `NO-GO: -002` to also include `REVISED: -003`; INDEX is the source of truth for the verdict; no Codex-side workflow state lives anywhere else.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this Specification Links section enumerates all governing specs (cross-cutting + topic-specific + advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED is conditional on test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section below maps every spec clause to a concrete test command and expected result; the Specifications-Tests Mapping section provides the rollup.

Topic-specific governance for this work:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source of this proposal's authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — Operational governance: 5 binding rules; waiver policy; supersession declaration; repo-topology contract.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract: fast_check + deep_check + doctor invariants + regression test contract; defines `CCR-PROJECT-ROOT-BOUNDARY-001` registry entry; specifies the migration-pending waiver scope as an exception.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — Pending-migration waiver DELIB created via the precursor thread `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md`. This umbrella relies on that DELIB existing in MemBase before its own INDEX entry is updated to `-003`. F2 bootstrap problem resolved.
- `.claude/rules/project-root-boundary.md` — Active rule auto-loaded at session start; encodes the 5 binding rules.
- `.claude/rules/operating-model.md` — Application-vs-platform partition (§1, §2 entries for "application", "platform", "hosted application").
- `.claude/rules/canonical-terminology.md` — Repo identity rules.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate + Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Placement contract from S310; triggered by content matches "applications/", "Agent Red", "project root boundary".
- `DCL-APP-ROOT-MINIMIZATION-001` — Minimization principle for `applications/Agent_Red/` root.
- `GOV-STANDING-BACKLOG-001` — Standing-backlog governance; ISOLATION-018 is implicitly TOP-priority per this rule.
- `.claude/rules/bridge-essential.md` — Bridge protocol invariants preserved by sub-slice plan.
- `bridge/gtkb-isolation-017-scoping-004.md` — Precedent for scoping-first-then-sub-slices proposal pattern.
- `bridge/application-isolation-contract-006.md` — Codex GO that established the existing `applications/Agent_Red/` scaffold.
- `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md` — Precursor thread (created in response to F2; must reach VERIFIED before this umbrella's INDEX entry is updated to `-003`).
- `applications/Agent_Red/.gtkb-app-isolation.json` — Current isolation-registry state at the migration target.
- `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md` — S310 inventory pattern.
- `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-nested-in-applications-rule.json` — Source DELIB packet.
- `.groundtruth/formal-artifact-approvals/2026-05-04-gov-agent-red-nested-in-applications-001.json` — GOV packet.
- `.groundtruth/formal-artifact-approvals/2026-05-04-dcl-agent-red-nested-in-applications-check-001.json` — DCL packet.
- Pending companion: `IPR-REQUIREMENTS-COLLECTION-HOOK-001` and `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — adjacent S330 spawn-queue items; not blocking.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete requirements, decisions, risks, procedures, and future work should be preserved as durable artifacts. Compliance: every sub-slice produces durable artifacts (KB DELIBs, formal-approval packets, post-impl REPORTs); the sub-slice plan explicitly enumerates outputs.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Development changes should preserve traceability across artifacts, tests, reports, and decisions. Compliance: each sub-slice's bridge thread is the traceability anchor; commits cite the bridge thread; tests cite the spec; the spec-to-test mapping section below provides the rollup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Artifact lifecycle transitions should expose candidate / active / deferred / blocked / superseded / verified / retired states. Compliance: this proposal explicitly tracks each sub-slice through NEW → GO/NO-GO → REVISED → GO → IMPLEMENTED → VERIFIED; the waiver DELIB has explicit ACTIVE / RETIRED states tied to ISOLATION-018 VERIFIED.

The proposed tests in the Test Plan section derive from these linked specs as follows: `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` rules 1–5 → tests T6–T10; `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` doctor invariants (a)–(e) → tests T1–T5; DCL regression test contract (a)–(c) → tests T11–T13; `GOV-FILE-BRIDGE-AUTHORITY-001` → T-bridge-1 (sub-slice level); `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` → T-spec-1 (preflight pass per sub-slice); `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → T-spec-2 (each post-impl REPORT carries spec-to-test mapping); platform integrity → T14, T15, T17; Agent Red app integrity → T16, T18.

---

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`); 4 search patterns; relevant results:

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source of this proposal's authority |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` | owner_conversation | (forthcoming via precursor thread) | The exception authorization that makes the in-flight pre-migration state compliant |
| `DELIB-0877` (multi-version) | owner_conversation | owner_decision | Parent isolation phased-planning program |
| `DELIB-0878` | owner_conversation | owner_decision | Phase 1 authority matrix |
| `DELIB-0879` | owner_conversation | owner_decision | SUPERSEDED — recommended sibling-folder topology that the owner did not actually choose |
| `DELIB-0912` | bridge_thread | go | ISOLATION-016 Phase 8 Wave 2 implementation |
| `DELIB-0921` | bridge_thread | go | INCIDENT-RESPONSE IR-0.1 inventory |
| `DELIB-0926` / `DELIB-0927` | bridge_thread | go / no_go | INCIDENT-RESPONSE multi-phase iteration |
| `DELIB-1375` | bridge_thread | no_go | ISOLATION-016 Phase 8 Wave 2 Slice 11 NO-GO |
| `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` | owner_conversation | informational | Role-contract framing |
| `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` | owner_conversation | owner_decision | "leave-behind-with-warning" pattern |

No prior NO-GO rejects the *direction* of this migration. The rejected-as-superseded `DELIB-0879` rejected Option A "as monorepo" and recommended Option B sibling-repos; the current source DELIB establishes Option A "as nested independent repos" — *which `DELIB-0879` did not consider* — so this is not revisiting a previously-rejected approach.

---

## Goal

Migrate Agent Red app code, infrastructure, CI workflows, docs, branding, legal, identity, and dev tooling from `E:/GT-KB/` root into `E:/GT-KB/applications/Agent_Red/`, separate the git history into independent nested repositories aligned with their canonical remotes, and verify all five binding rules from `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` are satisfied via the executable checks specified in `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`. The pre-migration state is authorized as a documented exception via `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`.

---

## Live-Probed Inventory — Agent Red files at GT-KB root (2026-05-04)

`git ls-files | wc -l` = 5,320 tracked files. Per-top-level breakdown:

### Stays at GT-KB root (platform)

| Top-level | Tracked files | Justification |
|-----------|--------------:|---------------|
| `bridge/` | 2,127 | Bridge protocol (PB ↔ LO coordination) — platform |
| `groundtruth-kb/` | 466 | GT-KB platform Python package — platform |
| `memory/` (subset) | partial | GT-KB platform memory + feedback files; some entries split (sub-slice 18.I handles split decisions) |
| `.claude/` | 62 | Platform-level harness rules/hooks/skills |
| `independent-progress-assessments/` | 58 | Loyal Opposition output directory — platform |
| `.groundtruth/` | 52 | Formal-approval-packets archive — platform |
| `.codex/` | 11 | Platform-level Codex config |
| `tools/knowledge-db/` | partial of 8 | KB Python API + web UI — platform |
| `tools/grafana/` | partial of 8 | Platform observability tooling |
| `tools/sqlite-cli/` | partial of 8 | Platform DB tooling |
| `harness-state/` | 3 | Role-record durables — platform |
| `applications/` | 7 (grows) | Existing scaffold; receives migration content |
| `groundtruth.toml` | 1 | Platform config |
| `groundtruth.db` (gitignored) | – | MemBase canonical store — platform |
| `MEMBASE-4-CLAUDE.md` | 1 | Pattern doc — GT-KB IP origin doc |
| `LICENSE` | 1 | Likely shared (sub-slice 18.I disambiguates) |

### Migrates to `applications/Agent_Red/` (Agent Red product)

| Top-level | Tracked files | Sub-slice |
|-----------|--------------:|-----------|
| `src/` (agents/, multi_tenant/, app/, chat/, etc.) | 305 | 18.E |
| `tests/` | 709 | 18.E |
| `admin/` | 361 | 18.E |
| `widget/` | 51 | 18.E |
| `docs/` | 188 | 18.C |
| `docs-site/` | 88 | 18.C |
| `branding/` | 67 | 18.D |
| `assets/` | 96 | 18.D |
| `infrastructure/terraform/` | 8 | 18.F |
| `legal/` | 4 | 18.D |
| `config/` | 4 | 18.D |
| `archive/` | 3 | 18.I (review) |
| `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui`, `docker-compose.yml`, `.dockerignore` | 5 | 18.F |
| `package.json`, `package-lock.json`, `package-pdf.json` | 3 | 18.H |
| `pyproject.toml`, `requirements.txt`, `requirements-test.txt`, `requirements-local.txt`, `uv.lock` | 5 | 18.H |
| `shopify.app.toml`, `.shopifyignore`, `sitemap.xml`, `sonar-project.properties` | 4 | 18.H |
| `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `vision.md`, `MEMORY.md` (Agent Red root duplicate?), `CHANGELOG.md`, `SECURITY.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | 10 | 18.I |
| `AGENTS.md` | 1 | 18.I — ambiguous (OQ-4) |
| `AgentRed-Technical-Evaluation-Report.docx`, `OrbaTech-Technical-Evaluation-Report.docx`, `PDF-Generation-Instructions.md`, `PRODUCTION-READINESS-ASSESSMENT.md`, `PRODUCTION-READINESS-SUMMARY.txt`, `Generate-PDF-Report.ps1`, `generate-pdf-report.{js,py,bat}`, `prechat-form-phone-screenshot.png` | 9 | 18.B (PDF cluster pre-scoped per existing isolation-registry sub-slice 4) + 18.I (Agent Red identity reports) |
| `_split_superadmin.py` | 1 | 18.I |
| `.github/workflows/` (build-agent-containers, build-api-gateway, build-slim-gateway, build-test-host, chromatic, deploy-docs, docs-quality, python-tests, release-candidate-gate, security-scan, sonarcloud, visual-regression, accessibility) | ~14 | 18.G |
| `.github/workflows/lint.yml` | 1 | 18.G — needs split |

### Splits (workflow files, scripts, memory entries)

| Top-level | Tracked files | Sub-slice |
|-----------|--------------:|-----------|
| `scripts/` | 468 | 18.E (split: `_archive_*`, `_capture_*`, `_insert_*`, `_defect_reporter`, `_env`, `_report_charts` are GT-KB platform; Agent Red-specific scripts migrate) |
| `memory/` | 114 | 18.I (split per Agent Red status vs PB platform feedback) |
| `.github/` | 18 | 18.G (workflows split per ownership; PR/issue templates depend on which project the repo belongs to) |
| `tools/` | 8 | 18.H review (knowledge-db = platform; grafana/sqlite-cli likely platform; verify) |

### Cleanup (transient/corrupt/orphan)

| Item | Disposition | Sub-slice |
|------|-------------|-----------|
| `nul` (Windows redirection accident) | DELETE | 18.L |
| `groundtruth (1).db-shm`, `(2).db-shm`, `(1).db-wal` | DELETE (Drive-sync corruption residue per S311) | 18.L |
| `C:UsersmichaAppDataLocalTempagentred-build-196` (path-as-filename Windows mishap) | DELETE | 18.L |
| `groundtruth.db.corrupt-S311-20260426-104115` | KEEP (audit evidence) or DELETE | 18.L |
| `groundtruth.db.pre-backfill-20260412-135740` | KEEP or DELETE | 18.L |
| `tmp-provider-mock.{err,}.log`, `tmp-standalone-mock.{err,}.log` | DELETE (gitignored transient mock outputs) | 18.L |
| `.gitignore` | UPDATE in 18.J (reflect new tree topology) | 18.J |
| `.driveignore` | UPDATE in 18.J (Agent Red paths now under applications/) | 18.J |

### Live-probed counts confirmed via:
```
git ls-files | awk -F/ '{print $1}' | sort | uniq -c | sort -rn
head -3 pyproject.toml          # → "Agent Red Customer Experience"
head -3 package.json            # → "name": "agent-red-customer-experience"
head -1 README.md               # → "Agent Red Customer Experience"
head -1 CLAUDE.md               # → "CLAUDE.md - Agent Red Customer Experience"
head -1 AGENTS.md               # → "Loyal Opposition Operating Contract"
head -1 MEMBASE-4-CLAUDE.md     # → "Membase for Claude — Persistent Knowledge Database Pattern"
ls applications/Agent_Red/      # → .claude .codex .vscode .gtkb-app-isolation.json .dockerignore incident-response
git remote -v                   # → origin = Remaker-Digital/groundtruth-kb (already correct)
                                # → agent-red = mike-remakerdigital/agent-red (already configured)
gh repo view mike-remakerdigital/agent-red  # → exists, default branch main, last push 2026-05-04T02:13Z
```

---

## Migration Strategy

### Repo-history preservation strategy — recommended default with owner override path

The 5 binding rules require `applications/Agent_Red/.git` to be an *independent* repository pointing at `https://github.com/mike-remakerdigital/agent-red`, nested within the GT-KB tree (not a submodule, not a monorepo). Three viable strategies:

**Option X — `git filter-repo` history extraction (preserves blame).** Use `git filter-repo` to extract the commit history of Agent Red paths from the current GT-KB repository into a new repository. Preserves authorship and blame. Cost: complex; requires careful path-rewriting; requires force-push to `mike-remakerdigital/agent-red` (which already has commits — see "Repo-target reconciliation" below).

**Option Y — Clean-cut at HEAD (no history preservation).** Initialize `applications/Agent_Red/.git` as a fresh repository; commit the migrated state as a single "v0.x.0 baseline" commit; force-push to `mike-remakerdigital/agent-red`. Cost: blame is lost; future debugging cannot trace original commit context.

**Option Z — Branch reconciliation (preserves history but on the wrong remote-history-line).** Push current `Remaker-Digital/agent-red-customer-engagement` branch state to `mike-remakerdigital/agent-red`; rename remote; clone a fresh copy at `applications/Agent_Red/`. Cost: history is preserved but the "origin" identity timeline is messy.

**Recommended default: Option X.** Blame preservation has high value for an active commercial product. The owner has previously authorized destructive remote rewrites for the next corrective push per `memory/MEMORY.md` "Repo history policy". Option X uses that authorization once. **18.A acceptance does not require a separate owner answer to OQ-1; this default is treated as the working assumption.** Sub-slice 18.J [the new 18.K] explicitly surfaces OQ-1 to the owner via `AskUserQuestion` at its start, where the owner can confirm or override.

### Order of operations (sub-slice ordering; mid-state non-broken invariant)

The migration MUST preserve a working state at every sub-slice boundary. No sub-slice may leave GT-KB platform tests broken or Agent Red dev workflows broken. Ordering rationale:

1. **18.A — Inventory finalization (this proposal post-VERIFIED).** No file moves; just establishes the authoritative inventory table that subsequent sub-slices reference.
2. **18.B — PDF cluster move.** Lowest-risk; no Python imports affected; pre-scoped per existing isolation registry sub-slice 4.
3. **18.C — docs/ + docs-site/.** No code dependencies on docs paths; safe early-stage move.
4. **18.D — branding/, assets/, legal/, config/, archive/.** Non-functional; no code import paths.
5. **18.E — src/ + tests/ + admin/ + widget/ + Agent-Red scripts.** Largest cluster; touches Python imports + JS module resolution; Agent Red CI must be re-pointed at `applications/Agent_Red/` paths.
6. **18.F — Docker* + docker-compose.yml + infrastructure/terraform/.** Container build context paths change; CI image-build workflows must be updated.
7. **18.G — `.github/workflows/` split.** Agent Red workflows move to `applications/Agent_Red/.github/workflows/`; platform workflows decided per owner. Required immediately before repo separation.
8. **18.H — package.json + pyproject.toml + lockfiles + tooling configs.** Language manifests move; node_modules/ regenerated under `applications/Agent_Red/`.
9. **18.I — Top-level identity files + memory/ split.** Last before repo separation; allows GT-KB platform to install GT-KB-specific top-level docs that replace the Agent Red ones.
10. **18.J — Repo separation (`git filter-repo` / `git init`).** Single sub-slice that cuts the topology; OQ-1 confirmed/overridden at start of this slice's bridge thread; before this, both projects share git history; after this, they don't.
11. **18.K — GT-KB platform top-level docs install.** New GT-KB-only top-level docs replacing the migrated Agent Red ones.
12. **18.L — Verification & cleanup.** Doctor invariants pass; DCL fast_check + deep_check pass; both repos build cleanly in CI; transient/corrupt files cleaned up; `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` retired.

(The pending-migration waiver DELIB was created via the precursor thread `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (VERIFIED 2026-05-04). It is NOT a sub-slice of this program; ISOLATION-018 sub-slices A through L all perform migration work, with sub-slice B being the PDF-cluster move pre-scoped by the existing isolation registry as sub-slice 4.)

### Use `git mv` not `cp + rm`

Within sub-slices that move tracked files, use `git mv` (preserves history within the source repo until 18.J cuts the history). For untracked files, plain `mv` is fine.

### Repo-target reconciliation

Three remotes are involved:
- `https://github.com/Remaker-Digital/groundtruth-kb` — current local `origin`; canonical GT-KB; remote already correct.
- `https://github.com/mike-remakerdigital/agent-red` — canonical Agent Red; configured as local `agent-red` remote; default branch `main`; recently active (last push 2026-05-04T02:13Z).
- `https://github.com/Remaker-Digital/agent-red-customer-engagement` — legacy GT-KB origin pre-S330 correction; per `memory/MEMORY.md` §S330 still has S330's slice-8.6 wrap commits; will be resolved during 18.J.

Sub-slice 18.J decides:
- Whether `Remaker-Digital/agent-red-customer-engagement` is deleted, archived, or repointed (OQ-2).
- Whether `mike-remakerdigital/agent-red` keeps its current branches (claude/, codex/, dependabot/, etc.) or is reset to migration HEAD (OQ-3).
- Whether to use Option X / Y / Z per OQ-1.

---

## Specification-Derived Test Plan

Tests derived from `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`'s fast_check + deep_check + doctor-invariants + regression-test contract. Tests run at the post-impl REPORT phase of 18.L (the final sub-slice). Earlier sub-slices have their own per-slice tests.

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T1** | DCL doctor.invariant.(a) | `python scripts/check_project_root_boundary.py` (created in 18.L or earlier) on a write to `widget/foo.tsx` | Block (no file should remain at root that's Agent-Red-allowlist-marked) |
| **T2** | DCL doctor.invariant.(b) | `git -C applications/Agent_Red remote get-url origin` | `https://github.com/mike-remakerdigital/agent-red` |
| **T3** | DCL doctor.invariant.(c) | `ls applications/` | Only named directories; no files; no `_test_*` |
| **T4** | DCL doctor.invariant.(d) | `git -C E:/GT-KB remote get-url origin` | `https://github.com/Remaker-Digital/groundtruth-kb` (already passes) |
| **T5** | DCL doctor.invariant.(e) | Query MemBase for `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` | Either "retired" or expiry > today |
| **T6** | GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 1 | `find E:/GT-KB -maxdepth 1 -type d \| grep -vE "^E:/GT-KB$"` produces only platform top-levels | All Agent Red top-levels gone from root |
| **T7** | GOV RULE 2 | `git -C E:/GT-KB ls-files \| grep -E "^(admin\|widget\|src/agents\|infrastructure/terraform)/"` | Empty (all migrated) |
| **T8** | GOV RULE 3 | `git -C applications/Agent_Red ls-files \| wc -l` | Substantially non-zero |
| **T9** | GOV RULE 4 | `find applications/ -maxdepth 1 -type f` | Empty |
| **T10** | GOV RULE 5 | New non-applications top-level dirs decided in 18.I/K are visible at root | Owner-confirmed |
| **T11** | DCL regression.test.(a) | Sample fixture proposal in `tests/scripts/test_check_project_root_boundary.py` violating rule | Fast-check blocks |
| **T12** | DCL regression.test.(b) | Sample fixture proposal citing active waiver DELIB | Fast-check allows |
| **T13** | DCL regression.test.(c) | Sample fixture proposal compliant | Deep-check returns no_violation_found |
| **T14** | GT-KB platform integrity | `cd E:/GT-KB && python -m pytest groundtruth-kb/tests/` | Pass |
| **T15** | GT-KB platform doctor | `gt project doctor` | All checks PASS or pre-existing-known WARN |
| **T16** | Agent Red app integrity | `cd applications/Agent_Red && python -m pytest tests/ -m "not slow and not integration"` | Pass (smoke) |
| **T17** | GT-KB CI green | `gh run list --repo Remaker-Digital/groundtruth-kb --branch develop --commit <full-SHA> --json conclusion,workflowName --limit 20` | All required workflows `success` |
| **T18** | Agent Red CI green | `gh run list --repo mike-remakerdigital/agent-red --branch main --commit <full-SHA> --json conclusion,workflowName --limit 20` | All required workflows `success` |

Per-sub-slice tests (executed at each sub-slice's post-impl REPORT, not at the umbrella level):

| Test ID | Spec coverage | Procedure (each sub-slice's bridge thread carries this) | Expected result |
|---------|---------------|---------------------------------------------------------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: <slice-id>" bridge/INDEX.md` | Match present; INDEX reflects the thread's progression |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id <slice-id>` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains "Specification-to-Test Mapping" + each test command + observed results | Codex VERIFIED contingent on this gate |

---

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 1 (root containment) | T6 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 2 (GT-KB-vs-application partition) | T7 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 3 (Agent Red location) | T8 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 4 (applications/ namespace purity) | T3, T9 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 5 (internal organization flexibility) | T10 | Owner-confirmed |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 "Repo Topology" | T2, T4 | Direct |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 fast_check contract | T1, T11, T12 | Direct |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 deep_check contract | T13 | Direct |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 doctor invariants (a–e) | T1, T2, T3, T4, T5 | One test per invariant |
| DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE | T1–T13 collectively | Comprehensive |
| DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER (covers in-flight state) | T5 (retirement check) | Direct |
| GOV-FILE-BRIDGE-AUTHORITY-001 | T-bridge-1 (per sub-slice) | Direct |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | T-spec-1 (per sub-slice) | Direct |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | T-spec-2 (per sub-slice) | Direct |
| Platform integrity preservation | T14, T15, T17 | Direct |
| Agent Red app integrity preservation | T16, T18 | Direct |
| Advisory: GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | (no new tests; satisfied by sub-slice plan structure) | Indirect |

Every required spec has direct test coverage at either the umbrella level (T1–T18) or the per-sub-slice level (T-bridge-1, T-spec-1, T-spec-2).

---

## Acceptance Criteria

This **scoping proposal** (18.A) is accepted when:

- [ ] Codex GO on this revision (`-003` or later)
- [ ] Inventory table is reviewed and either confirmed or correction-requested via NO-GO
- [ ] Sub-slice ordering is confirmed as preserving mid-state non-broken invariant
- [ ] Repo-history preservation strategy: **default Option X (git filter-repo)** accepted, OR explicit owner override recorded via AskUserQuestion at start of sub-slice 18.J — either path satisfies this criterion. (F3 resolution: default-with-override, not "decided before 18.A".)
- [ ] Precursor pending-migration waiver thread (`bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md`) has reached VERIFIED **before** this revision's INDEX entry is updated. (F2 resolution: waiver exists before umbrella claims it.)
- [ ] No relevant prior deliberation is cited as making this proposal redundant or contradictory

The full **GTKB-ISOLATION-018 program** is VERIFIED when:

- [ ] All 12 sub-slices (18.A through 18.L) have reached VERIFIED individually
- [ ] T1–T18 in the Test Plan section pass at the program-level post-impl REPORT (18.L)
- [ ] `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` has been retired (its expiry condition met)
- [ ] `gt project doctor` reports no ERRORs related to project-root-boundary
- [ ] Both `Remaker-Digital/groundtruth-kb` and `mike-remakerdigital/agent-red` CI on their respective post-migration HEADs are green
- [ ] CLAUDE.md, README.md, AGENTS.md at GT-KB root are GT-KB-specific (Agent Red versions migrated to applications/Agent_Red/)

---

## Sub-slice Plan

Each sub-slice is its own bridge thread (`bridge/gtkb-isolation-018-<slice-id>-<topic>-001.md`) gated by Codex GO/NO-GO and Codex VERIFIED. Sub-slice IDs are 18.A through 18.L (12 sub-slices). The pending-migration waiver DELIB is filed via a separate precursor thread (`bridge/gtkb-isolation-018-pending-migration-waiver-006.md`, VERIFIED), not as a sub-slice.

| ID | Title | Cluster | Risk | Pre-req | Outputs |
|----|-------|---------|------|---------|---------|
| **18.A** | Inventory finalization (this proposal) | n/a | Low | Precursor waiver thread VERIFIED | Authoritative inventory table; sub-slice plan |
| **18.B** | PDF cluster move | identity / tooling | Low | 18.A VERIFIED | PDF gen scripts, .docx evaluation reports, prechat screenshot, PRODUCTION-READINESS-* under `applications/Agent_Red/` |
| **18.C** | docs/ + docs-site/ migration | content | Low | 18.A VERIFIED | All docs content under `applications/Agent_Red/` |
| **18.D** | branding/ + assets/ + legal/ + config/ + archive/ | content | Low | 18.A VERIFIED | Brand & legal & config under app/ |
| **18.E** | src/ + tests/ + admin/ + widget/ + Agent-Red scripts | code | High | 18.A VERIFIED, 18.B–18.D VERIFIED | Python and JS app code under app/; imports updated; Agent Red tests pass against new paths |
| **18.F** | Dockerfiles + docker-compose + infrastructure/terraform/ | infra | Medium | 18.E VERIFIED | Container builds work with new context paths |
| **18.G** | `.github/workflows/` split | CI | High | 18.E + 18.F VERIFIED | Agent Red workflows under `applications/Agent_Red/.github/workflows/` (or kept at root with paths updated — owner decision); platform workflows isolated |
| **18.H** | package.json + pyproject.toml + lockfiles + tooling configs | manifests | Medium | 18.E VERIFIED | Project manifests under app/; node_modules/ regenerated; uv.lock if Agent Red |
| **18.I** | Top-level identity files + memory/ split | identity | Medium | 18.H VERIFIED | Agent Red README/CLAUDE/vision/etc. under app/; GT-KB platform memory entries retained at root |
| **18.J** | Repo separation (`git filter-repo` / `git init`) | repo | Critical | 18.A–18.I VERIFIED; OQ-1 owner confirmation/override recorded | `applications/Agent_Red/.git` exists, points at `mike-remakerdigital/agent-red`; root `.gitignore` excludes nested `.git`; repo histories independent |
| **18.K** | GT-KB platform top-level docs install | identity | Low | 18.J VERIFIED | New CLAUDE.md, README.md, AGENTS.md (if needed), at GT-KB root that are GT-KB-specific |
| **18.L** | Verification & cleanup | verification | Critical | 18.K VERIFIED | T1–T18 pass; transient files cleaned; doctor PASS; DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER retired |

Total: **12 sub-slices** (18.A through 18.L; each is its own bridge thread).

Note on sub-slice plan history: The original draft (`-001`) included an additional sub-slice for creating the pending-migration waiver DELIB. Codex F2 on `-002` correctly identified that this work belonged in a precursor thread, not in the umbrella's sub-slice plan. The revised plan reflects that decision; the precursor thread `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (VERIFIED 2026-05-04) created `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1.

---

## Risk / Rollback

### Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Mid-migration broken state (GT-KB platform tests failing) | Medium | High | Each sub-slice GO requires its own per-slice test plan; never merge a broken sub-slice; CI gate per sub-slice |
| Mid-migration broken state (Agent Red app dev workflows failing) | Medium | High | Same — per-slice test plan + CI gate |
| Lost Agent Red git history if Option Y is chosen at OQ-1 override | Low (default is Option X) | High | Default = Option X (preserves blame); OQ-1 surfaced explicitly at start of 18.J |
| `git filter-repo` rewrites cause unexpected behavior in dependent repos | Low | Medium | Test extraction in a scratch worktree first; don't push to canonical until validated locally |
| `mike-remakerdigital/agent-red` already has divergent branches — force-push loses them | Medium | Medium | 18.J asks owner via AskUserQuestion: keep, archive, or accept loss |
| `Remaker-Digital/agent-red-customer-engagement` legacy remote retains S330 wrap commits | High | Low | 18.J addresses; owner decision via AskUserQuestion |
| Cross-cutting files ambiguous ownership (AGENTS.md, LICENSE, MEMBASE-4-CLAUDE.md) | High | Low | 18.I addresses each individually with owner decision; default = stays at GT-KB root unless evidence supports migration |
| `node_modules/` regeneration breaks Agent Red admin builds | Low | Medium | 18.H regenerates from `package-lock.json`; CI catches |
| New `applications/Agent_Red/.git` corrupts GT-KB git tree | Low | Critical | Test in scratch worktree first; root `.gitignore` updates in 18.J must include `applications/Agent_Red/.git` exclusion before any clone |
| Waiver DELIB scope insufficient for some in-flight sub-slice | Medium | Medium | Waiver scope is broad (covers all listed Agent-Red-at-root paths); any extension requires owner-approved DELIB amendment via new bridge thread |

### Rollback

Per-sub-slice rollback: `git revert` of the sub-slice's commit chain. Each sub-slice produces a single owner-visible commit (or contiguous commit chain) on develop.

Full program rollback (post-18.J): more complex — repo separation creates an external repo at `mike-remakerdigital/agent-red`. Rollback requires: (a) revert local changes, (b) optionally force-push the canonical Agent Red remote back to its pre-migration state (recoverable via reflog within 90 days). Expensive but recoverable.

---

## Open Questions for Codex / Owner

| ID | Question | Default | Override path |
|----|----------|---------|---------------|
| **OQ-1** | Repo-history preservation: Option X (`git filter-repo`), Y (clean cut), or Z (branch reconciliation)? | **Option X (recommended; default for 18.A acceptance)** | Surface to owner via AskUserQuestion at start of sub-slice 18.J; owner can confirm Option X or override to Y/Z |
| **OQ-2** | `Remaker-Digital/agent-red-customer-engagement` legacy remote: deprecate, archive, or repoint? | **Default = deprecate (delete after retention period)** | Surface to owner via AskUserQuestion at start of sub-slice 18.J |
| **OQ-3** | `mike-remakerdigital/agent-red` divergent branches (claude/, codex/, dependabot/): preserve, archive, or accept loss? | **Default = archive (rename to `archive/<branch-name>`)** | Surface to owner via AskUserQuestion at start of sub-slice 18.J |
| **OQ-4** | `AGENTS.md` ownership: GT-KB platform or migrate to Agent Red? | Default = stays at GT-KB root (content is GT-KB bridge-protocol-specific) | Surface in 18.I review |
| **OQ-5** | `LICENSE`: shared, migrated, or duplicated? | Default = duplicated (one at each project root) | Surface in 18.I review |
| **OQ-6** | `MEMBASE-4-CLAUDE.md` ownership: GT-KB platform or migrate? | Default = stays at GT-KB root (origin pattern doc) | Surface in 18.I review |
| **OQ-7** | Should `bridge/` move into `applications/Agent_Red/`? | Default = stays at GT-KB root (platform infrastructure) | Surface in 18.I review |
| **OQ-8** | Should `independent-progress-assessments/` be split or stay at GT-KB root? | Default = stays at GT-KB root | Surface in 18.I review |
| **OQ-9** | `nul` file at root — confirm DELETE? | Default = DELETE | Surface in 18.L |
| **OQ-10** | `groundtruth.db.corrupt-S311-20260426-104115` — KEEP or DELETE? | Default = KEEP (audit evidence) | Surface in 18.L |

All defaults are in effect for 18.A acceptance. OQ-1 specifically: the owner does NOT need to answer OQ-1 to accept this proposal; the default applies and the owner's confirmation/override happens at start of 18.J. Codex F3 is resolved by this default-with-override structure.

---

## Out of scope

- v0.7.0-rc1 GT-KB tag publication (gated *by* ISOLATION-018 VERIFIED, but tag/publish is separate work).
- `mike-remakerdigital/agent-red` production deployment workflows.
- Agent Red SaaS hibernation policy changes.
- GT-KB platform feature work (`GTKB-DASHBOARD-002`, smart-poller enhancements, etc.).
- Bridge-compliance-gate hook updates that depend on `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — separate S330 spawn-queue thread.
- Production incident response procedures.

---

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Plans migrations that strictly move files from `E:/GT-KB/<root-paths>` → `E:/GT-KB/applications/Agent_Red/<paths>` (within-root operation).
- Does not introduce any live dependency on paths outside `E:/GT-KB/`.
- The pre-migration state (Agent Red files at GT-KB root) is the documented exception per the GOV's WAIVER POLICY clause + the DCL's exceptions[] entry, formalized as `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` via the precursor bridge thread `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md`.

---

## Provenance

| Source | Reference |
|--------|-----------|
| Owner directive (capture) | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330, 2026-05-04, AskUserQuestion) |
| Spawned governance | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1, `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (S330) |
| Precursor waiver thread | `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md` (S331; created in response to F2) |
| Codex NO-GO that triggered this revision | `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` (F1, F2, F3) |
| Formal-approval packets | `.groundtruth/formal-artifact-approvals/2026-05-04-{delib-s330-agent-red-nested-in-applications-rule,gov-agent-red-nested-in-applications-001,dcl-agent-red-nested-in-applications-check-001}.json` |
| Predecessor program | GTKB-ISOLATION-017 (Slices 1–8.6) |
| Existing scaffold | `applications/Agent_Red/.gtkb-app-isolation.json` registry |
| Spec-applicability config | `config/governance/spec-applicability.toml` |
| Preflight script | `scripts/bridge_applicability_preflight.py` |
| Bridge-compliance-gate hook | `.claude/hooks/bridge-compliance-gate.py` |
| Owner direction for this revision | S331 AskUserQuestion: "Pre-draft 18.A revision -003 (Recommended)" |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
