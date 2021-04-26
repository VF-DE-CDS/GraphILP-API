from gurobipy import Model, GRB, quicksum
from itertools import combinations


def create_model(G):
    r""" Create an ILP for the maximum clique problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        This formulation makes use of the connection between clique and vertex cover in the complement.
        It excludes as few nodes as possible from a clique but needs to exclude at least one node from each pair
        not connected by an edge.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v \in V} x_v\\
            \text{s.t.} &&\\
            \forall (u, v) \in \overline{E}: x_u + x_v \geq 1 && \text{(exclude at least one node from each unconnected pair)}\\
            \end{align*}

    Example:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_mapcolouring.png
             - `Map colouring <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/MapColouring.ipynb>`_

               Colour a map with as few colours as possible such that

               no two adjacent areas get the same colour.
    """
    # Create model
    m = Model("graphilp_max_clique")

    # Add variables for edges and nodes
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    m.update()

    nodes = G.node_variables

    # Create constraints
    # for every pair of nodes, at least one node must cover the edge
    for (u, v) in combinations(G.G.nodes(), 2):
        if (u, v) not in G.G.edges():
            m.addConstr(nodes[u] + nodes[v] >= 1)

    # set optimisation objective: minimum vertex cover
    m.setObjective(quicksum(nodes), GRB.MINIMIZE)

    return m


def extract_solution(G, model):
    """ Get a list of vertices comprising a maximal clique

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for maximum clique

        :return: a list of vertices comprising a maximal clique
    """
    clique_nodes = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]

    return clique_nodes
