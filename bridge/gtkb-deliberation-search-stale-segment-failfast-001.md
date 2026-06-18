NEW

Document: gtkb-deliberation-search-stale-segment-failfast
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4568
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Deliberation-search stale-segment fast-fail and semantic-only fail-closed (non-destructive subset)

## Summary

Fix the non-destructive core of the ChromaDB stale-HNSW-segment cascade on the
governance-critical deliberation-search read path, scoped to two surgical
changes that need no owner decision and no destructive recovery:

(b) In KnowledgeDB.search_deliberations, stop RETRYING the ChromaDB semantic
query on a stale-format / incompatible-segment error. The timeout branch already
breaks without retry ("a stalled store will stall again"); the generic-exception
branch currently `continue`s, re-attempting the same doomed query
_CHROMA_QUERY_RETRIES additional times, each attempt amplifying the doomed-query
/ abandoned-thread pileup. Classify stale-format errors and break (clean SQLite
LIKE fallback), retaining retry only for genuinely transient errors.

(c) Make `gt deliberations search --semantic-only` fail CLOSED. Today, when the
semantic pass degrades to the LIKE fallback, the --semantic-only filter yields
zero rows and the command prints "No deliberations match" with exit 0 - silently
hiding that the mandatory pre-proposal/pre-review semantic search did not run.
Surface a per-call degradation signal from search_deliberations and have the
--semantic-only CLI path exit non-zero when ChromaDB was expected but the
semantic pass degraded, so a degraded governance search is loud, not silent.

Out of scope (deliberately): the detect-only rebuild pre-check (candidate a) is
a follow-on slice; the DESTRUCTIVE recovery (deleting on-disk segment files,
reaping abandoned index-holding threads/processes) is the genuine lock-holder-
pileup root cause but is a destructive recovery-policy choice and is flagged
below as a separate owner-decision item, NOT included here.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 - governing lane; WI-4568 is a defect-origin,
  single-concern reliability fix admitted to PROJECT-GTKB-RELIABILITY-FIXES under
  the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING. The
  non-destructive (b)+(c) subset is small (two existing files + one test).
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - the deliberation-search is the mandatory
  pre-proposal/pre-review SoT read surface; failing closed on degradation and
  not silently returning [] protects the freshness contract.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the fast-fail, degradation-
  signal, and fail-closed tests derive from this constraint.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the fix and its decision
  trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the defect and remediation
  are captured as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - touching the deliberation-
  search surface triggers the artifact-lifecycle controls this constraint
  governs.

## Prior Deliberations

<!-- reviewed -->

- DELIB-FAB17-REMEDIATION-20260610 - owner fix-scope for DA/Chroma read-path
  reliability (wrap count() + timeout/retry); this slice continues that
  read-path hardening by removing the doomed-query retry and the silent
  degradation that the timeout/LIKE-merge work left.
- gtkb-wi4561-chromadb-py314-gate-fix (VERIFIED) - its Recommended Follow-On
  explicitly DEFERRED candidate (c) (--semantic-only fail-closed) to a separate
  standing-backlog reliability item, i.e. WI-4568; this proposal implements it.
- WI-4519 (always-on LIKE merge) and WI-4453 (embedding timeout) - hardened
  adjacent surfaces (the LIKE merge and the embedding-write timeout) but neither
  addresses the stale-segment retry amplification or the semantic-only silent
  degradation.
- No direct prior deliberation exists on the stale-segment fast-fail itself.

## Requirement Sufficiency

Existing requirements sufficient. The change removes a defect (doomed-query
retry amplification + silent semantic degradation) on an existing read path. It
introduces no new requirement or specification; the fail-closed behavior is the
defect removal itself (mandated by GOV-SOURCE-OF-TRUTH-FRESHNESS-001 and the
deliberation-protocol read contract), not a new capability. No policy/
architecture sign-off and no destructive/deploy action are involved.

## Problem / Background

