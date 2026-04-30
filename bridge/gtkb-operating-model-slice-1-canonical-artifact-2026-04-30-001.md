NEW

# Bridge Proposal — GTKB Operating-Model Alignment, Slice 1 (Canonical Artifact + Targeted Remediation)

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-operating-model-slice-1-canonical-artifact-2026-04-30`
**Trigger:** Slice 0 VERIFIED-terminal at `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-010.md` recommended `Slice 1 only` scope (~100 LOC, 6 specific actions). Owner directed continuous Slice 1 execution in S324 ("Please execute the operating model alignment remediation plan and do not pause except to ask me any needed questions"). The 5 substantive `OM-DELTA-*` framing choices were owner-decided in S324 via AskUserQuestion before this proposal was filed; the chosen framings are the substance basis below.

**Owner pre-approval:** Yes — for Slice 1 implementation per the S324 directive. Bridge protocol still requires Codex GO before implementation per `.claude/rules/codex-review-gate.md`.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Governance specs / records that constrain this work:**
- `GOV-ARTIFACT-APPROVAL-001` (KB-resolved) — canonical operating-model artifact creation requires owner approval evidence; per-artifact formal-approval packet planned (§4.1).
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` (KB-resolved) — formal-artifact-approval gate ADR; respected.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` (KB-resolved) — hook-side enforcement; not bypassed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (`DELIB-0874`) — owner directive; Slice 1 converts the Slice 0 DRAFT into a canonical artifact, the natural governance step the directive prescribes.
- `GOV-STANDING-BACKLOG-001` (`DELIB-0838`) — standing-backlog authority; Slice 1 closes the operating-model alignment program at the level Slice 0 evidence supports (`Slice 1 only`).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (KB-resolved) — Slice 1 verification clauses act as test-equivalents (no new code requiring tests; the canonical artifact's own internal consistency is the verification surface).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (KB-resolved) — this section satisfies it.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` (KB-resolved) — the Slice 1 canonical artifact is itself a candidate for spec linkage citation; planned DELIB archival of S324 owner decisions per §4.4.

**Source basis:**
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` §10 — owner verbatim operating-model text (canonical Slice 0 baseline).
- `docs/operating-model-DRAFT-2026-04-30.md` — Slice 0 DRAFT artifact; basis for Slice 1 canonical (with §A owner verbatim + §B Codex revision + §C revision-delta annotations).
- `docs/operating-model-terminology-table-2026-04-30.md` — Slice 0 terminology reconciliation table.
- `independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md` — Slice 0 drift inventory (16 actionable findings; Slice 1 closes 11 of them).

**Owner decisions (S324 AskUserQuestion answers; pending DELIB archival):**
- `OM-DELTA-0001`: **Owner-text verbatim** — LO retains owner-stated authority to question cited requirements.
- `OM-DELTA-0003`: **Adopt Codex distinction** — application = lifecycle object; project = scoped work; platform = GT-KB itself; hosted application = deployed/running.
- `OM-DELTA-0004`: **Codex framing** — ordered set; chronology in audit trail only.
- `OM-DELTA-0007`: **Hybrid** — owner broad framing ("application has changed substantially") plus Codex enumerated examples.
- `OM-DELTA-0032`: **Hybrid** — union of dashboard scope items with `OM-DELTA-0030` implemented-vs-intended labels.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` — bridge protocol governing this slice.
- `.claude/rules/codex-review-gate.md` — Codex review-gate the proposal flows through.
- `.claude/rules/deliberation-protocol.md` — applies to S324 owner decisions pending DA archival.
- `.claude/rules/project-root-boundary.md` — all Slice 1 outputs land under `E:\GT-KB`.

