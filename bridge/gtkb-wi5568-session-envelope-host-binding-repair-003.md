NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: implementation_report
Document: gtkb-wi5568-session-envelope-host-binding-repair
Version: 003
Responds to: bridge/gtkb-wi5568-session-envelope-host-binding-repair-002.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-5568
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_claim_cli.py"]

# WI-5568 Implementation Report — Codex host-bound session envelope

## Implementation Claim

Implemented the approved three-path runtime repair and committed it as
`6c0b0628fdb0b34bf06168ca37955649cc07ff30`. The Codex envelope-open command
now validates a present `CODEX_THREAD_ID`, binds the first role-bearing open to
that exact host ID, and returns an already-open exact host document without
rewriting either the authoritative document or its projections.

An existing host document is accepted only when its session ID, open status,
persisted harness identity, and worker-role provenance all validate. A newly
asserted conflicting role or subject fails before any write. Initial role-free
opens, no-host-ID runs, and non-Codex harnesses retain their prior behavior.
No change to `session/envelope.py` was needed.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`

The commit contains exactly these three GO-approved paths. All three are clean
against HEAD after commit; unrelated worktree changes were excluded.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION` authorized only this
  host-binding, refresh-persistence, and focused regression scope.
- `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-WI5568-RUNTIME-20260724` version 2 is the
  active project authorization. It covers WI-5568 and the three approved
  source/test targets without authorizing the separate broad role purge.
- No additional owner decision was required during implementation.

## Prior Deliberations

- `DELIB-20260724-WI5568-RUNTIME-SCOPE-AUTHORIZATION` — bounded owner runtime
  authorization.
- `bridge/gtkb-wi5568-session-envelope-host-binding-repair-001.md` — approved
  implementation proposal.
- `bridge/gtkb-wi5568-session-envelope-host-binding-repair-002.md` — independent
  Loyal Opposition GO and implementation boundaries.

## Implementation Details

`envelope_open_cmd` now performs a Codex-only host-session branch after the
existing canonical init-keyword validation:

1. A present `CODEX_THREAD_ID` passes the existing non-placeholder,
   single-line, 256-character metadata validation.
2. The persisted Codex harness identity is resolved and only the exact
   host-keyed session document is loaded.
3. Existing documents must be open and identity-consistent, and
   `resolve_worker_role_provenance` must validate their transcript authority.
4. Explicit role or subject conflicts raise a `ClickException` before any
   write. A compatible refresh returns the existing JSON document unchanged.
5. When no exact document exists, only a role-bearing initial open receives
   the host ID as `session_id`; all existing fallback paths remain intact.

The focused bridge-claim regression constructs the envelope through the real
CLI, without `_write_prime_marker` or `attest-author-metadata`, then proves a GO
implementation claim resolves the exact document as Prime Builder authority.

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| Initial host binding (`DCL-SESSION-ROLE-RESOLUTION-001`) | `test_cli_role_bearing_codex_open_binds_exact_host_thread` | PASS; exact document and worker provenance use `codex-thread-123` |
| Refresh persistence (`ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`) | `test_cli_same_host_refresh_returns_exact_envelope_without_rewrite` | PASS; transcript Prime role persists and exact/current/shared bytes remain unchanged |
| Conflict fail-closed (`GOV-FILE-BRIDGE-AUTHORITY-001`) | `test_cli_same_host_conflict_fails_before_exact_or_projection_write` | PASS; contradictory LO refresh is rejected before all three writes |
| Host metadata validation | `test_cli_rejects_invalid_codex_host_thread_before_write` (3 cases) | PASS; blank, placeholder, and multiline values fail before envelope creation |
| Bridge claim interoperability | `test_claim_go_implementation_uses_host_bound_cli_envelope_provenance` | PASS; exact CLI-created document yields `go_implementation` and `prime-builder` |
| Existing behavior / mandatory execution (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) | Full two-module focused pytest command | PASS; 44 passed |
| Code quality | Ruff check and format-check on all three targets | PASS |
| Scoped finalization and project linkage | Commit and clean-target audit | PASS; one authorized WI, one commit, exactly three declared paths |

## Commands Run And Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_claim_cli.py -q --tb=short
  44 passed, 1 warning in 30.48s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_claim_cli.py
  All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_claim_cli.py
  3 files already formatted

git diff --cached --check
  clean before commit

git show --name-status --format=fuller 6c0b0628fdb0b34bf06168ca37955649cc07ff30
  M groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py
  M platform_tests/scripts/test_bridge_claim_cli.py
  M platform_tests/scripts/test_session_envelope_cli_provenance.py
```

The sole pytest warning is the pre-existing unknown `asyncio_mode`
configuration warning; it does not represent a test failure.

## Acceptance Criteria Status

- PASS — first role-bearing Codex open uses the validated host task ID as the
  authoritative exact session ID without an attestation rebind.
- PASS — same-host role-free refresh preserves the exact transcript-derived
  role and performs no authority-document or projection write.
- PASS — conflicting role-bearing refresh fails with all authority surfaces
  byte-identical.
- PASS — bridge claim provenance resolves from the exact host-bound Prime
  document created by the envelope CLI.
- PASS — no-host-ID and non-Codex behavior remain on the existing path; the
  complete focused modules pass.
- PASS — exactly the three declared files changed and were committed.

## Commit Finalization Evidence

- Commit: `6c0b0628fdb0b34bf06168ca37955649cc07ff30`
- Subject: `fix(session): bind Codex envelope to host thread`
- Committed paths:
  - `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
  - `platform_tests/scripts/test_bridge_claim_cli.py`
  - `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- Protected-commit authorization: PASS for all three protected paths.
- Secret scan, inventory drift, narrative evidence, Ruff format: PASS in the
  commit hook.
- Post-commit target state: clean.

## Risk And Rollback

Residual risk is reuse of a malformed or foreign host ID. Exact-document
identity, status, session-ID, and worker-provenance validation fail closed
instead of replacing such a document. The host branch is Codex-only, and a
role-free first open intentionally remains timestamp-derived to preserve the
approved fallback contract.

Rollback is a governed revert of commit
`6c0b0628fdb0b34bf06168ca37955649cc07ff30`. Bridge audit artifacts remain
append-only.

## Loyal Opposition Asks

Independently rerun the two focused modules and inspect the committed three-path
diff. Verify especially that compatible refreshes do not call `write_current`
or `open_session`, contradictory refreshes leave exact/current/shared files
unchanged, and the claim test derives Prime authority from the CLI-created
host document. Return VERIFIED only if all linked requirements and acceptance
criteria are satisfied.

## Recommended Commit Type

Recommended commit type: `fix`
