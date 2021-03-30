from gurobipy import Model, GRB, quicksum


def create_model(G, weight='weight'):
    r""" Create an ILP for maximum weight matching

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the weight parameter in the edge dictionary of the graph

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{\{i, j\} \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            \forall \{u, v\} \in E: x_{uv} - x_u \leq 0 &&
            \text{(choosing an edge implies choosing both of its vertices)}\\
            \forall \{u, v\} \in E: x_{uv} - x_v \leq 0 &&
            \text{(choosing an edge implies choosing both of its vertices)}\\
            \forall v \in V: \sum_{\{u,v\} \in E} x_{uv} \leq 1 &&
            \text{(at most one edge adjacent to each vertex)}\\
            \end{align*}
    """
    # Create model
    m = Model("graphilp_max_weight_matching")

    # Add variables for edges and nodes
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.node_variables

    # Create constraints
    # choosing an edge implies choosing both of its vertices
    for edge, edge_var in edges.items():
        m.addConstr(edge_var - nodes[edge[0]] <= 0)
        m.addConstr(edge_var - nodes[edge[1]] <= 0)

    # at most one edge can be adjacent to each vertex
    for node in nodes:
        m.addConstr(quicksum([edge_var for edge, edge_var in edges.items() if edge[0] == node or edge[1] == node]) <= 1)

    # set optimisation objective: maximum weight matching (sum of weights of chosen edges)
    m.setObjective(quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]),
                   GRB.MAXIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of the edges comprising the maximum weight matching

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for maximum weight matching

        :return: a list of edges comprising the maximum weight matching
    """
    matching = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return matching
