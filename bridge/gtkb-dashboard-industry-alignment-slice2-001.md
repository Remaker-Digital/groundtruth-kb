NEW

# GTKB Dashboard Industry Alignment — Slice 2 (scoping + sub-slice plan)

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Prior deliberations:**
- `bridge/gtkb-dashboard-industry-alignment-slice1-008.md` — Slice 1 VERIFIED
- `bridge/gtkb-dashboard-industry-alignment-slice1-001.md` §3 — original Slice 2 scope declaration (6 deliverables)
- `bridge/gtkb-dashboard-industry-alignment-slice1-005.md:122-123` — reaffirmed Slice 2 scope at GO
- No prior deliberations found searching for `gtkb-dashboard-industry-alignment-slice2` — this is the first review pass on the slice.

bridge_kind: proposal
work_item_ids: [GTKB-DASHBOARD-002]
spec_ids: []
target_project: agent-red
target_paths: ["docs/gtkb-dashboard/**", "scripts/gtkb_dashboard/**", "tests/scripts/test_gtkb_dashboard_*.py"]
implementation_scope: dashboard
requires_review: true
requires_verification: true

---

## 1. Purpose

Slice 2 as declared in `slice1-001.md:149-161` bundles **six deliverables**:

1. Bridge state swimlane panel (per-thread latest status + age-in-state).
2. Work-subject selector (Application vs GT-KB scope toggle).
3. Coverage trend panel (line + branch, over time).
4. Security posture panel (open CVEs, Dependabot, pip-audit, Docker Scout).
5. CI workflow embed (GitHub Actions latest run results).
6. Alert-routing notifier wiring (email / Slack / Teams contact points).

These six items span four distinct integration surfaces (bridge filesystem parser, dashboard UI state, external metrics ingest, third-party notifier APIs). They are **not interdependent**: any subset can land without the others. A single monolithic Slice 2 bridge would also be (a) a large review target and (b) likely to produce partial GO / scope-reduction NO-GOs.

This bridge proposes an **explicit three-sub-slice breakdown** that preserves the WI's total scope while giving each implementation cycle a narrow, reviewable footprint. It is a **scoping proposal first**, not a monolithic implementation proposal. Each sub-slice becomes its own implementation bridge after this thread is VERIFIED.

---

## 2. Proposed Sub-Slice Structure

### 2.1 Slice 2.1 — Visibility (no new data ingest)

**Thread:** `gtkb-dashboard-industry-alignment-slice2a-visibility`

**Deliverables (items 1 + 2):**

- **Bridge state swimlane panel.** Static HTML rendering on the landing page, fed by a new generator `scripts/gtkb_dashboard/generate_bridge_swimlane.py` that parses `bridge/INDEX.md` and the referenced bridge files, extracts per-thread `(document, latest_status, latest_file, age_in_state_minutes)`, and writes a pinned JSON blob `docs/gtkb-dashboard/bridge-swimlane.json`. Landing page reads this JSON at load. Refresh path is the existing dashboard refresh service — swimlane regenerates as part of the dashboard refresh.
- **Work-subject selector.** UI toggle on the landing page (`docs/gtkb-dashboard/index.html`) that filters KPI cards by work subject via a data-attribute on each card. Default state reads `.claude/session/work-subject.json` (if present) for the harness's current subject. Local-state-only; no new backend surface.

**Why 2.1 first:** zero external dependencies. Reuses Slice 1 refresh pipeline. Parseable inputs already exist.

**Approximate size:** 1 new generator script + 1 generator test module + landing page changes + 2 schema tests.

### 2.2 Slice 2.2 — Metrics ingest (new data sources)

**Thread:** `gtkb-dashboard-industry-alignment-slice2b-metrics`

**Deliverables (items 3 + 4):**

- **Coverage trend panel.** Ingest of `coverage.xml` (or `.coverage` via `coverage json`) into `scripts/gtkb_dashboard/refresh_dashboard_db.py` as a new `coverage_runs(started_at, line_coverage, branch_coverage, project)` table. Grafana stat + time-series panel. Matches pattern already used by `refresh_runs`.
- **Security posture panel.** Ingest of `pip-audit --format=json`, Dependabot alerts (via `gh api /repos/:owner/:repo/dependabot/alerts`), and Docker Scout summary into new tables `security_findings(scanner, severity, identifier, introduced_at, resolved_at, project)` and `current_metrics` keys `security_open_critical`, `security_open_high`. Grafana stat panel.

**Why 2.2 second:** depends on a stable schema. Schema change is reviewable in isolation from UI work. Requires concrete source decisions (see Open Questions §5.1, §5.2).

**Approximate size:** schema migration + refresh_dashboard_db extension + new generator panels + 3 test modules.

### 2.3 Slice 2.3 — External integration

**Thread:** `gtkb-dashboard-industry-alignment-slice2c-integration`

**Deliverables (items 5 + 6):**

- **CI workflow embed.** GitHub Actions latest-runs summary. Two viable patterns: (a) `gh api /repos/:owner/:repo/actions/runs?per_page=10` + ingest into `ci_runs(workflow, status, conclusion, run_number, started_at, completed_at)` table + Grafana table panel; or (b) iframe embed of GitHub's workflow run UI (no ingest, no schema). Option (a) is preferred because it keeps dashboard offline-viable.
- **Notifier wiring.** Grafana `provisioning/alerting/contact-points.yaml` + `provisioning/alerting/notification-policies.yaml`. Owner selects one target (email / Slack webhook / Teams webhook) via an environment variable read at provisioning time; default is "no notifier configured, alert list only" (Slice 1 behavior preserved).

**Why 2.3 third:** requires owner input (which notifier, which CI repos), has external-service auth surface, and carries the highest configuration risk. Isolating it keeps the earlier, lower-risk sub-slices unblocked.

**Approximate size:** 1 ingest extension + 2 YAML provisioning files + env-var plumbing + parity tests.

---

## 3. Cross-Sub-Slice Non-Goals

These remain explicitly out of scope for **all three** sub-slices and are already assigned:

- **DORA four-keys / SLO / error budgets** — `GTKB-DORA-001` and onward.
- **Flow metrics / WIP aging / branch & PR health / MTTR** — `gtkb-dashboard-industry-alignment-slice3` (not yet filed).
- **Upstream `groundtruth-kb` dashboard convergence** — separate WI.
- **Production deployment** — no `src/` changes in any sub-slice; GOV-16 not triggered.

---

## 4. Files Touched (this bridge)

**New:** (none — this is a scoping/planning proposal)

**Modified:**
- `memory/work_list.md` — `GTKB-DASHBOARD-002` entry updated with the 2.1 / 2.2 / 2.3 sub-slice breakdown and blocking relationships (2.1 ready; 2.2 ready; 2.3 requires owner notifier decision).

**Not touched:**
- `docs/gtkb-dashboard/**`, `scripts/gtkb_dashboard/**`, `tests/**` — no implementation yet. Each sub-slice bridge will declare its own files-touched set.

---

## 5. Open Questions for Loyal Opposition Review

Explicit flags for Codex to accept / reject / redirect:

### 5.1 Is three sub-slices the right cut?

Alternative cuts:
- Two sub-slices (2.1 = visibility + CI embed; 2.2 = metrics + notifier).
- Six separate one-item bridges (most granular, most overhead).
- Monolithic Slice 2 (reject this scoping proposal, file one large bridge).

I chose three for: (a) clear dependency boundary between 2.2's schema and 2.3's external integration, (b) 2.1 can ship today with zero external decisions, (c) 2.3's owner-input requirement isolates the blocking decision.

### 5.2 Coverage data source — `coverage.xml` vs `coverage json`?

Both work. `coverage.xml` is the universal CI artifact; `coverage json` is cleaner to parse. Proposed: prefer `coverage json` if a `.coverage` file exists in the repo root; fallback to `coverage.xml`. Codex to confirm or override.

### 5.3 Security data source — pip-audit + Dependabot + Scout all in one ingest, or one at a time?

Prior experience (`CLAUDE-ARCHITECTURE.md` references Dependabot as active): Dependabot is the authoritative source for npm + pip dependency CVEs in this repo. pip-audit is a backup that runs in CI. Scout is Docker-image-specific. All three produce different severity taxonomies.

Proposed: Slice 2.2 ingests Dependabot + pip-audit (both Python-dependency scope) in a single pass; Scout ingest deferred to a Slice 2.2b if Codex wants. Codex to confirm or request earlier/later Scout.

### 5.4 CI workflow embed — ingest vs iframe?

Iframe is trivial (one line HTML) but makes the dashboard online-dependent on github.com. Ingest is ~100 lines Python but keeps the dashboard self-contained. Proposed: ingest. Codex to confirm or override.

### 5.5 Notifier — which default?

Owner decision required before 2.3 lands. Proposed default: "no notifier configured, alerts stay in Grafana alert list" (preserve Slice 1 behavior). Owner picks email / Slack / Teams when ready. Codex to accept or propose forcing a specific default.

### 5.6 Should `memory/work_list.md` update in this bridge or in each sub-slice bridge?

Proposed: update here (reflects the planning decision). Each sub-slice bridge marks its own entry DONE on VERIFIED. Codex to accept or request per-sub-slice updates.

---

## 6. Verification Matrix (this bridge)

| Risk | Test requirement |
|------|-----------------|
| Sub-slice allocation misaligned with `slice1-001.md` scope | Each of items 1-6 in `slice1-001.md:149-161` maps to exactly one sub-slice in §2. Manual cross-check in review. |
| Sub-slice dependencies wrong | 2.2's schema does not depend on 2.1 outputs; 2.3 does not depend on 2.2's ingest. Stated dependency relationships verified in §2. |
| Scope creep into Slice 3 territory | §3 enumerates Slice 3 items by name; none appear in §2. |
| `memory/work_list.md` drift | Once this bridge is VERIFIED, the work-list entry for `GTKB-DASHBOARD-002` reflects the sub-slice breakdown as its "next step" column. |
| Blocking relationships on the current actionable table | Slice 2.3 blocks on owner notifier choice; explicit in §2.3 and §5.5. |

---

## 7. Verification Matrix (each sub-slice bridge, to be specified at filing)

Each sub-slice bridge will carry its own full verification matrix with pytest lanes, schema-change guardrails, and Slice 1 non-regression assertions. This bridge does not pre-empt those matrices — that is the implementation bridge's job.

---

## 8. Out of Scope

- Implementation of any item 1-6 (that is the three sub-slice bridges).
- Slice 3 (DORA, SLO, flow metrics, MTTR).
- DORA-001 foundation (separate thread).
- `src/` changes.
- Production deployment.

---

## 9. Decision Needed From Owner

Only one: **notifier default** for Slice 2.3 (§5.5). Not blocking Slice 2.1 or 2.2. Defer until 2.2 VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
