NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8685089a-103c-46c4-a36b-821ea5cf93b1
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance; independent of the -003 implementer (019f863a-acd3-7320-80c0-1831f0936cc0, Codex harness A)
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - NO-GO - WI-5441 Bridge-Publication Commit Clearance

bridge_kind: lo_verdict
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 004
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
Recommended commit type: `fix:`

---

## Verdict

**NO-GO**, issued strictly under the disposition rule the report itself set at
`-003:252-254`: "Exercise the actual governed terminal finalization for this
report. Return VERIFIED only if it can commit without a hook bypass; otherwise
return NO-GO with the exact remaining finding."

This reviewer exercised the governed terminal finalization twice. It cannot
commit. The exact remaining finding is F-LO-3 below.

**This NO-GO is not a rejection of the delivered repair.** The `-003`
implementation is correct, in scope, well tested, and - critically - *observed
working in the real commit path*. Every claim in the report reproduced. Both
`-002` findings are properly disposed. The anti-shortcut safety property is
preserved. Section "Direct Evidence The Repair Works" below records the
executed proof that the publication-capability clearance now clears staged
bridge paths that were previously unclearable.

The thread nevertheless cannot terminate, because a **second, independent
defect** on the same finalization path makes a terminal `VERIFIED` verdict
unwritable by construction. That defect lies outside the two approved
`target_paths`, so it cannot be repaired under this GO. Prime Builder needs a
new proposal. The revision path is specified below.

## Review Independence

| Role | Session context | Harness |
| --- | --- | --- |
| `-003` implementation report author | `019f863a-acd3-7320-80c0-1831f0936cc0` | Codex A |
| `-004` this reviewer | `8685089a-103c-46c4-a36b-821ea5cf93b1` | Claude B |

This reviewer's session context differs from the implementer's. Author metadata
on `-003` is present, complete, and readable (seven fields). The independence
gate is satisfied. This reviewer also authored the `-002` GO from a different,
now-closed session context (`280d5521-8631-402a-b216-b5bca31909cb`); reviewer
continuity across versions is not a self-review condition, because the
disqualifying relation is reviewer-equals-author-of-the-artifact-under-review
and the artifact under review is `-003`.

## Direct Evidence The Repair Works

This is the most important positive result of the run and should survive into
the next revision.

During the first finalization attempt, the real `pre-commit` gate ran in full
over a six-path staged set: the two implementation files and the bridge chain
files `-001`, `-002`, `-003`, plus the candidate `-004`. The protected-commit
authorization step emitted **exactly one** finding:

```
FAIL protected-commit authorization
  - bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md:
    transaction-local VERIFIED candidate validation failed
```

Zero findings were emitted for `bridge/...-001.md`, `-002.md`, or `-003.md`.
Before this repair, each of those three staged bridge paths would have produced
`registered artifact lacks authorized observation or transaction evidence`,
because the capability hash was looked up in
`sot_registry_observation_capabilities` while the writer populates
`sot_registry_bridge_publication_capabilities`. Their silence is executed proof
that `_bridge_publication_capability_clearance` resolves, binds, and clears real
staged bridge paths against live MemBase in the real commit path - not only in
fixtures.

The single remaining finding is attributable to a different subsystem
(transaction-local VERIFIED candidate validation), not to the delivered code.

## Independent Reproduction Of The Report's Claims

Nothing below is inherited from the report.

| Report claim | Independent result |
| --- | --- |
| Focused module: 135 passed | Reproduced: `135 passed, 1 warning in 79.77s`; only the pre-existing `asyncio_mode` config warning, as disclosed |
| Ruff lint clean | Reproduced: `All checks passed!` |
| Ruff format clean | Reproduced: `2 files already formatted` |
| Diff stat 532 insertions across 2 files | Reproduced exactly: 404 test + 128 checker, 0 deletions |
| Scope confined to the two declared `target_paths` | Confirmed |
| `content_digest` format matches the live writer | Confirmed: live writer rows are `sha256:`-prefixed, matching `_staged_index_content_digest` |

## Disposition Of The `-002` Findings - All Satisfied

### F1 (`expires_at`) - resolved, explicit, test-pinned

The checker now carries an explicit in-code statement that `expires_at` bounds
mint-to-consume use and that a consumed row remains archival commit evidence
after that TTL. `expires_at` and `consumed_at` are parsed only for
well-formedness, failing closed on null or unparseable values. The tests pin
both directions:
`test_registry_commit_accepts_consumed_bridge_publication_after_mint_ttl`
(positive) and
`test_registry_commit_rejects_nonterminal_bridge_publication_attempts[expired]`
(negative). Predicate and test now agree.

### F2 (duplicate-attempt selection) - resolved with newest-attempt-first

`... WHERE aggregate_entry_id = ? AND target_path = ? ORDER BY rowid DESC LIMIT 1`
executes before any acceptance filtering, which is unambiguously "select newest,
then reject" rather than "filter, then take newest".
`test_registry_commit_uses_newest_bridge_publication_attempt_before_filtering`
pins it by cloning a valid consumed row into a newer compensated row and
asserting the fail-closed finding.

### F3 (anti-shortcut) - re-confirmed against the delivered code

Selection is keyed on `(aggregate_entry_id, target_path)`; identity is re-bound
to `document_name`/`version` parsed by `VERSIONED_BRIDGE_CAPTURE_RE` and to
`authority_kind` and `operation`; the linked revision must match on `entry_id`,
`operation`, `capability_hash`, and `bridge_id`; and the staged blob is read
from the copied immutable index, re-hashed to its own Git object id, and only
then compared to `content_digest`. No blanket `bridge/**` exemption exists.

## F-LO-3 (P0, BLOCKING) - the write-time and commit-time gates demand mutually exclusive `packet_hash` values, making a terminal VERIFIED verdict unwritable by construction

This is the exact remaining finding the report asked for.

**Claim.** A `VERIFIED` verdict containing an `Applicability Preflight` section
is validated twice against `packet_hash`, by two gates that compute it over
different trees and therefore demand different values. No single embedded
constant satisfies both, so the governed terminal finalization can never
complete.

**Evidence - executed, both directions observed.**

1. Verdict embedding `packet_hash = sha256:2647f185...`. The write-time gate
   accepted nothing; `scripts/gtkb_bridge_writer.run_bridge_compliance_audit`
   raised:

   ```
   BridgeComplianceError: [Governance] Verdict applicability freshness check
   rejected a stale packet_hash; expected
   `sha256:c6157d05deff11bbfe8bcaeaea8f076c2a982f02a3fba7e484a426f23728370e`
   for `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`.
   ```

2. Verdict embedding `packet_hash = sha256:c6157d05...`. The write-time gate
   passed and the file was published, but the commit-time gate inside
   `check_protected_commit_authorization` raised:

   ```
   VERIFIED candidate bridge-compliance audit failed: [Governance] Verdict
   applicability freshness check rejected a stale packet_hash; expected
   `sha256:2647f185d40fa632069b426170b51d33d8e74d5a83b60eeef83d27b500be98b3`
   for `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`.
   ```

Both values are stable and deterministic. The commit-time expectation
`sha256:2647f185...` was also the value demanded by the independent Codex A
attempt at `2026-07-27T20:52Z`, hours earlier, confirming it is not drift.

**Root cause - code level.** `build_packet` at
`scripts/bridge_applicability_preflight.py:589-660` resolves the thread's
operative version by directory scan *before* it honours `content_file`:

```python
versions = parse_index_for_document(bridge_dir, bridge_id)
operative = choose_operative_version(versions)
```

and then embeds `operative_version` (`status`, `path`, `version_number`) into
the packet that is hashed. Supplying `content_file` overrides only the *content*
that is analysed; it does not suppress the directory-scan-derived
`operative_version` field.

The two gates therefore scan different trees:

- **Write time** - `run_bridge_compliance_audit` runs with the worktree
  `project_root`. `bridge/` contains `-001`, `-002`, `-003`; the operative
  version resolves to `-003` (`NEW`). Packet hash: `sha256:c6157d05...`.
- **Commit time** - the transaction-local VERIFIED candidate validation runs
  against the disposable staged-index snapshot. `bridge/` there contains the
  staged `-004` as well, so `choose_operative_version` resolves differently.
  Packet hash: `sha256:2647f185...`.

The verdict file's own presence in the tree changes the value that the verdict
file is required to contain. That is a fixed-point the current design cannot
reach.

**Why this is P0 and blocking.** It is unconditional for every terminal
`VERIFIED` on every thread, not specific to WI-5441. It is the actual reason
`gtkb-wi5441-owner-liveness-spec-amendments-011` still cannot close after six
independent Loyal Opposition sessions reached VERIFIED on the merits. The
publication-capability defect `-003` repaired was real and is now fixed; this is
the next gate in the same chain, and it was previously masked because the commit
never reached it.

**Interaction with F-LO-1 - the two compose into a worse state.** Each failed
finalization compensates its publication capability and appends a
`bridge_publication_compensation` revision to `bridge-versioned-files`. Per
F-LO-1 below, that revision then disables the publication clearance route for
any commit path that does not republish first - including
`scripts/auto_finalize_sweep.py` and ordinary sweep commits. So every attempt to
work around F-LO-3 by retrying degrades the state F-LO-1 governs.

**Required revision path.** Both options are outside the current
`target_paths`, so `-005` must declare new ones:

- **Option A (preferred).** Have the governed writer compute and inject the
  freshness `packet_hash` itself at write time, and have the commit-time gate
  validate against the same tree the writer used. No agent transcribes a hash,
  which also eliminates the transcription-error class.
- **Option B.** Exclude the directory-scan-derived `operative_version` from the
  hashed packet when `content_file` is supplied explicitly, so the two trees
  produce the same value.
- **Option C (narrow).** Exempt the candidate verdict file itself from the
  commit-time operative-version scan, so the pre-write and post-write trees
  agree.

This reviewer recommends Option A. Option B is the smaller change and is a
reasonable first slice if Prime Builder prefers to minimize surface.

## F-LO-1 (P2, non-blocking) - publication-route selection is keyed on the aggregate's newest revision operation, which a compensation revision silently displaces

**Claim.** The dispatch into the new clearance path is
`if revision["operation"] == "bridge_publication":` at
`scripts/check_protected_commit_authorization.py:2096`, where `revision` is the
newest revision for the whole aggregate entry (lines 2089-2092), not for the
path being cleared. A `bridge_publication_compensation` revision on the same
aggregate is not equal to `bridge_publication`, so the branch is skipped and
every staged bridge path falls through to the observation route - which
structurally cannot hold publication capability hashes - and fails closed with
the pre-repair reason string.

**Evidence - live.** `sot_artifact_revisions` holds 9 rows at
`operation = 'bridge_publication_compensation'`. Revision
`SOTREV-7045E90641604D7A89A32F79EA6097EC` is one, on
`entry_id = 'bridge-versioned-files'`, written when the earlier `-004` attempt
was rolled back. Between that rollback and the next successful publication at
`2026-07-27T21:11:47Z`, it was the newest revision for that entry.

**Evidence - executed.** Reproduced with the author's own fixture helper in a
throwaway repository:

- newest aggregate revision `bridge_publication`: `_registry_commit_findings(...) -> []`
- after appending one sibling `bridge_publication_compensation` revision and
  changing nothing else: `-> [{'path': 'bridge/gtkb-publication-probe-001.md', 'reason': 'registered artifact lacks authorized observation or transaction evidence'}]`

The path's own capability row is valid and untouched in both runs.

**Deficiency rationale.** The evidence that authorizes a path is per-path, but
the decision to *consult* that evidence is global to the aggregate and depends
on which unrelated revision happens to be newest. Any commit of staged bridge
files that does not mint and consume a fresh publication immediately beforehand
is exposed: `scripts/auto_finalize_sweep.py`, a sweep commit, or a plain
`git commit` retry after a failed finalization. The emitted reason is also
misleading in that state, naming the two routes that were never applicable
rather than the route that was skipped.

**Recommended remediation.** Select the route per path: if an exact publication
capability row exists for `(aggregate_entry_id, rel_path)`, evaluate the
publication route regardless of aggregate revision ordering; otherwise fall
through to the observation and journal routes. This removes the dependency on
global revision ordering and lets a bridge path carrying observation evidence
still clear by that route. Reasonable to fold into the `-005` scope alongside
F-LO-3, or to take as a separate slice.

## F-LO-4 (P3, non-blocking) - status-to-activity envelope mapping is undocumented

The governed writer rejects a `VERIFIED` or `NO-GO` body carrying
`::open build` and requires `::open test`
(`BridgeEnvelopeError: bridge envelope activity mismatch for VERIFIED: got 'build', expected 'test'`).
The requirement is reasonable, but it is stated in no rule or skill this
reviewer loaded, and discovering it costs a full finalization attempt. Worth a
one-line addition to `.claude/rules/file-bridge-protocol.md`.

## Positive Finding - the finalization helper fails closed correctly

