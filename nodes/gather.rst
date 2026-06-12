Gather nodes
============

A gather node runs a tool **once per item** of an upstream collection and gathers the
per-run outputs into parallel lists. Use it when an upstream produces many items
but the tool's input is ``cardinality = "one"``, i.e. the tool can only consume
one item per invocation.

.. code-block:: python

   rf   = g.add_node("rfdiffusion")                  # output `designs`: a dir of N backbones
   mpnn = g.add_gather_node("proteinmpnn", split_key="designs")
   g.add_edge((rf, mpnn))

``split_key`` names the upstream output key whose value is the collection to fan
out over.

Finding ``split_key``
---------------------

``split_key`` is the **name of the upstream tool's output** that holds the
collection, read it from the *producing* tool's manifest, not the consuming
tool's inputs::

    bv show rfdiffusion --format json

RFdiffusion declares one output, ``designs`` (a directory of backbones), so
``split_key="designs"``. The rule of thumb: pick the upstream output that is a
directory or list of the items you want to process one at a time. You also need a
gather node (rather than a plain :doc:`tool node <tool>`) precisely when that upstream
output is a collection but the downstream tool's matching input is
``cardinality = "one"``.

.. mermaid::

   flowchart LR
       RF["rfdiffusion<br/>runs once → N backbones"] --> SC{{"scatter<br/>split into N inputs"}}
       K(["knobs<br/>num_seq_per_target=2"]) -. into every run .-> RUNS
       SC --> RUNS["proteinmpnn ×N<br/>one backbone each"]
       RUNS --> GA{{"gather<br/>N outputs → lists"}}
       GA --> OUT(["sequences: [s1 … sN]"])

Execution
---------

For ``rfdiffusion → gather(proteinmpnn)`` with N backbones, the executor:

#. runs the single upstream **once**, producing e.g. ``{"designs": "/dir"}``;
#. calls the edge's **scatter connector** once on that output; it returns a *list*
   of N per-item input dicts, e.g. ``[{"pdb_path": f0}, {"pdb_path": f1}, …]``;
#. runs the tool once per dict via ``run_one``, each invocation gets its own
   numbered output directory, and the tool itself is unaware of the fan-out;
#. **gathers** the N result dicts into a dict of lists,
   ``{"sequences": [s0, s1, …]}``.

Shared parameters (a separate input node) are applied verbatim into every run, not
scattered:

.. code-block:: python

   mpnn_in = g.add_input_node(num_seq_per_target="2", sampling_temp="0.1")
   g.add_edge((rfdiffusion, proteinmpnn), (mpnn_in, proteinmpnn))

A gather node requires **exactly one** non-input upstream (the collection source);
additional input nodes for scalars are allowed.

How the split happens
---------------------

The split is done by the **connector**, not by hand-written code. Because the
downstream is a gather node, the connector is generated with a scatter instruction
and returns ``list[dict]`` instead of a single dict. It infers the items from the
real runtime data: a directory's files (grouped by shared prefix, excluding
trajectory/temp artifacts), a list's elements, or a multi-record file's records.
There is no fixed splitter table, a new collection shape works because the
connector writes the appropriate crawling code (:doc:`../connectors`).

The connector is generated **once per edge** and reused for all N items; an
N-way fan-out does not generate N connectors.

Chaining gather nodes
---------------------

``gather`` emits lists, so a gather node can feed another gather node:

.. code-block:: python

   proteinmpnn = g.add_gather_node("proteinmpnn", split_key="designs")
   colabfold   = g.add_gather_node("colabfold",   split_key="sequences")
   g.add_edge((rfdiffusion, proteinmpnn))
   g.add_edge((proteinmpnn, colabfold))

The second scatter receives an already-gathered list of directories and flattens it
into per-item inputs. This two-level pattern (backbones → one sequence design each
→ one structure prediction each) is the basis of the self-consistency example
(:doc:`../examples`).

Reference
---------

.. autoclass:: biocomposer.GatherNode
   :members: run_one, gather
   :noindex:
