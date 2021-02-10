from gurobipy import *


def createModel(G):    
    """ Create an ILP for the maximum independet set problem                
    Arguments:            G -- a ILPGraph                    
    Returns:            a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_max_ind_set")        
    # Add variables for edges and nodes    
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))    
    m.update()    
    nodes = G.node_variables        
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges:                
        m.addConstr(nodes[u] + nodes[v] >= 1 )    
    # set optimisation objective: minimize cardinality of the vertex cover   
    m.setObjective( gurobipy.quicksum(nodes), GRB.MINIMIZE)      

    return m

def extractSolution(G, model):    
    """ Get a list of vertices comprising a maximum independent set           
    Arguments:            G     -- a ILPGraph            
    model -- a solved Gurobi model for maximum independent set                    
    Returns:            a list of vertices comprising a maximum independent set    """    
    ind_set = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]        
    
    return ind_set