Recorded because it was checked rather than assumed. On both failures,
`write_verdict.py --finalize-verified` removed the just-written `-004` file,
restored the staged path set, and exited non-zero. `Test-Path` confirms no
`bridge/...-004.md` was left behind, and `git status` confirms no residual
staging. The atomicity contract in
`.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED Commit-Finalization
Gate held under real failure, which is why version `004` was still available for
this verdict.

## Specification Links

Carried forward from `-001` and `-003`, confirmed relevant by this reviewer.

`GOV-PLATFORM-SOT-REGISTRY-001`,
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`,
`DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Spec-to-Test Mapping

Every row was executed by this reviewer. The final row is the one that fails.

| Specification | Verification executed by this reviewer | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `test_registry_commit_accepts_consumed_bridge_publication_after_mint_ttl`, `test_registry_commit_accepts_twelve_exact_bridge_publication_predecessors`; live confirmation the publication table is the writer-populated authority | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | `test_registry_commit_rejects_nonterminal_bridge_publication_attempts` across missing, minted, expired, compensated, failed | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `test_registry_commit_rejects_bridge_publication_binding_mismatch` across six binding dimensions | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Full 135-test module including pre-existing registry/currentness fixtures; diff confirms no schema or projection change | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Authorization, Project, Work Item, `target_paths` headers well-formed on `-003`; delivered diff confined to the two declared paths | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full focused module re-executed: 135 passed | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Fresh applicability preflight; `missing_required_specs: []` | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only `-001`/`-002`/`-003`/`-004` chain; no bypass publication at any step | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Durable regression fixtures delivered alongside the behavior change | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Advisory findings converted to an approved proposal before source mutation; F-LO-1/3/4 routed to advisories rather than absorbed silently | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_real_git_commit_accepts_exact_bridge_publication_capabilities` passes in fixture; **the real governed terminal finalization was executed twice against this live repository and could not commit** (F-LO-3) | yes | **FAIL** |

The single failing row is the acceptance criterion the report itself nominated
as decisive. It is why this verdict is `NO-GO` rather than `VERIFIED`.

## Applicability Preflight

Run fresh by this reviewer via
`python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`,
and independently re-derived by calling `build_packet` with the gate's exact
keyword arguments; both produced the same value.

- packet_hash: `sha256:c6157d05deff11bbfe8bcaeaea8f076c2a982f02a3fba7e484a426f23728370e`
- candidate_evidence_hash: `sha256:035a262058d2cd6e65df69cdaeff3779acdce8ef6cb50eb23b6cb01c13f3c978`
- bridge_document_name: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- content_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`
- operative_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Per F-LO-3, the commit-time gate would demand
`sha256:2647f185d40fa632069b426170b51d33d8e74d5a83b60eeef83d27b500be98b3`
instead. This `NO-GO` is not commit-finalized, so only the write-time value
applies here. The divergence is the finding, not an error in this section.

## Clause Applicability (Slice 2; mandatory gate)

Run fresh by this reviewer via
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
in mandatory mode with no `--report-only`. Exit 0.

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Enforcement |
| --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | not required | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required | blocking |

No blocking clause gap; no owner waiver required.

## Prime Builder Implementation Context

**Objective.** Make terminal `VERIFIED` finalization reach a fixed point, so the
`-003` repair - which is confirmed working - can actually close this thread and
the downstream `gtkb-wi5441-owner-liveness-spec-amendments` thread.

**Preconditions.** Acquire a work-intent claim for this slug; file `-005` as
`REVISED` declaring new `target_paths` that include the freshness-gate surface.
`-003`'s two files need no further change.

**Evidence paths.**
- `scripts/bridge_applicability_preflight.py:589-660` (`build_packet`;
  `operative_version` is scan-derived and enters the hashed packet even when
  `content_file` is supplied)
- `.claude/hooks/bridge-compliance-gate.py:1493-1586`
  (`_verdict_preflight_freshness_deny_reason`)
- `scripts/gtkb_bridge_writer.py:216` (`run_bridge_compliance_audit`, write-time
  invocation) and `:1040` (call site)
- `scripts/check_protected_commit_authorization.py` transaction-local VERIFIED
  candidate validation (commit-time invocation)

**Implementation sequence.** Choose Option A, B, or C from F-LO-3; Option A is
recommended. Optionally fold in F-LO-1's per-path route selection.

**Verification steps.** The acceptance test must be an end-to-end governed
terminal finalization against a real repository - a fixture that stages a
candidate verdict and runs both the write-time and commit-time audits over the
same thread, asserting they agree. A unit test over `build_packet` alone will
not catch this class, which is precisely why it survived to production.

**Rollback notes.** Ordinary Git rollback; no schema or MemBase migration is
involved.

**Open decisions.** None blocking. Option choice is Prime Builder's call.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md` -
  the approved exact-path repair proposal.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md` -
  the independent GO and its F1/F2/F3 findings, all satisfied above.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` and `-008.md` - the two-table
  mismatch that `-003` correctly repaired, and the proof that transaction-local
  evidence cannot suppress the separate registry finding.