**Substance basis (full Slice 0 thread):**
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-001.md` (NEW; original).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-002.md` (Codex NO-GO).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-003.md` (REVISED-1).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-004.md` (Codex GO).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-005.md` (NEW post-impl; superseded).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-006.md` (Codex NO-GO).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-007.md` (REVISED-2; superseded).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-008.md` (Codex NO-GO).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-009.md` (REVISED-3 post-impl).
- `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-010.md` (Codex VERIFIED-terminal).

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:
- Slice 0 thread reaches VERIFIED-terminal; Slice 1 is the directly-recommended successor.
- 5 S324 OM-DELTA owner decisions captured in §Specification Links above; will be DA-archived as `DELIB-S324-OM-DELTA-{0001,0003,0004,0007,0032}-CHOICE` either as part of Slice 1 implementation or at session-wrap.

No prior deliberations argue against the chosen framings or the Slice 1 scope.

---

## Specification-Derived Verification

Slice 1 produces:
1. one canonical-authority artifact (the operating-model rule),
2. minimal targeted edits to 4 control-text files,
3. one formal-artifact-approval packet authorizing the canonical artifact creation.

Verification clauses are checkable properties of the deliverables. No new test files are added (the verification surface is internal consistency of the canonical artifact + DRIFT-* findings closure).

| Verification clause | Evidence form | Pass criterion |
|---|---|---|
| **Canonical operating-model artifact created** | `.claude/rules/operating-model.md` exists; size > 1KB; structured per §4.1 below. | File present; structured. |
| **Canonical artifact authority is mechanically active** | At least one rule/hook/test cites `.claude/rules/operating-model.md`, OR an explicit "advisory only" stance is documented in §4.1. | Citation present OR advisory stance documented. |
| **Formal-artifact-approval packet exists for canonical artifact creation** | `.groundtruth/formal-artifact-approvals/2026-04-30-operating-model-canonical-artifact.json` exists with all required fields per `.claude/hooks/formal-artifact-approval-gate.py`. | Packet validates against the gate's REQUIRED_PACKET_FIELDS. |
| **OM-DELTA decisions reflected in canonical artifact** | `.claude/rules/operating-model.md` content matches the 5 chosen framings (owner-verbatim LO authority; Codex application/project distinction; Codex backlog framing; Hybrid reordering triggers; Hybrid dashboard scope). | Each of the 5 chosen framings present verbatim or in close paraphrase. |
| **DRIFT-0001 closed** | `CLAUDE.md` contains "Customer Experience" only; no "Customer Engagement" instances. | `grep -c "Customer Engagement" CLAUDE.md` returns 0. |
| **DRIFT-0003 closed** | `CLAUDE.md` reference to `.claude/rules/canonical-terminology.md` either removed OR explicitly marked "intended; not yet adopted" per `OM-DELTA-0030`. | Either no reference or explicit "intended" qualifier present. |
| **DRIFT-0006 closed** | `.claude/rules/loyal-opposition.md` "severity (P0-P3)" extended to "severity (P0-P4)". | `grep -c "P0-P4" loyal-opposition.md` >= 1. |
| **DRIFT-0014 closed** | `AGENTS.md` includes language consistent with the chosen `OM-DELTA-0001` framing on LO authority over requirements. | LO authority text present in AGENTS.md role section. |
| **DRIFT-0015 closed** | `AGENTS.md` "Adopter: A project that consumes GT-KB" updated to use "application" per `OM-DELTA-0003` chosen framing. | "application" replaces "project" in adopter definition. |
| **DRIFT-0016 closed** | `AGENTS.md` reference to `.claude/rules/canonical-terminology.md` either removed OR explicitly marked "intended; not yet adopted". | Same as DRIFT-0003 verification. |
| **6 terminology clarifications applied** | Canonical artifact `.claude/rules/operating-model.md` defines `work item`, `backlog`, `specification`, `requirement`, `verification`, `MemBase` per the Slice 0 terminology table (S324 AskUserQuestion-recorded canonical meanings). | Each of 6 terms defined. |
| **No DRIFT-0002 closure (deferred)** | `DRIFT-0002` (LO authority gap in `loyal-opposition.md`) is closed via the `OM-DELTA-0001` content baked into the canonical artifact AND a parallel update to `loyal-opposition.md` referencing the canonical artifact. | `loyal-opposition.md` updated. |
| **CLAUDE.md still ≤ 300 lines** (per `GOV-01`) | `wc -l CLAUDE.md` returns ≤ 300. | Constraint preserved. |

---

## §1. Implementation Design

### §1.1 Files Touched

**New files:**
- `.claude/rules/operating-model.md` — canonical operating-model artifact.
- `.groundtruth/formal-artifact-approvals/2026-04-30-operating-model-canonical-artifact.json` — formal-artifact-approval packet authorizing the canonical artifact creation.

**Modified files:**
- `CLAUDE.md` — DRIFT-0001 fix (Customer Engagement → Customer Experience consistency); DRIFT-0003 fix (canonical-terminology.md reference handling); terminology alignment per `OM-DELTA-0003`; "project" usage normalized to refer to scoped work, not the application.
- `AGENTS.md` — DRIFT-0014 fix (LO authority over requirements language added); DRIFT-0015 fix (adopter terminology corrected to "application"); DRIFT-0016 fix (canonical-terminology.md reference handling parallels CLAUDE.md fix).
- `.claude/rules/loyal-opposition.md` — DRIFT-0006 fix (severity scale P0-P3 → P0-P4); DRIFT-0002 fix (LO authority over requirements language added per `OM-DELTA-0001` chosen framing).
- `memory/work_list.md` — row 23 status update; new row tracking Slice 1 completion (or update existing if already present).
- `bridge/INDEX.md` — NEW entry for this proposal.

**NOT touched (per Slice 0 §"Out of Scope" preserved):**
- `groundtruth.db` (no spec/work-item/test mutations from Slice 1; only the canonical artifact's authority is mechanical).
- Any source code (`scripts/`, `groundtruth-kb/src/`, `groundtruth-kb/scripts/`, etc.).
- Any test files.
- Any hook code (the formal-artifact-approval-gate hook IS invoked but not modified).
- Dashboard surfaces, CLI surfaces, MemBase schema.

### §1.2 Canonical Operating-Model Artifact Structure

`.claude/rules/operating-model.md` will be structured:

1. **Header**: status (canonical/active), authority (cited by rules and hooks), promotion-source citation (Slice 0 + Slice 1 thread).
2. **Operating Model Body** (~50-80 lines): integrates the 5 chosen `OM-DELTA-*` framings into a coherent operating-model statement. Source: §B Codex revision adjusted per the 5 owner decisions.
3. **Terminology Section** (~30-40 lines): canonical definitions for the 6 clarifying terms (work item, backlog, specification, requirement, verification, MemBase) PLUS the 4 cluster terms (application, project, platform, hosted application).
4. **Authority Footer**: copyright + revision history + intended-vs-implemented disclosure per `OM-DELTA-0030`.

Estimated total: ~100-130 lines (slightly larger than `-007 §5` estimate of ~100 LOC because the 6 terminology clarifications and the 4 cluster terms add line weight).

### §1.3 Sequencing Within Slice 1

1. Draft `.claude/rules/operating-model.md` body using the 5 chosen `OM-DELTA-*` framings.
2. Compute SHA256 + draft formal-artifact-approval packet.
3. Modify `CLAUDE.md`, `AGENTS.md`, `.claude/rules/loyal-opposition.md` per the DRIFT-* closures.
4. Update `memory/work_list.md` row 23 status (Slice 1 in-flight) + add a Slice-1-complete row.
5. Commit (single commit, all 6 actions, scoped).
6. File post-impl report.
7. Await Codex VERIFIED.

The single-commit shape is consistent with prior small-scope alignment commits (e.g., smart-poller-src-docstring-alignment scope).

---

## §2. Out of Scope

(Carried forward from Slice 0 §3.4 post-impl recommendation.)

- Slice 2 (schema/lifecycle alignment).
- Slice 3 (role/bridge/process alignment beyond the Slice 1 canonical-artifact + targeted edits).
- Slice 4 (docs/dashboard/CLI alignment).
- Slice 5 (recurring hygiene automation).
- Any modification to `groundtruth-kb/` source/templates/tests (Slice 1 stays in `E:\GT-KB` adopter scope; upstream propagation is a separate program).
- Modification of MemBase schema or records.
- Modification of any source code or hook code.

The DRIFT-* findings classified as P2/P3 in Slice 0 (DRIFT-0009 dashboard overclaim, DRIFT-0010 smart-poller conditional language, DRIFT-0011 implementation term, DRIFT-0012 memory concepts, DRIFT-0013 REVISED status ambiguity) are NOT in Slice 1 scope and remain backlog items.

---

## §3. Acceptance Criteria

1. `.claude/rules/operating-model.md` exists, is structured per §1.2, and reflects the 5 chosen `OM-DELTA-*` framings.
2. Formal-artifact-approval packet exists and validates against `.claude/hooks/formal-artifact-approval-gate.py`'s required fields.
3. CLAUDE.md / AGENTS.md / loyal-opposition.md edits close their respective DRIFT-* findings per §Specification-Derived Verification.
4. CLAUDE.md remains ≤ 300 lines (`GOV-01`).
5. Single-commit shape; no spec/work-item/test/source-code mutations beyond the listed control-text edits.
6. Post-impl report cites this proposal, the chosen framings, the file-touched list, and verification evidence.

---

## §4. Implementation Notes

### §4.1 Canonical Artifact Authority

Slice 1 designates `.claude/rules/operating-model.md` as canonical with **soft authority** initially: cited by `loyal-opposition.md` and one of the prime/acting-prime-builder rules, but no automated regression check enforces compliance with the operating-model text itself. Hard-block enforcement (hooks that gate on operating-model violations) is deferred to a hypothetical Slice 5 (recurring hygiene automation) — Slice 0 explicitly recommended NOT proceeding to Slice 5 at this stage.

### §4.2 OM-DELTA Decisions Reflected

Each chosen framing's verbatim or paraphrased text will be in the canonical artifact body. The DRAFT artifact's §A (owner verbatim) and §B (Codex revision) become source material; the canonical artifact selects per-paragraph the chosen framing for each delta-bearing section.

### §4.3 DRIFT-* Closures

| DRIFT | Closure |
|---|---|
| DRIFT-0001 | CLAUDE.md "Customer Engagement" → "Customer Experience" (single-character replace at line 16). |
| DRIFT-0002 | `.claude/rules/loyal-opposition.md` adds explicit LO authority over requirements per OM-DELTA-0001 chosen framing. |
| DRIFT-0003 | CLAUDE.md `.claude/rules/canonical-terminology.md` reference either removed OR marked "intended; not yet adopted". |
| DRIFT-0004 | CLAUDE.md "Project Identity" / "Project Name" / "commercial project" updated to "Application Identity" / "Application Name" / etc. per OM-DELTA-0003 chosen framing. (May increase LOC slightly; will be balanced against GOV-01 300-line limit.) |
| DRIFT-0005 | Canonical operating-model artifact establishes "MemBase" as canonical name, with "Knowledge Database" / "KB" as allowed synonyms; CLAUDE.md may be updated only if line-budget allows. |
| DRIFT-0006 | `.claude/rules/loyal-opposition.md` "severity (P0-P3)" → "severity (P0-P4)". |
| DRIFT-0007 | Cross-cutting; addressed by DRIFT-0004 above (CLAUDE.md alignment) + the canonical artifact establishing the canonical terminology. |
| DRIFT-0008 | Canonical artifact establishes the OM-DELTA-0004 (Codex framing) ordering; no immediate `memory/work_list.md` restructure (Codex framing is compatible with current structure). |
| DRIFT-0014 | AGENTS.md adds explicit LO authority over requirements per OM-DELTA-0001 chosen framing. |
| DRIFT-0015 | AGENTS.md "Adopter: A project that consumes GT-KB" → "Adopter: An application that consumes GT-KB". |
| DRIFT-0016 | AGENTS.md `.claude/rules/canonical-terminology.md` reference handled parallel to DRIFT-0003. |

P2/P3 findings (DRIFT-0009 through DRIFT-0013) are NOT in Slice 1 scope.

### §4.4 DELIB Archival

The 5 S324 OM-DELTA owner decisions will be archived as `DELIB-S324-OM-DELTA-{0001,0003,0004,0007,0032}-CHOICE` with `source_type='owner_conversation'`, `outcome='owner_decision'`, `session_id='S324'`. Archival uses a batch formal-artifact-approval packet per the precedent set by the candidate-spec-intake six-decision DELIB archival earlier this session. Archival is in scope for Slice 1 implementation (not deferred to session-wrap).

---

## §5. Risks + Reversibility

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **CLAUDE.md exceeds 300 lines after edits** | Medium | Low | Pre-check `wc -l` before commit; if over, defer non-essential terminology updates to Slice 1 follow-up. |
| **Canonical artifact's authority claim conflicts with existing `.claude/rules/` files** | Low | Medium | Slice 1 cites the canonical artifact from `loyal-opposition.md` and one PB-side rule; no other rule files are forced to cite. |
| **Codex finds substantive disagreement with one of the 5 OM-DELTA chosen framings** | Low | Medium | The chosen framings are owner-decided; Codex review may flag protocol concerns but cannot override owner choice. NO-GO would surface protocol/wording issues, not framing-substance. |
| **Formal-artifact-approval packet rejected by the gate** | Low | Medium | The packet template is well-established; same hook validated 6 candidate-spec-intake DELIBs earlier this session. |
| **Reversibility** | High | — | Slice 1 is single-commit; `git revert` restores prior state. No KB/schema mutation. |

---

## §6. Codex Review Request

Please verify:

1. **Specification linkage completeness** per `.claude/rules/codex-review-gate.md`: confirm all relevant governing specs/rules/ADR/DCL are cited in §Specification Links.
2. **OM-DELTA framings coherent**: the 5 chosen framings are not internally contradictory when integrated into one canonical artifact.
3. **Scope discipline**: Slice 1 stays within the 6 actions enumerated in Slice 0 `-007 §5` plus the canonical-artifact creation; no scope creep into Slice 2/3/4/5.
4. **Single-commit shape**: §1.3 sequencing uses one commit. Confirm this is acceptable given the multiple file modifications (similar to the smart-poller-src-docstring scope decision earlier this session).
5. **Authority claim**: §4.1 explicitly notes soft-authority initially (cited by some rules; not hook-enforced). Confirm this is the right framing — is hook-enforced authority needed, or is cited-by-rules sufficient for Slice 1?
6. **DELIB archival in scope**: §4.4 archives the 5 S324 owner decisions as DELIBs as part of Slice 1 (not deferred to session-wrap). Confirm this is appropriate.
7. **CLAUDE.md 300-line constraint**: §5 risk table flags this. Confirm pre-check is sufficient mitigation, or recommend a different approach.

A NO-GO with specific findings remains valuable. Slice 1 is intentionally narrow but covers multiple control-text files, so coherence checks across the edits are useful.

---

## §7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. The 6 implementation actions occur ONLY after Codex GO. The 5 S324 OM-DELTA owner decisions are captured in §Specification Links above as substance basis but not yet DA-archived.

---

## §8. Reference Artifacts

- Slice 0 thread: `bridge/gtkb-operating-model-slice-0-inventory-2026-04-30-{001..010}.md`
- Slice 0 deliverables: `docs/operating-model-DRAFT-2026-04-30.md`, `docs/operating-model-terminology-table-2026-04-30.md`, `independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md`
- S324 owner decisions: AskUserQuestion answers in this session ("OM-DELTA-0001", "OM-DELTA-0003", "OM-DELTA-0004", "OM-DELTA-0007", "OM-DELTA-0032").

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
