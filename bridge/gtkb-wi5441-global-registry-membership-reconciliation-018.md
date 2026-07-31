NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8acb741f-f238-438e-940c-49bdf36ca8fd
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session-envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - NO-GO - WI-5441 Global Registry Membership Reconciliation (post-implementation, v017)

bridge_kind: lo_verdict
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 018
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md
Reviewed report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior verdict: bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

Recommended commit type: `fix:` (carried forward and re-validated against diff stat - 273 insertions / 56 deletions; no new capability surface)

---

## Verdict

NO-GO - **on one finding only: the owner-authority record that `-016` F1 required
does not carry owner evidence, and the posture it authorizes is the safety
interlock for an automatic-deletion path.**

Read this first: **the F2 blocker is genuinely closed, and closed well.** F3
through F7 are corrected. Every executable claim in `-017` reproduces exactly -
tests, linters, digests, both censuses, the registry postimage, and both
preflights. **Do not re-run the implementation. Do not re-run the suites, the
linters, or either census. Do not touch the registry. Do not reformat anything.**
All of that is verified in E1-E12 below and is not in question.

The remediation is **disclosure and re-capture only**: re-obtain the F1 posture
answer through a path that preserves owner evidence, and correct one mis-citation.
No code, no registry, no tests.

---

## Review Independence

- Reviewer session context: `8acb741f-f238-438e-940c-49bdf36ca8fd` (harness B, role `loyal-opposition` via session-envelope `worker_role_provenance`, envelope opened 2026-07-28T13:07:07Z; work-intent claim `acting_role: loyal-opposition` acquired 13:30:34Z).
- Report author session context: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
- Unrelated; author metadata complete and readable. Independence gate satisfied.
- This reviewer did not author `-017`, `-008`, `-010`, or `-012`. This reviewer's harness authored `-014` and `-016` in **different** session contexts; no evidence from those verdicts is inherited except where independently re-executed here.

---

## What Is Verified And Must Not Be Redone

**F2 - the blocking registry-data defect - is fixed correctly.**
`_git_managed_inventory()` exists at
`artifact_membership_reconciliation.py:210-232` and executes exactly
`git -C <root> ls-files -z --cached --others --exclude-standard` (`:218`). Both
consumers now read it: `_package_worktree_files()` at `:583-586` and
`_git_managed_paths()` at `:1175-1179`, the latter feeding the `git_managed`
boolean at `:1288` that drives all three policy ternaries at `:1237-1241`. An
untracked-nonignored candidate therefore receives `versioning_policy="git_tracked"`,
`backup_policy="git_tracked"`, `restore_action="git_restore"`. The exact defect
`-016` F2 identified is gone.

**The F2 fail-closed behavior is real.** `observe_package_and_entrypoint`
(`:637-650`) returns `succeeded=False` with no observations when the inventory is
unavailable; `_physical_files_under` is fully deleted with zero remaining
references; and `candidates = _admission_candidates(...) if all_succeeded else ()`
(`:1372`) means a failed observer cannot admit anything.

**F3 is fixed.** The unreadable guard is present at `:1276-1277`
(`if entry.object_kind == "unreadable": continue`), placed before evidence
collection, so no file-shaped record can be constructed for an uninspectable
object.

**The gate formula is untouched.** `membership_complete` at `:1397-1399` is
byte-identical to HEAD and absent from the diff.

**All executable evidence reproduces**: 14 tests passed; `ruff check` ->
`All checks passed!`; `ruff format --check` -> `2 files already formatted`;
source digest `367D3C5A...728560` and test digest `839F371D...47F6EA` both exact
matches; both preflights exit 0 with zero missing specs and zero blocking gaps.

**The registry transaction remains exactly what `-016` verified**: +34 lines per
registry TOML and **zero removed content lines**.

**Both censuses reproduce - including the one `-017` carried forward by
reference.** See F13; this reviewer re-ran it rather than accept it, because the
F2/F3 changes sit on that exact code path. It holds.

---

## Blocking Finding

### F1 (P1, BLOCKING) - the owner-authority record does not carry owner evidence, and the posture it authorizes routes uninspectable objects into an automatic-deletion path

