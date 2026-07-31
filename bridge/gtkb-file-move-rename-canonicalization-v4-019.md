REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5640 Registry Admission And Deterministic Preflight Implementation Report

bridge_kind: implementation_report
Document: gtkb-file-move-rename-canonicalization-v4
Version: 019
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-018.md
Approved proposal: bridge/gtkb-file-move-rename-canonicalization-v4-013.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "groundtruth.db", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | metadata | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: feat:

---

## Revision Delta

This is a report-evidence-only correction responding to v4-018. No
implementation postimage, registry record, target path, runtime preflight, PAUTH,
or commit recommendation changes.

v4-016 F1 remains corrected: the `groundtruth.db` exclusion stays outside
`## Files Changed`. This revision corrects five malformed 65-character digest
transcriptions in v4-015/v4-017 and replaces the two previously unspecified
retention aggregates with a fully specified canonical algorithm. It also aligns
the role-eligibility check with the actual `REVISED` first line and replaces the
stale fixed bridge-file count with a finalization-time derivation rule.

The malformed v4-015 Applicability Preflight `packet_hash` was removed in
v4-017 rather than corrected. This revision records that disposition explicitly
and relies on fresh exact-candidate preflights at publication; it does not reuse
the malformed value.

## Implementation Claim

The exact lifecycle-repair, registry-admission, public-inventory, recovery, and
read-only-preflight slice approved by v4-013/v4-014 is implemented. This report
requests independent verification of that bounded slice only. It does not claim
that Stage B, the 183-file reference rewrite plan, WI-5640 terminal resolution,
or the overall file-move program is complete.

The implementation:

1. Reapplied the ten reviewed source/test postimages through one exact observed
   mutation, then applied the one Ruff-only `db.py` formatting correction through
   a second exact observation.
2. Preserved the WI-5441 terminal-reopen policy while adding the separately
   authorized WI-5640 repair path, public registered-artifact inventory API, and
   journal-proven registry forward-completion behavior.
3. Registered 167 previously missing manifest members plus the one load-bearing
   WI-5640 policy file through one canonical 168-record transaction. The
   canonical declaration, packaged declaration, and SQLite projection now form
   one coherent, current 313-record generation.
4. Ran two fresh-process read-only migration preflights. Both produced the same
   approval-relevant binding and correctly stopped with 485 blockers, 311
   unresolved references, and 183 proposed writes. No Stage B write ran.
5. Retained all 90 obsolete sources and all 90 canonical destinations. No source
   deletion, registry-member removal, commit, push, release, deployment,
   dispatcher mutation, raw SQL, or history rewrite occurred.

## First-Line Role Eligibility Check

PASS. Session context `019f9b59-52a0-75b2-9973-bd5601f98e9f` is the Prime
Builder authoring this report-only revision. The implementation and v4-017 report
were performed under Prime Builder session context
`019f863a-acd3-7320-80c0-1831f0936cc0`, which held the matching
GO-implementation claim. v4-014 is an independent Loyal Opposition GO from
session context
`41395f7c-b6e7-4cc8-a5bc-37c2b528f816`. This file carries Prime Builder status
`REVISED`; it does not author a GO, NO-GO, or VERIFIED token.

Implementation packets were issued from exact proposal v4-013 and GO v4-014.
Observed source and registry mutations were bound to packet
`sha256:213b3869c1e206f305e41a07a15d4a90e7f4f1c3c626f11d90b883f387f698a3`;
the observed Ruff correction used
`sha256:2e4cb360b01d44dbf8a520c09ff551ab5a0231e22bacc214fda599c3ef5d0d22`.
After the governed claim extension, the publication-context packet is
`sha256:301b4949f78334a4246ea17ea29d4dd4a415b9d8a73cbcff58f5a78f058e30df`.
All three carry the same fifteen target paths and PAUTH.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- Owner rule: `config/registry/sot-artifacts.toml` is the ultimate SoT for GT-KB
  artifact membership. Every load-bearing artifact must be registered;
  registered move/rename/delete operations require mechanical authorization and
  transactional registry maintenance; removal requires oversight.
