# Contributing to GroundTruth KB

Thanks for your interest in GT-KB. This repository builds the GT-KB platform
itself, and it is developed *using* the platform's own governance model — so
contributing here means working through that model.

## The contribution model in one paragraph

GT-KB is **specification-driven** and **review-gated**. Changes do not start as
code; they start as a specification and an implementation proposal. A **Prime
Builder** agent drafts the proposal and, after review, implements it. A **Loyal
Opposition** agent independently reviews every proposal (`GO` / `NO-GO`) and
verifies every implementation against its linked specifications (`VERIFIED`).
Nothing is "done" until specification-derived tests have actually run.

The coordination surface is the **file bridge**: versioned markdown files under
[`bridge/`](bridge/) with [`bridge/INDEX.md`](bridge/INDEX.md) as canonical
state. See [`.claude/rules/file-bridge-protocol.md`](.claude/rules/file-bridge-protocol.md)
for the full protocol.

## Development setup

GT-KB targets **Python 3.12+**.

```sh
git clone https://github.com/Remaker-Digital/groundtruth-kb.git
cd groundtruth-kb

# Create and populate a virtual environment for the package
python -m venv groundtruth-kb/.venv
groundtruth-kb/.venv/Scripts/python -m pip install -e groundtruth-kb   # Windows
# groundtruth-kb/.venv/bin/python -m pip install -e groundtruth-kb     # macOS/Linux
```

## Before you open a change

Run the same gates CI and the pre-commit hook enforce:

```sh
python -m ruff check .
python -m ruff format --check .
python -m pytest -q --tb=short
```

Code quality conventions live in [`pyproject.toml`](pyproject.toml) (`ruff`
config, line length 120, `py312` target). The pre-commit hook additionally runs
a redacted secret scan, dev-environment inventory-drift checks, and
narrative-artifact evidence checks — **do not bypass commit hooks**; fix the
underlying issue.

## Proposing a change

1. **Specify first.** Capture the requirement as a specification before writing
   code. Owner-articulated requirements become specifications through the
   governed approval path, not silently.
2. **Propose via the bridge.** File an implementation proposal under `bridge/`
   that cites the governing specifications and the tests that will prove it.
3. **Get a `GO`.** Loyal Opposition reviews the proposal. Address `NO-GO`
   findings and revise.
4. **Implement and verify.** Implement the approved proposal, then file a report;
   verification runs the specification-derived tests and records `VERIFIED`.

Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`, …).

## Where to go next

- **Package-level contributor guide:** [`groundtruth-kb/CONTRIBUTING.md`](groundtruth-kb/CONTRIBUTING.md)
- **New-adopter walkthrough:** [`groundtruth-kb/docs/start-here.md`](groundtruth-kb/docs/start-here.md)
- **Harness governance & roles:** [`AGENTS.md`](AGENTS.md), [`.claude/rules/`](.claude/rules/)
- **Security policy:** [`SECURITY.md`](SECURITY.md)

## License of contributions

Contributions to the published package under [`groundtruth-kb/`](groundtruth-kb/)
are made under **AGPL-3.0-or-later** (see [`groundtruth-kb/LICENSE`](groundtruth-kb/LICENSE)).
The repository root carries a separate proprietary [`LICENSE`](LICENSE); for
contributions outside `groundtruth-kb/`, consult both files or contact the
maintainer via the [project repository](https://github.com/Remaker-Digital/groundtruth-kb).
