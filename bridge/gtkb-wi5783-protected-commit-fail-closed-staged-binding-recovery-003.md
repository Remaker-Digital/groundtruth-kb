REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; non-dispatching manual continuation; TAFE deliberately disabled
author_metadata_source: current parent session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5783-protected-commit-fail-closed-staged-binding-recovery
Version: 003
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5783-protected-commit-fail-closed-staged-binding-recovery-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5783
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

# Revised Recovery Implementation Proposal — WI-5783 protected-commit fail-closed staged binding

## Revision Claim

This revision answers every finding in NO-GO version 002 without broadening the
two-path repair. It replaces the noncontrolling WI-restricted authorization in
the operative header with the active list-free whole-project authorization,
serializes behind the one genuinely live same-target implementation report,
and adds a bounded repair for the currently failing full-suite fixture while
preserving the freshness gate it tests.

No source or test mutation may begin until WI-5824 reaches an independently
reviewed terminal state, the two targets are rechecked clean and unreserved,
this revision receives independent Loyal Opposition GO, and the implementing
Prime Builder acquires an exact current-session claim plus a fresh schema-v3
implementation-start packet.

## Finding Responses

### P1 — controlling project-only authorization corrected

The operative authorization is now
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` version 2.
It is active, non-expiring, list-free, has no excluded work items, and covers
source and test mutation for every active project member while retaining all
ordinary proposal, GO, claim, packet, target-path, report, and independent
verification gates. WI-5783 is an active member of the active
`PROJECT-GTKB-HOUSEKEEPING-HARDENING` project.

The active but WI-restricted
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3`
is retained only as historical exact-scope provenance. It is not a competing
operative grant. The MemBase work item's legacy `approval_state: unapproved`
is likewise noncontrolling under the owner's project-only approval doctrine;
active project membership plus the list-free project PAUTH is the approval
authority, so no work-item-specific AUQ is required.

### P1 — same-target ownership is serialized, not merged

The current physical bridge chain
`gtkb-wi5824-protected-commit-checker-null-safety-ordering` is latest
`REVISED` at version 009 and declares the same two target paths. Its committed
WI-5824 behavior remains awaiting independent verification at the current
post-WI-5742 baseline. WI-5783 therefore must not claim, start, or edit either
target until WI-5824 becomes terminal and no same-target claim or live start
packet remains.

After that terminal disposition, the implementer must re-read both target
files at current HEAD and preserve these established behaviors:

- WI-5824 state-first, null-safe publication-capability clearance and
  implementation-time terminal-evidence ordering;
- WI-5742 bounded evaluation, invocation-scoped registry snapshot reuse,
  protected-path prefiltering, and single-pass classification; and
- all resolved WI-5659 prefilter/materialization/finalizer behavior recorded by
  the terminal VERIFIED v2 recovery chain.

The WI-5783 production hunk belongs in explicit-input normalization and
validation around `evaluate(..., paths=...)`; it must not alter WI-5824's
capability-clearance or finalized-packet functions. The test additions may
share the approved focused test module but must be named and grouped as
WI-5783 regressions. If post-WI-5824 source movement makes that hunk boundary
false, implementation stops and returns through a new reviewed revision.

The older `gtkb-artifact-registry-authoritative-hygiene-sweep` version 002 GO
is a governance-design approval only. Its own verdict expressly forbids source
implementation and requires separate child implementation proposals, so its
incidental checker-path declaration is not an executable same-target claim.
The resolved WI-5659 v2 recovery is terminal VERIFIED and its work item is
resolved; the older prefilter carrier does not reopen that completed work.

At this revision's audit baseline, both target paths are clean, the current
implementation-start packet is for WI-5694 on an unrelated test path, and the
recovery slug has no active work-intent claim. Those observations are evidence
only, not permission to bypass the serialization condition above.

### P1 — failing complete-suite baseline diagnosed and brought into scope

