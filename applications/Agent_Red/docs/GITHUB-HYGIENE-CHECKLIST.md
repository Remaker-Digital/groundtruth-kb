# GitHub Hygiene Checklist

Reusable checklist for periodic repository hygiene sessions. Run this checklist after major milestones, at least monthly, or before any external-facing review.

**Last run:** 2026-04-07 (S267)

---

## 1. CI/CD Health

- [ ] All GitHub Actions workflows passing on `main`
  ```bash
  gh run list --branch main --limit 8 --json name,conclusion
  ```
- [ ] All GitHub Actions workflows passing on `develop`
  ```bash
  gh run list --branch develop --limit 8 --json name,conclusion
  ```
- [ ] No deprecated actions or pinned-to-old-version actions
- [ ] Dependency vulnerability scan (pip-audit) passing
- [ ] CI runs in reasonable time (<10 min for full test suite)

## 2. Branch Hygiene

- [ ] `main` matches current production deployment
  ```bash
  git log --oneline main -1  # Should show production version
  ```
- [ ] `develop` is the active working branch
  ```bash
  git branch --show-current  # Should be develop
  ```
- [ ] No stale feature branches
  ```bash
  git branch -a | grep -v "main\|develop\|gh-pages\|HEAD"
  ```
- [ ] Branch protection enabled on both `main` and `develop`
  ```bash
  gh api repos/{owner}/{repo}/branches/main/protection --jq '.required_status_checks.contexts'
  gh api repos/{owner}/{repo}/branches/develop/protection --jq '.required_status_checks.contexts'
  ```

## 3. Releases & Tags

- [ ] GitHub Release exists for current production version
  ```bash
  gh release list
  ```
- [ ] Release notes are accurate and complete
- [ ] Version tags match deployed versions

## 4. Issues & Project Tracking

- [ ] No stale open issues (>60 days without activity)
  ```bash
  gh issue list --state open --json number,title,updatedAt
  ```
- [ ] All open issues have labels
- [ ] Closed issues have closing comments explaining resolution
- [ ] Issue templates are functional (bug report, feature request)

## 5. Repository Metadata

- [ ] Description is current and accurate
  ```bash
  gh repo view --json description --jq .description
  ```
- [ ] Topics reflect current tech stack
  ```bash
  gh repo view --json repositoryTopics --jq '.repositoryTopics[].name'
  ```
- [ ] Homepage URL is valid and accessible
- [ ] README.md reflects current architecture, test counts, and project state

## 6. Wiki

- [ ] Home page shows current production version
- [ ] Project-Status page is current
- [ ] Changelog includes all recent releases
- [ ] No obviously stale pages with outdated version numbers in key navigation paths

## 7. Security

- [ ] SECURITY.md exists with contact info and response timeline
- [ ] No secrets, credentials, or API keys in repository
  ```bash
  git log --all --diff-filter=A -- '*.env' '*.key' '*.pem' '*secret*'
  ```
- [ ] .gitignore covers all sensitive patterns (.env, credentials, keys)
- [ ] Dependency vulnerability scan passing (pip-audit)
- [ ] No hardcoded connection strings or tokens

## 8. Documentation

- [ ] README.md is current (architecture, tests, infrastructure)
- [ ] PR template exists and is useful
- [ ] SECURITY.md exists
- [ ] Legal documents are present (ToS, Privacy, SLA, DPA)
- [ ] API documentation is accessible (Swagger/OpenAPI)

## 9. Working Tree Cleanliness

- [ ] No unexpected untracked files
  ```bash
  git status --porcelain -u | grep "^??" | head -20
  ```
- [ ] .gitignore covers ephemeral artifacts (playwright snapshots, pre-flight results, build outputs)
- [ ] No large binary files committed that should be in .gitignore

## 10. Code Quality Signals

- [ ] Linting passes (ruff for Python, ESLint for TypeScript)
- [ ] Test coverage meets gate (75%+)
- [ ] No import cycles detected
- [ ] No critical/high Dependabot alerts (if enabled)

---

## Quick Run Command

Run all verification commands at once:

```bash
echo "=== CI (main) ===" && gh run list --branch main --limit 5 --json name,conclusion --jq '.[] | "\(.name): \(.conclusion)"'
echo "=== CI (develop) ===" && gh run list --branch develop --limit 5 --json name,conclusion --jq '.[] | "\(.name): \(.conclusion)"'
echo "=== Branches ===" && git branch -a
echo "=== Releases ===" && gh release list
echo "=== Open Issues ===" && gh issue list --state open --json number,title --jq '.[] | "#\(.number) \(.title)"'
echo "=== Untracked ===" && git status --porcelain -u | grep "^??" | head -10
echo "=== Description ===" && gh repo view --json description --jq .description
echo "=== Topics ===" && gh repo view --json repositoryTopics --jq '.repositoryTopics[].name' | tr '\n' ', '
```

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
