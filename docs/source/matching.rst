.. _matching:

*********
Matching
*********

A `matching <https://en.wikipedia.org/wiki/Matching_(graph_theory)>`__ in a graph :math:`G = (V, E)` is a subset :math:`S \subset E` of edges such no pair of edges in :math:`S` shares a vertex.

.. image:: images/illustration_matching.png
    :height: 200
    
There are numerous natural optimisation questions on matchings, e.g., looking for perfect matchings (covering all vertices), maximal matchings (those that cannot be extended to a larger matching), maximum matchings (maximum cardinality), matching for certain classes of graphs, and matchings that optimise the weights of the edges involved in the matching.

An extensive discussion of matchings can be found in

* Lovász, Plummer: `Matching Theory <https://www.ams.org/publications/authors/books/postpub/chel-367>`__.

General matching
----------------

.. automodule:: graphilp.matching.maxweight
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Bipartite matching
------------------

.. automodule:: graphilp.matching.perfect_bipartite
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Details
-------

.. automodule:: graphilp.matching.maxweight
   :members:

.. automodule:: graphilp.matching.perfect_bipartite
   :members: