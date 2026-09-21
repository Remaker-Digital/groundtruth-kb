# 5. Governance

Governance is the self-regulating layer of the GroundTruth method. It defines the rules about how specifications, tests, and work items interact — and enforces those rules automatically through gates and assertions.

## Governance specifications

Governance rules are themselves specifications, prefixed with `GOV-`. This is intentional: the method governs itself using the same artifact system it provides to projects. Governance records, like all specification records, live in MemBase per ADR-0001: Three-Tier Memory Architecture. Governance specifications:

- Are stored in MemBase like any other spec
- Carry machine-verifiable assertions
- Use the current formal lifecycle: active, superseded or retired
- Can be proposed, reviewed, and refined like any requirement

### Core governance rules

Examples of governance concerns include the following. Retrieve each applicable current formal record before relying on its wording; this table does not seed or activate rules:

| Rule | Name | Principle |
|------|------|-----------|
| GOV-01 | Spec-first | Create or update specifications before writing implementation code |
| GOV-03 | Test clarity | Every test must produce an unambiguous pass or fail result |
| GOV-05 | Fix spec first | When specs and implementation disagree, correct the spec before changing code |
| GOV-07 | No fixes during testing | Record test failures as work items; fix in separate sessions |
| GOV-12 | WI triggers tests | Creating a work item must be followed by creating linked tests |

Projects can add their own governance specs. The only requirement is that each carries testable assertions — governance without enforcement is just documentation.

## Governance checks

The native domain services validate the requested operation against current
canonical state. A record amendment supplies its expected version, actor and
change reason; stale versions refuse instead of overwriting another change.
Read back the resulting record and verify the intended effect.

Project authorization, proposal review, claims, test evidence and Git
finalization have distinct roles. Authorization is the owner's value on the
project row. A work item has one project membership; it does not carry an
independent authorization record. Verification concerns the exact reviewed
work product and does not change a specification's lifecycle to `verified`.

The former package `pre_promote`, `pre_resolve_work_item` and `pre_test_pass`
plugin interfaces do not describe the native amendment route. Do not configure
those callbacks or `owner_approved` fields as a way to enforce or satisfy
native operations. Use the supported CLI and the current formal contract for
the operation, including its typed refusal and recovery path.

An assertion pass is evidence for the behavior it checks. It does not supply
authorization, independent review or a missing completion result.

## Assertions

Assertions are the continuous monitoring layer. Where gates enforce rules at transition points, assertions check the codebase at any time.

### Assertion types

| Type | Check | Example |
|------|-------|---------|
| `grep` | Pattern exists in file | "rate_limit" appears in config.py |
| `glob` | File matching pattern exists | tests/test_auth.py is present |
| `grep_absent` | Pattern does NOT exist in file | No hardcoded API keys in source |
| `file_exists` | Single file exists | src/config.py is a file |
| `count` | Pattern count with operator | Exactly 8 save fields in presets.py |
| `json_path` | Value at path in JSON/TOML | pyproject.toml version is "1.0.0" |
| `all_of` | All children pass (AND) | Config file exists AND has required key |
| `any_of` | At least one child passes (OR) | Has .toml or .yaml config |

For full field reference and examples, see [Assertion Language Reference](../reference/assertion-language.md).

### When assertions run

- **On demand**: `gt assert` from the CLI; scripts and CI run the same command with `--json` (machine-readable summary) and `--triggered-by <label>`
- **At project-configured checkpoints**: projects can configure hooks to run assertions at session start, before builds, or at other lifecycle points — these are project-specific automation, not built into the package

### Interpreting results

- **Pass:** the evaluated assertion is satisfied by the measured inputs.
- **Failure:** its required condition is not satisfied; investigate the exact
  diagnostic and preserve the failed evidence before correcting the cause.
- **Skipped or unevaluated:** the run has not established that condition.
  Record the reason and the required coverage instead of counting it as a pass.

Evaluate assertions of current active records. Specification lifecycle status
does not classify a failure as an expected implementation gap or a regression;
use the requirement, prior evidence and exact changed inputs to determine that.
Superseding or retiring a record preserves its history and requires the proper
canonical disposition; it is not a way to waive a failed assertion.

## Protected behaviors

Protected behaviors (`PB-*`) are a special class of governance specification for critical system invariants. They carry assertions that run before every build, acting as a regression gate.

Use protected behaviors for safety-critical constraints that must never silently regress: authentication requirements, data isolation guarantees, rate limiting enforcement, credential handling rules.

The difference from regular governance: regular GOV specs describe process rules (how to work). Protected behaviors describe system invariants (what must always be true about the running system).
