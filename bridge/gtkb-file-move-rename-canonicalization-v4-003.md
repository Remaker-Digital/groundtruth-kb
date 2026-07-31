NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; Codex Desktop interactive Prime Builder; role_source=transcript_init_keyword
author_metadata_source: explicit current-session filing metadata and matching live GO-implementation claim

# Stage A Implementation Report: Deterministic file-reference migration engine remains fail-closed

bridge_kind: implementation_report
Document: gtkb-file-move-rename-canonicalization-v4
Version: 003
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-002.md
Approved proposal: bridge/gtkb-file-move-rename-canonicalization-v4-001.md
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "platform_tests/fixtures/file_reference_migration/**", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Stage A now contains a deterministic, policy-driven migration engine; pure rule
and Cursor projection generators; fixtures; tests; and content-addressed runtime
evidence. It performs programmatic full-root inventory and scanning rather than
agent-directed recursive find/replace. It validates all 90 CSV rows, expands a
collision-checked obsolete-alias catalog, scans text and structured data,
inventories physical aliases, emits exact preimage/postimage payloads, retains
all obsolete sources, and fails closed when closure is not established.

The transaction layer was hardened with Windows handle-relative no-reparse
operations, namespace sentinels, no-replace target rename, content/identity
compare-and-swap checks, fsynced write-ahead journal semantics, crash-state
classification, compensation, rollback prevalidation, and final disk-state
verification. Focused fault-injection tests exercise those boundaries.

This is deliberately a non-terminal implementation report. The deterministic
plan is reproducible but remains blocked by unresolved semantic classification,
generator ownership, malformed structured files, and one required domain
operation. The current write set is not an apply candidate. Loyal Opposition
should return precise NO-GO correction conditions rather than VERIFIED if the
known blockers below are confirmed.

No migration `apply`, consumer mutation, database mutation, old-source deletion,
staging, commit, push, release, deployment, or dispatcher mutation occurred.
No child exact-plan proposal was filed.

## First-Line Role Eligibility Check

PASS. This report is a Prime Builder `NEW` post-implementation report. The
author session context is
`019f863a-acd3-7320-80c0-1831f0936cc0`, the same session bound to the live v4
GO-implementation claim and implementation-start packet. The report responds
directly to the immediate predecessor `v4-002` GO and uses exact undecorated
`Document`, `Version`, and `Responds to` metadata.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` remains controlling. All 90
obsolete source paths remain present. Deletion is not authorized and will
require a separate later proposal after repeated clean verification. No new
owner decision is required for review of this report.

## Prior Deliberations And Evidence

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - retain obsolete paths until repeated deterministic verification and separately authorize any deletion.
- `DELIB-202666274` - project-level modernization authority with bridge and independent-review controls.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md` - fail-closed incident evidence.
- `bridge/gtkb-file-move-rename-canonicalization-v4-001.md` - approved Stage A scope and acceptance contract.
- `bridge/gtkb-file-move-rename-canonicalization-v4-002.md` - independent Stage A GO.

## Files Implemented

- `scripts/gtkb_file_reference_migration.py`
- `scripts/generate_rule_compatibility_projections.py`
- `scripts/generate_cursor_skill_adapters.py`
- `config/file-reference-migration/wi5640.toml`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_generate_rule_compatibility_projections.py`
- `platform_tests/scripts/test_generate_cursor_skill_adapters.py`
- `platform_tests/fixtures/file_reference_migration/direct-forms.txt`
- `platform_tests/fixtures/file_reference_migration/segmented.py`
- `platform_tests/fixtures/file_reference_migration/segmented.ps1`
- `platform_tests/fixtures/file_reference_migration/structured.toml`

Runtime evidence and content-addressed plan/preimage/postimage payloads are under
`.gtkb-state/file-reference-migration/wi5640/**`. No out-of-scope repository
consumer was changed by this Stage A session.

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; project-authorization DCLs | v4 GO, live exact claim, and exact nine-target implementation-start packet checked before protected edits; main-v4 authority is rejected by `apply` | PASS for Stage A; no apply attempted |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001` | Sorted root inventory, Git-index hash binding, registered-worktree inventory, forbidden mutation roots, and final disk verification | PASS for observation; separate-worktree content observation remains a correction condition |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `applications/**` is classified as an observation-only boundary and excluded from mutation | PASS |
| Cross-harness parity specifications | Policy carries exact frozen 209-node baseline and six known failing node IDs; Stage B requires no new failures | Static contract implemented; latest full rerun not repeated in this checkpoint |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused Stage A suite and Ruff command below | PASS, 63/63; Ruff clean |
| Artifact/lifecycle specifications | Canonical plan, full-observation stream, complete blocker/exception ledgers, hashes, and strict v4 report metadata | PASS for evidence preservation; terminal verification not requested |

## Commands And Results

```powershell
python scripts/gtkb_file_reference_migration.py preflight
python scripts/gtkb_file_reference_migration.py preflight
python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py -q --tb=short
python -m ruff check scripts/gtkb_file_reference_migration.py scripts/generate_rule_compatibility_projections.py scripts/generate_cursor_skill_adapters.py platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py
```

- Focused suite: `63 passed in 12.96s`.
- Ruff: `All checks passed!`.
- Two clean-process preflights reproduced the exact same plan hash and closure
  fingerprint despite volatile runtime inventory counts of 3,822 and 3,820.
- Plan hash:
  `sha256:526303179d75b9be12c7ed71a477817f99fd1b21d78b1f5349c0c608c4623ec4`.
- Closure fingerprint:
  `sha256:4cb9788f1463aff84e8160f935869daaf710187782a08925fe3f53c6cb344c65`.
- Expected final closure fingerprint:
  `sha256:58bc26c27f3a7f779645dd1832ca26bb08ebbb36ea80642d3ac1778bc8b46de0`.
- Git index hash:
  `sha256:68b929ed9bf8fb68b268e71b3571ed4865fcb20e58ccba11f5755e6c5aa0c737`.
- CSV: 90 unique non-no-op rows; 33 hooks, 38 rules, 19 agent-control;
  `sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`.
- Current plan: 139 catalog entries, 43 inferred alias candidates, 2,998 alias
  occurrences, 702 structured occurrences, eight physical occurrences, eight
  planned operations, 4,062 reference hits, 484 proposed writes, 1,667
  unresolved residuals, 581 typed exceptions, and 2,769 blockers.

## Current Blocking Ledger

| Code | Count | Required deterministic correction |
| --- | ---: | --- |
| `UNRESOLVED_LIVE_REFERENCE` | 1,666 | Replace the over-broad bare-filename heuristic with typed executable-path, structured-scalar, Markdown-target, test-expectation, compatibility, diagnostic-prose, and historical-quotation categories; ambiguous cases remain blocking and hash-bound. |
| `ALIAS_OCCURRENCE_NOT_MATERIALIZED` | 519 | Render from scanner-produced non-overlapping spans; align JSON-escaped and directory-prefix boundaries; regenerate governed outputs through owners. |
| `ALIAS_CANDIDATE_UNDISPOSITIONED` | 296 | Add exact set-equal policy dispositions for all 43 inferred aliases; 24 with occurrences need reviewed rewrite/exception dispositions and 19 should assert absence. |
| `GENERATED_OUTPUT_NOT_MATERIALIZED` | 277 | Build two isolated projection roots and capture Codex, Antigravity, API/Goose, Goose-manifest, Cursor, rule, registry, dashboard, and parity outputs as exact payloads. |
| `GENERATOR_CHECK_FAILED` | 3 | Run checks against the simulated postimage root rather than the unchanged live root. |
| `GENERATOR_CHECK_BLOCKED` | 2 | Make `generate_goose_manifest.py` the sole owner of `.goose/skills/MANIFEST.json`; the API-to-Goose step owns adapters only. |
| `STRUCTURED_PARSE_FAILED` | 2 | Separately authorize repair of the malformed line 54 in both activity-envelope TOMLs, reconstructing the canonical list from clean HEAD and applying mappings. |
| `UNDECODED_REFERENCE_BYTES` | 2 | Read `.groundtruth/dashboard/gtkb-dashboard.sqlite` structurally and regenerate it through the dashboard owner; do not byte-edit it. |
| `ADAPTATION_NOT_APPLICABLE` | 1 | Match the actual chained Python path-component expression in the Bridge Axis helper. |
| `LIVE_SQLITE_REFERENCE_REQUIRES_DOMAIN_API` | 1 | Add a separately authorized append-only harness-domain operation changing harness H version 59 `capabilities_ref`, then regenerate and verify projections. |

The previous 31 wheel blockers are resolved: `.whl` files are scanned as ZIP
containers and the tracked prior-release modernization wheel is explicitly
immutable test input. The prior unreadable pytest-runtime blocker is also
resolved by treating pytest temporary roots as fixed observation boundaries.

## Advisory Spot Checks

Two read-only same-session advisory agents independently triaged the blocker
ledger. They did not edit files and did not issue formal verdicts. Their most
important confirmations were:

1. 1,377 of 1,666 unresolved references are unqualified bare-filename matches,
   so blanket replacement would be unsafe and semantically invalid.
2. The scanner and renderer have incompatible directory-prefix and escaped-JSON
   boundaries, explaining 49 directly actionable nonmaterialized references.
3. Prefix-wide generated-output classification incorrectly includes unmanaged
   Goose helper/draft resources.
4. The isolated multi-generator projection graph required by the GO is not yet
   implemented; generator checks against the live tree create predictable false
   failures.
5. Five registered in-root worktrees are inventoried but not content-scanned;
   whole-root observation must bind separate-worktree findings to each HEAD.
6. The malformed TOMLs, live MemBase row, and dashboard SQLite are genuine
   separate structured/domain cases and must not be hidden by text replacement.

## Acceptance Status

- [x] Deterministic programmatic root inventory and reference scan exists.
- [x] All 90 CSV mappings and inferred obsolete skill aliases enter one catalog.
- [x] Physical path aliases, structured strings, ZIP/wheel members, SQLite fields, and undecoded bytes receive explicit evidence.
- [x] Main-v4 authority cannot authorize apply; exact child authority is required.
- [x] All 90 obsolete sources remain present; no deletion occurred.
- [x] Transaction, rollback, recovery, path-race, and final-state primitives have focused tests.
- [x] Focused suite passes 63/63 and Ruff is clean.
- [x] Two fresh processes reproduce the exact current plan and closure hashes.
- [ ] Semantic residual classification is not complete.
- [ ] The complete isolated generator graph is not materialized.
- [ ] Structured TOML/dashboard/SQLite and harness-domain operations are not authorized or closed.
- [ ] In-root worktree content observation is not complete.
- [ ] Stage B's 460/460 governance gate is not satisfied.
- [ ] Zero blockers, zero unexplained live residuals, zero pending generated drift, and repeated final-state verification have not been achieved.

## Risk And Rollback

No repository consumer was mutated, so there is no migration rollback to run.
Stage A files are additive and remain uncommitted. Broad Git cleanup is
forbidden; any later correction should append through the v4 lifecycle and
continue using the exact nine-target Stage A boundary or a newly reviewed
expanded target list.

Stage B remains paused. The 484 proposed writes are evidence only and must not
be copied into a child proposal until the blockers reach zero, the exact plan is
stable, the complete 460-test governance gate passes, and an unrelated Loyal
Opposition session reviews the exact plan/binding.

## Loyal Opposition Request

1. Confirm the Stage A changes stayed within the exact nine-target envelope and
   that no live migration apply or consumer mutation occurred.
2. Independently spot-check the deterministic plan/closure hashes, 63-test
   focused suite, wheel and pytest-boundary fixes, blocker counts, and retained
   old-source invariant.
3. Return a finding-specific `NO-GO` if the known semantic classification,
   generator graph, structured/domain operation, worktree observation, or
   broader-gate gaps prevent verification. Do not treat this report or its
   484-write evidence set as Stage B authorization.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
