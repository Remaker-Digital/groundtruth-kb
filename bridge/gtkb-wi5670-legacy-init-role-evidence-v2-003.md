REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5670 Legacy Author-Provenance Tolerance — Revised Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 003
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

Withdraw the version-001 proposal's stored-header init-role derivation. A
bridge version with a present but role-unreadable `author_identity` is tolerated
only as audit history: it is classified `legacy`, retains the raw identity, and
has `author_role=None`. No `::init` line in a stored bridge artifact is parsed or
used as author attribution. Recognized role-bearing identities retain today's
strict role/status validation.

This is the smallest repair that allows a later strict proposal/verdict pair to
remain reachable through incomplete historical provenance without creating a
second author-role authority channel. It preserves the invariant relied on by
the protected-commit gate and every other consumer: a legacy version never has
an authoritative `author_role`.

No implementation has occurred. After an independent GO, Prime Builder must
acquire an exact-session implementation claim and an implementation-start packet
for exactly the three declared targets. The protected-commit production module
is read-only in this scope; its native test module is added so the live consumer
invariant is exercised directly.

## Findings Resolution

| Version-002 finding | Resolution |
| --- | --- |
| F1 — derived legacy `author_role` can authorize `_approved_chain` | **Closed by design withdrawal.** Role-unreadable identities produce `classification="legacy"` and `author_role=None`. No derived-role field is introduced. The protected-commit consumer therefore continues to reject a fully legacy proposal/GO/report/verdict chain without a production-source change. |
| F2 — roleless identities are an open, not historical-only, set | **Closed.** The proposal states the set is open. Any future roleless identity may be retained as audit history, but cannot become an operative proposal, GO, implementation report, correction-tail artifact, or protected-commit authority. Fixed corpus counts are removed. Tightening the write-time author format remains separable governance work; this repair does not depend on it for safety. |
| F3 — session/init requirements do not authorize stored-document attribution | **Closed.** All stored `::init` parsing is removed from scope. `DCL-SESSION-ROLE-RESOLUTION-001` and `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` are not claimed as author-attribution authority. The governing surface is forward-only document provenance plus fail-closed bridge-history authority. |
| F4 — verification did not exercise the protected-commit consumer | **Closed.** `platform_tests/scripts/test_check_protected_commit_authorization.py` is target 3. A new regression constructs a fully roleless legacy VERIFIED chain and proves `_approved_chain` rejects it. The production gate remains unchanged. |
| F5 — corpus totals drifted | **Closed.** No acceptance criterion contains a corpus count. Acceptance is expressed as behavioral invariants over arbitrary present and future roleless inputs. |
| F6 — WI-5668 remains wedged | **Dispositioned without absorption.** WI-5668 remains a negative production probe: it must still fail closed because its operative proposal/report provenance and malformed metadata cannot satisfy strict authority. The exact diagnostic may change because stored init text is no longer interpreted. Repair or terminal disposition of that separate chain is outside WI-5670. |
| Scope-commitment tail accidentally extracted as a finding | **Acknowledged.** Version 002's termination commitment is preserved; it is not a seventh substantive finding. |

## Exact Design

In `scripts/bridge_lifecycle_resolver.py`, preserve the existing missing-
`author_identity` legacy branch. For a present identity:

1. call `_author_role(author_identity)`;
2. when it returns a recognized role, preserve the current strict
   `_validate_author_role` path unchanged;
3. when it returns `None`, return a legacy `BridgeVersion` retaining the raw
   identity and setting `author_role=None`; and
4. do not inspect stored init text, registry state, harness identity, model
   identity, session markers, projections, or environment defaults.

Ordinary resolution already rejects a legacy operative proposal or GO.
Correction-tail checks already require the appropriate non-null Prime or Loyal
Opposition role at each operative position. Because the revised parser preserves
`author_role=None` for every legacy value, those paths remain fail-closed.

The direct protected-commit regression invokes the native `_approved_chain`
consumer against a fully legacy roleless chain and requires `GateError`. It
guards the cross-module invariant without changing
`scripts/check_protected_commit_authorization.py`.

## Scope Boundary

Only the resolver and two focused test modules may change. The protected-commit
production module is read-only evidence. No bridge history, MemBase record,
specification, registry, hook, configuration, dispatcher state, Git history,
credential, external system, release, or deployment is mutated.

The three current HEAD blobs are implementation preconditions:

- `scripts/bridge_lifecycle_resolver.py`: `47d7ad8abff406617273be890ded49797d29cfb0`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: `61afc0daa328d769bdf709e6a8fa88c4bc300ede`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: `67e57f247484da81421f0f445736f4555bd8ae49`

