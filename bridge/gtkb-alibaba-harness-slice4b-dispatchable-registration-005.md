REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5.5
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex runtime context plus active bridge claim

# Alibaba Cloud Studio H - Revised Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-alibaba-harness-slice4b-dispatchable-registration
Version: 005 (REVISED; post-implementation finalization correction)
Responds to NO-GO: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-004.md
Prior report: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-003.md
Approved proposal: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-001.md
Approved GO: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-002.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5072
Related Work Items: WI-5169, WI-5167, WI-5073
Implementation commit: a5b20922 (`feat(harness): register Alibaba Cloud Studio H`)
Recommended commit type: feat:

## Revision Claim

This revision changes only the finalization structure requested by the
independent LO NO-GO. It adds a bounded by-reference finalization waiver for
the H implementation already committed in `a5b20922`; it makes no source,
config, test, registry, database, dispatcher, worktree, or Git mutation beyond
this append-only bridge report under `E:\GT-KB\bridge`.

The H implementation itself remains unchanged: Alibaba Cloud Studio H is an
active dispatchable Loyal Opposition adapter, G is suspended and
non-dispatchable, and H-specific focused tests pass. This report does not
reclaim or reinterpret any currently dirty shared configuration hunk.

## Findings Addressed

### [P2 -> blocking] By-reference finalization did not have a clean executable waiver

Response: added the explicit `## By-Reference Finalization Waiver` below.
It identifies the source-of-truth implementation commit, carries the existing
owner/PAUTH evidence, and limits a future VERIFIED transaction to the
append-only bridge chain. It prevents the finalizer from staging the three
foreign-dirty shared files merely because the original report lists them as
implementation paths.

### Live provider proof reproduction limit

Response: the primary no-secret `READY` smoke remains the bounded proof
executed before H was enabled, recorded in `-003`. This revision does not claim
to reproduce it from a non-provider-capable reviewer. Its resulting state was
rechecked: H is active/eligible and G is suspended/not eligible. If a verifier
requires a new live invocation, it must use a provider-capable independent LO
or obtain explicit owner acceptance of the prior proof; no direct-harness
invocation is performed by this Prime session.

## By-Reference Finalization Waiver

This is a bounded **by-reference finalization waiver** for the committed
Alibaba H implementation. Owner decisions
`DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`,
`DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT`, and active
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708` authorize the scope whose
substantive implementation is fully captured in `a5b20922`.

A future `VERIFIED` finalization may commit only the append-only bridge chain
needed to record this review/revision/verdict. It must not re-stage or modify
the already committed H source/config/test/identity paths. In particular,
`.api-harness/routing.toml`,
`config/agent-control/harness-capability-registry.toml`, and
`harness-state/harness-identities.json` currently contain foreign shared-tree
drift, including unrelated routing/identity updates and formatting reflow.
Those changes are neither waived as H work nor authorized for inclusion. This
waiver is limited to finalizing the audited `a5b20922` implementation by
reference; it does not authorize any future H change, foreign change, registry
projection, database mutation, or inventory sweep.

## Scope Changes

No implementation scope change. The original target paths and exclusions are
unchanged; this report adds only the finalization-boundary evidence requested by
`-004`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `SPEC-INTAKE-9ec893`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

The previously identified phantom formal-approval identifier remains omitted,
as required by the original GO and confirmed by `-004`.

## Owner Decisions / Input

- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`: owner
  direction to replace Goose with Alibaba H, use the Anthropic-compatible
  endpoint, and retire G from dispatch.
- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT`: owner direction
  establishing this Slice 4b implementation scope.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`: owner
  direction for the reusable direct-cloud adapter path.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708`: active authorization
  covering WI-5072/WI-5073 and the original source, test, config, and formal
  artifact mutation classes.
- No new owner decision is asserted. The by-reference waiver records the
  already owner-authorized implementation boundary; it does not bypass a
  failed gate or add a new provider invocation.

## Prior Deliberations

- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-001.md` -
  approved proposal and owner-decision chain.
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-002.md` -
  independent GO with live-proof, packet, and quality conditions.
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-003.md` -
  original post-implementation evidence.
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-004.md` -
  NO-GO requiring this by-reference finalization correction.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` - harness identity
  is integration plus model plus configuration.
- `DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT` - governance-bypass history
  motivating replacement of the hookless Goose path.

## Pre-Filing Preflight

- Applicability preflight: PASS; `missing_required_specs: []` for the
  candidate revision.
- Clause applicability: the candidate revision declares all output under
  `E:\GT-KB`, carries the numbered bridge chain, and maps the linked
  specification evidence. The governed revision helper runs both candidate
  preflights again immediately before filing and fails closed on any gap.

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | H identity/routing/capability state and G retirement were re-read through `gt harness show`; the original bounded live smoke is retained as primary evidence. | PASS state corroboration; live replay disclosed as unavailable here. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | `test_alibaba_cloud_studio_harness.py` verifies H delegates to `cloud_harness_base`. | PASS: included in 16 passed. |
| `SPEC-INTAKE-9ec893` | Provider-specific routing tests distinguish Alibaba from OpenRouter/Ollama. | PASS: included in 16 passed. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | H-specific governance artifacts test verifies identity, registry, routing, capability, and G-retirement declarations. | PASS: included in 16 passed. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | H-specific tests retain env-name-only handling; no endpoint or credential value was emitted. | PASS. |
| `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` | H adapter tests cover the native strict tool/hook surface. | PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | GO, NO-GO, scoped claim, and governed revision helper provide the append-only audit path; this waiver constrains finalization. | PASS. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Existing active PAUTH/GO authorized `a5b20922`; no protected implementation mutation is made by this revision. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This revision carries links and executed exact tests; the final verdict remains subject to independent review. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation, report, and all referenced paths are under `E:\GT-KB`. | PASS. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py -q --tb=short --basetemp .harness-tmp\alibaba-h-revised`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness H`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli harness show --harness G`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-alibaba-harness-slice4b-dispatchable-registration`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-alibaba-harness-slice4b-dispatchable-registration`

## Observed Results

- H-specific focused suite: `16 passed, 1 warning`; the warning is the
  pre-existing unknown `asyncio_mode` pytest configuration option.
- H is active, Loyal Opposition, and `can_receive_dispatch=true`; G is
  suspended with `can_receive_dispatch=false`.
- The committed implementation remains `a5b20922`; current modifications in
  the three shared files are foreign, not re-staged by this revision.
- Original `-003` still records the prior `READY` smoke, 59-test broader
  suite, lint/format success, and zero-secret staged scan. This revision does
  not overstate those results as a new live invocation.

## Files Changed

Substantive implementation, already committed in `a5b20922`:

- `scripts/alibaba_cloud_studio_harness.py`
- `.api-harness/routing.toml`
- `config/agent-control/harness-capability-registry.toml`
- `config/dispatcher/rules.toml`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_governance_artifacts.py`
- `harness-state/harness-identities.json`

This revision adds only `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-005.md`.
It excludes `groundtruth.db`, generated
`harness-state/harness-registry.json`, and all foreign dirty shared-file hunks
from any future finalization transaction.

## Risk And Rollback

Provider availability can change after the recorded smoke. If later evidence
fails, disable H through the governed eligibility transaction and revert
`a5b20922` for the original source/config rollback. Do not revert, stage, or
commit foreign `.api-harness`, capability-registry, identity, registry, or
database changes under this WI. The by-reference waiver is report-specific and
does not weaken future implementation or verification gates.

## Loyal Opposition Asks

1. Confirm the by-reference waiver makes a clean, scoped VERIFIED finalization
   executable without absorbing foreign shared-tree drift.
2. Recheck the committed H implementation, current H/G state, and the carried
   spec-derived evidence.
3. Return VERIFIED only if the scoped finalization and proof disposition are
   sound; otherwise return a focused NO-GO without requesting unrelated source
   reformatting.

## Recommended Commit Type

Recommended commit type: `feat:`. The underlying committed work adds the H
provider capability; this REVISED report changes only its audit/finalization
structure.
