NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; non-live strict-recovery proposal draft; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5904-wi5316-strict-terminal-provenance-recovery
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5904
Related Work Items: WI-5316, WI-5370, WI-5825, WI-5858, WI-5879, WI-5881, WI-5898

target_paths: ["groundtruth.db"]
implementation_scope: service_owned_strict_terminal_provenance_recovery
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
git_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# NEW Proposal — WI-5316 Strict Terminal Provenance Recovery

## Purpose And Scope

WI-5904 establishes one fresh strict-valid recovery controller for the
WI-5316 terminal-provenance incident. It does not rewrite, replace, move,
archive, delete, normalize, or republish any of the 35 present WI-5316-related
bridge artifacts. It preserves their raw bytes as immutable historical
evidence, records the four strict-invalid chains as evidence-only quarantined
inputs, recognizes the two already-withdrawn carriers as closed, and binds the
historical implementation evidence by reference to a fresh receipt-complete
controller lifecycle.

The only implementation target is exact service-owned metadata in
`groundtruth.db`, accessed exclusively through the independently VERIFIED
WI-5881 reservation/control-plane service and WI-5825 capability/receipt
recovery service. No source, test, bridge-history file, cleanup-evidence path,
Git/index, raw SQLite, dispatcher/TAFE, credential, deployment, release, or
external-system mutation is in scope.

## Incident And Required Outcome

The physical WI-5316 original thread ends at tracked, clean v008 `VERIFIED`,
but the strict resolver rejects the immutable chain at v002 because its
`Responds to` metadata is absent. The historical implementation report v007
also carries decorated `Version` metadata and a noncanonical `Responds to GO`
field. Physical terminal-looking status is therefore not strict terminal
authority.

Earlier repair attempts cannot safely be resumed. They contain separate
immutable transition, version-metadata, and predecessor-link failures, and two
later correction lanes are already validly `WITHDRAWN`. The obsolete cleanup
proposal attempted to archive or delete a file that is now tracked, clean,
HEAD-identical evidence. WI-5904 supersedes all of those recovery attempts for
this exact incident without changing their bytes or reopening their slugs.

The required result is a new strict controller chain under this document name:

1. this v001 proposal and an independent v002 `GO` establish scope only;
2. after WI-5881 and WI-5825 are independently `VERIFIED`, a fresh exact claim
   and schema-v3 start create a durable by-reference reservation over the
   immutable evidence tuple;
3. a receipt-backed v003 implementation report proves the historical candidate
   from its reachable commit snapshot, the complete 35-file preservation
   manifest, the quarantine/controller records, and TEST-11822 predicates;
4. a distinct Loyal Opposition session independently publishes receipt-backed
   v004 `VERIFIED` only if every predicate holds; and
5. atomic verifier finalization consumes the exact receipt, records the fresh
   controller as the strict completion-evidence authority, and appends the
   corresponding WI-5316/WI-5904/test provenance without changing any legacy
   artifact or pretending an invalid chain became strict-valid.

Until that sequence completes, WI-5316's existing reconciler-produced
`resolved` row is historical state whose cited original thread is not strict
terminal proof. It must not be used to bypass this recovery, and it must not be
destructively rewritten. The terminal finalizer may append a new WI-5316
version that retains or corrects its resolution only after the fresh strict
controller is independently VERIFIED and receipt-complete.

## Complete Carrier Deduplication And Disposition

All current WI-5316 original, repair, and withdrawal carriers are accounted
for below. Physical latest status is descriptive only when strict resolution
fails.

| Carrier | Physical latest | Exact latest SHA-256 | Strict result | WI-5904 disposition |
|---|---:|---|---|---|
| `gtkb-wi5316-frozen-modernization-rc-contract` | v008 `VERIFIED` | `6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B` | `WRONG_RESPONDS_TO_LINK` at v002 | Original historical implementation/verdict evidence; quarantine as evidence-only and recover by reference. |
| `gtkb-wi5316-failed-verified-finalization-repair` | v009 `NO-GO` | `0477405F8C6A07A0BA7DD17E58E850214FBDFE923710E8DD4E9948B6FD746519` | `INVALID_BRIDGE_TRANSITION` at v004 (`NO-ACTION -> REVISED`) | Failed repair evidence; no append, move, or reuse as authority. |
| `gtkb-wi5316-failed-finalization-governance-recovery` | v005 `WITHDRAWN` | `41E385A3F53D72C4B0228F763D4C97CF6A48A287333F270E56356611D7753935` | strict-valid terminal | Closed; its targetless governance-review lane is not implementation authority. |
| `gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair` | v006 `NO-GO` | `5551DCBB539D0C9A1C23E5CC3FCFCD3F6DAB73CFE6D56BCB20124D1B4A469769` | `WRONG_BRIDGE_VERSION_METADATA` at v003 | Failed repair evidence; no append or scope adoption. |
| `gtkb-wi5370-no-responds-wi5316-failed-verified-finalization-repair` | v002 `WITHDRAWN` | `FB4B974A9ACDA1F0798C02B3072B9405D984148066330A3BB3F43FF7FB3D4693` | `WRONG_RESPONDS_TO_LINK` at v002 | Malformed withdrawn evidence; no append or normalization. |
| `gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup` | v005 `WITHDRAWN` | `2B9BDB3E5E1BCADD9BF9C25171002104EF97B15C7995CE133FEB861DF9C1EE35` | strict-valid terminal | Closed; expressly retires archive/delete of the tracked v008 and is not duplicated. |

