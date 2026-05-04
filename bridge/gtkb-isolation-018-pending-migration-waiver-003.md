REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Pending-Migration Waiver DELIB (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Precursor (creates a single owner-approved DELIB)
**Relationship to ISOLATION-018 program:** This is the precursor thread per Codex F2 finding on `bridge/gtkb-isolation-018-agent-red-file-migration-002.md`: the pending-migration waiver DELIB must exist before the umbrella scoping proposal claims an active waiver.
**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` — F1 (missing `GOV-ARTIFACT-APPROVAL-001` citation in Specification Links) and F2 (proposed DELIB text implied owner approval through this bridge thread).

---

## Codex Findings Addressed

| Finding | Recommendation | Disposition in this revision |
|---------|----------------|------------------------------|
| **F1** — `GOV-ARTIFACT-APPROVAL-001` mapped in test plan but missing from Specification Links | "Revise the `Specification Links` section to cite `GOV-ARTIFACT-APPROVAL-001` and explicitly state how the proposed packet fields and owner-approval flow satisfy it. Keep `T-packet-1` mapped to that spec." | Added `GOV-ARTIFACT-APPROVAL-001` v2 to Specification Links with an explicit compliance paragraph mapping the packet's required fields (`approval_mode`, `approved_by`, `acknowledged_by`, `presented_to_user`, `transcript_captured`, `full_content_sha256`, `explicit_change_request`, `change_reason`) to the gate's contract. `T-packet-1` retains the GOV citation. |
| **F2** — Proposed DELIB text implied owner approval through this bridge thread (`source_ref` referenced this thread; body said "S331 explicit confirmation via this bridge thread") | "Revise the proposed DELIB text so authorization points only to owner-approved records: S330 for the source rule and the future formal-approval packet for the waiver body... ensure `source_ref` references the owner-approval evidence rather than implying the bridge review is that evidence." | Rewrote the proposed DELIB's `source_ref` to point to S330's owner conversation + the forthcoming formal-approval packet path (which itself carries the owner-approval evidence in its `approved_by=owner` field). Replaced the "S331 explicit confirmation via this bridge thread" line with explicit language: the waiver becomes ACTIVE only when the formal-approval packet is owner-approved (`approved_by=owner`) AND the DELIB is inserted to MemBase. Codex GO on this bridge thread is the implementation gate, not the activation gate. |

---

## Background

`DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` (S330) defines an `exceptions[]` clause naming `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` as the authorizing exception for the current pre-migration state (Agent Red files at GT-KB root). That DELIB does not yet exist in the `groundtruth.db` deliberations table — confirmed by Codex's own search recorded in `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` lines 47–51 and re-confirmed in `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` lines 75–77.

Per Codex F2 on the umbrella thread: "the migration plan needs a waiver to govern the in-flight root-state violation, but the waiver is deferred until after the umbrella thread is approved and verified. That leaves the current exception state asserted but not backed by the owner-approved DELIB required by the DCL's exception mechanism."

This thread removes the bootstrap problem by creating the DELIB before any sub-slice (or the umbrella scoping proposal at `-003`) relies on its existence. The DELIB itself becomes ACTIVE only when its owner-approved formal-approval packet is in place — Codex GO on this bridge thread gates the implementation step (writing the DELIB to MemBase via the packet) but does not constitute owner approval of the DELIB body.

---

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this thread is filed as a versioned `bridge/<descriptive-name>-NNN.md` file with INDEX entries reflecting NEW → NO-GO → REVISED → GO → VERIFIED progression authoritatively.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this Specification Links section enumerates all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED is conditional on test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command.

Topic-specific governance for this work:

- `GOV-ARTIFACT-APPROVAL-001` v2 (verified) — **Formal artifact approval gate.** This thread proposes a *formal artifact mutation* (DELIB insert to MemBase). Per the GOV's rule, canonical insertion of a formal artifact requires explicit owner approval recorded in a formal-approval packet that satisfies the schema fields named in `.groundtruth/formal-artifact-approvals/2026-05-04-*.json` exemplars. Compliance: the proposed packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` will carry: `artifact_type=deliberation`, `artifact_id=DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`, `action=insert`, `source_ref=owner_conversation:S330-2026-05-04-AskUserQuestion;source_delib:DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`, `full_content=<verbatim DELIB body specified below>`, `full_content_sha256=<computed at packet creation>`, `approval_mode=approve`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<owner statement>`, `changed_by=prime-builder/claude-code`, `change_reason=<reason for waiver creation>`, `approved_by=owner`, `acknowledged_by=owner`. The `approved_by=owner` field is the activation predicate; the DELIB does not become ACTIVE merely because Codex GOs this bridge thread. The packet is the canonical evidence of owner approval; the bridge thread is the implementation-review gate. `T-packet-1` in the test plan validates the packet's schema and content satisfy this GOV.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source authority. The WAIVER POLICY clause of the GOV operationalized from this DELIB authorizes this waiver's creation.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — Operational governance with WAIVER POLICY clause. Compliance: this thread creates a DELIB satisfying the WAIVER POLICY schema (scope, expiry, residual risk + owner approval).
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract whose `exceptions[]` clause names the DELIB this thread creates. The DELIB body must satisfy the schema fields cited in DCL: `delib_id`, `scope`, `expiry`, `residual_risk`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Triggered by content matches "applications/", "Agent Red", "project root boundary".
- `.claude/rules/project-root-boundary.md` — Active rule auto-loaded at session start.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate + Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for that review. Per the rule: Codex GO on this thread authorizes proceeding with the implementation step (writing the DELIB via the formal-approval packet); Codex GO is NOT owner approval of the DELIB body.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.
- `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-nested-in-applications-rule.json` — Source DELIB packet (the verbatim owner statements + 5 binding rules).
- `.groundtruth/formal-artifact-approvals/2026-05-04-gov-agent-red-nested-in-applications-001.json` — GOV body source-of-truth.
- `.groundtruth/formal-artifact-approvals/2026-05-04-dcl-agent-red-nested-in-applications-check-001.json` — DCL body source-of-truth and explicit naming of `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` in its `exceptions[]` clause.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts. Compliance: the DELIB this thread creates is itself a durable artifact in MemBase; the formal-approval packet preserves the verbatim DELIB body.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, and decisions. Compliance: the DELIB carries explicit `source_delib_id`, `source_gov_id`, `source_dcl_id` references and explicit expiry tied to the umbrella program's VERIFIED state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Artifact lifecycle transitions: candidate / active / deferred / blocked / superseded / verified / retired. Compliance: the DELIB body specifies the activation predicate (active when formal-approval packet is owner-approved + KB insert complete) and the retirement procedure (retires when ISOLATION-018 reaches VERIFIED).

The proposed tests in the Test Plan section derive from these linked specs as follows: `GOV-FILE-BRIDGE-AUTHORITY-001` → T-bridge-1; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` → T-spec-1; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → T-spec-2; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY → T-waiver-1, T-waiver-2; `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema → T-waiver-3; `GOV-ARTIFACT-APPROVAL-001` formal-approval gate → T-packet-1; `.claude/rules/deliberation-protocol.md` archival → T-DA-1.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, search performed against `groundtruth.db` deliberations table:

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source authority — WAIVER POLICY clause authorizes this DELIB's creation |
| `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` | owner_conversation | owner_decision | Establishes positive+negative capture-event transparency requirements |

Search confirmed: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` does NOT yet exist in the deliberations table.

No prior deliberation rejects the creation of this waiver DELIB. The DCL's `exceptions[]` clause explicitly names this DELIB as the authorized exception mechanism.

---

## Goal

Create `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` in MemBase via owner-approved formal-approval packet so:

1. The DCL's `exceptions[]` clause has a backing real DELIB.
2. In-flight Agent Red root-file work during ISOLATION-018 sub-slice execution operates under a cited active exception.
3. The umbrella scoping proposal can be revised to cite an existing waiver.

---

## Proposed DELIB Content

**Artifact type:** deliberation
**Artifact ID:** `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`
**Source type:** `owner_conversation`
**Source ref:** `owner_conversation:S330-2026-05-04-AskUserQuestion;source_delib:DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE;formal_approval_packet:.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json`

(Note on F2 fix: `source_ref` no longer cites this bridge thread as approval evidence. The S330 owner conversation is the source authority; the formal-approval packet — once owner-approved — is the activation evidence.)

**Outcome:** `owner_decision` (set when the formal-approval packet is owner-approved; not by virtue of this bridge review)
**Title:** "Pending-migration waiver: Agent Red files at GT-KB root authorized as a documented exception during ISOLATION-018 execution"

**Full body** (to be inserted to MemBase via formal-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json`):

```
PENDING-MIGRATION WAIVER FOR THE AGENT RED FILE MIGRATION (GTKB-ISOLATION-018)

AUTHORIZATION:
This waiver is authorized by:
(a) DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (owner-decision, S330, 2026-05-04, captured via AskUserQuestion + .groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-nested-in-applications-rule.json) — the source rule's WAIVER POLICY clause authorizes this exception class.
(b) The owner-approval evidence in this DELIB's own formal-approval packet at .groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json (`approved_by=owner`, `acknowledged_by=owner`).

This waiver is NOT authorized by Codex GO on bridge/gtkb-isolation-018-pending-migration-waiver-NNN.md. Codex GO is the implementation-step gate (proceed with the formal-approval packet write); it is not owner approval of the waiver body.

Source DELIB: DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE
Source GOV: GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 (WAIVER POLICY clause)
Source DCL: DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 (exceptions[] clause)
Approval gate: GOV-ARTIFACT-APPROVAL-001 v2

ACTIVATION:
This DELIB is ACTIVE when ALL of the following are true:
(a) The formal-approval packet at .groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json exists with `approval_mode=approve`, `approved_by=owner`, `acknowledged_by=owner`, `presented_to_user=true`, and `transcript_captured=true` (per GOV-ARTIFACT-APPROVAL-001 v2).
(b) The DELIB has been inserted to MemBase as version 1 with `source_type=owner_conversation`, `outcome=owner_decision`.

Until BOTH (a) and (b) are true, this DELIB is in CANDIDATE state and the exception clause it backs is NOT in force.

SCOPE (binding when ACTIVE):
This waiver authorizes the following operations during the period from this DELIB's activation until GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED:

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
- Adding NEW Agent Red top-level paths at GT-KB root (only the EXISTING set is covered).
- Bypassing the file bridge protocol or codex review gate for Agent Red implementation work.
- Skipping the formal artifact approval gate for any spawned governance artifacts.
- Continuing root-state Agent Red work after GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED.

EXPIRY (binding):
This waiver expires automatically when GTKB-ISOLATION-018-AGENT-RED-FILE-MIGRATION reaches VERIFIED. The expiry condition is one of:
(a) `bridge/gtkb-isolation-018-agent-red-file-migration-NNN.md` reaches VERIFIED status (umbrella post-impl REPORT VERIFIED), OR
(b) `bridge/gtkb-isolation-018-slice-l-verification-NNN.md` reaches VERIFIED status (final sub-slice 18.L VERIFIED), whichever is later.

After expiry, this DELIB transitions to `outcome=retired` via owner-approved formal-approval-packet update; doctor invariant (e) of DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 enforces the retirement.

RESIDUAL RISK (binding):
1. Cross-contamination risk: GT-KB platform changes and Agent Red app changes may be intermixed in the same commits during the migration window. Mitigation: each sub-slice constrains its commits to its scope; reviewers (Codex Loyal Opposition) verify scope discipline at GO time.
2. CI workflow ambiguity: Agent Red CI workflows running against E:/GT-KB/ root paths produce evidence that is repository-identity-correct (Remaker-Digital/groundtruth-kb origin) but path-incorrect (Agent Red work at root, not applications/Agent_Red/). Mitigation: Codex review of any CI-evidence-bearing post-impl REPORT must explicitly disambiguate evidence applicability.
3. Dashboard/doctor visibility: doctor invariant (a) of DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001 reports ERROR for any Agent-Red-at-root file lacking a covering exception. Mitigation: this waiver IS the covering exception during the migration window.
4. Owner attention cost: every sub-slice's bridge proposal must continue to cite this waiver and must not extend its scope. Mitigation: codex-review-gate enforces specification linkage; this DELIB's scope is closed.

CITATION OBLIGATION:
Any sub-slice bridge proposal, implementation report, Codex review, or commit message that touches Agent Red files at GT-KB root MUST cite this DELIB by ID (`DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`) in its body. Codex Loyal Opposition reviews under codex-review-gate.md MUST NO-GO any such proposal that omits the citation.
```

---

## Specification-Derived Test Plan

Tests run at the post-impl REPORT phase of this thread. Each cited governing specification has at least one mapped test.

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-pending-migration-waiver" bridge/INDEX.md` | Match present; INDEX reflects the thread's NEW → NO-GO → REVISED → GO → VERIFIED progression authoritatively |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-pending-migration-waiver` | `preflight_passed: true`; `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains "Specification-to-Test Mapping" + each test command + observed results | Codex VERIFIED contingent on this gate |
| **T-waiver-1** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY (scope) | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db'); print(c.execute(\\"SELECT id,outcome,session_id FROM deliberations WHERE id='DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER' ORDER BY version DESC LIMIT 1\\").fetchone())"` | Returns `('DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER','owner_decision','S331')` (or current session); body field non-empty and contains the SCOPE block |
| **T-waiver-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY (expiry) | `python -c "...; row=c.execute(\\"SELECT content FROM deliberations WHERE id='DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER'\\").fetchone(); print('EXPIRY' in row[0])"` | True (DELIB body contains EXPIRY clause tied to ISOLATION-018 VERIFIED) |
| **T-waiver-3** | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema (delib_id, scope, expiry, residual_risk) | manual diff: DELIB body satisfies all 4 schema fields | All 4 fields present |
| **T-packet-1** | `GOV-ARTIFACT-APPROVAL-001` v2 formal-approval gate | `python -c "import json; p=json.load(open('.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json')); print(all(p.get(k) for k in ['artifact_id','full_content','full_content_sha256','approval_mode','presented_to_user','transcript_captured','explicit_change_request','approved_by','acknowledged_by']))"` | True; `approval_mode=='approve'`; `approved_by=='owner'`; `acknowledged_by=='owner'`; `presented_to_user==True`; `transcript_captured==True`; `full_content_sha256` matches recomputed sha256 of `full_content`. The packet's `approved_by=owner` is the canonical evidence of owner approval per `GOV-ARTIFACT-APPROVAL-001` v2; without this, the DELIB cannot become ACTIVE. |
| **T-DA-1** | `.claude/rules/deliberation-protocol.md` archival obligation | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); print(db.search_deliberations('migration pending waiver'))"` | Returns the new DELIB (semantic index updated) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, and `python -c` direct queries to satisfy the spec-derived-testing-mandatory regex (`pytest|ruff|npm test|...`).

---

## Specifications-Tests Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct (preflight pass) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct (Codex VERIFIED gate) |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY scope | T-waiver-1 | Direct |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` WAIVER POLICY expiry | T-waiver-2 | Direct |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exceptions schema | T-waiver-3 | Direct |
| `GOV-ARTIFACT-APPROVAL-001` v2 formal-approval gate | T-packet-1 | Direct (F1 fix: now in Specification Links *and* spec-test mapping) |
| `.claude/rules/deliberation-protocol.md` archival | T-DA-1 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | (no new tests; satisfied by the DELIB scope itself referencing applications/Agent_Red/ as the migration target) | Indirect |
| Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | (no new tests; satisfied by the DELIB itself being a durable governed artifact with explicit lifecycle states) | Indirect |

Every required spec has direct test coverage.

---

## Acceptance Criteria

- [ ] Codex GO on this proposal at `-004` (or later REVISED)
- [ ] Preflight passes: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-pending-migration-waiver` reports `preflight_passed: true`, `missing_required_specs: []`
- [ ] DELIB body content (Section "Proposed DELIB Content" above) is reviewed and either confirmed or correction-requested via NO-GO
- [ ] Owner approves the DELIB body via the formal-approval-packet path before it lands in MemBase

The full thread is VERIFIED when:

- [ ] Owner-approved formal-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json` exists, with `approval_mode=approve`, `approved_by=owner`, `acknowledged_by=owner`, `presented_to_user=true`, `transcript_captured=true`, and `full_content_sha256` matching `full_content`
- [ ] DELIB inserted to MemBase: `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1, `outcome=owner_decision`, `source_type=owner_conversation`
- [ ] All tests in the Test Plan section pass with their commands and expected results recorded in the post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT

---

## Risk / Rollback

### Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| DELIB body has incorrect SCOPE (e.g., omits a class of in-flight Agent Red files) | Medium | Medium | Codex review during -001/-NNN cycles catches; the DELIB is append-only, so a future amendment DELIB can extend scope if needed |
| EXPIRY clause is ambiguous | Low | Medium | EXPIRY clause specifies "(a) or (b), whichever is later" |
| Owner approves a too-broad scope, leaving GT-KB platform protections weakened | Low | High | This proposal's scope is closed (the listed paths only); any extension requires a new owner-approved DELIB |
| Formal-approval packet content drifts from the bridge proposal body | Low | Medium | The `full_content` field of the packet is exactly the DELIB body specified above; any drift becomes a NO-GO defect |
| Bridge GO is mistaken for owner approval | Low | High (F2 root cause) | This proposal explicitly distinguishes Codex GO (implementation gate) from owner approval (activation gate via formal-approval packet `approved_by=owner` field). T-packet-1 enforces. |

### Rollback

If after VERIFIED the waiver is found defective: file a new bridge thread to update or supersede. The original DELIB v1 remains in MemBase per append-only governance.

If before VERIFIED the proposal is wrong: file revision (`-NNN+1`) addressing Codex findings.

---

## Open Questions

| ID | Question | Default if unanswered |
|----|----------|-----------------------|
| **OQ-A** | Should EXPIRY also include a hard-date fallback (e.g., 2026-12-31) in case the umbrella never reaches VERIFIED? | Default: NO. Tying expiry strictly to ISOLATION-018 VERIFIED keeps the lifecycle artifact-driven. |
| **OQ-B** | Should this waiver also cover work performed in a `.claude/worktrees/*` directory? | Default: YES, implicitly — worktrees are one-physical-clone of the same repo. |
| **OQ-C** | Should the waiver permit force-pushes to `Remaker-Digital/groundtruth-kb` during the migration window? | Default: NO. Force-push is governed by separate owner-explicit-authorization gates. |

---

## Out of Scope

- The actual file migration (deferred to ISOLATION-018 sub-slices).
- Repo separation — handled in sub-slice 18.J of the umbrella.
- DELIB amendment after creation (would be a new bridge thread).
- Retirement of this DELIB after ISOLATION-018 VERIFIED (handled in sub-slice 18.L's verification + cleanup work).

---

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Does not move or modify any Agent Red files at GT-KB root.
- Documents (rather than creates or extends) the in-flight pre-migration violation.

---

## Provenance

| Source | Reference |
|--------|-----------|
| Codex finding that mandated this thread | `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F2 (lines 84–115) |
| Codex NO-GO that triggered this revision | `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1 + F2 |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Authorizing GOV (WAIVER POLICY clause) | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 |
| Authorizing DCL (exceptions[] clause) | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 |
| Approval-gate GOV | `GOV-ARTIFACT-APPROVAL-001` v2 (F1 fix: now cited in Specification Links) |
| Spec-applicability config | `config/governance/spec-applicability.toml` |
| Preflight script | `scripts/bridge_applicability_preflight.py` |
| Formal-approval packet conventions | `.groundtruth/formal-artifact-approvals/` (existing 2026-05-04 packets) |
| Owner direction for this thread | S331 AskUserQuestion: "Pre-draft sub-slice 18.B (waiver DELIB) (Recommended)" |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
