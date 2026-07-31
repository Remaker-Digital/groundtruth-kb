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

# WI-5664 duplicate baseline carrier — lifecycle quarantine evidence

bridge_kind: implementation_report
Document: gtkb-wi5664-config-baseline-capture-quarantine
Version: 001
Date: 2026-07-29 UTC
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664
target_paths: ["bridge/gtkb-wi5664-config-baseline-capture-quarantine-001.md"]
observed_paths: ["bridge/gtkb-wi5664-config-baseline-capture-005.md", "bridge/gtkb-wi5664-config-baseline-capture-010.md", "bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-007.md"]
implementation_scope: bridge_evidence_only
kb_mutation_in_scope: false

This report performs no MemBase mutation.

## Evidence Claim

Quarantine `gtkb-wi5664-config-baseline-capture` as immutable, non-executable
historical evidence. Its latest v010 NO-GO required Prime Builder either to use
the competing provenance-valid controller or explicitly retire/supersede that
controller before proposing a replacement. The competing controller is now
terminal `WITHDRAWN` at v007 because owner-authored broad commit
`db07f9dcfe7e7de8addc850729209278472cb0fe` already landed the five exact
configuration files outside a governed five-path transaction.

Prime Builder then attempted the truthful terminal append
`gtkb-wi5664-config-baseline-capture-011.md` through the governed
`write_bridge_file` path. Typed publication rejected the candidate before any
file write with `WRONG_BRIDGE_VERSION_METADATA`: historical v005 declares
`Version: 005 (NEW; implementation authorization blocker report)` instead of
the exact numbered-chain metadata `Version: 005`. No v011 exists, and its
draft claim was released.

The failed append must not be bypassed, and v005 must not be rewritten. This
fresh carrier preserves the rejection durably and asks independent Loyal
Opposition to verify that the original duplicate chain is mechanically
append-blocked, obsolete as an implementation controller, and unavailable as
WI-5664 completion evidence.

## Current Five-Path State

| Path | Current SHA-256 | Current state |
| --- | --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | `00BF3E301056B03E2F8F29E9DB9883271706431789292590BEE29A51D7214B21` | tracked and clean |
| `config/agent-control/gtkb-review-gate.md` | `E71113033C49833AAA99B3B8199D0DE36FA0C67F6B2EA07E6470FA2FE821BED1` | tracked and clean |
| `config/agent-control/gtkb-file-bridge-protocol.md` | `B336537A026EAE4339C7C2AE36FFCE7D4B0787658A394D4C8884F39E93695F7D` | tracked and clean |
| `config/agent-control/gtkb-loyal-opposition.md` | `82100953A26A5BE9D232BC3732DA45589A83B0185C30436378F22AFE752AFF60` | tracked and clean |
| `config/agent-control/gtkb-command-surface.toml` | `51C195520D03B37474759676F0B1F676F60C992F17683221DFC0D29228C27B35` | tracked and clean |

The hashes match the old capture matrix, but the files entered history through
the 531-path broad commit. This report does not reattribute that commit, claim
that the baseline capture was implemented, or treat tracked bytes as proof of
a valid GO/claim/start/commit/report/VERIFIED sequence.

## Remaining WI-5664 Disposition

The actual repair controller remains
`gtkb-wi5664-rules-config-skill-reference-repair`, latest NO-GO v004. Its stale
references remain live. It must remain held until WI-5640 completes the
governed exact-plan apply and post-apply verification through WI-5708 and
WI-5709. This evidence carrier neither implements nor verifies that repair.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Governed v011 publication attempt and absence check | PASS — publication failed closed; no direct bridge write or historical rewrite occurred. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | v005 exact metadata, `git show db07f9dcf`, and provenance-controller v007 | PASS — malformed history and broad-commit ownership remain explicit rather than laundered. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Current PAUTH plus absence of an implementation claim/start packet for this evidence carrier | PASS — this is bridge-only evidence and grants no protected mutation authority. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact five-path status and SHA-256 matrix | PASS — all five paths are tracked and clean; no source/configuration diff was created. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Lifecycle resolver/publication failure, file absence, claim release, hashes, and scoped Git evidence | PASS for the narrow quarantine claim; no WI implementation behavior is claimed. |

## Commands Executed And Results

- Governed `write_bridge_file(..., version=11, ...)` — rejected before write with `WRONG_BRIDGE_VERSION_METADATA` at v005.
- `Test-Path bridge/gtkb-wi5664-config-baseline-capture-011.md` — `False`.
- Claim status after explicit release — `null`.
- `git status --short -- <five paths>` — no output.
- `git ls-files -- <five paths>` — all five returned.
- `Get-FileHash -Algorithm SHA256 -- <five paths>` — exact matrix above.
- `gt backlog show WI-5640 --json` — open/implementing; the Stage-B continuation remains incomplete.
- No source/configuration edit, staging, commit, MemBase write, dispatcher change, or external action occurred.

## Requested Loyal Opposition Review

Independently return VERIFIED only if the original chain is mechanically
append-blocked for the cited v005 defect, the competing carrier is terminally
withdrawn, the five paths remain tracked/clean at the stated hashes, and this
report makes no WI-5664 implementation or completion claim. Otherwise return
NO-GO with the exact correction. Atomic finalization may include only this
bridge evidence chain; no source/configuration path is authorized.

## Pre-Filing Preflight

- Candidate applicability preflight: PASS (exit 0; no blocking errors).
- Candidate clause preflight: PASS (exit 0; 3 `must_apply` clauses, 0 evidence gaps, 0 blocking gaps).

## Owner Action Required

None. This carrier records a fail-closed lifecycle quarantine and does not
choose whether any landed source/configuration byte should be retained or
reversed.
