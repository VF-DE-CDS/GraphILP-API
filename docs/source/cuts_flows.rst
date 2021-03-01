.. _cuts_flows:

***************
Cuts and Flows
***************

Cuts and flows between nodes are related through the famous `max-flow min-cut theorem <https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem>`__. This theorem is implied by linear programming `duality <https://en.wikipedia.org/wiki/Duality_(optimization)>`__.

Bisection
---------

.. automodule:: graphilp.cuts_flows.bisection
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Cuts
-----

.. automodule:: graphilp.cuts_flows.max_cut
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

.. automodule:: graphilp.cuts_flows.min_uncut
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution

Flows
-----
.. automodule:: graphilp.cuts_flows.min_k_flow
   :noindex:

.. autosummary::
   :nosignatures:
   
   createModel
   extractSolution



Details
------------

.. automodule:: graphilp.cuts_flows.bisection
   :members:
  
.. automodule:: graphilp.cuts_flows.max_cut
   :members:
   
.. automodule:: graphilp.cuts_flows.min_uncut
   :members:

.. automodule:: graphilp.cuts_flows.min_k_flow
   :members:
   