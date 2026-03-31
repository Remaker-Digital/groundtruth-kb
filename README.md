# GroundTruth Knowledge DB

A specification-driven governance toolkit for AI engineering teams.

Track specifications, tests, work items, and architecture decisions with
append-only versioning. Built for teams that need traceable, auditable
engineering decisions.

## What is this?

GroundTruth implements a method for managing AI system quality:

1. **Specifications** describe what the system must do (decision log, not build spec)
2. **Tests** verify that the implementation meets the specifications
3. **Work items** track the gap between specs and implementation
4. **Architecture decisions** (ADRs) record cross-cutting technical choices
5. **Assertions** continuously verify that specs and implementation stay aligned

Everything is stored in an append-only SQLite database with full version
history. No UPDATE, no DELETE — every change is a new version.

## Quick start

```bash
pip install groundtruth-kb

# Initialize a new project
groundtruth init

# Open the web UI
groundtruth serve
# Visit http://localhost:8090
```

## Why?

AI-powered systems change fast. Without traceable specifications and
assertions, teams lose track of what was decided, why, and whether the
implementation still matches. GroundTruth provides the engineering
discipline layer.

## Status

This project is in early development. The toolkit is extracted from a
production system where it has managed 2,000+ specifications and 11,000+
tests. The extraction and packaging for standalone use is in progress.

## Documentation

The [method documentation](docs/method/README.md) describes the engineering discipline behind GroundTruth:

- [Method Overview](docs/method/01-overview.md) — what GroundTruth is, core workflow, governance model
- [Specifications](docs/method/02-specifications.md) — writing and managing specifications
- [Adoption & Promotion](docs/method/09-adoption.md) — upstream/downstream model, update procedures

More guides (testing, work items, governance, sessions, architecture) are coming soon.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute. We
especially value feedback about the engineering method itself — tag
issues with `method-feedback`.

## License

[AGPL-3.0](LICENSE)
