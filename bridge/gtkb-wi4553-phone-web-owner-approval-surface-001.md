NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1942-93f3-74f3-ad39-c27cad3b87c9
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop auto-builder automation

# GT-KB Bridge Implementation Proposal - gtkb-wi4553-phone-web-owner-approval-surface - 001

bridge_kind: prime_proposal
Document: gtkb-wi4553-phone-web-owner-approval-surface
Version: 001
Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4553
Recommended commit type: feat:

target_paths: ["groundtruth-kb/src/groundtruth_kb/owner_approval_surface.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_owner_approval_surface.py"]

implementation_scope: source_test_cli_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Implement WI-4553 Slice 1 by adding a deterministic, local, mobile-friendly owner-approval surface generator for pending owner decisions, including AskUserQuestion-style choices and bridge GO/NO-GO review packets.

This first slice deliberately does not make a browser click authoritative. It renders a phone/browser-readable approval bundle and an optional standard-library local preview server so Mike can inspect pending approval context away from the terminal. Authoritative decision capture remains the existing AUQ / bridge / formal-artifact evidence chain until a later bridge proposal explicitly designs and reviews write-back semantics.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing owner-decision, policy-engine, bridge-authority, and deterministic-service specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to linked requirements.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source and test implementation requires a live bridge `GO`, a work-intent claim, and an implementation-start packet.
- `GOV-STANDING-BACKLOG-001` - WI-4553 is the MemBase-backed Omnigent Alignment backlog item being processed.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision surfaces must reuse or preserve the deterministic AUQ policy model rather than creating a parallel approval authority.
- `SPEC-AUQ-ACTION-CLASSES-001` - rendered approval packets must declare explicit action classes and reject unknown action tokens.
- `SPEC-AUQ-ADAPTER-PATTERN-001` - the web surface must be a thin presentation adapter over existing decision concepts, not a second policy engine.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - packet classification and rendering must be deterministic and must not call LLM, network, or provider APIs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions and approvals must remain promotable into governed artifacts instead of being trapped in transient UI state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge GO/NO-GO authority remains file-bridge verdict authority; this surface can display verdict choices but cannot author verdict files in this slice.

## Requirement Sufficiency

Existing requirements are sufficient for Slice 1.

WI-4553 asks for an Omnigent-shaped phone/web owner-approval surface for AUQ and bridge GO/NO-GO. The Omnigent Alignment decisions authorize patterns-only emulation, and the existing AUQ policy specs already define deterministic action classes, adapter boundaries, and no-LLM classification. A read-only presentation slice can deliver immediate owner-burden reduction without deciding the more sensitive write-back protocol.

No new owner input is requested for this first slice. Any later slice that submits AUQ answers, writes bridge verdict files, creates formal approval packets, exposes LAN access by default, or stores durable owner decisions from browser events must be separately proposed and reviewed.

## Target Paths

The implementation is limited to:

- `groundtruth-kb/src/groundtruth_kb/owner_approval_surface.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_owner_approval_surface.py`

No edit to `.claude/hooks/`, `.codex/`, bridge verdict authoring helpers, dispatcher runtime, MemBase, formal artifacts, credentials, deployment configuration, dashboard Grafana assets, or application code is in scope.

## Implementation Plan

1. Add `groundtruth_kb.owner_approval_surface` with a pure data model for approval packets: packet id, title, summary, action class, source surface (`auq`, `bridge_go`, `bridge_no_go`, `bridge_verified`, or `formal_artifact_review`), options, evidence links, expiry/display metadata, and non-authoritative status.
2. Add deterministic validation: required fields, known action classes, known source surfaces, unique option ids, bounded option count, relative-path/root-boundary validation for evidence paths, and rejection of HTML/script injection in user-visible fields through escaping.
3. Add a renderer that emits a mobile-friendly static HTML page plus JSON payload. The page must show status, evidence links, options, and copyable command/evidence text, while clearly marking browser selections as non-authoritative in Slice 1.
4. Add an optional standard-library preview server for the generated bundle, bound to `127.0.0.1` by default. LAN exposure must require an explicit host argument and must not be enabled by default.
5. Add a small `gt owner-approval render` CLI command, or equivalent command under the existing CLI structure, that renders a packet from a JSON fixture/input file to a caller-specified output directory under the workspace.
6. Keep all write-back out of scope: no AUQ answer recording, no bridge verdict writing, no formal approval packet creation, no dispatcher routing, and no browser-originated mutation of GT-KB authority surfaces.
7. Add focused tests for model validation, HTML escaping, mobile surface content, no-authoritative-write marking, localhost default binding, explicit LAN opt-in behavior, CLI render output, and no LLM/network/provider dependency.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Approval packets contain titles, ids, paths, and prose only; no credentials or endpoint secrets. | Bridge helper credential scan and test fixture review. | |
| CQ-PATHS-001 | Yes | Implementation stays within the three declared target paths and generated runtime output remains caller-selected, not committed. | Implementation-start target validation and `git status --short -- <target paths>`. | |
| CQ-COMPLEXITY-001 | Yes | Keep the renderer deterministic and standard-library based; avoid a framework or persistent service in Slice 1. | Ruff check and focused tests. | |
| CQ-CONSTANTS-001 | Yes | Name source-surface tokens, action classes, schema version, default host, and max option count. | Unit tests for accepted/rejected tokens. | |
| CQ-SECURITY-001 | Yes | Escape HTML, default preview server to localhost, require explicit LAN host opt-in, and avoid browser-originated writes. | Tests for escaping, default binding, and no write-back endpoints. | |
| CQ-DOCS-001 | Yes | CLI help and rendered page copy must state non-authoritative Slice 1 status without creating in-app instructional clutter beyond safety labels. | CLI/render tests assert status text and evidence fields. | |
| CQ-TESTS-001 | Yes | Add tests for validation, rendering, CLI output, localhost default, LAN opt-in, and no hidden mutation. | `python -m pytest groundtruth-kb/tests/test_owner_approval_surface.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | Slice 1 does not add runtime logging. | Diff review confirms no logging surface. | No daemon or long-running service is introduced. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, ADR/DCL clause preflight, and proposal-pattern lint before implementation report. | Command output included in the post-implementation report. | |

## Cross-Harness Disposition

This slice adds a GT-KB package module and CLI command used by any harness that can run the local Python environment. It does not install harness hooks, alter role resolution, change dispatch routing, or create browser-originated bridge verdict authority.

| Harness surface | Disposition |
| --- | --- |
| Codex Prime Builder | Can render and preview packets through the CLI; no behavior change. |
| Cursor Prime Builder | Can render and preview packets through the CLI; no behavior change. |
| Loyal Opposition harnesses | Can review generated packet behavior through tests; verdict authority remains file bridge. |
| Owner browser/phone | Can inspect the generated page; selections are non-authoritative in Slice 1. |

No typed waiver is requested because no cross-harness behavior migration is introduced.

## Out Of Scope

- Browser-click submission of AUQ answers or bridge verdicts.
- Writing `GO`, `NO-GO`, `VERIFIED`, or formal approval packet files from the web surface.
- Replacing `AskUserQuestion`, the file bridge, or formal-artifact approval packets as authoritative decision channels.
- Adding authentication, LAN service discovery, mobile push notifications, WebSockets, QR pairing, or co-drive collaboration.
- Changing dispatcher selection, bridge claim logic, MemBase rows, dashboard Grafana assets, hook registrations, or production deployment configuration.
- Importing Omnigent or depending on Omnigent runtime code.

## Owner Decisions / Input

No new owner input is requested.

Relevant existing decisions:

- `DELIB-OMNIGENT-ADVISORY-20260614` - owner accepted Omnigent Alignment work items including WI-4553.
- `DELIB-20263229` - owner selected patterns-only Omnigent emulation: borrow useful design shape without importing Omnigent or creating a runtime dependency.
- `DELIB-20265586` - owner-approved project authorization snapshot covering the Omnigent Alignment bounded implementation scope.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic services with thin adapters are the preferred GT-KB shape for repeatable policy decisions.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - established Omnigent Alignment work items including WI-4553.
- `DELIB-20263229` - patterns-only Omnigent emulation decision.
- `DELIB-20265586` - project authorization snapshot for Omnigent Alignment.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service plus thin-adapter architecture.
- `bridge/gtkb-wi4551-unified-policy-registry-slice-1-001.md` - adjacent Omnigent Alignment policy-registry slice; WI-4553 should preserve the same deterministic-adapter boundary.
- `bridge/gtkb-wi4552-declarative-agent-role-manifest-slice-1-001.md` - adjacent Omnigent Alignment declarative-manifest slice; WI-4553 should remain inventory/presentation-first and avoid hidden authority migration.

## Spec-Derived Verification Plan

| Spec / governing surface | Verification obligation |
| --- | --- |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge preflight sees Project Authorization, Project, Work Item, and concrete `target_paths`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight has no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests map to deterministic validation, adapter boundary, no write-back, and localhost-default behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | PB obtains GO, work-intent claim, and implementation-start packet before touching source/test/CLI files. |
| `GOV-STANDING-BACKLOG-001` | WI-4553 remains tied to the MemBase-backed Omnigent Alignment backlog item. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Tests prove rendered packets preserve action-class and option semantics instead of inventing a second approval authority. |
| `SPEC-AUQ-ACTION-CLASSES-001` | Tests reject unknown action classes and source-surface tokens. |
| `SPEC-AUQ-ADAPTER-PATTERN-001` | Tests/source review prove the renderer is presentation-only and has no allow/deny/write-back policy branch. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Tests/source review prove no LLM, network, provider, or subprocess classifier dependency exists. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The rendered packet preserves evidence links and copyable evidence text so decisions can be promoted through governed channels. |

## Verification Commands

```powershell
python -m pytest groundtruth-kb/tests/test_owner_approval_surface.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/owner_approval_surface.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_owner_approval_surface.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/owner_approval_surface.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_owner_approval_surface.py
python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-wi4553-phone-web-owner-approval-surface --strict
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4553-phone-web-owner-approval-surface
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4553-phone-web-owner-approval-surface
```

## Acceptance Criteria

- `groundtruth_kb.owner_approval_surface` defines a deterministic approval-packet model with required-field validation, known action/source tokens, unique option ids, bounded option count, and escaped HTML rendering.
- The renderer emits a mobile-friendly static HTML page plus JSON payload containing title, status, evidence links, options, source surface, and non-authoritative Slice 1 warning.
- The preview server defaults to `127.0.0.1` and LAN exposure requires an explicit host argument.
- The CLI can render a fixture/input packet to a caller-selected output directory without touching bridge files, MemBase, formal artifacts, dispatcher state, credentials, or deployment config.
- Tests prove unknown action classes fail closed, browser-originated write-back is absent, HTML/script content is escaped, and output preserves evidence needed for later governed decision capture.
- Focused pytest, Ruff check, Ruff format-check, proposal-pattern lint, bridge applicability preflight, and ADR/DCL clause preflight pass.

## Risk And Rollback

Risk is moderate because owner-approval UX can be mistaken for owner-approval authority. The slice mitigates that risk by making the surface presentation-only, marking browser choices non-authoritative, keeping write-back out of scope, and preserving existing AUQ / bridge / formal-artifact evidence channels.

Rollback is to remove the new owner-approval module, CLI command wiring, and focused tests. Because Slice 1 writes no durable decisions and changes no live hooks, dispatcher state, MemBase rows, or bridge-verdict authoring code, rollback does not require data migration.

## Loyal Opposition Asks

1. Verify that the slice is narrow enough to provide a useful phone/browser approval view without creating a second owner-decision authority.
2. Confirm that preserving AUQ and file-bridge write-back as out of scope is the correct first-step boundary for WI-4553.
3. Return `GO` if the scope is acceptable; otherwise return `NO-GO` with concrete required changes.
