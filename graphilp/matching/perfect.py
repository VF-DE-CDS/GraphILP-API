from gurobipy import Model, GRB, quicksum


def create_model(G, weight='weight', direction=GRB.MAXIMIZE):
    r""" Create an ILP for maximum/minimum weight perfect matching

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param direction: GRB.MAXIMIZE for maximum weight matching, GRB.MINIMIZE for minimum weight matching

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`n` be the number of vertices in the graph.

        .. math::
            :nowrap:

            \begin{align*}
            \max / \min \sum_{\{i, j\} \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            \forall \{u, v\} \in E: x_{uv} = n/2&&
            \text{(} n/2 \text{ edges in matching)}\\
            \forall v \in V: \sum_{\{u,v\} \in E} x_{uv} \leq 1 &&
            \text{(at most one edge adjacent to each vertex)}\\
            \end{align*}
    """

    # Create model
    m = Model("graphilp_max_weight_perfect_matching")

    # Add variables for edges
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    m.update()

    edges = G.edge_variables

    # Create constraints
    # at most one edge can be adjacent to each vertex
    for node in G.G.nodes():
        m.addConstr(quicksum([edges.get(edge, edges.get((edge[1], edge[0]))) for edge in G.G.edges(node)]) <= 1)

    # perfect matching
    m.addConstr(quicksum(edge_var for edge_var in edges.values()) == G.G.number_of_nodes()//2)
    m.update()

    # set optimisation objective: maximum weight matching (sum of weights of chosen edges)
    m.setObjective(quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]),
                   direction)

    return m


def extract_solution(G, model):
    """ Get a list of the edges comprising the minimum/maximum weight perfect matching

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for maximum weight matching

        :return: a list of edges comprising the maximum weight matching
    """
    matching = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return matching
