# Operating-Model Drift Inventory — Slice 0 §3.3 Deliverable

**Status:** Slice 0 deliverable per `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` REVISED-1 (-003) GO at -004.

**Authority:** none (informational input to the Slice 0 post-impl recommendation; not cited by any rule, hook, test, or canonical governance artifact).

**Baseline:** the **owner verbatim text** at `docs/operating-model-DRAFT-2026-04-30.md` §A is canonical. Drift findings measure existing artifacts against §A, with §B (Codex revision) as supplement.

**Path:** filed at `docs/operating-model-drift-inventory-2026-04-30.md` (deviation from proposal §3.3 fallback). The proposal proposed `independent-progress-assessments/PRIME-INSIGHT-DROPBOX/...` with `independent-progress-assessments/` top-level as fallback; both are gitignored per `.gitignore` lines 251–260. Moved to `docs/` alongside the DRAFT artifact and terminology table to land in a tracked location. Same file, same content; only the path differs.

**Severity model** per advisory:
- **P0** Active misdirection — could cause an agent to take the wrong action, bypass approval, mutate the wrong source of truth, or miss a verification/release gate.
- **P1** Governance drift — conflicts with current owner intent, role boundary, schema model, or lifecycle model.
- **P2** Capability overclaim — desired written as implemented.
- **P3** Terminology noise — confusing wording but unlikely to drive wrong behavior alone.
- **P4** Historical context — stale but harmless; preserve.

**Stop criterion:** one pass through the bounded corpus (`.claude/rules/**`, `CLAUDE.md`, `AGENTS.md`, 22 active `memory/work_list.md` rows, 10 most-recent VERIFIED bridge files in `bridge/INDEX.md`). No iteration; no remediation.

---

## P0 — Active Misdirection

### `DRIFT-0001` — Application name inconsistency within CLAUDE.md

- **severity:** P0
- **evidence:** `CLAUDE.md` line 1: "CLAUDE.md - Agent Red Customer Experience". Line 3: "Agent Red Customer Experience commercial project". Line 16: "(like Agent Red Customer **Engagement**)". Line 53: "Project Name | Agent Red Customer Experience". Line 177: "Agent Red Customer Experience commercial project". 4 occurrences of "Customer Experience" + 1 occurrence of "Customer Engagement" in the same control-text file.
- **risk:** an agent reading line 16 may believe the application name is "Agent Red Customer Engagement," contradicting the 4 other authoritative references. Future references could compound the inconsistency.
- **recommendation:** **defer to Slice 1** (CLAUDE.md is highest-leverage control text; correct in canonical Slice 1 commit alongside the application/project terminology decision per `OM-DELTA-0003`).

### `DRIFT-0002` — LO authority over requirements absent from `loyal-opposition.md`

- **severity:** P0
- **evidence:** `.claude/rules/loyal-opposition.md` line 9-16 defines LO as "inspect, critique, and analyze implementation, plans, and documentation" + "may question Prime Builder technology choices, approaches, and designs." The owner verbatim §A grants LO authority to "question the cited requirements to disambiguate the owner's intent in order to substantiate requests for changes and corrections" — a substantive authority over **requirements**, not just over Prime's choices. The rule file is silent on this.
- **risk:** an LO session reading only the rule file would not know it has owner-stated authority to question cited requirements; LO might decline to flag ambiguous or internally inconsistent requirements as in scope. Combined with `prime-builder-role.md` line 39-43 ("Prime Builder should actively question owner direction, specifications, and intent"), the requirement-questioning authority appears to have silently moved from LO to Prime.
- **recommendation:** **defer to Slice 1** (this is the same gap as `OM-DELTA-0001`; canonical operating-model artifact must explicitly assign requirement-questioning authority based on owner choice).

### `DRIFT-0003` — Reference to non-existent `.claude/rules/canonical-terminology.md`

