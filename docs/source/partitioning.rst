.. _partitioning:

************
Partitioning
************

`Graph partitioning <https://en.wikipedia.org/wiki/Graph_partition>`__ deals with ways to partition the vertex set or the edge set of a graph into mutually exclusive groups. These may be used to reduce problems on large graphs to problems on smaller graphs derived from the parts of the partition.

Vertex colouring
================

A vertex `colouring <https://en.wikipedia.org/wiki/Graph_coloring>`__ of a graph is an assignment of colours to the vertices such that adjacent vertices get different colours. A minimal vertex colouring is such a colouring using the minimal possible number of colours. For example, trees can be coloured using only two colours whereas a complete graph on :math:`n` vertices needs exactly :math:`n` colours.

.. tikz:: Examples of minimal vertex colourings
   :align: left

   \tikzset{main node/.style={circle,draw,font=\sffamily\bfseries}}

   \node[main node,fill=red!50] (1) at (3, 4) {};
   \node[main node,fill=green!50] (2) at (2,3) {};
   \node[main node,fill=green!50] (3) at (4,3) {};
   \node[main node,fill=red!50] (4) at (1, 2) {};
   \node[main node,fill=red!50] (5) at (3, 2) {};
   \node[main node,fill=red!50] (6) at (5, 2) {};
   \node[main node,fill=green!50] (7) at (4, 1) {};
   \node[main node,fill=green!50] (8) at (6, 1) {};

   \path[every node/.style={font=\sffamily\small}]
    (1) edge node {} (2)
        edge node {} (3)
    (2) edge node {} (4)
        edge node {} (5)
    (3) edge node {} (6)
    (6) edge node {} (7)
        edge node {} (8);

   \node[main node,fill=red!50] (9) at (9, 3.4) {};
   \node[main node,fill=green!50] (10) at (9, 2) {};
   \node[main node,fill=blue!50] (11) at (10.2124, 1.3) {};
   \node[main node,fill=black!50] (12) at (7.7876, 1.3) {};

   \path[every node/.style={font=\sffamily\small}]
    (9) edge node {} (10)
        edge node {} (11)
        edge node {} (12)
    (10) edge node {} (11)
        edge node {} (12)
    (11) edge node {} (12);

.. automodule:: graphilp.partitioning.min_vertex_coloring
   :noindex:

.. autosummary::
   :nosignatures:

   create_model
   extract_solution

Heuristics
----------

Approximate solutions can be used as a warmstart in the optimisation, usually leading to shorter running times.
Constant factor approximations also imply a lower bound on the solution.

.. automodule:: graphilp.partitioning.heuristics.vertex_coloring_greedy
   :noindex:

.. autosummary::
   :nosignatures:

    get_heuristic

Details
=======

.. automodule:: graphilp.partitioning.min_vertex_coloring
   :members:

.. automodule:: graphilp.partitioning.heuristics.vertex_coloring_greedy
   :members:
