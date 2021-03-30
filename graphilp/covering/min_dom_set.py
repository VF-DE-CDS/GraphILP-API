from gurobipy import Model, quicksum, GRB


def create_model(G):
    r""" Create an ILP for the minimum dominating set problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v\in V}~x_v\\
            \text{s.t.}&&\\
            \forall v \in V:& \sum_{a\in \bigcup_{v\in e} e  }  x_a \geq 1 & \text{(each node is covered by a neighbour)}
            \end{align*}

    Example:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_mindomset.png
             - `Minimum dominating set <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/DominatingQueens.ipynb>`_

               Find how many queens are needed to cover all squares on an :math:`n\times n` chessboard.
    """
    # Create model
    m = Model("graphilp_min_dominating_set")

    # Add variables for edges
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables
    # Create constraints
    # for every node, at least one adjacent node or the node itself must be taken
    for u in G.G.nodes:
        m.addConstr(quicksum([nodes[n] for n in G.G.neighbors(u)]) + nodes[u] >= 1)

    # set optimisation objective: minimize the cardinality of the dominating set
    m.setObjective(quicksum(nodes), GRB.MINIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of edges comprising a dominating set

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for minimum dominating set

    :return: a list of nodes comprising a minimum dominating set
    """
    dominating_set = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]

    return dominating_set
