from gurobipy import *
import math


def createModel(G):    
    """ Create an ILP for the maximum bisection problem
    
    :param G: an ILPGraph                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """        
    # Create model    
    m = Model("graphilp_max_bisection")        
    # Add variables for edges and nodes    
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.node_variables
    
    number_nodes = len(G.G.nodes())
    bound_upper = math.ceil( number_nodes/2 )
    bound_lower = math.floor( number_nodes/2 )

    # Create constraints
    # balanced solutions are needed
    m.addConstr( gurobipy.quicksum(nodes) <= bound_upper )
    m.addConstr( gurobipy.quicksum(nodes) >= bound_lower )

    ## for every edge, the nodes must be seperated    
    for (u, v) in G.G.edges():                
        m.addConstr( edges[(u, v)]  <= nodes[v] +nodes[u] )
        m.addConstr( edges[(u, v)] <= 2 - nodes[v] - nodes[u] ) 
   
    # set optimisation objective: maximize the cardinality of the number of edges in the cut   
    m.setObjective( gurobipy.quicksum(  edges), GRB.MAXIMIZE)   

    return m


def extractSolution(G, model):    
    """ Get a list of vertices comprising a maximum balanced cut of G 
    
    :param G: an ILPGraph            
    :param model: a solved Gurobi model for the maximum bisection problem  
    
    :return: a list of vertices comprising a maximum balanced cut of G
    """    
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return cut_nodes
