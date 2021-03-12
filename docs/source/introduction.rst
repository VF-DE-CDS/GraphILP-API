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

Examples
--------
The best way to get startet with GraphILP is through one of our examples:

.. list-table:: List of examples
   :widths: 50 50
   :header-rows: 0

   * - .. image:: images/example_bipartite.png
     - `Two-coloured partitions <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/2-coloured%20partitions.ipynb>`_
     
       Learn how to use perfect matching in bipartite graphs to find a way 
       
       to connect n random blue points in the plane to n random orange points without crossings.
   * - .. image:: images/example_mapcolouring.png
     - `Map colouring <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/Map%20colouring.ipynb>`_
     
       Colour a map with as few colours as possible such that 
       
       no two adjacent areas get the same colour.
   * - .. image:: images/example_steiner.png
     - `Steiner trees <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/SteinerTreesOnStreetmap.ipynb>`_
     
       Find the shortest tree connecting a given set of nodes in a graph.
   * - .. image:: images/example_vertexcolour.png
     - `Minimum vertex cover <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/min_vertex_coloring_example.ipynb>`_
     
       A simple example finding the minimal number of colours needed
       
       to colour circle graphs such that neighbouring nodes get different colours.

   * - .. image:: images/example_mindomset.png
     - `Minimum dominating set <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/Dominating%20queens.ipynb>`_
     
       Find how many queens are needed to cover all squares on an :math:`n\times n` chessboard.

   * - .. image:: images/example_binarisation.png
     - `Maximum weight cuts <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/Binarisation.ipynb>`_
     
       Use maximum weight cuts for image binarisation.
