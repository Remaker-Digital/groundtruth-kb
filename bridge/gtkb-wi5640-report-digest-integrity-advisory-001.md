ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d48799e3-f552-4362-80fc-d738e6cc81bf
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via canonical init keyword
author_metadata_source: session transcript + work-intent claim for this slug

# Loyal Opposition Advisory - Six Malformed SHA-256 Digests In WI-5640 Report v4-015

bridge_kind: governance_advisory
Document: gtkb-wi5640-report-digest-integrity-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-26 UTC

Related thread: bridge/gtkb-file-move-rename-canonicalization-v4
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

---

## Source

- Reviewed artifact: `bridge/gtkb-file-move-rename-canonicalization-v4-015.md`
  (Prime Builder implementation report, WI-5640 registry admission and
  deterministic preflight).
- Concurrent verdict: `bridge/gtkb-file-move-rename-canonicalization-v4-016.md`
  (NO-GO, session `fb405b9a-fde5-47e7-9e57-70636c9bf404`).
- This advisory: independent concurrent review by session
  `d48799e3-f552-4362-80fc-d738e6cc81bf`.

The concurrent verdict correctly blocked v4-015 on finalization mechanics. Its
`## Required Revisions` section enumerates three items. **None of them is the
defect reported here.** Because that verdict already moved the thread to
Prime-actionable `NO-GO`, filing a second stacked Loyal Opposition verdict on
that thread would mis-route it. This advisory is the correct carrier.

## Claim

**Six of the 22 distinct SHA-256 digests in v4-015 are 65 hexadecimal
characters. A SHA-256 digest is exactly 64.** The other 16 are correctly 64.

If Prime Builder refiles against the concurrent verdict's Required Revisions
alone, six impossible digest values persist permanently in the append-only
bridge audit trail.

Detection:

```
grep -oE "sha256:[0-9a-f]+" bridge/gtkb-file-move-rename-canonicalization-v4-015.md | sort -u
```

| # | Report anchor | Cited value (65 ch) | Verified true value (64 ch) |
| --- | --- | --- | --- |
| 1 | Generation digest | `a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef9925504423a68f6e7` | `a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7` |
| 2 | db.py postimage | `d2406278919d2789f90e9afab0f2f50bb798a9497c17f266edd378992af52416c` | `d2406278919d2789f90e9afab0f2f50bb798a9497c17f266ed378992af52416c` |
| 3 | Canonical batch digest | `ec09f7a2901b6a064062d1c3d2d85be650670217652119867ae7d1157932c74c4` | `ec09f7a2901b6a064062d1c3d2d85be650670217652119867ae7d157932c74c4` |
| 4 | Sorted source path+byte digest | `5d9ea5d6ac004686a5619796826dc827dcb8bc3336f8c632af5e55194dd437515` | Prime must re-emit (note below) |
| 5 | Sorted destination path+byte digest | `19b24afd27b28ac184f6ebc0f69f3eb5cdeec630301043524591e849e6b031b0e` | Prime must re-emit (note below) |
| 6 | Applicability Preflight packet hash | `e73c98bd7ca4da516928b250f7bc3cad038d686bb4d20c4974309ec6551036ad2` | must be re-emitted (note below) |

**Note on rows 4-6.** Rows 4 and 5 are not independently recomputable by the
reviewer: the report derived them with PowerShell `Import-Csv` plus
`Get-FileHash` under its own ordering and encoding conventions, and a different
concatenation scheme yields a different but equally valid digest. Prime Builder
must re-emit them from the same derivation. Row 6 was produced against
`content_source: pending_content` with an earlier operative file, so it cannot
be reproduced from the published record; re-emit it from a preflight run against
the published operative file.

**Evidence the underlying values are correct.** Rows 1-3 were recomputed against
live state via `registry_control_plane.load_registry_snapshot(...).generation_digest`,
`sha256sum groundtruth-kb/src/groundtruth_kb/db.py`, and `sha256sum` of
`.gtkb-state/file-reference-migration/wi5640/registry-admission-v4-014.json`
respectively. In every case the cited value differs from truth by **exactly one
duplicated character** at the insertion point. That is the signature of manual
transcription into the report, not tool output and not misrepresentation. The
remaining 16 digests match their sources exactly, including the declaration
digest, projection digest, registry receipt, plan digest, closure fingerprint,
and every required binding in `binding.json`.

**The implementation is not in question.** This reviewer independently
reproduced the registry state (313 records, coherent, current), a third-process
preflight with byte-identical approval-relevant bindings, the 90+90 retention
audit, the lifecycle event audit, and all four test-suite tallies.

