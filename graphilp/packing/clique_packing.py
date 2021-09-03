from gurobipy import Model, GRB, quicksum
from itertools import product
from networkx import non_edges


def create_model(G, clique_size):
    r""" Create an ILP for the clique packing problem

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param clique_size: size of the clique to be packed

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`k` be the size of the cliques to be packed, :math:`\overline{E}` be the complement of
        the edge set, and :math:`C = \{0, \ldots, \lfloor |V|/k \rfloor \}`
        an index set for the possible cliques packed into :math:`G`.

        The ILP formulation uses the following variables:

        .. list-table::
           :widths: 20 80
           :header-rows: 0

           * - :math:`y_{c}`
             - Binary variables indicating whether a clique with index :math:`c` is used.
           * - :math:`a_{cv}`
             - Binary variables indicating whether vertex :math:`v` is part of the clique with index :math:`c`.

        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{c \in C} y_c\\
            \text{s.t.} &&\\
            \forall v \in V: \sum_{c \in C} a_{cv} \leq 1 && \text{(each vertex can be in at most one clique)}\\
            \forall \{u, v\} \in \overline{E}: \forall c \in C:\\
            a_{cu} + a_{cv} \leq 1
            && \text{(unconnected vertices cannot be in the same clique)}\\
            \forall c \in C: \sum_{v \in V} a_{cv} - k y_c = 0 && \text{(chosen cliques need to have k members)}\\
            \forall c \in C: \forall v \in V: y_c - a_{cv} \geq 0
            && \text{(cluster with } \geq 1 \text { vertex needs to be chosen as clique)}\\
            \end{align*}

    Example:
            .. list-table::
               :widths: 50 50
               :header-rows: 0

               * - .. image:: images/example_clique_packing.png
                 - `Packing tetrahedra <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/CliquePackingExample.ipynb>`_

                   How many vertex disjoint tetrahedra can you pack in a grid graph?
    """
    # create model
    m = Model("graphilp_clique_packing")

    # add variables for edges and nodes
    max_clusters = 1 + G.G.number_of_nodes() // clique_size

    # cluster choice variables
    cluster_choice = m.addVars(max_clusters, vtype=GRB.BINARY)

    # cluster assignment variables
    cluster_assignment = m.addVars(product(range(max_clusters), G.G.nodes()), vtype=GRB.BINARY)
    G.cluster_assignment = cluster_assignment

    m.update()

    # create constraints
    # each vertex can be in at most one clique
    for v in G.G.nodes():
        m.addConstr(quicksum([cluster_assignment[(c, v)] for c in range(max_clusters)]) <= 1)

    # clique condition: vertices not connected by an egde cannot be in the same clique
    for u, v in non_edges(G.G):
        for c in range(max_clusters):
            m.addConstr(cluster_assignment[(c, u)] + cluster_assignment[(c, v)] <= 1)

    # chosen cliques need to have k members
    for c in range(max_clusters):
        m.addConstr(quicksum([cluster_assignment[(c, v)] for v in G.G.nodes()])
                    - clique_size * cluster_choice[c] == 0)

    # each cluster with at least one vertex needs to be chosen as a clique
    for c in range(max_clusters):
        for v in G.G.nodes():
            m.addConstr(cluster_choice[c] - cluster_assignment[(c, v)] >= 0)

    m.update()

    # set optimisation objective: pack as many cliques as possible
    m.setObjective(quicksum(cluster_choice), sense=GRB.MAXIMIZE)

    return m


def extract_solution(G, model):
    """ Get a dictionary of vertex to clique assignments

    If a vertex is not assigned to a clique, its value in the dictionary is zero.

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for clique packing

    :returns: a dictionary mapping vertices to cliques
    """
    cliques = {v: 0 for v in G.G.nodes()}
    for k, v in G.cluster_assignment.items():
        if v.X > 0.5:
            cliques[k[1]] = k[0]+1

    return cliques
