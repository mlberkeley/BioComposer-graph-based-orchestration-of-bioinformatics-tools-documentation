Graph
=====

:class:`~biocomposer.Graph` is the pipeline: a set of nodes and the directed edges
between them. Building a graph only *describes* the pipeline, nothing runs until
:func:`~biocomposer.Graph.execute` (see :doc:`execute`).

.. code-block:: python

   from biocomposer import Graph

   g = Graph()
   a = g.add_input_node(sequences="/vol/inputs/family.fasta")
   b = g.add_node("clustalo")
   g.add_edge((a, b))
   g.set_output_node(b)

Graphs are defined using nodes (bioinformatics tools) and edges (auto-generated mapper 
functions) that enable data flow between nodes. There are 6 types of nodes, covered in 
:doc:`nodes/index`. Execution, run order, input merging, results, is covered in :doc:`execute`.

Edges
-----

``add_edge`` takes one or more ``(upstream, downstream)`` tuples and records the
wiring; it also tracks fan-out (how many downstreams each node feeds), which the
executor uses for caching. Rules:

- A node may have several incoming edges.
- An :class:`~biocomposer.InputNode` may only be a *source*.
- Both endpoints may be nodes or :doc:`subgraphs <nodes/subgraph>`.

Edge **order matters** when two upstreams collide on a key, see
:ref:`merge-order` on the :doc:`execute` page.

.. code-block:: python

   g.add_edge((rfdiffusion, proteinmpnn), (mpnn_in, proteinmpnn))  # two edges, one call

Output nodes
------------

``set_output_node(node)`` marks which node's result :func:`~biocomposer.Graph.execute`
returns. Execution starts from the output node(s) and walks backward. 
A graph may have several outputs; ``execute()`` returns
one result per output node. See :doc:`nodes/output`.

.. toctree::
   :hidden:

   nodes/index
   execute

Reference
---------

.. autoclass:: biocomposer.Graph
   :members: add_input_node, add_node, add_gather_node, add_decision_node,
             add_edge, set_output_node, set_llm, execute
   :noindex:
