from gurobipy import GRB
from graphilp.network import gen_path_atsp


def create_model(G, start, end, direction=GRB.MAXIMIZE, weight='weight', warmstart=[]):
    """ Create an ILP for the min/max asymmetric path TSP

    Uses :py:func:`graphilp.network.gen_path_atsp.createModel` to set up the problem.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param start: a vertex of the graph G in which the ATSP path should start
    :param end: a vertex of the graph G in which the ATSP path should end
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param warmstart: a list of edges forming a tour

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    # Create model
    m = gen_path_atsp.createModel(G, direction, '', weight=weight, start=start, end=end, warmstart=warmstart)

    return m


def extract_solution(G, model):
    """ Get the optimal tour in G

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for min/max asymmetric path TSP

    :return: the edges of an optimal tour in G
    """
    tour = gen_path_atsp.extractSolution(G, model)

    return tour
