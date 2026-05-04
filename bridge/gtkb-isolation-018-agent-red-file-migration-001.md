NEW

# Implementation Proposal — GTKB-ISOLATION-018: Agent Red File Migration

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Scoping & strategy proposal (umbrella for sub-slices)
**Predecessor program:** GTKB-ISOLATION-017 (Slices 1–8.6, all VERIFIED or terminally-blocked)
**Successor sub-slices:** 18.A through 18.M (defined under "Sub-slice Plan" below; each will be its own bridge thread)

---

## Background

The Slice 8.6 incident (S330, 2026-05-04) demonstrated that Agent Red files at GT-KB root are an active topology violation against the project-root-boundary rules. The owner-led S330 audit retroactively captured the binding rule as `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` and spawned `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` + `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`. Per the GOV's WAIVER POLICY, the current state — Agent Red files at GT-KB root pending migration — is a *known* violation tracked by *this* bridge thread. Until ISOLATION-018 reaches VERIFIED, Agent-Red-related work at GT-KB root operates under a documented exception (the pending-migration waiver, formalized in sub-slice 18.B).

ISOLATION-017 (the predecessor program) established the isolation harness scaffolding inside `applications/Agent_Red/` — `.claude/`, `.codex/`, `.vscode/`, `.gtkb-app-isolation.json`, and `incident-response/` already exist (per `applications/Agent_Red/.gtkb-app-isolation.json` registry; sub-slice 1 GO at `bridge/application-isolation-contract-006.md`). What remains is the *physical migration* of Agent Red app code, infrastructure, CI workflows, docs, branding, legal, and identity files into that scaffolded location, plus repo-target separation so each project has its own canonical remote.

This proposal does not perform the migration. It scopes the migration, enumerates Agent Red files at GT-KB root, defines the sub-slice plan, and specifies the test plan + acceptance criteria. The actual file moves are delegated to sub-slice bridge threads, each individually subject to Codex GO/NO-GO and Codex VERIFIED.

---

## Specification Links

Governing specifications cited by this proposal:

- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — operational governance: 5 binding rules formalized; waiver policy; supersession declaration; repo-topology contract.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` — machine-checkable contract: fast_check + deep_check + doctor invariants + regression test contract; defines `CCR-PROJECT-ROOT-BOUNDARY-001` registry entry; specifies the migration-pending waiver scope as an exception.
- `.claude/rules/project-root-boundary.md` — active rule auto-loaded at session start; encodes the 5 binding rules as the rule-cited soft-authority predicate.
- `.claude/rules/operating-model.md` — application-vs-platform partition (§1, §2 entries for "application", "platform", "hosted application").
- `.claude/rules/canonical-terminology.md` — repo identity rules (`Remaker-Digital/groundtruth-kb` for GT-KB; `mike-remakerdigital/agent-red` for Agent Red).
- `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate + Mandatory Specification-Derived Verification Gate; this proposal complies via the Test Plan section below.
- `.claude/rules/codex-review-gate.md` — pre-implementation review obligation; this proposal is the artifact submitted for that review.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation; satisfied via the Prior Deliberations section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — placement contract from S310 that authorized the existence of `applications/Agent_Red/`.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle for `applications/Agent_Red/` root; referenced by the existing isolation registry at `applications/Agent_Red/.gtkb-app-isolation.json`.
- `GOV-STANDING-BACKLOG-001` — standing-backlog governance; ISOLATION-018 is implicitly TOP-priority per this rule because it is the named successor program of an in-flight high-priority release thread.
- `.claude/rules/bridge-essential.md` — bridge protocol invariants preserved by sub-slice plan.
- `bridge/gtkb-isolation-017-scoping-004.md` — precedent for scoping-first-then-sub-slices proposal pattern.
- `bridge/application-isolation-contract-006.md` — the Codex GO that established the existing `applications/Agent_Red/` scaffold.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation-registry state at the migration target; sub-slice plan extends this.
- `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md` — S310 inventory pattern reused by this proposal's inventory section.
- `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-nested-in-applications-rule.json` — formal-approval packet carrying the verbatim owner statements + 5 binding rules.
- `.groundtruth/formal-artifact-approvals/2026-05-04-gov-agent-red-nested-in-applications-001.json` — formal-approval packet carrying the GOV body (KB body field is empty; this packet is the live source of the rule text until that gap is closed).
- `.groundtruth/formal-artifact-approvals/2026-05-04-dcl-agent-red-nested-in-applications-check-001.json` — formal-approval packet carrying the DCL body (same KB-body-empty gap).
- Pending companion: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (forthcoming, sub-slice 18.B). Referenced as an exception clause in the DCL above; sub-slice 18.B creates this DELIB and its formal-approval packet so the in-flight migration commits comply with the rule under a cited exception.
- Pending companion: `IPR-REQUIREMENTS-COLLECTION-HOOK-001` and `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — adjacent S330 spawn-queue items; this proposal does not block on them, but `CCR-PROJECT-ROOT-BOUNDARY-001` from the DCL will register against `DCL-CROSS-CUTTING-REQUIREMENTS-REGISTRY-001` once that registry lands.

The `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` source decision is the ultimate authority for this proposal; it has been retrieved from MemBase via the deliberations table search captured in the Prior Deliberations section below.

The proposed tests in the Test Plan section derive from the linked specifications as follows: `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` rules 1–5 → tests T6–T10; `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` doctor invariants (a)–(e) → tests T1–T5; DCL regression test contract (a)–(c) → tests T11–T13; GT-KB platform integrity preservation → tests T14, T15, T17; Agent Red app integrity preservation → tests T16, T18. The full mapping is in the Specifications-Tests Mapping section below.

---

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table; 4 search patterns; relevant results:

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source of this proposal's authority |
| `DELIB-0877` (multi-version) | owner_conversation | owner_decision | Parent isolation phased-planning program — established the umbrella |
| `DELIB-0878` | owner_conversation | owner_decision | Phase 1 authority matrix |
| `DELIB-0879` | owner_conversation | owner_decision | SUPERSEDED — recommended sibling-folder topology that the owner did not actually choose |
| `DELIB-0912` | bridge_thread | go | ISOLATION-016 Phase 8 Wave 2 implementation — built the isolation harness |
| `DELIB-0921` | bridge_thread | go | INCIDENT-RESPONSE IR-0.1 inventory — established `applications/Agent_Red/incident-response/` |
| `DELIB-0926` / `DELIB-0927` | bridge_thread | go / no_go | INCIDENT-RESPONSE multi-phase iteration — provides post-impl-report patterns |
| `DELIB-1375` | bridge_thread | no_go | ISOLATION-016 Phase 8 Wave 2 Slice 11 NO-GO — historical NO-GO learnings |
| `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` | owner_conversation | informational | Role-contract framing relevant to repo-separation discussion |
| `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` | owner_conversation | owner_decision | "leave-behind-with-warning" pattern for unclassified files — applies to migration ambiguity |

No prior NO-GO rejects the *direction* of this migration. The rejected-as-superseded `DELIB-0879` rejected Option A "as monorepo" and recommended Option B sibling-repos; the current source DELIB establishes Option A "as nested independent repos" — *which `DELIB-0879` did not consider* — so this is not revisiting a previously-rejected approach.

---

## Goal

Migrate Agent Red app code, infrastructure, CI workflows, docs, branding, legal, identity, and dev tooling from `E:/GT-KB/` root into `E:/GT-KB/applications/Agent_Red/`, separate the git history into independent nested repositories aligned with their canonical remotes, and verify all five binding rules from `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` are satisfied via the executable checks specified in `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`.

---

## Live-Probed Inventory — Agent Red files at GT-KB root (2026-05-04)

`git ls-files | wc -l` = 5,320 tracked files. Per-top-level breakdown:

### Stays at GT-KB root (platform)

| Top-level | Tracked files | Justification |
|-----------|--------------:|---------------|
| `bridge/` | 2,127 | Bridge protocol (PB ↔ LO coordination) — platform |
| `groundtruth-kb/` | 466 | GT-KB platform Python package — platform |
| `memory/` (subset) | partial | GT-KB platform memory + feedback files; SOME entries need Agent Red split (sub-slice 18.J handles split decisions) |
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
| `LICENSE` | 1 | Likely shared (sub-slice 18.J disambiguates) |

### Migrates to `applications/Agent_Red/` (Agent Red product)

| Top-level | Tracked files | Sub-slice |
|-----------|--------------:|-----------|
| `src/` (agents/, multi_tenant/, app/, chat/, etc.) | 305 | 18.F |
| `tests/` | 709 | 18.F |
| `admin/` | 361 | 18.F |
| `widget/` | 51 | 18.F |
| `docs/` | 188 | 18.D |
| `docs-site/` | 88 | 18.D |
| `branding/` | 67 | 18.E |
| `assets/` | 96 | 18.E |
| `infrastructure/terraform/` | 8 | 18.G |
| `legal/` | 4 | 18.E |
| `config/` | 4 | 18.E |
| `archive/` | 3 | 18.J (review — likely Agent Red archive) |
| `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui`, `docker-compose.yml`, `.dockerignore` | 5 | 18.G |
| `package.json` (`name: agent-red-customer-experience`), `package-lock.json`, `package-pdf.json` | 3 | 18.I |
| `pyproject.toml` (line 1: "Agent Red Customer Experience"), `requirements.txt`, `requirements-test.txt`, `requirements-local.txt`, `uv.lock` | 5 | 18.I |
| `shopify.app.toml`, `.shopifyignore`, `sitemap.xml`, `sonar-project.properties` | 4 | 18.I |
| `README.md` (line 1: "Agent Red Customer Experience"), `CLAUDE.md` (line 1: "Agent Red Customer Experience"), `CONTRIBUTING.md` (Agent Red), `vision.md`, `MEMORY.md` (Agent Red root duplicate?), `CHANGELOG.md`, `SECURITY.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | 10 | 18.J |
| `AGENTS.md` (line 1: "Loyal Opposition Operating Contract") | 1 | 18.J — ambiguous: content is GT-KB bridge-protocol-specific but could be relevant to both projects; sub-slice will disambiguate via owner decision |
| `AgentRed-Technical-Evaluation-Report.docx`, `OrbaTech-Technical-Evaluation-Report.docx`, `PDF-Generation-Instructions.md`, `PRODUCTION-READINESS-ASSESSMENT.md`, `PRODUCTION-READINESS-SUMMARY.txt`, `Generate-PDF-Report.ps1`, `generate-pdf-report.{js,py,bat}`, `prechat-form-phone-screenshot.png` | 9 | 18.C (PDF cluster pre-scoped per existing isolation-registry sub-slice 4) + 18.J (Agent Red identity reports) |
| `_split_superadmin.py` | 1 | 18.J (Agent Red one-shot migration helper — review for retention) |
| `.github/workflows/` (build-agent-containers, build-api-gateway, build-slim-gateway, build-test-host, chromatic, deploy-docs, docs-quality, python-tests, release-candidate-gate, security-scan, sonarcloud, visual-regression, accessibility) | ~14 | 18.H |
| `.github/workflows/lint.yml` | 1 | 18.H — needs split: lint may apply to both projects; one or both retain |

