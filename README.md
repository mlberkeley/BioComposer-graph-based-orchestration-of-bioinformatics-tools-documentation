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

# Overview

biocomposer is a graph-based orchestration framework in python for abstracting data flow between bioinformatics tools in executable pipelines. You describe a pipeline as a graph of tools; biocomposer runs each tool in its own container, generates the code that converts one tool’s output into the next tool’s input, and derives the execution order for you.

# biocomposer documentation

Source for the [biocomposer](https://pypi.org/project/biocomposer/) documentation
site. This repository contains **docs only** — the package source lives in a
separate private repository.

The site is built with [Sphinx](https://www.sphinx-doc.org/) (Furo theme) and
deployed to GitHub Pages by the `Docs` workflow on every push to `main`.

# Package Specs

* An explicit graph and generated glue, together. The pipeline is a graph you define in code, version, and re-run; the data conversion on each edge is generated per edge from the tools’ typed schemas and the data seen at runtime. The structure is highly modular for the scientist, and enables quick tool-swapping and controlled orchestration.

* Generated connectors are ordinary, inspectable code. Each edge’s converter is written out as a Python function and cached on disk, so the transformation between two tools is a concrete artifact you can read and reuse, not a hidden runtime step.

* The language model only writes the glue. It is used to generate the connector for an edge, from the two tools’ schemas and the runtime data. It does not choose the tools, run them, or interpret their results; those remain the user’s graph and the tools’ own execution.

* Tools are standardized behind a registry. Each tool is a container image plus a typed TOML manifest, resolved from the open bv registry (by Tejas Prabhune). Entries can wrap custom Docker/Apptainer images, BioContainers, or Docker Hub images, so specialized tools compose on the same footing as widely used ones.

* The graph carries real workflow logic. Beyond linear chains: fan-out and fan-in, per-item processing of collections (gather nodes), bounded feedback loops (decision nodes), and reusable sub-pipelines (subgraphs).

* Local or cloud, unchanged. The package resolves hardware depencies and sandbox staging smoothly. The package detects local or modal hardware, and runs the tools on the respective hardware.

Feel free to reach out with questions to aditya_lakshmi27@berkeley.edu or arshian@berkeley.edu
