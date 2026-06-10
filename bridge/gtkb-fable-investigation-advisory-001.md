ADVISORY

bridge_kind: governance_advisory
Document: gtkb-fable-investigation-advisory
Version: 001
Author: prime-builder (Claude Fable 5, harness B) under direct owner instruction — owner-directed advisory
Date: 2026-06-10

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 67ed84c1-5adb-44f8-ae29-3d0f8fd286b6
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

---

## Source

- Owner directive (2026-06-10, interactive session): create a bridge advisory chartering the "Fable Investigation" milestone remediation and hygiene project from the 2026-06-10 investigation results, including hygiene-skill enhancement for repeatable re-runs and the specific work items, with anti-duplication detail for Prime Builder.
- Chartering owner decisions: `DELIB-FABLE-GRILL-20260610-Q1` .. `-Q7` (AskUserQuestion chain, persisted to the Deliberation Archive; enumerated under Owner Decisions / Input below).
- Primary findings report (v1): `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md` — Claude Fable 5 (harness B), 16 subagents / 4 rounds, 60 ranked findings HYG-001..060, all live-verified, 14 adversarially re-verified. Finding IDs frozen.
- Merged source report (v2): `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10-v2.md` — parallel independent investigation by Antigravity (harness C), 45 findings under its own colliding HYG-001..045 numbering, plus LO review notes. Distinct survivors renumbered HYG-061..068 here; v2's internal numbering is not used outside this advisory's provenance/merge sections.
- Originating request thread: `bridge/gtkb-architecture-governance-hygiene-investigation-001/-003.md` (LO/owner-filed NEW/REVISED) — fulfilled by the two reports plus this advisory; owner may close it.

Protocol notes disclosed: (a) ADVISORY entries are conventionally Loyal-Opposition-authored; this one is Prime-Builder-authored under direct owner instruction (DELIB-...-Q6). (b) The owner-selected packaging label "owner_directed_advisory" is not a valid bridge_kind under DCL-BRIDGE-KIND-TAXONOMY-ENUM-001; the nearest taxonomy value `governance_advisory` is used and the owner-directed nature is recorded here.

## Claim

1. The GT-KB platform carries 68 verified, ranked hygiene/architecture findings (HYG-001..060 from v1; HYG-061..068 admitted from v2 after live spot-verification under the Q1 verified-merge policy), spanning dead bridge automation, a dead regression-signal system, pervasive Agent-Red residue, enforcement gaps/false-positive friction, and absent retention/backup policies.
2. These convert into one milestone project — **PROJECT-FABLE-INVESTIGATION** — of 23 cluster work items across three waves (charter table below), at hybrid-cluster granularity per DELIB-...-Q3, with owner approval batched at each cluster's proposal per DELIB-...-Q4.
3. Repeatable re-investigation at the same-or-better quality and lowest token cost requires the layered capability of DELIB-...-Q5: deterministic CLI detector core (FAB-19), a `gtkb-hygiene-investigation` orchestration skill (FAB-20), and a delta mode keyed to the HYG-001..068 baseline registry; targets <=400K tokens full re-run, <=150K delta (vs ~3.4M for the manual first run).
4. Eight v2 claims are refuted or superseded with live evidence and must not be re-chased (anti-duplication list below).

## Owner Decision Needed

None outstanding. All chartering decisions were collected via AskUserQuestion on 2026-06-10 and persisted (see Owner Decisions / Input). Future owner decisions arrive batched at each cluster proposal per DELIB-FABLE-GRILL-20260610-Q4.

## Recommended Prime Action

1. Acknowledge this advisory; cite it in every follow-on proposal's `Prior Deliberations` and `Source advisory` fields.
2. Work the charter in wave order: file one NEW implementation proposal per FAB work item (or small coherent group), each carrying its member-finding AUQ batch (DELIB-...-Q4), Specification Links, target_paths, and an h2 `## Requirement Sufficiency` section; standard GO -> implement -> report -> VERIFIED lifecycle per cluster.
3. Before any new investigation work, read the Anti-Duplication Guide below — the evidence base is already verified and indexed.
4. Land FAB-19/FAB-20 (deterministic core + investigation skill) before the first scheduled re-investigation.

