GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Agent Red File Migration Re-Scope

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed document: `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`
Verdict: GO

## Claim

The `-008` revision is acceptable as a proposal-level inventory re-scope for
the ISOLATION-018 umbrella. It preserves the previously approved umbrella
concept from `-006`, passes the mandatory bridge applicability preflight, and
corrects the material split decisions that triggered the re-scope: `archive/`
stays platform, `assets/` is deferred for investigation, `.githooks/` is
platform, and 18.D is narrowed to branding/legal/Stripe config.

This is not a post-implementation verification of migration work. Downstream
sub-slices still need their own live inventory confirmation, per-sub-slice
proposal review, implementation report, and spec-derived verification.

## Prior Deliberations

Relevant deliberation search command:

```text
python -m groundtruth_kb deliberations search "gtkb-isolation-018 agent red file migration"
```

Observed relevant results included
`DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`, `DELIB-0878`,
`DELIB-1137`, `DELIB-1049`, and `DELIB-1119`. The result set did not surface a
prior owner decision or review that rejects the `applications/Agent_Red/`
migration direction.

The proposal also carries forward the prior thread context from
`bridge/gtkb-isolation-018-agent-red-file-migration-001.md` through `-007.md`,
including Codex `GO` at `-006` and the in-flight 18.A report at `-007`.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-file-migration
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:6504f1d31f1c04402676667fd3d80db706b02afd62367598c65c963b7e2038b7`
- bridge_document_name: `gtkb-isolation-018-agent-red-file-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`
- operative_file: `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

The generated table reports all matched blocking and advisory specs as cited,
including `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Evidence Reviewed

- Live `bridge/INDEX.md` shows the latest status for this thread as
  `REVISED: bridge/gtkb-isolation-018-agent-red-file-migration-008.md`.
- Full bridge history reviewed:
  `bridge/gtkb-isolation-018-agent-red-file-migration-001.md` through
  `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md:22` through
  `:42` cite the cross-cutting bridge specs, Agent Red topology GOV/DCL,
  active waiver DELIB, root-boundary rule, placement ADR, and predecessor
  bridge artifacts.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md:61` records the
  S334 owner instruction to re-scope the umbrella first.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md:149` and
  `:262` clarify that `archive/bridge-v1/` is GT-KB platform infrastructure
  and must not move to `applications/Agent_Red/`.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md:243` through
  `:256` defer `assets/` for investigation instead of treating generated
  Docusaurus-style assets as confirmed Agent Red source.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md:291` explicitly
  treats continuing inventory drift as expected and requires live
  `git ls-files` re-confirmation in each downstream sub-slice.

Live probes:

```text
git ls-files | Measure-Object
```

Observed: `5650` tracked files at review time. This differs from the proposal's
`5636` snapshot, but the drift is not blocking because the proposal itself
identifies continued drift as high-likelihood/low-impact and requires
execution-time re-confirmation for every sub-slice. The visible delta is
dominated by active platform/bridge churn rather than a contradiction of the
18.D split.

Additional live probes support the revised split:

- `git ls-files assets | Select-Object -First 20` returned only
  `assets/css/...` and `assets/js/...` paths, consistent with the proposal's
  build-output hypothesis.
- `git ls-files config` shows nine platform config files plus
  `config/stripe_product_ids.json`, consistent with the proposed 18.D Stripe
  config move and platform config stay-behind.
- `git ls-files .githooks` shows four platform git-hook files.
- `git ls-files .github/workflows` shows the mixed platform/application
  workflow set named in the proposal, including `groundtruth-kb-tests.yml` and
  `gtkb-secrets-scan.yml` as platform additions.

## Findings

No blocking findings.

### Non-Blocking Observation - Inventory Drift Remains Live

The exact tracked-file total is already stale at review time. I do not treat
that as a blocker because `-008` no longer depends on a single frozen total for
execution. The operationally important requirement is that each implementing
sub-slice re-probes its own file set before moving files, and `-008` states
that requirement directly.

Prime Builder should keep the downstream slice proposals narrow and should not
reuse the `-008` totals as execution-time truth without fresh `git ls-files`
evidence.

## Decision

GO.

Prime Builder may proceed with downstream ISOLATION-018 sub-slice work against
the corrected re-scope. This `GO` accepts the proposal-level inventory
corrections; it does not verify any migration implementation and does not waive
per-sub-slice bridge, preflight, or spec-derived verification gates.
