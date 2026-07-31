WITHDRAWN
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5664 provenance-valid baseline carrier — obsolete-objective withdrawal

bridge_kind: operational_state_change
Document: gtkb-wi5664-provenance-valid-config-baseline-capture
Version: 007
Responds to: bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-006.md
Date: 2026-07-29 UTC
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664
target_paths: []
implementation_scope: none
kb_mutation_in_scope: false

## Withdrawal

This baseline-capture carrier is withdrawn because its proposed future object
no longer exists. Owner-authored broad commit
`db07f9dcfe7e7de8addc850729209278472cb0fe` added the five exact configuration
files among 531 committed paths from parent
`6c0b0628fdb0b34bf06168ca37955649cc07ff30`. All five are now tracked and clean
and remain byte-identical to the old hash matrix.

This is not a claim that WI-5664 was implemented or verified through this
thread. No matching five-path claim or schema-v3 implementation-start packet,
isolated five-file commit, implementation report, or independent VERIFIED
transaction exists. The broad commit contains unrelated work and must not be
attributed post hoc as a scoped WI-5664 implementation.

Withdrawal closes only this obsolete duplicate carrier. It does not resolve
WI-5664, approve the broad commit, authorize a source/configuration mutation,
or waive the WI-5640 prerequisite recorded in v006.

## Exact Current Evidence

| Path | Current SHA-256 | Current state |
| --- | --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | `00BF3E301056B03E2F8F29E9DB9883271706431789292590BEE29A51D7214B21` | tracked and clean |
| `config/agent-control/gtkb-review-gate.md` | `E71113033C49833AAA99B3B8199D0DE36FA0C67F6B2EA07E6470FA2FE821BED1` | tracked and clean |
| `config/agent-control/gtkb-file-bridge-protocol.md` | `B336537A026EAE4339C7C2AE36FFCE7D4B0787658A394D4C8884F39E93695F7D` | tracked and clean |
| `config/agent-control/gtkb-loyal-opposition.md` | `82100953A26A5BE9D232BC3732DA45589A83B0185C30436378F22AFE752AFF60` | tracked and clean |
| `config/agent-control/gtkb-command-surface.toml` | `51C195520D03B37474759676F0B1F676F60C992F17683221DFC0D29228C27B35` | tracked and clean |

`git show --name-status db07f9dcf -- <the five paths>` reports each as added.
`git status --short -- <the five paths>` is empty. The hashes are the same
values proposed when the files were untracked, proving object obsolescence but
not governed transaction provenance.

## Remaining Repair Hold

The actual implementation carrier remains
`gtkb-wi5664-rules-config-skill-reference-repair`, latest NO-GO v004. Its stale
references remain live, but it must not be revised until WI-5640's current
repair-forward sequence completes the governed exact-plan apply (WI-5708) and
post-apply verification (WI-5709). WI-5640 is still open/implementing; its
Stage-A VERIFIED result is not terminal Stage-B closure.

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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full carrier chain, current claim inventory, and broad-commit inspection | No valid capture transaction exists; terminal withdrawal prevents duplicate authority. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `git show` of `db07f9dcf` and v006 provenance finding | Broad owner commit is preserved as incident evidence, not reattributed. |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped `git status`, `git ls-files`, and SHA-256 comparison | All five files are tracked, clean, and byte-identical to the proposed matrix. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No source implementation or behavior claim; path/hash/history checks only | Withdrawal is evidence-only and does not claim tests establish implementation provenance. |

## Commands Executed And Observed Results

- `git status --short -- <the five paths>` — no output.
- `git ls-files -- <the five paths>` — all five paths returned.
- `git show --name-status --format='%H %P %s' db07f9dcf -- <the five paths>` — all five added in the 531-path broad commit.
- `Get-FileHash -Algorithm SHA256 -LiteralPath <the five paths>` — exact matrix above.
- `gt backlog show WI-5640` — open/implementing; Stage B remains decomposed into open WI-5707/WI-5708/WI-5709 work.
- No `pytest`, Ruff, source/configuration edit, staging, commit, MemBase write, dispatcher change, or external action was performed for this withdrawal.

## Pre-Filing Preflight

- Candidate applicability preflight: PASS (exit 0; no blocking errors).
- Candidate clause preflight: PASS (exit 0; 3 `must_apply` clauses, 0 evidence gaps, 0 blocking gaps).

## Owner Action Required

None. This terminal status removes an obsolete duplicate authority carrier and
does not choose whether to retain or reverse any implementation byte.
