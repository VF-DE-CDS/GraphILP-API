from gurobipy import *
import networkx as nx

def createGenModel(G, type_obj, metric, start= None, end= None ):
    """ Create an ILP for the min/max Path asymmetric TSP 
        
        Arguments:
            G -- a weighted ILPGraph
            
        Returns:
            a Gurobi model 
    """
    
    # Create model
    m = Model("graphilp_path_atsp")
    
    if metric == 'metric':
        G_d = G.G.to_directed()
        G_r = G_d.reverse(copy=True)
        G.G = nx.compose(G_d, G_r)
    
    # Add variables for edges   
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    
    nbr_nodes = G.G.number_of_nodes()
    
    # Add variables for labels
    label_vars = m.addVars(G.G.nodes(), lb = 0, ub = nbr_nodes - 1, vtype=gurobipy.GRB.INTEGER)
    m.update()
    
    edges = G.edge_variables
    
    # Create constraints
    # degree condition
    if ((start is None) and (end is None)):
        for node in G.G.nodes():
            m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[0] == node]) == 1)
            m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[1] == node]) == 1)            
    else:
        for node in G.G.nodes():
            if node != start:
                m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[1] == node]) == 1)
            if node != end:
                m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[0] == node]) == 1)
            if node == start:
                m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[1] == node]) == 0)
            if node == end:
                m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[0] == node]) == 0)
                
    # Create permutations via labels         
    if (start is None) and (end is None):        
        m.addConstr( label_vars[0]  ==  0 )
        for (u,v) in G.G.edges():
            if (v != 0):
                m.addConstr(label_vars[u] - label_vars[v] + nbr_nodes * edges[(u,v)]  <= nbr_nodes - 1 )
    else:
        m.addConstr( label_vars[start]  ==  0 )
        m.addConstr( label_vars[end]  ==  nbr_nodes -1 )
        for (u,v) in G.G.edges():
            if (v != start):
                m.addConstr(label_vars[u] - label_vars[v] + nbr_nodes * edges[(u,v)]  <= nbr_nodes - 1 )
        

    # set optimisation objective: find the min / max round tour in G
    if type_obj == 'min': 
        m.setObjective(gurobipy.quicksum( [edges[(u,v)]* w['weight'] for (u,v,w) in G.G.edges(data=True)] ), GRB.MINIMIZE)
    if type_obj == 'max': 
        m.setObjective(gurobipy.quicksum( [edges[(u,v)]* w['weight'] for (u,v,w) in G.G.edges(data=True)] ), GRB.MAXIMIZE)
    
    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for min/max Path asymmetric TSP 
            
        Returns:
            the edges of an optimal tour/path in G 
    """
    edge_vars = G.edge_variables
    
    tour = [      edge  for edge, edge_var in edge_vars.items() if edge_var.X > 0.5]
    
    return tour



