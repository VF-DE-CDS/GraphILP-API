.. _subsuper:

********************
Sub- and supergraphs
********************

Many questions in graph theory are revolving around the relationship between a graph and its sub-structures. Optimisation problems typically ask for the largest subgraph of a given type like a clique or a planar graph. They may also ask for the minimal modification necessary to ensure the existence of such a subgraph.

Clique
======

A clique is a fully connected graph. Hence, the fully connected graph :math:`K_n` is also called an :math:`n`-clique.
The maximum clique problem is asking for the largest :math:`n` such that a given graph has an :math:`n`-clique as a subgraph.

Packing version
---------------

The packing version of the integer linear program for max clique is using a straight-forward formulation that tries to find as many vertices as possible such that every pair of selected vertices is connected by an edge.

The :ref:`covering version <covering_version>` below has a tighter integrality gap. (The gap for the packing version is :math:`\geq \frac{n}{2}`.)

.. automodule:: graphilp.sub_super.max_clique_pack
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

.. _covering_version:

Covering version
----------------

The covering version of the integer linear program for max clique is using the connection between clique and vertex cover in the complement. It excludes as few nodes as possible from a clique but needs to exclude at least one node from each pair not connected by an edge. Vertex cover has an `integrality gap <https://en.wikipedia.org/wiki/Vertex_cover#ILP_formulation>`__ of 2.

.. tikz:: A maximal clique (bold edges, blue vertices) and a vertex cover of the complement (red edges, green vertices).
   :align: left

   \tikzset{main node/.style={circle,draw,font=\sffamily\bfseries}}

   \node[main node,fill=blue!50] (1) at (3, 3.4) {};
   \node[main node,fill=blue!50] (2) at (3, 2) {};
   \node[main node,fill=blue!50] (3) at (4.2124, 1.3) {};
   \node[main node,fill=blue!50] (4) at (1.7876, 1.3) {};

   \node[main node,fill=green!50] (5) at (1, 3.4) {};
   \node[main node,fill=green!50] (6) at (5, 3.4) {};
   \node[main node,fill=green!50] (7) at (3, 0) {};

   \path[every node/.style={font=\sffamily\small}]
   (1) edge[line width=1] (2)
       edge[line width=1] (3)
       edge[line width=1] (4)
       edge (5)
       edge (6)
       edge[color=red!50, bend left=25] (7)
   (2) edge[line width=1] (3)
       edge[line width=1] (4)
       edge[color=red!50] (5)
       edge[color=red!50] (6)
       edge[color=red!50] (7)
   (3) edge[line width=1] (4)
       edge[color=red!50, bend left=25] (5)
       edge (6)
       edge (7)
   (4) edge (5)
       edge[color=red!50, bend left=25] (6)
       edge (7)
   (5) edge[color=red!50, bend left=25] (6)
       edge[color=red!50, bend right=45] (7)
   (6) edge[color=red!50, bend left=45] (7);

.. automodule:: graphilp.sub_super.max_clique_cover
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Details
=======

.. automodule:: graphilp.sub_super.max_clique_pack
    :members:

.. automodule:: graphilp.sub_super.max_clique_cover
    :members:
