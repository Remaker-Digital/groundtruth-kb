GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 00612085-c010-4be3-8e81-ee9fac3256e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance; independent of the -007 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex harness A)
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - GO - WI-5441 Reproducible Verdict Freshness

bridge_kind: lo_verdict
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 008
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md

---

## Verdict

**GO.** All four live findings from `-006` are addressed, and the central P0
remedy was **independently reproduced by execution** in this session rather than
accepted on description.

The decisive question was not whether the projection is plausible but whether it
actually reaches a fixed point across the two trees the gate really runs in. It
does. Three non-blocking observations (O-LO-8, O-LO-9, O-LO-10) and four
implementation cautions are recorded below; none block implementation and none
require an owner decision.

## Review Independence

- `-007` author session context: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
- This reviewer session context: `00612085-c010-4be3-8e81-ee9fac3256e8` (Claude, harness B).

Distinct. Author metadata is present and readable. Independence satisfied; no
fail-closed condition. This reviewer did not author or implement any artifact in
this thread.

## F-LO-5 (P0) - RESOLVED, reproduced by execution

### Claim under review

`-007` asserts that computing `packet_hash` from a versioned projection
containing only source identity, normalized source bytes, and
content-plus-tracked-rule-derived facts yields one hash across the live worktree
and the index-only commit snapshot.

### Evidence - executed

The defect was first reproduced against the current tree to confirm `-006`'s
diagnosis still holds with `-007` as source. `build_packet` was invoked twice
with identical `bridge_id`, `bridge_dir`, `config_path`, and explicit
`content_file`, varying **only** `db_path`:

```
db-present hash : sha256:d38e8c98c9037083a33e38eb7700e153bd7732d0f7d202f99b0d1a46db6615e7
db-absent  hash : sha256:ca6b04e38f21ab4d10301e893179f8f67ce1c1048aecfff9eb6f1626d32928bd
EQUAL           : False
differing keys  : ['applicable_specs', 'packet_hash']
```

The divergence is confined to `applicable_specs`, exactly as `-006` found.

The **proposed** schema-v2 projection was then constructed from those same two
packets and compared:

```
PROJECTION db-present == db-absent : True
PROJECTION explicit   == default   : True
projected hash                     : sha256:1077badeb172f13d7a5fc3d8ee9cced870b0bf92e2cb9b2a3653779100ca99e2
source-byte mutation changes hash  : True
```

The projection collapses both divergence axes simultaneously while remaining
sensitive to source mutation. This is the fixed point the thread has been
pursuing since `-004`.

### Exclusion-list completeness

The live packet hashes 14 top-level keys:

```
applicability_path_evidence, applicable_specs, blocking_errors,
bridge_document_name, cited_specs, content_source, declared_target_paths,
missing_advisory_specs, missing_required_specs, operative_version,
preflight_passed, target_paths, warnings, work_items
```

`-007`'s include and exclude sets partition this key set exactly, with
`operative_version` subsumed by the new `source_identity`. No packet field is
left unclassified.

Two supporting facts were confirmed at code level:

- `compute_applicable_specs` performs **zero filesystem I/O**. Path rules
  string-match via `fnmatch.fnmatchcase` against content-harvested tokens; a
  path that does not exist still matches, and an existing path never matches
  unless the source text names it. `severity` and `rationale` come from the
  rules TOML, never from MemBase.
- `enrich_from_membase` writes **only** `title`, `status`, `type`, and
  `exists_in_membase`, and returns early when the database is absent. It never
  touches `severity`, `rationale`, `matched_by`, or the key set - so
  `missing_required_specs` is genuinely db-independent, and excluding the four
  enrichment fields cannot weaken blocking-spec enforcement.

### The scope question this review had to settle

`-007` places `.claude/hooks/bridge-compliance-gate.py` in Excluded Scope. That
is safe only if the commit-time audit rejects **solely** on hash mismatch. If it
independently re-evaluated `preflight_passed` or `blocking_errors` - both
computed in a snapshot that structurally cannot contain `groundtruth.db`, making
PAUTH lookups there unreliable - a hash-only remedy would leave the deadlock
intact through a third route and the gate would have to be in scope.

Verified directly: `_verdict_preflight_freshness_deny_reason`
(`.claude/hooks/bridge-compliance-gate.py:1493-1586`) rebuilds the packet at
`:1557-1563` and compares **only** `packet_hash` at `:1566-1571`. It never reads
`preflight_passed` or `blocking_errors` from the rebuilt packet.

A second scope question: three gate copies exist
(`.claude/hooks/bridge-compliance-gate.py`,
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`,
`config/hooks/gtkb-bridge-compliance-gate.py`). All three **import**
`build_packet` from the single `scripts/bridge_applicability_preflight.py` at
line 1555; none vendors its own digest logic. Changing the one declared script
therefore propagates consistently to every harness surface, with no
cross-harness parity gap.

Excluding those fields from the digest is sufficient, and leaving the gate out
of scope is correct.

**Disposition:** accepted. The remedy is sound, minimal, and correctly scoped.

## F-LO-6 (P1) - RESOLVED

`-007` replaces the ambiguous "materialize the candidate in the prospective
tree" step with a fixture that creates a real temporary Git repository, stages
the tracked inputs, leaves `groundtruth.db` outside the copied index, invokes
the real prospective-index audit, and **asserts from inside the materialized
tree** that `groundtruth.db` is absent and that root discovery resolves to that
tree.

Those two assertions are the ones that actually bind; without them the fixture
passes while production fails. `-007` names both explicitly. Accepted.

## F-LO-7 (P2) - RESOLVED, reproduced by execution

Reproduced with `-007` as source:

```
explicit --content-file : sha256:d38e8c98c9037083a33e38eb7700e153bd7732d0f7d202f99b0d1a46db6615e7
default  --bridge-id    : sha256:f55bc68744b419c0074a2953e436676a173d2e09f0bdb3ead97790463092db8b
differing keys          : ['content_source', 'packet_hash']
```

The divergence is confined to `content_source`, which the schema-v2 projection
excludes; the projection comparison above confirms parity is restored. This
reviewer had to embed the **explicit-mode** hash in this very verdict, because
the gate always calls `build_packet(content_file=responds_path)` - a live
demonstration of the defect being fixed. Accepted.

## F-LO-1 (P2) - RESOLVED

`-007` adopts both `-006` narrowings in substance: the four
non-`bridge_publication` aggregate heads (`bridge_publication_compensation`,
`wi5441_bridge_aggregate_recovery`, `amend`, `register`) are all named in the
test plan, and the revision states plainly that no "coercion, case folding,
separator rewriting, prefix matching, or other path widening is introduced". The
routing design - resolve the exact row before selecting an evidence family - is
unchanged from the shape accepted at `-006`. Accepted.

## F-LO-4 (P3) - deferred, unchanged

Sequencing under WI-5640's controlled reference migration remains correct.
Accepted.

## O-LO-8 (P2, non-blocking) - the v1 to v2 hash-contract change has no stated migration disposition

### Observation

`-007` introduces `packet_hash_schema_version: 2` but does not state what
happens to verdicts already authored under the v1 whole-packet digest. Seven
uncommitted verdict files currently carry embedded v1 `packet_hash` values:

```
bridge/gtkb-wi5424-auto-finalization-import-repair-v2-002.md             GO
bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md             VERIFIED
bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md GO
bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md NO-GO
bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md NO-GO
bridge/gtkb-wi5441-global-registry-membership-reconciliation-004.md      NO-GO
bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md      NO-GO
```

None records a schema version, so a v2 validator cannot detect that they are v1.

### Why this is not blocking

The commit-time snapshot audit runs on the **terminal VERIFIED candidate only**
(`scripts/check_protected_commit_authorization.py:1802-1822` gates
`_run_snapshot_compliance_audit` behind `latest.status == "VERIFIED"`). GO and
NO-GO verdicts are subject only to the write-time gate, which has already run.
Staging the older chain files alongside a finalization commit does not re-audit
them. This thread's own finalization computes a fresh v2 hash end-to-end and is
unaffected.

### The residual

Exactly one artifact is materially affected:
`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md`, an untracked
terminal `VERIFIED`. It is **already** stranded under v1 (its worktree-computed
hash cannot match a snapshot recomputation), and v2 does not rescue it - the
recomputed v2 hash will differ from the embedded v1 hash for a second,
independent reason. The correct disposition is re-issue of a fresh verdict on
that thread, not a migration shim.

### Recommended action

State this explicitly in the implementation report so the acceptance criteria
are not read as clearing the pre-existing stranded backlog, and so the
auto-finalization sweep's continued failure on that thread is understood as
expected rather than as a regression introduced by this change. No scope change
is requested.

## O-LO-9 (P2, non-blocking) - the projection asserts a rules-file dependency the hash does not witness

### Observation

The projection includes `severity`, `rationale`, and `matched_by`, all derived
from `config/governance/spec-applicability.toml`. `-007`'s field table justifies
their inclusion as "tracked-rule-derived". Two gaps sit behind that phrase:

1. **Tracked does not mean identical across the two trees.** Tracked guarantees
   the file is *present* in the index snapshot; it does not guarantee the
   snapshot bytes equal the worktree bytes. An unstaged edit to the rules file
   reintroduces a write-time/commit-time divergence **inside the included
   projection**.
2. **The rules file identity is never recorded.** `config_path` is a CLI
   override (`--config`) consumed by `load_rules`, and nothing about the rules
   file lands in the hashed packet. The projection's stated basis - source bytes
   plus the tracked rules file - is therefore not actually *witnessed* by the
   digest. A rules edit that changes applicability silently invalidates old
   hashes without ever saying why.

### Why this is not blocking

Categorically weaker than the `groundtruth.db` case. That divergence is
structural and unconditional - the file can never be in the snapshot, so every
terminal VERIFIED is affected. A dirty or substituted rules file is transient
and self-inflicted, and failing closed there is arguably correct: the
applicability genuinely differs between the two trees.

### Recommended action

Add a `rules_content_hash` (SHA-256 of the LF-normalized rules TOML) to the
projection. This small addition converts an unstated assumption into a witnessed
fact: it makes the digest's declared basis verifiable, makes rule edits visibly
invalidate stale hashes, and turns a staged-versus-worktree rules divergence
into a self-explaining failure rather than another opaque hash mismatch. It fits
inside the already-declared `scripts/bridge_applicability_preflight.py` and
`platform_tests/scripts/test_bridge_applicability_preflight.py` targets and
requires no scope change. If Prime Builder declines it, state the clean-rules
assumption explicitly in the field table instead.

## O-LO-10 (P3, non-blocking) - default/explicit parity holds only before the verdict file exists

Once `bridge/<slug>-NNN.md` is written, a bare `--bridge-id` run resolves the
operative file to the **new verdict**, not to the source it responds to, and
again reports a different hash. Production is unaffected because the gate always
passes `content_file=responds_path` explicitly. The residual is a documentation
hazard: a reviewer who re-runs the command in
`.claude/rules/file-bridge-protocol.md` section "Mandatory Applicability
Preflight Gate" *after* filing sees a mismatch and may mistake it for a defect.
A one-line note that the preflight must be run against the `Responds to:`
artifact would close it. Out of scope here; recorded as a backlog candidate.

## Implementation Cautions

These are not findings against `-007`'s design; they are hazards that could
defeat a correct design during implementation.

1. **`source_identity` must not route through `_display_path`.** That helper
   resolves against cwd and returns an **absolute** string for paths outside
   `PROJECT_ROOT`. The canonical identity must be built as a root-relative POSIX
   path, with first-line status taken from the source *text* and the version
   number from the matched `<bridge_id>-<NNN>.md` filename - never from a
   filesystem-resolved display path.
2. **`source_identity` must not fall back to sibling-glob resolution for a
   canonical explicit source.** Current operative-version machinery globs
   `bridge/<id>-*.md`, reads each sibling's first line, and can even read a
   *different* file's body to choose. If any of that leaks into
   `source_identity`, filing a later version would change an unchanged earlier
   source's hash - reintroducing the defect in a new form. `-007`'s resolver
   rule already forbids this; the implementation must honour it literally.
3. **`matched_by` ordering is already deterministic** - rules in TOML order, and
   within each rule doc then path then content, each in declared pattern order,
   with duplicate `spec_id`s resolving last-wins. The projection should preserve
   that order rather than re-sorting it, and sort only the outer
   `applicable_specs` sequence by `spec_id`.
4. **BOM edge case.** Source text is read with `encoding="utf-8"`, not
   `utf-8-sig`, and the first-line status regex does not tolerate a leading byte
   order mark. A BOM-prefixed source yields a null status. Since
   `source_identity` now includes first-line status, a BOM'd source would
   degrade identity rather than fail loudly. Worth an explicit guard or a
   negative test.

## Positive Findings

1. **The remedy was validated, not merely reviewed.** The projection reaches a
   fixed point across both divergence axes on a real packet and remains
   mutation-sensitive. This is the first version in the thread whose central
   claim could be confirmed by execution *before* implementation.
2. **The exclusion list is complete against live code**, not merely responsive
   to `-006`'s enumeration. `-007` disposed of `warnings.missing_parent_dirs`
   and `blocking_errors` - the two fields `-006` flagged - and also caught
   `content_source.mode`, closing F-LO-7 as a side effect rather than requiring
   a separate documentation fix.
3. **Adding `source_content_hash` strengthens rather than weakens binding.** The
   v1 digest bound source content only indirectly through harvested facts; an
   unrelated prose edit could retain the same hash. LF normalization
   additionally neutralizes Git line-ending materialization as a false
   divergence source, and is consistent with the rest of the pipeline, which
   already reads text with universal newlines.
4. **Scope discipline is correct.** Keeping the gate, `candidate_evidence_hash`,
   writer injection, and schema/registry surfaces out of scope is justified by
   the hash-only comparison at `:1566-1571` and by all three gate copies
   importing the single `build_packet`.
5. **Structural compliance is clean.** Both mandatory preflights pass on the
   `-007` operative file with no missing specs and no blocking gaps.

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
| GOV-FILE-BRIDGE-AUTHORITY-001 | One hash across worktree and real index-only audit; source mutation fails; live finalization succeeds | Design validated by execution; live finalization pending implementation |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Projection, gate, routing, negative, focused, live suites execute | Plan present and index-realistic per F-LO-6 |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | All five targets map to named specifications and tests | Satisfied in `-007` |
| GOV-PLATFORM-SOT-REGISTRY-001 | Registered bridge paths resolve only through exact typed publication evidence | Design accepted (F-LO-1) |
| DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 | Same-path invalid evidence fails; unrelated aggregate heads cannot hide valid evidence | Accepted; all four heads now in the test plan |
| DCL-SOT-REGISTRY-RECORD-SCHEMA-001 | Capability and revision identities remain bound without schema mutation | Preserved by design |
| DCL-SOT-REGISTRY-PROJECTION-PARITY-001 | No schema/projection change | Satisfied - revision declares none |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Packet covers exactly the declared targets | Satisfied; five declared targets |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Append-only chain and independent review | Satisfied by this `-008` |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Durable regressions encode the content/environment boundary | Planned; O-LO-9 proposes one addition |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `-006` findings converted to reviewed correction before mutation | Satisfied by `-007` |

## Applicability Preflight

- packet_hash: `sha256:d38e8c98c9037083a33e38eb7700e153bd7732d0f7d202f99b0d1a46db6615e7`
- bridge_document_name: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md`
- operative_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:c9b878d910aade07dccce263afcef3e02b82231467a467e7011e3b77580be5a0`

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
- Operative file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Blocking gaps: none. Exit 0. No owner waiver required.

## Prime Builder Implementation Context

**Objective.** Land the schema-v2 content-derived hash projection and the
exact-row-first publication routing correction across the five declared targets,
then reach live terminal finalization without bypass.

**Preconditions.** No new owner decision.
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
remains sufficient. Dispatcher stays disabled.

**Evidence paths confirmed by this review.**

- `.claude/hooks/bridge-compliance-gate.py:1493-1586` - verdict freshness check;
  `:1555` `build_packet` import; `:1557-1563` packet rebuild; `:1566-1571`
  hash-only comparison (the finding that justifies keeping the gate out of
  scope); `:1478-1490` `_candidate_evidence_hash` sentinel normalization; `:196`
  `VERDICT_PREFLIGHT_FRESHNESS_STATUSES`.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:1555` and
  `config/hooks/gtkb-bridge-compliance-gate.py:1555` - both import the same
  `build_packet`; no vendored digest logic in either.
- `scripts/check_protected_commit_authorization.py:1114-1187`
  `_isolated_compliance_audit` and `run_bridge_compliance_audit`; `:1190-1235`
  `_run_snapshot_compliance_audit`; `:1802-1822` the VERIFIED-candidate-only
  gating that bounds O-LO-8.
- `scripts/bridge_applicability_preflight.py` - `build_packet` signature is
  `(bridge_id, bridge_dir, config_path, db_path, content_file)`; note it takes
  **no** `project_root`, so any root-relativization inside `source_identity`
  must derive its root consistently with the gate's `_canonical_project_root`.

**Implementation sequence.**

1. Add the canonical source resolver and `source_identity`, honouring
   Implementation Cautions 1 and 2.
2. Add `source_content_hash` over LF-normalized source bytes.
3. Optionally add `rules_content_hash` per O-LO-9.
4. Build the explicit schema-v2 projection and hash only its sorted compact
   JSON; keep the complete packet and all diagnostics intact.
5. Land the F-LO-1 exact-row-first routing fix with the four-aggregate-head
   negative coverage.
6. Add the exact-key-set test so a future environment-derived field cannot enter
   the projection silently.

**Verification steps.** As specified in `-007` Verification Plan, plus the
O-LO-9 rules-divergence test and the Caution-4 BOM negative if adopted.

**Rollback.** Ordinary Git rollback of the five declared files before terminal
verification. No schema, registry, approval, or MemBase reversal required.

**Open decisions.** None for the owner.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
  through `-007.md` - the complete controlling chain: proposal, GO,
  implementation report, `-004` NO-GO, `-005` revision, `-006` NO-GO, and the
  `-007` revision under review.
- `DELIB-202667287` - "WI-5554: Bind LO verdict preflight evidence to its source
  and final candidate". Establishes the source-and-candidate binding. This
  revision preserves that binding and makes the source anchor reproducible;
  `source_content_hash` strengthens it.
- `DELIB-202667452` - "Loyal Opposition Verdict - WI-5659 Finalization Hold".
  Prior finalization-hold precedent on this program.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` - earlier record that an
  untracked `groundtruth.db` cannot enter the index snapshot; the structural
  fact underlying F-LO-5.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` through `-010.md` - typed
  publication-table diagnosis and publication-path friction.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner liveness
  direction; operational context only, not a hash or finalization waiver.

Fresh MemBase searches were run this session for `packet hash content
environment boundary`, `terminal VERIFIED finalization deadlock`, and `bridge
applicability preflight source identity`. No searched record requires ambient
MemBase description fields, invocation mode, or filesystem warnings to
participate in the source freshness digest.

## Commands Executed

```
gt bridge state-report
git status --short --branch
git ls-files --others --exclude-standard bridge     # 27 untracked; 7 carry embedded packet_hash
python scripts/bridge_applicability_preflight.py --bridge-id <slug>                       # exit 0
python scripts/bridge_applicability_preflight.py --bridge-id <slug> --content-file <-007>  # exit 0
python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>                              # exit 0
python -> build_packet(db present) vs build_packet(db absent)            # divergence reproduced
python -> build_packet(explicit content_file) vs build_packet(default)   # F-LO-7 reproduced
python -> schema-v2 projection over both packets                         # fixed point CONFIRMED
python -> projection under source-byte mutation                          # invalidation CONFIRMED
python scripts/bridge_claim_cli.py claim <slug>
db.search_deliberations x3
```

Read in full: `-006`, `-007`. Inspected: the gate's freshness region and
candidate-evidence hashing; the protected-commit checker's isolated-audit,
snapshot-audit, and VERIFIED-candidate regions; `build_packet` and its callees
(`compute_applicable_specs`, `enrich_from_membase`, `load_rules`, the
`extract_*` harvesters, warnings assembly, `_pauth_amendment_blocking_errors`);
and the import line in all three bridge-compliance-gate copies.

## Owner Decisions / Input

No owner decision is required by this verdict, and none was solicited.

`-007` correctly states that no new owner policy, waiver, specification,
approval packet, schema change, or MemBase mutation is needed; the remediation
choice between the stable projection and writer injection was delegated to Prime
Builder at `-006`, and `-007` selected the projection. This verdict confirms
that selection is sound and changes nothing about the authorization posture.

No waiver, destructive action, dispatcher activation, commit, push, release,
deployment, registry identity change, or MemBase mutation is requested or
performed by this verdict. The dispatcher remains disabled.

## Standing-Backlog Candidates Surfaced By This Review

1. **Re-issue the stranded terminal VERIFIED on
   `gtkb-wi5424-auto-finalization-import-repair-v2`.** Per O-LO-8 it is stranded
   under v1 and remains stranded under v2; it needs a fresh verdict, not a
   migration shim.
2. **Record the packet-hash content/environment boundary as a design
   constraint.** The exact-key-set test proposed in `-007` enforces the boundary
   mechanically, but no artifact *states* it. A DCL would prevent the class from
   recurring in adjacent digests (`candidate_evidence_hash`, capability hashes).
3. **`enrich_from_membase` fails soft and silently on an absent database.** A
   missing canonical database is indistinguishable from a spec genuinely absent
   from MemBase. Distinguishing the two would have made F-LO-5 self-announcing
   rather than requiring six bridge versions to isolate. Carried forward from
   `-006`; still unaddressed and now independently confirmed.
4. **Correct the documented preflight command.** Per O-LO-10,
   `.claude/rules/file-bridge-protocol.md` documents a bare `--bridge-id`
   invocation that yields a hash the gate cannot accept once the verdict exists.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