Fresh execution at HEAD `75decbfa704fe50288aecbc5669def329a0825df` produced
`1 failed, 175 passed, 1 warning in 113.18s`. The sole failure is
`test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits` at line
3505. Its candidate embeds a packet hash built by the parent-process
`scripts.bridge_applicability_preflight` module, then asks a copied,
isolated fixture compliance gate to rebuild that packet. The two derivations
currently disagree, and the gate correctly rejects the embedded hash as stale,
expecting
`sha256:0ab1e409b60e1a5558195cc2f96329c756c56de531824273a6bb14559fdbff39`.

The failure is not outside this proposal: it is in the already-declared test
target. The repair is deliberately test-fixture-only unless implementation
evidence proves a production defect. The fixture must derive the embedded
packet anchor through the same copied, isolated applicability-preflight module
and fixture authority state that the copied compliance gate uses. It must then
continue to prove both the live audit and real-index-only snapshot audit pass.
A paired negative assertion must change the responded-to source bytes after
packet construction and prove the unchanged hash is rejected as stale. The
implementation must not hard-code the currently expected hash, suppress the
freshness check, weaken candidate-evidence binding, or make the production
gate accept divergent packet derivations.

If the isolated re-derivation still disagrees after the fixture uses one
authority path, the implementer must stop and revise rather than changing
production preflight semantics under this two-target proposal.

## Current Defect Evidence

The WI-5783 production defect remains present at HEAD. `_normalize_rel` only
strips whitespace, changes separators, and removes leading `./`; it does not
canonicalize an absolute in-root path or reject empty, globbed, escaped,
directory, duplicate, casefold-colliding, or out-of-root explicit selections.
`evaluate()` currently maps explicit `paths` through that helper and sends the
result directly to `_evaluate_selected`; therefore an empty explicit list or a
selection that classifies to no protected target can still return PASS.

## Requirement Sufficiency

Existing requirements sufficient. WI-5783 and linked TEST-11755 define the
fail-closed explicit-selection and exact staged-content outcomes. The owner
project-approval decisions define the controlling project-only authority. This
revision only reconciles authority precedence, current same-target ordering,
and an executable verification baseline.

## Scope And Implementation Plan

The exclusive implementation targets remain:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

Implementation proceeds in four bounded parts after all conditions are met:

1. Add one explicit-input normalization/validation helper used only when
   `evaluate(..., paths=...)` is selected. It must require at least one input,
   reject blank entries, glob syntax, directory shorthand, directories,
   duplicates and normalized Unicode/casefold collisions, and reject paths
   that escape or cannot be expressed canonically relative to the resolved
   repository root.
2. Canonicalize valid absolute in-root and relative in-root explicit paths to
   one repository-relative POSIX form before protected-path classification.
   After canonicalization, fail when the explicit set contains no protected
   target. Preserve the ordinary `--staged` no-protected-path no-op behavior.
3. Bind committed-terminal clearance to the exact current staged path, status,
   mode, object identifier, SHA-256 content digest, complete manifest, and
   unexpired/operation-valid authority already required by the current
   transaction path. Historical terminal path-glob evidence must not replay
   over substituted bytes. Preserve valid live-GO clearance.
4. Repair the schema-v2 hash fixture through one isolated authority path and
   add the negative stale-source assertion described above. Do not weaken the
   production freshness gate.

No dispatcher/TAFE, routing, harness configuration, capability registry,
credential, external system, destructive cleanup, history rewrite, push,
deployment, release, database, formal artifact, or unrelated path mutation is
in scope. No historical bridge file may be modified or removed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — fail-closed numbered lifecycle and exact
  terminal commit evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active project membership
  plus the controlling list-free project grant.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not replace GO,
  claim, start, reporting, or independent verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — revalidate the
  controlling V2 grant at every protected operation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — terminal clearance and
  packet freshness remain deterministic and re-derivable.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — authorization binds the current
  staged transaction rather than historical path-only evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links and
  mapped tests are present.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — controlling PAUTH,
  active project, member WI, and exact target paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — full mapped execution is
  required before terminal verification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve WI-5824, WI-5742,
  resolved WI-5659, and valid live-GO behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — current bridge, project, PAUTH, Git,
  claim, packet, source, and test evidence is freshly derived.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve both rejected and revised
  lifecycle evidence append-only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every target and evidence source
  remains within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — work-item-specific
  approval state is not implementation authority.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — active project
  members inherit the parent project authorization.
