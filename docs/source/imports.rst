.. _imports:

*********
Imports
*********

Internally, GraphILP wraps the `NetworkX <https://networkx.org>`__ classes to represent graphs.
This makes it particularly easy to import graphs through the functionality provided by this package.
There are, however, a number of file formats specific to the types of optimisation problems covered by GraphILP.
This module therefore offers import filters for such file formats.

ILPGraph
========

The ILPGraph class takes care of both the graph instance used in an optimisation problem and the variables of the integer linear program used to solve it.

.. automodule:: graphilp.imports.ilpgraph
   :noindex:

.. autosummary::
   :nosignatures:

   ILPGraph
   ILPGraph.set_nx_graph
   ILPGraph.set_edge_vars
   ILPGraph.set_node_vars
   ILPGraph.set_label_vars

NetworkX
========

`NetworkX <https://networkx.org>`__ is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
GraphILP is using NetworkX objects both to represent graphs internally and as an interface to provide problem instances.

.. automodule:: graphilp.imports.networkx
   :noindex:

.. autosummary::
   :nosignatures:

   read

Graph file formats
==================

Many useful benchmark instances for optimisation problems on graphs are available from a variety of sources.
In this section, we provide import filters to create NetworkX Graph objects from various specialised file formats.

.. automodule:: graphilp.imports.graph_formats
   :noindex:

.. autosummary::
   :nosignatures:

   edges_to_networkx
   stp_to_networkx
   mis_to_networkx

ILPSetSystem
============

The ILPSetSystem class takes care of both the set system instance used in an optimisation problem and the variables of the integer linear program used to solve it.

A set system (or undirected `hypergraph <https://en.wikipedia.org/wiki/Hypergraph>`__) consists of a universe :math:`U` generalising the vertex set of a graph and a generalised edge set called the system of the graph. Each element of the system is a subset of the universe and hence generalises the notion of an edge which is a two element subset of the universe.

.. automodule:: graphilp.imports.ilpsetsystem
   :noindex:

.. autosummary::
   :nosignatures:

   ILPSetSystem
   ILPSetSystem.set_universe
   ILPSetSystem.set_system
   ILPSetSystem.set_inc_matrix
   ILPSetSystem.set_system_vars
   ILPSetSystem.set_universe_vars

Details
=======

.. automodule:: graphilp.imports.ilpgraph
    :members:

.. automodule:: graphilp.imports.ilpsetsystem
    :members:

.. automodule:: graphilp.imports.networkx
    :members:

.. automodule:: graphilp.imports.graph_formats
    :members:
