NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5826-finalizer-evidence-hash-restamp
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5826

target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", ".codex/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py"]
implementation_scope: verified_finalizer_candidate_evidence_hash_restamp
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5826 Implementation Proposal — Re-Stamp `candidate_evidence_hash` Over The Final Verdict Bytes Inside The VERIFIED Finalizer

## Summary

`finalize_verified_commit` mutates the reviewer's verdict body after the reviewer has already stamped the self-referential `candidate_evidence_hash` field, and never re-stamps it. Two mutations happen inside the finalizer itself (Prior-Deliberations seeding, then the `## Commit Finalization Evidence` append at `.claude/skills/gtkb-verify/helpers/write_verdict.py:1002-1014`), and two more happen inside the writer it calls (author-metadata materialization and envelope-head normalization at `scripts/gtkb_bridge_writer.py:1174-1179`). The bridge-compliance gate then recomputes the hash over exactly those post-mutation bytes (`.claude/hooks/bridge-compliance-gate.py:1478-1490`) and denies the write because the embedded value is stale (`.claude/hooks/bridge-compliance-gate.py:1573-1586`). The stamped hash therefore can never match the final verdict bytes, so terminal VERIFIED cannot be finalized through the sanctioned helper path. The recorded workaround is worse than the defect: the Cursor Loyal Opposition harness monkeypatched `write_bridge_file` inside its own finalizer scripts to stamp post-append (2026-07-30 wi5759 evidence recorded in the WI-5826 description).

This proposal moves the stamping into the finalizer as a deterministic, fail-closed step that runs after every body mutation and immediately before the write, reusing the gate's own hash function as the single source of truth rather than re-implementing the algorithm. It closes the last authoring step that no tool performs, and it removes the incentive to monkeypatch the governed writer.

This proposal is filed as `bridge/gtkb-wi5826-finalizer-evidence-hash-restamp-001.md`, the first entry of a new append-only versioned bridge file chain. No prior bridge file is deleted, rewritten, or renumbered; the numbered bridge files remain the canonical append-only audit trail under GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

Every claim below was re-derived this session from the live worktree, the code of record, `gt backlog show WI-5826 --json`, and direct first-line status-token reads of the sibling bridge chains. Line references are current-worktree references.

1. **The field is self-referential over post-normalization bytes.** `_candidate_evidence_hash` (`.claude/hooks/bridge-compliance-gate.py:1478-1490`) normalizes line endings, replaces the single `candidate_evidence_hash` line's value with the sentinel `<CANDIDATE_EVIDENCE_HASH>` via the regex at `.claude/hooks/bridge-compliance-gate.py:199-204`, and hashes the root-relative candidate path joined to the sentinel-substituted content. It returns `None` unless the substitution matched exactly once.

2. **The gate compares that recomputation against the embedded value.** The verdict freshness check at `.claude/hooks/bridge-compliance-gate.py:1573-1586` fires for GO, NO-GO, and VERIFIED first-line statuses and denies the write when the embedded value is missing, malformed, or unequal to the recomputation over the final candidate bytes.

3. **The finalizer mutates the body after stamping, with no re-stamp.** In `finalize_verified_commit`, `seed_prior_deliberations` may inject content and `_append_commit_finalization_evidence` appends a whole new section (`.claude/skills/gtkb-verify/helpers/write_verdict.py:1154-1168`); the body then goes straight to `write_bridge_file` (`.claude/skills/gtkb-verify/helpers/write_verdict.py:1184-1190`). Nothing between those points recomputes the field.

4. **The writer mutates it twice more before the audit.** `write_bridge_file` applies `ensure_author_metadata` and `normalize_bridge_envelope_head` and only then runs the compliance audit on the resulting bytes (`scripts/gtkb_bridge_writer.py:1174-1185`). Any stamping that happens before those two calls is stale by construction, which is why a naive finalizer-side stamp is insufficient and why the design below pre-applies the writer's own normalization.

