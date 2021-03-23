.. _packing:

*********
Packing
*********

Packing problems on graphs deal with the question of how to identify as many disjoint sub-structures of a given type as possible in a given graph. For example, we could look for finding as many pairwise non-connected vertices as possible (maximum independent set) or for as many disjoint cliques as possible (clique packing problem).

.. tikz:: Example of clique packing for 3-cliques (aka triangles).
   :align: center
   
   \tikzset{main node/.style={circle,draw,font=\sffamily\bfseries}}
   \tikzset{scale=0.5}

   \node[main node,fill=red!50] (1) at (-2, 0) {};
   \node[main node,fill=red!50] (2) at (2, 0) {};
   \node[main node,fill=red!50] (3) at (1, 1.732) {};
   \node[main node,fill=red!50] (4) at (-1, 1.732) {};
   \node[main node,fill=red!50] (5) at (1, -1.732) {};
   \node[main node,fill=red!50] (6) at (-1, -1.732) {};

   \node[main node,fill=red!50] (7) at (3.464, 2) {};
   \node[main node] (8) at (0, 4) {};
   \node[main node,fill=red!50] (9) at (-3.464, 2) {};
   \node[main node] (10) at (-3.464, -2) {};
   \node[main node,fill=red!50] (11) at (0, -4) {};
   \node[main node] (12) at (3.464, -2) {};

   \path[every node/.style={font=\sffamily\small}]
   (1) edge[red!50,line width=1] (4)
       edge (6)
       edge[red!50,line width=1] (9)
       edge (10)
   (2) edge[red!50,line width=1] (3)
       edge (5)
       edge[red!50,line width=1] (7)
       edge (12)
   (3) edge (4)
       edge[red!50,line width=1] (7)
       edge (8)
   (4) edge (8)
       edge[red!50,line width=1] (9)
   (5) edge[red!50,line width=1] (6)
       edge[red!50,line width=1] (11)
       edge (12)
   (6) edge (10)
       edge[red!50,line width=1] (11)
   ;


Independent set
===============

An independet set in the vertex set of a graph is a subset of the vertices in which no pair of vertices is connected by an edge.

.. automodule:: graphilp.packing.max_indset
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Clique packing
==============

.. automodule:: graphilp.packing.clique_packing
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Set packing
===========

.. automodule:: graphilp.packing.set_packing
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Details
=======

.. automodule:: graphilp.packing.max_indset
    :members:

.. automodule:: graphilp.packing.clique_packing
    :members:
    
.. automodule:: graphilp.packing.set_packing
    :members:    