Tool nodes
==========

A tool node wraps one tool from the registry and runs it once per execution.

.. code-block:: python

   align = g.add_node("clustalo")

Creation installs the tool
--------------------------
add_node():

#. waits for the container backend (Docker) to be ready;
#. adds the tool to the project and pulls its image (``bv add`` / ``bv sync``),
   restoring from the on-disk image cache when present;
#. reads the tool's manifest (``bv show --format json``) and stores it on the node.

The manifest is what the rest of the system reasons over: the tool's typed inputs
and outputs drive connector generation, and its command template drives execution.
See :doc:`../tools` for the manifest format.

What happens when it runs
-------------------------

During :func:`~biocomposer.Graph.execute`, a tool node:

#. receives its inputs (mapped from upstream outputs by the edge connectors);
#. is assigned a fresh output directory ``results/<tool>_output_N``, ``N``
   auto-increments by scanning the filesystem, so repeated runs of the same tool
   never collide;
#. runs the tool in its container via ``bv`` inside a temporary sandbox, then
   harvests the declared outputs back into that output directory;
#. returns a dictionary mapping each output ``name`` to its produced path (a
   directory path for ``type = "dir"`` outputs, a file path otherwise).


Cardinality determines composition
----------------------------------

A tool input declared ``cardinality = "one"`` consumes exactly one item per run. If
an upstream produces a *collection* and the next tool's input is ``one``, you wrap
that tool in a :doc:`gather node <gather>` so it runs once per item, the single most
common structural decision when building a pipeline. ``cardinality = "many"`` means
the tool accepts a list directly and no gather node is needed.

Overriding the command
----------------------

By default a node runs the manifest's entrypoint with its argument template. Two
overrides change that; ``{slot}`` placeholders map to the node's input/output names.

**Different binary**, for images that expose several programs:

.. code-block:: python

   g.add_node("trimal", entrypoint_override="readal")

**Different argument template**, to change flags or argument order:

.. code-block:: python

   g.add_node("colabfold",
              args_override="--num-recycle 0 {fasta} {output_dir}")

**Both**, common when invoking a non-default binary:

.. code-block:: python

   g.add_node("trimal",
              entrypoint_override="readal",
              args_override="-in {alignment} -out {trimmed} -fasta")

Overrides replace the corresponding manifest field for that node only; everything
else (image, typed I/O) is unchanged.

Reference
---------

.. autoclass:: biocomposer.Node
   :members: install, run
   :noindex:
