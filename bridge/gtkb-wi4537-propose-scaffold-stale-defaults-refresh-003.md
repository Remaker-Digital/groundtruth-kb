REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal (REVISED): WI-4537 refresh gtkb_propose_scaffold stale pytest flag (F1-only)

Document: gtkb-wi4537-propose-scaffold-stale-defaults-refresh
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-002.md
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: WI-4537
Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-WI-4537-SCAFFOLD-DEFAULTS-REFRESH

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

## Revision Note

REVISED as `-003` per the `-002` NO-GO. The NO-GO accepted F1 (the emitted
verification-command flag is scanner-tripping) and rejected F2 (the claim that
`prime_proposal` is an unrecognized `bridge_kind`). This revision is re-scoped to
**F1 only** and the F2 `bridge_kind` change is dropped entirely.

Verified live during this revision (so the dropped claim is grounded, not just
asserted): the bridge-compliance gate recognizes `prime_proposal` as a canonical
implementation-proposal token — `bridge-compliance-gate.py` defines
`BRIDGE_KIND_IMPLEMENTATION_PROPOSAL = frozenset({"prime_proposal",
"implementation_proposal", "prime_implementation_proposal"})` — and the scaffold's
`DEFAULT_BRIDGE_KIND = "prime_proposal"` is therefore correct. The scaffold's
`bridge_kind` default is left unchanged.

The F1 defect is confirmed live: `scripts/gtkb_propose_scaffold.py` (the emitted
verification-command template, currently around line 222) carries a short
pytest plugin-disable flag for the cache provider whose value pattern matches the
credential scanner's password-flag heuristic. A scaffold body that includes that
flag is blocked at Write time by the credential scan / scanner-safe writer, so
the scaffold — whose purpose is a first-pass-clean proposal body — currently
seeds a defect the author must hand-correct. (This proposal describes the flag in
words rather than quoting it, to avoid tripping the same scanner on this file.)

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
  covering PAUTH.
- bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-002.md — the `-002`
  NO-GO (independent Cursor LO, harness E) accepting F1 and rejecting F2; this
  `-003` applies its required re-scope to F1-only.
- bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-001.md — the original
  NEW proposal; this revision supersedes its design by dropping F2.
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

1. `scripts/gtkb_propose_scaffold.py` emitted verification-command template:
   replace the short cache-provider plugin-disable flag with a scanner-safe
   equivalent that preserves the deterministic-run intent — the simplest being to
   omit the cache-provider disable, leaving a plain quiet/no-header pytest
   invocation. The generated body must pass the credential scan.

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
(`bridge/gtkb-wi4537-propose-scaffold-stale-defaults-refresh-003.md`) under the
canonical append-only numbered-file chain. Prior versioned bridge files (`-001`
NEW, `-002` NO-GO) are never rewritten or deleted; this REVISED version is added
as a new numbered file so the chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), which minted the covering
  PAUTH PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-WI-4537-SCAFFOLD-DEFAULTS-REFRESH
  (allowed mutation classes: source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001). No further owner decision is required to review
  this revision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
