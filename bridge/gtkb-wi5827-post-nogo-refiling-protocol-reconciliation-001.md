NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched by the Harness Test Corrections program leader under owner mandate DELIB-202667735; this filing is a Prime Builder proposal-authoring act (envelope pb); the parent interactive session's resolver fallback reports loyal-opposition; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5827-post-nogo-refiling-protocol-reconciliation
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5827

target_paths: ["scripts/bridge_lifecycle_resolver.py", "config/agent-control/gtkb-file-bridge-protocol.md", ".claude/rules/file-bridge-protocol.md", ".claude/skills/gtkb-verify/SKILL.md", ".codex/skills/gtkb-verify/SKILL.md", "platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py", ".groundtruth/formal-artifact-approvals/**"]
implementation_scope: transition_table_authority_extraction_prose_correction_lo_remedy_codification_and_doc_code_consistency_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5827 Implementation Proposal — Post-NO-GO Refiling Protocol Reconciliation: One Authoritative Transition Table

## Summary

Reconcile the lawful post-`NO-GO` Prime Builder refiling status across the three surfaces that currently disagree: (a) the lifecycle resolver code of record (`scripts/bridge_lifecycle_resolver.py`), which rejects `NO-GO -> NEW`; (b) the file-bridge-protocol prose, whose § Post-Implementation Verification unconditionally instructs publishing a `NEW` verification-request entry with no post-`NO-GO` branch; and (c) the Loyal Opposition verdict/remedy template surface (`.claude/skills/gtkb-verify/SKILL.md`), which scaffolds `NO-GO` `## Required Revisions` sections without ever stating the required refile status token. The contradiction — not Prime Builder error — caused the live r2b second wedge on 2026-07-30 (evidence below). The fix extracts the resolver's transition table into a single module-level authoritative constant, corrects the canonical protocol prose (and its generated projection) to state that post-`NO-GO` reports are refiled as `REVISED` (never `NEW`), codifies the canonical post-`NO-GO` remedy sentence in the LO verdict template (feeding WI-5816's verdict-procedure hardening), and adds a doc-code consistency test that guards the table on every surface (TEST-11783).

This proposal is filed as `bridge/gtkb-wi5827-post-nogo-refiling-protocol-reconciliation-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files under `bridge/` form the canonical audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and this thread's own chain will evolve strictly by appending next-numbered files.

## Problem Statement And Live Evidence (fresh reads, 2026-07-30)

All quotes below were re-derived this session from the live worktree.

### 1. The code of record: resolver transition table rejects NO-GO -> NEW

`_validate_ordinary_transitions()` in `scripts/bridge_lifecycle_resolver.py` (lines 421-446) builds the allowed-successor sets inline:

```python
if previous.status in {"NEW", "REVISED"}:
    allowed = {"GO", "NO-GO", "WITHDRAWN", "DEFERRED"}
    # A Prime NEW filed after a GO is normally an implementation report. ...
    if previous.status == "NEW" and prior_go_seen:
        allowed.add("REVISED")
    if prior_go_seen:
        allowed.add("VERIFIED")
