NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

bridge_kind: implementation_report
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 010
Responds to GO: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-009.md
Approved proposal: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-008.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]
supporting_evidence_paths: ["bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch"]
hunk_patch: "bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch"

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

# Implementation Report - WI-5495 F/OpenRouter Publisher-Recovery Tool Choice

## Implementation Claim

The independently approved F/OpenRouter correction is implemented and isolated
for review. During a publisher-only recovery turn, the OpenAI-compatible
dialect now sends the exact forced-function `tool_choice` shape naming
`PublishBridgeVerdict`. Ordinary turns remain unchanged, and the existing
Anthropic-dialect recovery behavior remains intact.

The approved source and test bytes already existed as quarantined candidate
changes in the shared worktree. After acquiring claim row 33359 and a fresh
schema-v3 implementation-start packet, this session adopted only the WI-5495
hunks authorized by versions 008 and 009. It did not alter the neighboring
WI-5216 candidate source/test bytes.

Because both target files remain commingled, whole-file finalization is
prohibited. The canonical patch at
`bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
contains exactly the reviewed WI-5495 source and test hunks and excludes every
WI-5216 byte. Both targets must be finalized through that patch only.

## Authorization Evidence

- Latest bridge status before implementation: `GO` at
  `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-009.md`.
- Approved proposal:
  `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-008.md`.
- Exact work-intent claim: row 33359, session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, kind
  `go_implementation`, role `prime-builder`, project
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- Schema-v3 implementation-start packet:
  `sha256:b0ba32aa6ac866887bc3562bfd18724b947cbe1523c319d0cf02168bd99487e7`.
- Packet target paths:
  `scripts/cloud_harness_base.py` and
  `platform_tests/scripts/test_cloud_harness_base.py`.
- Project authorization:
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, active with no expiry.
- Exact target-path preflight: both candidates in scope; zero unused or
  out-of-scope targets.

## Hunk Patch Evidence

- Hunk patch:
  `bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
- Patch SHA-256:
  `2b71f7ff7772f353f967c61bcf21a082bb3d5b4ecf293b5a87cc6170d77b89d9`
- Patch Git blob: `c6593a5cc4250402e9cb3bfbaee648be2b18d3bd`
- Patch size: `3167` bytes
- Patch numstat:

```text
11      9       scripts/cloud_harness_base.py
6       1       platform_tests/scripts/test_cloud_harness_base.py
```

- `git apply --cached --check --whitespace=error
  bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
  passed against the clean index.
- `git apply -R --check --whitespace=error
  bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
  passed against the live working tree.
- `git apply --numstat` names exactly the two approved targets.
- A marker scan found no `bridge_recovery_turns`,
  `max(bridge_recovery_turns`, `raw_bridge`, `_tool_call_parts`,
  `ollama_harness`, `WI-5216`, or `WI-5471` text in the patch.
- `git diff --cached --name-only` remained empty after every check.

The patch therefore selects only:

1. the OpenAI-chat forced-function branch in
   `scripts/cloud_harness_base.py`; and
2. the three negative/positive `tool_choice` assertions in
   `test_bridge_review_requires_publish_before_final_text`.

It excludes the separately governed denied-raw-mutation recovery branch and
test owned by WI-5216.

## Files Changed

- `scripts/cloud_harness_base.py` - during publisher-only recovery with only
  `PublishBridgeVerdict` active, preserve the Anthropic branch and add the
  OpenAI Chat Completions forced-function `tool_choice` shape.
- `platform_tests/scripts/test_cloud_harness_base.py` - prove `tool_choice` is
  absent before recovery, exactly forced during recovery, and absent again
  after successful verdict publication.
- `bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
  - canonical hash-pinned isolation evidence.

No D/Ollama source, dispatcher/TAFE configuration or runtime, provider,
credential, deployment, release, cleanup, or unrelated source/test surface is
part of this implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Prior Deliberations

- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`,
  `DELIB-202666174`, and `DELIB-202666256` - provider publisher-recovery and
  governed verdict-publication precedents carried through the approved chain.
- `DELIB-202666850` - establishes that D/Ollama requires its separate
  protocol-appropriate design; that scope remains excluded.
- `bridge/gtkb-wi5216-denial-loop-recovery-reliability-fixes-007.md` -
  owner-directed terminal withdrawal of the rejected duplicate report that
  had retained the stale peer target claim.

The full numbered WI-5495 chain versions 001 through 009 was read before this
report.

## Owner Decisions / Input

No new owner decision is required for this implementation. The active
reliability fast-lane project authorization and the independent GO cover the
exact two-target correction. The owner-directed withdrawal cited above
terminally closed only the rejected duplicate WI-5216 lineage and expressly
preserved all quarantined source/test bytes; this implementation does not
adopt any WI-5216 byte.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Observed result |
| --- | --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Re-read latest proposal/GO, active PAUTH, exact claim, schema-v3 packet, and target-path preflight immediately before implementation evidence capture. | PASS: current GO, active PAUTH, Prime-owned exact claim, valid packet, 2/2 targets in scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py::test_bridge_review_requires_publish_before_final_text -q --tb=short` | PASS: 1 passed; one existing unknown-`asyncio_mode` warning. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short` | PASS: 104 passed; one existing unknown-`asyncio_mode` warning. |
| `GOV-WORK-TREE-HYGIENE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Patch path set, SHA-256, size, blob, numstat, forward cached check, reverse live check, marker exclusion, and empty-index checks. | PASS: only the two WI-5495 hunks selected; WI-5216 excluded. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Ruff check and format check on both targets; Python compilation on both targets. | PASS: Ruff clean, two files formatted, compilation exit 0. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Live applicability and mandatory clause preflights on the approved chain, followed by candidate-content preflights before filing. | PASS: no blocking errors or clause gaps; candidate content carries all required and advisory links. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths and the patch beneath `E:/GT-KB`. | PASS: all evidence is in-root. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal, independent GO, claim/start, implementation evidence, report, pending independent verification, and focused finalization remain distinct transitions. | PASS. |

## Commands Run

```text
python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-wi5495-publisher-recovery-tool-choice-forcing --candidate-paths scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py --json
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5495-publisher-recovery-tool-choice-forcing --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
git apply --cached --check --whitespace=error bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch
git apply -R --check --whitespace=error bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch
git apply --numstat bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch
git hash-object bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch
Get-FileHash bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch -Algorithm SHA256
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py::test_bridge_review_requires_publish_before_final_text -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5495-publisher-recovery-tool-choice-forcing
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5495-publisher-recovery-tool-choice-forcing
```

## Observed Results

- Exact target-path preflight: `in_scope`; two candidates accepted, zero
  unused or out-of-scope targets.
- Implementation-start: schema version 3; packet and PAUTH validated.
- Patch checks: forward cached PASS; reverse live PASS; two exact paths;
  SHA-256, blob, size, and numstat recorded above.
- Focused test: `1 passed`.
- Complete affected test module: `104 passed`.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`.
- Python compilation: exit 0.
- Mandatory clause gate: exit 0; zero blocking gaps.
- Git index: empty throughout.

## Pre-Filing Preflight

Candidate-content preflights were run immediately before governed filing:

- Declared targets: the exact two approved source/test paths.
- `preflight_passed: true`; `missing_required_specs: []`;
  `missing_advisory_specs: []`; `blocking_errors: []`.
- Mandatory clause gate: five clauses evaluated; four `must_apply`, one
  `may_apply`; zero evidence gaps and zero blocking gaps; exit 0.

The filing helper recomputes these gates against the exact filed bytes and
refuses any regression.

## Acceptance Criteria Status

- [x] F/OpenRouter recovery sends the exact forced-function `tool_choice`
  naming `PublishBridgeVerdict`.
- [x] Ordinary pre-recovery and post-publication turns omit `tool_choice`.
- [x] The focused test, complete affected module, Ruff checks, formatting,
  compilation, target-path preflight, applicability gate, and clause gate
  pass.
- [x] The hash-pinned patch excludes WI-5216 and every foreign hunk.
- [ ] Independent LO verification and focused `fix(dispatch)` finalization
  remain pending.

## Required Independent Verification

Loyal Opposition should:

1. Read versions 001 through 010 and independently inspect the hunk patch.
2. Recompute its SHA-256, Git blob, byte size, numstat, and two-path scope.
3. Re-run forward cached and reverse live applicability checks.
4. Confirm the patch contains only the OpenAI-chat source branch and the
   matching three test assertions, with no WI-5216 bytes.
5. Re-run the focused and complete module tests plus mechanical gates.
6. If satisfied, finalize VERIFIED atomically with both target paths in the
   include set and:

```text
--hunk-patch bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch
```

Both source and test paths are covered by the hunk patch and must not be
whole-file staged.

## Expected Focused Finalization Set

- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md` through
  `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-010.md`
- `bridge/hunks/gtkb-wi5495-publisher-recovery-tool-choice-forcing-hunks.patch`
- `scripts/cloud_harness_base.py` via hunk patch only
- `platform_tests/scripts/test_cloud_harness_base.py` via hunk patch only
- the resulting independent VERIFIED verdict

No other file or hunk belongs in the transaction.

Recommended commit:

```text
fix(dispatch): WI-5495 force publisher recovery tool choice
```

## Risk And Rollback

The behavioral change is narrow. The material risk is accidental adoption of
the neighboring WI-5216 candidate bytes; hash-pinned hunk finalization fails
closed against that risk.

Rollback requires separate authority and reverses only the two WI-5495 hunks.
It does not modify the append-only bridge history, WI-5216, dispatcher/runtime
state, provider configuration, credentials, deployment, or release state.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