### Splits (workflow files, scripts, memory entries)

| Top-level | Tracked files | Sub-slice |
|-----------|--------------:|-----------|
| `scripts/` | 468 | 18.F (split: `_archive_*`, `_capture_*`, `_insert_*`, `_defect_reporter`, `_env`, `_report_charts` are GT-KB platform; Agent Red-specific scripts migrate) |
| `memory/` | 114 | 18.J (split: `feedback_*` typically PB platform behavior → STAYS; `project_plan_of_record.md`, Agent-Red-status, hibernation runbooks → MIGRATE) |
| `.github/` | 18 | 18.H (workflows split per ownership; PR templates / issue templates depend on which project the repo belongs to) |
| `tools/` | 8 | 18.I review (knowledge-db = platform; grafana/sqlite-cli likely platform; verify) |

### Cleanup (transient/corrupt/orphan)

| Item | Disposition | Sub-slice |
|------|-------------|-----------|
| `nul` (Windows redirection accident) | DELETE | 18.M (verification + cleanup) |
| `groundtruth (1).db-shm`, `(2).db-shm`, `(1).db-wal` | DELETE (Drive-sync corruption residue per S311) | 18.M |
| `C:UsersmichaAppDataLocalTempagentred-build-196` (path-as-filename Windows mishap) | DELETE | 18.M |
| `groundtruth.db.corrupt-S311-20260426-104115` | KEEP (audit evidence) or DELETE (post-recovery) — owner decision | 18.M |
| `groundtruth.db.pre-backfill-20260412-135740` | KEEP or DELETE — owner decision | 18.M |
| `tmp-provider-mock.{err,}.log`, `tmp-standalone-mock.{err,}.log` | DELETE (gitignored transient mock outputs) | 18.M |
| `.gitignore` | UPDATE in 18.K (reflect new tree topology) | 18.K |
| `.driveignore` | UPDATE in 18.K (Agent Red paths now under applications/) | 18.K |

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

