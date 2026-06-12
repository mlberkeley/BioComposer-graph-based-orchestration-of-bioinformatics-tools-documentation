Execution
=========

``execute()`` runs the graph and returns a list with one entry per output node, in
registration order:

.. code-block:: python

   results = g.execute()        # [output_1, output_2, ...]

Run order
---------

Each output node is evaluated by walking **backward** through its dependencies (the
executor recurses over a node's upstreams before running the node). Consequences:

- **Shared results are computed once.** If a node feeds more than one downstream,
  its result is cached after the first evaluation and reused
- **Dead branches don't run.** A node with no path to an output is never evaluated.

For an ordinary tool node the executor, per incoming edge, runs the upstream,
obtains the edge's connector, maps the upstream output into this node's inputs
(dropping ``None`` values), then runs the tool once and records its inputs and
outputs to the run's state file.

Map and decision nodes follow the same backward walk but add their own loop,
running the tool once per scattered item (:doc:`nodes/gather`) or repeatedly until a
condition holds (:doc:`nodes/decision`).

.. _merge-order:

Input merging and key clashes
-----------------------------

A node's input dict is assembled by applying each incoming edge's mapped result
with ``dict.update``, so when two edges contribute the **same key**, the one
applied **later overwrites** the earlier. Two rules follow from the order the
executor uses:

**1. Input nodes override tool outputs.** The executor processes a node's non-input
(tool) upstreams first, then its input nodes. Because input nodes are applied last,
a value you set on an input node **overwrites** any value an upstream tool produced
under the same key. If you pass ``input_pdb=...`` on an input node into a step that
also receives a generated ``pdb`` from upstream, your input-node value wins, so set
a key only when you mean to override.

**2. Among tool edges, the last edge added wins.** Tool upstreams are applied in the
order they were wired with :func:`~biocomposer.Graph.add_edge` (an edge appends to
the downstream node's upstream list). If two upstream tools emit the same key, the
edge added **last** overwrites the earlier, so when two producers collide on a key,
order the edge you want to win last.

Results and state
-----------------

Each tool run writes to ``results/<tool>_output_N`` (``N`` auto-increments by
scanning the filesystem, so repeated runs never collide). Every node's inputs and
outputs are appended to a JSON state file as it runs, so intermediate products are
preserved and inspectable even when they aren't the declared output.

Output typing matters downstream: an output declared ``type = "dir"`` is returned
as the directory path (so a connector can look inside it), not flattened into the
list of files within it.
