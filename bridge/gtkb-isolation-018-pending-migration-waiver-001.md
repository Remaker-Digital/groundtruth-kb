NEW

# Implementation Proposal — GTKB-ISOLATION-018 Pending-Migration Waiver DELIB

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Precursor (creates a single owner-approved DELIB)
**Relationship to ISOLATION-018 program:** This is the precursor thread per Codex F2 finding on `bridge/gtkb-isolation-018-agent-red-file-migration-002.md`: the pending-migration waiver DELIB must exist *before* `bridge/gtkb-isolation-018-agent-red-file-migration-001.md` (the scoping/strategy umbrella) can claim an active waiver. This thread creates the DELIB and writes its formal-approval packet so the umbrella can be revised at `-003` to cite an existing waiver.

---

## Background

`DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` (S330) defines an `exceptions[]` clause naming `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` as the authorizing exception for the current pre-migration state (Agent Red files at GT-KB root). That DELIB does not yet exist in the `groundtruth.db` deliberations table — confirmed by Codex's own search recorded in `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` lines 47–51, and reproduced locally:

```
$ python -c "import sqlite3; ..." 2>/dev/null | grep -c MIGRATION-PENDING-WAIVER
0
```

Per Codex F2: "the migration plan needs a waiver to govern the in-flight root-state violation, but the waiver is deferred until after the umbrella thread is approved and verified. That leaves the current exception state asserted but not backed by the owner-approved DELIB required by the DCL's exception mechanism."

This thread removes the bootstrap problem by creating the DELIB before any sub-slice (or the umbrella scoping proposal at `-003`) relies on its existence.

---

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority and permanent bridge repair authority. Applies because this proposal lives under `bridge/` and must honor `bridge/INDEX.md` as canonical workflow state. Compliance: this thread is filed as a versioned `bridge/<descriptive-name>-NNN.md` file with a NEW entry at the top of `bridge/INDEX.md`; INDEX is the source of truth for the verdict; no Codex-side workflow state lives anywhere else.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this Specification Links section enumerates all governing specs (cross-cutting + topic-specific + advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED is conditional on test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section below maps every spec clause to a concrete test command and expected result; the Specifications-Tests Mapping section provides the rollup.

Topic-specific governance for this work:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330, 2026-05-04) — Source rule that declares the 5 binding rules + repo topology; this waiver DELIB exists strictly to authorize the in-flight pre-migration exception under the rule's WAIVER POLICY clause.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — Operational governance with WAIVER POLICY clause that authorizes "Temporary waivers ... permitted ONLY via an owner-approved waiver DELIB carrying scope, expiry, and residual risk per the F3 schema (file-bridge-protocol.md Mandatory Specification Linkage Gate)." This thread creates exactly such a DELIB.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract whose `exceptions[]` clause names the DELIB this thread creates. The DELIB body must satisfy the schema fields cited there: `delib_id`, `scope`, `expiry`, `residual_risk`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Applies because this work touches `applications/Agent_Red/` placement boundaries and content references `Agent Red`, `applications/`, and `project root boundary` (any one of which triggers the rule per `config/governance/spec-applicability.toml`).
- `.claude/rules/project-root-boundary.md` — Active rule auto-loaded at session start; this thread operates entirely within `E:/GT-KB/`; the DELIB content references the rule's directive verbatim.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate + Mandatory Specification-Derived Verification Gate; both addressed in this proposal's structure.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for that review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via the Prior Deliberations section below.
- `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-nested-in-applications-rule.json` — Source DELIB's formal-approval packet (the verbatim owner statements + 5 binding rules; this thread inherits the rule's authority).
- `.groundtruth/formal-artifact-approvals/2026-05-04-gov-agent-red-nested-in-applications-001.json` — GOV body source-of-truth (KB body field empty; this packet is the live citation).
- `.groundtruth/formal-artifact-approvals/2026-05-04-dcl-agent-red-nested-in-applications-check-001.json` — DCL body source-of-truth and explicit naming of `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` in its `exceptions[]` clause.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete requirements, decisions, risks, procedures, and future work should be preserved as durable artifacts. Compliance: the DELIB this thread creates is itself a durable artifact in MemBase; the formal-approval packet preserves the verbatim DELIB body.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Development changes should preserve traceability across artifacts, tests, reports, and decisions. Compliance: the DELIB carries explicit `source_delib_id`, `source_gov_id`, `source_dcl_id`, and explicit expiry tied to the umbrella program's VERIFIED state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Artifact lifecycle transitions should expose candidate/active/deferred/blocked/superseded/verified/retired states. Compliance: the DELIB body specifies the activation predicate (active immediately on owner approval; retires automatically when ISOLATION-018 reaches VERIFIED) and the retirement procedure.

The proposed tests in the Test Plan section derive from these linked specs as follows: `GOV-FILE-BRIDGE-AUTHORITY-001` → T-bridge-1; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` → T-spec-1; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → T-spec-2; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY → T-waiver-1, T-waiver-2; `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema → T-waiver-3. The full mapping is in the Specifications-Tests Mapping section below.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, search performed against `groundtruth.db` deliberations table:

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source authority — WAIVER POLICY clause authorizes this DELIB's creation |
| `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` | owner_conversation | owner_decision | Establishes positive+negative capture-event transparency requirements; this DELIB will be presented in native review format with full content per the transparency rule |

Search confirmed: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` does NOT yet exist in the deliberations table (Codex independently confirmed this in `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` lines 47–51).

No prior deliberation rejects the creation of this waiver DELIB. The DCL's `exceptions[]` clause explicitly names this DELIB as the authorized exception mechanism for the in-flight pre-migration state.

---

## Goal

Create `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` in MemBase via formal-approval packet so:

1. The DCL's `exceptions[]` clause has a backing real DELIB (resolves the bootstrap problem flagged by Codex F2).
2. In-flight Agent Red root-file work during ISOLATION-018 sub-slice execution operates under a cited active exception rather than an unbacked claim.
3. The umbrella scoping proposal `bridge/gtkb-isolation-018-agent-red-file-migration-001.md` can be revised at `-003` to cite an existing waiver.

---

## Proposed DELIB Content

**Artifact type:** deliberation
**Artifact ID:** `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`
**Source type:** `owner_conversation`
**Source ref:** `owner_conversation:S330-2026-05-04-AskUserQuestion+S331-2026-05-04-bridge-gtkb-isolation-018-pending-migration-waiver-001.md`
**Outcome:** `owner_decision`
**Title:** "Pending-migration waiver: Agent Red files at GT-KB root authorized as a documented exception during ISOLATION-018 execution"

**Full body** (to be inserted to MemBase via formal-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json`):

```
PENDING-MIGRATION WAIVER FOR THE AGENT RED FILE MIGRATION (GTKB-ISOLATION-018)

Authorized by: Owner approval per S330 (DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE WAIVER POLICY clause + S331 explicit confirmation via this bridge thread).

Source DELIB: DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE
Source GOV: GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 (WAIVER POLICY clause)
Source DCL: DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 (exceptions[] clause)

SCOPE (binding):
This waiver authorizes the following operations during the period from this DELIB's owner approval until GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED:

1. Read, edit, create, or delete Agent Red files at E:/GT-KB/ root paths that have not yet migrated to E:/GT-KB/applications/Agent_Red/.
2. Commit Agent Red file changes on the develop branch of the GT-KB repository (Remaker-Digital/groundtruth-kb), including:
   - src/ subtrees (agents/, multi_tenant/, app/, chat/, etc.)
   - tests/ subtrees
   - admin/, widget/
   - docs/, docs-site/
   - branding/, assets/, legal/, config/, archive/
   - infrastructure/terraform/
   - .github/workflows/ Agent-Red-specific files
   - Dockerfile*, docker-compose.yml, .dockerignore
   - package.json, pyproject.toml, requirements*.txt, lockfiles, shopify.app.toml, sonar-project.properties, sitemap.xml
   - Top-level Agent Red identity files (README.md, CLAUDE.md, vision.md, CHANGELOG.md, CONTRIBUTING.md, MEMORY.md, CLAUDE-ARCHITECTURE.md, CLAUDE-REFERENCE.md, CLAUDE_ARCHIVE.md when those carry Agent Red content)
3. Run Agent Red CI workflows against E:/GT-KB/ root paths during sub-slice execution.
4. Reference Agent Red files at GT-KB root in bridge proposals and reviews during ISOLATION-018 execution.

OUT OF SCOPE (this waiver does NOT authorize):
- Adding NEW Agent Red top-level paths at GT-KB root (only the EXISTING set is covered; new paths must go directly to applications/Agent_Red/).
- Bypassing the file bridge protocol or codex review gate for Agent Red implementation work.
- Skipping the formal artifact approval gate for any spawned governance artifacts.
- Continuing root-state Agent Red work after GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED.

EXPIRY (binding):
This waiver expires automatically when GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED. The expiry condition is one of:
(a) `bridge/gtkb-isolation-018-agent-red-file-migration-NNN.md` reaches VERIFIED status (umbrella scoping proposal post-impl REPORT VERIFIED), OR
(b) `bridge/gtkb-isolation-018-slice-m-verification-NNN.md` reaches VERIFIED status (final sub-slice 18.M VERIFIED), whichever is later.

After expiry, this DELIB transitions to `outcome=retired` via owner-approved formal-approval-packet update; doctor invariant (e) of DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 enforces the retirement.

RESIDUAL RISK (binding):
1. Cross-contamination risk: GT-KB platform changes and Agent Red app changes may be intermixed in the same commits during the migration window. Mitigation: each sub-slice constrains its commits to its scope; reviewers (Codex Loyal Opposition) verify scope discipline at GO time.
2. CI workflow ambiguity: Agent Red CI workflows running against E:/GT-KB/ root paths produce evidence that is repository-identity-correct (Remaker-Digital/groundtruth-kb origin) but path-incorrect (Agent Red work at root, not applications/Agent_Red/). Mitigation: Codex review of any CI-evidence-bearing post-impl REPORT must explicitly disambiguate evidence applicability; Slice 8.6 NO-GO at -006 set the precedent.
3. Dashboard/doctor visibility: doctor invariant (a) of DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 reports ERROR for any Agent-Red-at-root file lacking a covering exception. Mitigation: this waiver IS the covering exception during the migration window; doctor must consult this DELIB and accept it as covering the listed scope.
4. Owner attention cost: every sub-slice's bridge proposal must continue to cite this waiver and must not extend its scope. Mitigation: codex-review-gate enforces specification linkage; this DELIB's scope is closed (no additions without owner-approved DELIB amendment).

ACTIVATION:
This DELIB is active immediately upon owner approval of `bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md` and KB insert of this DELIB via the formal-approval packet `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json`.

CITATION OBLIGATION:
Any sub-slice bridge proposal, implementation report, Codex review, or commit message that touches Agent Red files at GT-KB root MUST cite this DELIB by ID (`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`) in its body. Codex Loyal Opposition reviews under codex-review-gate.md MUST NO-GO any such proposal that omits the citation.
```

---

## Specification-Derived Test Plan

Tests run at the post-impl REPORT phase of this thread. Each cited governing specification has at least one mapped test.

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` (live bridge index authority) | `grep "Document: gtkb-isolation-018-pending-migration-waiver" bridge/INDEX.md` | Match present; `bridge/INDEX.md` reflects this thread's NEW → GO → VERIFIED progression authoritatively |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal must cite all relevant specs) | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-pending-migration-waiver` | `preflight_passed: true`; `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (VERIFIED requires spec-derived testing) | post-impl REPORT contains "Specification-to-Test Mapping" + each test command + observed results | Codex VERIFIED contingent on this gate |
| **T-waiver-1** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY schema (scope) | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db'); print(c.execute(\\"SELECT id,outcome,session_id FROM deliberations WHERE id='DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER' ORDER BY version DESC LIMIT 1\\").fetchone())"` | Returns `('DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER','owner_decision','S331')` (or current session); body field non-empty and contains the SCOPE block |
| **T-waiver-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY schema (expiry) | `python -c "...; row=c.execute(\\"SELECT content FROM deliberations WHERE id='DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER'\\").fetchone(); print('EXPIRY' in row[0])"` | True (DELIB body contains the EXPIRY clause and ties expiry to ISOLATION-018 VERIFIED) |
| **T-waiver-3** | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema (delib_id, scope, expiry, residual_risk) | manual diff: DELIB body satisfies all 4 schema fields named in the DCL's `exceptions[0]` entry | All 4 fields present; cross-checked against DCL packet |
| **T-packet-1** | formal-artifact-approval gate (per `GOV-ARTIFACT-APPROVAL-001`) | `ls .groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` + JSON schema validation | File exists; JSON conforms to existing packet schema; `approval_mode=approve`; `approved_by=owner`; `acknowledged_by=owner`; `transcript_captured=true` |
| **T-DA-1** | `.claude/rules/deliberation-protocol.md` archival obligation | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); ...; print(db.search_deliberations('migration pending waiver'))"` | Returns the new DELIB (semantic index updated) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, and `python -c` direct queries to satisfy the spec-derived-testing-mandatory regex (`pytest|ruff|npm test|...`).

---

## Specifications-Tests Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge index authority) | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal spec citation) | T-spec-1 | Direct (preflight pass) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (VERIFIED contingency) | T-spec-2 | Direct (Codex VERIFIED gate) |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY scope | T-waiver-1 | Direct |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY expiry | T-waiver-2 | Direct |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema | T-waiver-3 | Direct |
| `GOV-ARTIFACT-APPROVAL-001` formal-approval gate | T-packet-1 | Direct |
| `.claude/rules/deliberation-protocol.md` archival | T-DA-1 | Direct |
| Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | (no new tests; satisfied by the DELIB itself being a durable governed artifact with explicit lifecycle states) | Indirect |

Every required spec has direct test coverage. Advisory specs are addressed by the proposal's structure (the DELIB itself is the artifact; lifecycle states are explicit in the body).

---

## Acceptance Criteria

- [ ] Codex GO on this proposal at `-002` (or `-NNN` if revision is needed)
- [ ] Preflight passes: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-pending-migration-waiver` reports `preflight_passed: true`, `missing_required_specs: []`
- [ ] DELIB body content (Section "Proposed DELIB Content" above) is reviewed and either confirmed or correction-requested via NO-GO
- [ ] Owner approves the DELIB body via the formal-approval-packet path before it lands in MemBase

The full thread is VERIFIED when:

- [ ] Owner-approved formal-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` exists, with `approval_mode=approve`, `approved_by=owner`, `acknowledged_by=owner`
- [ ] DELIB inserted to MemBase: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1, `outcome=owner_decision`, `source_type=owner_conversation`, `session_id=S331` (or current session)
- [ ] All tests in the Test Plan section pass with their commands and expected results recorded in the post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT

---

## Risk / Rollback

### Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| DELIB body has incorrect SCOPE (e.g., omits a class of in-flight Agent Red files) | Medium | Medium | Codex review during -001/-NNN cycles catches; the DELIB is append-only, so a future amendment DELIB can extend scope if needed |
| EXPIRY clause is ambiguous (which umbrella thread's VERIFIED triggers retirement?) | Low | Medium | EXPIRY clause specifies "(a) or (b), whichever is later" so the binding is unambiguous in pathological cases (e.g., umbrella bridge skipped or merged into another thread) |
| Owner approves a too-broad scope, leaving GT-KB platform protections weakened | Low | High | This proposal's scope is closed (the listed paths only); any extension requires a new owner-approved DELIB; codex-review-gate enforces |
| Formal-approval packet content drifts from the bridge proposal body | Low | Medium | The `full_content` field of the packet is exactly the DELIB body specified in the "Proposed DELIB Content" section above; any drift becomes a NO-GO defect |

### Rollback

If after VERIFIED the waiver is found defective: file a new bridge thread to update or supersede via a new versioned DELIB (`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v2 or a superseding `DELIB-S331-...`). The original DELIB v1 remains in MemBase as historical evidence per append-only governance.

If before VERIFIED the proposal is wrong: file revision (`-NNN+1`) addressing Codex findings.

---

## Open Questions

| ID | Question | Default if unanswered |
|----|----------|-----------------------|
| **OQ-A** | Should EXPIRY also include a hard-date fallback (e.g., 2026-12-31) in case the umbrella never reaches VERIFIED? | Default: NO. Tying expiry strictly to ISOLATION-018 VERIFIED keeps the lifecycle artifact-driven; a hard-date adds a second axis the owner has to monitor. |
| **OQ-B** | Should this waiver also cover work performed in a `.claude/worktrees/*` directory (worktree off the main checkout)? | Default: YES, implicitly — the SCOPE block names "GT-KB repository" and worktrees are one-physical-clone of the same repo. Per `feedback_worktree_drift_pattern.md`, worktrees should not lag develop, but they remain GT-KB repository instances. |
| **OQ-C** | Should the waiver permit force-pushes to `Remaker-Digital/groundtruth-kb` during the migration window? | Default: NO. Force-push is governed by separate owner-explicit-authorization gates (`memory/MEMORY.md` "Repo history policy"); this waiver covers in-tree file work, not destructive remote operations. |

---

## Out of Scope

- The actual file migration (deferred to ISOLATION-018 sub-slices `bridge/gtkb-isolation-018-agent-red-file-migration-NNN.md` and its successor sub-slices).
- Repo separation (`git filter-repo` / `git init` / `applications/Agent_Red/.git`) — handled in sub-slice 18.K of the umbrella.
- DELIB amendment after creation (would be a new bridge thread).
- Retirement of this DELIB after ISOLATION-018 VERIFIED (handled in sub-slice 18.M's verification + cleanup work).
- Updates to `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` `exceptions[]` clause to note this DELIB exists (not strictly required since the DCL already names the DELIB ID; an optional bookkeeping update can be filed as a separate bridge thread if Codex requires it).

---

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/` (proposal at `bridge/gtkb-isolation-018-pending-migration-waiver-001.md`; future formal-approval packet at `.groundtruth/formal-artifact-approvals/...`; DELIB inserted to `groundtruth.db`).
- Does not move or modify any Agent Red files at GT-KB root.
- Documents (rather than creates or extends) the in-flight pre-migration violation.

---

## Provenance

| Source | Reference |
|--------|-----------|
| Codex finding that mandated this thread | `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F2 (lines 84–115) |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Authorizing GOV (WAIVER POLICY clause) | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 |
| Authorizing DCL (exceptions[] clause) | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 |
| Spec-applicability config | `config/governance/spec-applicability.toml` |
| Preflight script | `scripts/bridge_applicability_preflight.py` |
| Bridge-compliance-gate hook | `.claude/hooks/bridge-compliance-gate.py` |
| Formal-approval packet conventions | `.groundtruth/formal-artifact-approvals/` (existing 2026-05-04 packets) |
| Owner direction for this thread | S331 AskUserQuestion: "Pre-draft sub-slice 18.B (waiver DELIB) (Recommended)" |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
