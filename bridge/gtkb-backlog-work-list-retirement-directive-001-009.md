REVISED

# Implementation Proposal — GTKB-BACKLOG-WORK-LIST-RETIREMENT-DIRECTIVE-001 (Slice 0 Scoping, Round 5)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-backlog-work-list-retirement-directive-001`
**NO-GO addressed:** `bridge/gtkb-backlog-work-list-retirement-directive-001-008.md` (F1, F2, F3)
**Supersedes:** `bridge/gtkb-backlog-work-list-retirement-directive-001-007.md`
**Status:** REVISED
**Parent thread:** `gtkb-gov-backlog-source-of-truth-2026-05-02` (Slice 1 VERIFIED at -008; Slices 2-7 actionable per [memory/work_list.md:79](memory/work_list.md:79)).

## Claim

The owner directive of 2026-05-08 says "the conclusion of the migration will be the deletion of the markdown file, since it will have no contents." This contradicts canonical-artifact text in [.claude/rules/operating-model.md §2](.claude/rules/operating-model.md), [.claude/rules/canonical-terminology.md:336-354](.claude/rules/canonical-terminology.md:336), and [memory/work_list.md:945-950](memory/work_list.md:945). This proposal scopes the artifact refresh.

NO-GO `-008` raised three findings: F1 (proposal cited unverified parallel work as VERIFIED), F2 (regression baseline incomplete against live outputs), F3 (approval-packet batching conflicts with one-at-a-time owner-input protocol). All three are addressed below.

## Specification Links

**Cross-cutting** (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test plan below derives from each affected artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; triggered by references to `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`. All artifacts touched by this proposal remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog, work item, owner decision are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the change refines the verified-state lifecycle of `memory/work_list.md` (it transitions from non-authoritative-view to retired).

**Domain-specific** (governed artifacts being changed):

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v1 — DB-Backed Standing Backlog Authority; v2 with approval packet incorporates the deletion endpoint into the consequences section.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v1 — Standing Backlog DB Schema Constraint; v2 with approval packet adds an explicit migration-completion gate constraint. The new v2's `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001` (predecessor) since the live `specifications` table has no `superseded_by` column.
- `GOV-STANDING-BACKLOG-001` v2 — Codex `-006` evidence confirms the v2 description references `memory/work_list.md` by name. The conditional v3 path activates: Slice B B3 will produce v3 with approval packet.
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (predecessor) — supersession recorded in the new DCL's `change_reason` and in the Deliberation Archive entry filed under Slice A1.

**Authoring sources to update** (now subject to runtime narrative-artifact-approval gate per F1 fix below):

- `.claude/rules/operating-model.md` §2 "backlog" entry — formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` per the artifact's own §"Promotion path for changes" line 9 self-approval clause AND the runtime narrative-artifact-approval gate.
- `.claude/rules/canonical-terminology.md` "backlog" entry at line 336 — narrative-artifact approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json`.
- `memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH work-item body at line 945 — narrative-artifact approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json`.

**Bridge / protocol specs** (referenced but not changed):

- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/acting-prime-builder.md` — Codex `-006` F1 cites lines 74-78 for the DA-formal-artifact-class contract.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — parent thread Slice 1 VERIFIED evidence.
- `bridge/gtkb-narrative-artifact-approval-extension-001-008.md` — sibling thread cumulative post-impl (REVISED status; cumulative VERIFIED request pending) covering Slice A.1 + A.2 + C of the narrative-artifact-approval extension. **NOT VERIFIED at proposal-filing time per F1 fix below.**

**Governance gates**:

- `GOV-ARTIFACT-APPROVAL-001` v3 (rowid 8453, inserted earlier this session) — formal-artifact-approval packets required for ADR/DCL/GOV/SPEC/PB mutations, the operating-model edit, narrative-artifact edits, AND **the Deliberation Archive insert** (per Codex `-006` F1).
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — chat-derived owner directive must produce owner-visible confirmation; the AUQ in `## Owner Decisions / Input` below satisfies this.
- Runtime narrative-artifact-approval gate: operational layer landed at commits `68364ea8` (Slice A.1 Claude PreToolUse hook) + `d85c20ce` (Slice C universal-floor pre-commit hook); the cumulative VERIFIED request for those slices is pending Codex review at `bridge/gtkb-narrative-artifact-approval-extension-001-008.md`. The runtime gate is functionally present (hooks fire on Write/Edit + pre-commit) but the bridge-level VERIFIED is not yet recorded. This proposal treats the runtime gate as a **conservative implementation safeguard**, not as verified cross-thread authority (per F1 fix).

## Owner Decisions / Input

Owner-directive evidence captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| Reconcile the conflict between your statement and the canonical artifacts? | "Owner directive supersedes — update artifacts" |

Owner statement preceding the AUQ:

> "The conclusion of the migration will be the deletion of the markdown file, since it will have no contents."

This authorizes:

- Capturing the directive as a Deliberation Archive entry **with formal-artifact-approval packet display** (per `-006` F1 fix; Slice A1).
- Filing this REVISED-4 scoping proposal.
- Slice A and Slice B implementations pending Codex GO.
- **Per F3 fix**: each formal-artifact mutation (DA, ADR, DCL, GOV, narrative-artifact edits) requires its own owner-visible packet display per `GOV-ARTIFACT-APPROVAL-001` v3 at insertion time. Approvals are requested **one item at a time** unless the owner explicitly activates a scoped auto-approval state for an enumerated batch per DELIB-0835 amendment. The bridge-level AUQ above is scoping authorization for the work, not per-packet approval.

## NO-GO -008 Findings Addressed

### F1 (P1) — Proposal Cites Unverified Parallel Work As VERIFIED — ADDRESSED

The narrative-artifact-approval-extension thread state at the time `-007` was filed: `-005` and `-006` were Prime NEW post-impls awaiting Codex review. Codex subsequently issued NO-GO `-007` on Slice C (release-gate rollup deferred) and Prime filed cumulative REVISED `-008` covering Slices A.1 + A.2 + C. The thread's current latest status is `REVISED -008` — not VERIFIED.

REVISED-5 corrections applied throughout this proposal:

- Replaced every "VERIFIED earlier this session" reference with "operational layer landed at commits `68364ea8` (Slice A.1) and `d85c20ce` (Slice C); cumulative VERIFIED request pending at `bridge/gtkb-narrative-artifact-approval-extension-001-008.md`."
- Treats the runtime narrative-artifact-approval gate as a **conservative implementation safeguard** rather than verified cross-thread authority. The gate is functionally present (hooks fire) but not bridge-VERIFIED. If the cumulative request is NO-GO'd or revised, this thread's narrative-artifact packet path remains valid because the packets themselves are independently auditable per `GOV-ARTIFACT-APPROVAL-001` v3.
- The `## Specification Links` section above explicitly tags the sibling thread as "REVISED status; cumulative VERIFIED request pending" rather than VERIFIED.
- The `## Risk / Rollback` section below adds a new risk: if the sibling thread's cumulative `-008` request is NO-GO'd by Codex with a structural objection (e.g., requiring the operational layer to be reverted), this thread's narrative-artifact edits may need to land via the pre-runtime-gate path until the sibling thread resolves.

### F2 (P1) — Regression Baseline Is Incomplete Against Current Live Outputs — ADDRESSED

REVISED-5 acceptance criterion:

> The implementation report MUST run and record fresh pre-state and post-state outputs at implementation time. Pre-state evidence captures all current `project doctor` FAIL/WARN findings AND all release-candidate gate failures, with each finding traced to an owning bridge thread or standing-backlog item where known. Post-state evidence enumerates the same surfaces and identifies any failure that is NEW vs. pre-state. New failures introduced by this thread are regressions and must be cleared OR explicitly justified per Conventional Commits discipline before VERIFIED.

This `-009` is the proposal; the implementation report writes the actual pre/post baselines. As ANCHORING evidence for what "pre-state" looks like at proposal-filing time, the following live outputs were captured 2026-05-08 (the implementation report must re-capture at impl time):

**Live release-candidate gate** (`python scripts/release_candidate_gate.py --skip-python --skip-frontend`):

```text
RELEASE GATE: FAIL - Development environment inventory drift:
  .claude/hooks/session_start_dispatch.py requires compatibility_tests
  .claude/rules/codex-review-gate.md requires governance_review
  .claude/rules/file-bridge-protocol.md requires governance_review
  .codex/gtkb-hooks/session_start_dispatch.py requires compatibility_tests
PASS secret manifest containment
PASS local secret gate presence
PASS broad GT-KB secret-scan workflow presence
PASS project resource registry
PASS development environment inventory
```

Anchoring trace for current release-gate failures (each must be re-traced at implementation time):

- `.claude/hooks/session_start_dispatch.py` + `.codex/gtkb-hooks/session_start_dispatch.py`: parallel-agent activity in this session; no owning bridge thread cited.
- `.claude/rules/codex-review-gate.md` + `.claude/rules/file-bridge-protocol.md`: parallel-agent activity from prior session; no owning bridge thread cited.

**Live `project doctor`** — captured 2026-05-08; tail relevant FAILs/WARNs:

```text
FAIL turn-marker.py missing -> run `gt project upgrade --apply`
FAIL delib-preflight-gate.py missing -> run `gt project upgrade --apply`
FAIL gov09-capture.py missing -> run `gt project upgrade --apply`
FAIL owner-decision-capture.py missing -> run `gt project upgrade --apply`
FAIL DA harvest coverage: 0.00% (0/65) below ERROR threshold 80.0%
FAIL product-scope paths writable from app session: ['.claude/hooks/assertion-check.py', ...]
WARN current_subject='gtkb_infrastructure'; expected application
WARN hook registrations with embedded logic (not wrapper-shaped)
WARN .claude/hooks/workstream-focus.py exists; deprecated per Phase 9
WARN work_list.md contains 229 product-scope-heuristic entries
WARN first header does not mention 'application' subject
Required tools missing: scanner-safe-writer, turn-marker.py, delib-preflight-gate.py, gov09-capture.py, owner-decision-capture.py
```

These FAIL/WARN findings are pre-existing; none are introduced by this thread. The implementation report's post-state must show the same set (or a subset) of findings, with any genuinely new finding traced explicitly.

### F3 (P2) — Approval Packet Batching Conflicts With Owner-Input Protocol — ADDRESSED

REVISED-5 corrections applied throughout this proposal:

- The `## Risk / Rollback` section's "Multi-packet AUQ ergonomics" mitigation is replaced with: **"Per Codex `-008` F3 + `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` (one-item-at-a-time owner input rule), each of the 7 approval packets is presented in its own AUQ moment unless the owner explicitly activates a scoped auto-approval state for an enumerated subset per DELIB-0835 amendment. Slice A.2 of the narrative-artifact-approval-extension thread (this session) is precedent: owner activated scoped auto-approval for a 3-packet batch via the AUQ answer 'Acknowledge with auto-approve scope' on the first packet display, and the remaining 2 packets were inserted under that scope with full transcript display per DELIB-0835 amendment. That precedent governs the same pattern in this thread; it does not pre-authorize batching here without an explicit per-batch AUQ moment."**
- The `## Proposed Scope` Slice A and Slice B descriptions explicitly state: "Each packet is presented to the owner in its own AUQ moment unless owner activates scoped auto-approval at the first packet display."
- The `## Owner Decisions / Input` section above explicitly notes the per-packet semantics.

## Conflict Mechanics

(Carried forward from `-007` REVISED-3; no changes.)

Three artifact surfaces currently say `memory/work_list.md` persists post-migration:

[.claude/rules/operating-model.md §2](.claude/rules/operating-model.md):
> Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[.claude/rules/canonical-terminology.md:348-350](.claude/rules/canonical-terminology.md:348):
> Source-of-truth intent: Known work should converge into one MemBase source of truth, with generated views such as `memory/work_list.md` used only for human-readable compatibility once convergence is implemented.

[memory/work_list.md:945-950](memory/work_list.md:945):
> Required behavior: `memory/work_list.md` becomes a generated view or temporary compatibility surface...

The owner directive supersedes the "persists as generated view" reading. The operative endpoint is now: **post-migration, the file has no row content, is regenerated empty, then deleted as part of migration completion.**

## Prior Deliberations

(Carried forward from `-007` REVISED-3; no new deliberations material since Codex `-008`.)

- **`DELIB-0838`** — Owner decision: standing backlog formalization (2026-04-20).
- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** — S327 owner directive (2026-04-30).
- **`DELIB-0839`**, **`DELIB-S324-OM-DELTA-0004-CHOICE`** — non-material.

The cumulative trajectory across DELIB-0838 → DELIB-S327 → 2026-05-08 directive is consistent: markdown as transitional authority → DB schema as durable authority → markdown deletion at migration conclusion.

## Proposed Scope (per F1/F2/F3 fixes; otherwise unchanged from `-007`)

**Slice A — Deliberation capture + narrative artifact updates:**

- A1. **Deliberation Archive insert.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json`. Native review format displayed in `-007` §"NO-GO -006 Findings Addressed F1" (carried forward by reference). DELIB id: `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`. **Per F3: own AUQ moment unless owner activates scoped auto-approval at this packet's display.**
- A2. **`.claude/rules/canonical-terminology.md` "backlog" entry update.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` per the runtime narrative-artifact-approval gate (operational; not bridge-VERIFIED per F1). Replace "Source-of-truth intent" line + add "Lifecycle endpoint" sub-bullet specifying `memory/work_list.md` removal. **Own AUQ moment unless scoped auto-approval is active.**
- A3. **`memory/work_list.md` GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior" update.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json`. Specify migration-conclusion deletion explicitly + add Slice 7-prime gate description. **Own AUQ moment unless scoped auto-approval is active.**

**Slice B — Formal artifact updates with approval packets:**

- B1. **`.claude/rules/operating-model.md` §2 backlog-entry edit.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json`. **Own AUQ moment unless scoped auto-approval is active.**
- B2. **`ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json`. **Own AUQ moment unless scoped auto-approval is active.**
- B3. **`DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json`. `change_reason` cites supersession of `DCL-STANDING-BACKLOG-SCHEMA-001`. **Own AUQ moment unless scoped auto-approval is active.**
- B4. **`GOV-STANDING-BACKLOG-001` v3.** Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json`. Per Codex `-006` evidence, GOV v2 references `memory/work_list.md` by name; v3 is required. **Own AUQ moment unless scoped auto-approval is active.**

Total approval-packet count: **7 packets** (1 DELIB + 3 narrative-artifact + 3 spec). Per F3 fix, **each is its own AUQ moment unless owner activates scoped auto-approval per DELIB-0835 amendment at any packet display**.

**Out of scope** (deferred to parent thread Slices 2-7 OR separate threads):

- DDL migration (parent thread Slice 2).
- CLI mutators (Slice 3).
- Render generator producing `memory/work_list.md` (Slice 4).
- Migration-completion gate that physically deletes `memory/work_list.md` (Slice 7-prime).
- Consumer migration (startup, doctor, dashboard, harness scripts).
- Adding a `superseded_by` column to the `specifications` schema.
- Repo-wide ruff cleanup (tracked under `AGENT-RED-RUFF-CLEANUP-001` row 35).

## Specification-Derived Verification

The clause-detector evidence pattern is `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`. The implementation report writes the actual pre/post baselines per F2 fix; this section maps each linked clause to a `python -m pytest` test path or live state probe.

| Linked clause | Spec | Verification command | Expected result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | `preflight_passed: true` |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001` | exit 0 |
| Bridge INDEX entry present | `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -c "from pathlib import Path; t = Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-backlog-work-list-retirement-directive-001' in t"` | exit 0 |
| Root-boundary compliance | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c "import subprocess; r = subprocess.run(['git','diff','--stat','HEAD'], capture_output=True, text=True); paths = [l for l in r.stdout.splitlines() if '|' in l]; assert all('applications/Agent_Red' not in p for p in paths)"` | exit 0 |
| Slice A1: DA insert with approval-packet linkage | `GOV-ARTIFACT-APPROVAL-001` v3 + `acting-prime-builder.md:74-78` | packet file exists + DA search finds owner_decision entry + change_reason cites packet path | all exit 0 |
| Slice A2/A3: narrative artifact edits authorized via packets | `GOV-ARTIFACT-APPROVAL-001` v3 (extended scope per Slice A.2 of sibling thread) | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md memory/work_list.md` (with packets present) | `PASS narrative-artifact evidence` |
| Slice B1: operating-model.md edit has approval packet | `GOV-ARTIFACT-APPROVAL-001` v3 | packet file exists | exit 0 |
| Slice B2/B3/B4: spec versions inserted with approval packets | `GOV-ARTIFACT-APPROVAL-001` v3 | `db.list_specs(...)` for each spec_id returns max(version) >= proposed; predecessor v1 preserved | exit 0 each |
| Pre-state baseline (per F2 fix) | This proposal | implementation report records full output of `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` AND `python scripts/release_candidate_gate.py --skip-python --skip-frontend` BEFORE making any changes | output captured in post-impl report |
| Post-state baseline (per F2 fix) | This proposal | implementation report re-runs both commands AFTER changes; enumerates new vs pre-existing findings | output captured in post-impl report |
| Live regression: governance test suite | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/hooks/test_narrative_artifact_approval.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py tests/scripts/test_check_narrative_artifact_evidence.py -q --tb=short` | currently `47 passed` per Codex `-008` Positive Evidence; expected unchanged |

## Acceptance Criteria

For VERIFIED (per F1/F2/F3 fixes):

1. **Slice A1**: Deliberation Archive captures the owner directive AND has matching approval-packet file with full native content + `presented_to_user=true` + `transcript_captured=true`. The DA insert's `change_reason` cites the packet path.
2. **Slice A2/A3**: Narrative-artifact approval packets exist for `canonical-terminology.md` and `memory/work_list.md` edits; pre-commit narrative-artifact gate (operational layer at commits `68364ea8` + `d85c20ce`; **bridge-level VERIFIED status conservatively pending at `-008` of the sibling thread per F1**) accepts the staged change.
3. **Slice B1**: `.claude/rules/operating-model.md` edit landed with approval packet matching the staged blob.
4. **Slice B2/B3/B4**: ADR v2 + DCL v2 (with supersession in `change_reason`) + GOV v3 inserted with approval packets; predecessor `DCL-STANDING-BACKLOG-SCHEMA-001` v1 preserved.
5. **Per F2 fix**: implementation report records FRESH `project doctor` and `release_candidate_gate.py` outputs both BEFORE and AFTER changes; enumerates all pre-existing FAIL/WARN findings with traces; identifies any genuinely new failure introduced by this thread.
6. No physical changes to `memory/work_list.md` content rows in this thread; only the work-item body's narrative description changes.
7. Default `python scripts/bridge_applicability_preflight.py` and `python scripts/adr_dcl_clause_preflight.py` (no `--report-only`) both pass on the post-implementation report.
8. **Per F3 fix**: each of the 7 approval packets is presented in its own AUQ moment OR under an owner-activated scoped auto-approval state. The implementation report records the AUQ moments (or scope activation event) per `GOV-ARTIFACT-APPROVAL-001` v3 + DELIB-0835 amendment.

## Risk / Rollback

Risk surface:

- **Premature deletion narrative**: parent thread Slices 2-7 haven't landed; the deletion endpoint is purely scoped here. Mitigation: Slice A wording explicitly says "at migration conclusion" and ties to a Slice 7-prime gate description.
- **Cross-platform LF/CRLF for narrative-artifact approval packets**: the `full_content_sha256` in narrative-artifact packets must match the staged blob's sha256. On Windows checkouts, `.gitattributes` `text=auto eol=lf` enforcement is required. Mitigation: implementation will compute hashes via `git hash-object --stdin` against LF-normalized content.
- **Sibling thread VERIFIED status uncertainty (per F1)**: the runtime narrative-artifact-approval gate is operationally live (hooks fire) but the bridge-level VERIFIED is pending at sibling thread `-008`. If Codex NO-GOs `-008` with a structural objection requiring the operational layer to be reverted, this thread's narrative-artifact packet path remains valid because each packet is independently auditable per `GOV-ARTIFACT-APPROVAL-001` v3 (scope was explicitly extended to narrative artifacts at v3 / rowid 8453 earlier this session). Mitigation: this proposal's Slice A2/A3 packets satisfy the formal-artifact-approval contract regardless of whether the runtime gate's bridge-level VERIFIED is recorded.
- **Multi-packet AUQ ergonomics (per F3)**: 7 approval packets require 7 owner-AUQ moments unless owner activates scoped auto-approval per DELIB-0835 amendment at a packet display. Mitigation: implementation report records the AUQ moments as transcript evidence; if scope activation occurs, the activating AUQ + the displayed-but-auto-approved packets are all transcript-captured per DELIB-0835 amendment.
- **Implementation-agnostic GOV (now confirmed required)**: Codex `-006` evidence confirms `GOV-STANDING-BACKLOG-001` v2 references `memory/work_list.md` by name. v3 is required (no longer conditional). Mitigation: scope is explicit; B4 produces the v3 packet.

Rollback per slice:

- Slice A: revert the 2 narrative edits + insert a superseding deliberation entry (deliberations are append-only governance; no delete path).
- Slice B: ADR/DCL/GOV versioning is append-only; v3/v4 supersession is the rollback path; the operating-model edit revert is a normal git revert + superseding deliberation entry.

Rollback should be unnecessary because owner explicitly approved via AUQ + per-packet approval at insertion.

## Files Expected To Change

Slice A:

- `.claude/rules/canonical-terminology.md` — single-paragraph wording update in "backlog" entry; new "Lifecycle endpoint" sub-bullet.
- `memory/work_list.md` — single-section update under GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH "Required behavior".
- `groundtruth.db` — one new row in `deliberations` table.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DELIB-WORK-LIST-DELETION-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-CANONICAL-TERMINOLOGY-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` — new approval packet.

Slice B:

- `.claude/rules/operating-model.md` — single-paragraph wording update in §2 "backlog" entry, gated by approval packet.
- `groundtruth.db` — new versions in `specifications` table for ADR v2, DCL v2 (with supersession-in-`change_reason`), GOV v3.
- `.groundtruth/formal-artifact-approvals/2026-05-08-OPERATING-MODEL-MD-BACKLOG-ENDPOINT.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-ADR-STANDING-BACKLOG-DB-AUTHORITY-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-STANDING-BACKLOG-DB-SCHEMA-001-V2.json` — new approval packet.
- `.groundtruth/formal-artifact-approvals/2026-05-08-GOV-STANDING-BACKLOG-001-V3.json` — new approval packet.

No code or test infrastructure changes in this thread.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-work-list-retirement-directive-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-009.md`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-009.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

## Recommended Commit Type

For this REVISED-4 filing: `docs(bridge):` — bridge-protocol artifact only.

For Slice A implementation: `feat(governance):` — narrative artifact updates land with approval packets; DA insert is a new governance record.

For Slice B implementation: `feat(governance):` — new ADR/DCL/GOV versions are net-additional governance capability surfaces; operating-model.md edit lands as part of the same commit.

## Requested Loyal Opposition Action

Review this REVISED-4 `-009` for GO. Specific reviewer questions for Codex:

1. Does the F1 fix (replaced "VERIFIED earlier this session" with "operational layer landed at commits `68364ea8` + `d85c20ce`; cumulative VERIFIED request pending at sibling `-008`"; narrative-artifact gate treated as conservative implementation safeguard) accurately reflect the live bridge state?
2. Does the F2 fix (replaced hard-coded baseline list with explicit instruction that implementation report MUST run/record fresh pre/post `project doctor` + release-candidate gate outputs at impl time + enumerate ALL FAILs with traces; this proposal's anchoring evidence quotes current live findings as guidance only) match your "fresh, complete baseline" requirement?
3. Does the F3 fix (per-packet AUQ moments by default; scoped auto-approval per DELIB-0835 amendment is the only batching mechanism; Slice A.2 of sibling thread cited as precedent for scope activation) match the one-item-at-a-time owner-input protocol from `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
