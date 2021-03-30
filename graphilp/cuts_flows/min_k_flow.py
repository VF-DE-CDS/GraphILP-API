from gurobipy import Model, GRB, quicksum


def create_model(G):
    r""" Create an ILP for the `minimum k-flow problem <https://en.wikipedia.org/wiki/Nowhere-zero_flow>`_

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min k\\
            \text{s.t.} &&\\
            \forall v \in V: \sum_{(v,u)\in E} x_{vu} - \sum_{(u,v)\in E} x_{uv} &= 0 & \text{(flow condition)}\\
            \forall (u,v) \in E: x_{uv}-k &\leq -1 & \text{(flow bounded by k)}\\
            \forall (u,v) \in E: x_{uv}+k &\geq 1 & \text{(flow bounded by k)}\\
            \forall (u,v) \in E: 2|E|\sigma_{uv} + x_{uv} &\geq 1 & \text{(nowhere zero)}\\
            \forall (u,v) \in E: 2|E|(1-\sigma_{uv}) - x_{uv} &\geq 1 & \text{(nowhere zero)}\\
            \end{align*}

        We assume an arbitrary orientation of the graph as given by the order of nodes in each edge.
        Binary sign variables :math:`\sigma_{uv}` indicate whether the flow value on an edge is positive
        (:math:`\sigma_{uv}=1`) or negative (:math:`\sigma_{uv}=0`).

    References:
        Diestel: `Graph Theory <http://diestel-graph-theory.com>`_, Chapter 6.
    """

    # Create model
    m = Model("graphilp_min_k_flow")

    # add variables for flow values on edges
    edge_vars = m.addVars(G.G.edges(), lb=-G.G.number_of_edges(), ub=G.G.number_of_edges(), vtype=GRB.INTEGER)
    G.set_edge_vars(edge_vars)

    # add helper variables indicating whether flow on an edge is positive or negative
    sign_vars = m.addVars(G.G.edges(), vtype=GRB.BINARY)

    # add target variable k bounding the flow
    k = m.addVar(vtype=GRB.INTEGER)

    G.sign_variables = sign_vars
    G.k = k

    m.update()

    # Create constraints

    # flow condition
    for node in G.G.nodes():
        m.addConstr(quicksum([edge_vars[e] for e in G.G.edges() if e[0] == node]
                           + [-edge_vars[e] for e in G.G.edges() if e[1] == node]) == 0)

    # flow bounded by k
    for edge, edge_var in edge_vars.items():
        m.addConstr(edge_var - k <= -1)
        m.addConstr(edge_var + k >= 1)

    # nowhere zero
    M = 2 * G.G.number_of_edges()

    for edge in G.G.edges():
        m.addConstr(M * sign_vars[edge] + edge_vars[edge] >= 1)
        m.addConstr(M * (1-sign_vars[edge]) - edge_vars[edge] >= 1)

    # set optimisation objective: find the smallest k such that there is a nowhere-zero k-bounded flow
    m.setObjective(k, GRB.MINIMIZE)

    return m


def extract_solution(G, model):
    """ Get the flow bound and a dictionary of edge weights realising a flow

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for minimum k-flow

        :return: the minimal flow bound k and a dictionary of edge weights realising a flow
    """
    edge_vars = G.edge_variables

    weights = [(edge, edge_var.X) if edge_var.X > 0
          else ((edge[1], edge[0]), -edge_var.X)
                for edge, edge_var in edge_vars.items()]

    return G.k.X, dict(weights)
