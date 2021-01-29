from gurobipy import *
from covering import warmstart_vertex_covering as ws


def createModel(G, warmstart:bool = False):    
    """ Create an ILP for the minimum vertex cover problem                
    Arguments:                  G -- an unweighted ILPGraph                    
    Returns:                	a Gurobi model     
    """        
   # Create model    
    m = Model("graphilp_min_vertex_cover")    
    warmstartNodes = set()    
    # Add variables for edges and nodes    
    if (warmstart == True):
        wsNodesHeur = ws.maximalMatching(G)
        wsNodesApprox = ws.createApproximation(G)
        if (len(wsNodesHeur) < len(wsNodesApprox)):
            warmstartNodes = wsNodesHeur
        else:
            warmstartNodes = wsNodesApprox
    
    node_list = G.G.nodes()
    nodesAmount = len(node_list)
    x = m.addVars(G.G.nodes(), vtype = GRB.BINARY)
    for i in range(nodesAmount):
        if(i in warmstartNodes):
            x[i].Start = 1
    
    m.update()            
    vars = m.getVars()
    for i in range(len(vars)):
        if (vars[i].Start == 1):
            print("foundi t at" + str(i))
    m.setObjective(sum(x[i] for i in range(nodesAmount)), GRB.MINIMIZE)
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges():            
        m.addConstr(x[int(u)] + x[int(v)] >= 1 )    
    
    m.optimize()
    return x

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
