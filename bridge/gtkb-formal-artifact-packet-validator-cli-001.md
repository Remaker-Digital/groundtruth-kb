NEW

# GT-KB Formal-Artifact Packet Validator CLI - Slice 1 NEW

bridge_kind: implementation_proposal
Document: gtkb-formal-artifact-packet-validator-cli
Version: 001 (NEW; Slice 1 — helper script + tests + first-proposal reference)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Implements: WI-3266 (GTKB-FORMAL-ARTIFACT-PACKET-VALIDATOR-CLI)

## Claim

This proposal authors `scripts/validate_formal_artifact_packet.py` as a small CLI that imports `.claude/hooks/formal-artifact-approval-gate.py` module's `_validate_packet()` + `_load_packet()` helpers and exposes a stable command-line interface. Currently 5+ bridge proposals (workflow-contract-adr, owner-gate-dcl, template-spec, routing-dcl, dashboard-counters-spec) embed similar inline-Python validation patterns that have been NO-GO'd 3+ times for (a) PowerShell-escaping fragility, (b) under-validating compared to the live gate (missing `approval_mode`, `presented_to_user`, `transcript_captured`, `full_content_sha256` integrity checks).

A canonical helper script eliminates duplication, prevents drift between proposals and the live gate, and matches `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (plumbing crossing the 5+ repetition threshold becomes a service).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directive that repetitive plumbing crossing the 5+ threshold should become a service.
- `bridge/gtkb-peer-solution-workflow-contract-adr-006.md` - Codex NO-GO citing F1 PowerShell-fragile inline Python + F2 under-validation.
- `bridge/gtkb-peer-solution-owner-gate-dcl-004.md` - Codex NO-GO with same F1/F2 pattern.
- `bridge/gtkb-advisory-report-template-spec-002.md` - Codex NO-GO with same F1/F2 pattern (third independent hit).
- WI-3266 MemBase backlog row (current_work_items).

## Owner Decisions / Input

- **Owner directive S341 (2026-05-11):** "Please proceed with WI-3266." Direct authorization to file this Slice 1 implementation proposal. Standing-backlog pre-approval (per `memory/work_list.md` Owner pre-approval header) authorizes the bridge-protocol-mediated workflow: propose → Codex GO → implement → post-impl → Codex VERIFIED → commit.
- **AUQ S341 (2026-05-11) prior autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context."

Outstanding owner decisions before VERIFIED: none. The helper script is non-protected source code under `scripts/`; the paired test is under `platform_tests/scripts/`. Neither path is in `config/governance/narrative-artifact-approval.toml`. The first-proposal reference work (filing a REVISED for one of the 5 affected proposals) creates a bridge document under `bridge/` which is governed by the bridge protocol, not the narrative-artifact gate.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `scripts/validate_formal_artifact_packet.py` helper script.** Contract:

1. CLI entry: `python scripts/validate_formal_artifact_packet.py <packet_path>`.
2. Imports `.claude/hooks/formal-artifact-approval-gate.py` module via `importlib.util.spec_from_file_location` (the only stable way to load the hook module without modifying it).
3. Calls the gate module's `_load_packet(path)` and `_validate_packet(packet)` helpers, returning the gate's own error message verbatim if validation fails. This guarantees the helper's validation matches the live gate by construction — no duplication, no drift.
4. Exit codes: `0` on packet_valid, `1` on validation failure (with the gate's error message printed to stderr), `2` on invocation error (e.g., missing packet path argument).
5. Stdout on success: a single line `packet_valid: <packet_path>` for citation in bridge post-impl reports.
6. PowerShell-safe: the CLI takes the packet path as a positional argument, NOT via a `python -c "..."` form. The proposal that cites this helper writes `python scripts/validate_formal_artifact_packet.py "<packet_path>"` with normal shell quoting.

**IP-2: Paired tests at `platform_tests/scripts/test_validate_formal_artifact_packet.py`.** Tests cover:

- Happy path: valid packet returns exit 0 and prints `packet_valid:` line.
- Missing required field: exit 1 with the gate's "approval packet missing required fields:" message.
- Invalid artifact_type: exit 1 with the gate's "approval packet artifact_type must be one of..." message.
- Invalid approval_mode: exit 1 with the gate's "approval_mode must be one of..." message.
- Wrong full_content_sha256: exit 1 with the gate's hash-mismatch message.
- Missing presented_to_user / transcript_captured: exit 1 with the gate's "requires {flag_name}=true" message.
- Auto-mode without auto_approval_scope: exit 1 with the gate's "auto approval requires auto_approval_scope" message.
- Expired packet: exit 1 with the gate's "approval packet is expired" message.
- Missing packet path argument: exit 2 with usage hint.

Tests use the gate module's actual constants (imported the same way as the helper) so they automatically track gate changes.

**IP-3: First-proposal reference — file a REVISED on workflow-contract-adr citing the helper.** After IP-1 + IP-2 land in commit, file `bridge/gtkb-peer-solution-workflow-contract-adr-007.md` (REVISED-3) replacing the IP-4 inline-Python command with:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

This closes the workflow-contract-adr `-006` NO-GO (F1 PowerShell + F2 under-validation) by reference rather than reproducing the brittle pattern.

### OUT OF SCOPE

- Retrofitting owner-gate-dcl, template-spec, routing-dcl, dashboard-counters-spec to also reference the helper (each is its own future REVISED filing; deferred to Slice 2 or per-thread maintenance).
- Modifying `.claude/hooks/formal-artifact-approval-gate.py` itself (the helper consumes it; the hook stays canonical).
- Adding a `--quiet` or `--json` output mode (Slice 1 emits only the canonical `packet_valid:` line + gate errors).
- Wrapping into a `gt` subcommand (deferred; the standalone script is the contract surface).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-formal-artifact-packet-validator-cli` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-formal-artifact-packet-validator-cli` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_validate_formal_artifact_packet.py -v --tb=short` - PASS expected (IP-2: 9 test cases).
4. **End-to-end smoke against a real packet:** construct a valid packet for a fixture artifact_type, run `python scripts/validate_formal_artifact_packet.py <fixture_path>`, assert exit 0 and `packet_valid:` line.
5. **End-to-end smoke against a deliberately-broken packet:** construct an invalid packet (missing `transcript_captured`), assert exit 1 and the gate's specific error message.

### Regression

6. Existing hook tests pass unchanged (helper does not modify the gate).
7. `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q` - PASS unchanged (regression guard against import-side-effects from spec_from_file_location).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Steps 3-7. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Helper at `scripts/` + tests at `platform_tests/scripts/` inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Helper consumes the gate's logic; does NOT bypass it. Verified by Step 4 happy-path test using a real packet structure. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Helper imports gate via `importlib.util.spec_from_file_location`; gate module stays canonical and untouched. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Helper replaces 5+ inline-Python duplications with one canonical CLI. Step 3 + IP-3 reference make the consolidation auditable. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Helper does NOT touch protected narrative artifacts; no OWNER ACTION REQUIRED block needed for Slice 1. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this Slice-1 NEW.
- [ ] `scripts/validate_formal_artifact_packet.py` exists; conforms to IP-1 contract.
- [ ] `platform_tests/scripts/test_validate_formal_artifact_packet.py` exists; 9 test cases PASS per IP-2.
- [ ] End-to-end smokes (happy + broken-packet) succeed per Test Plan Steps 4-5.
- [ ] No regression in existing hook tests or session-self-init tests (Steps 6-7).
- [ ] `bridge/gtkb-peer-solution-workflow-contract-adr-007.md` REVISED-3 filed citing the helper in IP-4 (IP-3 first-proposal reference).
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); append-only version chain per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This implementation slice resolves WI-3266 backlog row (priority MEDIUM).

- **inventory artifact:** IP-1 to IP-3 enumeration above.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** retrofit-cascade to the other 4 affected proposals (owner-gate-dcl, template-spec, routing-dcl, dashboard-counters-spec) deferred to Slice 2 OR per-thread maintenance REVISED filings.
- **formal-artifact-approval packet:** N/A (helper script + tests are non-protected source code; no narrative-artifact mutation).

## Risk + Rollback

**Risk R1 (Low):** Hook module load via `importlib.util.spec_from_file_location` could trigger unintended side effects from the gate's import-time code. Mitigation: regression Step 7 asserts no impact on existing tests; the gate module's top-level imports (`json`, `os`, `re`, `sys`, `hashlib`, `datetime`, `pathlib`, `typing`) are all stdlib + no `print()`/`sys.exit()` at module level.

**Risk R2 (Low):** If the gate module is later restructured (e.g., `_validate_packet` renamed or made private to a class), the helper would break silently. Mitigation: IP-2 tests use the gate's actual constants and helper functions via `importlib`, so a rename would cause `AttributeError` at test time, not silently passing.

**Risk R3 (Low):** Helper script and IP-3 reference REVISED could land in different commits; if IP-3 lands first the helper doesn't exist and CI fails. Mitigation: enforce single-commit landing for IP-1 + IP-2 + IP-3 (this Slice 1 acceptance criterion).

**Risk R4 (Low):** PowerShell path quoting with spaces in `<packet_path>` argument. Mitigation: IP-1 contract specifies positional argument + normal shell quoting; PowerShell's double-quote handling for positional args is well-defined.

**Rollback:** `git revert <commit-sha>`. Helper script, tests, and IP-3 REVISED revert atomically. Workflow-contract-adr `-006` NO-GO state remains unchanged in the bridge index until a new REVISED lands.

## Recommended Commit Type

`feat:` — new helper script + new test file + new bridge REVISED filing. Net-new capability surface eliminating 5+ duplicated inline-Python patterns.

## Loyal Opposition Asks

1. Confirm the IP-1 helper contract (positional packet-path arg + exit 0/1/2 + `packet_valid:` stdout line + gate error verbatim on failure) is the right surface for the 5 affected proposals to cite.
2. Confirm using `importlib.util.spec_from_file_location` to load the gate module is acceptable governance (the alternative is duplicating the gate's constants + validation logic in the helper, which is exactly the drift problem this helper exists to prevent).
3. Confirm IP-2's 9 test cases cover the gate's full validation surface (each `return f"..."` branch in `_validate_packet` mapped to one test).
4. Confirm IP-3 (one first-proposal reference + 4 deferred retrofits) is the right Slice-1 boundary, vs requiring all 5 retrofits in this single slice.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
