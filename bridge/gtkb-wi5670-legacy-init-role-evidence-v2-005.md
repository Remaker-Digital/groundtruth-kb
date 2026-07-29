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

# WI-5670 Legacy Author-Provenance Tolerance — Corrected No-Index Authority

bridge_kind: prime_proposal
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 005
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-004.md

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

Accept v004 and remove `DCL-VERIFIED-BRIDGE-HISTORY-001` from this proposal's
authority and verification mapping. That DCL's live v1 procedure is confined to
the VERIFIED runner and still requires retired `bridge/INDEX.md`; this proposal
does not claim to implement, exercise, or satisfy it. Its DCL/GOV contradiction
is handled only by the separate
`gtkb-lo-verified-runner-index-dcl-conflict-advisory` disposition path.

The actual no-index authority is
`GOV-FILE-BRIDGE-AUTHORITY-001` v3: numbered status-bearing files are the
append-only document chain, and malformed, conflicting, duplicate, or
unreadable required state fails closed. Combined with the forward-only
grandfathering in `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and the protected-
mutation/finalization fail-closed requirements in
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`, it directly supports the proposal's
audit-only legacy invariant and the protected-commit consumer regression.

All v003 design, scope, preimages, and findings resolutions remain unchanged:
a present but role-unreadable `author_identity` is retained only as
`classification="legacy"` with `author_role=None`; no stored `::init` or other
derived signal becomes document-author authority. No implementation has
occurred, and this revision performs no MemBase mutation or write.

## Findings Resolution

| v004 required correction | Resolution |
| --- | --- |
| Remove the retired-aggregate DCL as resolver/protected-commit authority | **Closed.** `DCL-VERIFIED-BRIDGE-HISTORY-001` is absent from Specification Links and from every acceptance/verification claim. It appears only in historical finding/disposition prose identifying why it is not authority. |
| State actual no-index authority | **Closed.** `GOV-FILE-BRIDGE-AUTHORITY-001` A1/A5 governs the numbered chain and fail-closed malformed state; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` governs forward-only grandfathering; `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` governs protected-operation and finalization failure behavior. |
| Map resolver and protected-commit tests to current authority | **Closed.** The verification table maps ordinary/correction-tail resolver fixtures to bridge-authority A1/A5 and the native `_approved_chain` regression to governed-Git A2/A8/A12 plus bridge-authority A5. |
| Preserve v003 design, three paths, and preimage gate | **Closed.** Design and target set are unchanged; all three worktree blobs still equal the v003 HEAD blobs recorded below. |
| Separate DCL correction | **Closed by non-absorption.** The advisory remains evidence only; no DCL, runner, registry, or retired aggregate change is authorized here. |

## Exact Design

In `scripts/bridge_lifecycle_resolver.py`, preserve the current missing-
`author_identity` legacy branch. For a present identity:

1. call `_author_role(author_identity)`;
2. preserve strict `_validate_author_role` behavior when a role is recognized;
3. when the role is unreadable, return a legacy `BridgeVersion` retaining the
   raw identity and setting `author_role=None`; and
4. do not inspect stored init text, registry state, harness/model identity,
   markers, projections, shared envelopes, or environment defaults.

Ordinary resolution already rejects legacy operative proposal/GO positions.
Correction-tail checks already require non-null, role-correct Prime and Loyal
Opposition identities in operative positions. Because legacy items retain
`author_role=None`, those paths remain fail closed.

The direct protected-commit regression constructs a fully roleless legacy
chain, invokes `_approved_chain`, and requires `GateError`. Production
`scripts/check_protected_commit_authorization.py` is read-only evidence and is
not changed.

## Scope And Preimage Boundary

The three current worktree blobs equal HEAD and remain the implementation gate:

- `scripts/bridge_lifecycle_resolver.py`: `47d7ad8abff406617273be890ded49797d29cfb0`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: `61afc0daa328d769bdf709e6a8fa88c4bc300ede`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: `67e57f247484da81421f0f445736f4555bd8ae49`

Any changed preimage or need for a fourth target stops implementation and
requires another revision. The protected-commit production module and all DCL,
runner, registry, hook, configuration, dispatcher, and bridge-history surfaces
are excluded from mutation.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
permits forward-only grandfathering without backfill;
`GOV-FILE-BRIDGE-AUTHORITY-001` requires numbered-file authority and fail-
closed malformed/unreadable state; and
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` requires protected operations and
terminal finalization to reject invalid authorization or attribution evidence
without advancing lifecycle. No stored-document attribution mechanism and no
retired-index exception is required or introduced.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
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

