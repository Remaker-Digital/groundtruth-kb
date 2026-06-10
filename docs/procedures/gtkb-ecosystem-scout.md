# Procedure: GT-KB Ecosystem Scout

This procedure describes how to perform periodic scouting, classification, and analysis of public GitHub projects relevant to AI coding harness capabilities.

## 1. Search Routine

To identify potential candidates for capability enhancement, follow this search routine:
1. Search GitHub and package registries (PyPI, npm, etc.) for projects related to agentic coding, MCP servers, harness automation, and project telemetry.
2. Review trending repositories and issues in relevant coding harness repositories.
3. Identify candidates that can add value to the GT-KB platform.

## 2. Classification Taxonomy

Each candidate identified during the search must be classified into one of the following five categories:
- **adopt**: Use the package directly as a dependency without changes, provided licensing and security checks pass.
- **adapt**: Fork the repository or copy the code to adapt it to GT-KB's specific conventions and architecture.
- **reject**: Do not use the package due to incompatibilities, hostile licenses, security issues, or architectural mismatch.
- **defer**: Put off consideration to a future session or work item.
- **monitor**: Watch the project for future updates or maturity.

## 3. Analysis and Security

> [!WARNING]
> NEVER install or execute unverified third-party scripts or packages on the host system. All candidates must undergo static analysis and manual verification in isolated sandboxes.

Before adoption:
- Analyze license compatibility (e.g., AGPL-3.0 compatibility, permissive licenses like MIT/Apache-2.0).
- Check the project provenance (author history, active maintainers, repository health).
- Review security issues and audit dependencies.
