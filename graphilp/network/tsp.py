from gurobipy import *
import networkx as nx
from graphilp.network import gen_path_atsp

def createModel(G, direction=GRB.MAXIMIZE, weight='weight'):
    """ Create an ILP for the min/max metric TSP 
    
    Uses :py:func:`graphilp.network.gen_path_atsp.createModel` to set up the problem.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param weight: name of the weight parameter in the edge dictionary of the graph

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = gen_path_atsp.createModel(G, direction, 'metric', weight=weight)
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for min/max metric TSP 

    :return: the edges of an optimal tour in G 
    """
    
    tour = gen_path_atsp.extractSolution(G, model)
    
    return tour
