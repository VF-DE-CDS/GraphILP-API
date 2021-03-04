from gurobipy import *
import networkx as nx
from graphilp.network import gen_path_atsp

def createModel(G, start = None, end = None):
    """ Create an ILP for the min metric TSP 
        
        :param G: a weighted ILPGraph
            
        :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = gen_path_atsp.createGenModel(G,'min','metric', start, end)
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for min metric TSP 
            
        :return: the edges of an optimal tour in G 
    """
    
    tour = gen_path_atsp.extractSolution(G, model)
    
    return tour
