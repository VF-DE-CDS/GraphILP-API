# -*- coding: utf-8 -*-
from gurobipy import Model, GRB, quicksum


def create_model(G, A, weight='weight', direction=GRB.MAXIMIZE):
    r""" Create an ILP for maximum/minimum bipartite perfect matching

    :param G: a weighted bipartite :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param A: subset of the vertex set of G giving the bipartition (each edge has exactly one end in A)
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param direction: GRB.MAXIMIZE for maximum weight matching, GRB.MINIMIZE for minimum weight matching

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        .. math::
            :nowrap:

            \begin{align*}
            \max / \min \sum_{\{i, j\} \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            \forall u \in A: \sum_{\{u,v\} \in E} x_{uv} = 1 &&
            \text{(exactly one edge adjacent to each } u \in A\text{)}\\
            \forall u \in V \setminus A: \sum_{\{u,v\} \in E} x_{uv} = 1 &&
            \text{(exactly one edge adjacent to each } u \in V \setminus A\text{)}\\
            \end{align*}

        This is actually a linear program, i.e., solutions to the LP relaxation are automatically integral.

    References:
        Lovász, Plummer: `Matching Theory <https://www.ams.org/publications/authors/books/postpub/chel-367>`__, Chapter 7.1.

    Example:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_bipartite.png
             - `Two-coloured partitions <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/2ColouredPartitions.ipynb>`_

               Learn how to use perfect matching in bipartite graphs to find a way

               to connect n random blue points in the plane

               to n random orange points without crossings.
    """

    # Create model
    m = Model("graphilp_bipartite_perfect_matching")

    # Add variables for edges and nodes
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.G.nodes()

    # Create constraints
    # for each u in A there is exactly one edge adjacent to it
    for u in A:
        m.addConstr(quicksum([edge_var for edge, edge_var in edges.items() if u in edge]) == 1)

    # for each v in V setminus A there is exactly one edge adjacent to it
    for v in nodes:
        if v not in A:
            m.addConstr(quicksum([edge_var for edge, edge_var in edges.items() if v in edge]) == 1)

    # set optimisation objective: maximum/minimum weight matching (sum of weights of chosen edges)
    m.setObjective(quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]), direction)

    return m


def extract_solution(G, model):
    """ Get a list of the edges comprising the miniumum/maximum weight perfect bipartite matching

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for minimum/maximum weight perfect bipartite matching

        :return: a list of edges comprising the minimum/maximum weight perfect bipartite matching
    """
    if model.Status == GRB.INFEASIBLE:
        matching = []
    else:
        matching = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return matching
