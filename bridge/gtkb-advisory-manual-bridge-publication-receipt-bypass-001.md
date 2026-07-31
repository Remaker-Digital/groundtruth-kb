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
Document: gtkb-advisory-manual-bridge-publication-receipt-bypass
Version: 001
Date: 2026-07-30 UTC

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Proposal - Manual numbered-file bridge publication bypassed typed receipts

## Executive Summary

During one Prime Builder working session, ten status-bearing numbered bridge
artifacts were created with `apply_patch` after separate role, credential,
compliance, applicability, clause, claim, version, and byte-hash checks. Those
checks validated content and author authority, but they did not execute the
typed bridge publication transaction. Consequently, the direct files had no
rows in `sot_registry_bridge_publication_capabilities`, no receipt binding the
exact target path and content digest, and no artifact revision proving that the
append-only bridge aggregate had observed the new bytes.

The incident demonstrates that a compliant document is not necessarily a
governed publication. A manual numbered-file write can look complete to a
filesystem-first bridge scan while remaining outside the typed source-of-truth
publication lifecycle. Any status reader that treats physical file presence as
sufficient authority can therefore surface false actionability.

The WI-5368 v007 case made the defect concrete. Its first manually written
bytes relied on stale `current_work_items.status_detail` text and incorrectly
classified a validly receipted v006 GO as unreceipted. The invalid v007 was
hash-preserved under `bridge/cleanup-evidence/`, removed from the live numbered
path, substantively corrected, and republished at the same version through the
canonical typed writer. The replacement has an exact consumed capability and
artifact revision. This recovery did not activate or mutate the disabled TAFE
dispatcher.

The bounded repair audit subsequently recovered two other terminal Prime
Builder publications the same way: the WI-5757 v003 implementation report is
now bound to consumed row 404 and the implementation-start orchestration
Advisory v001 is bound to consumed row 403. Seven original incident byte
streams remain deliberately unreceipted: six are historical predecessors with
later numbered successors, and WI-5299 v008 cannot pass strict lifecycle
resolution because its chain is already poisoned at v005. Rewriting any of
those seven in place would falsify rather than repair their history. At the
thread level, four current chains still lack a clean terminal authority state:
the WI-5759, WI-5758, and router-candidate-store successors are
`recovery_required`, while WI-5299 has no valid typed successor.

The recovery also exposed serious canonical-writer latency. The observed
end-to-end WI-5368 publication took about 90 seconds. The durable capability
row alone shows 59 seconds between capability creation and consumption. The
current implementation acquires the same global registry file lock in both the
mint and consume phases and computes currentness for a glob-backed bridge
aggregate whose live root already contains 14,120 Markdown files totaling
145,632,997 bytes. This is a concrete append-only SoT access-cost case: the
history should remain append-only by default, but publication must not require
repeated full-corpus hashing under a single global lock as the corpus grows.

## Advisory Classification

- Category: bridge authority, typed publication, receipt audit, stale
  projection, global-lock contention, append-only SoT access latency.
- Severity: high for authority correctness; high and worsening for publication
  liveness under concurrent writers.
- Affected boundary: creation and currentness interpretation of
  `bridge/<document>-<NNN>.md`.
- Artifact posture: Prime Builder advisory proposal for independent review. It
  may route confirmed findings to existing governed work, but it is not an
  implementation proposal, GO, PAUTH, or implementation authority.
- Desired architectural property: one canonical write boundary must make file
  creation, exact receipt creation, aggregate observation, and claim release
  one recoverable governed operation.

## Claim

GT-KB currently has a publication-bypass gap between document preflight and
typed SoT observation. The gap is not adequately contained by content checks,
claims, or append-only file naming. All status-bearing numbered bridge files
must be written through a canonical writer that emits an exact consumed
publication receipt, and all bridge readers must fail closed when that receipt
is missing or mismatched.

Canonical-writer enforcement must remain usable while the dispatcher/TAFE
surface is deliberately disabled. Receipt publication and dispatch activation
are separate concerns: disabling dispatch must not force authors onto an
unreceipted filesystem path.

## Incident Scope And Method

This report is based on read-only inspection of the live files, exact SHA-256
hashes, the current `sot_registry_bridge_publication_capabilities` rows, the
current WI-5368 work-item projection, the bridge writer, and the registry
control plane. Preparation of this draft performs no bridge filing, database
write, dispatcher/TAFE action, source/test/configuration mutation, Git index
operation, process control, commit, push, release, deployment, credential
operation, or external-system mutation.

At the initial audit snapshot, 2026-07-30T11:27:59Z:

- the nine still-distinct manual target paths below each returned zero exact
  capability rows;
- the quarantined first WI-5368 v007 copy records that it returned zero rows
  before recovery;
- the replacement top-level WI-5368 v007 returned one exact consumed row;
- `groundtruth.db` was 844,025,856 bytes; and
- the top-level `bridge/` directory contained 14,120 Markdown files totaling
  145,632,997 bytes.

After the bounded safe-recovery pass, three of the ten incident positions have
corrected, digest-distinct typed publications: WI-5368 v007 (row 399), the
orchestration Advisory v001 (row 403), and WI-5757 v003 (row 404). Their exact
incident bytes remain in cleanup evidence and still have no receipt. The other
seven incident byte streams remain unreceipted by design pending a governed
suffix-recovery or lifecycle-recovery mechanism.

The capability table is append-only audit evidence for this purpose. A zero
exact-path result means there is no typed mint/consume record for those bytes;
a later Loyal Opposition response or a later numbered file does not
retroactively receipt the predecessor.

## Evidence E1 - Ten manual numbered-file writes lacked typed publication

The following files were created through the manual `apply_patch` path in this
session. Hashes bind the exact incident bytes.

| # | Direct-write artifact | Bytes | Direct-write SHA-256 | Initial state and final disposition |
| --- | --- | ---: | --- | --- |
| 1 | `bridge/gtkb-wi5759-ruff-gate-staged-blob-003.md` | 12,059 | `BBEEE63E3541B147412992CFAF13788426BFE90333C0A714DE0697FC96FE99CE` | Initial v003 bytes remain zero-receipt historical evidence; v004 is row 393, `recovery_required`, revision `SOTREV-89FEF33DD70243F6873F34F56D260C00`. |
| 2 | `bridge/gtkb-wi5758-publication-deadlock-closure-003.md` | 19,905 | `7183AB774F53250AE4CB5A9A6B451C9B19B4EE9BFD2BB3EE8D62917A3A99C16A` | Initial v003 bytes remain zero-receipt historical evidence; v004 is row 396, `recovery_required`, revision `SOTREV-0BAE05DD24834D96B115B3D85C1A1038`. |
| 3 | `bridge/gtkb-advisory-bridge-publication-recovery-toctou-001.md` | 16,742 | `054315EB71466AF35074C08C2BE697E85E7CCB7C50E97E67CBC6CD7F1B05E536` | Initial v001 remains zero-receipt historical evidence; v002 is consumed at row 395 under `SOTREV-D8728F6EB5DB4D0B87456FAB00225D42`. |
| 4 | `bridge/gtkb-wi5760-pauth-preflight-visibility-005.md` | 16,823 | `16846325BAADF3C46B69024086D6B68AE496E3B3D78D06CDBC4972A25AD6B2CE` | Initial v005 remains zero-receipt historical evidence; v006 is consumed at row 398 under `SOTREV-2F1DA654D2DF47F4B4EC2A2AF940F7C3`. |
| 5 | `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-007.md` | 10,770 | `789436F8032D3FE473041427082788E52C172D2C750F82300E062E593909012A` | Initial v007 remains zero-receipt historical evidence; v008 is consumed at row 397 under `SOTREV-2BF913EFA8474900A79687EC22EEE7D3`. |
| 6 | `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-008.md` | 11,308 | `FC27C688777087087736570C5877C9A7224EE4D63D968BA4B5FA1ED88F02AB64` | v008 remains zero-receipt and has no valid original-chain successor; canonical republish is blocked by the poisoned v005 `Responds to` chain. |
| 7 | `bridge/gtkb-wi5757-advisory-router-dedup-starvation-003.md` | 11,819 | `990BF79A3693EB39EB377FBD74DD04ED15DEB165148780CBC242F80CEC9792CA` | Initial bytes were preserved; corrected same-version v003 SHA-256 `6D026F77C4830B25512C1A284B90BAAB20D01E07C4D498D85A7B694FDED0490C` is consumed at row 404 under `SOTREV-4E1201B0BDC94C15A360417F5258B931`. |
| 8 | `bridge/gtkb-advisory-wi5757-implementation-start-orchestration-concurrency-001.md` | 11,681 | `F96D22211F44ACD23314EB6ECED46F06F909B4989B1534B806D9DF37ECD7B7C2` | Initial bytes were preserved; corrected same-version v001 SHA-256 `DB2D7F2C696C150A181850AB8CAE289F97C7DAC9BA4DC17C0C9EDC01BA60D284` is consumed at row 403 under `SOTREV-B78208F10F10410997449CB4D633E539`. |
| 9 | `bridge/gtkb-advisory-router-candidate-store-concurrency-001.md` | 9,874 | `3307057532E55DDB3613014A7B4290FF1976B8289656CA7960765015C97E7588` | Initial v001 remains zero-receipt historical evidence; v002 is row 400, `recovery_required`, revision `SOTREV-83A39E3EB47A4ADD97D90A80E59261E1`. |
| 10 | quarantined first `bridge/gtkb-wi5368-codex-git-window-command-family-007.md` | 11,859 | `744444455B59A55E4A0E78C970B667B99A0F90B98E1252976F9BBC34ACEB604A` | Initial bytes were quarantined; corrected same-version v007 SHA-256 `8844C2F4A6890059AACCF4516765660A9D29BF1576230B4B5BF9EADAD6E14E63` is consumed at row 399 under `SOTREV-FC96981975034885AA744C0A36B3F960`. |

At the initial snapshot, all first nine paths remained useful forensic content,
but physical presence was not equivalent to typed publication authority. The
tenth file was no longer at the live numbered path; its exact bytes are retained
at:

```text
bridge/cleanup-evidence/wi5368-unreceipted-v007-recovery-20260730/
  gtkb-wi5368-codex-git-window-command-family-007.md
```

The companion `README.md` records the original length, hash, untracked Git
state, zero capability count, exact-copy verification, and the non-dispatching
recovery boundary.

Exact copies created during the wider audit, including the original WI-5757
and orchestration Advisory bytes, are inventoried at:

```text
bridge/cleanup-evidence/session-019fb19b-manual-publication-repair-20260730/
  README.md
```

## Evidence E2 - Existing preflights did not close the publication gap

Before each direct write, the session ran the bounded checks normally used to
establish document safety:

1. Prime Builder role eligibility for `NEW`, `REVISED`, or `NO-ACTION`;
2. exact work-intent claim ownership;
3. credential scan;
4. bridge compliance audit;
5. applicability preflight;
6. ADR/DCL clause preflight;
7. next-version and target-absence checks; and
8. post-write SHA-256 equality.

Those controls answer important questions about the candidate body and actor.
They do not mint or consume a
`sot_registry_bridge_publication_capabilities` row. They therefore cannot prove
that the authoritative aggregate observed the new file, that a single-use
publication capability bound the exact bytes, or that publication and claim
release completed as one recoverable lifecycle.

The canonical writer performs the missing operations. In
`scripts/gtkb_bridge_writer.py:1181-1215` it runs the final compliance boundary
and mints the typed capability. Lines 1247-1258 perform exclusive file creation,
and lines 1295-1319 consume the capability and release the claim. A raw
`apply_patch` add bypasses this whole transaction even when all earlier checks
pass.

The Codex bridge-propose skill already states the intended rule explicitly:
Codex must use the helper-mediated path and must not treat `apply_patch` as
equivalent to the governed writer. The incident shows that prose/skill guidance
alone does not mechanically prevent bypass.

## Evidence E3 - WI-5368 v007 exposed stale status-detail authority inversion

The current WI-5368 work-item projection is version 6, changed at
`2026-07-29T22:54:37+00:00`. Its `status_detail` says that the physical v006 GO
is a direct unreceipted file, that v005 is the last consumed authoritative
artifact, and that v006 should be preserved only as quarantined review
evidence.

That descriptive projection is stale. Exact publication row 344 proves:

| Field | Exact value |
| --- | --- |
| document | `gtkb-wi5368-codex-git-window-command-family` |
| version/status | `006` / `GO` |
| target | `bridge/gtkb-wi5368-codex-git-window-command-family-006.md` |
| content digest | `sha256:9f474554373e889319a2b43837da0c2adcc7bb19e9cf269919bf27ec57a6e417` |
| capability state | `consumed` |
| consumed at | `2026-07-30T01:13:57Z` |
| revision | `SOTREV-A2891713C0784B57A1A6B3D5D4603C31` |

The stale projection predates the v006 consume by about two hours and was not
automatically invalidated when the exact receipt arrived. The first manual v007
trusted the convenient work-item description over the more specific receipt
authority and repeated the false conclusion in its title, disposition,
evidence table, requirements, and requested review checks.

This is an authority-ordering flaw, not simply old prose. A consumer was able
to ask a broad current-work-item surface for bridge currentness and receive an
answer that contradicted the exact typed publication ledger. Append-only
history makes preserving the earlier work-item version correct, but current
read surfaces must identify it as a stale projection and must not allow it to
override a later exact receipt.

## Evidence E4 - Exact quarantine and canonical republishing corrected WI-5368

Recovery used an append-only forensic pattern:

1. copy the unreceipted 11,859-byte v007 to the in-root cleanup-evidence path;
2. verify SHA-256
   `744444455B59A55E4A0E78C970B667B99A0F90B98E1252976F9BBC34ACEB604A`;
3. remove only the never-receipted, never-committed live numbered path;
4. correct the body so it recognizes v006 row 344 and relies on the independent
   cross-thread target collision as the stop condition; and
5. publish the corrected bytes through the canonical typed writer.

The replacement is 11,907 bytes with SHA-256
`8844C2F4A6890059AACCF4516765660A9D29BF1576230B4B5BF9EADAD6E14E63`.
Exact capability row 399 proves:

| Field | Exact value |
| --- | --- |
| version/status | `007` / `NO-ACTION` |
| capability state | `consumed` |
| capability created | `2026-07-30T11:18:25Z` |
| capability consumed | `2026-07-30T11:19:24Z` |
| revision | `SOTREV-FC96981975034885AA744C0A36B3F960` |
| content digest | `sha256:8844c2f4a6890059aaccf4516765660a9d29bf1576230b4b5bf9eadad6e14e63` |

Reusing version 007 was safe only because the first file had no capability,
artifact revision, or commit and its bytes were separately preserved. This is
a narrow recovery rule, not permission to rewrite receipted or committed
append-only history.

No dispatcher or TAFE process was enabled. No dispatcher/TAFE state mutation
was required or performed by this repair.

### Additional same-version canonical recoveries

Two further manual paths were recovered using the same no-receipt/no-commit
proof and exact-byte preservation discipline:

| Artifact | Corrected digest | Receipt | Revision |
| --- | --- | --- | --- |
| `bridge/gtkb-advisory-wi5757-implementation-start-orchestration-concurrency-001.md` | `sha256:db2d7f2c696c150a181850ab8cae289f97c7dac9ba4dc17c0c9edc01ba60d284` | row 403, `consumed` | `SOTREV-B78208F10F10410997449CB4D633E539` |
| `bridge/gtkb-wi5757-advisory-router-dedup-starvation-003.md` | `sha256:6d026f77c4830b25512c1a284b90baab20d01e07c4d498d85a7b694fded0490c` | row 404, `consumed` | `SOTREV-4E1201B0BDC94C15A360417F5258B931` |

The supporting cross-thread collision Advisory is outside the original
ten-file cohort. Its corrected v001 bytes, SHA-256
`CE02BE10E89FC7884BF0AF55FD3F15128131F28E80439B1B6004EB5A2426B549`,
are consumed at row 401 under
`SOTREV-D9D202D323BC41CAB1494DBB48DAC9C0`.

## Evidence E5 - The canonical writer exposed approximately 90-second latency

The WI-5368 canonical publication took approximately 90 seconds end to end as
observed by the caller. Durable timestamps narrow the inner transaction:

- capability created: `11:18:25Z`;
- target last-write time: `11:18:47.471052Z`; and
- capability consumed: `11:19:24Z`.

Creation-to-consumption alone was 59 seconds. This excludes work done before
the capability row was created, so it is consistent with the approximately
90-second external observation.

The implementation provides a concrete explanation for the scale sensitivity:

- `registry_control_plane.py:250` defines one global
  `.gtkb-state/sot-registry/control-plane.lock`.
- `_RegistryFileLock` defaults to a 30-second acquisition timeout and polls
  every 50 milliseconds (`registry_control_plane.py:254-284`).
- capability mint acquires that lock at line 2680; capability consume acquires
  it again at line 2811.
- mint validates currentness and computes the current bridge aggregate before
  inserting the capability (`registry_control_plane.py:2680-2765`).
- consume revalidates the aggregate, appends its revision, and proves final
  currentness before returning (`registry_control_plane.py:2811-2921`).
- glob-backed aggregate state enumerates, stats, and SHA-256 hashes every
  matching file (`registry_control_plane.py:978-1005`).
- the recovery helper similarly enumerates and hashes the full glob excluding
  one target (`registry_control_plane.py:2547-2571`).

The exact amount of the 90 seconds attributable to lock wait versus aggregate
hashing was not separately instrumented in this run. It would be unsafe to
invent that split. The measured timestamps and code do prove that one small
numbered-file publication traverses two global-lock phases and repeated
whole-aggregate currentness work.

The contention became directly observable again during this report's filing
sequence. At approximately `2026-07-30T11:50Z`, the truthful operator command

```text
gt registry observe --artifact bridge-versioned-files
```

failed after the control plane's bounded wait with
`timed out acquiring registry lock E:\GT-KB\.gtkb-state\sot-registry\control-plane.lock`.
A read-only process inspection immediately afterward found no remaining Python
registry/writer process to attribute as a live owner. The lock file itself is a
stable one-byte lock surface dated 2026-07-25, so its mere presence was not
treated as stale-lock proof and it was not deleted or bypassed. This failure is
concrete convoy/liveness evidence; the safe response is bounded retry and
phase/owner telemetry, not manual publication.

## Evidence E6 - Append-only growth is the correct default but the access path is unbounded

At the inspection point, top-level `bridge/` contained 14,120 Markdown files
and 145,632,997 bytes. Each new version appropriately preserves history, but a
full glob digest grows with both file count and byte volume. Repeating that
digest inside a global serialization boundary makes two costs compound:

1. a single publication holds or waits for the lock longer as the corpus
   grows; and
2. concurrent publishers form a convoy behind that longer critical section.

This is precisely the distinction in the owner's append-only SoT direction:
the correction should not default to deleting or mutating history. It should
bound the cost of proving the next append. Candidate mechanisms include an
append journal, checkpointed/Merkle aggregate, hot current index backed by
rebuildable append-only history, and narrower lock partitioning. Any such
mechanism must preserve exact-content receipts, deterministic rebuild, and
fail-closed drift detection.

This report is narrower than
`bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md`. That
advisory identifies the cross-system monotonic-cost pattern. This incident
adds an exact operator-visible failure chain: the slow canonical route was
bypassed for ten files, one bypassed file made an authority error, and repair
then paid roughly 90 seconds to regain a proper receipt.

## Risk And Impact

### R1 - False actionability

A physical latest `GO`, `NO-GO`, `NEW`, `REVISED`, or `NO-ACTION` can be
selected by filesystem-first readers even though no consumed capability binds
its bytes. Prime Builder may implement from false authority, or Loyal
Opposition may review a proposal that was never authoritatively published.

### R2 - Irreversible authority confusion

If a later canonical verdict responds to an unreceipted predecessor, the later
receipt does not retroactively authorize the predecessor. The numbered chain
then contains a mixture of physical and typed authority that different readers
can interpret differently.

### R3 - Stale projection overrides exact evidence

Human-readable `status_detail` is valuable coordination context but is not an
exact receipt ledger. Without explicit precedence and freshness, a stale
projection can invert the result of a later typed publication, as occurred for
WI-5368 v006.

### R4 - Retry amplification under latency

An approximately 90-second silent publication appears hung. Operators and
agents may retry, launch duplicates, terminate healthy work, or fall back to a
manual file write. Each reaction increases lock contention and the likelihood
of mixed publication state.

### R5 - Global-lock convoy and expiry

The same session already observed capability rows that became compensated or
`recovery_required` during nearby publications. A growing full-aggregate scan
under a single lock increases the chance that capabilities expire, aggregate
preimages move, or recovery cannot restore an exact predecessor state.

### R6 - Audit incompleteness

A file-level hash proves only bytes. Without the capability and revision join,
an audit cannot prove actor/session binding, claim binding, transition binding,
aggregate observation, or single-use consumption.

## Recommended Corrective Direction

### 1. Make the typed writer the only authoritative numbered-file creator

- Route every PB and LO status through one canonical writer function.
- Do not let role-specific helpers, manual filing recipes, or harness fallbacks
  write `bridge/*-NNN.md` directly.
- Preserve a draft-only path under `.gtkb-state/`; only the writer may promote
  final bytes into `bridge/`.
- Return a structured receipt containing target path, content digest,
  capability hash, capability state, revision id, and claim-release result.
- Treat success without a consumed exact receipt as failure, not a warning.

### 2. Separate publication receipt from dispatch activation

- Provide an explicit canonical-writer mode for a deliberately disabled
  dispatcher/TAFE environment.
- That mode must still perform credential/compliance checks, exact exclusive
  file creation, capability mint/consume, artifact revision observation,
  recovery sidecar handling, and claim release.
- It must not start, enable, wake, configure, or publish to the disabled
  dispatcher/TAFE surface.
- Dispatch notification can be a later optional consumer of an already valid
  receipt; it must not be required to make the bridge artifact authoritative.

### 3. Add mandatory receipt audits to every read and write boundary

- Before announcing "filed for review," query by exact target path, version,
  status, content digest, author session, and capability state.
- `gt bridge show`, queue scans, lifecycle resolution, dispatcher selection,
  implementation authorization, and verification must ignore or quarantine a
  physical file unless the exact receipt is consumed and its revision/current
  aggregate evidence is valid.
- Protected commit authorization must reject newly added numbered bridge files
  lacking exact consumed receipts.
- A later receipt must not legitimize different bytes at the same path.
- A later numbered response must not retroactively legitimize an unreceipted
  predecessor.

### 4. Make projection precedence and staleness explicit

- Treat `current_work_items.status_detail` as descriptive projection, never as
  bridge publication authority.
- Current read APIs should expose the exact receipt/revision used for any
  bridge-currentness statement.
- If a work-item projection predates a newer receipt affecting its claim, mark
  the projection stale or return a machine-readable divergence finding.
- Correct stale descriptions append-only through a new work-item version; do
  not rewrite the historical version.
- Tests and agent instructions must require the typed ledger over a prose
  summary when they disagree.

### 5. Provide a governed unreceipted-file recovery command

The recovery command should:

1. prove there is no exact capability, revision, pending sidecar, or commit;
2. copy the bytes into an in-root cleanup-evidence directory;
3. record original path, size, SHA-256, author/session metadata, and detection
   time;
4. verify the copy before removing the live path;
5. allow same-version republish only when the no-receipt/no-commit proof is
   complete;
6. publish corrected or unchanged bytes only through the typed writer; and
7. emit both quarantine and replacement receipts.

If any receipt, revision, or commit exists, recovery must append a new version
instead of reusing the path.

### 6. Bound append-only aggregate cost without discarding history

- Replace repeated full bridge-glob hashing with a deterministic incremental
  append proof, checkpointed tree, or Merkle-style aggregate whose full state
  can be rebuilt from retained history.
- Partition locks by aggregate or bridge thread where cross-thread atomicity is
  not required.
- Keep the global commit section small: compare predecessor token, append one
  receipt/revision, and advance one aggregate root.
- Perform expensive candidate validation outside the lock, then revalidate a
  compact predecessor/root token inside it.
- Retain periodic full-corpus verification as an asynchronous audit, not the
  critical path for every append.
- Define explicit latency and lock-hold budgets at 1k, 5k, 15k, and projected
  future bridge-file counts.

### 7. Add phase telemetry and single-flight behavior

- Emit timings for helper import, compliance, claim lookup, lock wait, snapshot
  load, aggregate scan/hash, capability mint, file create, capability consume,
  final currentness, and claim release.
- Surface a top-level operation id immediately so callers poll one live command
  rather than launching duplicates.
- Log timeouts and capability expiry with the operation id and exact path.
- Make safe retry idempotent by exact session/path/content/capability binding.

## Bounded Receipt Audit And Current Disposition

The ten-file incident remains a bounded audit set. The safe recovery pass
records one exact disposition per incident byte stream without treating later
files as retroactive receipts:

| Incident artifact | Current disposition | Typed successor/replacement state |
| --- | --- | --- |
| WI-5368 first v007 | exact bytes quarantined; corrected same-version replacement published | v007 row 399 `consumed`, revision `SOTREV-FC96981975034885AA744C0A36B3F960` |
| WI-5757 v003 | exact bytes quarantined; corrected same-version report published | v003 row 404 `consumed`, revision `SOTREV-4E1201B0BDC94C15A360417F5258B931` |
| orchestration Advisory v001 | exact bytes quarantined; corrected same-version Advisory published | v001 row 403 `consumed`, revision `SOTREV-B78208F10F10410997449CB4D633E539` |
| bridge-publication recovery TOCTOU Advisory v001 | historical predecessor retained; later response prevents isolated replay | v002 row 395 `consumed` |
| WI-5760 v005 | historical predecessor retained; later response prevents isolated replay | v006 row 398 `consumed` |
| WI-5666 v007 | historical predecessor retained; later response prevents isolated replay | v008 row 397 `consumed` |
| WI-5759 v003 | historical predecessor retained; whole-suffix recovery would require the original Loyal Opposition context | v004 row 393 `recovery_required` |
| WI-5758 v003 | historical predecessor retained; whole-suffix recovery would require the original Loyal Opposition context | v004 row 396 `recovery_required` |
| router-candidate-store concurrency Advisory v001 | historical predecessor retained; current recovery API cannot disposition the successor's recovery state | v002 row 400 `recovery_required` |
| WI-5299 v008 | current physical historical file retained; unchanged typed replay fails strict resolution at v005's wrong `Responds to` link | no exact typed row for v008 |

The separately filed target-collision Advisory demonstrates the corrected
publication path: v001 row 401 is `consumed`, and its Loyal Opposition v002 GO
is row 402 `consumed`. Those rows are not part of the ten-file incident count.

These rows are evidence of correction state, not proof that all ten incident
byte streams are receipted. `recovery_required` is not equivalent to a clean
consumed receipt, and no successor can retroactively receipt different bytes at
the predecessor path. All seven unrecovered incident byte streams need an
append-only historical disposition mechanism; corrective current-thread work
is required for the three `recovery_required` successors and the poisoned
WI-5299 chain.

## Future Test Plan

### A. Direct-write exclusion

1. Create a syntactically valid numbered bridge file in a fixture without a
   capability row.
2. Assert lifecycle resolution labels it unreceipted/non-authoritative.
3. Assert bridge show, queue scan, dispatcher selection, implementation-start,
   and protected commit all fail closed on it.
4. Assert a fully compliant body and valid claim do not change that result.

### B. Exact receipt binding

1. Publish through the canonical writer.
2. Assert one consumed row binds document, version, status, target, content
   digest, author session, claim session, transition digest, compliance digest,
   and artifact revision.
3. Modify one byte and assert currentness fails.
4. Replace the path with different bytes and assert the old receipt is rejected.
5. Assert a later verdict cannot cure the mismatched predecessor.

### C. Projection-precedence regression

1. Seed a work-item `status_detail` that says v006 is unreceipted.
2. append a valid consumed v006 receipt after that work-item version;
3. assert current bridge authority selects the exact receipt;
4. assert the work-item read reports the description as stale/divergent; and
5. assert an agent-facing currentness API cannot return the old prose as its
   authoritative result.

### D. Quarantine and same-version recovery

1. Seed an unreceipted, uncommitted v007.
2. Run governed recovery and assert exact cleanup-evidence bytes/hash.
3. Inject copy, verify, remove, and republish failures one phase at a time.
4. Assert no evidence loss, no duplicate live path, and no false consumed row.
5. Assert same-version republish succeeds only after complete no-receipt and
   no-commit proof.
6. Seed any prior receipt or commit and assert the tool requires v008.

### E. Publication crash matrix

Inject failures:

- before capability mint;
- after mint but before sidecar;
- after sidecar but before file creation;
- after file creation but before consume;
- after consume but before claim release; and
- during cleanup of recovery evidence.

For every phase, assert deterministic finalize/rollback behavior, exact content
preservation, no orphan minted capability, no false actionability, and no claim
leak.

### F. Concurrency and single-flight

1. Launch two same-path writers and assert exactly one canonical publication.
2. Launch independent-thread writers and assert bounded progress without a
   global convoy where no shared aggregate mutation requires serialization.
3. Retry the same operation id and assert idempotent receipt lookup rather than
   duplicate mint.
4. Assert lock timeout diagnostics name the holder/operation when available.
5. Assert duplicate caller retries cannot create multiple process trees.

### G. Append-only scale and latency

Build deterministic corpora at 1k, 5k, and 15k numbered bridge files, then
measure:

- total publication latency;
- time waiting for the registry lock;
- time holding the lock;
- bytes/files hashed per publication;
- concurrent-writer throughput; and
- recovery latency after injected interruption.

Acceptance should require that steady-state append cost is bounded by the new
entry plus compact index/checkpoint work, not proportional to total retained
bridge bytes. A periodic full rebuild must reproduce the same aggregate root
and receipt currentness from append-only history.

### H. Dispatcher-disabled mode

1. Keep dispatcher/TAFE disabled.
2. Publish a PB proposal and an LO verdict through the canonical writer's
   receipt-only mode.
3. Assert exact consumed receipts and current bridge authority.
4. Assert no dispatcher process start, enablement, wakeup, configuration
   change, dispatch-state publication, or TAFE mutation.
5. Enable only a fake notification consumer and prove that notification
   failure cannot invalidate an already atomic local publication or silently
   leave mixed state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - status authority and role-correct numbered
  transitions require the governed bridge lifecycle.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does
  not bypass bridge publication authority.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - the WI-5368 correction must itself be
  a valid PB publication before it can route review.
- `GOV-WORK-TREE-HYGIENE-001` - repair must preserve unrelated/concurrent work
  and bind only the exact incident paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the incident and corrective
  decision as durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - treat the receipt and revision as
  first-class implementation-governance artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the concrete defect crosses the
  advisory and future-work threshold.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - each later
  corrective proposal must cite the governing requirements for its exact
  receipt, recovery, concurrency, and latency slice.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any later correction must
  prove authority, recovery, concurrency, and latency behavior from the cited
  requirements.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - performance changes may not
  weaken exact receipt, credential, compliance, applicability, clause, or
  recovery guarantees.

## Specification-Derived Verification Outline

| Requirement | Future evidence | Required result |
| --- | --- | --- |
| Governed bridge authority | `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` plus new receipt-exclusion cases | unreceipted files never become actionable |
| Protected commit boundary | `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | every added numbered file has an exact consumed receipt |
| Projection precedence | focused current-work-item/bridge-currentness regression suite | exact typed receipt outranks stale status detail |
| Crash recovery | writer fault-injection matrix | no evidence loss, false authority, orphan capability, or claim leak |
| Concurrency | same-path and independent-path parallel writer tests | single-flight same path; bounded independent progress |
| Append-only nonimpairment | full rebuild/checkpoint equivalence test | compact currentness proof reconstructs exactly from retained history |
| Latency | 1k/5k/15k corpus benchmark with named phase telemetry | steady-state append cost is bounded and lock hold meets declared budget |
| Disabled dispatch | receipt-only writer integration test | consumed local receipt with zero dispatcher/TAFE activation or mutation |

All future generated artifacts must remain in-root under `E:\GT-KB`. This
draft itself is intentionally outside `bridge/` and is not a filed status.

## Recommended Review Disposition

Loyal Opposition should validate the historical ten-file ledger, the final
3/6/1 reconciliation, the four currently unresolved threads, the WI-5368 stale
projection sequence, and the append-only/global-lock latency evidence.

Corrective scope should be attached to existing authorized carriers rather
than creating duplicate work:

- WI-5729 under the active, whole-project-authorized Harness Parity project for
  exact receipt enforcement and raw-write/non-bypass parity;
- WI-5763 under the active, whole-project-authorized Advisory Corrections
  project for the canonical PB/LO filing service; and
- WI-5788 under the same Advisory Corrections project for control-plane lock
  acquisition fairness, typed retry, and publication latency.

This Advisory Proposal itself authorizes none of that implementation.

## Owner Decisions / Input

No owner decision is required to file or independently review this Advisory
Proposal.

No new approval AUQ is required if confirmed findings are partitioned among
WI-5729, WI-5763, and WI-5788 under their active whole-project PAUTHs. Prime
Builder must still use the normal proposal, independent GO, claim,
implementation-start, verification, and operation-time gates.

Do not use WI-5744 as an implementation carrier in its current state because
it has no project membership. Do not rely solely on WI-5733 or WI-5719 without
first establishing a list-free whole-project PAUTH for
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`; its current active authorizations
are work-item-list-shaped under the rejected legacy model. If review requires
one of those routes, Prime Builder must present one owner AUQ for the missing
project membership or whole-project authorization before implementation
intake. No per-work-item approval may be inferred or requested.

## Explicit Non-Approval And TAFE Exclusion

This Advisory Proposal is not a GO, PAUTH, implementation proposal, implementation-start
packet, terminal verdict, commit authority, or release authority. It does not
authorize source, test, configuration, metadata, database, Git index/history,
dispatcher/TAFE, deployment, credential, or external-system mutation. The TAFE
dispatcher remained deliberately disabled throughout the described recovery;
the report does not request or imply its activation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
