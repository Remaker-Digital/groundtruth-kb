NEW
::init gtkb pb
::open build

# Bridge lifecycle resolver grandfathers legacy pre-provenance versions (GOV-DOCUMENT-AUTHOR-PROVENANCE-001 conformance)

bridge_kind: prime_proposal
Document: gtkb-wi5670-resolver-legacy-provenance-tolerance
Version: 001
Author: Prime Builder (Claude B)
Date: 2026-07-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 302c4543-bd90-4fe9-b169-e90390e528b1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (session-stated override; durable registry role loyal-opposition)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/bridge_lifecycle_resolver.py::_parse_version` hard-requires the
`author_identity` metadata field on **every** canonical-status bridge version
(the `_required_metadata(... "author_identity" ...)` call plus the following
`_validate_author_role` call). That blanket requirement **contradicts
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`**, whose Contract is explicitly
forward-only: "Existing files at implementation time are grandfathered and are
not required to be backfilled by this specification."

Because `implementation_authorization.py begin` resolves the full thread via
`resolve_bridge_lifecycle`, any thread that contains a single pre-provenance
verdict cannot produce an implementation-start packet — so the
`implementation_start_gate` denies all protected writes and implementation is
blocked. Concrete live impact:
`bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` is a valid
`NO-GO` authored 2026-07-16 by Cursor-E in the pre-contract prose format (it
records reviewer identity as prose — "Reviewer: Loyal Opposition (Cursor E)",
"Review context: dispatcher auto-dispatch
`2026-07-16T20-43-06Z-loyal-opposition-E-c2ed16`" — but carries no
`author_identity:` header). `begin` fails with `MISSING_BRIDGE_METADATA`, so the
already-`GO`'d, PAUTH-authorized P0 work item WI-5152 cannot be implemented.

This is a conformance defect in the resolver, not a data defect in v002 (which
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` explicitly grandfathers). The fix makes the
resolver honor the grandfathering clause while preserving the review-
independence guarantee that the `author_identity` parse ultimately serves.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the governing spec. Its forward-only
  Contract grandfathers pre-implementation files; the resolver must not
  retroactively hard-require the provenance header on grandfathered versions.
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility: origin `defect`, no new public
  API/CLI/behavior beyond removing the defect, no new/revised requirement, two
  files (~<150 net lines); filed under `PROJECT-GTKB-RELIABILITY-FIXES` +
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the resolver is bridge audit-trail
  infrastructure; the fix preserves append-only history (touches no bridge
  files) and the GO/NO-GO/VERIFIED discipline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  every governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project, PAUTH, WI, and
  inline-JSON `target_paths` are explicit in the header above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  executes every changed behavior (legacy tolerance and operative fail-closed).
- `GOV-STANDING-BACKLOG-001` — WI-5670 is the durable owner of this fix.

## Prior Deliberations

- `DELIB-20261032` — Document Artifact Author Provenance Gap Advisory: the
  provenance-gap concern this resolver conformance completes on the read side.
- `DELIB-20260683` — LO Verdict, Document Artifact Author Provenance Contract:
  the review that established the forward-only / grandfathering contract this
  fix conforms the resolver to.
- `DELIB-20260666` — PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE PAUTH Authorization:
  project context for the provenance contract.
- _No prior deliberation addresses resolver legacy-tolerance specifically; this
  proposal is the first to reconcile `resolve_bridge_lifecycle` with the
  grandfathering clause._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No per-fix owner approval is required: this is a fast-lane defect fix
(`GOV-RELIABILITY-FAST-LANE-001`) covered by the standing
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project
membership. The approach was owner-directed: when presented the v002
metadata-gap blocker via `AskUserQuestion` on 2026-07-24 (this interactive
session), the owner selected "Fix the resolver (root fix)" over targeted v002
backfill or deferral. That directive is recorded in this session's transcript
and by the owner-decision tracker.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (forward-only author provenance with
explicit grandfathering of pre-implementation files). The fix makes
`resolve_bridge_lifecycle` conform to that existing requirement; no new or
revised requirement or specification is created.

## Design (exact change)

**File 1 — `scripts/bridge_lifecycle_resolver.py`:**

1. `_parse_version`: when a version's first line is a canonical status token but
   the file has no `author_identity` field, do **not** hard-fail. Return a
   `BridgeVersion` with `classification="legacy"`, `author_identity=None`,
   `author_role=None`, and the parsed `status` / `document` / `responds_to`.
   Skip `_validate_author_role` for that version. Document / Version /
   Responds-to structural checks still apply — only the provenance-header
   requirement is grandfathered.
2. `BridgeVersion`: add an `is_legacy` property (`classification == "legacy"`).
   `is_strict` and `is_malformed` stay `False` for legacy versions, so the
   single-malformed correction path and its count are unaffected.
3. `_ordinary_resolution` and `_correction_resolution`: after selecting the
   operative `implementation_artifact` (the Prime `NEW`/`REVISED` proposal) and
   `implementation_verdict` (the `GO`), **re-validate both** for complete,
   role-correct provenance — `author_identity` present, GO `author_role ==
   "loyal-opposition"`, proposal `author_role == "prime-builder"`. If either
   operative version is legacy/incomplete, **fail closed** with a new stable
   diagnostic code (e.g. `OPERATIVE_VERSION_MISSING_PROVENANCE`). This preserves
   the exact pre-fix guarantee: implementation authority never derives from a
   version lacking verified provenance.

**Why safe:** transition validation (`_validate_ordinary_transitions`) uses
status only, so legacy versions with valid status tokens flow through unchanged;
operative selection is by status; and the operative pair is re-checked. New
bridge files always carry `author_identity` (the write-time
`document_author_provenance_gate` enforces it), so only historical files can be
legacy — precisely the set `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` grandfathers.
The `_go_self_review_error` backstop in `implementation_authorization.py`
remains the independent operative-pair independence guard. Net observable
change: **non-operative** legacy versions stop blocking; **operative-legacy
stays blocked** (previously via the blanket rule, now via targeted
re-validation).

**File 2 — `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:** add the
fixtures in the verification plan; existing strict-path tests are unchanged and
must remain green.

## Spec-Derived Verification Plan

| Requirement / behavior | Verification | Expected result |
| --- | --- | --- |
| Grandfather non-operative legacy version (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`) | New test: thread `NEW` -> legacy `NO-GO` (no `author_identity`) -> `REVISED` -> `GO` | Resolves without error; operative pair = strict `REVISED` proposal + `GO` verdict |
| Legacy is not malformed | New test asserts `is_malformed is False`, `is_legacy is True` for the legacy version | Ordinary resolution path used (no single-malformed correction) |
| Operative `GO` fail-closed | New test: the operative `GO` lacks `author_identity` | Raises `BridgeLifecycleResolutionError` (operative-provenance code) |
| Operative proposal fail-closed | New test: the operative `NEW`/`REVISED` lacks `author_identity` | Raises `BridgeLifecycleResolutionError` |
| No regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --no-header` | All existing + new tests pass |
| Real-world unblock | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5152-modernization-hard-invariant-registry` | `authorized: true` (v002 grandfathered; operative v005 proposal + v006 GO provenance-complete) |
| Lint / format | `groundtruth-kb/.venv/Scripts/ruff.exe check` and `ruff format --check` on both target files | Clean |
| Bridge preflights | applicability + clause preflight on this thread | `preflight_passed: true`; 0 blocking gaps |

## Risk / Rollback

Risk: the resolver feeds the review-independence gate, so an over-broad
relaxation could let implementation authority derive from an unverified version.
Mitigated by the operative re-validation (implementation authority requires a
provenance-complete, role-correct `GO`+proposal pair), the unchanged
`_go_self_review_error` backstop, and the write-time provenance gate that
guarantees new files are never legacy. Rollback: revert the two files in a
single commit; no bridge history, MemBase, or other path is touched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5670-resolver-legacy-provenance-tolerance`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs `resolve_bridge_lifecycle` to conform to
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`; adds no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
