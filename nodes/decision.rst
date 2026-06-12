Decision nodes
==============

A decision node re-runs an upstream tool until a **scored condition** is met. It
adds a bounded feedback loop to the graph: run the upstream, score its output,
and, if the condition fails, modify the upstream's inputs and run again.

.. code-block:: python

   from biocomposer import Graph
   from biocomposer.helpers.condition import Condition

   def count_sequences(seqkit_output):              # score the output
       out = seqkit_output.get("output")
       with open(out) as f:
           return sum(1 for line in f if line.startswith(">"))

   def fewer_sequences(inputs, scorer_output):      # adjust when not met
       n = int(inputs.get("n", "5"))
       return {"n": str(max(n - 1, 1))}

   decision = g.add_decision_node(
       score_fn=count_sequences,
       conditions=[Condition("<=", 2)],
       modifier_tool=fewer_sequences,
   )
   g.add_edge((seqkit, decision))
   g.set_output_node(decision)

A decision node requires at least one non-input upstream, the tool whose output
is scored and whose inputs are modified each iteration.

The loop
--------

.. mermaid::

   flowchart LR
       U["upstream tool"] --> S{"score_fn → score"}
       S -- conditions met --> OUT(["return output"])
       S -- not met --> M["modifier → new inputs"]
       M --> U

Each iteration: score the current output, check the conditions, and if they fail,
compute modified inputs and re-run the upstream. The loop is capped at **100
iterations**; if it exhausts them without satisfying the conditions it returns the
last output and logs a warning.

Conditions
----------

:class:`~biocomposer.Condition` wraps a comparison applied to the score. Pass a
list, **all** must hold to exit:

.. code-block:: python

   conditions=[Condition(">=", 3)]
   conditions=[Condition(">", 0), Condition("<=", 10)]

Supported comparators: ``>``, ``<``, ``>=``, ``<=``, ``==``, ``!=``.

The score
---------

``score_fn`` may be **either** a Python callable **or** the name of a registry
tool. This is the first of the two callable-or-tool choices a decision node makes.

**Callable score**, a function ``score_fn(upstream_output) -> number``. It receives
the upstream's output dict and returns the score directly:

.. code-block:: python

   def count_sequences(seqkit_output):
       return _count(seqkit_output["output"])

   g.add_decision_node(score_fn=count_sequences, ...)

The function's source is shown to the connector that feeds it, so the connector
maps the upstream output onto exactly the keys the function reads.

**Tool score**, a registry tool name. The tool is installed and run on the
upstream output, and a numeric score is extracted from *its* output: the value
under a ``score`` key if present, otherwise the single numeric value in the output
(an error is raised if the tool emits more than one number, since the score would
be ambiguous):

.. code-block:: python

   g.add_decision_node(score_fn="my_scoring_tool", ...)

The modifier
------------

``modifier_tool`` likewise may be **either** a callable **or** a registry tool, the
second callable-or-tool choice. It produces the changed inputs fed back to the
upstream for the next iteration.

**Callable modifier**, a function ``modifier(current_inputs, scorer_output) ->
dict``. It reads the upstream's current inputs and the latest score/output and
returns the keys to change; the returned dict is merged over the current inputs. No
connector is involved, because the dict already holds every key:

.. code-block:: python

   def fewer_sequences(inputs, scorer_output):
       n = int(inputs.get("n", "5"))
       return {"n": str(max(n - 1, 1))}

**Tool modifier**, a registry tool name. Because two tools' schemas must be bridged,
the loop generates three connectors the first time it runs: the upstream inputs →
modifier, the scorer output → modifier, and the modifier output → back to the
upstream's inputs. The modifier tool runs each iteration, and its result is mapped
back into the upstream's input dictionary:

.. code-block:: python

   g.add_decision_node(score_fn=count_designs,
                       conditions=[Condition(">=", 3)],
                       modifier_tool="my_modifier_tool")

The four combinations
---------------------

Score and modifier are chosen independently, giving four valid forms:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - ``score_fn``
     - ``modifier_tool``
     - Connectors involved
   * - callable
     - callable
     - none for the loop (both read/write keys directly)
   * - callable
     - tool
     - three, bridging upstream/scorer ↔ modifier tool
   * - tool
     - callable
     - the upstream → scoring-tool edge
   * - tool
     - tool
     - the scoring edge plus the three modifier-bridging connectors

Reference
---------

.. autoclass:: biocomposer.DecisionNode
   :members: check_all_conditions, extract_score
   :noindex:

.. autoclass:: biocomposer.Condition
   :members: check
   :noindex:
