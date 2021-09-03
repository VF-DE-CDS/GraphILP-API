from gurobipy import Model, quicksum, GRB


def create_model(G, weight='weight', warmstart=[]):
    r""" Create an ILP for the minimum vertex cover problem

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the weight parameter in the node dictionary of the graph
    :param warmstart: a list of vertices forming a vertex cover of G

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
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables

    # Create constraints
    # for every edge, at least one vertex must be in a vertex cover of G
    for (u, v) in G.G.edges:
        m.addConstr(nodes[u] + nodes[v] >= 1)

    # set optimisation objective: minimize total node weight of the vertex cover
    m.setObjective(quicksum([node_var * G.G.nodes()[node].get(weight, 1)
                                       for node, node_var in nodes.items()]),
                   GRB.MINIMIZE)

    # set warmstart
    if len(warmstart) > 0:
        for node in nodes:
            nodes[node].Start = node in warmstart
        m.update()

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a vertex cover

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for minimum vertex cover

    :return: list of vertices of minimum vertex cover
    """
    vertex_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]

    return vertex_nodes
