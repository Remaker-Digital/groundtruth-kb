REVISED
::init gtkb lo
::open build

# WI-6140 REVISED proposal — bounded exact-source applicability-horizon cycle-breaker

bridge_kind: prime_proposal
Document: gtkb-wi6140-source-horizon-cycle-breaker
Version: 003
Responds to: bridge/gtkb-wi6140-source-horizon-cycle-breaker-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-08-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; harness A; transcript-defined ::init gtkb pb; root-session-adopted governed proposal after exact WI-6183 terminal readback
author_metadata_source: explicit_interactive_session_metadata
session_init_keyword: ::init gtkb pb
activity_init_keyword: ::open build

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6140

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch", "bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
database_mutation_in_scope: false
registry_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
proposal_state: ready_for_independent_preimplementation_review

---

## Summary

This proposal performs no KB, MemBase, or groundtruth.db mutation.

Revise the clean five-target WI-6140 carrier so that it becomes executable
only after the separately governed WI-6183 protected-commit PAUTH read-snapshot
repair reaches independent atomic `VERIFIED`. The retained WI-6140 change then
binds an explicit canonical numbered source at version `N` to the immediate
prospective finalization member `N+1`; materializing that successor cannot make
unchanged source bytes synthesize and hash `N+2`.

This revision preserves the bounded dependency-order inversion authorized by
`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`, rowid
`14282`, content hash
`d1357c38af43e1bf20e4007c19e348d29159369e44edcdd0d8da18258b44212c`.
It also accepts v002's independently established WI-6183 prerequisite. The
inversion therefore means: terminalize WI-6183 first; independently GO,
implement, report, and atomically VERIFY this exact five-target carrier before
WI-5950 terminalization; then resume WI-5950, narrow WI-5953, and original
WI-6140 disposition under row 14277.

W0P remains quarantined non-closing evidence. Registry state, both foreign
registry index entries, all non-cohort index entries, the original WI-6140
chain, WI-5950 bytes, receipts, PAUTH records, database state, dispatcher state,
and disabled legacy TAFE remain untouched.

## Pre-Implementation Boundary

WI-6183 is now independently atomically `VERIFIED` at
`bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-014.md`, SHA-256
`53032C079E88A731004E47C781C67BE09BD7218A50F9C809C0BDD95853CABA7A`,
29,270 bytes, with consumed receipt row `2197` and atomic commit/HEAD
`c8ceae99f729738e06508feea6a2c444c9c951ed`. The exact terminal facts and
current five-target baseline are bound below.

This REVISED proposal is review authority only. It does not authorize an
implementation claim, implementation-start packet, protected-target or patch
mutation, staging, commit, finalization, receipt recovery, registry operation,
or legacy TAFE operation. The tests patch incompatibility recorded below is
resolved only after independent v004 `GO`, a fresh `go_implementation` claim,
and a current schema-v3 start packet.

## Response To Version 002

### F1 — corrected real-index invariant

Accepted. During Prime Builder proposal filing, implementation, testing, and
implementation-report publication, the complete logical real-index entry map
must remain identical to the post-WI6183 baseline recorded below. Prime Builder
does not stage any WI-6140 path. A physical index-file SHA is diagnostic only;
Git stat-cache refresh bytes are not a staged-entry mutation and do not replace
the complete mode/blob/stage map comparison.

During independent atomic `VERIFIED` finalization, the canonical finalizer may
realign only the exact committed WI-6140 cohort in the real index after the
temporary-index commit. The finalizer must prove:

1. every committed cohort entry equals the preservation-preflight result;
2. every non-cohort index entry remains exact;
3. the two foreign registry entries remain stage `0`, mode `100644`, and retain
   their post-WI-6183 blob identities exactly; and
4. any mismatch fails closed with no terminal verdict left behind.

The corrected requirement does not demand binary identity of the whole index
after lawful cohort realignment and does not suppress the canonical
`_realign_real_index_after_temp_commit()` behavior. It preserves the copied-
index transaction and the stronger relevant invariant: no non-cohort index
entry changes.

### F2 — WI-6183 is a mandatory completed prerequisite

Accepted. WI-6140 does not repair the protected checker's missing PAUTH read
authority and may not atomically terminalize against the pre-WI6183 checker.
The separate two-file WI-6183 carrier must first reach independent atomic
`VERIFIED`, with its exact source/test bytes committed and its verdict receipt
consumed. Only then may the Prime Builder re-read and bind the five-path
WI-6140 baseline, revalidate or minimally regenerate the retained patches, and
file this REVISED proposal for fresh independent review.

No trusted-packet shortcut, PAUTH omission, database staging, receipt bypass,
registry mutation, index bypass, audit bypass, or TAFE path is introduced.

## Proposal Claim

Repair only the exact-source finalization horizon:

1. When `build_packet()` receives an explicit canonical numbered
   `content_file`, `_pauth_phase_cohort()` derives the anticipated finalization
   member from the source's declared version, exactly `source_version + 1`.
2. Siblings newer than that explicit source are outside that packet's source
   horizon and cannot cause synthetic `N+2` drift.
3. Content without a canonical declared source version retains the existing
   observed-version fallback.
4. Source bytes, rules, target paths, current PAUTH state, and candidate bytes
   remain independently bound and fail closed on drift.
5. Writer, verdict-helper, packet-schema, approved-chain, candidate-evidence,
   receipt-recovery, registry, index-preservation, W0P, dispatcher, and TAFE
   behavior remain otherwise unchanged.

