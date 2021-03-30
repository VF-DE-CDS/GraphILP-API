from gurobipy import *
import networkx as nx

edge2var = None

def callbackCycle(model, where):
    """ Callback inserts constraints to forbid more than one cycle in solution candidates
    
    :param model: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    :param where: a Gurobi callback parameter indicating from which step of the optimisation the callback
        originated
    """
    global edge2var
    
    if where == gurobipy.GRB.Callback.MIPSOL:
        activeEdges = model.cbGetSolution(model._x)
        edges = []
        cycles = []
        for k, v in activeEdges.items():
            if (0 < v):
                edges.append(k)
        G2 = nx.Graph()
        G2.add_edges_from(edges)
        conComp = nx.connected_components(G2)
        for comp in conComp:
            cycles.append(comp)

        neededEdges = []
        neededEdgesRev = []
        try:
            listLenghts = [len(x) for x in cycles]
            minLenIndex = listLenghts.index(min(listLenghts))
            smallestCycle = cycles[minLenIndex]
        except:
            pass
        
        # Remove cycles if there are more than 1 
        if len(cycles) > 1:
            # Get all the edges from the first cycle to all others by joining the both nodepairs.
            for idx, cycle in enumerate(cycles):
                if  (idx == minLenIndex):
                    continue
                else:
                    for nodeOne in smallestCycle:
                        for nodeTwo in cycle:
                            neededEdges.append((nodeOne, nodeTwo))
                            neededEdgesRev.append((nodeTwo, nodeOne))
            
            model.cbLazy(quicksum(edge2var[edge] for edge in neededEdges) >= 1)
            model.cbLazy(quicksum(edge2var[edge] for edge in neededEdgesRev) >= 1)
            
    return

def createModel(G, direction=GRB.MAXIMIZE, metric='', weight='weight', start=None, end=None,
                warmstart=[]):
    r""" Create an ILP for the min/max Path asymmetric TSP 
    
    This formulation enforces that the solution has at least one cycle.
    A callback will detect if there is more than one cycle and adds constraints to explicity forbid this.
    Together, this ensures that the solution is a valid tour.
    
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph` 
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param metric: 'metric' for symmetric problem otherwise asymmetric problem
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param start: require the TSP path to start at this node
    :param end: require the TSP path to end at this node
    :param warmstart: a list of edges forming a tree in G connecting all terminals

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    Callbacks:
        This model uses callbacks which need to be included when calling Gurobi's optimize function:
    
        model.optimize(callback = :obj:`callbackCycle`)

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
            \end{align*}   
    """
    global edge2var
    
    # create model
    m = Model("graphilp_path_atsp")
    
    if metric == 'metric':
        G.G = G.G.to_directed()
        G.G.add_edges_from([(v,u) for (u,v) in G.G.edges()])
        
    # add variables for edges   
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edge2var = G.edge_variables
    edges = G.edge_variables
    var2edge = dict(zip(edges.values(), edges.keys()))
    nbr_nodes = G.G.number_of_nodes()

    # create constraints
    # degree condition
    if ((start is None) and (end is None)):
        for node in G.G.nodes():
            # Exactly one outgoing connection from every node
            m.addConstr(quicksum( [edges[e] for e in G.G.edges(node)]) == 1)
            # Exactly one incoming connection to every node
            m.addConstr(quicksum( [edges[e] for e in G.G.in_edges(node)]) == 1)                        
    else:
        for node in G.G.nodes():     
            if node != start:
                m.addConstr(quicksum([edges[e] for e in G.G.edges() if e[1] == node]) == 1)
            if node != end:
                m.addConstr(quicksum([edges[e] for e in G.G.edges() if e[0] == node]) == 1)
            if node == start:
                m.addConstr(quicksum([edges[e] for e in G.G.edges() if e[1] == node]) == 0)
            if node == end:
                m.addConstr(quicksum([edges[e] for e in G.G.edges() if e[0] == node]) == 0)

    # set optimisation objective: find the min / max weight round tour in G
    m.setObjective(quicksum([edges[(u,v)] * w[weight] for (u,v,w) in G.G.edges(data=True)]), direction)

    # set warmstart
    if len(warmstart) > 0:
        
        # initialise warmstart by excluding all edges from solution
        for edge_var in edges.values():
            edge_var.Start = 0
            
        # set edges along warmstart tour
        for edge in warmstart:
            edges[edge].Start = 1

        m.update()
        
    # prepare for callbacks
    m._x = G.edge_variables
    m.Params.lazyConstraints = 1

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
