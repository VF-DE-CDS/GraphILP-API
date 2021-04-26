from gurobipy import GRB
from graphilp.network import gen_path_atsp


def create_model(G, direction=GRB.MAXIMIZE, weight='weight', warmstart=[]):
    """ Create an ILP for the min/max metric TSP

    Uses :py:func:`graphilp.network.gen_path_atsp.create_model` to set up the problem.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param warmstart: a list of edges forming a tour

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    Example:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_tsp_art.png
             - `TSP art <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/TSP%20Art.ipynb>`_

               Transform an image into line art that can be drawn without lifting the pencil.
    """
    # Create model
    m = gen_path_atsp.create_model(G, direction, 'metric', weight=weight, warmstart=warmstart)

    return m


def extract_solution(G, model):
    """ Get the optimal tour in G

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for min/max metric TSP

    :return: the edges of an optimal tour in G
    """
    tour = gen_path_atsp.extract_solution(G, model)

    return tour
