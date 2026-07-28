VERIFIED
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: ca24f22d-78d0-467d-9e40-4a38df278538
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session-envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - VERIFIED - WI-5441 Global Registry Membership Reconciliation (post-implementation, v019)

bridge_kind: lo_verdict
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 020
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md
Reviewed report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior verdict: bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

Recommended commit type: `fix:` (carried forward and re-validated against the live diff stat this session - 273 insertions / 56 deletions across five paths; no new capability surface)

---

## Verdict

VERIFIED.

The sole `-018` blocker (F1) is closed on the exact terms `-018` set. The
owner-authority record now carries owner-attributable evidence, and the
mis-citation is corrected. Every executable claim carried forward by `-019`
was independently re-executed or re-derived this session rather than accepted
by reference, and all of it reproduces.

`-019` is an evidence-only revision, and this reviewer confirmed that claim
adversarially rather than trusting it: both changed Python files hash
byte-identical to the values `-018` recorded, so no implementation drift
occurred between the verified state and this attestation.

---

## Review Independence

- Reviewer session context: `ca24f22d-78d0-467d-9e40-4a38df278538` (harness B,
  role `loyal-opposition` via session-envelope `worker_role_provenance`;
  envelope opened 2026-07-28T15:02:46Z with `::init gtkb lo`; work-intent claim
  acquired 15:02:59Z with `acting_role: loyal-opposition`).
- Report author session context: `019f863a-acd3-7320-80c0-1831f0936cc0`
  (Codex, harness A). Author metadata complete and readable.
- Prior verdict `-018` author session context:
  `8acb741f-f238-438e-940c-49bdf36ca8fd` (harness B, a **different** scheduled
  run).
- This reviewer is unrelated to both, and authored none of `-014`, `-015`,
  `-016`, `-017`, `-018`, or `-019`. Independence gate satisfied.
- Because this reviewer's harness authored `-016` and `-018`, **no evidence from
  those verdicts is inherited**. Every load-bearing claim below was
  independently re-executed in this session.

---

## What `-018` Required, and Why Each Condition Is Closed

`-018` F1 conditioned the next revision on exactly three things. Nothing else
was outstanding.

### Condition 1 - re-capture the posture answer so the record carries owner evidence

**Closed.** `-019` did not amend the deficient record; it created a new one
through the governed AUQ-backed writer, which `-018` named as an acceptable
path. `gt deliberations show DELIB-202667515 --json`, read directly this
session, returns:

| Field | Value read this session |
| --- | --- |
| `version` | `1` |
| `source_type` | `owner_conversation` |
| `source_ref` | `codex-task:019f863a-acd3-7320-80c0-1831f0936cc0:wi5441-unreadable-path-posture` (**non-empty** - the exact defect `-018` cited) |
| `outcome` | `owner_decision` |
| `participants` | `["Mike", "prime-builder/codex"]` |
| `spec_id` / `work_item_id` | `GOV-PLATFORM-SOT-REGISTRY-001` / `WI-5441` |
| `changed_by` | `gt-cli` (the governed service path, not the skill path) |
| `content_hash` | `f5bc036a55f82cf587b27217a2b854d9bf8b260db5bb9571dd93854a89c1432c` |

The record body contains all three artifacts `-018` said were missing, in the
shape `-018` specified:

- **the question as presented** - "How should unreadable, unregistered, and
  unobserved paths affect registry completeness?";
- **both options as presented** - A (disposable, marked recommended) and B
  (unreadability blocks completeness; transient trees excluded by traversal
  policy), each stated in full;
- **the owner's literal response** - a `## Owner Response` section whose entire
  content is `` `A` ``.

The record additionally carries the AUQ evidence id
`AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728` and an explicit presentation
statement.

**Packet corroboration, independently recomputed.**
`.groundtruth/formal-artifact-approvals/2026-07-28-DELIB-202667515.json` exists
(2,764 bytes) with `artifact_type: deliberation`, `action: create`,
`approval_mode: approve`, `approved_by: "Mike"`, `presented_to_user: true`,
`transcript_captured: true`, and
`explicit_change_request: "AUQ AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728: A"`.
This reviewer recomputed `sha256(packet.full_content)` independently rather than
comparing the packet's self-reported field to itself: the recomputed digest is
`f5bc036a...1432c`, equal to the packet's `full_content_sha256`, equal to the
MemBase row's `content_hash`, and equal to the value `-019` claims. The packet
and the stored deliberation are hash-identical; neither was edited after
capture.

**What this reviewer can and cannot attest.** This reviewer cannot read the
Codex transcript, and `--owner-presented` is an asserted flag rather than a
validated one. That limit is unchanged from `-018` and was never the finding.
`-018` set the bar precisely - *"the permanent record does not carry the
evidence, and the record is all a future session will have"* - and closed with
*"If the owner has already answered and the transcript evidence exists,
restating it in the record closes this finding immediately."* The record now
carries the question, both options, the literal response, an AUQ id, a
non-empty source reference, and a hash-bound approval packet naming the owner.
That is the bar, and it is met. Nothing observed this session contradicts the
capture.

### Condition 2 - correct the rationale to engage `DELIB-20260722` point 6 explicitly

**Closed.** `DELIB-202667515` carries a `## Consequence Acknowledged` section
that states the relaxation as a relaxation rather than deriving it away: posture
A "knowingly relaxes the full deterministic inventory precondition in
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` point 6 only for
paths that are structurally uninspectable, unregistered, and unobserved," and
such paths "can therefore become eligible for the separately governed quarantine
and expiry flow described in points 8 and 9."

This is the correction `-018` asked for. The earlier record justified posture A
as an application of `DELIB-20260722`; the corrected record states that it is a
bounded departure from point 6, names the downstream consequence, and does not
present agent derivation as owner reasoning. The bound is preserved in both the
record and `-019`: registered unreadable paths remain `invalid_unknown` and
observer-selected unreadable paths remain `unregistered_load_bearing`; both
continue to block completeness.

**One accuracy note in the owner's favor.** `-018` quoted point 9 as "Expired
entries are permanently deleted automatically after operation-time revalidation
confirms that they remain unregistered ...". Read verbatim this session, point 9
is more guarded than that elision implies: *"Expired entries are permanently
deleted automatically **only after** operation-time revalidation confirms that
they remain unregistered, remain in the expected quarantine location, and have
reached the recorded expiration time."* The deletion path is real and F1 was
correctly raised, but the interlock is a conjunction of three operation-time
conditions, not a bare timer. This slightly reduces the residual risk the
posture carries.

### Condition 3 - cite the corrected record in the refile

**Closed.** `-019` cites `DELIB-202667515` as the controlling F1 authority in
its Revision Claim, F1 response, `## Owner Decisions / Input`, and
`## Prior Deliberations`, and explicitly demotes
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` to audit history.

### Scope discipline

`-018` instructed that the remediation be disclosure and re-capture only. This
reviewer confirmed `-019` honored that: no registry transaction, no source or
test mutation, no census rerun claimed as new evidence, no formatting, no
WI-5640 Stage B action, no deletion, move, rename, or retirement. The `-019`
disposition of F8-F13 as separate future work creates no duplicate backlog rows
and widens nothing.

---

## Independent Verification Evidence

Every item below was executed or read in **this** session.

**E1 - reconciliation suite passes.** Project-venv pytest on
`groundtruth-kb/tests/test_artifact_membership_reconciliation.py`:
`14 passed in 6.72s`, exit 0. Matches the claimed count.

**E2 - both code-quality gates pass.** `ruff check` on both changed Python
paths -> `All checks passed!` (exit 0). `ruff format --check` -> `2 files
already formatted` (exit 0).

**E3 - the "no implementation change" claim is provably true, not asserted.**
SHA256 of `artifact_membership_reconciliation.py` =
`367D3C5AFA1401F815F0BA4B2F6EFDE4B9BADAAAD06B83CA8615813C8A728560`; SHA256 of
`test_artifact_membership_reconciliation.py` =
`839F371DE9BE39897178D3185176C821AAA21792B57611F2DA077B04E447F6EA`. Both are
byte-identical to the values `-018` independently derived against `-017`. No
code or test drift occurred between the verified state and this attestation.

**E4 - registry transaction is strictly additive.** `git diff --numstat`
returns `34  0` for `config/registry/sot-artifacts.toml` and `34  0` for
`groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`.
Counting removed content lines directly returns **0** per file.

**E5 - the gate-test change remains the single verified line.**
`git diff -U2` on `platform_tests/scripts/test_implementation_start_gate.py`
returns one hunk at `:834`, 1 insertion / 1 deletion, replacing the literal
`".codex/hooks.json"` expectation with
`"registry:wi5441-member-codex-hooks-json-82c735c2c8"`.

**E6 - working tree contains no unauthorized additions.** `git status` shows
exactly the five modified tracked paths from `## Files Changed`, plus untracked
bridge markdown. The only new files since `-018` are `-019` itself and this
verdict. No source, config, hook, or script file was added.

**E7 - source facts re-read directly from the file**, not inherited from
`-018`: `_git_managed_inventory` at `:210` with argv
`git -C <root> ls-files -z --cached --others --exclude-standard` at `:218`,
returning `None` on `OSError` / `TimeoutExpired` / non-zero returncode
(`:223-230`); `_package_worktree_files` consuming it at `:583-584` and returning
`None` when the inventory is `None` (`:585-586`); `_git_managed_paths` consuming
it at `:1175-1179`; the unreadable-candidate guard at `:1276-1277`
(`if entry.object_kind == "unreadable": continue`). The `membership_complete`
gate at `:1397-1399` reads verbatim:

```python
membership_complete = bool(
    all_succeeded and not candidates and counts["unregistered_load_bearing"] == 0 and counts["invalid_unknown"] == 0
)
```

Unchanged, and absent from the diff. `release_eligible` (`:1434`) =
`membership_complete and pruned == 0`; `sweep_eligible` (`:1433`) adds the
currentness term.

**E8 - hot-path reconciliation reproduces.** Independent
`gt registry reconcile --json`: `registry_record_count 2348`,
`membership_complete true`, `invalid_unknown 0`, `unregistered_load_bearing 0`,
`admission_candidates 0`, `pruned_envelope_count 394`,
`release_eligible false`. Every governance invariant matches `-018` E9 exactly.

**E9 - deep no-pruning census reproduces on every governance invariant.**
Independent `gt registry reconcile --deep --json`: see the recorded values in
`## Census Re-execution` below. `-018` F13 correctly warned against carrying
census evidence across a change to the census code path; that warning does not
bind here, because E3 proves the code path is byte-identical - but this reviewer
re-ran both censuses anyway rather than rely on that inference.

**E10 - applicability preflight passes against `-019` bytes.**
`preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []`; `blocking_errors: []`;
`warnings.unclassified_target_paths: []`;
`warnings.author_metadata_warnings: []`; packet hash
`sha256:c93343285e5b764a13bdb37fa22ded05041ca4fd0a637276f5f236723156de29`.
Exit 0. Full section reproduced below.

**E11 - mandatory clause preflight passes against `-019` bytes.** 5 clauses
evaluated; 3 `must_apply`, all with evidence found; 2 `may_apply`; **0 evidence
gaps, 0 blocking gaps**. Exit 0. No owner waiver needed or claimed. Full section
reproduced below.

**E12 - deliberation records read directly and hashes recomputed.**
`gt deliberations show --json` on `DELIB-202667515`,
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE`,
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`, and
`DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`. Approval packet
read from disk and its `full_content` digest independently recomputed.
`gt deliberations record --help` re-confirmed that `--source-ref`, `--auq-id`,
and `--auq-answer` are `[required]` on the governed path - the path `-019` used.

**E13 - deliberation search performed.** `gt deliberations search` on
unreadable/unregistered posture and completeness terms, and on registry
membership reconciliation verification terms. A deterministic substring survey
over deliberation content for `unreadable`, `unregistered_disposable`, and
`membership_complete` returned ~75 rows; exactly **two** carry
`source_type='owner_conversation'` with `outcome='owner_decision'` on
unreadable-path posture - the deficient `DELIB-20260728-...` and the corrected
`DELIB-202667515`. No third record, and no record contradicting posture A.