### Repo-history preservation strategy — owner decision required

The 5 binding rules require `applications/Agent_Red/.git` to be an *independent* repository pointing at `https://github.com/mike-remakerdigital/agent-red`, nested within the GT-KB tree (not a submodule, not a monorepo). Three viable strategies:

**Option X — `git filter-repo` history extraction (preserves blame).** Use `git filter-repo` to extract the commit history of Agent Red paths from the current GT-KB repository into a new repository. Preserves authorship and blame. Cost: complex; requires careful path-rewriting; requires force-push to `mike-remakerdigital/agent-red` (which already has commits — see "Repo-target reconciliation" below).

**Option Y — Clean-cut at HEAD (no history preservation).** Initialize `applications/Agent_Red/.git` as a fresh repository; commit the migrated state as a single "v0.x.0 baseline" commit; force-push to `mike-remakerdigital/agent-red`. Cost: blame is lost; future debugging cannot trace original commit context.

**Option Z — Branch reconciliation (preserves history but on the wrong remote-history-line).** Push current `Remaker-Digital/agent-red-customer-engagement` branch state to `mike-remakerdigital/agent-red`; rename remote; clone a fresh copy at `applications/Agent_Red/`. Cost: history is preserved but the "origin" identity timeline is messy because the canonical repo gets a sudden full-history push from a different repo's history.

**Recommendation:** Option X. Blame preservation has high value for an active commercial product. The owner has previously authorized destructive remote rewrites for the *next corrective push* per `memory/MEMORY.md` "Repo history policy". Option X uses that authorization once.

This is open question OQ-1 in "Open Questions for Codex / Owner" below.

### Order of operations (sub-slice ordering; mid-state non-broken invariant)

The migration MUST preserve a working state at every sub-slice boundary. No sub-slice may leave GT-KB platform tests broken or Agent Red dev workflows broken. Ordering rationale:

1. **18.A — Inventory finalization (this proposal post-VERIFIED).** No file moves; just establishes the authoritative inventory table that subsequent sub-slices reference.
2. **18.B — Pending-migration waiver DELIB.** Creates `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` with explicit scope ("any commit on develop touching Agent Red files at GT-KB root, until ISOLATION-018 VERIFIED") + expiry. This unblocks the DCL exception clause, allowing the in-flight migration commits themselves to comply with the rule under the cited exception.
3. **18.C — PDF cluster move.** Lowest-risk; no Python imports affected; pre-scoped per existing isolation registry sub-slice 4.
4. **18.D — docs/ + docs-site/.** No code dependencies on docs paths; safe early-stage move.
5. **18.E — branding/, assets/, legal/, config/, archive/.** Non-functional; no code import paths.
6. **18.F — src/ + tests/ + admin/ + widget/ + Agent-Red scripts.** Largest cluster; touches Python imports + JS module resolution; Agent Red CI must be re-pointed at `applications/Agent_Red/` paths.
7. **18.G — Docker* + docker-compose.yml + infrastructure/terraform/.** Container build context paths change; CI image-build workflows must be updated.
8. **18.H — `.github/workflows/` split.** Agent Red workflows move to `applications/Agent_Red/.github/workflows/`; platform workflows (sonarcloud, lint if shared, security-scan if shared) decided per owner. Required immediately before repo separation.
9. **18.I — package.json + pyproject.toml + lockfiles + tooling configs.** Language manifests move; node_modules/ regenerated under `applications/Agent_Red/`.
10. **18.J — Top-level identity files (README, CLAUDE.md, vision, CHANGELOG, SECURITY, CONTRIBUTING, MEMORY.md, etc.) + memory/ split.** Last before repo separation; allows GT-KB platform to install GT-KB-specific top-level docs that replace the Agent Red ones.
11. **18.K — Repo separation (the actual `git filter-repo` / `git init` / `.gitignore` updates).** Single sub-slice that cuts the topology; before this, both projects share git history; after this, they don't.
12. **18.L — GT-KB platform CLAUDE.md / README.md / etc. installed.** New GT-KB-only top-level docs replacing the migrated Agent Red ones.
13. **18.M — Verification & cleanup.** Doctor invariants pass; DCL fast_check + deep_check pass; both repos build cleanly in CI; transient/corrupt files cleaned up.

