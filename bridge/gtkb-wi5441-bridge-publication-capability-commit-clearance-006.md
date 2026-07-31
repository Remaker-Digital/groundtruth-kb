NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 432112aa-4ae8-4476-8213-15594ad38640
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance; independent of the -005 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex harness A)
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - NO-GO - WI-5441 Terminal-VERIFIED Freshness Fixed Point

bridge_kind: lo_verdict
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 006
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md

---

## Verdict

**NO-GO.** One new P0 blocking finding.

The revision's diagnosis of `operative_version` is correct, and its correction is
necessary. It is not sufficient. `operative_version` is **not** the only
tree-dependent input to the hashed packet. MemBase enrichment
(`applicable_specs`) is a second, independent divergence source, and it diverges
for a structural reason the revision's declared scope cannot reach:
`groundtruth.db` is git-ignored and therefore cannot exist in the
index-materialized commit-time snapshot.

Implementing `-005` exactly as written would leave the terminal-`VERIFIED`
deadlock in place. This verdict is issued now, pre-implementation, specifically
to prevent a seventh failed finalization cycle.

The F-LO-1 per-path routing correction is sound and may be carried forward
unchanged.

## Review Independence

- `-005` author session context: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
- This reviewer session context: `432112aa-4ae8-4476-8213-15594ad38640` (Claude, harness B).

Distinct. Author metadata is present and readable. Independence satisfied; no
fail-closed condition.

## F-LO-5 (P0, BLOCKING) - the packet hash has a second tree-dependent input that `-005` does not address, so the proposed fixed point is not reached

### Claim

`-005` Acceptance Criterion 1 states the `c6157`/`2647` divergence becomes
"impossible for an explicit canonical source file". That is falsified. Deriving
`operative_version` from the explicit content file removes one divergence
source. A second remains: `applicable_specs`, whose contents depend on whether
`groundtruth.db` is present in the tree the gate runs against.

### Evidence - executed

`build_packet` was invoked twice against the identical `bridge_dir`, identical
`config_path`, and the identical explicit `content_file`
(`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`),
varying **only** `db_path`. `operative_version` was therefore constant across
both runs by construction, isolating the second variable:

```
db present hash : sha256:49a9f727276db17a4e10ff7566b5182e329f521582f13a92a9c9733e99bc05f7
db absent  hash : sha256:4a094282b04d3b4a64066dfa804fb6991daeb596baa6fab0cda15d77fd563ab2
HASHES EQUAL    : False
differing packet fields: ['applicable_specs']
```

The per-spec delta, e.g. for `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`:

```
with db: {..., 'title': 'Implementation proposals must be linked to all relevant
          specifications', 'status': 'specified', 'type': 'design_constraint',
          'exists_in_membase': True}
no   db: {..., 'title': None, 'status': None, 'type': None,
          'exists_in_membase': None}
```

### Root cause - code level

1. `scripts/bridge_applicability_preflight.py:633` calls
   `enrich_from_membase(applicable, db_path)`.
2. `enrich_from_membase:449-451` fails soft and silently: an absent db is not an
   error; it simply leaves `title`, `status`, `type`, and `exists_in_membase`
   unset.
3. `build_packet:663` embeds the enriched objects into the hashed packet as
   `applicable_specs`, and `:669-670` hashes the whole dict.

### Why the two gates see different db state

`.claude/hooks/bridge-compliance-gate.py:1557-1563` derives **all four** packet
inputs -- `bridge_dir`, `config_path`, `db_path`, and the `project_root` used for
warnings -- from one resolved root, where
`project_root = _canonical_project_root(cwd_path)` (`:1506`) resolves via the
nearest `groundtruth.toml` marker (`:595-597`).

- **Write time.** `cwd` is the real worktree. The marker resolves to the project
  root. `groundtruth.db` exists there. Specs enrich.
- **Commit time.** `scripts/check_protected_commit_authorization.py:1127-1130`
  and `:1149` run the gate as a subprocess with
  `payload["cwd"] = str(snapshot_root.resolve())` and `cwd=snapshot_root`. The
  snapshot is built by `_materialize_index_tree` (`:859`) from `_index_entries`
  -- **git index entries only**. `groundtruth.toml` is tracked, so the marker
  resolves to `snapshot_root`; `groundtruth.db` is git-ignored
  (`.gitignore:180`) and is therefore **absent** from the snapshot. Specs do not
  enrich.

Verified directly: `git ls-files --error-unmatch groundtruth.db` reports the path
is not known to git; `git check-ignore -v groundtruth.db` reports
`.gitignore:180`; `git ls-files --error-unmatch groundtruth.toml` confirms the
marker file is tracked.

### Deficiency rationale

`-005` treats `operative_version` as *the* mixed-authority field. The actual
invariant violation is broader: the hashed packet mixes **content-derived**
facts (stable for a fixed source artifact) with **environment-derived** facts
(not stable). Any environment-derived field makes the hash a function of the
tree, and the two gates run against deliberately different trees. Fixing one such
field leaves the class intact.

This is not specific to WI-5441. It is unconditional for every terminal
`VERIFIED` whose linked specs exist in MemBase -- i.e. effectively all of them,
since `GOV-FILE-BRIDGE-AUTHORITY-001` is always applicable to `bridge/**`.

### Recommended remediation

Either reaches a genuine fixed point; the first is smaller and is recommended:

1. **Exclude environment-derived descriptive fields from the hashed subset.**
   Hash a content-derived projection of the packet; keep the full enriched packet
   for human-readable reporting. Concretely, drop `title`, `status`, `type`, and
   `exists_in_membase` from the hashed form. This is safe: `enrich_from_membase`
   mutates only those four attributes (`:464-466`), and no gate decision depends
   on them. Severity -- and therefore `missing_required_specs` -- is derived from
   the rules file via `compute_applicable_specs(..., rules=load_rules(config_path))`,
   not from MemBase, so blocking-spec enforcement is unaffected.
2. **Option A from `-004`** (writer computes and injects the hash; commit-time
   validates against the same tree). This eliminates the entire tree-dependence
   class rather than field-by-field, and additionally removes the
   hash-transcription error class.

If remediation 1 is chosen, the successor revision must also confirm that
`warnings.missing_parent_dirs` -- computed against `project_root` (`:657`) and
therefore also environment-derived -- cannot diverge for the paths in scope, or
must be excluded on the same basis. It did not diverge in the experiment above
only because both runs shared a `project_root`.

## F-LO-6 (P1) - the proposed two-phase regression can pass while the real path still fails

`-005` Verification Plan, "Two-phase compliance audit", step 3 says
"materialize the candidate in the prospective tree". If that step is implemented
as an ordinary temporary directory that receives the candidate file, the fixture
will still contain (or still point at) a readable `groundtruth.db`, both phases
will enrich identically, and the test will pass **while the production path
continues to fail**. That is a false green on the exact regression this thread
exists to prevent.

The regression must reproduce the real commit-time conditions: an
index-materialized tree containing tracked files only, with **no**
`groundtruth.db` present, and with the gate resolving its own `project_root`
from that tree. Asserting hash equality between "worktree root" and "index-only
snapshot root" is the assertion that actually binds.

`-005` Loyal Opposition Ask 5 already requests "a real two-phase compliance
regression and live terminal finalization, not only a build_packet unit test".
This finding sharpens what "real" must mean.

## F-LO-1 disposition (carried forward, design accepted with two narrowings)

Independent trace of the current working-tree source confirms the routing defect
and refines it:

- The **clearance** selection is already exact per-path:
  `_bridge_publication_capability_clearance`
  (`scripts/check_protected_commit_authorization.py:1964`) queries
  `WHERE aggregate_entry_id = ? AND target_path = ? ORDER BY rowid DESC LIMIT 1`
  (`:1973-1977`), already fails closed on invalid states without falling back to
  an older success (`:2004-2015`), and has passing coverage at
  `test_..._uses_newest_bridge_publication_attempt_before_filtering` (`:2929`).
- The defect is the **routing gate** at `:2096`,
  `if revision["operation"] == "bridge_publication":`, where `revision` is the
  newest revision for the whole aggregate (`:2089-2092`).

`-005`'s correction (resolve the exact row *before* choosing the evidence family)
is the right shape and is accepted. Two narrowings for implementation:

1. **Suppression is broader than compensation.** Any newest-aggregate operation
   that is not literally `bridge_publication` suppresses the route -- including
   `wi5441_bridge_aggregate_recovery` (`registry_control_plane.py:2801-2816`),
   `amend`, and `register`, none of which carry a usable `capability_hash` or
   `journal_id`. `-005` describes only the compensation case. The fix as designed
   covers all of them; the **test plan must too**, or the regression under-covers
   the defect class.
2. **"Normalized target_path" must assert, not coerce.** The current query uses
   exact string equality on `rel_path` (`:1976`) with a redundant re-check at
   `:1990`; any divergence today fails closed. Introducing a normalization step
   must preserve that and must not widen matching.

No test currently seeds a non-`bridge_publication` aggregate head, so the routing
branch has no negative-path coverage today.

## F-LO-7 (P2) - the preflight CLI's default invocation yields a packet the gate never accepts

Encountered and reproduced while filing this verdict, and it corroborates F-LO-5
from a third direction: the packet is **invocation**-dependent as well as
tree-dependent.

For the same source artifact `-005`:

```
python scripts/bridge_applicability_preflight.py --bridge-id <slug>
  -> content_source: bridge_file_operative
  -> packet_hash:    sha256:76af1a2c8de178e0d0b340246b2c51bead08d42a9ef276c6600da7f3259886ed

python scripts/bridge_applicability_preflight.py --bridge-id <slug> \
       --content-file bridge/<slug>-005.md
  -> content_source: pending_content
  -> packet_hash:    sha256:ee4d5bbde468378f3dcd494448a42f3bf4e2ec15d04c8166c1a8587baa1427b7
```

The gate always calls `build_packet(..., content_file=responds_path)`
(`.claude/hooks/bridge-compliance-gate.py:1557-1563`), so only the second form
can ever satisfy it. A reviewer who follows the documented command in
`.claude/rules/file-bridge-protocol.md` § "Mandatory Applicability Preflight
Gate" — which specifies `--bridge-id` with no `--content-file` — obtains a hash
that is guaranteed to be rejected. This reviewer hit exactly that on the first
publish attempt.

`content_source.mode` is embedded in the hashed packet (`build_packet:642`), so
the divergence is caused by the same mixed-authority defect F-LO-5 describes:
metadata about *how the packet was produced* is hashed alongside the artifact
content it is supposed to bind.

Remediation 1 in F-LO-5 should therefore also exclude `content_source.mode` from
the hashed projection, or the documented preflight command must be corrected to
require `--content-file`. Either resolves it; doing neither leaves a documented
command that cannot produce an acceptable verdict.

## F-LO-4 disposition (P3, accepted as deferred)

`-005` defers the status-to-activity mapping documentation to WI-5640's
controlled reference migration, on the grounds that editing one legacy rule copy
would create another source-of-truth conflict. Accepted as correct sequencing.

## Positive findings

1. **The `operative_version` diagnosis is correct and the correction is
   necessary.** `build_packet:597-598` does resolve the operative version by
   directory scan before honouring `content_file`, and `:643-651` does embed it
   in the hashed packet. Deriving it from the explicit canonical source is the
   right fix for that field, and preserving directory-scan behaviour for
   out-of-`bridge_dir` draft content correctly protects existing proposal-draft
   semantics.
2. **Keeping `operative_version` in the packet rather than deleting it** is
   better than `-004`'s literal Option B, which proposed excluding it. Retaining
   the field with corrected authority preserves audit information.
3. **Fail-closed compensation behaviour is preserved** and correctly excluded
   from scope.
4. **Structural compliance is clean.** Both mandatory preflights pass on the
   `-005` operative file (sections below). Project-linkage metadata,
   `target_paths`, `Requirement Sufficiency`, `Owner Decisions / Input`,
   `Specification Links`, and `Prior Deliberations` are all present and
   substantive.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-PLATFORM-SOT-REGISTRY-001
- DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001
- DCL-SOT-REGISTRY-RECORD-SCHEMA-001
- DCL-SOT-REGISTRY-PROJECTION-PARITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Spec-to-Test Mapping

| Specification | Required evidence | Status at this verdict |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Same exact report packet before/after candidate materialization; real terminal finalization succeeds | **Not satisfiable as designed** -- F-LO-5 shows a second divergence source outside declared scope |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Packet, gate, routing, negative suites execute | Plan present; F-LO-6 requires an index-realistic two-phase fixture |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | All target surfaces map to named specs and tests | Satisfied in `-005` |
| GOV-PLATFORM-SOT-REGISTRY-001 | Exact registered bridge path resolves only through its own typed publication evidence | Design accepted (F-LO-1) |
| DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 | Same-path compensation fails; sibling aggregate compensation cannot hide valid evidence | Design accepted; test plan must extend beyond compensation |
| DCL-SOT-REGISTRY-RECORD-SCHEMA-001 | Exact capability and linked revision identities remain bound | Preserved by design |
| DCL-SOT-REGISTRY-PROJECTION-PARITY-001 | No schema/projection change | Satisfied -- revision declares none |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Packet covers exactly the declared targets | Satisfied; remediation 1 stays within the five declared paths |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Append-only chain and independent review | Satisfied by this `-006` |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Durable regressions accompany both corrections | Pending revision |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Findings converted to reviewed correction before source mutation | Satisfied by this NO-GO |

## Applicability Preflight

- packet_hash: `sha256:ee4d5bbde468378f3dcd494448a42f3bf4e2ec15d04c8166c1a8587baa1427b7`
- bridge_document_name: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md`
- operative_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:04e8dbcffb3840270b425da6f244057b94e9473f121becc6ea18cf70b6de5f26`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Warnings on the operative file: `missing_parent_dirs` empty; `spec_links_section`
harvested; `author_metadata_warnings` empty; `unclassified_target_paths` empty.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- Operative file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | -- | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

Blocking gaps: none. Exit 0. No owner waiver required.

## Prime Builder Implementation Context

**Objective.** Reach a packet-hash fixed point that survives both the worktree
root and the index-materialized snapshot root, then land the F-LO-1 routing
correction.

**Preconditions.** No new owner decision. Existing PAUTH and project
authorization remain sufficient. Dispatcher stays disabled.

**Evidence paths.**

- `scripts/bridge_applicability_preflight.py:597-598` (scan-before-content),
  `:633` (`enrich_from_membase`), `:640-670` (hashed packet assembly),
  `:449-468` (silent fail-soft on absent db), `:657` (`missing_parent_dirs`).
- `.claude/hooks/bridge-compliance-gate.py:1493-1586` (freshness check), `:1506`
  plus `:575-605` (root resolution), `:1557-1563` (four inputs from one root),
  `:196` (freshness applies to GO/NO-GO/VERIFIED).
- `scripts/check_protected_commit_authorization.py:1127-1158` (subprocess audit
  at `snapshot_root`), `:859-875` and `:688-706` (index-only materialization),
  `:2089-2096` (aggregate routing gate), `:1964-2029` (exact per-path clearance).
- `.gitignore:180` (`groundtruth.db` ignored).

**Implementation sequence.**

1. Keep the `-005` explicit-content `operative_version` resolver as designed.
2. Add the content-derived hashed projection (remediation 1), or adopt `-004`
   Option A. Either way, state in the revision which fields are
   environment-derived and why each is safe to exclude from the hash.
3. Audit the remaining packet fields for environment dependence and dispose of
   each explicitly -- at minimum `warnings.missing_parent_dirs` and
   `blocking_errors` (`_pauth_amendment_blocking_errors(content, project_root, db_path)`,
   `:639`), which also take `project_root` and `db_path`.
4. Land the F-LO-1 exact-row-first routing fix with the broadened negative
   coverage described above.

**Verification steps.**

- Hash-equality assertion across a worktree root and a genuine index-only
  snapshot root lacking `groundtruth.db` (not two ordinary temp directories).
- Retain the pending-draft directory-scan tests unchanged.
- Negative coverage for non-`bridge_publication` aggregate heads.
- Live acceptance: a real governed terminal finalization with no bypass and no
  force-add.

**Rollback.** Ordinary Git rollback of the declared files before terminal
verification. No schema, registry, or MemBase reversal required.

**Open decisions.** None for the owner. The choice between remediation 1 and
`-004` Option A is delegated to Prime Builder, consistent with `-004`.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
  through `-005.md`: proposal, GO, implementation report, controlling NO-GO, and
  the revision under review.
- `DELIB-202667287` -- "WI-5554: Bind LO verdict preflight evidence to its source
  and final candidate". Establishes the source-and-candidate binding the
  freshness check implements. F-LO-5 is a defect in how that binding computes its
  anchor, not a challenge to the binding requirement itself.
- `DELIB-202667452` -- "Loyal Opposition Verdict - WI-5659 Finalization Hold".
  Prior finalization-hold precedent on this program.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` -- an earlier session recorded
  that an untracked `groundtruth.db` cannot enter the index snapshot. F-LO-5
  confirms that observation by execution and identifies the exact packet field it
  corrupts.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` through `-009.md`: typed
  publication-table diagnosis and publication-path friction.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`: owner liveness
  direction; operational context only, not a finalization waiver.

## Commands Executed

```
gt bridge state-report
gt bridge status
git status --porcelain bridge/
git ls-files --error-unmatch groundtruth.db          # not tracked
git check-ignore -v groundtruth.db                   # .gitignore:180
git ls-files --error-unmatch groundtruth.toml        # tracked
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance --content-file bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md
python scripts/adr_dcl_clause_preflight.py  --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance   # exit 0
python  -> build_packet(db_path=<real>) vs build_packet(db_path=<absent>)     # divergence reproduced
python scripts/bridge_claim_cli.py claim gtkb-wi5441-bridge-publication-capability-commit-clearance
db.search_deliberations("packet hash freshness verdict finalization")
db.search_deliberations("bridge publication capability commit clearance")
db.search_deliberations("terminal VERIFIED finalization deadlock")
```

An independent ground-truth bridge scan (file-chain derived, not TAFE-derived)
was also run across all 2269 threads to confirm the LO-actionable set before
review.

## Owner Decisions / Input

No owner decision is required by this verdict, and none was solicited.

`-005` correctly states that no new owner policy, waiver, specification,
approval packet, or schema change is needed. This verdict does not change that.
The remediation choice remains delegated to Prime Builder under the existing
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
authorization.

No waiver, destructive action, dispatcher activation, commit, push, release,
deployment, registry identity change, or MemBase mutation is requested or
performed by this verdict.

## Standing-Backlog Candidates Surfaced By This Review

1. **Packet hashing has no stated content/environment boundary.** The F-LO-5
   defect class recurs because nothing declares which packet fields may be
   environment-derived. A design constraint plus a test that fails when a new
   environment-derived field enters the hashed form would close the class rather
   than the instance.
2. **`enrich_from_membase` fails soft and silently on absent db.** A missing
   canonical database is indistinguishable from a spec genuinely absent from
   MemBase. Distinguishing "not enriched" from "not present" would have made this
   defect self-announcing.
3. **LO file-safety hook false-positives on read-only shell reads.** A `grep`
   whose *search pattern* contained a mutation-shaped literal was blocked as an
   "opaque shell mutation target". Pattern text is not a mutation target; the gate
   should classify by the invoked verb.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
