NEW

# Defect-Fix Proposal - Codex PB readiness accepts runtime read-only sandbox despite workspace-write dispatch contract

bridge_kind: prime_proposal
Document: gtkb-wi5310-codex-effective-workspace-profile
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T21-31-23Z
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; reasoning xhigh


Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5310

target_paths: ["harness-state/harness-registry.json", "scripts/codex_no_window_smoke_probe.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Prime Builder proposes a bounded correction to the Codex A headless invocation
and readiness proof. A must remain Prime Builder only and must be able to do
authorized governed PB work through the dispatcher, not merely start and run
read-only commands without visible windows.

The current registry requests the legacy `--sandbox workspace-write` mode, but
Codex `0.130.0-alpha.5` reports `sandbox: read-only` at runtime. The existing
smoke nevertheless records PASS because it validates only marker commands and
window containment. The repair migrates the invocation to Codex's supported
built-in `:workspace` permissions profile and makes the proof fail closed on
either an effective-profile mismatch or inability to create, read, and remove
an in-root temporary sentinel.

This proposal is filed as the next append-only numbered bridge file,
`bridge/gtkb-wi5310-codex-effective-workspace-profile-001.md`. No prior bridge
version is deleted or rewritten.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`GOV-HARNESS-ONBOARDING-CONTRACT-001`, and
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` already require a real, governed,
write-capable headless PB execution surface and fail-closed parity behavior.
WI-5310 corrects implementation and verification drift against those existing
requirements; it does not introduce a new product or governance requirement.

## Defect / Reproduction

1. `python scripts/codex_no_window_smoke_probe.py --project-root . --dispatch-wrapper --json`
   returned PASS at `2026-07-15T21:48:16.004324Z` with two runs, three marker
   commands per run, private-desktop containment, and zero visible windows.
2. `python scripts/verify_codex_dispatch.py --json` then reported
   `live_headless_ready=true` and showed the registered
   `--sandbox workspace-write` argv.
3. Both smoke transcripts nevertheless contain `sandbox: read-only`.
4. Genuine dispatcher run
   `2026-07-15T21-48-32Z-prime-builder-A-aff7b2` launched A as PB on the
   Windows private desktop and exited 0 after 259 seconds, but its canonical
   `gt harness roles` command was rejected by policy and it could not file a
   governed `REVISED` artifact. Its stdout explicitly states the worker was
   read-only.
5. The installed Codex CLI exposes the new permissions-profile surface. The
   deterministic local command
   `codex sandbox windows --permissions-profile :workspace -C E:\\GT-KB
   cmd.exe /d /c echo GTKB-CODEX-SANDBOX-PROBE` exits 0. Binary-local contract
   text identifies `:workspace` as the implicit built-in workspace profile and
   warns that derived profiles which cannot be represented as legacy sandbox
   policy fall back to read-only.

This is distinct from WI-5308. WI-5308 renews a proof before its TTL expires;
WI-5310 corrects what the proof means and the effective permission profile it
must certify.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `harness-state/harness-registry.json`, `scripts/codex_no_window_smoke_probe.py`, `scripts/verify_codex_dispatch.py`, `platform_tests/scripts/test_codex_no_window_smoke_probe.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher readiness must describe
  the effective worker, not only static argv.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - an operating PB harness must execute
  its declared governed tool and write surfaces.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - native Windows Codex must preserve its
  self-enforced governance boundary when hook support differs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the implementation and final genuine write
  remain bridge- and role-gated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  carries the concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification
  requires the mapped automated and real-dispatch evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item,
  and active authorization are explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every changed and temporary
  surface remains inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the observed defect is normalized as WI-5310
  with linked TEST-11453 and PHASE-009 placement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - transient dispatch evidence is
  promoted into durable WI, test, proposal, report, and verdict artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - repair evidence is durable and
  independently reviewable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation follows the normal
  proposal, GO, claim, start, report, verification, and commit lifecycle.

## Prior Deliberations

- `DELIB-202665713` - WI-4985 Codex Headless Write Boundary — Implementation Report Review Verdict
- `DELIB-202665293` - independent confirmation that prior Codex headless
  workspace-write behavior could still be blocked at the effective sandbox
  identity.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - active fleet
  repair authorization used by the bounded WI-5310 PAUTH.

## Owner Decisions / Input

- Mike directed on 2026-07-15: "Codex must be restored to a fully dispatchable
  state in which headless PB workers are spawned on demand."
- The owner also requires every discovered bridge, TAFE, or harness defect to
  be captured as a work item with a linked test and processed through normal
  governance.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-20260715`
  bind this exact correction. They do not waive independent review, claims,
  implementation-start, testing, verification, or focused-commit gates.

## Proposed Scope

### 1. Canonical Invocation Migration

After GO and implementation-start authorization, use
`gt harness set-invocation-surface` for harness A's `headless` surface. Do not
hand-edit the generated registry or `groundtruth.db`.

The new argv must preserve model `gpt-5.5`, approval `never`, reasoning
`xhigh`, project-root selection, and `.codex` add-dir while replacing:

```text
--sandbox workspace-write
```

with:

```text
-c default_permissions=":workspace"
```

The old and new permission selectors must never coexist. A remains PB-only;
eligibility, routing, caps, precedence, and all other harness records remain
unchanged. Before and after canonical readback must prove that only A's
headless argv and generated projection version/timestamp changed.

`harness-state/harness-registry.json` currently contains unrelated staged and
unstaged generated projection changes. The canonical writer may preserve live
MemBase values, but this implementation must not stage, overwrite, revert, or
commit those foreign changes. Focused finalization waits until ownership is
clean or uses an approved hunk-exact finalizer.

### 2. Runtime-Capable Private-Desktop Smoke

Update `scripts/codex_no_window_smoke_probe.py` to invoke the same canonical
`:workspace` profile and require all of the following per run:

- effective runtime profile is exactly workspace-capable, with no read-only
  fallback in the Codex transcript;
- the worker creates a unique sentinel under the existing in-root smoke
  directory, reads the exact marker back, and removes it;
- the marker chain remains attributable and complete;
- the dispatcher wrapper and Windows private desktop remain active;
- all window observations remain zero;
- proof output records requested profile, observed effective profile,
  write/read/remove results, and a sanitized bounded transcript preview.

Any mismatch, missing sentinel lifecycle step, residual sentinel, visible
window, nonzero wrapper status, or ambiguous effective profile writes a failed
proof immediately. No still-current success may survive a visible-window or
permission-profile failure.

### 3. Static and Live Verifier Contract

Update `scripts/verify_codex_dispatch.py` to require the new
`default_permissions=":workspace"` selector, reject legacy `--sandbox`, reject
unknown or full-access profiles, and consume the stronger proof fields. Static
argv plus stale or incomplete runtime evidence must never produce
`dispatchable=true`.

### 4. Focused Tests and Genuine PB Proof

Add focused unit/integration fixtures for command construction, exact profile
parsing, read-only fallback, sentinel success/failure/cleanup, visible-window
failure, static verifier rejection, and current-proof acceptance. After those
tests pass, run one fresh substantive, governed, dispatcher-produced A/PB item
through the private desktop. It must use canonical helpers and publish an
authorized PB bridge artifact. Exit 0 without an artifact does not satisfy
acceptance.

## Specification-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_codex_no_window_smoke_probe.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` | Effective profile and write-capable readiness pass/fail cases are green. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Canonical `gt harness show A --json` plus before/after argv comparison | A is active, PB-only, and declares only `:workspace` with all existing pins preserved. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python scripts/codex_no_window_smoke_probe.py --project-root . --dispatch-wrapper --json` | Two private-desktop runs complete write/read/remove marker chains with zero visible windows. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh real A/PB dispatch on an independently approved actionable item | The target-authored next PB artifact is valid, attributable, and confined to approved paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO review of the report and command evidence | Every linked specification has executed evidence; verdict is VERIFIED. |
| Nonimpairment | Dispatcher report/status/health plus parity phase commands | No eligibility, role, cap, routing, live-worker, or parity regression. |

## Acceptance Criteria

1. A's canonical headless argv uses `default_permissions=":workspace"` and no
   legacy `--sandbox` selector.
2. A remains active, `can_receive_dispatch=true`, PB-only, max-items 4, model
   `gpt-5.5`, approval `never`, reasoning `xhigh`, and `.codex` add-dir intact.
3. The private-desktop smoke proves actual in-root write/read/remove capability
   and zero visible windows in two runs.
4. A transcript that reports read-only, unknown, ambiguous, or full-access
   effective permissions fails readiness even when commands exit 0.
5. `verify_codex_dispatch.py` cannot report live readiness from a legacy or
   incomplete proof.
6. A fresh dispatcher-produced A/PB worker publishes one substantive governed
   PB artifact through canonical helpers. Read-only analysis or a prose-only
   exit is insufficient.
7. Exact automated tests, parity checks, dispatcher health/status, and
   independent LO verification pass.
8. Unrelated staged/unstaged registry and worktree changes are preserved and
   excluded from the focused commit.

## Risks / Rollback

- **Permissions-profile compatibility:** Codex CLI versions before the active
  profile contract may not recognize `:workspace`. Fail closed in the static
  verifier and smoke; never fall back to read-only or full access silently.
- **Generated-registry concurrency:** canonical projection refresh can include
  concurrent harness changes. Compare exact before/after A argv and preserve
  every unrelated value; do not hand-edit or stage the shared file wholesale.
- **Sentinel residue:** unique per-run paths plus final cleanup are mandatory.
  A residual sentinel fails the probe and is removed by the probe's bounded
  cleanup path.
- **Window containment:** private-desktop behavior is unchanged. Any visible
  window revokes readiness immediately.
- **Rollback:** use the canonical `gt harness set-invocation-surface` writer to
  restore the exact pre-change A headless value, then write a failed readiness
  proof. Do not disable the bridge or daemon as rollback.

## Files Expected To Change

- `harness-state/harness-registry.json`
- `scripts/codex_no_window_smoke_probe.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`fix`