### Use `git mv` not `cp + rm`

Within sub-slices that move tracked files, use `git mv` (preserves history within the source repo until 18.K cuts the history). For untracked files, plain `mv` is fine. This applies even though 18.K may use `git filter-repo` afterwards — `git mv` keeps the in-progress commits more navigable for debugging.

### Repo-target reconciliation

Three remotes are involved:
- `https://github.com/Remaker-Digital/groundtruth-kb` — current local `origin`; canonical GT-KB; remote already correct.
- `https://github.com/mike-remakerdigital/agent-red` — canonical Agent Red; configured as local `agent-red` remote; default branch `main`; recently active (last push 2026-05-04T02:13Z).
- `https://github.com/Remaker-Digital/agent-red-customer-engagement` — legacy GT-KB origin pre-S330 correction; per `memory/MEMORY.md` §S330 still has S330's slice-8.6 wrap commits; will be resolved during 18.K (likely deprecated post-migration; sub-slice will check with owner before removing).

Sub-slice 18.K decides:
- Whether `Remaker-Digital/agent-red-customer-engagement` is deleted, archived, or repointed.
- Whether `mike-remakerdigital/agent-red` keeps its current branches (claude/, codex/, dependabot/, etc.) or is reset to migration HEAD.
- Whether to use Option X / Y / Z per the strategy section above.

---

## Specification-Derived Test Plan

