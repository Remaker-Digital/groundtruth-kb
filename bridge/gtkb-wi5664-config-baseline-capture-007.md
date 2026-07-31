REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5664 provenance-valid configuration baseline recovery

bridge_kind: prime_proposal
Document: gtkb-wi5664-config-baseline-capture
Version: 007
Responds to: bridge/gtkb-wi5664-config-baseline-capture-006.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664
target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

## Recovery Claim

Versions 001 through 006 remain immutable incident evidence. Version 001 has
unreadable Prime Builder provenance, so the old chain cannot issue a live
implementation-start packet. This fresh Prime-authored proposal creates the
only recovery carrier; it does not repair, stage, or restage any historical
version or configuration file.

No configuration capture starts until a new independent LO GO, matching claim,
and successful implementation-start packet exist. All targets are in-root
under `E:\GT-KB\config\agent-control\`.

## Scope And Ownership Matrix

The later capture may commit exactly these five currently observed, untracked
inputs, and no projection/package synchronization, source change, historical
bridge rewrite, or unrelated worktree path:

| Path | Expected SHA-256 |
| --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | `00bf3e301056b03e2f8f29e9db9883271706431789292590bee29a51d7214b21` |
| `config/agent-control/gtkb-review-gate.md` | `e71113033c49833aaa99b3b8199d0de36fa0c67f6b2ea07e6470fa2fe821bed1` |
| `config/agent-control/gtkb-file-bridge-protocol.md` | `b336537a026eae4339c7c2ae36ffce7d4b0787658a394d4c8884f39e93695f7d` |
| `config/agent-control/gtkb-loyal-opposition.md` | `82100953a26a5be9d232bc3732da45589a83b0185c30436378f22afe752aff60` |
| `config/agent-control/gtkb-command-surface.toml` | `51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35` |

Any hash mismatch stops the capture and requires a new reviewed proposal; it
does not authorize updating the ownership matrix in place.

## Requirement Sufficiency

Existing requirements are sufficient. The sweep PAUTH, bridge authority,
provenance requirements, and WI-5664 baseline-capture scope already define the
authorized recovery and validation path.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5664 v006 NO-GO and the preserved v003/v005 ownership evidence.",
  "canonical_authority": "The numbered bridge chain plus the active sweep PAUTH and live implementation-start packet.",
  "primary_route": "Fresh LO GO, matching claim, packet, five-hash reconfirmation, scoped commit, report, and independent verification.",
  "before_behavior": "The malformed historical proposal prevents a valid packet despite matching candidate bytes.",
  "after_behavior": "A provenance-valid recovery chain permits only the exact five revalidated baseline inputs.",
  "baseline": "Five untracked config candidates match recorded hashes; no capture commit exists.",
  "expected_result": "One scoped configuration commit with exact path and hash evidence, followed by independent review.",
  "self_descriptive_naming": "The slug names WI-5664 configuration baseline capture and this title names provenance recovery.",
  "obsolete_guidance_disposition": "Historical versions and their unreadable author metadata remain preserved but non-authorizing.",
  "history_preservation": "No existing bridge or configuration candidate is rewritten, cleaned, or attributed before GO.",
  "nonimpairment": "No source, package, projection, or unrelated configuration path is in scope.",
  "hard_invariants": ["exactly five paths", "hash match before staging", "fresh packet before protected write", "no historical rewrite"],
  "fail_closed_conditions": ["missing GO/claim/packet", "any hash mismatch", "any extra staged path", "failed projection or named test"],
  "essential_context_preservation": "The original byte ownership matrix stays durable while the malformed predecessor remains quarantined.",
  "rollback": "Use a new governed follow-up; do not reset or clean the shared worktree."
}
```

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

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Valid current authority | Fresh `implementation_authorization.py begin` after GO | packet authorizes exactly five targets |
| Byte ownership | SHA-256 recheck before staging | all five values equal the matrix |
| Scope isolation | cached diff, committed path list, and `git diff --check` | exactly five paths, no unrelated bytes |
| Config consistency | named projection check and tests from v003 | pass on the committed tree |
| Independent closure | implementation report with commit SHA and LO review | no terminal claim before independent VERIFIED |

## Owner Decisions / Input

No new owner decision is required. `DELIB-202667193` authorizes the bounded
self-driving sweep while retaining the per-slice GO, packet, scoped commit, and
independent verification gates.

## Pre-Filing Preflight

Run applicability and clause preflights against this complete content. Passing
preflight only permits filing the proposal; it does not permit capture.

## Risk / Rollback

Matching bytes are not implementation authority. The recovery stops on any
hash, authorization, scope, projection, or test divergence. No source or
configuration bytes change through this proposal filing.
