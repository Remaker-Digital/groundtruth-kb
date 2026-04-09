# Contributing to Agent Red Customer Experience

Thank you for your interest in Agent Red. This document describes our
development practices and contribution guidelines.

## Development Process

Agent Red follows a specification-first development methodology:

1. **Specification** — Requirements are documented and approved before
   implementation begins.
2. **Work Items** — Implementation tasks are created from specifications
   and prioritized in the backlog.
3. **Test Creation** — Tests are written alongside or before implementation
   to verify specification compliance.
4. **Implementation** — Code changes follow the approved specification.
5. **Review** — All changes go through code review before merge.
6. **Verification** — Tests must pass before deployment.

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production mirror. Always matches the current production deployment. |
| `develop` | Active development. All new features and fixes land here. |

- All work happens on `develop`.
- Never commit directly to `main`.
- Merge to `main` only as part of a production deployment.

## Code Standards

- **Python**: Formatted and linted with [ruff](https://docs.astral.sh/ruff/)
  (see `pyproject.toml` for rules).
- **TypeScript/React**: Standard ESLint + Prettier configuration.
- **Copyright**: All new files must include the copyright header:
  ```
  # © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
  ```
- **Tests**: Every feature requires corresponding tests. Coverage gate: 75%+.
- **Commits**: Concise, descriptive messages. Reference work item IDs when
  applicable.

## Reporting Issues

Use [GitHub Issues](https://github.com/mike-remakerdigital/agent-red/issues)
with the provided issue templates. Include:

- Clear description of the problem or feature request
- Steps to reproduce (for bugs)
- Expected vs. actual behavior
- Environment details (browser, OS, tenant tier)

## Security Vulnerabilities

Do **not** open public issues for security vulnerabilities. Instead, follow
the responsible disclosure process in [SECURITY.md](SECURITY.md).

## License

This is proprietary software. See [LICENSE](LICENSE) for details. By
contributing, you agree that your contributions become the property of
Remaker Digital.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