This is a regression repair of the exact-source binding contract. It is not a
freshness bypass, candidate restamp, append-only exception, PAUTH bypass, or
substitute for independent GO and atomic VERIFIED finalization.

## Exact Five-Target Scope

1. `scripts/bridge_applicability_preflight.py`
   - adopt only the retained declared-source `N+1` horizon hunk;
   - preserve the noncanonical observed-version fallback;
   - leave proposal selection, approved-chain resolution, operation-time PAUTH
     evaluation, packet material, candidate evidence, and schema unchanged.

2. `platform_tests/scripts/test_bridge_applicability_preflight.py`
   - adopt only the retained exact-source sibling-invariance and
     noncanonical-fallback tests.

3. `platform_tests/scripts/test_check_protected_commit_authorization.py`
   - start from the terminal WI-6183 committed postimage;
   - adopt only the retained report/prospective-VERIFIED source-horizon test;
   - preserve all WI-6183 hostile PAUTH snapshot, cleanup, oversized-blob
     omission, and fail-closed coverage;
   - prove unchanged source/candidate evidence passes before and after
     successor materialization while source and candidate drift fail
     independently.

4. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch`
   - retain byte-for-byte the exact reviewed source patch, SHA-256
     `810D6CC9030A8E4B9427B62EF157FE13C1DF55BD792CBBC0100FACF59FB316B4`,
     2,593 bytes, source delta `+16/-5`;
   - it passes strict worktree and cached checks against current HEAD and is
     not regenerated by this carrier.

5. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch`
   - treat historical SHA-256
     `FF5F00C8A0096FA96676E7B15B59875BA246B9F4224267A44CB55966E9FBE2BC`,
     7,668 bytes, as semantic input only;
   - after independent v004 `GO` plus the exact claim/schema-v3 start,
     regenerate only this already-declared patch path from the current two test
     preimages so the logical hunks remain applicability test `+109/-1` and
     protected-checker test `+35/-6` with no EOL-only normalization;
   - require strict worktree and disposable-index cached checks before applying
     it. No fuzz, ignore-whitespace, three-way, or whole-file replacement is
     permitted.

No sixth implementation target may be added. Any new target or behavior
requires another REVISED proposal and fresh independent review.

## Post-WI6183 Terminal Binding Ledger

The following values come from fresh post-terminal canonical readback. The
physical `.git/index` file hash is diagnostic only because Git may refresh
non-semantic stat-cache bytes; the controlling Prime-phase invariant is the
complete logical entry map, and the controlling finalizer invariant is exact
non-cohort entry preservation.

| Bound field | Exact current value |
| --- | --- |
| WI-6183 terminal artifact | `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-014.md`; SHA-256 `53032C079E88A731004E47C781C67BE09BD7218A50F9C809C0BDD95853CABA7A`; 29,270 bytes; status `VERIFIED` |
| WI-6183 candidate evidence | `sha256:24ac033a8fa37978c1e03996112f6b263b9eff553e1a521b53df10354bececb1` |
| WI-6183 receipt | row `2197`, `consumed`; capability `sha256:da6c06f7ad72b6501db9e57f84877e86bd991c1fade3fe1bf28e7465a5a442e9`; result `sha256:24586c90a3dc999622260eb4cfdc31b7c651a534374bf8a64c532cc44c087e27`; revision `SOTREV-731F153BD45D4B599479125E2D5CB175`; transition `sha256:d54592878b75e86edbcc4b6ab8db75c62455a41191b3968059d26e3f3fde595e`; failure/compensation null |
| WI-6183 atomic commit / current HEAD | `c8ceae99f729738e06508feea6a2c444c9c951ed`; parent `8b1262a2721e4c856e4e11cfa89d1f5715c99721` |
| current logical real-index baseline | SHA-256 `FB429040D062B927FD172CBE0BB041407E65190D1431F16034A991FD71631F9B` over the exact `git ls-files --stage -z` serialization, 21,264 entries |
| physical index diagnostic | current SHA-256 `AFCE3D78A8BAA02BE212BC69661742BF50913430BC5E1872340067158B013A6B`; WI-6183 immediate postcommit diagnostic was `96C48DB0DB5BE315574322A4162B6BD99357086A86BC3DB9CDD067DF540CAC12`; neither substitutes for the logical-entry invariant |
| foreign registry entry 1 | `config/registry/sot-artifacts.toml`, mode `100644`, stage `0`, blob `d4a1aca0e15172acad63f218f32c9814b2055677` |
| foreign registry entry 2 | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`, mode `100644`, stage `0`, blob `d4a1aca0e15172acad63f218f32c9814b2055677` |
| applicability source preimage | SHA-256 `44A2EC7CCBC4E86A7E04693AF1CC6048155C0364E4D725B606E5C2599ACED2AE`, 62,582 worktree bytes, clean; HEAD/index blob `aa6531294f43b42e5fc99437bcd185213d5e3d6b` |
| applicability test preimage | SHA-256 `BFD745633D176FBA474B6C155D5F65F57ACC0AA20FFB142461E0D37CA143FF27`, 59,373 worktree bytes, clean; HEAD/index blob `7292d46189da7461fd03ad0670849c524985be57` |
| protected-checker test preimage | SHA-256 `D835FB02CFAFE44168151608ABA2150E1D3A5CF665285CB1A4A4C29DDDD77EF3`, 208,529 bytes, clean, 5,157 CRLF records; HEAD/index blob `c852b994eb0a81667fad94c89b63df06b567da29` |
| retained source patch | SHA-256 `810D6CC9030A8E4B9427B62EF157FE13C1DF55BD792CBBC0100FACF59FB316B4`, 2,593 bytes, `+16/-5`; strict worktree and cached checks exit `0` |
| historical tests patch input | SHA-256 `FF5F00C8A0096FA96676E7B15B59875BA246B9F4224267A44CB55966E9FBE2BC`, 7,668 LF bytes; application-test `+109/-1`, protected-checker `+35/-6`; strict worktree check exits `0`, cached check exits `1` only at protected-checker line 3357 because the committed checker blob is CRLF |
| current collision/claim census | 21 nonterminal numbered chains declare at least one of the three Python targets; none has a live claim. Only expired historical draft claims row `35714` and row `33103` were returned. Exact dormant dispositions are below. |

## Retained Patch Rebase Rule

Post-WI6183 strict checks against current HEAD produced the following exact
boundary without mutating any target or patch:

```text
git apply --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch
git apply --cached --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch
git apply --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch
git apply --cached --check --whitespace=error-all -- bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch
```

The source patch exits `0` for both worktree and cached checks and remains
immutable. The historical tests patch exits `0` for the worktree check. Its
application-test hunk also passes cached. Only its protected-checker hunk fails
cached at line 3357 because WI-6183 committed checker blob
`c852b994eb0a81667fad94c89b63df06b567da29` with CRLF records while that patch
section encodes LF records.

An in-memory, non-governed diagnostic changed only the protected-checker diff
section's patch-record endings from LF to CRLF. The resulting diagnostic was
7,755 bytes and passed ordinary plus cached strict checks with no logical hunk
change. It was not written and is not an approved or final patch hash; it only
proves that the post-GO rebase can remain byte-level and bounded.

No pre-GO patch or protected target is regenerated. After independent v004
`GO`, a fresh exact `go_implementation` claim, and a current schema-v3 start
packet, Prime Builder regenerates only
`bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch`.
The governed result must:

1. encode exactly the same two logical test hunks: applicability test `+109/-1`
   and protected-checker test `+35/-6`;
2. preserve both test files' substantive bytes and avoid EOL-only target-file
   normalization;
3. pass strict ordinary and disposable-index cached checks with exit `0`;
4. record its final SHA-256, size, numstat, exact two target paths, preimages,
   and expected postimages in the implementation report; and
5. use no fuzz, whitespace-ignore option, three-way application, manual hunk
   absorption, or whole-file replacement.

Any substantive hunk or target expansion requires a new REVISED proposal.

## Dormant Overlap Ledger

Fresh post-terminal numbered-chain readback found 21 nonterminal threads whose
proposal history declares at least one of the three Python targets. None grants
authority to absorb its bytes. Claim readback returned no live claim for any of
the 21; only expired historical draft claims row `35714` and row `33103` were
present. The entire census is refreshed again immediately before the v004-backed
`go_implementation` acquisition.

| Work/thread | Current latest state | Shared surface | Disposition |
| --- | --- | --- | --- |
| `gtkb-wi5254-pauth-amendment-packet-preflight` | NO-GO v008 | applicability source/test | dormant; expired claim row 35714 only |
| `gtkb-wi5346-restore-wi5254-pauth-amendment-preflight` | NO-GO v010 | applicability source | dormant; expired claim row 33103 only |
| `gtkb-wi5403-declared-applicability-target-scope` | NO-GO v012 | applicability source/test | dormant/non-closing |
| `gtkb-wi5408-pauth-amendment-owner-evidence-applicability` | NO-GO v007 | applicability source/test | dormant/non-closing |
| `gtkb-wi5408-pauth-amendment-owner-evidence-strict-recovery` | GO v002 | applicability source/test | unclaimed; held outside this carrier |
| `gtkb-wi5441-registry-control-plane-reverse-coverage-v2` | NO-GO v002 | protected-checker test | dormant; registry bytes excluded |
| `gtkb-wi5460-wi5465-canonical-spec-existence-gates` | NO-GO v008 | applicability source/test | dormant/non-closing |
| `gtkb-wi5460-wi5465-canonical-spec-existence-gates-strict-recovery` | GO v002 | applicability source/test | unclaimed; held outside this carrier |
| `gtkb-wi5554-lo-verdict-candidate-preflight` | NO-GO v010 | applicability source/test | dormant/non-closing |
| `gtkb-wi5554-verdict-candidate-preparation-strict-recovery` | GO v002 | applicability source/test | unclaimed; held outside this carrier |
| `gtkb-wi5600-provider-applicability-preflight-recovery` | NO-GO v002 | applicability source | dormant/non-closing |
| `gtkb-wi5657-terminal-finalization-recovery` | NO-GO v002 | protected-checker test | dormant/non-closing |
| `gtkb-wi5659-protected-commit-finalizer-repair` | NO-GO v002 | protected-checker test | dormant/non-closing |
| `gtkb-wi5659-revert-superseded-separate-map` | NO-GO v006 | protected-checker test | dormant/non-closing |
| `gtkb-wi5665-skill-rename-test-recovery` | NO-GO v008 | protected-checker test | dormant/non-closing |
| `gtkb-wi5742-bound-protected-commit-evaluation` | GO v006 | protected-checker test | unclaimed; held outside this carrier |
| `gtkb-wi5811-cross-harness-append-only-enforcement` | GO v008 | applicability source | unclaimed; held outside this carrier |
| `gtkb-wi5824-protected-commit-checker-null-safety-ordering` | NO-GO v014 | protected-checker test | dormant/non-closing |
| `gtkb-wi5949-applicability-packet-determinism` | NO-GO v004 | applicability source/test | dormant/non-closing |
| `gtkb-wi6140-source-horizon-cycle-breaker` | NO-GO v002 | exact three Python targets | this REVISED proposal only |
| `gtkb-wi6140-verdict-packet-hash-source-horizon` | NO-GO v008 | exact three Python targets | original immutable non-closing evidence |

Terminal WI-6042 and WI-6183 chains remain historical committed baseline, not
current claimants. The current MemBase open target-string census additionally
finds WI-5408, WI-5502, WI-5825, WI-5844, WI-5949, WI-6020, WI-6042, WI-6057,
WI-6091, WI-6092, and WI-6114. They remain backlogged/unapproved or governed by
their own chains and confer no authority on this carrier.

Immediately before filing and before implementation start, also scan all open
work items and current numbered bridge declarations for the three Python path
strings. Any new claimant, live claim, dirty non-prerequisite target, staged
overlap, or incompatible patch ownership fails closed.

## Corrected Real-Index And Finalization Contract

The phase-specific invariant is:

- **Prime Builder phase:** record the post-WI6183 complete logical index-entry
  serialization plus mode, stage, and blob identity of every staged entry.
  Proposal filing, implementation, tests, applicability/clause checks, and
  implementation-report publication must leave every logical entry identical;
  no WI-6140 path is staged. Physical stat-cache byte drift is diagnostic, not
  an authorization to change any entry.
- **Independent finalization phase:** use the canonical protected copied-index
  transaction. The finalizer may realign only the exact WI-6140 committed
  cohort. It must compare every non-cohort entry before/after and preserve both
  registry TOMLs exactly. It must not broad-stage, reset, checkout, or restore
  the real index from an obsolete whole-file copy.
- **Failure:** any non-cohort drift, missing foreign entry, stage-number change,
  blob change, finalization error, or rollback error prevents terminal
  `VERIFIED` and preserves append-only failure evidence through the governed
  path.

The intended terminal commit cohort is exactly eleven paths:

1. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-001.md`
2. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-002.md`
3. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-003.md`
4. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-004.md`
5. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-005.md`
6. `bridge/gtkb-wi6140-source-horizon-cycle-breaker-006.md`
7. `scripts/bridge_applicability_preflight.py`
8. `platform_tests/scripts/test_bridge_applicability_preflight.py`
9. `platform_tests/scripts/test_check_protected_commit_authorization.py`
10. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-source.patch`
11. `bridge/cleanup-evidence/gtkb-wi6140-packet-hash-source-horizon-tests.patch`

The independent finalizer includes v001-v005 plus all five implementation
targets; it creates v006 in the same transaction. The three shared Python
paths must be finalized through the exact approved hunk patches, not whole-
file staging. The two dedicated cleanup-evidence patch artifacts may be
included as their exact reviewed files.

## Authorized Dependency Sequence

1. WI-6183 reaches independent atomic `VERIFIED`; its receipt is consumed and
   its exact two-file implementation plus verdict are committed.
2. Prime Builder binds every post-WI6183 field in this draft and reruns strict
   patch, overlap, claim, candidate applicability, clause, and compliance
   checks.
3. Prime Builder files this v003 as `REVISED` through one governed writer call
   under the narrow serialized release.
4. A distinct Loyal Opposition session independently reviews v003 and may file
   v004 `GO` only if the exact post-WI6183 baseline and gates pass.
5. The sole Prime implementation owner acquires the exact
   `go_implementation` claim and finalizes one current schema-v3 packet bound
   to v003, v004, PAUTH v2, five targets, and exact preimages.
6. Prime preserves the source patch unchanged, regenerates only the declared
   tests patch under the approved start boundary, applies the two then-current
   governed patches, runs the complete mapped matrix, keeps the full logical
   real-index entry map unchanged, and files v005 `NEW` implementation report.
7. A distinct Loyal Opposition verifier reruns the mapped gates and uses one
   atomic finalizer transaction to create v006 `VERIFIED` and the exact cohort
   commit while preserving every non-cohort index entry.
8. Only after exact receipt/commit/readback does coordination resume WI-5950,
   narrow WI-5953, and original WI-6140 disposition under row 14277.

The controlling ordinary sequence remains
`DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`,
rowid `14277`, content hash
`fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`,
except for row 14282's one bounded inversion.

## Explicit Non-Scope

- No modification to `scripts/check_protected_commit_authorization.py`; the
  terminal WI-6183 implementation is a prerequisite, not a WI-6140 target.
- No KB, MemBase, `groundtruth.db`, PAUTH, project-membership, registry,
  receipt-row, capability, or database mutation.
- No WI-5950 or WI-5953 byte, report, packet, receipt, claim, or recovery
  operation.
- No W0P release, ratification, terminalization, staging, or success claim.
- No original WI-6140 file rewrite or terminality claim.
- No proposal/GO selection, packet-schema, approved-chain, operation-time
  enforcement, candidate-evidence, writer, verdict-helper, compliance-hook,
  publication-currentness, or finalizer bypass.
- No Prime Builder index mutation, staging, commit, reset, checkout, or
  foreign-hunk adoption.
- No registry TOML or registry projection change; the two foreign stage-0
  entries remain outside this cohort.
- No dispatcher, scheduled-task, legacy TAFE, credential, external-system,
  release, deployment, push, destructive cleanup, or history-rewrite action.
- No numbered bridge writer from another lane while the carrier's serialized
  release is active.

## Requirement Sufficiency

Existing requirements sufficient. The owner decisions in
`DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION` and
`DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR`, WI-6140's
existing work-item requirement, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
version 2, active PAUTH v2, and the linked bridge-authority, exact-source
freshness, operation-time authorization, non-impairment, worktree-isolation,
and specification-derived verification requirements fully define the repair.

The new prerequisite changes execution order and baseline, not WI-6140's
target or behavior. No new specification, target, database action, registry
condition, receipt operation, W0P condition, dispatcher behavior, or TAFE
behavior is required.

## Acceptance Criteria

1. WI-6183 is independently atomically VERIFIED and receipt-complete before
   v003 is filed; exact terminal artifact, receipt, commit, HEAD, index, and
   target readback is recorded.
2. For explicit canonical source `bridge/<slug>-NNN.md`, identical source,
   rules, targets, PAUTH authority, and candidate state produce identical
   packet material/hash before and after `NNN+1` materializes.
3. The explicit-source cohort anticipates `NNN+1`, never synthetic `NNN+2`
   solely because `NNN+1` exists.
4. Source-content, rule, target, current-PAUTH, expiration, revocation, and
   candidate-byte drift remain independently detected and fail closed.
5. Noncanonical content with stale or plausible body-version metadata retains
   the observed-version fallback.
6. The protected-commit proposal → GO → report → prospective VERIFIED fixture
   passes before and after candidate materialization under the terminal WI-6183
   PAUTH snapshot implementation; all WI-6183 hostile tests remain green.
7. The retained source patch keeps exact SHA-256
   `810D6CC9030A8E4B9427B62EF157FE13C1DF55BD792CBBC0100FACF59FB316B4`
   and strict-forward applies. The historical tests patch is not applied; only
   after v004 GO/start, its same declared target path is regenerated and must
   pass strict worktree plus disposable-index cached checks.
8. Touched paths and logical numstat remain exactly: applicability source
   `+16/-5`, applicability test `+109/-1`, protected-checker test `+35/-6`.
   The tests-patch record may encode the checker preimage's CRLF but may not
   normalize target-file EOLs or expand behavior.
9. The three focused tests, WI-6183 focused suite, both full target modules,
   adjacent implementation-authorization and PAUTH-operation-time modules,
   Ruff lint, Ruff format, compile, diff, patch reverse checks, candidate
   applicability, clause, compliance, and post-file executability all pass.
10. Prime Builder leaves the complete post-WI6183 logical index-entry map
    identical and stages no WI-6140 path.
11. Independent finalization realigns only the exact committed cohort and
    preserves every non-cohort entry, especially both foreign registry TOMLs.
12. Database, registry, W0P, WI-5950, WI-5953, original WI-6140, dispatcher,
    and legacy TAFE state remain unchanged.
13. One unrelated Loyal Opposition session creates one atomic VERIFIED commit
    containing exactly v001-v006 plus the five implementation targets; no
    history rewrite or self-review occurs.

## Implementation Plan

1. Do not file this draft until WI-6183 terminal receipt/commit readback is
   complete and all binding-ledger tokens are replaced.
2. Recompute SHA-256/size/Git state for all five targets; record HEAD, logical
   index-entry digest, physical index diagnostic, all staged entries, and the
   exact two registry mode/stage/blob identities.
3. Preserve the source patch's strict worktree/cached pass and disclose the
   historical tests patch's checker-only CRLF cached incompatibility. Do not
   regenerate either patch before GO.
4. Re-run a full target-string/open-work-item/numbered-chain/claim collision
   audit. Preserve every dormant claimant as foreign.
5. Run candidate-aware applicability and clause checks with `--content-file`
   against the exact LF-normalized v003 bytes, then the bridge compliance audit.
6. File v003 once through the governed REVISED writer; require consumed receipt,
   no sidecar, and claim null before routing to independent LO.
7. After independent v004 GO, acquire the exact `go_implementation` claim and
   create one schema-v3 packet. Revalidate all target preimages immediately
   before mutation.
8. Preserve the source patch unchanged; regenerate only the tests patch target
   from the two exact test preimages, prove ordinary and disposable-index
   cached strict checks, then apply the two governed patches. Do not widen,
   fuzz, normalize target EOLs, or whole-file replace.
9. Prove exact postimages/touched paths/numstat and that the complete logical
   real-index entry map remains identical.
10. Execute the specification-derived matrix and capture actual counts,
    timings, warnings, hashes, and exit codes.
11. File a truthful v005 implementation report with final candidate-aware
    evidence and ordinary claim release after receipt consumption.
12. Require an unrelated LO session to perform one exact protected atomic v006
    finalization through the two hunk patches and the eleven-path cohort.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only numbered lifecycle,
  role-correct status authorship, independent GO, and independent VERIFIED.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — exact source/current authority
  evidence without self-invalidating sibling observation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — current project-scoped
  implementation authorization in addition to bridge approval.
- `GOV-ARTIFACT-APPROVAL-001` — separate protected artifact approval remains
  enforced.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — PAUTH is
  evaluated at proposal, start, report, and finalization.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — exact
  GO-backed claim and schema-v3 packet before target mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — literal concrete
  specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, work item,
  and PAUTH linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mapped executed tests
  before VERIFIED.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` version 2 — one protected atomic
  verdict/implementation commit with copied-index isolation and lawful
  real-index cohort realignment.
- `GOV-WORK-TREE-HYGIENE-001` — exact preimages, hunk isolation, collision
  checks, and foreign-byte preservation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — exact-candidate
  applicability and clause checks at lifecycle boundaries.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preservation of essential
  source, candidate, PAUTH, overlap, index, and history context.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — truthful session-context authorship.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH, owner ordering,
  retained patches, and prerequisite completion never replace GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable capture of dependency,
  review, implementation, and verification evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all active work and evidence
  remain inside `E:\GT-KB`.

## Specification-Derived Verification Plan

| Requirement | Exact executable evidence | Expected result |
| --- | --- | --- |
| Explicit-source sibling invariance | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py::test_finalization_exact_source_horizon_is_invariant_after_successor_materializes -q --tb=short` | PASS before/after successor with identical packet material/hash |
| Noncanonical fallback | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py::test_finalization_noncanonical_source_ignores_stale_declared_version_for_observed_fallback -q --tb=short` | PASS; observed-chain fallback preserved |
| Protected source/candidate separation | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py::test_report_verdict_hash_passes_before_and_after_candidate_materialization -q --tb=short` | PASS unchanged; independent source/candidate drift denial |
| WI-6183 non-regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short -k wi6183` | all terminal WI-6183 focused cases PASS |
| Full applicability module | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short` | exit 0; record count/timing |
| Full protected checker module | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | exit 0; record count/timing |
| Adjacent authority modules | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short` | exit 0; zero failures |
| Static lint | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py` | exit 0 |
| Static format | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py` | exit 0 |
| Compile/diff | in-memory compile for three Python paths plus `git diff --check -- <three paths>` | exit 0 |
| Patch integrity | source-patch SHA readback; post-GO governed tests-patch regeneration readback; strict worktree/disposable-index cached forward checks before apply; strict reverse checks after apply | source hash unchanged; new tests-patch hash/size recorded; same logical hunks; all strict checks exit 0 |
| Isolated cohort | copied-index application, whitespace check, numstat, touched-path census | exactly three Python paths and declared hunks; no foreign path |
| Governed lifecycle v2 | protected atomic finalizer evidence | exact eleven-path commit; no history rewrite; no same-session review |
| Index preservation | complete logical entry-map digest/comparison through Prime phase; non-cohort entry comparison through finalizer | Prime changes no logical index entry; finalizer changes only lawful cohort entries |
| Operation-time PAUTH/collision | current PAUTH evaluator and fresh claims/open-WI/target declaration scan | active PAUTH v2 and zero conflicting claim; otherwise fail closed |
| Candidate applicability | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file <exact-v003-or-v005-candidate>` | pass; missing required/advisory `[]`; blockers `[]` |
| Clause applicability | `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file <exact-v003-or-v005-candidate>` | exit 0; zero must-apply/blocking gaps |
| Post-file executability | `scripts/pre_verdict_executability_check.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --json` | live report `executable=true`, `gaps=[]` |
| Non-scope | pre/post DB, registry, W0P, WI-5950/WI-5953, original-WI6140, dispatcher, TAFE, index/claim/sidecar census | no unauthorized drift |

No historical test count is accepted as current evidence. The v005 report and
v006 verifier must record the then-current actual counts and timings.

## Project Authorization

`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
version 2 is the active whole-project authorization over active members.
WI-6140 is the cited work item. The PAUTH permits the source, test,
test-addition, governance-evidence, and bridge classes needed by the five
targets and forbids dispatcher mutation, external-system mutation, credential
lifecycle, push, history rewrite, deployment, release, and destructive
cleanup.

PAUTH v2 does not replace WI-6183 terminal prerequisite evidence, this REVISED
proposal, independent GO, the exact claim, schema-v3 start, implementation
report, or independent atomic VERIFIED finalization.

## Prior Deliberations

- `DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`,
  rowid `14282`, content hash
  `d1357c38af43e1bf20e4007c19e348d29159369e44edcdd0d8da18258b44212c`
  — owner authority for this clean five-target carrier to precede WI-5950.
- `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR`, rowid
  `14281`, content hash
  `adb613c6e92f393d189e549420d2e24fa516e0edddd113f06acc576f9dd8d6b4`
  — separate two-file prerequisite preserving oversized-blob omission and
  fail-closed behavior with no PAUTH/database/registry/index/TAFE bypass.
- `DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`,
  rowid `14277`, content hash
  `fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`
  — controlling sequence resumed after this carrier.
- `bridge/gtkb-wi6140-source-horizon-cycle-breaker-001.md` — original clean
  carrier proposal and retained patch provenance.
- `bridge/gtkb-wi6140-source-horizon-cycle-breaker-002.md` — independent NO-GO
  establishing the corrected index invariant and WI-6183 prerequisite.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-001.md` and
  `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-005.md` — original
  claim, tests, and exact retained patch evidence.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-008.md` — original
  chain's current NO-GO routing evidence, preserved for later disposition.
- `bridge/gtkb-wi5950-strict-terminal-recovery-016.md` — cycle evidence;
  WI-5950 remains paused until this carrier terminalizes.
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-014.md` — live
  terminal prerequisite, consumed receipt row 2197, and atomic commit
  `c8ceae99f729738e06508feea6a2c444c9c951ed` satisfying F2.

## Owner Decisions / Input

The owner expressly authorized the bounded dependency inversion captured in
row 14282 and the separate WI-6183 protected-checker repair captured in row
14281. Those decisions authorize the corrected dependency route through
ordinary governed lifecycles; they do not authorize a bypass, pre-GO patch
regeneration, or implementation without a current schema-v3 start.

The narrow numbered-writer release applies only to the serialized WI-6183 and
WI-6140 route. All unrelated numbered bridge writer lanes remain held.
Independent Loyal Opposition GO is mandatory before any WI-6140 target
mutation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-6140 clean source-horizon carrier v003 responding to v002 under owner rows 14281, 14282, and 14277",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, and REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001 version 2",
  "primary_route": "WI-6183 independent atomic VERIFIED, fresh post-terminal five-target binding, v003 REVISED, independent v004 GO, exact claim/schema-v3 start, unchanged source patch plus tests-patch-only CRLF record rebase, truthful v005 report, and independent atomic v006 VERIFIED",
  "before_behavior": "An explicit source at version N anticipates N+1 before publication but observes and hashes N+2 after N+1 materializes, making unchanged source evidence self-invalidating; the pre-WI6183 copied audit also lacks bounded PAUTH read authority.",
  "after_behavior": "After WI-6183 restores bounded PAUTH read authority, an explicit canonical source at N deterministically binds N and N+1 while real source, rules, targets, PAUTH, and candidate drift remain independently detectable and fail closed.",
  "self_descriptive_naming": "source horizon, canonical content_file, source_version + 1, packet_hash, candidate_evidence_hash, copied-index PAUTH snapshot, committed cohort, and non-cohort index entries state the boundaries directly.",
  "obsolete_guidance_disposition": "V001's impossible post-finalization whole-index identity and its WI-6183-behind-WI6140 ordering are superseded by v002; the original WI-6140 chain remains immutable non-closing evidence for row-14277 disposition.",
  "history_preservation": "All WI-6183, original WI-6140, WI-5950, WI-5953, and W0P numbered artifacts remain append-only; this v003 is filed only after exact terminal prerequisite readback.",
  "essential_context_preservation": "Preserve the exact five targets and logical hunk semantics; the source patch byte-for-byte; the historical tests patch as semantic input until its post-GO checker-record CRLF rebase; the terminal WI-6183 two-file implementation and all hostile PAUTH snapshot, cleanup, oversized-blob omission, and fail-closed coverage; exact-source, rules, targets, PAUTH, candidate, approved-chain, and operation-time binding; dormant target claimants; original WI-6140 evidence; row-14277 sequencing; W0P quarantine; database and registry state; both foreign registry index entries and every non-cohort index entry; independent review; and governed atomic finalization while changing only the exact source-horizon hunks.",
  "baseline": {
    "status": "fresh post-WI6183 terminal baseline bound",
    "wi6183_terminal": "v014 VERIFIED SHA53032C079E88A731004E47C781C67BE09BD7218A50F9C809C0BDD95853CABA7A, receipt2197 consumed, commit c8ceae99f729738e06508feea6a2c444c9c951ed",
    "head": "c8ceae99f729738e06508feea6a2c444c9c951ed",
    "real_index": "logical-entry SHA256 FB429040D062B927FD172CBE0BB041407E65190D1431F16034A991FD71631F9B over 21264 entries; physical SHA AFCE3D78A8BAA02BE212BC69661742BF50913430BC5E1872340067158B013A6B diagnostic only",
    "five_targets": "source SHA44A2EC7C/62582/blob aa653129; applicability-test SHABFD74563/59373/blob7292d461; checker-test SHAD835FB02/208529/blob c852b994 CRLF; source-patch SHA810D6CC9/2593 strict; tests-patch historical SHAFF5F00C8/7668 requiring post-GO tests-patch-only record-EOL rebase",
    "foreign_registry_entries": "exactly config/registry/sot-artifacts.toml and projected registry/sot-artifacts.toml, each mode100644 stage0 blob d4a1aca0e15172acad63f218f32c9814b2055677"
  },
  "expected_result": {
    "summary": "Terminalize one clean exact-source applicability-horizon cycle-breaker after its PAUTH read-snapshot prerequisite without absorbing foreign state.",
    "scope": [
      "one applicability-preflight source module",
      "two focused test modules",
      "one byte-preserved source patch and one post-GO regenerated tests patch at their existing declared paths"
    ],
    "acceptance": [
      "explicit source N remains packet-hash invariant after N+1 materializes",
      "no synthetic N+2 observation",
      "noncanonical fallback preserved",
      "source and candidate drift fail independently",
      "terminal WI-6183 PAUTH snapshot and cleanup protections remain green",
      "Prime complete logical-index preservation and finalizer non-cohort index preservation both hold",
      "database, registry, W0P, original WI-6140, WI-5950, WI-5953, dispatcher, and legacy TAFE remain unchanged",
      "fresh independent atomic VERIFIED under governed Git lifecycle version 2"
    ]
  },
  "rollback": {
    "instructions": "Before terminal verification, reverse only the two exact approved WI-6140 patches under the active governed claim and restore the five declared targets to their recorded post-WI6183 preimages; do not alter WI-6183, the real index, foreign registry entries, or historical evidence.",
    "verification": "Recompute all five hashes, rerun the mapped matrix, and prove database, registry, real-index non-cohort, W0P, WI-5950, WI-5953, original-WI6140, dispatcher, and TAFE state unchanged."
  },
  "hard_invariants": [
    "WI-6183 independent atomic VERIFIED before v003 filing",
    "exactly five WI-6140 implementation targets",
    "no KB, MemBase, or groundtruth.db mutation",
    "no registry mutation and no Prime index mutation",
    "finalizer may realign only the committed cohort and must preserve every non-cohort index entry",
    "no conflation with WI-6183 implementation or WI-5950 recovery",
    "independent GO, exact claim, schema-v3 start, report, and independent VERIFIED",
    "no whole-file staging of shared Python paths",
    "W0P remains quarantined non-closing evidence",
    "row-14277 sequence resumes only after this carrier terminalizes",
    "no dispatcher or legacy TAFE mutation",
    "atomic independent VERIFIED only"
  ],
  "fail_closed_conditions": [
    "WI-6183 terminal artifact, receipt, commit, HEAD, or target readback absent or inconsistent",
    "another numbered writer violates serialization",
    "new target or live claim collision",
    "proposal, GO, PAUTH, claim, packet, target, preimage, or patch drift",
    "source patch drift or regenerated tests patch failure under strict worktree/disposable-index cached checks",
    "touched-path or hunk expansion",
    "source, candidate, operation-time, or protected-audit freshness failure",
    "database, registry, foreign index, W0P, WI-5950, WI-5953, original-WI6140, dispatcher, or TAFE drift",
    "test, Ruff, compile, diff, applicability, clause, compliance, executability, receipt, or finalization failure"
  ]
}
```

