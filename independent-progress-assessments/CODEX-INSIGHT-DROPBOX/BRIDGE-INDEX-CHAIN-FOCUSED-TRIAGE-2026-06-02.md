# Bridge INDEX Chain Focused Triage

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, GOV-STANDING-BACKLOG-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
WIs: WI-4235, WI-4236, WI-4237, WI-4238

Session type: Loyal Opposition read-only bridge reconciliation triage
Reviewer: Codex / Loyal Opposition
Generated: 2026-06-02T17:15:00Z

## Claim

The read-only bridge INDEX/file-chain detector reports 3,900 findings, but
3,871 are the broad `versioned_bridge_file_unindexed` class. The remaining 29
findings are small enough for a focused correction packet. They should be split
into detector-normalization fixes and actual bridge correction candidates before
Prime Builder files any mutation proposal.

## Evidence

- Command:
  `python -m groundtruth_kb bridge reconcile index-chain --json`
- Counts by type:
  - `versioned_bridge_file_unindexed`: 3,871
  - `document_header_mismatch`: 17
  - `responds_to_mismatch`: 10
  - `index_status_body_mismatch`: 1
  - `missing_intermediate_versions`: 1
- No files, bridge entries, backlog rows, project rows, or deliberations were
  modified by this triage.

## Triage

### Detector-Normalization Candidates

Most `document_header_mismatch` rows are not substantive identity defects. The
affected files use Markdown code spans in their header, for example
`Document: `slug`` while `bridge/INDEX.md` records `Document: slug`. The
detector currently compares the raw string instead of normalizing code-span
backticks.

Examples:

- `bridge/gtkb-bridge-target-paths-kb-mutation-check-002.md`
- `bridge/gtkb-core-spec-intake-default-004.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-002.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-002.md`
- `bridge/gtkb-s358-w4-enforcement-calibration-002.md`
- `bridge/gtkb-s358-w5-token-framing-correction-002.md`

Recommended action: update the detector normalization so `Document: `slug``
and `Document: slug` compare equal. Do not mutate historical bridge files for
these rows unless Prime Builder separately decides the header style itself
should be standardized.

### Bridge Correction Candidates

These rows are more likely to need correction packets or explicit waiver notes:

| Type | Subject | Evidence | Suggested handling |
| --- | --- | --- | --- |
| `document_header_mismatch` | `gtkb-bridge-poller-001-smart-poller` | `bridge/gtkb-bridge-poller-001-smart-poller-001.md` contains `Document: <kebab-case-name>` inside proposal example text. | Confirm whether the detector should ignore fenced/example/template sections, or file a narrow historical-header correction. |
| `index_status_body_mismatch` | `gtkb-proposal-standards-test-claim-rerun-verifier` | `bridge/INDEX.md` records `REVISED` for `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-016.md`, but the body status token is `NEW`. | Real correction candidate: either INDEX should be `NEW` for an implementation report, or the body token should be corrected through a governed historical artifact packet. |
| `missing_intermediate_versions` | `gtkb-gov-proposal-standards-slice1` | Disk has `001`-`009` and `021`-`027`; versions `010`-`020` are absent from disk and not indexed. | Investigate git history before mutation; classify as historical deletion, parked-draft numbering gap, or artifact loss. |
| `responds_to_mismatch` | `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint` | `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-007.md` has an empty `Responds to:` field. | Real correction candidate if the verdict/report depends on a prior version reference. |

### Responds-To Heuristic Candidates

The other `responds_to_mismatch` findings may be legitimate deviations or
detector false positives. Several intentionally skip over an intermediate
version or respond to a self-detected clause-preflight gap rather than a normal
previous file path.

Affected subjects:

- `gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive`
- `gtkb-claude-md-scope-clarification-slice-3-implementation`
- `gtkb-hygiene-sweep-cli-scoping`
- `gtkb-hygiene-sweep-skill-scoping`
- `gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table`
- `gtkb-lo-hygiene-assessment-skill-build`
- `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`

Recommended action: before editing any bridge file, Prime Builder should decide
whether the detector should accept corrective verdicts that intentionally
respond to an earlier version and revision reports that cite prose such as
`self-detected clause-preflight gap on -001`.

## Risk / Impact

Treating the 29 findings as one homogeneous defect would cause unnecessary
historical artifact edits. The useful path is to first harden detector
normalization, then generate one governed correction packet for the few rows
that remain after normalization and heuristic refinements.

## Recommended Action

Prime Builder should make `WI-4235` consume this triage before implementation.
The first implementation slice should improve detector normalization and
classification, then rerun the detector to produce a smaller correction packet.

## Decision Needed From Owner

None for this Loyal Opposition triage. Future correction proposals should ask
one concrete owner decision only if they propose mutating historical bridge
files or `bridge/INDEX.md`.
