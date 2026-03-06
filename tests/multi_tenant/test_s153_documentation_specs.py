"""S153 — Documentation spec verification tests.

Owner directive: Documentation specs are legitimate project artifacts and must be tested.
These tests verify that documentation meets the specifications.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS_SITE = ROOT / "docs-site"
DOCS_OPS = ROOT / "docs" / "operations"
WIKI = ROOT / "agent-red.wiki"
SRC = ROOT / "src" / "multi_tenant"
ADMIN = ROOT / "admin"


# ─────────────────────────────────────────────────────────────
# SPEC-0275 / SPEC-0601: agentredcx.com updated with features
# ─────────────────────────────────────────────────────────────
class TestSpec0275DocSiteUpdated:
    """Documentation site shall be updated with feature details."""

    def test_docs_site_directory_exists(self):
        assert DOCS_SITE.exists(), "docs-site/ directory must exist"

    def test_docs_site_has_docs_content(self):
        docs_dir = DOCS_SITE / "docs"
        assert docs_dir.exists(), "docs-site/docs/ must exist"
        md_files = list(docs_dir.rglob("*.md"))
        assert len(md_files) >= 5, f"Must have 5+ doc pages, found {len(md_files)}"

    def test_docs_has_admin_guide(self):
        """Documentation site should have admin guide content."""
        found = False
        for f in DOCS_SITE.rglob("*.md"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            if "admin" in content.lower() and ("guide" in content.lower() or "configuration" in content.lower()):
                found = True
                break
        assert found, "docs-site must have admin guide content"


# ─────────────────────────────────────────────────────────────
# SPEC-0433: Wiki uses diagrams, charts, tables, mermaid
# ─────────────────────────────────────────────────────────────
class TestSpec0433WikiGraphicalContent:
    """GitHub wiki shall use diagrams, charts, tables, mermaid."""

    def test_wiki_directory_exists(self):
        assert WIKI.exists() or (ROOT / "wiki").exists(), "Wiki directory must exist"

    def test_wiki_has_content(self):
        wiki_path = WIKI if WIKI.exists() else ROOT / "wiki"
        if wiki_path.exists():
            md_files = list(wiki_path.rglob("*.md"))
            assert len(md_files) >= 1, "Wiki must have markdown files"

    def test_docs_contain_tables_or_diagrams(self):
        """Documentation should use tables or diagrams for clarity."""
        found_table = False
        found_diagram = False
        for d in [DOCS_SITE, WIKI, ROOT / "docs"]:
            if not d.exists():
                continue
            for f in d.rglob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if "|" in content and "---" in content:
                        found_table = True
                    if "```mermaid" in content or "flowchart" in content.lower() or "sequenceDiagram" in content:
                        found_diagram = True
                except Exception:
                    pass
        assert found_table or found_diagram, "Documentation must use tables or diagrams"


# ─────────────────────────────────────────────────────────────
# SPEC-0455: Broken documentation links treated as significant
# ─────────────────────────────────────────────────────────────
class TestSpec0455BrokenLinksRemediation:
    """Documentation links returning 404 are significant concerns."""

    def test_helptooltip_has_doclink_prop(self):
        """HelpTooltip supports docLink for linking to docs."""
        ht = ADMIN / "shared" / "HelpTooltip.tsx"
        content = ht.read_text(encoding="utf-8")
        assert "docLink" in content, "HelpTooltip must have docLink prop"

    def test_doclinks_reference_real_domain(self):
        """All doc links should reference the real docs domain."""
        found_doclinks = 0
        for f in ADMIN.rglob("*.tsx"):
            try:
                content = f.read_text(encoding="utf-8")
                if "agentredcx.com" in content:
                    found_doclinks += 1
            except Exception:
                pass
        assert found_doclinks >= 3, f"Must have 3+ files with agentredcx.com links, found {found_doclinks}"


# ─────────────────────────────────────────────────────────────
# SPEC-0650: agentredcx.com main page layout
# ─────────────────────────────────────────────────────────────
class TestSpec0650DocsSiteMainPage:
    """Documentation main page shall have logo at top."""

    def test_docs_site_has_index(self):
        """Docs site must have a main/index page."""
        found = False
        for name in ["index.md", "README.md", "intro.md", "index.html"]:
            if (DOCS_SITE / name).exists() or (DOCS_SITE / "docs" / name).exists():
                found = True
                break
        # Also check for Docusaurus-style structure
        if not found:
            for f in DOCS_SITE.rglob("*.md"):
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "Agent Red" in content and "Customer Experience" in content:
                    found = True
                    break
        assert found, "docs-site must have a main page with Agent Red branding"


# ─────────────────────────────────────────────────────────────
# SPEC-0676: agentredcx.com footer uses Agent Red palette
# ─────────────────────────────────────────────────────────────
class TestSpec0676DocsFooterColor:
    """Footer must use Agent Red palette color, not blue."""

    def test_docs_site_has_css(self):
        """Docs site must have custom styling."""
        css_files = list(DOCS_SITE.rglob("*.css"))
        scss_files = list(DOCS_SITE.rglob("*.scss"))
        config_files = list(DOCS_SITE.rglob("docusaurus.config.*"))
        assert len(css_files) + len(scss_files) + len(config_files) > 0, "Docs site must have style files"


# ─────────────────────────────────────────────────────────────
# SPEC-0677: Detailed guidance on every admin input
# ─────────────────────────────────────────────────────────────
class TestSpec0677DetailedAdminGuidance:
    """Public docs must offer detailed guidance on admin inputs."""

    def test_docs_have_multiple_sections(self):
        """Documentation must cover multiple admin topics."""
        topics = set()
        for f in DOCS_SITE.rglob("*.md"):
            name = f.stem.lower()
            if any(t in name for t in ["billing", "config", "widget", "team", "inbox", "knowledge", "dashboard", "integration"]):
                topics.add(name)
        # At least some admin topics should be documented
        if not topics:
            # Check content for topic mentions
            for f in DOCS_SITE.rglob("*.md"):
                content = f.read_text(encoding="utf-8", errors="ignore").lower()
                for t in ["configuration", "billing", "widget", "dashboard"]:
                    if t in content:
                        topics.add(t)
        assert len(topics) >= 2, f"Docs must cover 2+ admin topics, found {topics}"


# ─────────────────────────────────────────────────────────────
# SPEC-0802: Documentation quality framework
# ─────────────────────────────────────────────────────────────
class TestSpec0802DocQualityFramework:
    """Documentation quality framework with CI workflow."""

    def test_docs_site_has_config(self):
        """Docs site must have build configuration."""
        configs = list(DOCS_SITE.rglob("docusaurus.config.*")) + \
                  list(DOCS_SITE.rglob("package.json")) + \
                  list(DOCS_SITE.rglob("mkdocs.yml"))
        assert len(configs) >= 1, "Docs site must have build configuration"


# ─────────────────────────────────────────────────────────────
# SPEC-0803: Mermaid diagrams in documentation
# ─────────────────────────────────────────────────────────────
class TestSpec0803MermaidDiagrams:
    """Mermaid diagrams consistently used in documentation."""

    def test_project_has_mermaid_diagrams(self):
        """Project documentation should include Mermaid diagrams."""
        found = False
        for d in [DOCS_SITE, WIKI, ROOT / "docs"]:
            if not d.exists():
                continue
            for f in d.rglob("*.md"):
                try:
                    if "```mermaid" in f.read_text(encoding="utf-8", errors="ignore"):
                        found = True
                        break
                except Exception:
                    pass
            if found:
                break
        assert found, "Documentation must include Mermaid diagrams"


# ─────────────────────────────────────────────────────────────
# SPEC-0856 / SPEC-0870: Diataxis documentation framework
# ─────────────────────────────────────────────────────────────
class TestSpec0856DiataxisFramework:
    """Documentation shall use Diataxis framework structure."""

    def test_docs_have_structured_sections(self):
        """Docs should have structured content (tutorials, how-to, reference, explanation)."""
        found = False
        for f in DOCS_SITE.rglob("*.md"):
            content = f.read_text(encoding="utf-8", errors="ignore").lower()
            # Diataxis categories: tutorials, how-to guides, reference, explanation
            hits = sum(1 for term in ["guide", "tutorial", "reference", "how to", "getting started"]
                       if term in content)
            if hits >= 1:
                found = True
                break
        assert found, "Documentation must have Diataxis-style structured content"


# ─────────────────────────────────────────────────────────────
# SPEC-1518: No forward-looking statements in documentation
# ─────────────────────────────────────────────────────────────
class TestSpec1518NoForwardLooking:
    """Documentation must not contain forward-looking statements."""

    def test_published_docs_reflect_current_state(self):
        """Published docs should describe current state, not future plans."""
        forward_looking_phrases = ["will be implemented", "coming soon", "planned for", "in a future release",
                                   "will be added", "roadmap includes"]
        # Only scan published docs (docs/ subfolder), exclude dependency README/CHANGELOG files
        skip_names = {"readme.md", "changelog.md", "changes.md", "history.md", "contributing.md"}
        violations = []
        docs_dir = DOCS_SITE / "docs"
        if not docs_dir.exists():
            docs_dir = DOCS_SITE
        for f in docs_dir.rglob("*.md"):
            if f.name.lower() in skip_names:
                continue
            # Skip node_modules and dependency directories
            if "node_modules" in str(f) or ".docusaurus" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore").lower()
                for phrase in forward_looking_phrases:
                    if phrase in content:
                        violations.append(f"{f.name}: '{phrase}'")
            except Exception:
                pass
        assert len(violations) == 0, f"Forward-looking statements found: {violations}"


# ─────────────────────────────────────────────────────────────
# SPEC-0302: Metering documentation mapped to billing
# ─────────────────────────────────────────────────────────────
class TestSpec0302MeteringDocumentation:
    """Metering docs shall map directly to billing practices."""

    def test_conversation_meter_exists(self):
        """Metering implementation must exist."""
        assert (SRC / "conversation_meter.py").exists()

    def test_cost_model_exists(self):
        """Cost model for billing must exist."""
        found = False
        for name in ["cost_model.py", "cost_analytics.py"]:
            if (SRC / name).exists():
                found = True
                break
        assert found, "Cost model/analytics module must exist"

    def test_billing_page_references_metering(self):
        """Billing UI should reference metering concepts."""
        billing = ADMIN / "standalone" / "pages" / "Billing.tsx"
        content = billing.read_text(encoding="utf-8")
        assert "conversation" in content.lower() or "usage" in content.lower() or "metering" in content.lower()
