# +
from numpy import array, zeros
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.covering.heuristics import setcover_greedy

S = ilpss.ILPSetSystem()

S.set_system({1: {'weight': 1}, 2: {'weight': 1}, 3: {'weight': 1}, 4: {'weight': 1}, 5: {'weight': 1}})
S.set_universe({1: {'weight': 1}, 2: {'weight': 1}, 3: {'weight': 1}, 4: {'weight': 1}, 5: {'weight': 1}, 6: {'weight': 1}})
M = array([[1,1,1,0,0,0], [0,0,0,1,1,1], [1,1,0,0,0,0], [0,0,1,1,0,0], [0,0,0,0,1,1]])
S.set_inc_matrix(M.transpose())

cover = setcover_greedy.get_heuristic(S)
set_vector = zeros(len(S.S))
for index, setname in enumerate(S.S):
    if setname in cover:
        set_vector[index] = 1
covered = sum(sum((S.M*set_vector).transpose())) >= len(S.U)

assert(covered == True)
