NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed fleet proof audit; reasoning high

# Defect-Fix Proposal - WI-5255 B/C Telemetry Worker Provenance

bridge_kind: prime_proposal
Document: gtkb-wi5255-bc-telemetry-worker-provenance
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5255-BC-TELEMETRY-PROVENANCE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5255

target_paths: ["scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py"]

## Claim

Prime Builder proposes a bounded dispatcher/telemetry correction so native B and C runs receive the same trusted worker-provenance coverage as provider-shim D/F/H runs. The dispatcher will establish a per-dispatch worker session document for every launched role and pass only trusted target/session fields into reconciliation; telemetry will populate worker identity and role only after validating that session document.

## Defect / Reproduction

Two successful, substantive, dispatcher-produced LO runs expose the defect:

- B dispatch `2026-07-14T11-17-33Z-loyal-opposition-B-6fa33a` reviewed `gtkb-wi5224-provider-verdict-completion-contract`, emitted canonical `VERIFIED`, and exited zero. Its telemetry correlation and outcome are complete, but all seven `worker` fields are null.
- C dispatch `2026-07-15T00-03-02Z-loyal-opposition-C-7bf06c` reviewed `gtkb-wi5233-dispatch-selection-order-cap-repair-implementation`, emitted canonical `VERIFIED`, and exited zero. Its telemetry has the same null worker object.

The canonical B and C verdict files carry exact target-authored harness, session, model, and role metadata. Those verdicts prove the runs, but model-authored content must not be reused as telemetry role authority. Equivalent D, F, and H records are complete because their provider runtimes create `DispatchTelemetryObserver` instances before dispatcher reconciliation.

Code inspection shows the asymmetry:

1. `scripts/cloud_harness_base.py` and `scripts/ollama_harness.py` create full observer records for D/F/H.
2. Native B/C processes do not use that Python observer.
3. `scripts/dispatcher_runtime.py` currently creates a dispatcher-composed worker session only for Prime launches.
4. `reconcile_dispatch_telemetry` creates a partial record with a deliberately all-null `worker` object and accepts no trusted worker/session inputs, so it cannot enrich native B/C records.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` already require bounded telemetry with trustworthy worker and role provenance. WI-5255 corrects an adapter-path implementation gap; it does not define a new source of authority.

## In-Root Placement Evidence

All four implementation and test targets are inside `E:\GT-KB`. Runtime worker session documents and telemetry remain generated in the existing in-root harness-state and `.gtkb-state` locations through canonical APIs. The implementation does not edit retained telemetry, dispatcher runtime JSON, leases, eligibility, roles, model routes, or allowances directly.

## Proposed Scope

### IP-1 - Role-neutral dispatcher worker-session establishment

Generalize the existing Prime-only worker-session helper into one role-neutral helper. Before spawning either Prime or Loyal Opposition work, create the per-dispatch session document with the selected target's harness id/name, dispatcher-composed role, canonical init keyword, and dispatch id. Keep the existing Prime ordering invariant: session authority is established before work-intent acquisition or implementation packet issuance. For LO, establish the document after lease selection and launchability checks but before process spawn. A failure creates the existing bounded `worker_session_authority_failed` launch denial and no worker is started.

Do not use registry fallback or model output as the dispatched role source.

### IP-2 - Trusted reconciliation worker envelope

Extend `reconcile_dispatch_telemetry` with an optional, structured worker context supplied by the dispatcher launch record. The context may carry selected harness id/name, provider/command handle, configured model hint, turn budget, session id, and the expected role. Reconciliation must:

1. resolve the per-dispatch session document using the existing session-envelope authority path;
2. require its session id, dispatch id, harness id/name, and role to match the trusted launch context;
3. populate `worker.role` and `worker.role_source_document_id` only from the validated document;
4. populate non-authority identity/model fields only from dispatcher-selected target/configuration data, never verdict prose;
5. preserve a partial null worker plus an explicit bounded diagnostic when the document is absent, unreadable, or inconsistent; and
6. never overwrite a full provider observer's non-null fields with weaker or conflicting reconciliation input.

### IP-3 - Launch-record and completion plumbing

Persist the bounded trusted worker context in each launch-ledger entry and pass it into reconciliation at exit. Preserve concurrent launch-ledger semantics, exact dispatch correlation, failure reconciliation, retry classification, document lease behavior, and all 600/900/3600/29400/29700 allowances.

### IP-4 - Focused cross-adapter tests

Add hermetic tests for successful B and C native-style partial reconciliation, nonzero/timeout reconciliation, missing and mismatched session documents, provider-observer preservation, concurrent launch-ledger isolation, and Prime/LO pre-spawn worker-session ordering. Assert that no telemetry value is parsed from verdict text.

## Cross-Harness Disposition

- B/C: gain complete trusted worker provenance on dispatcher-reconciled telemetry without adding provider tools or direct harness contact.
- D/F/H: retain their full provider observer records; reconciliation may fill only missing fields from stronger validated dispatcher/session evidence.
- A: remains Prime Builder only; the generalized session helper preserves Prime start ordering and does not grant LO authority.
- E/G: no eligibility, role, or runtime change; behavior remains inert while suspended/out of scope.
- No typed waiver is requested.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - defines the bounded telemetry worker/provenance envelope corrected by this slice.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs launch records, target identity, exit reconciliation, and cross-adapter dispatch behavior.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role may be populated only from a validated per-dispatch session document.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - telemetry and verdict evidence must retain exact target/session/model attribution without model self-assertion becoming authority.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - genuine functional proof requires attributable dispatcher-produced work for each harness.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the correction preserves the complete generous launch and lease envelope.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - protected implementation remains PAUTH and operation-time gated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every applicable governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact PAUTH/project/WI metadata is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - TEST-11410 maps the provenance contract to executable tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this NEW artifact is filed as the next append-only numbered bridge file `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-001.md`; no protected implementation begins before independent GO, claim, and start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - session/telemetry evidence cannot substitute for the bridge lifecycle.
- `SPEC-AUQ-POLICY-ENGINE-001` - no missing provenance is inferred from user or model prose.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all source, tests, generated session documents, and telemetry stay under the GT-KB root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - A's Prime session ordering and Codex-specific enforcement remain intact while the helper becomes role-neutral.
- `GOV-STANDING-BACKLOG-001` - the proof-audit defect is preserved as WI-5255 rather than ignored.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - dispatch evidence, defect, test, PAUTH, proposal, implementation, and verification remain linked artifacts.

## Prior Deliberations

- `DELIB-202666173` authorizes correction of every defect discovered during the active A/B/C/D/F/H governed fleet proof.
- `DELIB-202666118` records the WI-5173 telemetry usage-coverage proposal review.
- `DELIB-202666117` records independent WI-5173 post-implementation verification.
- `DELIB-20263271` records the earlier dispatch-starvation telemetry verification lineage.
- The committed WI-5224 B verdict and WI-5233 C verdict provide the target-authored terminal evidence whose dispatcher telemetry is incomplete.

## Owner Decisions / Input

- `DELIB-202666173` is the active owner directive for fleet proof and durable correction of observed TAFE/bridge defects.
- No new role, eligibility, budget, direct harness access, runtime allowance, or provider decision is requested.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| TEST-11410 complete B/C worker envelope | `python -m pytest platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k "telemetry or worker_session"` proves native B/C reconciliation uses trusted target and session inputs. |
| Session role authority | Hermetic tests seed matching and conflicting per-dispatch documents and prove only the matching document populates role and role-source fields. |
| Provider observer preservation | Focused telemetry tests prove D/F/H-style full records are not overwritten by weaker reconciliation context. |
| Launch ordering and failure safety | Dispatcher tests prove both roles establish worker session authority before spawn and a document failure launches no process or claim-backed Prime work. |
| Envelope preservation | Existing lifetime, lease, concurrent launch-ledger, selection-order, and exit-reconciliation tests remain green. |
| Static quality | `python -m ruff check groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py scripts/dispatcher_runtime.py platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_dispatcher_runtime.py`. |

## Acceptance Criteria

- New successful and failed B/C dispatcher runs populate all available `worker` identity/model fields from trusted dispatcher inputs and populate role/source only from a validated per-dispatch session document.
- Missing or conflicting role evidence remains fail-closed and produces an explicit bounded coverage diagnostic instead of silently presenting an all-null successful record.
- No value is inferred from model-authored verdict content.
- Full D/F/H provider observer fields are preserved during exit reconciliation.
- A remains PB-only and Prime worker-session/claim/start ordering is unchanged.
- No dispatcher runtime JSON, retained telemetry, lease, eligibility, role, model route, credential, deployment, Git remote, or unrelated dirty-worktree mutation occurs.
- Focused and regression tests pass, followed by independent LO verification and a focused commit.

## Risks / Rollback

The primary risk is giving dispatcher intent the status of role authority. The validator therefore requires a matching per-dispatch session document and keeps role null on any mismatch. A second risk is reconciliation overwriting richer provider telemetry; merge tests enforce non-null/full-record preservation. Rollback is a focused revert of the four approved files; historical telemetry remains unchanged and the previous partial-record behavior returns.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`

## Recommended Commit Type

`fix`
