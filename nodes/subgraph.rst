Subgraphs
=========

A :class:`~biocomposer.SubGraph` is a pipeline that behaves as a single node. You
build it like a :class:`~biocomposer.Graph`, add nodes, wire edges, but it is
constrained to **exactly one input node and one output node**, so it has the same
one-in/one-out shape as an ordinary step and can be placed on an edge in an outer
graph.

.. mermaid::

   flowchart LR
       IN(["input"]) --> SG
       subgraph SG["SubGraph"]
           direction LR
           A["tool A"] --> B["tool B"]
       end
       SG --> OUT["next node"]

Constraints
-----------

The single-in/single-out rule is enforced at build time:
``add_input_node`` raises if called twice, and ``set_output_node`` raises if called
twice. The subgraph exposes ``get_input_node()`` and ``get_output_node()`` so the
outer graph can attach edges to its endpoints, you pass the subgraph object to
``add_edge`` and biocomposer resolves the correct inner node automatically.

Use in an outer graph
---------------------

.. code-block:: python

   from biocomposer import Graph, SubGraph

   pre = SubGraph()
   s_in  = pre.add_input_node(sequences="/vol/inputs/family.fasta")
   align = pre.add_node("clustalo")
   trim  = pre.add_node("trimal",
                        args_override="-in {alignment} -out {trimmed} -fasta -gappyout")
   pre.add_edge((s_in, align), (align, trim))
   pre.set_output_node(trim)

   g = Graph()
   tree = g.add_node("fasttree")
   g.add_edge((pre, tree))      # subgraph's output feeds the next tool
   g.set_output_node(tree)
   g.execute()

Run standalone
--------------

A subgraph can also be executed directly with fresh inputs via ``run(inputs)``,
which sets its single input node and runs:

.. code-block:: python

   pre.run({"sequences": "/vol/inputs/other_family.fasta"})

Reference
---------

.. autoclass:: biocomposer.SubGraph
   :members: get_input_node, get_output_node, run
   :noindex:
