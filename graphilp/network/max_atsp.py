from gurobipy import *
import networkx as nx
from graphilp.network import gen_path_atsp

def createModel(G):
    """ Create an ILP for the max asymmetric TSP 
        
        Arguments:
            G -- a weighted ILPGraph
            
        Returns:
            a Gurobi model 
    """
    
    # Create model
    m = gen_path_atsp.createGenModel(G,'max','')
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for max asymmetric TSP 
            
        Returns:
            the edges of an optimal tour in G 
    """
    
    tour = gen_path_atsp.extractSolution(G, model)
    
    return tour