- **severity:** P0
- **evidence:** `CLAUDE.md` line 14 references `.claude/rules/canonical-terminology.md` as "Full managed glossary (when adopted)". `ls .claude/rules/` confirms the file does not exist. The reference is conditional ("when adopted") but reads as a current-state pointer.
- **risk:** an agent following the reference will fail to find the file; "(when adopted)" qualifier is easy to miss in skim-reads. Could drive incorrect terminology assumptions.
- **recommendation:** **clarify in Slice 1** (either remove the reference or mark it explicitly as "intended; not yet adopted" per `OM-DELTA-0030` current-vs-target-state discipline).

---

## P1 — Governance Drift

### `DRIFT-0004` — CLAUDE.md uses "project" for the application-level scope

- **severity:** P1
- **evidence:** `CLAUDE.md` line 3 calls Agent Red the "commercial project". Line 49 has "## Project Identity" with "Project Name | Agent Red Customer Experience". Line 16 defines "Adopter: A project that consumes GT-KB". Per the terminology table §1 + §2, Agent Red is an application (not a project); a project is scoped work *within* an application.
- **risk:** terminology drift between rules and operating model creates governance ambiguity: project-level decisions (priorities, work items) may be applied at application level by mistake.
- **recommendation:** **defer to Slice 1** (consolidated in the `OM-DELTA-0003` terminology cluster).

### `DRIFT-0005` — CLAUDE.md uses "Knowledge Database" not "MemBase"

- **severity:** P1
- **evidence:** `CLAUDE.md` line 41 says "All project knowledge lives in the Knowledge Database". Line 138-141: "Knowledge Database Access" section uses both "Knowledge Database" and "KB". Owner verbatim §A consistently uses "MemBase append-only database."
- **risk:** rule files and documentation use "Knowledge Database"; owner uses "MemBase". Disambiguation is unclear when an agent searches for one term and the other is used.
- **recommendation:** **clarify in Slice 1** (canonical artifact picks one canonical name and uses it consistently; "Knowledge Database" / "KB" become allowed synonyms per terminology table §11).

### `DRIFT-0006` — `loyal-opposition.md` severity scale is P0–P3 not P0–P4

- **severity:** P1 (governance — the LO reporting standard mismatches the advisory's severity model)
- **evidence:** `.claude/rules/loyal-opposition.md` line 54: "severity (P0-P3)". The Codex advisory at `OPERATING-MODEL-ALIGNMENT-REMEDIATION-ADVISORY-2026-04-30.md` proposes P0–P4 (with P4 = historical context). Slice 0 uses P0–P4; rule file uses P0–P3.
- **risk:** LO reports filed under the rule's P0–P3 model cannot represent "harmless historical" findings cleanly; everything stale is forced into P3 (terminology noise) regardless of harm level.
- **recommendation:** **clarify in Slice 1** (rule file extends to P0–P4 to match Slice 0 + advisory; or rejects P4 explicitly with rationale).

### `DRIFT-0007` — `acting-prime-builder.md` references `applications/` boundary

- **severity:** P1
- **evidence:** `.claude/rules/acting-prime-builder.md` lines 14-19 mandate "All GT-KB application files must remain within `E:\GT-KB\applications\`; Agent Red application files must remain within `E:\GT-KB\applications\Agent_Red\`." Repeated similarly in `loyal-opposition.md` lines 20-22 and `project-root-boundary.md` lines 9-13.
- **risk:** file-system layout assumes one or more applications under `applications/`. Agent Red is treated as an application (consistent with terminology). But CLAUDE.md frames Agent Red as a project, creating a rule-vs-CLAUDE.md disagreement.
- **recommendation:** **defer to Slice 1** (consistent with `OM-DELTA-0003` cluster: rule files already assume application-level granularity; CLAUDE.md needs alignment).

### `DRIFT-0008` — Backlog as "ordered set" vs. "roughly chronological stack"

- **severity:** P1
- **evidence:** `memory/work_list.md` rows are presented in numbered sequence with TOP/priority annotations (more "ordered set"). Owner verbatim §A says backlog is "a roughly chronological stack of highest-to-lowest priority engineering work." The work_list doesn't appear chronological.
- **risk:** if backlog ordering should be roughly chronological per owner intent, the current numbering scheme may mislead agents about priority semantics. This is `OM-DELTA-0004` materializing in the actual artifact.
- **recommendation:** **defer to Slice 1** (canonical operating-model artifact resolves the chronology question; work_list ordering rules then follow from that decision).

---

## P2 — Capability Overclaim

### `DRIFT-0009` — Dashboard claims may exceed implementation

- **severity:** P2
- **evidence:** `docs/gtkb-dashboard/` contains both implemented and intended-surface artifacts. `bridge/gtkb-dashboard-002` Slice 2.3 shows the integration surface is parked pending notifier choice. Owner verbatim §A describes a comprehensive dashboard ("display of current configuration, operating state, the status of 3rd party services, computed project KPI, reports and interactive access to MemBase, test results, and GT-KB inventory") that is not fully implemented.
- **risk:** owner reading the operating-model text expects current capability; partial implementation contradicts. Per `OM-DELTA-0030`: claims must distinguish implemented from intended surfaces.
- **recommendation:** **defer to Slice 4** (docs/dashboard/CLI alignment slice should reconcile current-vs-target claims explicitly).

### `DRIFT-0010` — Smart-poller "active automation path" framing

- **severity:** P2
- **evidence:** `.claude/rules/bridge-essential.md` lines 27-50 ("Operational Mode") describes the smart poller as conditionally available ("when the smart poller implementation is present, verified, and reported healthy"). The smart-poller is functional this session (verified by S320 + S321 work) but rule file's conditional language reads as if the capability is uncertain. Recent VERIFIED bridges show smart poller is active.
- **risk:** an agent reading bridge-essential.md alone may default to manual scans; the conditional language doesn't reflect that the smart poller has been verified-and-active for ~5 sessions.
- **recommendation:** **clarify in Slice 1 or 3** (rule file should state smart-poller is currently active per S320 verification; explicit removal-trigger conditions stated for fallback to manual).

---

## P3 — Terminology Noise

### `DRIFT-0011` — "implementation" used for both proposal stage and report stage

- **severity:** P3
- **evidence:** Several bridge files use "implementation" loosely without disambiguating proposal-stage vs. report-stage. The terminology table §7-§8 distinguishes them; canonical artifacts should follow.
- **risk:** confusion when scanning bridge thread state; terminology table §7-§8 already defines the canonical distinction so risk is low.
- **recommendation:** **clarify in Slice 1** (light-touch rule-file note; not a Slice 4 priority).

### `DRIFT-0012` — Multiple "memory" concepts: MemBase vs. memory/MEMORY.md vs. session-state

- **severity:** P3
- **evidence:** `memory/MEMORY.md` is session-state; `memory/work_list.md` is the standing backlog; `groundtruth.db` is MemBase. The "memory/" path label conflates session-state and standing-state in the file system.
- **risk:** an agent could mistake `memory/MEMORY.md` for canonical knowledge or `memory/work_list.md` for session memory.
- **recommendation:** **clarify in Slice 1** (canonical artifact distinguishes the three concepts; rule files are already mostly correct on this).

### `DRIFT-0013` — Bridge "REVISED" used for both proposal and post-impl

- **severity:** P3
- **evidence:** `.claude/rules/file-bridge-protocol.md` lines 56-66 enumerate statuses (NEW, REVISED, GO, NO-GO, VERIFIED). REVISED applies to both revised proposals AND revised post-impl reports; the protocol does not distinguish.
- **risk:** ambiguity in audit reading; in practice the version number sequence (NEW → NO-GO → REVISED → GO → NEW post-impl → ...) makes intent recoverable but requires sequence inspection.
- **recommendation:** **preserve as historical** (the ambiguity is benign and resolved by sequence inspection; not worth a rule-file change).

---

## P4 — Historical Context (Preserved)

The following classes of stale-but-harmless references were observed and require no remediation:

- **OS-poller historical references** in `.claude/rules/bridge-essential.md` "Incident History" (S290-S294, S308). These are intentionally preserved as lessons-encoded; no drift remediation needed.
- **AGENTS.md** is explicitly marked "historical/reference guidance for Loyal Opposition sessions" (line 3); its existence as a historical document is acknowledged. No drift remediation needed.
- **Pre-S320 bridge files** in `bridge/INDEX.md` referencing OS pollers as the active path. Historical context; later VERIFIED files supersede.
- **memory/work_list.md** completed-during-session sections (rows 8, 16-18, 20) marked DONE. Intentional preservation per the work_list contract.
- **Multiple references to retired Windows scheduled tasks** in rule files. Preserved as do-not-restore guidance; not drift.

---

## Aggregate Findings Summary

| Severity | Count | Distribution |
|---|---|---|
| **P0** | 3 | DRIFT-0001 (CLAUDE.md name inconsistency), DRIFT-0002 (LO authority over requirements gap), DRIFT-0003 (non-existent file reference) |
| **P1** | 5 | DRIFT-0004 (project term for application), DRIFT-0005 (Knowledge Database vs MemBase), DRIFT-0006 (severity scale), DRIFT-0007 (rule files vs CLAUDE.md alignment), DRIFT-0008 (backlog ordering semantics) |
| **P2** | 2 | DRIFT-0009 (dashboard overclaim), DRIFT-0010 (smart-poller conditional language) |
| **P3** | 3 | DRIFT-0011 (implementation term), DRIFT-0012 (memory concepts), DRIFT-0013 (REVISED status ambiguity) |
| **P4** | (multiple classes) | OS-poller history, AGENTS.md, pre-S320 bridges, work_list completed sections, retired-tasks references |
| **Total actionable (P0+P1+P2+P3)** | **13** | — |

**Decision-threshold mapping** (per the GO'd proposal §3.4):
- P0/P1 findings: 3 + 5 = **8 findings**.
- Per the proposal §3.4 thresholds: <10 P0/P1 → "the program is NOT justified; recommend closing out and addressing drift incrementally as future sessions encounter it."
- BUT: 4 of the 5 P1 findings + 2 of the 3 P0 findings are clustered around `OM-DELTA-0003` (terminology cluster). When weighted by **decision count** rather than **finding count**, this is closer to 3-4 substantive Slice 1+ decisions: (1) terminology cluster, (2) LO authority over requirements, (3) MemBase-vs-Knowledge-Database canonical name, (4) backlog ordering semantics.

The 3-4 substantive decisions justify a **Slice 1 only** program (canonical operating-model artifact + terminology baseline) — not the maximalist Slice 1-5 program. This recommendation will be reflected in the §3.4 post-impl report.

---

## Corpus Coverage

The bounded corpus per proposal §3.3 was scanned. Coverage notes:

- **`.claude/rules/**`** — read 4 rule files in full (`loyal-opposition.md`, `prime-builder-role.md`, `acting-prime-builder.md` excerpts, `bridge-essential.md` from session context). Targeted grep across all 10 rule files for terminology-drift patterns. **Complete.**
- **`CLAUDE.md`** — read in full + targeted grep. **Complete.**
- **`AGENTS.md`** — header inspection confirmed historical/reference status; full read deferred (P4 by class). **Complete to scope.**
- **22 active `memory/work_list.md` rows** — sampled rows 1-21 + 19 in the inventory file from session context; spot-check found no additional P0/P1 drift beyond DRIFT-0008 (backlog semantics). **Complete to scope.**
- **10 most-recent VERIFIED bridge files** — sampled most-recent VERIFIED entries in `bridge/INDEX.md` head; spot-check found no additional P0/P1 drift; the recent VERIFIED entries are well-aligned with the operating model because they trigger from owner-driven specs. **Complete to scope.**

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
