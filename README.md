# biocomposer documentation

Source for the [biocomposer](https://pypi.org/project/biocomposer/) documentation
site. This repository contains **docs only** — the package source lives in a
separate private repository.

The site is built with [Sphinx](https://www.sphinx-doc.org/) (Furo theme) and
deployed to GitHub Pages by the `Docs` workflow on every push to `main`.

## Build locally

```bash
pip install -r requirements.txt
pip install --no-deps biocomposer   # for autodoc; heavy deps are mocked in conf.py
sphinx-build -b html . _build/html
open _build/html/index.html
```
