# 5. Governance

Governance is the self-regulating layer of the GroundTruth method. It defines the rules about how specifications, tests, and work items interact — and enforces those rules automatically through gates and assertions.

## Governance specifications

Governance rules are themselves specifications, prefixed with `GOV-`. This is intentional: the method governs itself using the same artifact system it provides to projects. Governance specifications:

- Are stored in the knowledge database like any other spec
- Carry machine-verifiable assertions
- Move through the same lifecycle (specified → implemented → verified)
- Can be proposed, reviewed, and refined like any requirement

### Core governance rules

A GroundTruth project typically starts with these foundational rules (seeded by `gt seed`):

| Rule | Name | Principle |
|------|------|-----------|
| GOV-01 | Spec-first | Create or update specifications before writing implementation code |
| GOV-03 | Test clarity | Every test must produce an unambiguous pass or fail result |
| GOV-05 | Fix spec first | When specs and implementation disagree, correct the spec before changing code |
| GOV-07 | No fixes during testing | Record test failures as work items; fix in separate sessions |
| GOV-12 | WI triggers tests | Creating a work item must be followed by creating linked tests |

Projects can add their own governance specs. The only requirement is that each carries testable assertions — governance without enforcement is just documentation.

## Governance gates

Gates are enforcement hooks that run at artifact lifecycle transitions. They are the mechanism by which governance rules become more than suggestions.

### Built-in gates

GroundTruth ships with two gates:

**ADR/DCL Assertion Gate**: Architecture decision and design constraint specifications must have non-empty assertions before promotion to "implemented". This prevents architecture decisions from being marked as implemented without evidence of compliance checking.

**Owner Approval Gate**: Defect and regression work items require explicit owner approval (`owner_approved=True`) before resolution. This ensures that defect fixes are reviewed, not just committed.

### Custom gates

Projects add domain-specific enforcement by writing gate plugins. A gate is a Python class that implements the `GovernanceGate` interface:

```python
from groundtruth_kb.gates import GovernanceGate, GovernanceGateError

class MyCustomGate(GovernanceGate):
    def name(self) -> str:
        return "My Custom Gate"

    def pre_promote(self, spec_id, current_status, target_status, spec_data):
        if target_status == "verified" and not some_condition(spec_data):
            raise GovernanceGateError(f"Cannot verify {spec_id}: condition not met")
```

Gates are registered via `groundtruth.toml`:

```toml
[gates]
plugins = ["my_project.gates:MyCustomGate"]

[gates.config.MyCustomGate]
# Gate-specific configuration here
```

### Gate hooks

Gates can implement three hooks:

| Hook | When it runs | Use case |
|------|-------------|----------|
| `pre_promote` | Before a spec status promotion | Enforce evidence requirements for verification |
| `pre_resolve_work_item` | Before a work item is resolved | Require approvals for certain work item types |
| `pre_test_pass` | Before a test is marked as "pass" | Require executable test files for certain specs |

Each hook can block the transition by raising `GovernanceGateError`. Hooks that return without raising are treated as passing.

## Assertions

Assertions are the continuous monitoring layer. Where gates enforce rules at transition points, assertions check the codebase at any time.

### Assertion types

| Type | Check | Example |
|------|-------|---------|
| `grep` | Pattern exists in file | "rate_limit" appears in config.py |
| `glob` | File exists | tests/test_auth.py is present |
| `grep_absent` | Pattern does NOT exist in file | No hardcoded API keys in source |

### When assertions run

- **Session start**: automatic check of all assertions on implemented/verified specs
- **Pre-build**: gate check before container builds
- **On demand**: `gt assert` from the CLI or triggered by scripts

### Interpreting results

- **Passing assertion on "specified" spec**: expected — the spec is not yet implemented
- **Failing assertion on "specified" spec**: expected — implementation doesn't exist yet
- **Passing assertion on "implemented" spec**: good — implementation matches the spec
- **Failing assertion on "implemented" or "verified" spec**: **regression** — something that was working has broken

Regressions are the critical signal. They mean the codebase has drifted from the agreed specifications and need immediate investigation.

## Protected behaviors

Protected behaviors (`PB-*`) are a special class of governance specification for critical system invariants. They carry assertions that run before every build, acting as a regression gate.

Use protected behaviors for safety-critical constraints that must never silently regress: authentication requirements, data isolation guarantees, rate limiting enforcement, credential handling rules.

The difference from regular governance: regular GOV specs describe process rules (how to work). Protected behaviors describe system invariants (what must always be true about the running system).
