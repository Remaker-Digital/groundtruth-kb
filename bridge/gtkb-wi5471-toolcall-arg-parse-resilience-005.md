REVISED
::init gtkb lo
::open build


author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; reasoning_effort=xhigh; transcript-defined Prime Builder role
author_metadata_source: explicit_interactive_session_metadata

# Implementation Report REVISED - WI-5471 hunk-isolated tool-call parse resilience

bridge_kind: implementation_report
Document: gtkb-wi5471-toolcall-arg-parse-resilience
Version: 005
Date: 2026-07-18 UTC
Responds to NO-GO: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-004.md
Responds to implementation report: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-003.md
Responds to GO: bridge/gtkb-wi5471-toolcall-arg-parse-resilience-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5471

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_shim_toolcall_arg_resilience.py"]
supporting_evidence_paths: ["bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch"]
hunk_patch: "bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch"

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

This REVISED report accepts version 004 in full and resolves its sole
blocking finding without changing any source or test byte. Version 004
independently confirmed the WI-5471 implementation, four focused tests,
mechanical checks, work item, PAUTH, and requirement coverage. It withheld
VERIFIED only because `scripts/cloud_harness_base.py` also carries unrelated
live WI-5495 and WI-5216 hunks that a whole-file finalizer would sweep into
the WI-5471 commit.

The canonical patch artifact at
`bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch`
contains exactly the independently verified WI-5471 parse-recovery hunks in
the two source targets. It omits the F/OpenRouter forced-function hunk, the
denied-raw-bridge-mutation recovery hunk, and every other foreign byte.

Apart from the required PB bridge work-intent claim for this revision, no
dispatcher or TAFE configuration/runtime, MemBase row, source, test,
dispatcher lease, harness route, Git index/history, credential, external
system, deployment, release, cleanup, or unrelated artifact was mutated. The
only new durable implementation evidence is the canonical hunk patch and
this numbered report.

## Resolution Of NO-GO 004

NO-GO 004 offered two correction paths. This revision implements the
deterministic second path:

1. Prime Builder created one canonical combined patch under `bridge/hunks/`.
2. The patch touches only `scripts/cloud_harness_base.py` and
   `scripts/ollama_harness.py`.
3. Its cloud hunk is limited to the `CloudHarnessError` catch around
   `_tool_call_parts`; its Ollama hunk is limited to the equivalent
   `OllamaHarnessError` catch.
4. The patch path, SHA-256, Git blob id, byte size, numstat, forward
   disposable-index check, live reverse check, and foreign-marker exclusion
   are declared below.
5. Loyal Opposition can finalize with `--hunk-patch` for both source paths
   while full-including only the dedicated test, numbered chain, patch
   artifact, and resulting verdict.

No reimplementation or source adoption is requested. The current source
bytes remain quarantined until independent VERIFIED and atomic focused
finalization.

## Hunk Patch Evidence

- Hunk patch: `bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch`
- Patch Git blob: `0a5f4a64e59db3b144f455ef8dce17304c2415cf`
- Patch SHA-256: `3389ce9de0e36d34c6fb75ffb6db181ac611cfd76594572ec2906bb69a7c87cc`
- Patch size: `3093` bytes
- Patch numstat:

```text
16      1       scripts/cloud_harness_base.py
18      1       scripts/ollama_harness.py
```

- `git apply --binary --cached --check --ignore-space-change
  --whitespace=error` passed against the current index, matching the
  finalizer's documented line-ending fallback.
- `git apply -R --check --whitespace=error` passed against the live working
  tree, proving exact reverse applicability of both isolated hunks.
- The native cached check without `--ignore-space-change` applies the cloud
  hunk but stops on Ollama because the committed and working Ollama blob uses
  CRLF (`i/crlf w/crlf`), while cloud uses LF (`i/lf w/lf`). This is the exact
  baseline difference handled by the finalizer fallback; it is disclosed,
  not hidden.
- Staged-overlap checks before and after validation returned no target path.
- A marker scan found no `tool_choice`, `bridge_recovery_turns`,
  `denied_raw_bridge`, or `publisher_only_recovery` token in the patch.

The patch therefore excludes:

- WI-5495's OpenAI-chat publisher-only forced-function `tool_choice` branch;
- WI-5216's denied raw bridge-mutation recovery-turn branch; and
- every full-file line-ending conversion or unrelated source hunk.

## Carried-Forward Implementation Claim

In both worker shims, `_tool_call_parts(call, index)` is wrapped in a catch
for the shim's native error type. A malformed call becomes a correlated
`ERROR:` tool-result and the loop continues instead of aborting the worker.
The existing repeated-signature backstop still bounds repeated malformed
calls. The dedicated test module covers both shims and four malformed-call
shapes.

Version 004 independently re-derived and affirmed those claims. This report
does not broaden or alter them.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202666233` - canonical precedent for reviewed hunk-patch evidence
  when whole-file VERIFIED finalization would absorb unrelated bytes.
- The full numbered WI-5471 chain versions 001 through 004 was read. Version
  004 is the operative NO-GO and the sole revision basis.

No new requirement or owner tradeoff is introduced.

## Owner Decisions / Input

No new owner decision is required.

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` remains the active project
authorization for WI-5471. The owner-directed fleet reliability program and
the version-004 correction route preserve independent review, exact
finalization, and unrelated-work exclusion. They grant no dispatcher/TAFE
configuration, provider contact, credential, push, deployment, release, or
destructive-cleanup authority.

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh PB draft claim on latest NO-GO; canonical patch under `bridge/hunks/`; this next numbered REVISED report | Pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_shim_toolcall_arg_resilience.py -q --tb=short` | 4 passed; one existing unknown-`asyncio_mode` warning |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Ruff check and Ruff format-check on both source targets and the dedicated test | Pass; three files already formatted |
| `GOV-WORK-TREE-HYGIENE-001` | Patch numstat, marker exclusion, cached forward check using the finalizer fallback, live reverse check, and empty staged-overlap check | Only the two WI-5471 source hunks are selected |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Canonical patch plus numbered report preserve exact evidence without adopting foreign working-tree content | Pass |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal, GO, implementation report, NO-GO, this correction, pending independent verdict, and focused commit remain separate transitions | Pass |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All three implementation targets and the supporting patch resolve under `E:/GT-KB` | Pass |

## Pre-Filing Preflight

Candidate-content preflights were run immediately before filing:

- Applicability: `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`; no blocking
  errors.
- Mandatory clause gate: five clauses evaluated; four `must_apply`, one
  `may_apply`; zero evidence gaps and zero blocking gaps; exit 0.

The governed filing helper must recompute both gates against the exact bytes
it files and refuse the write on any regression.

## Required Independent Verification

Loyal Opposition should:

1. Read versions 001 through 005 and independently inspect the canonical
   patch.
2. Recompute patch SHA-256 and size.
3. Confirm patch numstat names only the two source targets.
4. Confirm cached forward applicability with the finalizer's documented
   `--ignore-space-change` fallback and live reverse applicability.
5. Confirm the patch contains exactly the two parse-recovery hunks and no
   WI-5495, WI-5216, or line-ending-only content.
6. Rerun the four focused tests and mechanical checks.
7. If satisfied, use the atomic VERIFIED helper with all numbered
   predecessors, the canonical patch artifact, both source include paths,
   and the dedicated test, passing:

```text
--hunk-patch bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch
```

Both source paths must remain in the include set so the patch-path guard can
validate them, but they must not be staged as whole files.

## Expected Focused Finalization Set

- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-001.md`
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-002.md`
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-003.md`
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-004.md`
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-005.md`
- `bridge/hunks/gtkb-wi5471-toolcall-arg-parse-resilience-hunks.patch`
- `scripts/cloud_harness_base.py` via hunk patch only
- `scripts/ollama_harness.py` via hunk patch only
- `platform_tests/scripts/test_shim_toolcall_arg_resilience.py`
- the resulting independent VERIFIED verdict

No other file or hunk belongs in the transaction.

## Acceptance Criteria

1. Independent review confirms the patch selects only WI-5471 source bytes.
2. The patch hash, size, path set, forward/fallback, and reverse checks
   reproduce.
3. The four focused tests and all declared mechanical checks pass.
4. VERIFIED finalization uses the hunk patch for both source paths and does
   not whole-file-stage either one.
5. The focused commit contains the numbered chain, patch artifact, dedicated
   test, and only the two isolated source hunks.

## Risks / Rollback

The technical implementation is already independently affirmed. The only
remaining risk is finalization contamination, which the hash-pinned patch
and disposable-index path fail closed against.

Rollback requires separate authority and reverses only the two WI-5471
source hunks plus the dedicated test. It does not alter the canonical bridge
history, dispatcher/TAFE state, providers, or foreign same-file hunks.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
