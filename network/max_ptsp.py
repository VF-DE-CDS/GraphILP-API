from gurobipy import *
import networkx as nx
from graphilp.network import gen_path_atsp

def createModel(G,start,end):
    """ Create an ILP for the max metric Path TSP 
        
        Arguments:
            G -- a weighted ILPGraph
            start -- a node of the Graph G, in which the TSP path should start 
            end -- a node of the Graph G, in which the TSP path should end
            
        Returns:
            a Gurobi model 
    """
    
    # Create model
    m = gen_path_atsp.createGenModel(G,'max','metric',start,end)
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for min metric Path TSP 
            
        Returns:
            the edges of an optimal tour in G 
    """
    
    tour = gen_path_atsp.extractSolution(G, model)
    
    return tour
