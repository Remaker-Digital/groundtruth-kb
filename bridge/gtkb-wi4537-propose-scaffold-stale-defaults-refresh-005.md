REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal (REVISED): WI-4537 refresh gtkb_propose_scaffold stale pytest flag (F1-only, re-homed)

Document: gtkb-wi4537-propose-scaffold-stale-defaults-refresh
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-004.md
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4537
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4537-SCAFFOLD-DEFAULTS-REFRESH

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

## Revision Note

REVISED as `-005` for a project re-home only; the F1-only scope and design are
unchanged from `-003` (which the `-004` GO approved). The original project
`PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` auto-retired after its sibling work items
resolved, which stranded the GO'd thread's covering PAUTH: an
`implementation_authorization.py begin` failed with "Project authorization ... is
not attached to an active project". This revision re-homes WI-4537 to the active
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` (the scaffold's job is to emit a
proposal body that passes the bridge-compliance / credential-scan gates, which is
bridge-protocol reliability) under a fresh covering PAUTH
(`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4537-SCAFFOLD-DEFAULTS-REFRESH`).
No scope, design, target_paths, or test plan change relative to `-003`.

Scope recap (from the `-002` NO-GO and `-003` REVISED): **F1 only**. The scaffold
emits a verification-command template carrying a short pytest plugin-disable flag
for the cache provider whose value pattern matches the credential scanner's
password-flag heuristic, so a scaffolded body is blocked at Write time. The F2
`bridge_kind` change was dropped: `prime_proposal` is canonical
(`bridge-compliance-gate.py` `BRIDGE_KIND_IMPLEMENTATION_PROPOSAL` includes it),
so the scaffold's `DEFAULT_BRIDGE_KIND = "prime_proposal"` is correct and left
unchanged. (This proposal describes the flag in words rather than quoting it, to
avoid tripping the same scanner on this file.)

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge authority; the scaffold must emit a body
  that satisfies the current bridge-compliance gate, and this is a bridge artifact
  under the canonical append-only numbered-file chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4537 is the canonical backlog record for this
  work. Its CLAUSE-VISIBILITY-BULK-OPS does not apply: this is a single-flag
  scaffold fix, not a bulk backlog operation, so it produces no inventory
  artifact or review-packet and needs no bulk-action formal-artifact-approval
  packet.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the corrected
  default is enforced by a spec-derived test that audits the generated body.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4537 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop; basis for the
  covering PAUTH (original and re-homed).
- bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-004.md — the `-004`
  GO (independent Cursor LO) approving the `-003` F1-only design; this `-005`
  re-homes that approved design after the original project auto-retired.
- bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-002.md — the `-002`
  NO-GO accepting F1 and rejecting F2.
- WI-3268 — pre-filing mechanical lints; a scaffold that emits a gate-clean body
  reduces the lint surface there.
- No prior deliberation rejects refreshing the scaffold's emitted pytest flag.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already requires
proposals to satisfy the bridge-compliance gate; this WI makes the scaffold emit
a verification command that does so by default. No new or revised requirement is
needed; no formal spec/governance mutation is in scope.

## Design

One change plus tests, confined to the two authorized files:

1. `scripts/gtkb_propose_scaffold.py` emitted verification-command template
   (currently around line 222): replace the short cache-provider plugin-disable
   flag with a scanner-safe equivalent that preserves the deterministic-run intent
   — the simplest being to omit the cache-provider disable, leaving a plain
   quiet/no-header pytest invocation. The generated body must pass the credential
   scan.

2. No change to `DEFAULT_BRIDGE_KIND` or the emitted `bridge_kind:` header; the
   `prime_proposal` default is canonical and must remain (the existing
   `test_scaffold_bridge_kind_default_matches_taxonomy` requires it). No change to
   the bridge-compliance gate itself is in scope.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (generated scaffold body passes the bridge-compliance / credential-scan audit) | test_scaffold_body_passes_compliance_audit | platform_tests/scripts/test_gtkb_propose_scaffold.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (emitted verification command has no password-style flag the scanner rejects) | test_scaffold_test_command_scanner_clean | platform_tests/scripts/test_gtkb_propose_scaffold.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (bridge_kind default remains the canonical prime_proposal token) | test_scaffold_bridge_kind_default_matches_taxonomy (existing; must continue to pass) | platform_tests/scripts/test_gtkb_propose_scaffold.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --tb=short
python -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
python -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
```

## Risk / Rollback

- Risk: changing the emitted verification command alters author expectations.
  Mitigation: the replacement preserves the deterministic-run intent and remains a
  valid pytest invocation; the test asserts the generated command is scanner-clean.
- Risk: an inadvertent bridge_kind change. Mitigation: this revision explicitly
  leaves bridge_kind unchanged and relies on the existing taxonomy test to guard
  it.
- Rollback: the change is confined to the scaffold generator's emitted template
  and its test; reverting the two files restores prior behavior. No schema,
  governed-record, or narrative change is involved.

## Bridge Filing Discipline

This revision is filed as the next numbered bridge file
(`bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-005.md`) under the
canonical append-only numbered-file chain. Prior versioned bridge files (`-001`
NEW, `-002` NO-GO, `-003` REVISED, `-004` GO) are never rewritten or deleted; this
REVISED version is added as a new numbered file so the chain remains the canonical
audit trail per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), which minted the covering
  PAUTH. After the original project auto-retired, WI-4537 was re-homed to the active
  PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY and a fresh covering PAUTH
  (PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4537-SCAFFOLD-DEFAULTS-REFRESH;
  allowed mutation classes source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001) was minted under the same owner authorization. No
  further owner decision is required to review this revision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
