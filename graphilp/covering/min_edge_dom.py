from gurobipy import Model, quicksum, GRB


def create_model(G):
    r""" Create an ILP for the minimum edge dominating set problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{e\in E}x_e\\
            \text{s.t.}&&\\
            \forall e \in E:& \sum_{a\in E ~:~e\cap a \neq \emptyset  }  x_a \geq 1 &
            \text{(each edge must be covered by an adjacent one)} \\
            \end{align*}
    """
    # Create model
    m = Model("graphilp_min_edge_dominating_set")

    # Add variables for edges
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    m.update()

    edges = G.edge_variables

    # Create constraints
    # for every edge, at least one adjacent edge or the edge itself must be taken
    for (u, v) in G.G.edges:
        adjacent_edges = list(G.G.edges(u)) + list(G.G.edges(v))
        filter_adj = list(set([t if t[0] < t[1] else t[::-1] for t in adjacent_edges]))
        m.addConstr(quicksum([edges[(i, j)] for (i, j) in filter_adj]) >= 1)

    # set optimisation objective: minimize cardinality of the edge dominating set
    m.setObjective(quicksum(edges), GRB.MINIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of edges comprising an edge dominating set

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for minimum edge dominating set

    :return: a list of edges comprising a minimum edge dominating set
    """
    dominating_set = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return dominating_set