No seventh WI-5316 recovery lane is required. WI-5904 is the sole fresh
controller. A later scope discovery that identifies another exact carrier or
changes any row above fails currentness and returns this proposal for revision.

## Immutable Evidence Manifest

At preparation, exactly 35 `bridge/*wi5316*.md` artifacts exist: 30 tracked
and five untracked. The manifest below is sorted by path. Each line is
`path|raw-byte-length|SHA-256|physical-status|Git-state|Git-blob-or-dash`.
Joining the exact lines with LF and one terminal LF yields manifest SHA-256
`E0170F5618D2215309C0EFCB7CAA4431562E50FFD8818AA8D8B39B99E3C4162F`.

```text
bridge/gtkb-wi5316-failed-finalization-governance-recovery-001.md|8689|7A9F69E033276CE7D8B79659C74CDD32732455998FE994F18A45E30B1EA0F0E2|NEW|tracked|51054448d8f607927b248d829cbbaae1be4bb6d6
bridge/gtkb-wi5316-failed-finalization-governance-recovery-002.md|3712|CE0E80A3051B022C37C78A2492BAFE0B4AC1AF5FC637BCC009EC18A326891D07|GO|tracked|5232f98d1b0b4d1117712ab91711e6e342604249
bridge/gtkb-wi5316-failed-finalization-governance-recovery-003.md|10689|20FEF7ACF5F0CE854896B7AF78395682F60202D5DCCFD9A26EF253F60C40C180|NO-ACTION|tracked|af299e3ea1754e0c9caf672e285a9a6f07203142
bridge/gtkb-wi5316-failed-finalization-governance-recovery-004.md|3732|451155F54DBA71EEDD53B2D9452BED72B81845879AC561DC7CF8CBEADFCC16CD|NO-GO|tracked|8a1adffdeb74cf9bfcb5943d7eeb2571b00a5bd7
bridge/gtkb-wi5316-failed-finalization-governance-recovery-005.md|2755|41E385A3F53D72C4B0228F763D4C97CF6A48A287333F270E56356611D7753935|WITHDRAWN|tracked|1b9086e76d1ecd5c9c1f51bdb769488f3c2b6692
bridge/gtkb-wi5316-failed-verified-finalization-repair-001.md|8504|A78B01FCBDC0900CA0A9BAC7BA2C1C93A8C7AFC25A63175143E2C73C3C508CFE|NEW|tracked|afda533c5e46414a1df729daf2b67c056583f615
bridge/gtkb-wi5316-failed-verified-finalization-repair-002.md|2294|E432418DC7CCFECF993AAB4C1F96BA94EFDAC9EAD234486AE782230794BB4547|GO|tracked|1bde4606342ff4c7db6e50cb291e05fa2ee60d13
bridge/gtkb-wi5316-failed-verified-finalization-repair-003.md|2421|8453A1A4ACD6B866057BF0B555450536FC638F839A57103675EFC3849D0DF113|NO-ACTION|tracked|cdb9f7b20a98e789eba30b47e0abb210b8a46def
bridge/gtkb-wi5316-failed-verified-finalization-repair-004.md|8019|CDCAA3947631BCC44396752FFB3DA6ADDEA1731362195C80154317BFD3BFD956|REVISED|tracked|e3ac072d1917f95dd7191725a8c64cec5d1a3d84
bridge/gtkb-wi5316-failed-verified-finalization-repair-005.md|2335|038455E37AA8519A153E885F5D5EDF52E199D6FD45E2781BF7557B7F12628352|GO|tracked|d75678a9d134eb1bccf6bb384cfb509e49cf732b
bridge/gtkb-wi5316-failed-verified-finalization-repair-006.md|2250|8ACD94191E9C8BC484CE4F771481A7452AC25EABA003358DCA6FDCBDE05FDB91|NO-ACTION|tracked|935696ee524df181925f0762b9ba2eaef96f0577
bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md|6833|5DEA820C40C00503B48DE542B4899C4DA69888B5C75F6C93A0A8DFF354026407|GO|tracked|edcf8997c4d3dbfce036e9d0589d54aca117effc
bridge/gtkb-wi5316-failed-verified-finalization-repair-008.md|2625|B9E3D5BFBDB438F4CB6D43EC0C2CB8048EE42307FE478C25CEE062028DF8679C|NO-ACTION|tracked|5f5c6a8eccd9e7ef67c57b0e0d002b433b821a56
bridge/gtkb-wi5316-failed-verified-finalization-repair-009.md|1881|0477405F8C6A07A0BA7DD17E58E850214FBDFE923710E8DD4E9948B6FD746519|NO-GO|untracked|-
bridge/gtkb-wi5316-frozen-modernization-rc-contract-001.md|11404|89439028934B7ADB699D0E6FCB813C36076B0357326AD214E0ACC39A1F82D71E|NEW|tracked|6b8c25c718bba3c4a2f1fe6ee328dc5cd27c732b
bridge/gtkb-wi5316-frozen-modernization-rc-contract-002.md|7453|87C829E141B917D06632E23295A0F9DAD1E7A7AE4432EA05811765D8E52B3040|GO|tracked|409176cbf6e58324bd9bda1eae6806edb706874f
bridge/gtkb-wi5316-frozen-modernization-rc-contract-003.md|5887|F32505890AFCEC6734C8DBA9233C3083731F7A2050D445B0536820AFF9295A46|NO-ACTION|tracked|9e60b0a4c1b58d3231a83293c19c422a504ac225
bridge/gtkb-wi5316-frozen-modernization-rc-contract-004.md|11689|73E3DB8E3B3F6C882B7EF22C115A60FC502CDC66224409D7315937DA2985ACC3|NO-GO|tracked|a74d49f4f28e88feb0815d1e4e62326077d35f6f
bridge/gtkb-wi5316-frozen-modernization-rc-contract-005.md|13553|564F13184896B7DC990B20980851B3763D2B929F42074E506ED285CF7AA3626F|REVISED|tracked|4bb5e7eac2e7e144f0b66d74d9f0f59fcfbd2ebc
bridge/gtkb-wi5316-frozen-modernization-rc-contract-006.md|12615|C878FA75E3F7EA339A12036B3F8D8A79AA2666FCB18EEC2E11E5490E1BD30363|GO|tracked|c8a19d9b0ee1ff0f869536790a53acd0bbe6e147
bridge/gtkb-wi5316-frozen-modernization-rc-contract-007.md|9680|1D227CE0D3D7BE33411FE3F66A8BBACEAC6518C6186F0504A241EBEA29707432|NEW|tracked|e388ec32c048f6b1cf609a7c0d9fb09403194855
bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md|4721|6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B|VERIFIED|tracked|87d74ee132120fea6294ae9925684ff7d958f11e
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-001.md|8616|603947758E754DBC57490BC5EF61B8D426C9BE952F7ED2C9C56F05D6885CEA8E|NEW|tracked|aee132f9f557d252a50384c0c6ac8552973029ce
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-002.md|1985|5A0E72B1CAB3D9CA9B80ED2A9BF67F0BA49F38724F0324F96B594D2485FF5E53|GO|tracked|3da37b94940cf253e067778f6c704dc09712c9fc
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-003.md|11270|EEBC354BCF09967B4D82F7874AF99109FBD0D98E20CE6CE2D142C7682A672AAC|NEW|tracked|97117abc950fdd58ade8ee39072c6888162b3444
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-004.md|5745|0E4C1F66681A00D61D650B6B3BE0632EBFF8D96E193174F4BA3F10C873C16B87|NO-GO|tracked|0161dd608b29620f417a98453218d2f5627a4786
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-005.md|2424|6340A1578DE451B0147144A4A7EC1D9D5EE10FDAB4F58FDB96BD6F503E1993CF|NO-ACTION|tracked|1842ee7eadb594a6c60629121709495b80531617
bridge/gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair-006.md|9177|5551DCBB539D0C9A1C23E5CC3FCFCD3F6DAB73CFE6D56BCB20124D1B4A469769|NO-GO|untracked|-
bridge/gtkb-wi5370-no-responds-wi5316-failed-verified-finalization-repair-001.md|7288|0D4572045A1366F22D9C3BCE1AF6981641E9E7D9FEFBE4A7398A29D31D5150A1|NEW|tracked|c6193158026b6b8d161cd5322ce552756377af55
bridge/gtkb-wi5370-no-responds-wi5316-failed-verified-finalization-repair-002.md|3007|FB4B974A9ACDA1F0798C02B3072B9405D984148066330A3BB3F43FF7FB3D4693|WITHDRAWN|tracked|bbf6b1dc742c8a429470710f50f75fd57bdccb1e
bridge/gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup-001.md|8394|1701A81BE91F23C9A5698CFA0C763096A14024264B39C0F2E998F2200CDE169C|NEW|tracked|268498f21bb1de3996ebe2c3ebe68475e1803950
bridge/gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup-002.md|1905|F4E881CFB70338BCABFC1C3CF767AF5F668077CC78E3783550F9FE5A78D481D3|GO|tracked|d5771f552b8a097d4fbd890b8e6c8ce3209bdaad
bridge/gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup-003.md|16131|39B57F8C581ACE5DBAEBED6FA74963541FF514C0AD14ABF07EC4CB7F63C6E30B|NO-ACTION|untracked|-
bridge/gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup-004.md|2376|B5566A918F77E6A8B549452C437870F5DFE4462CDCF2F89E0FE8F142AA77B945|GO|untracked|-
bridge/gtkb-wi5370-wi5316-reappeared-invalid-terminal-cleanup-005.md|7395|2B9BDB3E5E1BCADD9BF9C25171002104EF97B15C7995CE133FEB861DF9C1EE35|WITHDRAWN|untracked|-
```

The reservation binds the full manifest, not only the six latest files. Any
path count, raw byte, length, hash, tracked state, or Git blob drift requires a
fresh independently reviewed revision before implementation. The five
untracked files are also immutable incident evidence; this scope does not
stage, commit, archive, delete, or otherwise take Git ownership of them.

## Historical Implementation Evidence Bound By Reference

Reachable ancestor commit
`9373C523164ECFA8A2ACADFE4C6E7FD1DCB008EE` contains the exact original v008
verdict and the three candidate blobs reviewed there. The commit is an ancestor
of current `HEAD`; it is evidence, not a branch or index mutation.

| Historical path at commit `9373c5231` | Git blob | Raw SHA-256 | Bytes |
|---|---|---|---:|
| `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` | `87d74ee132120fea6294ae9925684ff7d958f11e` | `6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B` | 4,721 |
| `config/governance/modernization-release-candidate.json` | `da7a65b139d53c35e77d8ec9619595abb49c02d7` | `203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D` | 50,741 |
| `scripts/check_modernization_release_candidate.py` | `14282fe840fff737d23f02361b6f50f513e6934f` | `40B64AE08FD3F278C62AB5A376D9420D061C98CF54592D7A946619D896E3A193` | 80,208 |
| `platform_tests/scripts/test_modernization_release_candidate.py` | `498493f474f13de17aac763f60ed9537866631bf` | `1B07D2130E40E5B88EC8CCDDF828FCACC37E8ED4A1490D83BB0680B630D5CA48` | 36,269 |

