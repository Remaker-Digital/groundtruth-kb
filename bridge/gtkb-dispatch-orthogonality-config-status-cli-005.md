NEW
Responds to: E:/GT-KB/bridge/gtkb-dispatch-orthogonality-config-status-cli-003.md (revise: fix-no-go-004-missing-required-spec-citations)

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Dispatch Orthogonality, Configuration, and Status CLI Implementation Report

bridge_kind: implementation_report
Document: gtkb-dispatch-orthogonality-config-status-cli
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC
Implemented Version: 001
Reviewed Version: 002
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

---

## Summary

Implemented the owner-agreed bridge topology and made role assignment, lifecycle status, event-firing capability, and dispatchability independent axes.

Current live bridge dispatch health is PASS:

- Prime Builder selected target: Codex (`A`).
- Prime Builder non-dispatch target: Claude Code (`B`).
- Loyal Opposition selected order: Ollama (`D`), OpenRouter (`F`), Antigravity (`C`).

## Implementation Notes

- Added `config/dispatcher/rules.toml` as the bridge dispatch configuration surface for per-harness dispatchability, event-firing capability, cost, quality, availability, max-items, and rule ranking.
- Added `groundtruth_kb.bridge_dispatch_config` and `groundtruth_kb.bridge_dispatch_rules`.
- Added `gt bridge dispatch config/status/health` plus direct aliases `gt bridge config/status/health`.
- Updated harness projection to apply dispatcher config overlays and to treat deprecated `event_driven_hooks` as the event-firing compatibility alias.
- Updated cross-harness and single-harness dispatchers so multiple active same-role harnesses are valid and final selection is ranked by dispatcher config.
- Updated role/invariant/attribution wording so multi-Prime topology is not reported as a defect; ambiguity-sensitive fallback attribution still fails closed when no explicit harness can be resolved.
- Added `.claude/skills/bridge-config/SKILL.md` and `.codex/skills/bridge-config/SKILL.md`.
- Updated canonical guidance in `AGENTS.md`, `CLAUDE.md`, `.claude/rules/operating-role.md`, and `.claude/rules/canonical-terminology.md`.

During implementation a stale auto-dispatched Codex child process for the same GO thread was still running and repeatedly reclaimed the bridge work intent. That duplicate worker was stopped before final implementation and verification continued under session `019ecc04-9ec8-7e81-a2e7-10000eba4ed9`.

## Specification-Derived Verification

| Requirement / Spec | Verification | Result |
|---|---|---|
| `DELIB-20263438` role/dispatchability orthogonality | `gt bridge dispatch health --json` reports Codex `A` as PB dispatch target, Claude `B` PB but non-dispatchable, and LO targets `D`, `F`, `C` | PASS |
| `DCL-DISPATCH-ENVELOPE-RULES-001` declarative routing | `platform_tests/scripts/test_bridge_dispatch_config.py` covers status/activity rule matching and fail-closed non-match | PASS |
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` `::open <activity>` context | `context_from_bridge_text` extracts `::open verify` and rule selection consumes activity context | PASS |
| `REQ-HARNESS-REGISTRY-001` projection and active-role invariants | `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` and `platform_tests/groundtruth_kb/cli/test_harness_cli.py` | PASS |
| Cross-harness dispatch behavior | `platform_tests/scripts/test_cross_harness_bridge_trigger.py` | PASS |
| Single-harness dispatcher fallback behavior | `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` | PASS |
| Capability split / event-source wake behavior | `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py` | PASS |
| Attribution ambiguity handling | `platform_tests/scripts/test_kb_attribution.py` and `platform_tests/scripts/test_bridge_author_metadata.py` | PASS |
| CLI health/status/config reporting | `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py` | PASS |

## Commands Run

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb.cli bridge dispatch config --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb.cli bridge dispatch status
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb.cli bridge dispatch health --json
$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short
```

Final focused regression result: `186 passed in 13.17s`.

## Residual Risk

The broader worktree contains many unrelated pre-existing dirty files outside this bridge implementation scope. They were not reverted or normalized as part of this implementation.

## Post-Filing Dispatch Note

After this report was filed, the cross-harness trigger correctly selected Ollama (`D`) as the cheapest Loyal Opposition verifier for this `NEW` item. The spawned Ollama verification process produced no stdout/stderr for more than 90 seconds and showed a duplicate `ollama_harness.py` parent/child loop, so the stuck worker and its post-dispatch poller were stopped. The bridge entry remains `NEW` for verification.

## Specification Links
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — added via `gt bridge revise` (citation_add).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — added via `gt bridge revise` (citation_add).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — added via `gt bridge revise` (citation_add).

