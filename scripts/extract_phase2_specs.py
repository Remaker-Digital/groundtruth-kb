"""
Phase 2 Specification Extractor — reads source code and generates spec JSON.

Extracts testable specifications from:
- Admin UI pages (TSX) → specs-batch-2a.json
- Config + API layer (Python) → specs-batch-2b.json
- Widget + Auth + Email → specs-batch-2c.json (already exists from agent)
- Backend infrastructure → specs-batch-2d.json
- Agents + Testing + Ops → specs-batch-2e.json

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import json
import os
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.parent
DOCS = BASE / "docs"


def read_file(relpath: str) -> str:
    """Read a source file relative to project root."""
    p = BASE / relpath
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


# ─────────────────────────────────────────────────────────────
# Area 2a: Admin UI Pages (TSX)
# ─────────────────────────────────────────────────────────────
def extract_2a() -> list[dict]:
    """Extract specs from Admin UI TSX pages."""
    specs = []
    pages_dir = BASE / "admin" / "standalone" / "pages"
    components_dir = BASE / "admin" / "standalone" / "components"

    # Process each TSX file in pages/
    for tsx_file in sorted(pages_dir.glob("*.tsx")):
        content = tsx_file.read_text(encoding="utf-8", errors="replace")
        page_name = tsx_file.stem
        relpath = str(tsx_file.relative_to(BASE)).replace("\\", "/")

        # Extract component names
        for m in re.finditer(r'<(SectionHeader|HelpTooltip)[^>]*label=["\']([^"\']+)["\']', content):
            specs.append({
                "title": f"{page_name} has '{m.group(2)}' section header",
                "section": "ADMIN_UI",
                "tags": [page_name, "section-header"],
                "source_file": relpath,
            })

        # Extract TextInput/Textarea labels
        for m in re.finditer(r'<(?:TextInput|Textarea|NumberInput|Select)\s[^>]*label=["\{](?:["\'])?([^"\'}\)]+)', content):
            label = m.group(1).strip()
            if label and len(label) < 80:
                specs.append({
                    "title": f"{page_name} has '{label}' input field",
                    "section": "ADMIN_UI",
                    "tags": [page_name, "form-field"],
                    "source_file": relpath,
                })

        # Extract Switch components
        for m in re.finditer(r'<Switch\s[^>]*label=["\{](?:["\'])?([^"\'}\)]+)', content):
            label = m.group(1).strip()
            if label and len(label) < 80:
                specs.append({
                    "title": f"{page_name} has '{label}' toggle switch",
                    "section": "ADMIN_UI",
                    "tags": [page_name, "switch"],
                    "source_file": relpath,
                })

        # Extract Button labels
        for m in re.finditer(r'<Button[^>]*>([^<]{3,50})</Button>', content):
            label = m.group(1).strip()
            if label and not label.startswith('{'):
                specs.append({
                    "title": f"{page_name} has '{label}' button",
                    "section": "ADMIN_UI",
                    "tags": [page_name, "button"],
                    "source_file": relpath,
                })

        # Extract page title from first heading or title prop
        for m in re.finditer(r'<Title[^>]*>([^<]+)</Title>|pageTitle=["\']([^"\']+)["\']', content):
            title = m.group(1) or m.group(2)
            if title:
                specs.append({
                    "title": f"{page_name} page title is '{title.strip()}'",
                    "section": "ADMIN_UI",
                    "tags": [page_name, "page-title"],
                    "source_file": relpath,
                })

        # Extract SegmentedControl options
        for m in re.finditer(r'<SegmentedControl[^>]*data=\{?\[([^\]]+)\]', content):
            data_str = m.group(1)
            options = re.findall(r"['\"]([^'\"]+)['\"]", data_str)
            if options:
                specs.append({
                    "title": f"{page_name} SegmentedControl offers options: {', '.join(options[:6])}",
                    "section": "ADMIN_UI",
                    "tags": [page_name, "segmented-control"],
                    "source_file": relpath,
                })

        # Extract Tab labels
        for m in re.finditer(r"<Tabs\.Tab\s[^>]*value=['\"]([^'\"]+)['\"]", content):
            specs.append({
                "title": f"{page_name} has '{m.group(1)}' tab",
                "section": "ADMIN_UI",
                "tags": [page_name, "tabs"],
                "source_file": relpath,
            })

        # Extract NumberInput ranges
        for m in re.finditer(r'<NumberInput[^>]*min=\{?(\d+)\}?[^>]*max=\{?(\d+)\}?[^>]*label=["\']([^"\']+)["\']', content):
            specs.append({
                "title": f"{page_name} '{m.group(3)}' NumberInput ranges from {m.group(1)} to {m.group(2)}",
                "section": "ADMIN_UI",
                "tags": [page_name, "validation"],
                "source_file": relpath,
            })

        # Extract validation: maxLength / max_length
        for m in re.finditer(r'maxLength[=:]\s*(\d+)', content):
            specs.append({
                "title": f"{page_name} has input with maxLength {m.group(1)}",
                "section": "ADMIN_UI",
                "tags": [page_name, "validation"],
                "source_file": relpath,
            })

    # Process key components
    for tsx_file in sorted(components_dir.glob("*.tsx")):
        content = tsx_file.read_text(encoding="utf-8", errors="replace")
        comp_name = tsx_file.stem
        relpath = str(tsx_file.relative_to(BASE)).replace("\\", "/")

        # Extract exported component function
        for m in re.finditer(r'export\s+(?:default\s+)?function\s+(\w+)', content):
            specs.append({
                "title": f"{comp_name} component exports {m.group(1)} function",
                "section": "ADMIN_UI",
                "tags": [comp_name, "component"],
                "source_file": relpath,
            })

    return specs


# ─────────────────────────────────────────────────────────────
# Area 2b: Config + API Layer
# ─────────────────────────────────────────────────────────────
def extract_2b() -> list[dict]:
    """Extract specs from config and API files."""
    specs = []

    # --- fields.yaml ---
    yaml_path = "src/multi_tenant/schema/fields.yaml"
    yaml_content = read_file(yaml_path)
    field_count = yaml_content.count("field_name:")
    specs.append({
        "title": f"fields.yaml defines {field_count} field definitions",
        "section": "CONFIG",
        "tags": ["config", "fields-yaml"],
        "source_file": yaml_path,
    })

    # Extract individual fields
    for m in re.finditer(
        r'field_name:\s*(\w+)\s*\n\s*type:\s*(\w+)(?:.*?max_length:\s*(\d+))?(?:.*?tier_gate:\s*(\w+))?',
        yaml_content, re.DOTALL
    ):
        fname, ftype = m.group(1), m.group(2)
        maxlen = m.group(3) or ""
        tier = m.group(4) or "all"
        title = f"Field '{fname}' type={ftype}"
        if maxlen:
            title += f", max_length={maxlen}"
        title += f", tier_gate={tier}"
        specs.append({
            "title": title,
            "section": "CONFIG",
            "tags": ["config", fname],
            "source_file": yaml_path,
        })

    # --- cosmos_schema.py enums ---
    schema_content = read_file("src/multi_tenant/cosmos_schema.py")
    schema_path = "src/multi_tenant/cosmos_schema.py"

    for m in re.finditer(r'class (\w+)\(str,\s*Enum\):\s*\n((?:\s+\w+\s*=.*\n)+)', schema_content):
        enum_name = m.group(1)
        values = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', m.group(2))
        val_names = [v[0] for v in values]
        specs.append({
            "title": f"{enum_name} enum has {len(val_names)} values: {', '.join(val_names[:8])}",
            "section": "CONFIG",
            "tags": ["config", enum_name.lower()],
            "source_file": schema_path,
        })

    # --- Cosmos collections ---
    for m in re.finditer(r'"name":\s*"(\w+)".*?"partition_key":\s*"([^"]+)"', schema_content, re.DOTALL):
        specs.append({
            "title": f"Cosmos collection '{m.group(1)}' has partition_key '{m.group(2)}'",
            "section": "CONFIG",
            "tags": ["config", "cosmos-collection"],
            "source_file": schema_path,
        })

    # --- TTL constants ---
    for m in re.finditer(r'(TTL_\w+)\s*=\s*(\d+)', schema_content):
        specs.append({
            "title": f"Constant {m.group(1)} = {m.group(2)}",
            "section": "CONFIG",
            "tags": ["config", "ttl"],
            "source_file": schema_path,
        })

    # --- API endpoints from *_api.py files ---
    api_dir = BASE / "src" / "multi_tenant"
    for api_file in sorted(api_dir.glob("*_api.py")):
        content = api_file.read_text(encoding="utf-8", errors="replace")
        relpath = str(api_file.relative_to(BASE)).replace("\\", "/")
        module = api_file.stem

        # Extract route decorators
        for m in re.finditer(
            r'@router\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']',
            content
        ):
            method = m.group(1).upper()
            path = m.group(2)
            specs.append({
                "title": f"{method} {path} endpoint in {module}",
                "section": "API",
                "tags": ["api", module],
                "source_file": relpath,
            })

        # Extract router prefix
        for m in re.finditer(r'prefix\s*=\s*["\']([^"\']+)["\']', content):
            specs.append({
                "title": f"{module} router prefix is '{m.group(1)}'",
                "section": "API",
                "tags": ["api", module],
                "source_file": relpath,
            })

    # --- API versioning ---
    versioning_content = read_file("src/multi_tenant/api_versioning.py")
    for m in re.finditer(r'(API_VERSION|PRODUCT_VERSION)\s*=\s*["\']([^"\']+)["\']', versioning_content):
        specs.append({
            "title": f"{m.group(1)} = '{m.group(2)}'",
            "section": "API",
            "tags": ["api", "versioning"],
            "source_file": "src/multi_tenant/api_versioning.py",
        })

    # --- Config models ---
    models_content = read_file("src/multi_tenant/config/models.py")
    for m in re.finditer(r'class (\w+)\(BaseModel\)', models_content):
        specs.append({
            "title": f"Config model class '{m.group(1)}'",
            "section": "CONFIG",
            "tags": ["config", "models"],
            "source_file": "src/multi_tenant/config/models.py",
        })

    # --- Validation rules ---
    validation_content = read_file("src/multi_tenant/schema/validation.py")
    for m in re.finditer(r'(TIER_RANK|GATE_RANK)\s*=\s*\{([^}]+)\}', validation_content):
        specs.append({
            "title": f"{m.group(1)} defines ordering for tier/gate ranking",
            "section": "CONFIG",
            "tags": ["config", "validation"],
            "source_file": "src/multi_tenant/schema/validation.py",
        })

    return specs


# ─────────────────────────────────────────────────────────────
# Area 2d: Backend Infrastructure
# ─────────────────────────────────────────────────────────────
def extract_2d() -> list[dict]:
    """Extract specs from repositories, middleware, rate limiting, etc."""
    specs = []

    # --- Repositories ---
    repo_dir = BASE / "src" / "multi_tenant" / "repositories"
    for py_file in sorted(repo_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        content = py_file.read_text(encoding="utf-8", errors="replace")
        relpath = str(py_file.relative_to(BASE)).replace("\\", "/")
        module = py_file.stem

        # Extract class definitions
        for m in re.finditer(r'class (\w+Repository)\(', content):
            specs.append({
                "title": f"Repository class '{m.group(1)}' in {module}.py",
                "section": "INFRASTRUCTURE",
                "tags": ["repository", module],
                "source_file": relpath,
            })

        # Extract async method signatures
        for m in re.finditer(r'async def (\w+)\(self[^)]*\)(?:\s*->\s*([^:]+))?:', content):
            method = m.group(1)
            if method.startswith("_"):
                continue
            return_type = (m.group(2) or "").strip()
            title = f"{module}.{method}()"
            if return_type:
                title += f" returns {return_type[:40]}"
            specs.append({
                "title": title,
                "section": "INFRASTRUCTURE",
                "tags": ["repository", module],
                "source_file": relpath,
            })

        # Extract constants
        for m in re.finditer(r'^([A-Z_]{3,})\s*=\s*(.+)$', content, re.MULTILINE):
            name, value = m.group(1), m.group(2).strip()[:60]
            specs.append({
                "title": f"Constant {name} = {value} in {module}",
                "section": "INFRASTRUCTURE",
                "tags": ["repository", module, "constant"],
                "source_file": relpath,
            })

    # --- Middleware ---
    for fname in ["auth.py", "security_middleware.py"]:
        content = read_file(f"src/multi_tenant/{fname}")
        relpath = f"src/multi_tenant/{fname}"
        module = fname.replace(".py", "")

        for m in re.finditer(r'async def (\w+)\(', content):
            if not m.group(1).startswith("_"):
                specs.append({
                    "title": f"Middleware function {m.group(1)}() in {module}",
                    "section": "INFRASTRUCTURE",
                    "tags": ["middleware", module],
                    "source_file": relpath,
                })

        # Security headers
        for m in re.finditer(r'["\']([A-Z][a-z]+-[A-Z][a-z]+-[A-Za-z-]+|X-[A-Za-z-]+|Content-Security-Policy|Strict-Transport-Security)["\']', content):
            specs.append({
                "title": f"Security header '{m.group(1)}' set by {module}",
                "section": "INFRASTRUCTURE",
                "tags": ["middleware", "security-headers"],
                "source_file": relpath,
            })

    # --- Rate limiting ---
    for fname in ["rate_limiter.py", "rate_limiting.py"]:
        content = read_file(f"src/multi_tenant/{fname}")
        if content:
            relpath = f"src/multi_tenant/{fname}"
            for m in re.finditer(r'(WINDOW_\w+|DEFAULT_\w+|MAX_\w+)\s*=\s*(\d+)', content):
                specs.append({
                    "title": f"Rate limit constant {m.group(1)} = {m.group(2)}",
                    "section": "INFRASTRUCTURE",
                    "tags": ["rate-limiting"],
                    "source_file": relpath,
                })

    # --- NATS / messaging ---
    nats_content = read_file("src/multi_tenant/nats_manager.py")
    if nats_content:
        for m in re.finditer(r'(TOPIC_\w+|STREAM_\w+|SUBJECT_\w+)\s*=\s*["\']([^"\']+)["\']', nats_content):
            specs.append({
                "title": f"NATS constant {m.group(1)} = '{m.group(2)}'",
                "section": "INFRASTRUCTURE",
                "tags": ["nats", "messaging"],
                "source_file": "src/multi_tenant/nats_manager.py",
            })

    return specs


# ─────────────────────────────────────────────────────────────
# Area 2e: Agents + Testing + Ops
# ─────────────────────────────────────────────────────────────
def extract_2e() -> list[dict]:
    """Extract specs from agent modules, test infrastructure, ops scripts."""
    specs = []

    # --- Agent modules ---
    agents_dir = BASE / "src" / "agents"
    for py_file in sorted(agents_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        content = py_file.read_text(encoding="utf-8", errors="replace")
        relpath = str(py_file.relative_to(BASE)).replace("\\", "/")
        module = py_file.stem

        # Extract class definitions
        for m in re.finditer(r'class (\w+Agent)\(', content):
            specs.append({
                "title": f"Agent class '{m.group(1)}' in {module}",
                "section": "AGENTS",
                "tags": ["agents", module],
                "source_file": relpath,
            })

        # Extract model env vars
        for m in re.finditer(r'os\.environ\.get\(["\'](\w+)["\'],\s*["\']([^"\']+)["\']', content):
            specs.append({
                "title": f"{module} uses env var {m.group(1)} (default: {m.group(2)})",
                "section": "AGENTS",
                "tags": ["agents", module, "config"],
                "source_file": relpath,
            })

        # Extract async process methods
        for m in re.finditer(r'async def (process|classify|retrieve|generate|evaluate|collect)\w*\(', content):
            specs.append({
                "title": f"{module} has {m.group(0).split('(')[0].replace('async def ', '')} method",
                "section": "AGENTS",
                "tags": ["agents", module],
                "source_file": relpath,
            })

    # --- Container apps ---
    containers_dir = BASE / "src" / "agents" / "containers"
    for py_file in sorted(containers_dir.glob("*_app.py")):
        content = py_file.read_text(encoding="utf-8", errors="replace")
        relpath = str(py_file.relative_to(BASE)).replace("\\", "/")
        module = py_file.stem

        for m in re.finditer(r'PORT\s*=\s*(\d+)|port["\']:\s*(\d+)', content):
            port = m.group(1) or m.group(2)
            specs.append({
                "title": f"{module} runs on port {port}",
                "section": "AGENTS",
                "tags": ["agents", "containers", module],
                "source_file": relpath,
            })

    # --- Test infrastructure ---
    conftest_content = read_file("tests/conftest.py")
    if conftest_content:
        # Extract fixture names
        for m in re.finditer(r'@pytest\.fixture(?:\(([^)]*)\))?\s*\ndef (\w+)\(', conftest_content):
            scope = m.group(1) or ""
            name = m.group(2)
            title = f"Test fixture '{name}'"
            if "session" in scope:
                title += " (session-scoped)"
            specs.append({
                "title": title,
                "section": "TESTING",
                "tags": ["testing", "fixtures"],
                "source_file": "tests/conftest.py",
            })

        # Extract test tenant IDs
        for m in re.finditer(r'["\']([a-z]-[a-z]+-\d+)["\']', conftest_content):
            specs.append({
                "title": f"Test tenant ID '{m.group(1)}'",
                "section": "TESTING",
                "tags": ["testing", "tenants"],
                "source_file": "tests/conftest.py",
            })

    # --- Ops scripts ---
    for script in ["seed_tenant.py", "upgrade_verification.py", "pre_flight_checklist.py"]:
        content = read_file(f"scripts/{script}")
        if not content:
            continue
        module = script.replace(".py", "")

        # Extract phase/step markers
        for m in re.finditer(r'(?:Phase|Step|PHASE)\s*(\w+)[:\s]+(.{10,60})', content):
            specs.append({
                "title": f"{module} {m.group(1)}: {m.group(2).strip()[:50]}",
                "section": "OPS",
                "tags": ["ops", module],
                "source_file": f"scripts/{script}",
            })

    # --- Hooks ---
    for hook in ["assertion-check.py", "scheduler.py"]:
        content = read_file(f".claude/hooks/{hook}")
        if content:
            specs.append({
                "title": f"Hook '{hook}' for session automation",
                "section": "OPS",
                "tags": ["ops", "hooks"],
                "source_file": f".claude/hooks/{hook}",
            })

    return specs


def main():
    areas = {
        "2a": ("Admin UI", extract_2a, "specs-batch-2a.json"),
        "2b": ("Config + API", extract_2b, "specs-batch-2b.json"),
        "2d": ("Infrastructure", extract_2d, "specs-batch-2d.json"),
        "2e": ("Agents + Testing", extract_2e, "specs-batch-2e.json"),
    }

    total = 0
    for key, (label, extractor, filename) in areas.items():
        outpath = DOCS / filename
        if outpath.exists():
            existing = json.loads(outpath.read_text(encoding="utf-8"))
            print(f"  {key} ({label}): SKIP — {filename} already exists ({len(existing)} specs)")
            total += len(existing)
            continue

        specs = extractor()
        outpath.write_text(
            json.dumps(specs, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  {key} ({label}): {len(specs)} specs -> {filename}")
        total += len(specs)

    # Check 2c
    c_path = DOCS / "specs-batch-2c.json"
    if c_path.exists():
        c_specs = json.loads(c_path.read_text(encoding="utf-8"))
        print(f"  2c (Widget+Auth+Email): {len(c_specs)} specs (pre-existing)")
        total += len(c_specs)

    print(f"\nTotal Phase 2 specs: {total}")


if __name__ == "__main__":
    main()
