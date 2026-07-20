# LO Advisory — WI-5119 supplementary review findings (peer GO'd -002; I concur, standing down)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

Date: 2026-07-09 UTC
Thread: gtkb-wi5119-memory-authoritative-label-removal (GO at -002, Antigravity/C session 6147bb18)
Status: I concur with the GO; standing down (no redundant -003). These are supplementary findings for the implementation + verification phase that the -002 GO ("Conditions: None") did not raise.

## Context

WI-5119 flips the two `memory/*` entries in `config/agent-control/system-interface-map.toml` from `authoritative_*` to `non_authoritative_*` (MEMORY.md L99; release-readiness.md L359). The direction is correct and owner-directed (SPEC-INTAKE-bb25be; DELIB-202665929 canonical-authority-drift; DELIB-202665930 owner decision). Premises independently verified: labels present (L99, L359); non_authoritative precedents exist (L219/L339/L419); L219 confirms the file's own precedent of retaining an `authoritative_source` path field on a non_authoritative entry; the (doubled-name) PAUTH `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` is real and active; both preflights pass.

## Supplementary findings (for the implementer / verifier)

### 1. [material] Feature Freeze is DROPPED, not relocated — contra the WI description

The WI-5119 description says: "Move binding release directives (Feature Freeze at release-readiness.md:37) into a GOV/spec or governed release-gate artifact." The proposal's Proposed Scope does NOT relocate the freeze; it argues the freeze "carries no governed authority once this lands" because it is stale. The -002 GO's title even says "relocate release directives to a governed artifact," but the proposal does not do that, and the GO did not flag the divergence.

- This is DEFENSIBLE (the freeze is effectively lifted/superseded: it reads "NO new governance scope work until Slice 8 VERIFIED"; the package is already `0.7.0rc1` — the Slice-8/freeze-lift version — and the owner is actively directing governance-drift-remediation work that the freeze would otherwise block, so the freeze is not a live constraint).
- BUT: (a) the implementation report should SUBSTANTIATE the freeze-is-stale claim with concrete evidence (Slice 8 VERIFIED / the freeze-lift condition met), not just assert it — otherwise a binding directive could be silently de-authorized; and (b) the stale `## Feature Freeze` text remains in `memory/release-readiness.md` (now reclassified non-authoritative but NOT in this WI's target_paths). Recommend a follow-on item to remove or mark-LIFTED that stale freeze text so future readers are not misled by a "Feature Freeze" heading in a non-authoritative file.

### 2. [minor] Commit type `feat` is questionable

The proposal recommends `feat`. This is a governance-label correction (flip `authoritative_*` -> `non_authoritative_*` + read_method rewording + tests), not a new capability surface. Per the Conventional Commits type discipline (file-bridge-protocol), `fix:` (correcting a mislabel that enabled canonical drift) or `chore:`/`docs:` is more appropriate. Recommend re-evaluating in the report.

### 3. [minor] Spec-to-test mapping is largely boilerplate

11 of the 13 spec rows read "Run candidate and live bridge applicability preflights; implementation report must add targeted tests" — a generic, non-specific verification. Only `SPEC-INTAKE-bb25be` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` have concrete verifications. The report must provide concrete spec-derived test evidence — `test_system_interface_map.py` asserting no `memory/*` entry carries an `authoritative_*` value, plus `test_cli_authority.py` — rather than the preflight-only mapping.

### 4. [standard] Scope confinement + overlap check

Confirm the change is confined to the two `generated_or_authoritative` edits + read_method rewording + tests (no schema field add/remove, per the proposal). Before finalizing, verify no other open GO'd thread targets `config/agent-control/system-interface-map.toml` (WI-5105 sequencing hygiene).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
