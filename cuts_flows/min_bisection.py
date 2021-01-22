from gurobipy import *
import math


def createModel(G):    
    """ Create an ILP for the minimum bisection problem                
    Arguments:            G -- an ILPGraph                    
    Returns:            a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_bisection")        
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
   
    # set optimisation objective: minimize the cardinality of the number of edges in the cut   
    m.setObjective( gurobipy.quicksum(  edges), GRB.MINIMIZE)   

    return m


def extractSolution(G, model):    
    """ Get a list of vertices comprising a minimum balanced cut of G          
    Arguments:            G     -- a ILPGraph            
    model -- a solved Gurobi model for the minimum bisection problem                    
    Returns:            a list of vertices comprising a minimum balanced cut of G    """    
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return cut_nodes
