REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit owner direction and current-session Codex metadata

bridge_kind: implementation_report
Document: gtkb-wi5428-codex-hook-parity-restoration
Version: 011
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5428-codex-hook-parity-restoration-010.md
Controlling GO: bridge/gtkb-wi5428-codex-hook-parity-restoration-006.md
Approved proposal: bridge/gtkb-wi5428-codex-hook-parity-restoration-005.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project Authorization Version: 5
Owner Decision: DELIB-202667714
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5428
project_id: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
work_item_ids: ["WI-5428"]
source_spec_ids: ["GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001", "ADR-CODEX-HOOK-PARITY-FALLBACK-001", "SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001", "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001", "GOV-HARNESS-ROLE-PORTABILITY-001", "DCL-SESSION-ROLE-RESOLUTION-001", "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001", "GOV-RELEASE-READINESS-GOVERNED-TESTING-001"]
target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: configuration,source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_evidence_work_in_scope: false

No KB mutation: this corrected report performs no MemBase mutation and no
`groundtruth.db` write; `groundtruth.db` is intentionally absent from
`target_paths`.

# WI-5428 Corrected Implementation Report — implemented four-path slice remains nonterminal

## Disposition

This substantive corrected report responds to NO-GO-010 and requests another
independent **NO-GO**, not VERIFIED. The approved four-path implementation is
present, committed, clean, and positive on its focused checks. The report now
contains the missing executed specification-to-test mapping and binds the
named schema-v3 implementation-start packet used by the version-007 authoring
session.

Terminal verification is still unsafe. Current read-only probes reproduce two
P1 false-green classes in the batch-discovery contract: unknown entry kinds
can advertise a required surface that the runtime rejects, duplicate children
collapse before occurrence counting, and trailing batch arguments are
accepted. Correcting those defects requires the public parser at
`scripts/parity_discovery_diff.py`, outside the four target paths approved by
versions 005/006. No fifth target is silently added here.

The earlier transcript-role concern is no longer a current blocker. Commit
`451956a13` added the interactive-role persistence contract downstream of the
wrap-up adapter, and the current twelve-test persistence module passes. This
report preserves the historical finding while distinguishing it from the two
still-reproducible batch defects.

No configuration, source, test, MemBase, approval packet, claim, Git,
dispatcher, or TAFE state is changed by this report.

## Current Authority And Membership

- Project `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` is active at version
  2.
- WI-5428 is an active project member, P0, open, and backlogged. Its legacy
  `approval_state=unapproved` field is noncontrolling because implementation
  authority is inherited from the active parent project.
- Whole-project authorization
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  is active at version 5, row 947, unexpired, and list-free under
  `DELIB-202667714`. It permits configuration, source, and test work while
  retaining the dispatcher, TAFE, external-system, credential, push, history
  rewrite, deployment, release, and destructive-cleanup prohibitions.
- No exact WI-5428 work-intent claim exists now. The overlapping, GO-status
  WI-5275 thread also has no current claim, but it names
  `scripts/check_codex_hook_parity.py`; any later code correction must serialize
  with that thread and recheck its current target ownership.

No owner AUQ is required to file this evidence-only report. It does not grant
new implementation authority.

## Fresh Packet Evidence

The version-007 authoring session's live named packet is preserved at:

`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5428-codex-hook-parity-restoration.json`

| Field | Bound value |
| --- | --- |
| Schema | 3 |
| Packet hash | `sha256:1da21320a0fa54b8e3aa5dfdc31eea8555fcf8c7e710eb92fa85ed3880b3d304` |
| Current file SHA-256 | `8250ecd3d13402378674b0bef3f96da61353437e6fc23043bf683a9b4854d84b` |
| Proposal / GO | v005 / v006 |
| Session | `G-2026-07-31T07-41-38Z` |
| Claim acquired | `2026-07-31T15:27:46Z` |
| Claim TTL | `2026-07-31T16:07:46Z` |
| Packet created and finalized | `2026-07-31T15:29:42Z` |
| Packet expiry | `2026-07-31T17:29:42Z` |
| Version-007 filesystem creation observation | `2026-07-31T15:35:21.2831090Z` |

The packet and claim were live when version 007 was created. The packet is
expired now and is not represented as current mutation authority. It cannot be
reactivated by copying it to `current.json`: activation validates expiry and
current bridge state before writing. This report needs no protected mutation,
so no post-hoc packet is minted and no historical packet is laundered.

## Current Four-Target Bytes And Commit Provenance

The exact implementation landed in commit
`02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`, whose four-target numstat is
356 insertions and 200 deletions. No later commit changes these four paths, and
scoped porcelain status is empty at current HEAD `75decbfa7`.

| Target | SHA-256 | Git blob | Bytes |
| --- | --- | --- | ---: |
| `.codex/config.toml` | `d5cc947c2f1e7c88ecb11248f250879ecb47f7a0941de68db07efff13983df97` | `cd126532e0c5d2b339fbac0661c01d1224fc4362` | 738 |
| `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | `df65d664b2a1b60206fca4f693df5ef832997cbddfa4c9f0e89a8bda7042437e` | `34890d2888810790d8829c8163467fbb446544ea` | 13,547 |
| `scripts/check_codex_hook_parity.py` | `db9aeb62f66428f3cde16adb567094e5a206d6f55f6092ed0749397efc52c519` | `3c6e78386ddcfc3c69b2bc125b2c203907317833` | 74,175 |
| `platform_tests/scripts/test_codex_hook_parity.py` | `662c3e1f94abb4020b3d54cb5a8bb9b5a645a3adb6b432f8eb12edd06d28b9f9` | `2330ae7de4f414a1921097c27d6c254195b68dee` | 33,712 |

The two excluded routing files retain the proposal locks:

| Excluded path | SHA-256 | Git blob |
| --- | --- | --- |
| `.codex/hooks.json` | `abd3c88f2b89958601acfe86483de50caf4c283eaa1bc27e1a58c76f5951d44a` | `e4881dca1b6a97c2c95ccc678a24697073909656` |
| `.codex/gtkb-hooks/run_py_no_window.py` | `575b07a5376171d27c9ba766abf0fa515b216d49ee7df63217be176a43f88a54` | `5e7bcf8f21b85bb243dee55fec5be11afe7cb9d3` |

## Current P1 Findings

### P1 — unknown batch entry kind can false-green

`scripts/parity_discovery_diff.py::_batch_surfaces()` scans every string value
inside an entry tuple and returns its path stem without validating the entry
kind. The runtime's `_batch_command()` accepts only `py` and `cmd`. A synthetic
`("unknown", ".codex/gtkb-hooks/formal-artifact-approval.cmd")` entry therefore
enumerates `formal-artifact-approval`, while the runtime raises
`ValueError: unknown batch entry kind: unknown`.

Impact: the checker can claim a required governance surface exists even though
the configured hook cannot run.

### P1 — duplicate children collapse before occurrence counting

The same public enumerator returns `set[str]`. Two identical batch children
therefore enumerate as one stem, while the runtime iterates and executes both
entries. The targeted probe declared two formal-artifact children and observed
`enumerated_unique_count=1`.

Impact: the checker can satisfy the proposal's exactly-once route assertion
while executing a governance or lifecycle handler twice. This is both a
correctness and concurrency/reentrancy risk.

### P1 — trailing batch arguments are accepted

`scripts/check_codex_hook_parity.py::_batch_route_errors()` only requires that
a `--batch <name>` token appear. The exact probe command
`pythonw.exe .codex/gtkb-hooks/run_py_no_window --batch pretooluse-bash --unexpected`
returned no checker errors.

Impact: an invalid outer invocation can pass configuration parity while the
runtime rejects or misinterprets the command line.

All three defects require a strict, typed public discovery result preserving
entry kind, normalized path provenance, occurrence count, and parse errors.
That change belongs in `scripts/parity_discovery_diff.py` with focused tests;
it is outside the current four-target GO.

## Specification-Derived Test Mapping

Every row below was executed on 2026-08-01 against current HEAD with
`PYTHONDONTWRITEBYTECODE=1`; pytest cache writing was disabled.

| Requirement / acceptance criterion | Executed | Exact command | Observed result |
| --- | --- | --- | --- |
| Live Codex hooks and parity checker | yes | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py` | Exit 0; `Codex hook parity: PASS`; zero findings. |
| Focused batch parity plus wrap-up adapter | yes | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short -pno:cacheprovider` | 19 passed, 1 warning in 2.17s. |
| No-window/runtime containment | yes | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_hook_runtime_containment.py platform_tests/scripts/test_codex_hook_batch_output.py platform_tests/scripts/test_codex_no_window_timeout_alignment.py platform_tests/scripts/test_codex_shell_no_window_wrapper.py -q --tb=short -pno:cacheprovider` | 24 passed, 1 warning in 3.06s. |
| Checker compatibility and resolution-table drift | yes | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short -pno:cacheprovider` | 36 passed, 1 failed, 1 warning in 3.91s. Failure: stale direct MCP-worker-guard registration expectation against excluded `.codex/hooks.json`. |
| Cross-harness nonimpairment | yes | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short -pno:cacheprovider` | 43 passed, 1 failed, 1 warning in 1.19s. Failure: tracked `gtkb-skill-rollout` skill is an undeclared registry extra. |
| Interactive transcript-role persistence | yes | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_interactive_session_role_persistence.py -q --tb=short -pno:cacheprovider` | 12 passed, 1 warning in 0.37s; supersedes the earlier source-only role concern for current HEAD. |
| Python lint | yes | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py` | Exit 0; all checks passed. |
| Python format | yes | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py` | Exit 0; three files already formatted. |
| Exact diff/status scope | yes | `git diff --check -- <four targets>` and `git status --porcelain=v2 -- <four targets>` | Exit 0 and no scoped status records. |
| Strict batch rejection and exactly-once visibility | yes | Read-only inline Python imported `_batch_surfaces`, `_batch_route_errors`, and runtime `_batch_command`; mocked only `Path.read_text` for synthetic BATCHES literals. | Unknown kind advertised the required surface but runtime raised `ValueError`; two declared children collapsed to one enumerated stem; trailing args returned `[]`. BLOCKED. |

The pytest warning is the existing unknown `asyncio_mode` configuration option;
it is not a WI-5428 target change. The two broader test failures reproduce the
same disclosed out-of-scope baselines from the earlier audited draft and are
not represented as passing.

## Acceptance Status

- PASS: hooks enabled; current checker reports PASS; focused 14/14 parity;
  wrap-up adapter 5/5; containment 24/24; role persistence 12/12; Ruff,
  formatting, exact diff, clean scope, and excluded-file hashes.
- FAIL: malformed/unknown child entries do not fail parity closed.
- FAIL: duplicate child occurrences are invisible to the set-based enumerator
  and can execute twice.
- FAIL: trailing batch arguments are not rejected.
- BASELINE FAIL: MCP-worker-guard direct-registration compatibility test.
- BASELINE FAIL: undeclared `gtkb-skill-rollout` registry-extra test.
- PENDING: independent VERIFIED and terminal finalization.

## Timer, Concurrency, And Advisory Deduplication

This audit found no new evidence that a WI-5428 hook runtime timeout is too
short: the focused and containment suites completed without timeout failure.
The current code still contains literal hook thresholds, so future
externalization remains covered by WI-5806 and recurring data-driven tuning by
WI-5807. No unsupported tuning value is proposed here.

The registry-control-plane acquisition defect also reproduced immediately
before this filing attempt: governed WI-5369 publication exhausted the fixed
lock budget after 34.6 seconds, failed closed with
`timed out acquiring registry lock ... control-plane.lock`, and created no
numbered file; after exact-state verification and a patient retry, the same
publication completed in 67.1 seconds. That right-censored observation is
direct evidence that the acquisition budget is too short under real fleet
width. It belongs to the existing SoT/concurrency advisory bundle and exact
open owner WI-5869, while WI-5804 inventories the value and WI-5806/WI-5807
own central externalization and recurring tuning. No duplicate Advisory Report
or timer WI is created by this report.

The duplicate-child finding is a deterministic execution-duplication defect
already recorded in WI-5428's status detail.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- Owner AskUserQuestion answer: **Approve Assurance PAUTH amendment**. This is
  durably represented by `DELIB-202667714` and active whole-project Assurance
  PAUTH v5; it authorizes the governed local project cohort while preserving
  every bridge, claim, packet, review, verification, and release gate.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` records the
  owner's project-level approval rule: an active WI member inherits the parent
  project's implementation approval, so WI-5428's legacy row-level
  `approval_state` does not create a separate AUQ.
- No new owner decision is requested or inferred by this corrected evidence
  report, and no implementation begins from it.

## Prior Deliberations

- `DELIB-202667714` is the current owner decision behind active Assurance
  PAUTH v5 and governed local finalization.
- `DELIB-202666774` and `DELIB-202667009` preserve the append-only WI-5364
  false-closure evidence.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establishes
  whole-project implementation-authority inheritance for active members.
- `DELIB-202667722` carries the timer-governance externalization and recurring
  tuning direction already represented by WI-5806/WI-5807.

## Exact Next Governed Path

1. Loyal Opposition should return NO-GO on this report because the two current
   batch false-green classes violate the approved fail-closed and exactly-once
   invariants.
2. Prime Builder should then file a fresh REVISED implementation proposal that
   adds the canonical public parser `scripts/parity_discovery_diff.py` and its
   focused tests to the exact target set, retains the existing four paths only
   where further changes are proven necessary, and serializes the overlapping
   checker path with GO-status WI-5275.
3. Only a later independent GO, exact claim, fresh schema-v3 packet, bounded
   implementation, complete green matrix or explicit governed baseline
   disposition, and independent VERIFIED may close WI-5428.

No AUQ is required for this report or for proposal filing under the active
Assurance project PAUTH. No current claim exists, and no implementation is
authorized by this REVISED report alone.

## Pre-Filing Preflight

- Candidate applicability preflight passed with
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`; PAUTH v5 operation-time evaluation allowed the exact
  governed report/finalization cohort.
- Mandatory ADR/DCL clause preflight evaluated five clauses, found three
  `must_apply` and two `may_apply` clauses, and reported zero evidence gaps and
  zero blocking gaps (exit 0).
- The governed revision helper must repeat both checks against this completed
  content before it creates the numbered bridge file.

## Non-Approval

This report does not authorize source/config/test mutation, staging, commit,
push, release, deployment, external-system work, credentials, destructive
cleanup, dispatcher mutation, or TAFE activation/mutation. Dispatcher and TAFE
remain deliberately disabled and untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
