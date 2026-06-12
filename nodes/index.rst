Nodes
=====

A node is one step in the pipeline graph. Every node has an ``id`` (the tool name,
suffixed ``_1``, ``_2``, … if the same tool is added more than once) and a list of
upstream nodes (``inNodes``) populated by :func:`~biocomposer.Graph.add_edge`.

There are six kinds:

.. list-table::
   :header-rows: 1
   :widths: 20 26 54

   * - Node
     - Constructor
     - Role
   * - :doc:`Input <input>`
     - ``add_input_node(**values)``
     - Holds user-supplied file paths and scalar parameters. Runs no tool.
   * - :doc:`Tool <tool>`
     - ``add_node(name)``
     - Wraps one registry tool; runs once per execution.
   * - :doc:`Gather <gather>`
     - ``add_gather_node(name, split_key=...)``
     - Runs a one-input tool once per item of an upstream collection, then gathers.
   * - :doc:`Decision <decision>`
     - ``add_decision_node(score_fn, conditions, modifier_tool)``
     - Re-runs an upstream until a scored condition holds (bounded feedback loop).
   * - :doc:`Output <output>`
     - ``set_output_node(node)``
     - Marks the node whose result :func:`~biocomposer.Graph.execute` returns.
   * - :doc:`Subgraph <subgraph>`
     - ``SubGraph()``
     - A one-in / one-out pipeline usable as a single node.

.. toctree::
   :hidden:

   input
   tool
   gather
   decision
   output
   subgraph
