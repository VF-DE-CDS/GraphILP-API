# +
from numpy import array, zeros

from graphilp.covering.heuristics import setcover_greedy
from graphilp.imports import ilpsetsystem as ilpss


def test_heuristic_set_cover():
    S = ilpss.ILPSetSystem()
    S.set_universe({0: {'weight': 1}, 1: {'weight': 1}, 2: {'weight': 1}, 3: {'weight': 1}})
    S.set_system({0: {'weight': 1}, 1: {'weight': 1}, 2: {'weight': 1}})
    M = array([[0, 0, 0, 1], [1, 1, 1, 0], [0, 1, 1, 0]])
    S.set_inc_matrix(M.transpose())

    cover = setcover_greedy.get_heuristic(S)

    assert _is_set_covered(S, cover)
    assert cover == [1, 0], "Expected: [1, 0]"


def _is_set_covered(S, cover):
    set_vector = zeros(len(S.S))
    for index, set_name in enumerate(S.S):
        if set_name in cover:
            set_vector[index] = 1
    return sum(sum((S.M * set_vector).transpose())) >= len(S.U)