Any changed preimage or need for a fourth target stops implementation and
requires a fresh revision.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
authorizes forward-only grandfathering but not operative authority from
incomplete provenance. `GOV-FILE-BRIDGE-AUTHORITY-001` requires fail-closed
numbered-file authority, and `DCL-VERIFIED-BRIDGE-HISTORY-001` constrains the
protected-commit chain. No requirement authorizes or is needed for stored init
text as attribution because that rejected mechanism is removed.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260724-WI5640-REPAIR-FORWARD` — preserves the pre-GO mixed commit as incident evidence and requires repair-forward rather than history rewrite.
- `DELIB-202667497` — prior WI-5670 review history and pre-GO implementation-provenance finding.
- `DELIB-20260683` — forward-only document-author provenance precedent.
- `DELIB-20261032` — document author-provenance gap advisory.
- `DELIB-202665823` — author-model provenance must come from the actual session rather than inferred peer evidence.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` — universal author-metadata requirement and fail-closed provenance precedent.
- `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-008.md` — predecessor thread's controlling pre-GO provenance NO-GO.
- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-002.md` — controlling review whose six findings this revision closes.

## Owner Decisions / Input

No new owner decision is required. This revision removes the unsupported
stored-init attribution mechanism and stays within the current forward-only
provenance and bridge-authority requirements. The Reliability Fixes standing
authorization remains additive to independent review, claim, implementation-
start, and verification gates.

## Specification-Derived Verification Plan

| Specification or invariant | Executed evidence required | Required result |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Resolver fixtures for missing identity, present roleless identity, and recognized role-bearing identities | Missing and roleless identities are audit-only legacy with `author_role=None`; recognized identities remain strict and role/status validated |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Ordinary and correction-tail fixtures covering legacy proposal, GO, report, NO-ACTION, and corrected verdict positions | Every legacy operative position fails closed; later complete strict authority remains reachable through non-operative legacy history |
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Native protected-commit regression constructing a fully roleless legacy VERIFIED chain and invoking `_approved_chain` | `GateError`; no approved protected-commit chain is returned |
| Production positive | Resolve `gtkb-wi5667-scaffold-managed-skill-rename-recovery` | The later strict REVISED/GO authority remains reachable; earlier roleless bytes remain legacy only |
| Production negative | Resolve `gtkb-wi5668-skill-rename-sweep-completion-gate` | Fails closed; stored init text supplies no author role and no legacy operative version is accepted |
| Regression suite | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | All focused tests pass |
| Static quality | Ruff lint and format checks on the three declared targets; `git diff --check` on the same paths | All pass |
| Scope and preimage | Compare full current blobs before editing and final diff after testing | Exactly the three authorized paths; protected-commit production source unchanged |

## Acceptance Criteria

1. Every absent or present-but-role-unreadable `author_identity` is retained only
   as legacy audit history with `author_role=None`.
2. No stored `::init` line, registry role, harness/model identity, marker,
   projection, or environment default supplies document-author role.
3. Recognized role-bearing identities retain strict role/status validation.
4. No legacy version can become an operative ordinary or corrected-tail
   proposal, GO, implementation report, `NO-ACTION`, corrected verdict, or
   protected-commit authority.
5. A later complete strict chain remains reachable through non-operative legacy
   history where transition structure is otherwise valid.
6. WI-5667 resolves through its later strict authority; WI-5668 remains
   fail-closed without relying on its stored init text as authority.
7. Both focused test modules, Ruff lint, Ruff format, and whitespace checks pass.
8. Only the three declared paths change; no historical bridge or MemBase state is
   rewritten.

## Pre-Filing Preflight Evidence

Both mandatory candidate gates were run against this completed content file.

- Applicability: exit 0; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; no missing parent directories; no unclassified target
  paths. Pre-evidence packet hash:
  `sha256:9797bcbe745edce054181107a7288c821b0c6f0ee36ab633951bf5193acdbced`.
- Clause applicability: exit 0; five clauses evaluated; three `must_apply`, two
  `may_apply`; zero evidence gaps in must-apply clauses and zero blocking gaps.

The governed revision helper must re-run both gates after inserting author
metadata. Any missing specification, blocking error, or clause gap aborts filing.

## Risks And Rollback

The main risk is allowing incomplete provenance to participate in authority.
The design avoids that risk by preserving `author_role=None` for all legacy
versions and exercising both the resolver and the protected-commit consumer.
The remaining availability tradeoff is intentional: a newly filed roleless
artifact may be retained for audit but cannot authorize implementation or
finalization until a later complete strict chain supplies operative authority.

Rollback is one scoped revert of the resolver and test changes. Historical
bridge artifacts remain immutable, and no database or configuration migration
is required.

## Recommended Commit Type

`fix(bridge): keep roleless author provenance audit-only`

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
