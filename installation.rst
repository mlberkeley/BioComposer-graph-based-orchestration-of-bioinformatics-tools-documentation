Installation
============

Install the package
-------------------

.. code-block:: bash

    pip install -e .          # editable install, for development

Create the working directories the CLI expects::

    mkdir inputs   # your FASTA / PDB / etc. input files
    mkdir run      # your pipeline scripts

What else you need
------------------

The full list of prerequisites, the ``bv`` registry client, Docker (for local
runs), Modal (for cloud runs), and API keys, is covered on the :doc:`running`
page, along with how to actually launch a pipeline.

In short:

* **API key** in a ``.env`` file (``GEMINI_API_KEY`` / ``GOOGLE_API_KEY`` /
  ``ANTHROPIC_API_KEY`` / ``OPENAI_API_KEY``), connectors are LLM-generated.
* **bv** registry client: ``cargo install biov``.
* **Docker** running, *for local execution only*.
* **Modal** (``pip install modal && modal setup``), *for cloud execution only*.

Then head to :doc:`running`, or see :doc:`examples` for worked pipelines.
