# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 2: Bridge Template Pre-Population (REVISED)

- Status: REVISED
- Date: 2026-05-09
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 2 of multi-phase plan)
- Supersedes: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md` (NO-GO at `-002`).
- Depends on: Phase 0 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`. Phase 1 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-010.md`. Phase 1 is now load-bearing for Phase 2's S331 replay test (per F2 of `-002` resolution: the helper reads the Phase 1 glossary's `Source:` block to deterministically seed candidate DELIB IDs).

## Revision Notes

This revision addresses Loyal Opposition findings F1 and F2 from `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-002.md`:

- **F1 (P1) — Missing skill-adapter and template parity scope.** Implementation scope expanded to include all parity-required surfaces per `config/agent-control/harness-capability-registry.toml:60-77` registration of `skill.bridge-propose`. Added to scope: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`, `groundtruth-kb/templates/skills/bridge-propose/SKILL.md`, `.codex/skills/bridge-propose/SKILL.md`, and the `scripts/generate_codex_skill_adapters.py --update-registry --check` regeneration step. Parity-verification test added.
- **F2 (P1) — S331 replay test not supported by current retrieval mechanism.** Codex's evidence: a plain `search_deliberations("isolation", limit=10)` returns only `DELIB-0877` from the four anchor set; `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` is not in the top 10. Resolution: helper design adds a **glossary-source seeding** step that runs *before* the semantic search. When the topic slug matches a canonical glossary heading in `.claude/rules/canonical-terminology.md`, the helper reads that heading's `Source:` block and extracts exact `DELIB-*` and MemBase spec IDs as deterministic seed candidates. Semantic search results are added on top of the seeds, deduplicated. The S331 replay test verifies the glossary-source-seeding mechanism returns the four anchor DELIB IDs deterministically. This makes Phase 1 (glossary backfill) structurally load-bearing for Phase 2: the glossary is the read surface; the bridge-propose helper consumes it. This wiring is the intended Phase 0 placement-pattern outcome.

## Summary

Extend the bridge-propose helper (`.claude/skills/bridge-propose/helpers/write_bridge.py`) to query the Deliberation Archive at template-creation time and pre-populate the proposal's `Prior Deliberations` section with relevant DA records. Convert the cognitive operation from "remember to populate the section" (failure-prone) to "review and prune the pre-populated section" (much more reliable). This is the bridge-template-side instance of the placement principle (`ADR-DA-READ-SURFACE-PLACEMENT-001` Path D — bridge templates pre-populated).

The proposal also adds a Loyal Opposition review check that NO-GOs proposals with empty `Prior Deliberations` sections lacking explicit justification.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger via rule-file references; no scope conflict)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` (extended to narrative artifacts via Slice A of `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001`) — Phase 2 modifies `.claude/rules/codex-review-gate.md`, which is in the protected narrative-artifact set per `config/governance/narrative-artifact-approval.toml`. The implementation pattern below adopts the narrative-artifact-packet workflow proven in Phase 1.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` (extended)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Phase 0 framing (`specified` in MemBase):

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — Phase 2 implements the bridge-template-side mechanism this principle covers.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — bridge-template pre-population is one of the named placement targets in the chosen Path D.
- `DCL-CONCEPT-ON-CONTACT-001` — proposals that introduce new concepts are subject to Stage B detection (Phase 6); Phase 2's helper change is not the Stage B detection but is adjacent.

Topic-specific:

- `.claude/rules/deliberation-protocol.md` — Prior Deliberations section requirement; the helper change makes the section reliably populated.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol authority.
- `.claude/rules/codex-review-gate.md` — review-gate rule that gains a new check (Change 3 below).
- `.claude/skills/bridge-propose/SKILL.md` — current helper documentation; updated to reflect pre-population behavior.
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — current helper code; extended with the new function.
- `SPEC-2098`, `ADR-008` — Deliberation Archive authority.
- Bridge thread `gtkb-narrative-artifact-approval-extension-001` (VERIFIED) — establishes the narrative-artifact gate Phase 2 must use for the codex-review-gate.md edit.

## Prior Deliberations

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — S331 owner-decision foundations (placement-over-coercion, glossary-as-DA-read-surface, bridge templates pre-populated as a placement target).
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879` — anchor deliberations for the `isolation` concept that demonstrate why pre-population matters (S331 wrong-frame failure).
- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` — adjacent canonical-terminology framing.
- `DELIB-0722` — original canonical-terminology-surface bridge thread.
- `DELIB-0835` — strict artifact approval discipline.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` — owner-visible capture transparency.

S331 in-session decisions: same set as Phase 0 and Phase 1 (begin/parallelize, cost-irrelevant, quality-and-completeness-only, owner-direction-via-AUQ).

Phase 0 and Phase 1 closure deliberations:

- Phase 0 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`.
- Phase 1 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-010.md`.
- Approval-packet evidence pattern proven in Phase 1 (preview file → AUQ → packet → write).

## Owner Decisions / Input

Authorizing context:

- Phase 0 VERIFIED + four Phase 0 artifacts at `specified` in MemBase.
- Phase 1 VERIFIED + glossary backfill landed.
- 2026-05-08 owner direction (S331): "Please begin. Please parallelize this work to the extent possible."
- 2026-05-09 owner direction (S331 continuation): "Please continue."

Future owner approvals this proposal will surface (each via `AskUserQuestion`):

1. **Approval of the helper extension behavior** (the DA-query algorithm parameters: similarity threshold, top-N, marker text, log path). Surfaced in the implementation step alongside test results.
2. **Narrative-artifact approval for `.claude/rules/codex-review-gate.md`** edit. Pattern: Prime writes the proposed full new content of `codex-review-gate.md` to a non-canonical preview file at `memory/codex-review-gate-md-rewrite-preview.md` *before* the AUQ; the owner reviews that file directly; the AUQ explicitly asks whether the owner reviewed that exact path + sha256 and approves writing the same content to `.claude/rules/codex-review-gate.md`. Required before the rule-file write. Same pattern Phase 1 used for canonical-terminology.md (proven in Phase 1 VERIFIED).

Items 1 and 2 are surfaced separately (one AUQ at a time per durable preference). The helper-code change (item 1) does not require a narrative-artifact packet (the file is `.claude/skills/bridge-propose/helpers/write_bridge.py`, code, not a narrative-authority `.md`). The SKILL.md update is in `.claude/skills/`, not `.claude/rules/`, and is therefore also outside the protected narrative-artifact set per `config/governance/narrative-artifact-approval.toml`.

## Proposed Changes

### Change 1: Extend `.claude/skills/bridge-propose/helpers/write_bridge.py`

Add a `pre_populate_prior_deliberations(topic_slug, body, *, limit=N, threshold=T, log_path=...)` function that combines **glossary-source seeding** (deterministic; the F2 fix) with **semantic search** (broad coverage):

1. Extract a search query from the topic slug (kebab-case to space-separated noun phrase) and the proposal's `## Summary` section if present (first paragraph).
2. **Glossary-source seeding (deterministic)**: read `.claude/rules/canonical-terminology.md`. Convert the topic slug to a candidate glossary heading (kebab-case → space-separated noun phrase, e.g., `"isolation"` → `"isolation"`; `"da-read-surface-placement"` → `"DA read surface placement"` or `"glossary as DA read surface"`). If a `### <heading>` matches in the glossary file, locate that heading's `Source:` line and parse out all matching tokens (regex on `DELIB-[A-Z0-9-]+`, `(GOV|ADR|DCL|PB|SPEC|REQ)-[A-Z0-9-]+`). Each extracted ID becomes a **seed candidate**.
3. **Semantic search (broad coverage)**: query the DA via `groundtruth_kb.db.KnowledgeDB.search_deliberations(query, limit=limit)` with `limit` configurable (default 5) and a similarity threshold configurable (default low). Results become **search candidates**.
4. **Combine and deduplicate**: union of (seeds, search). Seeds are surfaced first in the populated section because they are the canonical anchor for the topic; search candidates follow.
5. Locate the `## Prior Deliberations` section in the proposal body (or insert one if absent, just below `## Specification Links`).
6. Prepend pre-populated entries with the marker comment `<!-- Pre-populated by helper; review and prune. -->`. Each entry is formatted as:

   ```
   - DA: `<id>` — <source_type>, captured <date>. <one-line summary if available>. [seed=glossary | seed=search]
   ```

