# DRAFT — Phase 2 Bridge Proposal: Bridge Template Pre-Population

**Status:** working draft. Not filed. Becomes `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md` after Phase 0 GO + the four formal artifacts are owner-approved into MemBase.

---

# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 2: Template Pre-Population

- Status: NEW
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 2 of multi-phase plan)
- Depends on: Phase 0 GO + MemBase insertion of Phase 0 formal artifacts. Phase 1 not strictly required, but improves match quality.

## Summary

Extend the bridge-propose helper (`.claude/skills/bridge-propose/helpers/write_bridge.py`) to query the Deliberation Archive at template-creation time and pre-populate the proposal's `Prior Deliberations` section with relevant DA records. Convert the cognitive operation from "remember to populate the section" (failure-prone) to "review and prune the pre-populated section" (much more reliable).

The proposal also adds a Loyal Opposition review check that NO-GOs proposals with empty `Prior Deliberations` sections lacking explicit justification.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger; no scope conflict)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Phase 0 framing:

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — Phase 2 implements the bridge-template-side mechanism that the GOV principle covers.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — bridge templates are one of the named placement targets.

Topic-specific:

- `.claude/rules/deliberation-protocol.md` — Prior Deliberations section requirement.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol and template authority.
- `.claude/skills/bridge-propose/SKILL.md` — current helper documentation.
- `SPEC-2098`, `ADR-008` — DA authority.

## Prior Deliberations

- DA: "Canonical Terminology System accepted as GT-KB feature framing" — 2026-05-07.
- DA: "Bridge thread: gtkb-canonical-terminology-surface-implementation (12 versions, VERIFIED)".
- DA (S331): glossary-as-read-surface owner agreement.
- DA: prior bridge-propose helper bridge thread (whichever VERIFIED thread established the credential-scan-safe writer pattern).

S331 in-session decisions: same set as Phase 0; this proposal is downstream.

## Owner Decisions / Input

Authorizing context: Phase 0 GO + MemBase insertion of Phase 0 artifacts.

Future owner approvals this proposal will surface:

1. Approval of the helper extension behavior (the DA-query algorithm, similarity threshold, top-N).
2. Approval of the Codex review-side check for empty Prior Deliberations sections.

## Proposed Changes

### Change 1: Extend `helpers/write_bridge.py`

Add a `pre_populate_prior_deliberations(topic_slug, body)` function that:

1. Extracts a search query from the topic slug + the proposal's `Summary` section (if present).
2. Queries the DA via `groundtruth_kb.db.KnowledgeDB.search_deliberations(query, limit=N)` with N configurable, default 5, similarity threshold configurable, default low (catch wide net; let author prune).
3. Locates the `## Prior Deliberations` section in the proposal body (or inserts one if absent).
4. Prepends pre-populated entries with the marker comment `<!-- Pre-populated by helper; review and prune. -->`. Each entry is formatted as:

   ```
   - DA: "<title>" — <source_type>, <captured_at>. <one-line summary if available>.
   ```

5. If the section is non-empty pre-call (author has already populated some entries), the helper appends candidates below a `### Helper-suggested candidates` subheading rather than overwriting.

6. The helper logs its query + match list to a session-state file (`.gtkb-state/bridge-propose-helper/last-prepopulation.json`) for audit.

### Change 2: Update `.claude/skills/bridge-propose/SKILL.md`

Add a section documenting the pre-population behavior, the pruning responsibility, and the override flag (`pre_populate_prior_deliberations=False` for callers who genuinely want an empty section, e.g., novel topics with no DA precedent — those callers must include a justification line in the section: `_No prior deliberations: <reason>._`).

### Change 3: Codex review-side check

Add a check in the Loyal Opposition review path: when reviewing a NEW or REVISED entry, if the proposal's `Prior Deliberations` section is empty or absent AND no `_No prior deliberations: <reason>._` line is present, NO-GO with the finding. This check rides the existing review path; it does not introduce a new gate.

The check is documented in `.claude/rules/codex-review-gate.md` as a sixth review obligation.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 2 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Bridge templates are demonstrably populated with DA references when DA records exist for the topic. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Verifies one of the named placement targets is implemented. |
| `.claude/rules/deliberation-protocol.md` | Prior Deliberations section is populated by the helper without author intervention. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests below execute against the helper change. |

Tests:

1. *Helper unit test*: invoke the helper with a topic slug that has known DA matches (e.g., "isolation"); verify the Prior Deliberations section contains the four lifecycle-independence DA records.
2. *Empty-section integration test*: invoke the helper with a topic slug that has no DA matches; verify the section contains only the `_No prior deliberations: <reason>._` placeholder or a justification request.
3. *Override flag test*: invoke with `pre_populate_prior_deliberations=False`; verify the section is left untouched.
4. *S331-replay regression*: simulate authoring a bridge proposal on the topic "isolation"; verify the helper would have surfaced the four DA records that S331 missed.
5. *Codex review check*: file a draft proposal with an empty Prior Deliberations section and no justification; verify the LO review path NO-GOs with the documented finding.

## Risk and Rollback

Risks:

- DA query latency at template creation. Mitigation: the helper is invoked at proposal-creation time (not in a tight loop); a few hundred milliseconds is acceptable.
- Pre-populated entries are irrelevant or noisy. Mitigation: marker comment `<!-- Pre-populated by helper; review and prune. -->` makes the author's pruning responsibility explicit; the LO review path does not require all pre-populated entries to remain.
- Helper changes break the credential-scan-safe-writer pathway. Mitigation: changes are localized to a new function; existing `propose_bridge()` flow is unchanged.

Rollback: helper code is reverted via git; SKILL.md edit is reverted; rule edit is reverted. No persistent state.

## Recommended Commit Type

`feat:` — new helper capability (DA query + section pre-population). Existing helper behavior is preserved.

## Files Changed

- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `.claude/skills/bridge-propose/SKILL.md`
- `.claude/rules/codex-review-gate.md`
- `tests/skills/test_bridge_propose_helper.py` (new) — covering the four unit/integration tests above.
- `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md` (this proposal)
- `bridge/INDEX.md`

## Applicability Preflight

To be populated against the live bridge file.

## Clause Applicability

To be populated by clause preflight after INDEX entry.