## Classification Slot

Prime Builder disposition per the advisory loop: ____ (adopt | adapt | reject | defer | monitor). Expected: **adopt** — the chartering decisions are owner-recorded; this slot is completed by the acknowledging Prime session.

---

## Owner Decisions / Input

All seven chartering decisions were collected via AskUserQuestion on 2026-06-10 and persisted to the Deliberation Archive:

| Decision | Resolution | DELIB |
|---|---|---|
| v2 report incorporation | Verified-merge; adversarially-verified v1 wins conflicts; survivors admitted as HYG-061+ | DELIB-FABLE-GRILL-20260610-Q1 |
| Project scope | Full milestone, one project, internal waves (1 quick wins + security, 2 clusters, 3 architecture) | DELIB-FABLE-GRILL-20260610-Q2 |
| WI granularity | Hybrid clusters (~18-23 WIs), each enumerating its HYG IDs | DELIB-FABLE-GRILL-20260610-Q3 |
| Triage protocol | Per-finding Tier-1 superseded; owner AUQ batches at each cluster proposal; 19 high-complexity findings get grill-me depth in their cluster cycle | DELIB-FABLE-GRILL-20260610-Q4 |
| Repeatability architecture | Layered: deterministic CLI core + gtkb-hygiene-investigation skill + delta mode; <=400K tokens full re-run, <=150K delta | DELIB-FABLE-GRILL-20260610-Q5 |
| Advisory packaging | Owner-directed ADVISORY bridge entry (this file) | DELIB-FABLE-GRILL-20260610-Q6 |
| Creation timing | Chartering session creates project + WIs at approval_state=auq_resolved; implementation authorized later per cluster via bridge GO | DELIB-FABLE-GRILL-20260610-Q7 |

## Specification Links

Relevant governing specifications for this advisory and the downstream cluster proposals:

- `GOV-STANDING-BACKLOG-001` (backlog as governed work authority; capture is not implementation approval)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (durable-artifact bias)
- `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge lifecycle; ADVISORY semantics)
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` (bridge_kind taxonomy applied above)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (apply to each downstream cluster proposal, not satisfied here)
- `GOV-SESSION-SELF-INITIALIZATION-001` (implementation gaps must remain backlog-visible — satisfied by the cluster WIs)
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (governs the Q5 layered architecture)
- `.claude/rules/backlog-approval-state.md` (auq_resolved state for created WIs)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (isolation placement rules for applications)

## v2 Verified-Merge Results

Every v2-distinct claim was spot-verified against live state on 2026-06-10 (verifier agent; evidence per verdict). **Admitted findings (new frozen IDs):**