## Risk / Rollback

The source-binding risk is under-binding noncanonical content that merely
contains plausible version metadata. The bounded horizon applies only to an
explicit canonical numbered source; noncanonical content retains observed-
chain fallback and has dedicated coverage.

The prerequisite risk is treating a WI-6183 draft or report as terminal. Only
the live independent VERIFIED artifact, consumed receipt, atomic commit, and
post-commit target/index readback satisfy the prerequisite.

The overlap risk is allowing a dormant GO/NO-GO thread to mutate a shared path
concurrently. Row 14282 establishes this carrier's serialized priority only
after WI-6183; fresh claims/open-WI/bridge-target checks remain mandatory.

Before terminal WI-6140 verification, rollback reverses only the two exact
approved WI-6140 patches and restores the five targets to their recorded
post-WI6183 preimages. It never reverts WI-6183, rewrites history, replaces the
real index wholesale, or touches registry/W0P/receipt/TAFE state. After atomic
VERIFIED, any regression requires a new governed append-only repair and an
ordinary revert commit.

## Pre-Filing Applicability And Clause Evidence

An evidence-bearing pending-content pass against LF-only candidate SHA-256
`A3A15DCB0CA41030E7BB58A26F97F5755B075372F9F9AC25168F98F1E2F68981`,
49,058 bytes, returned:

- applicability `preflight_passed: true`, packet
  `sha256:b69b57b76b30b6e829c79f553bce1606efe95f1e5d8978447f81ceeea286d065`,
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`;
- clause exit `0`, 5 evaluated / 4 `must_apply` / 1 `may_apply` / 0 evidence
  gaps / 0 blocking gaps;
- bridge-compliance audit `pass`, reason null;
- credential-catalog hits `0`; and
- one parseable structured non-impairment JSON object.

The exact commands were:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi6140-source-horizon-cycle-breaker-003.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6140-source-horizon-cycle-breaker --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi6140-source-horizon-cycle-breaker-003.md
```

Adding this evidence changes the candidate bytes, so the embedded candidate and
packet hashes are explicitly penultimate provenance, not final-byte claims.
After this subsection is complete, Prime Builder reruns applicability, clause,
compliance, credential, structured-JSON, and LF checks against the exact final
bytes and reports those final hashes with the governed publication readback;
the writer independently repeats its mandatory gates. No content edit occurs
after that final pass.

`pre_verdict_executability_check.py` has no pending-content proposal mode: its
`--draft-verdict-body` option supplies a prospective reviewer verdict body while
Gates A and D still load the live proposal. Therefore this proposal makes no
false pre-publication v003 executability claim. Immediately after receipt-
complete publication, Prime Builder runs the live v003 check read-only and
routes to independent review only when it returns `executable=true`, `gaps=[]`.

## Bridge Filing

The sole matching Prime Builder session may adopt and file these bytes only
after post-WI6183 binding, final exact-byte gates, a fresh matching draft claim,
and explicit serialized coordination. Filing must use one governed REVISED
writer call. Require exact live SHA/size, consumed typed receipt, failure and
compensation null, sidecar absent, claim null, and aggregate currentness before
routing to an independent LO session.

The legacy TAFE dispatcher remains disabled. This carrier does not invoke,
enable, start, restart, reconfigure, repair, or use it.

## Recommended Commit Type

`fix` — the five-target delta repairs reproduced self-invalidating
applicability-packet freshness while preserving PAUTH, candidate, review,
overlap, non-cohort index, and finalization semantics.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