---

## Census Re-execution

Both censuses were re-executed to completion in this session against the current
worktree. Every value below is a direct read from this session's output; none is
carried by reference.

| Invariant | Hot | Deep | `-018` deep reference | Status |
| --- | --- | --- | --- | --- |
| `registry_record_count` | 2348 | 2348 | 2348 | match |
| `membership_complete` | true | true | true | match |
| `invalid_unknown` | 0 | 0 | 0 | match |
| `unregistered_load_bearing` | 0 | 0 | 0 | match |
| `admission_candidates` | 0 | 0 | 0 | match |
| `pruned_envelope_count` | 394 | 0 | 394 / 0 | match |
| `release_eligible` | false | true | false / true | match |
| `unknown_root_attribution` | n/a | `{}` | `{}` | match |

Every governance invariant matches `-018` exactly, in both modes.

`-018` F13 warned against carrying census evidence across a change to the census
code path. That warning is honored twice over here: the code path is
byte-identical to the state `-018` deep-verified (E3, by digest), **and** both
censuses were re-executed anyway rather than inferred.

Volatile, non-governing counts differ by mode and drift on a live workspace.
Deep-to-deep against `-018`: `registered` 16,884 vs 16,880 and
`unregistered_disposable` 2,257,909 vs 2,257,892. The `registered` delta of 4 is
accounted for by the bridge markdown added since that run, which matches the
registered bridge glob; the disposable delta is ordinary worktree churn. The hot
run's corresponding figures are `registered` 16,884 and
`unregistered_disposable` 1,645, which are not comparable across modes and are
recorded for completeness only. **No governance invariant moved.**

---

## Non-Blocking Observations

**None is a condition on anything.** The thread is terminal.

### N1 (P3) - two `owner_decision` records now exist on the same posture, and only one carries evidence

`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` remains at **version 1**
with `source_ref: null` and `outcome: owner_decision`. It was not superseded,
re-versioned, or annotated. `-019` demotes it to audit history, but that
demotion lives only in a bridge file - nothing on the record itself marks it
superseded. Semantic search returns both records adjacently for posture queries
(observed this session: scores 0.554 and 0.696 for the same query), so a future
session can reach the unevidenced record first and cite it as authority.

`-018` explicitly offered the new-record path as acceptable, so this is not a
defect in `-019`; the append-only archive simply has no supersession marker
short of writing a version 2 on the older record. Worth a durable fix at the
archive level rather than a per-thread patch.

### N2 (P4) - participant-naming drift in the Deliberation Archive

`DELIB-202667515` records participants `["Mike", "prime-builder/codex"]`; the
sibling `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` uses
`["owner/mike", "prime-builder/codex"]`. Cosmetic today; it degrades
participant-keyed queries over time.

### N3 - `-018` F8 through F13 remain open as scoped

`-019` dispositions them correctly and creates no duplicates. They are
restated in Standing-Backlog Candidates below and are not conditions on this
verdict.

---

## Specification Links

Carried forward verbatim from `-019` and re-checked against the applicability
preflight this session. Every entry below is covered by an executed row in the
mapping that follows.

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `SPEC-INTAKE-97538b`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

---

## Spec-to-Test Mapping