- `DELIB-20260724-WI5640-REPAIR-FORWARD` — preserve the pre-GO mixed commit as incident evidence and repair forward.
- `DELIB-202667497` — prior WI-5670 review history and pre-GO implementation-provenance finding.
- `DELIB-20260683` — forward-only document-author provenance precedent.
- `DELIB-20261032` — document author-provenance gap advisory.
- `DELIB-20266119` — owner-approved no-index cutover; it confirms why the retired-aggregate DCL is not used here.
- `DELIB-202665823` and `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` — fail-closed author-provenance precedents.
- `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-008.md` — predecessor chain's controlling pre-GO provenance NO-GO.
- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-002.md` and `-004.md` — controlling independent findings closed by v003 and this correction.

## Owner Decisions / Input

No new owner decision is required. This revision narrows its authority claims
to current no-index specifications and does not select or mutate the separate
formal-artifact advisory. The active Reliability Fixes standing PAUTH remains
additive to independent GO, exact claim, implementation-start, report,
independent verification, and finalization gates.

## Specification-Derived Verification Plan

| Specification or invariant | Executable verification | Required result |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Resolver fixtures for missing identity, present roleless identity, and recognized role-bearing identities | Missing and roleless values remain audit-only legacy with `author_role=None`; recognized identities remain strict and role/status validated. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` A1/A5 | Ordinary and correction-tail fixtures over numbered files with legacy proposal, GO, report, NO-ACTION, and corrected-verdict positions | Every legacy operative position fails closed; later complete strict authority remains reachable through non-operative legacy history. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` A2/A8/A12 | Native protected-commit regression constructing a fully roleless legacy terminal chain and invoking `_approved_chain` | `GateError`; no approved chain, protected mutation, commit, or lifecycle advance. |
| Production positive | Resolve `gtkb-wi5667-scaffold-managed-skill-rename-recovery` | Later strict REVISED/GO authority remains reachable; earlier roleless bytes are audit-only. |
| Production negative | Resolve `gtkb-wi5668-skill-rename-sweep-completion-gate` | Fails closed; stored init text supplies no author role and no legacy operative version is accepted. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Complete focused suite passes and directly exercises both consumers. |
| Static quality and hygiene | Ruff check/format and `git diff --check` on all three targets; final scoped status/diff | Pass; exactly three authorized paths and no DCL/runner/production-gate mutation. |
| Proposal gates | Applicability and clause candidate preflights against this exact revision | Pass with zero missing specifications, errors, evidence gaps, or blocking gaps. |

## Acceptance Criteria

1. Every absent or present-but-role-unreadable `author_identity` is audit-only
   legacy with `author_role=None`.
2. No stored `::init`, registry/harness/model identity, marker, projection,
   shared envelope, or environment default supplies document-author role.
3. Recognized role-bearing identities retain strict role/status validation.
4. No legacy version can become an operative ordinary or corrected-tail
   proposal, GO, report, NO-ACTION, corrected verdict, or protected-commit
   authority.
5. A later complete strict chain remains reachable through non-operative legacy
   history where transition structure is otherwise valid.
6. WI-5667 resolves through later strict authority; WI-5668 remains fail closed
   without treating stored init text or the retired aggregate as authority.
7. The resolver and protected-commit test suites, Ruff, format, and whitespace
   checks pass.
8. Only the three declared paths change from their pinned blobs; no historical
   bridge, DCL, MemBase, registry, runner, config, dispatcher, or Git-history
   state is rewritten.

## Pre-Filing Preflight Evidence

- Candidate applicability preflight: PASS; `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`.
- Candidate clause preflight: PASS; 5 clauses evaluated, 3 `must_apply`,
  2 `may_apply`, 0 must-apply evidence gaps, 0 blocking gaps, exit 0.

## Risks And Rollback

The main risk is allowing incomplete provenance to participate in authority.
The design avoids it by preserving `author_role=None` for all legacy versions
and exercising both the resolver and the protected-commit consumer under the
current no-index authority. The separate active DCL contradiction is not
silently cured or used as authority.

Rollback is one scoped revert of the resolver and two test modules. Historical
bridge artifacts, the protected-commit production module, the VERIFIED runner,
formal artifacts, and database/configuration state remain unchanged.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