| ID | Title (merged framing) | Verdict basis | Rating |
|---|---|---|---|
| HYG-061 | Antigravity skill adapters drifted: live 22 STALE + 14 MISSING, exit 1 (`check_harness_parity.py --harness antigravity --json`, 2026-06-10T18:42Z); v2's 17/11 counts were stale | PARTIAL -> confirmed with corrected numbers | M/M/H drift |
| HYG-062 | Goose harness (E) has zero entries in `config/agent-control/harness-capability-registry.toml` and no headless invocation surface (desktop-only registry entry); nuance: status=suspended | CONFIRMED | M/L/H drift |
| HYG-063 | `check_harness_parity.py:26` hardcodes `_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")` used when registry projection fails | CONFIRMED | L/L/H debt |
| HYG-064 | Direct spec contradiction: GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2 names `.claude/hooks/last-user-visible-startup-*.md` a forbidden read pattern while DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 MANDATES rendering that cached file, without invoking the GOV's declared-TTL exception. (Absorbed reconcilable tensions: GOV-SSI-vs-RELAY, RELAY-vs-FRESH-READ, TOKEN-BUDGET-vs-GOV-SSI) | CONFIRMED (v2 pair HYG-027) | M/M/H drift |
| HYG-065 | ~1,004 open WIs vs only 162 covered by any active project authorization — the doctor's "930 warn" backlog-health output is one orphaned-WI WARN per uncovered open item | CONFIRMED (interpretation verified in doctor.py:4089-4221) | M/M/H debt |
| HYG-066 | 76 skill-health findings across 72 skills (fenced_python 26, db_mutation 32, index_write 18; `check_skill_health.py` exit 1) and the checker is wired into NO gate or doctor check | CONFIRMED + corrected gate claim | M/M/H debt |
| HYG-067 | Doctor AUQ-coverage FAIL (92.0%, 46 non-AUQ) is polluted signal: all sampled non-AUQ entries are owner-decision-tracker prose-pattern FALSE POSITIVES already marked resolved in `memory/pending-owner-decisions.md` — the FAIL misdirects toward "seeding missing decisions" when the defect is detector precision | NEW (corrects v2's HYG-018 framing) | M/M/H defect |
| HYG-068 | Doctor isolation suite (`doctor_isolation.py:219-272` writability probe; sibling subject check) is an adopter-context suite run unconditionally against the platform root, producing standing FAILs (product-scope-writable, subject-expected-application) that are miscalibrated by design | NEW (corrects v2's HYG-040 framing) | M/M/H defect |

**Refuted v2 claims — do NOT chase (anti-duplication):**

- v2 HYG-045 (openrouter status mismatch DB vs registry): REFUTED — both surfaces identical (active, v7, wrapper `scripts/openrouter_harness.py` exists).
- v2 HYG-038 (impl-start gate not registered for Codex): REFUTED — `.codex/hooks.json` registers `implementation-start-gate.cmd` at matchers "Bash" and "apply_patch".
- v2 HYG-041/042 ("blocking release gates"): exit-1 facts true, gate-impact REFUTED — neither script is referenced by `release_candidate_gate.py` nor any workflow; orphan-citation audit sits in doctor at WARN severity.
- v2 HYG-025 (DCL-REPORTING-SURFACE-FRESH-READ-001 permits group-by on `project_name`): REFUTED — the DCL lists that column as a Forbidden source with a grep_absent assertion; v2 inverted the DCL's text.
- v2 HYG-028 (FRESH-READ DCL contradicts GOV-SOT-FRESHNESS): REFUTED — parent/child by design.
- v2 HYG-020 ("DA harvest effectively bypassed"): superseded by v1 HYG-049 (skeptic-upheld numerator-convention artifact).
- v2 HYG-002 (stand-downs caused by packet gates): superseded by v1 HYG-001/HYG-003 (64% of launches die at WinError 2 — reproduced; packet-gate stand-downs were the May-era class, already memorialized).
- v2 S14 "CONFIRMED": scope split — codex adapters PASS live (`generate_codex_skill_adapters.py --check`, 36 current); the drift is antigravity-side (HYG-061).

## Project Charter: PROJECT-FABLE-INVESTIGATION

One MemBase project, three waves, 23 cluster work items. Each WI enumerates its frozen HYG IDs; per-finding detail (problem, locations, verification, owner options) lives in the v1 report and is NOT duplicated here. Existing open WIs noted per row must be absorbed or superseded by the cluster proposal, not duplicated.

### Wave 1 — quick wins + safety

| WI | Title | Findings | Existing-WI overlap |
|---|---|---|---|
| FAB-01 | Restore bridge dispatch launchability + add launchability doctor check | HYG-001, HYG-004 | WI-4388, WI-4408, WI-4410 |
| FAB-02 | Secure stranded Terraform state + credential replication surfaces | HYG-019, HYG-020 | GTKB-SECRETS-PURGE workstream |
| FAB-03 | Operationalize MemBase backup (verified tool, zero runs, all channels closed) | HYG-002 | none |
| FAB-04 | Storage reclamation: git-LFS orphans (4.76GB), orphaned worktrees (~3GB), root DB residue (~3GB) | HYG-013, HYG-057, HYG-058 | WI-3394 (close as not-reproducing) |
| FAB-05 | Retire era-stranded + contradictory rule files (poller runbook, Cursor-era files, duplicated blocks, mojibake) | HYG-018, HYG-026, HYG-027, HYG-038 + demoted mojibake/codex-bootstrap items | WI-4348, WI-3278, WI-3465 |
| FAB-06 | Correct always-loaded narrative inaccuracies (CLAUDE.md KB-access pointer, AGENTS.md Agent-Red scope, GOV index numbering) | HYG-017 (CLAUDE.md half), HYG-031, HYG-037 | WI-4331 |
| FAB-07 | Repair doctor false signals (DA-harvest convention, four-demo-apps claim, isolation-suite calibration, AUQ-coverage pollution) + create missing bridge docs | HYG-049, HYG-035, HYG-067, HYG-068 + v2 missing-docs item | WI-3277 |
| FAB-08 | Fix applications/_test_* slot leak (rmtree/Windows root cause) + purge 229 slots + complete Agent_Red registration | HYG-053, HYG-022 | none |

### Wave 2 — remediation clusters

| WI | Title | Findings | Existing-WI overlap |
|---|---|---|---|
| FAB-09 | Safety-gate + hook registration normalization (tracked-vs-local settings, stub hooks, dead scheduler, missing registrations) | HYG-041, HYG-050, HYG-045 + v2 hook-registration consolidation | WI-4305 |
| FAB-10 | Dispatch telemetry, claim contract, INDEX write perimeter (ADS filenames, dead poll thread, TTL/holder/session-id contract, INDEX well-formedness lint) | HYG-005, HYG-006, HYG-007, HYG-039 | WI-4396, WI-4358, WI-3364, WI-3488, WI-3491 |
| FAB-11 | Regression-signal revival, SEQUENCED: assertion-corpus path repair -> sweep revival -> tests-table reconnection -> pipeline_events retention + VACUUM | HYG-029, HYG-044, HYG-030, HYG-014 | WORKLIST-ARCHITECTURE-IMPROVEMENT-P2, WI-3178..3224 cluster |
| FAB-12 | Agent-Red residue sweep: root config identity, pyproject, memory titles, .github templates/workflows/dependabot, CI lane repair | HYG-012, HYG-016, HYG-024, HYG-034, HYG-043 | WI-3417, WI-3419, WI-3430, WI-3431, WI-3466, WI-4346/4347 |
| FAB-13 | Retention policy umbrella for runtime stores (.gtkb-state 3.6GB, envelopes, pending-owner-decisions, Drive-sync interference + .driveignore coverage) | HYG-021, HYG-055, HYG-056 | WI-4282 |
| FAB-14 | Gate false-positive feedback loop: root-boundary Bash parser, impl-auth parsers, narrative-gate packet channel + consolidation of ~20 open gate-FP WIs into a tested gate-quality program | HYG-040, HYG-042, HYG-046, HYG-047 | WI-3322/3334/3336/3351/3356/3357/3358/3384/3410/3448/3454/3463/3493/3496/3497/3499/4304/4354/4355/4368 |
| FAB-15 | Role-narrative + spec reconciliation: durable-registry inversion, codex approval_policy posture, canonical-terms table freeze, startup-relay-vs-freshness contradiction | HYG-032, HYG-033, HYG-036, HYG-064 | WI-3479, WI-4338, WI-4362 |
| FAB-16 | Harness parity remediation: antigravity adapter regen, goose registration/wrapper decision, parity-fallback removal | HYG-061, HYG-062, HYG-063 | WI-3459, WI-4364 |
| FAB-17 | DA/Chroma read-path reliability: search fallback, concurrent-access hangs, benchmark CLI repair, chroma triplication | HYG-048 + demoted benchmarks-cli/chroma-triplication | WI-3395 |
| FAB-18 | Backlog dignity: advisory-flood drain policy execution, PAUTH coverage model, IPA root organization, startup metric accuracy | HYG-015, HYG-060, HYG-065 | WI-4402, WI-3327, WI-3502 |

### Wave 3 — architecture + repeatable capability

| WI | Title | Findings | Existing-WI overlap |
|---|---|---|---|
| FAB-19 | Deterministic hygiene detector expansion: encode the ~15 hand-derived detector classes (dispatch economics, INDEX health, retention sizes, scratch census, era markers, parity) into gt CLI / sweep registry + wire skill-health checker | HYG-051, HYG-066 | WI-3451, WI-4238 |
| FAB-20 | gtkb-hygiene-investigation skill: 4-round probe workflow + chunked report generator + delta mode against the HYG registry (token targets per DELIB-Q5) | Q5 charter | WI-3391 |
| FAB-21 | Startup load-cost reduction: 38-rule 336KB load vs 250K budget, per-tool-call hook latency floor, stale always-loaded pointers | HYG-008, HYG-025, HYG-028 | WI-4360, WI-4361, WI-4403 |
| FAB-22 | Architecture decisions cluster (owner-heavy): protocol overhead per landed change, god modules, environment/interpreter contract, ADR/DCL enforcement coverage, template-sync discipline | HYG-009, HYG-010, HYG-011, HYG-023, HYG-052 | GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001, WI-3354, WI-3498 |
| FAB-23 | Demoted near-miss cleanup batch (14 items incl. investigation self-residue $null file) | v1 Appendix A demoted list | various AUGMENTS noted in report |

Sequencing constraints carried from the report's cluster map: FAB-11 is internally ordered (corpus before sweep, or the sweep re-floods pipeline_events); FAB-01 without FAB-10 leaves the next dispatch breakage invisible; FAB-19/20 should land before the first scheduled re-investigation.

## Hygiene-Capability Enhancement Plan (Q5 charter detail for FAB-19/FAB-20)

1. **Deterministic core (FAB-19).** Promote every census/parse/aggregation the investigation hand-derived into `gt` surfaces: dispatch-economics aggregation over `.gtkb-state/bridge-poller/*.jsonl`; INDEX parse/health/growth metrics; store-size + retention census (.git breakdown, .gtkb-state, scratch dirs, memory stores); era-stranded/contradiction grep patterns into `config/governance/hygiene-sweep-patterns.toml`; harness launchability + parity probes; skill-health wiring. Output: a machine-readable evidence pack at ~0 tokens.
2. **Orchestration skill (FAB-20).** `gtkb-hygiene-investigation` skill packaging the proven method: parallel focus-area probes with the structured findings schema (slug/class/locations/verification/ratings/owner-question), gap-probe + completeness-critic + adversarial-skeptic round, loop-until-dry with decay disclosure, chunked report generator keyed to the schema. Probe prompts consume the layer-1 evidence pack instead of re-deriving it.
3. **Delta mode (FAB-20).** The HYG-001..068 registry (this advisory + v1 report) is the baseline; re-runs diff layer-1 evidence against baseline and probe only changed surfaces. Token targets: <=400K full re-run, <=150K delta (vs ~3.4M for the manual first run).

## Anti-Duplication Guide for Prime Builder

Do not re-derive any of the following — it is verified and documented:

- **Evidence locations.** v1 report Appendix C (Phase-0 tool digests), Appendix D (every probe's per-surface method/command log), Appendix E (seed verification). Quantified dispatch economics method + numbers in HYG-003 (107,156 trigger invocations; class breakdown in the finding body). Skeptic re-verification notes embedded in each of the 14 re-verified findings.
- **Verified-this-session facts** (cite, don't recheck): WinError-2 launch reproductions (HYG-001); git LFS orphan census (HYG-013); MemBase table-size breakdown (HYG-014); 229 slot count + conftest rmtree root cause (HYG-053); 38-rule 335,977-byte load vs the 250,000-byte budget constant (HYG-025); GOV index contradictions (HYG-031); antigravity parity counts 22/14 (HYG-061, 2026-06-10T18:42Z).
- **Refuted claims** (do not chase): the eight-item refuted list above, plus WI-3394 (broken blob not reproducing — close via FAB-04).
- **Tooling gotchas for investigation work:** `gt` is not on PATH (invoke `python -c "from groundtruth_kb.cli import main; ..."`); `python scripts/benchmarks/cli.py` crashes under its documented invocation (module-form also hangs on ChromaDB); `gt deliberations search` hangs under concurrent access — use read-only sqlite; the Bash root-boundary directive blocks `/dev/null` and MSYS paths — use PowerShell with relative paths; bridge claims need the transcript-filename UUID, not `CLAUDE_CODE_SESSION_ID`; `## Requirement Sufficiency` must be an h2; `SPEC_LINK_HEADING_RE` accepts only `relevant|linked|governing` + `Specification Links|References`.
- **Open-WI overlap.** Each FAB row lists the WIs its proposal must absorb or supersede; the v1 cross-reference map carries the per-finding AUGMENTS/DISTINCT calls with deltas.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
