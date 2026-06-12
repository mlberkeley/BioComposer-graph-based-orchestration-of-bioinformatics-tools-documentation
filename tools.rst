Tools and the registry
======================

biocomposer uses the **bv** registry and client by default. Because tools are just 
container images plus a manifest, the catalogue can wrap images from anywhere, 
purpose-built images, `BioContainers <https://biocontainers.pro>`_, or plain Docker Hub images.

.. note::

   The bv registry and ``bv`` client are developed by Tejas Prabhune,
   see the `bv-registry project <https://tejasprabhune.github.io/bv-registry/>`_.
   biocomposer builds on bv for tool resolution, container management, and execution.

Finding tools
-------------

List or inspect tools with the ``bv`` client:

.. code-block:: bash

    bv search clustalo            # find a tool
    bv show proteinmpnn           # human-readable manifest
    bv show proteinmpnn --format json   # machine-readable (use this for input keys)

``bv show`` is the authoritative source for a tool's **input names**, the exact
keyword names you pass to ``add_input_node``. See :ref:`input-keys`.

Anatomy of a manifest
---------------------

A manifest has four parts: identity, **inputs**, **outputs**, and how to run it
(image + entrypoint). Below is the real ProteinMPNN manifest, trimmed to the
essential fields.

Identity
~~~~~~~~

.. code-block:: toml

    [tool]
    id          = "proteinmpnn"
    version     = "1.0.1"
    description = "Deep-learning protein sequence design (inverse folding) ..."
    homepage    = "https://github.com/dauparas/ProteinMPNN"
    license     = "MIT"

Inputs
~~~~~~

Each input is one ``[[tool.inputs]]`` block. These are the fields that matter when
building a pipeline:

.. code-block:: toml

    [[tool.inputs]]
    name        = "pdb_path"      # the key you use in add_input_node / connectors
    type        = "pdb"           # what kind of data it is
    required    = true            # must be supplied
    cardinality = "one"           # exactly ONE item (not a list)
    description = "Single input backbone to redesign (--pdb_path) ..."

    [[tool.inputs]]
    name        = "num_seq_per_target"
    type        = "file"
    required    = true
    cardinality = "one"
    description = "Number of sequences to generate per backbone (--num_seq_per_target) ..."

The four fields, and why they matter:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Field
     - Meaning
   * - ``name``
     - The key. ``add_input_node(pdb_path=...)`` must use this exact name; the
       connector maps onto it; and the command template references it as
       ``{pdb_path}``.
   * - ``type``
     - The data kind (``pdb``, ``fasta``, ``dir``, ``file``, …). Connectors use it
       to decide whether a format conversion is needed between two tools.
   * - ``required``
     - Whether the tool fails without it. Optional inputs can be omitted.
   * - ``cardinality``
     - ``one`` = a single item; ``many`` = a list. **This is the field that decides
       whether you need a gather node.** If an upstream produces many items but this
       input is ``cardinality = "one"``, the tool consumes one at a time, wrap it
       in a :doc:`nodes/gather` to run it once per item.

Outputs
~~~~~~~

Outputs use the same fields. ProteinMPNN produces one output directory:

.. code-block:: toml

    [[tool.outputs]]
    name        = "sequences"
    type        = "dir"
    required    = true
    cardinality = "one"
    description = "Output folder; contains seqs/<name>.fa with the designed sequences ..."

An output's ``name`` is the key you see in the result dict, and, for a gather node,
the value you pass as ``split_key`` when this collection should be fanned out.

Image and entrypoint
~~~~~~~~~~~~~~~~~~~~~

These tell biocomposer which container to run and how to invoke the tool. The
``args_template`` is the command line, with ``{slot}`` placeholders that match
input/output ``name`` fields:

.. code-block:: toml

    [tool.image]
    backend   = "docker"
    reference = "docker.io/rosettacommons/proteinmpnn:latest"

    [tool.hardware.gpu]
    required     = false
    min_vram_gb  = 4
    cuda_version = "11.3"

    [tool.entrypoint]
    command       = "python"
    args_template = "/app/proteinmpnn/protein_mpnn_run.py --pdb_path {pdb_path} --out_folder {sequences} --num_seq_per_target {num_seq_per_target} --sampling_temp {sampling_temp}"

    [tool.binaries]
    exposed = ["python", "protein_mpnn_run.py", "parse_multiple_chains.py"]

At run time the placeholders are filled: ``{pdb_path}`` becomes the staged input
file, ``{sequences}`` the output directory, and scalar inputs like
``{num_seq_per_target}`` their literal values. A placeholder that nothing supplies
is stripped, which is why an input whose **key doesn't match a slot** silently has
no effect.

The ``exposed`` binaries list is what makes ``entrypoint_override`` possible: a
single tool image (e.g. ViennaRNA) can expose several programs, and you select one
with ``entrypoint_override="RNAplot"``. See :doc:`nodes/tool`.

How the manifest shapes your pipeline
-------------------------------------

Reading a manifest answers the three questions that come up while wiring a
pipeline:

#. **What do I name my input-node keys?** → the input ``name`` fields.
#. **Do I need a gather node here?** → is the downstream input ``cardinality = "one"``
   while the upstream produces many? If so, yes.
#. **What comes out, and under what key?** → the output ``name`` fields (and the
   one you'd use as ``split_key``).
