"""Sphinx configuration for the biocomposer documentation.

This is a standalone docs repository: the package source does NOT live here.
autodoc imports the `biocomposer` package that is `pip install`ed at build time,
so the API reference is generated from the published, compiled package."""

import importlib.metadata

project = "biocomposer"
copyright = "2026, biocomposer contributors"
author = "biocomposer contributors"

# Track whatever release is installed in the build; fall back if not importable.
try:
    release = importlib.metadata.version("biocomposer")
except importlib.metadata.PackageNotFoundError:
    release = "0.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinxcontrib.mermaid",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
templates_path = ["_templates"]
# Docs sources sit at the repo root in the standalone docs repo, so exclude the
# build output, the CI workflow dir, the README, and OS cruft from the source tree.
exclude_patterns = ["_build", ".github", "README.md", "Thumbs.db", ".DS_Store"]

# --- Theme: Furo (the modern flat look used by pip, Black, Hatch) ----------
html_theme = "furo"
html_title = "biocomposer"
html_static_path = ["_static"]
# Copy these verbatim into the published root. `.nojekyll` tells GitHub Pages not
# to run Jekyll (which would strip the leading-underscore _static/ directory).
html_extra_path = [".nojekyll"]
html_css_files = ["custom.css"]

_brand = "#5b54e8"        # indigo accent
_brand_dark = "#8b85ff"   # lighter accent for dark mode

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": _brand,
        "color-brand-content": _brand,
        "font-stack": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', "
                      "Roboto, Helvetica, Arial, sans-serif",
        "font-stack--monospace": "'JetBrains Mono', SFMono-Regular, Menlo, "
                                 "Consolas, monospace",
        "color-api-name": _brand,
        "color-api-pre-name": _brand,
    },
    "dark_css_variables": {
        "color-brand-primary": _brand_dark,
        "color-brand-content": _brand_dark,
    },
}

# Mermaid: match the docs palette and use clean rounded shapes.
mermaid_version = "10.9.1"
mermaid_init_js = """
mermaid.initialize({
  startOnLoad: true,
  theme: 'base',
  themeVariables: {
    primaryColor: '#eef0ff',
    primaryBorderColor: '#5b54e8',
    primaryTextColor: '#1f2330',
    lineColor: '#8a90a6',
    fontFamily: 'Inter, sans-serif',
    fontSize: '14px'
  },
  flowchart: { curve: 'basis', padding: 14 }
});
"""

# --- autodoc ---------------------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_mock_imports = ["modal", "google", "anthropic", "openai", "dotenv", "numpy", "pandas"]
autodoc_member_order = "bysource"
napoleon_google_docstring = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
