NEW

# Document the governance-emergency-bootstrap exception protocol (sanctioned bridge-GO / verify-hook bypass with audit trail)

bridge_kind: prime_proposal
Document: gtkb-wi4458-governance-emergency-bootstrap-protocol
Version: 001
Author: Prime Builder (harness B / claude)
Date: 2026-06-27 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a0db7838-e5c0-4090-a4e0-68158f676275
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: interactive-prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4458

target_paths: [".claude/rules/governance-emergency-bootstrap-protocol.md", "platform_tests/scripts/test_emergency_bootstrap_protocol_doc.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Document a governance-emergency-bootstrap exception protocol as a new tracked
rule at `.claude/rules/governance-emergency-bootstrap-protocol.md`.

The motivating incident (WI-4449, commit `e90b2f03`): Codex landed
`fix: restore registered governance hooks` with `git commit` plus the verify
bypass because the pre-commit verify path itself invoked registered hooks in the
very set being restored (scan-secrets, dev-environment-inventory-drift,
narrative-artifact-evidence, ruff-format). That is a chicken-and-egg deadlock —
the verify path required the hooks to exist, but the hooks were the artifact
being committed. The bypass was the correct call, but it is currently an
*undocumented* exception class, so the next such deadlock has no canonical,
audit-disciplined path to follow.

The normal bridge protocol (Prime files NEW -> LO GO -> impl-start packet ->
commit -> Prime files post-impl NEW -> LO VERIFIES) cannot run when the defect
being repaired is the infrastructure the protocol itself depends on. This rule
defines a parallel canonical path with explicit audit-trail discipline.

Proposed protocol content (the WI-4458 acceptance):

- **(a) Sanctioned conditions.** Define when the verify bypass and a
  bridge-GO-bypass are sanctioned: a registered hook file is missing or a
  session-block class is active, AND the bridge protocol path itself is blocked
  by the very defect being repaired. Scope is the minimal change that restores
  the foundational subsystem.
- **(b) After-action audit-trail entry.** Require a `WITHDRAWN`-status bridge
  entry after the fix, citing the commit SHA, the deadlock rationale, and the
  counterpart (LO) verification evidence. Precedent:
  `bridge/gtkb-commit-untracked-governance-hooks-002.md` (the WI-4449 closure).
- **(c) Retroactive owner-approval capture.** Require a post-fix Deliberation
  Archive owner-decision record if owner approval was not already on record.

This generalizes the `bridge-essential.md` mandate ("restoring bridge function
is always the top-priority task") from the bridge specifically to other
foundational governance subsystems (registered hooks, gates, the claim system).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the protocol is a narrow, audited exception
  to the bridge-GO / verify discipline this spec anchors; it preserves the audit
  trail (the `WITHDRAWN` after-action entry) rather than weakening it, and
  generalizes the bridge-restoration-is-top-priority mandate.
- `GOV-ARTIFACT-APPROVAL-001` — clause (c) requires retroactive owner-approval
  capture via a Deliberation record, keeping the formal-approval invariant intact
  even for emergency-bootstrap actions.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the new rule is a tracked document
  artifact under change control; its authoring honors document-provenance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata
  is present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives a structural test from the acceptance.
- `GOV-STANDING-BACKLOG-001` — WI-4458 is the standing-backlog work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the protocol converts an
  undocumented exception class into a durable, tracked governance artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — authoring the rule triggers
  the document-lifecycle obligations, satisfied by the structural test below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — governs the artifact-first
  treatment of the emergency-bootstrap exception class.

## Prior Deliberations

- WI-4449 / commit `e90b2f03` and `bridge/gtkb-commit-untracked-governance-hooks-002.md`
  — the precedent emergency-bootstrap action this protocol canonicalizes. This
  proposal does not re-do that fix; it documents the exception class the fix
  established so the next deadlock has a governed path.
- `DELIB-20266267` (owner AUQ 2026-06-27) — bounded authorization admitting
  WI-4458 (with WI-4457, WI-4871) for implementation under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

## Owner Decisions / Input

- `DELIB-20266267` — owner AUQ answer "Bundle under bridge-reliability"
  (2026-06-27) admitted WI-4458 for bounded implementation under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` via
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871`.
- Owner directive this session (2026-06-27): author NEW proposals for the
  genuinely-open reliability/governance work items. The new rule document itself
  is a protected narrative artifact and will require its own narrative-artifact
  approval packet at implementation time, in addition to LO `GO`.

## Requirement Sufficiency

Existing requirements sufficient. WI-4458 states the precise acceptance (the
(a)/(b)/(c) protocol elements). Governing authority is `GOV-FILE-BRIDGE-AUTHORITY-001`
(audit-trail / bridge discipline) and `GOV-ARTIFACT-APPROVAL-001` (retroactive
owner-approval capture). No new or revised specification is required before
implementation; the deliverable is a tracked rule document operationalizing
these existing specs.

## Spec-Derived Verification Plan

New structural test `platform_tests/scripts/test_emergency_bootstrap_protocol_doc.py`:

- **Rule document exists.** Assert `.claude/rules/governance-emergency-bootstrap-protocol.md`
  is present and non-empty. (Verifies WI-4458 deliverable.)
- **Required protocol elements present.** Assert the document contains the three
  acceptance elements: sanctioned-conditions section (a), after-action
  `WITHDRAWN` audit-trail-entry requirement (b) citing commit SHA + rationale +
  verification evidence, and retroactive-owner-approval-via-DELIB requirement
  (c). (Verifies `GOV-ARTIFACT-APPROVAL-001` retroactive-capture linkage and
  `GOV-FILE-BRIDGE-AUTHORITY-001` audit-trail linkage.)
- **Precedent citation present.** Assert the document references the WI-4449
  precedent (`bridge/gtkb-commit-untracked-governance-hooks-002.md`).

Command (repo venv for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_emergency_bootstrap_protocol_doc.py -q --no-header
```

## Risk / Rollback

- **Risk surface:** the rule is documentation; the principal risk is that a
  too-broad exception definition could be read as a general license to bypass
  the bridge. Mitigation: the protocol's sanctioned conditions are narrow
  (foundational-subsystem deadlock only) and every invocation requires the
  after-action `WITHDRAWN` entry + retroactive DELIB, so each use is auditable
  and owner-visible. LO review of the exact wording is the primary control.
- **Rollback:** single-commit revert of the new rule document and the structural
  test. No code-path or state change.

## Recommended Commit Type

`docs` — the deliverable is a new governance/rule document (plus a structural
doc-presence test). No production code behavior changes.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
