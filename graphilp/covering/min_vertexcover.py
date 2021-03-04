from gurobipy import *
from graphilp.covering import warmstart_vertex_covering as ws


def createModel(G, wsMaxMatch:bool = False, wsLPApprox:bool = False):    
    r""" Create an ILP for the minimum vertex cover problem
    
    :param G: an unweighted ILPGraph                    
    :param warmstart: choose whether to use a warmstart
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v\in V} x_v\\
            \text{s.t.}&&\\
            \forall \{k,j\} \in E: & x_k + x_j \geq 1 & \text{(at least one vertex in each edge is covered)}
            \end{align*}
    """        
   # Create model    
    m = Model("graphilp_min_vertex_cover")    

    node_list = list(G.G.nodes())
    x = m.addVars(G.G.nodes(), vtype = GRB.BINARY)
    
    if (wsMaxMatch == True or wsLPApprox == True):
        # Perform Maximal Matching Heuristic if wanted
        if (wsMaxMatch == True):
            wsNodesHeur = ws.maxMatch(G)
            if wsNodesHeur != None:
                print("Setting Warmstart Nodes...")
                warmstartNodes = set.copy(wsNodesHeur)
                print("Successful!")
        else:
            wsNodesHeur = None
        # Perform LP Approximation Heuristic if wanted
        if (wsLPApprox == True):
            wsNodesApprox = ws.approxLP(G)
            # If both Heuristics were performed they have to be compared to each other.
            # They can only be compard if the are not None, i.e. both Heuristics have returned a valid solution
            if wsNodesApprox != None and wsNodesHeur != None:
                # If the Approximation Heuristic is in fact better, change warmstartNodes to the Approximation solution
                if (len(wsNodesHeur) > len(wsNodesApprox)):
                    warmstartNodes = set.copy(wsNodesApprox)
            elif wsNodesApprox != None:
                warmstartNodes = set.copy(wsNodesApprox)
        try:
            for i in node_list:
                if(i in warmstartNodes):
                    x[i].Start = 1
        except:
            print("Something with the Heuristics went wrong. Continuing without Heuristics ")
    
    m.update()            

    m.setObjective(sum(x[i] for i in node_list), GRB.MINIMIZE)
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges():            
        m.addConstr(x[int(u)] + x[int(v)] >= 1 )    
    
    m.optimize()
    return x

def extractSolution(G, model):    
    """ Get a list of vertices comprising a vertex cover  
    
    :param G: an ILPGraph            
    :param model: a solved Gurobi model for minimum vertex cover                    
    
    :return: a list of vertices comprising a minimum vertex cover
    """    
    vertex_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return vertex_nodes

def createModelWeighted(G):
    r""" Create an ILP for the minimum vertex cover problem 
    
    :param G: a weighted ILPGraph   
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_    

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v\in V} w_v x_v\\
            \text{s.t.}&&\\
            \forall \{k,j\} \in E: & x_k + x_j \geq 1 & \text{(at least one vertex in each edge is covered)}
            \end{align*}

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
