.. _subsuper:

********************
Sub- and supergraphs
********************

Many questions in graph theory are asking revolving around the relationship between a graph and its sub-structures. Optimisation problems typically ask for the largest subgraph of a given type like a clique or a planar graph. They may also ask for the minimal modification necessary to ensure the existence of such a subgraph.

Clique
------

A clique is a fully connected graph. Hence, the fully connected graph :math:`K_n` is also called an :math:`n`-clique.
The maximum clique problem is asking for the largest :math:`n` such that a given a has an :math:`n`-clique as a subgraph.

Packing version

.. automodule:: graphilp.sub_super.max_clique_pack
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Covering version

.. automodule:: graphilp.sub_super.max_clique_cover
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Details
-------

.. automodule:: graphilp.sub_super.max_clique_pack
    :members:

.. automodule:: graphilp.sub_super.max_clique_cover
    :members:
   