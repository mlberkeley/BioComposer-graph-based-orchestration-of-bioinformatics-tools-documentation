.. raw:: html

   <div class="mg-hero">
     <div class="mg-hero-title">biocomposer: graph-based orchestration of bioinformatics tools</div>
     <div class="mg-hero-org">Machine Learning @ Berkeley (ML@B)</div>
     <div class="mg-hero-authors">
       Aditya Lakshminarasimhan &middot; Arshia Nayebnazar &middot; Avyukth Harish
       &middot; Lucas Gu &middot; Tvisha Londhe &middot; Tejas Prabhune
     </div>
   </div>

Overview
========
biocomposer is a graph-based orchestration framework in python for abstracting data flow 
between bioinformatics tools in executable pipelines. You describe a pipeline as a graph 
of tools; biocomposer runs each tool in its own container, generates the code that converts 
one tool's output into the next tool's input, and derives the execution order for you.

Why it exists
-------------

Composing bioinformatics tools or orchestrating them together, normally forces the 
user to reason about which tools to chain, how their formats and arguments line up, 
how to invoke each one, and how to install dependencies. Ultimately, there is a lot 
of complex python coding knowledge and syntax, along with many hours or weeks 
of debugging, just to build a modular bioinformatics pipeline. Additionally, some 
tools may be highly specialized and tailored to one specific task on very specific 
inputs, which limits their ability to interoperate with other tools and models. 
For this reason, we have developed biocomposer as an open-source effort to standardize 
various bioinformatics tools, and modularize them so that they can be discovered by 
other scientists, and be used in pipelines with other scientific tools to investigate 
various hypotheses. 

- **Inconsistent I/O.** One tool emits ``.pdb`` where the next expects ``.cif``;
  argument names and file layouts differ between every pair of tools.
- **Idiosyncratic invocation.** Each tool has its own flags, entrypoints, and
  environment, and many ship as under-documented repositories rather than packages.
- **No orchestration layer.** There is no common substrate for wiring tools
  together, so even semantically compatible models (say, structure generation and
  docking) are tedious to combine.

biocomposer removes the integration burden so effort goes into *workflow design*
rather than format conversion and command-line plumbing. It handles compatibility
between steps, performs LLM-guided data transformation across them, and runs the
result reproducibly, locally or on the cloud.

An Example Pipeline:
--------------------

This script aligns a FASTA file with Clustal Omega:

.. code-block:: python

   from biocomposer import Graph

   g = Graph()
   seqs  = g.add_input_node(sequences="/vol/inputs/family.fasta")
   align = g.add_node("clustalo")
   g.add_edge((seqs, align))
   g.set_output_node(align)
   result = g.execute()

The edge ``(seqs, align)`` says only *what connects to what*. The hand-off itself,
turning the input file into the exact arguments and format Clustal Omega expects, is
not written by hand: biocomposer reads both tools' manifests, inspects the data at
runtime, and generates the connector for that edge.

Package Specs
------------------

- **An explicit graph and generated glue, together.** The pipeline is a graph you
  define in code, version, and re-run; the data conversion on each edge is generated
  per edge from the tools' typed schemas and the data seen at runtime. The
  structure is highly modular for the scientist, and enables quick tool-swapping and
  controlled orchestration.
- **Generated connectors are ordinary, inspectable code.** Each edge's converter is
  written out as a Python function and cached on disk, so the transformation between
  two tools is a concrete artifact you can read and reuse, not a hidden runtime step.
- **The language model only writes the glue.** It is used to generate the connector
  for an edge, from the two tools' schemas and the runtime data. It does not choose
  the tools, run them, or interpret their results; those remain the user's graph and
  the tools' own execution.
- **Tools are standardized behind a registry.** Each tool is a container image plus
  a typed TOML manifest, resolved from the open `bv registry
  <https://tejasprabhune.github.io/bv-registry/>`_ (by Tejas Prabhune TEJAS INSERT HOW YOU WANT TO BE CITED). Entries can wrap custom Docker/Apptainer images, `BioContainers
  <https://biocontainers.pro>`_, or `Docker Hub <https://hub.docker.com>`_ images,
  so specialized tools compose on the same footing as widely used ones.
- **The graph carries real workflow logic.** Beyond linear chains: fan-out and
  fan-in, per-item processing of collections (:doc:`gather nodes <nodes/gather>`),
  bounded feedback loops (:doc:`decision nodes <nodes/decision>`), and reusable
  sub-pipelines (:doc:`subgraphs <nodes/subgraph>`).
- **Local or cloud, unchanged.** The package resolves hardware depencies and sandbox
  staging smoothly. The package detects local or modal hardware, and runs the tools
  on the respective hardware. 

same script runs on local Docker or a Modal
  GPU sandbox, with tool images cached across runs.

See :doc:`how_it_works` for the architecture and execution model, or
:doc:`examples` for worked pipelines.

.. toctree::
   :maxdepth: 1
   :caption: Getting started
   :hidden:

   Overview <self>
   how_it_works
   installation
   running

.. toctree::
   :maxdepth: 2
   :caption: Building pipelines
   :hidden:

   graph
   connectors
   examples

.. toctree::
   :maxdepth: 1
   :caption: Tools
   :hidden:

   tools
   contributing_tools

.. toctree::
   :maxdepth: 1
   :caption: Reference
   :hidden:

   cli
   api


Feel free to reach out with questions to aditya_lakshmi27@berkeley.edu or 
arshian@berkeley.edu
