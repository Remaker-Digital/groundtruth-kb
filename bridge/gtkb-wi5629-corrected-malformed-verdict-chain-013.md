NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5629-corrected-malformed-verdict-chain - 013

bridge_kind: implementation_report
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 013
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-012.md
Approved proposal: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md
Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629
Recommended commit type: feat:

## Implementation Claim

Implemented one operation-neutral exact-thread lifecycle resolver and rewired
implementation authorization to consume its immutable result. Canonical
`bridge/<bridge-id>-NNN.md` files are now the only lifecycle authority for this
consumer. Legacy no-suffix files and longer prefix siblings are observationally
irrelevant.

The resolver returns separate audit, latest-state, review, implementation,
quarantine, and diagnostic views. It fails closed on gaps, wrong document or
version metadata, bad `Responds to` links, wrong author roles, invalid UTF-8,
invalid ordinary transitions, and arbitrary or multiple malformed exact
versions.

The one approved correction shape is implemented exactly:

`Prime NEW/REVISED -> malformed LO verdict -> Prime NO-ACTION -> corrected LO verdict`.

A pending correction exposes the strict NO-ACTION as reviewable, with no
implementation pair and no quarantine. A complete adjacent corrected GO
quarantines exactly the malformed LO path and exposes the original proposal plus
corrected GO as the implementation pair. Corrected NO-GO and VERIFIED never
expose implementation authority.

`implementation_authorization.py begin` now consumes that public pair directly.
It no longer reparses numbered files or falls back to stale GO content.

The implementation is complete for the four approved targets. Terminal
verification still has one explicit predecessor constraint: ten committed
WI-5178 authorization-operation assertions fail against the pre-existing
unimplemented WI-5178 source baseline. They are not regressions introduced by
WI-5629 and were not changed or weakened here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision is required. The implementation carries forward
`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` and active
`PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner authorization for the isolated replacement program and derived reliability work.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-012.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` through `-004.md` - live malformed-correction proving chain.
- `WI-5178` - existing operation-time authority enforcement predecessor whose committed assertions remain open.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | 36 isolated resolver tests cover exact numbering, strict metadata, role/link validation, malformed correction, sibling invariance, and terminal states. Live foundation resolution selects v001 plus v004 and no stale v002 authority. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Pending and complete correction tests prove NO-ACTION is reviewable but non-authorizing until a later corrected GO. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-STANDING-BACKLOG-001` | The report preserves the open WI-5178 predecessor failures and does not adopt that implementation. Dependent WI-5626 remains sequenced after terminal WI-5629. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Public `begin --no-write` on WI-5617 returns the active PAUTH, exact claim, proposal v001, corrected GO v004, schema-v2 packet hash, and six approved targets. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Resolver changes are isolated to one new module plus one consumer. 185 non-WI-5178 resolver/authorization tests, 34 work-intent tests, Ruff, format, and compile pass. |
| `GOV-WORK-TREE-HYGIENE-001` | Only four approved targets changed. 1,082 unrelated dirty paths remain excluded. The pre-existing WI-5382 hunk remains exactly 53 added lines in its three original zero-context hunks. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Start packet binds proposal v011, GO v012, WI-5629, the project, PAUTH, target set, and all linked specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The proposal's isolated resolver matrix, authorization integration, live foundation proof, work-intent regression, static, formatting, and compile checks were executed. The ten committed WI-5178 failures are disclosed below. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Proposal, exact GO, claim, finalized start packet, this implementation report, and independent terminal review remain separate durable lifecycle artifacts. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short --timeout=120 --basetemp E:\GT-KB\.pytest-tmp\wi5629-focused-0651 -k "<ten known WI-5178/fixture-root exclusions>"`.
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=120`.
- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\wi5629-targeted-0650 -k "clear_active_packet_if_terminal_preserves_in_flight_packets or finalization_target_paths_for_verified or create_authorization_packet_accepts_target_paths_heading_proposal"`.
- `python -m ruff check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py`.
- `python -m ruff format --check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py`.
- `python -m py_compile scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py`.
- `python scripts/implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-dispatcher-next-foundation-spike --session-id 019f77f8-0931-75e2-a78d-7dea7037f743 --no-write`.
- Full 195-test command without exclusions, using an isolated in-root pytest temp root and bounded Git discovery, to classify all remaining failures.

## Observed Results

- Resolver plus non-WI-5178 authorization regression: `185 passed, 10 deselected`.
- Canonical terminal/finalization fixture regression: `10 passed, 149 deselected`.
- Work-intent regression: `34 passed`.
- Ruff: `All checks passed`.
- Format: `4 files already formatted`.
- Compile: exit 0.
- Live WI-5617 packet proof: exit 0; proposal
  `bridge/gtkb-dispatcher-next-foundation-spike-001.md`; corrected GO
  `bridge/gtkb-dispatcher-next-foundation-spike-004.md`; six exact targets;
  packet hash
  `sha256:d099503df6b0f6cc4e1786eeea8f4b56ad083c40dd2b5c8ea4e4024c575a3366`.
- Full 195-test classification after canonical fixture correction:
  185 pass. Ten pre-existing failures remain: one exact-root dirty-collision
  fixture is intentionally disabled by bounded Git discovery for the fast
  run, and nine committed WI-5178 operation-time enforcement assertions expose
  the unimplemented WI-5178 baseline. Running under ordinary ancestor Git
  discovery preserves the collision semantics but repeatedly exceeds the
  existing 30-second fixture timeout in this 1,000-plus-dirty-path worktree.
  These are upstream dependency evidence, not concealed PASS claims.

## Files Changed

- `platform_tests/scripts/test_implementation_authorization.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`
- `scripts/bridge_lifecycle_resolver.py`

Excluded out-of-scope dirty paths: 1082.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     .../scripts/test_implementation_authorization.py   | 204 ++++++++++++++++++---
     scripts/implementation_authorization.py            |  86 +++++----
     2 files changed, 223 insertions(+), 67 deletions(-)
```

## Acceptance Criteria Status

- One shared resolver is the only new numbered lifecycle authority in this consumer: PASS.
- Its public result separates audit, review, implementation, quarantine, and diagnostics: PASS.
- Pending correction is reviewable and never implementation-authorizing: PASS.
- Complete corrected GO authorizes the original proposal only after every role, document, version, and link check passes: PASS.
- Arbitrary malformed history cannot reactivate stale Prime content: PASS.
- Prefix siblings are ignored and cannot perturb exact-thread authority: PASS.
- Only canonical `-NNN.md` files participate; legacy no-suffix files cannot supply authority: PASS.
- Foundation WI-5617 can mint and finalize its normal packet: PASS in public `begin --no-write`; finalized write is deferred to the foundation implementation step.
- Existing strict lifecycle, claim, PAUTH, target, packet, and denial semantics: PASS for 185 applicable tests; terminal WI-5629 remains dependency-blocked by the nine pre-existing WI-5178 enforcement failures.
- WI-5382 foreign test bytes remain byte-identical: the three original hunks remain 53 added lines; no WI-5629 edit was made inside those hunks.

## Risk And Rollback

Residual risk is bounded to consumers that have not yet adopted the public
resolver. Protected-commit is already tracked as a derived follow-on integration
after WI-5629. WI-5626 must consume the public fields after WI-5629 is terminal
and may not add another parser.

The open WI-5178 source baseline blocks an unconditional full-suite PASS. Do not
weaken or delete those assertions. Complete WI-5178 through its own governed
chain, then rerun this exact 195-test command before VERIFIED.

Before VERIFIED, rollback may reverse only the hash-attributed WI-5629 hunks and
remove only the two new resolver files under separate authority. Preserve the
WI-5382 hunk, all bridge audit files, and concurrent worktree bytes. After
VERIFIED, correction requires a governed successor.

## Loyal Opposition Asks

1. Verify the resolver contract, live WI-5617 selection, exact four-target attribution, and 185 passing applicable tests.
2. Treat the disclosed WI-5178 failures as an explicit dependency question. Return NO-GO if terminal WI-5629 must wait for that predecessor; do not attribute those missing WI-5178 source semantics to the resolver implementation.
3. A valid substantive GO/NO-GO from harness D also serves as fresh DeepSeek V4 Flash reviewer-lane evidence for WI-5628 and WI-5578.