5. **Nothing in the toolchain computes the value.** No helper, CLI, or preflight emits the expected hash. The only way a reviewer can obtain it today is to trigger a governance rejection and read the expected value out of the deny message. This is recorded repeatedly in the standing advisory set: `bridge/gtkb-lo-tooling-defect-advisory-011.md` finding A11e (nothing computes it; recommendation 5 is precisely "make write_verdict.py compute and inject it"), `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md` finding C2 (obtainable only by deliberately triggering a rejection), `bridge/gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-001.md` finding C6 (no forward computation path), and `bridge/gtkb-lo-verdict-filing-path-advisory-001.md` finding D3 (documented nowhere).

6. **The workaround is a monkeypatch of the governed writer.** Per the WI-5826 description, the Cursor Loyal Opposition harness patched `write_bridge_file` inside its finalizer scripts to stamp post-append. That reaches the correct seam but does so by replacing the governed writer at runtime, outside review, per-session, per-harness — an ungoverned bypass of the exact chokepoint the bridge protocol depends on.

7. **The canonical helper file is clean right now.** `git --no-optional-locks status` shows the `gtkb-verify` skill dirty only at `.claude/skills/gtkb-verify/SKILL.md` and `.codex/skills/gtkb-verify/SKILL.md`; `helpers/write_verdict.py` is clean in both surfaces. See the Coordination Note.

## Proposed Design

One slice, function-scoped, inside the canonical helper; the Codex adapter copy is regenerated mechanically; one new regression module.

### Slice A — Deterministic fail-closed re-stamp before the write

Three additions to `.claude/skills/gtkb-verify/helpers/write_verdict.py`:

**A1. Fail-closed gate loader.** A module-level loader resolves `.claude/hooks/bridge-compliance-gate.py` (a hyphenated filename, so loaded through `importlib.util.spec_from_file_location`, the convention already used by `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`) and exposes its `_candidate_evidence_hash`, `CANDIDATE_EVIDENCE_HASH_LINE_RE`, and `CANDIDATE_EVIDENCE_HASH_SENTINEL`. If the gate module cannot be loaded, the finalizer raises `VerifiedFinalizationError` and writes nothing — the same fail-closed posture already used for the review-independence comparator at `.claude/skills/gtkb-verify/helpers/write_verdict.py:1071-1089`. The algorithm is never re-implemented; the gate remains the single definition, so the two surfaces cannot drift.

**A2. `_restamp_candidate_evidence_hash(body, *, verdict_rel_path, project_root)`.** Deterministic, no network, no clock, no retry:

1. Apply the writer's own pre-audit normalization to the body — `ensure_author_metadata(body, project_root=root, explicit=None)` then `normalize_bridge_envelope_head(...)`, both imported from `scripts.gtkb_bridge_writer` — so the bytes being stamped are the bytes that will be audited. Both are idempotent for a body that already carries complete author metadata and a canonical envelope head (`scripts/gtkb_bridge_writer.py:368-399` rebuilds the same envelope from the validated existing one; `ensure_author_metadata` returns content unchanged when metadata is complete), which is exactly the finalizer's body shape after its own guards. Idempotence is asserted by test, not assumed.
2. Count `candidate_evidence_hash` field occurrences. Zero occurrences raises `VerifiedFinalizationError` naming the missing field and the sentinel placeholder the author should add; more than one raises as well, because the gate's substitution requires exactly one match and returns `None` otherwise.
3. Substitute the sentinel for the current value, compute the hash through the gate function against `verdict_rel_path`, and write the computed value back into the field.
4. Assert the fixpoint: recompute the hash over the stamped body and require equality with the value just written. This is TEST-11782's expected outcome asserted inline as a runtime invariant, so a future normalization change cannot silently reintroduce a stale stamp.
5. Return the stamped, normalized body.

**A3. Wiring.** `finalize_verified_commit` calls the re-stamp after `_append_commit_finalization_evidence` and after the review-independence and synthetic-session assertions (both read author metadata and are order-insensitive with respect to the hash field), and passes the returned body to `write_bridge_file`. The writer re-applies its normalization idempotently and audits the identical bytes. All existing preconditions, guards, staged-set checks, disposable-index commit mechanics, and rollback behavior are untouched. On any re-stamp failure the finalizer raises before the verdict file is written, so no partial terminal artifact and no commit can result.

**Why not stamp inside the writer.** The seam inside `write_bridge_file` immediately before the audit is where the Cursor monkeypatch landed, and it is the more general fix. It is rejected here for two reasons: it would silently rewrite a declared governance field for every bridge write including proposals and Prime-authored reports, converting a reviewer attestation into a writer-generated value across surfaces this work item does not scope; and `scripts/gtkb_bridge_writer.py` is inside the declared target paths of the concurrently GO'd WI-5825 thread, so editing it would create a direct file collision. Confining the change to the finalizer keeps the diff disjoint and keeps the attestation semantics scoped to the one status that cannot otherwise be finalized.

### Cross-harness parity

`.codex/skills/gtkb-verify/helpers/write_verdict.py` is a tracked, currently byte-identical projection of the canonical helper, produced by `scripts/generate_codex_skill_adapters.py` (which mirrors `helpers` resource directories). The implementation regenerates it with that script and verifies with its `--check` mode, so the Codex bridge submission path receives the same fix. The generator's canonical-helper path rewriting targets `.claude/skills/<name>/helpers/` strings only, so the new reference to the hooks path is projected unchanged. The registry `source_sha256` refresh is computed from the skill source document rather than helper files, so no registry file changes and none is declared in the target paths.

## Cross-Harness Disposition

The declared target paths touch two harness skill surfaces, so behavioral parity is declared per applicable harness. No waiver is requested and none is needed.

- **Claude (harness B) — parity by construction.** `.claude/skills/gtkb-verify/helpers/write_verdict.py` is the canonical source of the change. The re-stamp runs inside `finalize_verified_commit` for every invocation, with no harness-conditional branch, no environment-variable gate, and no per-harness code path.
- **Codex (harness A) — parity by regenerated projection.** `.codex/skills/gtkb-verify/helpers/write_verdict.py` is a tracked, currently byte-identical projection of the canonical helper and is regenerated by `scripts/generate_codex_skill_adapters.py` as part of this implementation, with `--check` confirming zero drift. The generator rewrites only `.claude/skills/<name>/helpers/` path strings, so the helper's new reference to the compliance-gate hook path projects unchanged and the Codex finalization path executes identical logic. Byte identity after regeneration is asserted by `test_codex_adapter_projection_matches_canonical_helper`.
- **Antigravity (harness C) and Cursor — not applicable.** Neither surface carries a `gtkb-verify` helpers directory in the tracked tree, so there is no projection to update and no behavioral surface to diverge. Their generators are unaffected by this change.
- **Goose — known pre-existing divergence, explicitly out of scope.** `.goose/skills/gtkb-verify/helpers/write_verdict.py` is a tracked third copy whose content already differs from the canonical helper today, before any change proposed here, and no Goose skill-adapter generator exists to reproject it. This proposal neither widens nor repairs that drift; it is surfaced as a review question and a follow-on work-item candidate so the gap is recorded rather than silently inherited.
- **Ollama and OpenRouter — not applicable.** These harnesses consume skills through routing configuration rather than a mirrored helpers directory, so no projection exists for this file.

### Rejected alternatives

- **Keep the per-harness monkeypatch.** Replaces the governed writer at runtime, is invisible to review, and must be re-invented by every harness. It is the defect's current symptom, not a remedy.
- **Re-implement the hash algorithm in the helper.** Two definitions of a self-referential hash will drift the first time the gate's normalization or regex changes, and the failure mode is a silent deny at the worst moment. Loading the gate as the single source of truth is strictly safer.
- **Have the reviewer stamp manually and forbid finalizer body mutation.** Would require removing the Commit Finalization Evidence append and Prior-Deliberations seeding, both of which are load-bearing evidence behavior. Rejected.
- **Emit the expected hash from a separate advisory command.** Helps authoring ergonomics but does not fix finalization, because the finalizer mutates the body after any pre-computation. Worth pursuing separately for the GO and NO-GO authoring paths; out of scope here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — the WI-5826 source specification; the append-only numbered bridge chain and terminal-verdict authority this defect blocks, and the audit-trail integrity the re-stamp restores.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation; every relevant governing specification is cited in this section in bullet form directly under the heading, the shape both the applicability preflight and the implementation-authorization extractor accept today.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain under which the header triple proceeds; the implementation-start packet enforces the declared target paths exactly.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required (blocking) — the finalizer's author-metadata and review-independence guards sit in the touched function; the re-stamp runs after them and preserves their fail-closed behavior unchanged.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — required (blocking) — bridge submission-path enforcement must hold across harnesses; the Codex adapter projection is regenerated so the Claude and Codex finalization paths stay identical.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — required (blocking) — the declared target paths touch harness skill surfaces, so the Cross-Harness Disposition section above declares behavioral parity per applicable harness with no waiver requested.
- `ADR-CROSS-HARNESS-PARITY-001` — required (blocking) — the behavioral-parity invariant the disposition section satisfies; the change carries no harness-conditional branch and the Codex projection is regenerated in the same implementation.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is created, updated, or retired by this implementation; bridge artifacts and the authorization chain remain under the gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every declared target path is in-root under the GT-KB project root; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the write-time compliance gate and the finalization helper are the two layers involved; this change restores their coherence instead of weakening the gate.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — converts an undocumented manual derivation and a per-harness runtime patch into one deterministic helper step.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence here derives from fresh canonical reads made this session; the gate module is loaded as the single hash definition rather than copied.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (recomputed hash equality over final on-disk bytes, absence of artifacts on failure), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the terminal verdict artifact and its commit remain the durable evidence; this change makes that artifact reachable through the governed path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability: the verdict artifact, its stamped evidence field, and the finalization commit stay linked as one durable record in the artifact graph.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — advisory — Loyal Opposition finalization must work identically on whichever harness holds the role, which is why the adapter projection is in scope.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5826 is the sole work authority for this proposal; no parallel authority is created.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5826 follow the recorded trigger classifications.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667731`, `DELIB-202667730`, `DELIB-202667722`, `DELIB-202667726`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with role-transition plan: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667731** — Harness Test Corrections whole-project authorization decision: the list-free whole-project grant recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730, under which this proposal is filed.
- **DELIB-202667730** — Harness Test final synthesis: the evaluation-run synthesis whose diagnosis phase produced the WI-5826 defect record and the wi5759 finalizer evidence.
- **DELIB-202667722** — Timer and throttle governance is a first-class concern: no hard-coded timer, interval, retry, or throttle literal is introduced by this change; the re-stamp is a pure deterministic transform.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the program whose runs surfaced this defect.
- Standing advisory precedent for this exact finding, read fresh this session: `bridge/gtkb-lo-tooling-defect-advisory-011.md` (A11e and its recommendation 5), `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md` (C2), `bridge/gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-001.md` (C6), and `bridge/gtkb-lo-verdict-filing-path-advisory-001.md` (D3). This proposal is the first implementation response to that advisory cluster; no prior deliberation rejects this approach.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase; the sibling bridge chains were verified by direct first-line status-token reads of the numbered files.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5826. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731** — the owner's list-free whole-project grant (PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730, status active, no expiry, no included-work-item list) covers WI-5826 as a member work item. Per its recorded scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, a fresh work-intent claim, an implementation-start packet, exact target-path enforcement, an implementation report, and independent VERIFIED with governed atomic finalization.
3. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5826 defect description (fresh-read verified), the gate's hash contract as implemented, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, DCL-CROSS-HARNESS-ENFORCEMENT-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, and TEST-11782's recorded expected outcome fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11782` ("Finalized VERIFIED verdict bytes hash-match their stamped candidate_evidence_hash"), created with WI-5826 under GOV-12 and linked to GOV-FILE-BRIDGE-AUTHORITY-001, is the spec-derived anchor. Its recorded expected outcome is the operative assertion: after `finalize_verified_commit` completes, recomputing the candidate evidence hash over the final verdict file equals the stamped value, with the evidence-append path covered by regression. All new tests land in `platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py`, following the git-fixture and monkeypatch conventions already established in `platform_tests/skills/test_verified_finalization_validation_hardening.py`.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11782 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_final_verdict_bytes_match_stamped_candidate_evidence_hash` | After a successful `finalize_verified_commit`, the gate's own hash function recomputed over the final on-disk verdict file bytes equals the value stamped in that file — TEST-11782's expected outcome, asserted end to end |
| TEST-11782 (evidence-append path) | `test_evidence_append_path_is_hash_consistent` | A body with no `## Commit Finalization Evidence` section finalizes hash-consistently after the append fires; a body that already carries the section (append is a no-op) finalizes hash-consistently too |
| WI-5826 (seeding mutation path) | `test_prior_deliberations_seeding_path_is_hash_consistent` | With seeding enabled the injected content is inside the stamped bytes and the recomputation still matches |
| WI-5826 (writer normalization) | `test_writer_normalization_is_idempotent_for_finalizer_bodies` | `ensure_author_metadata` and `normalize_bridge_envelope_head` applied twice to a finalizer-shaped body equal one application, so the pre-applied normalization and the writer's re-application produce identical bytes |
| GOV-FILE-BRIDGE-AUTHORITY-001 (fail-closed) | `test_missing_candidate_evidence_hash_field_fails_closed`, `test_duplicate_candidate_evidence_hash_field_fails_closed` | Zero or multiple field occurrences raise `VerifiedFinalizationError`; no verdict file is written and HEAD is unchanged |
| GOV-DOCUMENT-AUTHOR-PROVENANCE-001 (fail-closed) | `test_gate_module_unavailable_fails_closed` | When the compliance-gate module cannot be loaded, finalization raises, no terminal verdict artifact exists on disk, and no commit is created |
| WI-5826 (regression lock) | `test_finalization_succeeds_where_stale_stamp_previously_denied` | The full finalize path completes on a fixture chain whose authored body carries a pre-mutation stamp — the exact input that is denied today with the stale-hash rejection |
| DCL-CROSS-HARNESS-ENFORCEMENT-001 | `test_codex_adapter_projection_matches_canonical_helper` | The Codex adapter copy is byte-identical to the canonical helper after regeneration, so both submission paths carry the fix |
| SPEC-1662 | (assertion quality applies to all of the above) | Assertions are behavioral — recomputed-hash equality, artifact absence on failure, byte identity — not mere presence checks |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` both pass clean on every changed Python file (two separate gates).
2. `python -m pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q --tb=short` passes green.
3. `python scripts/generate_codex_skill_adapters.py --check` reports no drift after regeneration, and `python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q` passes.
4. TEST-11782's outcome holds end to end: the gate's hash function recomputed over the final verdict file equals the stamped value in every finalization test.
5. Every failure mode leaves no terminal verdict artifact on disk and no new commit.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals.
7. No file outside the three declared target paths is modified.

## Risk And Rollback

- **Normalization-drift risk.** If a future change makes the writer's pre-audit normalization non-idempotent, the pre-applied stamp could go stale again. Mitigated three ways: the inline fixpoint assertion in step 4 raises before any write; the idempotence property is tested directly; and the failure mode is a fail-closed raise, never a false-green terminal verdict.
- **Gate-coupling risk.** The helper now loads the compliance-gate module. Mitigated by the fail-closed loader (unavailable gate denies finalization, matching the existing review-independence precedent) and by reusing the gate's definitions rather than copying them, so the coupling is the point rather than a hazard.
- **Semantic risk — attestation becomes tool-generated.** The field stops being a reviewer-transcribed value for VERIFIED finalization. This is deliberate and bounded to the one path that cannot otherwise complete; the value it attests (final normalized candidate bytes) is mechanical, not judgmental, and the reviewer's substantive attestations are unchanged. Reviewer-authored GO and NO-GO stamping behavior is untouched by this change.
- **Cross-harness risk.** `.goose/skills/gtkb-verify/helpers/write_verdict.py` is a tracked third copy that is **already divergent** from the canonical helper today (differing content hash, pre-existing and not caused by this work), and no Goose skill-adapter generator exists alongside the Codex and Antigravity generators. It is deliberately excluded from the target paths as pre-existing drift; see the Loyal Opposition review questions.
- **Rollback** is the exact revert of the canonical helper plus a regeneration of the Codex adapter, and deletion of the new test module. No MemBase record, no dispatcher/TAFE state, and no existing bridge chain file is touched by this work, so rollback is a source-only operation.

## Coordination Note (sequencing constraints, not scope)

1. **wi5827 dirty skill documents.** `.claude/skills/gtkb-verify/SKILL.md` and `.codex/skills/gtkb-verify/SKILL.md` are modified in the worktree from the VERIFIED-but-unfinalized `gtkb-wi5827-post-nogo-refiling-protocol-reconciliation` thread (latest numbered file `-004`, first-line status VERIFIED, not yet finalized into a commit). The helper file this proposal targets is **clean** in both surfaces, and the skill documents are **not** in the declared target paths. The implementing session must not stage or commit those two skill documents; the implementation-start packet's exact target-path enforcement plus scoped commits keep the two threads separate. If the wi5827 finalization lands first, the implementing session re-baselines line references before editing and records the re-baseline in the implementation report.
2. **WI-5825 file collision avoided by design.** The GO'd `gtkb-wi5825-publication-capability-recovery-receipt-backfill` thread declares `scripts/gtkb_bridge_writer.py` among its target paths. This proposal deliberately does **not** modify that file — it imports two already-public functions from it — so the two diffs are disjoint at the file level and the threads may proceed in either order.
3. **wi5827 lifecycle-metadata thread.** The separately GO'd `gtkb-wi5827-bridge-lifecycle-metadata-normalization` thread targets `scripts/bridge_lifecycle_resolver.py` and its test module; no overlap with this work.

## DISARM — KB Mechanics

This work performs no MemBase mutation. This work performs no KB write, no MemBase insert, and no groundtruth.db change of any kind. The implementation creates and modifies source and test files only. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change. Every specification, deliberation, work-item, and test identifier cited in this proposal is a read-only reference used as evidence, not a mutation, insert, or edit of any kind.

## DISARM — Packet Mechanics

The implementation-start packet minted by `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5826-finalizer-evidence-hash-restamp` (run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact and requires no formal-artifact approval packet, because no approval-gated artifact is created, changed, or inserted by this work. The packet derives from dispatcher/TAFE bridge state, the approved proposal file, and the GO verdict file; it expires and fails closed on bridge status drift. The project-authorization triple in this proposal's header supplies the authorization evidence the packet validator consumes; it never broadens the declared target paths and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — this repairs a defect that makes the sanctioned terminal-verdict finalization path structurally unusable, with regression coverage. It adds no new capability surface; the re-stamp is the missing step in an existing transaction.

## Loyal Opposition Review Questions

1. Is confining the re-stamp to the VERIFIED finalizer the right scope, or should the seam move into the writer immediately before the compliance audit (the more general fix) once the WI-5825 thread has landed and the file collision is gone?
2. Is loading the compliance-gate module from the helper acceptable coupling, given the fail-closed loader, or would you require a small shared module extracted from the gate instead?
3. Does making the field tool-generated for VERIFIED finalization weaken its attestation value in any way that matters, given the value is mechanical and the reviewer's substantive attestations are unchanged?
4. Should the already-divergent Goose helper copy be brought into this thread's scope, or captured as a separate work item covering both the drift and the missing Goose adapter generator?
5. Does the TEST-11782 mapping plus the fail-closed and idempotence tests satisfy the specification-derived testing requirement for every linked specification?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
