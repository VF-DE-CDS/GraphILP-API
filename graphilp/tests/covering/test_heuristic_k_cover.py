from numpy import array
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering.heuristics import setcover_greedy
from graphilp.tests.covering.test_heuristic_set_cover import _is_set_covered


def test_heuristic_k_cover():
    S = ilpss.ILPSetSystem()

    S.set_system({1: {'weight': 1}, 2: {'weight': 1}, 3: {'weight': 1}, 4: {'weight': 1}, 5: {'weight': 1}})
    S.set_universe({1: {'weight': 1}, 2: {'weight': 1}, 3: {'weight': 1}, 4: {'weight': 1}, 5: {'weight': 1}, 6: {'weight': 1}})
    M = array([[1,1,1,0,0,0], [0,0,0,1,1,1], [1,1,0,0,0,0], [0,0,1,1,0,0], [0,0,0,0,1,1]])
    S.set_inc_matrix(M.transpose())

    k = 2

    cover = setcover_greedy.get_heuristic(S, k)

    assert(len(cover) <= k)
    assert _is_set_covered(S, cover)
