# Contributing to GroundTruth Knowledge DB

Thank you for your interest in improving GroundTruth. This project is a
specification-driven governance toolkit for AI engineering teams, and your
feedback directly improves the method behind it.

## What kind of feedback is most valuable?

We use this project as a **feedback instrument**. The most valuable
contributions tell us where the method works, where it fails, and where
it needs to grow.

### High-signal contributions

- **Bug reports** with reproduction steps — these reveal method failures.
  Use the [Bug Report](https://github.com/Remaker-Digital/groundtruth-kb/issues/new?template=bug_report.yml) template.

- **Feature requests** that describe the problem, not just the solution.
  Use the [Feature Request](https://github.com/Remaker-Digital/groundtruth-kb/issues/new?template=feature_request.yml) template.

- **Pull requests** with clear problem/approach/rationale.
  See the PR template for the expected structure.

- **Questions** about how the method works or why a decision was made.
  Open a [Discussion](https://github.com/Remaker-Digital/groundtruth-kb/discussions).

### The `method-feedback` label

Issues and PRs that reveal something about the engineering method itself
(not just a code bug) are tagged with **`method-feedback`**. This label
is triaged monthly and may result in changes to both the toolkit and the
method it implements.

## Development setup

```bash
git clone https://github.com/Remaker-Digital/groundtruth-kb.git
cd groundtruth-kb
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev,web]"
make check  # lint + format-check + test
```

## Code style

- Python 3.11+
- Format with `ruff format` (or `make format`)
- Lint with `ruff check` (or `make lint`)
- Type hints encouraged but not required
- Docstrings for public APIs

## License

By contributing, you agree that your contributions will be licensed under
the [AGPL-3.0 License](https://github.com/Remaker-Digital/groundtruth-kb/blob/main/LICENSE).