- Owner sequencing: WI-5441 owns general registry completeness and enforcement.
  WI-5640 owns only its exact transactional admission and migration work.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` controls retention. All old
  sources remain until repeated verification and a separately authorized
  deletion operation.
- The owner manually drives Loyal Opposition reviews. No LO sub-agent or
  dispatcher was activated by this Prime Builder session.

No new owner decision is required to review this bounded implementation report.

## Prior Deliberations And Dependencies

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - obsolete-source retention.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` -
  independently VERIFIED registry control plane consumed by this slice.
- `bridge/gtkb-file-move-rename-canonicalization-v4-010.md` and v4-012 - prior
  GO conditions carried forward.
- `bridge/gtkb-file-move-rename-canonicalization-v4-013.md` - exact revised
  implementation proposal.
- `bridge/gtkb-file-move-rename-canonicalization-v4-014.md` - controlling GO.
- `bridge/gtkb-file-move-rename-canonicalization-v4-016.md` - independent
  NO-GO confirming the implementation evidence and requiring this report-only F1 correction.
- `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` - advisory
  follow-up only; it is not treated as implementation authority here.

## Registry Transaction Evidence

The deterministic batch builder independently checked the 90-row CSV as 33 hook,
38 rule, and 19 agent-control mappings. It found 180 unique, tracked, present
locators: 13 already registered and 167 missing (79 sources and 88 destinations).
The one missing load-bearing policy record brought the canonical transaction to
168 additions.

- Missing-path set digest:
  `sha256:92baca678bd277f8b0aa3c76576b1bcae48e07d83cefdcc64e58b9aa16ae31b4`
- Singleton policy declaration digest:
  `sha256:6274a9af4ded39d66445f30bb0ebbbebd32a700fc03ef4db3e6a4fddc645521b`
- Canonical batch digest:
  `sha256:ec09f7a2901b6a064062d1c3d2d85be650670217652119867ae7d157932c74c4`
- Journal: `SOTTXN-FBA582E3F96443558549BD1C1B2CD1FE`
- Receipt:
  `sha256:a931530a8dfc52f9925e345f975ccca07eca53f889733acb91869c05fb14abb5`
- Declaration and packaged-mirror digest:
  `sha256:cd6ff2d4b5fed0898442159b152127301fd9a33316db2881a5769328e72f8a44`
- Projection digest:
  `sha256:90240e8d96613020245277d762eac2aab00adbaf6cbcdffbf8243e798be4c1ae`
- Generation digest:
  `sha256:a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7`

Independent post-transaction verification reports `record_count: 313`,
`coherent: true`, `current: true`, canonical/packaged byte equality, 168/168
exact batch resolutions, 180/180 manifest-locator resolutions, and exact policy
ID `wi5640-config-file-reference-migration-wi5640-toml`. Zero stale or missing
revisions were reported.

Scope disclosure: `gt registry validate --json` still reports `valid: false`
because global `reverse_coverage_incomplete` remains WI-5441 scope. This report
claims transaction coherence/currentness for the bounded WI-5640 admission, not
global registry membership completeness.

The ten postimage reapplications were recorded under event
`018b4e94-a5ca-463a-b1ba-e747d4c68092` with revisions:

- `SOTREV-9BAF9C0438B94543B693FE625F448441`
- `SOTREV-2728EFF6CE9F4DC5BFF08A7E5AA1D73D`
- `SOTREV-D9F6C1CC47634A7790F1CCE7E292E8DF`
- `SOTREV-C65F6879F07D4D7D8D8AF9AC46CF7030`
- `SOTREV-6C7C046A9AA740148EC93B6AE90DF805`
- `SOTREV-610DBC80BA564E4CBF42EC233BB42776`
- `SOTREV-3EC859F11274499686892AD188B542DE`
- `SOTREV-B9A225F811DC47918EE21B3E4E71C340`
- `SOTREV-04DDCFB79C8B44A980858924F88B557F`
- `SOTREV-D71A0D4AD6914FBB85262930A7E20C0B`

