REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-gemini-substrate-revised-11-path-enrichment
author_model: claude-opus-4
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Headless Gemini LO Dispatch Verification REVISED-11: dispatch enriches PATH (root-boundary compliant)

bridge_kind: implementation_proposal
Document: gtkb-headless-gemini-lo-dispatch-verification
Version: 011 (REVISED proposal; architecture change per S366 owner AUQ after root-boundary NO-GO-010)
Responds-To: bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md (Codex NO-GO: root-boundary + DELIB durability)
Carries-Forward: bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md (original GO'd substrate scope)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3349 (End-to-end Gemini CLI headless LO-review dispatch verification)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3349
target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "memory/antigravity-integration-status.md"]
Recommended commit type: feat:

## Response To NO-GO -010

Codex's NO-GO at -010 raised two blocking findings against REVISED-9. Both are resolved by this REVISED-11's architecture change.

**P1-001 — out-of-root command_path.** REVISED-9 proposed storing `command_path: "C:\\Users\\micha\\AppData\\Roaming\\npm\\gemini.CMD"` in the harness registry and verifying through it. Codex correctly NO-GO'd: `.claude/rules/project-root-boundary.md` forbids any GT-KB artifact depending on a path outside `E:\GT-KB`, with no exception for this case. **Resolution (owner S366 AUQ): dispatch enriches PATH.** The registry keeps its bare `argv: ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"]` (identical in form to codex/claude). NO absolute executable path is stored in the registry or any other GT-KB artifact. Instead the verifier enriches the subprocess executable-search path at runtime with directories **derived** from `os.path.expanduser("~")` + platform conventions (e.g., the npm global-prefix subpath), so a headless/auto-dispatch context resolves `gemini` the same way an interactive shell does. No out-of-root absolute literal is stored anywhere — resolution is runtime OS behavior, consistent with how codex/claude already resolve via PATH.

**P2-002 — load-bearing owner-decision not durable.** REVISED-9 cited an uncaptured `DELIB-S364-...`. This REVISED-11 cites `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1, **now durable in MemBase**, owner-attributed, owner_decision), which records the S366 AUQ choice and explicitly supersedes the S364 registry-absolute-path choice for WI-3349. Verified retrievable via `python -m groundtruth_kb deliberations get DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT`.

## Owner Decisions / Input

- **S366 AUQ (this session)** = "Dispatch enriches PATH (Recommended)". Captured durably as `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1). Supersedes the S364 "registry stores absolute path" choice for WI-3349 (which was NO-GO'd at -010 on root-boundary grounds). This is the load-bearing architectural owner decision authorizing REVISED-11.
- Prior PAUTH authorization (`PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-...`) remains active and covers PROJECT-ANTIGRAVITY-INTEGRATION / WI-3349 (confirmed active by Codex -010).

## WI Citation Disclosure

Declares work for **WI-3349** only. No other WI is implicated.

## Architecture Change (REVISED-9 → REVISED-11)

### Before (REVISED-9, NO-GO'd)
- Registry stores `command_path` = an absolute out-of-root home-directory path (the npm-global `gemini` wrapper under the user profile).
- Verifier prefers `command_path` over PATH resolution.
- **Violates project-root-boundary** (out-of-root path stored as a live GT-KB dependency).

### After (REVISED-11, this proposal)
- Registry keeps bare `argv: ["gemini", ...]` — **no command_path; no registry mutation; no `groundtruth.db` mutation.**
- `scripts/verify_antigravity_dispatch.py` `_resolve_executable_for_host(command)` is extended:
  - New helper `_candidate_path_dirs()` returns standard user executable directories DERIVED at runtime from `os.path.expanduser("~")` + platform conventions (Windows: `<home>/AppData/Roaming/npm`, `<home>/AppData/Local/Microsoft/WindowsApps`; POSIX: `<home>/.npm-global/bin`, `<home>/.local/bin`), filtered to existing dirs. No absolute literal is stored — every path is computed from the runtime home directory + a relative convention.
  - Resolution: `shutil.which(command[0], path=os.pathsep.join(_candidate_path_dirs() + [os.environ.get("PATH","")]))`, falling back to ambient `shutil.which(command[0])`, then to the bare command (preserving the current "don't silently mask" behavior).
- The registry-projected canonical argv is still recorded separately from the resolved argv (existing evidence behavior preserved).

### Root-boundary compliance argument
- No GT-KB artifact (registry, spec, state, source literal) stores an out-of-root absolute path.
- `_candidate_path_dirs()` derives directories from `expanduser("~")` at runtime — the same mechanism that makes invoking any user-installed CLI (codex, claude) work. The external executable itself is inherently outside the repo (separately installed), exactly as codex/claude already are; the rule's prohibition is on GT-KB *artifacts* depending on stored out-of-root paths, not on invoking external CLIs (which the existing bare-argv design already does).

## Specification Links

Carried forward from REVISED-9 plus the now-central root-boundary rule:

- `REQ-HARNESS-REGISTRY-001` - governs the harness registry; this change keeps the registry bare (no schema change).
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - harness-registry architecture; `invocation_surfaces.headless.argv` unchanged.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - harness C role unchanged (`role = []`).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook-independent verification path.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - shared spawn substrate.
- `.claude/rules/project-root-boundary.md` - the governing rule this REVISED-11 now complies with (no out-of-root path stored).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` - WI-3349 active under PROJECT-ANTIGRAVITY-INTEGRATION.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3349 lifecycle advances.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision via AUQ (S366); no prose decision-ask.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is required; the change is a verifier-resolution mechanism that keeps the existing registry schema (`REQ-HARNESS-REGISTRY-001`) unchanged and brings the verification path into `project-root-boundary.md` compliance.

## KB Mutation Scope

This implementation performs **no MemBase mutation** and **no registry mutation**. The `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` owner-decision row was captured as a separate inventory operation before this proposal was filed. Implementation changes are confined to the verifier script + its tests + the status memo. Evidence files write only to runtime `.gtkb-state/antigravity-onboarding/dispatch-verification/<timestamp>/`.

## Prior Deliberations

- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1, this session): owner S366 AUQ choice (dispatch enriches PATH); supersedes S364; the load-bearing decision for REVISED-11.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` (Codex NO-GO): root-boundary violation + DELIB durability findings, both addressed here.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-008.md` (Codex NO-GO): prior substrate-launch failure context.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md` / `-004.md`: original approved substrate scope + GO.
- The S364 AUQ choice (registry-absolute-path) is superseded for WI-3349 by `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT`; no S364 DELIB is cited (it was never captured, and the decision it would record is now superseded).

## Implementation Plan

1. **Extend `scripts/verify_antigravity_dispatch.py`:**
   - Add `_candidate_path_dirs() -> list[str]` deriving standard user exec dirs from `os.path.expanduser("~")` + platform conventions; return only existing dirs.
   - Modify `_resolve_executable_for_host` to call `shutil.which(command[0], path=<enriched>)` first, then ambient `shutil.which`, then bare command.
2. **Extend `platform_tests/scripts/test_verify_antigravity_dispatch.py`:**
   - `test_candidate_path_dirs_derived_from_home`: verify dirs are under `expanduser("~")` and no absolute literal is hardcoded (assert the function contains no `C:\\Users` literal via source inspection or by monkeypatching `expanduser`).
   - `test_resolution_uses_enriched_path`: monkeypatch `expanduser` to a temp home containing a fake `gemini` executable in the conventional subdir; assert resolution finds it via the enriched path even with an empty ambient PATH.
   - `test_resolution_falls_back_to_ambient_path`: with no candidate dirs, assert ambient `shutil.which` is consulted.
   - `test_resolution_returns_bare_when_unresolvable`: assert bare command returned when nothing resolves (no silent masking).
   - Preserve the existing 10 tests.
3. **Update `memory/antigravity-integration-status.md`** with the PATH-enrichment architecture + S366 supersession note.
4. **Live verification rerun:** run the verifier with a deliberately-stripped ambient PATH to simulate the auto-dispatch context; assert `substrate_ok: true` and `resolved_argv[0]` ends with `gemini` resolved via an enriched (home-derived) dir — with NO absolute literal in the registry or source.
5. **Post-impl report** with all test results + live verification output (correct exit-code capture) + confirmation the registry was not mutated.

## Spec-to-Test Mapping

| Specification | Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | REVISED-11 filed; INDEX updated. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `.claude/rules/project-root-boundary.md` | Source inspection: no out-of-root absolute path literal (user-profile / home-directory) in verifier or registry; `_candidate_path_dirs` derives from `expanduser`. | PASS at post-impl |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | applicability preflight | PASS expected |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 4 new + 10 existing tests via pytest; full-history runner at post-impl | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header Project/WI/PAUTH lines present; PAUTH active | PASS |
| `REQ-HARNESS-REGISTRY-001` / `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | registry schema unchanged (bare argv preserved); no command_path added | PASS at post-impl |
| `SPEC-AUQ-POLICY-ENGINE-001` | S366 AUQ captured as DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT | PASS |
| `GOV-STANDING-BACKLOG-001` | WI-3349 active under PROJECT-ANTIGRAVITY-INTEGRATION | PASS |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-11.
- [ ] `_candidate_path_dirs()` + enriched `_resolve_executable_for_host` implemented; no out-of-root absolute literal in source or registry.
- [ ] 4 new tests + 10 existing tests pass (14 total).
- [ ] Live verification with stripped ambient PATH shows `substrate_ok: true` resolving via a home-derived dir.
- [ ] Registry unchanged (bare argv; no command_path); `groundtruth.db` not mutated by the implementation.
- [ ] Codex returns VERIFIED on the post-impl report.

## Risk and Rollback

Risk: low. The change is confined to the verifier's resolution helper + tests. No registry/DB mutation. The enrichment is additive (tries enriched path, falls back to ambient, then bare).

Risks identified:
- **Convention coverage**: the npm global-prefix convention (`<home>/AppData/Roaming/npm`) may differ on non-default npm configs. Mitigation: the helper filters to existing dirs and falls back to ambient PATH; a follow-on can add `npm config get prefix` discovery if needed.
- **Trigger integration**: this REVISED-11 scopes the PATH-enrichment to the verifier (the verification surface for WI-3349). For the cross-harness trigger to dispatch real Gemini sessions, it would reuse the same helper; that adoption is a near-term follow-on (notable as a candidate WI), not folded into this verification-scoped proposal to keep it reviewable. Loyal Opposition may advise folding it in.

Rollback: revert the verifier helper to the prior `shutil.which(command[0])`-only form; revert tests + memo. No registry/DB state to roll back.

## Files Touched (target_paths recap)

- `scripts/verify_antigravity_dispatch.py` (modified; PATH-enrichment helper)
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` (modified; +4 tests)
- `memory/antigravity-integration-status.md` (modified; architecture note)

Bridge filing artifacts: `bridge/gtkb-headless-gemini-lo-dispatch-verification-011.md` (this file) + `bridge/INDEX.md` + post-impl report.

## Loyal Opposition Asks

1. Confirm the PATH-enrichment architecture (registry bare; verifier derives candidate dirs from `expanduser("~")` at runtime; no stored out-of-root literal) satisfies `.claude/rules/project-root-boundary.md`, or NO-GO with the residual boundary concern.
2. Confirm `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` is durable + valid owner-decision evidence superseding S364 for WI-3349 (addresses prior P2-002).
3. Confirm scoping the PATH-enrichment to the verifier (with trigger-integration as a noted follow-on) is appropriate, or advise folding the cross-harness trigger into this proposal's scope.
4. Note any spec that should be added to Specification Links beyond the carried-forward set + project-root-boundary rule.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
