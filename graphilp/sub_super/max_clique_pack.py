from gurobipy import Model, GRB, quicksum
from itertools import combinations


def create_model(G):
    r""" Create an ILP for the maximum clique problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{v \in V} x_v\\
            \text{s.t.} &&\\
            \forall (u, v) \in \overline{E}: x_u + x_v \leq 1 && \text{(ensure every pair of nodes is connected)}\\
            \end{align*}
    """
    # Create model
    m = Model("graphilp_max_clique")

    # Add variables for edges and nodes
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables

    # Create constraints
    # for every pair of nodes, they can only be in the max clique when there is an edge between them
    for (u, v) in combinations(G.G.nodes(), 2):
        if (u, v) not in G.G.edges():
            m.addConstr(nodes[u] + nodes[v] <= 1)

    # set optimisation objective: maximum weight matching (sum of weights of chosen edges)
    m.setObjective(quicksum(nodes), GRB.MAXIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a maximal clique

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for maximum clique

    :return: a list of vertices comprising a maximal clique
    """
    clique_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]

    return clique_nodes
