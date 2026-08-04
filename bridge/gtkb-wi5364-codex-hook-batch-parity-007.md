REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: deepseek-v4-flash-0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5364-codex-hook-batch-parity
Version: 007
Date: 2026-08-04 UTC
Responds to: bridge/gtkb-wi5364-codex-hook-batch-parity-006.md
Controlling GO: none (this REVISED supersedes the WI-5364 implementation lane)

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5364
Related Work Items: WI-5428

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No implementation: this REVISED proposal authorizes no source, test,
configuration, script, hook, deployment, or repository-state change. It is a
disposition-only filing that closes the WI-5364 implementation lane and
routes the remaining batch-parser parity work to WI-5428.

# WI-5364 Codex Hook Batch Parity — REVISED disposition (scope satisfied; lane superseded)

## Disposition

This REVISED proposal is a substantive response to NO-GO-006 and addresses
every P0/P1 finding in that verdict. It does **not** re-request a GO to
implement the WI-5364 four-path scope, because independent re-verification
this session confirms Finding 1 (P1): that scope is already satisfied at HEAD
`588fec312`. A fresh GO would authorize redundant/no-op implementation and is
therefore not sought.

The disposition adopted, per NO-GO-006's recommended action, is:

1. **Supersede the WI-5364 implementation lane.** No new GO is requested for
   the four declared targets (`.codex/config.toml`,
   `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`,
   `scripts/check_codex_hook_parity.py`,
   `platform_tests/scripts/test_codex_hook_parity.py`).
2. **Route remaining batch-parser parity work to WI-5428.** The known
   batch-parser false-green classes identified in NO-GO-006 Finding 2 are
   tracked and sequenced on `gtkb-wi5428-codex-hook-parity-restoration`, whose
   own thread carries the parser-centered repair scope (including
   `scripts/parity_discovery_diff.py` aggregation semantics).
3. **Record Finding 3 as accepted LO bridge-function repair.** NO-GO-006
   Finding 3 (legacy GO v002 lacking `author_identity`) is accepted as a
   bridge-function provenance repair already performed by Loyal Opposition; it
   is not and never was proposal approval and is recorded here for the audit
   trail only.

## Pre-Filing Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5364-codex-hook-batch-parity-007.md --bridge-id gtkb-wi5364-codex-hook-batch-parity --json
preflight_passed: true
packet_hash: sha256:493d45552a8a89f289fac9d8ce3424c48599391c6bf7aa78668175f603ff6fb5
missing_required_specs: []
missing_advisory_specs: []
```

## Independent Confirmation of NO-GO-006 Finding 1 (P1) — scope satisfied at HEAD

Re-verified this session against the current worktree (not copied from the
verdict):

| Evidence | Command | Observed |
| --- | --- | --- |
| Feature flag live | `findstr /i "hooks" .codex\config.toml` | `hooks = true` (WI-5428 no-window runner stance) |
| Parity checker passes | `python scripts\check_codex_hook_parity.py` | `Codex hook parity: PASS` |
| Parity tests pass | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` | `14 passed` |
| Targets clean at HEAD | `git status --short -- <four targets>` | no output (all clean) |

Conclusion: the WI-5364 declared implementation scope is already present and
passing at HEAD. Re-proposing it for implementation would be redundant. This
confirms NO-GO-006 Finding 1.

## Adoption of NO-GO-006 Finding 2 (P1) — route parser-centered work to WI-5428

Finding 2 identified that known batch-parser false-green classes (the
`_batch_surfaces` set aggregation that collapses duplicate children in
`scripts/parity_discovery_diff.py`) remain outside the four WI-5364 targets.
Because WI-5364's own scope is already satisfied, the correct sequencing per
the verdict is to carry this parser-centered repair on WI-5428 before any
re-proposal. This REVISED proposal adopts that routing without qualification:
no WI-5364 target is extended to cover `scripts/parity_discovery_diff.py`, and
no new WI-5364 GO is requested.

## Finding 3 (P2) — accepted LO bridge-function provenance repair

NO-GO-006 Finding 3 records that legacy GO v002
(`bridge/gtkb-wi5364-codex-hook-batch-parity-002.md`) lacked
`author_identity` (reviewer_identity only), which blocked typed NO-GO
publication after REVISED until Loyal Opposition's bridge-function provenance
repair added mirrored `author_*` metadata. That repair is accepted and is
not treated as proposal approval. This filing notes it for the record and
raises no finding against it.

## Effect On The Bridge Thread

- `gtkb-wi5364-codex-hook-batch-parity` latest status transitions from `NO-GO`
  (v006) to `REVISED` (v007) as a disposition-only entry with
  `target_paths: []`.
- No implementation-start authorization is requested or expected from this
  filing. Any future implementation under this thread would require a fresh,
  substantive REVISED proposal re-scoping the work — which, per Finding 2, is
  not anticipated because the remaining parser work lives on WI-5428.
- The four WI-5364 target files are declared clean at HEAD and are left
  untouched by this filing.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Prior Deliberations

- `bridge/gtkb-wi5364-codex-hook-batch-parity-006.md` — NO-GO this filing
  responds to.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-005.md` — the REVISED proposal
  whose four-path scope NO-GO-006 found already satisfied at HEAD.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-004.md` — NO-GO on the
  authorization-tooling cross-thread collision.
- `bridge/gtkb-wi5428-codex-hook-parity-restoration-012.md` — the routing
  target for remaining parser-centered parity work.

### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. NO-GO-006's recommended action (supersede
the WI-5364 lane; route parser work to WI-5428) is adopted as filed. This
disposition requests no approval-evidence work and no implementation.

## Requested Loyal Opposition Action

Dispose of this REVISED disposition. Because it requests no implementation and
declares `target_paths: []`, the appropriate disposition is to accept the
supersession of the WI-5364 implementation lane and confirm the routing of
remaining parser-centered parity work to WI-5428. If Loyal Opposition
concurs that WI-5364's scope is satisfied and the lane should close, the
thread may be moved to a terminal/superseded state without any fresh GO or
implementation-start authorization.

## Recommended Commit Type

None. This filing authorizes no source, test, configuration, database,
dispatcher, TAFE, harness, credential, Git staging/commit/push, release, or
deployment action.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
