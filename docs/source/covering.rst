.. _covering:

*********
Covering
*********

Covering problems in graphs ask for substructures in the graph such that all other elements of the graph are adjacent to this substructure. For example, in a minimal vertex cover we look for a subset of the vertex set such that all other vertices are connected to the selected ones by an edge.

Dominating set
-------------------
A `dominating set <https://en.wikipedia.org/wiki/Dominating_set>`_ in a graph :math:`G = (V, E)` is a subset :math:`S \subset V` of the vertex set such that each vertex :math:`v \in V` is connected to a vertex :math:`s \in S` by an edge :math:`\{s,v\} \in E`. 

.. tikz:: A minimum dominating set (red vertices) of the Petersen graph.
   :align: center
   
   \tikzset{main node/.style={circle,draw,font=\sffamily\bfseries}}
   \tikzset{scale=0.5}

   \node[main node,fill=red!50] (1) at (4, 0) {};
   \node[main node,fill=blue!50] (2) at (1.236, 3.8) {};
   \node[main node,fill=red!50] (3) at (-3.236, 2.351) {};
   \node[main node,fill=blue!50] (4) at (-3.236, -2.351) {};
   \node[main node,fill=blue!50] (5) at (1.236, -3.8) {};

   \node[main node,fill=blue!50] (6) at (2.0, 0.0) {};
   \node[main node,fill=red!50] (7) at (0.618, 1.902) {};
   \node[main node,fill=blue!50] (8) at (-1.618, 1.176) {};
   \node[main node,fill=blue!50] (9) at (-1.618, -1.176) {};
   \node[main node,fill=blue!50] (10) at (0.618, -1.902) {};

   \path[every node/.style={font=\sffamily\small}]
   (1) edge (2) edge (6) 
   (2) edge (3) edge (7)
   (3) edge (4) edge (8)
   (4) edge (5) edge (9)
   (5) edge (1) edge (10)
   (6) edge (8)
   (7) edge (9)
   (8) edge (10)
   (9) edge (6)
   (10) edge (7);

.. automodule:: graphilp.covering.min_dom_set
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Edge dominating set
-------------------

An `edge dominating set <https://en.wikipedia.org/wiki/Edge_dominating_set>`_ in a graph :math:`G = (V, E)` is a subset :math:`S \subset E` of the edge set such that each edge in :math:`E` is adjacent to an edge in :math:`S`.

.. image:: images/illustration_edge_dom.png
    :height: 200

.. automodule:: graphilp.covering.min_edge_dom
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Vertex cover
------------

A `vertex cover <https://en.wikipedia.org/wiki/Vertex_cover>`_ in a graph :math:`G = (V, E)` is a subset :math:`S \subset V` of the vertex set such that for each edge :math:`\{u, v\} \in E` at least one of its vertices is in :math:`S`: :math:`\{u,v\} \cap S \neq \emptyset`. 

.. image:: images/illustration_covering.png
    :height: 200

.. automodule:: graphilp.covering.min_vertexcover
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution
   
Warmstarts
==========
.. automodule:: graphilp.covering.warmstart_vertex_covering
   :noindex:

.. autosummary::
   :nosignatures:

   createApproximation

Details
------------

.. automodule:: graphilp.covering.min_dom_set
  :members:
  
.. automodule:: graphilp.covering.min_edge_dom
  :members:  
  
.. automodule:: graphilp.covering.min_vertexcover
  :members:    
  
.. automodule:: graphilp.covering.warmstart_vertex_covering
  :members:      