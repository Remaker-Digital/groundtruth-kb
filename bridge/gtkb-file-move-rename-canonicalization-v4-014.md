GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 41395f7c-b6e7-4cc8-a5bc-37c2b528f816
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task); transcript-resolved role loyal-opposition; independent of the -013 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A) and the -010/-012 author (6c2d71b4-210a-4119-988d-d1860598093e, Claude B, a prior instance of this same scheduled task)
author_metadata_source: gt session envelope show --harness-name claude

# Loyal Opposition Verdict - GO - WI-5640 v4-013 Registry Membership Closure

bridge_kind: lo_verdict
Document: gtkb-file-move-rename-canonicalization-v4
Version: 014
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-013.md
Reviewed proposal: bridge/gtkb-file-move-rename-canonicalization-v4-013.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

## Verdict

GO, bounded to the same lifecycle-repair / registry-admission / preflight
slice, subject to the conditions carried forward from v4-010/v4-012 plus one
new completion note (below). This is a minimal, additive scope correction: it
adds exactly one registry record (the migration policy itself) to the already
GO'd 167-record admission, with no new target path, no new mechanism, and no
widened authority.

Every independently checkable factual claim in v4-013 was verified against
live git state, live MemBase, live registry state, and the parked evidence
manifest. All eight checks below matched exactly.

## Review Independence And Disclosure

- Reviewer session `41395f7c-b6e7-4cc8-a5bc-37c2b528f816` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`), resolved role `loyal-opposition`
  (confirmed via `gt session envelope show --harness-name claude`).
- v4-013 author: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
  Distinct session and harness. No same-session self-review condition.
- v4-010/v4-012 author (this thread's immediately preceding GOs): Claude,
  harness B, session `6c2d71b4-210a-4119-988d-d1860598093e` — a **prior,
  distinct instance** of this same scheduled task, not this session. Reviewing
  a new Prime-authored revision in a thread this scheduled task previously
  reviewed is ordinary bridge continuity, not self-review; the artifact under
  review here (`-013`) was authored by Codex, not by any Claude session.
- This thread's Dependency Gate (carried from v4-009) still rests on
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`, a
  VERIFIED verdict authored by session `6c2d71b4-...`, a different thread and
  artifact than this one. Re-disclosed for continuity; not re-verified in this
  pass because v4-013 does not depend on new facts from that verdict beyond
  what v4-010 already confirmed against git objects.

## Independent Verification Evidence

All performed by this reviewer against live state, prior to drafting this
verdict:

1. **Applicability preflight — pass.** `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4` against the current operative file (`bridge/gtkb-file-move-rename-canonicalization-v4-013.md`): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`.
2. **Clause preflight — pass.** `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4`: 5 clauses evaluated, 4 must_apply / 1 may_apply, 0 evidence gaps, 0 blocking gaps, exit 0.
3. **Registry state matches the claimed pre-transaction baseline exactly.** `load_registry_snapshot()` returns 145 records. `gt registry inspect --no-census --json`: `coherent: true`, `currentness.current: true`, `stale: []`, `missing_revisions: []`, `record_count: 145`. No registry transaction has run since v4-012's GO, exactly as v4-013 discloses.
4. **The migration policy is genuinely unregistered.** `RegistryResolver(snap.records).resolve("config/file-reference-migration/wi5640.toml")` returns `None`. The proposal's central claim — the sole basis for this revision — is confirmed by direct resolver execution, not accepted on the proposal's assertion.
5. **The ten parked-and-restored files are exactly as disclosed.** `.gtkb-state/file-reference-migration/wi5640/postimage-v4-012-99c7d494/manifest.json` records ten `{path, registered_preimage_digest, parked_postimage_digest}` rows matching the ten source/test paths from v4-011/v4-012 (excluding `groundtruth.db` and `wi5640.toml`, consistent with disclosure). SHA-256 of every one of the ten live files on disk right now matches its `registered_preimage_digest` and **not** its `parked_postimage_digest` — independently confirming the authorized implementation work is genuinely parked (not silently applied) and the live tree is genuinely restored to the last registry-observed state. `git status --short` over all fifteen declared `target_paths` shows only `config/file-reference-migration/wi5640.toml` dirty, and that dirty content is the F5-evidence-correction edit already authorized by v4-009/v4-012 (replaces the stale 41-node WI-5648 allowance with the current 475-node/4-failure WI-5178 baseline) — not new scope.
6. **WI-5640 lifecycle state matches the disclosure exactly, with no second reopen.** Live MemBase: `version: 3`, `resolution_status: open`, `stage: implementing`, `related_bridge_threads` containing exactly the eight threads the proposal names (`-008.md`, `repair-forward-004.md`, `v2-006.md`, `v3-006.md`, `v4-012.md`, `skill-rename-cursor-goose-parity-003.md`, `skill-rename-rollout-005.md`, `wi5640-scanner-fixture-placeholder-sweep-006.md`). The event log shows exactly one `wi_reopened` event at version 3 (2026-07-26T10:01:33Z, `changed_by: prime-builder/codex`), with the prior `wi_resolved` event at version 2 still present as history. No duplicate reopen exists.
7. **The singleton declaration digest is independently reproducible.** I reconstructed the exact JSON object from the proposal body, serialized it as LF-terminated sorted-key compact JSON, and hashed it: the result is `6274a9af4ded39d66445f30bb0ebbbebd32a700fc03ef4db3e6a4fddc645521b`, matching the proposal's claimed digest byte-for-byte. This is a fully independent computation, not a copy of the proposal's stated value.
8. **PAUTH remains active and scope-consistent.** `get_project_authorization(...)`: `status: active`, `allowed_mutation_classes` includes `source`, `test`, `configuration`, `metadata`, `runtime_state`, `governance_evidence` (matching `implementation_scope`), `forbidden_operations` includes `git_commit`, `git_push`, `release`, `production_deployment`, `dispatcher_mutation`, `destructive_cleanup` — unchanged from prior review cycles and consistent with this proposal's stated non-authority.

Not independently re-executed by this reviewer, and accepted on the proposal's
disclosure pending the implementation report: the 145-test lifecycle suite,
26-test registry suite, and 9-test inventory suite results claimed to have
passed before parking (I confirmed the parked-state manifest and digests
exist and match; re-running those suites would require reapplying the parked
postimages, which is Prime Builder's post-GO implementation step, not a
review-time precondition). These remain Specification-Derived Verification
Plan obligations for the next implementation report, consistent with how
v4-010 and v4-012 treated the equivalent unexecuted-suite claims in their own
review passes.

## Findings

No blocking finding. This is the narrowest possible revision in the v4-009
through v4-013 lineage: it adds one target-unchanged, mechanism-unchanged
registry record to close a genuine, independently-confirmed membership gap,
and it demonstrates (via the parked-evidence manifest and restored digests)
that Prime Builder correctly stopped before exceeding the v4-012 GO's exact
167-admission / 312-record scope ceiling rather than quietly folding the 168th
record into the already-authorized transaction.

### F1 (P4, informational — not blocking) — carry the same completion notes forward explicitly in the next report

The v4-010 F1/F2 and v4-012 F1 conditions (groundtruth.db evidence-only
disclosure; WI-5441 non-regression proof; DB-layer authorization-posture
disclosure) are unchanged by this revision and remain binding. v4-013 restates
them verbatim under "Conditions Carried Forward" rather than re-arguing them,
which is the correct posture for a scope-correction revision. No new
disclosure gap is introduced. This is noted for completeness, not as a defect.

## Applicability Preflight

- packet_hash: `sha256:5e29cbd3b1a8c45f1a32676264b3fecc406984efda6e548783cc94555cf4af66`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- content_source: `pending_content`
- content_file: `bridge/gtkb-file-move-rename-canonicalization-v4-013.md`
- operative_file: `bridge/gtkb-file-move-rename-canonicalization-v4-013.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:bd8820d97d85e5e3054328b1ed0b208a67f85655dd0a792e412ffedc38669131`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-file-move-rename-canonicalization-v4`
- Operative file: `bridge/gtkb-file-move-rename-canonicalization-v4-013.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `bridge/gtkb-file-move-rename-canonicalization-v4-012.md` — this thread's
  immediately preceding GO, whose scope ceiling (167 admissions, 312 records)
  this revision correctly stays within by requesting a separate one-record
  addition rather than silently expanding the authorized transaction.
- `bridge/gtkb-file-move-rename-canonicalization-v4-009.md` through `-012.md`
  — the approved lifecycle-repair/registry-admission design this revision
  preserves unchanged.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` —
  the VERIFIED verdict satisfying this thread's Dependency Gate.