On a ChromaDB version bump the prior on-disk HNSW segment becomes incompatible
(1.5.9), and semantic queries error ("Failed to apply logs to the hnsw segment
writer" / "Error querying knn") or hang. search_deliberations
(db.py:8463) wraps the query in _call_with_timeout: a hang is bounded by
_CHROMA_QUERY_TIMEOUT_SECONDS and the TimeoutError branch breaks without retry
(db.py:8513). But the generic-exception branch (db.py:8514-8522) `continue`s,
retrying the same doomed query - on a stale/incompatible segment each retry
fails identically and each spawns another bounded-but-abandoned query attempt,
amplifying the pileup. Separately, --semantic-only (cli.py:5471-5493) filters to
semantic rows and, on degradation, prints "No deliberations match" with exit 0,
silently masking that the mandatory governance search degraded to LIKE.

## Proposed Change

1. db.py search_deliberations - stale-format fast-fail: in the generic-exception
   branch, classify the error. For a stale-format / incompatible-segment error
   (matched by a conservative message signature such as "hnsw segment" /
   "Error querying knn" / "Failed to apply logs"), set seen_delib_ids={} and
   BREAK (no retry), mirroring the timeout branch's "a stalled store will stall
   again" rationale. Retain `continue` (retry) only for other (potentially
   transient) errors. The always-on SQLite LIKE pass continues to run, so search
   still returns results.
2. db.py search_deliberations - degradation signal: record per call whether the
   semantic pass DEGRADED (timed out or errored -> LIKE-only) versus SUCCEEDED
   (ran, even with zero matches), via a per-call status the CLI can read. The
   list[dict] return type is unchanged for all existing callers.
3. cli.py deliberations_search - fail closed: when --semantic-only is set and
   ChromaDB is expected (HAS_CHROMADB true) but the per-call status reports the
   semantic pass degraded, raise SystemExit(non-zero) with a clear degradation
   message instead of printing "No deliberations match" and exiting 0.

target_paths: ["./groundtruth-kb/src/groundtruth_kb/db.py", "./groundtruth-kb/src/groundtruth_kb/cli.py", "./platform_tests/scripts/test_deliberation_search_stale_segment.py"]

## Verification Plan (spec-derived)

- Stale-format fast-fail (GOV-SOURCE-OF-TRUTH-FRESHNESS-001) -> test: with a
  stubbed collection whose query raises a stale-format error, search_deliberations
  attempts the semantic query exactly ONCE (no retry), falls back to LIKE, and
  returns LIKE results; a transient-error stub still retries.
- Degradation signal -> test: the per-call status reports degraded=True after a
  timeout/stale-format error and degraded=False after a successful semantic pass
  (including a successful pass with zero matches).
- Fail-closed (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) -> test: invoking
  the search command with --semantic-only when the semantic pass degraded exits
  non-zero with a degradation message; a successful semantic pass with zero
  matches still exits 0 (genuine no-match is not a degradation).
- Optional-dependency matrix -> test: behavior is correct whether or not
  ChromaDB is installed (HAS_CHROMADB true/false).
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_deliberation_search_stale_segment.py -q ; plus ruff
  check and ruff format --check on the changed files.

## Risk / Rollback

- Risk: the stale-format message signature is too broad and suppresses retry for
  a transient error. Mitigation: the signature is conservative (specific HNSW/
  knn phrases); other errors keep the existing retry; the LIKE fallback always
  runs, so worst case is one fewer retry, never a lost result.
- Risk: fail-closed breaks a workflow that relied on --semantic-only silently
  returning []. Mitigation: that silent-empty behavior IS the defect; the new
  exit is loud-on-degradation only, and a genuine zero-match semantic pass still
  exits 0.
- Rollback: revert the two source edits and remove the test. No data migration;
  no on-disk index or segment files are touched (this slice is non-destructive).
- Blast radius: two localized edits on the deliberation-search read path plus one
  test; no schema change, no index mutation, no process management.

## Owner-Decision Item (flagged, NOT in this slice)

The full lock-holder-pileup root cause is the abandoned daemon-thread / native
HNSW handle that stays open after the Python-side timeout, plus stale on-disk
segment files that a rebuild cannot replace in place. Clearing those requires
DESTRUCTIVE recovery (deleting .groundtruth-chroma segment files and/or
reaping index-holding threads/processes), which is a destructive recovery-policy
choice. It is deliberately excluded here and should be raised to the owner as a
separate decision in a follow-on slice; this slice does not perform or authorize
any destructive recovery.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

- origin = defect (not new)
- no new public API/CLI surface; the --semantic-only behavior change is the
  defect removal itself (silent degradation -> fail closed)
- no new or revised requirement or specification
- small, single-concern: two existing source files (db.py, cli.py) plus one new
  test, well under 150 net lines

WI-4568 is an active member of PROJECT-GTKB-RELIABILITY-FIXES and is covered by
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership.

## Recommended Commit Type

`fix:` - repairs broken behavior (doomed-query retry amplification + silent
semantic degradation) on the deliberation-search read path; the accompanying
test is verification for the fix.
