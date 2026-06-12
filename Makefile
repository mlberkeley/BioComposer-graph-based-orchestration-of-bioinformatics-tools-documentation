# Minimal makefile for Sphinx documentation.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

# Build, then serve the rendered site (opens the home page at http://localhost:8000).
serve: html
	@cd "$(BUILDDIR)/html" && python3 -m http.server 8000

.PHONY: help serve Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
