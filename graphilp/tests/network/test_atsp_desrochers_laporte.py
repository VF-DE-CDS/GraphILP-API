import networkx as nx

from graphilp.imports import networkx as impnx
from graphilp.network import atsp_desrochers_laporte as tsp
from gurobipy import GRB

def test_atsp_desrochers_laporte():
    # create graph instance
    n=10

    G = nx.complete_graph(n)
    G.add_weighted_edges_from([(u, (u+1)%n, 2) for u in range(n)])
    G.add_weighted_edges_from([(2, 7, 10)])

    # wrap as GraphILP graph
    optG = impnx.read(G)

    # create a warmstart
    warmstart=[(0, 2), (2, 1), (1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 0)]

    # generate model
    m = tsp.create_model(optG, GRB.MAXIMIZE, metric='metric', warmstart=warmstart)

    # solve model
    m.optimize()

    # extract solution
    tour = tsp.extract_solution(optG, m)

    # check correctness
    assert(len(tour) == n)
    assert((2, 7) in tour)