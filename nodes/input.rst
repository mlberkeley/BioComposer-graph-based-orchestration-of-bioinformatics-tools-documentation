Input nodes
===========

An input node holds the values *you* supply to a pipeline: input file paths and
scalar parameters. It runs no tool, its key/value dictionary *is* its output, fed
to downstream nodes through their connectors.

.. code-block:: python

   rf_in = g.add_input_node(
       input_pdb="/vol/inputs/1l9h.pdb",
       contigs="[150-150]",
       num_designs="2",
   )

.. _input-keys:

Keys must match the downstream tool
-----------------------------------

For a value to reach a tool, its key must
match one of that tool's declared input ``name`` fields, and that name must appear
as a ``{slot}`` in the tool's command template. Read the names from the manifest::

   bv show <tool> --format json

For example, ``bv show proteinmpnn --format json`` declares inputs ``pdb_path``,
``num_seq_per_target``, ``sampling_temp``, so the input node uses exactly those
keys. A value whose key matches no slot is silently dropped, which is the usual
cause of a parameter "not taking effect." See :doc:`../tools` for reading manifests
in full.

Files vs. scalars
-----------------

Both kinds of value are taken directly, biocomposer never rewrites a value you
set yourself:

- **File paths** (values that exist on disk) are staged into the tool's sandbox at
  run time and the command receives the staged filename.
- **Scalars** (numbers, short strings like ``"[150-150]"`` or ``"0.1"``) are
  substituted literally into the command line.

Input nodes override upstream outputs
-------------------------------------

A node's inputs are merged with input-node values applied **last**, so a value you
set on an input node **overrides** any value an upstream tool produced for the same
key. For example, if a step receives a generated ``pdb`` from upstream but you also
pass ``input_pdb=...`` on an input node into it, your input-node value is chosen. Only
set a key when you intend that override. See :ref:`merge-order` for the full rule
(including which of two colliding *tool* outputs wins).


Multiple input nodes
--------------------

A node may take several input nodes (plus one upstream tool). This is common with
map and decision nodes, where one input node supplies the collection-producing
tool and another supplies shared scalar parameters:

.. code-block:: python

   mpnn_in = g.add_input_node(num_seq_per_target="2", sampling_temp="0.1")
   g.add_edge((rfdiffusion, proteinmpnn), (mpnn_in, proteinmpnn))

Reference
---------

.. autoclass:: biocomposer.InputNode
   :members: set_input
   :noindex:
