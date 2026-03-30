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

If you think your contribution affects the method, add this label yourself
or mention it in the description.

## Development setup

```bash
# Clone the repository
git clone https://github.com/Remaker-Digital/groundtruth-kb.git
cd groundtruth-kb

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format --check .
```

## Making changes

1. Fork the repository and create a branch from `main`.
2. Make your changes with tests.
3. Run `pytest` and `ruff check .` to verify.
4. Submit a pull request using the PR template.

## Code style

- Python 3.11+
- Format with `ruff format`
- Lint with `ruff check`
- Type hints encouraged but not required
- Docstrings for public APIs

## Monthly triage process

On the first Monday of each month, maintainers review all items tagged
`method-feedback` and:

1. Classify each as: actionable (create work item), informational (note
   and close), or needs-discussion (move to Discussions).
2. Actionable items become specifications or work items in the toolkit.
3. A brief triage summary is posted as a Discussion.

## License

By contributing, you agree that your contributions will be licensed under
the [AGPL-3.0 License](LICENSE).