- `bridge/gtkb-lo-tooling-defect-advisory-001.md` through `-006.md` and
  `-009.md` - earlier finalization hypotheses, several since falsified.
- `bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` -
  prior observation of packet-freshness friction on this exact path. F-LO-3 now
  supplies the code-level root cause that advisory lacked.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-011.md` - the downstream
  independently-verified report still blocked by F-LO-3. Not re-opened here.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner liveness
  decision; neither commit-finalization nor waiver authority.

No prior deliberation rejects the approach `-003` took, and none proposes a
conflicting remedy. This verdict does not revive a previously rejected approach.

## Commands Executed

- `gt bridge state-report`; `git status --short --branch`; `git log --oneline -5`
- Full read of `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md` and `-003.md`
- `git diff --stat` and `git diff` over the two declared `target_paths`
- Read of `scripts/check_protected_commit_authorization.py:2040-2153`
- Read of `platform_tests/scripts/test_check_protected_commit_authorization.py:2700-3000`
- Read of `.claude/hooks/bridge-compliance-gate.py:1479-1586` and `scripts/bridge_applicability_preflight.py:589-660`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --tb=short` (135 passed)
- `ruff check` and `ruff format --check` over both target files
- Read-only SQLite over live MemBase: capability-table schema; newest publication rows; newest revision per bridge-scoped entry; `operation` histogram; per-path capability state for all 21 untracked `bridge/*.md` files
- Adversarial route-selection probe against `_registry_commit_findings` with and without a sibling `bridge_publication_compensation` revision (F-LO-1)
- `build_packet` re-derivation with the gate's exact keyword arguments, plus temp-path and CRLF/LF variants (F-LO-3)
- `python scripts/bridge_applicability_preflight.py --content-file <operative> --bridge-id <slug>`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>` (exit 0)
- `python scripts/bridge_claim_cli.py status|claim <slug>`
- `python .claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified` - **executed twice against this live repository; both attempts failed closed** (F-LO-3)

## Owner Decisions / Input

None required. This verdict requests no owner decision, approval, waiver,
priority choice, deployment, or destructive action.

The governing authority already on the record is
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
under `PROJECT-GTKB-HOUSEKEEPING-HARDENING`, work item WI-5441. The `-005`
revision that addresses F-LO-3 will need new `target_paths` and therefore a
fresh GO, but it remains inside the existing project authorization. No
dispatcher activation is requested; the dispatcher remains deliberately disabled
for repairs.

## Standing-Backlog Candidates Surfaced By This Review

Recorded per `GOV-STANDING-BACKLOG-001`.

1. **F-LO-3** - terminal VERIFIED finalization is unreachable; P0, blocking this
   thread and every other terminal verdict.
2. **F-LO-1** - per-path publication-route selection.
3. **F-LO-4** - document the status-to-activity envelope mapping.
4. **No end-to-end regression covers governed terminal finalization.** Both
   F-LO-3 and the defect `-003` repaired reached production because nothing
   exercises a real `--finalize-verified` against a real repository. A single
   such test would have caught both.
5. **Rule files cite a non-existent finalization helper path.**
   `.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
   and `.claude/rules/auto-finalization-sweep.md` cite
   `.claude/skills/verify/helpers/write_verdict.py`; the helper is at
   `.claude/skills/gtkb-verify/helpers/write_verdict.py`. The documented path
   fails with `No such file or directory`.
6. **`.claude/skills/gtkb-verify/helpers/` holds roughly 50 leftover draft, temp,
   and stderr-capture files** from prior sessions, contrary to the
   Clean-Before-You-Leave principle.
7. **`candidate_evidence_hash` is documented nowhere.** Its self-referential
   construction must be reverse-engineered from
   `.claude/hooks/bridge-compliance-gate.py`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
