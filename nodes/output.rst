Output nodes
============

``set_output_node(node)`` marks which node's result
:func:`~biocomposer.Graph.execute` should return. Execution starts from the output
node(s) and walks backward through their dependencies, so the output node defines
*what gets computed*, any node not on a path to an output is never run.

.. code-block:: python

   g.set_output_node(align)
   result = g.execute()     # result == align's output dict

``execute()`` returns a **list**, one entry per output node, in the order they were
registered. A graph may declare several outputs:

.. code-block:: python

   g.set_output_node(rfdiffusion)   # also keep the backbones
   g.set_output_node(colabfold)     # and the predictions
   rf_out, cf_out = g.execute()

Every intermediate node's inputs and outputs are also written to ``results/`` (and
to the run's state file) as it executes, so nothing produced along the way is lost
even if it isn't the declared output.

A dedicated ``OutputNode`` object also exists and *collects* results when used; in
typical pipelines you simply pass the final tool node to ``set_output_node`` and
read the returned dict.
