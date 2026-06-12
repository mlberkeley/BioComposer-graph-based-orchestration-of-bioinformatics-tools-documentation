Example pipelines
=================


In the diagrams: rounded boxes are **inputs**, plain boxes are **tools**, a box
marked *(map)* runs **once per item**, and a diamond is a **decision loop**.


Walkthrough 1: align a set of sequences
----------------------------------------

**Task:** align a set of protein sequences with Clustal Omega.

.. mermaid::

   flowchart LR
       IN(["family.fasta"]) --> CL["clustalo"]
       CL --> OUT(["alignment"])

**Step 1: inspect the tool.** Every input-node key must match a name the tool
declares, so start by reading the manifest:

.. code-block:: console

    $ bv show clustalo --format json

.. code-block:: json

    {
      "tool": {
        "id": "clustalo",
        "description": "Clustal Omega: fast and scalable multiple sequence aligner ...",
        "image": { "reference": "quay.io/biocontainers/clustalo:1.2.4--h503566f_10" },
        "inputs": [
          {
            "name": "sequences",
            "type": "fasta",
            "cardinality": "one",
            "description": "Unaligned input sequences (protein or nucleotide)"
          }
        ],
        "outputs": [
          { "name": "alignment", "type": "msa", "cardinality": "one",
            "description": "Multiple sequence alignment" }
        ],
        "entrypoint": {
          "command": "clustalo",
          "args_template": "--threads={cpu_cores} -i {sequences} -o {alignment} --outfmt=fa"
        }
      }
    }

**Step 2: pick the inputs.** Clustal Omega declares one input, ``sequences``
(``required`` is implied for the only input; in tools with several inputs, supply
every one marked ``"required": true``). Its single output is ``alignment``.

**Step 3: put your file in** ``inputs/``. The CLI uploads the ``inputs/`` folder,
which appears in the run as ``/vol/inputs/``::

    inputs/family.fasta

**Step 4: write the pipeline.** The input-node key is exactly the manifest name,
``sequences``:

.. code-block:: python

    from biocomposer import Graph

    g = Graph()
    seqs  = g.add_input_node(sequences="/vol/inputs/family.fasta")  # key = manifest input name
    align = g.add_node("clustalo")
    g.add_edge((seqs, align))
    g.set_output_node(align)
    print(g.execute())

**Step 5: run it**::

    biocomp run run/align.py --env .env

The result dict is keyed by the tool's output name, ``alignment``.


Walkthrough 2: design a sequence for each generated backbone
-------------------------------------------------------------

**Task:** generate protein backbones with RFdiffusion, then design an amino-acid
sequence for each one with ProteinMPNN. This introduces two things: a tool with
**several inputs** (some required), and a **gather node**, whose ``split_key`` is also
read from a manifest.

.. mermaid::

   flowchart LR
       RFI(["input_pdb, contigs,<br/>num_designs"]) --> RF["rfdiffusion"]
       KN(["num_seq_per_target,<br/>sampling_temp"]) -.-> MP
       RF -->|"designs (N backbones)"| MP["proteinmpnn (map)"]
       MP --> OUT(["sequences: [...]"])

**Step 1: inspect both tools.**

.. code-block:: console

    $ bv show rfdiffusion --format json

.. code-block:: text

    {
      "tool": {
        "id": "rfdiffusion",
        "inputs": [
          { "name": "input_pdb", "type": "pdb", "cardinality": "one", "required": false, ... },
          { "name": "contigs",   "type": "file", "cardinality": "one", "required": true,  ... },
          { "name": "num_designs","type": "file","cardinality": "one", "required": true,  ... }
        ],
        "outputs": [
          { "name": "designs", "type": "dir", "cardinality": "one",
            "description": "Output directory; one design_<n>.pdb backbone per design ..." }
        ]
      }
    }

.. code-block:: console

    $ bv show proteinmpnn --format json

.. code-block:: text

    {
      "tool": {
        "id": "proteinmpnn",
        "inputs": [
          { "name": "pdb_path",          "type": "pdb",  "cardinality": "one", "required": true,  ... },
          { "name": "num_seq_per_target","type": "file", "cardinality": "one", "required": true,  ... },
          { "name": "sampling_temp",     "type": "file", "cardinality": "one", "required": true,  ... }
        ],
        "outputs": [
          { "name": "sequences", "type": "dir", "cardinality": "one", ... }
        ]
      }
    }

**Step 2: pick the inputs.** Supply every ``"required": true`` input. For
RFdiffusion that's ``contigs`` and ``num_designs`` (``input_pdb`` is optional but
used here). For ProteinMPNN: ``pdb_path``, ``num_seq_per_target``,
``sampling_temp``.

**Step 3: why a gather node, and what** ``split_key`` **is.** RFdiffusion's output
``designs`` is ``cardinality = "one"`` *but it is a directory of many backbones*,
while ProteinMPNN's ``pdb_path`` takes ``cardinality = "one"``, one backbone per
run. So ProteinMPNN is a **gather node**, and ``split_key`` is the **upstream output
name** holding the collection to fan out over, here, ``"designs"``. (You read
``split_key`` from the *producing* tool's outputs, not the consuming tool's
inputs.)

**Step 4: put inputs in** ``inputs/``::

    inputs/1l9h.pdb

**Step 5: write the pipeline.** Note the two input nodes: one feeds RFdiffusion,
the other carries ProteinMPNN's shared parameters. Every key below is a manifest
input name.

.. code-block:: python

    from biocomposer import Graph

    g = Graph()
    rf_in = g.add_input_node(
        input_pdb="/vol/inputs/1l9h.pdb",   # rfdiffusion input names
        contigs="[150-150]",
        num_designs="2",
    )
    rfdiffusion = g.add_node("rfdiffusion")
    g.add_edge((rf_in, rfdiffusion))

    mpnn_in = g.add_input_node(             # proteinmpnn input names (shared scalars)
        num_seq_per_target="2",
        sampling_temp="0.1",
    )
    proteinmpnn = g.add_gather_node("proteinmpnn", split_key="designs")  # = rfdiffusion's output name
    g.add_edge((rfdiffusion, proteinmpnn), (mpnn_in, proteinmpnn))
    g.set_output_node(proteinmpnn)
    print(g.execute())

**Step 6: run** (GPU tool → use Modal)::

    biocomp run --modal run/design.py --env .env

ProteinMPNN runs once per backbone; the result gathers each run's ``sequences``
output into a list.


Multiple sequence alignment, then trim, then fold
-------------------------------------------------

**Task:** align an RNA family, trim noisy columns, predict a consensus secondary
structure, and draw it.

A four-tool chain. Each edge's connector handles the format changes between the
aligner, the trimmer, and the ViennaRNA programs.

.. mermaid::

   flowchart LR
       IN(["rna_family.fasta"]) --> CL["clustalo"]
       CL --> TR["trimal"]
       TR --> AF["RNAalifold"]
       AF --> PL["RNAplot"]

.. code-block:: python

    from biocomposer import Graph

    g = Graph()
    inp        = g.add_input_node(sequences="/vol/inputs/rna_family.fasta")
    clustalo   = g.add_node("clustalo")
    trimal     = g.add_node("trimal",
                            args_override="-in {alignment} -out {trimmed} -fasta -gappyout")
    rnaalifold = g.add_node("viennarna", entrypoint_override="RNAalifold",
                            args_override="-f F --noPS {sequences} > {structures}")
    rnaplot    = g.add_node("viennarna", entrypoint_override="RNAplot",
                            args_override="{sequences} > {structures}")

    g.add_edge((inp, clustalo), (clustalo, trimal),
               (trimal, rnaalifold), (rnaalifold, rnaplot))
    g.set_output_node(rnaplot)
    print(g.execute())

``viennarna`` exposes several programs, selected per node with
``entrypoint_override`` (see :doc:`nodes/tool`).


Backbones → sequences → predicted structures
--------------------------------------------

**Task:** generate backbones, design sequences for each, then fold every designed
sequence into a 3-D structure.

ColabFold predicts structure from *sequence*, so backbones first become sequences
(ProteinMPNN), then each sequence is folded (ColabFold). Two map stages chain: the
first fans over backbones, the second over the sequences the first produced.

.. mermaid::

   flowchart LR
       RFI(["1l9h.pdb"]) --> RF["rfdiffusion"]
       RF -->|"designs"| MP["proteinmpnn (map)"]
       MP -->|"sequences"| CF["colabfold (map)"]
       CF --> OUT(["predicted structures"])

.. code-block:: python

    import json
    from biocomposer import Graph

    g = Graph()
    rf_in = g.add_input_node(
        input_pdb="/vol/inputs/1l9h.pdb", contigs="[150-150]",
        num_designs="2", config_name="base", diffuser_T="20",
    )
    rfdiffusion = g.add_node("rfdiffusion")
    g.add_edge((rf_in, rfdiffusion))

    mpnn_in = g.add_input_node(num_seq_per_target="2", sampling_temp="0.1")
    proteinmpnn = g.add_gather_node("proteinmpnn", split_key="designs")
    g.add_edge((rfdiffusion, proteinmpnn), (mpnn_in, proteinmpnn))

    cf_in = g.add_input_node(
        model_type="auto", num_models="1", num_recycles="3",
        msa_mode="single_sequence", num_seeds="1",
        rank_by="plddt", stop_at_score="100",
    )
    colabfold = g.add_gather_node("colabfold", split_key="sequences")
    g.add_edge((proteinmpnn, colabfold), (cf_in, colabfold))
    g.set_output_node(colabfold)
    print(json.dumps(g.execute(), indent=2, default=str))


Self-consistency: does a design fold back to its intended shape?
----------------------------------------------------------------

**Question:** for each de-novo backbone, do the designed sequences fold back into
that backbone? This is the standard **self-consistency RMSD** filter for protein
designs.

The pipeline is the two-stage fan-out above
(``rfdiffusion -> map(proteinmpnn) -> map(colabfold)``), followed by a geometry
step that superposes each predicted structure onto its source backbone and reports
the deviation (low = the design folds as intended).

.. mermaid::

   flowchart LR
       RF["rfdiffusion"] -->|"backbones"| MP["proteinmpnn (map)"]
       MP -->|"sequences"| CF["colabfold (map)"]
       RF -. compare .-> SC
       CF --> SC{{"scRMSD<br/>predicted vs. backbone"}}
       SC --> OUT(["pass / fail per design"])

The fan-out uses two gather nodes as above; the RMSD comparison is a short Python
step over the results (a *join* between each prediction and its source backbone,
which the graph does not express as an edge). The full script is
``run/run_scrmsd_pipeline.py``.

.. note::

   This pipeline is heavy, ColabFold runs once per designed sequence. Use
   ``--modal`` with a GPU and start small (``num_designs=2``, ``diffuser_T=20``).
