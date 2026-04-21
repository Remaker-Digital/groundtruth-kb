# NO-GO - GT-KB Adoption Gap Closure Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-adoption-gap-closure-001.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `31fe2c4833170127e52ed905b528627b4e00234d`
**Review type:** Loyal Opposition proposal review, not implementation verification

## Summary

The adoption-gap objective is valid, but this plan should not be approved as written. Several current-state claims are materially stale relative to the target checkout, and the highest-risk phase (`G2`) conflicts with the repository's current bridge reliability contract unless the owner explicitly changes that contract. `G4` also imports zero-knowledge and multi-tenant scope without enough product boundary, generated-file inventory, or owner depth decision to approve safely.

This is a proposal-baseline NO-GO, not a rejection of the overall goal. A revised plan should be evidence-accurate against `31fe2c4`, split lower-risk doc/CI cleanup from bridge-runtime and advanced-architecture decisions, and preserve the alpha/developer-preview posture until external validation proves otherwise.

## Prior Deliberations

Required deliberation search was run before review from the Agent Red KB:

- `python -m groundtruth_kb deliberations search "groundtruth-kb mass adoption bridge scheduler CI templates second customer"` returned `DELIB-0211`, `DELIB-0472`, `DELIB-0184`, `DELIB-0601`, and `DELIB-0229`.
- `python -m groundtruth_kb deliberations search "GroundTruth KB init posture token posture SPEC-GTKB-SCOPE"` returned `DELIB-GTKB-TOKEN-POSTURE` among the top matches.
- `python -m groundtruth_kb deliberations search "zero knowledge multi tenant scaffold GroundTruth KB"` returned `DELIB-0474` and `DELIB-0633` among the top matches.

Relevant prior decisions:

- `DELIB-GTKB-INIT-POSTURE`: owner decision keeps `gt init` as Layer 1 and makes `gt project init` the mass-adoption scaffold entry point.
- `DELIB-GTKB-TOKEN-POSTURE`: owner decision forbids GT-KB token management; GT-KB may provide auth troubleshooting docs and doctor pointers only.
- `DELIB-0474`: staged GroundTruth execution plan requires productized, gated scaffold/doctor/bridge work, external validation, and no hidden Agent Red assumptions.
- `DELIB-0633`: GroundTruth-KB is "promising but still alpha", not a validated multi-project platform.
- `bridge/gtkb-mass-adoption-readiness-012.md`: prior MVP was VERIFIED, landing bridge INDEX scaffolding, provider templates, doctor accuracy, and bridge rule templates.

## Findings

### Finding 1 - P1: The gap baseline is stale for docs, CI, and example-project evidence

**Claim in proposal:** G1 says there is "no adopter documentation"; G3 says GitHub CI is "not templated" and `gt project init` does not generate CI workflows; G5 says Agent Red is the only project.

**Evidence:**

- Documentation already has a Getting Started nav section with `User Journey` and `Start Here` in `groundtruth-kb/mkdocs.yml:54-56`, and a Task Tracker example in `groundtruth-kb/mkdocs.yml:80`.
- `groundtruth-kb/docs/start-here.md:72` says default `gt project init` includes example specs/tests and GitHub Actions workflows; `groundtruth-kb/docs/start-here.md:240` says CI workflows are included automatically unless `--no-include-ci` is passed.
- `groundtruth-kb/docs/bootstrap.md:1` is an existing "Getting Started with groundtruth-kb" guide, though `groundtruth-kb/docs/bootstrap.md:12` still references Agent Red deployment topology and needs cleanup.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:92-94` copies CI templates when `include_ci` or profile defaults require them.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:322-328` copies every `templates/ci/*.yml` file into `.github/workflows/`.
- `groundtruth-kb/docs/reference/templates.md:50-52` documents `templates/ci/build.yml`, `deploy.yml`, and `test.yml` as workflow templates.
- `groundtruth-kb/examples/task-tracker/WALKTHROUGH.md:1-5` is an existing non-Agent-Red example covering specs, tests, governance, review cycle, CI/CD, and web UI.
- Verification command: `python -m pytest tests/test_scaffold_project.py tests/test_scaffold_smoke.py tests/test_doctor_bridge_accuracy.py tests/test_scaffold_bridge_index.py tests/test_scaffold_bridge_rules.py -q --tb=short -p no:cacheprovider` returned `37 passed`.
- Verification command: `python -m pytest tests/test_cli.py::TestBootstrapDesktop -q --tb=short -p no:cacheprovider` returned `3 passed`.
- Verification command: `python -m mkdocs build --strict --site-dir "$env:TEMP\gtkb_mkdocs_bridge_review"` exited `0` and built the docs.

**Risk/impact:**

Approving implementation from a false baseline will duplicate or replace existing surfaces instead of closing the real gaps. The real issue is not "nothing exists"; it is that existing docs/templates/examples are incomplete, still contain some Agent Red references, and may not prove a new developer can self-serve.

**Required action:**

Revise the G1/G3/G5 gap table to distinguish "absent" from "present but insufficient". For CI, specify the delta from current `templates/ci/*.yml` behavior instead of creating a parallel template system from scratch. For G5, decide whether the existing `examples/task-tracker` should become the second-customer proof, or whether the proof must be a separate repo/project outside the GT-KB source tree.

### Finding 2 - P1: G2 conflicts with the current bridge reliability contract

**Claim in proposal:** G2 will add `gt bridge start/status/stop` as a cross-platform Python scheduler using stdlib `sched`, foreground process semantics, status JSON files named `claude-scan-status.json` and `codex-scan-status.json`, and a stop sentinel.

**Evidence:**

- Current docs make the OS scheduler the reliability boundary: `groundtruth-kb/docs/method/12-file-bridge-automation.md:50`, `:116`, `:251`, and `:264`.
- The generated bridge setup prompt says to poll from the OS scheduler, not manual prompting or app-native automation, in `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md:42-43`, and stores poller artifacts under project-owned paths at `:53`.
- `groundtruth-kb/templates/rules/bridge-essential.md:14` explicitly says bridge scheduler commands are not implemented in this release.
- `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py:5-7`, `poller.py:4-5`, and `worker.py:4-5` describe the packaged bridge runtime as legacy and direct new dual-agent projects to project-owned file bridge OS pollers.
- `python -m groundtruth_kb --help` listed command groups but no `bridge` command group.
- `rg -n 'claude-scan-status|codex-scan-status|poller-freshness|scan-status' src docs templates tests README.md` returned no matches in the target checkout.
- Current doctor checks bridge file presence only: `groundtruth-kb/src/groundtruth_kb/project/doctor.py:487-537`; it does not check scheduler freshness or parse scan-status JSON.
- `DELIB-GTKB-TOKEN-POSTURE` allows auth troubleshooting docs and doctor pointers, but no token management.

**Risk/impact:**

This phase may accidentally replace a deliberate project-owned OS-poller contract with a package-owned foreground loop. That changes the bridge reliability model, ownership boundary, generated docs, doctor semantics, and failure model. It also proposes status-file compatibility with names that are not present in this checkout, so the implementation target is not yet anchored.

**Required action:**

Either revise G2 to preserve the current OS-scheduler contract, or get an explicit owner decision that `gt bridge start` is now the desired reliability boundary. A revised G2 must specify: index parser rules, lock semantics, dispatch command contract for Prime/Codex, status JSON schema and file locations, stop behavior, interaction with project-owned pollers, and doctor/freshness acceptance tests. It must also state that auth handling remains documentation-only per `DELIB-GTKB-TOKEN-POSTURE`.

### Finding 3 - P1: G4 is underspecified and over-bundled with app-specific architecture

**Claim in proposal:** G4 will add `zero-knowledge` and `multi-tenant` profiles and generate working Azure Terraform plus tenant isolation/key-management/API patterns based on Agent Red.

**Evidence:**

- Current CLI profile surface only supports `local-only`, `dual-agent`, and `dual-agent-webapp`; verified by `python -m groundtruth_kb project init --help`.
- `groundtruth-kb/src/groundtruth_kb/project/profiles.py:24-59` defines only those three profiles.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:553-556` currently writes provider stubs only, and `groundtruth-kb/tests/test_scaffold_smoke.py:145-151` asserts the Azure Terraform output contains `# stub`.
- `rg -n 'zero-knowledge|zero knowledge|BL-ZK|multi-tenant|multi tenant' src\groundtruth_kb docs templates tests examples README.md pyproject.toml` found no implemented ZK scaffold/spec surface in `src/groundtruth_kb`; only user-journey/example references and Terraform stub tests.
- `DELIB-0474` warns that Agent Red is a behavioral reference, not the literal distributable artifact, and requires productized staging/cloud work behind explicit gates.

**Risk/impact:**

This bundles advanced cloud, crypto, and multi-tenant application architecture into the same approval as docs/CI/adoption cleanup. It risks copying Agent Red-specific application patterns into a generic toolkit and risks overclaiming "zero-knowledge" by scaffolding security-sensitive placeholders that users may mistake for working cryptographic architecture.

**Required action:**

Move G4 into a separate bridge proposal or explicitly mark it out of scope for the adoption-gap closure critical path. A future G4 proposal needs an exact generated-file inventory, profile names, cloud-provider scope, Terraform validation plan, security disclaimers, and owner decision on scaffold depth. The default should be documented patterns and safe placeholders, not working crypto or direct Agent Red code transfer.

### Finding 4 - P2: The success criteria overclaim mass-adoption readiness before beta/field validation

**Claim in proposal:** After G1/G2/G3/G5, GroundTruth-KB can be considered ready for mass adoption; G4 is optional.

**Evidence:**

- `groundtruth-kb/pyproject.toml:17` still classifies the package as `Development Status :: 3 - Alpha`.
- `groundtruth-kb/docs/changelog.md:80-83` says v0.4.0 remains alpha and does not claim production readiness for the full dual-agent, scaffold, or bridge runtime surface.
- `DELIB-0633` explicitly concludes that GroundTruth-KB is not yet proven as a repeatable software-factory system across projects and supports a "promising but still alpha" verdict.
- `bridge/gtkb-production-readiness-002.md:128-129` previously required beta-first posture, explicit cross-platform/release evidence, and a real field trial before stable claims.

**Risk/impact:**

Even if the proposed phases land, calling the package "ready for mass adoption" can exceed the evidence. The second-customer validation is the proof step, not a box to check before a readiness claim.

**Required action:**

Change the readiness language to "developer preview" or "beta candidate" until a field trial proves the flow from a release artifact in a fresh project. G5 must specify the install artifact, operating systems, time-to-green-doctor target, bridge proof, CI proof, friction report format, and criteria for accepting or rejecting the field trial.

### Finding 5 - P2: Template-engine dependency handling is incomplete

**Claim in proposal:** G3 adds Jinja2 because workflow templates need conditionals.

**Evidence:**

- Base install currently has only `click>=8.1` as a required dependency in `groundtruth-kb/pyproject.toml:26-28`.
- Jinja2 already exists as an optional `web` dependency at `groundtruth-kb/pyproject.toml:30-35`, not as a base CLI dependency.
- Current scaffold rendering uses simple placeholder replacement across renderable files in `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:334-425`.

**Risk/impact:**

Adding Jinja2 to the base CLI path changes the package dependency posture for all adopters. Keeping it optional while using it in `gt project init` would break base installs. Neither choice is unacceptable, but the proposal does not acknowledge the dependency boundary.

**Required action:**

Decide explicitly whether G3 moves Jinja2 into base dependencies, uses stdlib templating, or gates richer templates behind an extra. Add base-install smoke tests for `gt project init` after the decision.

## Conditions for a Revised GO

A revised proposal can be approved if it:

1. Re-baselines every gap against `groundtruth-kb` commit `31fe2c4`, with "exists but insufficient" called out separately from "absent".
2. Splits advanced G4 architecture work from the adoption-critical docs/bridge/CI/field-trial path, or includes a narrow owner-approved G4 scope.
3. Reconciles G2 with the current OS-scheduler bridge contract or obtains an explicit owner decision to replace that contract with package-owned `gt bridge` commands.
4. Defines exact deltas for existing docs, CI templates, examples, and doctor checks instead of proposing duplicate surfaces.
5. Keeps auth token handling documentation-only.
6. Keeps public readiness language at alpha/developer-preview or beta-candidate until second-customer field validation is complete.

## Verification Commands Run

- `git rev-parse HEAD` in `groundtruth-kb` -> `31fe2c4833170127e52ed905b528627b4e00234d`
- `git log --oneline -5` confirmed `31fe2c4` follows MVP commit `12fd083`.
- `python -m groundtruth_kb --help` -> no `gt bridge` group.
- `python -m groundtruth_kb project init --help` -> profiles are `local-only`, `dual-agent`, `dual-agent-webapp`.
- `python -m pytest tests/test_scaffold_project.py tests/test_scaffold_smoke.py tests/test_doctor_bridge_accuracy.py tests/test_scaffold_bridge_index.py tests/test_scaffold_bridge_rules.py -q --tb=short -p no:cacheprovider` -> `37 passed`.
- `python -m pytest tests/test_cli.py::TestBootstrapDesktop -q --tb=short -p no:cacheprovider` -> `3 passed`.
- `python -m mkdocs build --strict --site-dir "$env:TEMP\gtkb_mkdocs_bridge_review"` -> exit `0`.
