from gurobipy import Model, GRB, quicksum


def get_heuristic(G):
    r""" Approximate solution to the minimum vertex cover problem via LP rounding

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a list of vertices forming a vertex cover of G

    LP:
        The following LP with continuous node variables is rounded to obtain an approximation.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v\in V} x_v\\
            \text{s.t.}&&\\
            \forall \{u, v\} \in E: x_u + x_v \geq 1 && \text{(at least one vertex in each edge is covered)}\\
            \forall v \in V: & x_v \geq 0\\
            \forall v \in V: & x_v \leq 1\\
            \end{align*}
    """
    # create model
    m = Model("graphilp_min_vertex_cover")

    # add continuous variables for the nodes
    nodes = m.addVars(G.G.nodes())
    m.update()

    # set objective: minimise the sum of node values
    m.setObjective(quicksum(nodes.values()), GRB.MINIMIZE)

    # create constraints
    # for every edge, at least one vertex must be in a vertex cover of G
    for (u, v) in G.G.edges():
        m.addConstr(nodes[u] + nodes[v] >= 1)

    for node_var in nodes.values():
        m.addConstr(node_var <= 1)
        m.addConstr(node_var >= 0)

    # solve model
    m.optimize()

    # round the LP to get a valid vertex cover
    warmstart = [node for node, node_var in nodes.items() if node_var.X >= 0.5]

    return warmstart