Those three target hashes exactly match the v007 implementation report and
v008 independent review. The manifest remains byte-identical in the working
tree. The checker and focused test have later committed current bytes
(`808DC89B8DFC3B4CCDFD2F352B49D2A229985DA01A0254FBC456920D3E874BE3`
and `485B7BCE544F353B32813717A463B3613AB60B03AABCF822D449BD782644D85E`),
so the recovery must evaluate the historical commit snapshot by reference. It
must not falsely assert that the old implementation candidate equals current
source/test bytes, restore historical source, or absorb later work.

## Current Work Item, Project, PAUTH, Test, And Claim Authority

- WI-5904 is current v1, P0, open/backlogged, origin `defect`, and names
  TEST-11822 under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Active membership
  `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-5904` places WI-5904 in
  active `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  is active v2, unexpired and list-free. It permits metadata,
  governance-evidence, bridge, source/test and configuration classes while
  forbidding dispatcher mutation, external-system mutation, credential
  lifecycle, push, history rewrite, deployment, release, and destructive
  cleanup. This proposal uses only the metadata/governance-evidence portion.
- Legacy `work_items.approval_state: unapproved` is not operation-time
  authority. Active exact project membership and current list-free project
  PAUTH control under the owner's project-inheritance decision.
- TEST-11822 is current v1 and has no result. It may record PASS only from the
  complete receipt-bound live predicates below.
- The new controller slug has no claim, no physical v001, and no existing
  bridge thread. At preparation there is no active claim on any six carrier
  slugs; two retain expired draft rows, which are evidence and are not mutated.

The PAUTH never substitutes for independent v002 `GO`, a fresh exact
`go_implementation` claim, schema-v3 start, target enforcement, governed
service APIs, a factual v003 report, distinct-session independent v004 review,
or atomic receipt-backed finalization.

## Dependency Gate And Scope Separation

- WI-5881's current physical strict-valid head is v005 `REVISED`, SHA-256
  `B36E0146371D91F8BA9C430DDBF61D2C0B7F055A7BA027B34F61273813C30569`.
  It is not independently VERIFIED and cannot yet supply the generic durable
  candidate/reservation, claim-fence, recovery-owner, event-journal, or
  reservation-aware publication contract.
- WI-5825's current physical strict-valid head is v006 `GO`, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`.
  It is not independently VERIFIED and cannot yet supply durable capability
  recovery, exact-byte republish, or receipt back-fill.
- WI-5879 v005 and WI-5898 v001 are incident-consumer precedents for different
  invalid generations that require physical evidence replacement. WI-5904
  shares their generic dependency ordering but does not share their victim
  paths, archive paths, incident rows, or replacement operations.
- WI-5858 remains the owner of timer, retry, TTL, throttle, and concurrency
  externalization. WI-5904 introduces no literal timer value.
- WI-5370 and its five recovery/cleanup carriers are resolved or withdrawn
  historical scope. WI-5904 does not reactivate WI-5370 or adopt its stale
  archive/delete operation.

WI-5904 remains implementation-disabled until WI-5881 and WI-5825 each have a
factual report, distinct-session independent `VERIFIED`, current exact hashes,
receipt-complete publication, closed claims/start packets, and clean shared
implementation targets. Proposal existence or `GO` alone is insufficient.

## Exact Service-Owned Database Boundary

`groundtruth.db` is a shared service-owned SoT, not an exclusive whole-file
checkout target. WI-5904 may mutate only these exact logical record cohorts
through governed APIs and short row-level transactions/CAS:

- the WI-5904 reservation/controller and append-only event rows keyed to the
  exact 35-file manifest and historical commit tuple;
- evidence-only quarantine/link rows for the four strict-invalid carrier
  slugs and closed-reference rows for the two strict-valid withdrawn carriers;
- publication capability and receipt rows for this controller's exact v003
  report and independently authored exact v004 verdict;
- the TEST-11822 result row and exact supporting evidence packet;
- WI-5904 completion linkage; and
- a new version of WI-5316 completion evidence, only during successful atomic
  terminal finalization, that cites this strict controller without erasing its
  prior reconciler history.

It may not hash-bind, lock, copy, replace, checkpoint, vacuum, or otherwise
treat the whole database file as exclusively owned. It may not mutate WI-5370,
another WI, another test, a foreign claim/start/capability/receipt, a generic
WI-5881/WI-5825 row, or unrelated registry state. Exact-row or current-claim
collision fails closed; unrelated SoT operations remain parallel.

## Governed Recovery Execution

Only after both generic dependencies are independently VERIFIED and all
preconditions are freshly revalidated:

1. Re-read WI-5904, WI-5316, WI-5370, TEST-11822, exact membership/PAUTH,
   dependency report/verdict receipts, all 35 physical files, six resolver
   outcomes, the historical commit/blobs, current claims/start packets, and
   exact row overlaps. Any drift returns the proposal for revision.
2. Acquire WI-5904's exact `go_implementation` claim and schema-v3 start for
   `groundtruth.db` with the logical row cohort above. No carrier-file claim or
   target ownership is acquired because no carrier file changes.
3. Through the independently VERIFIED WI-5881 service, atomically persist and
   canonically read back the normalized by-reference controller candidate,
   exact bytes/size/content/compliance/resource-bound digests, original author
   envelope, full evidence manifest, historical commit/blob tuple, current
   invoker/claim/start/owner epoch, immutable reservation, and first event.
4. Re-run the six strict resolutions and the 35-file raw manifest without
   changing any file. Require the four exact typed failures and two exact
   strict-valid `WITHDRAWN` results shown above. A different result is drift,
   not an invitation to normalize history.
5. Independently read the four historical blobs from reachable commit
   `9373c5231`, recompute their raw hashes, and compare them with v007/v008.
   Evaluate the historical implementation evidence at that snapshot; do not
   substitute current source/test bytes.
6. Publish only the durably stored exact v003 implementation-report bytes
   through the reservation-aware writer. If publication is ambiguous, use
   only the independently VERIFIED WI-5825 recovery/readback operation. Never
   blind-retry a numbered version.
7. Require a distinct Loyal Opposition session to review the v003 report and
   publish only the exact receipt-bound v004 `VERIFIED` or a concrete `NO-GO`.
   The reviewer must not self-review, alter legacy files, or infer terminality
   from their physical first-line statuses.
8. On `VERIFIED`, the governed finalizer atomically consumes the exact receipt,
   records the strict controller link, appends TEST-11822 PASS and the exact
   WI-5316/WI-5904 completion evidence versions, and canonically reads back all
   rows. On `NO-GO` or ambiguity, leave the reservation/evidence events intact
   and append no terminal linkage or PASS result.
9. File the final current-state report only from canonical readback. No Git
   finalization, dispatcher/TAFE action, or legacy artifact mutation is part of
   this incident.

## Reservation, Provenance, And Receipt Invariants

The reservation and receipt must bind all of the following as one immutable
tuple:

- controller document/version and exact proposal/GO/report/verdict hashes;
- active WI-5904 membership, PAUTH v2, future GO, claim, schema-v3 start,
  original report author, current invoker/owner epoch, and independent reviewer;
- all 35 exact paths, lengths, raw hashes, physical statuses, tracked states,
  and Git blobs plus the manifest-construction algorithm and aggregate digest;
- all six exact strict resolver outcomes and diagnostics;
- historical commit `9373c5231`, its ancestry proof, four exact blobs/hashes,
  v007 report hash, v008 verdict hash, and the later-current source/test drift
  disposition;
- WI-5881 and WI-5825 exact independent report/verdict/capability/receipt
  identities and executed dependency tests;
- exact quarantine/controller/event/capability/receipt/test/work-item row keys;
  and
- zero legacy-file, source/test, Git/index, dispatcher/TAFE, credential,
  deployment, release, external-system, and unrelated-row mutation.

Original author metadata and current recovery invoker metadata remain separate.
Ordinary publication author-session-equals-claim-session enforcement remains
unchanged; only the independently VERIFIED reservation-aware recovery path may
preserve the original author while separately validating the current invoker.

## Timer, Parallelism, Append-Only, And Git Disposition

All waits, lock bounds, retry policies, claim TTLs, throttles, fan-out, and
concurrency limits come from the centralized configuration SoT owned by Timer
Governance/WI-5858. This incident introduces no hard-coded duration, sleep,
repository-wide lock, global serialization role, or global leader. Only short
exact-row reservation/event/capability/receipt/finalization transactions
serialize; preparation, validation, unrelated claims, and unrelated
publications remain parallel.

All 35 bridge artifacts remain at their current paths and raw bytes. The
service adds only append-only metadata/events and later numbered artifacts on
this fresh controller thread. No archive copy is created because there is no
same-number replacement and no need to remove an origin. No legacy file is
deleted to make the strict parser pass.

No Git operation, index mutation, lock classification/removal, staging,
commit, push, or history rewrite belongs to WI-5904. The foreign
`.git/index.lock` remains outside scope and untouched. Dispatcher and TAFE are
deliberately disabled for repairs and remain unactivated and unmodified.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — strict status/role/transition authority,
  governed publication, independent review, and immutable-history handling.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` — terminal provenance must be proved by a
  valid append-only chain, not a physical first-line status alone.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every evidence, reservation, claim,
  capability, receipt, registry, work-item, and test predicate is re-read from
  current canonical services.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — the
  recovery claim remains bound to this exact controller document and row scope.
- `DCL-SESSION-ROLE-RESOLUTION-001` — author, recovery invoker, and reviewer
  roles derive from exact session envelopes and remain distinct.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current
  membership and list-free PAUTH are revalidated at each effect boundary.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, WI,
  and exact service target are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing links
  and scope separation precede independent review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11822 maps every
  exact preservation, strictness, receipt, authority, and nonimpairment
  predicate.
- `GOV-ARTIFACT-APPROVAL-001` — project PAUTH does not waive formal record,
  claim, packet, report, test-result, verdict, or finalization gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — invalid evidence, dependencies,
  reservations, results, reports, reviews, and corrections remain durable.
- `GOV-STANDING-BACKLOG-001` — WI-5316, WI-5370, WI-5825, WI-5858, WI-5879,
  WI-5881, WI-5898, and WI-5904 retain nonduplicated ownership.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — unrelated rows, claims, bridge
  threads, current source/tests, and harness work remain unchanged.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — recovery uses
  independently VERIFIED deterministic services, not session lore or raw SQL.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every evidence and service SoT
  path remains inside `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native Windows execution
  self-enforces exact GO/claim/start and governed-writer boundaries.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — prior NO-ACTION carriers remain
  historical; this strict controller does not reinterpret them as closure.

## Prior Deliberations

- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — active parent
  project authorization, not legacy work-item approval state, is controlling.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — earlier controlling
  project-level approval decision.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  whole-project authorization and active v2 repair.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — exact
  row/path CAS and unrelated-worker parallelism, not a global leader.
- `DELIB-202667722` — timer and concurrency configuration is centralized.
- `bridge/gtkb-wi5316-frozen-modernization-rc-contract-001.md` through v008 —
  exact original proposal, review, implementation-report, and verdict evidence.
- The five repair/withdrawal carrier chains in the deduplication table — exact
  immutable correction attempts and their nonoverlapping dispositions.
- `bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-005.md`
  and `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-006.md`
  — current generic dependency heads; neither is yet implementation-complete or
  independently VERIFIED.
- `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-005.md` and
  `bridge/gtkb-wi5898-wi5741-invalid-terminal-chain-repair-001.md` — separate
  incident-consumer precedents whose physical replacement scope is not copied.

## Owner Decisions / Input

No new owner decision is requested. WI-5904 has active exact membership in the
active list-free authorized project. Existing owner direction requires
project-level approval inheritance, append-only evidence preservation,
parallel SoT access, generous externally configured waits, and disabled
dispatcher/TAFE. Independent bridge review, exact claims, schema-v3 start,
factual reporting, test-result evidence, independent verification, and
receipt-backed finalization remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. WI-5904, TEST-11822, the exact 35-file
manifest, six resolver outcomes, reachable historical commit/blobs, current
project/PAUTH, and the WI-5881/WI-5825 dependency contracts fully determine the
incident. No new generic service, physical archive, source/test edit, role,
status, timer policy, or owner choice is needed before independent review.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO, independently VERIFIED WI-5881 and WI-5825, exact claim/start, by-reference reservation, receipt-backed v003 report, independent v004 VERIFIED, and atomic terminal linkage.",
  "baseline": {
    "original": "physical v008 VERIFIED but strict-invalid at v002",
    "carrier_count": 6,
    "evidence_file_count": 35,
    "evidence_manifest_sha256": "E0170F5618D2215309C0EFCB7CAA4431562E50FFD8818AA8D8B39B99E3C4162F",
    "historical_commit": "9373C523164ECFA8A2ACADFE4C6E7FD1DCB008EE",
    "generic_dependency": "WI-5881 v005 REVISED; not independently VERIFIED",
    "receipt_dependency": "WI-5825 v006 GO; not independently VERIFIED"
  },
  "before_behavior": "Physical terminal-looking files and malformed repair chains cannot supply strict terminal provenance, while the backlog completion row cites the invalid original chain.",
  "after_behavior": "A fresh strict and receipt-complete controller binds the historical implementation snapshot and all legacy bytes by reference, quarantines invalid carriers as evidence-only, and appends correct completion provenance without moving any legacy file.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, active PAUTH v2, strict controller lifecycle, independently VERIFIED WI-5881/WI-5825 services, governed service rows, and TEST-11822.",
  "essential_context_preservation": "Preserve all 35 exact bytes and Git identities, six carrier dispositions, historical snapshot blobs, current-source drift distinction, dependency ownership, row-level parallelism, and the no-dispatcher/TAFE/Git boundary.",
  "obsolete_guidance_disposition": "The two strict-valid withdrawal carriers stay closed; four strict-invalid carriers are evidence-only and receive no further append. The tracked-file archive/delete lane remains retired.",
  "history_preservation": "No legacy file moves or changes; only append-only service events, a fresh numbered controller chain, and new work-item/test linkage versions are added.",
  "provenance": "WI-5904; TEST-11822; WI-5316; WI-5370 carrier manifest; WI-5881; WI-5825; WI-5879; WI-5898; DELIB-202667724; DELIB-202667732; DELIB-202667722; project-authorization inheritance decisions.",
  "self_descriptive_naming": "Use evidence manifest, evidence-only quarantine, strict recovery controller, historical snapshot binding, publication capability, consumed receipt, and terminal linkage.",
  "expected_result": {
    "legacy_files": "35 files byte-identical at unchanged paths",
    "controller": "fresh strict v001 GO v002 report v003 VERIFIED v004 chain",
    "receipt": "exact v003 and v004 capability/receipt identities are durable and consumed once",
    "work_items": "WI-5316 completion evidence and WI-5904 terminal state append only after independent v004",
    "test": "TEST-11822 PASS only after all live predicates",
    "scope": "only exact service-owned incident rows change"
  },
  "hard_invariants": [
    "WI-5881 and WI-5825 are independently VERIFIED and receipt-complete before incident mutation",
    "All 35 legacy file bytes, paths, tracked states, and Git blobs remain unchanged",
    "The historical candidate is evaluated from reachable commit 9373c5231, not substituted with current source/test bytes",
    "Only the fresh strict controller may become completion authority; invalid carriers remain evidence-only",
    "Only exact receipt consumption permits TEST-11822 PASS and work-item completion linkage",
    "No hard-coded timer, global leader, raw SQLite, Git/index, dispatcher/TAFE, source/test, archive/delete, credential, deployment, release, or unrelated-row mutation"
  ],
  "fail_closed_conditions": [
    "Dependency not independently VERIFIED or shared targets/claims not closed",
    "Any manifest, resolver, historical commit/blob, role, project, PAUTH, claim, start, capability, receipt, or target-row drift",
    "Ambiguous publication/finalization result or exact-row collision",
    "Missing independent v004 or any attempt to treat a physical legacy status as strict authority"
  ],
  "rollback": {
    "instructions": "Before reservation, no incident mutation exists. After reservation, preserve append-only events and use only the generic governed abort before capability mint. After controller publication, correct forward through higher controller versions; never alter legacy files or erase consumed receipts.",
    "verification": "Re-run dependency receipts, strict controller resolution, full manifest, six legacy diagnostics, historical blob hashes, row/event/capability/receipt readbacks, TEST-11822 and work-item histories, and no-touch checks."
  }
}
```

## Specification-Derived Verification Plan

| Requirement | Required executed evidence |
|---|---|
| Generic reservation and claim fence | exact independently VERIFIED WI-5881 report/verdict/receipt and executed TEST-11809 results |
| Capability and receipt recovery | exact independently VERIFIED WI-5825 report/verdict/receipt and crash/ambiguous-publication recovery results |
| Complete immutable evidence | recomputed 35-line manifest and aggregate SHA-256 match; every raw file, path, length, Git state, and blob is unchanged |
| Carrier deduplication | six resolver readbacks reproduce four exact failures and two strict-valid `WITHDRAWN` terminals; no undisclosed carrier exists |
| Historical candidate identity | commit `9373c5231` remains reachable and the four exact blobs/hashes match v007/v008 evidence |
| Current-versus-historical truth | current manifest is separately identified; current checker/test drift is not rewritten, restored, or attributed to WI-5904 |
| Controller strictness | v001 proposal, v002 independent GO, v003 factual report, and v004 distinct-session VERIFIED form one strict-valid chain |
| Receipt completeness | exact v003/v004 capabilities and receipts are canonical, single-consumed, and bind the full reservation tuple |
| Work-item/test integrity | TEST-11822 PASS and new WI-5316/WI-5904 completion versions appear only in successful atomic terminal finalization |
| Row containment | changed-row census contains only the declared controller/quarantine/event/capability/receipt/test/work-item cohorts |
| Nonimpairment | no legacy file, source/test, foreign claim/packet, unrelated DB row, Git/index, dispatcher/TAFE, credential, deployment, release, or external system changes |
| Parallelism and timers | unrelated row/slug work remains concurrent and no new literal wait/TTL/retry/throttle/fan-out/concurrency value exists |

TEST-11822's result packet must preserve exact dependency report/verdict/
receipt hashes, proposal/GO/report/verdict hashes, reservation/event identities,
the full evidence manifest and aggregate digest, all six resolver diagnostics,
historical commit ancestry and blob hashes, current-source drift evidence,
capability/receipt readbacks, exact changed-row census, WI-5316/WI-5904
history readbacks, and all no-touch checks.

## Acceptance Criteria

1. WI-5881 and WI-5825 are implemented, factually reported, independently
   VERIFIED, receipt-complete, and their shared source/test targets and claims
   are closed/clean before WI-5904 mutation.
2. The reservation durably binds the exact controller authority, all 35
   evidence files, aggregate manifest digest, six resolver outcomes,
   historical snapshot tuple, dependency receipts, claim/start/owner epoch,
   and exact service-row cohort before v003 publication.
3. All 35 WI-5316-related bridge artifacts remain byte-identical at their
   existing paths; no archive, delete, rename, normalization, Git ownership,
   or same-number replacement occurs.
4. The four strict-invalid carriers remain evidence-only quarantined inputs;
   the two strict-valid `WITHDRAWN` carriers remain closed; no legacy thread is
   appended or presented as implementation authority.
5. The historical implementation candidate is proven from reachable commit
   `9373c5231` and its four exact blobs. Later current source/test bytes remain
   untouched and are not misrepresented as the historical candidate.
6. Only the durably stored exact v003 report is published; any ambiguous
   outcome is resolved through WI-5825 canonical recovery with no blind retry.
7. A distinct Loyal Opposition session publishes exact receipt-bound v004
   `VERIFIED`; the fresh controller resolves strict-valid and current.
8. Atomic terminal finalization consumes the exact receipt once and appends
   TEST-11822 PASS plus WI-5316/WI-5904 completion linkage only after v004.
9. The exact changed-row census contains only the declared incident cohorts;
   unrelated DB rows, claims, packets, capabilities, receipts, tests, work
   items, and slugs remain parallel and unchanged.
10. WI-5904 copies or reimplements no generic WI-5881/WI-5825 behavior and no
    physical-replacement WI-5879/WI-5898 incident scope.
11. No hard-coded timer/TTL/retry/throttle/concurrency value, global leader,
    whole-DB lock/hash, raw SQLite, source/test edit, Git/index operation,
    dispatcher/TAFE activation or mutation, credential action, deployment,
    release, push, history rewrite, external mutation, or destructive cleanup
    occurs.

## Risks And Rollback

- **Dependency drift:** any WI-5881/WI-5825 report, verdict, receipt, target,
  claim, or API drift returns WI-5904 to revision before mutation.
- **Evidence drift:** any change to the 35-file manifest, six resolver results,
  historical ancestry, or four blob hashes blocks reservation/finalization.
- **Shared DB contention:** only exact rows/CAS serialize. Typed contention or
  currentness failure pauses safely; it never triggers raw SQL or blind retry.
- **Ambiguous publication:** use WI-5825 capability/receipt readback only;
  never publish a second numbered candidate based only on an exception.
- **Rollback:** before reservation there is nothing to undo. After reservation,
  preserve events and use governed abort only before mint. After publication,
  correct forward through later controller versions; legacy evidence and
  consumed receipts are never erased.

## Candidate Pre-Filing Gates

Applicability, mandatory clause, strict candidate, credential/pattern, and
writer-compliance audits must pass against these exact stable bytes. Live
filing additionally requires current WI/project/PAUTH/test/dependency/carrier
readback, physical v001 absence, null claim, unchanged manifest and historical
tuple, exact target-row overlap clearance, a fresh proposal-draft claim, the
governed writer, and canonical path/status/hash/claim-consumption readback.

## DISARM — Implementation Boundary

This proposal authorizes no reservation, DB-row mutation, evidence quarantine,
test result, work-item update, source/test edit, legacy bridge-file mutation,
Git/index operation, dispatcher/TAFE operation, credential action, deployment,
release, or external-system mutation. Both dependencies, independent GO,
fresh exact claim/start, currentness/overlap gates, factual report, independent
verification, and receipt-backed finalization remain mandatory.

## Files Expected To Change

- `groundtruth.db` through only the exact governed service-owned row cohorts
  declared above.

Later numbered v003/v004 controller artifacts are governed report/verdict
publications, not implementation target globs and not authority to modify any
legacy WI-5316 carrier.

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
