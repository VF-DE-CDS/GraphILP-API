.. _network:

*********
Networks
*********

Graphs are very well-suited as models for networks. Typical questions in this area aim at the distribution of some commodity through a network. Such commodities could be water in a pipe network, bandwidth in a communications network, or goods in a supply chain.

Steiner Tree Problem
--------------------

The `Steiner Tree Problem in graphs <https://en.wikipedia.org/wiki/Steiner_tree_problem#Steiner_tree_in_graphs_and_variants>`__ asks for the shortest connection of a subset of the node set. This subset is usually called the set of terminals. While this problem is easy when all nodes are terminals (minimum spanning tree) or when there are only two terminals (shortest path), it is NP-hard otherwise. This means that unless P=NP, we expect any algorithm to become very slow for large instances. For this reason, we provide different formulations of the problem which may be more or less suitable for solving different types of instances.

Cycle-based constraint system
=============================
.. automodule:: graphilp.network.Steiner
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Linear-size constraint system
=============================
.. automodule:: graphilp.network.Steiner_Linear
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution   

Flow-based constraint system
=============================
.. automodule:: graphilp.network.Steiner_Flow
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Prize Collecting Steiner Tree (PCST)
------------------------------------

.. automodule:: graphilp.network.PCST
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Linear-size constraint system
=============================

.. automodule:: graphilp.network.PCST_Linear
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Travelling Salesman Problem (TSP)
---------------------------------

Asymmetric TSP
==============
.. automodule:: graphilp.network.max_atsp
   :noindex:
   
.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.network.min_atsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
.. automodule:: graphilp.network.atsp_DT_formulation 
   :noindex:

.. autosummary::
   :nosignatures:

   createGenModel
   extractSolution

.. automodule:: graphilp.network.gen_path_atsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createGenModel
   extractSolution
   
.. automodule:: graphilp.network.max_patsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.network.min_patsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Metric TSP
==============   
.. automodule:: graphilp.network.max_ptsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.network.min_ptsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.network.max_tsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.network.min_tsp
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

   
Details
------------

.. automodule:: graphilp.network.Steiner
   :members:

.. automodule:: graphilp.network.Steiner_Linear
   :members:   
   
.. automodule:: graphilp.network.Steiner_Flow   
   :members:   

.. automodule:: graphilp.network.PCST
   :members:   
   
.. automodule:: graphilp.network.PCST_Linear
   :members:   

.. automodule:: graphilp.network.max_atsp
   :members:   
   
.. automodule:: graphilp.network.min_atsp
   :members:

.. automodule:: graphilp.network.atsp_DT_formulation
   :members:

.. automodule:: graphilp.network.gen_path_atsp
   :members:

.. automodule:: graphilp.network.max_patsp
   :members:

.. automodule:: graphilp.network.min_patsp
   :members:

.. automodule:: graphilp.network.max_ptsp
   :members:

.. automodule:: graphilp.network.min_ptsp
   :members:

.. automodule:: graphilp.network.max_tsp
   :members:

.. automodule:: graphilp.network.min_tsp
   :members: