from gurobipy import Model, GRB, quicksum


def create_model(G):
    r""" Create an ILP for the maximum independet set problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        This formulation creates a vertex cover and uses the fact that
        a `maximum independent set <https://en.wikipedia.org/wiki/Independent_set_(graph_theory)#Relationship_to_other_graph_parameters>`__
        consists of the complement of the vertices in a minimum vertex cover.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v \in V} x_v\\
            \text{s.t.} &&\\
            \forall (u, v) \in E: x_u + x_v \geq 1 && \text{(at least one vertex must be in a vertex cover of G)}\\
            \end{align*}
    """
    # Create model
    m = Model("graphilp_max_ind_set")

    # Add variables for edges and nodes
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()
    nodes = G.node_variables

    # Create constraints
    # for every edge, at least one vertex must be in a vertex cover of G
    for (u, v) in G.G.edges:
        m.addConstr(nodes[u] + nodes[v] >= 1)

    # set optimisation objective: minimize cardinality of the vertex cover
    m.setObjective(quicksum(nodes), GRB.MINIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a maximum independent set

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for maximum independent set

    :returns: a list of vertices comprising a maximum independent set
    """
    ind_set = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]

    return ind_set
