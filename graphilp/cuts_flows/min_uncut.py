from gurobipy import Model, GRB, quicksum
from networkx import complement


def create_model(G):
    r""" Create an ILP for the min uncut problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`\bar{G} = (V, \bar{E} := \{\{u, v\} \in V\times V \mid \{u, v\} \not\in E\})`
        be the complement of the input graph :math:`G`.

        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{(u,v) \in \bar{E}}x_{uv}\\
            \text{s.t.} &&\\
            \forall (u,v) \in \bar{E}: x_{uv} & \leq x_u + x_v & \text{(for every edge, the nodes must be separated )}\\
            \forall (u,v) \in \bar{E}: x_{uv} & \leq 2 - x_u - x_v & \text{(for every edge, the nodes must be separated )}\\
            \end{align*}

    """

    # Create model
    m = Model("graphilp_min_uncut")

    # Add variables for nodes
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables

    GC = complement(G.G)

    edges = m.addVars(GC.edges(), vtype=GRB.BINARY)
    m.update()

    # Create constraints
    # for every edge, the nodes must be separated in the complement graph
    for (u, v) in GC.edges():
        m.addConstr(edges[(u, v)] <= nodes[v] + nodes[u])
        m.addConstr(edges[(u, v)] <= 2 - nodes[v] - nodes[u])

    # set optimisation objective: maximize the cardinality of the number of edges in the cut of the complement graph
    m.setObjective(quicksum(edges), GRB.MAXIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a maximum cut of the complement graph

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :model: a solved Gurobi model for minimum uncut problem

        :return: a list of vertices comprising a cut and a solution to the minimum uncut problem
    """
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]

    return cut_nodes