7. If the section is non-empty before the call (the author has already populated some entries), the helper appends candidates below a `### Helper-suggested candidates` subheading rather than overwriting prior author content.

8. The helper logs its query + match list to a session-state file (`.gtkb-state/bridge-propose-helper/last-prepopulation.json`) for audit. The log records: timestamp, topic slug, derived query, glossary-seed IDs, search-result IDs, similarity scores, threshold used.

9. The function exposes a kwarg `pre_populate_prior_deliberations=True` (default) on the existing `propose_bridge()` entry point. Callers can opt out with `pre_populate_prior_deliberations=False`; opt-out callers must include a justification line in the section: `_No prior deliberations: <reason>._` (mirrors the empty-justification convention).

The glossary-source-seeding step is what makes the S331 replay deterministic: the topic slug `"isolation"` matches the `### isolation` heading; the heading's `Source:` block contains `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, "S321 owner directive", `DELIB-0879`, and `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`; the helper extracts all five and seeds them into the populated section regardless of semantic-search ranking.

### Change 2: Update `.claude/skills/bridge-propose/SKILL.md`

Add a "Prior Deliberations pre-population" section to SKILL.md documenting:

- The default behavior (helper performs glossary-source seeding, then semantic search; pre-populates section; marks for pruning).
- The opt-out flag and the empty-justification requirement.
- The audit log location and format.
- The author's pruning responsibility.
- The relationship to the LO review-side check (Change 3).
- The dependency on `.claude/rules/canonical-terminology.md` for glossary-source seeding.

### Change 2a: Update parity-required surfaces (per F1 of `-002`)

Per the `skill.bridge-propose` parity registration at `config/agent-control/harness-capability-registry.toml:60-77`, the canonical Claude SKILL is `adapter_source` for the Codex adapter. After Changes 1-2 land in the canonical files, regenerate and propagate:

- Update `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` to mirror Change 1 (scaffold template for new GT-KB installations).
- Update `groundtruth-kb/templates/skills/bridge-propose/SKILL.md` to mirror Change 2.
- Run `python scripts/generate_codex_skill_adapters.py --update-registry --check` (and the non-`--check` form to actually regenerate) to propagate the canonical Claude SKILL into the Codex adapter at `.codex/skills/bridge-propose/SKILL.md`.
- Verify the harness-capability-registry hash/check fields are updated.

### Change 3: Codex review-side check (rule-file edit on `.claude/rules/codex-review-gate.md`)

Add a sixth review obligation in `.claude/rules/codex-review-gate.md`: when reviewing a `NEW` or `REVISED` entry, if the proposal's `Prior Deliberations` section is empty or absent AND no `_No prior deliberations: <reason>._` line is present, Loyal Opposition issues `NO-GO` with the documented finding. This check rides the existing review path; it does not introduce a new gate or hook.

The rule-file edit is governed by `GOV-ARTIFACT-APPROVAL-001` (extended to narrative artifacts) and follows the Phase-1-proven preview-file → AUQ → narrative-artifact-packet → write pattern (see § Implementation Pattern below).

## Implementation Pattern (revised per F1 of `-002`)

After Phase 2 GO arrives:

1. **Helper code change** (Change 1): Edit `.claude/skills/bridge-propose/helpers/write_bridge.py`. Code file, not a narrative artifact; direct Write (subject to scanner-safe-writer credential-scan hook only).
2. **SKILL.md update on canonical** (Change 2): Edit `.claude/skills/bridge-propose/SKILL.md`. Skill files are outside the narrative-artifact protected set; direct Write.
3. **Parity propagation** (Change 2a):
   1. Edit `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` to mirror Change 1.
   2. Edit `groundtruth-kb/templates/skills/bridge-propose/SKILL.md` to mirror Change 2.
   3. Run `python scripts/generate_codex_skill_adapters.py --update-registry` to regenerate `.codex/skills/bridge-propose/SKILL.md` from the canonical Claude SKILL and update the harness-capability-registry hash.
   4. Run `python scripts/generate_codex_skill_adapters.py --update-registry --check` to verify parity (post-regenerate sanity check).