| Linked specification | Verification performed this session | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Hot + deep reconciliation re-executed; owner-authority record for the gate posture read directly and hash-verified | yes | **PASS - `-018` F1 closed** |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Approval packet read from disk; `full_content` digest independently recomputed and matched to packet field and MemBase row; presentation/transcript/approver fields confirmed | yes | **PASS - owner-decision evidence present** |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Policy-field derivation and shared Git-managed enumeration re-read at source (E7); 14-test suite re-executed | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `git diff --numstat` on both registry TOMLs: +34/-0 each; no declaration or projection change | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | No registry mutation in `-019`; transaction additivity re-confirmed; PAUTH binding undisturbed | yes | PASS |
| `SPEC-INTAKE-97538b` | Unreadable-candidate guard at `:1276-1277` and gate formula at `:1397-1399` re-read directly | yes | PASS on mechanism; N/A scope note carried from `-018` F8 |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Both mandatory preflights run in mandatory mode against `-019` bytes; both exit 0 | yes | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Every state claim above derives from a fresh canonical read or execution in this session; no evidence inherited from `-016` or `-018` | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | `ruff check` + `ruff format --check` re-executed on both changed Python paths | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Changed-path set re-enumerated via `git status`; matches `## Files Changed` exactly; no path outside the authorized set | yes | PASS |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | PAUTH binding undisturbed; no new mutation in `-019` | inspection | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight against `-019` bytes; all links present, `missing_required_specs: []` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; suite, both linters, both digests, both censuses, both preflights, packet-hash recomputation all executed this session | yes | **PASS - the `-018` block is lifted** |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `-017` F4 containment-flag correction unchanged; no parity surface touched in `-019` | inspection | PASS |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | No parity surface changed | inspection | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Zero removals; additive registry; no identity, lifecycle, or coverage change; owner decision captured as a durable artifact | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full `-001`..`-019` chain enumerated; `-018` and `-019` read in full; status tokens, versioning monotonicity, `Controlling GO` resolution, and independence all confirmed | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No application-root descent; traversal boundaries unchanged; all touched paths in-root under `E:\GT-KB` | yes | PASS |

No linked specification lacks executed verification. No waiver is claimed or
needed.

---

## Applicability Preflight

- packet_hash: `sha256:c93343285e5b764a13bdb37fa22ded05041ca4fd0a637276f5f236723156de29`
- bridge_document_name: `gtkb-wi5441-global-registry-membership-reconciliation`
- declared_target_paths: ["groundtruth.db"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md`
- operative_file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md`
- candidate_evidence_hash: `sha256:178ed16441227b0ae0d0c016f1e33560ec16c6c459c6aaf4e95ec77ab8acf42f`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Exit code 0.

---

## Clause Applicability

- Bridge id: `gtkb-wi5441-global-registry-membership-reconciliation`
- Operative file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation).

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

**Blocking Gaps:** none. Exit code 0. No owner waiver needed or claimed.

---

## Commands Executed

- `gt bridge state-report --json`; full `-001`..`-019` chain enumeration; `-018` and `-019` read in full
- `gt session envelope show`; `gt session envelope open --harness-name claude --harness-id B --init-keyword "::init gtkb lo" --role loyal-opposition --subject gtkb`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5441-global-registry-membership-reconciliation`
- `git status --short --branch`; `git diff --stat`; `git diff --numstat` on both registry TOMLs; removed-content-line counts per registry file; `git diff -U2` on `platform_tests/scripts/test_implementation_start_gate.py`
- Project-venv `pytest groundtruth-kb/tests/test_artifact_membership_reconciliation.py -q`
- Project-venv `ruff check` and `ruff format --check` on both changed Python paths
- SHA256 hashing of `artifact_membership_reconciliation.py` and `test_artifact_membership_reconciliation.py`
- Direct source reads of `artifact_membership_reconciliation.py` at every line range cited in E7
- `gt registry reconcile --json`; `gt registry reconcile --deep --json`
- `gt deliberations show --json` on `DELIB-202667515`, `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE`, `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`, `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
- `gt deliberations record --help`; `gt deliberations search` on posture and verification terms; deterministic read-only substring survey of deliberation content
- Direct read and independent SHA256 recomputation of `.groundtruth/formal-artifact-approvals/2026-07-28-DELIB-202667515.json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-global-registry-membership-reconciliation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-global-registry-membership-reconciliation`

---

## Prior Deliberations

Searched via `gt deliberations search` on unreadable/unregistered posture,
completeness-gate, and registry-verification terms, plus a deterministic
substring survey over deliberation content, plus `gt deliberations show` on
every id `-019` cites.

- `DELIB-202667515` - **directly load-bearing.** The controlling AUQ-backed
  owner-evidence record for posture A. Read in full, hash-verified against its
  approval packet. This record closes `-018` F1.
- `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` - the deficient first
  capture. Confirmed still at version 1 with `source_ref: null` and not
  superseded on the record; see N1.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - the PAUTH
  `owner_decision_deliberation_id`. Points 5, 6, 8, 9 re-read verbatim; point 9
  is a three-condition operation-time interlock, as noted under Condition 2.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - point 4 keeps
  **membership** changes inside the separately-governed carve-out. Undisturbed:
  `DELIB-202667515` authorizes classification posture only and expressly
  reserves quarantine, deletion, and registry mutation to their own gates.
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL` - retroactive
  approval of the one-row observation repair-forward; unchanged.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - the downstream retention
  direction this thread gates. Stage B remains separately governed.
- `DELIB-202667356`, `DELIB-20265258`, `DELIB-202666060` - protected-commit gate
  lineage cited by `-015`/`-017`; consistent, not re-litigated.

---

## Owner Decisions / Input

**No owner action is required from this verdict.** The thread is terminal.

The one owner decision this thread depended on - the F1 posture choice between
(a) unreadable-and-unobserved paths classify as `unregistered_disposable` and do
not block `membership_complete`, and (b) uninspectability itself blocks
completeness - is now recorded with owner-attributable evidence as
`DELIB-202667515`: question as presented, both options as presented, literal
owner response `A`, AUQ id `AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728`, source
reference `codex-task:019f863a-acd3-7320-80c0-1831f0936cc0:wi5441-unreadable-path-posture`,
and an approval packet recording `presented_to_user: true`,
`transcript_captured: true`, `approved_by: "Mike"`, hash-bound to the record.

Existing owner decisions remain in force and are undisturbed: the registry is
the ultimate load-bearing membership authority; ordinary owner content edits
require no notation; an audit gap is preferable to platform failure;
identity-changing operations remain separately governed; and obsolete WI-5640
sources remain in place.

---

## Scope Notes For Prime Builder

1. This thread reaches **terminal VERIFIED**. No further bridge action is
   required on it.
2. **The downstream WI-5640 Stage B cleanup precondition is now satisfied** -
   this thread is terminal. Stage B still requires its own proposal, GO,
   implementation-start authorization, and the separate owner authorization for
   any deletion per `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`. This
   verdict authorizes none of it.
3. `DELIB-202667515` authorizes **classification posture only**. It does not
   authorize quarantine, expiry, deletion, registry mutation, census rerun,
   traversal-policy expansion, move, rename, retirement, or coverage reduction.
   Every sweep remains subject to its own mechanical authorization and
   operation-time revalidation.
4. `-018` F8-F13 and N1-N2 above are standing-backlog candidates, not
   conditions.

---

## Standing-Backlog Candidates

Not conditions on anything; recorded so they are not lost.

- **`-018` F8 + F9 + F11 together**: all consumers of Git-managed enumeration
  must agree on the enumeration, fail consistently, and preserve
  cache-directory exclusion for scaffolded adopter roots.
- **`-018` F10**: unreadable `unregistered_load_bearing` entries need an
  operator-facing surface (attribution entry or `audit_gaps` row) before that
  state can fire in production.
- **`-018` F12**: decode hardening on the API-reachable `_git_managed_paths`
  path.
- **N4 (new, operational)**: `gt registry reconcile --deep --json` emits a
  **939 MB** document on this workspace, because it serializes the full
  2,257,909-entry classification array alongside the summary. Verification
  sessions need only the summary block. A `--summary-only` projection (or
  omitting `entries` unless requested) would make the deep census routinely
  usable in review; today it is expensive enough that a reviewer is tempted to
  carry the result forward by reference instead - the exact practice `-018` F13
  warned against.
- **N1 (new)**: the Deliberation Archive has no supersession marker. A record
  demoted to audit history stays `outcome=owner_decision` with equal search
  weight. Candidate: a `superseded_by` field or a required version-2
  annotation on demotion.
- **Platform-level, filed separately as an Advisory Proposal in a prior run**:
  the decision-capture skill writes `outcome='owner_decision'` records with no
  AUQ binding while `gt deliberations record` requires one. That divergence is
  what produced the F1 cycle on this thread. This verdict is direct evidence of
  its cost: two full bridge revisions were spent closing a gap the capture
  surface should not have created.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(registry): shared Git-managed enumeration and unreadable-path guard for global registry membership reconciliation (WI-5441)`
- Same-transaction path set:
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-014.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
