ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: cf6a1dd6-565e-4fd0-82f3-2adb697272db
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-gov-file-bridge-authority-spec-body-path-orphaned-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28

# Loyal Opposition Advisory - Registered spec_body_path for GOV-FILE-BRIDGE-AUTHORITY-001 Is Orphaned by an Unaccompanied File Move

## Source

Surfaced during a scheduled Loyal Opposition bridge-queue run on 2026-07-28. The
LO-actionable queue was empty (0 NEW/REVISED/NO-ACTION), so the run proceeded to
verify the nine bridge threads that live TAFE state classifies as `UNKNOWN`. One
of those threads, `bridge/gov-file-bridge-authority-001.md`, proved not to be a
bridge thread at all but a governance spec body, which exposed the registry
mismatch reported here.

Related thread: `bridge/gtkb-gov-file-bridge-authority-001-004.md` (VERIFIED).
Related work item: WI-5193 (adjacent, same spec family; distinct defect).
Originating commits: `7896c1e7e` (formalization), `db07f9dcf` (the rename).

## Claim

`config/governance/spec-applicability.toml` registers a `spec_body_path` for
`GOV-FILE-BRIDGE-AUTHORITY-001` that does not resolve in the working tree. A pure
file rename in commit `db07f9dcf` relocated the spec body from
`config/governance/` to `bridge/` without updating the registry pointer that
names it. The rule carrying the broken pointer is `severity = "blocking"` with
`applies_when_doc_matches = ["*"]`, so it is evaluated against every bridge
document in the platform.

### Evidence

**Registry declaration** - `config/governance/spec-applicability.toml` lines 25-31
declare `spec_id = "GOV-FILE-BRIDGE-AUTHORITY-001"`, `severity = "blocking"`,
`spec_body_path = "config/governance/gov-file-bridge-authority-001.md"`,
`clause_count = 16`, and `applies_when_doc_matches = ["*"]`.

**The declared path does not exist.** A filesystem check of
`config/governance/gov-file-bridge-authority-001.md` returns MISSING. Listing
`config/governance/*.md` returns "No such file or directory" - the directory
contains no markdown files at all, only `.toml` and one `.json`.

**The path is not tracked at HEAD.** `git ls-files config/governance/` lists 20
entries; `gov-file-bridge-authority-001.md` is not among them.

**The body actually lives at `bridge/gov-file-bridge-authority-001.md`.**

**Root cause - an unaccompanied rename.** `git show --stat --find-renames db07f9dcf`
scoped to the two candidate paths reports exactly one changed file,
`{config/governance => bridge}/gov-file-bridge-authority-001.md`, with 0
insertions and 0 deletions: a pure rename, zero content change. The same command
scoped to `config/governance/spec-applicability.toml` returns empty output - the
registry was NOT touched in that commit. The move orphaned the pointer. Commit
`db07f9dcf` ("Synching backlog") describes itself as a bulk push to clear a
GitHub blockage, consistent with an incidental relocation rather than a
deliberate re-registration.

**Original placement was the registered one.** `git log` for the declared path
shows it was created by `7896c1e7e` ("chore: register goose harness E, formalize
GOV-FILE-BRIDGE-AUTHORITY-001, ..."), the same commit that added the
`spec_body_path` field. The pointer was correct when written.

**Prior verification did not catch it, and cannot be relied on to.**
`bridge/gtkb-gov-file-bridge-authority-001-003.md` records: "Verified that
`spec_body_path` and `clause_count` match the physical file." That verification
predates the `db07f9dcf` rename, so it was accurate when issued - stale now, not
wrong-at-issue. Note that the file still sits at the old `config/governance/`
location inside four `.claude/worktrees/*` checkouts and several `.gtkb-state/`
snapshots, so a re-check run from a stale worktree would still pass. That is a
false-green surface for any future re-verification.

### Impact and severity

**Assessed severity: P2 (meaningful weakness, bounded impact).**

Bounding evidence - `spec_body_path` currently has ZERO Python consumers. A
repository-wide search finds the identifier only in the TOML declaration itself
and in bridge narrative files. No gate, preflight, doctor check, or test resolves
it today. There is no active runtime breakage, which is why nothing failed and no
test went red.

Why it still matters:

1. **It is the only `spec_body_path` in the registry.** No other rule declares the
   field, so there is no sibling to make the breakage visible by comparison.
2. **It was the stated closure of a citation gap.** Per
   `bridge/gtkb-gov-file-bridge-authority-001-002.md`, registering the field
   "closes the citation gap that originally blocked the B1-B5 bundle proposals."
   Downstream proposals are told a machine-readable, clause-numbered 16-clause
   body exists at that path. It does not.
3. **It is latent, not benign.** The first consumer that resolves `spec_body_path`
   - a clause-level preflight, a doctor check, a spec-coherence validator -
   inherits a broken path on a blocking rule that matches every document. The
   failure mode is then either a hard error on all bridge traffic or a silent skip
   of a blocking-severity rule.
4. **Agent discoverability.** An agent told to read the canonical clause body under
   `config/governance/` will not find it and may conclude the formalization never
   landed.

## Owner Decision Needed

None to file this advisory. Advisory capture is explicitly non-approval and
requires no owner decision.

One owner-relevant choice is deferred to Prime Builder disposition: Option A
(correct the pointer) versus Option B (restore the file), below. If Prime Builder
judges that choice to carry governance weight - specifically whether a live
governance spec body belongs under `bridge/`, a directory whose contents are
otherwise append-only protocol audit artifacts - it should be routed to the owner
via `AskUserQuestion` at proposal time, not resolved silently.

## Recommended Prime Action

File a focused implementation proposal. The repair is small, but the choice of
direction is a design decision that belongs to Prime Builder, not to this
advisory.

**Option A - correct the pointer (lower risk).** Update
`config/governance/spec-applicability.toml` to
`spec_body_path = "bridge/gov-file-bridge-authority-001.md"`. Accepts the current
location. Leaves a governance spec body living under `bridge/`.

**Option B - restore the file to its registered home.** Move
`bridge/gov-file-bridge-authority-001.md` back to
`config/governance/gov-file-bridge-authority-001.md`, leaving the registry
unchanged. Consistent with the original formalization intent and with
`config/governance/` as the home for governance config. Requires confirming
nothing now cites the `bridge/` path. Would incidentally remove one spurious
`UNKNOWN` thread from bridge state, since the file is currently counted as a
bridge thread whose first line is a markdown heading rather than a status token.

**Regardless of option, add an existence assertion.** The durable fix is not the
path edit; it is preventing silent recurrence. Recommend a deterministic check
that every `spec_body_path` declared in `spec-applicability.toml` resolves to an
existing tracked file, wired into the doctor or the applicability preflight, so a
future rename fails loudly instead of orphaning the pointer.

Suggested target paths for the eventual proposal:

- `config/governance/spec-applicability.toml`
- `bridge/gov-file-bridge-authority-001.md` (if Option B)
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (existence assertion)
- `platform_tests/` (test proving a dangling `spec_body_path` is detected)

**Relationship to WI-5193.** WI-5193 already tracks unfinished work in this spec
family: `scripts/check_file_bridge_authority.py` and its focused test are absent,
and `GOV-FILE-BRIDGE-AUTHORITY-001` v3 must not be promoted until its declared
assertions are implemented and independently verified. This advisory is adjacent
but distinct - WI-5193 concerns missing assertion implementation blocking a status
promotion; this concerns a registry pointer orphaned by a file move. They are
separable, but Prime Builder may prefer to fold this repair into WI-5193 scope
since both touch the same spec family and both bear on whether that spec can be
promoted. That scoping decision is Prime Builder's.

## Classification Slot

Recommended classification: **adapt**. The defect is real and confirmed, but the
correct remedy is a Prime Builder design choice between two viable directions
plus a durable existence assertion, not a mechanical application of a
pre-determined fix.

Slot left open for Prime Builder disposition. Permitted values: `adopt`, `adapt`,
`reject`, `defer`, `monitor`.

## Prior Deliberations

Two Deliberation Archive searches were run before filing:

1. "spec_body_path GOV-FILE-BRIDGE-AUTHORITY spec body path missing
   config/governance" - 5 results, best semantic score 0.638 (`DELIB-202667351`,
   an unrelated WI-5629 verdict chain). No result addresses this defect.
2. "governance config registry path does not resolve orphaned file move rename" -
   5 results, best semantic score 0.972 (`DELIB-202666361`, WI-5142 registry
   readiness). No result addresses this defect.

Bridge advisory duplicate search: no file under `bridge/*advisory*.md` mentions
`spec_body_path`. Backlog search surfaced WI-5193 and WI-5357 as the only
`GOV-FILE-BRIDGE-AUTHORITY-001` matches; neither covers the orphaned pointer.

No prior deliberation, advisory, or work item covers this finding.

## Non-Approval Statement

This advisory preserves a defect finding for later governed disposition. It is NOT
implementation approval. It does not authorize protected-file edits, does not open
an implementation-start packet, and does not bypass the bridge proposal, Loyal
Opposition `GO`, project-authorization, or verification gates. Any repair requires
a normal Prime Builder implementation proposal reviewed under the standard bridge
protocol.

## Methodology Trail

- `gt bridge state-report` and `--json` - live TAFE/dispatcher bridge state.
- Filesystem checks on `config/governance/` and the declared body path.
- `git ls-files config/governance/`, `git log` on both candidate paths,
  `git show --stat --find-renames db07f9dcf`.
- Repository-wide search for `spec_body_path` consumers (TOML plus bridge
  narrative only; zero Python consumers).
- `gt deliberations search` (two queries), bridge advisory grep, `gt backlog list`
  filtered to the spec family.
- Full read of the nine `UNKNOWN`-status bridge files to confirm none was an
  unreviewed proposal (delegated to a read-only subagent; its incidental claims
  were independently re-checked, and one - an allegedly missing
  `gtkb-v1-s509-proposal-remediation-*.md` thread - was found to be incorrect and
  is not carried into this advisory).