Tests derived from `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`'s fast_check + deep_check + doctor-invariants + regression-test contract. Tests run at the post-impl REPORT phase of 18.M (the final sub-slice). Earlier sub-slices have their own per-slice tests; only 18.M asserts the full DCL.

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T1** | DCL doctor.invariant.(a) | `python scripts/check_project_root_boundary.py` (created in 18.M or earlier) on a write to `widget/foo.tsx` | Block (no file should remain at root that's Agent-Red-allowlist-marked) |
| **T2** | DCL doctor.invariant.(b) | `git -C applications/Agent_Red remote get-url origin` | `https://github.com/mike-remakerdigital/agent-red` |
| **T3** | DCL doctor.invariant.(c) | `ls applications/` | only named directories (`Agent_Red/` and any other deployed-app dirs); no files; no `_test_*` |
| **T4** | DCL doctor.invariant.(d) | `git -C E:/GT-KB remote get-url origin` | `https://github.com/Remaker-Digital/groundtruth-kb` (already passes) |
| **T5** | DCL doctor.invariant.(e) | Query MemBase for `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` | Either "retired" or expiry > today (or both — retire-after-VERIFIED is acceptable) |
| **T6** | GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 1 | `find E:/GT-KB -maxdepth 1 -type d \| grep -vE "^E:/GT-KB$"` produces only platform top-levels (no `admin/`, `widget/`, `src/agents/`, etc.) | All Agent Red top-levels gone from root |
| **T7** | GOV RULE 2 | `git -C E:/GT-KB ls-files \| grep -E "^(admin\|widget\|src/agents\|infrastructure/terraform)/"` | Empty (all migrated) |
| **T8** | GOV RULE 3 | `git -C applications/Agent_Red ls-files \| wc -l` | Substantially non-zero (migrated tree present) |
| **T9** | GOV RULE 4 | `find applications/ -maxdepth 1 -type f` | Empty (no files at applications/ root) |
| **T10** | GOV RULE 5 | New non-applications top-level dirs decided in 18.J/L are visible at root | Owner-confirmed reorganization (subjective; passes when owner approves) |
| **T11** | DCL regression.test.(a) | Sample fixture proposal in `tests/scripts/test_check_project_root_boundary.py` violating rule | Fast-check blocks |
| **T12** | DCL regression.test.(b) | Sample fixture proposal citing active waiver DELIB | Fast-check allows |
| **T13** | DCL regression.test.(c) | Sample fixture proposal compliant | Deep-check returns no_violation_found |
| **T14** | GT-KB platform integrity | `cd E:/GT-KB && python -m pytest groundtruth-kb/tests/` | Pass |
| **T15** | GT-KB platform doctor | `gt project doctor` | All checks PASS or pre-existing-known WARN |
| **T16** | Agent Red app integrity | `cd applications/Agent_Red && python -m pytest tests/ -m "not slow and not integration"` | Pass (smoke level; full sweep gated by sub-slice 18.F's per-slice test plan) |
| **T17** | GT-KB CI green | `gh run list --repo Remaker-Digital/groundtruth-kb --branch develop --commit <full-SHA> --json conclusion,workflowName --limit 20` | All required workflows `success` |
| **T18** | Agent Red CI green | `gh run list --repo mike-remakerdigital/agent-red --branch main --commit <full-SHA> --json conclusion,workflowName --limit 20` | All required workflows `success` |

---

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 1 (root containment) | T6 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 2 (GT-KB-vs-application partition) | T7 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 3 (Agent Red location) | T8 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 4 (applications/ namespace purity) | T3, T9 | Direct |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 RULE 5 (internal organization flexibility) | T10 | Owner-confirmed (subjective) |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 "Repo Topology" | T2, T4 | Direct |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 fast_check contract | T1, T11, T12 | Direct (T11 + T12 are regression fixtures from DCL regression.test) |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 deep_check contract | T13 | Direct (T13 is regression fixture from DCL regression.test) |
| DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 doctor invariants (a–e) | T1, T2, T3, T4, T5 | One test per invariant |
| DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE | T1–T13 collectively | Comprehensive |
| Platform integrity preservation | T14, T15, T17 | Direct |
| Agent Red app integrity preservation | T16, T18 | Direct |

Every cited specification has at least one test directly mapped to it. The full mapping is reaffirmed in each sub-slice's per-slice test plan; this proposal's mapping is the program-level rollup.

---

## Acceptance Criteria

This **scoping proposal** (18.A) is accepted when:

- [ ] Codex GO on this proposal
- [ ] Inventory table is reviewed and either confirmed or correction-requested via NO-GO
- [ ] Sub-slice ordering is confirmed as preserving mid-state non-broken invariant
- [ ] Repo-history preservation strategy is decided by owner (OQ-1)
- [ ] Pending-migration waiver DELIB plan (sub-slice 18.B as next thread) is acceptable
- [ ] No relevant prior deliberation is cited as making this proposal redundant or contradictory

The full **GTKB-ISOLATION-018 program** is VERIFIED when:

- [ ] All 13 sub-slices have reached VERIFIED individually
- [ ] T1–T18 in the Test Plan section pass at the program-level post-impl REPORT (18.M)
- [ ] `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` has been retired (its expiry condition met)
- [ ] `gt project doctor` reports no ERRORs related to project-root-boundary
- [ ] Both `Remaker-Digital/groundtruth-kb` and `mike-remakerdigital/agent-red` CI on their respective post-migration HEADs are green
- [ ] CLAUDE.md, README.md, AGENTS.md at GT-KB root are GT-KB-specific (Agent Red versions migrated to applications/Agent_Red/)

---

## Sub-slice Plan

Each sub-slice is its own bridge thread (`bridge/gtkb-isolation-018-<slice-id>-<topic>-001.md`) gated by Codex GO/NO-GO and Codex VERIFIED.

| ID | Title | Cluster | Risk | Pre-req | Outputs |
|----|-------|---------|------|---------|---------|
| **18.A** | Inventory finalization (this proposal) | n/a | Low | None | Authoritative inventory table; sub-slice plan |
| **18.B** | Pending-migration waiver DELIB | n/a | Low | 18.A VERIFIED | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` with scope + expiry; KB insert via formal-approval packet |
| **18.C** | PDF cluster move | identity / tooling | Low | 18.B VERIFIED | PDF gen scripts, .docx evaluation reports, prechat screenshot, PRODUCTION-READINESS-* under `applications/Agent_Red/` |
| **18.D** | docs/ + docs-site/ migration | content | Low | 18.B VERIFIED | All docs content under `applications/Agent_Red/` |
| **18.E** | branding/ + assets/ + legal/ + config/ + archive/ | content | Low | 18.B VERIFIED | Brand & legal & config under app/ |
| **18.F** | src/ + tests/ + admin/ + widget/ + Agent-Red scripts | code | High | 18.B VERIFIED, 18.C–18.E VERIFIED | Python and JS app code under app/; imports updated; Agent Red tests pass against new paths |
| **18.G** | Dockerfiles + docker-compose + infrastructure/terraform/ | infra | Medium | 18.F VERIFIED | Container builds work with new context paths |
| **18.H** | `.github/workflows/` split | CI | High | 18.F + 18.G VERIFIED | Agent Red workflows under `applications/Agent_Red/.github/workflows/` (or kept at root with paths updated — owner decision); platform workflows isolated |
| **18.I** | package.json + pyproject.toml + lockfiles + tooling configs | manifests | Medium | 18.F VERIFIED | Project manifests under app/; node_modules/ regenerated; uv.lock if Agent Red |
| **18.J** | Top-level identity files + memory/ split | identity | Medium | 18.I VERIFIED | Agent Red README/CLAUDE/vision/etc. under app/; GT-KB platform memory entries retained at root |
| **18.K** | Repo separation (`git filter-repo` / `git init`) | repo | Critical | 18.A–18.J VERIFIED | `applications/Agent_Red/.git` exists, points at `mike-remakerdigital/agent-red`; root `.gitignore` excludes nested `.git`; repo histories independent |
| **18.L** | GT-KB platform top-level docs install | identity | Low | 18.K VERIFIED | New CLAUDE.md, README.md, AGENTS.md (if needed), at GT-KB root that are GT-KB-specific |
| **18.M** | Verification & cleanup | verification | Critical | 18.L VERIFIED | T1–T18 pass; transient files cleaned; doctor PASS; DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER retired |

Total: **13 sub-slices** (18.A through 18.M, skipping no letters; each is its own bridge thread).

---

## Risk / Rollback

### Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Mid-migration broken state (GT-KB platform tests failing) | Medium | High | Each sub-slice GO requires its own per-slice test plan; never merge a broken sub-slice; CI gate per sub-slice |
| Mid-migration broken state (Agent Red app dev workflows failing) | Medium | High | Same — per-slice test plan + CI gate |
| Lost Agent Red git history if Option Y is chosen at OQ-1 | Low (only if owner picks Y) | High | Recommend Option X; surface OQ-1 explicitly |
| `git filter-repo` rewrites cause unexpected behavior in dependent repos | Low | Medium | Test extraction in a scratch worktree first; don't push to canonical until validated locally |
| `mike-remakerdigital/agent-red` already has divergent branches (claude/, codex/, dependabot/) — force-push loses them | Medium | Medium | Sub-slice 18.K asks owner: keep those branches, archive them, or accept loss |
| `Remaker-Digital/agent-red-customer-engagement` legacy remote retains S330 wrap commits — needs reconciliation | High | Low | 18.K addresses; owner decision on whether to deprecate the legacy remote |
| Cross-cutting files (`AGENTS.md`, `LICENSE`, `MEMBASE-4-CLAUDE.md`) ambiguous ownership | High | Low | 18.J addresses each individually with owner decision; default = stays at GT-KB root unless evidence supports migration |
| `node_modules/` regeneration breaks Agent Red admin builds | Low | Medium | Sub-slice 18.I regenerates from `package-lock.json`; CI catches |
| New `applications/Agent_Red/.git` corrupts GT-KB git tree | Low | Critical | Test in scratch worktree first; root `.gitignore` updates in 18.K must include `applications/Agent_Red/.git` exclusion before any clone |

### Rollback

Per-sub-slice rollback: `git revert` of the sub-slice's commit chain. Each sub-slice produces a single owner-visible commit (or contiguous commit chain) on develop; reverting puts the tree back to pre-slice state.

Full program rollback (post-18.K): more complex — the repo separation creates an external repo at `mike-remakerdigital/agent-red`. Rollback requires: (a) revert local changes, (b) optionally force-push the canonical Agent Red remote back to its pre-migration state (recoverable via reflog within 90 days). This is "expensive but recoverable" — not a hard cutover.

---

## Open Questions for Codex / Owner

| ID | Question | Default if unanswered |
|----|----------|-----------------------|
| **OQ-1** | Repo-history preservation: Option X (`git filter-repo`, recommended), Y (clean cut), or Z (branch reconciliation)? | Surface to owner via AskUserQuestion at start of sub-slice 18.K |
| **OQ-2** | `Remaker-Digital/agent-red-customer-engagement` legacy remote: deprecate, archive, or repoint? | Surface to owner at start of sub-slice 18.K |
| **OQ-3** | `mike-remakerdigital/agent-red` divergent branches (claude/, codex/, dependabot/): preserve, archive, or accept loss? | Surface to owner at start of sub-slice 18.K |
| **OQ-4** | `AGENTS.md` ownership: GT-KB platform (current content suggests this) or migrate to Agent Red and create new GT-KB AGENTS.md? | Surface to Codex in 18.J review; default = stays at GT-KB root |
| **OQ-5** | `LICENSE`: shared (one copy at root + symlink), migrated (only at app/), or duplicated? | Surface in 18.J; default = duplicated (one at each project root) |
| **OQ-6** | `MEMBASE-4-CLAUDE.md` ownership: GT-KB platform (origin pattern doc — likely stays) or migrate? | Surface in 18.J; default = stays at GT-KB root |
| **OQ-7** | Should the `bridge/` directory move into `applications/Agent_Red/` since Agent Red was the primary user, or stay at GT-KB root for cross-application use? | Surface to Codex in 18.J review; default = stays at GT-KB root (bridge protocol is platform infrastructure) |
| **OQ-8** | Should the `independent-progress-assessments/` directory be split between GT-KB and Agent Red, or stay at GT-KB root? | Surface in 18.J; default = stays at GT-KB root |
| **OQ-9** | `nul` file at root — confirm DELETE? | Default = DELETE (Windows shell-redirection accident) |
| **OQ-10** | `groundtruth.db.corrupt-S311-20260426-104115` — KEEP as audit evidence or DELETE? | Surface in 18.M; default = KEEP (small file; preserves S311 incident evidence) |

---

## Out of scope

- v0.7.0-rc1 GT-KB tag publication (gated *by* ISOLATION-018 VERIFIED, but tag/publish is separate work).
- `mike-remakerdigital/agent-red` production deployment workflows (stay-the-course; only path-references update).
- Agent Red SaaS hibernation policy changes.
- GT-KB platform feature work (`GTKB-DASHBOARD-002`, smart-poller enhancements, etc.).
- Bridge-compliance-gate hook updates that depend on `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — that's a separate S330 spawn-queue thread.
- Production incident response procedures (handled per `applications/Agent_Red/incident-response/`).

---

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/` (the proposal file itself is at `bridge/gtkb-isolation-018-agent-red-file-migration-001.md`).
- Plans migrations that strictly move files from `E:/GT-KB/<root-paths>` → `E:/GT-KB/applications/Agent_Red/<paths>` (within-root operation).
- Does not introduce any live dependency on paths outside `E:/GT-KB/` (the canonical Agent Red GitHub remote is referenced but is not a live file dependency — it's a repo-target identity).
- The pre-migration state (Agent Red files at GT-KB root) is the documented exception per the GOV's WAIVER POLICY clause + the DCL's exceptions[] entry, formalized as a DELIB in sub-slice 18.B.

---

## Provenance

| Source | Reference |
|--------|-----------|
| Owner directive (capture) | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330, 2026-05-04, AskUserQuestion) |
| Spawned governance | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1, `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (S330) |
| Formal-approval packets | `.groundtruth/formal-artifact-approvals/2026-05-04-{delib-s330-agent-red-nested-in-applications-rule,gov-agent-red-nested-in-applications-001,dcl-agent-red-nested-in-applications-check-001}.json` |
| Predecessor program | GTKB-ISOLATION-017 (Slices 1–8.6) — see `bridge/gtkb-isolation-017-*.md` |
| Existing scaffold | `applications/Agent_Red/.gtkb-app-isolation.json` registry; sub-slice 1 GO at `bridge/application-isolation-contract-006.md` |
| Canonical terminology | `.claude/rules/canonical-terminology.md` "Agent Red" entry |
| Project root boundary rule | `.claude/rules/project-root-boundary.md` |
| Operating model | `.claude/rules/operating-model.md` §1 + §2 (application/platform partition) |
| Incident-surfaces inventory pattern | `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md` (S310 pattern) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
