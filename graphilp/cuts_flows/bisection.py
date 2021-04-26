from gurobipy import Model, GRB, quicksum
from math import ceil, floor


def create_model(G, slack=0, weight='weight', direction=GRB.MAXIMIZE):
    r""" Create an ILP for the minimum/maximum bisection problem

    Bisect the graph into two partitions of equal size (allowing some slack) such that
    the sum of the weights of the edges removed to bisect the graph is minimal/maximal.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param slack: allow imbalance between the two partitions by slack many nodes
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param direction: GRB.MAXIMIZE for maximum weight bisection, GRB.MINIMIZE for minimum weight bisection

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`s` denote the slack allowed in the partition size.

        .. math::
            :nowrap:

            \begin{align*}
            & \min / \max_{\{u,v\} \in E} \sum x_{u,v}\\
            & \text{s.t.} &\\
            & \sum_{v \in V} x_v \leq \lceil |V|/2 \rceil + s & \text{(lower bound size of one partition)}\\
            & \sum_{v \in V} x_v \geq \lfloor |V|/2 \rfloor - s & \text{(upper bound size of one partition)}\\
            & \forall \{u,v\} \in E: x_{u, v} \leq x_u + x_v & \text{(no edge between partitions)}\\
            & \forall \{u,v\} \in E: x_{u, v} \leq 2 - x_u - x_v & \text{(no edge between partitions)}\\
            \end{align*}
    """
    # Create model
    m = Model("graphilp_bisection")

    # Add variables for edges and nodes
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.node_variables

    number_nodes = len(G.G.nodes())
    bound_upper = ceil(number_nodes/2)
    bound_lower = floor(number_nodes/2)

    # Create constraints
    # balanced solutions are needed
    m.addConstr(quicksum(nodes) <= bound_upper + slack)
    m.addConstr(quicksum(nodes) >= bound_lower - slack)

    # for every edge, the nodes must be separated
    for (u, v) in G.G.edges():
        m.addConstr(edges[(u, v)] <= nodes[v] + nodes[u])
        m.addConstr(edges[(u, v)] <= 2 - nodes[v] - nodes[u])

    # set optimisation objective: minimize/maximize the cardinality of the number of edges in the cut
    m.setObjective(quicksum([G.G.edges[edge][weight] * edge_var for edge, edge_var in edges.items()]),
                   direction)

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a minimum/maximum balanced cut of G

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for the minimum/maximum bisection problem

    :return: a list of vertices comprising a minimum/maximum balanced cut of G
    """
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]

    return cut_nodes
