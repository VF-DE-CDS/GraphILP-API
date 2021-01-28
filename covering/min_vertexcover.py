from gurobipy import *


def createModel(G):    
    """ Create an ILP for the minimum vertex cover problem                
    Arguments:            G -- an unweighted ILPGraph                    
    Returns:            a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        
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
    """ Get a list of vertices comprising a vertex cover           
    Arguments:            G     -- a ILPGraph            
    model -- a solved Gurobi model for minimum vertex cover                    
    Returns:            a list of vertices comprising a minimum vertex cover    """    
    vertex_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return vertex_nodes

def createModelWeighted(G):
    """ Create an ILP for the minimum vertex cover problem                
    Arguments:              G -- a weighted ILPGraph                    
    Returns:                a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        
    # Add variables for edges and nodes    
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))    
    node_list = G.G.nodes()
    weights = []
    for node in node_list(data=True):
        weights.append(node[1]['prize'])
    m.update()    
    nodes = G.node_variables        
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges:                
        m.addConstr(nodes[u] + nodes[v] >= 1 )    
    # set optimisation objective: minimize cardinality of the vertex cover   
    m.setObjective( gurobipy.quicksum(nodes*weights), GRB.MINIMIZE)      

    return m
