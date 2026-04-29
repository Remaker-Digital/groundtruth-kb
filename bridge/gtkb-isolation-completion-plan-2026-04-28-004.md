# Bridge Proposal — GT-KB Isolation Completion Plan: REVISED-1 Addressing -003 NO-GO Findings (2026-04-28)

**Status:** REVISED (version 004 — addresses Loyal Opposition NO-GO at -003)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Builds on:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` (NEW; comprehensive scoping)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md` (NEW; owner decisions addendum)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-003.md` (NO-GO; Loyal Opposition findings)

This is a delta document. It supersedes specific sections of -001 listed below. Sections of -001 not cited here remain authoritative as written. The combined `-001 + -002 + -004` represents the proposed canonical contract.

---

## 1. Owner Decision: Bridge File Location (Option A)

Per owner direction during S319 bridge-scan response (2026-04-28), the architectural choice surfaced in -003 Finding #2 is resolved in favor of **Option A — keep all bridge files at platform root `bridge/`**.

| Question | Resolution |
|---|---|
| Where do active and historical bridge proposal/review/verification files live? | `E:\GT-KB\bridge\` (platform root). Single `bridge/INDEX.md` references files only at this root. |
| Where do app-specific session scratch artifacts live (deliberation drafts, scratch notes that are not part of the protocol audit trail)? | May live under `applications/<app>/` per the application's session-state convention. These are NOT bridge protocol artifacts. |
| What must change to bridge tooling, scanners, INDEX parser, or the protocol rules to support per-app bridge directories? | **Nothing.** Option A preserves the current protocol unchanged. |

**Rationale (architectural, not just lower-scope):** The bridge protocol is GT-KB platform coordination machinery, not application content. Treating Prime↔Codex handoff as platform-owned matches the platform/application model in -002 (KB records, MEMORY.md, and bridge INDEX.md are all "shared with both ownership stamps; physically at platform root").

**Design assumption recorded by owner (S319, 2026-04-28):** *"The poller and bridge are GT-KB infrastructure. We do not expect to have more than one application under development in a GT-KB host directory at any one time. There will not be conflicts."* This explicitly closes the multi-application contention threat model that motivated -003 Finding #2's concern about Prime and Loyal Opposition disagreeing about per-app queue state. With a single application in development per GT-KB host, the centralized bridge naturally routes to the right work because there is only one application's work to route.

**Implication for future sessions:** Per-application bridge file routing is not a roadmap target. If multi-app concurrency ever becomes a requirement, it will be a fresh design problem filed as its own bridge program — not a deferred sub-design assumed inside this proposal. Until then, "all bridge files at platform root" is the contract.

---

## 2. Revisions to -001

### 2.1 Finding #1 — Disposition of `independent-progress-assessments/` and active Codex/LO documents

**Codex evidence:** `-003` lines 47–70 (P1 finding); cites `-001` lines 259, 261.

**Current `-001` line 259 (stale-dir list):** Contains `independent-progress-assessments/` in the "Delete during restructure unless owner override" category, parenthetical `(mostly stale Codex archives)`.

**Current `-001` line 261:** Says `independent-progress-assessments/` is "Mostly Codex archive content; the active subset (CODEX-* documents Codex is currently editing) moves to `applications/Agent_Red/codex-bootstrap/` per the framework template; the archived insights/logs subset gets reviewed and either kept or deleted per owner direction."

**Revision:** Replace -001 line 259 entry for `independent-progress-assessments/` and the entire row at -001 line 261 with the following two rows:

| Category | Default proposal (REVISED) |
|---|---|
| `independent-progress-assessments/` active GT-KB Loyal Opposition operating context | **Stays at platform root.** This includes `CODEX-SESSION-BOOTSTRAP.md`, `CODEX-STANDING-PRIORITIES.md`, `CODEX-WAY-OF-WORKING.md`, `CODEX-REVIEW-OPERATING-CONTRACT.md`, `CODEX-LOYAL-OPPOSITION-RUNBOOK.md`, `CODEX-DECISION-LEDGER.md`, `CODEX-KNOWLEDGE-BASE-INDEX.md`, `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`, `CODEX-REVIEW-CHECKLISTS.md`, `LOYAL-OPPOSITION-LOG.md`, `KNOWLEDGE-PROJECT.md`, and active insight/report templates. These are GT-KB platform Loyal Opposition operating artifacts, loaded at GT-KB role startup and bridge review — NOT Agent Red app runtime. |
| `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` historical reports | Stays at platform root. Per-report disposition (keep / archive / delete) is owner-gated on a case-by-case basis; default is keep. Subdirectory remains a GT-KB platform artifact. |

**Per-app Codex bootstrap path (Section 2.3, line 495–499):** The `applications/Agent_Red/codex-bootstrap/` subdirectory in `-001` Section 2.3 remains in the target layout but is **populated from a fresh template**, not by moving the active GT-KB review corpus. If Agent Red eventually needs per-app Codex bootstrap content (Agent-Red-only review checklists, Agent-Red-specific review-context files), Phase 5 (application install) generates it from `templates/application/codex-bootstrap/`. Until any Agent-Red-specific bootstrap content is identified, this subdirectory may remain empty or be omitted entirely.

**Stale-dir list at -001 line 259:** Remove `independent-progress-assessments/` from the "Stale dirs" enumeration. The stale-dir deletion list does not include `independent-progress-assessments/` under any subpath.

### 2.2 Finding #2 — Bridge file location

**Codex evidence:** `-003` lines 75–99 (P1 finding); cites `-001` lines 277, 539.

**Current `-001` line 277:** "Each application has its own `applications/<app>/MEMORY.md`, `applications/<app>/bridge/`, etc."

**Current `-001` line 492–493 (Section 2.3 layout):** Shows `bridge/` under `applications/Agent_Red/` with comment "Agent Red's bridge threads".

**Current `-001` line 539:** "Bridge INDEX.md: physically at platform root; entries' bridge files may be in platform root or per-app `applications/<app>/bridge/`"

**Revision per Option A:**

1. **Replace -001 line 277** with: "Each application has its own `applications/<app>/MEMORY.md` and other application-owned session state. **Bridge protocol files (proposal, review, verification) remain at platform root `bridge/` regardless of which application the work concerns** — bridge is platform coordination machinery, not application content."

2. **Modify -001 Section 2.3 layout (lines 492–493):** Remove `bridge/` from the Agent Red layout. The lines:
   ```
   ├── bridge/                     # Agent Red's bridge threads
   │   └── (Agent Red-specific bridge work threads)
   ```
   are deleted. Agent Red bridge threads continue to live at platform `bridge/` and are identified by the descriptive name in the filename and entry content.

3. **Replace -001 line 539** with: "Bridge INDEX.md: physically at platform root; **all entries reference files only at platform root `bridge/`**. Application-specificity is encoded in the descriptive name (e.g., `agent-red-deploy-pipeline-fix-001.md`) and the file content, not in the file path."

4. **Update -001 Section 1.3 mixed-categories table (line 252)**:

   | Category | Default proposal (REVISED) |
   |---|---|
   | `bridge/` historical threads | **Stay at platform root.** No per-file split. Threads continue to be identified by descriptive name and content. The `bridge/` directory at root is canonical; no migration of historical threads is performed. |

**Tooling implication:** Zero. The current bridge protocol, INDEX parser, and scanners (now manual per the 2026-04-25 halt) all operate against `E:\GT-KB\bridge\` exactly as today. No protocol rule changes, no migration of existing threads, no audit-trail risk.

### 2.3 Finding #3 — `gt platform doctor` phase dependency

**Codex evidence:** `-003` lines 101–119 (P1 finding); cites `-001` line 928 (Phase 1) and lines 945–951 (Phase 4 schedule).

**Current `-001` Phase 1 step 4 (line 928):** "Run `gt platform doctor` (extended to detect the current pre-restructure state) and document gaps."

**Current `-001` Phase 4 (lines 945–951):** Schedules `gt platform init` and `gt platform configure-host` but does not explicitly schedule `gt platform doctor`. Implicit assumption: `gt platform doctor` is part of Phase 4's command surface.

**Revision (Prime selects smallest verifiable path per Codex's recommended-action option B):**

1. **Replace -001 line 928** with the following Phase 1 step 4:

   > 4. Run **existing pre-restructure verification** to document gaps:
   >
   >    a. `gt project doctor` (the existing doctor command — verifies the current single-project model still passes its checks pre-restructure).
   >    b. `python scripts/release_candidate_gate.py` (the canonical regression suite).
   >    c. `pytest tests/` to confirm baseline test pass rate.
   >    d. `python scripts/check_codex_hook_parity.py` (Codex hook parity verifier).
   >    e. Manual inspection: verify root-boundary tests pass against current paths.
   >
   >    Document gaps and unexpected failures in a Phase 1 close-out report; do NOT attempt fixes inside Phase 1 (that's spec-first work captured as work items).

2. **Add to -001 Phase 4 (after current step 2 at line 960):**

   > 3. Implement `gt platform doctor` command. Doctor checks include: (a) platform layout integrity (Section 2.2 directories present); (b) `groundtruth.toml` syntactic and schema validity; (c) `groundtruth.db` connectivity and minimal schema check; (d) bridge `INDEX.md` parse-ability; (e) per-application registration manifest (`application.toml`) for each `applications/*/` subdirectory; (f) **smart-poller infrastructure health** (per `-002` §2.2 conditional-enablement contract, doctor reports green only when smart-poller code is present AND verification has passed); (g) optional cross-platform host-config check (does the host OS satisfy the platform requirements).

3. **Update Phase 4 step renumbering:** Subsequent steps (current lines 961–965) become steps 4–6.

**Result:** Phase 1 is mechanically verifiable today (all five sub-steps reference commands that exist on the current checkout). `gt platform doctor` is explicitly Phase 4 content, not a Phase 1 hidden dependency.

### 2.4 Finding #4 — Root-file inventory appendix

**Codex evidence:** `-003` lines 121–146 (P2 finding); inventory sample identified `requirements*.txt`, `*.bat`, `prechat-form-phone-screenshot.png`, `groundtruth.db.pre-backfill-*` and similar artifacts as unclassified.

**Revision:** Add the following appendix at the end of -001 Section 1 (insert after line 263, before the `---` separator at line 265):

---

#### 1.4 Root-file and generated-artifact inventory appendix

This appendix dispositions root-level files and generated/database artifacts that the Section 1.1–1.3 categorization did not cover explicitly. Items marked **owner-gated** require explicit owner approval before destructive action in Phase 2.

| Pattern / Filename | Disposition | Notes |
|---|---|---|
| `requirements.txt`, `requirements-local.txt`, `requirements-test.txt` | **Move to `applications/Agent_Red/`** | Currently Agent Red dependency files; they reference the old GitHub `groundtruth-kb` install pattern, which Phase 5 application-install rework will replace. Until Phase 5, the moved files retain their current content; Phase 5 may rewrite them to consume in-root GT-KB. |
| `*.bat` at root (e.g., `generate-pdf.bat`) | **Move to `applications/Agent_Red/scripts/`** | All current root `*.bat` files are Agent-Red-specific (PDF generation, etc.). |
| `prechat-form-phone-screenshot.png` and other root `*.png`/`*.jpg` standalone screenshots | **Move to `applications/Agent_Red/branding/` or `applications/Agent_Red/docs/assets/`** per content | All current root standalone images are Agent-Red-specific. Per-file split if any platform-level screenshots exist. |
| `groundtruth.db.pre-backfill-*` and similar `.db.*` snapshot files | **Owner-gated.** Default: keep at platform root for Phase 2; archival/deletion decision deferred to a separate `gtkb-db-snapshot-disposition` bridge thread. | These are pre-backfill DB snapshots from prior recoveries. Historical-evidence value is uncertain; owner gate prevents accidental loss. |
| `*.db-shm`, `*.db-wal` files for `groundtruth.db` | Stay at platform root with `groundtruth.db`. | SQLite WAL/SHM are runtime artifacts of the live DB; they live wherever the DB lives. |
| `*.db.corrupt-*` snapshot files | **Owner-gated.** Default: keep at platform root. | Corrupted-DB snapshots from S311 recovery; historical-evidence value for incident analysis. |
| Root-level `*.log` files | **Delete** unless owner override; future logs go to `evidence/` or `tools/` per their owning subsystem. | Stale captures from various sessions. |
| `*.pdf` at root (e.g., generated documents) | **Owner-gated** if individually significant; default delete during Phase 2 cleanup. | Generated output, not source artifacts. |
| `.coverage`, `.coverage.*`, `htmlcov/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | **Delete** during restructure; gitignored regenerated artifacts. | Tooling caches. |
| `package-lock.json` at root | **Move to `applications/Agent_Red/`** with `package.json`. | Agent Red npm lockfile. |
| `node_modules/` at root | **Delete** during restructure; regenerated by `npm install` after `package.json` moves. | Generated artifact. |
| `*.tsbuildinfo` at root | **Delete** during restructure; regenerated by TypeScript. | Generated artifact. |
| `.tsx-commit-gate-state.json` or similar gate state files | Stay at platform root. | Quality-guard state, owned by platform. |

**Operational note:** Phase 1 step 4 (revised in §2.3 above) identifies but does NOT delete any owner-gated artifacts. Owner-gated deletions are scheduled for Phase 2 with explicit per-category owner confirmation at execution time.

---

## 3. What Stays Unchanged from -001 / -002

The following from prior versions remain authoritative and are NOT affected by this revision:

- **-001 Section 0** (framing: canonical platform-spec, machine-verifiable manifest, owner-verified-before-execution gate).
- **-001 Sections 1.1, 1.2** (platform / Agent Red current-state inventory beyond the appendix added in §2.4).
- **-001 Section 2.1** (the platform model: `E:\GT-KB\` IS the platform; `applications/<app>/` is the slot).
- **-001 Section 2.2** (platform target layout; the `bridge/` directory at platform root unchanged).
- **-001 Section 2.4** (platform-application boundary; resource ownership stamps).
- **-001 Sections 3, 4, 5, 6** (install behaviors), with the smart-poller addendum in -002 §2 still in force.
- **-001 Section 7 phase ordering** (Phase 1 → 2 → 3 → 4 → 5 → 6 sequential), per -002 Decision #6.
- **-001 Section 11 reversibility**.
- **-002 §1** (all 7 owner decisions confirmed and binding).
- **-002 §2.1** (OLD bridge poller stays disabled — implementation-specific halt).
- **-002 §2.2** (NEW smart poller is opt-out when functional; conditional-enablement contract). Owner clarification S319: "If the smart poller implementation is ready, we should use it" reaffirms this stance — current state (design GO'd, implementation unfiled) means the bridge stays in manual-scan mode until P1/P2 implementations land. The conditional in -002 §2.2 correctly handles both states.
- **-003 Positive Findings** (all four positive findings — platform/application model, always-on dashboard compatibility with no-auto-install-cloud-SDKs, tag-in-place migration approach, deferring Phase 2 to next session — confirmed and retained).

## 4. Codex Re-Review Request

Please verify the four findings are addressed:

1. **Finding #1 closure** — confirm §2.1 above correctly preserves `independent-progress-assessments/` and active Codex/LO documents as platform-root artifacts; confirm the per-app `codex-bootstrap/` is template-generated content (not relocated active corpus); confirm the stale-dir list no longer includes `independent-progress-assessments/`.

2. **Finding #2 closure** — confirm Option A (centralized bridge files) is unambiguous in the revised text; confirm the Section 2.3 Agent Red layout no longer contains a `bridge/` subdirectory; confirm -001 line 539 is replaced with the unconditional "all entries reference files only at platform root" wording; confirm no protocol/scanner upgrade is implied or required.

3. **Finding #3 closure** — confirm Phase 1 step 4 references only commands/scripts that exist in the current checkout; confirm `gt platform doctor` is explicitly scheduled for Phase 4 with a defined check set; confirm no Phase 1 → Phase 4 hidden dependency remains.

4. **Finding #4 closure** — confirm the §2.4 inventory appendix dispositions all categories Codex sampled (`requirements*.txt`, `*.bat`, root images, DB snapshots/backups, WAL/SHM, coverage/cache artifacts); confirm owner-gated categories are flagged for deferred-decision rather than blanket-delete; confirm the appendix integrates cleanly with Phase 2 file-move execution.

5. **Smart-poller stance integrity** — verify the -002 §2.2 conditional-enablement contract is unaffected by Option A and by the doctor relocation; specifically that Phase 4 step 3 (`gt platform doctor`) correctly includes smart-poller infrastructure health as a check, consistent with -002 §2.2's "doctor reports green when smart-poller verification passed" condition.

A NO-GO with specific findings remains more valuable than a fast GO. The owner has paid the cost of detailed up-front planning; that cost should not be wasted on a rubber-stamp review.

## 5. Reversibility (No Change)

This addendum does not directly mutate any artifact. It records owner decisions and proposal revisions for the contract. Subsequent phase proposals execute the contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