- `DELIB-202667719` — list-free project authorization controls the retained
  WI-restricted grants.
- `DELIB-202667721` — owner grant for the whole Housekeeping Hardening project.
- `DELIB-202667734` — v2 schema-shape repair preserving the whole-project grant.
- `DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION` — historical exact
  repair scope preserved without operative PAUTH precedence.
- `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION` —
  owner confirmation of the bounded behavior.

## Owner Decisions / Input

The list-free whole-project grant is already owner-approved and controlling.
WI-5783 is an active project member, and the legacy per-WI `approval_state`
does not create an additional approval gate. No new owner decision or waiver is
required for this revision. Independent review and all implementation gates
remain mandatory.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5783; TEST-11755; whole-project PAUTH v2; NO-GO v002; WI-5824 v009; HEAD 75decbfa7",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001",
  "primary_route": "scripts/check_protected_commit_authorization.py --paths <explicit paths>",
  "before_behavior": "Invalid or protected-target-free explicit selections can pass, and the complete focused suite contains one stale fixture-hash failure.",
  "after_behavior": "Explicit selection is canonical and fail-closed, exact staged binding remains mandatory, and the isolated freshness fixture passes without weakening stale-hash rejection.",
  "self_descriptive_naming": "Diagnostics identify the invalid explicit selection or exact transaction-binding failure.",
  "obsolete_guidance_disposition": "WI-restricted V3 remains historical provenance; list-free project V2 controls.",
  "history_preservation": "All rejected, superseded, and terminal bridge evidence remains append-only and unchanged.",
  "baseline": {
    "head": "75decbfa704fe50288aecbc5669def329a0825df",
    "source_sha256": "5DC75E85B32086F77EC939AB1D9AC7B7FF45DB4BF697A45FF7640340059F352E",
    "test_sha256": "4D0001A9B6B2FB3BDDF45C9E5C06295BA6F072388C78BED6AC51413C86E371F1",
    "focused_suite": "1 failed, 175 passed"
  },
  "expected_result": {
    "summary": "Fail-closed explicit selection and exact staged evidence with a green complete checker suite.",
    "scope": ["explicit selection validation", "absolute in-root canonicalization", "terminal replay prevention", "exact staged binding", "isolated freshness fixture"]
  },
  "rollback": {
    "instructions": "Use a separately governed forward proposal limited to the same two targets.",
    "verification": "Rerun complete checker tests, WI-5824/WI-5742 non-impairment selection, Ruff, format, diff check, and bridge preflights."
  },
  "hard_invariants": [
    "TAFE and dispatcher remain untouched",
    "WI-5824 reaches terminal before WI-5783 implementation",
    "No historical path glob authorizes substituted bytes",
    "Freshness checks remain fail-closed",
    "Valid live-GO clearance remains available"
  ],
  "fail_closed_conditions": [
    "Invalid explicit selection",
    "No protected explicit target",
    "Stale or malformed packet",
    "Staged manifest, status, mode, object, or digest mismatch"
  ],
  "essential_context_preservation": "Project-only authority, exact targets, current collision ordering, existing checker behavior, and full-suite failure evidence remain explicit."
}
```

## Specification-Derived Verification Plan

| Requirement | Test or command | Required result |
| --- | --- | --- |
| Empty/invalid explicit selection | New WI-5783 CLI and direct-evaluate regressions for empty, blank, globbed, directory, escaped, out-of-root, duplicate, Unicode/casefold-colliding, and protected-target-free inputs | Every invalid explicit selection returns structured FAIL/nonzero and names the reason. |
| Absolute in-root normalization | Temporary-root test with an absolute protected path | The canonical repository-relative POSIX path is evaluated as protected. |
| Staged no-op compatibility | Existing and focused `--staged` test with no protected target | PASS remains valid for an ordinary staged set containing no protected path. |
| No terminal replay | Stage changed same-path bytes after historical terminal evidence | Historical evidence cannot clear the new object/content. |
| Exact staged binding | Tests for path, status, mode, OID, SHA-256, deletion, manifest, and index-snapshot mismatch | Only one exact current staged transaction clears. |
| Packet and authority validity | Expired, malformed, stale, tampered, never-live, PAUTH-denied, and unbound packet regressions | Every invalid packet fails closed. |
| Live-GO non-impairment | Existing live-GO clearance tests | A valid GO'd exact target still clears. |
| WI-5824/WI-5742/WI-5659 non-impairment | `-k "wi5824 or capability_clearance or finalize_verified_same_transaction or committed_terminal_thread or transaction_local or wi5659 or evaluation_budget"` | All selected tests pass at the implementation postimage. |
| Isolated packet freshness fixture | Repaired `test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits` plus stale-source negative assertion | Live and index-only audits pass for one authority-derived hash; altered source with old hash is denied. |
| Complete checker suite | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | All 176 currently collected tests plus new WI-5783 cases pass; zero failures. |
| Static quality | `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`; `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`; `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | All pass. |
| Scope and ownership | `git diff --name-only` plus current claim/start collision validation immediately before implementation and report filing | Only the two declared targets differ; WI-5824 is terminal; no foreign claim or packet reserves either target. |
| Governance | Applicability and mandatory clause preflights against this exact revision/report | No missing required/advisory specs and zero blocking clause gaps. |

## Acceptance Criteria

1. The operative header cites the active list-free whole-project V2 PAUTH,
   active project, active WI member, and only the two exact targets.
2. WI-5824 reaches a terminal independent disposition before WI-5783 claims or
   mutates either target; established WI-5824, WI-5742, and WI-5659 behavior is
   preserved at the implementation postimage.
3. Empty, blank, globbed, directory, escaped, out-of-root, duplicate,
   Unicode/casefold-colliding, and protected-target-free explicit selections
   fail closed with structured diagnostics.
4. Valid absolute in-root paths canonicalize to repository-relative POSIX paths
   before protection classification; staged no-protected transactions retain
   their valid no-op behavior.
5. Historical terminal evidence cannot authorize substituted staged bytes;
   clearance binds the exact path, status, mode, OID, SHA-256, complete
   manifest, authority, and validity evidence.
6. The schema-v2 fixture derives one packet hash through the isolated authority
   path and proves source drift still makes that hash stale.
7. The complete checker suite, non-impairment selection, Ruff lint, Ruff format,
   diff check, applicability preflight, and clause preflight all pass.
8. No path beyond the declared two changes, and independent verification uses
   governed atomic finalization or refuses terminal publication.

## Risks / Rollback

Failing explicit protected-target-free selections is an intentional
compatibility tightening; staged-mode no-op behavior remains unchanged.
Canonicalization must remain root-contained and must not follow an out-of-root
escape. The fixture repair risks masking freshness drift if implemented as a
constant or bypass, so the negative stale-source assertion is mandatory.

Rollback is forward-only through a separately reviewed proposal limited to the
same two targets. It must not restore unsafe empty/ambiguous input, historical
path-only replay, or divergent packet-hash authority.

## Pre-Filing Preflight Evidence

Candidate applicability preflight passed with `missing_required_specs: []`,
`missing_advisory_specs: []`, and `blocking_errors: []`. Its operation-time
evaluation selected the active list-free whole-project V2 authorization and
allowed both declared targets for `implementation_packet_create` and
`implementation_start`.

The mandatory clause preflight evaluated five registered clauses: four
`must_apply`, one `may_apply`, zero evidence gaps in must-apply clauses, and
zero blocking gaps (exit 0). Because this is a non-dispatchable draft outside
`bridge/`, the writer must rerun both gates against the exact candidate bytes
and canonical live target identity immediately before filing; no draft packet
hash is represented as a live filing anchor.
