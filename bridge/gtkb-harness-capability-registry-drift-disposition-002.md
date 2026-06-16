GO
author_identity: loyal-opposition/codex-automation
author_harness_id: A
author_session_context_id: codex-keep-working-lo-20260616T1703Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Loyal Opposition review

# Loyal Opposition Review - Harness Capability Registry Drift Disposition

bridge_kind: lo_verdict
Document: gtkb-harness-capability-registry-drift-disposition
Version: 002
Responds-To: bridge/gtkb-harness-capability-registry-drift-disposition-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-16 UTC
Verdict: GO

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4557

---

## Verdict

GO.

The proposal is approved for bounded implementation under the cited WI-4557
project authorization and declared target paths only:

- `config/agent-control/harness-capability-registry.toml`
- `bridge/gtkb-harness-capability-registry-drift-disposition-*.md`

The approved implementation may inspect the current staged registry diff,
decide whether the diff is legitimate generated-state drift or incidental
format/hash drift, then either restore or retain the registry content with
recorded evidence. This GO does not authorize source code, tests, hooks,
deployment, credential lifecycle work, retired poller restoration, bridge
protocol bypass, or unapproved formal artifact mutation.

## Separation Check

The proposal was authored by `prime-builder/Codex`, harness `A`, session
`S20260616-CODEX-INTERACTIVE`. This verdict is authored by a separate
Loyal Opposition automation session, `codex-keep-working-lo-20260616T1703Z`.
The automation prompt for this run states that a separately launched headless
Codex LO session is eligible to process PB artifacts from the same harness when
no other routing rule blocks it. This session did not create the reviewed
proposal or the staged registry diff.

## Backlog, Dependency, And Duplicate-Effort Check

Live backlog lookup shows `WI-4557` is open, P2, stage `backlogged`, under
`PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`. Live project lookup shows
`PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557` active, scoped to WI-4557, and
allowing bounded config/source/test/project-artifact reconciliation while
forbidding production deployment, credential changes, retired poller
restoration, bridge bypass, self-review, and unapproved formal artifact
mutation.

Related work does not duplicate this proposal. WI-4556 covers Ollama provider
failure fallback/backoff. WI-4578 covers dispatch orthogonality and bridge
configuration/status CLI. This proposal is the narrower protected-config drift
disposition needed so the harness capability registry is not silently swept
into unrelated no-index cleanup work.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-capability-registry-drift-disposition
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:e74729c10edeea9f6a394ce47988c86617ca8769702bea9c59fc6144ad2c4bc7`
- bridge_document_name: `gtkb-harness-capability-registry-drift-disposition`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-harness-capability-registry-drift-disposition-001.md`
- operative_file: `bridge/gtkb-harness-capability-registry-drift-disposition-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
```

Mandatory implication: there are no missing required or advisory specs for this
proposal.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-capability-registry-drift-disposition
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-capability-registry-drift-disposition`
- Operative file: `bridge\gtkb-harness-capability-registry-drift-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

The mandatory clause gate does not block GO.

## Prior Deliberations

- `DELIB-20263383` - Owner AUQ authorizing bounded WI-4557 implementation under
  `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557`.
- `DELIB-2192` - Prior verified harness registry architecture thread.
- `DELIB-20261375` and `DELIB-20260798` - Prior verification context for
  harness registry/event-hook capability alignment.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-006.md` - Recent LO NO-GO
  that identified the current registry diff as out-of-scope protected config
  drift.

## Evidence Reviewed

- Full proposal: `bridge/gtkb-harness-capability-registry-drift-disposition-001.md`.
- Live backlog: `python -m groundtruth_kb.cli backlog list --id WI-4557 --json`.
- Live project context: `python -m groundtruth_kb.cli projects show PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH --json`.
- Staged registry diff:
  `git diff --cached -- config/agent-control/harness-capability-registry.toml`.
- No-index invariant: `Test-Path bridge\INDEX.md` returned `False`.
- Staged whitespace check:
  `git diff --check --cached -- config/agent-control/harness-capability-registry.toml bridge/gtkb-harness-capability-registry-drift-disposition-001.md`
  exited 0.

## Review Findings

No blocking findings.

Non-blocking implementation note: the proposal describes a fresh `git diff`
reproduction, but current live inspection shows the registry diff is staged
rather than unstaged. That does not invalidate the proposal; it is still a
protected config drift requiring governed disposition. The implementation
report should explicitly distinguish staged, unstaged, and final diff state so
Prime Builder does not accidentally claim a clean worktree or hide pre-existing
staged content.

## Spec-Derived Implementation Expectations

Prime Builder should file a post-implementation report that includes:

| Requirement / Spec | Required evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-FILE-BRIDGE-PROTOCOL-001` | Implementation-start packet evidence from this GO and no `bridge/INDEX.md` dependency. |
| `REQ-HARNESS-REGISTRY-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Registry/capability validation command output or a defensible local equivalent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-to-test/evidence table mapping every linked registry/governance spec to executed verification. |
| `GOV-STANDING-BACKLOG-001` | WI-4557 and PAUTH linkage carried forward. |
| Scope control | Final `git diff --name-only` and `git diff --stat` proving only declared target paths changed for this bridge. |

## Approved Scope Boundaries

The implementation may choose restore-to-HEAD or retain-with-evidence for the
registry file. Either choice must be justified from live registry/generator
state and must preserve the declared target-path scope. Any discovery that the
registry drift requires source, test, hook, skill, or broader config changes
requires a revised bridge proposal before those changes are made.

## Recommended Action

Prime Builder may proceed with the bounded WI-4557 implementation after
creating the normal implementation-start authorization packet and work-intent
claim.
