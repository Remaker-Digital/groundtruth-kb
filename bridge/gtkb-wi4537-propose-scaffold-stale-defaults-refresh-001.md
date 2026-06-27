NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e150e9ce-4657-4130-9e10-af48d3e79a44
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4537 refresh gtkb_propose_scaffold stale defaults

Document: gtkb-wi4537-propose-scaffold-stale-defaults-refresh
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: WI-4537
Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-WI-4537-SCAFFOLD-DEFAULTS-REFRESH

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

## Summary

`scripts/gtkb_propose_scaffold.py` generates a "structurally compliant" NEW
bridge-proposal scaffold body. Two of its emitted defaults are stale relative to
the current bridge gates, so a body produced from the scaffold can fail the very
gates the scaffold is meant to satisfy:

1. The emitted verification command (the scaffold's pytest invocation template,
   currently around line 222) carries a short plugin-selection flag whose value
   pattern matches the credential scanner's password-flag heuristic. A scaffold
   body that includes that flag is blocked by the credential scan / scanner-safe
   writer at Write time. (This proposal deliberately describes the flag in words
   rather than quoting it, to avoid tripping the same scanner on this file.)

2. `DEFAULT_BRIDGE_KIND` (line 40) is `prime_proposal`, emitted as a
   `bridge_kind:` header (line 174). That value is not in the bridge-compliance
   gate's recognized bridge_kind set ({spec_intake, governance_review,
   loyal_opposition_advisory}); implementation-kind proposals are gated by their
   Project Authorization line, not by a bridge_kind exemption. Emitting an
   unrecognized bridge_kind is stale and misleading.

Net effect: the scaffold, whose purpose is to produce a first-pass-clean
proposal body, currently seeds two defects an author must hand-correct.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge authority; the scaffold must emit a body
  that satisfies the current bridge-compliance gate.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4537 is the canonical backlog record for this
  work; no bulk backlog operation is performed.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the corrected
  defaults are enforced by a spec-derived test that audits the generated body.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4537 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop; basis for the
  covering PAUTH.
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-001.md / -006.md and
  bridge/gtkb-wi4854-extract-target-paths-cross-gate-consistency-001.md — recent
  evidence that scanner-tripping flags and stale form defaults cause real filing
  friction; this WI removes one such seed at the scaffold source.
- WI-3268 — pre-filing mechanical lints; a scaffold that emits a gate-clean body
  reduces the lint surface there.
- No prior deliberation rejects refreshing the scaffold defaults.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already requires
proposals to satisfy the bridge-compliance gate; this WI makes the scaffold emit
a body that does so by default. No new or revised requirement is needed; no
formal spec/governance mutation is in scope.

## Design

Two changes plus tests, confined to the two authorized files:

1. `scripts/gtkb_propose_scaffold.py` emitted verification command: replace the
   stale short plugin-selection flag with a scanner-safe equivalent that achieves
   the same intent (deterministic test run without the cache provider) — e.g. the
   long-form plugin option or simply omitting the cache-provider disable — so the
   emitted command no longer matches the credential scanner's password-flag
   heuristic. The generated body must pass the credential scan.

2. `DEFAULT_BRIDGE_KIND` / the emitted `bridge_kind:` line: for implementation-kind
   scaffolds (the default), do not emit an unrecognized bridge_kind; rely on the
   emitted Project Authorization line for gate compliance. Only emit a
   `bridge_kind:` header for the gate-recognized exempt kinds. The exact accepted
   set is confirmed against the current bridge-compliance gate during
   implementation.

No change to the bridge-compliance gate itself is in scope; this fixes the
scaffold output so its default body is gate-clean.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (generated scaffold body passes the bridge-compliance audit) | test_scaffold_body_passes_compliance_audit | platform_tests/scripts/test_gtkb_propose_scaffold.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (emitted verification command has no password-style flag the scanner rejects) | test_scaffold_test_command_scanner_clean | platform_tests/scripts/test_gtkb_propose_scaffold.py |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (implementation-kind body relies on Project Authorization, emits no unrecognized bridge_kind) | test_scaffold_bridge_kind_aligned | platform_tests/scripts/test_gtkb_propose_scaffold.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (exempt-kind scaffolds still emit a recognized bridge_kind) | test_scaffold_exempt_kind_emits_recognized_bridge_kind | platform_tests/scripts/test_gtkb_propose_scaffold.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --tb=short
python -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
python -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
```

## Risk / Rollback

- Risk: changing the emitted verification command alters author expectations.
  Mitigation: the replacement preserves the deterministic-run intent; the test
  asserts the generated command is scanner-clean and still a valid pytest
  invocation.
- Risk: omitting bridge_kind for implementation kind changes the body shape.
  Mitigation: tests assert the implementation-kind body still passes the
  compliance audit (Project Authorization present) and exempt kinds still emit a
  recognized bridge_kind.
- Rollback: changes are confined to the scaffold generator and its test;
  reverting the two files restores prior behavior. No schema, governed-record, or
  narrative change is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-001.md`) under the
canonical append-only numbered-file chain; revisions and verdicts are added as
new numbered files so the numbered file chain remains the canonical audit trail
per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), which minted the covering
  PAUTH PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-WI-4537-SCAFFOLD-DEFAULTS-REFRESH
  (allowed mutation classes: source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001). No further owner decision is required to review
  this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
