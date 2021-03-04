from gurobipy import *
import networkx as nx
from graphilp.network import gen_path_atsp

def createModel(G,start,end):
    """ Create an ILP for the min asymmetric Path TSP 
        
        :param G: a weighted ILPGraph
        :param start: a node of the Graph G, in which the ATSP path should start 
        :param end: a node of the Graph G, in which the ATSP path should end
            
        :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = gen_path_atsp.createGenModel(G,'min','',start,end)
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for min asymmetric Path TSP 
            
        :return: the edges of an optimal tour in G 
    """
    
    tour = gen_path_atsp.extractSolution(G, model)
    
    return tour
