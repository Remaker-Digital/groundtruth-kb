# Harness Parity Phase 2 Codex Baseline Matrix

- Overall status: FAIL
- Project: PROJECT-HARNESS-PARITY-PHASE-2
- Work item: WI-4899
- Evaluator source work item: WI-4900
- Project authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
- Bridge: gtkb-harness-parity-phase-2-codex-baseline-matrix
- Counts: blocked: 4, needs_adapter: 13, supported: 43

## WI-4926 Provider Readiness Contract

| Harness | Credential source | Default readiness assertion | Live-probe boundary | Failure classification |
| --- | --- | --- | --- | --- |
| ollama | No API key is read from `.env.local`; the provider endpoint is the local Ollama HTTP service. | Provider-scoped routing validation is mocked and only validates Ollama rows from `.api-harness/routing.toml`. | Dispatch startup may call local `/api/tags`; no peer harness may be launched. | Unreachable local endpoint or missing advertised model is a provider/configuration readiness failure. |
| openrouter | `OPENROUTER_API_KEY` is loaded from process environment or authoritative `.env.local` through `scripts._env.load_env_local()`. | Missing-key, retry, provider-backpressure, and invalid-response behavior is tested with mocks. | Dispatch startup may call OpenRouter chat completions after key loading; no peer harness may be launched. | Missing key is configuration failure; provider 401/403 is invalid credential/provider rejection; 429/5xx is provider outage/backpressure. |

Relevant active Phase 2 waivers remain event-source or transcript-surface
waivers only: `WAIVER-P2-OLLAMA-EVENT-SOURCE`,
`WAIVER-P2-OPENROUTER-EVENT-SOURCE`,
`WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE`, and
`WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE`. They do not waive provider
readiness, credential-source, or live-probe classification assertions.

## Findings

| Harness | Dimension | State | Release Blocking | Evidence | Disposition | Details |
| --- | --- | --- | --- | --- | --- | --- |
| antigravity | Bridge write and verdict path | supported | True | .agent/skills/bridge | Supported | Bridge helper or harness bridge route exists. |
| antigravity | Dispatcher receive capability | blocked | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Candidate: Close antigravity dispatcher receive capability gap | can_receive_dispatch=False; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| antigravity | Event-source capability | blocked | False | harness-state/harness-registry.json | Candidate: Close antigravity event-source capability gap | can_fire_events=False |
| antigravity | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| antigravity | Hook or governed-helper surface | supported | True | .agent | Supported | Harness has a hook or governed-helper surface. |
| antigravity | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close antigravity no-window launch evidence gap | Provider/adapter invocation lacks explicit no-window evidence. |
| antigravity | Provider or adapter settings | supported | True | harness-state/harness-registry.json | Supported | Harness is not provider-shim scoped. |
| antigravity | Readiness probe | supported | True | scripts/verify_antigravity_dispatch.py | Supported | Readiness or harness wrapper script exists. |
| antigravity | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=retired; roles=['loyal-opposition'] |
| antigravity | Skill projection surface | supported | True | .agent/skills | Supported | Known skill projection surface exists. |
| claude | Bridge write and verdict path | supported | True | .claude/skills/gtkb-bridge/helpers<br>.claude/skills/gtkb-verify/helpers | Supported | Bridge helper or harness bridge route exists. |
| claude | Dispatcher receive capability | blocked | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Candidate: Close claude dispatcher receive capability gap | can_receive_dispatch=False; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| claude | Event-source capability | blocked | False | harness-state/harness-registry.json | Candidate: Close claude event-source capability gap | can_fire_events=False |
| claude | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| claude | Hook or governed-helper surface | supported | True | .claude/settings.json<br>.claude/hooks | Supported | Harness has a hook or governed-helper surface. |
| claude | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close claude no-window launch evidence gap | Native CLI invocation lacks explicit no-window evidence. |
| claude | Provider or adapter settings | supported | True | harness-state/harness-registry.json | Supported | Harness is not provider-shim scoped. |
| claude | Readiness probe | needs_adapter | True | scripts/verify_claude_dispatch.py<br>scripts/claude_harness.py<br>scripts/check_claude_harness.py | Candidate: Close claude readiness probe gap | No deterministic readiness probe was found. |
| claude | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=suspended; roles=['prime-builder'] |
| claude | Skill projection surface | supported | True | .claude/skills | Supported | Known skill projection surface exists. |
| codex | Bridge write and verdict path | supported | True | .codex/skills/gtkb-bridge/helpers<br>.codex/skills/gtkb-verify/helpers | Supported | Bridge helper or harness bridge route exists. |
| codex | Dispatcher receive capability | supported | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Supported | can_receive_dispatch=True; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| codex | Event-source capability | supported | False | harness-state/harness-registry.json | Supported | can_fire_events=True |
| codex | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| codex | Hook or governed-helper surface | supported | True | .codex/hooks.json<br>.codex/gtkb-hooks | Supported | Harness has a hook or governed-helper surface. |
| codex | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close codex no-window launch evidence gap | Native CLI invocation lacks explicit no-window evidence. |
| codex | Provider or adapter settings | supported | True | harness-state/harness-registry.json | Supported | Harness is not provider-shim scoped. |
| codex | Readiness probe | needs_adapter | True | scripts/verify_codex_dispatch.py<br>scripts/codex_harness.py<br>scripts/check_codex_harness.py | Candidate: Close codex readiness probe gap | No deterministic readiness probe was found. |
| codex | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=active; roles=['prime-builder'] |
| codex | Skill projection surface | supported | True | .codex/skills/MANIFEST.json | Supported | Known skill projection surface exists. |
| cursor | Bridge write and verdict path | supported | True | .cursor/skills/bridge/helpers | Supported | Bridge helper or harness bridge route exists. |
| cursor | Dispatcher receive capability | needs_adapter | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Candidate: Close cursor dispatcher receive capability gap | can_receive_dispatch=False; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| cursor | Event-source capability | needs_adapter | False | harness-state/harness-registry.json | Candidate: Close cursor event-source capability gap | can_fire_events=False |
| cursor | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| cursor | Hook or governed-helper surface | supported | True | .cursor/rules<br>.cursor/gtkb-hooks | Supported | Harness has a hook or governed-helper surface. |
| cursor | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close cursor no-window launch evidence gap | Provider/adapter invocation lacks explicit no-window evidence. |
| cursor | Provider or adapter settings | needs_adapter | True | config/agent-control/harness-capability-registry.toml::[harnesses.cursor] | Candidate: Close cursor provider or adapter settings gap | Provider-shim floor is missing: routing_schema_version, skill_adapter_manifest, skill_adapter_generation_supported. |
| cursor | Readiness probe | supported | True | scripts/cursor_harness.py | Supported | Readiness or harness wrapper script exists. |
| cursor | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=active; roles=['prime-builder'] |
| cursor | Skill projection surface | supported | True | .cursor/skills/MANIFEST.json | Supported | Known skill projection surface exists. |
| ollama | Bridge write and verdict path | supported | True | scripts/ollama_harness.py<br>.api-harness/skills/bridge | Supported | Bridge helper or harness bridge route exists. |
| ollama | Dispatcher receive capability | supported | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Supported | can_receive_dispatch=True; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| ollama | Event-source capability | needs_adapter | False | harness-state/harness-registry.json | Candidate: Close ollama event-source capability gap | can_fire_events=False |
| ollama | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| ollama | Hook or governed-helper surface | supported | True | scripts/ollama_harness.py | Supported | Harness has a hook or governed-helper surface. |
| ollama | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close ollama no-window launch evidence gap | Provider/adapter invocation lacks explicit no-window evidence. |
| ollama | Provider or adapter settings | supported | True | config/agent-control/harness-capability-registry.toml::[harnesses.ollama] | Supported | Provider-shim capability floor is declared. |
| ollama | Readiness probe | supported | True | scripts/verify_ollama_dispatch.py<br>scripts/ollama_harness.py | Supported | Readiness or harness wrapper script exists. |
| ollama | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=active; roles=['loyal-opposition'] |
| ollama | Skill projection surface | supported | True | .api-harness/skills/MANIFEST.json | Supported | Harness declares an adapter manifest and the file exists. |
| openrouter | Bridge write and verdict path | supported | True | scripts/openrouter_harness.py<br>.api-harness/skills/bridge | Supported | Bridge helper or harness bridge route exists. |
| openrouter | Dispatcher receive capability | supported | True | config/dispatcher/rules.toml<br>harness-state/harness-registry.json | Supported | can_receive_dispatch=True; dispatcher required roles=['loyal-opposition', 'prime-builder'] |
| openrouter | Event-source capability | needs_adapter | False | harness-state/harness-registry.json | Candidate: Close openrouter event-source capability gap | can_fire_events=False |
| openrouter | Headless invocation surface | supported | True | harness-state/harness-registry.json | Supported | Headless argv is declared. |
| openrouter | Hook or governed-helper surface | supported | True | scripts/openrouter_harness.py | Supported | Harness has a hook or governed-helper surface. |
| openrouter | No-window launch evidence | needs_adapter | True | harness-state/harness-registry.json::invocation_surfaces.headless.argv | Candidate: Close openrouter no-window launch evidence gap | Provider/adapter invocation lacks explicit no-window evidence. |
| openrouter | Provider or adapter settings | supported | True | config/agent-control/harness-capability-registry.toml::[harnesses.openrouter] | Supported | Provider-shim capability floor is declared. |
| openrouter | Readiness probe | supported | True | scripts/openrouter_harness.py | Supported | Readiness or harness wrapper script exists. |
| openrouter | Harness registry projection | supported | True | harness-state/harness-registry.json | Supported | status=active; roles=['loyal-opposition'] |
| openrouter | Skill projection surface | supported | True | .api-harness/skills/MANIFEST.json | Supported | Harness declares an adapter manifest and the file exists. |

## Candidate Work Items

- Close codex readiness probe gap: Add a deterministic codex readiness probe that Phase 2 release checks can execute before dispatching work. Evidence: scripts/verify_codex_dispatch.py; scripts/codex_harness.py; scripts/check_codex_harness.py.
- Close codex no-window launch evidence gap: Add static or runtime no-window launch evidence for codex so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
- Close claude dispatcher receive capability gap: Make the claude dispatcher receive configuration truthful and release-ready, or record a typed Phase 2 waiver if the harness cannot receive dispatched work. Evidence: config/dispatcher/rules.toml; harness-state/harness-registry.json.
- Close claude event-source capability gap: Classify and implement the claude event-source path, or record why this harness is receive-only for Phase 2. Evidence: harness-state/harness-registry.json.
- Close claude readiness probe gap: Add a deterministic claude readiness probe that Phase 2 release checks can execute before dispatching work. Evidence: scripts/verify_claude_dispatch.py; scripts/claude_harness.py; scripts/check_claude_harness.py.
- Close claude no-window launch evidence gap: Add static or runtime no-window launch evidence for claude so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
- Close antigravity dispatcher receive capability gap: Make the antigravity dispatcher receive configuration truthful and release-ready, or record a typed Phase 2 waiver if the harness cannot receive dispatched work. Evidence: config/dispatcher/rules.toml; harness-state/harness-registry.json.
- Close antigravity event-source capability gap: Classify and implement the antigravity event-source path, or record why this harness is receive-only for Phase 2. Evidence: harness-state/harness-registry.json.
- Close antigravity no-window launch evidence gap: Add static or runtime no-window launch evidence for antigravity so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
- Close ollama event-source capability gap: Classify and implement the ollama event-source path, or record why this harness is receive-only for Phase 2. Evidence: harness-state/harness-registry.json.
- Close ollama no-window launch evidence gap: Add static or runtime no-window launch evidence for ollama so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
- Close cursor dispatcher receive capability gap: Make the cursor dispatcher receive configuration truthful and release-ready, or record a typed Phase 2 waiver if the harness cannot receive dispatched work. Evidence: config/dispatcher/rules.toml; harness-state/harness-registry.json.
- Close cursor event-source capability gap: Classify and implement the cursor event-source path, or record why this harness is receive-only for Phase 2. Evidence: harness-state/harness-registry.json.
- Close cursor provider or adapter settings gap: Add or repair provider/adapter settings for cursor, including model/routing evidence when this harness is backed by a provider shim. Evidence: config/agent-control/harness-capability-registry.toml::[harnesses.cursor].
- Close cursor no-window launch evidence gap: Add static or runtime no-window launch evidence for cursor so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
- Close openrouter event-source capability gap: Classify and implement the openrouter event-source path, or record why this harness is receive-only for Phase 2. Evidence: harness-state/harness-registry.json.
- Close openrouter no-window launch evidence gap: Add static or runtime no-window launch evidence for openrouter so Windows background dispatch cannot flash visible consoles. Evidence: harness-state/harness-registry.json::invocation_surfaces.headless.argv.