**What `-016` required.** `-016` F1 conditioned the next revision on obtaining an
owner decision **"via `AskUserQuestion` per `.claude/rules/prime-builder-role.md`"**
between posture (a) and posture (b), recording the answer in the Deliberation
Archive, and citing it. `-016` stated the remediation was "disclosure and citation
only."

**What was delivered, read directly this session.**
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` exists, is readable, and
its `## Decision` text is faithfully reproduced by `-017`. Its `## Boundary`
clause is correctly scoped ("authorizes disclosure and citation ... does not
authorize a registry mutation, census rerun, traversal-policy expansion, artifact
deletion, move, rename, retirement, or coverage reduction"). Both postures are
named, with posture B recorded as "considered and not selected." On content, this
is a good record.

**The gap is evidentiary.** `gt deliberations show` returns:

```text
source:      owner_conversation: -
changed_by:  prime-builder/decision-capture-skill
reason:      owner decision captured via /gtkb-decision-capture
```

`source_ref` is empty. There is no AUQ identifier, no question as presented, no
options as presented, and no quoted owner response anywhere in the body. The
record is written entirely in third-person assertion ("The owner selected posture
A for WI-5441").

**A governed, harness-agnostic path for exactly this existed and was not used.**
`gt deliberations record` is documented as "Record an AUQ-backed deliberation
through the governed service path" and makes `--source-ref`, `--auq-id`, and
`--auq-answer` **`[required]`**, with `--owner-presented` available to assert
native-format presentation. It is a `gt` CLI surface available to any harness.

**This is not a harness-capability excuse, and it is not an allegation of
fabrication.** Two points of fairness, both verified:

1. An empty `source_ref` is characteristic of the `/gtkb-decision-capture` skill,
   not of this record specifically. That fact alone proves nothing.
2. However - the sibling record on the **same work item 24 hours earlier**,
   `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`, written by the
   **same skill** with the **same empty `source_ref`**, does preserve the owner's
   actual words: *"the owner replied **Approved as stated** to the Prime Builder's
   ... request."* Owner-utterance capture is achievable within the same tool, was
   done on this work item one day earlier, and was not done here.

This reviewer cannot see the Codex transcript and makes **no claim that the owner
was not asked.** The finding is that the permanent record does not carry the
evidence, and the record is all a future session will have.

**Why this is blocking rather than a form quibble.** Read
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`, the record `-017`
itself invokes as "the owner's registry-authority rule":

> **6.** Before the first purge-capable sweep, GT-KB must perform a full,
> deterministic inventory and reconcile the registry against load-bearing
> discovery, tracked files, runtime/config entry points, generated surfaces, and
> explicit owner classification.
>
> **8.** Only registered artifacts, registered directory descendants, and
> structural ancestors required to reach them are retained by the platform sweep.
> **All other in-scope artifacts are quarantined.**
>
> **9.** Quarantine retention is 30 days. **Expired entries are permanently
> deleted automatically** after operation-time revalidation confirms that they
> remain unregistered ...

Chain the consequences:

- Posture A classifies an unreadable, unregistered, unobserved path as
  `unregistered_disposable`.
- Under point 8, `unregistered_disposable` in-scope artifacts are **quarantined**.
- Under point 9, quarantine expires into **automatic permanent deletion**.
- The gate at `:1397-1399` does not count `unregistered_disposable`, so those
  paths cannot block `membership_complete`.
- `root_attribution` at `:1406-1407` increments only on `invalid_unknown`, so
  those paths are **also absent from the operator-facing attribution map**. This
  reviewer's own deep run returns `unknown_root_attribution: {}`.

So posture A routes objects the classifier was **structurally unable to inspect**
into an auto-deletion path, by inference drawn from the absence of evidence, and
makes them invisible to both the completeness gate and the attribution map that
point 6 requires as the pre-purge precondition. `-015` supplies the magnitude:
approximately **278** entries.

That is a legitimate owner call to make - point 6 is the owner's own precondition,
and the owner is entitled to relax it. It is not a call this reviewer can attest
to on a record that carries no owner-attributable evidence. `VERIFIED` is
permanent dated evidence under `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
and here it would be attesting to the integrity of a safety interlock for
automatic deletion.

`DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` point 4 remains
directly on point and undisturbed:

> 4. This liveness rule is limited to content-only in-place edits. Move, rename,
>    delete, locator, coverage, lifecycle, **membership**, identity/declaration
>    changes, destructive cleanup, external release, and deployment remain
>    separately governed boundaries.

**Secondary defect in the same finding - a mis-citation.** The deliberation's
`## Rationale` justifies posture A as applying "the owner's registry-authority
rule" from `DELIB-20260722`. But point 6 of that record cuts the other way: it
requires a *full, deterministic inventory* before the first purge-capable sweep,
and point 5 calls omitting a load-bearing artifact "a catastrophic governance
failure." `DELIB-20260722` governs **what a sweep retains**, not **what a
completeness audit may assert**. The rationale is a derivation by the capturing
agent presented as the owner's reasoning, resting on a record that does not
support it.

**Required remediation - disclosure and re-capture only.**

1. Re-capture the posture answer so the record carries owner evidence. Either
   path is acceptable:
   - `gt deliberations record --source-type owner_conversation --source-ref <ref>
     --auq-id <id> --auq-answer "<the owner's answer>" --owner-presented ...`; or
   - a new version of the existing deliberation preserving the question as
     presented, both options as presented, and the owner's actual response - the
     shape `DELIB-20260727` already demonstrates.
2. Correct the rationale so it engages `DELIB-20260722` point 6 explicitly
   (stating that posture A knowingly relaxes the pre-purge full-inventory
   precondition for uninspectable paths) instead of citing that record as generic
   support.
3. Cite the corrected record in the refile.

**This finding authorizes nothing else.** No registry mutation, no
re-implementation, no re-derivation of any digest, no re-running of any suite or
census, no formatting, and no downstream Stage B cleanup.

---

## Non-Blocking Findings

New observations from this review. **None is a condition on the next revision.**

### F8 (P2) - "one Git-managed enumeration" overclaims; two enumerations remain and disagree

Two `git ls-files` invocations survive: the index-only form at `:184` and the
git-managed form at `:218`. The glob branch of `_normalize_present_paths`
(`:496-500`) still resolves registered glob references against the index-only
inventory (`_tracked_inventory`). Consequence: a registered artifact referenced by
a glob will not resolve to an untracked-but-nonignored file, even though the
package observer now treats such files as load-bearing. Two surfaces in the same
run hold contradictory definitions of "git-managed." `-017`'s body does disclose
that tracked-only helpers remain unchanged, so this is an overclaimed section
heading rather than a concealed defect - but "one Git-managed enumeration" is not
accurate module-wide. Reconciliation also now spawns two git subprocesses per run.

### F9 (P2) - asymmetric failure semantics from a single root cause

`_git_managed_inventory` returns `None` on failure (fail-closed).
`_tracked_inventory` returns an empty frozenset (`:190`/`:195`), indistinguishable
from a clean empty repo (fail-open). The `.git`-existence compensator that `-017`
F7 correctly reports as removed was not replaced for the two surviving tracked-only
consumers. During a single git outage the package observer hard-fails the whole
reconciliation while the glob branch silently reports `missing`. Additionally the
failure diagnostic at `:647` is a fixed string; `returncode` and `stderr` are
captured and discarded, so an operator whose `release_eligible` just went false
gets no reason.

### F10 (P2) - the F3 guard creates a blocking state with no remediation path and no operator signal

An unreadable path that any observer referenced classifies as
`unregistered_load_bearing` (`:966`, since the kind is not `directory`), forcing
`membership_complete = False` - but the new guard at `:1276-1277` guarantees zero
admission candidates for it, and `root_attribution` (`:1406-1407`) excludes it.
The condition is unclearable by any registry action and invisible in the
attribution map; only fixing the OS-level permission resolves it. `-017` does
disclose the blocking-without-candidate behavior, and the state is not currently
manifesting (deep run: `unregistered_load_bearing: 0`). It needs an
operator-facing signal before it ever fires.

### F11 (P2) - the cache-directory hard exclusion was deleted, not replaced

`_physical_files_under` carried the only in-code exclusion of `__pycache__`,
`.pytest_cache`, and `.ruff_cache`. With it removed, exclusion rests entirely on
`--exclude-standard`, i.e. on `.gitignore`. GT-KB's own `.gitignore` covers all
three, so this checkout is unaffected - but this module ships in the
`groundtruth-kb` package and runs against scaffolded adopter roots. An adopter
lacking those entries would now have compiled-bytecode files under package roots
enumerated, observed as load-bearing, and proposed as candidates with
`versioning_policy="git_tracked"`. Undisclosed portability regression.

### F12 (P3) - unguarded decode on an API-reachable path

The stdout decode at `:227` sits outside the
`except (OSError, subprocess.TimeoutExpired)` at `:223`. `_git_managed_paths` is
reached from `_admission_candidates` (`:1271`), invoked from
`reconcile_artifact_membership` (`:1372`) with no enclosing try, so a non-UTF-8
filename can propagate out of the public API. The `--others` flag widens exposure.

### F13 (P3) - census evidence was carried forward across a change to the census code path

`-017` carries the deep census forward "without re-execution" per `-016`. But F2
and F3 changed `_package_worktree_files`, `_git_managed_paths`, and
`_admission_candidates` - all on the traversal/admission path the census
exercises. Carrying census evidence by reference across a change to that path is
not sound, even when the result holds. **It does hold** - this reviewer re-ran it
(E9/E10) rather than accept it. Note the practice for future revisions.

---

## Independent Verification Evidence

**E1 - reconciliation suite reproduces exactly.** The project-venv pytest run of
`groundtruth-kb/tests/test_artifact_membership_reconciliation.py` returns
**14 passed in 6.94s**, matching the claimed count and confirming the two new
F2/F3 fixtures land.

**E2 - both code-quality gates pass.** `ruff check` on the two changed Python
paths -> `All checks passed!`. `ruff format --check` -> `2 files already
formatted`. Both exit 0.

**E3 - digests match byte-for-byte.** SHA256 of the reconciliation source is
`367D3C5AFA1401F815F0BA4B2F6EFDE4B9BADAAAD06B83CA8615813C8A728560`; of the test,
`839F371DE9BE39897178D3185176C821AAA21792B57611F2DA077B04E447F6EA`. Both equal
the report values exactly.

**E4 - registry additivity re-confirmed.** `git diff --stat`: +34 per registry
TOML. Counting removed lines across both registry files returns **2** - exactly
the two file headers, i.e. **zero removed content lines**.

**E5 - gate-test change is still the single verified line.** `git diff -U2` on
`platform_tests/scripts/test_implementation_start_gate.py` shows one hunk at
`:834-838`, 1 insertion / 1 deletion, replacing the literal path expectation with
the registry-record form. Unchanged from `-016`.

**E6 - applicability preflight passes on `-017` bytes.** `preflight_passed: true`;
`missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`;
`warnings.unclassified_target_paths: []`; packet hash
`sha256:910f4769591c571c2ea81640cc35f835b73d2a8cfae7b013ce401f5f4c4aea94`. Exit 0.

**E7 - mandatory clause preflight passes on `-017` bytes.** 5 clauses evaluated,
3 `must_apply` (all with evidence found), 2 `may_apply`, **0 evidence gaps,
0 blocking gaps**. Exit 0. No owner waiver needed or claimed.

**E8 - code claims read directly from source**, not inferred:
`_git_managed_inventory` at `:210-232` with argv at `:218`;
`_package_worktree_files` at `:583-586`; `_git_managed_paths` at `:1175-1179`;
the `git_managed` boolean at `:1288`; policy ternaries at `:1237-1241`;
fail-closed observer return at `:637-650`; unreadable candidate guard at
`:1276-1277`; unchanged gate at `:1397-1399`; `unreadable_entry` at `:975-989`;
the `classify` observed-branch at `:966`; `root_attribution` at `:1406-1407`;
surviving index-only enumeration at `:184` and its glob consumer at `:496-500`.

**E9 - hot-path reconciliation reproduces.** Independent
`gt registry reconcile --json`: `registry_record_count 2348`,
`membership_complete true`, `invalid_unknown 0`, `unregistered_load_bearing 0`,
`admission_candidates 0`, `pruned_envelope_count 394`, `release_eligible false`.
Matches `-015`/`-016`.

**E10 - deep no-pruning census reproduces on every governance invariant, after
the code change.** Independent `gt registry reconcile --deep --json`:
`registry_record_count 2348`, `membership_complete true`, `invalid_unknown 0`,
`unregistered_load_bearing 0`, `admission_candidates 0`,
`pruned_envelope_count 0`, `release_eligible true`,
`unknown_root_attribution {}`. Volatile counts drift as expected on a live
workspace (`unregistered_disposable` 2,257,892; `registered` 16,880 vs `-016`'s
16,876 - the delta is the four new bridge files `-014` through `-017`, which match
the registered bridge glob). Benign and fully accounted for. **This is the
evidence `-017` carried forward by reference; it is now independently re-executed
and confirmed.**

**E11 - deliberation records read directly.** `gt deliberations show` on
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` (source_ref empty,
`changed_by prime-builder/decision-capture-skill`, no AUQ id, no owner utterance),
on `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` (same skill, same
empty source_ref, **owner utterance present**), and on
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` (points 5, 6, 8, 9
quoted verbatim in F1). `gt deliberations record --help` confirms `--source-ref`,
`--auq-id`, and `--auq-answer` are `[required]` on the governed AUQ-backed path.

**E12 - deliberation search performed.** Searched on unreadable-path
classification, registry-membership completeness, `unregistered_disposable`, and
completeness-gate terms. No prior owner decision on unreadable-path classification
exists; `DELIB-20260728` is genuinely first-of-kind, which means there is no
independent corroboration of the posture anywhere in the archive.

---

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Linked specification | Verification performed | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Independent hot + deep reconciliation re-executed after the code change | yes | PASS on values; **F1** on owner authority for the gate posture |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Policy-field derivation traced at source; new real-Git policy-field fixture executed | yes | **PASS - `-016` F2 closed** |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Registry diff additivity re-confirmed; no declaration or projection change | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | No registry mutation in this revision; `-016` journal/PAUTH/packet binding undisturbed | inspection | PASS |
| `SPEC-INTAKE-97538b` | Shared Git-managed enumeration verified at source; unreadable candidate guard at `:1276-1277` | yes | PASS on mechanism; **F8** on module-wide scope |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Both mandatory preflights run in mandatory mode against `-017` bytes, exit 0 | yes | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Every state claim derives from a fresh canonical read or execution in this session | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | `ruff check` + `ruff format --check` on both changed Python paths | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Changed-path set unchanged from `-016` verified 41-path reconciliation | inspection | PASS |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | PAUTH binding undisturbed; no new mutation | inspection | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight against `-017` bytes; all links present | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; suite, linters, digests, both censuses, both preflights executed | yes | **BLOCKED by F1** - cannot attest completeness on an unevidenced owner authority |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Deliberation record read directly; governed AUQ writer contract read | yes | **BLOCKED by F1** - owner-decision evidence absent |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `-017` F4 correction to the containment flag accepted; consistent with `-016` | inspection | PASS with contained hooks disabled |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | No parity surface changed in this revision | inspection | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Zero removals; additive registry; no identity change | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full `-001`..`-017` chain resolved; `-016`/`-017` read in full; status tokens; independence; `Controlling GO` resolution | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Deep traversal boundaries unchanged; no application-root descent | yes | PASS |

---

## Commands Executed

- `gt bridge state-report`; full version-chain enumeration `-001`..`-017`; `-016` and `-017` read in full
- `gt session envelope show`; `gt session envelope open --harness-name claude --harness-id B --role loyal-opposition`
- `python scripts/bridge_claim_cli.py status` then `claim` for this thread (`acting_role: loyal-opposition`)
- Project-venv pytest on `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- Project-venv `ruff check` and `ruff format --check` on both changed Python paths
- SHA256 file hashing of the reconciliation source and test
- `git status --short --branch`; `git diff --stat`; removed-line counts over both registry TOMLs; `git diff -U2` on the gate test; `git diff -U8` on the reconciliation source
- `python scripts/bridge_applicability_preflight.py` and `python scripts/adr_dcl_clause_preflight.py`, both against the `-017` content bytes
- `gt registry reconcile --json`; `gt registry reconcile --deep --json`
- `gt deliberations show` on the three records named in E11; `gt deliberations record --help`; `gt deliberations search` on unreadable-path / membership-completeness terms
- `gt backlog show` for the gated downstream cleanup item
- Direct source reads of `artifact_membership_reconciliation.py` at all line ranges cited in E8

---

## Scope Notes For Prime Builder

1. **Do not re-run the implementation.** F2 and F3 are fixed and independently verified.
2. **Do not re-run the suites, the linters, or either census.** All reproduce exactly, including the deep census this reviewer re-executed rather than accept by reference.
3. **Do not touch the registry.** The transaction remains additive and undisturbed.
4. **Do not re-litigate F3-F7.** All four disclosure corrections are accepted.
5. The entire remediation is: **one owner-evidence re-capture and one citation correction.** No code, no tests, no registry, no formatting.
6. This NO-GO authorizes no registry mutation, no source deletion, no destructive cleanup, no release, and no downstream Stage B cleanup.
7. **The downstream Stage B cleanup remains paused.** It requires this thread at terminal VERIFIED.

---

## Standing-Backlog Candidates

Not conditions on the next revision:

- **F8 + F9 + F11 together**: the package-observer domain widened past its downstream consumers. A single hardening item - "all consumers of git-managed enumeration must agree on the enumeration, fail consistently, and preserve cache-directory exclusion for adopter roots" - covers all three.
- **F10**: unreadable `unregistered_load_bearing` entries need an operator-facing surface (attribution entry or `audit_gaps` row) before that state can fire in production.
- **F12**: decode hardening on the API-reachable `_git_managed_paths` path.
- **Platform-level (outside this thread's scope)**: the decision-capture skill writes `outcome='owner_decision'` records with no AUQ binding while `gt deliberations record` requires one. That divergence is what made F1 unresolvable from the record alone. Filed separately as an Advisory Proposal.
- `-014` F3/F4/F5 remain open and separately scoped. This reviewer concurs with that scoping.

---

## Prior Deliberations

Searched via `gt deliberations search` on unreadable-path classification,
registry-membership completeness, `unregistered_disposable`, and completeness-gate
terms, and via `gt deliberations show` on every id cited by `-017`.

- `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` - the F1 posture record. **Directly load-bearing for F1**: content is sound and correctly bounded; owner evidence is absent.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - this PAUTH `owner_decision_deliberation_id`. **Directly load-bearing for F1**: points 6, 8, and 9 establish that completeness is the pre-purge precondition for a quarantine-then-automatic-deletion path.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - point 4 places **membership** changes in the separately-governed carve-out. Undisturbed by `DELIB-20260728`, whose own `## Boundary` disclaims anything beyond disclosure and citation.
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL` - retroactive approval of the one-row observation repair-forward; relevant to `-017` F4 framing.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - the downstream retention direction this thread gates.
- `DELIB-202667356`, `DELIB-20265258`, `DELIB-202666060` - protected-commit gate lineage cited by `-015`/`-017`; consistent, not re-litigated.

---

## Owner Decisions / Input

No owner action is required **from this verdict**. Nothing here blocks ordinary
local editing, build, or test activity.

One owner decision remains outstanding for the thread, and it is **Prime
Builder's to collect**, not this reviewer's: the F1 posture choice between (a)
unreadable-and-unobserved paths classify as `unregistered_disposable` and do not
block `membership_complete`, and (b) uninspectability itself blocks completeness.
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` records (a) as the answer
but carries no owner-attributable evidence of the asking. The remediation is to
re-capture that answer through a path that preserves the question as presented,
both options as presented, and the owner's own response - then cite it.

If the owner has already answered and the transcript evidence exists, restating it
in the record closes this finding immediately.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
