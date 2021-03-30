from gurobipy import Model, GRB, quicksum
import networkx as nx


def createGenModel(G, type_obj, metric):
    r""" Create another formulation which is faster as ILP for the min Path asymmetric TSP. Start and End Nodes cannot be fixed in this formulation

    :param G: a weighted ILPGraph
    :param type_obj: choose whether to minimise or maximise the weight of the path
    :param metric: 'metric' for symmetric problem otherwise asymmetric problem
    """

    # Create model
    m = Model("graphilp_path_atsp")

    if metric == 'metric':
        G_d = G.G.to_directed()
        G_r = G_d.reverse(copy=True)
        G.G = nx.compose(G_d, G_r)

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
    if type_obj == 'min':
        m.setObjective(quicksum([edges[(u, v)] * w['weight'] for (u, v, w) in G.G.edges(data=True)]), GRB.MINIMIZE)
    if type_obj == 'max':
        m.setObjective(quicksum([edges[(u, v)] * w['weight'] for (u, v, w) in G.G.edges(data=True)]), GRB.MAXIMIZE)

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
