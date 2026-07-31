NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

bridge_kind: governance_review
Document: gtkb-advisory-wi5368-cross-thread-target-collision
Version: 001
Date: 2026-07-30 UTC
Related Work Items: WI-5368, WI-5298, WI-4471, WI-3274
target_paths: []

requires_review: true
requires_verification: false
kb_mutation_in_scope: false
implementation_authority: none
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report - Cross-thread target collision produced contradictory live GOs

## Advisory Status

This is a concurrency and lifecycle-control report, not implementation
approval. It preserves a concrete recurrence so a later owner-approved project
can correct target ownership, lookup, claim, and implementation-start behavior.
No source, test, configuration, MemBase, dispatcher, TAFE, Git, process, or
external-system mutation is authorized by this report.

## Claim

GT-KB allowed two numbered bridge threads to reach physically latest `GO`
status over the exact same two protected files even though their approved
designs cannot both be implemented. The proposal and review workflows failed
to detect the collision because current bridge lookup is keyed by thread or
work item, not by declared target path. A shared narrative predecessor check
then produced the same blind spot in both proposal and review.

The unsafe executable signal was removed by
`bridge/gtkb-wi5368-codex-git-window-command-family-007.md`. The underlying
concurrency flaw remains and should be corrected before another overlapping GO
reaches implementation start.

## Case Context

The contested paths are:

- `scripts/ops/codex_snapshot_window_hider.py`
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`

The colliding threads are:

| Thread | Physical latest state | Project state | Design summary |
| --- | --- | --- | --- |
| `gtkb-wi5368-codex-git-window-command-family` | v006 `GO` on 2026-07-29; exact live bytes are receipted and consumed; now followed by PB `NO-ACTION` v007 whose receipt rationale was based on stale work-item detail | Harness Parity project active; WI-5368 open | require exact `core.hooksPath=NUL` and empty `core.fsmonitor=` markers; direct Git/conhost relation; mutex unchanged |
| `gtkb-wi5298-codex-git-window-family-containment-repair` | v002 `GO` on 2026-07-19; no report or terminal verdict | Goose Harness Adoption project retired; WI-5298 resolved | do not use Git arguments as an allowlist; allow nested Git ancestry; bump singleton mutex to v2 |

Both paths remained clean at discovery. The source Git blob was
`4b0ed05225b161bd582e53489c393a2b5a7693e9`; the test Git blob was
`309f56fa9f7f499815628281c27ccd2890cef13d`. The defect was caught before
either competing design changed the files.

## Findings

### F1 - P1 - Live target ownership is not serialized across bridge threads

**Evidence.** The two proposals declare identical target sets but different
work items and projects. Both received independent GO verdicts. No mechanism in
the numbered-file lifecycle prevented the second GO or made the earlier claim
visible as a target-path conflict.

**Risk/impact.** Either implementation can overwrite, absorb, or misattribute
the other's changes. A later report can present a clean scoped diff while
silently violating the other approved contract. Exact preimage checks catch
only target drift after a mutation; they do not prevent contradictory authority
while both targets are still clean.

**Recommended action.** At proposal review and
`implementation_authorization.py begin`, calculate the declared target set and
query all nonterminal bridge threads for intersections. Fail closed when an
intersecting live GO has no explicit serialization, supersession, or shared
carrier disposition. The result should name every conflicting thread, project,
work item, target, status, and recovery route.

### F2 - P1 - Work-item-keyed lookup cannot answer target-ownership questions

**Evidence.** `gt bridge threads --help` exposes a work-item selector but no
target-path selector. The colliding threads use WI-5368 and WI-5298, so a
correct `--wi WI-5368` lookup cannot return the WI-5298 repair. Discovery
required a broad repository text search for the target filename.

**Risk/impact.** Review correctness depends on authors independently guessing
which other work items may touch the same path. As the append-only bridge SoT
grows, full-text discovery becomes slower, noisier, and easier to truncate or
scope incorrectly.

**Recommended action.** Add a maintained target-path projection or index and a
read-only query such as `gt bridge threads --target-path <path>`. The index must
be derived from canonical numbered files, preserve append-only history, expose
current lifecycle state, and support bounded rebuild/verification so its access
cost does not scale as a full historical rescan on every implementation start.

### F3 - P1 - Shared narrative evidence created correlated review failure

**Evidence.** WI-5368 v005 declared shared ownership closed after confirming
that `gtkb-wi5298-codex-snapshot-git-window-containment` was terminal VERIFIED.
The v006 reviewer repeated the same named-thread check. Neither inspected the
separate `-family-containment-repair` successor.

**Risk/impact.** Independent sessions can still share the same incomplete
retrieval path. Session independence is necessary for review, but it is not
sufficient when both sides use an unindexed narrative anchor.

**Recommended action.** Make target collision evidence deterministic and
machine-produced in proposal and verdict preflights. Reviewers should verify a
complete generated conflict set rather than restating the proposal's manually
selected predecessor list.

### F4 - P1 - Stale work-item detail contradicted exact receipt authority

**Evidence.** The WI-5368 `status_detail` read during Prime triage says the live
v006 is a direct unreceipted file and names v005 revision
`SOTREV-7A3E89F74F084BF8904022ED9D8FDA56` as the last consumed artifact. That
text describes an older quarantined v006 copy at
`bridge/cleanup-evidence/wi5733-unreceipted-publication-incident-20260729/`
whose SHA-256 is
`7111189EA2A85E88EBB521D823412EA9F11DABDC28C169D68671FC6A21A06582`.

The current live v006 is a different 7,445-byte artifact with SHA-256
`9F474554373E889319A2B43837DA0C2ADCC7BB19E9CF269919BF27EC57A6E417`.
Exact capability row 344 in
`sot_registry_bridge_publication_capabilities` binds that live digest, path,
version, GO status, and author session. It is `consumed` at
`2026-07-30T01:13:57Z` under revision
`SOTREV-A2891713C0784B57A1A6B3D5D4603C31` with no failure reason.

The stale status detail caused Prime Builder to file v007 with a false
unreceipted-artifact rationale. The v007 stop outcome remains correct because
the sibling target collision is independently sufficient, but the receipt
finding must be rejected during independent review and must not be propagated.

**Risk/impact.** A convenient work-item projection can lag the exact typed
authority surface while retaining authoritative-sounding hashes and recovery
instructions. Operators can make a governance mutation that is internally
coherent, passes static preflights, and is nevertheless factually stale. The
failure is more dangerous than a slow read because the faster surface returns
a confident obsolete answer.

**Recommended action.** Make generated work-item status detail revision-aware.
Any detail that cites bridge currentness should record the exact physical
digest and receipt revision it was derived from, expose an `as_of` marker, and
be invalidated or regenerated when a later exact publication capability is
consumed. Triage commands should resolve exact capability/currentness first and
label stale narrative detail as advisory context rather than current authority.

## Append-only SoT And Latency Considerations

Append-only bridge history is valuable here because it preserves both
contradictory approvals and the evidence showing how they arose. The corrective
design should not erase or rewrite either chain. It should add a compact,
rebuildable current-target projection so common ownership queries do not scan
the entire historical SoT.

The projection should record at least normalized target path, bridge thread,
physical head, receipted head, lifecycle status, project, work item, claim
state, source revision, and derivation time. Updates should be atomic with
governed bridge publication where possible; a deterministic rebuild and
comparison command should detect drift. Historical files and exact typed
receipts remain authoritative evidence, while the projection is the
bounded-access route whose integrity and freshness are continuously checked.

## Relationship To Existing Work

- `bridge/gtkb-lo-concurrent-go-target-overlap-advisory-001.md` records an
  earlier occurrence and already recommends target intersection checks.
- `.gtkb-state/propose-drafts/gtkb-lo-wi5368-contested-target-paths-advisory-001.md`
  contains the detailed Loyal Opposition investigation of this case. This live
  Prime Builder report preserves its core evidence without pretending to author
  an LO-only `ADVISORY` status.
- `bridge/gtkb-lo-wi5368-legacy-chain-verdict-publication-blocker-advisory-001.md`
  records the adjacent WI-5368 publication-lifecycle defect.
- WI-4471 and WI-3274 are the identified historical backlog carriers for
  collision detection and target-path indexing. Their current lifecycle and
  project authority must be rechecked before any corrective proposal; this
  report does not reactivate or approve either item.

## Recommended Governed Disposition

1. Obtain independent review of WI5368 v007. Preserve its collision-based stop,
   explicitly reject its stale unreceipted-artifact rationale, and do not carry
   that false receipt finding forward.
2. Give the retired WI5298 repair thread an explicit bridge terminal,
   supersession, or withdrawal disposition without inferring authority from its
   retired project.
3. Select one active project carrier for the target-index and collision-gate
   correction, preferring an existing related project/work item over a duplicate.
4. Obtain owner project approval through the required one-question AUQ flow if
   that carrier lacks active whole-project PAUTH.
5. File a bounded implementation proposal, independent GO, exact claim, and
   implementation-start packet before protected source or test work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` - work items
  inherit implementation approval only from an active parent project.
- `DELIB-202665330` - mutation work intent must be target scoped.
- `DELIB-202665331` - project authorization may mint target-scoped mutation
  intents.
- `DELIB-202665746` - prior target-path dispatch serialization treatment.
- `DELIB-202667231` - an undisclosed sibling claimant over shared paths is a
  NO-GO-grade defect.
- `DELIB-202666274` - historical project authority with preserved bridge,
  independent review, claim, implementation-start, and operation-time gates.

## Owner Decision Needed

None to preserve this Advisory Report. Corrective implementation is not
approved here. If the selected existing backlog carrier lacks active
whole-project authority, Prime Builder must present one AUQ for the parent
project after the already-pending exact formal-artifact decision is resolved.

## Specification-Derived Verification Outline For Future Correction

| Governing requirement | Future verification | Required result |
| --- | --- | --- |
| Cross-thread serialization | `python -m pytest` focused collision tests using different WIs and projects with identical/overlapping paths | second live authority is rejected with complete conflict evidence |
| Target query bounded access | focused CLI tests plus benchmark on a large synthetic append-only bridge history | query returns complete current owners without a full per-request historical scan |
| Projection integrity | deterministic rebuild and compare tests | projection matches canonical numbered files and reports drift fail closed |
| Narrative projection freshness | tests that consume a replacement artifact with the same document/version but different digest | stale status detail is invalidated or visibly marked stale; exact receipt wins |
| Independent review | proposal and verdict fixtures sharing an incomplete narrative predecessor | generated conflict set prevents correlated omission |
| Nonimpairment | scoped tests and static review | no dispatcher, TAFE, harness role, eligibility, process, credential, Git, release, or deployment mutation |

All generated artifacts remain in-root under `E:\GT-KB\bridge\`. The canonical
future test command family is `python -m pytest <focused-targets> -q --tb=short`
with scoped Ruff and `git diff --check` evidence.

## Risk And Recovery

The main correction risk is over-serializing legitimate sequential work or
making a stale projection a new opaque authority. Preserve explicit
supersession/serialization exceptions, make the projection rebuildable from
append-only files, and fail closed only for unresolved live intersections or
currentness divergence. Rollback is a governed source/test repair; never delete
or rewrite the historical bridge chains.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