4. **Test creation**: Write `tests/skills/test_bridge_propose_helper.py` covering the tests in § Test Plan. Code file; direct Write.
5. **Rule-file edit on `.claude/rules/codex-review-gate.md`** (Change 3): protected narrative artifact. Apply the Phase-1-proven pattern:
   1. Read current `.claude/rules/codex-review-gate.md`; compute `current_file_sha256`.
   2. Compute new full content with the sixth review obligation added; compute `new_file_sha256`.
   3. Write the full proposed new content to `memory/codex-review-gate-md-rewrite-preview.md`.
   4. Inform owner of preview path + sha256 in assistant text; direct review.
   5. AUQ explicitly: "Have you reviewed the proposed full new content at `memory/codex-review-gate-md-rewrite-preview.md` (sha256 `<new_file_sha256>`), and do you approve writing this exact content to `.claude/rules/codex-review-gate.md`?" with options "I have reviewed and approve" / "Hold for revision" / "Reject".
   6. On approval, generate narrative-artifact packet at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-codex-review-gate-md.json` with `full_content`, `full_content_sha256`, `presented_to_user=true`, etc.
   7. Write the protected file.
   8. Verify with `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/codex-review-gate.md`.
6. **Run tests**: `python -m pytest tests/skills/test_bridge_propose_helper.py -v`.
7. **File implementation report** (next bridge version after Codex VERIFIED on this proposal) with: helper code diff summary, SKILL.md diff summary (canonical + template), Codex adapter regeneration evidence (`generate_codex_skill_adapters.py --check` output), codex-review-gate.md preview path + sha256 + packet hash, test results, S331-replay glossary-source-seeding verification.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 2 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Bridge templates are demonstrably populated with DA references when DA records exist for the topic. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | One of the named placement targets (bridge templates) is implemented. |
| `.claude/rules/deliberation-protocol.md` | `Prior Deliberations` section is populated by the helper without author intervention. |
| `.claude/rules/codex-review-gate.md` | Sixth review obligation is added; LO NO-GOs proposals with empty Prior Deliberations sections lacking justification. |
| `GOV-ARTIFACT-APPROVAL-001` (extended) | Narrative-artifact packet exists for `codex-review-gate.md` rule-file edit; packet `full_content_sha256` matches the post-write file's sha256. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests below execute against the helper change. |

Tests (in `tests/skills/test_bridge_propose_helper.py`):

1. *Glossary-source-seeding unit test (the F2 grounding)*: invoke the helper's seeding step with topic slug `"isolation"`. Verify the seed-extraction step reads `### isolation` from `.claude/rules/canonical-terminology.md`, parses the `Source:` block, and returns the deterministic seed set: `{DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT, DELIB-0877, DELIB-0879, DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS}` (the four DELIB-IDs explicitly cited; "S321 owner directive" is by-title and may be returned as-is or filtered to ID-shaped tokens — the test asserts the four ID-shaped tokens are returned). This is the deterministic substitute for plain semantic search; it grounds the S331 replay test mechanically.
2. *Helper unit test — known-DA-match topic*: invoke the full helper (seeding + search) with topic slug `"isolation"`. Verify the populated `Prior Deliberations` section contains the four anchor DELIB-IDs (from seeding) regardless of semantic-search ranking, and additional candidates from semantic search.
3. *Empty-section integration test*: invoke the helper with a topic slug that does not match any glossary heading and has no DA semantic matches above threshold (e.g., a synthetic novel topic). Verify the section contains the `_No prior deliberations: <reason>._` placeholder or a justification request.
4. *Override flag test*: invoke with `pre_populate_prior_deliberations=False`. Verify the section is left untouched.
5. *S331-replay regression (the F2 acceptance test)*: simulate authoring a bridge proposal on the topic `"isolation"` with the pre-population helper enabled. Verify the helper would have surfaced all four lifecycle-independence DELIB-IDs that the original S331 evaluation missed. The mechanism is glossary-source seeding; the test asserts seed-set membership, not semantic-search ranking.
6. *Audit log test*: invoke the helper; verify `.gtkb-state/bridge-propose-helper/last-prepopulation.json` is written with the expected schema (timestamp, topic slug, query, glossary-seed IDs, search-result IDs, similarity scores, threshold used).
7. *Parity check (the F1 acceptance test)*: run `python scripts/generate_codex_skill_adapters.py --update-registry --check` after the implementation. Verify exit 0 and that the canonical Claude SKILL hash matches the registered hash in `config/agent-control/harness-capability-registry.toml`.
8. *Template parity check*: verify `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and `groundtruth-kb/templates/skills/bridge-propose/SKILL.md` contain the new `pre_populate_prior_deliberations` function and Prior-Deliberations-pre-population section respectively (string-presence assertions).
9. *Codex review check (manual integration test)*: file a draft proposal with an empty `Prior Deliberations` section and no `_No prior deliberations:_` justification line; verify the LO review path NO-GOs with the documented finding (this test is documented in the implementation report rather than automated, since it requires LO harness invocation).

## Risk and Rollback

Risks:

- *DA query latency at template creation.* Mitigation: helper invoked at proposal-creation time only; a few hundred milliseconds is acceptable. The helper logs query duration for monitoring.
- *Pre-populated entries are irrelevant or noisy.* Mitigation: marker comment `<!-- Pre-populated by helper; review and prune. -->` makes pruning responsibility explicit; LO review path does not require all pre-populated entries to remain after authoring.
- *Helper changes break the credential-scan-safe-writer pathway.* Mitigation: changes are localized to a new function; existing `propose_bridge()` flow is unchanged. The new function does not call any credential-handling code.
- *codex-review-gate.md rule edit conflicts with concurrent edits from other bridge work.* Mitigation: read-modify-write at implementation time; the narrative-artifact-packet hash binds the exact content approved.

Rollback: helper code reverted via git; SKILL.md edit reverted; rule-file edit reverted (and superseded by a new packet if subsequent change). No persistent state outside the audit log file (which can be deleted).

## Recommended Commit Type

`feat:` — new helper capability (DA query + section pre-population) + new LO review obligation. Existing helper behavior is preserved as the no-op fallback.

## Files Changed

This proposal's commit will include:

- `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-001.md` (this file; new)
- `bridge/INDEX.md` (NEW entry inserted at top)

Phase 2 implementation (after Codex GO):

Canonical Claude surfaces:
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — extended with `pre_populate_prior_deliberations` function (glossary-source seeding + semantic search).
- `.claude/skills/bridge-propose/SKILL.md` — documentation update.

Parity-required surfaces (per F1 of `-002`):
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` — mirrors Change 1 (scaffold template).
- `groundtruth-kb/templates/skills/bridge-propose/SKILL.md` — mirrors Change 2 (scaffold template).
- `.codex/skills/bridge-propose/SKILL.md` — regenerated by `scripts/generate_codex_skill_adapters.py --update-registry`.
- `config/agent-control/harness-capability-registry.toml` — hash field updated by the regeneration script.

Protected narrative artifact (Change 3):
- `.claude/rules/codex-review-gate.md` — sixth review obligation added (narrative-artifact-packet-gated).
- `memory/codex-review-gate-md-rewrite-preview.md` — non-canonical preview file for narrative-artifact approval.
- `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-codex-review-gate-md.json` — narrative-artifact approval packet.

Tests:
- `tests/skills/test_bridge_propose_helper.py` — new test file covering tests 1-8 in § Test Plan.

Implementation report:
- `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-NNN.md` — implementation report (next bridge version after GO).

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-2-template-pre-population --json` (after REVISED INDEX entry in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:f0cb500a0431c113a02c3cfea1393a6f3a5cf91dd2e984c56a1a90bb9102f454`

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-2-template-pre-population`:

- Exit code: `0` (pass)
- Operative file: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-003.md`
- Clauses evaluated: 5; must_apply: 4 (all with evidence); may_apply: 1; blocking gaps: 0.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
