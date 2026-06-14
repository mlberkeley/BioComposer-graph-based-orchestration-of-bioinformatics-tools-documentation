<div align="center">

<h1>biocomposer</h1>

<h3>graph-based orchestration of bioinformatics tools</h3>

<p><b>made by Machine Learning @ Berkeley (ML@B)</b></p>

<sub>
Aditya Lakshminarasimhan&nbsp;&middot;&nbsp;Arshia Nayebnazar&nbsp;&middot;&nbsp;Avyukth Harish<br>
Lucas Gu&nbsp;&middot;&nbsp;Tvisha Londhe&nbsp;&middot;&nbsp;Tejas Prabhune
</sub>

<p>
<a href="https://pypi.org/project/biocomposer/">PyPI</a> &middot;
<a href="https://mlberkeley.github.io/BioComposer-graph-based-orchestration-of-bioinformatics-tools-documentation/">Documentation</a>
</p>

</div>

---

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


Feel free to reach out with questions to aditya_lakshmi27@berkeley.edu or arshian@berkeley.edu