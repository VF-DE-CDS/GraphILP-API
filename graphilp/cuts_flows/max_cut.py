from gurobipy import Model, GRB, quicksum


def create_model(G, weight='weight', warmstart=[]):
    r""" Create an ILP for the maximum weight cut problem

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param warmstart: a list of vertices inducing a cut

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{(u,v) \in E} w_{uv}x_{uv}\\
            \text{s.t.} &&\\
            \forall (u,v) \in E: x_{uv} & \leq x_u + x_v & \text{(for every edge, the nodes must be separated )}\\
            \forall (u,v) \in E: x_{uv} & \leq 2 - x_u - x_v & \text{(for every edge, the nodes must be separated )}\\
            \end{align*}

    Example:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_binarisation.png
             - `Maximum weight cuts <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/Binarisation.ipynb>`_

               Use maximum weight cuts for image binarisation.
    """
    # Create model
    m = Model("graphilp_max_cut")

    # Add variables for edges and nodes
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables
    edges = G.edge_variables

    # Create constraints
    # for every edge, the nodes must be separated
    for (u, v) in G.G.edges:
        m.addConstr(edges[(u, v)] <= nodes[v] + nodes[u])
        m.addConstr(edges[(u, v)] <= 2 - nodes[v] - nodes[u])

    # set optimisation objective: maximize the total weight of edges in the cut
    m.setObjective(quicksum([G.G.edges[edge].get(weight, 1) * edge_var for edge, edge_var in edges.items()]),
                   GRB.MAXIMIZE)

    if len(warmstart) > 0:

        # put all vertices in one set
        for node_var in nodes.values():
            node_var.Start = 0

        # move all vertices in warmstart into the other set
        for node in warmstart:
            nodes[node].Start = 1

    m.update()

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a maximum cut of G

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for max weight cut

    :return: a list of vertices comprising a maximum weight cut of G
    """
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]

    return cut_nodes
