.. _cuts_flows:

***************
Cuts and Flows
***************

`Cuts <https://en.wikipedia.org/wiki/Cut_(graph_theory)>`__ in graphs describe how removing some elements of the graph result in a certain segmentation of the graph. A typical question is what the minimal number of edges is that need to be removed in order for a connected graph to be separated into two connected components.

`Flows <https://en.wikipedia.org/wiki/Flow_network>`__ are functions on the edges of directed graphs describing how much of a commodity is flowing from one node to another. Often, the condition that the flow into a node equals the flow out of the node is imposed. The prototypical questions is how much flow can be transferred from one given node to another when the flow must not exceed the edge weights of the graph.

Cuts and flows between nodes are related through the famous `max-flow min-cut theorem <https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem>`__. This theorem is implied by linear programming `duality <https://en.wikipedia.org/wiki/Duality_(optimization)>`__.

Bisection
---------

Graph bisection deals with the question of how to cut edges in a connected graph so that the resulting graph has two connected components. Typically, there are restrictions to the type of the resulting connected components such as that their sizes should be as close to each other as possible. The optimisation objective is usually the sum of the weights of those edges that are removed to bisect the graph.

.. automodule:: graphilp.cuts_flows.bisection
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Cuts
-----

.. automodule:: graphilp.cuts_flows.max_cut
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.cuts_flows.min_uncut
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Flows
-----
.. automodule:: graphilp.cuts_flows.min_k_flow
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution



Details
------------

.. automodule:: graphilp.cuts_flows.bisection
   :members:
  
.. automodule:: graphilp.cuts_flows.max_cut
   :members:
   
.. automodule:: graphilp.cuts_flows.min_uncut
   :members:

.. automodule:: graphilp.cuts_flows.min_k_flow
   :members:
   