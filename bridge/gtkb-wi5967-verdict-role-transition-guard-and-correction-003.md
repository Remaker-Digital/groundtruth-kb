REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5967-verdict-role-transition-guard-and-correction
Version: 003
Responds to: bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-002.md
Date: 2026-08-06 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5967

target_paths: ["scripts/bridge_lifecycle_resolver.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_role_invalid_correction.py", "platform_tests/hooks/test_bridge_compliance_gate_verdict_role_transition.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

**No KB mutation.** This proposal performs no MemBase write and does not modify
`groundtruth.db`.
**No approval-evidence work.** This proposal creates no formal-artifact-approval packet
and writes no approval-packet path.
**No dispatcher or TAFE mutation.** No dispatcher configuration, substrate, scheduled task,
routing rule, or harness registry entry is changed. The legacy TAFE/dispatcher remains
quiesced per `DELIB-20260806011871`.
**No bridge file is edited.** Bridge files are append-only. This proposal changes code that
governs future writes and future chain resolution; it rewrites no history.

# WI-5967 - Block out-of-role verdicts at write time, and make role-invalid chains recoverable

## Revision Basis - two corrections found during implementation

Implementation under the `-002` `GO` is complete and green, but surfaced two things the
`-001` proposal got wrong. Both are corrected here rather than reported after the fact.

### Correction 1 - `target_paths` was incomplete (scope defect)

C2 changes the diagnostic a role-invalid chain fails with. Three existing cases in
`platform_tests/scripts/test_bridge_lifecycle_resolver.py` assert the **old error code** and
therefore fail:

```
test_wrong_document_version_link_or_verdict_role_fails_closed[mutation4-WRONG_STATUS_AUTHOR_ROLE]
test_wrong_prime_author_role_fails_closed
test_roleless_terminal_verified_after_strict_report_fails_closed
```

All three fail on the code, not on the security property:

```
AssertionError: assert 'MALFORMED_CORRECTION_INVALID_TAIL' == 'WRONG_STATUS_AUTHOR_ROLE'
AssertionError: assert 'MALFORMED_CORRECTION_WRONG_SHAPE'  == 'WRONG_STATUS_AUTHOR_ROLE'
```

**Fail-closed is preserved.** Each chain still raises `BridgeLifecycleResolutionError`; only
the diagnostic changes, because the entry now reaches the correction machinery instead of
aborting at the role check. That is exactly the behaviour `-001` described and `-002`
approved. What `-001` failed to do was declare the test file that encodes the superseded
code, so the approved change necessarily invalidates assertions in a file outside its own
scope.

`platform_tests/scripts/test_bridge_lifecycle_resolver.py` is added to `target_paths`. The
edit is confined to updating those three expected codes; no assertion is deleted and no
coverage is weakened. Each updated case will additionally assert that resolution still
raises, so the fail-closed property is pinned independently of the code string.

### Correction 2 - the stated recovery for the motivating thread will not work

`-001` section "Post-Implementation Consequence" claimed that a Prime `NO-ACTION` at v014
plus a role-correct Loyal Opposition verdict at v015 would unwedge
`gtkb-dispatcher-next-foundation-spike`. **That claim is withdrawn.**

With C2 applied, resolution of that thread now reports:

```
BridgeLifecycleResolutionError: Bridge lifecycle has multiple malformed exact versions:
bridge/gtkb-dispatcher-next-foundation-spike-002.md,
bridge/gtkb-dispatcher-next-foundation-spike-013.md
```

The thread carries **two** correction-eligible entries, not one:

- `-013` - the out-of-role `VERIFIED` this thread targets.
- `-002` - first line `GO - Proposal Approved With Observations`, a **decorated** status
  token rather than a canonical one, with `author_identity: OpenRouter F` which parses to no
  role. It was already `classification="malformed"` before this change; resolution simply
  never reached it, because `-013`'s role check aborted first.

The single-correction-per-chain invariant - which `-001` deliberately preserved and T12 pins
- refuses a chain with two correction-eligible entries. So this change makes the thread's
defect *visible and classified*, but does not by itself make it recoverable.

This is disclosed rather than fixed. Widening the correction machinery to handle multiple
malformed entries is a materially larger change to a governance-critical resolver, it was
not reviewed under `-002`, and the decorated-status class is already tracked separately
(`WI-5827`; `bridge/gtkb-wi5637-bounded-decorated-version-history-compatibility`). The
foundation thread needs its own disposition once that class is addressed.

Nothing else changes: C1 and C2 as approved, the test plan, the acceptance criteria, and the
non-impairment and cross-harness dispositions are all carried forward unaltered.

## Problem Statement

`bridge/gtkb-dispatcher-next-foundation-spike-013.md` carries first-line status `VERIFIED`
with `author_identity: prime-builder/goose/G` and `bridge_kind: pb_respond`. Two protocol
violations:

1. `.claude/rules/file-bridge-protocol.md` § Statuses assigns `VERIFIED` to **Loyal
   Opposition**. A Prime-authored `VERIFIED` is not a valid verdict.
2. The § Post-Verdict Transition Table permits `VERIFIED` only as a post-`GO` successor to
   `NEW` or `REVISED`. The observed transition is `GO` (v012) -> `VERIFIED` (v013).
   `ORDINARY_TRANSITIONS["GO"]` is
   `{GO, NEW, REVISED, NO-ACTION, DEFERRED, WITHDRAWN}` - measured live; `VERIFIED` is
   absent, and `POST_GO_REPORT_AUGMENTATIONS` augments only `NEW` and `REVISED`.

### This is load-bearing, not cosmetic

`bridge_lifecycle_resolver.resolve_bridge_lifecycle` **rejects the chain today**:

```
BridgeLifecycleResolutionError: Status VERIFIED has wrong or unreadable
author role 'prime-builder': bridge/gtkb-dispatcher-next-foundation-spike-013.md
```

`implementation_authorization.py` converts resolver errors into `AuthorizationError`, so no
implementation-start packet can ever be minted for this thread. The thread is **wedged** -
the same class WI-5827 documented across 14 threads - and it is the foundation thread of
the P0 Dispatcher Next spine (WI-5617, blocking WI-5618..WI-5624).

### The two gaps, precisely

**Gap A - the rule is enforced at read time only.** The role rule exists and is correct.
It runs when a chain is *resolved*, not when a verdict is *written*, so an invalid verdict
reaches disk and only fails later, at an unrelated caller. The compliance gate already
hosts an equivalent write-time check for a sibling invariant - `_verdict_self_review_deny`
(line 1982, WI-4829) blocks a self-review `GO`/`NO-GO`/`VERIFIED` before it lands - so the
pattern and its dispatch point already exist; the role and transition invariants simply
were not given the same treatment.

**Gap B - role-invalid verdicts have no recovery path.** WI-5629 landed a sanctioned
correction for **malformed** verdicts: append a strict Prime `NO-ACTION`, then a
role-correct Loyal Opposition verdict (`_correction_resolution`,
`scripts/bridge_lifecycle_resolver.py` lines 634-740). That path is unreachable here.
`classification = "malformed"` is set **only** when the first line is not a canonical status
token (lines 377-385). v013's first line **is** `VERIFIED`, so it classifies `strict` and
then fails the strict role check in `_ordinary_resolution`. A strict-but-role-invalid
verdict therefore wedges a thread exactly as a malformed one does, but is the only one of
the two with no way out.

Fixing Gap A alone prevents recurrence and leaves the P0 foundation thread permanently
unresolvable. Both are required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority; the status/author-role
  contract this proposal enforces at write time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each acceptance
  criterion to a test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - discharged by the Project/PAUTH
  metadata above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no `applications/`
  path is touched.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the change adds guards and one recovery
  branch; it removes no existing validation and weakens no fail-closed behaviour.
- `GOV-WORK-TREE-HYGIENE-001` - scoped change; five declared targets, no incidental edits.
- `.claude/rules/file-bridge-protocol.md` - § Statuses and § Post-Verdict Transition Table,
  the two contracts violated by v013.
- `.claude/rules/codex-review-gate.md` - the implementation-start authorization gate whose
  resolution path is wedged by the defect.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-20260806011873` - owner directive authorizing this repair.

## Prior Deliberations

- `DELIB-20260806011873` - owner directive "Fix WI-5967"; admitted WI-5967 to the
  `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` cohort at v5 with permissions and the linked
  specification set carried forward unchanged from v4.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - the master authorization for
  the Dispatcher Next program.
- `WI-5629` (resolved, same project) - "Authorize corrected malformed-verdict chains without
  weakening fail-closed status validation". Its `_correction_resolution` is the mechanism
  this proposal extends. This proposal deliberately preserves its stated constraint: the
  recovery must not weaken fail-closed status validation.
- `WI-5827` - the wedged-thread survey (14 of 17 PB-actionable threads failing strict
  lifecycle resolution before content evaluation). This defect is another instance of that
  class, from a different cause.
- `WI-5939` - the false-terminal finalization class; v013 is the same shape (a terminal
  status that should not have been reachable).
- `bridge/gtkb-dispatcher-next-foundation-spike-013.md` - the offending artifact.
- `bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-001.md` - the sibling P0
  proposal that opened a fresh thread specifically to avoid relying on v013.
- Deliberation search executed 2026-08-06 found no prior decision accepting Prime-authored
  terminal verdicts or rejecting a write-time role guard.

## Requirement Sufficiency

Existing requirements sufficient. The status/author-role contract and the transition table
are already specified in `.claude/rules/file-bridge-protocol.md` and implemented in
`scripts/bridge_lifecycle_resolver.py`. This proposal enforces existing requirements
earlier and makes an existing recovery mechanism reach a case it already should have
covered. No requirement is created or revised.

## Proposed Change

### C1 - Write-time verdict role and transition guard (Gap A)

Add `_verdict_role_and_transition_deny(file_path, content, cwd_path)` to
`.claude/hooks/bridge-compliance-gate.py`, modelled directly on the existing
`_verdict_self_review_deny` (line 1982) and dispatched from the same point (line ~2212).
It denies a bridge write when either holds:

- **Role mismatch.** The first-line status's required author role does not match the role
  parsed from `author_identity`. `GO`/`NO-GO`/`VERIFIED` require `loyal-opposition`;
  `NEW`/`REVISED`/`NO-ACTION` require `prime-builder`.
- **Unlawful transition.** The status is not an allowed successor of the current latest
  status for that thread.

Both checks import the tables and role sets from `scripts/bridge_lifecycle_resolver`
(`ORDINARY_TRANSITIONS`, `POST_GO_REPORT_AUGMENTATIONS`, `PRIME_STATUSES`,
`LOYAL_OPPOSITION_STATUSES`). **No table is duplicated** - a second copy would drift from
the resolver, and a guard that disagrees with the resolver is worse than no guard.

Fail-soft on infrastructure error, matching the sibling guard's documented contract: an
unavailable import or unexpected error returns `None` (allow), because the read-time
resolver remains the backstop. Fail-**closed** on the substantive checks: a determinable
role mismatch or unlawful transition denies.

`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` receives the identical guard.

**Correction to a common assumption.** `.claude/rules/file-bridge-protocol.md` states the
hook is activated byte-for-byte from that template. Measured 2026-08-06, that is **already
false**: the active hook is 117,864 B (`sha256:31cd71f0...`) and the template is 115,200 B
(`sha256:0f7a5614...`). This proposal therefore does not claim to preserve a byte-for-byte
relationship that does not currently hold; it applies the same guard to both copies and
leaves the pre-existing 2,664-byte divergence untouched and unmasked. Reconciling that
drift is separate work and is deliberately not bundled here.

### C2 - Extend correction eligibility to strict-but-role-invalid verdicts (Gap B)

In `scripts/bridge_lifecycle_resolver.py`, treat a **strict verdict whose author role is
wrong for its status** as correction-eligible, exactly as a malformed entry already is:
recoverable by appending a strict Prime `NO-ACTION` followed by a role-correct Loyal
Opposition verdict.

Implementation is deliberately minimal: the existing `_correction_resolution` machinery is
reused unchanged; only the eligibility predicate that currently selects `is_malformed`
entries is widened to also select role-invalid strict entries. The correction *shape*
requirements are untouched, so a role-invalid entry cannot be silently accepted - it still
requires the full corrective chain, authored by the correct roles, before the thread
resolves.

The existing single-correction-per-chain invariant is preserved: a chain containing more
than one correction-eligible entry still fails with `MULTIPLE_MALFORMED_BRIDGE_VERSIONS`
rather than attempting a multi-correction resolution.

### Why this does not weaken fail-closed validation

WI-5629's constraint is explicit and is honoured. Nothing here makes an invalid verdict
valid. A role-invalid `VERIFIED` still confers no verification and no implementation
authority; the thread stays blocked until an independent, role-correct Loyal Opposition
verdict is appended. The change converts a **permanent dead end** into a **governed
recovery that requires the correct roles to complete it** - and C1 ensures the situation
stops arising in the first place.

## Cross-Harness Disposition

Four copies of this gate exist in the repository. Measured 2026-08-06 (sha256 prefix, bytes):

| Copy | Digest | Size | Disposition |
| --- | --- | --- | --- |
| `.claude/hooks/bridge-compliance-gate.py` | `31cd71f0` | 117,864 | **Parity applied** - in `target_paths`. This is the live gate the governed writer invokes via `PROVIDER_VERDICT_GUARDS`. |
| `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | `0f7a5614` | 115,200 | **Parity applied** - in `target_paths`. Scaffold source for adopter installs. |
| `config/hooks/gtkb-bridge-compliance-gate.py` | `7fd9d7f3` | 111,070 | **Deferred, blocked - disclosed gap.** See below. |
| `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/hooks/bridge-compliance-gate.py` | `7fd9d7f3` | 111,070 | **Not modified.** Golden fixture; regenerated by the scaffold flow, not hand-edited. If a scaffold-golden test asserts equality with the template, it will surface at verification and is addressed then rather than pre-emptively edited. |

Per-harness registration, verified by direct inspection rather than assumption:

- **Claude (harness B)** - registers the gate; `.claude/hooks/bridge-compliance-gate.py` is the
  operative copy. Parity applied.
- **Cursor (harness E)** - `.cursor/hooks.json` references `bridge-compliance-gate.py`. Cursor
  reaches the same shared script, so the guard applies without a Cursor-specific edit.
- **Codex (harness A)** - `.codex/hooks.json` contains **no** reference to
  `bridge-compliance-gate.py` (grep returned no match). Codex therefore does not enforce this
  gate today, for this defect or any other it covers. That is a pre-existing coverage gap, not
  one introduced here; it is disclosed rather than silently inherited, and the read-time
  resolver remains the backstop for Codex-authored writes.
- **Goose (harness G)** - no `.goose/hooks.json` present. Same disposition as Codex: no
  write-time enforcement, read-time resolver backstop. Notably, the offending v013 verdict was
  authored by Goose, which is consistent with this gap.
- **Antigravity (C), Ollama (D), OpenRouter (F)** - not registered for this gate; same
  backstop.

### Blocked copy: `config/hooks/gtkb-bridge-compliance-gate.py`

This copy is **excluded from `target_paths` because it cannot currently be written.** The
work-subject guard classifies it as `application_product`
(`workstream_focus.classify_root` measured 2026-08-06), so a write is refused with
`BLOCKED (GTKB-WORK-SUBJECT)` while the session subject is `gtkb_infrastructure`. The same
misclassification blocks `config/hooks/gtkb-bridge-axis-2-surface.py`, so this is a
directory-wide `config/hooks/**` defect, tracked as **WI-5957**.

The disposition is deliberate: the alternative - switching the work subject to `application`
to force the write - would misrepresent GT-KB platform work as application work and defeat
the guard's purpose. This proposal accepts a disclosed, tracked parity gap rather than
subvert a governance control to close it. When WI-5957 lands, this copy should receive the
same guard in a follow-on with `config/hooks/gtkb-bridge-compliance-gate.py` in scope.

No owner waiver is requested. Every gap above is a disclosed pre-existing condition, and none
is created by this change.

## Test Plan (specification-derived)

New: `platform_tests/hooks/test_bridge_compliance_gate_verdict_role_transition.py`

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | `.claude/rules/file-bridge-protocol.md` § Statuses | a `VERIFIED` write with `author_identity: prime-builder/...` is denied, and the reason names the role mismatch |
| T2 | § Statuses | a `NEW`/`REVISED` write authored under `loyal-opposition` is denied |
| T3 | § Statuses (no over-blocking) | a `VERIFIED` authored under `loyal-opposition`, lawful in transition, is allowed |
| T4 | § Post-Verdict Transition Table | a `VERIFIED` written directly onto a latest `GO` is denied as an unlawful transition, even when authored by `loyal-opposition` |
| T5 | § Post-Verdict Transition Table (no over-blocking) | a `VERIFIED` written onto a post-GO `NEW` report is allowed |
| T6 | sibling-guard contract | an infrastructure failure (unimportable resolver) returns allow, not deny |
| T7 | template parity | the template hook and the active hook contain the identical guard |

New: `platform_tests/scripts/test_bridge_lifecycle_role_invalid_correction.py`

| Test | Derived from | Asserts |
| --- | --- | --- |
| T8 | C2 | a chain ending in a strict role-invalid verdict is correction-eligible, not a hard `_fail` |
| T9 | C2 + WI-5629 constraint | role-invalid entry + Prime `NO-ACTION` alone yields the pending-correction diagnostic and **no** implementation authority |
| T10 | C2 + WI-5629 constraint | role-invalid entry + Prime `NO-ACTION` + role-correct LO verdict resolves, and the corrected verdict is the operative one |
| T11 | fail-closed preserved | a correction chain whose corrected verdict is itself role-incorrect still fails `MALFORMED_CORRECTION_INVALID_VERDICT` |
| T12 | single-correction invariant | two correction-eligible entries still fail `MULTIPLE_MALFORMED_BRIDGE_VERSIONS` |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_verdict_role_transition.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_role_invalid_correction.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_role_invalid_correction.py platform_tests/hooks/test_bridge_compliance_gate_verdict_role_transition.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_role_invalid_correction.py platform_tests/hooks/test_bridge_compliance_gate_verdict_role_transition.py
```

The existing resolver suite and the doc-code transition-table consistency test are re-run
to prove the tables are unchanged and no existing validation regressed.

## Acceptance Criteria

1. A Prime-authored `VERIFIED` cannot be written (T1); a Loyal-Opposition-authored
   `NEW`/`REVISED` cannot be written (T2).
2. Legitimate verdicts are unaffected (T3, T5) - no over-blocking.
3. An unlawful `GO -> VERIFIED` transition is denied at write time (T4).
4. The guard fails soft on infrastructure error (T6) and the template stays in parity (T7).
5. A strict role-invalid verdict is correction-eligible and recoverable only via the full
   Prime `NO-ACTION` + role-correct LO verdict chain (T8, T9, T10).
6. Fail-closed validation is not weakened (T11) and the single-correction invariant holds
   (T12).
7. `test_bridge_lifecycle_resolver.py` and the transition-table consistency test show no
   regression; both ruff gates pass on changed files.

## Post-Implementation Consequence (WITHDRAWN - see Revision Basis, Correction 2)

`-001` claimed here that a Prime `NO-ACTION` at v014 plus a role-correct Loyal Opposition
verdict at v015 would unwedge `gtkb-dispatcher-next-foundation-spike`. Measured after
implementing C2, that is false: the thread carries two correction-eligible entries
(`-002` decorated status, `-013` out-of-role verdict) and the preserved
single-correction invariant refuses it. The claim is withdrawn; the thread requires a
separate disposition. Full evidence in Revision Basis, Correction 2.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5967, filed 2026-08-06 after bridge/gtkb-dispatcher-next-foundation-spike-013.md was found carrying a Prime-authored VERIFIED that wedges the P0 WI-5617 foundation thread. Owner directive 'Fix WI-5967' recorded as DELIB-20260806011873.",
  "canonical_authority": ".claude/rules/file-bridge-protocol.md sections Statuses and Post-Verdict Transition Table are the canonical contracts; scripts/bridge_lifecycle_resolver.py ORDINARY_TRANSITIONS and POST_GO_REPORT_AUGMENTATIONS are the code of record. This change adds no new authority and defines no new table.",
  "primary_route": "Bridge verdict writes route through the compliance gate at write time and through resolve_bridge_lifecycle at read time. The guard is added to the existing write-time dispatch point beside _verdict_self_review_deny; the correction path reuses _correction_resolution unchanged.",
  "before_behavior": "A verdict whose author role is wrong for its status, or whose transition is unlawful, is written to disk without objection. It fails only later at read time, wedging the thread permanently: resolve_bridge_lifecycle raises, implementation_authorization converts that to AuthorizationError, and no implementation-start packet can be minted. Only first-line-malformed entries are recoverable via the WI-5629 correction path.",
  "after_behavior": "The invalid write is denied at write time with a reason naming the role mismatch or unlawful transition, so the thread is never wedged in the first place. A strict-but-role-invalid entry already on disk becomes correction-eligible and is recoverable by appending a strict Prime NO-ACTION followed by a role-correct Loyal Opposition verdict, exactly as a malformed entry already is.",
  "self_descriptive_naming": "New guard is named _verdict_role_and_transition_deny, mirroring the existing _verdict_self_review_deny so the sibling relationship is obvious. New test modules are test_bridge_compliance_gate_verdict_role_transition.py and test_bridge_lifecycle_role_invalid_correction.py, each naming the surface and the invariant it pins.",
  "obsolete_guidance_disposition": "No guidance becomes obsolete. The protocol rules are unchanged and are now enforced earlier. WI-5629's malformed-correction documentation remains accurate; this change widens which entries reach that path without altering its shape or its constraint.",
  "history_preservation": "Bridge files are append-only and none is edited, moved, or deleted. bridge/gtkb-dispatcher-next-foundation-spike-013.md stays on disk verbatim as the audit record; recovery works by appending a corrected chain, never by rewriting history.",
  "baseline": "Measured 2026-08-06: resolve_bridge_lifecycle('gtkb-dispatcher-next-foundation-spike') raises BridgeLifecycleResolutionError 'Status VERIFIED has wrong or unreadable author role prime-builder'. ORDINARY_TRANSITIONS['GO'] = {GO, NEW, REVISED, NO-ACTION, DEFERRED, WITHDRAWN}; VERIFIED absent. Existing suites test_bridge_lifecycle_resolver.py and test_bridge_protocol_transition_table_consistency.py pass before the change.",
  "expected_result": "T1-T7 pin the write-time guard in both deny and no-over-block directions plus fail-soft and template parity; T8-T12 pin correction eligibility, the pending-correction no-authority state, successful recovery, preserved fail-closed rejection of an incorrect corrected verdict, and the single-correction invariant. Both pre-existing suites continue to pass; both ruff gates pass.",
  "rollback": "Revert scripts/bridge_lifecycle_resolver.py and the two bridge-compliance-gate copies. The two new test modules are additive and can be deleted independently. No data migration, no bridge-file change, and no MemBase write to undo.",
  "hard_invariants": "Status-to-author-role binding (GO/NO-GO/VERIFIED are Loyal Opposition; NEW/REVISED/NO-ACTION are Prime Builder); the Post-Verdict Transition Table; bridge-file append-only; single correction per chain; and WI-5629's constraint that corrected chains must not weaken fail-closed status validation. All are preserved, and the guard imports the resolver's tables rather than copying them so the two cannot disagree.",
  "fail_closed_conditions": "Substantive checks fail closed: a determinable role mismatch or unlawful transition denies the write. A role-invalid verdict confers no verification and no implementation authority at any intermediate state; the pending-correction state explicitly withholds implementation authority. A corrected verdict that is itself role-incorrect still fails MALFORMED_CORRECTION_INVALID_VERDICT. Infrastructure failure of the guard itself fails soft to allow, matching the sibling self-review guard, because the read-time resolver remains the backstop.",
  "essential_context_preservation": "The offending artifact, its chain, and the resolver diagnostic remain readable and unchanged. The proposal records the live measured evidence (resolver error text, transition-table contents, classification line numbers) so a future reader can reconstruct the diagnosis without re-deriving it, and WI-5967 retains the finding independently of this thread's outcome.",
  "applicability_rationale": "Applies. The change touches scripts/bridge_lifecycle_resolver.py and both copies of the bridge-compliance gate, which are cross-cutting bridge-protocol surfaces every thread's authorization depends on."
}
```

## Risk and Rollback

- **Risk: the write-time guard blocks legitimate verdicts.** The material risk, since a
  false deny would stall the bridge entirely. Mitigated by T3/T5 (both no-over-blocking
  directions), by reusing the resolver's own tables so the guard cannot be stricter than
  the resolver, and by the fail-soft contract (T6) inherited from the sibling guard.
- **Risk: widening correction eligibility launders invalid verdicts.** Mitigated by T9/T11:
  the corrective chain must be completed by the correct roles, and an incorrect corrected
  verdict still fails closed. No implementation authority is granted at any intermediate
  state.
- **Risk: hook and template drift.** Mitigated by T7.
- **Risk: `scripts/bridge_lifecycle_resolver.py` is currently dirty in the worktree.** If a
  peer thread holds a non-terminal claim on it, the implementation-start packet will be
  denied at mint time; that is the gate working correctly, and this proposal will wait
  rather than contend.
- **Rollback:** revert `scripts/bridge_lifecycle_resolver.py` and the two hook copies; the
  two test modules are additive and can be deleted independently.

## Owner Decisions / Input

- **Owner directive 2026-08-06, verbatim: "Fix WI-5967".** Recorded as
  `DELIB-20260806011873` with the full defect analysis, the two-part repair scope, and the
  explicit statement that no bridge file may be edited and no permission is relaxed.
- **PAUTH amendment made under that directive:**
  `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` v5 (active) admits `WI-5967` to the cohort.
  `allowed_mutation_classes`, `forbidden_operations`, and `included_spec_ids` are carried
  forward byte-identically from v4 - a cohort change only, no permission relaxation and no
  specification amendment.
- **`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`** - the master program
  authorization.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. All five declared targets are in-root platform
paths and this bridge file resides under `E:/GT-KB/bridge/`. No `applications/` path is
touched. No artifact is written outside the project root.

## Recommended Commit Type

`fix:` - the change repairs broken governance behaviour: an invariant that should have been
enforced at write time was not, allowing an invalid terminal verdict to wedge a P0 thread.
It is not `feat:` (no new capability surface - the rule and the recovery mechanism both
already exist) and not `refactor:` (behaviour changes: writes that previously succeeded now
correctly fail, and chains that previously dead-ended become recoverable).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