elif previous.status == "GO":
    allowed = {"NEW", "REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}
elif previous.status == "NO-GO":
    allowed = {"REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}
elif previous.status == "NO-ACTION":
    allowed = {"GO", "NO-GO", "VERIFIED"}
elif previous.status == "ADVISORY":
    allowed = {"ADVISORY", "ACCEPTED", "BLOCKED", "DEFERRED", "WITHDRAWN"}
elif previous.status in {"BLOCKED", "DEFERRED"}:
    allowed = {"REVISED", "WITHDRAWN"}
```

A disallowed successor fails at lines 448-454 with:

```python
_fail(
    "INVALID_BRIDGE_TRANSITION",
    f"Invalid bridge transition {previous.status} -> {current.status}",
    ...
)
```

Post-`NO-GO`, the lawful Prime statuses are `REVISED` (corrected proposal or corrected implementation report) and `NO-ACTION` (Prime rejection of a governance-non-compliant verdict per DCL-NO-ACTION-STATUS-SEMANTICS-001); `DEFERRED` (owner parking) and `WITHDRAWN` (terminal) complete the set. `NEW` is never lawful after `NO-GO`.

### 2. The contradicting prose (canonical source and projection, byte-identical)

`config/agent-control/gtkb-file-bridge-protocol.md` § Post-Implementation Verification (lines 417-424; the `.claude/rules/file-bridge-protocol.md` projection carries the identical text at the same lines):

```
## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Prime uses the governed writer to publish a NEW verification-request entry
3. Loyal Opposition reviews and responds with NO-GO, or records VERIFIED only
   through the commit-finalization helper so the verified work, implementation
   report, and verdict artifact enter git history in the same local commit.
```

Step 2 states `NEW` unconditionally for every verification request and the section has no post-`NO-GO` branch at all: step 3 anticipates an LO `NO-GO` on the report but the section never says what status the corrected report takes. The protocol's only `NO-GO`-response guidance is § Prime Workflow step 6 (lines 404-405), which is proposal-scoped: "On NO-GO: read the NO-GO file, address findings, save revised file with incremented version, and use the governed writer to publish a REVISED state." An agent following § Post-Implementation Verification literally — every verification request is `NEW` — collides with the resolver.

Projection provenance (verified fresh, per the WI-5664 lesson): `config/file-reference-migration/wi5640.toml` lines 970-974 record `source = ".claude/rules/file-bridge-protocol.md"`, `canonical = "config/agent-control/gtkb-file-bridge-protocol.md"`, `class = "canonical_authority"`. The one-way generator `scripts/generate_rule_compatibility_projections.py` states: "Canonical rule content lives under `config/agent-control/gtkb-*`. ... it never reads a retained projection as authority and never mutates a canonical file." The prose fix therefore targets the canonical `config/agent-control/gtkb-file-bridge-protocol.md` and regenerates the `.claude/rules/file-bridge-protocol.md` projection through that generator; both paths are declared in `target_paths` so the regeneration lands within exact target-path enforcement.

### 3. The LO remedy template gap

`.claude/skills/gtkb-verify/SKILL.md` (canonical skill source; `.codex/skills/gtkb-verify/SKILL.md` is its generated adapter) scaffolds the `NO-GO` verdict shape at lines 158-159: "`## Required Revisions` — for a `NO-GO` verdict only; the finding-by-finding required changes Prime Builder must address before resubmitting." Nowhere does the skill state the status token the resubmission must carry. With no codified remedy sentence, each LO session improvises — and on 2026-07-30 one improvised wrong.

### 4. The live wedge (r2b chain, 2026-07-30)

- **Wrong remedy issued.** `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2b-006.md` (LO `NO-GO`, line 24): "Refile the same implementation report as `NEW` (exact Responds-to GO-004), keep target_paths and evidence, then LO can issue VERIFIED on a live packet." Required Revisions item 1 (line 78): "Refile the implementation report with status token `NEW` (not `NO-ACTION`)."
- **Wedge.** Prime followed that remedy and filed 007 as `NEW`; the resolver rejected the chain. The unpublished LO NO-GO-008 draft (`.gtkb-state/lo-verdicts/file_dsv4pro_r2b_nogo008.py`, F1 observation, line 135) records: "Packet consultation: `AuthorizationError: Invalid bridge transition NO-GO -> NEW`; `evidence_valid=False` with the same reason."
- **LO self-correction (unpublished).** Same draft, line 111: "Correction to prior LO guidance in 006: asking for `NEW` after NO-GO was wrong for this transition table; `REVISED` is the required post-NO-GO Prime status."
- **Aftermath on disk.** `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2b-007.md` now carries the owner-authorized repair, Revision Note: "status token corrected `NEW` → `REVISED` so the chain obeys `NO-GO → REVISED` (`scripts/bridge_lifecycle_resolver.py`). ... after LO NO-GO-006 the lawful Prime status is `REVISED`, not `NEW`."

The WI-5827 record (MemBase, fresh read) states the diagnosis: the contradiction — not Prime Builder error — caused the second wedge. Both the LO remedy and the Prime refiling were each locally consistent with a different surface; only the resolver is load-bearing at packet-consultation time, so the disagreement converts a routine correction loop into a hard wedge.

## Design

### D1. Resolver: extract the authoritative transition table (behavior-preserving)

`scripts/bridge_lifecycle_resolver.py` gains module-level constants that become the single in-code authority:

- `ORDINARY_TRANSITIONS: dict[str, frozenset[str]]` — the base allowed-successor map exactly as the inline sets read today (`NEW`/`REVISED`, `GO`, `NO-GO`, `NO-ACTION`, `ADVISORY`, `BLOCKED`/`DEFERRED` rows).
- `POST_GO_REPORT_AUGMENTATIONS` — the two documented `prior_go_seen` augmentations (post-GO `NEW` additionally allows `REVISED`; post-GO `NEW`/`REVISED` additionally allow `VERIFIED`), kept as data with the existing explanatory comment moved alongside.

`_validate_ordinary_transitions()` is refactored to consume the constants. No allowed set changes; the existing suite `platform_tests/scripts/test_bridge_lifecycle_resolver.py` must remain green unmodified, which is the behavior-preservation proof.

### D2. Canonical prose correction + authoritative table section

In `config/agent-control/gtkb-file-bridge-protocol.md`:

1. § Post-Implementation Verification is corrected to distinguish the first post-GO report from post-NO-GO corrections: the first post-implementation report publishes as `NEW`; after a Loyal Opposition `NO-GO` on a report, the corrected report publishes as `REVISED` — never `NEW` — mirroring § Prime Workflow step 6.
2. A new `## Post-Verdict Transition Table` section renders the full `ORDINARY_TRANSITIONS` map (plus the two post-GO augmentations) as a markdown table with a stable heading, explicitly sourced to `scripts/bridge_lifecycle_resolver.py` as the code of record. The table states in prose: post-`NO-GO`, lawful Prime statuses are `REVISED` and `NO-ACTION` (per DCL-NO-ACTION-STATUS-SEMANTICS-001); `DEFERRED` and `WITHDRAWN` are the owner/terminal complements; `NEW` is never a lawful successor to `NO-GO`.

`.claude/rules/file-bridge-protocol.md` is then regenerated via `scripts/generate_rule_compatibility_projections.py` (one-way, canonical-to-projection). No hand edit of the projection occurs.

### D3. LO remedy codification (feeds WI-5816)

`.claude/skills/gtkb-verify/SKILL.md` gains a canonical remedy sentence in the `NO-GO` verdict scaffolding: a `NO-GO` verdict's `## Required Revisions` section MUST instruct Prime Builder to refile the corrected report as `REVISED` (citing the transition table), and MUST NOT instruct a `NEW` refile after `NO-GO`. The `.codex/skills/gtkb-verify/SKILL.md` adapter is regenerated from the canonical skill source. WI-5816 (verdict-procedure hardening: copy-aware review, provenance resolution, filename validity) will build its hardened procedure on top of this codified remedy language; this slice deliberately adds only the transition-remedy sentence and leaves WI-5816's additional steps to that thread.

### D4. Doc-code consistency test (TEST-11783)

New `platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py`:

- Parses the `## Post-Verdict Transition Table` markdown table from the canonical `config/agent-control/gtkb-file-bridge-protocol.md` AND from the `.claude/rules/file-bridge-protocol.md` projection, asserting each equals `ORDINARY_TRANSITIONS` (+ augmentations) imported from the resolver.
- Regression-asserts the `NO-GO` row does not contain `NEW` (the exact wedge class).
- Asserts § Post-Implementation Verification names `REVISED` as the post-NO-GO report status and no longer instructs an unconditional `NEW`.
- Asserts `.claude/skills/gtkb-verify/SKILL.md` contains the codified `REVISED` remedy sentence and contains no instruction to refile as `NEW` after `NO-GO`.

### Explicitly out of scope

- No change to any allowed transition. This is reconciliation to the existing resolver semantics, not a semantics change; if review concludes any transition should itself change, that is a separate owner-decision thread.
- No dispatcher or TAFE mutation (forbidden operation under the PAUTH); no dispatch-eligibility or routing change.
- No repair, rewrite, or deletion of any existing bridge chain file. The r2b chain and the unpublished NO-GO-008 draft are cited read-only as evidence; the numbered files remain the append-only audit trail.
- No MemBase formal-artifact insert/update (no new GOV/ADR/DCL/SPEC rows).
- WI-5816's broader verdict-procedure hardening (sibling-diff, session-id resolution, filename validity, claim-holder consistency) stays in WI-5816.

### Rejected alternatives

- **Change the resolver to accept `NO-GO -> NEW`** — rejected: the resolver's rule is correct and consistent with § Prime Workflow step 6 and the `REVISED` status definition ("Updated proposal after a NO-GO"); loosening the code of record to match defective prose inverts the authority relationship.
- **Prose-only fix without the extracted constant and consistency test** — rejected: the drift already recurred once between prose and code; without a machine-checked bind, the next prose edit can silently reintroduce it (WI-5827's linked TEST-11783 explicitly requires the guard).
- **Hand-editing the `.claude/rules/` projection directly** — rejected per the WI-5664 lesson and the one-way generator contract: canonical authority lives at `config/agent-control/gtkb-file-bridge-protocol.md`; the projection must only ever be regenerated.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking): bridge audit-trail and protocol authority; WI-5827's source spec; the append-only numbered chain this reconciliation protects.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking): protected narrative rule-file edit requires its own per-artifact formal-artifact approval packet at implementation time.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — required (blocking): governs the NO-ACTION branch the transition table documents as the lawful post-NO-GO alternative to REVISED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking): this proposal carries concrete specification links and derives its tests from them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking): governs downstream verification against the spec-to-test mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking): all target paths are in-root under the project root; no out-of-root dependency is created.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory: the transition table becomes a durable cited artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory: doc-code binding preserves traceability between narrative and code of record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory: the wedge evidence is a lifecycle trigger resolved through governed correction.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory: the consistency test is a deterministic guard replacing per-session judgment.
- `SPEC-1662` — advisory: tests assert behavioral agreement, not structural presence.
- `GOV-STANDING-BACKLOG-001` — advisory: WI-5827 in MemBase is the sole work authority for this slice.
- Deliberations: `DELIB-202667735`, `DELIB-202667731`, `DELIB-202667730`, `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`.

### Required (blocking)

| Spec ID | Relevance |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | The bridge audit-trail and protocol authority this reconciliation serves; WI-5827's `source_spec_id`. The append-only numbered chain is canonical; the corrected prose and the transition table document how that chain lawfully evolves. |
| GOV-ARTIFACT-APPROVAL-001 | The protocol rule file is a protected narrative artifact; its edit requires a per-artifact formal-artifact approval packet at implementation time (see Protected Narrative Surface Handling below). `target_paths` listing does not substitute for that packet. |
| DCL-NO-ACTION-STATUS-SEMANTICS-001 | Defines `NO-ACTION` as the Prime rejection-of-verdict status; the transition table documents it as the lawful post-`NO-GO` alternative to `REVISED`, and the prose correction must not blur that boundary. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal carries concrete specification links and derives its tests from them. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Governs downstream verification: the spec-to-test mapping below is the derivation record the LO verifier will execute against. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths are in-root under `E:\GT-KB` (`scripts/`, `config/agent-control/`, `.claude/rules/`, `.claude/skills/`, `.codex/skills/`, `platform_tests/scripts/`, `.groundtruth/formal-artifact-approvals/`); no out-of-root dependency is created. |

### Advisory

| Spec ID | Relevance |
|---|---|
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | The transition table becomes a durable, cited artifact instead of per-session reconstruction from code. |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Doc-code binding preserves traceability between the protocol narrative and the code of record. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | The wedge evidence is a lifecycle trigger (defect) resolved through governed correction rather than ad-hoc chain repair. |
| GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 | The consistency test is a deterministic guard replacing per-session judgment about which surface is authoritative. |
| SPEC-1662 | Assertion quality: the tests assert behavioral agreement (parsed table equals code constant; wedge-class regression), not mere structural presence. |
| GOV-STANDING-BACKLOG-001 | WI-5827 in MemBase is the sole work authority for this slice; no parallel authority is created. |

## Prior Deliberations

- **DELIB-202667735** — Owner mandate for the GT-KB parallel-operation program under which this proposal-author worker was dispatched; authorizes proposal authoring for the corrections program work items including WI-5827.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): list-free whole-project implementation authorization for PROJECT-GTKB-HARNESS-TEST-CORRECTIONS, recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730; covers WI-5827 through active project membership (fresh read this session: status `active`, `included_work_item_ids: null`).
- **DELIB-202667730** — WI-5808 Harness Test evaluation synthesis: the 2026-07-30 evaluation program whose r2b chain produced the wedge evidence this proposal cites.
- **DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS** — Owner decision establishing `NO-ACTION` semantics; constrains how the transition table documents the post-`NO-GO` `NO-ACTION` branch.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's parallel-operation program mandate: proposal-author workers file NEW implementation proposals for the corrections program; stop-at-gates (LO review) is the designed outcome. This filing is that deliverable for WI-5827.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the taxonomy-clean, list-free whole-project grant covering PROJECT-GTKB-HARNESS-TEST-CORRECTIONS member work items, including WI-5827. The grant authorizes this proposal-review-implementation cycle; it does not waive independent Loyal Opposition GO, the fresh work-intent claim, the implementation-start packet, exact target-path enforcement, the implementation report, or independent VERIFIED with governed atomic finalization. Per the PAUTH scope summary: "Protected narrative artifacts and formal MemBase records still require their own per-artifact approval packets under GOV-ARTIFACT-APPROVAL-001; class authorization does not substitute."
3. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Protected Narrative Surface Handling

`config/agent-control/gtkb-file-bridge-protocol.md` is the canonical narrative authority for the file-bridge protocol, and `.claude/rules/file-bridge-protocol.md` is its protected generated projection (protected path class `.claude/rules/*.md`). The `target_paths` listing above scopes the implementation-start gate only; it does NOT substitute for the per-artifact approval evidence:

- At implementation time, the rule-file edit requires its own formal-artifact approval packet under GOV-ARTIFACT-APPROVAL-001, presented to the owner with the full proposed content and metadata before the protected write, with the packet recorded at `.groundtruth/formal-artifact-approvals/` and matching content hash. Auto-approval states, if any, do not remove the display and audit requirement. The `.groundtruth/formal-artifact-approvals/**` envelope is declared in `target_paths` so the packet-evidence write is itself within implementation-start scope; the envelope declaration is scope only and is not the approval evidence.
- The canonical file is edited first; the projection is then regenerated via `scripts/generate_rule_compatibility_projections.py` (never hand-edited), and the implementation report will include generator `--check` evidence that source and projection are in sync.
- The skill files (`.claude/skills/gtkb-verify/SKILL.md` canonical; `.codex/skills/gtkb-verify/SKILL.md` generated adapter) are managed skill surfaces, not `.claude/rules/` narrative artifacts; they follow the skill-governance projection path, with adapter regeneration evidence in the implementation report.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5827's description (one authoritative transition table, corrected prose, LO verdict-template codification, doc-code consistency test), TEST-11783's expected outcome ("The protocol prose, LO remedy templates, and bridge_lifecycle_resolver.py agree on lawful post-NO-GO Prime statuses; a doc-code consistency test guards the transition table"), GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, and GOV-ARTIFACT-APPROVAL-001 fully constrain this implementation. No new or revised requirement is required before implementation.

## Specification-to-Test Mapping

Verification derives from WI-5827's linked test TEST-11783 (unit; spec GOV-FILE-BRIDGE-AUTHORITY-001). All new tests land in `platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py`; behavior preservation is proven by the existing untouched suite.

| Requirement source | Test | What it proves |
|---|---|---|
| TEST-11783 / GOV-FILE-BRIDGE-AUTHORITY-001 — prose/code agreement | `test_canonical_prose_table_matches_resolver` (parse `## Post-Verdict Transition Table` in `config/agent-control/gtkb-file-bridge-protocol.md`; assert equality with `ORDINARY_TRANSITIONS` + augmentations) | Canonical prose equals code of record |
| TEST-11783 — projection agreement | `test_projection_table_matches_resolver` (same parse against `.claude/rules/file-bridge-protocol.md`) | Generated projection equals code of record |
| TEST-11783 — wedge-class regression | `test_no_go_row_never_allows_new` (assert `"NEW" not in ORDINARY_TRANSITIONS["NO-GO"]` and not in either parsed doc row) | The exact r2b wedge class cannot silently return |
| TEST-11783 — post-NO-GO report prose | `test_post_implementation_section_names_revised` (§ Post-Implementation Verification names `REVISED` for post-NO-GO report refiling; no unconditional `NEW` instruction) | Prose branch exists and is correct |
| TEST-11783 / WI-5816 feed — LO remedy codification | `test_verify_skill_remedy_names_revised` (canonical SKILL.md contains the `REVISED` remedy sentence; contains no NEW-after-NO-GO instruction) | Remedy template agrees with the table |
| DCL-NO-ACTION-STATUS-SEMANTICS-001 — NO-ACTION branch documented | `test_table_documents_no_action_branch` (parsed `NO-GO` row contains `NO-ACTION`; table section cites the DCL) | Post-NO-GO alternatives documented per owner-decided semantics |
| D1 behavior preservation | Existing `platform_tests/scripts/test_bridge_lifecycle_resolver.py` runs unmodified and green | Refactor changes no transition semantics |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (separate gates).
2. `python -m pytest platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short` passes green, with the resolver suite unmodified.
3. `scripts/generate_rule_compatibility_projections.py --check` reports no drift between the canonical protocol file and the `.claude/rules/` projection after regeneration.
4. § Post-Implementation Verification in both prose surfaces states `NEW` for the first post-GO report and `REVISED` (never `NEW`) for post-NO-GO corrections; the `## Post-Verdict Transition Table` section exists in both and matches `ORDINARY_TRANSITIONS`.
5. `.claude/skills/gtkb-verify/SKILL.md` and its regenerated `.codex` adapter carry the codified post-NO-GO `REVISED` remedy sentence.
6. The formal-artifact approval packet for the protected rule-file edit exists with matching content hash before the protected write; packet path cited in the implementation report.
7. No bridge chain file, MemBase row, or dispatcher/TAFE state is mutated.

## Risk And Rollback

- **Behavior-preserving refactor risk.** The D1 constant extraction could accidentally alter an allowed set. Mitigation: the untouched existing resolver suite is the regression net, and the new consistency test pins every row; any drift fails both.
- **Projection regeneration scope.** Regenerating `.claude/rules/file-bridge-protocol.md` rewrites the whole projection from canonical; if canonical and projection had pre-existing unrelated drift, the regeneration would surface it. Mitigation: implementation runs `--check` before editing to snapshot the pre-state, and the implementation report discloses any pre-existing drift for separate disposition rather than silently absorbing it.
- **Concurrent program filings.** Sibling corrections workers file bridge threads concurrently; this proposal touches no shared write surface with them (resolver + prose + skill + one new test file) and adds no contention on the bridge write path.
- **Rollback** is the exact revert of the changed target files (the projection and adapter by re-running their generators against the reverted canonicals); an already-recorded approval packet remains as inert audit evidence. No data migration; no chain files or MemBase rows are touched.

## Cross-Harness Disposition

Target paths touch harness-facing narrative/skill surfaces but no hook or dispatch behavior (per DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001; ADR-CROSS-HARNESS-PARITY-001):

- **Claude (harness B):** `.claude/rules/file-bridge-protocol.md` (regenerated projection) and `.claude/skills/gtkb-verify/SKILL.md` (canonical skill) update the guidance Claude sessions load; no `.claude/settings.json` or hook registration changes.
- **Codex (harness A):** `.codex/skills/gtkb-verify/SKILL.md` is regenerated from the canonical skill source, preserving adapter parity; no `.codex/hooks.json` change.
- **Cursor (E), Goose (G), and other harnesses:** these harnesses consume the resolver and the canonical protocol prose through shared CLI/library surfaces (`scripts/bridge_lifecycle_resolver.py` is harness-neutral code of record); the reconciliation removes the cross-surface disagreement that wedged the Goose-authored r2b chain. No per-harness behavioral surface is changed, so no typed waiver is required.
- **Resolver:** harness-neutral library/script code; identical behavior regardless of invoking harness, now with the transition table importable as a constant for any future harness-side tooling.

## DISARM — KB Mechanics

This proposal modifies source, canonical narrative/skill files, their generated projections, and one new test file only. No MemBase records, specifications, ADRs, DCLs, work items, Deliberation Archive entries, or other KB-governed rows are created, updated, or retired by this work. `kb_mutation_in_scope: false` is accurate. Citations of DELIB, WI, TEST, and spec IDs are read-only references. The protected-file edits require file-side formal-artifact approval packets (see Protected Narrative Surface Handling), which are approval evidence records, not MemBase mutations.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5827-post-nogo-refiling-protocol-reconciliation`, run post-GO by the implementing session) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet of its own; the separate per-artifact approval packet obligation for the protected rule-file edit stands independently. The PAUTH triple cited in this proposal's head is the metadata the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement.

## Recommended Commit Type

Recommended commit type: fix — repairs a live protocol-documentation defect that wedged a bridge chain; the extracted constant, corrected prose, codified remedy, and consistency test are the repair and its regression guard.

## Loyal Opposition Review Questions

1. Is the two-constant shape (base map + explicit post-GO augmentations) the right authority extraction, or should the augmentations be folded into a context-aware lookup function that the docs describe prose-only?
2. Should the doc-code consistency test also pin § Prime Workflow step 6 and the status-semantics table rows, or is that over-binding prose that legitimately evolves?
3. Is placing the canonical remedy sentence in `gtkb-verify/SKILL.md` sufficient for the WI-5816 feed, or should this slice also add it to `gtkb-proposal-review` (proposal-side NO-GO verdicts), where the same wrong-remedy class could recur?
4. Does the Protected Narrative Surface Handling section correctly sequence canonical-edit → approval packet → projection regeneration for the dual-surface rule file?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
