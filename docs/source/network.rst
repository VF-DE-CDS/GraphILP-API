.. _network:

*********
Networks
*********

Graphs are very well-suited as models for networks. Typical questions in this area aim at the distribution of some commodity through a network. Such commodities could be water in a pipe network, bandwidth in a communications network, or goods in a supply chain.

.. _steiner tree problem:

Steiner Tree Problem
====================

The `Steiner Tree Problem in graphs <https://en.wikipedia.org/wiki/Steiner_tree_problem#Steiner_tree_in_graphs_and_variants>`__ asks for the shortest connection of a subset of the vertex set. This subset is usually called the set of terminals. While this problem is easy when all vertices are terminals (minimum spanning tree) or when there are only two terminals (shortest path), it is NP-hard otherwise. This means that unless P=NP, we expect any algorithm to become very slow for large instances. For this reason, we provide different formulations of the problem which may be more or less suitable for solving different types of instances.

Cycle-based constraint system
-----------------------------

This formulation ensures that non-connected solutions must contain a cycle. Any cycles appearing in incumbent solutions are then avoided by explicitly adding constraints forbidding them through a callback.

.. automodule:: graphilp.network.steiner
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution
   callback_cycle

Linear-size constraint system
-----------------------------

Introducing vertex labels that increase along edges of the solution in the Steiner tree allows to give a formulation of linear size in the number of edges of the graph. Thus, the use of callback functions can be avoided.

.. automodule:: graphilp.network.steiner_linear
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

There is also a version of this constraint system with somewhat stronger conditions on the labels:

.. automodule:: graphilp.network.steiner_linear_tightened
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Heuristics
----------

Approximate solutions can be used as a warmstart in the optimisation, usually leading to shorter running times.
Constant factor approximations also imply a lower bound on the solution.

.. automodule:: graphilp.network.heuristics.steiner_metric_closure
   :noindex:

.. autosummary::
   :nosignatures:

    get_heuristic


Prize Collecting Steiner Tree (PCST)
====================================

The Prize Collecting Steiner Tree Problem is similar to the :ref:`Steiner Tree Problem` in that a lowest weight network spanning a given set of vertices is desired. However, each vertex comes with a prize value that is counted against the edge weights and it is a part of the problem to select a subset of the vertex set that optimises the total prize against the total cost of the network.

Cycle-based constraint system
-----------------------------

This formulation ensures that non-connected solutions must contain a cycle. Any cycles appearing in incumbent solutions are then avoided by explicitly adding constraints forbidding them through a callback.

.. automodule:: graphilp.network.pcst
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution
   callback_cycle

Linear-size constraint system
-----------------------------

Introducing vertex labels that increase along edges of the solution in the prize collecting Steiner tree allows to give a formulation of linear size in the number of edges of the graph. Thus, the use of callback functions can be avoided.

.. automodule:: graphilp.network.pcst_linear
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Travelling Salesman Problem (TSP)
=================================

The `Travelling Salesman Problem <https://en.wikipedia.org/wiki/Travelling_salesman_problem>`__ is one of the most well-known problems of combinatorial optimisation. Given a list of cities (nodes in a graph) and distances between all pairs of cities (weighted edges in a graph), a solution to this problem is a shortest tour going through all cities but visiting no city twice.

Depending on whether the tour needs to start where it began and on the properties of the distances (for example they can be required to give a metric) there are many variants of the problem.

Asymmetric TSP
--------------

In the asymmetric case, the underlying graph is directed and the distance from A to B may be different from the distance from B to A.

Generic
^^^^^^^

Introducing vertex labels that increase along the edges of the tour allows to give a formulation of linear size in the number of edges of the graph. Thus, the use of callback functions can be avoided.

.. automodule:: graphilp.network.gen_path_atsp
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

This formulation ensures that solutions are a disjoint union of cycles. More than one cycle appearing in incumbent solutions is then avoided by explicitly adding constraints forbidding this through a callback (sub-tour elimination).

.. automodule:: graphilp.network.tsp_callbacks
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

ATSP
^^^^

.. automodule:: graphilp.network.atsp
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

.. automodule:: graphilp.network.atsp_desrochers_laporte
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Path ATSP
^^^^^^^^^

In the path version, the tour may start and end in different vertices.

.. automodule:: graphilp.network.path_atsp
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Metric TSP
----------

In the metric TSP, the edge weights form a metric on the graph, i.e., they obey the triangle inequality :math:`w_{uv} \leq w_{ux} + w_{xv}` for any three vertices :math:`u, v, x`.

.. automodule:: graphilp.network.tsp
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Path TSP
^^^^^^^^

In the path version, the tour may start and end in different vertices.

.. automodule:: graphilp.network.path_tsp
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Heuristics
----------

Approximate solutions can be used as a warmstart in the optimisation, usually leading to shorter running times.
Constant factor approximations also imply a lower bound on the solution.

.. automodule:: graphilp.network.heuristics.tsp_christofides
   :noindex:

.. autosummary::
   :nosignatures:

    get_heuristic

.. automodule:: graphilp.network.heuristics.tsp_nearest_neighbour
   :noindex:

.. autosummary::
   :nosignatures:

    get_heuristic

.. automodule:: graphilp.network.heuristics.tsp_two_opt
   :noindex:

.. autosummary::
   :nosignatures:

    get_heuristic

Details
=======

.. automodule:: graphilp.network.steiner
   :members:

.. automodule:: graphilp.network.steiner_linear
   :members:

.. automodule:: graphilp.network.steiner_linear_tightened
   :members:

.. automodule:: graphilp.network.heuristics.steiner_metric_closure
   :members:

.. automodule:: graphilp.network.pcst
   :members:

.. automodule:: graphilp.network.pcst_linear
   :members:

.. automodule:: graphilp.network.atsp
   :members:

.. automodule:: graphilp.network.atsp_desrochers_laporte
   :members:

.. automodule:: graphilp.network.gen_path_atsp
   :members:

.. automodule:: graphilp.network.path_atsp
   :members:

.. automodule:: graphilp.network.path_tsp
   :members:

.. automodule:: graphilp.network.tsp
   :members:

.. automodule:: graphilp.network.tsp_callbacks
   :members:

.. automodule:: graphilp.network.heuristics.tsp_christofides
   :members:

.. automodule:: graphilp.network.heuristics.tsp_nearest_neighbour
   :members:

.. automodule:: graphilp.network.heuristics.tsp_two_opt
   :members:
