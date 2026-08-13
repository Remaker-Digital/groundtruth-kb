ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 56cb086c-98da-4aa8-b759-912c91d060f0
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via harness-state/harness-registry.json (no session-stated override declared)
author_metadata_source: harness registry (canonical role projection)

bridge_kind: governance_advisory
Document: gtkb-wi5844-legacy-proposal-kind-resolution
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-31

# Loyal Opposition Advisory - `_approved_proposal_for_report()` Can Never Resolve a Legacy No-`bridge_kind` Proposal, Making the Commit-Governing Finalization Gate Unreachable on 258 Threads

## Classification Slot

**adopt** - the corrective pattern already exists inside the same file.
`_pauth_phase()` (lines 785-796) already implements the exact legacy fallback
this advisory recommends; `_approved_proposal_for_report()` is the only resolver
in the file missing it. The recommendation is to adopt the existing in-file
pattern, not to invent a new mechanism.

Severity **P1** - governance drift. This is not merely an unavailable gate: the
observed practical effect is that the commit-governing project-authorization
gate is *bypassed* rather than satisfied.

Work Item: WI-5844
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

## Non-Approval Statement

This ADVISORY is **not implementation approval**. It does not authorize
protected mutation, an implementation-start packet, a commit, or any edit to
`scripts/bridge_applicability_preflight.py`. Prime Builder disposition must
convert it into a normal `NEW` implementation proposal, obtain an independent
Loyal Opposition `GO`, acquire a fresh work-intent claim, and open an
implementation-start packet before any code changes. Advisory capture, owner
interest, and the existence of WI-5844 are each individually insufficient as
implementation authority.

## Source

Owner directive, 2026-07-31: investigate and propose a fix for a defect in
`scripts/bridge_applicability_preflight.py` found during the WI-5694 refile
(thread `gtkb-wi5694-terminal-evidence-packet-validator`).

Filed as ADVISORY rather than `NEW` because the resolved role of the
investigating session is Loyal Opposition: `harness-state/harness-registry.json`
maps `claude` to `{loyal-opposition}` and no session-stated override was
declared, so per `DCL-SESSION-ROLE-RESOLUTION-001` the registry fallback governs.
Proposal filing and implementation are Prime Builder acts per
`.claude/rules/file-bridge-protocol.md` and `.claude/rules/operating-role.md`.
The owner selected this routing explicitly (see Owner Decision Needed below).

## Claim

`_approved_proposal_for_report()` can never resolve an approving proposal on any
bridge thread whose proposal was filed before the `bridge_kind:` convention was
adopted. Because that resolver gates the finalization-phase project-authorization
evaluation, the gate governing the eventual commit (`requested_operations` =
`git_commit` + `protected_mutation`) is unreachable on those threads.

### E1 - The defect, located

Two call sites require a declared proposal kind:

- Implicit candidate scan, line 860:
  `if _bridge_kind(candidate_content) in PROPOSAL_BRIDGE_KINDS and approved_by_go(version):`
- Explicit `Approved proposal:` escape hatch, line 842:
  `if _bridge_kind(proposal_content) not in PROPOSAL_BRIDGE_KINDS:`

`_bridge_kind()` (line 780) returns `None` when `BRIDGE_KIND_RE` finds no
`bridge_kind:` line. `PROPOSAL_BRIDGE_KINDS` (line 130) is
`frozenset({"prime_proposal", "implementation_proposal"})`. `None` is in neither
set, so a legacy proposal fails both paths. The documented escape hatch provides
no relief because it applies the identical check.

### E2 - Reproduction, executed against live bridge state

Thread `gtkb-wi5694-terminal-evidence-packet-validator`:

| Version | Status | `bridge_kind` | References |
|---|---|---|---|
| -001 | NEW | *(absent)* | - |
| -002 | GO | `lo_verdict` | `Responds to: ...-001.md` |
| -003 | NEW | *(absent)* | `Responds to: ...-002.md` |
| -004 | NO-GO | `lo_verdict` | `Responds to: ...-003.md` |
| -005 | REVISED | `prime_proposal` | `Responds to: ...-004.md` |
| -006 | NO-GO | `lo_verdict` | `Responds to: ...-005.md` |

Simulating a correctly-labelled implementation report as `-007`
(`bridge_kind: implementation_report`):

```text
_pauth_phase(report)       -> finalization
resolver                   -> rel=None
                              err='Implementation report has no readable earlier
                                   proposal-kind artifact with a matching GO verdict'
explicit escape hatch      -> rel=None
                              err='Approved proposal metadata does not identify a
                                   proposal-kind artifact:
                                   bridge/gtkb-wi5694-terminal-evidence-packet-validator-001.md'
_bridge_kind(-001)         -> None
_status_from_content(-001) -> NEW
```

Both paths fail closed, matching the reported
`reason_code: approved_proposal_resolution_failed`.

`-005` is not rescued by its `prime_proposal` label either: its only later
verdict `-006` is `NO-GO`, not `GO`, so `approved_by_go()` rejects it. The
GO-reference requirement, not the kind label, is what actually selects the
approving proposal.

### E3 - Root cause: an unbackfilled migration

`scripts/migrate_bridge_kind_taxonomy.py` lines 152-154:

```python
match = BRIDGE_KIND_RE.search(content)
if not match:
    continue
```

The taxonomy migration normalized *existing* `bridge_kind` values (for example
`implementation_proposal` -> `prime_proposal`) but skipped files that had no
`bridge_kind:` line at all. It never backfilled.
`_approved_proposal_for_report()` was written later assuming the line is always
present. Neither component is wrong in isolation; the defect lives in the seam.

### E4 - Population, census over the live `bridge/` tree

| Measure | Count |
|---|---|
| Versioned bridge files | 14,377 |
| Files with no `bridge_kind:` line | 3,303 (23%) |
| Legacy `NEW`/`REVISED` files with no `bridge_kind:` | 726 |
| **Threads with a legacy proposal AND a GO (affected)** | **258** |

Affected threads include `application-isolation-contract`,
`agent-red-repo-migration-001`, and `active-workspace-declaration-slice-1`.

### E5 - The resolver contradicts `_pauth_phase()` in the same file

`_pauth_phase()` lines 791-795 already implement the recommended fallback:

```python
if PAUTH_METADATA_RE.search(content) and extract_declared_target_paths(content):
    status = _status_from_content(content)
    if status in {"NEW", "REVISED"} and any(version.status == "GO" for version in versions):
        return "finalization"
    return "proposal"
```

It reads the first-line status token and requires an in-thread GO when
`bridge_kind` is absent. The two functions therefore disagree about the same
artifact: `_pauth_phase()` routes the report to `finalization`, and the resolver
then refuses to supply the approving proposal that the finalization phase
requires.

### E6 - Status-token inference is already shipped precedent

`migrate_bridge_kind_taxonomy.py::map_bridge_kind()` lines 84-91 fall back to the
first-line status token when the kind is unknown, classifying
`GO`/`NO-GO`/`VERIFIED`/`WITHDRAWN` as `lo_verdict`, `ADVISORY` as
`governance_advisory`, and defaulting everything else to `prime_proposal`. The
recommended fallback is the same inference applied more conservatively: it
additionally requires status in `{NEW, REVISED}` **and** a GO reference.

### E7 - Safety: zero mis-rescues across the full corpus

Simulating the proposed fallback over all 14,377 bridge files, classifying each
rescued artifact by shape (counting report-only headings `Implementation Report`,
`Spec-to-Test Mapping`, `Commands Executed`, `Files Changed`,
`Recommended Commit Type`):

| Result | Count |
|---|---|
| Artifacts the fallback would rescue | 55 |
| ...proposal-shaped | **55** |
| ...report-shaped, i.e. a mis-classification | **0** |

No legacy implementation report in the corpus is referenced by a `GO`. This
empirically confirms the protocol invariant that makes the fallback safe: only
proposals receive `GO`; reports receive `VERIFIED` or `NO-GO`.

### E8 - A second consumer inherits the defect

`scripts/pauth_finalization_exposure_sweep.py` states it "delegates PAUTH
evaluation to the same canonical operation-time path used by
`bridge_applicability_preflight.py`". Repairing the resolver corrects both
surfaces; no separate change is required there.

## Risk / Impact

The finalization-phase PAUTH evaluation is the gate standing between an
implementation report and its commit. On the 258 affected threads it cannot
pass. Both observed consequences are failure modes of bypass, not of blockage:

1. Reports omit the finalization markers entirely, so the gate never runs; or
2. Reports mislabel themselves `bridge_kind: prime_proposal`, so `_pauth_phase()`
   routes to the proposal phase and evaluates `implementation_packet_create` /
   `implementation_start` instead of `git_commit` / `protected_mutation`.

`bridge/gtkb-wi5694-terminal-evidence-packet-validator-005.md` is a live
instance of mode 2: it is titled "Implementation Report (REVISED)" and carries
`## Spec-to-Test Mapping`, `## Commands Executed`, `## Files Changed`, and
`## Recommended Commit Type`, yet declares `bridge_kind: prime_proposal`.

## Recommended Prime Action

File a `NEW` implementation proposal under WI-5844 and
PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, covered by the list-free
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
(owner decision `DELIB-202667732`), with `target_paths`
`scripts/bridge_applicability_preflight.py` and
`platform_tests/scripts/test_bridge_applicability_preflight.py`.

Proposed change - add a legacy status-token fallback to the proposal-kind test,
applied at both call sites, retaining `approved_by_go()` as the discriminator:

```python
LEGACY_PROPOSAL_STATUS_TOKENS: Final[frozenset[str]] = frozenset({"NEW", "REVISED"})


def _is_proposal_kind(content: str) -> bool:
    """True when the artifact is a proposal-kind bridge artifact.

    Artifacts filed before the ``bridge_kind`` convention carry no such line.
    For those, fall back to the first-line status token: NEW/REVISED identifies
    a Prime-authored proposal. Callers pair this with ``approved_by_go``, which
    is what excludes legacy implementation reports (also filed NEW) - only
    proposals receive GO.
    """
    kind = _bridge_kind(content)
    if kind is not None:
        return kind in PROPOSAL_BRIDGE_KINDS
    return _status_from_content(content) in LEGACY_PROPOSAL_STATUS_TOKENS
```

Call-site edits:

- Line 842: `if not _is_proposal_kind(proposal_content):`
- Line 860: `if _is_proposal_kind(candidate_content) and approved_by_go(version):`

Both paths keep the GO requirement - the explicit path checks
`approved_by_go(match)` immediately afterward at line 848 - so neither weakens
the discriminator. The change alters no status semantics, no packet-hash
material, and no `bridge_kind` authoring rule.

### Proposed spec-derived tests

For `platform_tests/scripts/test_bridge_applicability_preflight.py`:

1. Legacy proposal (`NEW`, no `bridge_kind`) plus later GO referencing it -> resolves.
2. Legacy artifact (`NEW`, no `bridge_kind`) not GO-referenced -> still rejected.
3. Explicit `Approved proposal:` pointing at a legacy proposal -> resolves.
4. Modern `bridge_kind: prime_proposal` behaviour -> unchanged.
5. Non-proposal status token (`ADVISORY`, `DEFERRED`, `NO-ACTION`) with no
   `bridge_kind` -> still rejected.
6. End-to-end: finalization-phase PAUTH evaluation on a legacy-proposal thread
   reaches a verdict instead of `approved_proposal_resolution_failed`.

### Explicitly out of scope

**`bridge_kind` shape validation.** The mislabeling incentive that produced
`-005` is real, but closing it is a new blocking authoring gate with heuristic
false-positive risk, and bridge files are append-only, so `-005`'s wrong
`bridge_kind` can never be corrected. Any such validator needs its own
grandfathering design and owner decision. The owner selected resolver-fallback-only
scope for this cycle; shape validation should be filed as its own work item.

**Backfilling `bridge_kind` into 3,303 historical files.** Declined: it would
rewrite append-only audit artifacts and would require an explicit owner waiver
against `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Owner Decision Needed

Three decisions were already collected via AskUserQuestion during the
investigation session (2026-07-31) and are recorded here as durable evidence:

1. **Work location** - "Main checkout `E:\GT-KB`". The investigating session's
   worktree held a 604-line copy of the target file predating
   `_approved_proposal_for_report()` entirely, and a `bridge/` tree 2,138 files
   behind the main checkout.
2. **Fix scope** - "Resolver fallback only". Shape validation and migration
   backfill were both explicitly declined for this cycle.
3. **Role path** - "File LO ADVISORY". The owner declined to declare a
   session-stated Prime Builder role, routing this to Prime Builder disposition.

The following remain **open** and must be resolved before a derived
implementation proposal is filed as `NEW`:

4. **Retroactive effect.** The fix makes the finalization gate *reachable* on 258
   previously-ungated threads. Should those threads be swept and re-evaluated
   after the fix lands, potentially surfacing new blocking findings on work
   already committed, or does the fix apply prospectively only?
5. **WI-5694 chain disposition.** Should that thread proceed on the corrected
   resolver, be refiled at a new version carrying the correct
   `bridge_kind: implementation_report`, or be preserved as historical evidence?
6. **Shape-validation follow-on.** File it now as its own work item, or hold
   until the resolver fix is VERIFIED and its effect on the mislabeling incentive
   is observed?

## Required Prime Builder Owner-Grilling Gate

Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and
`.claude/rules/peer-solution-advisory-loop.md`, this section is mandatory
because the classification is `adopt`.

### Implementation implied

**Yes.** Adoption modifies `scripts/bridge_applicability_preflight.py` (one new
constant, one new helper, two call-site edits) and adds regression cases to
`platform_tests/scripts/test_bridge_applicability_preflight.py`.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to open items
4, 5, and 6 under Owner Decision Needed above before drafting the derived
implementation proposal.

### Required durable owner decisions

- Retroactive-versus-prospective scope for the 258 affected threads.
- WI-5694 chain disposition: proceed, refile, or preserve.
- Whether shape validation is filed now or deferred.

The AskUserQuestion evidence must land in the derived proposal's mandatory
`## Owner Decisions / Input` section per
`.claude/rules/file-bridge-protocol.md`.

## Prior Deliberations

Deliberation search executed 2026-07-31 for
`bridge_kind proposal resolution legacy artifact approved proposal resolver`
returned 5 results, none on topic (semantic scores 0.652-0.700; all unrelated LO
verdicts: `DELIB-202667576`, `DELIB-202667164`, `DELIB-20264722`, `DELIB-2576`,
`DELIB-20265748`).

_No prior deliberations found for legacy `bridge_kind` proposal-kind resolution._

Related but distinct work items, checked for overlap and duplication:

- **WI-5479** - bridge_kind taxonomy: advisory enum bakes in role/domain. Same
  file family, different concern (enum vocabulary, not absent-value resolution).
- **WI-5372** - stale docs cite retired `loyal_opposition_advisory`.
  Documentation drift, not resolver behaviour.
- **WI-5694** - the thread whose refile surfaced this defect. Separate concern
  (packet-expiry authority model, owner-decided 2026-07-30).
- **WI-4808** - preflight performance, O(n) bridge read. Same file, unrelated
  defect.

No existing work item covered this defect; WI-5844 was created for it.

## Verification Expectations

An implementation report converting this advisory must carry forward the
`Specification Links` set, provide a spec-to-test mapping for tests 1-6 above,
report `ruff check` **and** `ruff format --check` results on the changed Python
files (separate gates per `.claude/rules/file-bridge-protocol.md`), and re-run
the E7 corpus safety measurement to confirm the mis-rescue count remains 0 at
implementation time.

## Reproduction Commands

All measurements are reproducible read-only from the main checkout:

```bash
python - <<'PY'
import sys, pathlib
sys.path.insert(0, "scripts")
import bridge_applicability_preflight as bap
BID = "gtkb-wi5694-terminal-evidence-packet-validator"
versions = bap.parse_versioned_files_for_document(pathlib.Path("bridge"), BID)
report = "NEW\n\nbridge_kind: implementation_report\nVersion: 007\n"
print(bap._pauth_phase(report, versions))
print(bap._approved_proposal_for_report(
    bridge_id=BID, report_content=report, versions=versions))
PY
```

## Incidental Observation (not part of this advisory's claim)

While filing this advisory, the WI-ID collision gate emitted
`[Governance] WI-ID collision gate skipped ...: database disk image is malformed`.
Canonical MemBase is healthy - `PRAGMA quick_check` on `groundtruth.db` returns
`ok` - so this points at a separate store used by that gate, which is silently
degrading to skip. Not investigated further here; flagged for triage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
