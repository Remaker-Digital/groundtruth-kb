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

Default runs are non-mutating. JSON and Markdown output can be written under
`.gtkb-state/harness-parity/` as runtime evidence:

```powershell
python scripts/harness_parity_phase2.py --project-root . --format json --output .gtkb-state/harness-parity/phase2-latest.json
python scripts/harness_parity_phase2.py --project-root . --format markdown --output .gtkb-state/harness-parity/phase2-latest.md
```

Use `--strict` when release automation should fail on unwaived
release-blocking parity gaps. Candidate work-item commands in the report are
advisory text only; the evaluator does not mutate MemBase or bridge state.
