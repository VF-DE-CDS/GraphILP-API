.. _introduction:

*************
Introduction
*************

Many optimisation problems on graphs can be solved by `integer linear programming <https://en.wikipedia.org/wiki/Integer_programming>`_ (ILP). The following sketch gives an overview of a general approach for translating graph problems to integer linear programs:

.. image:: images/graph2ilp.png

In this documentation, we will consistently use the following notation to describe our linear programs:

.. list-table:: Notation
   :widths: 20 80
   :header-rows: 0

   * - :math:`x_{v}`
     - Binary node variables: indicator whether node :math:`v` is part of the solution
   * - :math:`x_{uv}`
     - Binary edge variables: indicator whether edge :math:`(u, v)` is part of the solution
     
       (depending on the problem, this may encode directed or undirected edges)
   * - :math:`w_{uv}`
     - Edge weights: usually from the problem instance, can be any number
   * - :math:`\ell_v`
     - Node labels: often used to set up the problem formulation

GraphILP aims at providing ILP formulations for many graph problems and making them easy to use.
The general idea is to input a graph, select an optimisation problem, and run an optimiser on it.

We are currently supporting `Gurobi <https://www.gurobi.com>`_ as an underlying ILP solver and interfacing through its Python API.

How to use
==========
The following figure illustrates the general usage pattern of GraphILP. It consists of creating a problem instance in the form of a graph (or hypergraph), choosing a problem, generating and solving an integer linear programming model for this problem, and finally extracting the solution.

.. tikz:: Usage pattern for GraphILP. Methods in red are from GraphILP, blue indicates a method from the Gurobi API.
   :libs: shapes
   :align: center
   
   \tikzset{main node/.style={circle,draw,font=\sffamily\bfseries}}
   \tikzset{heading node/.style={anchor=west,font=\sffamily\bfseries}}

   \node [heading node] (heading1) at (0, 12) {1) Create graph};
   \node [heading node] (heading2) at (7, 12) {2) Choose problem};
   \node [heading node] (heading3) at (7, 8) {3) Generate model};
   \node [heading node, text=gray] (heading3b) at (0, 6) {3') Create warmstart};
   \node [heading node] (heading4) at (7, 4) {4) Solve model};
   \node [heading node] (heading5) at (7, 2) {5) Extract solution};
   
   \node[main node,fill=blue!50] (6) at (2+2.0, 9.5-0.0) {};
   \node[main node,fill=blue!50] (7) at (2+0.618, 9.5-1.902) {};
   \node[main node,fill=blue!50] (8) at (2-1.618, 9.5-1.176) {};
   \node[main node,fill=blue!50] (9) at (2-1.618, 9.5+1.176) {};
   \node[main node,fill=blue!50] (10) at (2+0.618, 9.5+1.902) {};

   \path[every node/.style={font=\sffamily\small}]
   (6) edge (8)
   (7) edge (9)
   (8) edge (10)
   (9) edge (6)
   (10) edge (7);

   \node (labelG) at (2, 9.5) {G};
   \node [anchor=west, font=\ttfamily] (graphimp) at (0, 7) {\footnotesize G' = imports.networkx.{\color{red} read}(G)};
   
   \node [anchor=north west, font=\sffamily\bfseries, align=left] (problem) at (7, 11)
   {\footnotesize Covering\\
   \footnotesize $\vdots$ -- vertex cover\\
   \footnotesize Partitioning\\
   \footnotesize $\vdots$ -- vertex colouring
   };
   
   \node [ellipse, draw=red, minimum width=75pt, minimum height=25pt] (choose) at (8.7, 10) {};

   \node [anchor=west, font=\ttfamily] (model) at (7, 7) {\footnotesize m = covering.min\_vertexcover.{\color{red} create\_model}(G', {\color{gray} warmstart=w})};

   \node [heading node, text=gray] (heading3bopt) at (0, 5) {\footnotesize (optional)};
   \node [anchor=west, font=\ttfamily, text=gray] (warmstart) at (0, 4) {\footnotesize w = $\cdots$.{\color{red} get\_heuristic(G')}};

   \node [anchor=west, font=\ttfamily] (optimize) at (7, 3) {\footnotesize m.{\color{blue} optimize}()};

   \node [anchor=west, font=\ttfamily] (extract) at (7, 1) {\footnotesize H = covering.min\_vertexcover.{\color{red} extract\_solution}(G', m)};
   
   \path[->,gray,every node/.style={font=\sffamily\small}]
   (graphimp) edge (model)
   (warmstart) edge (model);

   \node[main node,fill=blue!50] (1) at (2+2.0, 1-0.0) {};
   \node[main node,fill=red!50] (2) at (2+0.618, 1-1.902) {};
   \node[main node,fill=red!50] (3) at (2-1.618, 1-1.176) {};
   \node[main node,fill=red!50] (4) at (2-1.618, 1+1.176) {};
   \node[main node,fill=blue!50] (5) at (2+0.618, 1+1.902) {};

   \path[every node/.style={font=\sffamily\small}]
   (1) edge (3)
   (2) edge (4)
   (3) edge (5)
   (4) edge (1)
   (5) edge (2);

   \node (labelH) at (2, 1) {H};

Examples
========
The best way to get started with GraphILP is through one of our examples:

.. list-table:: List of examples
   :widths: 50 50
   :header-rows: 0

   * - .. image:: images/example_bipartite.png
     - `Two-coloured partitions <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/2ColouredPartitions.ipynb>`_
     
       Learn how to use perfect matching in bipartite graphs to find a way 
       
       to connect n random blue points in the plane to n random orange points without crossings.
   * - .. image:: images/example_mapcolouring.png
     - `Map colouring <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/MapColouring.ipynb>`_
     
       Colour a map with as few colours as possible such that 
       
       no two adjacent areas get the same colour.
   * - .. image:: images/example_steiner.png
     - `Steiner trees <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/SteinerTreesOnStreetmap.ipynb>`_
     
       Find the shortest tree connecting a given set of nodes in a graph.
   * - .. image:: images/example_tsp_art.png
     - `TSP art <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/TSPArt.ipynb>`_
     
       Transform an image into line art that can be drawn without lifting the pencil.
   * - .. image:: images/example_vertexcolour.png
     - `Minimum vertex cover <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/MinVertexColouring.ipynb>`_
     
       A simple example finding the minimal number of colours needed
       
       to colour circle graphs such that neighbouring nodes get different colours.

   * - .. image:: images/example_mindomset.png
     - `Minimum dominating set <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/DominatingQueens.ipynb>`_
     
       Find how many queens are needed to cover all squares on an :math:`n\times n` chessboard.

   * - .. image:: images/example_binarisation.png
     - `Maximum weight cuts <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/Binarisation.ipynb>`_
     
       Use maximum weight cuts for image binarisation.

   * - .. image:: images/example_clique_packing.png
     - `Packing tetrahedra <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/CliquePackingExample.ipynb>`_
     
       How many vertex disjoint tetrahedra can you pack in a grid graph?