REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5933-slice-b-resolver-fail-closed
Version: 003
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-002.md
Prior GO: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py"]

**No KB mutation.** This slice performs no MemBase/KB write and does not modify
`groundtruth.db`. It changes source, harness-hook, and test files only.

**No approval-evidence work.** This slice creates no formal-artifact-approval packet and modifies no approval-packet path.
No `.groundtruth/formal-artifact-approvals` path is written, read as authority, or declared in `target_paths`, because none is touched.
The v7 approval record is cited by date only, as historical evidence that the DCL was approved; this slice does not consume, amend, or supersede it.
The protected narrative artifacts carrying stale retired-spec citations are explicitly out of scope here and are captured as WI-5945 for separate, per-artifact remediation.

# WI-5933 Slice B REVISED (003) - authority re-grounded; retired-spec citation removed

## Why This Revision Exists

The `-002` GO is sound on substance and its findings are accepted unchanged. This
revision is filed by the proposal's own author to correct a **citation defect in
`-001`** that would otherwise have been carried into implementation and
verification.

`-001` cited `GOV-SESSION-ROLE-AUTHORITY-001` in Specification Links. Verification
against MemBase shows that spec is **version 6, status `retired`**. Citing it as
active authority is a recorded repeat NO-GO cause per `DELIB-202668164`. It is
removed from the authority set below and is **not** relied upon anywhere in this
proposal.

No scope, design, target path, or test-plan change accompanies this correction.
C1/C2/C4/C5 and the C3 proof obligation are exactly as approved at `-002`.

## Authority Verification (performed for this revision)

An adjacent thread, `gtkb-wi5679-session-role-keying-continuity-016.md` (NO-GO),
asserts that `DCL-SESSION-ROLE-RESOLUTION-001` v7 is not valid completed
prerequisite evidence, on two grounds. Both were checked against canonical state
rather than accepted or dismissed:

| Ground asserted at WI-5679 `-016` | Canonical check | Result |
| --- | --- | --- |
| v7 "still actively cites retired `GOV-SESSION-ROLE-AUTHORITY-001`" | scan of the v7 spec body in MemBase | **Not supported.** The v7 body contains no reference to that spec. |
| v7 "was approved from a packet that omits the changed assertions" | approval-packet directory | A v7 packet **exists** at `.groundtruth/formal-artifact-approvals/2026-07-29-DCL-SESSION-ROLE-RESOLUTION-001-v7.json`. Whether its assertion set is complete is **not** adjudicated here and is left to WI-5679. |

The retired-spec citations that do exist are in **narrative surfaces**, not in the
DCL: `CLAUDE.md` line 7 and line 144 (governance index), plus
`.claude/rules/operating-role.md` line 166 and
`.claude/rules/prime-builder-role.md` line 105. That stale-surface defect is
captured as **WI-5945** and is not remediated by this slice (those are protected
narrative artifacts requiring their own approval packets).

This proposal therefore rests on `DCL-SESSION-ROLE-RESOLUTION-001` v7 as recorded
in MemBase (`status: specified`) together with the owner decision behind it. It
does not claim to resolve the WI-5679 packet-completeness question, and it does
not depend on it: the v7 clauses quoted below are the operative constraint, and
the defect they describe is independently observable in live source.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Every declared target is an in-root
path, and this bridge file resides under `E:/GT-KB/bridge/`. No generated
artifact is written outside the project root. No file under `applications/` is
touched.

## Problem Statement (unchanged from `-001`)

`DCL-SESSION-ROLE-RESOLUTION-001` v7 states:

> When explicit session-role identity cannot be resolved from the current
> session's validated transcript or session envelope, resolution fails closed
> with a typed recovery result. It MUST NOT substitute the durable registry role
> and MUST NOT emit `session_resolver_fallback`.

`scripts/session_role_resolution.py` violates this today, as independently
confirmed by the `-002` GO ("Live source still substitutes durable registry role
at lines 164/180 and exposes `durable_registry_role` at line 244; AXIS-2 still
coerces non-role results to `ROLE_PRIME`"):

| Line | Code | Violation |
| --- | --- | --- |
| 164 | `durable = _durable_role(project_root, harness_name)` | resolver consults the durable registry role |
| 180 | `fallback = envelope_role if envelope_role is not None else durable` | resolver substitutes it on four return paths |
| 244 | `"durable_registry_role": durable` | resolver exposes it to worker consumers |

First-hand reproduction remains as filed at `-001`: this session opened with
`::init gtkb pb` yet its envelope recorded `role: loyal-opposition` with
`role_resolution_source: session_resolver_fallback`, and governed bridge filing
refused the session until the envelope was re-opened.

## Consumer Analysis (unchanged; one constraint made explicit)

Thirty files reference the resolver. The `-002` GO confirmed the target set is
disjoint from WI-5723's declared paths.

A constraint discovered during implementation preparation is recorded here
because it shapes C1: `.claude/hooks/lo-file-safety-gate.py` line 309 and its
`config/hooks/` mirror refuse authority via
`if str(_outcome).startswith("durable_"): return False`. Neither file is in this
slice's `target_paths`. The existing source strings
(`durable_marker_absent`, `durable_marker_invalid_role`,
`durable_marker_stale_session`) are therefore **preserved verbatim** so that gate
continues to refuse. Only the substituted *role value* is removed. v7 forbids the
`session_resolver_fallback` label specifically; it does not require renaming these
source tokens, and renaming them would silently disable a live safety gate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each v7 clause to a test.
- `DCL-SESSION-ROLE-RESOLUTION-001` **v7** (`status: specified`; approved 2026-07-29) - the controlling constraint, plus assertions `ROLE-DCL-A5` and `ROLE-DCL-A6`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/application placement boundary; only platform surfaces are touched, as declared above.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role persistence, preserved by C5.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - discharged by the Cross-Harness Disposition section.
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary - why a mislabelled interactive role is a review-integrity defect.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

`GOV-SESSION-ROLE-AUTHORITY-001` is **deliberately absent**: verified retired
(v6). It is referenced nowhere in this proposal as authority.

## Prior Deliberations

- `DELIB-202668164` - owner authorization for the consolidated session-role purge
  lane and the Slice A/B split; also the record that citing the retired
  `GOV-SESSION-ROLE-AUTHORITY-001` as active authority is a repeat NO-GO cause.
- `AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01 - the owner decision requiring
  unresolved identity to fail closed and forbidding durable-registry fallback and
  the `session_resolver_fallback` label.
- `DELIB-202667742` - emergency repair authorization for interactive role
  persistence across session boundaries.
- `DELIB-202668165` - retroactive approval of the Slice A emergency-bootstrap
  repair; Slice A landed at `b638b42da` and was independently verified.
- WI-5723 (`gtkb-wi5723-session-resolver-fallback-removal`) - complementary lane
  with a disjoint target set per the `-002` GO; owner of the envelope-path label
  removal. C3 here is verification, not deletion.
- WI-5679 (`gtkb-wi5679-session-role-keying-continuity`) - adjacent, currently
  NO-GO; its DCL-v7 objection is addressed under Authority Verification above.
- WI-5945 - the stale retired-spec narrative citations captured during this
  revision.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` v7 is
recorded in MemBase as `specified` and was approved on 2026-07-29, and the
defect it describes is independently observable in live source and was
independently confirmed by the `-002` GO. This slice is source conformance to an
existing constraint. No new requirement is implied and no DCL amendment is
proposed.

## Proposed Change (unchanged from `-001`)

- **C1** - remove the `_durable_role` read (line 164) and the `else durable`
  substitution (line 180) from the interactive path; return a typed unresolved
  result when explicit evidence is absent, invalid, or stale, **preserving the
  existing `durable_*` source strings** so the LO file-safety gate keeps refusing.
- **C2** - remove `durable_registry_role` and `durable_registry_authority` from
  `resolve_interactive_session_role_details`; recompute `authority_mode` without a
  durable-fallback branch.
- **C3** - **verification only**, per the `-002` GO residual risk: prove in the
  implementation report that no production emitter of `session_resolver_fallback`
  remains, rather than assuming deletion work. The envelope-path removal belongs
  to WI-5723.
- **C4** - both AXIS-2 copies suppress the surface on an unresolved result instead
  of coercing to `ROLE_PRIME`.
- **C5** - preserve transcript-role persistence; fail-closed applies only where no
  valid explicit evidence exists.

## Cross-Harness Disposition

Unchanged from `-001` and accepted at `-002`. The behavioural change lives in the
shared `scripts/session_role_resolution.py`, which every harness consumes, so
resolver semantics are identical across harnesses by construction.

| Harness | Surface | Disposition |
| --- | --- | --- |
| B claude | `.claude/hooks/bridge-axis-2-surface.py` | **Updated (C4).** Unresolved suppresses the surface. |
| (tracked mirror) | `config/hooks/gtkb-bridge-axis-2-surface.py` | **Updated in lockstep**; parity asserted by T5. |
| A codex | `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | **Parity, no edit.** Already `try/except` -> `{}`; reads details via `.get()`, so removed keys degrade to `None`. Re-verified. |
| shared | `lo-file-safety-gate.py` / `gtkb-lo-file-safety-gate.py` | **Parity, no edit.** Already refuse on `durable_` prefix, which C1 preserves. Covered by T6. |
| C antigravity, D ollama, E cursor, F openrouter, G goose, H alibaba-cloud-studio | no harness-local role-resolution surface | **Parity via the shared resolver.** |

No owner-approved typed waiver is requested.

## Test Plan (specification-derived; unchanged)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | v7 no-substitution clause | with no explicit evidence and a durable role present, the resolver returns unresolved - never the durable role |
| T2 | v7 forbidden-label clause | no production path emits `session_resolver_fallback` (this is the C3 proof) |
| T3 | `ROLE-DCL-A5` | invalid-role and stale-session paths return typed unresolved with a recovery-bearing source |
| T4 | `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `ROLE-DCL-A6` | a validly established transcript role still resolves and persists |
| T5 | Cross-Harness Disposition | unresolved suppresses the AXIS-2 surface in both copies instead of defaulting to Prime Builder |
| T6 | Cross-Harness Disposition | the LO file-safety gate still refuses on non-explicit sources; `durable_*` strings preserved |
| T7 | v7 details-surface clause | `resolve_interactive_session_role_details` exposes no `durable_registry_role` key |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_role_resolution_table.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_runtime.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
```

## Acceptance Criteria (unchanged)

1. The interactive resolver never returns the durable registry role.
2. No production path emits `session_resolver_fallback` (proved, not assumed).
3. `resolve_interactive_session_role_details` exposes no durable role key.
4. A validly established transcript role still resolves and persists.
5. AXIS-2 suppresses rather than defaulting to Prime Builder on unresolved.
6. The LO file-safety gate shows no behavioural regression; `durable_*` source strings preserved.
7. All listed suites pass; both ruff gates pass on the changed files.

## Risk and Rollback

Unchanged from `-001`. Principal risk remains session-start fragility, mitigated
by C5 + T4 and by the fact that fail-closed applies only where evidence is
genuinely absent - the same condition that today yields a *wrong* role. Added
mitigation: the `durable_*` source strings are preserved so the out-of-scope LO
file-safety gate cannot silently stop refusing. Rollback is reverting the five
target files; no data migration, no schema change.

## Owner Decisions / Input

- **AUQ 2026-08-06 (Slice B disposition):** owner selected "Proceed under the GO",
  keeping the `-002` GO's adjudication of the WI-5723 overlap and its C3
  proof-obligation framing.
- **AUQ 2026-08-06 (Slice B footing):** owner selected "File REVISED, then
  implement" - the direct authority for this revision, which drops the retired-spec
  citation and re-grounds authority before implementation.
- **AUQ 2026-08-06 (stale citation):** owner authorized capturing the retired-spec
  narrative defect, filed as WI-5945.
- **`DELIB-202668164`** - owner authorization for the consolidated session-role
  purge lane.
- **`AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01** - the owner decision requiring
  fail-closed unresolved identity.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization.

## Recommended commit type

`fix:` - brings existing source into conformance with an approved design
constraint and removes an incorrect-role defect. No new capability surface.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
