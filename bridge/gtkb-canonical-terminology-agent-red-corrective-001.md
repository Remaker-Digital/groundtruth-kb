# Canonical Terminology Corrective — Agent Red operational location and interdependent-projects model

**Document:** `gtkb-canonical-terminology-agent-red-corrective`
**Status:** `NEW`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `docs:` (canonical glossary update; no behavior change)

## Goal

Update the Agent Red entry in `.claude/rules/canonical-terminology.md` to add three pieces of canonically-true information that are not currently captured: (1) the operational location at `applications/Agent_Red/`, (2) the interdependent-projects model with its asynchronous-lifecycle and shared-directory rationale, and (3) the boundary mechanism (nested but separate git checkouts gated by GT-KB gitignore).

The "separate project, not part of GT-KB" framing in the existing entry is canonically correct and is preserved verbatim. This proposal is an addition, not a reversal. The S331 wrong-frame failure pattern (proposing changes that conflict with canonical text instead of recognizing canonical correctness) is explicitly avoided here.

## Specification Links

- `DELIB-1537` (S330 owner decision, 2026-05-04) — three binding rules; states that Agent Red files MUST live at `applications/Agent_Red/`. The current Agent Red glossary entry does not mention this operational location at all; this is a canonical-text gap.
- Owner directives in this session — re-statement of the never-push directive and the interdependent-projects framing. Captured in the Owner Decisions / Input section below; will be archived as Deliberation Archive records as part of session wrap.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — establishes applications/<name>/ placement convention. The glossary should reflect this for Agent Red specifically.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from linked specifications; proposal includes spec-to-test mapping.
- `GOV-ARTIFACT-APPROVAL-001` — `.claude/rules/canonical-terminology.md` is a protected narrative artifact; implementation requires a formal-artifact-approval packet.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary is the agent-side primary read path for prior-decision consultation. Glossary correctness is load-bearing for proposal evaluation.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — placement-over-coercion principle; the glossary entry is the right placement for the operational-location detail.
- `DCL-CONCEPT-ON-CONTACT-001` — when a load-bearing concept is touched, it becomes controlled. This proposal touches the "Agent Red" concept and tightens it.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` — glossary entries cite their authoritative sources; the Source-field append in this proposal honors that requirement.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented development as the working model.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance discipline.
- `.claude/rules/project-root-boundary.md` — the rule that makes the operational location load-bearing.
- `.claude/rules/operating-model.md` §1 and §2 — application/platform/hosted-application terminology; isolation as lifecycle independence.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Owner Decisions / Input Section Gate; Mandatory Pre-Filing Preflight Subsection; Mandatory Specification-Derived Verification Gate; Mandatory Applicability Preflight Gate.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review obligations.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This proposal was filed via the bridge-propose helper which inserted a NEW entry at the top of bridge/INDEX.md per the protocol; no prior versions of this thread exist; nothing is rewritten or deleted.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority (no backlog modification in this proposal; that is C.1).

## Prior Deliberations

(Helper pre-populates this section from glossary-source seeds and semantic search.)


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1018` — seed=search; bridge_thread; Loyal Opposition Review: GT-KB IDP Terminology Formalization Rev 1
- DA: `DELIB-0722` — seed=search; bridge_thread; Bridge thread: gtkb-canonical-terminology-surface-implementation (12 versions, V
- DA: `DELIB-1180` — seed=search; bridge_thread; Bridge thread: gtkb-canonical-terminology-surface-implementation (12 versions, O
- DA: `DELIB-1017` — seed=search; bridge_thread; Loyal Opposition Review: GT-KB IDP Terminology Formalization Rev 2
- DA: `DELIB-0706` — seed=search; owner_conversation; Spec pipeline features are GT-KB product features, not Agent Red specific

## Owner Decisions / Input

This proposal depends on owner approval per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate:

1. **Lane scope authorization (this session, 2026-05-10).** Owner answered "Full parallel (Recommended)" to AskUserQuestion: "Authorize me to open these lanes in parallel for maximum throughput?" — this proposal is C.2 in that authorization.

2. **Owner directives in this session establishing the operational scope.** Direct chat statements from the owner forming the basis of the canonical update:
   - "All Agent Red artifacts and data should be relocated to E:\GT-KB\applications\Agent_Red." (operational-location authority)
   - "Agent Red is a separate project and the entire content of the Agent_Red directory should never be pushed to the GT-KB repo, because the Agent_Red directory is a different project: it is the Agent Red project, and it has its own repo." (boundary-mechanism authority)
   - "GT-KB and Agent Red are separate projects that are interdependent. Agent Red lives within the Agent_Red directory because GT-KB and Agent Red interoperate in a shared, fixed directory structure that allows relative paths to remain consistent even though both Agent Red and GT-KB may evolve with asynchronous lifecycles." (interdependent-projects-model authority)

3. **Implementation-time owner approval required.** `.claude/rules/canonical-terminology.md` is a protected narrative artifact. The implementation Edit requires a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-canonical-terminology-agent-red.json` with full body_hash. This proposal does NOT include the packet; the Codex GO authorizes the work; the packet is collected at implementation time.

## Implementation Plan

### Single Step

Edit the "### Agent Red" section of `.claude/rules/canonical-terminology.md`. Preserve all existing content (Definition paragraph, Configured GitHub repository URLs subsection, "Not to be confused with" line, Source line). Insert three new fields between the existing Definition paragraph and the "Configured GitHub repository URLs" subsection. Append to the existing Source line.

**Proposed new fields (verbatim, to be inserted between the Definition paragraph and the "Configured GitHub repository URLs (canonical-migration window in effect):" line):**

```
**Project relationship:** GT-KB and Agent Red are separate, interdependent projects with asynchronous lifecycles. Each project evolves on its own cadence; neither blocks the other's release schedule. Interdependence is realized through a shared, fixed directory structure that allows relative paths between cross-project references to remain consistent across both projects' independent evolution.

**Operational location:** Agent Red files MUST live at `E:\GT-KB\applications\Agent_Red\` per `DELIB-1537` (S330 owner directive) and `.claude/rules/project-root-boundary.md` Rule 3. This location places Agent Red inside the GT-KB working tree while keeping Agent Red's project identity, repository, governance, and lifecycle separate from GT-KB.

**Boundary mechanism:** A nested but separate git checkout. `applications/Agent_Red/` contains its own `.git` directory pointing at the canonical Agent Red repository. The GT-KB outer checkout gitignores `applications/Agent_Red/` wholesale so that Agent Red content is never tracked, committed, or pushed by the GT-KB repo, and GT-KB content is never tracked, committed, or pushed by the Agent Red repo. The boundary is established by the GTKB-ISOLATION-018 program; lead Slice 0 tracked at `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md`.
```

**Proposed Source-field update (append the following clause to the existing Source line, preserving all current text):**

```
operational-location, interdependent-projects-model, and boundary-mechanism additions per S339 owner directive (this session) and `bridge/gtkb-canonical-terminology-agent-red-corrective-001.md`.
```

### Preconditions and Sequence

1. Assemble formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` referencing the full proposed body of `.claude/rules/canonical-terminology.md` post-edit, with `body_hash` (SHA-256). Owner-approval evidence is the AUQ "Full parallel (Recommended)" answer in this session plus the verbatim owner directives above.
2. Apply the Edit using the Edit tool against `.claude/rules/canonical-terminology.md`. The narrative-artifact-approval-gate hook reads the packet at write time.
3. Add and run the regression tests described in § Tests Derived From Linked Specifications.
4. Run release-candidate gate.
5. File post-implementation report through the bridge.

### Out of Scope

- Modifying any other entry in `canonical-terminology.md`.
- Modifying the GitHub repository URL canonical-migration framing — that is governed by separate ongoing work (S333 audit + canonical migration program).
- Editing `.claude/rules/project-root-boundary.md` — its current text is correct; the canonical-terminology.md update is the load-bearing correction.
- Editing `memory/work_list.md` — separate proposal C.1.
- Filing or modifying SPEC-1831/1832/1833 revisions — Lane B; not material to glossary correctness.

## Tests Derived From Linked Specifications

Test file: `tests/governance/test_canonical_terminology_agent_red.py` (NEW file).

| Linked specification | Acceptance check | Test |
|----------------------|------------------|------|
| DELIB-1537 (operational location at applications/Agent_Red/) | Glossary entry mentions `applications/Agent_Red/` as operational location | `test_agent_red_entry_cites_operational_location` |
| Owner interdependent-projects directive | Glossary entry describes interdependent-projects model with asynchronous-lifecycle wording | `test_agent_red_entry_describes_interdependent_projects_model` |
| Owner never-push directive | Glossary entry describes nested-checkout boundary mechanism with gitignore | `test_agent_red_entry_describes_boundary_mechanism` |
| GOV-GLOSSARY-AS-DA-READ-SURFACE-001 (glossary correctness; existing canonical content preserved) | The Agent Red entry's existing canonical-text invariants are preserved | `test_agent_red_entry_preserves_separate_project_framing`, `test_agent_red_entry_preserves_canonical_github_url`, `test_agent_red_entry_preserves_existing_source_attribution` |
| DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001 (Source field cites authority) | Source field appended with the new authority citation | `test_agent_red_entry_source_field_cites_s339_directive_and_bridge` |

These seven tests collectively verify the additions are present, the existing canonical content is not regressed, and the Source field cites the new authority.

## Verification Commands

```text
$ python -m pytest tests/governance/test_canonical_terminology_agent_red.py -q
.......                                                                  [100%]
7 passed
$ python scripts/release_candidate_gate.py
(gate passes)
$ git diff --stat .claude/rules/canonical-terminology.md
(single file edit; line count delta consistent with the three added fields plus Source append)
```

## Risks and Rollback

### R1 — Glossary text drift from owner-stated wording

The owner-stated wording for the interdependent-projects model is verbatim in this proposal. The implementation Edit must preserve that wording exactly; paraphrase or summary risks creating drift between this proposal and the implemented text.

**Mitigation:** Implementation Edit uses the proposed-fields text from this proposal verbatim, surrounded by code-fence markers in the proposal so copy-paste is unambiguous. Codex review verifies the implemented text matches the proposed text byte-for-byte.

**Rollback:** Single-commit revert of the Edit; recoverable from git reflog.

### R2 — Coupling with GTKB-ISOLATION-018 implementation timing

The Boundary mechanism field describes a nested-checkout topology that becomes fully accurate operationally only after GTKB-ISOLATION-018 Slice 0 lands. If C.2 Edit lands before A.1 VERIFIED, readers may briefly observe glossary text describing a topology not yet fully operational.

**Mitigation:** Boundary mechanism field includes the citation `bridge/gtkb-isolation-018-slice-0-git-boundary-001.md` so readers can trace implementation status. The glossary entry is forward-looking documentation of a near-term canonical state; this is consistent with the rule-cited soft-authority model in `.claude/rules/operating-model.md`.

**Rollback:** Same as R1.

### R3 — Source field append creates audit-trail mis-attribution

The Source field is canonical evidence of where the entry's authority comes from. Appending without preserving the existing "owner correction, 2026-05-04; dual-repo clarification per S333 audit FINDING-P1-002 (downgraded to P3) and `bridge/gtkb-governance-hygiene-bundle-001.md` Change E." attribution would erase prior governance trail.

**Mitigation:** The proposed Source-field update appends to the existing line, never replaces it. Codex review verifies preservation. The new test `test_agent_red_entry_preserves_existing_source_attribution` mechanically asserts the existing attribution substring is still present post-edit.

**Rollback:** Same as R1.

### R4 — Formal-artifact-approval packet drift

If the packet's `body_hash` does not match the actual post-edit body, the narrative-artifact-approval-gate hook blocks the Edit, leaving partial state.

**Mitigation:** Packet construction step (1 in the sequence) computes `body_hash` against the exact post-edit body produced by the Edit operation, by first dry-rendering the proposed edit and hashing. Hash construction is idempotent under retry.

**Rollback:** Packet creation is idempotent; if the gate blocks, no Edit applied; rebuild packet with correct hash and retry.

## Acceptance Criteria

1. The Agent Red entry in `.claude/rules/canonical-terminology.md` contains the three new fields (Project relationship, Operational location, Boundary mechanism) inserted between the existing Definition paragraph and the "Configured GitHub repository URLs" subsection.
2. The new fields' text matches the proposed text byte-for-byte.
3. The Source field is appended to (not replaced); existing attribution string preserved verbatim.
4. All seven new tests in `tests/governance/test_canonical_terminology_agent_red.py` pass.
5. The implementation Edit was preceded by a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-canonical-terminology-agent-red.json` whose `body_hash` matches the post-edit body.
6. `python scripts/release_candidate_gate.py` passes.
7. No other entry in `canonical-terminology.md` is modified.

## Pre-Filing Applicability Preflight

Will run after this proposal is filed and INDEX entry is in place; final preflight result and `packet_hash` recorded post-revision in this section.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
