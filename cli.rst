Command-line interface
======================

Pipelines are executed with the ``biocomp`` command (installed by
``pip install -e .``).

.. code-block:: text

    biocomp run [--modal] run/run_pipeline.py --env .env

Flags
-----

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Flag
     - Scope
     - Meaning
   * - ``--env <path>``
     - both
     - env file with API keys (default ``.env``)
   * - ``--clean``
     - both
     - clear previous outputs first
   * - ``--modal``
     - both
     - run on Modal instead of locally
   * - ``--gpu T4``
     - modal
     - GPU type (default ``A10G``)
   * - ``--memory 32768``
     - modal
     - sandbox memory in MB (default ``8192``)
   * - ``--shell``
     - modal
     - drop into an interactive sandbox shell

Local runs require Docker and ``bv``; Modal runs require ``modal setup``. See
:doc:`installation`.

Retrieving Modal outputs
------------------------

.. code-block:: bash

    modal volume get biocomp results/<tool>_output_1/stdout/<file> ./<file>
