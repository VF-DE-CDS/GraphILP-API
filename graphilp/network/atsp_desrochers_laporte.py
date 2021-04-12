from gurobipy import Model, GRB, quicksum


def create_model(G, direction=GRB.MAXIMIZE, metric='', weight='weight', warmstart=[]):
    r""" Faster formulation for the min/max path asymmetric TSP

    Start and end vertices cannot be chosen in this formulation.

    TODO: Update ILP and check use of node "1"

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param metric: 'metric' for symmetric problem otherwise asymmetric problem
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param warmstart: a list of edges forming a tour

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min / \max \sum_{(u,v) \in E} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall v \in V \setminus \{s, e\}: \sum_{(u, v) \in E}x_{uv} = 1 && \text{(exactly one incoming edge)}\\
            \forall v \in V \setminus \{s, e\}: \sum_{(v, u) \in E}x_{vu} = 1 && \text{(exactly one outgoing edge)}\\
            \sum_{(s, v) \in E}x_{sv} = 1 && \text{(exactly one outgoing edge from start vertex)}\\
            \sum_{(v, e) \in E}x_{ve} = 1 && \text{(exactly one incoming edge to end vertex)}\\
            \sum_{(v, s) \in E}x_{vs} = 0 && \text{(no incoming edge to start vertex)}\\
            \sum_{(e, v) \in E}x_{ev} = 0 && \text{(no outgoing edge from end vertex)}\\
            \ell_s = 0 && \text{(start vertex has label 0)}\\
            \ell_e = n-1 && \text{(end vertex has label } n-1 \text{)}\\
            \forall (u,v) \in E \setminus \{(u, s)\mid u \in V \}:\\
            \ell_u - \ell_v + nx_{uv} \leq n-1
            && \text{(increasing labels along tour)}\\
            \end{align*}
    """

    # Create model
    m = Model("graphilp_path_atsp")

    if metric == 'metric':
        G.G = G.G.to_directed()
        G.G.add_edges_from([(v, u) for (u, v) in G.G.edges()])

    # Add variables for edges
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))

    nbr_nodes = G.G.number_of_nodes()
    edges = G.G.edges()
    # Add variables for labels
    label_vars = m.addVars(G.G.nodes(), lb=0, ub=nbr_nodes - 1, vtype=GRB.INTEGER)
    m.update()
    edges = G.edge_variables

    # Create constraints
    # degree condition
    for node in G.G.nodes():
        # Only one outgoing connection from every node
        m.addConstr(quicksum([edges[e] for e in G.G.edges(node)]) == 1)
        
        # Only one incoming connection to every node
        m.addConstr(quicksum([edges[e] for e in G.G.in_edges(node)]) == 1)
        
        # lifted constraints after Desrochers and Laporte
        if (node, 1) in edges:
            m.addConstr(-label_vars[node] + (nbr_nodes - 3) * edges[(node, 1)]
                + sum(edges[(j, node)] for j in range(2, nbr_nodes) if ((j, node) in edges and j != node)) <= -1)
        else:
            m.addConstr(-label_vars[node]
                + sum(edges[(j, node)] for j in range(2, nbr_nodes) if ((j, node) in edges and j != node)) <= -1)
        if (1, node) in edges:
            m.addConstr(label_vars[node] + (nbr_nodes - 3) * edges[(1, node)]
                + sum(edges[(node, j)] for j in range(2, nbr_nodes) if ((node, j) in edges and j != node)) <= nbr_nodes - 1)
        else:
            m.addConstr(label_vars[node] + sum(edges[(node, j)] for j in range(2, nbr_nodes) if ((node, j) in edges and j != node)) <= nbr_nodes - 1)

    for (u, v) in G.G.edges():
        if (u >= 2 and v >= 2):
            m.addConstr(label_vars[u] - label_vars[v] + (nbr_nodes - 1) * edges[(u, v)] + (nbr_nodes - 3) * edges[(v, u)] <= nbr_nodes - 2)

    # set optimisation objective: find the min / max round tour in G
    m.setObjective(quicksum([edges[(u, v)] * w.get(weight, 1) for (u, v, w) in G.G.edges(data=True)]), direction)

    # set warmstart
    if len(warmstart) > 0:

        # initialise warmstart by excluding all edges and vertices from solution
        for edge_var in edges.values():
            edge_var.Start = 0

        for label_var in label_vars.values():
            label_var.Start = 0

        # set edges and labels along warmstart tour
        pos = 0

        for edge in warmstart:
            edges[edge].Start = 1
            label_vars[edge[0]].Start = pos
            pos += 1

        m.update()

    return m


def extract_solution(G, model):
    """ Get the optimal tour in G

        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for min/max Path asymmetric TSP

        :return: the edges of an optimal tour/path in G
    """
    edge_vars = G.edge_variables

    tour = [edge for edge, edge_var in edge_vars.items() if edge_var.X > 0.5]

    return tour
