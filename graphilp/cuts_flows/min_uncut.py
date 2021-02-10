# +
from gurobipy import *
from itertools import combinations
import networkx as nx

def createModel(G):
    """ Create an ILP for the min uncut problem
        
    :param G: a weighted ILPGraph                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = Model("graphilp_min_uncut")
    
    # Add variables for nodes
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    nodes = G.node_variables
    
    GC = nx.complement(G.G)
            
    edges = m.addVars(GC.edges(), vtype=gurobipy.GRB.BINARY)
    m.update()        
    
    # Create constraints
    ## for every edge, the nodes must be seperated in the complement graph
    for (u, v) in GC.edges():
            m.addConstr( edges[(u, v)]  <= nodes[v] +nodes[u] )
            m.addConstr( edges[(u, v)] <= 2 - nodes[v] - nodes[u] ) 

    # set optimisation objective: maximize the cardinality of the number of edges in the cut of the complement graph  
    m.setObjective( gurobipy.quicksum(  edges), GRB.MAXIMIZE)  
    
    return m

def extractSolution(G, model):
    """ Get a list of vertices comprising a maximum cut of the complement graph
    
        :param G: a weighted ILPGraph
        :model: a solved Gurobi model for minimum uncut problem
            
        :return: a list of vertices comprising a cut and a solution to the minimum uncut problem
    """
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]
    
    return cut_nodes
