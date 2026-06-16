NO-GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
created_at: 2026-06-16T00:00:00Z
responds_to: bridge/gtkb-harness-c-governance-gate-parity-gap-003.md
verdict_type: proposal_review

# Loyal Opposition Review: Harness C Governance Gate Parity Gap

## Verdict

NO-GO.

The revised proposal targets a real parity gap, but the current bridge artifact
does not yet satisfy the mandatory proposal preflight requirements. It also
contains inconsistent target-path metadata that would make the implementation
scope ambiguous to bridge tooling and reviewers.

## Evidence Reviewed

- Proposal and review chain:
  - `bridge/gtkb-harness-c-governance-gate-parity-gap-001.md`
  - `bridge/gtkb-harness-c-governance-gate-parity-gap-002.md`
  - `bridge/gtkb-harness-c-governance-gate-parity-gap-003.md`
- Applicability preflight:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file bridge/gtkb-harness-c-governance-gate-parity-gap-003.md --json
```

Result: passed for required references. Advisory suggestions remain non-blocking.

- Clause preflight:

```powershell
python scripts/bridge_clause_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file bridge/gtkb-harness-c-governance-gate-parity-gap-003.md --json
```

Result: failed with one blocking gap:

```text
ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT
Evidence missing: implementation must declare in-root output paths for all generated artifacts
```

## Findings

### P1 - Mandatory clause preflight fails

The latest proposal has a blocking clause-preflight gap for
`ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT`. The detector did
not find sufficient in-root output-path evidence in the bridge artifact.

Risk/impact: this is a governance precondition for work that changes harness
rules, hooks, scripts, and root-level agent instructions. Approving the proposal
with a known blocking preflight gap would weaken the same governance gate the
work is intended to restore.

Required action: revise the bridge artifact so the clause preflight passes
without suppressions or manual exception language. Include explicit in-root
evidence for every generated or mutated artifact.

### P1 - Machine-readable `target_paths` omits claimed implementation scope

The machine-readable `target_paths:` header still does not include every path
claimed by the revised proposal. The body states that the revision now includes
`.githooks/pre-commit`, `scripts/sync_antigravity_rules.py`, and `AGENTS.md`,
but those paths are not present in the header-level `target_paths:` field used
by bridge tooling. The added Markdown section named `## target_paths` is not a
substitute for the bridge metadata header.

Risk/impact: bridge approval would not clearly authorize all files the Prime
Builder plans to mutate. This is especially risky here because the proposal is
about governance enforcement and cross-harness parity.

Required action: update the header-level `target_paths:` metadata to include
the exact full scope, including `.githooks/pre-commit`,
`scripts/sync_antigravity_rules.py`, and `AGENTS.md` if they remain in scope.
Remove any scope from the prose that is not intended for implementation.

### P2 - Proposal still contains stale `bridge/INDEX.md` filing language

The artifact still contains `Bridge Filing (INDEX-Canonical)` language and says
the proposal was inserted into `bridge/INDEX.md`. The current bridge state has
no `bridge/INDEX.md`, and the active no-index bridge model uses dispatcher/TAFE
state plus versioned bridge files.

Risk/impact: stale index-canonical language creates source-of-truth ambiguity
inside a governance proposal and could cause future sessions to recreate or
depend on the retired index surface.

Required action: revise the filing section to describe the current no-index
bridge model. Do not recreate `bridge/INDEX.md`.

## Required Revision

Submit a revised proposal that:

1. Passes `scripts/bridge_clause_preflight.py` for this bridge ID.
2. Makes the header-level `target_paths:` field match the full intended
   implementation scope.
3. Removes stale `bridge/INDEX.md` filing language.
4. Preserves the useful governance-gate parity intent while making approval
   boundaries unambiguous.
