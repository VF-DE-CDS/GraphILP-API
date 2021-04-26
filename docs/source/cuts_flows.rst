.. _cuts_flows:

***************
Cuts and Flows
***************

`Cuts <https://en.wikipedia.org/wiki/Cut_(graph_theory)>`__ in graphs describe how removing some elements of the graph result in a certain segmentation of the graph. A typical question is what the minimal number of edges is that need to be removed in order for a connected graph to be separated into two connected components.

`Flows <https://en.wikipedia.org/wiki/Flow_network>`__ are functions on the edges of directed graphs describing how much of a commodity is flowing from one vertex to another. Often, the condition that the total flow into a vertex equals the total flow out of the vertex is imposed. The prototypical questions is how much flow can be transferred from one given vertex to another when the flow must not exceed the edge weights of the graph.

Cuts and flows between vertices are related through the famous `max-flow min-cut theorem <https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem>`__. This theorem is implied by linear programming `duality <https://en.wikipedia.org/wiki/Duality_(optimization)>`__.

Bisection
=========

Graph bisection deals with the question of how to cut edges in a connected graph so that the resulting graph has two connected components. Typically, there are restrictions to the type of the resulting connected components such as that their sizes should be as close to each other as possible. The optimisation objective is usually the sum of the weights of those edges that are removed to bisect the graph.

.. automodule:: graphilp.cuts_flows.bisection
   :noindex:

.. autosummary::
   :nosignatures:
   
   create_model
   extract_solution

Cuts
====

A cut in a graph is a partition of the vertex set into two disjoint subsets.
A `maximum cut <https://en.wikipedia.org/wiki/Maximum_cut>`__ is a cut for which the total weight of the edges between the two sets is maximal.

.. automodule:: graphilp.cuts_flows.max_cut
   :noindex:

.. autosummary::
   :nosignatures:
   
   create_model
   extract_solution
   
The minimum uncut problem is complementary to the maximum cut problem. It asks for a cut that minimises the total number of edges which are not cut.   

.. automodule:: graphilp.cuts_flows.min_uncut
   :noindex:

.. autosummary::
   :nosignatures:
   
   create_model
   extract_solution
   
Heuristics
----------

The methods in this section provide approximate solutions to the max cut problem constituting admissible solutions from which to start the exact optimisation.

.. automodule:: graphilp.cuts_flows.heuristics.maxcut_greedy
   :noindex:

.. autosummary::
   :nosignatures:
   
   get_heuristic

Flows
=====
.. automodule:: graphilp.cuts_flows.min_k_flow
   :noindex:

.. autosummary::
   :nosignatures:
   
   create_model
   extract_solution

Details
=======

.. automodule:: graphilp.cuts_flows.bisection
   :members:
  
.. automodule:: graphilp.cuts_flows.max_cut
   :members:
   
.. automodule:: graphilp.cuts_flows.heuristics.maxcut_greedy   
   :members:
   
.. automodule:: graphilp.cuts_flows.min_uncut
   :members:

.. automodule:: graphilp.cuts_flows.min_k_flow
   :members:
   