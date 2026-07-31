# Harness Parity Phase 2 Baseline Evaluator

Harness Parity Phase 2 uses `scripts/harness_parity_phase2.py` as the read-only
baseline evaluator for `PROJECT-HARNESS-PARITY-PHASE-2` / `WI-4900`.

The evaluator reads live repository state from:

- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`
- `config/agent-control/harness-capability-registry.toml`
- `config/harness-parity/phase2-waivers.toml`

It reports per-harness cells for registry projection, headless invocation,
dispatcher receive capability, event-source capability, skill projection,
hook or governed-helper projection, bridge write/verdict route, readiness
probe, provider settings, and no-window launch evidence.

## WI-4926 Provider Readiness Contract

Provider-harness readiness is a contract over GT-KB control-plane behavior, not
a credential rotation or provider-activation workflow. Default Harness Parity
Phase 2 evaluator runs remain non-mutating and must not launch one harness from
another harness. Readiness proof for provider-backed harnesses is split into
mocked assertions and live dispatch operation:

| Surface | Default parity/assertion behavior | Live-provider boundary | Failure class |
| --- | --- | --- | --- |
| Ollama | Tests and evaluator checks validate provider-scoped routing without contacting a live provider. OpenRouter rows in `.api-harness/routing.toml` are ignored by Ollama routing validation. | `scripts/ollama_harness.py` dispatch startup calls the local Ollama `/api/tags` inventory and then the configured chat endpoint. This is a live local-provider probe, not a peer-harness invocation. | Missing local endpoint, unreachable inventory, or configured Ollama model absent from `/api/tags` is provider/configuration readiness failure. |
| OpenRouter | Tests and evaluator checks validate routing, guard behavior, retry classification, and missing-key handling with mocks. | `scripts/openrouter_harness.py` loads the authoritative `.env.local` surface through `scripts._env.load_env_local()` before dispatch and requires `OPENROUTER_API_KEY`. | Missing `OPENROUTER_API_KEY` is configuration failure. HTTP 401/403 from OpenRouter is invalid-credential/provider rejection. HTTP 429/5xx and malformed transient responses are provider outage/backpressure paths with bounded retry. |

Credential values must never appear in governed docs, tests, bridge files, or
registry metadata. It is acceptable to cite variable names, fake examples, and
placeholder values. The Phase 2 waiver registry keeps the event-source and
full-transcript exceptions for Ollama/OpenRouter separate from readiness:
receive-only provider harnesses can be waived for event firing or transcript
archive parity without waiving their provider readiness contract.

Default runs are non-mutating. JSON and Markdown output can be written under
`.gtkb-state/harness-parity/` as runtime evidence:

```powershell
python scripts/harness_parity_phase2.py --project-root . --format json --output .gtkb-state/harness-parity/phase2-latest.json
python scripts/harness_parity_phase2.py --project-root . --format markdown --output .gtkb-state/harness-parity/phase2-latest.md
```

Use `--strict` when release automation should fail on unwaived
release-blocking parity gaps. Candidate work-item commands in the report are
advisory text only; the evaluator does not mutate MemBase or bridge state.
