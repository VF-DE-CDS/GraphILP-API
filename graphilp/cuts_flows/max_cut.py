from gurobipy import *


def createModel(G):    
    """ Create an ILP for the maximum cut problem
    
    :param G: an ILPGraph                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """        
    # Create model    
    m = Model("graphilp_max_cut")     
    
    # Add variables for edges and nodes    
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY )) 
    m.update()    
    
    nodes = G.node_variables  
    edges = G.edge_variables
    
    # Create constraints    
    ## for every edge, the nodes must be seperated    
    for (u, v) in G.G.edges:                
        m.addConstr( edges[(u, v)]  <= nodes[v] +nodes[u] )
        m.addConstr( edges[(u, v)] <= 2 - nodes[v] - nodes[u] ) 
    # set optimisation objective: maximize the cardinality of the number of edges in the cut  
    
    m.setObjective( gurobipy.quicksum(  edges), GRB.MAXIMIZE)   

    return m


def extractSolution(G, model):    
    """ Get a list of vertices comprising a maximum cut of G   
    
    :param G: an ILPGraph            
    :param model: a solved Gurobi model for max cut                    
    
    :return: a list of vertices comprising a maximum cut of G
    """    
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return cut_nodes
