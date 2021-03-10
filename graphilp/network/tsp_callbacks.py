from gurobipy import *
import networkx as nx

edge2var = None

def callbackCycle(model, where):
    global edge2var
    if where == gurobipy.GRB.Callback.MIPSOL:
        activeEdges = model.cbGetSolution(model._x)
        edges = []
        for k, v in activeEdges.items():
            if (0 < v):
                edges.append(k)
        G2 = nx.Graph()
        G2.add_edges_from(edges)
        cyc = nx.cycle_basis(G2)
        neededEdges = []
        neededEdgesRev = []
        
        # Remove cycles if there are more than 1 
        if len(cyc) > 1:
            # Get all the edges from the first cycle to the second by joining the both nodepairs.
            for nodeOne in cyc[0]:
                for nodeTwo in cyc[1]:
                    neededEdges.append((nodeOne, nodeTwo))
                    neededEdgesRev.append((nodeTwo, nodeOne))
            
            model.cbLazy(gurobipy.quicksum(edge2var[edge] for edge in neededEdges) >= 1)
            model.cbLazy(gurobipy.quicksum(edge2var[edge] for edge in neededEdgesRev) >= 1)

def createGenModel(G, type_obj, metric, start=None, end=None):
    global edge2var
    r""" Create an ILP for the min/max Path asymmetric TSP 
        
    :param G: a weighted ILPGraph
    :param type_obj: choose whether to minimise or maximise the weight of the path
    :param metric: 'metric' for symmetric problem otherwise asymmetric problem
    :param start: require the TSP path to start at this node
    :param end: require the TSP path to end at this node

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
        
    ILP: 
        Let :math:`s` be the start node (if it is specified) and :math:`e` the end node.
    
        .. math::
            :nowrap:

            \begin{align*}
            \min / \max \sum_{(i,j) \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            \forall v \in V \setminus \{s, e\}: \sum_{(u, v) \in R}x_{uv} = 1 && \text{(Exactly one outgoing edge.)}\\
            \forall v \in V \setminus \{s, e\}: \sum_{(v, u) \in R}x_{vu} = 1 && \text{(Exactly one incoming edge.)}\\
            \sum_{(s, v) \in R}x_{sv} = 1 && \text{(Exactly one outgoing edge from start node.)}\\
            \sum_{(v, e) \in R}x_{ve} = 1 && \text{(Exactly one incoming edge to end node.)}\\
            \sum_{(v, e) \in R}x_{ve} = 1 && \text{(Increasing labels along path.)}\\
            \sum_{(v, e) \in R}x_{ve} = 1 && \text{(Increasing labels along path.)}\\
            \end{align*}   
    """
    
    # Create model
    m = Model("graphilp_path_atsp")
    
    if metric == 'metric':
        G_d = G.G.to_directed()
        G_r = G_d.reverse(copy=True)
        G.G = nx.compose(G_d, G_r)
    
    # Add variables for edges   
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    edge2var = G.edge_variables
    nbr_nodes = G.G.number_of_nodes()
    nodes = list(G.G.nodes())
    # Add variables for labels
    label_vars = m.addVars(G.G.nodes(), lb = 0, ub = nbr_nodes - 1, vtype=gurobipy.GRB.INTEGER)
    m.update()
    
    edges = G.edge_variables
    
    # Create constraints
    # degree condition
    if ((start is None) and (end is None)):
        for node in G.G.nodes():
            # Only one outgoing connection from every node
            m.addConstr(gurobipy.quicksum( [edges[e] for e in G.G.edges() if e[0] == node]) == 1)
            # Only one incoming connection to every node
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
                
    """ # Create permutations via labels         
    if (start is None) and (end is None):        
        m.addConstr( label_vars[nodes[0]]  ==  0 )
        for (u,v) in G.G.edges():
            if (v != nodes[0]):
                m.addConstr(label_vars[u] - label_vars[v] + nbr_nodes * edges[(u,v)]  <= nbr_nodes - 1 )
    else:
        m.addConstr( label_vars[start]  ==  0 )
        m.addConstr( label_vars[end]  ==  nbr_nodes - 1 )
        for (u,v) in G.G.edges():
            if (v != start):
                m.addConstr(label_vars[u] - label_vars[v] + nbr_nodes * edges[(u,v)]  <= nbr_nodes - 1 ) """
        

    # set optimisation objective: find the min / max round tour in G
    if type_obj == 'min': 
        m.setObjective(gurobipy.quicksum( [edges[(u,v)]* w['weight'] for (u,v,w) in G.G.edges(data=True)] ), GRB.MINIMIZE)
    if type_obj == 'max': 
        m.setObjective(gurobipy.quicksum( [edges[(u,v)]* w['weight'] for (u,v,w) in G.G.edges(data=True)] ), GRB.MAXIMIZE)
    

    m._u = label_vars
    m._x = G.edge_variables

    m.Params.lazyConstraints = 1
    m.optimize(callbackCycle)

    return m

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for min/max Path asymmetric TSP 
            
        :return: the edges of an optimal tour/path in G 
    """
    edge_vars = G.edge_variables
    
    tour = [edge  for edge, edge_var in edge_vars.items() if edge_var.X > 0.5]
    
    return tour