The Ruff-only `db.py` correction was separately observed under event
`5bb5a603-6f5e-4335-a5bb-aa291040be21`, revision
`SOTREV-61DD3334E6D24625B0397D0EBD2D3EC4`, postimage
`sha256:d2406278919d2789f90e9afab0f2f50bb798a9497c17f266ed378992af52416c`.

## DB Authorization Posture

The implementation intentionally relocates terminal-reopen subject policy from
the DB primitive to the governed CLI caller:

- `KnowledgeDB.reopen_terminal_work_item` validates authorization shape: a
  non-empty string policy, exact/subset semantics, metadata validity, optimistic
  version match, and terminal-state transition. It no longer hard-codes WI-5441
  or any bridge subject identity.
- The current repository has exactly one production call site:
  `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py:402`; the primitive is
  defined at `groundtruth-kb/src/groundtruth_kb/db.py:4984`. This sole-caller
  status is an observed repository fact, not a structural restriction against a
  future production caller.
- The caller constrains subjects through `_TERMINAL_REOPEN_POLICIES`. WI-5441
  still requires its original PAUTH, v007/v008 strict evidence, controlling v008
  GO, metadata checks, and subset semantics. WI-5640 has its separate exact
  eight-thread policy and v4-011/v4-012 strict authority.
- `test_reopen_terminal_work_item_requires_explicit_non_empty_path_policy`
  proves that an empty caller policy fails closed.

This disclosure is the v4-012/v4-014 F1 condition. It does not claim that the DB
primitive itself constrains policy subject identity.

## Lifecycle Evidence

`gt backlog show WI-5640 --json` still reports version 3, `resolution_status:
open`, and `stage: implementing`, with exactly the eight approved related bridge
paths. The canonical `KnowledgeDB.list_events` API returns exactly one
`wi_reopened` event for WI-5640: event
`86a7ebd5-0276-408e-b239-5d61aefbe49f`, artifact version 3,
2026-07-26T10:01:33Z. The lifecycle repair was not repeated.

## Deterministic Preflight Evidence

Two sequential fresh Python processes ran `preflight` against the live root.
Each exited with the intentional blocked status and produced exactly:

- inventory entries: 14,102
- reference hits: 1,429
- unresolved residuals: 311
- proposed writes: 183
- blockers: 485
- plan:
  `sha256:fe29f0817601f0d1fcd380cbd2904b61da58b28db5559787de4f2024ec79eba6`
- closure fingerprint:
  `sha256:ba4ea771600a709aba3a31a3c091c8f6c15a70113e27eb3c3c4b99ce20755c5d`

The two `binding.json` files are byte-identical with digest
`sha256:521635a547cf3c7a5306e513fdba5acac51464c10914ce05e5ebab1ea7edff5d`.
Required bindings are identical:

- manifest/CSV:
  `sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`
- policy:
  `sha256:9241fa778f4117262c6e4e020af616ccccaa91a1d4ae0cd35be93403c141f5fc`
- scanner/engine:
  `sha256:959cc9b4d7ef8f12c9ab603702e5c464e362a965d1278f9c14c59ef3a9087806`
- physical inventory:
  `sha256:b33519524d49791297bc1c5646e7fc32ba909a64b7a0bec37c84f63c7273cc4e`
- operation manifest:
  `sha256:e8dfe1699c7ff40f31d6491e3c78343c4bac1f39bd6eac5d6b9991ca8526dab0`
- registry generation and receipt: the exact current 313-record values listed
  in Registry Transaction Evidence.

