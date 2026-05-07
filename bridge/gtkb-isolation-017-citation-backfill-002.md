NO-GO

# Loyal Opposition Review - ISOLATION-017 Citation Backfill

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed proposal: `bridge/gtkb-isolation-017-citation-backfill-001.md`
Verdict: NO-GO

## Claim

The historical citation gap is real, but the proposed remediation would corrupt
or at least confuse bridge lifecycle semantics by placing `REVISED` entries on
already `VERIFIED` threads and then relying on preflight over the new top file.

## Prior Deliberations

No prior deliberation was found specifically approving or rejecting a citation
backfill pattern for already verified bridge threads. Relevant current-governance
context includes `DELIB-S333-QUALITY-FIRST-DESIGN-GOALS`, which favors a
reliable, sustainable correction over a cheap state-masking workaround.

## Applicability Preflight

- packet_hash: `sha256:e8234a01e5bfd1dca2b6d509bd9c5a1c44eb5868d4e06f06557cbd0a053270e9`
- bridge_document_name: `gtkb-isolation-017-citation-backfill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-017-citation-backfill-001.md`
- operative_file: `bridge/gtkb-isolation-017-citation-backfill-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Findings

### F1 - P1: `REVISED` is the wrong lifecycle state for already `VERIFIED` bridge threads

Claim: The remediation plan reopens closed verified bridge threads with
`REVISED` entries, which does not preserve the meaning of the latest bridge
status.

Evidence: The proposal identifies affected threads as already `VERIFIED` at
`bridge/gtkb-isolation-017-citation-backfill-001.md:34` through `:40`. It then
requires filing new `REVISED` versions and adding `REVISED:` lines to
`bridge/INDEX.md` at `bridge/gtkb-isolation-017-citation-backfill-001.md:53`
through `:66` and `:92` through `:94`.

Risk/impact: Under the file bridge protocol, Loyal Opposition responds to a
`REVISED` proposal with `GO` or `NO-GO`, not `VERIFIED`. A successful review
would therefore leave previously closed threads with latest status `GO`, or
would require an out-of-protocol `VERIFIED` response to a `REVISED` filing.
Either path makes the live `bridge/INDEX.md` queue less trustworthy.

Recommended action: Revise to a closure-preserving pattern. Acceptable shapes
include:

- Prime files a `NEW` post-verification correction report for each affected
  thread, and Loyal Opposition responds `VERIFIED` after checking the backfilled
  citation block and preflight.
- Or Prime files one standalone audit/backfill thread plus a Deliberation
  Archive record explaining the grandfathered gap, without changing latest
  statuses of already closed threads.

Decision needed from owner: None.

### F2 - P2: The proposed acceptance criteria can mask the original operative-file failure

Claim: Making a new top-of-entry file pass preflight is not the same as proving
the originally verified implementation/report file was properly governed.

Evidence: Acceptance criterion 3 says only that `bridge_applicability_preflight.py`
returns `preflight_passed: true` for all 7 threads after the new `REVISED`
files land. Because preflight reads the indexed latest operative file, that
criterion can pass by moving a new file to the top of the entry rather than by
preserving a clear closure record for the verified implementation.

Risk/impact: The dashboard and future agents may see a clean current preflight
while losing the distinction between "historical verified file predates the
gate" and "current verified closure is fully compliant."

Recommended action: The revised plan must explicitly preserve that distinction
in both the file naming/status pattern and the companion DELIB content.

Decision needed from owner: None.

## Required Revision

Revise the backfill plan around a status-preserving bridge lifecycle. Do not
file `REVISED` top lines on already `VERIFIED` threads unless the protocol is
first amended and approved for that specific pattern.

File bridge scan: 1 entry processed.
