Adding your own tool
====================

.. note::

   This workflow is still being finalised. The commands below reflect the current
   ``bv`` client; the registry submission process may change.

Anything that runs in a container can be wrapped, custom images, a `BioContainers
<https://biocontainers.pro>`_ image, or a plain `Docker Hub <https://hub.docker.com>`_
image.

Manifest template
-----------------

We have documented the following skeleton. Repeat the ``[[tool.inputs]]`` /
``[[tool.outputs]]`` blocks per field. Every ``{slot}`` in ``args_template`` must
match an input or output ``name``.

.. code-block:: toml

    [tool]
    id          = ""              # unique tool name, e.g. "clustalo"
    version     = ""              # e.g. "1.2.4"
    description = ""              # one or two sentences; the connector LLM reads this
    homepage    = ""
    license     = ""

    [[tool.inputs]]
    name        = ""             # the key users pass to add_input_node / {slot} name
    type        = ""             # pdb | fasta | msa | dir | file | ...
    required    = true           # true if the tool fails without it
    cardinality = "one"          # "one" = single item, "many" = a list
    description = ""             # what it is, its format, the flag it maps to

    # ... one [[tool.inputs]] block per input ...

    [[tool.outputs]]
    name        = ""             # key in the result dict; a gather node's split_key
    type        = ""             # dir | file | pdb | ...
    required    = true
    cardinality = "one"
    description = ""

    [tool.image]
    backend   = "docker"
    reference = ""               # e.g. "docker.io/org/tool:tag"

    [tool.hardware.gpu]
    required     = false         # true for GPU tools
    min_vram_gb  = 0
    cuda_version = ""

    [tool.entrypoint]
    command       = ""           # binary to run, e.g. "clustalo" or "python"
    args_template = ""           # command line; {slot} placeholders = input/output names

    [tool.binaries]
    exposed = []                 # extra binaries selectable via entrypoint_override

Field guidance
--------------

- **cardinality is the field that most affects composition.** Mark an input
  ``"one"`` if the program processes a single item per run (most do); downstream
  users then wrap it in a :doc:`gather node <nodes/gather>` to feed it many items. Mark
  it ``"many"`` only if the program genuinely accepts a list.
- **Descriptions** The connector LLM reads each
  field's ``description`` to map data in and out, state what the field is, its
  format, and the command-line flag it corresponds to.
- **Expose multiple binaries** in ``[tool.binaries].exposed`` when one image ships
  several programs, so users can pick one with ``entrypoint_override`` instead of
  you publishing a tool per binary.
- **Stdout-only tools** can declare an output and redirect into it in the template
  (``... > {structures}``); biocomposer captures stdout into that output slot.

Two complete, real manifests live in the repository root,
``proteinmpnn_1.0.1.toml`` and ``rfdiffusion_1.1.0.toml``, and are the best
references to copy from. See :doc:`tools` for a field-by-field walkthrough.

Validate and publish
--------------------

Check the manifest against the registry's conformance suite, then submit it (this
opens a pull request)::

    bv conformance <path-to-manifest>
    bv publish <tool>

Once published, or while iterating locally, use it like any other tool::

    g.add_node("your_tool")