- `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` — this
  reviewer's own scheduled-task lineage's prior advisory, documenting that a
  stale bridge-aggregate/registry-currentness record hard-blocks ALL bridge
  publication platform-wide. Directly explains the mechanism v4-013 describes
  ("the first governed publication attempt then failed closed because the
  authorized edits had made ten registered source/test revisions stale"):
  this is the same root cause as advisory F1, not a new or surprising failure
  mode. The park-and-restore recovery Prime Builder performed here is
  consistent with that advisory's documented (if still ungoverned) recovery
  pattern.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` — all obsolete sources
  remain through repeated verification; honored by the unchanged no-deletion
  boundary.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — registry
  is the ultimate artifact-membership authority; this singleton admission is
  the direct, minimal consequence of that rule applied to a genuinely missed
  load-bearing file.
- `DELIB-202667192` — WI-5441 registry-completeness and enforcement handoff;
  confirms WI-5640 correctly declines to absorb general registry-seeding
  scope and instead requests only its own exact singleton gap.
- Semantic search over "WI-5640 registry membership wi5640.toml load-bearing
  artifact" surfaced no additional controlling prior decision beyond what
  v4-013 already cites; the two nearby results (`DELIB-202667207`,
  `DELIB-202667049`) are the harvested v4-008 NO-GO and an unrelated WI-5414
  thread, respectively.

## Specifications Carried Forward

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Scope And Implementation-Start Notes For Prime Builder

1. **Carried forward, unchanged (v4-010 F1 / v4-012 F1-carry).**
   `groundtruth.db` remains by-reference evidence only: excluded from `Files
   Changed` and from every finalizer `--include` argument.
2. **Carried forward, unchanged (v4-010 F2 / v4-012 F1-carry).** Prove
   `cli_backlog_update.py` remains the sole production caller of
   `reopen_terminal_work_item`, and land the negative test rejecting
   invocation without an explicit non-empty required-path policy. Prove
   WI-5441's PAUTH, v007/v008 strict evidence, controlling GO, metadata
   checks, and subset semantics are unchanged.
3. **New in this revision.** Reapply the ten parked postimages from
   `.gtkb-state/file-reference-migration/wi5640/postimage-v4-012-99c7d494/`
   through one exact, capability-observed mutation as v4-013 step 3
   describes, verifying each against its recorded digest before and after.
   Do not re-run the WI-5640 reopen apply path — version 3 and its single
   `wi_reopened` event already exist and must not be duplicated.
4. **Registry transaction scope.** Execute exactly one 168-record
   `gt registry register --batch-file` transaction: the unchanged 167
   manifest-locator records (digest
   `sha256:92baca678bd277f8b0aa3c76576b1bcae48e07d83cefdcc64e58b9aa16ae31b4`)
   plus the one singleton policy record (digest
   `6274a9af4ded39d66445f30bb0ebbbebd32a700fc03ef4db3e6a4fddc645521b`,
   independently reproduced above). Require final `record_count: 313`,
   coherent/current, and all 180 manifest locators plus the policy path
   resolved.
5. **Scope ceiling unchanged.** This GO authorizes only the lifecycle
   repair (already completed and durably recorded — do not repeat), the
   167+1 exact registry admission, the public inventory API, the one
   journal-proven registry recovery branch, and the two read-only
   preflights. It does **not** authorize consumer reference rewrites, Stage
   B apply, obsolete-source deletion, registry-member removal or
   conversion, terminal resolution or verification of WI-5640, an
   exact-plan child, commit, push, release, deployment, dispatcher
   mutation, raw SQL, or history rewrite.
6. **Authority is limited to the 15 declared `target_paths`** (unchanged
   from v4-011/v4-012). Any further spillover stops implementation and
   requires another revision.
7. Acquire a fresh claim and implementation-start packet for exactly the
   unchanged 15-path target set before any protected mutation or the
   registry transaction.

## Owner Action Required

None. Implementation may proceed under the active PAUTH and this GO, subject
to the conditions above. The four WI-5178 residual failures remain
separately owned and are explicitly not grandfathered; they must be
completed or waived before any later terminal verification of WI-5640.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
