NO-GO

# GENERATOR-HARDENING-002 - Codex Review of REVISED-2

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-002-005.md`

## Claim

GH-002 REVISED-2 fixes the prior weak test shape, but the implementation scope
still has one blocking ambiguity: it says `--harness-config-root` has default
`Path.home()`. That conflicts with the stated guarantee that an invocation
which explicitly supplies `--harness-config-root <tmp>` must not call
`Path.home()`.

## Evidence

`generator-hardening-002-005.md` says:

> Add `--harness-config-root` argparse argument with default `Path.home()`
> (resolved at parse-time in `main()`).

If the parser or argument default evaluates `Path.home()` while building the
parser, then the hard-fail monkeypatch test will fail even when
`--harness-config-root` is supplied. The correct shape for this scope is the
same pattern already used for other derived paths in GH-001:

```python
parser.add_argument("--harness-config-root", type=Path, default=None, ...)
...
harness_config_root = (
    args.harness_config_root.resolve()
    if args.harness_config_root is not None
    else Path.home()
)
```

That preserves legacy behavior when the argument is omitted, while guaranteeing
that the explicit override path does not require `Path.home()`.

The revised tests otherwise move in the right direction:

- hard-fail `Path.home()` during the generator run;
- AST-based check instead of fixed line numbers;
- stronger positive proof tying output back to the sentinel-bearing role record.

## Required Revision

Revise the scoping text to require:

1. `--harness-config-root` default is `None`, not `Path.home()`.
2. `Path.home()` is called only after parse, and only when the argument is
   omitted.
3. The hard-fail monkeypatch is installed before `module.main(...)` is invoked
   with `--harness-config-root`.
4. The positive proof should assert the resolved fake harness-root path or
   sentinel-bearing role source through a stable output field, avoiding a brittle
   regex if the report has a structured model/helper available.

No owner decision is needed.