The raw full-observation/report byte hashes are not binding fields and differ
between runs because a governed work-intent extension changed non-authoritative
runtime state between the two processes. No approval-relevant binding changed.
Each process independently required a coherent current registry receipt before
expanding the public registered-artifact inventory.

Generator observations were also repeatable:

- Codex adapters: PASS, 44 current.
- Rule compatibility projections: PASS, 38 current.
- Harness parity command: exit 0, with its approved Stage B disposition retained.
- Antigravity adapters: exit 1, seven proposed updates.
- API adapters: exit 1, six proposed updates.
- Cursor adapters: exit 1, planned generated updates.
- Goose API and manifest checks: exit 1 under the typed
  `blocked_by_shared_manifest_owner_conflict` disposition.

These non-clean generator results are represented in the 183-write exact plan;
they were not applied under this GO.

## Source Retention Audit

A deterministic `Import-Csv` plus `Test-Path`/`Get-FileHash` pass recomputed all
90 source and destination paths from the CSV:

- sources present: 90; missing: 0
- destinations present: 90; missing: 0
- sorted source path+byte digest:
  `sha256:073e9420fa30502ababde61a8da5e15c9a4f9ae145c9e5a296cc8560086ff7c0`
- sorted destination path+byte digest:
  `sha256:e1351fc5a533acf77246a4d5486911b3849d16fd0e58c599344ccacd7cfc7858`

Aggregate algorithm: SHA-256 over UTF-8 compact canonical JSON with sorted keys.
Each array is sorted by repo-relative POSIX path and each element is exactly
`{"path":<path>,"sha256":<file-byte-sha256>}`. The recomputation and report-integrity command
is `.gtkb-state/file-reference-migration/wi5640/verify_report_digest_evidence_v4_019.py`.

The 180/180 registry resolution check independently covers the same locators.
No obsolete source was removed.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Canonical 168-record transaction plus post-transaction 313-record resolver audit. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Batch simulation and `test_registry_control_plane.py`: 26 passed. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Canonical/packaged byte equality, exact projection receipt, 26 registry tests. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | One journaled transaction, eleven observed revisions, registry fault matrix. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Two blocked read-only preflights, 90+90 retention audit, lifecycle and migration suites. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict v4 lifecycle resolution, independent v4-014 GO, matching live claim and packets. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | v4-013/v4-014 project, WI, and PAUTH linkage plus report preflight. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All v4-013 linked specifications carried forward here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping and every exact observed result below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact fifteen-target implementation packets under active project PAUTH. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact 475-node governance suite plus packet-time PAUTH decisions. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | WI-5441 VERIFIED control plane consumed before registry admission; lifecycle repair not repeated. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Registry, inventory, lifecycle, migration, and governance suites executed. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Governed report helper will add canonical author metadata at publication. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Full-root classifier/preflight preserved application boundaries and nine-worktree observations. |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short` shows exactly 13 in-scope tracked changes; excluded bridge audit artifacts remain append-only. |
| `GOV-STANDING-BACKLOG-001` | WI-5178 residuals and aggregate-drift follow-up remain explicit and non-waived. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Registry transaction, receipts, revisions, runtime evidence, and this report preserve every material action. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Same governed artifact chain; no informal mutation substitutes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-5640 lifecycle/event audit and this non-terminal implementation report. |

## Commands Run

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-file-move-rename-canonicalization-v4 --session-id 019f863a-acd3-7320-80c0-1831f0936cc0 --expires-minutes 60`
- `python .gtkb-state/file-reference-migration/wi5640/reapply_parked_postimages.py --expected-packet-hash sha256:213b3869c1e206f305e41a07a15d4a90e7f4f1c3c626f11d90b883f387f698a3`
- `python .gtkb-state/file-reference-migration/wi5640/build_registry_batch_v4_014.py`
- `gt registry register --batch-file .gtkb-state/file-reference-migration/wi5640/registry-admission-v4-014.json --bridge-id gtkb-file-move-rename-canonicalization-v4 --session-id 019f863a-acd3-7320-80c0-1831f0936cc0 --start-packet-hash sha256:213b3869c1e206f305e41a07a15d4a90e7f4f1c3c626f11d90b883f387f698a3 --pauth-id PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE --changed-by prime-builder/codex --change-reason "WI-5640 v4-014: atomically admit 167 reviewed manifest locators plus the exact load-bearing migration policy record."`
- `python .gtkb-state/file-reference-migration/wi5640/verify_registry_admission_v4_014.py --expected-receipt sha256:a931530a8dfc52f9925e345f975ccca07eca53f889733acb91869c05fb14abb5 --expected-declaration sha256:cd6ff2d4b5fed0898442159b152127301fd9a33316db2881a5769328e72f8a44 --expected-projection sha256:90240e8d96613020245277d762eac2aab00adbaf6cbcdffbf8243e798be4c1ae`
- `python .gtkb-state/file-reference-migration/wi5640/observed_ruff_format_db.py --expected-packet-hash sha256:2e4cb360b01d44dbf8a520c09ff551ab5a0231e22bacc214fda599c3ef5d0d22`
- `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_inventory_string_scan.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_generate_cursor_skill_adapters.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_governance_mutation.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_project_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`
- `ruff check <the ten changed Python source/test files>`
- `ruff format --check <the ten changed Python source/test files>`
- `python scripts/gtkb_file_reference_migration.py preflight --project-root E:\GT-KB --policy config/file-reference-migration/wi5640.toml` (two fresh processes)
- `python .gtkb-state/file-reference-migration/wi5640/verify_report_digest_evidence_v4_019.py --report <candidate> --expected-report-sha256 <sha256>`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4 --content-file <candidate>`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4 --content-file <candidate>`
- `rg -n "reopen_terminal_work_item\(" groundtruth-kb/src scripts config`
- `gt backlog show WI-5640 --json`
- Canonical `KnowledgeDB.list_events(event_type="wi_reopened", artifact_id="WI-5640", artifact_type="work_item")` read.

## Observed Results

- Lifecycle/CLI DB suite: 145 passed, 1 warning.
- Registry control-plane fault matrix: 26 passed.
- Public inventory suite: 9 passed.
- Migration/generator suite: v4-015 observed 66 passed, 1 warning; v4-016 independently observed 65 passed, 1 deselected, 1 warning on a host without symlink privilege.
- Exact governance suite: v4-015 observed 475 collected, 471 passed, 4 failed, 2 warnings; v4-016 independently reproduced the same 475/471/4 result with 1 warning.
- Ruff: all checks passed; 10 files already formatted after the observed `db.py` correction.
- Two migration preflights: both blocked with identical required bindings and no Stage B writes.
- Digest integrity: all report SHA-256 tokens are exactly 64 lowercase hex characters; producer-derived batch, generation, and db.py values match live evidence.
- Registry postcheck: 313 records, coherent/current, 168 exact batch resolutions, 180 manifest resolutions.

The four exact governance-suite failures are unchanged WI-5178 residuals:

- `test_work_intent_acquire_denial_creates_no_claim`
- `test_work_intent_extension_denial_leaves_claim_unchanged`
- `test_work_intent_renew_denial_leaves_go_claim_unchanged`
- `test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`

They are non-waiving. They prohibit Stage B authorization and terminal WI-5640
verification; they do not erase the completed v4-013/v4-014 registry/preflight
slice. This report asks Loyal Opposition to verify only that bounded slice.

## Files Changed

- `config/file-reference-migration/wi5640.toml`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_backlog_update_cli.py`
- `groundtruth-kb/tests/test_db.py`
- `groundtruth-kb/tests/test_inventory_string_scan.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `scripts/gtkb_file_reference_migration.py`

## By-Reference Runtime Evidence Exclusion

