.. _imports:

*********
Imports
*********

Internally, GraphILP wraps the `NetworkX <https://networkx.org>`__ classes to represent graphs.
This makes it particularly easy to import graphs through the functionality provided by this package.
There are, however, a number of file formats specific to the types of optimisation problems covered by GraphILP.
This module therefore offers import filters for such file formats.

ILPGraph
--------

The ILPGraph class takes care of both the graph instance used in an optimisation problem and the variables of the integer linear program used to solve it.

.. automodule:: graphilp.imports.ilpgraph
   :noindex:

.. autosummary::
   :nosignatures:
   
   ILPGraph
   ILPGraph.setNXGraph
   ILPGraph.setEdgeVars
   ILPGraph.setNodeVars
   ILPGraph.setLabelVars
   
Networkx
--------
   
.. automodule:: graphilp.imports.networkx
   :noindex:

.. autosummary::
   :nosignatures:
   
   read
   col_file_to_networkx
      
stp format
----------

.. automodule:: graphilp.imports.readFile
   :noindex:

.. autosummary::
   :nosignatures:

   edges_to_networkx
   stp_to_networkx
   mis_to_networkx

Details
-------

.. automodule:: graphilp.imports.ilpgraph
    :members:
        
.. automodule:: graphilp.imports.networkx
    :members:

.. automodule:: graphilp.imports.readFile
    :members: