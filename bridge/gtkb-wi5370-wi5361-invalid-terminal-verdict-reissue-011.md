NEW
::init gtkb lo
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue - 011

bridge_kind: implementation_report
Document: gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue
Version: 011 (NEW; post-implementation report)
Date: 2026-07-18 UTC
Responds to GO: bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-010.md
Approved proposal: bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-009.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Related Work Items: WI-5361, WI-5501
Recommended commit type: chore:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

## Implementation Claim

Phase 1 of the approved repair is complete.

The substantive but structurally invalid WI-5361 version-004 body was preserved
byte-for-byte at the canonical evidence path
`bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`.
Only the untracked numbered source
`bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md` was then removed.
The target thread now falls back to its prior version-003 `NEW` state.

Both required work-intent claims remained held by this exact Prime Builder
session throughout preservation, removal, verification, and publication of this
report:

- repair-thread claim row `32985`, kind `go_implementation`;
- target-thread claim row `32939`, kind `draft`;
- session `019f6668-9974-7d72-a456-826f9a67e627`.

The exact schema-v3 implementation-start packet was
`sha256:d7aad8e4636ba3548a687edcf5a195527704fbbf782a32b04daec62cce852715`;
its pre-start authorization hash was
`sha256:92762d6945fdadd364e4c7b2ea74e5770eef148117ab0e3e4c077236f63ed8b6`.
Operation-time authorization passed for both approved paths immediately before
their respective mutations.

An initial preservation candidate was detected with LF-normalized bytes:
`1952` bytes instead of the required `1988`. It was rejected and removed before
the numbered source was touched. Operation-time authorization was revalidated,
and an exact mechanical byte copy was then made. This fail-closed check
prevented the normalized candidate from becoming preservation evidence.

The final preserved body has:

- byte length `1988`;
- SHA-256
  `7156D04B75B73D389E13F706820F39EA5FE62D9CA783491D136EDAF30FF7FF78`;
- Git blob `087ba3add848bbaa572be3b4795b1855a5bbed9b`;
- first line `VERIFIED`;
- exact source-to-target byte equality at the pre-removal checkpoint.

The staged-index snapshot was unchanged across the transaction. Both before and
after snapshots, computed as SHA-256 over the LF-joined output of
`git ls-files --stage`, were
`7E4C6A7E64B899A76F146C6B14F36112CA813FB96F5FFBB28057A4519295D983`.
The scoped status now contains only the approved untracked preservation target.
The full unrelated worktree was concurrently active and therefore did not yield
a stable whole-status hash; no whole-worktree neutrality claim is made. The
approved invariant is the exact unchanged index plus the scoped one-record
substitution, both of which passed.

This report does not reissue WI-5361 version 004. Corrected `VERIFIED` authorship
is reserved to an independent Loyal Opposition session. Durable finalization
must also wait for terminal WI-5501 or a separately owner-directed exclusive
finalization window, exactly as required by the GO.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The approved
Tree Stabilization project authorization and the owner-directed canonical
artifact boundary remain the controlling authority. This implementation did
not modify dispatcher configuration, dispatcher runtime, TAFE, harness state,
source, tests, database content, credentials, deployment, release state, or Git
history.

## Prior Deliberations

- `DELIB-202666332` - bounded clean-worktree finalization authority and the
  requirement to exclude uncharacterized concurrent bytes.
- `DELIB-202666274` - owner decision supporting the active Tree Stabilization
  project authorization.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - canonical bridge
  artifacts depend only on canonical evidence.
- `bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-009.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-010.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Exact scoped status plus before/after staged-index hashing proved only the approved untracked source-to-evidence substitution and an unchanged index. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Both exact-thread claims were queried after the transaction and remained active under this session; direct exact-thread enumeration showed only v001 and v003, both `NEW`. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Length, SHA-256, Git blob, first-line status, and pre-removal byte equality were recomputed from the exact source and preservation target. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | All implementation claims were re-derived from the numbered thread, live claim CLI, exact files, Git index, and focused source/test commands immediately before reporting. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The exact two-path schema-v3 packet and pre-start authorization passed; operation-time authorization was revalidated before the final byte copy and removal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-report planning resolved the active PAUTH, project, WI-5370, approved proposal v009, GO v010, and report v011. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The report carries forward all 15 linked specifications from the approved proposal and GO. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, Ruff check, Ruff format, preserved-body finalizer validation, byte-identity checks, and bridge preflights were executed and are mapped here. |
| `ADR-CROSS-HARNESS-PARITY-001` | Claude, Codex, and Cursor `write_verdict.py` projections were SHA-256 compared and were byte-identical at `549E12E6B8CB2F998C36D06B51DA8AC98A013ED2D6D5EE766ABAE66535AF5EC2`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | The byte-identical supported helper projections enforce the same malformed-body rejection and finalization floor; no harness-specific bypass was used. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed paths and every executed dependency resolved within `E:/GT-KB`. |
| `GOV-STANDING-BACKLOG-001` | WI-5370 remains the repair work item, WI-5361 remains the target, and WI-5501 remains the explicit concurrent-finalization dependency. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Substantive invalid evidence was retained in the canonical bridge evidence surface instead of being discarded. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The repair preserves evidence, appends this implementation report, and leaves corrected terminal authorship to independent review. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Phase 1 ends at a `NEW` implementation report; Phase 2 and terminal finalization remain gated rather than being inferred from file removal. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/impl_report_bridge.py plan gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue --compact`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi5361-dispatch-cap-authority-precedence`
- `git hash-object --no-filters -- bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`
- `git status --short -- bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`
- `git ls-files --stage` with deterministic LF joining and SHA-256 hashing.
- Direct `validate_verified_body()` invocation against the preserved body.
- SHA-256 comparison of the Claude, Codex, and Cursor `write_verdict.py` projections.

## Observed Results

- Focused test module: `7 passed, 1 warning in 0.22s`; the warning is the
  existing unknown `asyncio_mode` pytest configuration warning.
- Ruff check: `All checks passed!`.
- Ruff format: `3 files already formatted`.
- Implementation-report plan: latest status `GO`, proposal v009, GO v010,
  next version v011, all 15 linked specifications carried forward.
- Both claim records: active, unexpired, same session, exact expected claim
  kinds and threads.
- Preserved evidence: exact `1988` bytes, declared SHA-256 and Git blob,
  first line `VERIFIED`.
- Exact target thread: only v001 and v003 are present; both begin with `NEW`.
- Scoped Git status: only
  `?? bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`.
- Index snapshot: identical before and after at
  `7E4C6A7E64B899A76F146C6B14F36112CA813FB96F5FFBB28057A4519295D983`.
- Preserved-body finalizer validation failed as expected with
  `VERIFIED verdict body must include Recommended commit type evidence.`
- Cross-harness helper projection hashes were identical.

## Files Changed

- `bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`

Excluded out-of-scope dirty paths: 1801.

## Recommended Commit Type

- Recommended commit type: `chore:`
- Diff-stat justification: the implemented change is a bounded bridge-evidence
  preservation and invalid untracked slot repair; it adds no product capability
  and changes no source or test behavior.

```text
1 canonical bridge-evidence file created; 1 invalid untracked numbered source
removed; no staged-index change; source and tests unchanged.
```

## Acceptance Criteria Status

- [x] The current v004 body was classified as substantive LO evidence and
  verified against its exact current identity.
- [x] Exact bytes were preserved only at the approved canonical
  `bridge/hunks/` target.
- [x] Both thread claims and exact start/operation-time authority were active
  before and through mutation and remain held through report publication.
- [x] Only the invalid untracked numbered v004 source was removed.
- [x] This report records byte equality, exact target fallback, claim evidence,
  and unchanged staged-index identity.
- [ ] Independent Loyal Opposition must rerun the checks and reissue a valid
  WI-5361 v004; this is explicitly outside Prime Builder authority.
- [ ] WI-5361 terminal commit finalization must wait for terminal WI-5501 or a
  separately owner-directed exclusive window.
- [x] No source, test, dispatcher, TAFE, harness, database, credential,
  deployment, release, Git-history, or unrelated staged/index mutation occurred.

## Pre-Filing Preflight

- Candidate-content applicability preflight: PASS,
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`.
- Candidate-content mandatory clause preflight: PASS, five clauses evaluated,
  four `must_apply`, one `may_apply`, zero mandatory evidence gaps, zero
  blocking gaps, exit `0`.
- Exact status and role eligibility: the repair thread remained latest `GO`
  v010, both required claims remained held by this Prime Builder session, and
  v011 is the authorized Prime-authored `NEW` implementation report.
- Canonical-reference boundary: every evidence dependency cited by this report
  is a canonical numbered bridge path, canonical bridge evidence path, MemBase
  specification/work item, Deliberation Archive record, source/test path, or
  live governed CLI result.

## Risk And Rollback

Residual risk remains the same concurrent-finalizer race tracked by WI-5501.
This Phase 1 report does not claim that risk is solved. The target thread must
not be finalized until WI-5501 is terminal or the owner establishes a separate
exclusive window.

Before a corrected independent reissue, rollback may restore the preserved
exact bytes to the numbered source path only under renewed dual-claim and
operation-time authorization. The restored body must match the recorded length,
SHA-256, Git blob, and bytes. No broader rollback, history rewrite, or unrelated
worktree mutation is authorized.

## Loyal Opposition Asks

1. Verify Phase 1 against the linked specifications and executed evidence.
2. Return VERIFIED for this repair thread if Phase 1 satisfies v009/v010;
   otherwise return NO-GO with exact findings.
3. Treat corrected WI-5361 v004 authorship as a separate independent-LO
   action, and do not attempt commit finalization until the WI-5501 or owner
   exclusive-window gate is satisfied.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