`groundtruth.db` is by-reference runtime evidence only. It is deliberately absent
from `## Files Changed` and must remain absent from every finalizer include list.

## Finalization Include Derivation

No fixed count of append-only bridge files is asserted. At terminal finalization,
derive the audit-trail include set from the live untracked numbered files matching
`bridge/gtkb-file-move-rename-canonicalization-v4-*.md` at execution time, plus
any separately governed related advisory selected by finalizer policy. These audit
entries are distinct from the exact 13 implementation paths harvested from
`## Files Changed`; that harvest excludes `groundtruth.db`.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: this slice adds the governed registry control-plane,
  public inventory, lifecycle policy, recovery, and deterministic preflight
  behavior needed to continue WI-5640.
- No commit is authorized or requested by this report.

## Acceptance Criteria Status

- [x] Reapply all ten reviewed postimages through exact observation.
- [x] Preserve the original WI-5441 terminal-reopen policy and tests.
- [x] Admit the exact 167 missing manifest records plus one policy record through one canonical transaction.
- [x] Produce one coherent/current 313-record canonical, packaged, and projected generation.
- [x] Resolve all 180 manifest locators and the exact policy ID through the canonical reader.
- [x] Exercise the journal-proven recovery branch and unknown/tampered-state failures.
- [x] Run two fresh-process read-only preflights with identical required bindings.
- [x] Retain all 90 obsolete sources and all 90 destinations.
- [x] Preserve Stage B, deletion, terminal closure, commit, release, and deployment prohibitions.
- [x] Preserve the v4-016 F1 correction and repair all blocking v4-018 report-form findings without changing implementation.

## Risk And Rollback

Residual risk is explicit rather than waived:

- The DB primitive validates policy shape but no longer constrains policy subject
  identity; the governed CLI is presently its sole production caller.
- Stage B remains blocked by 485 plan blockers, 311 unresolved references, three
  required-clean generator drifts, two typed Goose conflicts, and four WI-5178
  governance failures.
- Raw full-observation evidence includes non-authoritative runtime state and is
  therefore not byte-stable across the intervening governed claim extension;
  every reviewed binding is byte-stable.

Rollback must be repair-forward and separately authorized. Source/test
postimages have registered preimages and exact revision evidence; the registry
transaction has its journal and receipt. Because registry-member removal requires
oversight, neither a raw file restore nor an ad hoc 168-record removal is an
authorized rollback. All 90 old sources remain available as compatibility
fallbacks, and no Stage B consumer was changed.

## Applicability Preflight

The exact pending v4-019 candidate was rerun through
`bridge_applicability_preflight.py` before governed publication.

- preflight passed: true
- missing required specifications: none
- missing advisory specifications: none
- unclassified target paths: none
- blocking errors: none
- author metadata warnings: none

v4-016 independently reached the same clean applicability result against the
reviewed implementation state. The governed bridge writer reruns this gate on
the exact bytes before any bridge file reaches disk.

## Clause Applicability (Slice 2; Mandatory Gate)

The exact pending v4-019 candidate was rerun in mandatory mode before
governed publication.

- clauses evaluated: 5
- must apply: 4
- may apply: 1
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- mandatory-mode exit: 0

v4-016 independently reproduced the same zero-gap result. The governed writer
reruns the mandatory clause gate on the exact candidate bytes before writing.

## Loyal Opposition Asks

1. Confirm v4-016 F1 remains corrected, all v4-018 digest findings are repaired, and the bounded v4-013/v4-014 implementation, transaction, currentness,
   lifecycle non-regression, source retention, and two preflight bindings.
2. Confirm the DB subject-policy disclosure, sole production caller, and empty
   policy negative test satisfy the carried v4-012/v4-014 conditions.
3. Return VERIFIED only for this bounded slice if the evidence holds. Return
   NO-GO with exact findings otherwise. Do not treat VERIFIED here as authority
   for Stage B, deletion, terminal WI-5640 closure, commit, release, or deployment.
