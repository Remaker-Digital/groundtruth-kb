# Assertion Format Reference (GOV-18)

Every spec SHOULD include at least one machine-verifiable assertion. Assertions must be **meaningful** — no rubber-stamp assertions (GOV-18).

## Format

```python
assertions = [
    {
        "description": "Human-readable description of what is verified",
        "type": "grep",           # grep, http, python, exists
        "target": "src/path.py",  # File path, URL, or script
        "pattern": "search_term", # What to look for
        "min_count": 1            # Minimum occurrences
    }
]
```

## Assertion Types

| Type | Target | Pattern | Checks |
|------|--------|---------|--------|
| `grep` | File path | Regex/string | Pattern found >= min_count times |
| `exists` | File path | — | File exists on disk |
| `http` | URL | Status code | HTTP response matches expected |
| `python` | Script path | — | Script exits 0 |

## Good Assertion Examples

```python
# Verifies specific behavior is wired
{"description": "Rate limit middleware applied to all API routes",
 "type": "grep", "target": "src/main.py", "pattern": "RateLimitMiddleware", "min_count": 1}

# Verifies a function exists with specific logic
{"description": "Escalation handler classifies into 6 categories",
 "type": "grep", "target": "src/agents/escalation_handler.py",
 "pattern": "escalation_category", "min_count": 3}

# Verifies a config value
{"description": "Default rate limit is 300 RPM",
 "type": "grep", "target": "src/multi_tenant/cosmos_schema.py",
 "pattern": "RATE_LIMIT_RPM_DEFAULT = 300", "min_count": 1}
```

## Bad Assertion Examples (rubber-stamp — GOV-18 violation)

```python
# Too vague — proves nothing about behavior
{"description": "File exists", "type": "exists", "target": "src/main.py"}

# Meaningless string match
{"description": "Import exists", "type": "grep", "target": "src/foo.py", "pattern": "import", "min_count": 1}
```

## Spec Types Reference

| Type | ID Pattern | Purpose |
|------|-----------|---------|
| `requirement` | SPEC-NNNN | Standard functional/non-functional requirement |
| `governance` | GOV-NN | Process rules (stored as specs with type=governance) |
| `protected_behavior` | PB-XXX | Machine-verifiable behaviors that must never be removed |
