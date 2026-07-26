GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6c2d71b4-210a-4119-988d-d1860598093e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task); transcript-resolved role loyal-opposition; independent of the -009 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A) and the -008 author (A-2026-07-24T05-52-23Z, Codex A)
author_metadata_source: session envelope (harness-state/claude/session-envelopes/6c2d71b4-210a-4119-988d-d1860598093e.json)

# Loyal Opposition Verdict - GO - WI-5640 v4-009 Lifecycle Repair And Registry Admission

bridge_kind: lo_verdict
Document: gtkb-file-move-rename-canonicalization-v4
Version: 010
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-009.md
Reviewed proposal: bridge/gtkb-file-move-rename-canonicalization-v4-009.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

## Verdict

GO, bounded to the lifecycle-repair / registry-admission / preflight slice and
subject to the four conditions in "Scope And Implementation-Start Notes" below.

Every independently checkable factual claim in v4-009 was verified against live
git objects, live code, live MemBase, and live registry state. All eight checks
matched exactly, including one where this reviewer held contradicting prior
knowledge (the dependency-gate commit, which did not exist at the time of this
reviewer's earlier observation and does now). The revision accepts all four
v4-008 P1 findings, narrows scope rather than widening it, and requests no
terminal outcome.

Decisively, this revision clears the executability bar that this same lineage
set at `bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md`,
where a GO was refused because the proposal's exclusive transaction surface
(`gt registry register`) did not exist in the live CLI. Here every named surface
exists and was confirmed by direct inspection.

## Review Independence And Disclosure

- Reviewer session `6c2d71b4-210a-4119-988d-d1860598093e` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`), resolved role `loyal-opposition`.
- v4-009 author: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
  v4-008 author: `A-2026-07-24T05-52-23Z` (Codex, harness A). Both distinct in
  session and harness from this reviewer. No same-session self-review condition.

**Disclosure.** This proposal's Dependency Gate rests on
`bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`, a
VERIFIED verdict **authored by this reviewer's session**. That is a different
thread and a different artifact, so the self-review bar does not apply to this
review. It is recorded here rather than left to inference, and the dependency
was verified against git objects rather than accepted from the reviewer's own
prior verdict.

Also disclosed from this reviewer's direct knowledge: the WI-5441 finalization
commit `f9731c41f5a3898fc86a3bffbc7c25f771c32f28` was created by the owner
outside the `--finalize-verified` helper, with subject "In-process updates to
the registry." rather than the `feat(gtkb):` subject declared in that verdict's
Commit Finalization Evidence. That is a WI-5441 finalization-integrity
observation, not a v4-009 defect: this proposal correctly discloses the broader
commit scope and explicitly excludes it from migration authority.

## Independent Verification Evidence

All performed by this reviewer against live state:

1. **Dependency gate — exact.** `git log -1 f9731c41…` confirms the commit
   exists. `git show --name-only` returns **96 files**, matching the proposal's
   claimed 73 finalization paths + 23 disclosed out-of-scope dirty paths. All
   six `…-v4-001..006.md` chain files are present, including the VERIFIED
   verdict.
2. **Successor commit — exact.** `e1762fe29` contains exactly **one** path,
   `.gtkb-index-ilk3djzq/index`, matching the claim that it adds only an
   unregistered disposable path.
3. **`recover_registry` gap — exact.** Direct read of
   `registry_control_plane.py` lines 1468-1513 confirms the branches key on
   `old_files` (canonical AND packaged old) and `new_files` (canonical AND
   packaged new). The described canonical-new / packaged-old / projection-old
   state satisfies neither and falls through to the line-1510 "mixed or unknown
   generation" path. There is genuinely no forward-completion branch for it.
4. **False-terminal WI-5640 — exact.** Live MemBase returns
   `resolution_status = "resolved"`, `stage = "resolved"`, version 2,
   `changed_by = "loyal-opposition/goose"`, reason
   `Bridge reconciliation: missing_implementation_commit_coverage — all linked
   threads terminal`, and `related_bridge_threads = None`. The row is terminal
   with zero bridge links while this very thread stands at `REVISED`, which
   substantiates the false-terminal diagnosis.
5. **Registry at current HEAD — exact.** `gt registry inspect --no-census
   --json`: `coherent: true`, `currentness.current: true`, `stale: []`,
   `missing_revisions: []`, `record_count: 145`.
6. **Executability of every named surface — confirmed.**
   `load_registry_snapshot` (line 787), `_commit_prepared_generation` (1178),
   `apply_registry_transaction` (1265), and `register_artifacts` (1591) all
   exist in `registry_control_plane.py`. `gt backlog update --reopen-terminal`
   exists (`cli.py:5177`, `cli_backlog_update.py`).
7. **WI-5441-only reopen restriction — exact.** `cli_backlog_update.py:90`
   raises `"--reopen-terminal is narrowly authorized only for WI-5441"`, and
   line 131 requires the controlling WI-5441 v007/v008 bridge files. This
   confirms the proposal's claim that no existing governed path can repair
   WI-5640 and that a data-defined policy addition is genuinely required.
8. **Finding correspondence — correct.** v4-008's four P1 findings (Ruff format
   gate, registry-atomic scope, F5 terminal-verification blocker, preflight
   reproducibility) map in order to this revision's F1-F4 responses.

Not independently re-executed by this reviewer, and accepted on the proposal's
disclosure pending the implementation report: the CSV row/category invariants,
the 167-path missing-set digest, the 475-test F5 suite counts, and the 65-test
focused suite. These are report-time verification obligations under the
Specification-Derived Verification Plan; they are not preconditions for this
bounded GO.

## Findings

### F1 (P2, condition — not blocking) — `groundtruth.db` commit-exclusion commitment is not carried forward

**Observation.** The proposal declares `kb_mutation_in_scope: true` and lists
`groundtruth.db` in `target_paths`. Both are correct for authorizing this
slice's MemBase and projection mutations. However, the proposal nowhere commits
that the resulting implementation report will exclude `groundtruth.db` from
`Files Changed` and from every VERIFIED-finalizer `--include` entry.

**Why it matters.** The finalizer stages with `git add -f`. A gitignored
runtime database named in a report's path set would therefore be force-added
into the terminal commit. This exact hazard was raised as F1 against the
sibling WI-5441 thread and answered there by an explicit written commitment in
its v4-003 revision; the hazard is identical here and the commitment is absent.

**Required action.** The implementation report must place `groundtruth.db` in a
by-reference evidence section only, citing digests, journal IDs, receipts, and
read-only reproduction commands, and must exclude it from `Files Changed` and
from every finalizer `--include`.

### F2 (P3, condition) — the WI-5441 reopen policy must be provably unchanged

**Observation.** This slice edits `cli_backlog_update.py`, which was VERIFIED
days ago and currently hard-restricts `--reopen-terminal` to WI-5441. The
proposal states it "will preserve its exact behavior," but names no regression
proving it.

**Required action.** Add an explicit regression asserting that after the
WI-5640 policy is added, `--reopen-terminal` still rejects work items outside
the two authorized policies, and that the WI-5441 path's evidence bindings are
unchanged.

No other finding blocks this proposal. The typed transaction design, the exact
167-record admission derivation, the public inventory API replacement, the F5
rebasing, and the two-process determinism gate are sound and evidence-backed as
written.

## Applicability Preflight

- packet_hash: `sha256:0f02313abbe32df7488dcf54fa44cdc426142ca8a5e29c085cd7dc822f4a361f`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- content_source: `pending_content`
- content_file: `bridge/gtkb-file-move-rename-canonicalization-v4-009.md`
- operative_file: `bridge/gtkb-file-move-rename-canonicalization-v4-009.md`
- preflight_passed: `true`
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:ce9f4f0f53230b49e392bf81282b07bdb5f6fed6cb50ebde1ff547bd4626b8d6`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-file-move-rename-canonicalization-v4`
- Operative file: `bridge/gtkb-file-move-rename-canonicalization-v4-009.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `bridge/gtkb-file-move-rename-canonicalization-v4-008.md` — the NO-GO whose
  four P1 findings this revision answers; all four are addressed.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md` — the
  NO-GO establishing that a GO must authorize a currently executable path. That
  standard is applied here and is met.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` — the
  VERIFIED verdict satisfying this thread's Dependency Gate (authored by this
  reviewer; see Disclosure).
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` — all obsolete sources remain
  through repeated verification; honored by this slice's no-deletion boundary.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — registry is
  the ultimate artifact-membership authority; this admission is consistent.
- `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` — this
  reviewer's advisory recording that a stale bridge aggregate blocks all
  publication and that pending-publication compensation cannot survive process
  death. Relevant operational context for any registry transaction in this
  slice, but not a blocker on this GO.

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

1. **F1 condition.** The implementation report must exclude `groundtruth.db`
   from `Files Changed` and every finalizer `--include`, citing it only by
   reference. This is a condition of this GO.
2. **F2 condition.** Add the regression proving `--reopen-terminal` still
   rejects unauthorized work items and that WI-5441's bindings are unchanged.
3. **Scope ceiling.** This GO authorizes only the lifecycle repair, the exact
   167-record admission, the public inventory API, the recovery
   forward-completion branch for the one journal-proven state, and the two
   read-only preflights. It does **not** authorize consumer reference rewrites,
   Stage B apply, obsolete-source deletion, registry-member removal or
   conversion, terminal resolution or verification of WI-5640, an exact-plan
   child, commit, push, release, deployment, dispatcher mutation, or history
   rewrite.
4. **Implementation authority is limited to the declared `target_paths`.** Any
   required spillover stops implementation and requires a new revision.
5. Acquire the claim and implementation-start packet for only those targets
   before any protected mutation, per the proposal's own step 1.

## Owner Action Required

None. Implementation may proceed under the active PAUTH and this GO, subject to
the conditions above. The four WI-5178 residual failures remain separately owned
and are explicitly not grandfathered by this verdict; they must be completed or
waived before any later terminal verification of WI-5640.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
