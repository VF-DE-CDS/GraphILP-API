# -*- coding: utf-8 -*-
from gurobipy import Model, GRB, quicksum


def create_model(G, direction=GRB.MAXIMIZE, metric='', weight='weight', warmstart=[]):
    r""" Faster formulation for the min/max asymmetric TSP

    This formulation implements a formulation from Desrochers and Laporte (1990):
    `Improvements and extensions to the Miller–Tucker–Zemlin subtour elimination constraints
    <https://doi.org/10.1016/0167-6377(91)90083-2>`__

    :param G: a complete weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param direction: GRB.MAXIMIZE for maximum weight tour, GRB.MINIMIZE for minimum weight tour
    :param metric: 'metric' for symmetric problem otherwise asymmetric problem
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param warmstart: a list of edges forming a tour

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`s` be an arbitrary starting node for the tour.

        .. math::
            :nowrap:

            \begin{align*}
            \min / \max \sum_{(u,v) \in E} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall v \in V: \sum_{(u, v) \in E}x_{uv} = 1 && \text{(exactly one incoming edge)}\\
            \forall u \in V: \sum_{(u, v) \in E}x_{uv} = 1 && \text{(exactly one outgoing edge)}\\
            \forall u, v \in V \setminus \{s\}: \\
            \ell_u - \ell_v + (n-1)x_{uv} + (n-3)x_{vu} \leq n-2
            && \text{(labels increase by one in edge direction)}\\
            \\
            \forall u \in V \setminus \{s\}:\\
            -\ell_u + (n-3)x_{us} + \sum_{v \in V \setminus \{s\}}x_{vu} \leq -1
            && \text{(subtour elimination)}\\
            \\
            \forall u \in V \setminus \{s\}:\\
            \ell_u + (n-3)x_{su} + \sum_{v \in V \setminus \{s\}}x_{uv} \leq n-1
            && \text{(subtour elimination)}\\
            \end{align*}

    References:
        See Roberti and Toth: `Models and algorithms for the Asymmetric Traveling Salesman Problem:
        an experimental comparison <https://link.springer.com/article/10.1007/s13676-012-0010-0>`__
        for this formulation in context.
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

    # Choose an arbitrary start node
    start_node = list(G.G.nodes())[0]

    # Create constraints
    # degree condition
    for node in G.G.nodes():
        # Only one outgoing connection from every node
        m.addConstr(quicksum([edges[e] for e in G.G.edges(node)]) == 1)

        # Only one incoming connection to every node
        m.addConstr(quicksum([edges[e] for e in G.G.in_edges(node)]) == 1)

        if node != start_node:
            m.addConstr(-label_vars[node] + (nbr_nodes - 3) * edges[(node, start_node)]
                        + sum(edges[(j, node)] for j in G.G.nodes() if j != start_node and j != node) <= -1)

            m.addConstr(label_vars[node] + (nbr_nodes - 3) * edges[(start_node, node)]
                        + sum(edges[(node, j)] for j in G.G.nodes() if j != start_node and j != node) <= nbr_nodes - 1)

    for (u, v) in G.G.edges():
        if (u != start_node and v != start_node):
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

        :param G: a complete weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for min/max asymmetric TSP

        :return: the edges of an optimal tour in G
    """
    edge_vars = G.edge_variables

    tour = [edge for edge, edge_var in edge_vars.items() if edge_var.X > 0.5]

    return tour