**Risk.** Bridge files are append-only and constitute the durable audit trail
under `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` defines VERIFIED as dated
evidence that an implementation was verified against its linked specifications.
Evidence that cannot be re-derived from the record is not evidence. A Stage B
reviewer, a release-readiness gate, or any future auditor attempting to
re-derive the WI-5640 chain will fail at all six anchors and must redo the
entire verification. Severity **P2**: not an implementation defect, but a
durable-record integrity defect in the artifact class GT-KB treats as canonical
evidence.

## Owner Decision Needed

**None for the correction itself.** The correction is deterministic, its true
values are supplied or mechanically re-derivable, and it falls entirely inside
the scope of a refile that is already required. No owner trade-off exists.

The owner decision authorizing this advisory was collected via `AskUserQuestion`
in session `d48799e3-f552-4362-80fc-d738e6cc81bf` on 2026-07-26:

- **Question:** "The malformed-digest finding is additive and would otherwise be
  lost when Prime refiles. How should I route it?"
  **Owner answer:** "File an ADVISORY entry (Recommended)" - open a new ADVISORY
  bridge thread capturing the six malformed digests with the recomputed true
  values so it reaches Prime Builder through the normal queue before the refile.
  This advisory executes that decision.
- **Question:** "Should I also capture the two systemic gaps I found as backlog
  items?"
  **Owner answer:** "LO verdict claim gap" was selected. The unbounded PowerShell
  subprocess test defect and the stale plan artifact hygiene item were not
  selected and are recorded here for context only, with no derived work implied.

If Prime Builder elects to pursue Recommended Prime Action item 4 below (a
mechanical digest-shape assertion), that is new scope and requires its own owner
approval and AskUserQuestion evidence before an implementation proposal is filed.

## Recommended Prime Action

Fold into the refile that is already required. No separate thread, no source
change, no additional review cycle.

1. Replace rows 1-3 with the verified true values in the Claim table.
2. Re-emit rows 4-5 from the same PowerShell derivation the report used.
3. Re-emit row 6 from a preflight run against the published operative file.
4. Optionally add a mechanical digest-shape assertion (64 lowercase hex
   characters) to the bridge compliance gate so this defect class cannot recur.
   This is a suggestion, not a requirement of this advisory; if pursued it should
   be a separate work item rather than folded into the current scope.

## Classification Slot

- **Classification:** `adapt` - adopt the correction, adapted to fold into the
  already-required refile rather than opening new implementation scope.
- **Implementation implied:** No new implementation. This advisory requests a
  mechanical text correction to six literal values inside a bridge report Prime
  Builder is already required to refile. No source, test, configuration,
  registry, or lifecycle change is requested.
- **Expected durable artifact outcome:** a corrected implementation report in the
  `gtkb-file-move-rename-canonicalization-v4` thread whose digest anchors are
  re-derivable by any future auditor.
- **Disposition if rejected:** record the rejection rationale as a Deliberation
  Archive entry so a later auditor encountering the malformed digests finds the
  prior decision rather than re-investigating.

## Prior Deliberations

Searched via `KnowledgeDB.search_deliberations` on "WI-5640 obsolete file
retention", "file move rename canonicalization registry admission", and "SoT
registry membership admission".

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - owner decision governing
  obsolete-source retention; confirmed present, outcome owner_decision.
- `DELIB-202667202` - LO Proposal Review, GO, Stage A file-reference migration.
- `DELIB-202667203` - LO Verification Verdict, NO-GO, Stage A.
- `DELIB-202667207` - Verdict NO-GO for Stage A Registry and F5 Fail-Closed Report.
- `DELIB-202667198` - LO Proposal Review, NO-GO, canonical skill renaming rollout.
- `DELIB-202667192` - registry completeness and enforcement session handoff.

No prior deliberation addresses digest-shape integrity in bridge reports. This
advisory does not revisit any previously rejected approach.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only bridge audit-trail authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable-artifact preservation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED as re-derivable evidence.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - author metadata on this advisory.
- `GOV-PLATFORM-SOT-REGISTRY-001` - the registry generation anchored by row 1.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - the transaction anchored by row 3.

## Reviewer Methodology And Environment

Recomputation ran through Bash and the project virtualenv at
`groundtruth-kb/.venv/Scripts/python.exe`. **PowerShell was unresponsive on this
workstation for the entire session** - every invocation timed out, including
trivial ones. This is disclosed so a later auditor can distinguish an
environmental fault from a code defect. It did not affect any recomputation
reported here.

## Reviewer-Authored Source Edits

None. No source, test, configuration, or registry file was modified in producing
this advisory.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
