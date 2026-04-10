# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in groundtruth-kb, please report it
responsibly. **Do not open a public issue.**

### How to Report

1. **Email:** Send details to dev@remakerdigital.com
2. **GitHub Security Advisory:** Open a private advisory at
   https://github.com/Remaker-Digital/groundtruth-kb/security/advisories/new

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Impact assessment (if known)

### Response Timeline

- **48 hours:** Acknowledgment of your report
- **14 days:** Initial assessment and severity classification
- **90 days:** Fix released or public disclosure (whichever comes first)

### Scope

The following are in scope for security reports:

- Core Python source (`src/groundtruth_kb/`)
- Governance gates and assertion engine
- Web UI and API endpoints
- Bridge runtime message handling
- Template hooks (credential-scan, destructive-gate)

The following are **out of scope:**

- User-generated scaffolded project files
- Example project code (`examples/`)
- Documentation content

## Disclosure Policy

We follow coordinated disclosure. After a fix is released, we will publish
a security advisory on GitHub with credit to the reporter (unless anonymity
is requested).
